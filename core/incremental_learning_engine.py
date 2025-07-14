#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
増分学習エンジン - Phase 2E実装
継続的知識更新・学習パターン適応・効率的知識統合システム
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from datetime import datetime, timedelta
import hashlib
import numpy as np
from statistics import mean, median, stdev
import copy

# プロジェクトルートをパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 関連システム
try:
    from core.real_time_knowledge_updater import RealTimeKnowledgeUpdater, NewInformation, KnowledgeUpdate
    from core.user_interest_tracker import UserInterestTracker
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False

# Windowsパス設定
if os.name == 'nt':
    DATA_DIR = Path("D:/setsuna_bot/youtube_knowledge_system/data")
    LEARNING_CACHE_DIR = Path("D:/setsuna_bot/incremental_learning_cache")
else:
    DATA_DIR = Path("/mnt/d/setsuna_bot/youtube_knowledge_system/data")
    LEARNING_CACHE_DIR = Path("/mnt/d/setsuna_bot/incremental_learning_cache")

LEARNING_CACHE_DIR.mkdir(parents=True, exist_ok=True)

@dataclass
class LearningPattern:
    """学習パターンデータクラス"""
    pattern_id: str
    pattern_type: str           # "incremental", "batch", "reinforcement", "forgetting"
    learning_rate: float        # 学習速度
    retention_rate: float       # 記憶保持率
    adaptation_speed: float     # 適応速度
    effectiveness_score: float  # 効果性スコア
    usage_frequency: int
    last_applied: str
    success_rate: float

@dataclass
class LearningSession:
    """学習セッションデータクラス"""
    session_id: str
    start_time: str
    end_time: Optional[str]
    session_type: str           # "continuous", "burst", "scheduled", "triggered"
    updates_processed: int
    knowledge_gained: float     # 知識獲得量
    learning_efficiency: float  # 学習効率
    conflicts_resolved: int
    errors_encountered: List[str]

@dataclass
class KnowledgeIntegration:
    """知識統合データクラス"""
    integration_id: str
    source_knowledge: List[str]  # 統合元知識ID
    integrated_knowledge: str    # 統合後知識ID
    integration_method: str      # "merge", "synthesize", "hierarchical", "associative"
    confidence: float
    validation_status: str       # "pending", "validated", "rejected"
    integration_complexity: float
    created_at: str

@dataclass
class AdaptiveLearningModel:
    """適応学習モデルデータクラス"""
    model_id: str
    learning_parameters: Dict[str, float]
    performance_metrics: Dict[str, float]
    adaptation_history: List[Dict[str, Any]]
    current_strategy: str        # "conservative", "aggressive", "balanced", "experimental"
    optimization_target: str     # "accuracy", "speed", "efficiency", "comprehensiveness"
    last_updated: str

class IncrementalLearningEngine:
    """増分学習エンジンクラス"""
    
    def __init__(self):
        """初期化"""
        # データパス
        self.learning_patterns_path = LEARNING_CACHE_DIR / "learning_patterns.json"
        self.learning_sessions_path = LEARNING_CACHE_DIR / "learning_sessions.json"
        self.knowledge_integrations_path = LEARNING_CACHE_DIR / "knowledge_integrations.json"
        self.adaptive_model_path = LEARNING_CACHE_DIR / "adaptive_learning_model.json"
        self.learning_metrics_path = LEARNING_CACHE_DIR / "learning_metrics.json"
        
        # 依存システム
        if DEPENDENCIES_AVAILABLE:
            self.knowledge_updater = RealTimeKnowledgeUpdater()
            self.interest_tracker = UserInterestTracker()
        else:
            self.knowledge_updater = None
            self.interest_tracker = None
            print("[増分学習] ⚠️ 依存システムが利用できません")
        
        # データ
        self.learning_patterns = {}
        self.learning_sessions = deque(maxlen=100)  # 最新100セッション
        self.knowledge_integrations = {}
        self.adaptive_model = None
        self.current_session = None
        self.learning_metrics = {}
        
        # 学習パラメータ
        self.default_learning_rate = 0.1
        self.max_integration_complexity = 0.9
        self.min_confidence_threshold = 0.6
        self.forgetting_curve_factor = 0.85
        
        # 初期化
        self._load_data()
        self._initialize_adaptive_model()
        
    def _load_data(self):
        """データ読み込み"""
        try:
            if self.learning_patterns_path.exists():
                with open(self.learning_patterns_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.learning_patterns = {k: LearningPattern(**v) for k, v in data.items()}
            
            if self.learning_sessions_path.exists():
                with open(self.learning_sessions_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.learning_sessions = deque([LearningSession(**item) for item in data], maxlen=100)
            
            if self.knowledge_integrations_path.exists():
                with open(self.knowledge_integrations_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.knowledge_integrations = {k: KnowledgeIntegration(**v) for k, v in data.items()}
            
            if self.adaptive_model_path.exists():
                with open(self.adaptive_model_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.adaptive_model = AdaptiveLearningModel(**data)
            
            if self.learning_metrics_path.exists():
                with open(self.learning_metrics_path, 'r', encoding='utf-8') as f:
                    self.learning_metrics = json.load(f)
                    
        except Exception as e:
            print(f"[増分学習] データ読み込みエラー: {e}")
    
    def _save_data(self):
        """データ保存"""
        try:
            # 学習パターン保存
            with open(self.learning_patterns_path, 'w', encoding='utf-8') as f:
                json.dump({k: asdict(v) for k, v in self.learning_patterns.items()}, f, 
                         ensure_ascii=False, indent=2)
            
            # 学習セッション保存
            with open(self.learning_sessions_path, 'w', encoding='utf-8') as f:
                json.dump([asdict(session) for session in self.learning_sessions], f, 
                         ensure_ascii=False, indent=2)
            
            # 知識統合保存
            with open(self.knowledge_integrations_path, 'w', encoding='utf-8') as f:
                json.dump({k: asdict(v) for k, v in self.knowledge_integrations.items()}, f, 
                         ensure_ascii=False, indent=2)
            
            # 適応モデル保存
            if self.adaptive_model:
                with open(self.adaptive_model_path, 'w', encoding='utf-8') as f:
                    json.dump(asdict(self.adaptive_model), f, ensure_ascii=False, indent=2)
            
            # メトリクス保存
            with open(self.learning_metrics_path, 'w', encoding='utf-8') as f:
                json.dump(self.learning_metrics, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"[増分学習] データ保存エラー: {e}")
    
    def _initialize_adaptive_model(self):
        """適応学習モデル初期化"""
        if not self.adaptive_model:
            self.adaptive_model = AdaptiveLearningModel(
                model_id=f"adaptive_model_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                learning_parameters={
                    "base_learning_rate": self.default_learning_rate,
                    "adaptation_factor": 1.0,
                    "exploration_rate": 0.1,
                    "consolidation_threshold": 0.8
                },
                performance_metrics={
                    "accuracy": 0.0,
                    "learning_speed": 0.0,
                    "retention_rate": 0.0,
                    "adaptation_efficiency": 0.0
                },
                adaptation_history=[],
                current_strategy="balanced",
                optimization_target="efficiency",
                last_updated=datetime.now().isoformat()
            )
    
    def start_learning_session(self, session_type: str = "continuous") -> str:
        """学習セッション開始"""
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.current_session = LearningSession(
            session_id=session_id,
            start_time=datetime.now().isoformat(),
            end_time=None,
            session_type=session_type,
            updates_processed=0,
            knowledge_gained=0.0,
            learning_efficiency=0.0,
            conflicts_resolved=0,
            errors_encountered=[]
        )
        
        print(f"[増分学習] 学習セッション開始: {session_id}")
        return session_id
    
    def process_knowledge_updates(self, updates: List[KnowledgeUpdate]) -> Dict[str, Any]:
        """知識更新の増分処理"""
        if not self.current_session:
            self.start_learning_session()
        
        processing_results = {
            "processed_updates": 0,
            "successful_integrations": 0,
            "conflicts_detected": 0,
            "learning_improvements": [],
            "errors": []
        }
        
        for update in updates:
            try:
                # 更新処理
                integration_result = self._integrate_knowledge_update(update)
                
                if integration_result["success"]:
                    processing_results["successful_integrations"] += 1
                    self.current_session.knowledge_gained += integration_result.get("knowledge_gain", 0.1)
                    
                    # 学習パターン更新
                    self._update_learning_patterns(update, integration_result)
                
                if integration_result.get("conflict_resolved"):
                    processing_results["conflicts_detected"] += 1
                    self.current_session.conflicts_resolved += 1
                
                processing_results["processed_updates"] += 1
                self.current_session.updates_processed += 1
                
            except Exception as e:
                error_msg = f"更新処理エラー: {str(e)}"
                processing_results["errors"].append(error_msg)
                self.current_session.errors_encountered.append(error_msg)
        
        # 学習効率計算
        if processing_results["processed_updates"] > 0:
            self.current_session.learning_efficiency = (
                processing_results["successful_integrations"] / 
                processing_results["processed_updates"]
            )
        
        # 適応モデル更新
        self._adapt_learning_model(processing_results)
        
        return processing_results
    
    def _integrate_knowledge_update(self, update: KnowledgeUpdate) -> Dict[str, Any]:
        """単一知識更新の統合"""
        integration_id = f"int_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{update.update_id[:8]}"
        
        result = {
            "success": False,
            "integration_id": integration_id,
            "knowledge_gain": 0.0,
            "conflict_resolved": False,
            "integration_method": "merge"
        }
        
        try:
            # 統合方法決定
            integration_method = self._determine_integration_method(update)
            
            # 既存知識との整合性チェック
            conflicts = self._detect_knowledge_conflicts(update)
            
            if conflicts:
                # 矛盾解決
                resolution_result = self._resolve_knowledge_conflicts(update, conflicts)
                result["conflict_resolved"] = resolution_result["resolved"]
                if not resolution_result["resolved"]:
                    result["error"] = "矛盾解決失敗"
                    return result
            
            # 知識統合実行
            integration = KnowledgeIntegration(
                integration_id=integration_id,
                source_knowledge=[update.update_id],
                integrated_knowledge=f"integrated_{integration_id}",
                integration_method=integration_method,
                confidence=update.confidence,
                validation_status="pending",
                integration_complexity=self._calculate_integration_complexity(update),
                created_at=datetime.now().isoformat()
            )
            
            self.knowledge_integrations[integration_id] = integration
            
            # 知識獲得量計算
            result["knowledge_gain"] = self._calculate_knowledge_gain(update, integration)
            result["success"] = True
            result["integration_method"] = integration_method
            
        except Exception as e:
            result["error"] = str(e)
        
        return result
    
    def _determine_integration_method(self, update: KnowledgeUpdate) -> str:
        """統合方法決定"""
        if update.update_type == "add":
            return "merge"
        elif update.update_type == "modify":
            return "synthesize"
        elif update.update_type == "enhance":
            return "hierarchical"
        else:
            return "associative"
    
    def _detect_knowledge_conflicts(self, update: KnowledgeUpdate) -> List[Dict[str, Any]]:
        """知識矛盾検出"""
        conflicts = []
        
        # 既存の知識統合と比較
        for integration_id, integration in self.knowledge_integrations.items():
            if integration.target_entity == update.target_entity:
                # 同一エンティティへの矛盾する更新
                similarity = self._calculate_knowledge_similarity(
                    update.new_value, integration.integrated_knowledge
                )
                
                if similarity < 0.3:  # 類似度が低い = 矛盾の可能性
                    conflicts.append({
                        "type": "entity_conflict",
                        "existing_integration": integration_id,
                        "conflict_severity": 1.0 - similarity,
                        "resolution_suggestion": "merge_with_validation"
                    })
        
        return conflicts
    
    def _resolve_knowledge_conflicts(self, update: KnowledgeUpdate, conflicts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """知識矛盾解決"""
        resolution_result = {
            "resolved": False,
            "resolution_method": None,
            "confidence": 0.0
        }
        
        try:
            for conflict in conflicts:
                if conflict["conflict_severity"] > 0.8:
                    # 高い矛盾 - 専門的検証が必要
                    resolution_result["resolution_method"] = "require_validation"
                    resolution_result["confidence"] = 0.3
                elif conflict["conflict_severity"] > 0.5:
                    # 中程度の矛盾 - 統合的解決
                    resolution_result["resolution_method"] = "integrate_conflicting"
                    resolution_result["confidence"] = 0.6
                else:
                    # 軽微な矛盾 - マージ
                    resolution_result["resolution_method"] = "merge_with_priority"
                    resolution_result["confidence"] = 0.8
                
                resolution_result["resolved"] = True
                break
            
        except Exception as e:
            resolution_result["error"] = str(e)
        
        return resolution_result
    
    def _calculate_integration_complexity(self, update: KnowledgeUpdate) -> float:
        """統合複雑度計算"""
        complexity = 0.0
        
        # 更新タイプによる複雑度
        type_complexity = {
            "add": 0.2,
            "modify": 0.5,
            "enhance": 0.7,
            "correct": 0.8
        }
        complexity += type_complexity.get(update.update_type, 0.5)
        
        # 関連エンティティ数による複雑度
        related_entities = len(update.supporting_evidence)
        complexity += min(related_entities * 0.1, 0.3)
        
        # 信頼度による複雑度（低信頼度 = 高複雑度）
        complexity += (1.0 - update.confidence) * 0.3
        
        return min(complexity, 1.0)
    
    def _calculate_knowledge_gain(self, update: KnowledgeUpdate, integration: KnowledgeIntegration) -> float:
        """知識獲得量計算"""
        base_gain = update.impact_score * update.confidence
        
        # 統合複雑度による調整
        complexity_factor = 1.0 + (integration.integration_complexity * 0.5)
        
        # 新規性による調整
        novelty_factor = self._calculate_knowledge_novelty(update)
        
        return base_gain * complexity_factor * novelty_factor
    
    def _calculate_knowledge_novelty(self, update: KnowledgeUpdate) -> float:
        """知識新規性計算"""
        # 既存の類似更新をチェック
        similar_updates = 0
        total_updates = len(self.knowledge_integrations)
        
        for integration in self.knowledge_integrations.values():
            if integration.target_entity == update.target_entity:
                similar_updates += 1
        
        if total_updates == 0:
            return 1.0
        
        novelty = 1.0 - (similar_updates / total_updates)
        return max(novelty, 0.1)
    
    def _calculate_knowledge_similarity(self, knowledge1: Any, knowledge2: Any) -> float:
        """知識類似度計算"""
        try:
            # 文字列の場合
            if isinstance(knowledge1, str) and isinstance(knowledge2, str):
                # 簡単な文字列類似度計算
                common_words = set(knowledge1.lower().split()) & set(knowledge2.lower().split())
                total_words = set(knowledge1.lower().split()) | set(knowledge2.lower().split())
                
                if not total_words:
                    return 0.0
                
                return len(common_words) / len(total_words)
            
            # その他の場合は基本的な比較
            return 1.0 if knowledge1 == knowledge2 else 0.0
            
        except Exception:
            return 0.0
    
    def _update_learning_patterns(self, update: KnowledgeUpdate, integration_result: Dict[str, Any]):
        """学習パターン更新"""
        pattern_type = self._classify_learning_pattern(update, integration_result)
        pattern_id = f"pattern_{pattern_type}"
        
        if pattern_id in self.learning_patterns:
            pattern = self.learning_patterns[pattern_id]
            pattern.usage_frequency += 1
            pattern.success_rate = (
                (pattern.success_rate * (pattern.usage_frequency - 1) + 
                 (1.0 if integration_result["success"] else 0.0)) / pattern.usage_frequency
            )
            pattern.last_applied = datetime.now().isoformat()
        else:
            # 新しいパターン作成
            self.learning_patterns[pattern_id] = LearningPattern(
                pattern_id=pattern_id,
                pattern_type=pattern_type,
                learning_rate=self.default_learning_rate,
                retention_rate=0.9,
                adaptation_speed=0.5,
                effectiveness_score=1.0 if integration_result["success"] else 0.0,
                usage_frequency=1,
                last_applied=datetime.now().isoformat(),
                success_rate=1.0 if integration_result["success"] else 0.0
            )
    
    def _classify_learning_pattern(self, update: KnowledgeUpdate, integration_result: Dict[str, Any]) -> str:
        """学習パターン分類"""
        if integration_result.get("conflict_resolved"):
            return "conflict_resolution"
        elif update.update_type == "add":
            return "incremental_addition"
        elif update.update_type == "modify":
            return "adaptive_modification"
        elif update.confidence > 0.8:
            return "high_confidence_learning"
        else:
            return "exploratory_learning"
    
    def _adapt_learning_model(self, processing_results: Dict[str, Any]):
        """適応学習モデル更新"""
        if not self.adaptive_model:
            return
        
        # パフォーマンスメトリクス更新
        if processing_results["processed_updates"] > 0:
            success_rate = processing_results["successful_integrations"] / processing_results["processed_updates"]
            
            # 指数移動平均で更新
            alpha = 0.1
            self.adaptive_model.performance_metrics["accuracy"] = (
                (1 - alpha) * self.adaptive_model.performance_metrics["accuracy"] + 
                alpha * success_rate
            )
        
        # 学習パラメータ適応
        if self.adaptive_model.performance_metrics["accuracy"] < 0.7:
            # 精度が低い場合、学習率を下げる
            self.adaptive_model.learning_parameters["base_learning_rate"] *= 0.95
            self.adaptive_model.current_strategy = "conservative"
        elif self.adaptive_model.performance_metrics["accuracy"] > 0.9:
            # 精度が高い場合、探索率を上げる
            self.adaptive_model.learning_parameters["exploration_rate"] = min(
                self.adaptive_model.learning_parameters["exploration_rate"] * 1.05, 0.3
            )
            self.adaptive_model.current_strategy = "aggressive"
        
        # 適応履歴記録
        adaptation_record = {
            "timestamp": datetime.now().isoformat(),
            "performance_snapshot": copy.deepcopy(self.adaptive_model.performance_metrics),
            "parameter_changes": {},
            "trigger": "processing_results"
        }
        
        self.adaptive_model.adaptation_history.append(adaptation_record)
        self.adaptive_model.last_updated = datetime.now().isoformat()
    
    def end_learning_session(self) -> Dict[str, Any]:
        """学習セッション終了"""
        if not self.current_session:
            return {"error": "アクティブなセッションがありません"}
        
        self.current_session.end_time = datetime.now().isoformat()
        
        # セッション統計計算
        session_stats = {
            "session_id": self.current_session.session_id,
            "duration_minutes": self._calculate_session_duration(),
            "updates_processed": self.current_session.updates_processed,
            "knowledge_gained": self.current_session.knowledge_gained,
            "learning_efficiency": self.current_session.learning_efficiency,
            "conflicts_resolved": self.current_session.conflicts_resolved,
            "error_count": len(self.current_session.errors_encountered)
        }
        
        # セッション保存
        self.learning_sessions.append(self.current_session)
        self.current_session = None
        
        # データ保存
        self._save_data()
        
        print(f"[増分学習] セッション終了: {session_stats}")
        return session_stats
    
    def _calculate_session_duration(self) -> float:
        """セッション継続時間計算（分）"""
        if not self.current_session or not self.current_session.end_time:
            return 0.0
        
        start = datetime.fromisoformat(self.current_session.start_time)
        end = datetime.fromisoformat(self.current_session.end_time)
        
        return (end - start).total_seconds() / 60.0
    
    def get_learning_analytics(self) -> Dict[str, Any]:
        """学習分析レポート生成"""
        analytics = {
            "learning_patterns": {},
            "session_statistics": {},
            "knowledge_integration_stats": {},
            "adaptive_model_status": {},
            "performance_trends": {}
        }
        
        # 学習パターン分析
        analytics["learning_patterns"] = {
            "total_patterns": len(self.learning_patterns),
            "most_effective_pattern": self._get_most_effective_pattern(),
            "pattern_usage_distribution": self._get_pattern_usage_distribution()
        }
        
        # セッション統計
        if self.learning_sessions:
            session_data = list(self.learning_sessions)
            analytics["session_statistics"] = {
                "total_sessions": len(session_data),
                "average_efficiency": mean([s.learning_efficiency for s in session_data if s.learning_efficiency > 0]),
                "total_knowledge_gained": sum([s.knowledge_gained for s in session_data]),
                "average_updates_per_session": mean([s.updates_processed for s in session_data])
            }
        
        # 知識統合統計
        analytics["knowledge_integration_stats"] = {
            "total_integrations": len(self.knowledge_integrations),
            "integration_methods": self._get_integration_method_distribution(),
            "average_confidence": mean([ki.confidence for ki in self.knowledge_integrations.values()]),
            "pending_validations": len([ki for ki in self.knowledge_integrations.values() 
                                      if ki.validation_status == "pending"])
        }
        
        # 適応モデル状態
        if self.adaptive_model:
            analytics["adaptive_model_status"] = {
                "current_strategy": self.adaptive_model.current_strategy,
                "performance_metrics": self.adaptive_model.performance_metrics,
                "learning_parameters": self.adaptive_model.learning_parameters,
                "adaptation_count": len(self.adaptive_model.adaptation_history)
            }
        
        return analytics
    
    def _get_most_effective_pattern(self) -> Optional[str]:
        """最も効果的な学習パターン取得"""
        if not self.learning_patterns:
            return None
        
        best_pattern = max(self.learning_patterns.values(), 
                          key=lambda p: p.effectiveness_score * p.success_rate)
        return best_pattern.pattern_id
    
    def _get_pattern_usage_distribution(self) -> Dict[str, int]:
        """パターン使用分布取得"""
        return {pattern_id: pattern.usage_frequency 
                for pattern_id, pattern in self.learning_patterns.items()}
    
    def _get_integration_method_distribution(self) -> Dict[str, int]:
        """統合方法分布取得"""
        distribution = defaultdict(int)
        for integration in self.knowledge_integrations.values():
            distribution[integration.integration_method] += 1
        return dict(distribution)

def main():
    """テスト実行"""
    print("=== 増分学習エンジンテスト ===")
    
    engine = IncrementalLearningEngine()
    
    # 学習セッション開始
    session_id = engine.start_learning_session("test")
    
    # テスト用の知識更新
    test_updates = [
        KnowledgeUpdate(
            update_id="test_update_1",
            target_entity="test_entity",
            update_type="add",
            old_value=None,
            new_value="新しい情報",
            confidence=0.8,
            supporting_evidence=["evidence1"],
            impact_score=0.7,
            applied_at=None
        )
    ]
    
    # 知識更新処理
    results = engine.process_knowledge_updates(test_updates)
    print(f"処理結果: {results}")
    
    # セッション終了
    session_stats = engine.end_learning_session()
    print(f"セッション統計: {session_stats}")
    
    # 分析レポート
    analytics = engine.get_learning_analytics()
    print(f"学習分析: {analytics}")

if __name__ == "__main__":
    main()
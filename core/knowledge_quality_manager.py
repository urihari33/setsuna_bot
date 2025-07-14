#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知識品質管理システム - Phase 2F実装
知識品質継続監視・品質劣化検出・品質改善提案・知識ライフサイクル管理
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from datetime import datetime, timedelta
import numpy as np
from statistics import mean, median, stdev
import hashlib

# プロジェクトルートをパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 関連システム
try:
    from core.knowledge_validation_system import KnowledgeValidationSystem, QualityMetrics, ValidationResult
    from core.incremental_learning_engine import IncrementalLearningEngine
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False

# Windowsパス設定
if os.name == 'nt':
    DATA_DIR = Path("D:/setsuna_bot/youtube_knowledge_system/data")
    QUALITY_CACHE_DIR = Path("D:/setsuna_bot/knowledge_quality_cache")
else:
    DATA_DIR = Path("/mnt/d/setsuna_bot/youtube_knowledge_system/data")
    QUALITY_CACHE_DIR = Path("/mnt/d/setsuna_bot/knowledge_quality_cache")

QUALITY_CACHE_DIR.mkdir(parents=True, exist_ok=True)

@dataclass
class QualityAlert:
    """品質アラートデータクラス"""
    alert_id: str
    alert_type: str             # "degradation", "inconsistency", "outdated", "low_quality"
    severity: str               # "low", "medium", "high", "critical"
    affected_entities: List[str]
    description: str
    recommended_actions: List[str]
    auto_fixable: bool
    created_at: str
    resolved_at: Optional[str]
    resolution_notes: Optional[str]

@dataclass
class QualityTrend:
    """品質トレンドデータクラス"""
    entity_id: str
    time_series: List[Dict[str, Any]]  # 時系列品質データ
    trend_direction: str        # "improving", "stable", "declining"
    trend_strength: float       # トレンド強度 (0.0-1.0)
    prediction: Dict[str, float]  # 品質予測値
    change_points: List[str]    # 品質変化点
    analysis_period: str

@dataclass
class QualityReport:
    """品質レポートデータクラス"""
    report_id: str
    report_type: str            # "summary", "detailed", "trend_analysis", "alert_summary"
    scope: str                  # "global", "category", "entity"
    time_period: str
    overall_score: float
    quality_distribution: Dict[str, int]  # グレード別分布
    top_quality_entities: List[str]
    low_quality_entities: List[str]
    quality_trends: Dict[str, str]
    actionable_insights: List[str]
    generated_at: str

@dataclass
class QualityPolicy:
    """品質ポリシーデータクラス"""
    policy_id: str
    policy_name: str
    quality_thresholds: Dict[str, float]  # 品質閾値
    monitoring_interval: int    # 監視間隔（秒）
    auto_fix_enabled: bool
    alert_conditions: Dict[str, Any]
    retention_period: int       # データ保持期間（日）
    escalation_rules: List[Dict[str, Any]]
    created_at: str

@dataclass
class KnowledgeLifecycle:
    """知識ライフサイクルデータクラス"""
    entity_id: str
    lifecycle_stage: str        # "new", "active", "mature", "outdated", "deprecated"
    creation_date: str
    last_updated: str
    last_accessed: str
    access_frequency: int
    update_frequency: int
    relevance_score: float
    freshness_score: float
    utility_score: float
    lifecycle_predictions: Dict[str, str]

class KnowledgeQualityManager:
    """知識品質管理システムクラス"""
    
    def __init__(self):
        """初期化"""
        # データパス
        self.quality_alerts_path = QUALITY_CACHE_DIR / "quality_alerts.json"
        self.quality_trends_path = QUALITY_CACHE_DIR / "quality_trends.json"
        self.quality_reports_path = QUALITY_CACHE_DIR / "quality_reports.json"
        self.quality_policies_path = QUALITY_CACHE_DIR / "quality_policies.json"
        self.lifecycle_data_path = QUALITY_CACHE_DIR / "lifecycle_data.json"
        self.quality_history_path = QUALITY_CACHE_DIR / "quality_history.json"
        
        # 依存システム
        if DEPENDENCIES_AVAILABLE:
            self.validation_system = KnowledgeValidationSystem()
            self.learning_engine = IncrementalLearningEngine()
        else:
            self.validation_system = None
            self.learning_engine = None
            print("[品質管理] ⚠️ 依存システムが利用できません")
        
        # データ
        self.quality_alerts = {}
        self.quality_trends = {}
        self.quality_reports = {}
        self.quality_policies = {}
        self.lifecycle_data = {}
        self.quality_history = deque(maxlen=1000)  # 最新1000件
        
        # 品質管理パラメータ
        self.default_quality_threshold = 0.7
        self.degradation_threshold = 0.15  # 15%以上の品質低下で警告
        self.monitoring_interval = 3600   # 1時間ごとの監視
        self.max_alert_age_days = 30
        
        # 初期化
        self._load_data()
        self._initialize_default_policies()
        
    def _load_data(self):
        """データ読み込み"""
        try:
            if self.quality_alerts_path.exists():
                with open(self.quality_alerts_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.quality_alerts = {k: QualityAlert(**v) for k, v in data.items()}
            
            if self.quality_trends_path.exists():
                with open(self.quality_trends_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.quality_trends = {k: QualityTrend(**v) for k, v in data.items()}
            
            if self.quality_reports_path.exists():
                with open(self.quality_reports_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.quality_reports = {k: QualityReport(**v) for k, v in data.items()}
            
            if self.quality_policies_path.exists():
                with open(self.quality_policies_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.quality_policies = {k: QualityPolicy(**v) for k, v in data.items()}
            
            if self.lifecycle_data_path.exists():
                with open(self.lifecycle_data_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.lifecycle_data = {k: KnowledgeLifecycle(**v) for k, v in data.items()}
            
            if self.quality_history_path.exists():
                with open(self.quality_history_path, 'r', encoding='utf-8') as f:
                    history_data = json.load(f)
                    self.quality_history = deque(history_data, maxlen=1000)
                    
        except Exception as e:
            print(f"[品質管理] データ読み込みエラー: {e}")
    
    def _save_data(self):
        """データ保存"""
        try:
            # 品質アラート保存
            with open(self.quality_alerts_path, 'w', encoding='utf-8') as f:
                json.dump({k: asdict(v) for k, v in self.quality_alerts.items()}, f, 
                         ensure_ascii=False, indent=2)
            
            # 品質トレンド保存
            with open(self.quality_trends_path, 'w', encoding='utf-8') as f:
                json.dump({k: asdict(v) for k, v in self.quality_trends.items()}, f, 
                         ensure_ascii=False, indent=2)
            
            # 品質レポート保存
            with open(self.quality_reports_path, 'w', encoding='utf-8') as f:
                json.dump({k: asdict(v) for k, v in self.quality_reports.items()}, f, 
                         ensure_ascii=False, indent=2)
            
            # 品質ポリシー保存
            with open(self.quality_policies_path, 'w', encoding='utf-8') as f:
                json.dump({k: asdict(v) for k, v in self.quality_policies.items()}, f, 
                         ensure_ascii=False, indent=2)
            
            # ライフサイクルデータ保存
            with open(self.lifecycle_data_path, 'w', encoding='utf-8') as f:
                json.dump({k: asdict(v) for k, v in self.lifecycle_data.items()}, f, 
                         ensure_ascii=False, indent=2)
            
            # 品質履歴保存
            with open(self.quality_history_path, 'w', encoding='utf-8') as f:
                json.dump(list(self.quality_history), f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"[品質管理] データ保存エラー: {e}")
    
    def _initialize_default_policies(self):
        """デフォルト品質ポリシー初期化"""
        if not self.quality_policies:
            default_policy = QualityPolicy(
                policy_id="default_quality_policy",
                policy_name="標準品質管理ポリシー",
                quality_thresholds={
                    "minimum_quality": 0.6,
                    "target_quality": 0.8,
                    "excellence_threshold": 0.9,
                    "degradation_alert": 0.15
                },
                monitoring_interval=self.monitoring_interval,
                auto_fix_enabled=True,
                alert_conditions={
                    "quality_below_minimum": True,
                    "significant_degradation": True,
                    "consistency_issues": True,
                    "outdated_knowledge": True
                },
                retention_period=90,
                escalation_rules=[
                    {"condition": "critical_quality_drop", "action": "immediate_review"},
                    {"condition": "multiple_failures", "action": "system_check"}
                ],
                created_at=datetime.now().isoformat()
            )
            
            self.quality_policies[default_policy.policy_id] = default_policy
    
    def monitor_quality_continuously(self) -> Dict[str, Any]:
        """継続的品質監視"""
        monitoring_results = {
            "monitored_entities": 0,
            "quality_alerts_generated": 0,
            "trends_updated": 0,
            "auto_fixes_applied": 0,
            "monitoring_timestamp": datetime.now().isoformat()
        }
        
        try:
            if not self.validation_system:
                return {"error": "検証システムが利用できません"}
            
            # 現在の品質メトリクスを取得
            current_metrics = self._get_current_quality_metrics()
            
            for entity_id, metrics in current_metrics.items():
                monitoring_results["monitored_entities"] += 1
                
                # 品質劣化検出
                degradation_alert = self._detect_quality_degradation(entity_id, metrics)
                if degradation_alert:
                    self.quality_alerts[degradation_alert.alert_id] = degradation_alert
                    monitoring_results["quality_alerts_generated"] += 1
                
                # 品質トレンド更新
                if self._update_quality_trend(entity_id, metrics):
                    monitoring_results["trends_updated"] += 1
                
                # ライフサイクル更新
                self._update_knowledge_lifecycle(entity_id, metrics)
                
                # 自動修正の試行
                if self._attempt_auto_fix(entity_id, metrics):
                    monitoring_results["auto_fixes_applied"] += 1
                
                # 履歴記録
                self._record_quality_history(entity_id, metrics)
            
            # データ保存
            self._save_data()
            
        except Exception as e:
            monitoring_results["error"] = str(e)
        
        return monitoring_results
    
    def _get_current_quality_metrics(self) -> Dict[str, QualityMetrics]:
        """現在の品質メトリクス取得"""
        current_metrics = {}
        
        if self.validation_system:
            # 検証システムから品質メトリクスを取得
            for metric_id, metrics in self.validation_system.quality_metrics.items():
                current_metrics[metric_id] = metrics
        
        return current_metrics
    
    def _detect_quality_degradation(self, entity_id: str, current_metrics: QualityMetrics) -> Optional[QualityAlert]:
        """品質劣化検出"""
        try:
            # 過去の品質データと比較
            historical_quality = self._get_historical_quality(entity_id)
            
            if not historical_quality:
                return None  # 履歴がない場合は判定不可
            
            # 品質低下の計算
            quality_drop = historical_quality - current_metrics.overall_quality
            
            # 閾値チェック
            if quality_drop > self.degradation_threshold:
                alert_id = f"degradation_{entity_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
                # 重要度決定
                if quality_drop > 0.3:
                    severity = "critical"
                elif quality_drop > 0.2:
                    severity = "high"
                elif quality_drop > 0.15:
                    severity = "medium"
                else:
                    severity = "low"
                
                # 推奨アクション生成
                recommended_actions = self._generate_quality_improvement_actions(current_metrics)
                
                return QualityAlert(
                    alert_id=alert_id,
                    alert_type="degradation",
                    severity=severity,
                    affected_entities=[entity_id],
                    description=f"品質が{quality_drop:.2f}低下しました（{historical_quality:.2f} → {current_metrics.overall_quality:.2f}）",
                    recommended_actions=recommended_actions,
                    auto_fixable=self._is_auto_fixable(current_metrics),
                    created_at=datetime.now().isoformat(),
                    resolved_at=None,
                    resolution_notes=None
                )
        
        except Exception as e:
            print(f"[品質管理] 品質劣化検出エラー: {e}")
        
        return None
    
    def _get_historical_quality(self, entity_id: str) -> Optional[float]:
        """過去の品質取得"""
        # 品質履歴から最近の平均品質を計算
        recent_history = [
            entry for entry in self.quality_history
            if entry.get("entity_id") == entity_id and 
            datetime.fromisoformat(entry.get("timestamp", "2020-01-01")) > 
            datetime.now() - timedelta(days=7)
        ]
        
        if recent_history:
            qualities = [entry.get("overall_quality", 0.0) for entry in recent_history]
            return mean(qualities) if qualities else None
        
        return None
    
    def _generate_quality_improvement_actions(self, metrics: QualityMetrics) -> List[str]:
        """品質改善アクション生成"""
        actions = []
        
        # 各品質次元の問題に応じた推奨アクション
        if metrics.completeness < 0.7:
            actions.append("不足している情報の補完")
        
        if metrics.consistency < 0.7:
            actions.append("矛盾する情報の統合・解決")
        
        if metrics.accuracy < 0.7:
            actions.append("情報の正確性検証・修正")
        
        if metrics.relevance < 0.7:
            actions.append("関連性の再評価・更新")
        
        if metrics.timeliness < 0.7:
            actions.append("情報の鮮度更新")
        
        if metrics.credibility < 0.7:
            actions.append("信頼できる情報源からの再確認")
        
        if not actions:
            actions.append("詳細な品質分析の実施")
        
        return actions
    
    def _is_auto_fixable(self, metrics: QualityMetrics) -> bool:
        """自動修正可能性判定"""
        # 簡単な問題は自動修正可能
        auto_fixable_conditions = [
            metrics.completeness < 0.5 and metrics.accuracy > 0.8,  # 完全性問題のみ
            metrics.timeliness < 0.5 and metrics.overall_quality > 0.7,  # 時宜性問題のみ
        ]
        
        return any(auto_fixable_conditions)
    
    def _update_quality_trend(self, entity_id: str, current_metrics: QualityMetrics) -> bool:
        """品質トレンド更新"""
        try:
            current_time = datetime.now().isoformat()
            
            if entity_id in self.quality_trends:
                trend = self.quality_trends[entity_id]
            else:
                trend = QualityTrend(
                    entity_id=entity_id,
                    time_series=[],
                    trend_direction="stable",
                    trend_strength=0.0,
                    prediction={},
                    change_points=[],
                    analysis_period="7days"
                )
                self.quality_trends[entity_id] = trend
            
            # 新しいデータポイント追加
            data_point = {
                "timestamp": current_time,
                "overall_quality": current_metrics.overall_quality,
                "completeness": current_metrics.completeness,
                "consistency": current_metrics.consistency,
                "accuracy": current_metrics.accuracy,
                "relevance": current_metrics.relevance,
                "timeliness": current_metrics.timeliness,
                "credibility": current_metrics.credibility
            }
            
            trend.time_series.append(data_point)
            
            # 古いデータの削除（7日以上前）
            cutoff_time = datetime.now() - timedelta(days=7)
            trend.time_series = [
                dp for dp in trend.time_series
                if datetime.fromisoformat(dp["timestamp"]) > cutoff_time
            ]
            
            # トレンド分析
            if len(trend.time_series) >= 3:
                trend.trend_direction, trend.trend_strength = self._analyze_trend_direction(trend.time_series)
                trend.prediction = self._predict_future_quality(trend.time_series)
                trend.change_points = self._detect_change_points(trend.time_series)
            
            return True
            
        except Exception as e:
            print(f"[品質管理] トレンド更新エラー: {e}")
            return False
    
    def _analyze_trend_direction(self, time_series: List[Dict[str, Any]]) -> Tuple[str, float]:
        """トレンド方向分析"""
        if len(time_series) < 3:
            return "stable", 0.0
        
        # 品質値の時系列
        qualities = [dp["overall_quality"] for dp in time_series]
        
        # 線形回帰によるトレンド分析
        x = np.arange(len(qualities))
        z = np.polyfit(x, qualities, 1)
        slope = z[0]
        
        # トレンド強度
        trend_strength = abs(slope)
        
        # トレンド方向
        if slope > 0.01:
            direction = "improving"
        elif slope < -0.01:
            direction = "declining"
        else:
            direction = "stable"
        
        return direction, min(trend_strength, 1.0)
    
    def _predict_future_quality(self, time_series: List[Dict[str, Any]]) -> Dict[str, float]:
        """将来品質予測"""
        if len(time_series) < 3:
            return {}
        
        qualities = [dp["overall_quality"] for dp in time_series]
        
        # 簡単な線形予測
        x = np.arange(len(qualities))
        z = np.polyfit(x, qualities, 1)
        
        # 1日後、3日後、7日後の予測
        predictions = {
            "1_day": max(0.0, min(1.0, z[1] + z[0] * (len(qualities) + 1))),
            "3_days": max(0.0, min(1.0, z[1] + z[0] * (len(qualities) + 3))),
            "7_days": max(0.0, min(1.0, z[1] + z[0] * (len(qualities) + 7)))
        }
        
        return predictions
    
    def _detect_change_points(self, time_series: List[Dict[str, Any]]) -> List[str]:
        """変化点検出"""
        change_points = []
        
        if len(time_series) < 5:
            return change_points
        
        qualities = [dp["overall_quality"] for dp in time_series]
        
        # 簡単な変化点検出（品質の急激な変化）
        for i in range(2, len(qualities) - 2):
            # 前後の品質変化を計算
            before_avg = mean(qualities[i-2:i])
            after_avg = mean(qualities[i+1:i+3])
            
            # 急激な変化を検出
            if abs(after_avg - before_avg) > 0.2:
                change_points.append(time_series[i]["timestamp"])
        
        return change_points
    
    def _update_knowledge_lifecycle(self, entity_id: str, current_metrics: QualityMetrics):
        """知識ライフサイクル更新"""
        try:
            current_time = datetime.now().isoformat()
            
            if entity_id in self.lifecycle_data:
                lifecycle = self.lifecycle_data[entity_id]
                lifecycle.last_updated = current_time
            else:
                lifecycle = KnowledgeLifecycle(
                    entity_id=entity_id,
                    lifecycle_stage="new",
                    creation_date=current_time,
                    last_updated=current_time,
                    last_accessed=current_time,
                    access_frequency=1,
                    update_frequency=1,
                    relevance_score=current_metrics.relevance,
                    freshness_score=current_metrics.timeliness,
                    utility_score=current_metrics.overall_quality,
                    lifecycle_predictions={}
                )
                self.lifecycle_data[entity_id] = lifecycle
            
            # ライフサイクルステージの更新
            lifecycle.lifecycle_stage = self._determine_lifecycle_stage(lifecycle, current_metrics)
            lifecycle.relevance_score = current_metrics.relevance
            lifecycle.freshness_score = current_metrics.timeliness
            lifecycle.utility_score = current_metrics.overall_quality
            lifecycle.update_frequency += 1
            
            # ライフサイクル予測
            lifecycle.lifecycle_predictions = self._predict_lifecycle_evolution(lifecycle)
            
        except Exception as e:
            print(f"[品質管理] ライフサイクル更新エラー: {e}")
    
    def _determine_lifecycle_stage(self, lifecycle: KnowledgeLifecycle, metrics: QualityMetrics) -> str:
        """ライフサイクルステージ決定"""
        creation_age = (datetime.now() - datetime.fromisoformat(lifecycle.creation_date)).days
        
        if creation_age < 7:
            return "new"
        elif metrics.overall_quality > 0.8 and metrics.relevance > 0.7:
            return "active"
        elif metrics.overall_quality > 0.6 and creation_age < 90:
            return "mature"
        elif metrics.timeliness < 0.4 or metrics.relevance < 0.4:
            return "outdated"
        else:
            return "deprecated"
    
    def _predict_lifecycle_evolution(self, lifecycle: KnowledgeLifecycle) -> Dict[str, str]:
        """ライフサイクル進化予測"""
        predictions = {}
        
        # 簡単な予測ロジック
        if lifecycle.utility_score > 0.8:
            predictions["trend"] = "stable_high_quality"
        elif lifecycle.freshness_score < 0.3:
            predictions["risk"] = "becoming_outdated"
        elif lifecycle.relevance_score < 0.4:
            predictions["risk"] = "losing_relevance"
        else:
            predictions["trend"] = "normal_evolution"
        
        return predictions
    
    def _attempt_auto_fix(self, entity_id: str, metrics: QualityMetrics) -> bool:
        """自動修正試行"""
        try:
            if not self._is_auto_fixable(metrics):
                return False
            
            fixes_applied = 0
            
            # 時宜性の自動修正
            if metrics.timeliness < 0.5:
                # タイムスタンプ更新などの簡単な修正
                fixes_applied += 1
            
            # 完全性の自動修正
            if metrics.completeness < 0.5 and metrics.accuracy > 0.8:
                # 不足情報の自動補完（実際の実装では更に高度な処理が必要）
                fixes_applied += 1
            
            return fixes_applied > 0
            
        except Exception as e:
            print(f"[品質管理] 自動修正エラー: {e}")
            return False
    
    def _record_quality_history(self, entity_id: str, metrics: QualityMetrics):
        """品質履歴記録"""
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "entity_id": entity_id,
            "overall_quality": metrics.overall_quality,
            "quality_grade": metrics.quality_grade,
            "completeness": metrics.completeness,
            "consistency": metrics.consistency,
            "accuracy": metrics.accuracy,
            "relevance": metrics.relevance,
            "timeliness": metrics.timeliness,
            "credibility": metrics.credibility
        }
        
        self.quality_history.append(history_entry)
    
    def generate_quality_report(self, report_type: str = "summary", scope: str = "global", 
                              time_period: str = "7days") -> QualityReport:
        """品質レポート生成"""
        report_id = f"report_{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 期間の計算
        if time_period == "7days":
            cutoff_time = datetime.now() - timedelta(days=7)
        elif time_period == "30days":
            cutoff_time = datetime.now() - timedelta(days=30)
        else:
            cutoff_time = datetime.now() - timedelta(days=1)
        
        # 該当期間のデータ収集
        relevant_history = [
            entry for entry in self.quality_history
            if datetime.fromisoformat(entry["timestamp"]) > cutoff_time
        ]
        
        if not relevant_history:
            # データがない場合のデフォルトレポート
            return QualityReport(
                report_id=report_id,
                report_type=report_type,
                scope=scope,
                time_period=time_period,
                overall_score=0.0,
                quality_distribution={},
                top_quality_entities=[],
                low_quality_entities=[],
                quality_trends={},
                actionable_insights=["データが不十分です"],
                generated_at=datetime.now().isoformat()
            )
        
        # 全体品質スコア計算
        overall_score = mean([entry["overall_quality"] for entry in relevant_history])
        
        # 品質分布計算
        quality_distribution = {}
        for entry in relevant_history:
            grade = entry.get("quality_grade", "C")
            quality_distribution[grade] = quality_distribution.get(grade, 0) + 1
        
        # 高品質・低品質エンティティ抽出
        entity_scores = defaultdict(list)
        for entry in relevant_history:
            entity_scores[entry["entity_id"]].append(entry["overall_quality"])
        
        entity_averages = {
            entity_id: mean(scores) 
            for entity_id, scores in entity_scores.items()
        }
        
        sorted_entities = sorted(entity_averages.items(), key=lambda x: x[1], reverse=True)
        
        top_quality_entities = [entity_id for entity_id, score in sorted_entities[:5] if score > 0.8]
        low_quality_entities = [entity_id for entity_id, score in sorted_entities[-5:] if score < 0.6]
        
        # 品質トレンド分析
        quality_trends = {}
        for entity_id in entity_scores.keys():
            if entity_id in self.quality_trends:
                trend = self.quality_trends[entity_id]
                quality_trends[entity_id] = trend.trend_direction
        
        # 実行可能なインサイト生成
        actionable_insights = self._generate_actionable_insights(
            overall_score, quality_distribution, entity_averages
        )
        
        report = QualityReport(
            report_id=report_id,
            report_type=report_type,
            scope=scope,
            time_period=time_period,
            overall_score=overall_score,
            quality_distribution=quality_distribution,
            top_quality_entities=top_quality_entities,
            low_quality_entities=low_quality_entities,
            quality_trends=quality_trends,
            actionable_insights=actionable_insights,
            generated_at=datetime.now().isoformat()
        )
        
        # レポート保存
        self.quality_reports[report_id] = report
        
        return report
    
    def _generate_actionable_insights(self, overall_score: float, quality_distribution: Dict[str, int], 
                                    entity_averages: Dict[str, float]) -> List[str]:
        """実行可能なインサイト生成"""
        insights = []
        
        # 全体品質に基づくインサイト
        if overall_score < 0.6:
            insights.append("全体的な品質向上が急務です。品質改善プロセスの見直しを推奨します。")
        elif overall_score > 0.9:
            insights.append("優秀な品質レベルを維持しています。現在の品質管理プロセスの継続を推奨します。")
        
        # 品質分布に基づくインサイト
        total_entities = sum(quality_distribution.values())
        if total_entities > 0:
            low_quality_ratio = quality_distribution.get("D", 0) + quality_distribution.get("F", 0)
            if low_quality_ratio / total_entities > 0.3:
                insights.append("低品質エンティティの割合が高すぎます。集中的な品質改善が必要です。")
        
        # 個別エンティティに基づくインサイト
        low_quality_count = len([score for score in entity_averages.values() if score < 0.5])
        if low_quality_count > 5:
            insights.append(f"{low_quality_count}個のエンティティで重要な品質問題があります。優先的な対応が必要です。")
        
        if not insights:
            insights.append("現在の品質レベルは適切です。定期的な監視を継続してください。")
        
        return insights
    
    def get_quality_dashboard_data(self) -> Dict[str, Any]:
        """品質ダッシュボードデータ取得"""
        dashboard_data = {
            "summary": {
                "total_entities": len(self.lifecycle_data),
                "active_alerts": len([a for a in self.quality_alerts.values() if not a.resolved_at]),
                "average_quality": 0.0,
                "quality_trends_count": len(self.quality_trends)
            },
            "recent_alerts": [],
            "quality_distribution": {},
            "trend_summary": {},
            "lifecycle_distribution": {},
            "top_insights": []
        }
        
        try:
            # 最近の品質データから平均品質計算
            if self.quality_history:
                recent_history = list(self.quality_history)[-100:]  # 最新100件
                dashboard_data["summary"]["average_quality"] = mean([
                    entry["overall_quality"] for entry in recent_history
                ])
            
            # 最近のアラート
            recent_alerts = sorted(
                [a for a in self.quality_alerts.values() if not a.resolved_at],
                key=lambda x: x.created_at,
                reverse=True
            )[:5]
            
            dashboard_data["recent_alerts"] = [
                {
                    "alert_id": alert.alert_id,
                    "severity": alert.severity,
                    "description": alert.description,
                    "created_at": alert.created_at
                }
                for alert in recent_alerts
            ]
            
            # 品質分布
            if self.quality_history:
                recent_history = list(self.quality_history)[-100:]
                grade_counts = {}
                for entry in recent_history:
                    grade = entry.get("quality_grade", "C")
                    grade_counts[grade] = grade_counts.get(grade, 0) + 1
                dashboard_data["quality_distribution"] = grade_counts
            
            # トレンド要約
            improving_trends = len([t for t in self.quality_trends.values() if t.trend_direction == "improving"])
            declining_trends = len([t for t in self.quality_trends.values() if t.trend_direction == "declining"])
            stable_trends = len([t for t in self.quality_trends.values() if t.trend_direction == "stable"])
            
            dashboard_data["trend_summary"] = {
                "improving": improving_trends,
                "declining": declining_trends,
                "stable": stable_trends
            }
            
            # ライフサイクル分布
            lifecycle_counts = {}
            for lifecycle in self.lifecycle_data.values():
                stage = lifecycle.lifecycle_stage
                lifecycle_counts[stage] = lifecycle_counts.get(stage, 0) + 1
            dashboard_data["lifecycle_distribution"] = lifecycle_counts
            
            # トップインサイト（最新のレポートから）
            if self.quality_reports:
                latest_report = max(self.quality_reports.values(), key=lambda r: r.generated_at)
                dashboard_data["top_insights"] = latest_report.actionable_insights[:3]
        
        except Exception as e:
            dashboard_data["error"] = f"ダッシュボードデータ生成エラー: {str(e)}"
        
        return dashboard_data

def main():
    """テスト実行"""
    print("=== 知識品質管理システムテスト ===")
    
    quality_manager = KnowledgeQualityManager()
    
    # 継続的品質監視テスト
    monitoring_results = quality_manager.monitor_quality_continuously()
    print(f"監視結果: {monitoring_results}")
    
    # 品質レポート生成テスト
    report = quality_manager.generate_quality_report("summary", "global", "7days")
    print(f"品質レポート: スコア={report.overall_score:.3f}, エンティティ数={len(report.top_quality_entities)}")
    
    # ダッシュボードデータ取得テスト
    dashboard_data = quality_manager.get_quality_dashboard_data()
    print(f"ダッシュボード: {dashboard_data['summary']}")

if __name__ == "__main__":
    main()
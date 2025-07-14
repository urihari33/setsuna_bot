#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知識検証システム - Phase 2E実装
学習知識の信頼性検証・品質評価・統合前検証システム
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
from datetime import datetime, timedelta
import re
import hashlib
from statistics import mean, median, stdev
import difflib

# プロジェクトルートをパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 関連システム
try:
    from core.real_time_knowledge_updater import NewInformation, KnowledgeUpdate
    from core.incremental_learning_engine import KnowledgeIntegration
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False

# Windowsパス設定
if os.name == 'nt':
    DATA_DIR = Path("D:/setsuna_bot/youtube_knowledge_system/data")
    VALIDATION_CACHE_DIR = Path("D:/setsuna_bot/knowledge_validation_cache")
else:
    DATA_DIR = Path("/mnt/d/setsuna_bot/youtube_knowledge_system/data")
    VALIDATION_CACHE_DIR = Path("/mnt/d/setsuna_bot/knowledge_validation_cache")

VALIDATION_CACHE_DIR.mkdir(parents=True, exist_ok=True)

@dataclass
class ValidationRule:
    """検証ルールデータクラス"""
    rule_id: str
    rule_name: str
    rule_type: str               # "consistency", "reliability", "completeness", "accuracy"
    validation_logic: str        # 検証ロジックの説明
    weight: float               # ルールの重み
    threshold: float            # 合格閾値
    error_tolerance: float      # エラー許容度
    is_active: bool
    last_updated: str

@dataclass
class ValidationResult:
    """検証結果データクラス"""
    validation_id: str
    target_id: str              # 検証対象ID
    target_type: str            # "information", "update", "integration"
    validation_score: float     # 総合検証スコア (0.0-1.0)
    rule_results: Dict[str, float]  # ルール別結果
    passed: bool
    confidence_level: str       # "high", "medium", "low"
    validation_issues: List[str]  # 検出された問題
    recommendations: List[str]    # 改善推奨事項
    validated_at: str
    validator_notes: Optional[str]

@dataclass
class QualityMetrics:
    """品質メトリクスデータクラス"""
    target_id: str
    completeness: float         # 完全性
    consistency: float          # 一貫性
    accuracy: float            # 正確性
    relevance: float           # 関連性
    timeliness: float          # 時宜性
    credibility: float         # 信頼性
    overall_quality: float     # 総合品質
    quality_grade: str         # "A", "B", "C", "D", "F"
    calculated_at: str

@dataclass
class ValidationPolicy:
    """検証ポリシーデータクラス"""
    policy_id: str
    policy_name: str
    target_types: List[str]     # 適用対象タイプ
    required_rules: List[str]   # 必須ルール
    optional_rules: List[str]   # オプションルール
    minimum_score: float        # 最低合格スコア
    escalation_threshold: float # エスカレーション閾値
    auto_approval_threshold: float  # 自動承認閾値
    review_required: bool
    created_at: str

class KnowledgeValidationSystem:
    """知識検証システムクラス"""
    
    def __init__(self):
        """初期化"""
        # データパス
        self.validation_rules_path = VALIDATION_CACHE_DIR / "validation_rules.json"
        self.validation_results_path = VALIDATION_CACHE_DIR / "validation_results.json"
        self.quality_metrics_path = VALIDATION_CACHE_DIR / "quality_metrics.json"
        self.validation_policies_path = VALIDATION_CACHE_DIR / "validation_policies.json"
        self.validation_log_path = VALIDATION_CACHE_DIR / "validation_log.json"
        self.knowledge_db_path = DATA_DIR / "unified_knowledge_db.json"
        
        # データ
        self.validation_rules = {}
        self.validation_results = {}
        self.quality_metrics = {}
        self.validation_policies = {}
        self.validation_log = []
        self.knowledge_db = {}
        
        # 検証パラメータ
        self.default_confidence_threshold = 0.7
        self.consistency_tolerance = 0.15
        self.completeness_weight = 0.25
        self.accuracy_weight = 0.30
        self.relevance_weight = 0.20
        self.timeliness_weight = 0.15
        self.credibility_weight = 0.10
        
        # 初期化
        self._load_data()
        self._initialize_default_rules()
        self._initialize_default_policies()
        
    def _load_data(self):
        """データ読み込み"""
        try:
            if self.validation_rules_path.exists():
                with open(self.validation_rules_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.validation_rules = {k: ValidationRule(**v) for k, v in data.items()}
            
            if self.validation_results_path.exists():
                with open(self.validation_results_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.validation_results = {k: ValidationResult(**v) for k, v in data.items()}
            
            if self.quality_metrics_path.exists():
                with open(self.quality_metrics_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.quality_metrics = {k: QualityMetrics(**v) for k, v in data.items()}
            
            if self.validation_policies_path.exists():
                with open(self.validation_policies_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.validation_policies = {k: ValidationPolicy(**v) for k, v in data.items()}
            
            if self.validation_log_path.exists():
                with open(self.validation_log_path, 'r', encoding='utf-8') as f:
                    self.validation_log = json.load(f)
            
            if self.knowledge_db_path.exists():
                with open(self.knowledge_db_path, 'r', encoding='utf-8') as f:
                    self.knowledge_db = json.load(f)
                    
        except Exception as e:
            print(f"[知識検証] データ読み込みエラー: {e}")
    
    def _save_data(self):
        """データ保存"""
        try:
            # 検証ルール保存
            with open(self.validation_rules_path, 'w', encoding='utf-8') as f:
                json.dump({k: asdict(v) for k, v in self.validation_rules.items()}, f, 
                         ensure_ascii=False, indent=2)
            
            # 検証結果保存
            with open(self.validation_results_path, 'w', encoding='utf-8') as f:
                json.dump({k: asdict(v) for k, v in self.validation_results.items()}, f, 
                         ensure_ascii=False, indent=2)
            
            # 品質メトリクス保存
            with open(self.quality_metrics_path, 'w', encoding='utf-8') as f:
                json.dump({k: asdict(v) for k, v in self.quality_metrics.items()}, f, 
                         ensure_ascii=False, indent=2)
            
            # 検証ポリシー保存
            with open(self.validation_policies_path, 'w', encoding='utf-8') as f:
                json.dump({k: asdict(v) for k, v in self.validation_policies.items()}, f, 
                         ensure_ascii=False, indent=2)
            
            # 検証ログ保存
            with open(self.validation_log_path, 'w', encoding='utf-8') as f:
                json.dump(self.validation_log[-1000:], f, ensure_ascii=False, indent=2)  # 最新1000件
                
        except Exception as e:
            print(f"[知識検証] データ保存エラー: {e}")
    
    def _initialize_default_rules(self):
        """デフォルト検証ルール初期化"""
        if not self.validation_rules:
            default_rules = [
                {
                    "rule_id": "consistency_check",
                    "rule_name": "一貫性チェック",
                    "rule_type": "consistency",
                    "validation_logic": "既存知識との矛盾がないかチェック",
                    "weight": 0.3,
                    "threshold": 0.7,
                    "error_tolerance": 0.1,
                    "is_active": True
                },
                {
                    "rule_id": "reliability_check",
                    "rule_name": "信頼性チェック",
                    "rule_type": "reliability",
                    "validation_logic": "情報源の信頼性と証拠の質をチェック",
                    "weight": 0.25,
                    "threshold": 0.6,
                    "error_tolerance": 0.15,
                    "is_active": True
                },
                {
                    "rule_id": "completeness_check",
                    "rule_name": "完全性チェック",
                    "rule_type": "completeness",
                    "validation_logic": "必要な情報が不足していないかチェック",
                    "weight": 0.2,
                    "threshold": 0.5,
                    "error_tolerance": 0.2,
                    "is_active": True
                },
                {
                    "rule_id": "accuracy_check",
                    "rule_name": "正確性チェック",
                    "rule_type": "accuracy",
                    "validation_logic": "情報の正確性と事実性をチェック",
                    "weight": 0.25,
                    "threshold": 0.8,
                    "error_tolerance": 0.05,
                    "is_active": True
                }
            ]
            
            for rule_data in default_rules:
                rule_data["last_updated"] = datetime.now().isoformat()
                rule = ValidationRule(**rule_data)
                self.validation_rules[rule.rule_id] = rule
    
    def _initialize_default_policies(self):
        """デフォルト検証ポリシー初期化"""
        if not self.validation_policies:
            default_policies = [
                {
                    "policy_id": "standard_validation",
                    "policy_name": "標準検証ポリシー",
                    "target_types": ["information", "update"],
                    "required_rules": ["consistency_check", "reliability_check"],
                    "optional_rules": ["completeness_check", "accuracy_check"],
                    "minimum_score": 0.6,
                    "escalation_threshold": 0.4,
                    "auto_approval_threshold": 0.9,
                    "review_required": False
                },
                {
                    "policy_id": "strict_validation",
                    "policy_name": "厳格検証ポリシー",
                    "target_types": ["integration"],
                    "required_rules": ["consistency_check", "reliability_check", "accuracy_check"],
                    "optional_rules": ["completeness_check"],
                    "minimum_score": 0.8,
                    "escalation_threshold": 0.6,
                    "auto_approval_threshold": 0.95,
                    "review_required": True
                }
            ]
            
            for policy_data in default_policies:
                policy_data["created_at"] = datetime.now().isoformat()
                policy = ValidationPolicy(**policy_data)
                self.validation_policies[policy.policy_id] = policy
    
    def validate_new_information(self, info: NewInformation) -> ValidationResult:
        """新情報検証"""
        validation_id = f"val_info_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{info.info_id[:8]}"
        
        # 適用ポリシー決定
        policy = self._get_applicable_policy("information")
        
        # ルール実行
        rule_results = {}
        validation_issues = []
        recommendations = []
        
        # 必須ルール検証
        for rule_id in policy.required_rules:
            if rule_id in self.validation_rules and self.validation_rules[rule_id].is_active:
                result = self._execute_validation_rule(rule_id, info, "information")
                rule_results[rule_id] = result["score"]
                validation_issues.extend(result.get("issues", []))
                recommendations.extend(result.get("recommendations", []))
        
        # オプションルール検証
        for rule_id in policy.optional_rules:
            if rule_id in self.validation_rules and self.validation_rules[rule_id].is_active:
                result = self._execute_validation_rule(rule_id, info, "information")
                rule_results[rule_id] = result["score"]
                validation_issues.extend(result.get("issues", []))
                recommendations.extend(result.get("recommendations", []))
        
        # 総合スコア計算
        validation_score = self._calculate_total_validation_score(rule_results)
        
        # 合格判定
        passed = validation_score >= policy.minimum_score
        
        # 信頼度レベル決定
        confidence_level = self._determine_confidence_level(validation_score)
        
        # 検証結果作成
        validation_result = ValidationResult(
            validation_id=validation_id,
            target_id=info.info_id,
            target_type="information",
            validation_score=validation_score,
            rule_results=rule_results,
            passed=passed,
            confidence_level=confidence_level,
            validation_issues=validation_issues,
            recommendations=recommendations,
            validated_at=datetime.now().isoformat(),
            validator_notes=None
        )
        
        # 結果保存
        self.validation_results[validation_id] = validation_result
        
        # ログ記録
        self._log_validation_event(validation_result, policy)
        
        return validation_result
    
    def validate_knowledge_update(self, update: KnowledgeUpdate) -> ValidationResult:
        """知識更新検証"""
        validation_id = f"val_update_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{update.update_id[:8]}"
        
        # 適用ポリシー決定
        policy = self._get_applicable_policy("update")
        
        # ルール実行
        rule_results = {}
        validation_issues = []
        recommendations = []
        
        # 必須ルール検証
        for rule_id in policy.required_rules:
            if rule_id in self.validation_rules and self.validation_rules[rule_id].is_active:
                result = self._execute_validation_rule(rule_id, update, "update")
                rule_results[rule_id] = result["score"]
                validation_issues.extend(result.get("issues", []))
                recommendations.extend(result.get("recommendations", []))
        
        # オプションルール検証
        for rule_id in policy.optional_rules:
            if rule_id in self.validation_rules and self.validation_rules[rule_id].is_active:
                result = self._execute_validation_rule(rule_id, update, "update")
                rule_results[rule_id] = result["score"]
                validation_issues.extend(result.get("issues", []))
                recommendations.extend(result.get("recommendations", []))
        
        # 総合スコア計算
        validation_score = self._calculate_total_validation_score(rule_results)
        
        # 合格判定
        passed = validation_score >= policy.minimum_score
        
        # 信頼度レベル決定
        confidence_level = self._determine_confidence_level(validation_score)
        
        # 検証結果作成
        validation_result = ValidationResult(
            validation_id=validation_id,
            target_id=update.update_id,
            target_type="update",
            validation_score=validation_score,
            rule_results=rule_results,
            passed=passed,
            confidence_level=confidence_level,
            validation_issues=validation_issues,
            recommendations=recommendations,
            validated_at=datetime.now().isoformat(),
            validator_notes=None
        )
        
        # 結果保存
        self.validation_results[validation_id] = validation_result
        
        # ログ記録
        self._log_validation_event(validation_result, policy)
        
        return validation_result
    
    def _get_applicable_policy(self, target_type: str) -> ValidationPolicy:
        """適用可能ポリシー取得"""
        for policy in self.validation_policies.values():
            if target_type in policy.target_types:
                return policy
        
        # デフォルトポリシー返却
        return list(self.validation_policies.values())[0]
    
    def _execute_validation_rule(self, rule_id: str, target: Any, target_type: str) -> Dict[str, Any]:
        """検証ルール実行"""
        rule = self.validation_rules[rule_id]
        result = {
            "score": 0.0,
            "issues": [],
            "recommendations": []
        }
        
        try:
            if rule.rule_type == "consistency":
                result = self._check_consistency(target, target_type)
            elif rule.rule_type == "reliability":
                result = self._check_reliability(target, target_type)
            elif rule.rule_type == "completeness":
                result = self._check_completeness(target, target_type)
            elif rule.rule_type == "accuracy":
                result = self._check_accuracy(target, target_type)
            
            # ルール重み適用
            result["score"] *= rule.weight
            
        except Exception as e:
            result["issues"].append(f"ルール実行エラー: {str(e)}")
            result["score"] = 0.0
        
        return result
    
    def _check_consistency(self, target: Any, target_type: str) -> Dict[str, Any]:
        """一貫性チェック"""
        result = {
            "score": 1.0,
            "issues": [],
            "recommendations": []
        }
        
        try:
            if target_type == "information" and hasattr(target, 'content'):
                # 既存知識との矛盾チェック
                conflicts = self._find_knowledge_conflicts(target.content)
                
                if conflicts:
                    conflict_severity = len(conflicts) / 10.0  # 最大10個の矛盾を想定
                    result["score"] = max(0.0, 1.0 - conflict_severity)
                    result["issues"].extend([f"知識矛盾: {c}" for c in conflicts[:3]])
                    result["recommendations"].append("既存知識との整合性確認が必要")
            
            elif target_type == "update" and hasattr(target, 'new_value'):
                # 更新の一貫性チェック
                if hasattr(target, 'old_value') and target.old_value:
                    similarity = self._calculate_content_similarity(str(target.old_value), str(target.new_value))
                    if similarity < 0.1:  # 極端に異なる場合
                        result["score"] *= 0.7
                        result["issues"].append("更新内容が既存値と大幅に異なります")
            
        except Exception as e:
            result["issues"].append(f"一貫性チェックエラー: {str(e)}")
            result["score"] = 0.5
        
        return result
    
    def _check_reliability(self, target: Any, target_type: str) -> Dict[str, Any]:
        """信頼性チェック"""
        result = {
            "score": 1.0,
            "issues": [],
            "recommendations": []
        }
        
        try:
            # 信頼度スコア取得
            if hasattr(target, 'confidence'):
                base_confidence = target.confidence
            else:
                base_confidence = 0.5
            
            # 証拠の質評価
            evidence_quality = 1.0
            if hasattr(target, 'supporting_evidence'):
                evidence_count = len(target.supporting_evidence) if target.supporting_evidence else 0
                evidence_quality = min(evidence_count / 3.0, 1.0)  # 3個以上で最高評価
            
            # 情報源評価
            source_reliability = 1.0
            if hasattr(target, 'source_context') and target.source_context:
                # 簡単な情報源信頼性評価
                if "公式" in target.source_context or "official" in target.source_context.lower():
                    source_reliability = 1.0
                elif "wiki" in target.source_context.lower():
                    source_reliability = 0.8
                elif "blog" in target.source_context.lower():
                    source_reliability = 0.6
                else:
                    source_reliability = 0.7
            
            # 総合信頼性計算
            result["score"] = (base_confidence * 0.5 + evidence_quality * 0.3 + source_reliability * 0.2)
            
            if result["score"] < 0.6:
                result["issues"].append("信頼性が低い情報です")
                result["recommendations"].append("追加の証拠収集を推奨")
            
        except Exception as e:
            result["issues"].append(f"信頼性チェックエラー: {str(e)}")
            result["score"] = 0.5
        
        return result
    
    def _check_completeness(self, target: Any, target_type: str) -> Dict[str, Any]:
        """完全性チェック"""
        result = {
            "score": 1.0,
            "issues": [],
            "recommendations": []
        }
        
        try:
            # 必須フィールドチェック
            required_fields = []
            if target_type == "information":
                required_fields = ["content", "info_type", "confidence"]
            elif target_type == "update":
                required_fields = ["target_entity", "update_type", "new_value"]
            
            missing_fields = []
            for field in required_fields:
                if not hasattr(target, field) or getattr(target, field) is None:
                    missing_fields.append(field)
            
            if missing_fields:
                completeness_score = 1.0 - (len(missing_fields) / len(required_fields))
                result["score"] = max(0.0, completeness_score)
                result["issues"].extend([f"必須フィールド不足: {field}" for field in missing_fields])
                result["recommendations"].append("不足情報の補完が必要")
            
            # 内容の完全性チェック
            if hasattr(target, 'content'):
                content_length = len(str(target.content))
                if content_length < 10:
                    result["score"] *= 0.7
                    result["issues"].append("内容が不十分です")
                elif content_length < 5:
                    result["score"] *= 0.4
                    result["issues"].append("内容が極めて不十分です")
            
        except Exception as e:
            result["issues"].append(f"完全性チェックエラー: {str(e)}")
            result["score"] = 0.5
        
        return result
    
    def _check_accuracy(self, target: Any, target_type: str) -> Dict[str, Any]:
        """正確性チェック"""
        result = {
            "score": 1.0,
            "issues": [],
            "recommendations": []
        }
        
        try:
            # 基本的な正確性チェック
            accuracy_indicators = []
            
            # 信頼度による正確性推定
            if hasattr(target, 'confidence'):
                accuracy_indicators.append(target.confidence)
            
            # 検証方法による正確性推定
            if hasattr(target, 'extraction_method'):
                method_reliability = {
                    "pattern_matching": 0.7,
                    "entity_recognition": 0.8,
                    "manual_extraction": 0.9,
                    "automated_extraction": 0.6
                }
                method_score = method_reliability.get(target.extraction_method, 0.5)
                accuracy_indicators.append(method_score)
            
            # 関連エンティティ数による正確性推定
            if hasattr(target, 'related_entities'):
                entity_count = len(target.related_entities) if target.related_entities else 0
                entity_score = min(entity_count / 5.0, 1.0)  # 5個以上で最高評価
                accuracy_indicators.append(entity_score)
            
            # 総合正確性計算
            if accuracy_indicators:
                result["score"] = mean(accuracy_indicators)
            
            # 内容の妥当性チェック
            if hasattr(target, 'content') and target.content:
                content_issues = self._validate_content_format(str(target.content))
                if content_issues:
                    result["score"] *= 0.8
                    result["issues"].extend(content_issues)
            
            if result["score"] < 0.7:
                result["recommendations"].append("正確性向上のための追加検証を推奨")
        
        except Exception as e:
            result["issues"].append(f"正確性チェックエラー: {str(e)}")
            result["score"] = 0.5
        
        return result
    
    def _find_knowledge_conflicts(self, content: str) -> List[str]:
        """知識矛盾検出"""
        conflicts = []
        
        try:
            # 既存知識との簡単な矛盾チェック
            # 実際の実装では、より高度な自然言語処理が必要
            
            # 既存の動画データとの矛盾チェック
            if "videos" in self.knowledge_db:
                for video in self.knowledge_db["videos"][:10]:  # 最初の10件をチェック
                    video_title = video.get("title", "")
                    if video_title and content:
                        # 簡単な矛盾検出（実際にはより高度な手法が必要）
                        if "ない" in content and video_title in content:
                            conflicts.append(f"動画「{video_title}」の存在と矛盾する可能性")
        
        except Exception:
            pass  # エラーは無視
        
        return conflicts
    
    def _calculate_content_similarity(self, content1: str, content2: str) -> float:
        """内容類似度計算"""
        try:
            # 簡単な類似度計算（実際にはより高度な手法が必要）
            common_words = set(content1.lower().split()) & set(content2.lower().split())
            total_words = set(content1.lower().split()) | set(content2.lower().split())
            
            if not total_words:
                return 1.0 if content1 == content2 else 0.0
            
            return len(common_words) / len(total_words)
        
        except Exception:
            return 0.0
    
    def _validate_content_format(self, content: str) -> List[str]:
        """内容形式検証"""
        issues = []
        
        try:
            # 基本的な形式チェック
            if not content.strip():
                issues.append("内容が空です")
            elif len(content) > 10000:
                issues.append("内容が長すぎます")
            
            # 不適切な文字チェック
            if re.search(r'[^\w\s\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF\u002D\u0021-\u007E]', content):
                issues.append("不適切な文字が含まれています")
            
        except Exception:
            issues.append("内容形式の検証中にエラーが発生しました")
        
        return issues
    
    def _calculate_total_validation_score(self, rule_results: Dict[str, float]) -> float:
        """総合検証スコア計算"""
        if not rule_results:
            return 0.0
        
        total_weight = 0.0
        weighted_sum = 0.0
        
        for rule_id, score in rule_results.items():
            if rule_id in self.validation_rules:
                weight = self.validation_rules[rule_id].weight
                weighted_sum += score * weight
                total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def _determine_confidence_level(self, validation_score: float) -> str:
        """信頼度レベル決定"""
        if validation_score >= 0.9:
            return "high"
        elif validation_score >= 0.7:
            return "medium"
        else:
            return "low"
    
    def _log_validation_event(self, validation_result: ValidationResult, policy: ValidationPolicy):
        """検証イベントログ記録"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "validation_id": validation_result.validation_id,
            "target_type": validation_result.target_type,
            "policy_used": policy.policy_id,
            "validation_score": validation_result.validation_score,
            "passed": validation_result.passed,
            "confidence_level": validation_result.confidence_level,
            "issues_count": len(validation_result.validation_issues)
        }
        
        self.validation_log.append(log_entry)
    
    def generate_quality_metrics(self, target_id: str, target_type: str) -> QualityMetrics:
        """品質メトリクス生成"""
        # 検証結果から品質メトリクス計算
        relevant_results = [
            result for result in self.validation_results.values()
            if result.target_id == target_id and result.target_type == target_type
        ]
        
        if not relevant_results:
            # デフォルト品質メトリクス
            return QualityMetrics(
                target_id=target_id,
                completeness=0.5,
                consistency=0.5,
                accuracy=0.5,
                relevance=0.5,
                timeliness=0.5,
                credibility=0.5,
                overall_quality=0.5,
                quality_grade="C",
                calculated_at=datetime.now().isoformat()
            )
        
        # 最新の検証結果を使用
        latest_result = max(relevant_results, key=lambda r: r.validated_at)
        
        # 各次元のスコア計算
        completeness = latest_result.rule_results.get("completeness_check", 0.5)
        consistency = latest_result.rule_results.get("consistency_check", 0.5)
        accuracy = latest_result.rule_results.get("accuracy_check", 0.5)
        reliability = latest_result.rule_results.get("reliability_check", 0.5)
        
        # その他の次元は推定値
        relevance = latest_result.validation_score  # 検証スコアから推定
        timeliness = 1.0  # 新しい情報なので最大値
        credibility = reliability
        
        # 総合品質計算
        overall_quality = (
            completeness * self.completeness_weight +
            consistency * 0.25 +
            accuracy * self.accuracy_weight +
            relevance * self.relevance_weight +
            timeliness * self.timeliness_weight +
            credibility * self.credibility_weight
        )
        
        # 品質グレード決定
        quality_grade = self._calculate_quality_grade(overall_quality)
        
        metrics = QualityMetrics(
            target_id=target_id,
            completeness=completeness,
            consistency=consistency,
            accuracy=accuracy,
            relevance=relevance,
            timeliness=timeliness,
            credibility=credibility,
            overall_quality=overall_quality,
            quality_grade=quality_grade,
            calculated_at=datetime.now().isoformat()
        )
        
        self.quality_metrics[target_id] = metrics
        return metrics
    
    def _calculate_quality_grade(self, overall_quality: float) -> str:
        """品質グレード計算"""
        if overall_quality >= 0.9:
            return "A"
        elif overall_quality >= 0.8:
            return "B"
        elif overall_quality >= 0.6:
            return "C"
        elif overall_quality >= 0.4:
            return "D"
        else:
            return "F"
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """検証サマリー取得"""
        if not self.validation_results:
            return {"message": "検証結果がありません"}
        
        results = list(self.validation_results.values())
        
        summary = {
            "total_validations": len(results),
            "passed_validations": len([r for r in results if r.passed]),
            "average_score": mean([r.validation_score for r in results]),
            "confidence_distribution": {
                "high": len([r for r in results if r.confidence_level == "high"]),
                "medium": len([r for r in results if r.confidence_level == "medium"]),
                "low": len([r for r in results if r.confidence_level == "low"])
            },
            "common_issues": self._get_common_issues(results),
            "validation_trends": self._analyze_validation_trends()
        }
        
        return summary
    
    def _get_common_issues(self, results: List[ValidationResult]) -> Dict[str, int]:
        """共通問題取得"""
        all_issues = []
        for result in results:
            all_issues.extend(result.validation_issues)
        
        issue_counter = Counter(all_issues)
        return dict(issue_counter.most_common(5))
    
    def _analyze_validation_trends(self) -> Dict[str, Any]:
        """検証トレンド分析"""
        if len(self.validation_log) < 2:
            return {"message": "十分なデータがありません"}
        
        recent_logs = self.validation_log[-30:]  # 最新30件
        
        trends = {
            "recent_pass_rate": len([log for log in recent_logs if log["passed"]]) / len(recent_logs),
            "average_recent_score": mean([log["validation_score"] for log in recent_logs]),
            "improvement_trend": "analyzing"  # 実際には時系列分析が必要
        }
        
        return trends

def main():
    """テスト実行"""
    print("=== 知識検証システムテスト ===")
    
    validator = KnowledgeValidationSystem()
    
    # テスト用新情報
    test_info = NewInformation(
        info_id="test_info_1",
        content="テスト情報内容",
        info_type="fact",
        confidence=0.8,
        source_context="テストコンテキスト",
        extraction_method="manual_extraction",
        related_entities=["entity1", "entity2"],
        validation_status="pending",
        detected_at=datetime.now().isoformat()
    )
    
    # 検証実行
    validation_result = validator.validate_new_information(test_info)
    print(f"検証結果: スコア={validation_result.validation_score:.3f}, 合格={validation_result.passed}")
    
    # 品質メトリクス生成
    quality_metrics = validator.generate_quality_metrics(test_info.info_id, "information")
    print(f"品質メトリクス: グレード={quality_metrics.quality_grade}, 総合品質={quality_metrics.overall_quality:.3f}")
    
    # 検証サマリー
    summary = validator.get_validation_summary()
    print(f"検証サマリー: {summary}")

if __name__ == "__main__":
    main()
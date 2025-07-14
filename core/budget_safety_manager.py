#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BudgetSafetyManager - Phase 2A-3
予算制限・コスト管理・安全停止システム
"""

import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from collections import defaultdict
import uuid

# Windows環境のパス設定
if os.name == 'nt':
    DATA_DIR = Path("D:/setsuna_bot/data/activity_knowledge/learning_budget")
else:
    DATA_DIR = Path("/mnt/d/setsuna_bot/data/activity_knowledge/learning_budget")

@dataclass
class BudgetConfig:
    """予算設定データクラス"""
    monthly_limit: float
    daily_limit: float
    session_limits: Dict[str, float]  # セッションタイプ別制限
    alert_thresholds: Dict[str, bool]  # アラート閾値設定
    auto_stop: Dict[str, bool]  # 自動停止設定
    
    def __post_init__(self):
        # デフォルト値設定
        if not self.session_limits:
            self.session_limits = {
                "light": 2.0,
                "standard": 5.0,
                "thorough": 10.0,
                "unlimited": 25.0
            }
        
        if not self.alert_thresholds:
            self.alert_thresholds = {
                "session_50percent": True,
                "session_80percent": True,
                "daily_80percent": True,
                "monthly_80percent": True
            }
        
        if not self.auto_stop:
            self.auto_stop = {
                "session_limit": True,
                "daily_limit": True,
                "monthly_limit": True
            }

@dataclass
class CostRecord:
    """コスト記録データクラス"""
    record_id: str
    session_id: str
    timestamp: datetime
    api_type: str  # "openai", "search", "news"
    operation: str  # "text_analysis", "web_search", "news_fetch"
    input_tokens: int
    output_tokens: int
    cost: float
    details: Dict[str, Any]

@dataclass
class BudgetAlert:
    """予算アラートデータクラス"""
    alert_id: str
    alert_type: str  # "session_threshold", "daily_threshold", "monthly_threshold"
    severity: str  # "warning", "critical", "emergency"
    timestamp: datetime
    current_usage: float
    limit: float
    percentage: float
    session_id: Optional[str] = None
    message: str = ""
    acknowledged: bool = False

class BudgetSafetyManager:
    """予算安全管理メインクラス"""
    
    def __init__(self):
        """初期化"""
        self.budget_dir = DATA_DIR
        self.budget_dir.mkdir(parents=True, exist_ok=True)
        
        # データファイル
        self.daily_usage_file = self.budget_dir / "daily_usage.json"
        self.monthly_budget_file = self.budget_dir / "monthly_budget.json"
        self.cost_history_file = self.budget_dir / "cost_history.json"
        
        # 予算設定
        self.budget_config = BudgetConfig(
            monthly_limit=200.0,
            daily_limit=25.0,
            session_limits={},
            alert_thresholds={},
            auto_stop={}
        )
        
        # 使用量追跡
        self.daily_usage: Dict[str, float] = {}  # 日付 -> 使用量
        self.session_usage: Dict[str, float] = {}  # セッションID -> 使用量
        self.cost_records: List[CostRecord] = []
        self.active_alerts: List[BudgetAlert] = []
        
        # コールバック
        self.alert_callbacks: List[Callable] = []
        self.stop_callbacks: List[Callable] = []
        
        # 最適化設定
        self.optimization_config = {
            "enable_batch_processing": True,
            "enable_cache_utilization": True,
            "enable_api_efficiency": True,
            "max_concurrent_sessions": 3,
            "cost_prediction_enabled": True
        }
        
        self._load_existing_data()
        
        print("[予算管理] ✅ BudgetSafetyManager初期化完了")
    
    def _load_existing_data(self):
        """既存データの読み込み"""
        try:
            # 月次予算設定読み込み
            if self.monthly_budget_file.exists():
                with open(self.monthly_budget_file, 'r', encoding='utf-8') as f:
                    budget_data = json.load(f)
                    if "budget_config" in budget_data:
                        config_data = budget_data["budget_config"]
                        self.budget_config = BudgetConfig(**config_data)
                    
                    if "usage_tracking" in budget_data:
                        usage_data = budget_data["usage_tracking"]
                        self.daily_usage = usage_data.get("daily_usage", {})
                
                print(f"[予算管理] 📊 予算設定読み込み: 月次${self.budget_config.monthly_limit}, 日次${self.budget_config.daily_limit}")
            
            # 日次使用量読み込み
            if self.daily_usage_file.exists():
                with open(self.daily_usage_file, 'r', encoding='utf-8') as f:
                    daily_data = json.load(f)
                    self.daily_usage.update(daily_data.get("daily_usage", {}))
            
            # コスト履歴読み込み
            if self.cost_history_file.exists():
                with open(self.cost_history_file, 'r', encoding='utf-8') as f:
                    cost_data = json.load(f)
                    for record_data in cost_data.get("cost_records", []):
                        record = CostRecord(
                            record_id=record_data["record_id"],
                            session_id=record_data["session_id"],
                            timestamp=datetime.fromisoformat(record_data["timestamp"]),
                            api_type=record_data["api_type"],
                            operation=record_data["operation"],
                            input_tokens=record_data["input_tokens"],
                            output_tokens=record_data["output_tokens"],
                            cost=record_data["cost"],
                            details=record_data["details"]
                        )
                        self.cost_records.append(record)
            
            print(f"[予算管理] 📈 履歴読み込み: {len(self.cost_records)}件のコスト記録")
            
        except Exception as e:
            print(f"[予算管理] ⚠️ データ読み込み失敗: {e}")
    
    def set_budget_limits(self,
                         monthly_limit: Optional[float] = None,
                         daily_limit: Optional[float] = None,
                         session_limits: Optional[Dict[str, float]] = None):
        """
        予算制限設定
        
        Args:
            monthly_limit: 月次制限
            daily_limit: 日次制限
            session_limits: セッション別制限
        """
        try:
            if monthly_limit is not None:
                self.budget_config.monthly_limit = monthly_limit
            
            if daily_limit is not None:
                self.budget_config.daily_limit = daily_limit
            
            if session_limits:
                self.budget_config.session_limits.update(session_limits)
            
            self._save_budget_config()
            
            print(f"[予算管理] ⚙️ 予算制限更新: 月次${self.budget_config.monthly_limit}, 日次${self.budget_config.daily_limit}")
            
        except Exception as e:
            print(f"[予算管理] ❌ 予算設定失敗: {e}")
    
    def add_alert_callback(self, callback: Callable):
        """アラートコールバック追加"""
        self.alert_callbacks.append(callback)
    
    def add_stop_callback(self, callback: Callable):
        """停止コールバック追加"""
        self.stop_callbacks.append(callback)
    
    def record_cost(self,
                   session_id: str,
                   api_type: str,
                   operation: str,
                   input_tokens: int,
                   output_tokens: int,
                   additional_cost: float = 0.0,
                   details: Dict[str, Any] = None) -> str:
        """
        コスト記録
        
        Args:
            session_id: セッションID
            api_type: APIタイプ
            operation: 操作種別
            input_tokens: 入力トークン数
            output_tokens: 出力トークン数
            additional_cost: 追加コスト
            details: 詳細情報
            
        Returns:
            コスト記録ID
        """
        try:
            # コスト計算
            cost = self._calculate_api_cost(api_type, input_tokens, output_tokens) + additional_cost
            
            # コスト記録作成
            record_id = f"cost_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            record = CostRecord(
                record_id=record_id,
                session_id=session_id,
                timestamp=datetime.now(),
                api_type=api_type,
                operation=operation,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cost=cost,
                details=details or {}
            )
            
            self.cost_records.append(record)
            
            # 使用量更新
            today = datetime.now().strftime("%Y-%m-%d")
            self.daily_usage[today] = self.daily_usage.get(today, 0.0) + cost
            self.session_usage[session_id] = self.session_usage.get(session_id, 0.0) + cost
            
            # 予算チェック
            self._check_budget_limits(session_id, cost)
            
            # データ保存
            self._save_cost_data()
            
            print(f"[予算管理] 💰 コスト記録: {session_id} ${cost:.4f} ({api_type}/{operation})")
            return record_id
            
        except Exception as e:
            print(f"[予算管理] ❌ コスト記録失敗: {e}")
            return ""
    
    def _calculate_api_cost(self, api_type: str, input_tokens: int, output_tokens: int) -> float:
        """APIコスト計算"""
        cost_rates = {
            "openai": {
                "input_rate": 0.01 / 1000,   # $0.01 per 1K input tokens
                "output_rate": 0.03 / 1000   # $0.03 per 1K output tokens
            },
            "search": {
                "per_query": 0.005  # $0.005 per query
            },
            "news": {
                "per_request": 0.001  # $0.001 per request
            }
        }
        
        if api_type == "openai":
            rates = cost_rates["openai"]
            return (input_tokens * rates["input_rate"]) + (output_tokens * rates["output_rate"])
        elif api_type == "search":
            return cost_rates["search"]["per_query"]
        elif api_type == "news":
            return cost_rates["news"]["per_request"]
        else:
            return 0.0
    
    def _check_budget_limits(self, session_id: str, new_cost: float):
        """予算制限チェック"""
        try:
            current_session_cost = self.session_usage.get(session_id, 0.0)
            today = datetime.now().strftime("%Y-%m-%d")
            current_daily_cost = self.daily_usage.get(today, 0.0)
            current_monthly_cost = self._get_monthly_usage()
            
            # セッション制限チェック
            session_limit = self._get_session_limit(session_id)
            if session_limit and current_session_cost > 0:
                session_percentage = (current_session_cost / session_limit) * 100
                
                if session_percentage >= 50 and self.budget_config.alert_thresholds.get("session_50percent"):
                    self._create_alert("session_threshold", "warning", session_id, 
                                     current_session_cost, session_limit, session_percentage)
                
                if session_percentage >= 80 and self.budget_config.alert_thresholds.get("session_80percent"):
                    self._create_alert("session_threshold", "critical", session_id,
                                     current_session_cost, session_limit, session_percentage)
                
                if session_percentage >= 100 and self.budget_config.auto_stop.get("session_limit"):
                    self._trigger_emergency_stop(session_id, "session_limit_exceeded", 
                                                current_session_cost, session_limit)
            
            # 日次制限チェック
            daily_percentage = (current_daily_cost / self.budget_config.daily_limit) * 100
            if daily_percentage >= 80 and self.budget_config.alert_thresholds.get("daily_80percent"):
                self._create_alert("daily_threshold", "critical", None,
                                 current_daily_cost, self.budget_config.daily_limit, daily_percentage)
            
            if daily_percentage >= 100 and self.budget_config.auto_stop.get("daily_limit"):
                self._trigger_emergency_stop(session_id, "daily_limit_exceeded",
                                            current_daily_cost, self.budget_config.daily_limit)
            
            # 月次制限チェック
            monthly_percentage = (current_monthly_cost / self.budget_config.monthly_limit) * 100
            if monthly_percentage >= 80 and self.budget_config.alert_thresholds.get("monthly_80percent"):
                self._create_alert("monthly_threshold", "critical", None,
                                 current_monthly_cost, self.budget_config.monthly_limit, monthly_percentage)
            
            if monthly_percentage >= 100 and self.budget_config.auto_stop.get("monthly_limit"):
                self._trigger_emergency_stop(session_id, "monthly_limit_exceeded",
                                            current_monthly_cost, self.budget_config.monthly_limit)
            
        except Exception as e:
            print(f"[予算管理] ❌ 予算チェック失敗: {e}")
    
    def _get_session_limit(self, session_id: str) -> Optional[float]:
        """セッション制限取得"""
        # セッション情報から制限タイプを取得（実装は後でセッション管理と連携）
        # 現在はデフォルト値を使用
        return self.budget_config.session_limits.get("standard", 5.0)
    
    def _get_monthly_usage(self) -> float:
        """月次使用量取得"""
        current_month = datetime.now().strftime("%Y-%m")
        monthly_total = 0.0
        
        for date_str, usage in self.daily_usage.items():
            if date_str.startswith(current_month):
                monthly_total += usage
        
        return monthly_total
    
    def _create_alert(self, alert_type: str, severity: str, session_id: Optional[str],
                     current_usage: float, limit: float, percentage: float):
        """アラート作成"""
        try:
            alert_id = f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            
            message_templates = {
                "session_threshold": f"セッション予算 {percentage:.1f}% 使用 (${current_usage:.2f}/${limit:.2f})",
                "daily_threshold": f"日次予算 {percentage:.1f}% 使用 (${current_usage:.2f}/${limit:.2f})",
                "monthly_threshold": f"月次予算 {percentage:.1f}% 使用 (${current_usage:.2f}/${limit:.2f})"
            }
            
            alert = BudgetAlert(
                alert_id=alert_id,
                alert_type=alert_type,
                severity=severity,
                timestamp=datetime.now(),
                current_usage=current_usage,
                limit=limit,
                percentage=percentage,
                session_id=session_id,
                message=message_templates.get(alert_type, "予算アラート")
            )
            
            self.active_alerts.append(alert)
            
            # コールバック通知
            for callback in self.alert_callbacks:
                try:
                    callback(alert)
                except Exception as e:
                    print(f"[予算管理] ⚠️ アラートコールバックエラー: {e}")
            
            severity_emoji = {"warning": "⚠️", "critical": "🚨", "emergency": "🆘"}
            print(f"[予算管理] {severity_emoji.get(severity, '💰')} {alert.message}")
            
        except Exception as e:
            print(f"[予算管理] ❌ アラート作成失敗: {e}")
    
    def _trigger_emergency_stop(self, session_id: str, reason: str, current_usage: float, limit: float):
        """緊急停止トリガー"""
        try:
            print(f"[予算管理] 🆘 緊急停止: {reason} (${current_usage:.2f}/${limit:.2f})")
            
            # 緊急停止アラート
            self._create_alert("emergency_stop", "emergency", session_id,
                             current_usage, limit, (current_usage / limit) * 100)
            
            # 停止コールバック実行
            for callback in self.stop_callbacks:
                try:
                    callback(session_id, reason, current_usage, limit)
                except Exception as e:
                    print(f"[予算管理] ⚠️ 停止コールバックエラー: {e}")
            
        except Exception as e:
            print(f"[予算管理] ❌ 緊急停止失敗: {e}")
    
    def predict_session_cost(self, session_config: Dict[str, Any]) -> Dict[str, float]:
        """
        セッションコスト予測
        
        Args:
            session_config: セッション設定
            
        Returns:
            コスト予測結果
        """
        try:
            theme = session_config.get("theme", "")
            learning_type = session_config.get("learning_type", "標準")
            depth_level = session_config.get("depth_level", 3)
            time_limit = session_config.get("time_limit", 1800)
            
            # 過去の類似セッションから予測
            similar_sessions = self._find_similar_sessions(theme, learning_type, depth_level)
            
            if similar_sessions:
                avg_cost = sum(session["total_cost"] for session in similar_sessions) / len(similar_sessions)
                cost_variance = max(session["total_cost"] for session in similar_sessions) - min(session["total_cost"] for session in similar_sessions)
            else:
                # デフォルト予測値
                base_cost_per_hour = {
                    "概要": 3.0,
                    "深掘り": 6.0,
                    "実用": 10.0
                }.get(learning_type, 5.0)
                
                depth_multiplier = 1.0 + (depth_level - 3) * 0.3
                time_factor = time_limit / 3600  # 時間単位
                
                avg_cost = base_cost_per_hour * depth_multiplier * time_factor
                cost_variance = avg_cost * 0.3
            
            prediction = {
                "estimated_cost": avg_cost,
                "min_cost": max(0.5, avg_cost - cost_variance / 2),
                "max_cost": avg_cost + cost_variance / 2,
                "confidence": 0.8 if similar_sessions else 0.6,
                "similar_sessions_count": len(similar_sessions)
            }
            
            print(f"[予算管理] 💡 コスト予測: ${prediction['estimated_cost']:.2f} (範囲: ${prediction['min_cost']:.2f}-${prediction['max_cost']:.2f})")
            return prediction
            
        except Exception as e:
            print(f"[予算管理] ❌ コスト予測失敗: {e}")
            return {"estimated_cost": 5.0, "min_cost": 2.0, "max_cost": 10.0, "confidence": 0.3}
    
    def _find_similar_sessions(self, theme: str, learning_type: str, depth_level: int) -> List[Dict]:
        """類似セッション検索"""
        # 簡易実装（実際はセッション履歴データベースと連携）
        return []
    
    def get_usage_summary(self, period: str = "today") -> Dict[str, Any]:
        """
        使用量サマリー取得
        
        Args:
            period: 期間 ("today", "week", "month")
            
        Returns:
            使用量サマリー
        """
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            current_month = datetime.now().strftime("%Y-%m")
            
            if period == "today":
                daily_cost = self.daily_usage.get(today, 0.0)
                daily_limit = self.budget_config.daily_limit
                
                return {
                    "period": "today",
                    "current_usage": daily_cost,
                    "limit": daily_limit,
                    "percentage": (daily_cost / daily_limit) * 100 if daily_limit > 0 else 0,
                    "remaining": max(0, daily_limit - daily_cost),
                    "status": self._get_usage_status(daily_cost, daily_limit)
                }
            
            elif period == "month":
                monthly_cost = self._get_monthly_usage()
                monthly_limit = self.budget_config.monthly_limit
                
                return {
                    "period": "month",
                    "current_usage": monthly_cost,
                    "limit": monthly_limit,
                    "percentage": (monthly_cost / monthly_limit) * 100 if monthly_limit > 0 else 0,
                    "remaining": max(0, monthly_limit - monthly_cost),
                    "status": self._get_usage_status(monthly_cost, monthly_limit),
                    "daily_average": monthly_cost / datetime.now().day,
                    "projected_monthly": (monthly_cost / datetime.now().day) * 30
                }
            
            elif period == "week":
                week_cost = self._get_weekly_usage()
                week_limit = self.budget_config.daily_limit * 7
                
                return {
                    "period": "week", 
                    "current_usage": week_cost,
                    "limit": week_limit,
                    "percentage": (week_cost / week_limit) * 100 if week_limit > 0 else 0,
                    "remaining": max(0, week_limit - week_cost),
                    "status": self._get_usage_status(week_cost, week_limit)
                }
            
        except Exception as e:
            print(f"[予算管理] ❌ 使用量サマリー取得失敗: {e}")
            return {"error": str(e)}
    
    def _get_weekly_usage(self) -> float:
        """週次使用量取得"""
        week_start = datetime.now() - timedelta(days=7)
        weekly_total = 0.0
        
        for date_str, usage in self.daily_usage.items():
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            if date_obj >= week_start:
                weekly_total += usage
        
        return weekly_total
    
    def get_budget_status(self) -> Dict[str, Any]:
        """予算状況の総合取得"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            current_daily_cost = self.daily_usage.get(today, 0.0)
            current_monthly_cost = self._get_monthly_usage()
            
            status = {
                "status": "normal",
                "daily_usage": current_daily_cost,
                "daily_limit": self.budget_config.daily_limit,
                "monthly_usage": current_monthly_cost,
                "monthly_limit": self.budget_config.monthly_limit,
                "active_alerts": len(self.active_alerts),
                "daily_percentage": (current_daily_cost / self.budget_config.daily_limit) * 100 if self.budget_config.daily_limit > 0 else 0,
                "monthly_percentage": (current_monthly_cost / self.budget_config.monthly_limit) * 100 if self.budget_config.monthly_limit > 0 else 0
            }
            
            # ステータス判定
            if status["daily_percentage"] >= 100 or status["monthly_percentage"] >= 100:
                status["status"] = "exceeded"
            elif status["daily_percentage"] >= 80 or status["monthly_percentage"] >= 80:
                status["status"] = "critical"
            elif status["daily_percentage"] >= 50 or status["monthly_percentage"] >= 50:
                status["status"] = "warning"
            
            return status
            
        except Exception as e:
            print(f"[予算管理] ❌ 予算状況取得失敗: {e}")
            return {
                "status": "error",
                "error": str(e),
                "daily_usage": 0.0,
                "daily_limit": 0.0,
                "monthly_usage": 0.0,
                "monthly_limit": 0.0,
                "active_alerts": 0,
                "daily_percentage": 0.0,
                "monthly_percentage": 0.0
            }
    
    def _get_usage_status(self, current: float, limit: float) -> str:
        """使用量ステータス判定"""
        if limit <= 0:
            return "unlimited"
        
        percentage = (current / limit) * 100
        
        if percentage >= 100:
            return "exceeded"
        elif percentage >= 80:
            return "critical"
        elif percentage >= 50:
            return "warning"
        else:
            return "normal"
    
    def get_cost_optimization_suggestions(self) -> List[Dict[str, Any]]:
        """コスト最適化提案"""
        suggestions = []
        
        try:
            # 最近の使用パターン分析
            recent_records = [r for r in self.cost_records 
                            if r.timestamp > datetime.now() - timedelta(days=7)]
            
            if not recent_records:
                return suggestions
            
            # API使用効率分析
            api_usage = defaultdict(list)
            for record in recent_records:
                api_usage[record.api_type].append(record.cost)
            
            # OpenAI API最適化提案
            if "openai" in api_usage:
                openai_costs = api_usage["openai"]
                avg_cost = sum(openai_costs) / len(openai_costs)
                
                if avg_cost > 0.5:
                    suggestions.append({
                        "type": "api_optimization",
                        "title": "GPT-4-turbo バッチ処理の活用",
                        "description": "複数のコンテンツを一括分析することで、API呼び出し回数を削減できます",
                        "potential_savings": avg_cost * 0.3,
                        "difficulty": "easy"
                    })
            
            # 検索API最適化提案
            if "search" in api_usage:
                search_costs = api_usage["search"]
                if len(search_costs) > 10:
                    suggestions.append({
                        "type": "search_optimization",
                        "title": "無料検索APIの優先使用",
                        "description": "DuckDuckGo等の無料APIを優先的に使用し、有料APIは重要な検索のみに制限",
                        "potential_savings": sum(search_costs) * 0.7,
                        "difficulty": "medium"
                    })
            
            # キャッシュ活用提案
            duplicate_operations = self._detect_duplicate_operations(recent_records)
            if duplicate_operations > 5:
                suggestions.append({
                    "type": "cache_optimization",
                    "title": "分析結果キャッシュの活用",
                    "description": "類似コンテンツの分析結果を再利用することで、重複処理を削減",
                    "potential_savings": sum(r.cost for r in recent_records) * 0.2,
                    "difficulty": "medium"
                })
            
            return suggestions
            
        except Exception as e:
            print(f"[予算管理] ❌ 最適化提案生成失敗: {e}")
            return []
    
    def _detect_duplicate_operations(self, records: List[CostRecord]) -> int:
        """重複操作検出"""
        operation_signatures = defaultdict(int)
        
        for record in records:
            # 操作のシグネチャ作成（簡易版）
            signature = f"{record.operation}_{record.input_tokens}_{record.output_tokens}"
            operation_signatures[signature] += 1
        
        # 重複カウント
        duplicates = sum(count - 1 for count in operation_signatures.values() if count > 1)
        return duplicates
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """アラート確認"""
        try:
            for alert in self.active_alerts:
                if alert.alert_id == alert_id:
                    alert.acknowledged = True
                    print(f"[予算管理] ✅ アラート確認: {alert_id}")
                    return True
            return False
        except Exception as e:
            print(f"[予算管理] ❌ アラート確認失敗: {e}")
            return False
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """アクティブアラート取得"""
        return [
            {
                "alert_id": alert.alert_id,
                "alert_type": alert.alert_type,
                "severity": alert.severity,
                "message": alert.message,
                "timestamp": alert.timestamp.isoformat(),
                "session_id": alert.session_id,
                "acknowledged": alert.acknowledged
            }
            for alert in self.active_alerts
            if not alert.acknowledged
        ]
    
    def get_budget_status(self) -> Dict[str, Any]:
        """予算状態取得"""
        try:
            today = datetime.now().date()
            current_month = today.strftime("%Y-%m")
            
            # 今日の使用量
            daily_usage = sum(
                record.cost for record in self.cost_records 
                if record.timestamp.date() == today
            )
            
            # 今月の使用量
            monthly_usage = sum(
                record.cost for record in self.cost_records 
                if record.timestamp.strftime("%Y-%m") == current_month
            )
            
            return {
                "status": "active",
                "daily_usage": daily_usage,
                "daily_limit": self.budget_config.daily_limit,
                "daily_remaining": max(0, self.budget_config.daily_limit - daily_usage),
                "monthly_usage": monthly_usage,
                "monthly_limit": self.budget_config.monthly_limit,
                "monthly_remaining": max(0, self.budget_config.monthly_limit - monthly_usage),
                "active_alerts": len(self.active_alerts),
                "total_cost_records": len(self.cost_records)
            }
        except Exception as e:
            print(f"[予算管理] ❌ 予算状態取得失敗: {e}")
            return {"status": "error", "error": str(e)}
    
    def _save_budget_config(self):
        """予算設定保存"""
        try:
            budget_data = {
                "budget_period": datetime.now().strftime("%Y-%m"),
                "budget_config": asdict(self.budget_config),
                "usage_tracking": {
                    "current_month_total": self._get_monthly_usage(),
                    "daily_usage": self.daily_usage,
                    "session_usage": list(self.session_usage.items())[:10]  # 最新10セッション
                },
                "cost_optimization": self._get_optimization_stats(),
                "last_updated": datetime.now().isoformat()
            }
            
            with open(self.monthly_budget_file, 'w', encoding='utf-8') as f:
                json.dump(budget_data, f, ensure_ascii=False, indent=2, default=str)
                
        except Exception as e:
            print(f"[予算管理] ❌ 予算設定保存失敗: {e}")
    
    def _save_cost_data(self):
        """コスト履歴保存"""
        try:
            # 最新1000件のみ保存
            recent_records = self.cost_records[-1000:]
            
            cost_data = {
                "cost_records": [asdict(record) for record in recent_records],
                "total_records": len(self.cost_records),
                "last_updated": datetime.now().isoformat()
            }
            
            with open(self.cost_history_file, 'w', encoding='utf-8') as f:
                json.dump(cost_data, f, ensure_ascii=False, indent=2, default=str)
                
        except Exception as e:
            print(f"[予算管理] ❌ コスト履歴保存失敗: {e}")
    
    def _get_optimization_stats(self) -> Dict[str, Any]:
        """最適化統計"""
        return {
            "total_savings": 0.0,  # 実装時に計算
            "optimization_methods": {
                "batch_processing": 0.0,
                "cache_utilization": 0.0,
                "api_efficiency": 0.0
            },
            "efficiency_trends": {
                "average_session_efficiency": 0.42,
                "improving_trend": True
            }
        }
    
    def reset_daily_usage(self):
        """日次使用量リセット"""
        today = datetime.now().strftime("%Y-%m-%d")
        if today in self.daily_usage:
            del self.daily_usage[today]
        print(f"[予算管理] 🔄 日次使用量リセット: {today}")
    
    def export_cost_report(self, period_days: int = 30) -> Dict[str, Any]:
        """コストレポート出力"""
        try:
            cutoff_date = datetime.now() - timedelta(days=period_days)
            period_records = [r for r in self.cost_records if r.timestamp > cutoff_date]
            
            # API別集計
            api_breakdown = defaultdict(float)
            operation_breakdown = defaultdict(float)
            
            for record in period_records:
                api_breakdown[record.api_type] += record.cost
                operation_breakdown[record.operation] += record.cost
            
            report = {
                "period": f"{period_days}日間",
                "total_cost": sum(record.cost for record in period_records),
                "total_records": len(period_records),
                "api_breakdown": dict(api_breakdown),
                "operation_breakdown": dict(operation_breakdown),
                "daily_average": sum(record.cost for record in period_records) / period_days,
                "generated_at": datetime.now().isoformat()
            }
            
            print(f"[予算管理] 📊 コストレポート生成: {period_days}日間")
            return report
            
        except Exception as e:
            print(f"[予算管理] ❌ レポート生成失敗: {e}")
            return {"error": str(e)}


# テスト用コード
if __name__ == "__main__":
    print("=== BudgetSafetyManager テスト ===")
    
    manager = BudgetSafetyManager()
    
    # アラートコールバック設定
    def alert_callback(alert: BudgetAlert):
        print(f"[アラート] {alert.severity}: {alert.message}")
    
    def stop_callback(session_id: str, reason: str, current: float, limit: float):
        print(f"[緊急停止] セッション{session_id}: {reason} (${current:.2f}/${limit:.2f})")
    
    manager.add_alert_callback(alert_callback)
    manager.add_stop_callback(stop_callback)
    
    # 予算設定テスト
    print("\n⚙️ 予算設定テスト:")
    manager.set_budget_limits(
        monthly_limit=100.0,
        daily_limit=15.0,
        session_limits={"test": 3.0}
    )
    
    # コスト記録テスト
    print("\n💰 コスト記録テスト:")
    test_session_id = "test_session_001"
    
    cost_id = manager.record_cost(
        session_id=test_session_id,
        api_type="openai",
        operation="text_analysis",
        input_tokens=5000,
        output_tokens=1500,
        details={"model": "gpt-4-turbo"}
    )
    print(f"✅ コスト記録完了: {cost_id}")
    
    # 使用量サマリーテスト
    print("\n📊 使用量サマリーテスト:")
    today_summary = manager.get_usage_summary("today")
    print(f"今日の使用量: ${today_summary['current_usage']:.2f}/${today_summary['limit']:.2f} ({today_summary['percentage']:.1f}%)")
    
    # 最適化提案テスト
    print("\n💡 最適化提案テスト:")
    suggestions = manager.get_cost_optimization_suggestions()
    print(f"提案数: {len(suggestions)}件")
    for suggestion in suggestions:
        print(f"  - {suggestion['title']}: 節約見込み${suggestion.get('potential_savings', 0):.2f}")
    
    # コスト予測テスト
    print("\n🔮 コスト予測テスト:")
    session_config = {
        "theme": "AI音楽生成",
        "learning_type": "標準",
        "depth_level": 3,
        "time_limit": 1800
    }
    prediction = manager.predict_session_cost(session_config)
    print(f"予測コスト: ${prediction['estimated_cost']:.2f} (信頼度: {prediction['confidence']:.1%})")
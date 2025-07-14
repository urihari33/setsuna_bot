#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QualityHistoryManager - 品質履歴追跡・モニタリングシステム
ReportQualityValidatorの検証結果を永続化し、品質傾向を分析・監視
"""

import json
import sqlite3
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum
import statistics
import threading
from contextlib import contextmanager

# プロジェクトルートを確実にパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from core.knowledge_analysis.report_quality_validator import ValidationReport, ValidationSeverity, ValidationIssue
    VALIDATOR_AVAILABLE = True
except ImportError:
    VALIDATOR_AVAILABLE = False
    print("⚠️ ReportQualityValidatorが利用できません")

# ログシステム統合
try:
    from logging_system import get_logger
    LOGGER_AVAILABLE = True
except ImportError:
    LOGGER_AVAILABLE = False

class QualityTrend(Enum):
    """品質傾向"""
    IMPROVING = "improving"
    DECLINING = "declining"
    STABLE = "stable"
    VOLATILE = "volatile"

class AlertLevel(Enum):
    """アラートレベル"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"

@dataclass
class QualitySnapshot:
    """品質スナップショット"""
    timestamp: str
    overall_score: float
    total_issues: int
    critical_issues: int
    error_issues: int
    warning_issues: int
    info_issues: int
    validation_summary: str
    processing_time: float = 0.0
    search_count: int = 0
    cost: float = 0.0
    data_quality: float = 0.0

@dataclass
class QualityAlert:
    """品質アラート"""
    alert_id: str
    timestamp: str
    level: AlertLevel
    message: str
    metrics: Dict[str, Any]
    threshold_violated: str
    suggested_action: str

@dataclass
class QualityTrendAnalysis:
    """品質傾向分析"""
    period_days: int
    trend: QualityTrend
    avg_score: float
    score_change: float
    volatility: float
    issue_trend: Dict[str, float]
    recommendations: List[str]

class QualityHistoryManager:
    """品質履歴管理システム"""
    
    def __init__(self, db_path: Optional[str] = None):
        """初期化"""
        # ログシステム初期化
        if LOGGER_AVAILABLE:
            self.logger = get_logger()
            self.logger.info("quality_monitoring", "init", "QualityHistoryManager初期化開始")
        else:
            self.logger = None
        
        # データベースパス設定
        if db_path:
            self.db_path = Path(db_path)
        else:
            self.db_path = Path("D:/setsuna_bot/quality_monitoring/quality_history.db")
        
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # スレッドロック
        self._lock = threading.Lock()
        
        # 品質設定
        self.quality_config = {
            "score_warning_threshold": 0.6,
            "score_critical_threshold": 0.4,
            "max_critical_issues": 3,
            "max_error_issues": 5,
            "trend_analysis_days": 7,
            "volatility_threshold": 0.3,
            "cost_warning_threshold": 1.0,  # $1以上で警告
            "processing_time_warning": 60.0  # 60秒以上で警告
        }
        
        # データベース初期化
        self._initialize_database()
        
        print("[品質履歴] ✅ QualityHistoryManager初期化完了")
    
    def _initialize_database(self):
        """データベース初期化"""
        try:
            with self._get_db_connection() as conn:
                # 品質履歴テーブル
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS quality_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        overall_score REAL NOT NULL,
                        total_issues INTEGER NOT NULL,
                        critical_issues INTEGER NOT NULL,
                        error_issues INTEGER NOT NULL,
                        warning_issues INTEGER NOT NULL,
                        info_issues INTEGER NOT NULL,
                        validation_summary TEXT,
                        processing_time REAL DEFAULT 0.0,
                        search_count INTEGER DEFAULT 0,
                        cost REAL DEFAULT 0.0,
                        data_quality REAL DEFAULT 0.0,
                        raw_data TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # 品質アラートテーブル
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS quality_alerts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        alert_id TEXT UNIQUE NOT NULL,
                        timestamp TEXT NOT NULL,
                        level TEXT NOT NULL,
                        message TEXT NOT NULL,
                        metrics TEXT,
                        threshold_violated TEXT,
                        suggested_action TEXT,
                        resolved BOOLEAN DEFAULT FALSE,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # 品質メトリクステーブル
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS quality_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        metric_name TEXT NOT NULL,
                        metric_value REAL NOT NULL,
                        metric_type TEXT DEFAULT 'gauge',
                        tags TEXT,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # インデックス作成
                conn.execute("CREATE INDEX IF NOT EXISTS idx_quality_timestamp ON quality_history(timestamp)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON quality_alerts(timestamp)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON quality_metrics(timestamp)")
                
                conn.commit()
            
            if self.logger:
                self.logger.info("quality_monitoring", "init_db", "品質履歴データベース初期化完了")
            
        except Exception as e:
            print(f"❌ 品質履歴データベース初期化失敗: {e}")
            if self.logger:
                self.logger.error("quality_monitoring", "init_db", f"データベース初期化エラー: {e}")
    
    @contextmanager
    def _get_db_connection(self):
        """データベース接続コンテキストマネージャ"""
        conn = None
        try:
            conn = sqlite3.connect(str(self.db_path), timeout=30.0)
            conn.row_factory = sqlite3.Row
            yield conn
        finally:
            if conn:
                conn.close()
    
    def record_validation_result(self, validation_report: ValidationReport, 
                               processing_time: float = 0.0, search_count: int = 0,
                               cost: float = 0.0, data_quality: float = 0.0) -> str:
        """検証結果を記録"""
        try:
            with self._lock:
                # 品質スナップショット作成
                snapshot = QualitySnapshot(
                    timestamp=validation_report.validation_timestamp,
                    overall_score=validation_report.overall_score,
                    total_issues=validation_report.total_issues,
                    critical_issues=validation_report.issues_by_severity.get("critical", 0),
                    error_issues=validation_report.issues_by_severity.get("error", 0),
                    warning_issues=validation_report.issues_by_severity.get("warning", 0),
                    info_issues=validation_report.issues_by_severity.get("info", 0),
                    validation_summary=validation_report.validation_summary,
                    processing_time=processing_time,
                    search_count=search_count,
                    cost=cost,
                    data_quality=data_quality
                )
                
                # データベースに保存
                record_id = self._save_quality_snapshot(snapshot, validation_report)
                
                # メトリクス記録
                self._record_metrics(snapshot)
                
                # アラート判定
                alerts = self._check_quality_alerts(snapshot)
                for alert in alerts:
                    self._save_alert(alert)
                
                if self.logger:
                    self.logger.info("quality_monitoring", "record", f"品質記録保存完了: ID={record_id}")
                
                print(f"[品質履歴] 📊 品質記録保存: スコア{snapshot.overall_score:.2f}, 問題{snapshot.total_issues}件")
                
                return record_id
                
        except Exception as e:
            print(f"❌ 品質記録保存エラー: {e}")
            if self.logger:
                self.logger.error("quality_monitoring", "record", f"品質記録エラー: {e}")
            return ""
    
    def _save_quality_snapshot(self, snapshot: QualitySnapshot, validation_report: ValidationReport) -> str:
        """品質スナップショットをデータベースに保存"""
        try:
            with self._get_db_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO quality_history (
                        timestamp, overall_score, total_issues, critical_issues,
                        error_issues, warning_issues, info_issues, validation_summary,
                        processing_time, search_count, cost, data_quality, raw_data
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    snapshot.timestamp,
                    snapshot.overall_score,
                    snapshot.total_issues,
                    snapshot.critical_issues,
                    snapshot.error_issues,
                    snapshot.warning_issues,
                    snapshot.info_issues,
                    snapshot.validation_summary,
                    snapshot.processing_time,
                    snapshot.search_count,
                    snapshot.cost,
                    snapshot.data_quality,
                    json.dumps(asdict(validation_report), default=str, ensure_ascii=False)
                ))
                
                conn.commit()
                return str(cursor.lastrowid)
                
        except Exception as e:
            print(f"⚠️ 品質スナップショット保存エラー: {e}")
            return ""
    
    def _record_metrics(self, snapshot: QualitySnapshot):
        """メトリクス記録"""
        try:
            metrics = [
                ("overall_score", snapshot.overall_score, "gauge"),
                ("total_issues", snapshot.total_issues, "gauge"),
                ("critical_issues", snapshot.critical_issues, "gauge"),
                ("processing_time", snapshot.processing_time, "gauge"),
                ("search_count", snapshot.search_count, "counter"),
                ("cost", snapshot.cost, "counter"),
                ("data_quality", snapshot.data_quality, "gauge")
            ]
            
            with self._get_db_connection() as conn:
                for metric_name, value, metric_type in metrics:
                    conn.execute("""
                        INSERT INTO quality_metrics (timestamp, metric_name, metric_value, metric_type)
                        VALUES (?, ?, ?, ?)
                    """, (snapshot.timestamp, metric_name, value, metric_type))
                
                conn.commit()
                
        except Exception as e:
            print(f"⚠️ メトリクス記録エラー: {e}")
    
    def _check_quality_alerts(self, snapshot: QualitySnapshot) -> List[QualityAlert]:
        """品質アラート判定"""
        alerts = []
        timestamp = datetime.now().isoformat()
        
        try:
            # スコアベースアラート
            if snapshot.overall_score <= self.quality_config["score_critical_threshold"]:
                alerts.append(QualityAlert(
                    alert_id=f"score_critical_{timestamp}",
                    timestamp=timestamp,
                    level=AlertLevel.CRITICAL,
                    message=f"品質スコアが臨界値を下回りました: {snapshot.overall_score:.2f}",
                    metrics={"overall_score": snapshot.overall_score},
                    threshold_violated="score_critical_threshold",
                    suggested_action="緊急対応: システム設定確認・データ品質改善が必要"
                ))
            elif snapshot.overall_score <= self.quality_config["score_warning_threshold"]:
                alerts.append(QualityAlert(
                    alert_id=f"score_warning_{timestamp}",
                    timestamp=timestamp,
                    level=AlertLevel.WARNING,
                    message=f"品質スコアが警告値を下回りました: {snapshot.overall_score:.2f}",
                    metrics={"overall_score": snapshot.overall_score},
                    threshold_violated="score_warning_threshold",
                    suggested_action="品質改善の検討・監視強化を推奨"
                ))
            
            # クリティカル問題アラート
            if snapshot.critical_issues >= self.quality_config["max_critical_issues"]:
                alerts.append(QualityAlert(
                    alert_id=f"critical_issues_{timestamp}",
                    timestamp=timestamp,
                    level=AlertLevel.EMERGENCY,
                    message=f"クリティカル問題が多発: {snapshot.critical_issues}件",
                    metrics={"critical_issues": snapshot.critical_issues},
                    threshold_violated="max_critical_issues",
                    suggested_action="緊急対応: システム停止・原因調査が必要"
                ))
            
            # コストアラート
            if snapshot.cost >= self.quality_config["cost_warning_threshold"]:
                alerts.append(QualityAlert(
                    alert_id=f"cost_warning_{timestamp}",
                    timestamp=timestamp,
                    level=AlertLevel.WARNING,
                    message=f"コストが警告値を超過: ${snapshot.cost:.2f}",
                    metrics={"cost": snapshot.cost},
                    threshold_violated="cost_warning_threshold",
                    suggested_action="コスト最適化・使用量制限の検討"
                ))
            
            # 処理時間アラート
            if snapshot.processing_time >= self.quality_config["processing_time_warning"]:
                alerts.append(QualityAlert(
                    alert_id=f"performance_warning_{timestamp}",
                    timestamp=timestamp,
                    level=AlertLevel.WARNING,
                    message=f"処理時間が遅延: {snapshot.processing_time:.1f}秒",
                    metrics={"processing_time": snapshot.processing_time},
                    threshold_violated="processing_time_warning",
                    suggested_action="パフォーマンス最適化・リソース増強の検討"
                ))
            
        except Exception as e:
            print(f"⚠️ アラート判定エラー: {e}")
        
        return alerts
    
    def _save_alert(self, alert: QualityAlert):
        """アラート保存"""
        try:
            with self._get_db_connection() as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO quality_alerts (
                        alert_id, timestamp, level, message, metrics,
                        threshold_violated, suggested_action
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    alert.alert_id,
                    alert.timestamp,
                    alert.level.value,
                    alert.message,
                    json.dumps(alert.metrics),
                    alert.threshold_violated,
                    alert.suggested_action
                ))
                
                conn.commit()
                
                # アラート表示
                level_emoji = {"info": "ℹ️", "warning": "⚠️", "critical": "🔴", "emergency": "🚨"}
                emoji = level_emoji.get(alert.level.value, "📊")
                print(f"[品質アラート] {emoji} {alert.level.value.upper()}: {alert.message}")
                
        except Exception as e:
            print(f"⚠️ アラート保存エラー: {e}")
    
    def get_quality_trend_analysis(self, days: int = 7) -> QualityTrendAnalysis:
        """品質傾向分析"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            with self._get_db_connection() as conn:
                cursor = conn.execute("""
                    SELECT overall_score, total_issues, critical_issues, error_issues, 
                           warning_issues, timestamp
                    FROM quality_history 
                    WHERE timestamp >= ?
                    ORDER BY timestamp ASC
                """, (cutoff_date,))
                
                records = cursor.fetchall()
            
            if not records:
                return QualityTrendAnalysis(
                    period_days=days,
                    trend=QualityTrend.STABLE,
                    avg_score=0.0,
                    score_change=0.0,
                    volatility=0.0,
                    issue_trend={},
                    recommendations=["データ不足: 品質記録を蓄積してください"]
                )
            
            # スコア分析
            scores = [float(record["overall_score"]) for record in records]
            avg_score = statistics.mean(scores)
            
            # 傾向計算
            if len(scores) >= 2:
                score_change = scores[-1] - scores[0]
                volatility = statistics.stdev(scores) if len(scores) > 1 else 0.0
            else:
                score_change = 0.0
                volatility = 0.0
            
            # 傾向判定
            trend = self._determine_trend(score_change, volatility)
            
            # 問題傾向分析
            issue_trend = self._analyze_issue_trends(records)
            
            # 推奨事項生成
            recommendations = self._generate_trend_recommendations(
                avg_score, score_change, volatility, issue_trend
            )
            
            return QualityTrendAnalysis(
                period_days=days,
                trend=trend,
                avg_score=avg_score,
                score_change=score_change,
                volatility=volatility,
                issue_trend=issue_trend,
                recommendations=recommendations
            )
            
        except Exception as e:
            print(f"⚠️ 品質傾向分析エラー: {e}")
            return QualityTrendAnalysis(
                period_days=days,
                trend=QualityTrend.STABLE,
                avg_score=0.0,
                score_change=0.0,
                volatility=0.0,
                issue_trend={},
                recommendations=[f"分析エラー: {e}"]
            )
    
    def _determine_trend(self, score_change: float, volatility: float) -> QualityTrend:
        """傾向判定"""
        volatility_threshold = self.quality_config["volatility_threshold"]
        
        if volatility > volatility_threshold:
            return QualityTrend.VOLATILE
        elif score_change > 0.1:
            return QualityTrend.IMPROVING
        elif score_change < -0.1:
            return QualityTrend.DECLINING
        else:
            return QualityTrend.STABLE
    
    def _analyze_issue_trends(self, records: List) -> Dict[str, float]:
        """問題傾向分析"""
        issue_types = ["critical_issues", "error_issues", "warning_issues"]
        trends = {}
        
        for issue_type in issue_types:
            values = [int(record[issue_type]) for record in records]
            if len(values) >= 2:
                change = values[-1] - values[0]
                avg = statistics.mean(values)
                trends[issue_type] = change / (avg + 1)  # 正規化
            else:
                trends[issue_type] = 0.0
        
        return trends
    
    def _generate_trend_recommendations(self, avg_score: float, score_change: float, 
                                      volatility: float, issue_trend: Dict[str, float]) -> List[str]:
        """傾向推奨事項生成"""
        recommendations = []
        
        # スコアベース推奨
        if avg_score < 0.5:
            recommendations.append("低品質警告: システム全体の見直しが必要")
        elif avg_score < 0.7:
            recommendations.append("品質改善: 設定調整・データ品質向上を検討")
        
        # 傾向ベース推奨
        if score_change < -0.2:
            recommendations.append("品質劣化傾向: 原因分析・緊急対応が必要")
        elif score_change > 0.2:
            recommendations.append("品質改善傾向: 現在の取り組みを継続")
        
        # 変動性ベース推奨
        if volatility > 0.3:
            recommendations.append("品質不安定: 設定の標準化・安定化が必要")
        
        # 問題傾向ベース推奨
        if issue_trend.get("critical_issues", 0) > 0.5:
            recommendations.append("クリティカル問題増加: 緊急対応・根本原因調査")
        
        if not recommendations:
            recommendations.append("品質状況は良好です")
        
        return recommendations
    
    def get_recent_alerts(self, hours: int = 24, level: Optional[AlertLevel] = None) -> List[QualityAlert]:
        """最近のアラート取得"""
        try:
            cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat()
            
            query = """
                SELECT alert_id, timestamp, level, message, metrics,
                       threshold_violated, suggested_action
                FROM quality_alerts 
                WHERE timestamp >= ? AND resolved = FALSE
            """
            params = [cutoff_time]
            
            if level:
                query += " AND level = ?"
                params.append(level.value)
            
            query += " ORDER BY timestamp DESC"
            
            with self._get_db_connection() as conn:
                cursor = conn.execute(query, params)
                records = cursor.fetchall()
            
            alerts = []
            for record in records:
                alerts.append(QualityAlert(
                    alert_id=record["alert_id"],
                    timestamp=record["timestamp"],
                    level=AlertLevel(record["level"]),
                    message=record["message"],
                    metrics=json.loads(record["metrics"]) if record["metrics"] else {},
                    threshold_violated=record["threshold_violated"],
                    suggested_action=record["suggested_action"]
                ))
            
            return alerts
            
        except Exception as e:
            print(f"⚠️ アラート取得エラー: {e}")
            return []
    
    def get_quality_statistics(self, days: int = 30) -> Dict[str, Any]:
        """品質統計情報取得"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            with self._get_db_connection() as conn:
                # 基本統計
                cursor = conn.execute("""
                    SELECT 
                        COUNT(*) as total_records,
                        AVG(overall_score) as avg_score,
                        MIN(overall_score) as min_score,
                        MAX(overall_score) as max_score,
                        SUM(total_issues) as total_issues,
                        SUM(critical_issues) as total_critical,
                        SUM(cost) as total_cost,
                        AVG(processing_time) as avg_processing_time
                    FROM quality_history 
                    WHERE timestamp >= ?
                """, (cutoff_date,))
                
                stats = cursor.fetchone()
                
                # アラート統計
                cursor = conn.execute("""
                    SELECT level, COUNT(*) as count
                    FROM quality_alerts 
                    WHERE timestamp >= ?
                    GROUP BY level
                """, (cutoff_date,))
                
                alert_stats = dict(cursor.fetchall())
            
            return {
                "period_days": days,
                "total_records": stats["total_records"] or 0,
                "average_score": round(stats["avg_score"] or 0, 3),
                "score_range": [round(stats["min_score"] or 0, 3), round(stats["max_score"] or 0, 3)],
                "total_issues": stats["total_issues"] or 0,
                "critical_issues": stats["total_critical"] or 0,
                "total_cost": round(stats["total_cost"] or 0, 4),
                "avg_processing_time": round(stats["avg_processing_time"] or 0, 2),
                "alert_counts": alert_stats,
                "db_path": str(self.db_path),
                "db_size_mb": round(self.db_path.stat().st_size / (1024*1024), 2) if self.db_path.exists() else 0
            }
            
        except Exception as e:
            print(f"⚠️ 統計情報取得エラー: {e}")
            return {"error": str(e)}
    
    def cleanup_old_records(self, keep_days: int = 90):
        """古い記録のクリーンアップ"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=keep_days)).isoformat()
            
            with self._get_db_connection() as conn:
                # 古い履歴削除
                cursor = conn.execute("DELETE FROM quality_history WHERE timestamp < ?", (cutoff_date,))
                history_deleted = cursor.rowcount
                
                # 古いアラート削除（解決済み）
                cursor = conn.execute("""
                    DELETE FROM quality_alerts 
                    WHERE timestamp < ? AND resolved = TRUE
                """, (cutoff_date,))
                alerts_deleted = cursor.rowcount
                
                # 古いメトリクス削除
                cursor = conn.execute("DELETE FROM quality_metrics WHERE timestamp < ?", (cutoff_date,))
                metrics_deleted = cursor.rowcount
                
                conn.commit()
            
            print(f"[品質履歴] 🗑️ クリーンアップ完了: 履歴{history_deleted}件, アラート{alerts_deleted}件, メトリクス{metrics_deleted}件削除")
            
            if self.logger:
                self.logger.info("quality_monitoring", "cleanup", 
                               f"古い記録削除完了: {history_deleted + alerts_deleted + metrics_deleted}件")
            
        except Exception as e:
            print(f"⚠️ クリーンアップエラー: {e}")

if __name__ == "__main__":
    """テスト実行"""
    print("🧪 QualityHistoryManager テスト実行")
    print("=" * 60)
    
    manager = QualityHistoryManager()
    
    # 統計情報テスト
    print("\n📊 品質統計情報:")
    stats = manager.get_quality_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")
    
    # 傾向分析テスト
    print(f"\n📈 品質傾向分析:")
    trend = manager.get_quality_trend_analysis()
    print(f"   傾向: {trend.trend.value}")
    print(f"   平均スコア: {trend.avg_score:.3f}")
    print(f"   スコア変化: {trend.score_change:+.3f}")
    print(f"   推奨事項: {trend.recommendations}")
    
    # アラート確認テスト
    print(f"\n🚨 最近のアラート:")
    alerts = manager.get_recent_alerts()
    if alerts:
        for alert in alerts[:3]:
            print(f"   {alert.level.value}: {alert.message}")
    else:
        print("   アラートはありません")
    
    print(f"\n✅ QualityHistoryManager テスト完了")
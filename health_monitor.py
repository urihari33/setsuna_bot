#!/usr/bin/env python3
"""
高度なシステムヘルスモニタリング機能
システムのパフォーマンス、リソース使用状況、エラー率を監視
"""

import os
import json
import time
import psutil
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from logging_system import get_logger

@dataclass
class HealthMetrics:
    """システムヘルスメトリクス"""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    process_count: int
    thread_count: int
    error_rate: float
    response_time: float
    cache_hit_rate: float
    status: str

@dataclass
class SystemAlert:
    """システムアラート"""
    timestamp: str
    level: str  # INFO, WARNING, ERROR, CRITICAL
    component: str
    message: str
    metric_value: float
    threshold: float

class HealthMonitor:
    """高度なヘルスモニタリングシステム"""
    
    def __init__(self, data_dir: str = "/mnt/d/setsuna_bot/monitoring"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.logger = get_logger()
        self.metrics_file = self.data_dir / "health_metrics.json"
        self.alerts_file = self.data_dir / "alerts.json"
        self.config_file = self.data_dir / "monitor_config.json"
        
        # デフォルト設定
        self.config = {
            "monitoring_interval": 30,  # 30秒間隔
            "metrics_retention_days": 7,
            "thresholds": {
                "cpu_warning": 70.0,
                "cpu_critical": 85.0,
                "memory_warning": 80.0,
                "memory_critical": 90.0,
                "disk_warning": 85.0,
                "disk_critical": 95.0,
                "error_rate_warning": 5.0,
                "error_rate_critical": 10.0,
                "response_time_warning": 2.0,
                "response_time_critical": 5.0
            }
        }
        
        self.load_config()
        self.monitoring_thread = None
        self.stop_monitoring = False
        
        # メトリクス履歴
        self.metrics_history: List[HealthMetrics] = []
        self.alerts_history: List[SystemAlert] = []
        
        self.load_historical_data()
        
    def load_config(self):
        """設定を読み込み"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    self.config.update(loaded_config)
        except Exception as e:
            self.logger.warning(f"設定読み込みエラー: {e}")
            
    def save_config(self):
        """設定を保存"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"設定保存エラー: {e}")
    
    def load_historical_data(self):
        """履歴データを読み込み"""
        try:
            if self.metrics_file.exists():
                with open(self.metrics_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.metrics_history = [
                        HealthMetrics(**metric) for metric in data.get('metrics', [])
                    ]
                    
            if self.alerts_file.exists():
                with open(self.alerts_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.alerts_history = [
                        SystemAlert(**alert) for alert in data.get('alerts', [])
                    ]
        except Exception as e:
            self.logger.warning(f"履歴データ読み込みエラー: {e}")
    
    def save_historical_data(self):
        """履歴データを保存"""
        try:
            # メトリクス保存
            metrics_data = {
                'metrics': [asdict(metric) for metric in self.metrics_history],
                'last_updated': datetime.now().isoformat()
            }
            with open(self.metrics_file, 'w', encoding='utf-8') as f:
                json.dump(metrics_data, f, indent=2, ensure_ascii=False)
                
            # アラート保存
            alerts_data = {
                'alerts': [asdict(alert) for alert in self.alerts_history],
                'last_updated': datetime.now().isoformat()
            }
            with open(self.alerts_file, 'w', encoding='utf-8') as f:
                json.dump(alerts_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"履歴データ保存エラー: {e}")
    
    def collect_system_metrics(self) -> HealthMetrics:
        """システムメトリクスを収集"""
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # メモリ使用率
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # ディスク使用率
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # プロセス数
            process_count = len(psutil.pids())
            
            # スレッド数
            thread_count = threading.active_count()
            
            # エラー率とレスポンス時間を計算
            error_rate, response_time = self.calculate_performance_metrics()
            
            # キャッシュヒット率
            cache_hit_rate = self.calculate_cache_hit_rate()
            
            # システム状態判定
            status = self.determine_system_status(
                cpu_percent, memory_percent, disk_percent, error_rate, response_time
            )
            
            return HealthMetrics(
                timestamp=datetime.now().isoformat(),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                disk_percent=disk_percent,
                process_count=process_count,
                thread_count=thread_count,
                error_rate=error_rate,
                response_time=response_time,
                cache_hit_rate=cache_hit_rate,
                status=status
            )
            
        except Exception as e:
            self.logger.error(f"メトリクス収集エラー: {e}")
            return HealthMetrics(
                timestamp=datetime.now().isoformat(),
                cpu_percent=0.0,
                memory_percent=0.0,
                disk_percent=0.0,
                process_count=0,
                thread_count=0,
                error_rate=0.0,
                response_time=0.0,
                cache_hit_rate=0.0,
                status="ERROR"
            )
    
    def calculate_performance_metrics(self) -> Tuple[float, float]:
        """パフォーマンスメトリクスを計算"""
        try:
            # ログファイルから最近のエラー率を計算
            error_rate = 0.0
            response_time = 0.0
            
            # 簡単な実装：過去のメトリクスから平均を計算
            if self.metrics_history:
                recent_metrics = self.metrics_history[-10:]  # 最近10件
                if recent_metrics:
                    error_rate = sum(m.error_rate for m in recent_metrics) / len(recent_metrics)
                    response_time = sum(m.response_time for m in recent_metrics) / len(recent_metrics)
            
            return error_rate, response_time
            
        except Exception as e:
            self.logger.warning(f"パフォーマンスメトリクス計算エラー: {e}")
            return 0.0, 0.0
    
    def calculate_cache_hit_rate(self) -> float:
        """キャッシュヒット率を計算"""
        try:
            cache_stats_file = Path("/mnt/d/setsuna_bot/response_cache/cache_stats.json")
            if cache_stats_file.exists():
                with open(cache_stats_file, 'r', encoding='utf-8') as f:
                    stats = json.load(f)
                    total_requests = stats.get('total_requests', 0)
                    hits = stats.get('hits', 0)
                    
                    if total_requests > 0:
                        return (hits / total_requests) * 100
            
            return 0.0
            
        except Exception as e:
            self.logger.warning(f"キャッシュヒット率計算エラー: {e}")
            return 0.0
    
    def determine_system_status(self, cpu: float, memory: float, disk: float, 
                              error_rate: float, response_time: float) -> str:
        """システム状態を判定"""
        thresholds = self.config['thresholds']
        
        # クリティカルレベルのチェック
        if (cpu >= thresholds['cpu_critical'] or 
            memory >= thresholds['memory_critical'] or
            disk >= thresholds['disk_critical'] or
            error_rate >= thresholds['error_rate_critical'] or
            response_time >= thresholds['response_time_critical']):
            return "CRITICAL"
        
        # 警告レベルのチェック
        if (cpu >= thresholds['cpu_warning'] or 
            memory >= thresholds['memory_warning'] or
            disk >= thresholds['disk_warning'] or
            error_rate >= thresholds['error_rate_warning'] or
            response_time >= thresholds['response_time_warning']):
            return "WARNING"
        
        return "HEALTHY"
    
    def generate_alerts(self, metrics: HealthMetrics):
        """アラートを生成"""
        thresholds = self.config['thresholds']
        
        alerts = []
        
        # CPU使用率チェック
        if metrics.cpu_percent >= thresholds['cpu_critical']:
            alerts.append(SystemAlert(
                timestamp=datetime.now().isoformat(),
                level="CRITICAL",
                component="CPU",
                message=f"CPU使用率が危険レベルに達しました: {metrics.cpu_percent:.1f}%",
                metric_value=metrics.cpu_percent,
                threshold=thresholds['cpu_critical']
            ))
        elif metrics.cpu_percent >= thresholds['cpu_warning']:
            alerts.append(SystemAlert(
                timestamp=datetime.now().isoformat(),
                level="WARNING",
                component="CPU",
                message=f"CPU使用率が警告レベルに達しました: {metrics.cpu_percent:.1f}%",
                metric_value=metrics.cpu_percent,
                threshold=thresholds['cpu_warning']
            ))
        
        # メモリ使用率チェック
        if metrics.memory_percent >= thresholds['memory_critical']:
            alerts.append(SystemAlert(
                timestamp=datetime.now().isoformat(),
                level="CRITICAL",
                component="Memory",
                message=f"メモリ使用率が危険レベルに達しました: {metrics.memory_percent:.1f}%",
                metric_value=metrics.memory_percent,
                threshold=thresholds['memory_critical']
            ))
        elif metrics.memory_percent >= thresholds['memory_warning']:
            alerts.append(SystemAlert(
                timestamp=datetime.now().isoformat(),
                level="WARNING",
                component="Memory",
                message=f"メモリ使用率が警告レベルに達しました: {metrics.memory_percent:.1f}%",
                metric_value=metrics.memory_percent,
                threshold=thresholds['memory_warning']
            ))
        
        # ディスク使用率チェック
        if metrics.disk_percent >= thresholds['disk_critical']:
            alerts.append(SystemAlert(
                timestamp=datetime.now().isoformat(),
                level="CRITICAL",
                component="Disk",
                message=f"ディスク使用率が危険レベルに達しました: {metrics.disk_percent:.1f}%",
                metric_value=metrics.disk_percent,
                threshold=thresholds['disk_critical']
            ))
        elif metrics.disk_percent >= thresholds['disk_warning']:
            alerts.append(SystemAlert(
                timestamp=datetime.now().isoformat(),
                level="WARNING",
                component="Disk",
                message=f"ディスク使用率が警告レベルに達しました: {metrics.disk_percent:.1f}%",
                metric_value=metrics.disk_percent,
                threshold=thresholds['disk_warning']
            ))
        
        # アラートを履歴に追加
        for alert in alerts:
            self.alerts_history.append(alert)
            self.logger.warning(f"アラート生成: {alert.message}")
        
        return alerts
    
    def cleanup_old_data(self):
        """古いデータをクリーンアップ"""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.config['metrics_retention_days'])
            
            # 古いメトリクスを削除
            self.metrics_history = [
                metric for metric in self.metrics_history
                if datetime.fromisoformat(metric.timestamp) > cutoff_date
            ]
            
            # 古いアラートを削除
            self.alerts_history = [
                alert for alert in self.alerts_history
                if datetime.fromisoformat(alert.timestamp) > cutoff_date
            ]
            
            self.logger.info(f"古いデータをクリーンアップ（保持期間: {self.config['metrics_retention_days']}日）")
            
        except Exception as e:
            self.logger.error(f"データクリーンアップエラー: {e}")
    
    def start_monitoring(self):
        """モニタリングを開始"""
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.logger.warning("モニタリングは既に開始されています")
            return
        
        self.stop_monitoring = False
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        self.logger.info("ヘルスモニタリング開始")
    
    def stop_monitoring_service(self):
        """モニタリングを停止"""
        self.stop_monitoring = True
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        self.logger.info("ヘルスモニタリング停止")
    
    def _monitoring_loop(self):
        """モニタリングループ"""
        while not self.stop_monitoring:
            try:
                # メトリクス収集
                metrics = self.collect_system_metrics()
                self.metrics_history.append(metrics)
                
                # アラート生成
                self.generate_alerts(metrics)
                
                # データ保存
                self.save_historical_data()
                
                # 古いデータクリーンアップ（1時間に1回）
                if len(self.metrics_history) % 120 == 0:  # 30秒間隔で120回 = 1時間
                    self.cleanup_old_data()
                
                # 次のチェックまで待機
                time.sleep(self.config['monitoring_interval'])
                
            except Exception as e:
                self.logger.error(f"モニタリングループエラー: {e}")
                time.sleep(self.config['monitoring_interval'])
    
    def get_system_health_summary(self) -> Dict:
        """システムヘルスサマリを取得"""
        try:
            if not self.metrics_history:
                return {"status": "NO_DATA", "message": "メトリクスデータがありません"}
            
            latest_metrics = self.metrics_history[-1]
            
            # 最近のアラート数を集計
            recent_alerts = [
                alert for alert in self.alerts_history
                if datetime.fromisoformat(alert.timestamp) > datetime.now() - timedelta(hours=1)
            ]
            
            alert_counts = {
                'CRITICAL': len([a for a in recent_alerts if a.level == 'CRITICAL']),
                'WARNING': len([a for a in recent_alerts if a.level == 'WARNING']),
                'INFO': len([a for a in recent_alerts if a.level == 'INFO'])
            }
            
            return {
                "status": latest_metrics.status,
                "timestamp": latest_metrics.timestamp,
                "metrics": {
                    "cpu_percent": latest_metrics.cpu_percent,
                    "memory_percent": latest_metrics.memory_percent,
                    "disk_percent": latest_metrics.disk_percent,
                    "process_count": latest_metrics.process_count,
                    "thread_count": latest_metrics.thread_count,
                    "error_rate": latest_metrics.error_rate,
                    "response_time": latest_metrics.response_time,
                    "cache_hit_rate": latest_metrics.cache_hit_rate
                },
                "recent_alerts": alert_counts,
                "total_metrics": len(self.metrics_history),
                "monitoring_active": self.monitoring_thread and self.monitoring_thread.is_alive()
            }
            
        except Exception as e:
            self.logger.error(f"ヘルスサマリ取得エラー: {e}")
            return {"status": "ERROR", "message": str(e)}

# グローバルインスタンス
_health_monitor = None

def get_health_monitor() -> HealthMonitor:
    """ヘルスモニターのグローバルインスタンスを取得"""
    global _health_monitor
    if _health_monitor is None:
        _health_monitor = HealthMonitor()
    return _health_monitor

if __name__ == "__main__":
    # テスト実行
    monitor = get_health_monitor()
    
    print("=== ヘルスモニタリングシステムテスト ===")
    
    # モニタリング開始
    monitor.start_monitoring()
    
    # 30秒間モニタリング
    time.sleep(30)
    
    # サマリ表示
    summary = monitor.get_system_health_summary()
    print(f"システム状態: {summary['status']}")
    print(f"CPU使用率: {summary['metrics']['cpu_percent']:.1f}%")
    print(f"メモリ使用率: {summary['metrics']['memory_percent']:.1f}%")
    print(f"ディスク使用率: {summary['metrics']['disk_percent']:.1f}%")
    print(f"キャッシュヒット率: {summary['metrics']['cache_hit_rate']:.1f}%")
    
    # モニタリング停止
    monitor.stop_monitoring_service()
    
    print("テスト完了")
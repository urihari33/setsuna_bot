#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
パフォーマンス監視システム - Phase 2F実装
システム全体のパフォーマンス監視・ボトルネック検出・リソース使用量追跡
"""

import json
import os
import sys
import time
import psutil
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from datetime import datetime, timedelta
import traceback
from statistics import mean, median, stdev
import functools

# プロジェクトルートをパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Windowsパス設定
if os.name == 'nt':
    PERFORMANCE_CACHE_DIR = Path("D:/setsuna_bot/performance_monitor_cache")
else:
    PERFORMANCE_CACHE_DIR = Path("/mnt/d/setsuna_bot/performance_monitor_cache")

PERFORMANCE_CACHE_DIR.mkdir(parents=True, exist_ok=True)

@dataclass
class PerformanceMetric:
    """パフォーマンスメトリクスデータクラス"""
    metric_id: str
    metric_name: str
    component: str               # "system", "memory", "cpu", "disk", "network", "application"
    value: float
    unit: str                   # "seconds", "mb", "percent", "count", "requests_per_second"
    timestamp: str
    context: Dict[str, Any]     # 追加コンテキスト情報

@dataclass
class PerformanceAlert:
    """パフォーマンスアラートデータクラス"""
    alert_id: str
    alert_type: str             # "threshold_exceeded", "anomaly_detected", "degradation", "resource_exhaustion"
    severity: str               # "low", "medium", "high", "critical"
    component: str
    metric_name: str
    current_value: float
    threshold_value: float
    description: str
    detected_at: str
    resolved_at: Optional[str]
    auto_resolved: bool

@dataclass
class BottleneckDetection:
    """ボトルネック検出データクラス"""
    detection_id: str
    bottleneck_type: str        # "cpu", "memory", "io", "network", "function_call", "database"
    affected_components: List[str]
    severity_score: float       # 0.0-1.0
    impact_description: str
    suggested_optimizations: List[str]
    detection_confidence: float
    detected_at: str

@dataclass
class FunctionPerformance:
    """関数パフォーマンスデータクラス"""
    function_name: str
    module_name: str
    call_count: int
    total_time: float
    average_time: float
    min_time: float
    max_time: float
    last_called: str
    memory_usage: Optional[float]
    error_count: int

@dataclass
class SystemSnapshot:
    """システムスナップショットデータクラス"""
    snapshot_id: str
    timestamp: str
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_io: Dict[str, float]
    active_processes: int
    open_files: int
    system_uptime: float
    load_average: Optional[List[float]]

class PerformanceMonitor:
    """パフォーマンス監視システムクラス"""
    
    def __init__(self):
        """初期化"""
        # データパス
        self.metrics_path = PERFORMANCE_CACHE_DIR / "performance_metrics.json"
        self.alerts_path = PERFORMANCE_CACHE_DIR / "performance_alerts.json"
        self.bottlenecks_path = PERFORMANCE_CACHE_DIR / "bottleneck_detections.json"
        self.function_performance_path = PERFORMANCE_CACHE_DIR / "function_performance.json"
        self.system_snapshots_path = PERFORMANCE_CACHE_DIR / "system_snapshots.json"
        self.monitoring_config_path = PERFORMANCE_CACHE_DIR / "monitoring_config.json"
        
        # データ
        self.metrics_buffer = deque(maxlen=1000)  # 最新1000メトリクス
        self.performance_alerts = {}
        self.bottleneck_detections = {}
        self.function_performance = {}
        self.system_snapshots = deque(maxlen=288)  # 24時間分（5分間隔）
        
        # 監視設定
        self.monitoring_config = {
            "cpu_threshold": 80.0,
            "memory_threshold": 85.0,
            "disk_threshold": 90.0,
            "response_time_threshold": 5.0,
            "monitoring_interval": 60,  # 秒
            "alert_cooldown": 300,     # 秒
            "auto_optimization": True
        }
        
        # 監視状態
        self.monitoring_active = False
        self.monitor_thread = None
        self.function_call_tracking = {}
        self.baseline_metrics = {}
        
        # 初期化
        self._load_data()
        self._load_monitoring_config()
        
    def _load_data(self):
        """データ読み込み"""
        try:
            if self.alerts_path.exists():
                with open(self.alerts_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.performance_alerts = {k: PerformanceAlert(**v) for k, v in data.items()}
            
            if self.bottlenecks_path.exists():
                with open(self.bottlenecks_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.bottleneck_detections = {k: BottleneckDetection(**v) for k, v in data.items()}
            
            if self.function_performance_path.exists():
                with open(self.function_performance_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.function_performance = {k: FunctionPerformance(**v) for k, v in data.items()}
            
            if self.system_snapshots_path.exists():
                with open(self.system_snapshots_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.system_snapshots = deque([SystemSnapshot(**item) for item in data], maxlen=288)
                    
        except Exception as e:
            print(f"[パフォーマンス監視] データ読み込みエラー: {e}")
    
    def _save_data(self):
        """データ保存"""
        try:
            # パフォーマンスアラート保存
            with open(self.alerts_path, 'w', encoding='utf-8') as f:
                json.dump({k: asdict(v) for k, v in self.performance_alerts.items()}, f, 
                         ensure_ascii=False, indent=2)
            
            # ボトルネック検出保存
            with open(self.bottlenecks_path, 'w', encoding='utf-8') as f:
                json.dump({k: asdict(v) for k, v in self.bottleneck_detections.items()}, f, 
                         ensure_ascii=False, indent=2)
            
            # 関数パフォーマンス保存
            with open(self.function_performance_path, 'w', encoding='utf-8') as f:
                json.dump({k: asdict(v) for k, v in self.function_performance.items()}, f, 
                         ensure_ascii=False, indent=2)
            
            # システムスナップショット保存
            with open(self.system_snapshots_path, 'w', encoding='utf-8') as f:
                json.dump([asdict(snapshot) for snapshot in self.system_snapshots], f, 
                         ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"[パフォーマンス監視] データ保存エラー: {e}")
    
    def _load_monitoring_config(self):
        """監視設定読み込み"""
        try:
            if self.monitoring_config_path.exists():
                with open(self.monitoring_config_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    self.monitoring_config.update(loaded_config)
        except Exception as e:
            print(f"[パフォーマンス監視] 設定読み込みエラー: {e}")
    
    def start_monitoring(self):
        """監視開始"""
        if self.monitoring_active:
            print("[パフォーマンス監視] 既に監視中です")
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()
        print("[パフォーマンス監視] 監視を開始しました")
    
    def stop_monitoring(self):
        """監視停止"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        print("[パフォーマンス監視] 監視を停止しました")
    
    def _monitoring_loop(self):
        """監視ループ"""
        while self.monitoring_active:
            try:
                # システムスナップショット取得
                snapshot = self._capture_system_snapshot()
                self.system_snapshots.append(snapshot)
                
                # メトリクス収集
                self._collect_system_metrics()
                
                # パフォーマンス分析
                self._analyze_performance()
                
                # ボトルネック検出
                self._detect_bottlenecks()
                
                # データ保存
                self._save_data()
                
                # 監視間隔待機
                time.sleep(self.monitoring_config["monitoring_interval"])
                
            except Exception as e:
                print(f"[パフォーマンス監視] 監視ループエラー: {e}")
                time.sleep(10)  # エラー時は短い間隔で再試行
    
    def _capture_system_snapshot(self) -> SystemSnapshot:
        """システムスナップショット取得"""
        snapshot_id = f"snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            # CPU使用率
            cpu_usage = psutil.cpu_percent(interval=1)
            
            # メモリ使用率
            memory = psutil.virtual_memory()
            memory_usage = memory.percent
            
            # ディスク使用率
            disk = psutil.disk_usage('/')
            disk_usage = disk.percent
            
            # ネットワークI/O
            network = psutil.net_io_counters()
            network_io = {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv
            }
            
            # プロセス情報
            active_processes = len(psutil.pids())
            
            # オープンファイル数（可能な場合）
            try:
                open_files = len(psutil.Process().open_files())
            except:
                open_files = 0
            
            # システムアップタイム
            boot_time = psutil.boot_time()
            system_uptime = time.time() - boot_time
            
            # ロードアベレージ（Unix系のみ）
            load_average = None
            if hasattr(os, 'getloadavg'):
                try:
                    load_average = list(os.getloadavg())
                except:
                    pass
            
            snapshot = SystemSnapshot(
                snapshot_id=snapshot_id,
                timestamp=datetime.now().isoformat(),
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                disk_usage=disk_usage,
                network_io=network_io,
                active_processes=active_processes,
                open_files=open_files,
                system_uptime=system_uptime,
                load_average=load_average
            )
            
        except Exception as e:
            print(f"[パフォーマンス監視] スナップショット取得エラー: {e}")
            # エラー時のデフォルトスナップショット
            snapshot = SystemSnapshot(
                snapshot_id=snapshot_id,
                timestamp=datetime.now().isoformat(),
                cpu_usage=0.0,
                memory_usage=0.0,
                disk_usage=0.0,
                network_io={},
                active_processes=0,
                open_files=0,
                system_uptime=0.0,
                load_average=None
            )
        
        return snapshot
    
    def _collect_system_metrics(self):
        """システムメトリクス収集"""
        timestamp = datetime.now().isoformat()
        
        # 最新のスナップショットから基本メトリクス作成
        if self.system_snapshots:
            latest_snapshot = self.system_snapshots[-1]
            
            metrics = [
                PerformanceMetric(
                    metric_id=f"cpu_usage_{timestamp}",
                    metric_name="CPU使用率",
                    component="cpu",
                    value=latest_snapshot.cpu_usage,
                    unit="percent",
                    timestamp=timestamp,
                    context={}
                ),
                PerformanceMetric(
                    metric_id=f"memory_usage_{timestamp}",
                    metric_name="メモリ使用率",
                    component="memory",
                    value=latest_snapshot.memory_usage,
                    unit="percent",
                    timestamp=timestamp,
                    context={}
                ),
                PerformanceMetric(
                    metric_id=f"disk_usage_{timestamp}",
                    metric_name="ディスク使用率",
                    component="disk",
                    value=latest_snapshot.disk_usage,
                    unit="percent",
                    timestamp=timestamp,
                    context={}
                )
            ]
            
            for metric in metrics:
                self.metrics_buffer.append(metric)
    
    def _analyze_performance(self):
        """パフォーマンス分析"""
        if not self.system_snapshots:
            return
        
        latest_snapshot = self.system_snapshots[-1]
        
        # 閾値チェック
        self._check_thresholds(latest_snapshot)
        
        # 異常検出
        self._detect_anomalies(latest_snapshot)
        
        # パフォーマンス劣化検出
        self._detect_performance_degradation()
    
    def _check_thresholds(self, snapshot: SystemSnapshot):
        """閾値チェック"""
        threshold_checks = [
            ("cpu", snapshot.cpu_usage, self.monitoring_config["cpu_threshold"], "CPU使用率が閾値を超過"),
            ("memory", snapshot.memory_usage, self.monitoring_config["memory_threshold"], "メモリ使用率が閾値を超過"),
            ("disk", snapshot.disk_usage, self.monitoring_config["disk_threshold"], "ディスク使用率が閾値を超過")
        ]
        
        for component, current_value, threshold, description in threshold_checks:
            if current_value > threshold:
                self._create_performance_alert(
                    alert_type="threshold_exceeded",
                    severity=self._determine_severity(current_value, threshold),
                    component=component,
                    metric_name=f"{component}_usage",
                    current_value=current_value,
                    threshold_value=threshold,
                    description=description
                )
    
    def _detect_anomalies(self, snapshot: SystemSnapshot):
        """異常検出"""
        if len(self.system_snapshots) < 10:
            return  # 十分なデータがない
        
        # 過去のデータとの比較
        recent_snapshots = list(self.system_snapshots)[-10:]
        
        # CPU使用率の異常検出
        cpu_values = [s.cpu_usage for s in recent_snapshots[:-1]]
        if cpu_values:
            cpu_avg = mean(cpu_values)
            cpu_std = stdev(cpu_values) if len(cpu_values) > 1 else 0
            
            if cpu_std > 0 and abs(snapshot.cpu_usage - cpu_avg) > 2 * cpu_std:
                self._create_performance_alert(
                    alert_type="anomaly_detected",
                    severity="medium",
                    component="cpu",
                    metric_name="cpu_usage",
                    current_value=snapshot.cpu_usage,
                    threshold_value=cpu_avg + 2 * cpu_std,
                    description=f"CPU使用率の異常値を検出（平均: {cpu_avg:.1f}%, 現在: {snapshot.cpu_usage:.1f}%）"
                )
    
    def _detect_performance_degradation(self):
        """パフォーマンス劣化検出"""
        if len(self.system_snapshots) < 20:
            return
        
        # 過去1時間と直近の比較
        recent_snapshots = list(self.system_snapshots)
        past_hour = recent_snapshots[-60:] if len(recent_snapshots) >= 60 else recent_snapshots[:-10]
        current_window = recent_snapshots[-10:]
        
        if not past_hour or not current_window:
            return
        
        # CPU使用率の劣化チェック
        past_cpu_avg = mean([s.cpu_usage for s in past_hour])
        current_cpu_avg = mean([s.cpu_usage for s in current_window])
        
        if current_cpu_avg > past_cpu_avg * 1.5:  # 50%以上の増加
            self._create_performance_alert(
                alert_type="degradation",
                severity="high",
                component="cpu",
                metric_name="cpu_usage",
                current_value=current_cpu_avg,
                threshold_value=past_cpu_avg,
                description=f"CPU使用率の劣化を検出（過去平均: {past_cpu_avg:.1f}%, 現在平均: {current_cpu_avg:.1f}%）"
            )
    
    def _detect_bottlenecks(self):
        """ボトルネック検出"""
        if not self.system_snapshots:
            return
        
        latest_snapshot = self.system_snapshots[-1]
        
        # CPU ボトルネック
        if latest_snapshot.cpu_usage > 90:
            self._create_bottleneck_detection(
                bottleneck_type="cpu",
                affected_components=["system"],
                severity_score=latest_snapshot.cpu_usage / 100.0,
                impact_description="高いCPU使用率によりシステム応答性が低下",
                suggested_optimizations=[
                    "CPU集約的なタスクの最適化",
                    "並列処理の見直し",
                    "不要なプロセスの停止"
                ]
            )
        
        # メモリ ボトルネック
        if latest_snapshot.memory_usage > 85:
            self._create_bottleneck_detection(
                bottleneck_type="memory",
                affected_components=["system"],
                severity_score=latest_snapshot.memory_usage / 100.0,
                impact_description="高いメモリ使用率によりパフォーマンスが低下",
                suggested_optimizations=[
                    "メモリリークの調査",
                    "キャッシュサイズの調整",
                    "不要なデータの解放"
                ]
            )
        
        # 関数レベルのボトルネック検出
        self._detect_function_bottlenecks()
    
    def _detect_function_bottlenecks(self):
        """関数レベルのボトルネック検出"""
        slow_functions = []
        
        for func_key, perf in self.function_performance.items():
            if perf.average_time > self.monitoring_config["response_time_threshold"]:
                slow_functions.append((func_key, perf.average_time))
        
        if slow_functions:
            # 最も遅い関数を特定
            slowest_func, slowest_time = max(slow_functions, key=lambda x: x[1])
            
            self._create_bottleneck_detection(
                bottleneck_type="function_call",
                affected_components=[slowest_func],
                severity_score=min(slowest_time / 10.0, 1.0),  # 10秒で最大
                impact_description=f"関数 {slowest_func} の実行時間が長い（{slowest_time:.2f}秒）",
                suggested_optimizations=[
                    "アルゴリズムの最適化",
                    "キャッシュの導入",
                    "データベースクエリの最適化"
                ]
            )
    
    def _create_performance_alert(self, alert_type: str, severity: str, component: str,
                                metric_name: str, current_value: float, threshold_value: float,
                                description: str):
        """パフォーマンスアラート作成"""
        alert_id = f"alert_{component}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # クールダウンチェック
        recent_alerts = [
            alert for alert in self.performance_alerts.values()
            if alert.component == component and alert.metric_name == metric_name and
            not alert.resolved_at and
            (datetime.now() - datetime.fromisoformat(alert.detected_at)).total_seconds() < self.monitoring_config["alert_cooldown"]
        ]
        
        if recent_alerts:
            return  # クールダウン期間中
        
        alert = PerformanceAlert(
            alert_id=alert_id,
            alert_type=alert_type,
            severity=severity,
            component=component,
            metric_name=metric_name,
            current_value=current_value,
            threshold_value=threshold_value,
            description=description,
            detected_at=datetime.now().isoformat(),
            resolved_at=None,
            auto_resolved=False
        )
        
        self.performance_alerts[alert_id] = alert
        print(f"[パフォーマンス監視] アラート: {description}")
    
    def _create_bottleneck_detection(self, bottleneck_type: str, affected_components: List[str],
                                   severity_score: float, impact_description: str,
                                   suggested_optimizations: List[str]):
        """ボトルネック検出作成"""
        detection_id = f"bottleneck_{bottleneck_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        detection = BottleneckDetection(
            detection_id=detection_id,
            bottleneck_type=bottleneck_type,
            affected_components=affected_components,
            severity_score=severity_score,
            impact_description=impact_description,
            suggested_optimizations=suggested_optimizations,
            detection_confidence=0.8,  # デフォルト信頼度
            detected_at=datetime.now().isoformat()
        )
        
        self.bottleneck_detections[detection_id] = detection
        print(f"[パフォーマンス監視] ボトルネック検出: {impact_description}")
    
    def _determine_severity(self, current_value: float, threshold: float) -> str:
        """重要度決定"""
        ratio = current_value / threshold
        
        if ratio > 1.5:
            return "critical"
        elif ratio > 1.3:
            return "high"
        elif ratio > 1.1:
            return "medium"
        else:
            return "low"
    
    def performance_decorator(self, func: Callable) -> Callable:
        """パフォーマンス計測デコレータ"""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            func_key = f"{func.__module__}.{func.__name__}"
            start_time = time.time()
            start_memory = self._get_memory_usage()
            
            try:
                result = func(*args, **kwargs)
                error_occurred = False
            except Exception as e:
                error_occurred = True
                raise
            finally:
                end_time = time.time()
                execution_time = end_time - start_time
                end_memory = self._get_memory_usage()
                memory_delta = end_memory - start_memory if start_memory is not None and end_memory is not None else None
                
                # パフォーマンスデータ更新
                self._update_function_performance(func_key, execution_time, memory_delta, error_occurred)
            
            return result
        
        return wrapper
    
    def _get_memory_usage(self) -> Optional[float]:
        """現在のメモリ使用量取得（MB）"""
        try:
            process = psutil.Process()
            return process.memory_info().rss / (1024 * 1024)  # バイトからMBに変換
        except:
            return None
    
    def _update_function_performance(self, func_key: str, execution_time: float, 
                                   memory_delta: Optional[float], error_occurred: bool):
        """関数パフォーマンス更新"""
        if func_key in self.function_performance:
            perf = self.function_performance[func_key]
            
            # 統計更新
            perf.call_count += 1
            perf.total_time += execution_time
            perf.average_time = perf.total_time / perf.call_count
            perf.min_time = min(perf.min_time, execution_time)
            perf.max_time = max(perf.max_time, execution_time)
            perf.last_called = datetime.now().isoformat()
            
            if memory_delta is not None:
                if perf.memory_usage is None:
                    perf.memory_usage = memory_delta
                else:
                    perf.memory_usage = (perf.memory_usage + memory_delta) / 2  # 移動平均
            
            if error_occurred:
                perf.error_count += 1
        
        else:
            # 新しい関数パフォーマンス記録
            module_name, function_name = func_key.rsplit('.', 1) if '.' in func_key else ('unknown', func_key)
            
            self.function_performance[func_key] = FunctionPerformance(
                function_name=function_name,
                module_name=module_name,
                call_count=1,
                total_time=execution_time,
                average_time=execution_time,
                min_time=execution_time,
                max_time=execution_time,
                last_called=datetime.now().isoformat(),
                memory_usage=memory_delta,
                error_count=1 if error_occurred else 0
            )
    
    def get_performance_dashboard(self) -> Dict[str, Any]:
        """パフォーマンスダッシュボードデータ取得"""
        dashboard = {
            "system_status": {},
            "recent_alerts": [],
            "bottlenecks": [],
            "top_slow_functions": [],
            "resource_trends": {},
            "recommendations": []
        }
        
        try:
            # システム状態
            if self.system_snapshots:
                latest_snapshot = self.system_snapshots[-1]
                dashboard["system_status"] = {
                    "cpu_usage": latest_snapshot.cpu_usage,
                    "memory_usage": latest_snapshot.memory_usage,
                    "disk_usage": latest_snapshot.disk_usage,
                    "active_processes": latest_snapshot.active_processes,
                    "timestamp": latest_snapshot.timestamp
                }
            
            # 最近のアラート
            recent_alerts = sorted(
                [alert for alert in self.performance_alerts.values() if not alert.resolved_at],
                key=lambda x: x.detected_at,
                reverse=True
            )[:5]
            
            dashboard["recent_alerts"] = [
                {
                    "severity": alert.severity,
                    "component": alert.component,
                    "description": alert.description,
                    "detected_at": alert.detected_at
                }
                for alert in recent_alerts
            ]
            
            # ボトルネック
            recent_bottlenecks = sorted(
                self.bottleneck_detections.values(),
                key=lambda x: x.severity_score,
                reverse=True
            )[:3]
            
            dashboard["bottlenecks"] = [
                {
                    "type": bottleneck.bottleneck_type,
                    "severity": bottleneck.severity_score,
                    "description": bottleneck.impact_description,
                    "optimizations": bottleneck.suggested_optimizations[:2]
                }
                for bottleneck in recent_bottlenecks
            ]
            
            # 遅い関数トップ5
            slow_functions = sorted(
                self.function_performance.values(),
                key=lambda x: x.average_time,
                reverse=True
            )[:5]
            
            dashboard["top_slow_functions"] = [
                {
                    "function": f"{func.module_name}.{func.function_name}",
                    "average_time": func.average_time,
                    "call_count": func.call_count,
                    "error_rate": func.error_count / func.call_count if func.call_count > 0 else 0
                }
                for func in slow_functions
            ]
            
            # リソーストレンド
            if len(self.system_snapshots) >= 2:
                snapshots = list(self.system_snapshots)
                dashboard["resource_trends"] = {
                    "cpu_trend": self._calculate_trend([s.cpu_usage for s in snapshots[-10:]]),
                    "memory_trend": self._calculate_trend([s.memory_usage for s in snapshots[-10:]]),
                    "disk_trend": self._calculate_trend([s.disk_usage for s in snapshots[-10:]])
                }
            
            # 推奨事項生成
            dashboard["recommendations"] = self._generate_performance_recommendations()
        
        except Exception as e:
            dashboard["error"] = f"ダッシュボード生成エラー: {str(e)}"
        
        return dashboard
    
    def _calculate_trend(self, values: List[float]) -> str:
        """トレンド計算"""
        if len(values) < 2:
            return "stable"
        
        recent_avg = mean(values[-3:]) if len(values) >= 3 else values[-1]
        past_avg = mean(values[:-3]) if len(values) >= 6 else mean(values[:-1])
        
        change_percent = ((recent_avg - past_avg) / past_avg) * 100 if past_avg > 0 else 0
        
        if change_percent > 10:
            return "increasing"
        elif change_percent < -10:
            return "decreasing"
        else:
            return "stable"
    
    def _generate_performance_recommendations(self) -> List[str]:
        """パフォーマンス推奨事項生成"""
        recommendations = []
        
        # アクティブアラートに基づく推奨事項
        active_alerts = [alert for alert in self.performance_alerts.values() if not alert.resolved_at]
        
        if any(alert.severity == "critical" for alert in active_alerts):
            recommendations.append("クリティカルなパフォーマンス問題があります。即座に対応してください。")
        
        # ボトルネックに基づく推奨事項
        if self.bottleneck_detections:
            recent_bottlenecks = sorted(
                self.bottleneck_detections.values(),
                key=lambda x: x.detected_at,
                reverse=True
            )[:3]
            
            for bottleneck in recent_bottlenecks:
                if bottleneck.suggested_optimizations:
                    recommendations.append(f"{bottleneck.bottleneck_type}ボトルネック: {bottleneck.suggested_optimizations[0]}")
        
        # 関数パフォーマンスに基づく推奨事項
        slow_functions = [f for f in self.function_performance.values() if f.average_time > 2.0]
        if slow_functions:
            recommendations.append(f"{len(slow_functions)}個の関数で性能改善の余地があります。")
        
        if not recommendations:
            recommendations.append("現在のパフォーマンスは良好です。定期的な監視を継続してください。")
        
        return recommendations

def main():
    """テスト実行"""
    print("=== パフォーマンス監視システムテスト ===")
    
    monitor = PerformanceMonitor()
    
    # システムスナップショット取得テスト
    snapshot = monitor._capture_system_snapshot()
    print(f"システムスナップショット: CPU={snapshot.cpu_usage:.1f}%, Memory={snapshot.memory_usage:.1f}%")
    
    # パフォーマンスダッシュボード取得テスト
    dashboard = monitor.get_performance_dashboard()
    print(f"ダッシュボード: {dashboard.get('system_status', {})}")
    
    # デコレータテスト用関数
    @monitor.performance_decorator
    def test_function():
        time.sleep(0.1)  # 0.1秒の処理時間をシミュレート
        return "test_result"
    
    # 関数実行
    result = test_function()
    print(f"テスト関数結果: {result}")
    
    # 関数パフォーマンス確認
    if monitor.function_performance:
        for func_key, perf in monitor.function_performance.items():
            print(f"関数パフォーマンス: {func_key} - {perf.average_time:.3f}秒")

if __name__ == "__main__":
    main()
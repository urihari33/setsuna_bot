#!/usr/bin/env python3
"""
メンテナンスユーティリティ
システムの総合的なメンテナンス機能を提供
"""

import os
import json
import shutil
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict

from logging_system import get_logger
from health_monitor import get_health_monitor
from performance_optimizer import get_performance_optimizer
from backup_system import BackupManager
from recovery_system import RecoveryManager

@dataclass
class MaintenanceTask:
    """メンテナンスタスク"""
    id: str
    name: str
    description: str
    category: str
    priority: str
    schedule: str
    last_run: Optional[str]
    next_run: Optional[str]
    status: str
    enabled: bool

@dataclass
class MaintenanceReport:
    """メンテナンスレポート"""
    timestamp: str
    task_id: str
    task_name: str
    duration: float
    success: bool
    message: str
    details: Dict[str, Any]

class MaintenanceManager:
    """メンテナンス管理システム"""
    
    def __init__(self, data_dir: str = "/mnt/d/setsuna_bot/maintenance"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.logger = get_logger()
        self.tasks_file = self.data_dir / "maintenance_tasks.json"
        self.reports_file = self.data_dir / "maintenance_reports.json"
        self.config_file = self.data_dir / "maintenance_config.json"
        
        # 設定
        self.config = {
            "auto_maintenance": True,
            "maintenance_window": "02:00-04:00",  # 深夜2時-4時
            "report_retention_days": 30,
            "notification_enabled": True,
            "emergency_maintenance_threshold": {
                "cpu_percent": 90.0,
                "memory_percent": 95.0,
                "disk_percent": 98.0,
                "error_rate": 20.0
            }
        }
        
        self.load_config()
        
        # メンテナンスタスク
        self.maintenance_tasks: List[MaintenanceTask] = []
        self.maintenance_reports: List[MaintenanceReport] = []
        
        self.initialize_default_tasks()
        self.load_tasks()
        self.load_reports()
        
        # 外部システムへの参照
        self.health_monitor = get_health_monitor()
        self.performance_optimizer = get_performance_optimizer()
        self.backup_manager = BackupManager()
        self.recovery_system = RecoveryManager(self.backup_manager)
        
        # メンテナンススレッド
        self.maintenance_thread = None
        self.stop_maintenance = False
        
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
    
    def initialize_default_tasks(self):
        """デフォルトメンテナンスタスクを初期化"""
        default_tasks = [
            MaintenanceTask(
                id="daily_backup",
                name="日次バックアップ",
                description="重要なデータファイルの日次バックアップを実行",
                category="backup",
                priority="high",
                schedule="daily:02:00",
                last_run=None,
                next_run=None,
                status="pending",
                enabled=True
            ),
            MaintenanceTask(
                id="performance_optimization",
                name="パフォーマンス最適化",
                description="キャッシュクリーンアップとメモリ最適化を実行",
                category="optimization",
                priority="medium",
                schedule="daily:03:00",
                last_run=None,
                next_run=None,
                status="pending",
                enabled=True
            ),
            MaintenanceTask(
                id="health_check",
                name="システムヘルスチェック",
                description="システムの健全性を確認し、問題があれば通知",
                category="monitoring",
                priority="high",
                schedule="hourly",
                last_run=None,
                next_run=None,
                status="pending",
                enabled=True
            ),
            MaintenanceTask(
                id="log_cleanup",
                name="ログクリーンアップ",
                description="古いログファイルを圧縮・削除",
                category="cleanup",
                priority="low",
                schedule="weekly:sunday:01:00",
                last_run=None,
                next_run=None,
                status="pending",
                enabled=True
            ),
            MaintenanceTask(
                id="integrity_check",
                name="データ整合性チェック",
                description="データファイルの整合性を検証",
                category="verification",
                priority="medium",
                schedule="weekly:friday:23:00",
                last_run=None,
                next_run=None,
                status="pending",
                enabled=True
            ),
            MaintenanceTask(
                id="cache_verification",
                name="キャッシュ検証",
                description="キャッシュの有効性を確認し、破損データを修復",
                category="verification",
                priority="medium",
                schedule="daily:04:00",
                last_run=None,
                next_run=None,
                status="pending",
                enabled=True
            )
        ]
        
        self.maintenance_tasks = default_tasks
    
    def load_tasks(self):
        """メンテナンスタスクを読み込み"""
        try:
            if self.tasks_file.exists():
                with open(self.tasks_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    loaded_tasks = [
                        MaintenanceTask(**task) for task in data.get('tasks', [])
                    ]
                    
                    # 既存タスクをアップデート
                    for loaded_task in loaded_tasks:
                        for i, existing_task in enumerate(self.maintenance_tasks):
                            if existing_task.id == loaded_task.id:
                                self.maintenance_tasks[i] = loaded_task
                                break
                        else:
                            # 新しいタスクを追加
                            self.maintenance_tasks.append(loaded_task)
                            
        except Exception as e:
            self.logger.warning(f"タスク読み込みエラー: {e}")
    
    def save_tasks(self):
        """メンテナンスタスクを保存"""
        try:
            tasks_data = {
                'tasks': [asdict(task) for task in self.maintenance_tasks],
                'last_updated': datetime.now().isoformat()
            }
            with open(self.tasks_file, 'w', encoding='utf-8') as f:
                json.dump(tasks_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"タスク保存エラー: {e}")
    
    def load_reports(self):
        """メンテナンスレポートを読み込み"""
        try:
            if self.reports_file.exists():
                with open(self.reports_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.maintenance_reports = [
                        MaintenanceReport(**report) for report in data.get('reports', [])
                    ]
        except Exception as e:
            self.logger.warning(f"レポート読み込みエラー: {e}")
    
    def save_reports(self):
        """メンテナンスレポートを保存"""
        try:
            reports_data = {
                'reports': [asdict(report) for report in self.maintenance_reports],
                'last_updated': datetime.now().isoformat()
            }
            with open(self.reports_file, 'w', encoding='utf-8') as f:
                json.dump(reports_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"レポート保存エラー: {e}")
    
    def calculate_next_run(self, task: MaintenanceTask) -> Optional[str]:
        """次回実行時刻を計算"""
        try:
            now = datetime.now()
            schedule = task.schedule
            
            if schedule == "hourly":
                next_run = now + timedelta(hours=1)
            elif schedule.startswith("daily:"):
                time_str = schedule.split(":")[1] + ":" + schedule.split(":")[2]
                hour, minute = map(int, time_str.split(":"))
                next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                if next_run <= now:
                    next_run += timedelta(days=1)
            elif schedule.startswith("weekly:"):
                parts = schedule.split(":")
                weekday = parts[1]  # sunday, monday, etc.
                time_str = parts[2] + ":" + parts[3]
                hour, minute = map(int, time_str.split(":"))
                
                # 曜日マッピング
                weekdays = {
                    "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
                    "friday": 4, "saturday": 5, "sunday": 6
                }
                
                target_weekday = weekdays.get(weekday, 0)
                days_ahead = target_weekday - now.weekday()
                if days_ahead <= 0:
                    days_ahead += 7
                
                next_run = now + timedelta(days=days_ahead)
                next_run = next_run.replace(hour=hour, minute=minute, second=0, microsecond=0)
            else:
                # 不明なスケジュール形式
                return None
            
            return next_run.isoformat()
            
        except Exception as e:
            self.logger.error(f"次回実行時刻計算エラー ({task.id}): {e}")
            return None
    
    def is_maintenance_window(self) -> bool:
        """メンテナンス時間帯かどうかを判定"""
        try:
            now = datetime.now()
            window = self.config['maintenance_window']
            start_time, end_time = window.split('-')
            
            start_hour, start_minute = map(int, start_time.split(':'))
            end_hour, end_minute = map(int, end_time.split(':'))
            
            current_time = now.time()
            start = datetime.time(start_hour, start_minute)
            end = datetime.time(end_hour, end_minute)
            
            if start <= end:
                return start <= current_time <= end
            else:
                # 深夜を跨ぐ場合（例：23:00-01:00）
                return current_time >= start or current_time <= end
            
        except Exception as e:
            self.logger.error(f"メンテナンス時間判定エラー: {e}")
            return False
    
    def execute_task(self, task: MaintenanceTask) -> MaintenanceReport:
        """メンテナンスタスクを実行"""
        start_time = time.time()
        
        try:
            self.logger.info(f"メンテナンスタスク開始: {task.name}")
            
            details = {}
            success = False
            message = ""
            
            if task.id == "daily_backup":
                # バックアップ実行
                backup_result = self.backup_manager.create_backup()
                success = backup_result.get("success", False)
                message = backup_result.get("message", "")
                details = backup_result
                
            elif task.id == "performance_optimization":
                # パフォーマンス最適化実行
                optimization_results = self.performance_optimizer.run_full_optimization()
                success = all(result.success for result in optimization_results)
                message = f"{len(optimization_results)}個の最適化タスクを実行"
                details = {"results": [asdict(result) for result in optimization_results]}
                
            elif task.id == "health_check":
                # ヘルスチェック実行
                health_summary = self.health_monitor.get_system_health_summary()
                success = health_summary.get("status") != "ERROR"
                message = f"システム状態: {health_summary.get('status', 'UNKNOWN')}"
                details = health_summary
                
            elif task.id == "log_cleanup":
                # ログクリーンアップ実行
                cleanup_result = self.cleanup_old_logs()
                success = cleanup_result.get("success", False)
                message = cleanup_result.get("message", "")
                details = cleanup_result
                
            elif task.id == "integrity_check":
                # データ整合性チェック実行
                integrity_result = self.check_data_integrity()
                success = integrity_result.get("success", False)
                message = integrity_result.get("message", "")
                details = integrity_result
                
            elif task.id == "cache_verification":
                # キャッシュ検証実行
                cache_result = self.verify_cache_integrity()
                success = cache_result.get("success", False)
                message = cache_result.get("message", "")
                details = cache_result
                
            else:
                success = False
                message = f"未知のタスク: {task.id}"
            
            # タスクの状態を更新
            task.last_run = datetime.now().isoformat()
            task.next_run = self.calculate_next_run(task)
            task.status = "completed" if success else "failed"
            
            duration = time.time() - start_time
            
            report = MaintenanceReport(
                timestamp=datetime.now().isoformat(),
                task_id=task.id,
                task_name=task.name,
                duration=duration,
                success=success,
                message=message,
                details=details
            )
            
            self.maintenance_reports.append(report)
            self.logger.info(f"メンテナンスタスク完了: {task.name} ({duration:.2f}秒)")
            
            return report
            
        except Exception as e:
            duration = time.time() - start_time
            error_message = f"メンテナンスタスクエラー: {e}"
            
            task.status = "failed"
            task.last_run = datetime.now().isoformat()
            task.next_run = self.calculate_next_run(task)
            
            report = MaintenanceReport(
                timestamp=datetime.now().isoformat(),
                task_id=task.id,
                task_name=task.name,
                duration=duration,
                success=False,
                message=error_message,
                details={"error": str(e)}
            )
            
            self.maintenance_reports.append(report)
            self.logger.error(error_message)
            
            return report
    
    def cleanup_old_logs(self) -> Dict[str, Any]:
        """古いログファイルをクリーンアップ"""
        try:
            cleaned_files = 0
            total_size_freed = 0
            
            # ログディレクトリ
            log_dirs = [
                Path("/mnt/d/setsuna_bot/logs"),
                Path("/mnt/d/setsuna_bot/monitoring"),
                Path("/mnt/d/setsuna_bot/maintenance")
            ]
            
            cutoff_date = datetime.now() - timedelta(days=self.config['report_retention_days'])
            
            for log_dir in log_dirs:
                if log_dir.exists():
                    for log_file in log_dir.glob("*.log"):
                        try:
                            file_mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                            if file_mtime < cutoff_date:
                                file_size = log_file.stat().st_size
                                log_file.unlink()
                                cleaned_files += 1
                                total_size_freed += file_size
                        except Exception as e:
                            self.logger.warning(f"ログファイル削除エラー ({log_file}): {e}")
            
            return {
                "success": True,
                "message": f"ログクリーンアップ完了: {cleaned_files}ファイル削除",
                "cleaned_files": cleaned_files,
                "size_freed": total_size_freed
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"ログクリーンアップエラー: {e}",
                "error": str(e)
            }
    
    def check_data_integrity(self) -> Dict[str, Any]:
        """データ整合性をチェック"""
        try:
            integrity_results = []
            
            # 重要なデータファイル
            data_files = [
                "/mnt/d/setsuna_bot/character/setsuna_memory_data.json",
                "/mnt/d/setsuna_bot/data/user_preferences.json",
                "/mnt/d/setsuna_bot/response_cache/response_cache.json",
                "/mnt/d/setsuna_bot/youtube_knowledge_system/data/unified_knowledge_db.json"
            ]
            
            for file_path in data_files:
                file_path = Path(file_path)
                if file_path.exists():
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            json.load(f)  # JSON形式の検証
                        integrity_results.append({
                            "file": str(file_path),
                            "status": "ok",
                            "message": "整合性OK"
                        })
                    except json.JSONDecodeError as e:
                        integrity_results.append({
                            "file": str(file_path),
                            "status": "error",
                            "message": f"JSON形式エラー: {e}"
                        })
                else:
                    integrity_results.append({
                        "file": str(file_path),
                        "status": "missing",
                        "message": "ファイルが存在しません"
                    })
            
            error_count = sum(1 for result in integrity_results if result["status"] == "error")
            missing_count = sum(1 for result in integrity_results if result["status"] == "missing")
            
            return {
                "success": error_count == 0,
                "message": f"データ整合性チェック完了: {error_count}エラー, {missing_count}欠損",
                "results": integrity_results,
                "error_count": error_count,
                "missing_count": missing_count
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"データ整合性チェックエラー: {e}",
                "error": str(e)
            }
    
    def verify_cache_integrity(self) -> Dict[str, Any]:
        """キャッシュの整合性を検証"""
        try:
            cache_results = []
            
            # レスポンスキャッシュ
            response_cache_file = Path("/mnt/d/setsuna_bot/response_cache/response_cache.json")
            if response_cache_file.exists():
                try:
                    with open(response_cache_file, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                    
                    # キャッシュエントリの検証
                    valid_entries = 0
                    invalid_entries = 0
                    
                    for key, entry in cache_data.items():
                        if all(k in entry for k in ['original_input', 'response', 'created_at']):
                            valid_entries += 1
                        else:
                            invalid_entries += 1
                    
                    cache_results.append({
                        "cache_type": "response_cache",
                        "total_entries": len(cache_data),
                        "valid_entries": valid_entries,
                        "invalid_entries": invalid_entries,
                        "status": "ok" if invalid_entries == 0 else "warning"
                    })
                    
                except Exception as e:
                    cache_results.append({
                        "cache_type": "response_cache",
                        "status": "error",
                        "message": str(e)
                    })
            
            # 音声キャッシュ
            voice_cache_dir = Path("/mnt/d/setsuna_bot/voice_cache")
            if voice_cache_dir.exists():
                voice_files = list(voice_cache_dir.glob("*.wav"))
                broken_files = []
                
                for voice_file in voice_files:
                    try:
                        if voice_file.stat().st_size == 0:
                            broken_files.append(str(voice_file))
                    except Exception:
                        broken_files.append(str(voice_file))
                
                cache_results.append({
                    "cache_type": "voice_cache",
                    "total_files": len(voice_files),
                    "broken_files": len(broken_files),
                    "status": "ok" if len(broken_files) == 0 else "warning"
                })
            
            error_count = sum(1 for result in cache_results if result.get("status") == "error")
            warning_count = sum(1 for result in cache_results if result.get("status") == "warning")
            
            return {
                "success": error_count == 0,
                "message": f"キャッシュ検証完了: {error_count}エラー, {warning_count}警告",
                "results": cache_results,
                "error_count": error_count,
                "warning_count": warning_count
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"キャッシュ検証エラー: {e}",
                "error": str(e)
            }
    
    def check_emergency_maintenance_needed(self) -> bool:
        """緊急メンテナンスが必要かどうかを判定"""
        try:
            health_summary = self.health_monitor.get_system_health_summary()
            
            if health_summary.get("status") == "ERROR":
                return True
            
            metrics = health_summary.get("metrics", {})
            thresholds = self.config['emergency_maintenance_threshold']
            
            # 緊急閾値チェック
            if (metrics.get('cpu_percent', 0) >= thresholds['cpu_percent'] or
                metrics.get('memory_percent', 0) >= thresholds['memory_percent'] or
                metrics.get('disk_percent', 0) >= thresholds['disk_percent'] or
                metrics.get('error_rate', 0) >= thresholds['error_rate']):
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"緊急メンテナンス判定エラー: {e}")
            return False
    
    def run_emergency_maintenance(self) -> List[MaintenanceReport]:
        """緊急メンテナンスを実行"""
        self.logger.warning("緊急メンテナンスを開始します")
        
        emergency_reports = []
        
        # 緊急メンテナンスタスク
        emergency_tasks = [
            task for task in self.maintenance_tasks 
            if task.category in ["optimization", "cleanup"] and task.enabled
        ]
        
        for task in emergency_tasks:
            try:
                report = self.execute_task(task)
                emergency_reports.append(report)
            except Exception as e:
                self.logger.error(f"緊急メンテナンスタスクエラー ({task.id}): {e}")
        
        self.logger.warning("緊急メンテナンスが完了しました")
        return emergency_reports
    
    def get_pending_tasks(self) -> List[MaintenanceTask]:
        """実行待ちのタスクを取得"""
        now = datetime.now()
        pending_tasks = []
        
        for task in self.maintenance_tasks:
            if not task.enabled:
                continue
                
            if task.next_run is None:
                task.next_run = self.calculate_next_run(task)
            
            if task.next_run and datetime.fromisoformat(task.next_run) <= now:
                pending_tasks.append(task)
        
        return pending_tasks
    
    def run_scheduled_maintenance(self) -> List[MaintenanceReport]:
        """スケジュールされたメンテナンスを実行"""
        pending_tasks = self.get_pending_tasks()
        
        if not pending_tasks:
            return []
        
        self.logger.info(f"スケジュールメンテナンス開始: {len(pending_tasks)}タスク")
        
        reports = []
        for task in pending_tasks:
            try:
                report = self.execute_task(task)
                reports.append(report)
            except Exception as e:
                self.logger.error(f"スケジュールメンテナンスエラー ({task.id}): {e}")
        
        # データを保存
        self.save_tasks()
        self.save_reports()
        
        self.logger.info(f"スケジュールメンテナンス完了: {len(reports)}タスク実行")
        return reports
    
    def start_auto_maintenance(self):
        """自動メンテナンスを開始"""
        if not self.config['auto_maintenance']:
            self.logger.info("自動メンテナンスは無効になっています")
            return
        
        if self.maintenance_thread and self.maintenance_thread.is_alive():
            self.logger.warning("自動メンテナンスは既に開始されています")
            return
        
        self.stop_maintenance = False
        self.maintenance_thread = threading.Thread(target=self._maintenance_loop, daemon=True)
        self.maintenance_thread.start()
        
        self.logger.info("自動メンテナンス開始")
    
    def stop_auto_maintenance(self):
        """自動メンテナンスを停止"""
        self.stop_maintenance = True
        if self.maintenance_thread:
            self.maintenance_thread.join(timeout=10)
        
        self.logger.info("自動メンテナンス停止")
    
    def _maintenance_loop(self):
        """メンテナンスループ"""
        while not self.stop_maintenance:
            try:
                # 緊急メンテナンスチェック
                if self.check_emergency_maintenance_needed():
                    self.run_emergency_maintenance()
                
                # スケジュールメンテナンス
                if self.is_maintenance_window():
                    self.run_scheduled_maintenance()
                
                # 古いレポートをクリーンアップ
                self.cleanup_old_reports()
                
                # 5分間隔でチェック
                time.sleep(300)
                
            except Exception as e:
                self.logger.error(f"メンテナンスループエラー: {e}")
                time.sleep(300)
    
    def cleanup_old_reports(self):
        """古いレポートをクリーンアップ"""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.config['report_retention_days'])
            
            original_count = len(self.maintenance_reports)
            self.maintenance_reports = [
                report for report in self.maintenance_reports
                if datetime.fromisoformat(report.timestamp) > cutoff_date
            ]
            
            removed_count = original_count - len(self.maintenance_reports)
            if removed_count > 0:
                self.save_reports()
                self.logger.info(f"古いメンテナンスレポートを削除: {removed_count}件")
                
        except Exception as e:
            self.logger.error(f"レポートクリーンアップエラー: {e}")
    
    def get_maintenance_summary(self) -> Dict[str, Any]:
        """メンテナンスサマリを取得"""
        try:
            now = datetime.now()
            
            # 最近のレポート統計
            recent_reports = [
                report for report in self.maintenance_reports
                if datetime.fromisoformat(report.timestamp) > now - timedelta(days=7)
            ]
            
            success_count = sum(1 for report in recent_reports if report.success)
            
            # 次回実行予定
            next_tasks = []
            for task in self.maintenance_tasks:
                if task.enabled and task.next_run:
                    next_tasks.append({
                        "task_name": task.name,
                        "next_run": task.next_run,
                        "priority": task.priority
                    })
            
            next_tasks.sort(key=lambda x: x["next_run"])
            
            return {
                "auto_maintenance_active": self.maintenance_thread and self.maintenance_thread.is_alive(),
                "total_tasks": len(self.maintenance_tasks),
                "enabled_tasks": len([t for t in self.maintenance_tasks if t.enabled]),
                "recent_reports": len(recent_reports),
                "success_rate": (success_count / len(recent_reports)) * 100 if recent_reports else 0,
                "next_scheduled_tasks": next_tasks[:5],  # 次の5タスク
                "emergency_maintenance_needed": self.check_emergency_maintenance_needed(),
                "maintenance_window": self.config['maintenance_window'],
                "in_maintenance_window": self.is_maintenance_window()
            }
            
        except Exception as e:
            self.logger.error(f"メンテナンスサマリ取得エラー: {e}")
            return {"error": str(e)}

# グローバルインスタンス
_maintenance_manager = None

def get_maintenance_manager() -> MaintenanceManager:
    """メンテナンスマネージャーのグローバルインスタンスを取得"""
    global _maintenance_manager
    if _maintenance_manager is None:
        _maintenance_manager = MaintenanceManager()
    return _maintenance_manager

if __name__ == "__main__":
    # テスト実行
    manager = get_maintenance_manager()
    
    print("=== メンテナンスユーティリティテスト ===")
    
    # サマリ表示
    summary = manager.get_maintenance_summary()
    print(f"総タスク数: {summary['total_tasks']}")
    print(f"有効タスク数: {summary['enabled_tasks']}")
    print(f"成功率: {summary['success_rate']:.1f}%")
    print(f"緊急メンテナンス必要: {summary['emergency_maintenance_needed']}")
    
    # 実行待ちタスク確認
    pending_tasks = manager.get_pending_tasks()
    print(f"実行待ちタスク: {len(pending_tasks)}件")
    
    # 手動メンテナンス実行
    if pending_tasks:
        print("手動メンテナンス実行中...")
        reports = manager.run_scheduled_maintenance()
        print(f"実行完了: {len(reports)}タスク")
        
        for report in reports:
            status = "✅" if report.success else "❌"
            print(f"{status} {report.task_name}: {report.message}")
    
    print("テスト完了")
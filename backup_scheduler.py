#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
バックアップスケジューラー - せつなBot D案 Phase 2
定期的な自動バックアップ実行システム
"""

import threading
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Callable, Optional
from backup_system import BackupManager
from logging_system import get_logger, get_monitor


class BackupScheduler:
    """バックアップスケジューラー"""
    
    def __init__(self, backup_manager: BackupManager):
        """
        初期化
        
        Args:
            backup_manager: BackupManagerインスタンス
        """
        self.logger = get_logger()
        self.monitor = get_monitor()
        self.backup_manager = backup_manager
        
        # スケジュール設定
        self.schedules = {
            "daily": {
                "hour": 2,  # 深夜2時
                "minute": 0,
                "last_run": None,
                "enabled": True
            },
            "weekly": {
                "weekday": 0,  # 月曜日 (0=月曜, 6=日曜)
                "hour": 3,     # 深夜3時
                "minute": 0,
                "last_run": None,
                "enabled": True
            },
            "monthly": {
                "day": 1,      # 毎月1日
                "hour": 4,     # 深夜4時
                "minute": 0,
                "last_run": None,
                "enabled": True
            }
        }
        
        # スケジューラー制御
        self.running = False
        self.scheduler_thread = None
        self.check_interval = 60  # 60秒間隔でチェック
        
        self.logger.info("backup_scheduler", "__init__", "バックアップスケジューラー初期化完了")
    
    def start_scheduler(self):
        """スケジューラー開始"""
        if self.running:
            self.logger.warning("backup_scheduler", "start_scheduler", "スケジューラーは既に実行中です")
            return
        
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_worker, daemon=True)
        self.scheduler_thread.start()
        
        self.logger.info("backup_scheduler", "start_scheduler", "バックアップスケジューラー開始")
    
    def stop_scheduler(self):
        """スケジューラー停止"""
        if not self.running:
            return
        
        self.running = False
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5.0)
        
        self.logger.info("backup_scheduler", "stop_scheduler", "バックアップスケジューラー停止")
    
    def _scheduler_worker(self):
        """スケジューラーワーカースレッド"""
        self.logger.info("backup_scheduler", "_scheduler_worker", "スケジューラーワーカー開始")
        
        while self.running:
            try:
                current_time = datetime.now()
                
                # 各スケジュールをチェック
                for schedule_type, schedule_config in self.schedules.items():
                    if not schedule_config.get("enabled", True):
                        continue
                    
                    if self._should_run_backup(schedule_type, current_time):
                        self._execute_scheduled_backup(schedule_type)
                
                # 指定間隔で待機
                time.sleep(self.check_interval)
                
            except Exception as e:
                self.logger.error("backup_scheduler", "_scheduler_worker", f"スケジューラーエラー: {e}")
                time.sleep(60)  # エラー時は1分待機
    
    def _should_run_backup(self, schedule_type: str, current_time: datetime) -> bool:
        """バックアップを実行すべきかチェック"""
        schedule_config = self.schedules[schedule_type]
        last_run = schedule_config.get("last_run")
        
        # 前回実行時刻確認
        if last_run:
            # 同じ日に既に実行済みの場合はスキップ
            if last_run.date() == current_time.date() and schedule_type == "daily":
                return False
            # 週次の場合：同じ週に実行済みならスキップ
            if schedule_type == "weekly":
                week_start = current_time - timedelta(days=current_time.weekday())
                last_week_start = last_run - timedelta(days=last_run.weekday())
                if week_start.date() == last_week_start.date():
                    return False
            # 月次の場合：同じ月に実行済みならスキップ
            if schedule_type == "monthly":
                if (last_run.year == current_time.year and 
                    last_run.month == current_time.month):
                    return False
        
        # 実行時刻確認
        if schedule_type == "daily":
            target_hour = schedule_config["hour"]
            target_minute = schedule_config["minute"]
            
            return (current_time.hour == target_hour and 
                   current_time.minute == target_minute)
        
        elif schedule_type == "weekly":
            target_weekday = schedule_config["weekday"]
            target_hour = schedule_config["hour"]
            target_minute = schedule_config["minute"]
            
            return (current_time.weekday() == target_weekday and
                   current_time.hour == target_hour and
                   current_time.minute == target_minute)
        
        elif schedule_type == "monthly":
            target_day = schedule_config["day"]
            target_hour = schedule_config["hour"]
            target_minute = schedule_config["minute"]
            
            return (current_time.day == target_day and
                   current_time.hour == target_hour and
                   current_time.minute == target_minute)
        
        return False
    
    @get_monitor().monitor_function("execute_scheduled_backup")
    def _execute_scheduled_backup(self, schedule_type: str):
        """スケジュールされたバックアップを実行"""
        self.logger.info("backup_scheduler", "_execute_scheduled_backup", 
                        f"スケジュールバックアップ開始: {schedule_type}")
        
        try:
            # バックアップ実行
            backup_path = self.backup_manager.create_backup(
                backup_type=schedule_type,
                compress=True,
                verify=True
            )
            
            if backup_path:
                self.logger.info("backup_scheduler", "_execute_scheduled_backup", 
                               f"スケジュールバックアップ成功: {schedule_type}", {
                                   "backup_path": str(backup_path)
                               })
                
                # 実行時刻記録
                self.schedules[schedule_type]["last_run"] = datetime.now()
                
                # 古いバックアップクリーンアップ
                if schedule_type == "daily":
                    retention_days = 7  # 日次は1週間保持
                elif schedule_type == "weekly":
                    retention_days = 30  # 週次は1ヶ月保持
                elif schedule_type == "monthly":
                    retention_days = 90  # 月次は3ヶ月保持
                else:
                    retention_days = 30
                
                self._cleanup_old_backups(schedule_type, retention_days)
                
            else:
                self.logger.error("backup_scheduler", "_execute_scheduled_backup", 
                                f"スケジュールバックアップ失敗: {schedule_type}")
        
        except Exception as e:
            self.logger.error("backup_scheduler", "_execute_scheduled_backup", 
                            f"スケジュールバックアップエラー: {schedule_type}", {
                                "error": str(e)
                            })
    
    def _cleanup_old_backups(self, backup_type: str, retention_days: int):
        """指定タイプの古いバックアップを削除"""
        try:
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            deleted_count = 0
            
            backup_type_dir = self.backup_manager.backup_dir / backup_type
            if not backup_type_dir.exists():
                return
            
            for item in backup_type_dir.iterdir():
                item_time = datetime.fromtimestamp(item.stat().st_mtime)
                
                if item_time < cutoff_date:
                    if item.is_dir():
                        import shutil
                        shutil.rmtree(item)
                    else:
                        item.unlink()
                    
                    deleted_count += 1
                    self.logger.info("backup_scheduler", "_cleanup_old_backups", 
                                   f"古い{backup_type}バックアップ削除: {item.name}")
            
            if deleted_count > 0:
                self.logger.info("backup_scheduler", "_cleanup_old_backups", 
                               f"{backup_type}バックアップクリーンアップ完了: {deleted_count}件削除")
        
        except Exception as e:
            self.logger.error("backup_scheduler", "_cleanup_old_backups", 
                            f"クリーンアップエラー: {backup_type}", {"error": str(e)})
    
    def force_backup(self, backup_type: str = "manual") -> bool:
        """手動でバックアップを強制実行"""
        self.logger.info("backup_scheduler", "force_backup", f"手動バックアップ実行: {backup_type}")
        
        try:
            backup_path = self.backup_manager.create_backup(
                backup_type=backup_type,
                compress=True,
                verify=True
            )
            
            if backup_path:
                self.logger.info("backup_scheduler", "force_backup", "手動バックアップ成功", {
                    "backup_path": str(backup_path)
                })
                return True
            else:
                self.logger.error("backup_scheduler", "force_backup", "手動バックアップ失敗")
                return False
        
        except Exception as e:
            self.logger.error("backup_scheduler", "force_backup", f"手動バックアップエラー: {e}")
            return False
    
    def update_schedule(self, schedule_type: str, **kwargs):
        """スケジュール設定を更新"""
        if schedule_type not in self.schedules:
            self.logger.error("backup_scheduler", "update_schedule", 
                            f"不正なスケジュールタイプ: {schedule_type}")
            return
        
        for key, value in kwargs.items():
            if key in self.schedules[schedule_type]:
                self.schedules[schedule_type][key] = value
        
        self.logger.info("backup_scheduler", "update_schedule", 
                        f"スケジュール更新: {schedule_type}", kwargs)
    
    def get_schedule_status(self) -> Dict[str, Any]:
        """スケジュール状況を取得"""
        status = {
            "running": self.running,
            "schedules": {}
        }
        
        for schedule_type, config in self.schedules.items():
            last_run = config.get("last_run")
            status["schedules"][schedule_type] = {
                "enabled": config.get("enabled", True),
                "last_run": last_run.isoformat() if last_run else None,
                "config": {k: v for k, v in config.items() if k != "last_run"}
            }
        
        return status
    
    def get_next_backup_times(self) -> Dict[str, Optional[datetime]]:
        """次回バックアップ予定時刻を取得"""
        next_times = {}
        current_time = datetime.now()
        
        for schedule_type, config in self.schedules.items():
            if not config.get("enabled", True):
                next_times[schedule_type] = None
                continue
            
            try:
                if schedule_type == "daily":
                    next_time = current_time.replace(
                        hour=config["hour"], 
                        minute=config["minute"], 
                        second=0, 
                        microsecond=0
                    )
                    if next_time <= current_time:
                        next_time += timedelta(days=1)
                
                elif schedule_type == "weekly":
                    days_ahead = config["weekday"] - current_time.weekday()
                    if days_ahead <= 0:  # 今週はもう過ぎている
                        days_ahead += 7
                    
                    next_time = current_time + timedelta(days=days_ahead)
                    next_time = next_time.replace(
                        hour=config["hour"],
                        minute=config["minute"],
                        second=0,
                        microsecond=0
                    )
                
                elif schedule_type == "monthly":
                    next_time = current_time.replace(
                        day=config["day"],
                        hour=config["hour"],
                        minute=config["minute"],
                        second=0,
                        microsecond=0
                    )
                    if next_time <= current_time:
                        # 次月の同日
                        if current_time.month == 12:
                            next_time = next_time.replace(year=current_time.year + 1, month=1)
                        else:
                            next_time = next_time.replace(month=current_time.month + 1)
                
                next_times[schedule_type] = next_time
                
            except Exception as e:
                self.logger.error("backup_scheduler", "get_next_backup_times", 
                                f"次回時刻計算エラー: {schedule_type}", {"error": str(e)})
                next_times[schedule_type] = None
        
        return next_times


# テスト用関数
if __name__ == "__main__":
    print("🧪 バックアップスケジューラーテスト開始")
    
    # バックアップマネージャー初期化
    backup_manager = BackupManager()
    
    # スケジューラー初期化
    scheduler = BackupScheduler(backup_manager)
    
    try:
        # スケジュール状況確認
        status = scheduler.get_schedule_status()
        print("📋 スケジュール状況:")
        for schedule_type, schedule_info in status["schedules"].items():
            enabled = "有効" if schedule_info["enabled"] else "無効"
            last_run = schedule_info["last_run"] or "未実行"
            print(f"   - {schedule_type}: {enabled}, 前回実行: {last_run}")
        
        # 次回実行予定確認
        next_times = scheduler.get_next_backup_times()
        print("\n⏰ 次回実行予定:")
        for schedule_type, next_time in next_times.items():
            if next_time:
                print(f"   - {schedule_type}: {next_time.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                print(f"   - {schedule_type}: 無効")
        
        # 手動バックアップテスト
        print("\n📦 手動バックアップテスト実行中...")
        success = scheduler.force_backup("manual_test")
        
        if success:
            print("✅ 手動バックアップ成功")
        else:
            print("❌ 手動バックアップ失敗")
        
        print("✅ スケジューラーテスト完了")
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
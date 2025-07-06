#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
システム管理統合モジュール - せつなBot D案
ログシステム・バックアップシステムの統合管理
"""

import atexit
import signal
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from logging_system import get_logger, get_monitor, cleanup_logging
from backup_system import BackupManager
from backup_scheduler import BackupScheduler
from recovery_system import RecoveryManager
from log_rotation import LogRotationManager
from health_monitor import get_health_monitor
from performance_optimizer import get_performance_optimizer
from maintenance_utilities import get_maintenance_manager


class SetsunaSystemManager:
    """せつなBotシステム統合管理クラス"""
    
    def __init__(self):
        """初期化"""
        self.logger = get_logger()
        self.monitor = get_monitor()
        
        # システムコンポーネント初期化
        self.backup_manager = None
        self.backup_scheduler = None
        self.recovery_manager = None
        self.log_rotation_manager = None
        
        # Phase 3 コンポーネント
        self.health_monitor = None
        self.performance_optimizer = None
        self.maintenance_manager = None
        
        # システム状態
        self.initialized = False
        self.running = False
        
        self.logger.info("system_manager", "__init__", "システム管理初期化開始")
        
        # シャットダウン処理登録
        atexit.register(self.cleanup)
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def initialize_systems(self) -> bool:
        """全システムコンポーネントを初期化"""
        try:
            self.logger.info("system_manager", "initialize_systems", "システムコンポーネント初期化開始")
            
            # バックアップマネージャー初期化
            self.backup_manager = BackupManager()
            self.logger.info("system_manager", "initialize_systems", "バックアップマネージャー初期化完了")
            
            # バックアップスケジューラー初期化
            self.backup_scheduler = BackupScheduler(self.backup_manager)
            self.logger.info("system_manager", "initialize_systems", "バックアップスケジューラー初期化完了")
            
            # 復旧マネージャー初期化
            self.recovery_manager = RecoveryManager(self.backup_manager)
            self.logger.info("system_manager", "initialize_systems", "復旧マネージャー初期化完了")
            
            # ログローテーションマネージャー初期化
            self.log_rotation_manager = LogRotationManager()
            self.logger.info("system_manager", "initialize_systems", "ログローテーションマネージャー初期化完了")
            
            # Phase 3 コンポーネント初期化
            self.health_monitor = get_health_monitor()
            self.logger.info("system_manager", "initialize_systems", "ヘルスモニター初期化完了")
            
            self.performance_optimizer = get_performance_optimizer()
            self.logger.info("system_manager", "initialize_systems", "パフォーマンス最適化初期化完了")
            
            self.maintenance_manager = get_maintenance_manager()
            self.logger.info("system_manager", "initialize_systems", "メンテナンス管理初期化完了")
            
            self.initialized = True
            self.logger.info("system_manager", "initialize_systems", "全システムコンポーネント初期化完了")
            
            return True
            
        except Exception as e:
            self.logger.error("system_manager", "initialize_systems", f"システム初期化エラー: {e}")
            return False
    
    def start_services(self) -> bool:
        """バックグラウンドサービス開始"""
        if not self.initialized:
            self.logger.error("system_manager", "start_services", "システムが初期化されていません")
            return False
        
        try:
            self.logger.info("system_manager", "start_services", "バックグラウンドサービス開始")
            
            # バックアップスケジューラー開始
            self.backup_scheduler.start_scheduler()
            
            # ログローテーション開始
            self.log_rotation_manager.start_background_rotation(check_interval_minutes=60)
            
            # Phase 3 サービス開始
            self.health_monitor.start_monitoring()
            self.performance_optimizer.start_auto_optimization()
            self.maintenance_manager.start_auto_maintenance()
            
            self.running = True
            self.logger.info("system_manager", "start_services", "全サービス開始完了")
            
            return True
            
        except Exception as e:
            self.logger.error("system_manager", "start_services", f"サービス開始エラー: {e}")
            return False
    
    def stop_services(self):
        """バックグラウンドサービス停止"""
        if not self.running:
            return
        
        try:
            self.logger.info("system_manager", "stop_services", "バックグラウンドサービス停止中")
            
            # バックアップスケジューラー停止
            if self.backup_scheduler:
                self.backup_scheduler.stop_scheduler()
            
            # ログローテーション停止
            if self.log_rotation_manager:
                self.log_rotation_manager.stop_background_rotation()
            
            # Phase 3 サービス停止
            if self.health_monitor:
                self.health_monitor.stop_monitoring_service()
            
            if self.performance_optimizer:
                self.performance_optimizer.stop_auto_optimization()
            
            if self.maintenance_manager:
                self.maintenance_manager.stop_auto_maintenance()
            
            self.running = False
            self.logger.info("system_manager", "stop_services", "全サービス停止完了")
            
        except Exception as e:
            self.logger.error("system_manager", "stop_services", f"サービス停止エラー: {e}")
    
    def create_emergency_backup(self, reason: str = "emergency") -> Optional[Path]:
        """緊急バックアップを作成"""
        if not self.backup_manager:
            self.logger.error("system_manager", "create_emergency_backup", "バックアップマネージャーが初期化されていません")
            return None
        
        try:
            self.logger.warning("system_manager", "create_emergency_backup", f"緊急バックアップ作成: {reason}")
            
            backup_path = self.backup_manager.create_backup(
                backup_type=f"emergency_{reason}",
                compress=True,
                verify=True
            )
            
            if backup_path:
                self.logger.info("system_manager", "create_emergency_backup", 
                               f"緊急バックアップ作成成功: {backup_path.name}")
            else:
                self.logger.error("system_manager", "create_emergency_backup", "緊急バックアップ作成失敗")
            
            return backup_path
            
        except Exception as e:
            self.logger.error("system_manager", "create_emergency_backup", f"緊急バックアップエラー: {e}")
            return None
    
    def get_system_status(self) -> Dict[str, Any]:
        """システム全体の状況を取得"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "initialized": self.initialized,
            "running": self.running,
            "components": {}
        }
        
        try:
            # ログシステム状況
            if self.log_rotation_manager:
                log_stats = self.log_rotation_manager.get_log_statistics()
                status["components"]["logging"] = {
                    "log_files": log_stats.get("total_files", 0),
                    "total_size_mb": log_stats.get("total_size_mb", 0),
                    "oldest_file": log_stats.get("oldest_file"),
                    "newest_file": log_stats.get("newest_file")
                }
            
            # バックアップシステム状況
            if self.backup_manager and self.backup_scheduler:
                backups = self.backup_manager.list_backups()
                schedule_status = self.backup_scheduler.get_schedule_status()
                next_times = self.backup_scheduler.get_next_backup_times()
                
                status["components"]["backup"] = {
                    "total_backups": len(backups),
                    "latest_backup": backups[0] if backups else None,
                    "scheduler_running": schedule_status.get("running", False),
                    "next_scheduled": {
                        schedule_type: next_time.isoformat() if next_time else None
                        for schedule_type, next_time in next_times.items()
                    }
                }
            
            # パフォーマンス統計
            if self.monitor:
                perf_report = self.logger.get_performance_report()
                system_metrics = self.monitor.get_system_metrics()
                
                status["components"]["performance"] = {
                    "monitored_functions": len(perf_report.get("functions", {})),
                    "cpu_percent": system_metrics.get("cpu_percent"),
                    "memory_percent": system_metrics.get("memory_info", {}).get("percent"),
                    "thread_count": system_metrics.get("thread_count")
                }
            
            # Phase 3 コンポーネント状況
            if self.health_monitor:
                health_summary = self.health_monitor.get_system_health_summary()
                status["components"]["health_monitor"] = {
                    "monitoring_active": health_summary.get("monitoring_active", False),
                    "system_status": health_summary.get("status", "UNKNOWN"),
                    "total_metrics": health_summary.get("total_metrics", 0),
                    "recent_alerts": health_summary.get("recent_alerts", {})
                }
            
            if self.performance_optimizer:
                optimization_summary = self.performance_optimizer.get_optimization_summary()
                status["components"]["performance_optimizer"] = {
                    "auto_optimization_active": optimization_summary.get("auto_optimization_active", False),
                    "total_optimizations": optimization_summary.get("total_optimizations", 0),
                    "success_rate": optimization_summary.get("success_rate", 0),
                    "last_optimization": optimization_summary.get("last_optimization")
                }
            
            if self.maintenance_manager:
                maintenance_summary = self.maintenance_manager.get_maintenance_summary()
                status["components"]["maintenance"] = {
                    "auto_maintenance_active": maintenance_summary.get("auto_maintenance_active", False),
                    "total_tasks": maintenance_summary.get("total_tasks", 0),
                    "enabled_tasks": maintenance_summary.get("enabled_tasks", 0),
                    "success_rate": maintenance_summary.get("success_rate", 0),
                    "emergency_maintenance_needed": maintenance_summary.get("emergency_maintenance_needed", False)
                }
            
            return status
            
        except Exception as e:
            self.logger.error("system_manager", "get_system_status", f"ステータス取得エラー: {e}")
            status["error"] = str(e)
            return status
    
    def perform_health_check(self) -> Dict[str, Any]:
        """システムヘルスチェック実行"""
        health_check = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "healthy",
            "checks": {}
        }
        
        issues = []
        
        try:
            # ログシステムチェック
            if self.log_rotation_manager:
                log_stats = self.log_rotation_manager.get_log_statistics()
                log_size_mb = log_stats.get("total_size_mb", 0)
                
                if log_size_mb > 100:  # 100MB超過
                    issues.append("ログファイルサイズが大きすぎます")
                    health_check["checks"]["logging"] = "warning"
                else:
                    health_check["checks"]["logging"] = "healthy"
            
            # バックアップシステムチェック
            if self.backup_manager:
                backups = self.backup_manager.list_backups()
                
                if not backups:
                    issues.append("利用可能なバックアップがありません")
                    health_check["checks"]["backup"] = "error"
                else:
                    latest_backup = backups[0]
                    backup_age = datetime.now() - datetime.fromisoformat(latest_backup["created_at"])
                    
                    if backup_age.days > 7:
                        issues.append(f"最新バックアップが{backup_age.days}日前です")
                        health_check["checks"]["backup"] = "warning"
                    else:
                        health_check["checks"]["backup"] = "healthy"
            
            # パフォーマンスチェック
            if self.monitor:
                system_metrics = self.monitor.get_system_metrics()
                memory_percent = system_metrics.get("memory_info", {}).get("percent", 0)
                
                if memory_percent > 80:
                    issues.append(f"メモリ使用率が高いです: {memory_percent:.1f}%")
                    health_check["checks"]["performance"] = "warning"
                else:
                    health_check["checks"]["performance"] = "healthy"
            
            # 全体ステータス決定
            if any(status == "error" for status in health_check["checks"].values()):
                health_check["overall_status"] = "error"
            elif any(status == "warning" for status in health_check["checks"].values()):
                health_check["overall_status"] = "warning"
            
            health_check["issues"] = issues
            
            self.logger.info("system_manager", "perform_health_check", 
                           f"ヘルスチェック完了: {health_check['overall_status']}")
            
            return health_check
            
        except Exception as e:
            self.logger.error("system_manager", "perform_health_check", f"ヘルスチェックエラー: {e}")
            health_check["overall_status"] = "error"
            health_check["error"] = str(e)
            return health_check
    
    def cleanup(self):
        """システムクリーンアップ"""
        if not self.initialized:
            return
        
        try:
            self.logger.info("system_manager", "cleanup", "システムクリーンアップ開始")
            
            # サービス停止
            self.stop_services()
            
            # ログシステムクリーンアップ
            cleanup_logging()
            
            self.logger.info("system_manager", "cleanup", "システムクリーンアップ完了")
            
        except Exception as e:
            print(f"❌ [SystemManager] クリーンアップエラー: {e}")
    
    def _signal_handler(self, signum, frame):
        """シグナルハンドラー"""
        self.logger.info("system_manager", "_signal_handler", f"シグナル受信: {signum}")
        self.cleanup()
        sys.exit(0)


# グローバルシステムマネージャー
_system_manager: Optional[SetsunaSystemManager] = None


def get_system_manager() -> SetsunaSystemManager:
    """グローバルシステムマネージャーを取得"""
    global _system_manager
    if _system_manager is None:
        _system_manager = SetsunaSystemManager()
    return _system_manager


def initialize_setsuna_systems() -> bool:
    """せつなBotの全システムを初期化"""
    manager = get_system_manager()
    return manager.initialize_systems()


def start_setsuna_services() -> bool:
    """せつなBotのバックグラウンドサービスを開始"""
    manager = get_system_manager()
    return manager.start_services()


# テスト用関数
if __name__ == "__main__":
    print("🧪 システム管理統合テスト開始")
    
    try:
        # システムマネージャー取得
        manager = get_system_manager()
        
        # システム初期化
        print("🔧 システム初期化中...")
        if manager.initialize_systems():
            print("✅ システム初期化成功")
        else:
            print("❌ システム初期化失敗")
            sys.exit(1)
        
        # サービス開始
        print("🚀 サービス開始中...")
        if manager.start_services():
            print("✅ サービス開始成功")
        else:
            print("❌ サービス開始失敗")
            sys.exit(1)
        
        # システム状況確認
        print("\n📊 システム状況:")
        status = manager.get_system_status()
        print(f"   - 初期化済み: {status['initialized']}")
        print(f"   - 稼働中: {status['running']}")
        
        if "backup" in status["components"]:
            backup_info = status["components"]["backup"]
            print(f"   - バックアップ総数: {backup_info['total_backups']}")
            print(f"   - スケジューラー稼働: {backup_info['scheduler_running']}")
        
        # Phase 3 コンポーネント状況
        if "health_monitor" in status["components"]:
            health_info = status["components"]["health_monitor"]
            print(f"   - ヘルスモニター稼働: {health_info['monitoring_active']}")
            print(f"   - システム状態: {health_info['system_status']}")
        
        if "performance_optimizer" in status["components"]:
            perf_info = status["components"]["performance_optimizer"]
            print(f"   - 自動最適化稼働: {perf_info['auto_optimization_active']}")
            print(f"   - 最適化成功率: {perf_info['success_rate']:.1f}%")
        
        if "maintenance" in status["components"]:
            maint_info = status["components"]["maintenance"]
            print(f"   - 自動メンテナンス稼働: {maint_info['auto_maintenance_active']}")
            print(f"   - 有効タスク: {maint_info['enabled_tasks']}/{maint_info['total_tasks']}")
            if maint_info['emergency_maintenance_needed']:
                print("   - ⚠️ 緊急メンテナンスが必要です")
        
        # ヘルスチェック
        print("\n🏥 ヘルスチェック:")
        health = manager.perform_health_check()
        print(f"   - 全体ステータス: {health['overall_status']}")
        
        for check_name, check_status in health["checks"].items():
            status_emoji = {"healthy": "✅", "warning": "⚠️", "error": "❌"}.get(check_status, "❓")
            print(f"   - {check_name}: {status_emoji} {check_status}")
        
        if health.get("issues"):
            print("   - 課題:")
            for issue in health["issues"]:
                print(f"     * {issue}")
        
        # 緊急バックアップテスト
        print("\n📦 緊急バックアップテスト:")
        emergency_backup = manager.create_emergency_backup("test")
        if emergency_backup:
            print(f"✅ 緊急バックアップ成功: {emergency_backup.name}")
        else:
            print("❌ 緊急バックアップ失敗")
        
        print("\n✅ 統合テスト完了")
        
        # 短時間実行してサービス動作確認
        print("⏱️ 5秒間サービス動作確認...")
        time.sleep(5)
        
    except KeyboardInterrupt:
        print("\n⚠️ ユーザーによる中断")
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # クリーンアップ
        if _system_manager:
            _system_manager.cleanup()
        print("🧹 クリーンアップ完了")
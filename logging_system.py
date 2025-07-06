#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
構造化ログシステム - せつなBot D案 Phase 1
JSON形式での詳細ログ記録・監視機能
"""

import logging
import json
import threading
import queue
import time
import traceback
import psutil
import os
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, Union
from functools import wraps


class StructuredLogger:
    """構造化ログシステムのメインクラス"""
    
    def __init__(self, log_dir: str = "/mnt/d/setsuna_bot/logs", log_level: str = "INFO"):
        """
        初期化
        
        Args:
            log_dir: ログ出力ディレクトリ
            log_level: ログレベル (DEBUG/INFO/WARNING/ERROR/CRITICAL)
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # ログレベル設定
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        
        # セッションID生成
        self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # ログキューとワーカースレッド
        self.log_queue = queue.Queue(maxsize=1000)
        self.log_worker_running = True
        self.log_thread = threading.Thread(target=self._log_worker, daemon=True)
        self.log_thread.start()
        
        # パフォーマンス統計
        self.performance_stats = {}
        
        # 初期化完了ログ
        self.info("logging_system", "__init__", "構造化ログシステム初期化完了", {
            "session_id": self.session_id,
            "log_dir": str(self.log_dir),
            "log_level": log_level
        })
    
    def _log_worker(self):
        """バックグラウンドでログを処理するワーカー"""
        while self.log_worker_running:
            try:
                # キューからログエントリを取得（タイムアウト付き）
                log_entry = self.log_queue.get(timeout=0.5)
                self._write_log_to_file(log_entry)
                self.log_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                # ログワーカー自体のエラーは標準出力に
                print(f"❌ [LogWorker] エラー: {e}")
                break
    
    def _write_log_to_file(self, log_entry: Dict[str, Any]):
        """ログエントリをファイルに書き込み"""
        try:
            # 日付別ログファイル
            log_date = datetime.now().strftime("%Y-%m-%d")
            log_file = self.log_dir / f"setsuna_bot_{log_date}.log"
            
            # JSON形式で書き込み
            with open(log_file, 'a', encoding='utf-8') as f:
                json.dump(log_entry, f, ensure_ascii=False, separators=(',', ':'))
                f.write('\n')
                
            # コンソール出力（簡略版）
            level = log_entry['level']
            module = log_entry['module']
            message = log_entry['message']
            print(f"[{level}] {module}: {message}")
            
        except Exception as e:
            print(f"❌ [LogWriter] ファイル書き込みエラー: {e}")
    
    def _create_log_entry(self, level: str, module: str, function: str, 
                         message: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """ログエントリを作成"""
        return {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "local_time": datetime.now().isoformat(),
            "level": level,
            "module": module,
            "function": function,
            "message": message,
            "data": data or {},
            "session_id": self.session_id,
            "process_id": os.getpid(),
            "thread_id": threading.get_ident()
        }
    
    def log(self, level: str, module: str, function: str, message: str, 
            data: Optional[Dict[str, Any]] = None):
        """汎用ログメソッド"""
        # ログレベルチェック
        level_value = getattr(logging, level.upper(), logging.INFO)
        if level_value < self.log_level:
            return
        
        log_entry = self._create_log_entry(level, module, function, message, data)
        
        try:
            self.log_queue.put_nowait(log_entry)
        except queue.Full:
            # キューが満杯の場合は標準出力に緊急出力
            print(f"⚠️ [LogQueue] キュー満杯: {level} - {message}")
    
    def debug(self, module: str, function: str, message: str, data: Optional[Dict[str, Any]] = None):
        """DEBUGレベルのログ"""
        self.log("DEBUG", module, function, message, data)
    
    def info(self, module: str, function: str, message: str, data: Optional[Dict[str, Any]] = None):
        """INFOレベルのログ"""
        self.log("INFO", module, function, message, data)
    
    def warning(self, module: str, function: str, message: str, data: Optional[Dict[str, Any]] = None):
        """WARNINGレベルのログ"""
        self.log("WARNING", module, function, message, data)
    
    def error(self, module: str, function: str, message: str, data: Optional[Dict[str, Any]] = None):
        """ERRORレベルのログ"""
        # エラーの場合はスタックトレースも記録
        if data is None:
            data = {}
        data["stack_trace"] = traceback.format_stack()
        self.log("ERROR", module, function, message, data)
    
    def critical(self, module: str, function: str, message: str, data: Optional[Dict[str, Any]] = None):
        """CRITICALレベルのログ"""
        if data is None:
            data = {}
        data["stack_trace"] = traceback.format_stack()
        self.log("CRITICAL", module, function, message, data)
    
    def log_exception(self, module: str, function: str, exception: Exception, 
                     additional_data: Optional[Dict[str, Any]] = None):
        """例外ログの専用メソッド"""
        data = {
            "exception_type": type(exception).__name__,
            "exception_message": str(exception),
            "traceback": traceback.format_exc()
        }
        if additional_data:
            data.update(additional_data)
        
        self.error(module, function, f"例外が発生: {type(exception).__name__}", data)
    
    def update_performance_stats(self, function_name: str, stats: Dict[str, Any]):
        """パフォーマンス統計を更新"""
        if function_name not in self.performance_stats:
            self.performance_stats[function_name] = {
                "call_count": 0,
                "total_time": 0,
                "avg_time": 0,
                "max_time": 0,
                "min_time": float('inf'),
                "error_count": 0
            }
        
        func_stats = self.performance_stats[function_name]
        func_stats["call_count"] += 1
        
        if "execution_time" in stats:
            exec_time = stats["execution_time"]
            func_stats["total_time"] += exec_time
            func_stats["avg_time"] = func_stats["total_time"] / func_stats["call_count"]
            func_stats["max_time"] = max(func_stats["max_time"], exec_time)
            func_stats["min_time"] = min(func_stats["min_time"], exec_time)
        
        if not stats.get("success", True):
            func_stats["error_count"] += 1
    
    def get_performance_report(self) -> Dict[str, Any]:
        """パフォーマンスレポートを取得"""
        return {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "functions": dict(self.performance_stats)
        }
    
    def cleanup(self):
        """ログシステムのクリーンアップ"""
        print(f"🔧 [StructuredLogger] クリーンアップ開始")
        
        # ワーカースレッド停止
        self.log_worker_running = False
        
        # スレッド終了待機（短時間）
        if self.log_thread.is_alive():
            self.log_thread.join(timeout=1.0)
        
        print(f"✅ [StructuredLogger] クリーンアップ完了 (Session: {self.session_id})")


class PerformanceMonitor:
    """パフォーマンス監視クラス"""
    
    def __init__(self, logger: StructuredLogger):
        """
        初期化
        
        Args:
            logger: StructuredLoggerインスタンス
        """
        self.logger = logger
        self.process = psutil.Process()
    
    def monitor_function(self, function_name: Optional[str] = None):
        """
        関数の実行時間・メモリ使用量を監視するデコレータ
        
        Args:
            function_name: 監視対象関数名（Noneの場合は実際の関数名を使用）
        """
        def decorator(func):
            monitored_name = function_name or func.__name__
            
            @wraps(func)
            def wrapper(*args, **kwargs):
                # 実行前の状態記録
                start_time = time.perf_counter()
                start_memory = self.process.memory_info().rss
                start_cpu_percent = self.process.cpu_percent()
                
                success = True
                error = None
                result = None
                
                try:
                    result = func(*args, **kwargs)
                except Exception as e:
                    success = False
                    error = str(e)
                    self.logger.log_exception(func.__module__ or "unknown", monitored_name, e)
                    raise
                finally:
                    # 実行後の状態記録
                    end_time = time.perf_counter()
                    end_memory = self.process.memory_info().rss
                    end_cpu_percent = self.process.cpu_percent()
                    
                    # メトリクス計算
                    execution_time = end_time - start_time
                    memory_delta = end_memory - start_memory
                    
                    metrics = {
                        "execution_time": execution_time,
                        "memory_before": start_memory,
                        "memory_after": end_memory,
                        "memory_delta": memory_delta,
                        "cpu_percent": end_cpu_percent,
                        "success": success,
                        "error": error,
                        "args_count": len(args),
                        "kwargs_count": len(kwargs)
                    }
                    
                    # パフォーマンス統計更新
                    self.logger.update_performance_stats(monitored_name, metrics)
                    
                    # 実行時間が長い場合は警告
                    if execution_time > 5.0:  # 5秒以上
                        self.logger.warning(
                            func.__module__ or "unknown",
                            monitored_name,
                            f"実行時間が長い関数を検出: {execution_time:.2f}秒",
                            metrics
                        )
                    else:
                        self.logger.debug(
                            func.__module__ or "unknown",
                            monitored_name,
                            f"関数実行完了: {execution_time:.3f}秒",
                            metrics
                        )
                
                return result
            return wrapper
        return decorator
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """システム全体のメトリクスを取得"""
        try:
            return {
                "timestamp": datetime.now().isoformat(),
                "cpu_percent": self.process.cpu_percent(interval=0.1),
                "memory_info": {
                    "rss": self.process.memory_info().rss,
                    "vms": self.process.memory_info().vms,
                    "percent": self.process.memory_percent()
                },
                "disk_usage": {
                    path: {
                        "total": shutil.disk_usage(path).total,
                        "used": shutil.disk_usage(path).used,
                        "free": shutil.disk_usage(path).free
                    } for path in ["/mnt/d"] if os.path.exists(path)
                },
                "thread_count": self.process.num_threads(),
                "open_files": len(self.process.open_files())
            }
        except Exception as e:
            self.logger.error("performance_monitor", "get_system_metrics", f"システムメトリクス取得エラー: {e}")
            return {}


# グローバルロガーインスタンス（シングルトン的な使用）
_global_logger: Optional[StructuredLogger] = None
_global_monitor: Optional[PerformanceMonitor] = None


def get_logger() -> StructuredLogger:
    """グローバルロガーインスタンスを取得"""
    global _global_logger
    if _global_logger is None:
        _global_logger = StructuredLogger()
    return _global_logger


def get_monitor() -> PerformanceMonitor:
    """グローバルパフォーマンスモニターを取得"""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = PerformanceMonitor(get_logger())
    return _global_monitor


def cleanup_logging():
    """ログシステムのグローバルクリーンアップ"""
    global _global_logger, _global_monitor
    if _global_logger:
        _global_logger.cleanup()
        _global_logger = None
    _global_monitor = None


# テスト用関数
if __name__ == "__main__":
    print("🧪 構造化ログシステムテスト開始")
    
    # ロガー初期化
    logger = StructuredLogger(log_level="INFO")
    monitor = PerformanceMonitor(logger)
    
    # テスト用関数
    @monitor.monitor_function("test_function")
    def test_function(duration: float = 0.01):
        """テスト用の関数"""
        time.sleep(duration)
        return f"テスト完了: {duration}秒"
    
    try:
        # 基本ログテスト
        logger.info("test_main", "main", "情報メッセージ", {"test_data": "info"})
        logger.warning("test_main", "main", "警告メッセージ", {"test_data": "warning"})
        
        # パフォーマンス監視テスト
        result = test_function(0.01)
        logger.info("test_main", "main", f"関数実行結果: {result}")
        
        print("✅ 基本テスト完了")
        
    finally:
        # クリーンアップ
        logger.cleanup()
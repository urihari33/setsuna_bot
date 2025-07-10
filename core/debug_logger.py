#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DebugLogger - デバッグログシステム
学習セッションの詳細なデバッグ情報を記録・管理するシステム
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from enum import Enum
import traceback
import threading
import queue
import time

# Windows環境のパス設定
if os.name == 'nt':
    DEBUG_LOG_DIR = Path("D:/setsuna_bot/logs/debug")
else:
    DEBUG_LOG_DIR = Path("/mnt/d/setsuna_bot/logs/debug")

class LogLevel(Enum):
    """ログレベル定義"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class DebugLogger:
    """デバッグログシステムメインクラス"""
    
    def __init__(self, session_id: str = None, component: str = "SYSTEM"):
        """
        初期化
        
        Args:
            session_id: セッションID
            component: コンポーネント名
        """
        self.session_id = session_id or f"debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.component = component
        
        # ログディレクトリ作成
        DEBUG_LOG_DIR.mkdir(parents=True, exist_ok=True)
        
        # ログファイル設定
        self.log_file = DEBUG_LOG_DIR / f"{self.session_id}_{component.lower()}.log"
        self.json_log_file = DEBUG_LOG_DIR / f"{self.session_id}_{component.lower()}.json"
        
        # ログ設定
        self.log_level = LogLevel.DEBUG
        self.console_output = True
        self.file_output = True
        self.json_output = True
        
        # ログバッファ（JSON用）
        self.json_logs = []
        self.log_buffer = queue.Queue()
        
        # スレッドセーフティ
        self.lock = threading.Lock()
        
        # バックグラウンドログ処理スレッド
        self.log_thread = None
        self.stop_logging = False
        
        self._start_logging_thread()
        
        # 初期化ログ
        self.info(f"デバッグログシステム初期化完了: {self.session_id}")
    
    def _start_logging_thread(self):
        """バックグラウンドログ処理スレッド開始"""
        self.log_thread = threading.Thread(
            target=self._log_writer_thread,
            daemon=True,
            name=f"DebugLogger_{self.session_id}"
        )
        self.log_thread.start()
    
    def _log_writer_thread(self):
        """ログ書き込みスレッド"""
        while not self.stop_logging:
            try:
                # バッファからログを取得（タイムアウト付き）
                log_entry = self.log_buffer.get(timeout=1)
                if log_entry is None:  # 終了シグナル
                    break
                
                # ファイルに書き込み
                if self.file_output:
                    self._write_to_file(log_entry)
                
                # JSONログに追加
                if self.json_output:
                    self._add_to_json_log(log_entry)
                
                self.log_buffer.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                # ログ書き込みエラーはコンソールに出力
                print(f"[DebugLogger] ログ書き込みエラー: {e}")
    
    def _write_to_file(self, log_entry: Dict):
        """ファイルにログ書き込み"""
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry['formatted_message'] + '\n')
        except Exception as e:
            print(f"[DebugLogger] ファイル書き込みエラー: {e}")
    
    def _add_to_json_log(self, log_entry: Dict):
        """JSONログに追加"""
        try:
            with self.lock:
                self.json_logs.append(log_entry)
                
                # 定期的にJSONファイルに保存
                if len(self.json_logs) % 10 == 0:
                    self._save_json_logs()
        except Exception as e:
            print(f"[DebugLogger] JSONログ追加エラー: {e}")
    
    def _save_json_logs(self):
        """JSONログをファイルに保存"""
        try:
            with open(self.json_log_file, 'w', encoding='utf-8') as f:
                json.dump(self.json_logs, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            print(f"[DebugLogger] JSONファイル保存エラー: {e}")
    
    def _format_message(self, level: LogLevel, message: str, 
                       context: Dict = None, exception: Exception = None) -> str:
        """ログメッセージのフォーマット"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        
        # 基本メッセージ
        formatted = f"[{timestamp}] [{level.value}] [{self.component}] {message}"
        
        # コンテキスト情報追加
        if context:
            formatted += f" | Context: {json.dumps(context, ensure_ascii=False, default=str)}"
        
        # 例外情報追加
        if exception:
            formatted += f" | Exception: {str(exception)}"
            formatted += f" | Traceback: {traceback.format_exc()}"
        
        return formatted
    
    def _create_log_entry(self, level: LogLevel, message: str,
                         context: Dict = None, exception: Exception = None) -> Dict:
        """ログエントリ作成"""
        timestamp = datetime.now()
        
        entry = {
            'timestamp': timestamp.isoformat(),
            'session_id': self.session_id,
            'component': self.component,
            'level': level.value,
            'message': message,
            'context': context or {},
            'exception': str(exception) if exception else None,
            'traceback': traceback.format_exc() if exception else None,
            'thread_id': threading.get_ident(),
            'formatted_message': self._format_message(level, message, context, exception)
        }
        
        return entry
    
    def _log(self, level: LogLevel, message: str, context: Dict = None, exception: Exception = None):
        """内部ログ処理"""
        try:
            # ログレベルチェック
            if level.value == LogLevel.DEBUG.value and self.log_level != LogLevel.DEBUG:
                return
            
            # ログエントリ作成
            log_entry = self._create_log_entry(level, message, context, exception)
            
            # コンソール出力
            if self.console_output:
                print(log_entry['formatted_message'])
            
            # バックグラウンド処理にキューイング
            self.log_buffer.put(log_entry)
            
        except Exception as e:
            # ログ処理エラーはコンソールに出力
            print(f"[DebugLogger] ログ処理エラー: {e}")
    
    def debug(self, message: str, context: Dict = None, exception: Exception = None):
        """デバッグレベルログ"""
        self._log(LogLevel.DEBUG, message, context, exception)
    
    def info(self, message: str, context: Dict = None, exception: Exception = None):
        """情報レベルログ"""
        self._log(LogLevel.INFO, message, context, exception)
    
    def warning(self, message: str, context: Dict = None, exception: Exception = None):
        """警告レベルログ"""
        self._log(LogLevel.WARNING, message, context, exception)
    
    def error(self, message: str, context: Dict = None, exception: Exception = None):
        """エラーレベルログ"""
        self._log(LogLevel.ERROR, message, context, exception)
    
    def critical(self, message: str, context: Dict = None, exception: Exception = None):
        """クリティカルレベルログ"""
        self._log(LogLevel.CRITICAL, message, context, exception)
    
    def log_api_request(self, url: str, method: str = "GET", 
                       headers: Dict = None, data: Any = None, 
                       response_status: int = None, response_data: Any = None):
        """API リクエスト/レスポンスログ"""
        context = {
            'api_request': {
                'url': url,
                'method': method,
                'headers': headers or {},
                'data': data,
                'response_status': response_status,
                'response_data': response_data
            }
        }
        
        if response_status and response_status >= 400:
            self.error(f"API リクエスト失敗: {method} {url}", context)
        else:
            self.debug(f"API リクエスト: {method} {url}", context)
    
    def log_function_call(self, function_name: str, args: tuple = None, 
                         kwargs: Dict = None, result: Any = None, 
                         execution_time: float = None):
        """関数呼び出しログ"""
        context = {
            'function_call': {
                'name': function_name,
                'args': args,
                'kwargs': kwargs,
                'result': result,
                'execution_time': execution_time
            }
        }
        
        self.debug(f"関数呼び出し: {function_name}", context)
    
    def log_session_phase(self, phase: str, status: str, 
                         progress: float = None, details: Dict = None):
        """セッションフェーズログ"""
        context = {
            'session_phase': {
                'phase': phase,
                'status': status,
                'progress': progress,
                'details': details or {}
            }
        }
        
        self.info(f"セッションフェーズ: {phase} - {status}", context)
    
    def log_data_processing(self, data_type: str, input_count: int, 
                           output_count: int, processing_time: float = None,
                           details: Dict = None):
        """データ処理ログ"""
        context = {
            'data_processing': {
                'type': data_type,
                'input_count': input_count,
                'output_count': output_count,
                'processing_time': processing_time,
                'details': details or {}
            }
        }
        
        self.info(f"データ処理: {data_type} ({input_count} -> {output_count})", context)
    
    def log_web_search(self, query: str, search_url: str, 
                      response_status: int = None, results_count: int = None,
                      response_data: Any = None, error: Exception = None):
        """Web検索ログ"""
        context = {
            'web_search': {
                'query': query,
                'search_url': search_url,
                'response_status': response_status,
                'results_count': results_count,
                'response_data': response_data
            }
        }
        
        if error:
            self.error(f"Web検索エラー: {query}", context, error)
        elif response_status and response_status >= 400:
            self.warning(f"Web検索失敗: {query}", context)
        else:
            self.info(f"Web検索実行: {query} ({results_count}件)", context)
    
    def set_log_level(self, level: LogLevel):
        """ログレベル設定"""
        self.log_level = level
        self.info(f"ログレベル変更: {level.value}")
    
    def enable_console_output(self, enable: bool = True):
        """コンソール出力有効/無効"""
        self.console_output = enable
        self.info(f"コンソール出力: {'有効' if enable else '無効'}")
    
    def enable_file_output(self, enable: bool = True):
        """ファイル出力有効/無効"""
        self.file_output = enable
        self.info(f"ファイル出力: {'有効' if enable else '無効'}")
    
    def get_log_summary(self) -> Dict:
        """ログサマリー取得"""
        with self.lock:
            level_counts = {}
            for log in self.json_logs:
                level = log['level']
                level_counts[level] = level_counts.get(level, 0) + 1
            
            return {
                'session_id': self.session_id,
                'component': self.component,
                'total_logs': len(self.json_logs),
                'level_counts': level_counts,
                'log_file': str(self.log_file),
                'json_log_file': str(self.json_log_file),
                'start_time': self.json_logs[0]['timestamp'] if self.json_logs else None,
                'end_time': self.json_logs[-1]['timestamp'] if self.json_logs else None
            }
    
    def get_logs_by_level(self, level: LogLevel) -> List[Dict]:
        """指定レベルのログ取得"""
        with self.lock:
            return [log for log in self.json_logs if log['level'] == level.value]
    
    def get_logs_by_component(self, component: str) -> List[Dict]:
        """指定コンポーネントのログ取得"""
        with self.lock:
            return [log for log in self.json_logs if log['component'] == component]
    
    def search_logs(self, keyword: str) -> List[Dict]:
        """ログ検索"""
        with self.lock:
            results = []
            for log in self.json_logs:
                if keyword.lower() in log['message'].lower():
                    results.append(log)
                elif log['context'] and keyword.lower() in str(log['context']).lower():
                    results.append(log)
            return results
    
    def export_logs(self, export_path: Path = None) -> Path:
        """ログエクスポート"""
        if export_path is None:
            export_path = DEBUG_LOG_DIR / f"{self.session_id}_export.json"
        
        export_data = {
            'session_info': {
                'session_id': self.session_id,
                'component': self.component,
                'export_time': datetime.now().isoformat(),
                'total_logs': len(self.json_logs)
            },
            'logs': self.json_logs,
            'summary': self.get_log_summary()
        }
        
        with open(export_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2, default=str)
        
        self.info(f"ログエクスポート完了: {export_path}")
        return export_path
    
    def close(self):
        """ログシステム終了"""
        self.info("デバッグログシステム終了")
        
        # バックグラウンドスレッド終了
        self.stop_logging = True
        self.log_buffer.put(None)  # 終了シグナル
        
        if self.log_thread and self.log_thread.is_alive():
            self.log_thread.join(timeout=5)
        
        # 残りのJSONログを保存
        self._save_json_logs()

# グローバルロガーインスタンス管理
_logger_instances = {}
_logger_lock = threading.Lock()

def get_debug_logger(session_id: str = None, component: str = "SYSTEM") -> DebugLogger:
    """デバッグロガーインスタンス取得"""
    global _logger_instances, _logger_lock
    
    with _logger_lock:
        key = f"{session_id}_{component}"
        
        if key not in _logger_instances:
            _logger_instances[key] = DebugLogger(session_id, component)
        
        return _logger_instances[key]

def close_all_loggers():
    """すべてのロガーを閉じる"""
    global _logger_instances, _logger_lock
    
    with _logger_lock:
        for logger in _logger_instances.values():
            logger.close()
        _logger_instances.clear()

# デバッグデコレータ
def debug_function(logger: DebugLogger = None, log_args: bool = True, log_result: bool = True):
    """関数デバッグデコレータ"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            nonlocal logger
            if logger is None:
                logger = get_debug_logger(component="FUNCTION")
            
            start_time = time.time()
            
            # 関数呼び出しログ
            log_args_data = args if log_args else None
            log_kwargs_data = kwargs if log_args else None
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                # 結果ログ
                log_result_data = result if log_result else None
                logger.log_function_call(
                    func.__name__, 
                    log_args_data, 
                    log_kwargs_data, 
                    log_result_data, 
                    execution_time
                )
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                logger.log_function_call(
                    func.__name__, 
                    log_args_data, 
                    log_kwargs_data, 
                    None, 
                    execution_time
                )
                logger.error(f"関数実行エラー: {func.__name__}", exception=e)
                raise
        
        return wrapper
    return decorator

# テスト用コード
if __name__ == "__main__":
    print("=== DebugLogger テスト ===")
    
    # テスト用ロガー作成
    logger = get_debug_logger("test_session", "TEST")
    
    # 各レベルのログテスト
    logger.debug("デバッグメッセージ", {'test_data': 'debug_value'})
    logger.info("情報メッセージ", {'test_data': 'info_value'})
    logger.warning("警告メッセージ", {'test_data': 'warning_value'})
    logger.error("エラーメッセージ", {'test_data': 'error_value'})
    
    # API リクエストログテスト
    logger.log_api_request(
        "https://api.example.com/search",
        "GET",
        {"Authorization": "Bearer test"},
        None,
        200,
        {"results": ["item1", "item2"]}
    )
    
    # Web検索ログテスト
    logger.log_web_search(
        "test query",
        "https://duckduckgo.com/?q=test",
        200,
        5,
        {"results": ["result1", "result2"]}
    )
    
    # セッションフェーズログテスト
    logger.log_session_phase(
        "information_collection",
        "completed",
        0.5,
        {"collected_items": 10}
    )
    
    # データ処理ログテスト
    logger.log_data_processing(
        "web_search_results",
        10,
        5,
        2.5,
        {"filter_method": "relevance_threshold"}
    )
    
    # ログサマリー表示
    summary = logger.get_log_summary()
    print("\n📊 ログサマリー:")
    for key, value in summary.items():
        print(f"  {key}: {value}")
    
    # ログエクスポート
    export_path = logger.export_logs()
    print(f"\n📁 ログエクスポート: {export_path}")
    
    # 終了
    logger.close()
    close_all_loggers()
    
    print("\n✅ DebugLogger テスト完了")
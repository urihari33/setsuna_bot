#!/usr/bin/env python3
"""
パフォーマンス最適化システム
キャッシュ、メモリ、データベースのパフォーマンスを最適化
"""

import os
import gc
import json
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from logging_system import get_logger

@dataclass
class OptimizationResult:
    """最適化結果"""
    timestamp: str
    operation: str
    before_metrics: Dict
    after_metrics: Dict
    improvement: Dict
    success: bool
    message: str

class PerformanceOptimizer:
    """パフォーマンス最適化システム"""
    
    def __init__(self, data_dir: str = "/mnt/d/setsuna_bot/optimization"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.logger = get_logger()
        self.results_file = self.data_dir / "optimization_results.json"
        self.config_file = self.data_dir / "optimizer_config.json"
        
        # デフォルト設定
        self.config = {
            "auto_optimization": True,
            "optimization_interval": 3600,  # 1時間間隔
            "cache_cleanup_threshold": 1000,  # キャッシュエントリ数
            "memory_cleanup_threshold": 80.0,  # メモリ使用率%
            "log_retention_days": 30,
            "optimization_targets": {
                "response_cache": True,
                "memory_cleanup": True,
                "log_rotation": True,
                "database_optimization": True
            }
        }
        
        self.load_config()
        
        # 最適化結果履歴
        self.optimization_history: List[OptimizationResult] = []
        self.load_optimization_history()
        
        # 自動最適化スレッド
        self.optimization_thread = None
        self.stop_optimization = False
        
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
    
    def load_optimization_history(self):
        """最適化履歴を読み込み"""
        try:
            if self.results_file.exists():
                with open(self.results_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.optimization_history = [
                        OptimizationResult(**result) for result in data.get('results', [])
                    ]
        except Exception as e:
            self.logger.warning(f"最適化履歴読み込みエラー: {e}")
    
    def save_optimization_history(self):
        """最適化履歴を保存"""
        try:
            history_data = {
                'results': [asdict(result) for result in self.optimization_history],
                'last_updated': datetime.now().isoformat()
            }
            with open(self.results_file, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"最適化履歴保存エラー: {e}")
    
    def get_current_performance_metrics(self) -> Dict:
        """現在のパフォーマンスメトリクスを取得"""
        try:
            import psutil
            
            # メモリ使用率
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available = memory.available
            
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # ディスク使用率
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            
            # キャッシュ統計
            cache_stats = self.get_cache_stats()
            
            # ログファイルサイズ
            log_sizes = self.get_log_file_sizes()
            
            return {
                "memory_percent": memory_percent,
                "memory_available": memory_available,
                "cpu_percent": cpu_percent,
                "disk_percent": disk_percent,
                "cache_stats": cache_stats,
                "log_sizes": log_sizes,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"パフォーマンスメトリクス取得エラー: {e}")
            return {}
    
    def get_cache_stats(self) -> Dict:
        """キャッシュ統計を取得"""
        try:
            cache_stats = {"total_entries": 0, "total_size": 0}
            
            # レスポンスキャッシュ
            response_cache_file = Path("/mnt/d/setsuna_bot/response_cache/response_cache.json")
            if response_cache_file.exists():
                with open(response_cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    cache_stats["total_entries"] = len(cache_data)
                    cache_stats["total_size"] = response_cache_file.stat().st_size
            
            # 音声キャッシュ
            voice_cache_dir = Path("/mnt/d/setsuna_bot/voice_cache")
            if voice_cache_dir.exists():
                voice_files = list(voice_cache_dir.glob("*.wav"))
                cache_stats["voice_cache_count"] = len(voice_files)
                cache_stats["voice_cache_size"] = sum(f.stat().st_size for f in voice_files)
            
            return cache_stats
            
        except Exception as e:
            self.logger.warning(f"キャッシュ統計取得エラー: {e}")
            return {}
    
    def get_log_file_sizes(self) -> Dict:
        """ログファイルサイズを取得"""
        try:
            log_sizes = {}
            
            # ログディレクトリ
            log_dirs = [
                Path("/mnt/d/setsuna_bot/logs"),
                Path("/mnt/d/setsuna_bot/monitoring")
            ]
            
            for log_dir in log_dirs:
                if log_dir.exists():
                    log_files = list(log_dir.glob("*.log")) + list(log_dir.glob("*.json"))
                    total_size = sum(f.stat().st_size for f in log_files)
                    log_sizes[log_dir.name] = {
                        "file_count": len(log_files),
                        "total_size": total_size
                    }
            
            return log_sizes
            
        except Exception as e:
            self.logger.warning(f"ログファイルサイズ取得エラー: {e}")
            return {}
    
    def optimize_response_cache(self) -> OptimizationResult:
        """レスポンスキャッシュを最適化"""
        try:
            before_metrics = self.get_current_performance_metrics()
            
            response_cache_file = Path("/mnt/d/setsuna_bot/response_cache/response_cache.json")
            if not response_cache_file.exists():
                return OptimizationResult(
                    timestamp=datetime.now().isoformat(),
                    operation="response_cache_optimization",
                    before_metrics=before_metrics,
                    after_metrics=before_metrics,
                    improvement={},
                    success=False,
                    message="レスポンスキャッシュファイルが存在しません"
                )
            
            # キャッシュデータを読み込み
            with open(response_cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            original_count = len(cache_data)
            
            # 古いキャッシュエントリを削除
            cutoff_date = datetime.now() - timedelta(days=7)
            optimized_cache = {}
            
            for key, entry in cache_data.items():
                try:
                    last_used = datetime.fromisoformat(entry.get('last_used', entry.get('created_at', '')))
                    if last_used > cutoff_date:
                        optimized_cache[key] = entry
                except:
                    # 日付解析エラーの場合はエントリを保持
                    optimized_cache[key] = entry
            
            # 使用頻度が低いエントリを削除
            if len(optimized_cache) > self.config['cache_cleanup_threshold']:
                # 使用回数でソート
                sorted_entries = sorted(
                    optimized_cache.items(),
                    key=lambda x: x[1].get('use_count', 0),
                    reverse=True
                )
                optimized_cache = dict(sorted_entries[:self.config['cache_cleanup_threshold']])
            
            # 最適化されたキャッシュを保存
            with open(response_cache_file, 'w', encoding='utf-8') as f:
                json.dump(optimized_cache, f, indent=2, ensure_ascii=False)
            
            after_metrics = self.get_current_performance_metrics()
            
            removed_count = original_count - len(optimized_cache)
            improvement = {
                "removed_entries": removed_count,
                "retention_rate": (len(optimized_cache) / original_count) * 100 if original_count > 0 else 0,
                "size_reduction": before_metrics.get('cache_stats', {}).get('total_size', 0) - after_metrics.get('cache_stats', {}).get('total_size', 0)
            }
            
            result = OptimizationResult(
                timestamp=datetime.now().isoformat(),
                operation="response_cache_optimization",
                before_metrics=before_metrics,
                after_metrics=after_metrics,
                improvement=improvement,
                success=True,
                message=f"キャッシュ最適化完了: {removed_count}件のエントリを削除"
            )
            
            self.logger.info(f"レスポンスキャッシュ最適化完了: {removed_count}件削除")
            return result
            
        except Exception as e:
            self.logger.error(f"レスポンスキャッシュ最適化エラー: {e}")
            return OptimizationResult(
                timestamp=datetime.now().isoformat(),
                operation="response_cache_optimization",
                before_metrics={},
                after_metrics={},
                improvement={},
                success=False,
                message=str(e)
            )
    
    def optimize_memory(self) -> OptimizationResult:
        """メモリを最適化"""
        try:
            before_metrics = self.get_current_performance_metrics()
            
            # ガベージコレクション実行
            collected_objects = gc.collect()
            
            # メモリ使用量を再測定
            time.sleep(1)  # 測定値安定化のため待機
            after_metrics = self.get_current_performance_metrics()
            
            improvement = {
                "collected_objects": collected_objects,
                "memory_freed": before_metrics.get('memory_percent', 0) - after_metrics.get('memory_percent', 0),
                "memory_available_increase": after_metrics.get('memory_available', 0) - before_metrics.get('memory_available', 0)
            }
            
            result = OptimizationResult(
                timestamp=datetime.now().isoformat(),
                operation="memory_optimization",
                before_metrics=before_metrics,
                after_metrics=after_metrics,
                improvement=improvement,
                success=True,
                message=f"メモリ最適化完了: {collected_objects}個のオブジェクトを解放"
            )
            
            self.logger.info(f"メモリ最適化完了: {collected_objects}個のオブジェクト解放")
            return result
            
        except Exception as e:
            self.logger.error(f"メモリ最適化エラー: {e}")
            return OptimizationResult(
                timestamp=datetime.now().isoformat(),
                operation="memory_optimization",
                before_metrics={},
                after_metrics={},
                improvement={},
                success=False,
                message=str(e)
            )
    
    def optimize_logs(self) -> OptimizationResult:
        """ログファイルを最適化"""
        try:
            before_metrics = self.get_current_performance_metrics()
            
            cleaned_files = 0
            total_size_freed = 0
            
            # ログディレクトリを処理
            log_dirs = [
                Path("D:/setsuna_bot/logs"),
                Path("D:/setsuna_bot/monitoring")
            ]
            
            cutoff_date = datetime.now() - timedelta(days=self.config['log_retention_days'])
            
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
            
            after_metrics = self.get_current_performance_metrics()
            
            improvement = {
                "cleaned_files": cleaned_files,
                "size_freed": total_size_freed,
                "retention_days": self.config['log_retention_days']
            }
            
            result = OptimizationResult(
                timestamp=datetime.now().isoformat(),
                operation="log_optimization",
                before_metrics=before_metrics,
                after_metrics=after_metrics,
                improvement=improvement,
                success=True,
                message=f"ログ最適化完了: {cleaned_files}個のファイル削除 ({total_size_freed} bytes解放)"
            )
            
            self.logger.info(f"ログ最適化完了: {cleaned_files}ファイル削除")
            return result
            
        except Exception as e:
            self.logger.error(f"ログ最適化エラー: {e}")
            return OptimizationResult(
                timestamp=datetime.now().isoformat(),
                operation="log_optimization",
                before_metrics={},
                after_metrics={},
                improvement={},
                success=False,
                message=str(e)
            )
    
    def optimize_voice_cache(self) -> OptimizationResult:
        """音声キャッシュを最適化"""
        try:
            before_metrics = self.get_current_performance_metrics()
            
            voice_cache_dir = Path("/mnt/d/setsuna_bot/voice_cache")
            if not voice_cache_dir.exists():
                return OptimizationResult(
                    timestamp=datetime.now().isoformat(),
                    operation="voice_cache_optimization",
                    before_metrics=before_metrics,
                    after_metrics=before_metrics,
                    improvement={},
                    success=False,
                    message="音声キャッシュディレクトリが存在しません"
                )
            
            # 古い音声キャッシュファイルを削除
            cutoff_date = datetime.now() - timedelta(days=3)  # 3日以上古いファイル
            
            cleaned_files = 0
            total_size_freed = 0
            
            for voice_file in voice_cache_dir.glob("*.wav"):
                try:
                    file_mtime = datetime.fromtimestamp(voice_file.stat().st_mtime)
                    if file_mtime < cutoff_date:
                        file_size = voice_file.stat().st_size
                        voice_file.unlink()
                        cleaned_files += 1
                        total_size_freed += file_size
                except Exception as e:
                    self.logger.warning(f"音声キャッシュファイル削除エラー ({voice_file}): {e}")
            
            after_metrics = self.get_current_performance_metrics()
            
            improvement = {
                "cleaned_files": cleaned_files,
                "size_freed": total_size_freed,
                "retention_days": 3
            }
            
            result = OptimizationResult(
                timestamp=datetime.now().isoformat(),
                operation="voice_cache_optimization",
                before_metrics=before_metrics,
                after_metrics=after_metrics,
                improvement=improvement,
                success=True,
                message=f"音声キャッシュ最適化完了: {cleaned_files}個のファイル削除 ({total_size_freed} bytes解放)"
            )
            
            self.logger.info(f"音声キャッシュ最適化完了: {cleaned_files}ファイル削除")
            return result
            
        except Exception as e:
            self.logger.error(f"音声キャッシュ最適化エラー: {e}")
            return OptimizationResult(
                timestamp=datetime.now().isoformat(),
                operation="voice_cache_optimization",
                before_metrics={},
                after_metrics={},
                improvement={},
                success=False,
                message=str(e)
            )
    
    def run_full_optimization(self) -> List[OptimizationResult]:
        """全体最適化を実行"""
        results = []
        
        self.logger.info("全体最適化を開始します")
        
        # 各最適化を実行
        optimization_tasks = [
            ("response_cache", self.optimize_response_cache),
            ("voice_cache", self.optimize_voice_cache),
            ("memory_cleanup", self.optimize_memory),
            ("log_rotation", self.optimize_logs)
        ]
        
        for task_name, task_func in optimization_tasks:
            if self.config['optimization_targets'].get(task_name, True):
                try:
                    result = task_func()
                    results.append(result)
                    self.optimization_history.append(result)
                    
                    # 各最適化の間に短い待機
                    time.sleep(1)
                    
                except Exception as e:
                    self.logger.error(f"最適化タスクエラー ({task_name}): {e}")
                    results.append(OptimizationResult(
                        timestamp=datetime.now().isoformat(),
                        operation=task_name,
                        before_metrics={},
                        after_metrics={},
                        improvement={},
                        success=False,
                        message=str(e)
                    ))
        
        # 結果を保存
        self.save_optimization_history()
        
        successful_count = sum(1 for r in results if r.success)
        self.logger.info(f"全体最適化完了: {successful_count}/{len(results)} 成功")
        
        return results
    
    def start_auto_optimization(self):
        """自動最適化を開始"""
        if not self.config['auto_optimization']:
            self.logger.info("自動最適化は無効になっています")
            return
        
        if self.optimization_thread and self.optimization_thread.is_alive():
            self.logger.warning("自動最適化は既に開始されています")
            return
        
        self.stop_optimization = False
        self.optimization_thread = threading.Thread(target=self._optimization_loop, daemon=True)
        self.optimization_thread.start()
        
        self.logger.info("自動最適化を開始しました")
    
    def stop_auto_optimization(self):
        """自動最適化を停止"""
        self.stop_optimization = True
        if self.optimization_thread:
            self.optimization_thread.join(timeout=5)
        
        self.logger.info("自動最適化を停止しました")
    
    def _optimization_loop(self):
        """自動最適化ループ"""
        while not self.stop_optimization:
            try:
                # 最適化実行
                self.run_full_optimization()
                
                # 次の実行まで待機
                time.sleep(self.config['optimization_interval'])
                
            except Exception as e:
                self.logger.error(f"自動最適化ループエラー: {e}")
                time.sleep(self.config['optimization_interval'])
    
    def get_optimization_summary(self) -> Dict:
        """最適化サマリを取得"""
        try:
            if not self.optimization_history:
                return {"status": "NO_DATA", "message": "最適化履歴がありません"}
            
            # 最近の最適化結果を分析
            recent_results = [
                result for result in self.optimization_history
                if datetime.fromisoformat(result.timestamp) > datetime.now() - timedelta(hours=24)
            ]
            
            summary = {
                "total_optimizations": len(self.optimization_history),
                "recent_optimizations": len(recent_results),
                "success_rate": (sum(1 for r in recent_results if r.success) / len(recent_results)) * 100 if recent_results else 0,
                "auto_optimization_active": self.optimization_thread and self.optimization_thread.is_alive(),
                "last_optimization": self.optimization_history[-1].timestamp if self.optimization_history else None,
                "optimization_breakdown": {}
            }
            
            # 最適化タイプ別の統計
            for result in recent_results:
                op_type = result.operation
                if op_type not in summary["optimization_breakdown"]:
                    summary["optimization_breakdown"][op_type] = {
                        "count": 0,
                        "success_count": 0,
                        "total_improvement": {}
                    }
                
                summary["optimization_breakdown"][op_type]["count"] += 1
                if result.success:
                    summary["optimization_breakdown"][op_type]["success_count"] += 1
                    
                    # 改善量を集計
                    for key, value in result.improvement.items():
                        if isinstance(value, (int, float)):
                            if key not in summary["optimization_breakdown"][op_type]["total_improvement"]:
                                summary["optimization_breakdown"][op_type]["total_improvement"][key] = 0
                            summary["optimization_breakdown"][op_type]["total_improvement"][key] += value
            
            return summary
            
        except Exception as e:
            self.logger.error(f"最適化サマリ取得エラー: {e}")
            return {"status": "ERROR", "message": str(e)}

# グローバルインスタンス
_performance_optimizer = None

def get_performance_optimizer() -> PerformanceOptimizer:
    """パフォーマンスオプティマイザのグローバルインスタンスを取得"""
    global _performance_optimizer
    if _performance_optimizer is None:
        _performance_optimizer = PerformanceOptimizer()
    return _performance_optimizer

if __name__ == "__main__":
    # テスト実行
    optimizer = get_performance_optimizer()
    
    print("=== パフォーマンス最適化システムテスト ===")
    
    # 現在のメトリクス表示
    metrics = optimizer.get_current_performance_metrics()
    print(f"現在のメトリクス:")
    print(f"  メモリ使用率: {metrics.get('memory_percent', 0):.1f}%")
    print(f"  CPU使用率: {metrics.get('cpu_percent', 0):.1f}%")
    print(f"  キャッシュエントリ数: {metrics.get('cache_stats', {}).get('total_entries', 0)}")
    
    # 最適化実行
    results = optimizer.run_full_optimization()
    
    print(f"\n最適化結果:")
    for result in results:
        status = "✅" if result.success else "❌"
        print(f"{status} {result.operation}: {result.message}")
    
    # サマリ表示
    summary = optimizer.get_optimization_summary()
    print(f"\n最適化サマリ:")
    print(f"  成功率: {summary['success_rate']:.1f}%")
    print(f"  最近の最適化: {summary['recent_optimizations']}回")
    
    print("テスト完了")
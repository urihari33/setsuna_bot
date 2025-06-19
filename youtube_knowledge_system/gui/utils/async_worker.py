"""
非同期処理ワーカー

バックグラウンド処理とGUIの通信を管理
"""

import threading
import queue
from typing import Callable, Any, Optional
from datetime import datetime


class AsyncWorker:
    """非同期処理ワーカークラス"""
    
    def __init__(self):
        self.result_queue = queue.Queue()
        self.progress_queue = queue.Queue()
        self.current_thread: Optional[threading.Thread] = None
        self.is_running = False
    
    def start_task(
        self, 
        target_func: Callable,
        args: tuple = (),
        kwargs: dict = None,
        progress_callback: Optional[Callable] = None
    ):
        """タスクを開始"""
        if self.is_running:
            return False
        
        kwargs = kwargs or {}
        
        def worker():
            try:
                self.is_running = True
                
                # プログレスコールバックを設定
                if progress_callback:
                    kwargs['progress_callback'] = lambda msg, progress=None: self.progress_queue.put((msg, progress))
                
                # タスク実行
                result = target_func(*args, **kwargs)
                
                # 結果をキューに追加
                self.result_queue.put(('success', result))
                
            except Exception as e:
                # エラーをキューに追加
                self.result_queue.put(('error', str(e)))
            finally:
                self.is_running = False
        
        self.current_thread = threading.Thread(target=worker, daemon=True)
        self.current_thread.start()
        return True
    
    def get_result(self, timeout: float = 0.1):
        """結果を取得（ノンブロッキング）"""
        try:
            return self.result_queue.get_nowait()
        except queue.Empty:
            return None
    
    def get_progress(self, timeout: float = 0.1):
        """進捗を取得（ノンブロッキング）"""
        try:
            return self.progress_queue.get_nowait()
        except queue.Empty:
            return None
    
    def stop_task(self):
        """タスクを停止（強制終了は困難なので、フラグのみ）"""
        self.is_running = False


class ProgressCallback:
    """進捗コールバックヘルパー"""
    
    def __init__(self, progress_queue: queue.Queue):
        self.progress_queue = progress_queue
        self.total_steps = 100
        self.current_step = 0
    
    def set_total_steps(self, total: int):
        """総ステップ数を設定"""
        self.total_steps = total
        self.current_step = 0
    
    def update(self, message: str, step: Optional[int] = None):
        """進捗を更新"""
        if step is not None:
            self.current_step = step
        else:
            self.current_step += 1
        
        progress = (self.current_step / self.total_steps) * 100 if self.total_steps > 0 else 0
        progress = min(100, max(0, progress))  # 0-100の範囲に制限
        
        self.progress_queue.put((message, progress))
    
    def finish(self, message: str = "完了"):
        """処理完了"""
        self.progress_queue.put((message, 100))


class TaskManager:
    """タスク管理クラス"""
    
    def __init__(self):
        self.workers = {}
        self.task_history = []
    
    def create_worker(self, worker_id: str) -> AsyncWorker:
        """ワーカーを作成"""
        worker = AsyncWorker()
        self.workers[worker_id] = worker
        return worker
    
    def get_worker(self, worker_id: str) -> Optional[AsyncWorker]:
        """ワーカーを取得"""
        return self.workers.get(worker_id)
    
    def is_any_running(self) -> bool:
        """いずれかのワーカーが実行中か"""
        return any(worker.is_running for worker in self.workers.values())
    
    def stop_all(self):
        """全ワーカーを停止"""
        for worker in self.workers.values():
            worker.stop_task()
    
    def add_to_history(self, task_name: str, result: str, duration: float = 0):
        """タスク履歴に追加"""
        self.task_history.append({
            'task_name': task_name,
            'result': result,
            'duration': duration,
            'timestamp': datetime.now()
        })
        
        # 履歴は最大100件まで
        if len(self.task_history) > 100:
            self.task_history = self.task_history[-100:]
    
    def get_recent_history(self, count: int = 10) -> list:
        """最近のタスク履歴を取得"""
        return self.task_history[-count:] if self.task_history else []


# グローバルタスクマネージャー
global_task_manager = TaskManager()
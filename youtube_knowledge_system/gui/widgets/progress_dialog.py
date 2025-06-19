"""
進捗ダイアログ

長時間処理の進捗表示とキャンセル機能
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable


class ProgressDialog:
    """進捗ダイアログクラス"""
    
    def __init__(self, parent, title: str = "処理中", cancelable: bool = True):
        self.parent = parent
        self.canceled = False
        self.cancel_callback: Optional[Callable] = None
        
        # ダイアログ作成
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("400x150")
        self.dialog.resizable(False, False)
        
        # 親ウィンドウの中央に配置
        self.center_on_parent()
        
        # モーダルダイアログに設定
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 閉じるボタンを無効化
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_close if cancelable else lambda: None)
        
        # ウィジェット作成
        self.create_widgets(cancelable)
        
        # 初期状態
        self.set_message("準備中...")
        self.set_progress(0)
    
    def center_on_parent(self):
        """親ウィンドウの中央に配置"""
        self.dialog.update_idletasks()
        
        # 親ウィンドウの位置とサイズを取得
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        # ダイアログのサイズを取得
        dialog_width = self.dialog.winfo_reqwidth()
        dialog_height = self.dialog.winfo_reqheight()
        
        # 中央位置を計算
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
    
    def create_widgets(self, cancelable: bool):
        """ウィジェットを作成"""
        # メインフレーム
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # メッセージラベル
        self.message_label = ttk.Label(
            main_frame,
            text="処理中...",
            font=('Segoe UI', 10)
        )
        self.message_label.pack(pady=(0, 10))
        
        # 進捗バー
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            main_frame,
            variable=self.progress_var,
            maximum=100,
            length=300
        )
        self.progress_bar.pack(pady=(0, 10))
        
        # パーセンテージラベル
        self.percentage_label = ttk.Label(
            main_frame,
            text="0%",
            font=('Segoe UI', 9)
        )
        self.percentage_label.pack(pady=(0, 10))
        
        # ボタンフレーム
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(side='bottom', fill='x')
        
        if cancelable:
            self.cancel_button = ttk.Button(
                button_frame,
                text="キャンセル",
                command=self.on_cancel
            )
            self.cancel_button.pack(side='right')
        else:
            self.cancel_button = None
    
    def set_message(self, message: str):
        """メッセージを設定"""
        self.message_label.config(text=message)
        self.dialog.update_idletasks()
    
    def set_progress(self, progress: float):
        """進捗を設定（0-100）"""
        progress = max(0, min(100, progress))  # 0-100の範囲に制限
        self.progress_var.set(progress)
        self.percentage_label.config(text=f"{progress:.1f}%")
        self.dialog.update_idletasks()
    
    def update(self, message: str = None, progress: float = None):
        """メッセージと進捗を更新"""
        if message is not None:
            self.set_message(message)
        if progress is not None:
            self.set_progress(progress)
    
    def set_cancel_callback(self, callback: Callable):
        """キャンセルコールバックを設定"""
        self.cancel_callback = callback
    
    def on_cancel(self):
        """キャンセルボタンクリック"""
        self.canceled = True
        if self.cancel_callback:
            self.cancel_callback()
        self.close()
    
    def on_close(self):
        """ダイアログクローズ"""
        self.on_cancel()
    
    def is_canceled(self) -> bool:
        """キャンセルされたかどうか"""
        return self.canceled
    
    def close(self):
        """ダイアログを閉じる"""
        if self.dialog.winfo_exists():
            self.dialog.grab_release()
            self.dialog.destroy()
    
    def show(self):
        """ダイアログを表示（ブロッキング）"""
        self.dialog.wait_window()


class IndeterminateProgressDialog:
    """不定進捗ダイアログ（進捗不明な処理用）"""
    
    def __init__(self, parent, title: str = "処理中", message: str = "しばらくお待ちください..."):
        self.parent = parent
        self.canceled = False
        
        # ダイアログ作成
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("350x120")
        self.dialog.resizable(False, False)
        
        # 親ウィンドウの中央に配置
        self.center_on_parent()
        
        # モーダルダイアログに設定
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 閉じるボタンを無効化
        self.dialog.protocol("WM_DELETE_WINDOW", lambda: None)
        
        # ウィジェット作成
        self.create_widgets(message)
    
    def center_on_parent(self):
        """親ウィンドウの中央に配置"""
        self.dialog.update_idletasks()
        
        parent_x = self.parent.winfo_x()
        parent_y = self.parent.winfo_y()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        dialog_width = self.dialog.winfo_reqwidth()
        dialog_height = self.dialog.winfo_reqheight()
        
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
    
    def create_widgets(self, message: str):
        """ウィジェットを作成"""
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # メッセージラベル
        self.message_label = ttk.Label(
            main_frame,
            text=message,
            font=('Segoe UI', 10)
        )
        self.message_label.pack(pady=(0, 15))
        
        # 不定進捗バー
        self.progress_bar = ttk.Progressbar(
            main_frame,
            mode='indeterminate',
            length=250
        )
        self.progress_bar.pack()
        self.progress_bar.start(10)  # アニメーション開始
    
    def set_message(self, message: str):
        """メッセージを設定"""
        self.message_label.config(text=message)
        self.dialog.update_idletasks()
    
    def close(self):
        """ダイアログを閉じる"""
        if self.dialog.winfo_exists():
            self.progress_bar.stop()
            self.dialog.grab_release()
            self.dialog.destroy()


class ProgressManager:
    """進捗管理クラス"""
    
    def __init__(self, parent):
        self.parent = parent
        self.current_dialog: Optional[ProgressDialog] = None
        self.indeterminate_dialog: Optional[IndeterminateProgressDialog] = None
    
    def show_progress(self, title: str = "処理中", cancelable: bool = True) -> ProgressDialog:
        """進捗ダイアログを表示"""
        self.close_current()
        self.current_dialog = ProgressDialog(self.parent, title, cancelable)
        return self.current_dialog
    
    def show_indeterminate(self, title: str = "処理中", message: str = "しばらくお待ちください...") -> IndeterminateProgressDialog:
        """不定進捗ダイアログを表示"""
        self.close_current()
        self.indeterminate_dialog = IndeterminateProgressDialog(self.parent, title, message)
        return self.indeterminate_dialog
    
    def close_current(self):
        """現在のダイアログを閉じる"""
        if self.current_dialog:
            self.current_dialog.close()
            self.current_dialog = None
        
        if self.indeterminate_dialog:
            self.indeterminate_dialog.close()
            self.indeterminate_dialog = None
    
    def is_showing(self) -> bool:
        """ダイアログが表示中かどうか"""
        return self.current_dialog is not None or self.indeterminate_dialog is not None


# テスト用関数
def test_progress_dialog():
    """進捗ダイアログのテスト"""
    import time
    import threading
    
    root = tk.Tk()
    root.title("進捗ダイアログ テスト")
    root.geometry("300x200")
    
    def test_determinate():
        """確定進捗テスト"""
        manager = ProgressManager(root)
        dialog = manager.show_progress("テスト処理", True)
        
        def worker():
            try:
                for i in range(101):
                    if dialog.is_canceled():
                        break
                    dialog.update(f"ステップ {i}/100", i)
                    time.sleep(0.05)
                dialog.close()
            except:
                dialog.close()
        
        threading.Thread(target=worker, daemon=True).start()
    
    def test_indeterminate():
        """不定進捗テスト"""
        manager = ProgressManager(root)
        dialog = manager.show_indeterminate("データ取得中", "YouTube APIに接続中...")
        
        def worker():
            time.sleep(3)
            dialog.set_message("プレイリスト情報を取得中...")
            time.sleep(2)
            dialog.close()
        
        threading.Thread(target=worker, daemon=True).start()
    
    # テストボタン
    ttk.Button(root, text="確定進捗テスト", command=test_determinate).pack(pady=10)
    ttk.Button(root, text="不定進捗テスト", command=test_indeterminate).pack(pady=10)
    
    root.mainloop()


if __name__ == "__main__":
    test_progress_dialog()
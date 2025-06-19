"""
メインウィンドウ

プレイリスト管理GUIのメインインターフェース
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import sys
from pathlib import Path
import threading
import time

# パス設定
sys.path.append(str(Path(__file__).parent.parent))

from gui.widgets.status_panel import StatusPanel
from gui.widgets.playlist_tree import PlaylistTree
from gui.widgets.progress_dialog import ProgressManager
from gui.utils.async_worker import global_task_manager

from managers.playlist_manager import PlaylistManager
from managers.multi_incremental_manager import MultiIncrementalManager
from managers.integrated_workflow_manager import IntegratedWorkflowManager
from analyzers.batch_analyzer import BatchAnalyzer
from core.data_models import PlaylistCategory, UpdateFrequency


class MainWindow:
    """メインウィンドウクラス"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        
        # 管理システム初期化
        self.playlist_manager = PlaylistManager()
        self.incremental_manager = MultiIncrementalManager()
        self.workflow_manager = IntegratedWorkflowManager()
        self.batch_analyzer = BatchAnalyzer()
        
        # GUI管理
        self.progress_manager = ProgressManager(self.root)
        
        # ウィジェット作成
        self.create_widgets()
        
        # イベントバインド
        self.bind_events()
        
        # 定期更新開始
        self.start_periodic_update()
    
    def setup_window(self):
        """ウィンドウの基本設定"""
        self.root.title("🎵 YouTube知識システム - プレイリスト管理")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
        # アイコン設定（もしあれば）
        try:
            # アイコンファイルがあれば設定
            pass
        except:
            pass
        
        # 終了処理
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_widgets(self):
        """ウィジェットを作成"""
        # メニューバー
        self.create_menu()
        
        # メインフレーム
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 上部：状態表示パネル
        self.status_panel = StatusPanel(main_frame)
        self.status_panel.pack(fill='x', pady=(0, 5))
        
        # 中央：プレイリスト一覧
        self.playlist_tree = PlaylistTree(main_frame)
        self.playlist_tree.pack(fill='both', expand=True, pady=(0, 5))
        
        # 下部：アクションボタン
        self.create_action_buttons(main_frame)
        
        # ステータスバー
        self.create_status_bar()
    
    def create_menu(self):
        """メニューバーを作成"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # ファイルメニュー
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="ファイル", menu=file_menu)
        file_menu.add_command(label="プレイリスト追加...", command=self.add_playlist_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="設定...", command=self.show_settings)
        file_menu.add_separator()
        file_menu.add_command(label="終了", command=self.on_closing)
        
        # 更新メニュー
        update_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="更新", menu=update_menu)
        update_menu.add_command(label="全プレイリスト差分更新", command=self.update_all_playlists)
        update_menu.add_command(label="選択プレイリスト更新", command=self.update_selected_playlist)
        update_menu.add_separator()
        update_menu.add_command(label="強制全更新", command=self.force_update_all)
        
        # 分析メニュー
        analysis_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="分析", menu=analysis_menu)
        analysis_menu.add_command(label="バッチ分析実行", command=self.run_batch_analysis)
        analysis_menu.add_command(label="少量分析 (5件)", command=lambda: self.run_batch_analysis(5))
        analysis_menu.add_separator()
        analysis_menu.add_command(label="分析進捗確認", command=self.show_analysis_progress)
        
        # ワークフローメニュー
        workflow_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="ワークフロー", menu=workflow_menu)
        workflow_menu.add_command(label="統合ワークフロー実行", command=self.run_full_workflow)
        workflow_menu.add_command(label="スケジュール更新", command=self.run_scheduled_update)
        workflow_menu.add_separator()
        workflow_menu.add_command(label="レポート生成", command=self.generate_report)
        
        # ヘルプメニュー
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="ヘルプ", menu=help_menu)
        help_menu.add_command(label="使用方法", command=self.show_help)
        help_menu.add_command(label="バージョン情報", command=self.show_about)
    
    def create_action_buttons(self, parent):
        """アクションボタンを作成"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill='x', pady=5)
        
        # 左側ボタン群
        left_frame = ttk.Frame(button_frame)
        left_frame.pack(side='left')
        
        ttk.Button(
            left_frame,
            text="➕ プレイリスト追加",
            command=self.add_playlist_dialog,
            width=15
        ).pack(side='left', padx=(0, 5))
        
        ttk.Button(
            left_frame,
            text="🔄 差分更新",
            command=self.update_all_playlists,
            width=12
        ).pack(side='left', padx=(0, 5))
        
        ttk.Button(
            left_frame,
            text="🔍 分析実行",
            command=lambda: self.run_batch_analysis(10),
            width=12
        ).pack(side='left', padx=(0, 5))
        
        # 中央スペース
        ttk.Frame(button_frame).pack(side='left', expand=True, fill='x')
        
        # 右側ボタン群
        right_frame = ttk.Frame(button_frame)
        right_frame.pack(side='right')
        
        ttk.Button(
            right_frame,
            text="⚡ ワークフロー",
            command=self.run_full_workflow,
            width=12
        ).pack(side='left', padx=(5, 0))
        
        ttk.Button(
            right_frame,
            text="⚙️ 設定",
            command=self.show_settings,
            width=8
        ).pack(side='left', padx=(5, 0))
    
    def create_status_bar(self):
        """ステータスバーを作成"""
        self.status_var = tk.StringVar()
        self.status_var.set("準備完了")
        
        status_bar = ttk.Label(
            self.root,
            textvariable=self.status_var,
            relief='sunken',
            anchor='w'
        )
        status_bar.pack(side='bottom', fill='x')
    
    def bind_events(self):
        """イベントをバインド"""
        # プレイリスト一覧のカスタムイベント
        self.playlist_tree.bind('<<UpdatePlaylist>>', self.on_update_playlist)
        self.playlist_tree.bind('<<EditPlaylist>>', self.on_edit_playlist)
    
    def start_periodic_update(self):
        """定期更新を開始"""
        def update_status():
            try:
                # タスクが実行中でなければ状態表示を更新
                if not global_task_manager.is_any_running():
                    self.status_panel.update_status()
                    self.status_var.set("準備完了")
                else:
                    self.status_var.set("処理実行中...")
            except:
                pass
            
            # 30秒後に再実行
            self.root.after(30000, update_status)
        
        # 5秒後に初回実行
        self.root.after(5000, update_status)
    
    def set_status(self, message: str):
        """ステータスメッセージを設定"""
        self.status_var.set(message)
        self.root.update_idletasks()
    
    # プレイリスト管理
    def add_playlist_dialog(self):
        """プレイリスト追加ダイアログ"""
        dialog = PlaylistAddDialog(self.root, self.playlist_manager)
        if dialog.result:
            self.refresh_all()
            messagebox.showinfo("成功", "プレイリストを追加しました")
    
    def on_update_playlist(self, event):
        """プレイリスト更新イベント"""
        playlist_id = self.playlist_tree.get_selected_playlist_id()
        if playlist_id:
            self.update_specific_playlist(playlist_id)
    
    def on_edit_playlist(self, event):
        """プレイリスト編集イベント"""
        playlist_id = self.playlist_tree.get_selected_playlist_id()
        if playlist_id:
            dialog = PlaylistEditDialog(self.root, self.playlist_manager, playlist_id)
            if dialog.result:
                self.refresh_all()
    
    # 更新処理
    def update_all_playlists(self):
        """全プレイリスト差分更新"""
        def worker(progress_callback):
            return self.incremental_manager.update_multiple_playlists(
                force_update=False,
                priority_order=True,
                enabled_only=True
            )
        
        self.run_async_task(
            "差分更新",
            worker,
            "プレイリストの差分更新を実行中...",
            self.on_update_complete
        )
    
    def update_specific_playlist(self, playlist_id: str):
        """特定プレイリスト更新"""
        def worker(progress_callback):
            return self.incremental_manager.update_multiple_playlists(
                playlist_ids=[playlist_id],
                force_update=False
            )
        
        self.run_async_task(
            "プレイリスト更新",
            worker,
            f"プレイリスト {playlist_id} を更新中...",
            self.on_update_complete
        )
    
    def update_selected_playlist(self):
        """選択プレイリスト更新"""
        playlist_id = self.playlist_tree.get_selected_playlist_id()
        if not playlist_id:
            messagebox.showwarning("警告", "プレイリストを選択してください")
            return
        self.update_specific_playlist(playlist_id)
    
    def force_update_all(self):
        """強制全更新"""
        result = messagebox.askyesno(
            "確認",
            "強制更新を実行しますか？\n全プレイリストを更新頻度に関係なく更新します。"
        )
        if not result:
            return
        
        def worker(progress_callback):
            return self.incremental_manager.update_multiple_playlists(
                force_update=True,
                priority_order=True,
                enabled_only=True
            )
        
        self.run_async_task(
            "強制更新",
            worker,
            "全プレイリストを強制更新中...",
            self.on_update_complete
        )
    
    # 分析処理
    def run_batch_analysis(self, max_videos: int = None):
        """バッチ分析実行"""
        # 分析対象確認
        progress = self.batch_analyzer.get_analysis_progress()
        if progress['pending'] == 0:
            messagebox.showinfo("情報", "分析対象の動画がありません")
            return
        
        target_count = min(progress['pending'], max_videos) if max_videos else progress['pending']
        
        result = messagebox.askyesno(
            "確認",
            f"動画分析を実行しますか？\n対象: {target_count}件"
        )
        if not result:
            return
        
        def worker(progress_callback):
            return self.batch_analyzer.run_batch_analysis(max_videos=max_videos)
        
        self.run_async_task(
            "動画分析",
            worker,
            f"動画分析を実行中... (最大{target_count}件)",
            self.on_analysis_complete
        )
    
    def show_analysis_progress(self):
        """分析進捗表示"""
        progress = self.batch_analyzer.get_analysis_progress()
        
        message = f"""分析進捗状況:
        
総動画数: {progress['total_videos']}
完了: {progress['completed']}件
未分析: {progress['pending']}件
失敗: {progress['failed']}件

成功率: {progress['success_rate']:.1%}
完了率: {progress['completion_rate']:.1%}"""
        
        messagebox.showinfo("分析進捗", message)
    
    # ワークフロー処理
    def run_full_workflow(self):
        """統合ワークフロー実行"""
        result = messagebox.askyesno(
            "確認",
            "統合ワークフローを実行しますか？\n\n実行内容:\n1. 差分更新\n2. 動画分析\n3. レポート生成"
        )
        if not result:
            return
        
        def worker(progress_callback):
            return self.workflow_manager.execute_full_workflow(
                force_update=False,
                auto_analyze=True,
                generate_report=True
            )
        
        self.run_async_task(
            "統合ワークフロー",
            worker,
            "統合ワークフローを実行中...",
            self.on_workflow_complete
        )
    
    def run_scheduled_update(self):
        """スケジュール更新実行"""
        def worker(progress_callback):
            return self.workflow_manager.execute_scheduled_update()
        
        self.run_async_task(
            "スケジュール更新",
            worker,
            "スケジュール更新を実行中...",
            self.on_update_complete
        )
    
    def generate_report(self):
        """レポート生成"""
        def worker(progress_callback):
            return self.workflow_manager.generate_comprehensive_report()
        
        self.run_async_task(
            "レポート生成",
            worker,
            "レポートを生成中...",
            self.on_report_complete
        )
    
    # 非同期処理管理
    def run_async_task(self, task_name: str, worker_func, message: str, callback=None):
        """非同期タスクを実行"""
        if global_task_manager.is_any_running():
            messagebox.showwarning("警告", "他の処理が実行中です。しばらくお待ちください。")
            return
        
        # 進捗ダイアログ表示
        progress_dialog = self.progress_manager.show_indeterminate(task_name, message)
        
        def task_worker():
            try:
                start_time = time.time()
                result = worker_func(lambda msg, prog=None: progress_dialog.set_message(msg))
                duration = time.time() - start_time
                
                # メインスレッドで結果処理
                self.root.after(0, lambda: self.handle_task_result(task_name, result, duration, callback, progress_dialog))
                
            except Exception as e:
                # メインスレッドでエラー処理
                self.root.after(0, lambda: self.handle_task_error(task_name, str(e), progress_dialog))
        
        # ワーカー開始
        worker = global_task_manager.create_worker(task_name)
        worker.start_task(task_worker)
    
    def handle_task_result(self, task_name: str, result, duration: float, callback, progress_dialog):
        """タスク結果処理"""
        progress_dialog.close()
        
        # 履歴に追加
        global_task_manager.add_to_history(task_name, "成功", duration)
        
        # コールバック実行
        if callback:
            callback(result)
        
        # 画面更新
        self.refresh_all()
        self.set_status("準備完了")
    
    def handle_task_error(self, task_name: str, error_message: str, progress_dialog):
        """タスクエラー処理"""
        progress_dialog.close()
        
        # 履歴に追加
        global_task_manager.add_to_history(task_name, f"エラー: {error_message}")
        
        # エラー表示
        messagebox.showerror("エラー", f"{task_name}でエラーが発生しました:\n{error_message}")
        
        self.set_status("準備完了")
    
    # 結果処理コールバック
    def on_update_complete(self, result):
        """更新完了処理"""
        if result.get('success'):
            stats = result.get('stats', {})
            message = f"""更新完了:
            
更新: {stats.get('updated_playlists', 0)}件
スキップ: {stats.get('skipped_playlists', 0)}件
失敗: {stats.get('failed_playlists', 0)}件
新規動画: {stats.get('total_new_videos', 0)}件"""
            messagebox.showinfo("更新完了", message)
    
    def on_analysis_complete(self, result):
        """分析完了処理"""
        message = f"""分析完了:
        
処理: {result.get('processed_videos', 0)}件
成功: {result.get('successful_analyses', 0)}件
失敗: {result.get('failed_analyses', 0)}件
成功率: {result.get('successful_analyses', 0) / result.get('processed_videos', 1) * 100:.1f}%"""
        messagebox.showinfo("分析完了", message)
    
    def on_workflow_complete(self, result):
        """ワークフロー完了処理"""
        if result.get('overall_success'):
            messagebox.showinfo("ワークフロー完了", "統合ワークフローが正常に完了しました")
        else:
            errors = '\n'.join(result.get('errors', []))
            messagebox.showerror("ワークフローエラー", f"ワークフローでエラーが発生しました:\n{errors}")
    
    def on_report_complete(self, result):
        """レポート完了処理"""
        report_file = result.get('report_file')
        if report_file:
            messagebox.showinfo("レポート生成完了", f"レポートを生成しました:\n{report_file}")
        else:
            messagebox.showinfo("レポート生成完了", "レポートを生成しました")
    
    # その他
    def refresh_all(self):
        """全画面を更新"""
        self.status_panel.update_status()
        self.playlist_tree.refresh_data()
    
    def show_settings(self):
        """設定ダイアログ"""
        messagebox.showinfo("設定", "設定機能は今後実装予定です")
    
    def show_help(self):
        """ヘルプ表示"""
        help_text = """YouTube知識システム 使用方法:

1. プレイリスト追加:
   [➕ プレイリスト追加] ボタンまたは
   メニュー > ファイル > プレイリスト追加

2. 差分更新:
   [🔄 差分更新] ボタンで新規動画を取得

3. 動画分析:
   [🔍 分析実行] ボタンでGPT-4分析を実行

4. 統合ワークフロー:
   [⚡ ワークフロー] ボタンで
   更新→分析→レポート生成を一括実行

5. プレイリスト操作:
   一覧を右クリックで詳細操作"""
        
        messagebox.showinfo("使用方法", help_text)
    
    def show_about(self):
        """バージョン情報"""
        about_text = """YouTube知識システム
プレイリスト管理GUI

バージョン: 1.0.0
作成者: せつなBot開発チーム

複数プレイリストの効率的な管理と
GPT-4による動画分析を提供します。"""
        
        messagebox.showinfo("バージョン情報", about_text)
    
    def on_closing(self):
        """終了処理"""
        if global_task_manager.is_any_running():
            result = messagebox.askyesno(
                "確認",
                "処理が実行中です。終了しますか？"
            )
            if not result:
                return
            
            global_task_manager.stop_all()
        
        self.root.destroy()
    
    def run(self):
        """アプリケーション実行"""
        self.root.mainloop()


class PlaylistAddDialog:
    """プレイリスト追加ダイアログ"""
    
    def __init__(self, parent, playlist_manager):
        self.parent = parent
        self.playlist_manager = playlist_manager
        self.result = False
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("プレイリスト追加")
        self.dialog.geometry("500x500")
        self.dialog.resizable(True, True)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_widgets()
        self.center_on_parent()
    
    def center_on_parent(self):
        """親ウィンドウの中央に配置"""
        self.dialog.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() - self.dialog.winfo_width()) // 2
        y = self.parent.winfo_y() + (self.parent.winfo_height() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{x}+{y}")
    
    def create_widgets(self):
        """ウィジェットを作成"""
        # スクロール可能なフレームを作成
        canvas = tk.Canvas(self.dialog)
        scrollbar = ttk.Scrollbar(self.dialog, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # パックレイアウト
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # メインフレーム
        main_frame = ttk.Frame(self.scrollable_frame, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # マウスホイールスクロール対応（修正版）
        self.canvas = canvas  # cleanup用に保存
        def _on_mousewheel(event):
            try:
                if canvas.winfo_exists():
                    canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except (tk.TclError, AttributeError):
                pass  # ダイアログが閉じられている場合は無視
        
        # イベントハンドラを保存
        self._mousewheel_handler = _on_mousewheel
        
        # canvasのみにバインド（ダイアログ全体は無効化）
        canvas.bind("<MouseWheel>", _on_mousewheel)
        
        # URL入力
        ttk.Label(main_frame, text="プレイリストURL/ID:").pack(anchor='w')
        self.url_var = tk.StringVar()
        url_entry = ttk.Entry(main_frame, textvariable=self.url_var, width=60)
        url_entry.pack(fill='x', pady=(5, 10))
        url_entry.focus()
        
        # 表示名
        ttk.Label(main_frame, text="表示名 (省略可):").pack(anchor='w')
        self.name_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.name_var, width=60).pack(fill='x', pady=(5, 10))
        
        # カテゴリ
        ttk.Label(main_frame, text="カテゴリ:").pack(anchor='w')
        self.category_var = tk.StringVar(value="other")
        category_combo = ttk.Combobox(
            main_frame,
            textvariable=self.category_var,
            values=[cat.value for cat in PlaylistCategory],
            state='readonly'
        )
        category_combo.pack(fill='x', pady=(5, 10))
        
        # 更新頻度
        ttk.Label(main_frame, text="更新頻度:").pack(anchor='w')
        self.frequency_var = tk.StringVar(value="manual")
        frequency_combo = ttk.Combobox(
            main_frame,
            textvariable=self.frequency_var,
            values=[freq.value for freq in UpdateFrequency],
            state='readonly'
        )
        frequency_combo.pack(fill='x', pady=(5, 10))
        
        # 優先度
        ttk.Label(main_frame, text="優先度 (1-5):").pack(anchor='w')
        self.priority_var = tk.IntVar(value=3)
        priority_spin = ttk.Spinbox(main_frame, from_=1, to=5, textvariable=self.priority_var, width=10)
        priority_spin.pack(anchor='w', pady=(5, 10))
        
        # オプション
        self.auto_analyze_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(main_frame, text="自動分析を有効にする", variable=self.auto_analyze_var).pack(anchor='w', pady=5)
        
        self.verify_access_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(main_frame, text="アクセス検証を行う", variable=self.verify_access_var).pack(anchor='w', pady=5)
        
        self.collect_immediately_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(main_frame, text="即座にデータ収集", variable=self.collect_immediately_var).pack(anchor='w', pady=5)
        
        # ボタン
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(side='bottom', fill='x', pady=(20, 0))
        
        def safe_close():
            try:
                if hasattr(self, 'canvas'):
                    self.canvas.unbind("<MouseWheel>")
                self.dialog.destroy()
            except:
                pass
        
        ttk.Button(button_frame, text="キャンセル", command=safe_close).pack(side='right', padx=(5, 0))
        ttk.Button(button_frame, text="追加", command=self.add_playlist).pack(side='right')
    
    def add_playlist(self):
        """プレイリスト追加実行"""
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("警告", "URLまたはIDを入力してください")
            return
        
        try:
            # プレイリスト追加実行
            success, message, result = self.playlist_manager.add_playlist_from_url(
                url_or_id=url,
                display_name=self.name_var.get().strip(),
                category=PlaylistCategory(self.category_var.get()),
                update_frequency=UpdateFrequency(self.frequency_var.get()),
                priority=self.priority_var.get(),
                auto_analyze=self.auto_analyze_var.get(),
                verify_access=self.verify_access_var.get(),
                collect_immediately=self.collect_immediately_var.get()
            )
            
            if success:
                self.result = True
                try:
                    if hasattr(self, 'canvas'):
                        self.canvas.unbind("<MouseWheel>")
                    self.dialog.destroy()
                except:
                    pass
            else:
                messagebox.showerror("エラー", message)
                
        except Exception as e:
            messagebox.showerror("エラー", f"追加処理でエラーが発生しました: {e}")


class PlaylistEditDialog:
    """プレイリスト編集ダイアログ"""
    
    def __init__(self, parent, playlist_manager, playlist_id):
        self.parent = parent
        self.playlist_manager = playlist_manager
        self.playlist_id = playlist_id
        self.result = False
        
        # 現在の設定を取得
        self.config = playlist_manager.config_manager.get_config(playlist_id)
        if not self.config:
            messagebox.showerror("エラー", "プレイリスト設定が見つかりません")
            return
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"プレイリスト編集 - {self.config.display_name}")
        self.dialog.geometry("500x450")
        self.dialog.resizable(True, True)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_widgets()
        self.center_on_parent()
    
    def center_on_parent(self):
        """親ウィンドウの中央に配置"""
        self.dialog.update_idletasks()
        x = self.parent.winfo_x() + (self.parent.winfo_width() - self.dialog.winfo_width()) // 2
        y = self.parent.winfo_y() + (self.parent.winfo_height() - self.dialog.winfo_height()) // 2
        self.dialog.geometry(f"+{x}+{y}")
    
    def create_widgets(self):
        """ウィジェットを作成"""
        # スクロール可能なフレームを作成
        canvas = tk.Canvas(self.dialog)
        scrollbar = ttk.Scrollbar(self.dialog, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # パックレイアウト
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # メインフレーム
        main_frame = ttk.Frame(self.scrollable_frame, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # マウスホイールスクロール対応（修正版）
        self.canvas = canvas  # cleanup用に保存
        def _on_mousewheel(event):
            try:
                if canvas.winfo_exists():
                    canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            except (tk.TclError, AttributeError):
                pass  # ダイアログが閉じられている場合は無視
        
        # イベントハンドラを保存
        self._mousewheel_handler = _on_mousewheel
        
        # canvasのみにバインド（ダイアログ全体は無効化）
        canvas.bind("<MouseWheel>", _on_mousewheel)
        
        # 表示名
        ttk.Label(main_frame, text="表示名:").pack(anchor='w')
        self.name_var = tk.StringVar(value=self.config.display_name)
        ttk.Entry(main_frame, textvariable=self.name_var, width=60).pack(fill='x', pady=(5, 10))
        
        # カテゴリ
        ttk.Label(main_frame, text="カテゴリ:").pack(anchor='w')
        self.category_var = tk.StringVar(value=self.config.category.value)
        category_combo = ttk.Combobox(
            main_frame,
            textvariable=self.category_var,
            values=[cat.value for cat in PlaylistCategory],
            state='readonly'
        )
        category_combo.pack(fill='x', pady=(5, 10))
        
        # 更新頻度
        ttk.Label(main_frame, text="更新頻度:").pack(anchor='w')
        self.frequency_var = tk.StringVar(value=self.config.update_frequency.value)
        frequency_combo = ttk.Combobox(
            main_frame,
            textvariable=self.frequency_var,
            values=[freq.value for freq in UpdateFrequency],
            state='readonly'
        )
        frequency_combo.pack(fill='x', pady=(5, 10))
        
        # 優先度
        ttk.Label(main_frame, text="優先度 (1-5):").pack(anchor='w')
        self.priority_var = tk.IntVar(value=self.config.priority)
        priority_spin = ttk.Spinbox(main_frame, from_=1, to=5, textvariable=self.priority_var, width=10)
        priority_spin.pack(anchor='w', pady=(5, 10))
        
        # オプション
        self.enabled_var = tk.BooleanVar(value=self.config.enabled)
        ttk.Checkbutton(main_frame, text="有効", variable=self.enabled_var).pack(anchor='w', pady=5)
        
        self.auto_analyze_var = tk.BooleanVar(value=self.config.auto_analyze)
        ttk.Checkbutton(main_frame, text="自動分析を有効にする", variable=self.auto_analyze_var).pack(anchor='w', pady=5)
        
        # 説明
        ttk.Label(main_frame, text="説明:").pack(anchor='w', pady=(10, 0))
        self.description_var = tk.StringVar(value=self.config.description)
        ttk.Entry(main_frame, textvariable=self.description_var, width=60).pack(fill='x', pady=(5, 10))
        
        # ボタン
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(side='bottom', fill='x', pady=(20, 0))
        
        def safe_close():
            try:
                if hasattr(self, 'canvas'):
                    self.canvas.unbind("<MouseWheel>")
                self.dialog.destroy()
            except:
                pass
        
        ttk.Button(button_frame, text="キャンセル", command=safe_close).pack(side='right', padx=(5, 0))
        ttk.Button(button_frame, text="保存", command=self.save_changes).pack(side='right')
    
    def save_changes(self):
        """変更を保存"""
        try:
            # 更新内容を準備
            updates = {
                'display_name': self.name_var.get().strip(),
                'category': self.category_var.get(),
                'update_frequency': self.frequency_var.get(),
                'priority': self.priority_var.get(),
                'enabled': self.enabled_var.get(),
                'auto_analyze': self.auto_analyze_var.get(),
                'description': self.description_var.get().strip()
            }
            
            # 更新実行
            success, message = self.playlist_manager.config_manager.update_config(
                self.playlist_id, **updates
            )
            
            if success:
                self.result = True
                try:
                    if hasattr(self, 'canvas'):
                        self.canvas.unbind("<MouseWheel>")
                    self.dialog.destroy()
                except:
                    pass
            else:
                messagebox.showerror("エラー", message)
                
        except Exception as e:
            messagebox.showerror("エラー", f"保存処理でエラーが発生しました: {e}")


def main():
    """メイン関数"""
    try:
        app = MainWindow()
        app.run()
    except Exception as e:
        messagebox.showerror("起動エラー", f"アプリケーションの起動に失敗しました:\n{e}")


if __name__ == "__main__":
    main()
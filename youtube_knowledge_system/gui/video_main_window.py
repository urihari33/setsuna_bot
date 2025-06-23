# -*- coding: utf-8 -*-
"""
動画中心メインウィンドウ

統合データベース中心の動画ライブラリ管理GUI
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
from pathlib import Path
import threading
import time

# パス設定
sys.path.append(str(Path(__file__).parent.parent))

from gui.widgets.video_list import VideoListWidget
from gui.widgets.video_detail import VideoDetailPanel
from gui.widgets.status_panel import StatusPanel
from gui.widgets.progress_dialog import ProgressManager
from gui.utils.async_worker import global_task_manager

from storage.unified_storage import UnifiedStorage
from analyzers.description_analyzer import DescriptionAnalyzer
from config.settings import DATA_DIR
from collectors.multi_playlist_collector import MultiPlaylistCollector


class VideoMainWindow:
    """動画中心メインウィンドウクラス"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        
        # サービス初期化
        self.storage = UnifiedStorage(DATA_DIR)
        self.analyzer = DescriptionAnalyzer()
        self.collector = MultiPlaylistCollector()
        
        # GUI管理
        self.progress_manager = ProgressManager(self.root)
        
        # ウィジェット作成
        self.create_widgets()
        
        # 定期更新開始
        self.start_periodic_update()
    
    def setup_window(self):
        """ウィンドウの基本設定"""
        self.root.title("🎵 YouTube知識システム - 動画ライブラリ")
        self.root.geometry("1400x800")
        self.root.minsize(1000, 600)
        
        # 終了処理
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_widgets(self):
        """ウィジェットを作成"""
        # メニューバー
        self.create_menu()
        
        # メインフレーム
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 上部：ステータスパネル
        self.status_panel = StatusPanel(main_frame)
        self.status_panel.pack(fill='x', pady=(0, 5))
        
        # 中央：動画一覧と詳細パネル
        self.create_main_content(main_frame)
        
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
        file_menu.add_command(label="データ更新", command=self.refresh_data)
        file_menu.add_separator()
        file_menu.add_command(label="エクスポート...", command=self.export_data)
        file_menu.add_separator()
        file_menu.add_command(label="終了", command=self.on_closing)
        
        # プレイリストメニュー
        playlist_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="プレイリスト", menu=playlist_menu)
        playlist_menu.add_command(label="プレイリスト追加...", command=self.add_playlist_dialog)
        playlist_menu.add_command(label="プレイリスト同期", command=self.sync_playlists)
        
        # 分析メニュー
        analysis_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="分析", menu=analysis_menu)
        analysis_menu.add_command(label="未分析動画を全件分析", command=self.run_full_batch_analysis)
        analysis_menu.add_command(label="少量分析 (10件)", command=lambda: self.run_batch_analysis(10))
        analysis_menu.add_command(label="カスタム分析...", command=self.run_custom_batch_analysis)
        analysis_menu.add_separator()
        analysis_menu.add_command(label="選択動画分析", command=self.analyze_selected_video)
        analysis_menu.add_separator()
        analysis_menu.add_command(label="分析進捗確認", command=self.show_analysis_progress)
        
        # 表示メニュー
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="表示", menu=view_menu)
        view_menu.add_command(label="詳細パネル切り替え", command=self.toggle_detail_panel)
        view_menu.add_command(label="フィルタリセット", command=self.reset_filters)
        
        # ヘルプメニュー
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="ヘルプ", menu=help_menu)
        help_menu.add_command(label="使用方法", command=self.show_help)
        help_menu.add_command(label="バージョン情報", command=self.show_about)
    
    def create_main_content(self, parent):
        """メインコンテンツエリアを作成"""
        # デバッグ用：シンプルなレイアウトで動画一覧のみ表示
        
        # 動画一覧ウィジェット（親に直接配置）
        self.video_list = VideoListWidget(parent)
        self.video_list.pack(fill='both', expand=True, padx=5, pady=5)
        self.video_list.set_selection_callback(self.on_video_selected)
        
        # 初期データ読み込みを明示的に実行
        self.root.after(100, self.video_list.load_videos)
        
        # 動画詳細パネル（暫定的に非表示）
        # TODO: 動画一覧が表示されることを確認後、分割レイアウトに戻す
    
    def create_action_buttons(self, parent):
        """アクションボタンを作成"""
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill='x', pady=5)
        
        # 左側ボタン群
        left_frame = ttk.Frame(button_frame)
        left_frame.pack(side='left')
        
        ttk.Button(
            left_frame,
            text="🔄 データ更新",
            command=self.refresh_data,
            width=12
        ).pack(side='left', padx=(0, 5))
        
        ttk.Button(
            left_frame,
            text="➕ プレイリスト追加",
            command=self.add_playlist_dialog,
            width=15
        ).pack(side='left', padx=(0, 5))
        
        ttk.Button(
            left_frame,
            text="🔍 少量分析",
            command=lambda: self.run_batch_analysis(10),
            width=12
        ).pack(side='left', padx=(0, 5))
        
        ttk.Button(
            left_frame,
            text="🔄 全件分析",
            command=self.run_full_batch_analysis,
            width=12
        ).pack(side='left', padx=(0, 5))
        
        ttk.Button(
            left_frame,
            text="📊 進捗確認",
            command=self.show_analysis_progress,
            width=12
        ).pack(side='left', padx=(0, 5))
        
        # 中央スペース
        ttk.Frame(button_frame).pack(side='left', expand=True, fill='x')
        
        # 右側ボタン群
        right_frame = ttk.Frame(button_frame)
        right_frame.pack(side='right')
        
        ttk.Button(
            right_frame,
            text="📋 エクスポート",
            command=self.export_data,
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
    
    def start_periodic_update(self):
        """定期更新を開始"""
        def update_status():
            try:
                # タスクが実行中でなければ状態表示を更新
                if not global_task_manager.is_any_running():
                    # ステータスパネルの更新
                    self.status_panel.update_status()
                    self.status_var.set("準備完了")
                else:
                    self.status_var.set("処理実行中...")
            except Exception as e:
                print(f"定期更新エラー: {e}")
            
            # 30秒後に再実行
            self.root.after(30000, update_status)
        
        # 5秒後に初回実行
        self.root.after(5000, update_status)
    
    def on_video_selected(self, video_id: str, video):
        """動画選択時の処理"""
        self.video_detail.display_video(video_id, video)
    
    def refresh_data(self):
        """データを更新"""
        try:
            self.status_var.set("データを更新中...")
            
            # 統合ストレージの再読み込みを強制
            self.storage._database = None
            
            # 各コンポーネントの更新
            self.video_list.refresh()
            self.status_panel.update_status()
            
            # 最新の統計情報を取得して表示
            stats = self.storage.get_statistics()
            update_message = f"データを更新しました (動画: {stats['total_videos']}件, プレイリスト: {stats['total_playlists']}件)"
            self.status_var.set(update_message)
            
            # 5秒後に通常状態に戻す
            self.root.after(5000, lambda: self.status_var.set("準備完了"))
            
        except Exception as e:
            self.status_var.set(f"更新エラー: {e}")
            messagebox.showerror("エラー", f"データ更新でエラーが発生しました: {e}")
    
    def run_batch_analysis(self, max_videos: int = None):
        """バッチ分析実行"""
        # 分析対象確認
        videos = self.storage.get_all_videos()
        pending_videos = [vid for vid, video in videos.items() if video.analysis_status.value == 'pending']
        
        if len(pending_videos) == 0:
            messagebox.showinfo("情報", "分析対象の動画がありません")
            return
        
        target_count = min(len(pending_videos), max_videos) if max_videos else len(pending_videos)
        
        result = messagebox.askyesno(
            "確認",
            f"動画分析を実行しますか？\n対象: {target_count}件\n\n※ OpenAI APIを使用します"
        )
        if not result:
            return
        
        def worker(progress_callback):
            analyzed_count = 0
            failed_count = 0
            
            for i, video_id in enumerate(pending_videos[:target_count]):
                if progress_callback:
                    progress_callback(f"動画分析中... ({i+1}/{target_count})")
                
                video = videos[video_id]
                if video.metadata.description:
                    try:
                        result = self.analyzer.analyze_description(video.metadata.description)
                        if result:
                            self.storage.update_video_analysis(video_id, 'completed', creative_insight=result)
                            analyzed_count += 1
                        else:
                            self.storage.update_video_analysis(video_id, 'failed', analysis_error='分析失敗')
                            failed_count += 1
                    except Exception as e:
                        self.storage.update_video_analysis(video_id, 'failed', analysis_error=str(e))
                        failed_count += 1
                else:
                    self.storage.update_video_analysis(video_id, 'failed', analysis_error='概要欄が空')
                    failed_count += 1
            
            return {'analyzed_count': analyzed_count, 'failed_count': failed_count}
        
        self.run_async_task(
            "動画分析",
            worker,
            f"動画分析を実行中... (最大{target_count}件)",
            self.on_analysis_complete
        )
    
    def analyze_selected_video(self):
        """選択動画の分析実行"""
        selected = self.video_list.get_selected_video()
        if not selected:
            messagebox.showwarning("警告", "分析する動画を選択してください")
            return
        
        # 詳細パネルの分析機能を呼び出す
        self.video_detail.analyze_video()
    
    def show_analysis_progress(self):
        """分析進捗表示"""
        videos = self.storage.get_all_videos()
        
        total_videos = len(videos)
        completed = sum(1 for v in videos.values() if v.analysis_status.value == 'completed')
        pending = sum(1 for v in videos.values() if v.analysis_status.value == 'pending')
        failed = sum(1 for v in videos.values() if v.analysis_status.value == 'failed')
        
        success_rate = completed / total_videos if total_videos > 0 else 0
        completion_rate = (completed + failed) / total_videos if total_videos > 0 else 0
        
        message = f"""分析進捗状況:

総動画数: {total_videos}
完了: {completed}件
未分析: {pending}件
失敗: {failed}件

成功率: {success_rate:.1%}
完了率: {completion_rate:.1%}"""
        
        messagebox.showinfo("分析進捗", message)
    
    def toggle_detail_panel(self):
        """詳細パネルの表示切り替え"""
        # TODO: 詳細パネルの表示/非表示切り替え
        messagebox.showinfo("情報", "詳細パネル切り替え機能は今後実装予定です")
    
    def reset_filters(self):
        """フィルタをリセット"""
        self.video_list.search_var.set("")
        self.video_list.status_filter_var.set("全て")
        self.video_list.apply_filters()
    
    def export_data(self):
        """データエクスポート"""
        try:
            from tkinter import filedialog
            
            file_path = filedialog.asksaveasfilename(
                title="エクスポート先を選択",
                defaultextension=".json",
                filetypes=[("JSONファイル", "*.json"), ("すべてのファイル", "*.*")]
            )
            
            if file_path:
                # エクスポート実行
                export_path = self.storage.export_for_setsuna(Path(file_path))
                messagebox.showinfo("エクスポート完了", f"データをエクスポートしました:\n{export_path}")
                
        except Exception as e:
            messagebox.showerror("エラー", f"エクスポートでエラーが発生しました: {e}")
    
    def show_settings(self):
        """設定ダイアログ"""
        messagebox.showinfo("設定", "設定機能は今後実装予定です")
    
    def show_help(self):
        """ヘルプ表示"""
        help_text = """YouTube知識システム - 動画ライブラリ

🎵 動画中心の統合管理システム

主な機能:
1. 📋 動画一覧表示
   - 275件の動画を一覧表示
   - 検索・フィルタリング機能
   - 分析状況の確認

2. 🔍 分析機能
   - GPT-4による動画分析
   - 個別・一括分析対応
   - 創作インサイトの生成

3. 📊 詳細表示
   - 動画の詳細情報表示
   - 分析結果の表示
   - YouTubeリンクへのアクセス

4. 📋 エクスポート
   - 分析結果のエクスポート
   - データの外部利用

操作方法:
- 動画一覧から動画を選択すると詳細が表示されます
- ダブルクリックでYouTubeを開きます
- 検索ボックスでタイトル・チャンネル検索が可能です"""
        
        messagebox.showinfo("使用方法", help_text)
    
    def show_about(self):
        """バージョン情報"""
        about_text = """YouTube知識システム
動画ライブラリ管理GUI

バージョン: 2.0.0
作成者: せつなBot開発チーム

統合データベース中心の動画管理システムで、
275件の動画を効率的に管理・分析します。

搭載機能:
• 高速検索・フィルタリング
• GPT-4分析エンジン
• 創作インサイト生成
• データエクスポート"""
        
        messagebox.showinfo("バージョン情報", about_text)
    
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
        
        # 画面更新（強制的にデータベース再読み込み）
        self.storage._database = None
        self.refresh_data()
    
    def handle_task_error(self, task_name: str, error_message: str, progress_dialog):
        """タスクエラー処理"""
        progress_dialog.close()
        
        # 履歴に追加
        global_task_manager.add_to_history(task_name, f"エラー: {error_message}")
        
        # エラー表示
        messagebox.showerror("エラー", f"{task_name}でエラーが発生しました:\n{error_message}")
    
    def on_analysis_complete(self, result):
        """分析完了処理"""
        analyzed_count = result.get('analyzed_count', 0)
        failed_count = result.get('failed_count', 0)
        total_processed = analyzed_count + failed_count
        
        success_rate = (analyzed_count / total_processed * 100) if total_processed > 0 else 0.0
        
        message = f"""分析完了:

処理: {total_processed}件
成功: {analyzed_count}件
失敗: {failed_count}件
成功率: {success_rate:.1f}%"""
        
        messagebox.showinfo("分析完了", message)
    
    def run_full_batch_analysis(self):
        """未分析動画を全件分析"""
        # 分析対象確認
        videos = self.storage.get_all_videos()
        pending_videos = [vid for vid, video in videos.items() if video.analysis_status.value == 'pending']
        
        if len(pending_videos) == 0:
            messagebox.showinfo("情報", "未分析の動画がありません")
            return
        
        result = messagebox.askyesno(
            "確認",
            f"未分析動画を全件分析しますか？\n対象: {len(pending_videos)}件\n\n※ OpenAI APIを使用します\n※ 処理に時間がかかる場合があります"
        )
        if not result:
            return
        
        def worker(progress_callback):
            analyzed_count = 0
            failed_count = 0
            
            for i, video_id in enumerate(pending_videos):
                if progress_callback:
                    progress_callback(f"動画分析中... ({i+1}/{len(pending_videos)}) - {analyzed_count}件完了")
                
                video = videos[video_id]
                if video.metadata.description:
                    try:
                        result = self.analyzer.analyze_description(video.metadata.description)
                        if result:
                            self.storage.update_video_analysis(video_id, 'completed', creative_insight=result)
                            analyzed_count += 1
                        else:
                            self.storage.update_video_analysis(video_id, 'failed', analysis_error='分析失敗')
                            failed_count += 1
                    except Exception as e:
                        self.storage.update_video_analysis(video_id, 'failed', analysis_error=str(e))
                        failed_count += 1
                else:
                    self.storage.update_video_analysis(video_id, 'failed', analysis_error='概要欄が空')
                    failed_count += 1
                
                # 10件ごとに中間保存
                if (i + 1) % 10 == 0:
                    self.storage.save_database()
            
            # 最終保存
            self.storage.save_database()
            
            return {'analyzed_count': analyzed_count, 'failed_count': failed_count}
        
        self.run_async_task(
            "全件動画分析",
            worker,
            f"未分析動画を全件分析中... (最大{len(pending_videos)}件)",
            self.on_analysis_complete
        )
    
    def run_custom_batch_analysis(self):
        """カスタム件数での分析実行"""
        # 分析対象確認
        videos = self.storage.get_all_videos()
        pending_videos = [vid for vid, video in videos.items() if video.analysis_status.value == 'pending']
        
        if len(pending_videos) == 0:
            messagebox.showinfo("情報", "未分析の動画がありません")
            return
        
        # カスタム件数入力ダイアログ
        dialog = CustomAnalysisDialog(self.root, len(pending_videos))
        if not dialog.result:
            return
        
        max_videos = dialog.selected_count
        target_count = min(len(pending_videos), max_videos)
        
        result = messagebox.askyesno(
            "確認",
            f"動画分析を実行しますか？\n対象: {target_count}件 (未分析: {len(pending_videos)}件中)\n\n※ OpenAI APIを使用します"
        )
        if not result:
            return
        
        def worker(progress_callback):
            analyzed_count = 0
            failed_count = 0
            
            for i, video_id in enumerate(pending_videos[:target_count]):
                if progress_callback:
                    progress_callback(f"動画分析中... ({i+1}/{target_count})")
                
                video = videos[video_id]
                if video.metadata.description:
                    try:
                        result = self.analyzer.analyze_description(video.metadata.description)
                        if result:
                            self.storage.update_video_analysis(video_id, 'completed', creative_insight=result)
                            analyzed_count += 1
                        else:
                            self.storage.update_video_analysis(video_id, 'failed', analysis_error='分析失敗')
                            failed_count += 1
                    except Exception as e:
                        self.storage.update_video_analysis(video_id, 'failed', analysis_error=str(e))
                        failed_count += 1
                else:
                    self.storage.update_video_analysis(video_id, 'failed', analysis_error='概要欄が空')
                    failed_count += 1
            
            return {'analyzed_count': analyzed_count, 'failed_count': failed_count}
        
        self.run_async_task(
            "カスタム動画分析",
            worker,
            f"動画分析を実行中... (最大{target_count}件)",
            self.on_analysis_complete
        )
    
    def add_playlist_dialog(self):
        """プレイリスト追加ダイアログ"""
        dialog = SimplePlaylistAddDialog(self.root, self.collector, self.storage)
        if dialog.result:
            self.refresh_data()
            messagebox.showinfo("成功", f"プレイリストを追加しました\n{dialog.result_message}")
    
    def sync_playlists(self):
        """既存プレイリストの再同期実行"""
        # 統合データベースから既存プレイリストを取得
        db = self.storage.load_database()
        playlists = list(db.playlists.keys())
        
        if not playlists:
            messagebox.showinfo("情報", "同期対象のプレイリストがありません")
            return
        
        result = messagebox.askyesno(
            "確認",
            f"既存の{len(playlists)}個のプレイリストを再同期しますか？\n\n※ YouTube APIを使用します"
        )
        if not result:
            return
        
        def worker(progress_callback):
            try:
                # API初期化
                if not self.collector._initialize_service():
                    return {"success": False, "error": "API初期化に失敗しました"}
                
                total_new_videos = 0
                updated_playlists = 0
                
                for i, playlist_id in enumerate(playlists):
                    if progress_callback:
                        progress_callback(f"プレイリスト同期中... ({i+1}/{len(playlists)})")
                    
                    playlist = db.playlists[playlist_id]
                    display_name = playlist.metadata.title
                    
                    success, message, result = self.collector.process_playlist_by_id(
                        playlist_id, 
                        display_name
                    )
                    
                    if success:
                        total_new_videos += result.get('new_videos', 0)
                        updated_playlists += 1
                
                return {
                    "success": True, 
                    "new_videos": total_new_videos,
                    "updated_playlists": updated_playlists,
                    "total_playlists": len(playlists)
                }
            except Exception as e:
                return {"success": False, "error": str(e)}
        
        self.run_async_task(
            "プレイリスト再同期",
            worker,
            "プレイリストを再同期中...",
            self.on_sync_complete
        )
    
    def on_sync_complete(self, result):
        """同期完了処理"""
        if result.get("success"):
            new_videos = result.get("new_videos", 0)
            updated_playlists = result.get("updated_playlists", 0)
            total_playlists = result.get("total_playlists", 0)
            
            message = f"""プレイリスト再同期が完了しました

処理プレイリスト: {updated_playlists}/{total_playlists}
新規取得動画: {new_videos}件"""
            
            messagebox.showinfo("同期完了", message)
            self.refresh_data()
        else:
            error = result.get("error", "不明なエラー")
            messagebox.showerror("同期失敗", f"プレイリスト同期に失敗しました:\n{error}")
    
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


class SimplePlaylistAddDialog:
    """シンプルなプレイリスト追加ダイアログ（統合データベース直接更新）"""
    
    def __init__(self, parent, collector, storage):
        self.parent = parent
        self.collector = collector
        self.storage = storage
        self.result = False
        self.result_message = ""
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("プレイリスト追加")
        self.dialog.geometry("500x300")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_widgets()
        self.center_on_parent()
    
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
    
    def create_widgets(self):
        """ウィジェットを作成"""
        # メインフレーム
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # タイトル
        title_label = ttk.Label(
            main_frame,
            text="🎵 プレイリスト追加",
            font=('Segoe UI', 14, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # 説明
        desc_label = ttk.Label(
            main_frame,
            text="YouTubeプレイリストのURLまたはIDを入力してください。\n動画データは統合データベースに直接追加されます。",
            foreground="gray"
        )
        desc_label.pack(pady=(0, 20))
        
        # URL入力
        url_frame = ttk.LabelFrame(main_frame, text="プレイリスト情報", padding="15")
        url_frame.pack(fill='x', pady=(0, 20))
        
        ttk.Label(url_frame, text="YouTubeプレイリストURL または ID:").pack(anchor='w')
        self.url_var = tk.StringVar()
        url_entry = ttk.Entry(url_frame, textvariable=self.url_var, font=('Consolas', 10))
        url_entry.pack(fill='x', pady=(10, 10))
        
        # 表示名（オプション）
        ttk.Label(url_frame, text="表示名（オプション）:").pack(anchor='w')
        self.display_name_var = tk.StringVar()
        ttk.Entry(url_frame, textvariable=self.display_name_var).pack(fill='x', pady=(5, 0))
        
        # ボタンフレーム
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(20, 0))
        
        def safe_close():
            try:
                self.dialog.destroy()
            except:
                pass
        
        ttk.Button(button_frame, text="キャンセル", command=safe_close).pack(side='right', padx=(5, 0))
        ttk.Button(
            button_frame, 
            text="追加して動画を取得", 
            command=self.add_playlist,
            style='Accent.TButton'
        ).pack(side='right')
        
        # URL入力フィールドにフォーカス
        url_entry.focus_set()
    
    def add_playlist(self):
        """プレイリスト追加実行"""
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning("警告", "URLまたはIDを入力してください")
            return
        
        try:
            # プレイリストID抽出
            playlist_id = self._extract_playlist_id(url)
            if not playlist_id:
                messagebox.showerror("エラー", "有効なプレイリストURLまたはIDを入力してください")
                return
            
            display_name = self.display_name_var.get().strip()
            
            # API初期化
            if not self.collector._initialize_service():
                messagebox.showerror("エラー", "YouTube API認証に失敗しました")
                return
            
            # プレイリスト収集実行
            success, message, result = self.collector.process_playlist_by_id(
                playlist_id, 
                display_name
            )
            
            if success:
                video_count = result.get('new_videos', 0)
                total_videos = result.get('videos_found', 0)
                self.result_message = f"取得動画数: {total_videos}件（新規: {video_count}件）"
                self.result = True
                self.dialog.destroy()
            else:
                messagebox.showerror("エラー", f"プレイリスト追加に失敗しました:\n{message}")
            
        except Exception as e:
            messagebox.showerror("エラー", f"プレイリスト追加でエラーが発生しました:\n{e}")
    
    def _extract_playlist_id(self, url_or_id: str) -> str:
        """URLまたはIDからプレイリストIDを抽出"""
        if not url_or_id:
            return ""
        
        # 既にIDの場合（PL で始まる）
        if url_or_id.startswith('PL'):
            return url_or_id
        
        # URL の場合
        import re
        patterns = [
            r'list=([a-zA-Z0-9_-]+)',
            r'playlist\?list=([a-zA-Z0-9_-]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url_or_id)
            if match:
                return match.group(1)
        
        return ""


class CustomAnalysisDialog:
    """カスタム分析件数入力ダイアログ"""
    
    def __init__(self, parent, max_pending):
        self.parent = parent
        self.max_pending = max_pending
        self.result = False
        self.selected_count = 10
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("カスタム分析設定")
        self.dialog.geometry("400x250")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_widgets()
        self.center_on_parent()
    
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
    
    def create_widgets(self):
        """ウィジェットを作成"""
        # メインフレーム
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # タイトル
        title_label = ttk.Label(
            main_frame,
            text="🔍 カスタム分析設定",
            font=('Segoe UI', 14, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # 説明
        desc_label = ttk.Label(
            main_frame,
            text=f"分析する動画の件数を指定してください。\n未分析動画: {self.max_pending}件",
            foreground="gray"
        )
        desc_label.pack(pady=(0, 20))
        
        # 件数入力
        count_frame = ttk.LabelFrame(main_frame, text="分析件数", padding="15")
        count_frame.pack(fill='x', pady=(0, 20))
        
        # スライダーと数値入力
        slider_frame = ttk.Frame(count_frame)
        slider_frame.pack(fill='x')
        
        self.count_var = tk.IntVar(value=min(50, self.max_pending))
        
        # スライダー
        self.scale = tk.Scale(
            slider_frame,
            from_=1,
            to=min(self.max_pending, 500),
            orient='horizontal',
            variable=self.count_var,
            command=self.on_scale_change
        )
        self.scale.pack(fill='x', pady=(0, 10))
        
        # 数値入力
        entry_frame = ttk.Frame(slider_frame)
        entry_frame.pack(fill='x')
        
        ttk.Label(entry_frame, text="件数:").pack(side='left')
        self.count_entry = ttk.Entry(entry_frame, textvariable=self.count_var, width=10)
        self.count_entry.pack(side='left', padx=(5, 10))
        self.count_entry.bind('<KeyRelease>', self.on_entry_change)
        
        ttk.Label(entry_frame, text=f"(最大: {self.max_pending}件)").pack(side='left')
        
        # プリセットボタン
        preset_frame = ttk.Frame(count_frame)
        preset_frame.pack(fill='x', pady=(10, 0))
        
        presets = [10, 25, 50, 100]
        for preset in presets:
            if preset <= self.max_pending:
                ttk.Button(
                    preset_frame,
                    text=f"{preset}件",
                    command=lambda p=preset: self.set_preset(p),
                    width=8
                ).pack(side='left', padx=(0, 5))
        
        if self.max_pending > 100:
            ttk.Button(
                preset_frame,
                text="全件",
                command=lambda: self.set_preset(self.max_pending),
                width=8
            ).pack(side='left', padx=(0, 5))
        
        # ボタンフレーム
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill='x', pady=(20, 0))
        
        def safe_close():
            try:
                self.dialog.destroy()
            except:
                pass
        
        ttk.Button(button_frame, text="キャンセル", command=safe_close).pack(side='right', padx=(5, 0))
        ttk.Button(
            button_frame, 
            text="分析開始", 
            command=self.start_analysis,
            style='Accent.TButton'
        ).pack(side='right')
    
    def on_scale_change(self, value):
        """スライダー変更時"""
        pass
    
    def on_entry_change(self, event):
        """数値入力変更時"""
        try:
            value = int(self.count_var.get())
            if value > self.max_pending:
                self.count_var.set(self.max_pending)
            elif value < 1:
                self.count_var.set(1)
        except:
            pass
    
    def set_preset(self, count):
        """プリセット値設定"""
        self.count_var.set(count)
    
    def start_analysis(self):
        """分析開始"""
        try:
            count = int(self.count_var.get())
            if 1 <= count <= self.max_pending:
                self.selected_count = count
                self.result = True
                self.dialog.destroy()
            else:
                messagebox.showwarning("警告", f"1〜{self.max_pending}の範囲で入力してください")
        except ValueError:
            messagebox.showwarning("警告", "有効な数値を入力してください")


def main():
    """メイン関数"""
    try:
        app = VideoMainWindow()
        app.run()
    except Exception as e:
        messagebox.showerror("起動エラー", f"アプリケーションの起動に失敗しました:\n{e}")


if __name__ == "__main__":
    main()
# -*- coding: utf-8 -*-
"""
動画一覧表示ウィジェット

統合データベース中心の動画ライブラリ表示
"""

import tkinter as tk
from tkinter import ttk
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# パス設定
sys.path.append(str(Path(__file__).parent.parent.parent))

from storage.unified_storage import UnifiedStorage
from core.data_models import Video, AnalysisStatus
from config.settings import DATA_DIR


class VideoListWidget(ttk.Frame):
    """動画一覧表示ウィジェット"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # データストレージ
        self.storage = UnifiedStorage(DATA_DIR)
        self.videos: Dict[str, Video] = {}
        self.filtered_videos: List[str] = []  # フィルタリング済み動画IDリスト
        
        # イベント
        self.selection_callback = None
        self.delete_callback = None  # 削除コールバック
        
        # ウィジェット作成
        self.create_widgets()
        self.load_videos()
    
    def create_widgets(self):
        """ウィジェットを作成"""
        # 検索・フィルタフレーム
        search_frame = ttk.Frame(self)
        search_frame.pack(fill='x', padx=5, pady=5)
        
        # 検索ボックス
        ttk.Label(search_frame, text="🔍 検索:").pack(side='left', padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.on_search_changed)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side='left', padx=(0, 10))
        
        # 分析状況フィルタ
        ttk.Label(search_frame, text="分析状況:").pack(side='left', padx=(0, 5))
        self.status_filter_var = tk.StringVar(value="全て")
        status_combo = ttk.Combobox(
            search_frame,
            textvariable=self.status_filter_var,
            values=["全て", "未分析", "分析済み", "失敗"],
            state='readonly',
            width=10
        )
        status_combo.pack(side='left', padx=(0, 10))
        status_combo.bind('<<ComboboxSelected>>', self.on_filter_changed)
        
        
        # 動画一覧テーブル
        self.create_video_table()
    
    def create_video_table(self):
        """動画一覧テーブルを作成"""
        # テーブルフレーム
        table_frame = ttk.Frame(self)
        table_frame.pack(fill='both', expand=True, padx=5, pady=(0, 5))
        
        # Treeview作成
        columns = ('status', 'title', 'channel', 'analysis', 'published', 'duration', 'playlists')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=15)
        
        # 列設定
        column_config = {
            'status': {'text': '状態', 'width': 60, 'anchor': 'center'},
            'title': {'text': 'タイトル', 'width': 300, 'anchor': 'w'},
            'channel': {'text': 'チャンネル', 'width': 150, 'anchor': 'w'},
            'analysis': {'text': '分析状況', 'width': 80, 'anchor': 'center'},
            'published': {'text': 'YouTubeで開く', 'width': 120, 'anchor': 'center'},
            'duration': {'text': '時間', 'width': 60, 'anchor': 'center'},
            'playlists': {'text': 'プレイリスト', 'width': 100, 'anchor': 'center'}
        }
        
        for col, config in column_config.items():
            self.tree.heading(col, text=config['text'], command=lambda c=col: self.sort_by_column(c))
            self.tree.column(col, width=config['width'], anchor=config['anchor'], minwidth=50)
        
        # スクロールバー
        scrollbar_y = ttk.Scrollbar(table_frame, orient='vertical', command=self.tree.yview)
        scrollbar_x = ttk.Scrollbar(table_frame, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        # 配置
        self.tree.grid(row=0, column=0, sticky='nsew')
        scrollbar_y.grid(row=0, column=1, sticky='ns')
        scrollbar_x.grid(row=1, column=0, sticky='ew')
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # イベントバインド
        self.tree.bind('<<TreeviewSelect>>', self.on_selection_changed)
        self.tree.bind('<Double-1>', self.on_double_click)
        self.tree.bind('<Button-1>', self.on_single_click)
        self.tree.bind('<Button-3>', self.on_right_click)  # 右クリック
    
    def load_videos(self):
        """動画データを読み込み"""
        try:
            print("動画データ読み込み開始...")
            self.videos = self.storage.get_all_videos()
            print(f"ストレージから取得: {len(self.videos)}件")
            
            self.filtered_videos = list(self.videos.keys())
            print(f"フィルタリング後: {len(self.filtered_videos)}件")
            
            self.update_table()
            print(f"動画データを読み込みました: {len(self.videos)}件")
        except Exception as e:
            print(f"動画データ読み込みエラー: {e}")
            import traceback
            traceback.print_exc()
            self.videos = {}
            self.filtered_videos = []
    
    def update_table(self):
        """テーブル表示を更新"""
        print(f"テーブル更新開始: {len(self.filtered_videos)}件を処理")
        
        # 既存アイテムを削除
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # フィルタリング済み動画を表示
        inserted_count = 0
        for video_id in self.filtered_videos:
            if video_id in self.videos:
                video = self.videos[video_id]
                self.insert_video_item(video_id, video)
                inserted_count += 1
        
        print(f"テーブル更新完了: {inserted_count}件を挿入")
    
    def insert_video_item(self, video_id: str, video: Video):
        """動画アイテムをテーブルに挿入"""
        try:
            # 状態アイコン
            status_icon = self.get_status_icon(video.analysis_status)
            
            # タイトル（長い場合は省略）
            title = video.metadata.title
            if len(title) > 50:
                title = title[:47] + "..."
            
            # チャンネル名（長い場合は省略）
            channel = video.metadata.channel_title
            if len(channel) > 20:
                channel = channel[:17] + "..."
            
            # 分析状況
            analysis_status = self.get_analysis_status_text(video.analysis_status, video)
            
            # YouTubeリンク
            published_date = "🔗 YouTube"
            
            # 動画時間
            duration = self.format_duration(video.metadata.duration)
            
            # 所属プレイリスト数
            playlist_count = len(video.playlists)
            
            # アイテム挿入
            item = self.tree.insert('', 'end', values=(
                status_icon,
                title,
                channel,
                analysis_status,
                published_date,
                duration,
                f"{playlist_count}件"
            ), tags=(video_id,))
            
            # 状態に応じた色設定
            if video.analysis_status.value == 'completed':
                self.tree.set(item, 'status', '🟢')
            elif video.analysis_status.value == 'failed':
                self.tree.set(item, 'status', '🔴')
            else:
                self.tree.set(item, 'status', '🟡')
                
        except Exception as e:
            print(f"動画アイテム挿入エラー ({video_id}): {e}")
            import traceback
            traceback.print_exc()
    
    def get_status_icon(self, status: AnalysisStatus) -> str:
        """分析状況のアイコンを取得"""
        if status.value == 'completed':
            return '🟢'
        elif status.value == 'failed':
            return '🔴'
        else:
            return '🟡'
    
    def get_analysis_status_text(self, status: AnalysisStatus, video: Video = None) -> str:
        """分析状況のテキストを取得"""
        status_map = {
            'completed': '完了',
            'pending': '未分析',
            'failed': '失敗'
        }
        base_text = status_map.get(status.value, '不明')
        
        # 失敗状況で再試行回数がある場合
        if status.value == 'failed' and video and hasattr(video, 'retry_count') and video.retry_count > 0:
            base_text += f"({video.retry_count}回)"
        
        return base_text
    
    def format_duration(self, duration_str: str) -> str:
        """動画時間をフォーマット"""
        try:
            # ISO 8601 duration format (PT3M11S) を MM:SS に変換
            if duration_str.startswith('PT'):
                import re
                match = re.search(r'PT(?:(\d+)M)?(?:(\d+)S)?', duration_str)
                if match:
                    minutes = int(match.group(1) or 0)
                    seconds = int(match.group(2) or 0)
                    return f"{minutes}:{seconds:02d}"
            return duration_str
        except:
            return "N/A"
    
    def on_search_changed(self, *args):
        """検索テキスト変更時の処理"""
        self.apply_filters()
    
    def on_filter_changed(self, event=None):
        """フィルタ変更時の処理"""
        self.apply_filters()
    
    def apply_filters(self):
        """フィルタを適用"""
        search_text = self.search_var.get().lower()
        status_filter = self.status_filter_var.get()
        
        self.filtered_videos = []
        
        for video_id, video in self.videos.items():
            # テキスト検索
            if search_text:
                searchable_text = (
                    video.metadata.title.lower() + " " +
                    video.metadata.channel_title.lower() + " " +
                    video.metadata.description.lower()
                )
                if search_text not in searchable_text:
                    continue
            
            # 分析状況フィルタ
            if status_filter != "全て":
                status_map = {
                    "未分析": "pending",
                    "分析済み": "completed",
                    "失敗": "failed"
                }
                if video.analysis_status.value != status_map.get(status_filter):
                    continue
            
            self.filtered_videos.append(video_id)
        
        self.update_table()
    
    def sort_by_column(self, column: str):
        """列でソート"""
        # TODO: ソート機能の実装
        print(f"ソート: {column}")
    
    def on_selection_changed(self, event):
        """選択変更時の処理"""
        selection = self.tree.selection()
        if selection and self.selection_callback:
            item = selection[0]
            tags = self.tree.item(item, 'tags')
            if tags:
                video_id = tags[0]
                if video_id in self.videos:
                    self.selection_callback(video_id, self.videos[video_id])
    
    def on_single_click(self, event):
        """シングルクリック時の処理（YouTubeリンク列のクリック）"""
        # クリック位置の確認
        region = self.tree.identify_region(event.x, event.y)
        if region == "cell":
            # どの列がクリックされたかを確認
            column = self.tree.identify_column(event.x)
            if column == '#5':  # published列（5番目）
                item = self.tree.identify_row(event.y)
                if item:
                    tags = self.tree.item(item, 'tags')
                    if tags:
                        video_id = tags[0]
                        # YouTube URLを開く
                        import webbrowser
                        youtube_url = f"https://www.youtube.com/watch?v={video_id}"
                        webbrowser.open(youtube_url)
                        return 'break'  # イベントの伝播を停止
    
    def on_double_click(self, event):
        """ダブルクリック時の処理"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            tags = self.tree.item(item, 'tags')
            if tags:
                video_id = tags[0]
                # YouTube URLを開く
                import webbrowser
                youtube_url = f"https://www.youtube.com/watch?v={video_id}"
                webbrowser.open(youtube_url)
    
    def on_right_click(self, event):
        """右クリック時のコンテキストメニュー表示"""
        # クリックされた行を特定
        item = self.tree.identify_row(event.y)
        if not item:
            return
        
        # 該当行を選択
        self.tree.selection_set(item)
        
        # 動画情報取得
        tags = self.tree.item(item, 'tags')
        if not tags:
            return
        
        video_id = tags[0]
        if video_id not in self.videos:
            return
        
        video = self.videos[video_id]
        
        # コンテキストメニューを作成
        context_menu = tk.Menu(self.tree, tearoff=0)
        context_menu.add_command(
            label="🔗 YouTubeで開く",
            command=lambda: self._open_youtube(video_id)
        )
        context_menu.add_separator()
        context_menu.add_command(
            label="🗑️ 動画を削除",
            command=lambda: self._delete_video(video_id, video)
        )
        
        # メニューを表示
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def _open_youtube(self, video_id: str):
        """YouTube動画を開く"""
        import webbrowser
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"
        webbrowser.open(youtube_url)
    
    def _delete_video(self, video_id: str, video: Video):
        """動画削除処理"""
        if self.delete_callback:
            self.delete_callback(video_id, video)
        else:
            # デフォルトの処理（コンソール出力）
            print(f"削除コールバックが設定されていません: {video.metadata.title}")
    
    def get_selected_video(self) -> Optional[tuple]:
        """選択された動画を取得"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            tags = self.tree.item(item, 'tags')
            if tags:
                video_id = tags[0]
                if video_id in self.videos:
                    return video_id, self.videos[video_id]
        return None
    
    def refresh(self):
        """データを再読み込み"""
        print("📋 video_list.refresh() 実行開始")
        # ストレージの完全初期化
        self.storage._database = None
        if hasattr(self.storage, '_cache_valid'):
            self.storage._cache_valid = False
        
        # 既存の動画データをクリア
        self.videos.clear()
        self.filtered_videos.clear()
        
        # データ再読み込み
        self.load_videos()
        print("📋 video_list.refresh() 実行完了")
    
    def set_selection_callback(self, callback):
        """選択変更時のコールバックを設定"""
        self.selection_callback = callback
    
    def set_delete_callback(self, callback):
        """動画削除時のコールバックを設定"""
        self.delete_callback = callback


def main():
    """テスト用メイン関数"""
    root = tk.Tk()
    root.title("動画一覧テスト")
    root.geometry("1000x600")
    
    video_list = VideoListWidget(root)
    video_list.pack(fill='both', expand=True)
    
    def on_video_selected(video_id, video):
        print(f"選択された動画: {video.metadata.title}")
    
    video_list.set_selection_callback(on_video_selected)
    
    root.mainloop()


if __name__ == "__main__":
    main()
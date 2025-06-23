# -*- coding: utf-8 -*-
"""
動画詳細表示パネル

選択された動画の詳細情報と分析結果を表示
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
from pathlib import Path
from typing import Optional
import webbrowser

# パス設定
sys.path.append(str(Path(__file__).parent.parent.parent))

from core.data_models import Video, AnalysisStatus
from storage.unified_storage import UnifiedStorage
from analyzers.description_analyzer import DescriptionAnalyzer
from config.settings import DATA_DIR


class VideoDetailPanel(ttk.Frame):
    """動画詳細表示パネル"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        
        # データ
        self.current_video: Optional[Video] = None
        self.current_video_id: Optional[str] = None
        
        # サービス
        self.storage = UnifiedStorage(DATA_DIR)
        self.analyzer = DescriptionAnalyzer()
        
        # ウィジェット作成
        self.create_widgets()
        self.show_empty_state()
    
    def create_widgets(self):
        """ウィジェットを作成"""
        # スクロール可能フレーム
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # パック
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # マウスホイールスクロール
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind("<MouseWheel>", _on_mousewheel)
        
        # メインコンテンツフレーム
        self.content_frame = ttk.Frame(self.scrollable_frame, padding="10")
        self.content_frame.pack(fill='both', expand=True)
    
    def show_empty_state(self):
        """空状態を表示"""
        self.clear_content()
        
        empty_label = ttk.Label(
            self.content_frame,
            text="📺 動画を選択してください",
            font=('Segoe UI', 12),
            foreground='gray'
        )
        empty_label.pack(expand=True)
    
    def clear_content(self):
        """コンテンツをクリア"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def display_video(self, video_id: str, video: Video):
        """動画詳細を表示"""
        self.current_video_id = video_id
        self.current_video = video
        
        self.clear_content()
        
        # 基本情報セクション
        self.create_basic_info_section(video_id, video)
        
        # 分析状況セクション
        self.create_analysis_section(video)
        
        # 概要欄セクション
        self.create_description_section(video)
        
        # プレイリスト情報セクション
        self.create_playlist_section(video)
    
    def create_basic_info_section(self, video_id: str, video: Video):
        """基本情報セクションを作成"""
        # タイトル
        title_frame = ttk.Frame(self.content_frame)
        title_frame.pack(fill='x', pady=(0, 10))
        
        title_label = ttk.Label(
            title_frame,
            text=f"🎵 {video.metadata.title}",
            font=('Segoe UI', 14, 'bold'),
            wraplength=400
        )
        title_label.pack(anchor='w')
        
        # 基本情報グリッド
        info_frame = ttk.LabelFrame(self.content_frame, text="📋 基本情報", padding="10")
        info_frame.pack(fill='x', pady=(0, 10))
        
        # 情報項目
        info_items = [
            ("📺 チャンネル", video.metadata.channel_title),
            ("📅 公開日", video.metadata.published_at.strftime('%Y年%m月%d日')),
            ("⏱️ 時間", self.format_duration(video.metadata.duration)),
            ("👀 再生数", f"{video.metadata.view_count:,}回" if video.metadata.view_count else "N/A"),
            ("👍 高評価", f"{video.metadata.like_count:,}" if video.metadata.like_count else "N/A"),
            ("💬 コメント", f"{video.metadata.comment_count:,}件" if video.metadata.comment_count else "N/A"),
        ]
        
        for i, (label, value) in enumerate(info_items):
            row = i // 2
            col = (i % 2) * 2
            
            ttk.Label(info_frame, text=label, font=('Segoe UI', 9, 'bold')).grid(
                row=row, column=col, sticky='w', padx=(0, 5), pady=2
            )
            ttk.Label(info_frame, text=value).grid(
                row=row, column=col+1, sticky='w', padx=(0, 20), pady=2
            )
        
        # アクションボタン
        action_frame = ttk.Frame(self.content_frame)
        action_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Button(
            action_frame,
            text="🔗 YouTubeで開く",
            command=lambda: self.open_youtube_url(video_id),
            width=15
        ).pack(side='left', padx=(0, 5))
        
        ttk.Button(
            action_frame,
            text="🔍 分析実行",
            command=self.analyze_video,
            width=15
        ).pack(side='left')
    
    def create_analysis_section(self, video: Video):
        """分析状況セクションを作成"""
        analysis_frame = ttk.LabelFrame(self.content_frame, text="🔍 分析状況", padding="10")
        analysis_frame.pack(fill='x', pady=(0, 10))
        
        # 分析状況表示
        status_frame = ttk.Frame(analysis_frame)
        status_frame.pack(fill='x', pady=(0, 10))
        
        # 状態アイコンとテキスト
        status_icon = self.get_status_icon(video.analysis_status)
        status_text = self.get_status_text(video.analysis_status)
        
        status_label = ttk.Label(
            status_frame,
            text=f"{status_icon} 分析状況: {status_text}",
            font=('Segoe UI', 11, 'bold')
        )
        status_label.pack(anchor='w')
        
        # 分析結果表示（分析済みの場合）
        if video.analysis_status.value == 'completed' and video.creative_insight:
            self.create_analysis_results(analysis_frame, video.creative_insight)
        elif video.analysis_status.value == 'failed' and video.analysis_error:
            error_label = ttk.Label(
                analysis_frame,
                text=f"❌ エラー: {video.analysis_error}",
                foreground='red'
            )
            error_label.pack(anchor='w', pady=(5, 0))
    
    def create_analysis_results(self, parent, creative_insight):
        """分析結果を表示"""
        results_frame = ttk.Frame(parent)
        results_frame.pack(fill='x', pady=(10, 0))
        
        # 分析結果タイトル
        ttk.Label(
            results_frame,
            text="🎨 創作インサイト:",
            font=('Segoe UI', 10, 'bold')
        ).pack(anchor='w', pady=(0, 5))
        
        # 分析結果テキスト
        insight_text = creative_insight.insights if hasattr(creative_insight, 'insights') else str(creative_insight)
        
        # Text ウィジェットで表示（スクロール可能）
        text_frame = ttk.Frame(results_frame)
        text_frame.pack(fill='x')
        
        text_widget = tk.Text(
            text_frame,
            height=6,
            wrap='word',
            font=('Segoe UI', 9),
            relief='sunken',
            borderwidth=1
        )
        text_scrollbar = ttk.Scrollbar(text_frame, command=text_widget.yview)
        text_widget.configure(yscrollcommand=text_scrollbar.set)
        
        text_widget.pack(side='left', fill='both', expand=True)
        text_scrollbar.pack(side='right', fill='y')
        
        text_widget.insert('1.0', insight_text)
        text_widget.configure(state='disabled')
    
    def create_description_section(self, video: Video):
        """概要欄セクションを作成"""
        if not video.metadata.description:
            return
        
        desc_frame = ttk.LabelFrame(self.content_frame, text="📝 概要欄", padding="10")
        desc_frame.pack(fill='x', pady=(0, 10))
        
        # 概要欄テキスト
        text_frame = ttk.Frame(desc_frame)
        text_frame.pack(fill='x')
        
        text_widget = tk.Text(
            text_frame,
            height=8,
            wrap='word',
            font=('Segoe UI', 9),
            relief='sunken',
            borderwidth=1
        )
        text_scrollbar = ttk.Scrollbar(text_frame, command=text_widget.yview)
        text_widget.configure(yscrollcommand=text_scrollbar.set)
        
        text_widget.pack(side='left', fill='both', expand=True)
        text_scrollbar.pack(side='right', fill='y')
        
        # 概要欄を省略表示（長い場合）
        description = video.metadata.description
        if len(description) > 1000:
            description = description[:1000] + "\n\n... (省略)"
        
        text_widget.insert('1.0', description)
        text_widget.configure(state='disabled')
    
    def create_playlist_section(self, video: Video):
        """プレイリスト情報セクションを作成"""
        if not video.playlists:
            return
        
        playlist_frame = ttk.LabelFrame(self.content_frame, text="📋 所属プレイリスト", padding="10")
        playlist_frame.pack(fill='x', pady=(0, 10))
        
        # プレイリスト一覧
        try:
            db = self.storage.load_database()
            for i, playlist_id in enumerate(video.playlists):
                if playlist_id in db.playlists:
                    playlist = db.playlists[playlist_id]
                    position = video.playlist_positions.get(playlist_id, 0)
                    total_videos = len(playlist.video_ids)
                    
                    playlist_text = f"• {playlist.metadata.title} (位置: {position+1}/{total_videos})"
                    
                    ttk.Label(
                        playlist_frame,
                        text=playlist_text,
                        font=('Segoe UI', 9)
                    ).pack(anchor='w', pady=1)
        except Exception as e:
            ttk.Label(
                playlist_frame,
                text=f"プレイリスト情報の取得に失敗: {e}",
                foreground='red'
            ).pack(anchor='w')
    
    def get_status_icon(self, status: AnalysisStatus) -> str:
        """分析状況のアイコンを取得"""
        if status.value == 'completed':
            return '🟢'
        elif status.value == 'failed':
            return '🔴'
        else:
            return '🟡'
    
    def get_status_text(self, status: AnalysisStatus) -> str:
        """分析状況のテキストを取得"""
        status_map = {
            'completed': '分析完了',
            'pending': '未分析',
            'failed': '分析失敗'
        }
        return status_map.get(status.value, '不明')
    
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
    
    def open_youtube_url(self, video_id: str):
        """YouTube URLを開く"""
        youtube_url = f"https://www.youtube.com/watch?v={video_id}"
        webbrowser.open(youtube_url)
    
    def analyze_video(self):
        """動画分析を実行"""
        if not self.current_video or not self.current_video_id:
            return
        
        try:
            # 分析確認
            result = messagebox.askyesno(
                "分析実行確認",
                f"この動画を分析しますか？\n\n"
                f"タイトル: {self.current_video.metadata.title[:50]}...\n"
                f"\n※ OpenAI APIを使用します"
            )
            
            if not result:
                return
            
            # 分析実行
            description = self.current_video.metadata.description
            if not description:
                messagebox.showwarning("分析不可", "概要欄が空のため分析できません")
                return
            
            # 分析開始
            self.set_analysis_status("🔄 分析中...")
            
            analysis_result = self.analyzer.analyze_description(description)
            
            if analysis_result:
                # 分析成功
                success = self.storage.update_video_analysis(
                    self.current_video_id,
                    analysis_status='completed',
                    creative_insight=analysis_result
                )
                
                if success:
                    # 表示を更新
                    updated_video = self.storage.get_video(self.current_video_id)
                    if updated_video:
                        self.display_video(self.current_video_id, updated_video)
                    
                    messagebox.showinfo("分析完了", "動画の分析が完了しました")
                else:
                    self.set_analysis_status("❌ 保存失敗")
                    messagebox.showerror("エラー", "分析結果の保存に失敗しました")
            else:
                # 分析失敗
                self.storage.update_video_analysis(
                    self.current_video_id,
                    analysis_status='failed',
                    analysis_error='分析処理失敗'
                )
                
                self.set_analysis_status("❌ 分析失敗")
                messagebox.showerror("分析失敗", "動画の分析に失敗しました")
                
        except Exception as e:
            self.set_analysis_status("❌ エラー")
            messagebox.showerror("エラー", f"分析処理でエラーが発生しました:\n{e}")
    
    def set_analysis_status(self, status_text: str):
        """分析状況を一時的に表示"""
        # TODO: 分析状況の一時表示機能
        print(f"分析状況: {status_text}")


def main():
    """テスト用メイン関数"""
    root = tk.Tk()
    root.title("動画詳細テスト")
    root.geometry("500x700")
    
    detail_panel = VideoDetailPanel(root)
    detail_panel.pack(fill='both', expand=True)
    
    # テスト用：動画データを読み込んで表示
    try:
        storage = UnifiedStorage(DATA_DIR)
        videos = storage.get_all_videos()
        if videos:
            video_id, video = next(iter(videos.items()))
            detail_panel.display_video(video_id, video)
    except Exception as e:
        print(f"テストデータ読み込みエラー: {e}")
    
    root.mainloop()


if __name__ == "__main__":
    main()
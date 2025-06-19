"""
状態表示パネル

システムの現在状況を表示するウィジェット
"""

import tkinter as tk
from tkinter import ttk
import sys
from pathlib import Path

# パス設定
sys.path.append(str(Path(__file__).parent.parent.parent))

from managers.playlist_manager import PlaylistManager


class StatusPanel(ttk.Frame):
    """状態表示パネル"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.playlist_manager = PlaylistManager()
        
        # ウィジェット作成
        self.create_widgets()
        
        # 初期データ読み込み
        self.update_status()
    
    def create_widgets(self):
        """ウィジェットを作成"""
        # メインタイトル
        title_frame = ttk.Frame(self)
        title_frame.pack(fill='x', padx=5, pady=5)
        
        title_label = ttk.Label(
            title_frame, 
            text="🎵 YouTube知識システム", 
            font=('Segoe UI', 12, 'bold')
        )
        title_label.pack(side='left')
        
        self.refresh_button = ttk.Button(
            title_frame,
            text="🔄 更新",
            command=self.update_status,
            width=8
        )
        self.refresh_button.pack(side='right')
        
        # 統計情報フレーム
        stats_frame = ttk.LabelFrame(self, text="システム状況")
        stats_frame.pack(fill='x', padx=5, pady=5)
        
        # 統計ラベル
        self.stats_label = ttk.Label(
            stats_frame, 
            text="読み込み中...",
            font=('Segoe UI', 10)
        )
        self.stats_label.pack(pady=5)
        
        # 分析進捗フレーム
        progress_frame = ttk.Frame(stats_frame)
        progress_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(progress_frame, text="分析進捗:").pack(side='left')
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            length=200
        )
        self.progress_bar.pack(side='left', padx=(5, 10))
        
        self.progress_label = ttk.Label(progress_frame, text="0/0 (0%)")
        self.progress_label.pack(side='left')
        
        # 詳細情報フレーム
        details_frame = ttk.LabelFrame(self, text="詳細情報")
        details_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 詳細テキスト
        self.details_text = tk.Text(
            details_frame,
            height=6,
            wrap='word',
            font=('Segoe UI', 9),
            state='disabled'
        )
        self.details_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # スクロールバー
        scrollbar = ttk.Scrollbar(details_frame, orient='vertical', command=self.details_text.yview)
        scrollbar.pack(side='right', fill='y')
        self.details_text.config(yscrollcommand=scrollbar.set)
    
    def update_status(self):
        """状況を更新"""
        try:
            # プレイリスト状況取得
            status = self.playlist_manager.get_playlist_status()
            
            if 'error' in status:
                self.stats_label.config(text=f"❌ エラー: {status['error']}")
                return
            
            # 統計情報更新
            db_stats = status['database_stats']
            config_stats = status['config_stats']
            
            stats_text = (
                f"📊 プレイリスト: {config_stats['total_playlists']}件 | "
                f"動画: {db_stats['total_videos']}件 | "
                f"分析済み: {db_stats['total_analyzed']}件"
            )
            self.stats_label.config(text=stats_text)
            
            # 進捗バー更新
            if db_stats['total_videos'] > 0:
                analysis_percentage = (db_stats['total_analyzed'] / db_stats['total_videos']) * 100
                self.progress_var.set(analysis_percentage)
                self.progress_label.config(
                    text=f"{db_stats['total_analyzed']}/{db_stats['total_videos']} ({analysis_percentage:.1f}%)"
                )
            else:
                self.progress_var.set(0)
                self.progress_label.config(text="0/0 (0%)")
            
            # 詳細情報更新
            self.update_details(status)
            
        except Exception as e:
            self.stats_label.config(text=f"❌ 状況取得エラー: {e}")
    
    def update_details(self, status):
        """詳細情報を更新"""
        details = []
        
        # プレイリスト別情報
        playlist_details = status.get('playlist_details', [])
        
        if playlist_details:
            details.append("📋 プレイリスト詳細:")
            for detail in playlist_details:
                enabled_icon = "✅" if detail['enabled'] else "❌"
                db_icon = "📁" if detail['in_database'] else "🆕"
                
                line = (
                    f"{enabled_icon}{db_icon} {detail['display_name']} "
                    f"({detail['category']}) - "
                    f"{detail['total_videos']}動画, "
                    f"{detail['analyzed_videos']}分析済み "
                    f"({detail['analysis_rate']:.1%})"
                )
                details.append(line)
                
                if detail['last_sync']:
                    details.append(f"    最終同期: {detail['last_sync']}")
                else:
                    details.append(f"    最終同期: 未実行")
                details.append("")  # 空行
        else:
            details.append("プレイリストが登録されていません")
        
        # カテゴリ別統計
        config_stats = status.get('config_stats', {})
        category_stats = config_stats.get('category_stats', {})
        
        if category_stats:
            details.append("📊 カテゴリ別統計:")
            for category, count in category_stats.items():
                details.append(f"  {category}: {count}件")
            details.append("")
        
        # 更新頻度別統計
        frequency_stats = config_stats.get('frequency_stats', {})
        if frequency_stats:
            details.append("⏰ 更新頻度別統計:")
            for frequency, count in frequency_stats.items():
                details.append(f"  {frequency}: {count}件")
        
        # テキスト更新
        self.details_text.config(state='normal')
        self.details_text.delete('1.0', 'end')
        self.details_text.insert('1.0', '\n'.join(details))
        self.details_text.config(state='disabled')
    
    def set_status_message(self, message: str):
        """ステータスメッセージを設定"""
        # 統計ラベルの下にメッセージを表示
        self.stats_label.config(text=message)
    
    def show_progress(self, progress: float, message: str = ""):
        """進捗を表示"""
        self.progress_var.set(progress)
        if message:
            self.progress_label.config(text=message)


# テスト用関数
def test_status_panel():
    """状態表示パネルのテスト"""
    root = tk.Tk()
    root.title("状態表示パネル テスト")
    root.geometry("600x400")
    
    panel = StatusPanel(root)
    panel.pack(fill='both', expand=True, padx=10, pady=10)
    
    root.mainloop()


if __name__ == "__main__":
    test_status_panel()
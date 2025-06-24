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

from storage.unified_storage import UnifiedStorage
from config.settings import DATA_DIR


class StatusPanel(ttk.Frame):
    """状態表示パネル"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.storage = UnifiedStorage(DATA_DIR)
        
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
            # データベースの再読み込みを強制
            self.storage._database = None
            
            # 統計情報取得
            stats = self.storage.get_statistics()
            
            # 統計情報更新
            stats_text = (
                f"📊 プレイリスト: {stats['total_playlists']}件 | "
                f"動画: {stats['total_videos']}件 | "
                f"分析済み: {stats['analyzed_videos']}件"
            )
            self.stats_label.config(text=stats_text)
            
            # 進捗バー更新
            if stats['total_videos'] > 0:
                analysis_percentage = stats['analysis_success_rate'] * 100
                self.progress_var.set(analysis_percentage)
                self.progress_label.config(
                    text=f"{stats['analyzed_videos']}/{stats['total_videos']} ({analysis_percentage:.1f}%)"
                )
            else:
                self.progress_var.set(0)
                self.progress_label.config(text="0/0 (0%)")
            
            # 詳細情報更新
            self.update_details(stats)
            
            print(f"📊 ステータス更新完了: 動画{stats['total_videos']}件, プレイリスト{stats['total_playlists']}件")
            
        except Exception as e:
            error_message = f"❌ 状況取得エラー: {e}"
            self.stats_label.config(text=error_message)
            print(error_message)
    
    def update_details(self, stats):
        """詳細情報を更新"""
        details = []
        
        # プレイリスト別情報
        playlists = stats.get('playlists', {})
        
        if playlists:
            details.append("📋 プレイリスト詳細:")
            for playlist_id, playlist_info in playlists.items():
                line = (
                    f"📁 {playlist_info['title']} - "
                    f"{playlist_info['total_videos']}動画, "
                    f"{playlist_info['analyzed_videos']}分析済み "
                    f"({playlist_info['analysis_rate']:.1%})"
                )
                details.append(line)
                details.append(f"    最終同期: {playlist_info['last_sync']}")
                details.append("")  # 空行
        else:
            details.append("プレイリストが登録されていません")
        
        # クリエイター統計
        total_creators = stats.get('total_creators', 0)
        if total_creators > 0:
            details.append(f"👥 クリエイター: {total_creators}名")
            details.append("")
        
        # タグ・テーマ統計
        total_tags = stats.get('total_tags', 0)
        total_themes = stats.get('total_themes', 0)
        if total_tags > 0 or total_themes > 0:
            details.append(f"🏷️ タグ: {total_tags}件")
            details.append(f"🎨 テーマ: {total_themes}件")
            details.append("")
        
        # データベース情報
        last_updated = stats.get('last_updated', 'N/A')
        database_version = stats.get('database_version', 'N/A')
        details.append(f"💾 データベースバージョン: {database_version}")
        details.append(f"🕒 最終更新: {last_updated}")
        
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
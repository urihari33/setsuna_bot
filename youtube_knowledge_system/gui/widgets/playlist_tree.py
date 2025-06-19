"""
プレイリスト一覧ウィジェット

TreeViewを使用したプレイリスト管理インターフェース
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
from pathlib import Path
from typing import Optional, Dict, Any

# パス設定
sys.path.append(str(Path(__file__).parent.parent.parent))

from managers.playlist_manager import PlaylistManager
from core.data_models import PlaylistCategory, UpdateFrequency


class PlaylistTree(ttk.Frame):
    """プレイリスト一覧ウィジェット"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.playlist_manager = PlaylistManager()
        self.selected_playlist_id: Optional[str] = None
        
        # ウィジェット作成
        self.create_widgets()
        
        # 初期データ読み込み
        self.refresh_data()
    
    def create_widgets(self):
        """ウィジェットを作成"""
        # ヘッダーフレーム
        header_frame = ttk.Frame(self)
        header_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(header_frame, text="📋 プレイリスト一覧", font=('Segoe UI', 11, 'bold')).pack(side='left')
        
        # 更新ボタン
        self.refresh_button = ttk.Button(
            header_frame,
            text="🔄",
            command=self.refresh_data,
            width=3
        )
        self.refresh_button.pack(side='right')
        
        # フィルターフレーム
        filter_frame = ttk.Frame(self)
        filter_frame.pack(fill='x', padx=5, pady=(0, 5))
        
        ttk.Label(filter_frame, text="フィルター:").pack(side='left')
        
        # 有効/無効フィルター
        self.show_enabled_only = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            filter_frame,
            text="有効のみ",
            variable=self.show_enabled_only,
            command=self.apply_filter
        ).pack(side='left', padx=(5, 10))
        
        # カテゴリフィルター
        ttk.Label(filter_frame, text="カテゴリ:").pack(side='left')
        self.category_filter = ttk.Combobox(
            filter_frame,
            values=['全て'] + [cat.value for cat in PlaylistCategory],
            state='readonly',
            width=10
        )
        self.category_filter.set('全て')
        self.category_filter.bind('<<ComboboxSelected>>', lambda e: self.apply_filter())
        self.category_filter.pack(side='left', padx=(5, 0))
        
        # TreeViewフレーム
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # TreeView作成
        columns = ('名前', 'カテゴリ', '動画数', '分析率', '優先度', '更新頻度', '最終同期')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='tree headings', height=10)
        
        # 列設定
        self.tree.heading('#0', text='状態')
        self.tree.column('#0', width=60, minwidth=60)
        
        column_widths = {'名前': 200, 'カテゴリ': 80, '動画数': 60, '分析率': 80, '優先度': 60, '更新頻度': 80, '最終同期': 120}
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=column_widths.get(col, 100), minwidth=50)
        
        # スクロールバー
        scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.tree.config(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side='left', fill='both', expand=True)
        
        # 選択イベント
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        self.tree.bind('<Double-1>', self.on_double_click)
        
        # コンテキストメニュー
        self.create_context_menu()
        self.tree.bind('<Button-3>', self.show_context_menu)  # 右クリック
        
        # 詳細パネル
        self.create_details_panel()
    
    def create_context_menu(self):
        """コンテキストメニューを作成"""
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="差分更新", command=self.update_selected)
        self.context_menu.add_command(label="設定編集", command=self.edit_selected)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="有効化", command=self.enable_selected)
        self.context_menu.add_command(label="無効化", command=self.disable_selected)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="削除", command=self.delete_selected)
    
    def create_details_panel(self):
        """詳細パネルを作成"""
        details_frame = ttk.LabelFrame(self, text="プレイリスト詳細")
        details_frame.pack(fill='x', padx=5, pady=5)
        
        self.details_text = tk.Text(
            details_frame,
            height=4,
            wrap='word',
            font=('Segoe UI', 9),
            state='disabled'
        )
        self.details_text.pack(fill='x', padx=5, pady=5)
    
    def refresh_data(self):
        """データを更新"""
        try:
            # 既存データをクリア
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # プレイリスト状況取得
            status = self.playlist_manager.get_playlist_status()
            
            if 'error' in status:
                messagebox.showerror("エラー", f"データ取得エラー: {status['error']}")
                return
            
            # プレイリスト詳細を挿入
            playlist_details = status.get('playlist_details', [])
            
            for detail in playlist_details:
                # ステータスアイコン
                enabled_icon = "✅" if detail['enabled'] else "❌"
                db_icon = "📁" if detail['in_database'] else "🆕"
                status_icon = f"{enabled_icon}{db_icon}"
                
                # 最終同期時刻の整形
                last_sync = detail['last_sync']
                if last_sync:
                    from datetime import datetime
                    try:
                        sync_time = datetime.fromisoformat(last_sync)
                        last_sync_str = sync_time.strftime('%m/%d %H:%M')
                    except:
                        last_sync_str = "不明"
                else:
                    last_sync_str = "未実行"
                
                # 行データ
                values = (
                    detail['display_name'],
                    detail['category'],
                    detail['total_videos'],
                    f"{detail['analysis_rate']:.1%}",
                    detail['priority'],
                    detail['update_frequency'],
                    last_sync_str
                )
                
                # TreeViewに挿入
                item_id = self.tree.insert('', 'end', text=status_icon, values=values)
                
                # プレイリストIDをアイテムにタグとして保存（#0列は設定できないため削除）
                self.tree.item(item_id, tags=(detail['id'],))
            
            # フィルター適用
            self.apply_filter()
            
        except Exception as e:
            messagebox.showerror("エラー", f"データ更新エラー: {e}")
    
    def apply_filter(self):
        """フィルターを適用"""
        enabled_only = self.show_enabled_only.get()
        category_filter = self.category_filter.get()
        
        # 全アイテムを表示
        for item in self.tree.get_children():
            self.tree.reattach(item, '', 'end')
        
        # フィルター適用
        if enabled_only or category_filter != '全て':
            status = self.playlist_manager.get_playlist_status()
            if 'playlist_details' in status:
                items_to_hide = []
                
                for item in self.tree.get_children():
                    tags = self.tree.item(item, 'tags')
                    if tags:
                        playlist_id = tags[0]
                        
                        # 対応する詳細情報を検索
                        detail = next((d for d in status['playlist_details'] if d['id'] == playlist_id), None)
                        
                        if detail:
                            # フィルター条件チェック
                            if enabled_only and not detail['enabled']:
                                items_to_hide.append(item)
                            elif category_filter != '全て' and detail['category'] != category_filter:
                                items_to_hide.append(item)
                
                # 非表示
                for item in items_to_hide:
                    self.tree.detach(item)
    
    def on_select(self, event):
        """選択イベント"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            tags = self.tree.item(item, 'tags')
            if tags:
                self.selected_playlist_id = tags[0]
                self.update_details()
    
    def on_double_click(self, event):
        """ダブルクリックイベント"""
        if self.selected_playlist_id:
            self.edit_selected()
    
    def update_details(self):
        """詳細パネルを更新"""
        if not self.selected_playlist_id:
            self.details_text.config(state='normal')
            self.details_text.delete('1.0', 'end')
            self.details_text.insert('1.0', "プレイリストを選択してください")
            self.details_text.config(state='disabled')
            return
        
        try:
            # 設定情報取得
            config = self.playlist_manager.config_manager.get_config(self.selected_playlist_id)
            if not config:
                return
            
            # 詳細情報作成
            details = []
            details.append(f"📋 名前: {config.display_name}")
            details.append(f"🆔 ID: {config.playlist_id}")
            details.append(f"🏷️ カテゴリ: {config.category.value}")
            details.append(f"🔄 更新頻度: {config.update_frequency.value}")
            details.append(f"⭐ 優先度: {config.priority}")
            details.append(f"🔍 自動分析: {'有効' if config.auto_analyze else '無効'}")
            details.append(f"📝 説明: {config.description or 'なし'}")
            
            if config.tags:
                details.append(f"🏷️ タグ: {', '.join(config.tags)}")
            
            details.append(f"🔗 URL: {config.url}")
            
            # 詳細テキスト更新
            self.details_text.config(state='normal')
            self.details_text.delete('1.0', 'end')
            self.details_text.insert('1.0', '\n'.join(details))
            self.details_text.config(state='disabled')
            
        except Exception as e:
            self.details_text.config(state='normal')
            self.details_text.delete('1.0', 'end')
            self.details_text.insert('1.0', f"詳細取得エラー: {e}")
            self.details_text.config(state='disabled')
    
    def show_context_menu(self, event):
        """コンテキストメニューを表示"""
        # クリック位置のアイテムを選択
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.on_select(None)
            self.context_menu.post(event.x_root, event.y_root)
    
    def update_selected(self):
        """選択したプレイリストを更新"""
        if not self.selected_playlist_id:
            messagebox.showwarning("警告", "プレイリストを選択してください")
            return
        
        # 親ウィンドウにイベントを通知
        self.event_generate('<<UpdatePlaylist>>')
    
    def edit_selected(self):
        """選択したプレイリストを編集"""
        if not self.selected_playlist_id:
            messagebox.showwarning("警告", "プレイリストを選択してください")
            return
        
        # 親ウィンドウにイベントを通知
        self.event_generate('<<EditPlaylist>>')
    
    def enable_selected(self):
        """選択したプレイリストを有効化"""
        if not self.selected_playlist_id:
            messagebox.showwarning("警告", "プレイリストを選択してください")
            return
        
        try:
            success, message = self.playlist_manager.config_manager.enable_playlist(self.selected_playlist_id)
            if success:
                messagebox.showinfo("成功", message)
                self.refresh_data()
            else:
                messagebox.showerror("エラー", message)
        except Exception as e:
            messagebox.showerror("エラー", f"有効化エラー: {e}")
    
    def disable_selected(self):
        """選択したプレイリストを無効化"""
        if not self.selected_playlist_id:
            messagebox.showwarning("警告", "プレイリストを選択してください")
            return
        
        try:
            success, message = self.playlist_manager.config_manager.disable_playlist(self.selected_playlist_id)
            if success:
                messagebox.showinfo("成功", message)
                self.refresh_data()
            else:
                messagebox.showerror("エラー", message)
        except Exception as e:
            messagebox.showerror("エラー", f"無効化エラー: {e}")
    
    def delete_selected(self):
        """選択したプレイリストを削除"""
        if not self.selected_playlist_id:
            messagebox.showwarning("警告", "プレイリストを選択してください")
            return
        
        config = self.playlist_manager.config_manager.get_config(self.selected_playlist_id)
        if not config:
            return
        
        # 確認ダイアログ
        result = messagebox.askyesnocancel(
            "プレイリスト削除",
            f"プレイリスト '{config.display_name}' を削除しますか？\n\n"
            f"「はい」: 設定のみ削除\n"
            f"「いいえ」: 設定とデータを削除\n"
            f"「キャンセル」: 削除しない"
        )
        
        if result is None:  # キャンセル
            return
        
        try:
            success, message = self.playlist_manager.remove_playlist(
                playlist_id=self.selected_playlist_id,
                remove_data=not result,  # 「いいえ」の場合はデータも削除
                backup_before_removal=True
            )
            
            if success:
                messagebox.showinfo("成功", message)
                self.refresh_data()
                self.selected_playlist_id = None
                self.update_details()
            else:
                messagebox.showerror("エラー", message)
        except Exception as e:
            messagebox.showerror("エラー", f"削除エラー: {e}")
    
    def get_selected_playlist_id(self) -> Optional[str]:
        """選択中のプレイリストIDを取得"""
        return self.selected_playlist_id


# テスト用関数
def test_playlist_tree():
    """プレイリスト一覧ウィジェットのテスト"""
    root = tk.Tk()
    root.title("プレイリスト一覧 テスト")
    root.geometry("800x600")
    
    tree = PlaylistTree(root)
    tree.pack(fill='both', expand=True, padx=10, pady=10)
    
    root.mainloop()


if __name__ == "__main__":
    test_playlist_tree()
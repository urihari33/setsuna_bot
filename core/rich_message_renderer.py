#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
リッチメッセージ表示システム - Phase 2C-2
統合メッセージ（画像+URL+テキスト）の美しい表示機能
"""

import tkinter as tk
from tkinter import ttk
import os
from pathlib import Path
from PIL import Image, ImageTk
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
import re
from urllib.parse import urlparse

class RichMessageRenderer:
    """リッチメッセージ表示を管理するクラス"""
    
    def __init__(self, text_widget: tk.Text):
        """
        初期化
        
        Args:
            text_widget: 表示対象のtkinter.Textウィジェット
        """
        self.text_widget = text_widget
        self.image_cache = {}  # 画像キャッシュ
        self.thumbnail_size = (80, 60)  # サムネイルサイズ
        
        # スタイル設定
        self._setup_styles()
        
        print("🎨 RichMessageRenderer初期化完了")
    
    def _setup_styles(self):
        """表示スタイルの設定"""
        # 基本スタイル
        self.text_widget.tag_config("user_name", foreground="blue", font=('Arial', 10, 'bold'))
        self.text_widget.tag_config("bot_name", foreground="green", font=('Arial', 10, 'bold'))
        self.text_widget.tag_config("timestamp", foreground="gray", font=('Arial', 8))
        self.text_widget.tag_config("message_text", font=('Arial', 10))
        
        # 統合メッセージ用スタイル
        self.text_widget.tag_config("integrated_bg", background="#f0f8ff", relief="raised")
        self.text_widget.tag_config("attachment_info", foreground="#666666", font=('Arial', 9, 'italic'))
        self.text_widget.tag_config("url_link", foreground="#1e90ff", font=('Arial', 9, 'underline'))
        self.text_widget.tag_config("image_info", foreground="#228b22", font=('Arial', 9))
        
        print("🎨 メッセージスタイル設定完了")
    
    def render_message(self, speaker: str, message: Union[str, Dict], message_type: str = "text"):
        """
        メッセージを表示
        
        Args:
            speaker: 発言者名
            message: メッセージ内容（文字列 or 統合メッセージ辞書）
            message_type: メッセージタイプ
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # メッセージタイプに応じて分岐
        if message_type == "integrated" and isinstance(message, dict):
            self._render_integrated_message(speaker, message, timestamp)
        else:
            self._render_simple_message(speaker, str(message), message_type, timestamp)
    
    def _render_simple_message(self, speaker: str, message: str, message_type: str, timestamp: str):
        """シンプルメッセージの表示"""
        self.text_widget.config(state=tk.NORMAL)
        
        # 発言者によって色分け
        if speaker == "あなた":
            speaker_color = "user_name"
            type_icon = "🗣️" if message_type == "voice" else "💬"
        else:  # せつな
            speaker_color = "bot_name"
            type_icon = "🤖"
        
        # メッセージヘッダー
        self.text_widget.insert(tk.END, f"[{timestamp}] ", "timestamp")
        self.text_widget.insert(tk.END, f"{type_icon} {speaker}: ", speaker_color)
        self.text_widget.insert(tk.END, f"{message}\n", "message_text")
        
        # 最下部にスクロール
        self.text_widget.see(tk.END)
        self.text_widget.config(state=tk.DISABLED)
    
    def _render_integrated_message(self, speaker: str, integrated_message: Dict, timestamp: str):
        """統合メッセージの表示"""
        self.text_widget.config(state=tk.NORMAL)
        
        # 発言者によって設定
        if speaker == "あなた":
            speaker_color = "user_name"
            type_icon = "📤"
        else:
            speaker_color = "bot_name"
            type_icon = "🤖"
        
        # メッセージヘッダー
        self.text_widget.insert(tk.END, f"[{timestamp}] ", "timestamp")
        self.text_widget.insert(tk.END, f"{type_icon} {speaker}: ", speaker_color)
        
        # 統合メッセージ背景開始
        start_index = self.text_widget.index(tk.END)
        
        # テキスト部分
        text_content = integrated_message.get('text', '')
        if text_content:
            self.text_widget.insert(tk.END, f"{text_content}\n", "message_text")
        
        # 添付情報表示
        self._render_attachments(integrated_message)
        
        # 統合メッセージ背景終了
        end_index = self.text_widget.index(tk.END)
        # 統合メッセージ全体に背景色を適用
        # self.text_widget.tag_add("integrated_bg", start_index, end_index)
        
        self.text_widget.insert(tk.END, "\n")
        
        # 最下部にスクロール
        self.text_widget.see(tk.END)
        self.text_widget.config(state=tk.DISABLED)
    
    def _render_attachments(self, integrated_message: Dict):
        """添付ファイル・URL情報の表示"""
        images = integrated_message.get('images', [])
        url_info = integrated_message.get('url')
        
        if images or url_info:
            self.text_widget.insert(tk.END, "📎 添付:\n", "attachment_info")
        
        # 画像添付の表示
        for image_info in images:
            self._render_image_attachment(image_info)
        
        # URL添付の表示
        if url_info:
            self._render_url_attachment(url_info)
    
    def _render_image_attachment(self, image_info: Dict):
        """画像添付の表示"""
        image_name = image_info.get('name', 'unknown')
        image_path = image_info.get('path', '')
        image_size = image_info.get('size', 0)
        
        # ファイルサイズ表示
        size_mb = image_size / (1024 * 1024) if image_size > 0 else 0
        
        # 画像サムネイル表示（実際の画像があれば）
        thumbnail_displayed = False
        if image_path and os.path.exists(image_path):
            thumbnail_displayed = self._display_image_thumbnail(image_path, image_name)
        
        # 画像情報テキスト
        if thumbnail_displayed:
            self.text_widget.insert(tk.END, f"  📸 {image_name} ({size_mb:.1f}MB)\n", "image_info")
        else:
            self.text_widget.insert(tk.END, f"  📸 {image_name} ({size_mb:.1f}MB) [プレビュー不可]\n", "image_info")
    
    def _display_image_thumbnail(self, image_path: str, image_name: str) -> bool:
        """画像サムネイルの表示"""
        try:
            # キャッシュ確認
            if image_path in self.image_cache:
                photo = self.image_cache[image_path]
            else:
                # 画像読み込み・リサイズ
                with Image.open(image_path) as img:
                    # サムネイル作成
                    try:
                        img.thumbnail(self.thumbnail_size, Image.Resampling.LANCZOS)
                    except AttributeError:
                        # 古いPILバージョン対応
                        img.thumbnail(self.thumbnail_size, Image.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    self.image_cache[image_path] = photo
            
            # テキストウィジェットに画像を挿入
            self.text_widget.image_create(tk.END, image=photo)
            self.text_widget.insert(tk.END, "\n")
            
            return True
            
        except Exception as e:
            print(f"⚠️ 画像サムネイル表示エラー: {e}")
            return False
    
    def _render_url_attachment(self, url_info: Dict):
        """URL添付の表示"""
        url = url_info.get('url', '')
        title = url_info.get('title', 'URL')
        
        # URLプレビューカード風表示
        self.text_widget.insert(tk.END, f"  🔗 {title}\n", "url_link")
        
        # URLの短縮表示
        if len(url) > 50:
            display_url = url[:47] + "..."
        else:
            display_url = url
        
        self.text_widget.insert(tk.END, f"     {display_url}\n", "attachment_info")
        
        # URL種別の表示
        url_type = self._classify_url(url)
        if url_type != "一般":
            self.text_widget.insert(tk.END, f"     [{url_type}]\n", "attachment_info")
    
    def _classify_url(self, url: str) -> str:
        """URLの分類"""
        if 'youtube.com' in url or 'youtu.be' in url:
            return "YouTube動画"
        elif 'twitter.com' in url or 'x.com' in url:
            return "Twitter/X"
        elif 'instagram.com' in url:
            return "Instagram"
        elif 'tiktok.com' in url:
            return "TikTok"
        else:
            return "一般"
    
    def clear_display(self):
        """表示内容をクリア"""
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete("1.0", tk.END)
        self.text_widget.config(state=tk.DISABLED)
        self.image_cache.clear()
        print("🧹 メッセージ表示クリア完了")
    
    def get_message_count(self) -> int:
        """表示されているメッセージ数を取得"""
        content = self.text_widget.get("1.0", tk.END)
        # タイムスタンプ付きの行をカウント
        timestamps = re.findall(r'\[\d{2}:\d{2}:\d{2}\]', content)
        return len(timestamps)
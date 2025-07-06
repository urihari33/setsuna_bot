#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
プログレス表示ウィジェット - Phase 2C-4
統合メッセージ処理の詳細進捗をGUIで表示
"""

import tkinter as tk
from tkinter import ttk
import time
from typing import Dict, Optional

class ProgressWidget:
    """プログレス表示ウィジェット"""
    
    def __init__(self, parent_frame: tk.Widget):
        """
        初期化
        
        Args:
            parent_frame: 親フレーム
        """
        self.parent_frame = parent_frame
        self.is_visible = False
        self.last_update_time = 0.0
        
        # メインフレーム（初期状態では非表示）
        self.main_frame = ttk.LabelFrame(parent_frame, text="📊 処理進捗", padding=10)
        
        # プログレスバー
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            self.main_frame,
            variable=self.progress_var,
            maximum=100,
            mode='determinate',
            length=400
        )
        self.progress_bar.pack(fill=tk.X, pady=(0, 5))
        
        # 進捗ラベル
        self.progress_label = ttk.Label(
            self.main_frame,
            text="待機中...",
            font=('Arial', 9)
        )
        self.progress_label.pack(anchor=tk.W)
        
        # 詳細情報フレーム
        self.detail_frame = ttk.Frame(self.main_frame)
        self.detail_frame.pack(fill=tk.X, pady=(5, 0))
        
        # 現在のステップ
        self.current_step_label = ttk.Label(
            self.detail_frame,
            text="",
            font=('Arial', 8),
            foreground="blue"
        )
        self.current_step_label.pack(anchor=tk.W)
        
        # 経過時間・推定残り時間
        self.time_label = ttk.Label(
            self.detail_frame,
            text="",
            font=('Arial', 8),
            foreground="gray"
        )
        self.time_label.pack(anchor=tk.W)
        
        # キャンセルボタン
        self.cancel_button = ttk.Button(
            self.detail_frame,
            text="🛑 キャンセル",
            command=self._on_cancel,
            state="disabled"
        )
        self.cancel_button.pack(side=tk.RIGHT, padx=(10, 0))
        
        # 詳細表示ボタン
        self.detail_button = ttk.Button(
            self.detail_frame,
            text="📋 詳細",
            command=self._show_details,
            state="disabled"
        )
        self.detail_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # コールバック関数
        self.cancel_callback = None
        self.detail_callback = None
        
        print("📊 ProgressWidget初期化完了")
    
    def show(self):
        """プログレス表示を表示"""
        if not self.is_visible:
            self.main_frame.pack(fill=tk.X, pady=(5, 0))
            self.is_visible = True
            self.cancel_button.config(state="normal")
            self.detail_button.config(state="normal")
            print("📊 プログレス表示開始")
    
    def hide(self):
        """プログレス表示を非表示"""
        if self.is_visible:
            self.main_frame.pack_forget()
            self.is_visible = False
            self.cancel_button.config(state="disabled")
            self.detail_button.config(state="disabled")
            print("📊 プログレス表示終了")
    
    def update_progress(self, status: Dict):
        """
        プログレス状況を更新
        
        Args:
            status: ProgressManagerから取得した状況辞書
        """
        # 更新頻度制限（秒間最大10回）
        current_time = time.time()
        if current_time - self.last_update_time < 0.1:
            return
        self.last_update_time = current_time
        
        try:
            # プログレスバー更新
            total_progress = status.get('total_progress', 0.0)
            self.progress_var.set(total_progress)
            
            # 進捗ラベル更新
            if status.get('is_running', False):
                self.progress_label.config(text=f"処理中... {total_progress:.1f}%")
            elif status.get('is_cancelled', False):
                self.progress_label.config(text="🛑 キャンセルされました")
            elif total_progress >= 100.0:
                self.progress_label.config(text="✅ 完了")
            else:
                self.progress_label.config(text="待機中...")
            
            # 現在のステップ情報
            current_step = status.get('current_step')
            if current_step and status.get('is_running', False):
                step_name = current_step.get('name', '')
                step_desc = current_step.get('description', '')
                sub_progress = current_step.get('sub_progress', 0.0)
                
                step_text = f"🔄 {step_name}"
                if step_desc and step_desc != step_name:
                    step_text += f": {step_desc}"
                if sub_progress > 0:
                    step_text += f" ({sub_progress:.1f}%)"
                
                self.current_step_label.config(text=step_text)
            else:
                self.current_step_label.config(text="")
            
            # 時間情報
            elapsed_time = status.get('elapsed_time', 0.0)
            estimated_remaining = status.get('estimated_remaining', 0.0)
            
            time_text = ""
            if elapsed_time > 0:
                time_text = f"経過: {elapsed_time:.1f}秒"
                if estimated_remaining > 0 and status.get('is_running', False):
                    time_text += f" | 残り: 約{estimated_remaining:.1f}秒"
            
            self.time_label.config(text=time_text)
            
            # 完了時は3秒後に自動非表示
            if not status.get('is_running', False) and total_progress >= 100.0:
                self.parent_frame.after(3000, self.hide)
            
        except Exception as e:
            print(f"⚠️ プログレス更新エラー: {e}")
    
    def set_cancel_callback(self, callback):
        """キャンセルコールバック設定"""
        self.cancel_callback = callback
    
    def set_detail_callback(self, callback):
        """詳細表示コールバック設定"""
        self.detail_callback = callback
    
    def _on_cancel(self):
        """キャンセルボタンクリック"""
        if self.cancel_callback:
            try:
                self.cancel_callback()
            except Exception as e:
                print(f"⚠️ キャンセルコールバックエラー: {e}")
    
    def _show_details(self):
        """詳細表示ボタンクリック"""
        if self.detail_callback:
            try:
                self.detail_callback()
            except Exception as e:
                print(f"⚠️ 詳細表示コールバックエラー: {e}")

class DetailProgressDialog:
    """詳細プログレス表示ダイアログ"""
    
    def __init__(self, parent, status: Dict):
        """
        初期化
        
        Args:
            parent: 親ウィンドウ
            status: プログレス状況
        """
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("📊 処理詳細")
        self.dialog.geometry("500x400")
        self.dialog.resizable(True, True)
        
        # メインフレーム
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 全体情報
        info_frame = ttk.LabelFrame(main_frame, text="📊 全体情報", padding=10)
        info_frame.pack(fill=tk.X, pady=(0, 10))
        
        total_progress = status.get('total_progress', 0.0)
        stats = status.get('stats', {})
        
        ttk.Label(
            info_frame,
            text=f"全体進捗: {total_progress:.1f}%"
        ).pack(anchor=tk.W)
        
        ttk.Label(
            info_frame,
            text=f"ステップ: {stats.get('completed_steps', 0)}/{stats.get('total_steps', 0)} 完了"
        ).pack(anchor=tk.W)
        
        if stats.get('error_steps', 0) > 0:
            ttk.Label(
                info_frame,
                text=f"エラー: {stats.get('error_steps', 0)} 件",
                foreground="red"
            ).pack(anchor=tk.W)
        
        elapsed_time = status.get('elapsed_time', 0.0)
        if elapsed_time > 0:
            ttk.Label(
                info_frame,
                text=f"経過時間: {elapsed_time:.1f} 秒"
            ).pack(anchor=tk.W)
        
        # ステップ詳細
        steps_frame = ttk.LabelFrame(main_frame, text="📋 ステップ詳細", padding=10)
        steps_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # スクロール可能なテキストエリア
        text_frame = ttk.Frame(steps_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.text_widget = tk.Text(
            text_frame,
            wrap=tk.WORD,
            height=15,
            width=60,
            font=('Consolas', 9)
        )
        
        scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.text_widget.yview)
        self.text_widget.configure(yscrollcommand=scrollbar.set)
        
        self.text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # ステップ情報を表示
        self._display_steps(status.get('steps', []))
        
        # 閉じるボタン
        close_button = ttk.Button(
            main_frame,
            text="閉じる",
            command=self.dialog.destroy
        )
        close_button.pack(side=tk.RIGHT)
    
    def _display_steps(self, steps):
        """ステップ詳細を表示"""
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete("1.0", tk.END)
        
        for i, step in enumerate(steps, 1):
            status_icon = {
                'pending': '⏳',
                'running': '🔄',
                'completed': '✅',
                'error': '❌'
            }.get(step.get('status', 'pending'), '❓')
            
            step_text = f"{i}. {status_icon} {step.get('name', 'Unknown')}\n"
            
            description = step.get('description', '')
            if description:
                step_text += f"   説明: {description}\n"
            
            sub_progress = step.get('sub_progress', 0.0)
            if sub_progress > 0:
                step_text += f"   進捗: {sub_progress:.1f}%\n"
            
            error_message = step.get('error_message', '')
            if error_message:
                step_text += f"   エラー: {error_message}\n"
            
            step_text += "\n"
            
            self.text_widget.insert(tk.END, step_text)
        
        self.text_widget.config(state=tk.DISABLED)
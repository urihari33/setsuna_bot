#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
せつなBot ミニマルGUI - 新せつなBot
ステータス表示・音声パラメータ調整・簡易操作
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import sys
import os
import tkinter.font as tkFont

# 文字エンコーディング強制設定
import locale
locale.setlocale(locale.LC_ALL, 'C.UTF-8')

# coreモジュールのパスを追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class SetsunaGUI:
    def __init__(self):
        """せつなBot GUI初期化"""
        # メインウィンドウ作成
        self.root = tk.Tk()
        # エンコーディング設定
        self.root.option_add('*font', 'TkDefaultFont')
        
        # ウィンドウ設定
        self.root.title("せつなBot - 音声対話システム")
        self.root.geometry("500x600")
        self.root.resizable(True, True)
        
        # 日本語フォント設定
        self.fonts = self._setup_fonts()
        
        # システムコンポーネント（遅延初期化）
        self.voice_output = None
        self.setsuna_chat = None
        self.voice_input = None
        
        # 状態管理
        self.is_initialized = False
        self.is_talking = False
        self.conversation_count = 0
        
        # GUI要素の初期化
        self._create_widgets()
        self._setup_layout()
        
        # 初期化開始
        self._initialize_system()
    
    def _setup_fonts(self):
        """日本語フォント設定"""
        try:
            # 日本語フォント候補（優先順）
            jp_font_candidates = [
                "Yu Gothic",
                "Meiryo", 
                "BIZ UDMincho",
                "DejaVu Sans",
                "TkDefaultFont"
            ]
            
            # フォント動作テスト
            selected_font = "TkDefaultFont"  # デフォルト
            for font_name in jp_font_candidates:
                try:
                    # フォント作成テストで動作確認
                    test_font = tkFont.Font(family=font_name, size=10)
                    selected_font = font_name
                    print(f"✅ 選択フォント: {selected_font}")
                    break
                except Exception as e:
                    print(f"⚠️ {font_name}: 使用不可 - {e}")
                    continue
            
            # フォント設定
            fonts = {
                'default': (selected_font, 10),
                'title': (selected_font, 16, "bold"),
                'small': (selected_font, 8)
            }
            
            return fonts
            
        except Exception as e:
            print(f"フォント設定エラー: {e}")
            # フォールバック
            return {
                'default': ("TkDefaultFont", 10),
                'title': ("TkDefaultFont", 16, "bold"),
                'small': ("TkDefaultFont", 8)
            }
    
    def _create_widgets(self):
        """GUI要素を作成"""
        # ===== タイトルエリア =====
        title_frame = ttk.Frame(self.root)
        title_frame.pack(fill=tk.X, padx=10, pady=10)
        
        title_label = ttk.Label(
            title_frame, 
            text="せつなBot", 
            font=self.fonts['title']
        )
        title_label.pack()
        
        subtitle_label = ttk.Label(
            title_frame,
            text="音声対話システム v2.0",
            font=self.fonts['default']
        )
        subtitle_label.pack()
        
        # ===== ステータスエリア =====
        status_frame = ttk.LabelFrame(self.root, text="Status")  # 英語に変更
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 日本語タイトルを別途追加
        status_title = ttk.Label(status_frame, text="ステータス", font=self.fonts['title'])
        status_title.grid(row=0, column=0, columnspan=2, pady=(0,5))
        
        # システム状態
        self.system_status_var = tk.StringVar(value="初期化中...")
        ttk.Label(status_frame, text="システム状態:", font=self.fonts['default']).grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.system_status_label = ttk.Label(status_frame, textvariable=self.system_status_var, font=self.fonts['default'])
        self.system_status_label.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        # 対話回数
        self.conversation_count_var = tk.StringVar(value="0回")
        ttk.Label(status_frame, text="対話回数:", font=self.fonts['default']).grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(status_frame, textvariable=self.conversation_count_var, font=self.fonts['default']).grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        
        # ===== 音声パラメータエリア =====
        voice_frame = ttk.LabelFrame(self.root, text="Voice Settings")  # 英語に変更
        voice_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 日本語タイトルを別途追加
        voice_title = ttk.Label(voice_frame, text="音声設定", font=self.fonts['title'])
        voice_title.grid(row=0, column=0, columnspan=3, pady=(0,5))
        
        # 話速スライダー
        ttk.Label(voice_frame, text="話速:", font=self.fonts['default']).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.speed_var = tk.DoubleVar(value=1.2)
        self.speed_scale = ttk.Scale(
            voice_frame, 
            from_=0.5, to=2.0, 
            variable=self.speed_var,
            orient=tk.HORIZONTAL,
            command=self._on_voice_parameter_change
        )
        self.speed_scale.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        self.speed_value_label = ttk.Label(voice_frame, text="1.2x", font=self.fonts['default'])
        self.speed_value_label.grid(row=1, column=2, padx=5, pady=5)
        
        # 音程スライダー
        ttk.Label(voice_frame, text="音程:", font=self.fonts['default']).grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.pitch_var = tk.DoubleVar(value=0.0)
        self.pitch_scale = ttk.Scale(
            voice_frame,
            from_=-0.15, to=0.15,
            variable=self.pitch_var,
            orient=tk.HORIZONTAL,
            command=self._on_voice_parameter_change
        )
        self.pitch_scale.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        self.pitch_value_label = ttk.Label(voice_frame, text="0.0", font=self.fonts['default'])
        self.pitch_value_label.grid(row=2, column=2, padx=5, pady=5)
        
        # 抑揚スライダー
        ttk.Label(voice_frame, text="抑揚:", font=self.fonts['default']).grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        self.intonation_var = tk.DoubleVar(value=1.0)
        self.intonation_scale = ttk.Scale(
            voice_frame,
            from_=0.5, to=2.0,
            variable=self.intonation_var,
            orient=tk.HORIZONTAL,
            command=self._on_voice_parameter_change
        )
        self.intonation_scale.grid(row=3, column=1, sticky=tk.EW, padx=5, pady=5)
        self.intonation_value_label = ttk.Label(voice_frame, text="1.0", font=self.fonts['default'])
        self.intonation_value_label.grid(row=3, column=2, padx=5, pady=5)
        
        # カラムのリサイズ設定
        voice_frame.columnconfigure(1, weight=1)
        
        # ===== 操作エリア =====
        control_frame = ttk.LabelFrame(self.root, text="Control Panel")
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 日本語タイトルを別途追加
        control_title = ttk.Label(control_frame, text="操作パネル", font=self.fonts['title'])
        control_title.pack(pady=(0,5))
        
        # テスト再生ボタン
        self.test_button = ttk.Button(
            control_frame,
            text="音声テスト",
            command=self._test_voice,
            state=tk.DISABLED
        )
        self.test_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # 会話開始ボタン
        self.chat_button = ttk.Button(
            control_frame,
            text="テキスト会話",
            command=self._start_text_chat,
            state=tk.DISABLED
        )
        self.chat_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # 設定リセットボタン
        self.reset_button = ttk.Button(
            control_frame,
            text="設定リセット",
            command=self._reset_settings
        )
        self.reset_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # ===== ログエリア =====
        log_frame = ttk.LabelFrame(self.root, text="Log")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 日本語タイトルを別途追加
        log_title = ttk.Label(log_frame, text="ログ", font=self.fonts['title'])
        log_title.pack(pady=(0,5))
        
        # ログテキストエリア
        self.log_text = tk.Text(log_frame, height=10, wrap=tk.WORD, font=self.fonts['default'])
        log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
    
    def _setup_layout(self):
        """レイアウト設定"""
        # ウィンドウ終了時の処理
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # 初期ログメッセージ
        self._log("🤖 せつなBot GUI起動中...")
        self._log("システム初期化を開始します...")
    
    def _initialize_system(self):
        """システムコンポーネントの初期化"""
        def init_worker():
            try:
                self._log("🔧 音声出力システム初期化中...")
                from voice_output import VoiceOutput
                self.voice_output = VoiceOutput()
                
                self._log("🔧 チャットシステム初期化中...")
                from setsuna_chat import SetsunaChat
                self.setsuna_chat = SetsunaChat()
                
                self._log("🔧 音声入力システム初期化中...")
                try:
                    from voice_input import VoiceInput
                    self.voice_input = VoiceInput()
                except:
                    from voice_input_mock import VoiceInput
                    self.voice_input = VoiceInput()
                    self._log("⚠️ モック音声入力を使用します")
                
                # UI更新
                self.root.after(0, self._on_initialization_complete)
                
            except Exception as e:
                error_msg = f"❌ 初期化エラー: {e}"
                self._log(error_msg)
                self.root.after(0, lambda: self._on_initialization_error(str(e)))
        
        # 別スレッドで初期化実行
        threading.Thread(target=init_worker, daemon=True).start()
    
    def _on_initialization_complete(self):
        """初期化完了時の処理"""
        self.is_initialized = True
        self.system_status_var.set("✅ 待機中")
        
        # ボタンの有効化
        self.test_button.config(state=tk.NORMAL)
        self.chat_button.config(state=tk.NORMAL)
        
        self._log("✅ せつなBot 初期化完了！")
        self._log("🎛️ 音声パラメータを調整できます")
        self._log("💬 テキスト会話ボタンで対話開始")
        
        # 音声パラメータの初期適用
        self._apply_voice_parameters()
    
    def _on_initialization_error(self, error):
        """初期化エラー時の処理"""
        self.system_status_var.set("❌ 初期化失敗")
        messagebox.showerror("初期化エラー", f"システムの初期化に失敗しました:\n{error}")
    
    def _on_voice_parameter_change(self, value=None):
        """音声パラメータ変更時の処理"""
        # ラベル更新
        self.speed_value_label.config(text=f"{self.speed_var.get():.1f}x")
        self.pitch_value_label.config(text=f"{self.pitch_var.get():.2f}")
        self.intonation_value_label.config(text=f"{self.intonation_var.get():.1f}")
        
        # 音声システムに反映
        if self.is_initialized and self.voice_output:
            self._apply_voice_parameters()
    
    def _apply_voice_parameters(self):
        """音声パラメータを音声システムに適用"""
        try:
            self.voice_output.update_settings(
                speed=self.speed_var.get(),
                pitch=self.pitch_var.get(),
                intonation=self.intonation_var.get()
            )
            self._log(f"🎛️ 音声設定更新: 話速{self.speed_var.get():.1f}x, 音程{self.pitch_var.get():.2f}, 抑揚{self.intonation_var.get():.1f}")
        except Exception as e:
            self._log(f"❌ 音声設定エラー: {e}")
    
    def _test_voice(self):
        """音声テスト実行"""
        if not self.is_initialized:
            return
        
        def test_worker():
            try:
                self.root.after(0, lambda: self.system_status_var.set("🔊 音声テスト中"))
                self._log("🔊 音声テスト実行中...")
                
                test_text = "こんにちは、せつなです。音声設定のテストをしています。"
                self.voice_output.speak(test_text)
                
                self.root.after(0, lambda: self.system_status_var.set("✅ 待機中"))
                self._log("✅ 音声テスト完了")
                
            except Exception as e:
                error_msg = f"❌ 音声テストエラー: {e}"
                self._log(error_msg)
                self.root.after(0, lambda: self.system_status_var.set("❌ エラー"))
        
        threading.Thread(target=test_worker, daemon=True).start()
    
    def _start_text_chat(self):
        """テキスト会話開始"""
        if not self.is_initialized:
            return
        
        # 簡易テキスト会話ウィンドウを開く
        self._open_text_chat_window()
    
    def _open_text_chat_window(self):
        """テキスト会話ウィンドウを開く"""
        chat_window = tk.Toplevel(self.root)
        chat_window.title("せつなとテキスト会話")
        chat_window.geometry("600x400")
        
        # 会話表示エリア
        chat_frame = ttk.Frame(chat_window)
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        chat_display = tk.Text(chat_frame, wrap=tk.WORD, height=15, font=self.fonts['default'])
        chat_scrollbar = ttk.Scrollbar(chat_frame, orient=tk.VERTICAL, command=chat_display.yview)
        chat_display.configure(yscrollcommand=chat_scrollbar.set)
        
        chat_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        chat_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 入力エリア
        input_frame = ttk.Frame(chat_window)
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        input_entry = ttk.Entry(input_frame, font=self.fonts['default'])
        input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        send_button = ttk.Button(input_frame, text="送信")
        send_button.pack(side=tk.RIGHT)
        
        # 初期メッセージ
        chat_display.insert(tk.END, "せつな: こんにちは！何かお話ししましょうか？\n\n")
        chat_display.config(state=tk.DISABLED)
        
        def send_message():
            user_input = input_entry.get().strip()
            if not user_input:
                return
            
            # ユーザーメッセージ表示
            chat_display.config(state=tk.NORMAL)
            chat_display.insert(tk.END, f"あなた: {user_input}\n")
            chat_display.config(state=tk.DISABLED)
            chat_display.see(tk.END)
            
            input_entry.delete(0, tk.END)
            
            # 応答生成
            def response_worker():
                try:
                    response = self.setsuna_chat.get_response(user_input)
                    
                    # 応答表示
                    chat_window.after(0, lambda: self._display_response(chat_display, response))
                    
                    # 音声再生
                    self.voice_output.speak(response)
                    
                    # 統計更新
                    self.conversation_count += 1
                    self.root.after(0, lambda: self.conversation_count_var.set(f"{self.conversation_count}回"))
                    
                except Exception as e:
                    error_msg = f"❌ 応答エラー: {e}"
                    chat_window.after(0, lambda: self._display_response(chat_display, error_msg))
            
            threading.Thread(target=response_worker, daemon=True).start()
        
        # イベントバインド
        send_button.config(command=send_message)
        input_entry.bind("<Return>", lambda e: send_message())
        
        # フォーカス設定
        input_entry.focus()
    
    def _display_response(self, chat_display, response):
        """チャット応答を表示"""
        chat_display.config(state=tk.NORMAL)
        chat_display.insert(tk.END, f"せつな: {response}\n\n")
        chat_display.config(state=tk.DISABLED)
        chat_display.see(tk.END)
    
    def _reset_settings(self):
        """設定リセット"""
        self.speed_var.set(1.2)
        self.pitch_var.set(0.0)
        self.intonation_var.set(1.0)
        
        if self.is_initialized:
            self._apply_voice_parameters()
        
        self._log("🔄 音声設定をリセットしました")
    
    def _log(self, message):
        """ログメッセージを追加"""
        timestamp = time.strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)
    
    def _on_closing(self):
        """ウィンドウ終了時の処理"""
        self._log("👋 せつなBot GUI を終了します")
        self.root.destroy()
    
    def run(self):
        """GUI実行"""
        self.root.mainloop()

# 使用例
if __name__ == "__main__":
    print("🤖 せつなBot ミニマルGUI起動中...")
    
    try:
        gui = SetsunaGUI()
        gui.run()
    except Exception as e:
        print(f"❌ GUI起動エラー: {e}")
        print("WSL2環境ではGUIが制限される場合があります")
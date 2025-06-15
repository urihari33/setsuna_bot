#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
せつなBot ミニマルGUI - WSL2対応版
文字エンコーディング問題対応
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

class SetsunaGUIFixed:
    def __init__(self):
        """せつなBot GUI初期化（WSL2対応版）"""
        # メインウィンドウ作成
        self.root = tk.Tk()
        
        # エンコーディング設定
        self.root.option_add('*font', 'TkDefaultFont')
        
        # ウィンドウ設定（ASCII文字のみでテスト）
        self.root.title("Setsuna Bot - Voice Chat System")
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
        """フォント設定（WSL2対応）"""
        try:
            # フォント候補（WSL2対応優先順）
            font_candidates = [
                "Yu Gothic",
                "Meiryo", 
                "DejaVu Sans",
                "Liberation Sans",
                "TkDefaultFont"
            ]
            
            selected_font = "TkDefaultFont"
            for font_name in font_candidates:
                try:
                    test_font = tkFont.Font(family=font_name, size=10)
                    selected_font = font_name
                    print(f"Selected font: {selected_font}")
                    break
                except:
                    continue
            
            fonts = {
                'default': (selected_font, 10),
                'title': (selected_font, 16, "bold"),
                'small': (selected_font, 8)
            }
            
            return fonts
            
        except Exception as e:
            print(f"Font setup error: {e}")
            return {
                'default': ("TkDefaultFont", 10),
                'title': ("TkDefaultFont", 16, "bold"),
                'small': ("TkDefaultFont", 8)
            }
    
    def _create_widgets(self):
        """GUI要素を作成（混合モード）"""
        # タイトルエリア（英語）
        title_frame = ttk.Frame(self.root)
        title_frame.pack(fill=tk.X, padx=10, pady=10)
        
        title_label = ttk.Label(
            title_frame, 
            text="Setsuna Bot",
            font=self.fonts['title']
        )
        title_label.pack()
        
        subtitle_label = ttk.Label(
            title_frame,
            text="Voice Dialogue System v2.0",
            font=self.fonts['default']
        )
        subtitle_label.pack()
        
        # 日本語テスト表示
        jp_test_frame = ttk.Frame(title_frame)
        jp_test_frame.pack(pady=5)
        
        # 日本語文字列を直接指定してテスト
        jp_texts = [
            "こんにちは、せつなです",
            "音声対話システム", 
            "システム状態",
            "音声設定"
        ]
        
        for i, jp_text in enumerate(jp_texts):
            try:
                jp_label = ttk.Label(
                    jp_test_frame,
                    text=jp_text,
                    font=self.fonts['default']
                )
                jp_label.grid(row=i//2, column=i%2, padx=5, pady=2)
                print(f"Japanese label created: {jp_text}")
            except Exception as e:
                print(f"Failed to create Japanese label: {jp_text} - {e}")
        
        # ステータスエリア（英語ラベル）
        status_frame = ttk.LabelFrame(self.root, text="Status")
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # システム状態
        self.system_status_var = tk.StringVar(value="Initializing...")
        ttk.Label(status_frame, text="System Status:", font=self.fonts['default']).grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.system_status_label = ttk.Label(status_frame, textvariable=self.system_status_var, font=self.fonts['default'])
        self.system_status_label.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        # 対話回数
        self.conversation_count_var = tk.StringVar(value="0 times")
        ttk.Label(status_frame, text="Conversations:", font=self.fonts['default']).grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        ttk.Label(status_frame, textvariable=self.conversation_count_var, font=self.fonts['default']).grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        # 音声パラメータエリア
        voice_frame = ttk.LabelFrame(self.root, text="Voice Settings")
        voice_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 話速スライダー
        ttk.Label(voice_frame, text="Speed:", font=self.fonts['default']).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.speed_var = tk.DoubleVar(value=1.2)
        self.speed_scale = ttk.Scale(
            voice_frame, 
            from_=0.5, to=2.0, 
            variable=self.speed_var,
            orient=tk.HORIZONTAL,
            command=self._on_voice_parameter_change
        )
        self.speed_scale.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        self.speed_value_label = ttk.Label(voice_frame, text="1.2x", font=self.fonts['default'])
        self.speed_value_label.grid(row=0, column=2, padx=5, pady=5)
        
        # 音程スライダー
        ttk.Label(voice_frame, text="Pitch:", font=self.fonts['default']).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.pitch_var = tk.DoubleVar(value=0.0)
        self.pitch_scale = ttk.Scale(
            voice_frame,
            from_=-0.15, to=0.15,
            variable=self.pitch_var,
            orient=tk.HORIZONTAL,
            command=self._on_voice_parameter_change
        )
        self.pitch_scale.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        self.pitch_value_label = ttk.Label(voice_frame, text="0.0", font=self.fonts['default'])
        self.pitch_value_label.grid(row=1, column=2, padx=5, pady=5)
        
        # 抑揚スライダー
        ttk.Label(voice_frame, text="Intonation:", font=self.fonts['default']).grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.intonation_var = tk.DoubleVar(value=1.0)
        self.intonation_scale = ttk.Scale(
            voice_frame,
            from_=0.5, to=2.0,
            variable=self.intonation_var,
            orient=tk.HORIZONTAL,
            command=self._on_voice_parameter_change
        )
        self.intonation_scale.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        self.intonation_value_label = ttk.Label(voice_frame, text="1.0", font=self.fonts['default'])
        self.intonation_value_label.grid(row=2, column=2, padx=5, pady=5)
        
        voice_frame.columnconfigure(1, weight=1)
        
        # 操作エリア
        control_frame = ttk.LabelFrame(self.root, text="Control Panel")
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # テスト再生ボタン
        self.test_button = ttk.Button(
            control_frame,
            text="Voice Test",
            command=self._test_voice,
            state=tk.DISABLED
        )
        self.test_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # 会話開始ボタン
        self.chat_button = ttk.Button(
            control_frame,
            text="Text Chat",
            command=self._start_text_chat,
            state=tk.DISABLED
        )
        self.chat_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # 設定リセットボタン
        self.reset_button = ttk.Button(
            control_frame,
            text="Reset Settings",
            command=self._reset_settings
        )
        self.reset_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        # ログエリア
        log_frame = ttk.LabelFrame(self.root, text="Log")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.log_text = tk.Text(log_frame, height=10, wrap=tk.WORD, font=self.fonts['default'])
        log_scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)
    
    def _setup_layout(self):
        """レイアウト設定"""
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        self._log("Setsuna Bot GUI starting...")
        self._log("System initialization in progress...")
    
    def _initialize_system(self):
        """システム初期化"""
        def init_worker():
            try:
                self._log("Initializing voice output system...")
                from voice_output import VoiceOutput
                self.voice_output = VoiceOutput()
                
                self._log("Initializing chat system...")
                from setsuna_chat import SetsunaChat
                self.setsuna_chat = SetsunaChat()
                
                self._log("Initializing voice input system...")
                try:
                    from voice_input import VoiceInput
                    self.voice_input = VoiceInput()
                except:
                    from voice_input_mock import VoiceInput
                    self.voice_input = VoiceInput()
                    self._log("Using mock voice input")
                
                self.root.after(0, self._on_initialization_complete)
                
            except Exception as e:
                error_msg = f"Initialization error: {e}"
                self._log(error_msg)
                self.root.after(0, lambda: self._on_initialization_error(str(e)))
        
        threading.Thread(target=init_worker, daemon=True).start()
    
    def _on_initialization_complete(self):
        """初期化完了処理"""
        self.is_initialized = True
        self.system_status_var.set("Ready")
        
        self.test_button.config(state=tk.NORMAL)
        self.chat_button.config(state=tk.NORMAL)
        
        self._log("Setsuna Bot initialization complete!")
        self._log("Voice parameters can be adjusted")
        self._log("Click Text Chat button to start conversation")
        
        self._apply_voice_parameters()
    
    def _on_initialization_error(self, error):
        """初期化エラー処理"""
        self.system_status_var.set("Initialization failed")
        messagebox.showerror("Initialization Error", f"System initialization failed:\n{error}")
    
    def _on_voice_parameter_change(self, value=None):
        """音声パラメータ変更処理"""
        self.speed_value_label.config(text=f"{self.speed_var.get():.1f}x")
        self.pitch_value_label.config(text=f"{self.pitch_var.get():.2f}")
        self.intonation_value_label.config(text=f"{self.intonation_var.get():.1f}")
        
        if self.is_initialized and self.voice_output:
            self._apply_voice_parameters()
    
    def _apply_voice_parameters(self):
        """音声パラメータ適用"""
        try:
            self.voice_output.update_settings(
                speed=self.speed_var.get(),
                pitch=self.pitch_var.get(),
                intonation=self.intonation_var.get()
            )
            self._log(f"Voice settings updated: Speed {self.speed_var.get():.1f}x, Pitch {self.pitch_var.get():.2f}, Intonation {self.intonation_var.get():.1f}")
        except Exception as e:
            self._log(f"Voice settings error: {e}")
    
    def _test_voice(self):
        """音声テスト"""
        if not self.is_initialized:
            return
        
        def test_worker():
            try:
                self.root.after(0, lambda: self.system_status_var.set("Voice testing"))
                self._log("Executing voice test...")
                
                test_text = "こんにちは、せつなです。音声設定のテストをしています。"
                self.voice_output.speak(test_text)
                
                self.root.after(0, lambda: self.system_status_var.set("Ready"))
                self._log("Voice test complete")
                
            except Exception as e:
                error_msg = f"Voice test error: {e}"
                self._log(error_msg)
                self.root.after(0, lambda: self.system_status_var.set("Error"))
        
        threading.Thread(target=test_worker, daemon=True).start()
    
    def _start_text_chat(self):
        """テキスト会話開始"""
        if not self.is_initialized:
            return
        
        self._open_text_chat_window()
    
    def _open_text_chat_window(self):
        """テキスト会話ウィンドウ"""
        chat_window = tk.Toplevel(self.root)
        chat_window.title("Text Chat with Setsuna")
        chat_window.geometry("600x400")
        
        # 会話表示
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
        
        send_button = ttk.Button(input_frame, text="Send")
        send_button.pack(side=tk.RIGHT)
        
        # 初期メッセージ（日本語テスト）
        initial_msg = "Setsuna: こんにちは！何かお話ししましょうか？\n\n"
        chat_display.insert(tk.END, initial_msg)
        chat_display.config(state=tk.DISABLED)
        
        def send_message():
            user_input = input_entry.get().strip()
            if not user_input:
                return
            
            chat_display.config(state=tk.NORMAL)
            chat_display.insert(tk.END, f"You: {user_input}\n")
            chat_display.config(state=tk.DISABLED)
            chat_display.see(tk.END)
            
            input_entry.delete(0, tk.END)
            
            def response_worker():
                try:
                    response = self.setsuna_chat.get_response(user_input)
                    
                    chat_window.after(0, lambda: self._display_response(chat_display, response))
                    self.voice_output.speak(response)
                    
                    self.conversation_count += 1
                    self.root.after(0, lambda: self.conversation_count_var.set(f"{self.conversation_count} times"))
                    
                except Exception as e:
                    error_msg = f"Response error: {e}"
                    chat_window.after(0, lambda: self._display_response(chat_display, error_msg))
            
            threading.Thread(target=response_worker, daemon=True).start()
        
        send_button.config(command=send_message)
        input_entry.bind("<Return>", lambda e: send_message())
        input_entry.focus()
    
    def _display_response(self, chat_display, response):
        """応答表示"""
        chat_display.config(state=tk.NORMAL)
        chat_display.insert(tk.END, f"Setsuna: {response}\n\n")
        chat_display.config(state=tk.DISABLED)
        chat_display.see(tk.END)
    
    def _reset_settings(self):
        """設定リセット"""
        self.speed_var.set(1.2)
        self.pitch_var.set(0.0)
        self.intonation_var.set(1.0)
        
        if self.is_initialized:
            self._apply_voice_parameters()
        
        self._log("Voice settings reset")
    
    def _log(self, message):
        """ログ表示"""
        timestamp = time.strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)
    
    def _on_closing(self):
        """終了処理"""
        self._log("Closing Setsuna Bot GUI")
        self.root.destroy()
    
    def run(self):
        """GUI実行"""
        self.root.mainloop()

if __name__ == "__main__":
    print("Setsuna Bot GUI (WSL2 Fixed) starting...")
    
    try:
        gui = SetsunaGUIFixed()
        gui.run()
    except Exception as e:
        print(f"GUI startup error: {e}")
        print("GUI may be limited in WSL2 environment")
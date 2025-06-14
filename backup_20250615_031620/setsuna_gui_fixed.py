#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setsuna Bot GUI - 文字化け・日本語入力・音声認識修正版
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import queue
import time
from datetime import datetime

# システム統合
try:
    from setsuna_bot import get_setsuna_response
    from voicevox_speaker import voice_settings, speak_with_voicevox
    from speech_input import get_voice_input
    from setsuna_logger import log_system
    IMPORTS_AVAILABLE = True
    print("✅ All modules imported successfully")
except ImportError as e:
    print(f"❌ Import error: {e}")
    IMPORTS_AVAILABLE = False
    
    def get_setsuna_response(text):
        return f"[エラー] システムが利用できません: {text}"
    
    def speak_with_voicevox(text):
        print(f"[音声] {text}")
    
    def get_voice_input():
        return ""
    
    def log_system(msg):
        print(f"[LOG] {msg}")
    
    voice_settings = {"speedScale": 1.0, "pitchScale": 0.0, "intonationScale": 1.0}

class SetsunaGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("せつなBot 音声対話システム")
        self.root.geometry("800x600")
        
        # 日本語フォント設定
        self.font_normal = ("Yu Gothic UI", 10)
        self.font_large = ("Yu Gothic UI", 12)
        self.font_title = ("Yu Gothic UI", 14, "bold")
        
        # 状態管理
        self.is_listening = False
        self.voice_processing = False
        
        self.setup_ui()
        self.setup_voice_controls()
        
    def setup_ui(self):
        """UIの基本構成"""
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # タイトル
        title_label = tk.Label(main_frame, text="せつなBot 音声対話システム", 
                              font=self.font_title, fg="darkblue")
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky=tk.W)
        
        # 左側: チャット表示
        chat_frame = ttk.LabelFrame(main_frame, text="会話履歴", padding="5")
        chat_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # チャット表示エリア
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame, 
            width=50, height=20,
            font=self.font_normal,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.chat_display.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # テキスト入力エリア
        input_frame = ttk.Frame(chat_frame)
        input_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        self.text_input = tk.Entry(input_frame, font=self.font_normal, width=40)
        self.text_input.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        self.text_input.bind('<Return>', self.on_text_submit)
        
        send_button = tk.Button(input_frame, text="送信", 
                               command=self.on_text_submit, font=self.font_normal)
        send_button.grid(row=0, column=1)
        
        # 右側: 音声設定とコントロール
        control_frame = ttk.LabelFrame(main_frame, text="音声設定", padding="5")
        control_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 音声パラメータ設定
        self.setup_voice_sliders(control_frame)
        
        # 音声入力ボタン
        voice_button = tk.Button(control_frame, text="🎤 音声入力", 
                                font=self.font_large, bg="lightgreen",
                                command=self.start_voice_input)
        voice_button.grid(row=4, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))
        
        # 状態表示
        self.status_label = tk.Label(control_frame, text="待機中", 
                                    font=self.font_normal, fg="green")
        self.status_label.grid(row=5, column=0, columnspan=2, pady=5)
        
        # ホットキー説明
        hotkey_label = tk.Label(control_frame, 
                               text="ホットキー: Ctrl+Shift+Alt",
                               font=self.font_normal, fg="blue")
        hotkey_label.grid(row=6, column=0, columnspan=2, pady=5)
        
        # グリッド設定
        main_frame.columnconfigure(0, weight=3)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        chat_frame.columnconfigure(0, weight=1)
        chat_frame.rowconfigure(0, weight=1)
        input_frame.columnconfigure(0, weight=1)
        
    def setup_voice_sliders(self, parent):
        """音声パラメータスライダーの設定"""
        # 話速
        speed_label = tk.Label(parent, text="話速:", font=self.font_normal)
        speed_label.grid(row=0, column=0, sticky=tk.W, pady=2)
        
        self.speed_var = tk.DoubleVar(value=voice_settings.get("speedScale", 1.0))
        speed_slider = tk.Scale(parent, from_=0.5, to=2.0, resolution=0.1,
                               orient=tk.HORIZONTAL, variable=self.speed_var,
                               command=self.update_voice_settings)
        speed_slider.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # 音程
        pitch_label = tk.Label(parent, text="音程:", font=self.font_normal)
        pitch_label.grid(row=1, column=0, sticky=tk.W, pady=2)
        
        self.pitch_var = tk.DoubleVar(value=voice_settings.get("pitchScale", 0.0))
        pitch_slider = tk.Scale(parent, from_=-0.15, to=0.15, resolution=0.05,
                               orient=tk.HORIZONTAL, variable=self.pitch_var,
                               command=self.update_voice_settings)
        pitch_slider.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # 抑揚
        intonation_label = tk.Label(parent, text="抑揚:", font=self.font_normal)
        intonation_label.grid(row=2, column=0, sticky=tk.W, pady=2)
        
        self.intonation_var = tk.DoubleVar(value=voice_settings.get("intonationScale", 1.0))
        intonation_slider = tk.Scale(parent, from_=0.0, to=2.0, resolution=0.1,
                                    orient=tk.HORIZONTAL, variable=self.intonation_var,
                                    command=self.update_voice_settings)
        intonation_slider.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=2)
        
        parent.columnconfigure(1, weight=1)
        
    def setup_voice_controls(self):
        """音声入力のホットキー設定"""
        # 簡単なホットキー監視
        self.root.bind('<Control-Shift-Alt_L>', self.hotkey_pressed)
        self.root.focus_set()  # フォーカス設定
        
    def update_voice_settings(self, value=None):
        """音声設定の更新"""
        if IMPORTS_AVAILABLE:
            voice_settings["speedScale"] = self.speed_var.get()
            voice_settings["pitchScale"] = self.pitch_var.get()
            voice_settings["intonationScale"] = self.intonation_var.get()
            print(f"[設定] 音声パラメータ更新: {voice_settings}")
    
    def add_message(self, speaker, content):
        """チャットにメッセージを追加"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        speaker_name = "あなた" if speaker == "user" else "せつな"
        
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.insert(tk.END, f"[{timestamp}] {speaker_name}: {content}\n\n")
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def update_status(self, status, color="black"):
        """ステータス表示の更新"""
        self.status_label.config(text=status, fg=color)
        self.root.update()
    
    def on_text_submit(self, event=None):
        """テキスト入力の処理"""
        user_input = self.text_input.get().strip()
        if not user_input:
            return
            
        self.text_input.delete(0, tk.END)
        self.add_message("user", user_input)
        
        # 別スレッドで応答処理
        threading.Thread(target=self.process_response, args=(user_input,), daemon=True).start()
    
    def process_response(self, user_input):
        """せつなの応答処理"""
        try:
            self.update_status("考え中...", "blue")
            
            # GPT応答取得
            response = get_setsuna_response(user_input)
            
            if response:
                self.add_message("setsuna", response)
                
                # 音声で応答
                self.update_status("音声合成中...", "orange")
                speak_with_voicevox(response)
                
            self.update_status("待機中", "green")
            
        except Exception as e:
            error_msg = f"エラーが発生しました: {e}"
            self.add_message("system", error_msg)
            self.update_status("エラー", "red")
            print(f"[エラー] 応答処理: {e}")
    
    def start_voice_input(self):
        """音声入力の開始"""
        if self.voice_processing:
            return
            
        threading.Thread(target=self.process_voice_input, daemon=True).start()
    
    def process_voice_input(self):
        """音声入力の処理"""
        if self.voice_processing:
            return
            
        self.voice_processing = True
        
        try:
            self.update_status("音声入力中...", "red")
            
            # 音声入力（タイムアウト短縮、エラー音声無効）
            user_input = get_voice_input(timeout=10, phrase_time_limit=10)
            
            if user_input and user_input.strip():
                self.add_message("user", f"[音声] {user_input}")
                self.process_response(user_input)
            else:
                # エラー音声を出さずに静かに待機状態に戻る
                self.update_status("待機中", "green")
                
        except Exception as e:
            print(f"[エラー] 音声入力: {e}")
            self.update_status("音声入力エラー", "red")
            
        finally:
            self.voice_processing = False
    
    def hotkey_pressed(self, event):
        """ホットキーが押された時の処理"""
        self.start_voice_input()
    
    def run(self):
        """GUIの実行"""
        try:
            self.add_message("system", "せつなBot が起動しました。テキストまたは音声で話しかけてください。")
            log_system("GUI起動完了")
            self.root.mainloop()
        except Exception as e:
            print(f"[エラー] GUI実行: {e}")

def main():
    """メイン関数"""
    print("=" * 50)
    print("🤖 Setsuna Bot GUI 起動中...")
    print("=" * 50)
    
    try:
        app = SetsunaGUI()
        app.run()
    except Exception as e:
        print(f"❌ GUI起動エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
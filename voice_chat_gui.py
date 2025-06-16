#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
統合音声・テキスト対話システム
Phase 1: GUI基本構造作成
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
from datetime import datetime
import speech_recognition as sr
from pynput import keyboard
from core.setsuna_chat import SetsunaChat
from voice_synthesizer import VoiceVoxSynthesizer

class SetsunaGUI:
    """せつなBot統合GUI"""
    
    def __init__(self):
        """GUI初期化"""
        self.root = tk.Tk()
        self.root.title("せつなBot - 統合音声・テキスト対話システム")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # 会話履歴（共有データ）
        self.conversation_history = []
        
        # GUI状態
        self.voice_status = "待機中"
        
        # システムコンポーネント初期化
        self.setsuna_chat = None
        self.voice_synthesizer = None
        self.voice_recognizer = None
        self.microphone = None
        
        # 音声ホットキー関連
        self.listening = False
        self.current_keys = set()
        self.required_keys = {keyboard.Key.ctrl_l, keyboard.Key.shift_l, keyboard.Key.alt_l}
        self.hotkey_listener = None
        
        self._create_widgets()
        self._setup_layout()
        self._initialize_systems()
        
        print("🎮 せつなBot GUI初期化完了")
    
    def _initialize_systems(self):
        """システムコンポーネント初期化"""
        print("🤖 システムコンポーネント初期化中...")
        
        # GPT-4チャットシステム初期化
        try:
            self.setsuna_chat = SetsunaChat()
            self.update_status("GPT-4チャットシステム: ✅")
        except Exception as e:
            self.update_status(f"GPT-4チャットシステム: ❌ {e}")
            print(f"⚠️ GPT-4初期化失敗: {e}")
        
        # 音声認識システム初期化
        try:
            self.voice_recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            
            # マイクロフォン事前調整
            with self.microphone as source:
                self.voice_recognizer.adjust_for_ambient_noise(source, duration=0.5)
            self.update_status("音声認識システム: ✅")
        except Exception as e:
            self.update_status(f"音声認識システム: ❌ {e}")
            print(f"⚠️ 音声認識初期化失敗: {e}")
        
        # 音声合成システム初期化
        try:
            self.voice_synthesizer = VoiceVoxSynthesizer()
            self.update_status("VOICEVOX音声合成: ✅")
        except Exception as e:
            self.update_status(f"VOICEVOX音声合成: ❌ {e}")
            print(f"⚠️ VOICEVOX初期化失敗: {e}")
        
        # 音声ホットキーリスナー開始
        self._start_hotkey_listener()
        
        print("✅ システムコンポーネント初期化完了")
    
    def _create_widgets(self):
        """ウィジェット作成"""
        
        # タイトルフレーム
        self.title_frame = ttk.Frame(self.root)
        self.title_label = ttk.Label(
            self.title_frame, 
            text="🤖 せつなBot - 音声・テキスト対話システム",
            font=('Arial', 16, 'bold')
        )
        
        # ステータスフレーム
        self.status_frame = ttk.Frame(self.root)
        self.voice_status_label = ttk.Label(
            self.status_frame,
            text="🎤 音声: 待機中",
            font=('Arial', 10)
        )
        self.hotkey_info_label = ttk.Label(
            self.status_frame,
            text="📌 Ctrl+Shift+Alt: 音声入力",
            font=('Arial', 10),
            foreground='blue'
        )
        
        # 会話履歴表示エリア
        self.history_frame = ttk.LabelFrame(self.root, text="会話履歴", padding=10)
        self.history_text = scrolledtext.ScrolledText(
            self.history_frame,
            wrap=tk.WORD,
            height=20,
            width=70,
            font=('Arial', 11),
            state=tk.DISABLED
        )
        
        # テキスト入力エリア
        self.input_frame = ttk.LabelFrame(self.root, text="テキスト入力", padding=10)
        
        # テキスト入力フィールド
        self.text_input = tk.Text(
            self.input_frame,
            height=3,
            width=60,
            font=('Arial', 11),
            wrap=tk.WORD
        )
        
        # 送信ボタン
        self.send_button = ttk.Button(
            self.input_frame,
            text="送信 📤",
            command=self.send_text_message
        )
        
        # クリアボタン
        self.clear_button = ttk.Button(
            self.input_frame,
            text="履歴クリア 🗑️",
            command=self.clear_history
        )
        
        # キャッシュ統計ボタン
        self.cache_stats_button = ttk.Button(
            self.input_frame,
            text="キャッシュ統計 📊",
            command=self.show_cache_stats
        )
    
    def _setup_layout(self):
        """レイアウト設定"""
        
        # タイトル
        self.title_frame.pack(fill=tk.X, padx=10, pady=5)
        self.title_label.pack()
        
        # ステータス
        self.status_frame.pack(fill=tk.X, padx=10, pady=5)
        self.voice_status_label.pack(side=tk.LEFT)
        self.hotkey_info_label.pack(side=tk.RIGHT)
        
        # 会話履歴
        self.history_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.history_text.pack(fill=tk.BOTH, expand=True)
        
        # テキスト入力
        self.input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 入力フィールドと送信ボタンを横並び
        input_container = ttk.Frame(self.input_frame)
        input_container.pack(fill=tk.X, pady=5)
        
        self.text_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        button_container = ttk.Frame(input_container)
        button_container.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.send_button.pack(pady=(0, 2))
        self.clear_button.pack(pady=(0, 2))
        self.cache_stats_button.pack()
        
        # Enterキーで送信
        self.text_input.bind('<Control-Return>', lambda event: self.send_text_message())
    
    def add_message_to_history(self, speaker, message, message_type="text"):
        """会話履歴にメッセージを追加"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # 履歴データに追加
        history_entry = {
            "timestamp": timestamp,
            "speaker": speaker,
            "message": message,
            "type": message_type
        }
        self.conversation_history.append(history_entry)
        
        # GUI表示更新
        self.history_text.config(state=tk.NORMAL)
        
        # 発言者によって色分け
        if speaker == "あなた":
            speaker_color = "blue"
            type_icon = "🗣️" if message_type == "voice" else "💬"
        else:  # せつな
            speaker_color = "green"
            type_icon = "🤖"
        
        # メッセージを追加
        self.history_text.insert(tk.END, f"[{timestamp}] {type_icon} {speaker}: ", (speaker_color,))
        self.history_text.insert(tk.END, f"{message}\n\n")
        
        # タグ設定
        self.history_text.tag_config(speaker_color, foreground=speaker_color, font=('Arial', 11, 'bold'))
        
        # 最下部にスクロール
        self.history_text.see(tk.END)
        self.history_text.config(state=tk.DISABLED)
    
    def send_text_message(self):
        """テキストメッセージ送信"""
        message = self.text_input.get("1.0", tk.END).strip()
        
        if not message:
            return
        
        # 入力フィールドをクリア
        self.text_input.delete("1.0", tk.END)
        
        # ユーザーメッセージを履歴に追加
        self.add_message_to_history("あなた", message, "text")
        
        # 別スレッドで応答生成（UIをブロックしないため）
        threading.Thread(target=self._process_text_message, args=(message,), daemon=True).start()
        
        print(f"📝 テキストメッセージ送信: {message}")
    
    def _process_text_message(self, message):
        """テキストメッセージ処理（別スレッド）"""
        try:
            self.update_voice_status("思考中...")
            
            # GPT-4応答生成
            if self.setsuna_chat:
                response = self.setsuna_chat.get_response(message)
            else:
                response = f"申し訳ありません。システムが初期化されていません。"
            
            # UIスレッドで履歴更新
            self.root.after(0, lambda: self.add_message_to_history("せつな", response, "text"))
            
            # 音声合成実行
            if self.voice_synthesizer:
                self.update_voice_status("音声合成中...")
                wav_path = self.voice_synthesizer.synthesize_voice(response)
                if wav_path:
                    self.voice_synthesizer.play_voice(wav_path)
                    print("✅ 音声出力完了")
                else:
                    print("❌ 音声合成失敗")
            
            self.update_voice_status("待機中")
            
        except Exception as e:
            error_msg = f"処理エラー: {e}"
            print(f"❌ {error_msg}")
            self.root.after(0, lambda: self.add_message_to_history("システム", error_msg, "error"))
            self.update_voice_status("エラー")
    
    def update_voice_status(self, status):
        """音声ステータス更新（スレッドセーフ）"""
        def _update():
            self.voice_status = status
            self.voice_status_label.config(text=f"🎤 音声: {status}")
            
            # ステータスによって色を変更
            if status in ["録音中", "エラー"]:
                self.voice_status_label.config(foreground="red")
            elif status in ["処理中", "思考中...", "音声合成中..."]:
                self.voice_status_label.config(foreground="orange")
            else:
                self.voice_status_label.config(foreground="black")
        
        # UIスレッドで実行
        self.root.after(0, _update)
    
    def update_status(self, message):
        """ステータスメッセージ更新"""
        print(f"📊 {message}")
        # 必要に応じてGUIに表示する場合は、ステータスバーを拡張
    
    def _start_hotkey_listener(self):
        """音声ホットキーリスナー開始"""
        try:
            self.hotkey_listener = keyboard.Listener(
                on_press=self._on_key_press,
                on_release=self._on_key_release
            )
            self.hotkey_listener.start()
            self.update_status("音声ホットキー: ✅ (Ctrl+Shift+Alt)")
        except Exception as e:
            self.update_status(f"音声ホットキー: ❌ {e}")
            print(f"⚠️ ホットキーリスナー開始失敗: {e}")
    
    def _on_key_press(self, key):
        """キー押下処理"""
        self.current_keys.add(key)
        
        if self.required_keys.issubset(self.current_keys) and not self.listening:
            self.listening = True
            self.update_voice_status("録音中")
            threading.Thread(target=self._handle_voice_input, daemon=True).start()
    
    def _on_key_release(self, key):
        """キー離上処理"""
        if key in self.current_keys:
            self.current_keys.remove(key)
        
        # メインキーが離されたら停止
        if key in self.required_keys:
            self.listening = False
    
    def _handle_voice_input(self):
        """音声入力処理"""
        if not self.listening:
            return
        
        try:
            print("🎤 音声入力開始")
            
            # 音声認識実行
            user_input = self._voice_recognition()
            
            if user_input and user_input not in ["音声が聞き取れませんでした", "音声認識サービスエラー", "録音に失敗しました"]:
                # UIスレッドで履歴更新
                self.root.after(0, lambda: self.add_message_to_history("あなた", user_input, "voice"))
                
                # 応答生成
                self._process_voice_message(user_input)
            else:
                # エラーメッセージを表示
                error_msg = "音声がよく聞こえませんでした。もう一度お話しください。"
                self.root.after(0, lambda: self.add_message_to_history("せつな", error_msg, "voice"))
            
        except Exception as e:
            error_msg = f"音声入力エラー: {e}"
            print(f"❌ {error_msg}")
            self.root.after(0, lambda: self.add_message_to_history("システム", error_msg, "error"))
        
        finally:
            self.update_voice_status("待機中")
            print("✅ 音声入力完了")
    
    def _voice_recognition(self):
        """音声認識実行"""
        if not self.voice_recognizer or not self.microphone:
            return "音声認識システムが初期化されていません"
        
        try:
            print("🎤 録音開始...")
            with self.microphone as source:
                print("🎤 話してください（15秒間）...")
                
                # 録音実行（15秒）
                audio = self.voice_recognizer.listen(source, timeout=15, phrase_time_limit=15)
                print("✅ 録音完了")
                
                # 音声認識実行
                print("🌐 音声認識中...")
                self.update_voice_status("音声認識中...")
                
                text = self.voice_recognizer.recognize_google(audio, language="ja-JP")
                print(f"✅ 認識成功: '{text}'")
                return text
                
        except sr.UnknownValueError:
            print("❌ 音声認識失敗（音声不明瞭）")
            return "音声が聞き取れませんでした"
        except sr.RequestError as e:
            print(f"❌ API呼び出しエラー: {e}")
            return "音声認識サービスエラー"
        except Exception as e:
            print(f"❌ 録音エラー: {e}")
            return "録音に失敗しました"
    
    def _process_voice_message(self, message):
        """音声メッセージ処理"""
        try:
            self.update_voice_status("思考中...")
            
            # GPT-4応答生成
            if self.setsuna_chat:
                response = self.setsuna_chat.get_response(message)
            else:
                response = "申し訳ありません。システムが初期化されていません。"
            
            # UIスレッドで履歴更新
            self.root.after(0, lambda: self.add_message_to_history("せつな", response, "voice"))
            
            # 音声合成実行
            if self.voice_synthesizer:
                self.update_voice_status("音声合成中...")
                wav_path = self.voice_synthesizer.synthesize_voice(response)
                if wav_path:
                    self.voice_synthesizer.play_voice(wav_path)
                    print("✅ 音声出力完了")
                else:
                    print("❌ 音声合成失敗")
            
        except Exception as e:
            error_msg = f"音声処理エラー: {e}"
            print(f"❌ {error_msg}")
            self.root.after(0, lambda: self.add_message_to_history("システム", error_msg, "error"))
    
    def add_voice_message(self, user_input, setsuna_response):
        """音声対話メッセージを履歴に追加"""
        self.add_message_to_history("あなた", user_input, "voice")
        self.add_message_to_history("せつな", setsuna_response, "voice")
    
    def clear_history(self):
        """会話履歴をクリア"""
        self.conversation_history.clear()
        self.history_text.config(state=tk.NORMAL)
        self.history_text.delete("1.0", tk.END)
        self.history_text.config(state=tk.DISABLED)
        print("🗑️ 会話履歴をクリアしました")
    
    def show_cache_stats(self):
        """キャッシュ統計情報を表示"""
        if self.setsuna_chat:
            stats = self.setsuna_chat.get_cache_stats()
            
            if "message" in stats:
                self.add_message_to_history("システム", stats["message"], "text")
            else:
                stats_message = f"""📊 キャッシュ統計情報:
• ヒット率: {stats.get('hit_rate', 0):.1%}
• 総リクエスト: {stats.get('total_requests', 0)}件
• キャッシュヒット: {stats.get('hits', 0)}件
• キャッシュミス: {stats.get('misses', 0)}件
• キャッシュサイズ: {stats.get('cache_size_current', 0)}件"""
                
                self.add_message_to_history("システム", stats_message, "text")
                print("📊 キャッシュ統計表示完了")
        else:
            self.add_message_to_history("システム", "チャットシステムが初期化されていません", "text")
    
    def run(self):
        """GUI実行"""
        print("🚀 GUI開始")
        
        # ウィンドウ閉じるときの処理
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self._on_closing()
    
    def _on_closing(self):
        """アプリケーション終了処理"""
        print("👋 アプリケーション終了中...")
        
        # キャッシュ保存
        if self.setsuna_chat:
            self.setsuna_chat.save_cache()
            print("✅ キャッシュ保存完了")
        
        # ホットキーリスナー停止
        if self.hotkey_listener:
            self.hotkey_listener.stop()
            print("✅ ホットキーリスナー停止")
        
        # GUI終了
        self.root.quit()
        self.root.destroy()
        print("✅ アプリケーション終了完了")

# テスト実行
if __name__ == "__main__":
    print("="*60)
    print("🎮 Phase 3: 完全統合システムテスト")
    print("="*60)
    
    gui = SetsunaGUI()
    
    # テスト用メッセージ（システム初期化後）
    def show_instructions():
        gui.add_message_to_history("システム", "🎉 統合音声・テキスト対話システム起動完了！", "text")
        gui.add_message_to_history("システム", "📝 テキスト入力: このフィールドで入力・送信", "text")
        gui.add_message_to_history("システム", "🎤 音声入力: Ctrl+Shift+Alt を押しながら話す", "text")
        gui.add_message_to_history("システム", "両方の入力が統合され、せつなが応答します！", "text")
    
    gui.root.after(2000, show_instructions)
    
    gui.run()
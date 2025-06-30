#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
統合音声・テキスト対話システム
Phase 1: GUI基本構造作成
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
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
        self.fast_mode_keys = {keyboard.Key.ctrl_l, keyboard.Key.shift_l}  # 高速モード用キー
        self.current_mode = "full_search"  # デフォルトは通常モード
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
            text="📌 Ctrl+Shift+Alt: 通常モード | Shift+Ctrl: 高速モード",
            font=('Arial', 10),
            foreground='blue'
        )
        
        # タブコントロール作成
        self.notebook = ttk.Notebook(self.root)
        
        # チャットタブ
        self.chat_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.chat_tab, text="💬 チャット")
        
        # 記憶編集タブ
        self.memory_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.memory_tab, text="🧠 記憶編集")
        
        # プロジェクトタブ
        self.project_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.project_tab, text="📽️ プロジェクト")
        
        # チャットタブのウィジェット作成
        self._create_chat_widgets()
        
        # 記憶編集タブのウィジェット作成
        self._create_memory_widgets()
        
        # プロジェクトタブのウィジェット作成
        self._create_project_widgets()
    
    def _create_chat_widgets(self):
        """チャットタブのウィジェット作成"""
        
        # 会話履歴表示エリア
        self.history_frame = ttk.LabelFrame(self.chat_tab, text="会話履歴", padding=10)
        self.history_text = scrolledtext.ScrolledText(
            self.history_frame,
            wrap=tk.WORD,
            height=12,  # 高さを小さくして入力欄が表示されるようにする
            width=70,
            font=('Arial', 10),  # フォントサイズを少し小さく
            state=tk.DISABLED,
            spacing1=2,  # 段落前の間隔
            spacing2=0,  # 行間隔
            spacing3=2   # 段落後の間隔
        )
        
        # モード選択エリア
        self.mode_frame = ttk.LabelFrame(self.chat_tab, text="応答モード選択", padding=10)
        
        # モード選択用変数
        self.response_mode = tk.StringVar(value="full_search")
        
        # ラジオボタン
        self.mode_normal_radio = ttk.Radiobutton(
            self.mode_frame,
            text="🔍 通常モード（YouTube検索あり）",
            variable=self.response_mode,
            value="full_search"
        )
        self.mode_fast_radio = ttk.Radiobutton(
            self.mode_frame,
            text="⚡ 高速モード（既存知識のみ）",
            variable=self.response_mode,
            value="fast_response"
        )
        
        # テキスト入力エリア（高さを固定）
        self.input_frame = ttk.LabelFrame(self.chat_tab, text="テキスト入力", padding=10)
        
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
    
    def _create_memory_widgets(self):
        """記憶編集タブのウィジェット作成"""
        
        # メインフレーム
        main_frame = ttk.Frame(self.memory_tab, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # タイトル
        title_label = ttk.Label(
            main_frame, 
            text="🧠 せつなが学習した事実（編集可能）",
            font=('Arial', 12, 'bold')
        )
        title_label.pack(pady=(0, 10))
        
        # 学習事実リストフレーム
        facts_frame = ttk.LabelFrame(main_frame, text="学習した事実", padding=10)
        facts_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # スクロール可能なリストボックス
        facts_container = ttk.Frame(facts_frame)
        facts_container.pack(fill=tk.BOTH, expand=True)
        
        # リストボックスとスクロールバー
        self.facts_listbox = tk.Listbox(
            facts_container,
            font=('Arial', 10),
            height=15,
            selectmode=tk.SINGLE
        )
        
        scrollbar = ttk.Scrollbar(facts_container, orient=tk.VERTICAL, command=self.facts_listbox.yview)
        self.facts_listbox.configure(yscrollcommand=scrollbar.set)
        
        self.facts_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 手動追加フレーム
        add_frame = ttk.LabelFrame(main_frame, text="手動で事実を追加", padding=10)
        add_frame.pack(fill=tk.X, pady=(0, 10))
        
        # カテゴリ選択
        category_frame = ttk.Frame(add_frame)
        category_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(category_frame, text="カテゴリ:").pack(side=tk.LEFT)
        self.category_var = tk.StringVar(value="名前")
        category_combo = ttk.Combobox(
            category_frame,
            textvariable=self.category_var,
            values=["名前", "趣味", "仕事", "年齢", "住んでいる", "好み", "特徴", "その他"],
            state="readonly",
            width=15
        )
        category_combo.pack(side=tk.LEFT, padx=(5, 0))
        
        # 内容入力
        content_frame = ttk.Frame(add_frame)
        content_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(content_frame, text="内容:").pack(side=tk.LEFT)
        self.content_entry = tk.Entry(
            content_frame,
            font=('Arial', 10),
            width=50
        )
        self.content_entry.pack(side=tk.LEFT, padx=(5, 0), fill=tk.X, expand=True)
        
        # 追加ボタン
        add_button = ttk.Button(
            content_frame,
            text="追加 ➕",
            command=self.add_manual_fact
        )
        add_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Enterキーで追加
        self.content_entry.bind('<Return>', lambda event: self.add_manual_fact())
        
        # ボタンフレーム
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 削除ボタン
        delete_button = ttk.Button(
            button_frame,
            text="選択した事実を削除 🗑️",
            command=self.delete_selected_fact
        )
        delete_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # セッション記憶クリアボタン
        clear_session_button = ttk.Button(
            button_frame,
            text="セッション記憶クリア 🔄",
            command=self.clear_session_memory_tab
        )
        clear_session_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # 全記憶クリアボタン
        clear_all_button = ttk.Button(
            button_frame,
            text="全記憶クリア ⚠️",
            command=self.clear_all_memory_tab
        )
        clear_all_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # 更新ボタン
        refresh_button = ttk.Button(
            button_frame,
            text="更新 🔄",
            command=self.refresh_facts_list
        )
        refresh_button.pack(side=tk.RIGHT)
        
        # 統計情報フレーム
        stats_frame = ttk.LabelFrame(main_frame, text="記憶統計", padding=10)
        stats_frame.pack(fill=tk.X)
        
        self.memory_stats_label = ttk.Label(stats_frame, text="統計情報読み込み中...")
        self.memory_stats_label.pack()
        
        # タブが切り替わった時に更新するためのバインド
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
    
    def _create_project_widgets(self):
        """プロジェクトタブのウィジェット作成"""
        
        # メインフレーム
        main_frame = ttk.Frame(self.project_tab, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # タイトル
        title_label = ttk.Label(
            main_frame, 
            text="📽️ 創作プロジェクト管理",
            font=('Arial', 12, 'bold')
        )
        title_label.pack(pady=(0, 10))
        
        # 上部フレーム（進行中プロジェクト + アイデア）
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 進行中プロジェクトフレーム
        projects_frame = ttk.LabelFrame(top_frame, text="進行中のプロジェクト", padding=10)
        projects_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # プロジェクトリストボックス
        self.projects_listbox = tk.Listbox(
            projects_frame,
            font=('Arial', 10),
            height=8,
            selectmode=tk.SINGLE
        )
        projects_scrollbar = ttk.Scrollbar(projects_frame, orient=tk.VERTICAL, command=self.projects_listbox.yview)
        self.projects_listbox.configure(yscrollcommand=projects_scrollbar.set)
        
        self.projects_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        projects_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # アイデアストックフレーム
        ideas_frame = ttk.LabelFrame(top_frame, text="アイデアストック", padding=10)
        ideas_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # アイデアリストボックス
        self.ideas_listbox = tk.Listbox(
            ideas_frame,
            font=('Arial', 10),
            height=8,
            selectmode=tk.SINGLE
        )
        ideas_scrollbar = ttk.Scrollbar(ideas_frame, orient=tk.VERTICAL, command=self.ideas_listbox.yview)
        self.ideas_listbox.configure(yscrollcommand=ideas_scrollbar.set)
        
        self.ideas_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ideas_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 新規作成フレーム
        create_frame = ttk.LabelFrame(main_frame, text="新規作成", padding=10)
        create_frame.pack(fill=tk.X, pady=(0, 10))
        
        # プロジェクト作成行
        project_create_frame = ttk.Frame(create_frame)
        project_create_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(project_create_frame, text="プロジェクト:").pack(side=tk.LEFT)
        self.project_title_entry = tk.Entry(project_create_frame, width=30)
        self.project_title_entry.pack(side=tk.LEFT, padx=(5, 5))
        
        ttk.Label(project_create_frame, text="種類:").pack(side=tk.LEFT)
        self.project_type_var = tk.StringVar(value="動画")
        project_type_combo = ttk.Combobox(
            project_create_frame,
            textvariable=self.project_type_var,
            values=["動画", "音楽", "イラスト", "脚本", "その他"],
            state="readonly",
            width=10
        )
        project_type_combo.pack(side=tk.LEFT, padx=(5, 5))
        
        create_project_button = ttk.Button(
            project_create_frame,
            text="プロジェクト作成 🎬",
            command=self.create_new_project
        )
        create_project_button.pack(side=tk.LEFT, padx=(5, 0))
        
        # アイデア作成行
        idea_create_frame = ttk.Frame(create_frame)
        idea_create_frame.pack(fill=tk.X)
        
        ttk.Label(idea_create_frame, text="アイデア:").pack(side=tk.LEFT)
        self.idea_content_entry = tk.Entry(idea_create_frame, width=40)
        self.idea_content_entry.pack(side=tk.LEFT, padx=(5, 5))
        
        ttk.Label(idea_create_frame, text="カテゴリ:").pack(side=tk.LEFT)
        self.idea_category_var = tk.StringVar(value="動画")
        idea_category_combo = ttk.Combobox(
            idea_create_frame,
            textvariable=self.idea_category_var,
            values=["動画", "音楽", "イラスト", "脚本", "その他"],
            state="readonly",
            width=10
        )
        idea_category_combo.pack(side=tk.LEFT, padx=(5, 5))
        
        create_idea_button = ttk.Button(
            idea_create_frame,
            text="アイデア追加 💡",
            command=self.create_new_idea
        )
        create_idea_button.pack(side=tk.LEFT, padx=(5, 0))
        
        # ボタンフレーム
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 削除ボタン
        delete_project_button = ttk.Button(
            button_frame,
            text="プロジェクト削除 🗑️",
            command=self.delete_selected_project
        )
        delete_project_button.pack(side=tk.LEFT, padx=(0, 5))
        
        delete_idea_button = ttk.Button(
            button_frame,
            text="アイデア削除 🗑️",
            command=self.delete_selected_idea
        )
        delete_idea_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # 更新ボタン
        refresh_projects_button = ttk.Button(
            button_frame,
            text="更新 🔄",
            command=self.refresh_projects_list
        )
        refresh_projects_button.pack(side=tk.RIGHT)
        
        # 統計情報フレーム
        project_stats_frame = ttk.LabelFrame(main_frame, text="プロジェクト統計", padding=10)
        project_stats_frame.pack(fill=tk.X)
        
        self.project_stats_label = ttk.Label(project_stats_frame, text="統計情報読み込み中...")
        self.project_stats_label.pack()
    
    def _setup_layout(self):
        """レイアウト設定"""
        
        # タイトル
        self.title_frame.pack(fill=tk.X, padx=10, pady=5)
        self.title_label.pack()
        
        # ステータス
        self.status_frame.pack(fill=tk.X, padx=10, pady=5)
        self.voice_status_label.pack(side=tk.LEFT)
        self.hotkey_info_label.pack(side=tk.RIGHT)
        
        # タブコントロール
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # チャットタブのレイアウト
        self._setup_chat_layout()
    
    def _setup_chat_layout(self):
        """チャットタブのレイアウト設定（モード選択対応）"""
        
        # モード選択エリア（上部に配置）
        self.mode_frame.pack(fill=tk.X, padx=5, pady=5, side=tk.TOP)
        self.mode_normal_radio.pack(side=tk.LEFT, padx=(0, 10))
        self.mode_fast_radio.pack(side=tk.LEFT)
        
        # テキスト入力エリア（下部固定）
        self.input_frame.pack(fill=tk.X, padx=5, pady=5, side=tk.BOTTOM)
        
        # テキスト入力フィールドを上部に配置（高さを固定）
        self.text_input.pack(fill=tk.X, pady=(0, 5), expand=False)
        
        # 会話履歴（残りのスペースを使用）
        self.history_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(5, 0))
        self.history_text.pack(fill=tk.BOTH, expand=True)
        
        # ボタンを横並びで下部に配置
        button_frame = ttk.Frame(self.input_frame)
        button_frame.pack(fill=tk.X)
        
        # 送信ボタンを button_frame に配置
        self.send_button = ttk.Button(
            button_frame,
            text="送信 📤",
            command=self.send_text_message
        )
        self.send_button.pack(side=tk.LEFT)
        
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
        
        # メッセージを追加（行間を詰める）
        self.history_text.insert(tk.END, f"[{timestamp}] {type_icon} {speaker}: ", (speaker_color,))
        self.history_text.insert(tk.END, f"{message}\n")
        
        # タグ設定
        self.history_text.tag_config(speaker_color, foreground=speaker_color, font=('Arial', 10, 'bold'))
        
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
            
            # GPT-4応答生成（モード選択対応）
            if self.setsuna_chat:
                # テキスト入力では選択されたモードを使用
                selected_mode = getattr(self, 'response_mode', 'full_search')
                response = self.setsuna_chat.get_response(message, mode=selected_mode)
                
                # Phase 1: URL表示機能 - テキスト入力時のURL表示（応答フィルター付き）
                try:
                    print(f"🔍 [URL表示デバッグ] テキスト入力処理開始")
                    print(f"🔍 [URL表示デバッグ] context_builder存在: {self.setsuna_chat.context_builder is not None}")
                    
                    from url_display_manager import show_recommended_urls
                    if self.setsuna_chat.context_builder and hasattr(self.setsuna_chat.context_builder, 'get_last_context'):
                        last_context = self.setsuna_chat.context_builder.get_last_context()
                        print(f"🔍 [URL表示デバッグ] last_context: {last_context is not None}")
                        if last_context:
                            videos = last_context.get('videos', [])
                            print(f"🔍 [URL表示デバッグ] 動画数: {len(videos)}")
                            if videos:
                                print(f"🔗 [URL表示] テキスト入力: {len(videos)}件の動画から応答言及分をフィルター中...")
                                # せつなの応答文を渡してフィルタリング
                                show_recommended_urls(last_context, response)
                            else:
                                print(f"⚠️ [URL表示] 動画推薦結果が空です")
                        else:
                            print(f"⚠️ [URL表示] last_contextがNullです")
                    else:
                        print(f"⚠️ [URL表示] context_builderまたはget_last_contextメソッドが存在しません")
                except ImportError as e:
                    print(f"⚠️ [URL表示] Import エラー: {e}")
                except Exception as e:
                    print(f"⚠️ [テキストURL表示] エラー: {e}")
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
        """キー押下処理（高速モード対応）"""
        self.current_keys.add(key)
        
        # 通常モード（Ctrl+Shift+Alt）
        if self.required_keys.issubset(self.current_keys) and not self.listening:
            self.listening = True
            self.current_mode = "full_search"
            self.update_voice_status("録音中（通常モード）")
            threading.Thread(target=self._handle_voice_input, daemon=True).start()
        
        # 高速モード（Shift+Ctrl）
        elif self.fast_mode_keys.issubset(self.current_keys) and keyboard.Key.alt_l not in self.current_keys and not self.listening:
            self.listening = True
            self.current_mode = "fast_response"
            self.update_voice_status("録音中（高速モード）")
            threading.Thread(target=self._handle_voice_input, daemon=True).start()
    
    def _on_key_release(self, key):
        """キー離上処理（高速モード対応）"""
        if key in self.current_keys:
            self.current_keys.remove(key)
        
        # メインキーが離されたら停止
        if (key in self.required_keys or key in self.fast_mode_keys):
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
            mode_display = "高速モード" if self.current_mode == "fast_response" else "通常モード"
            self.update_voice_status(f"思考中（{mode_display}）...")
            print(f"🤖 音声入力処理開始 - {mode_display}")
            
            # GPT-4応答生成（音声モード対応）
            if self.setsuna_chat:
                # 音声入力では current_mode を使用
                response = self.setsuna_chat.get_response(message, mode=self.current_mode)
                
                # Phase 1: URL表示機能 - 音声入力時のURL表示（応答フィルター付き）
                try:
                    print(f"🔍 [URL表示デバッグ] 音声入力処理開始")
                    print(f"🔍 [URL表示デバッグ] context_builder存在: {self.setsuna_chat.context_builder is not None}")
                    
                    from url_display_manager import show_recommended_urls
                    if self.setsuna_chat.context_builder and hasattr(self.setsuna_chat.context_builder, 'get_last_context'):
                        last_context = self.setsuna_chat.context_builder.get_last_context()
                        print(f"🔍 [URL表示デバッグ] last_context: {last_context is not None}")
                        if last_context:
                            videos = last_context.get('videos', [])
                            print(f"🔍 [URL表示デバッグ] 動画数: {len(videos)}")
                            if videos:
                                print(f"🔗 [URL表示] 音声入力: {len(videos)}件の動画から応答言及分をフィルター中...")
                                # せつなの応答文を渡してフィルタリング
                                show_recommended_urls(last_context, response)
                            else:
                                print(f"⚠️ [URL表示] 動画推薦結果が空です")
                        else:
                            print(f"⚠️ [URL表示] last_contextがNullです")
                    else:
                        print(f"⚠️ [URL表示] context_builderまたはget_last_contextメソッドが存在しません")
                except ImportError as e:
                    print(f"⚠️ [URL表示] Import エラー: {e}")
                except Exception as e:
                    print(f"⚠️ [音声URL表示] エラー: {e}")
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
                # システムメッセージは表示しない（ダイアログで表示）
                messagebox.showinfo("キャッシュ統計", stats["message"])
            else:
                stats_message = f"""📊 キャッシュ統計情報:
• ヒット率: {stats.get('hit_rate', 0):.1%}
• 総リクエスト: {stats.get('total_requests', 0)}件
• キャッシュヒット: {stats.get('hits', 0)}件
• キャッシュミス: {stats.get('misses', 0)}件
• キャッシュサイズ: {stats.get('cache_size_current', 0)}件"""
                
                # システムメッセージは表示しない（ダイアログで表示）
                messagebox.showinfo("キャッシュ統計", stats_message)
                print("📊 キャッシュ統計表示完了")
        else:
            # システムメッセージは表示しない（ダイアログで表示）
            messagebox.showerror("エラー", "チャットシステムが初期化されていません")
    
    def on_tab_changed(self, event):
        """タブ切り替え時の処理"""
        current_tab = self.notebook.tab(self.notebook.select(), "text")
        if current_tab == "🧠 記憶編集":
            # 記憶編集タブが選択されたら記憶リストを更新
            self.refresh_facts_list()
        elif current_tab == "📽️ プロジェクト":
            # プロジェクトタブが選択されたらプロジェクトリストを更新
            self.refresh_projects_list()
    
    def refresh_facts_list(self):
        """記憶事実リストを更新"""
        if not self.setsuna_chat:
            return
        
        try:
            # リストボックスをクリア
            self.facts_listbox.delete(0, tk.END)
            
            # 学習した事実を取得
            facts = self.setsuna_chat.get_learned_facts()
            
            for i, fact in enumerate(facts):
                # 表示用テキスト作成
                timestamp = fact.get('timestamp', '')[:10]  # 日付のみ
                category = fact.get('category', '不明')
                content = fact.get('content', '')[:50]  # 50文字まで
                confidence = fact.get('confidence', 0)
                
                display_text = f"[{timestamp}] {category}: {content}... (信頼度: {confidence:.1f})"
                self.facts_listbox.insert(tk.END, display_text)
            
            # 統計情報を更新
            stats = self.setsuna_chat.get_memory_stats()
            stats_text = f"""学習事実: {stats.get('learned_facts', 0)}件
セッション会話: {stats.get('session_conversations', 0)}件
会話セッション: {stats.get('conversation_sessions', 0)}回
関係レベル: {stats.get('relationship_level', 1)}"""
            
            if hasattr(self, 'memory_stats_label'):
                self.memory_stats_label.config(text=stats_text)
            
            print(f"🔄 記憶リスト更新: {len(facts)}件の事実")
        except Exception as e:
            print(f"❌ 記憶リスト更新エラー: {e}")
    
    def delete_selected_fact(self):
        """選択された事実を削除"""
        selection = self.facts_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "削除する事実を選択してください")
            return
        
        fact_index = selection[0]
        facts = self.setsuna_chat.get_learned_facts()
        
        if fact_index < len(facts):
            fact = facts[fact_index]
            content = fact.get('content', '')[:50]
            
            # 確認ダイアログ
            result = messagebox.askyesno(
                "確認", 
                f"以下の事実を削除しますか？\n\n{content}..."
            )
            
            if result:
                success = self.setsuna_chat.delete_memory_fact(fact_index)
                if success:
                    self.refresh_facts_list()
                    # システムメッセージは表示しない（コンソールログのみ）
                    print(f"✅ 記憶削除成功: {content}...")
                else:
                    messagebox.showerror("エラー", "記憶の削除に失敗しました")
    
    def clear_session_memory_tab(self):
        """セッション記憶をクリア（タブ用）"""
        result = messagebox.askyesno(
            "確認", 
            "今回のセッションでの会話記憶をクリアします。\n（学習した事実は残ります）\n\nよろしいですか？"
        )
        
        if result:
            self.setsuna_chat.clear_session_memory()
            self.refresh_facts_list()
            # システムメッセージは表示しない（コンソールログのみ）
            print("✅ セッション記憶クリア完了")
    
    def clear_all_memory_tab(self):
        """全記憶をクリア（タブ用）"""
        result = messagebox.askyesno(
            "⚠️ 警告", 
            "せつなの全ての記憶（学習した事実・セッション記憶）を削除します。\n\nこの操作は取り消せません。本当によろしいですか？"
        )
        
        if result:
            # 二重確認
            result2 = messagebox.askyesno(
                "⚠️ 最終確認", 
                "本当に全ての記憶を削除しますか？\n\nせつながあなたについて学んだことが全て失われます。"
            )
            
            if result2:
                self.setsuna_chat.clear_all_memory()
                self.refresh_facts_list()
                # システムメッセージは表示しない（コンソールログのみ）
                print("✅ 全記憶クリア完了")
    
    def add_manual_fact(self):
        """手動で事実を追加"""
        if not self.setsuna_chat:
            messagebox.showerror("エラー", "チャットシステムが初期化されていません")
            return
        
        category = self.category_var.get()
        content = self.content_entry.get().strip()
        
        if not content:
            messagebox.showwarning("警告", "内容を入力してください")
            self.content_entry.focus()
            return
        
        # 手動追加実行
        success = self.setsuna_chat.add_manual_memory(category, content)
        
        if success:
            # 成功時の処理
            self.content_entry.delete(0, tk.END)  # 入力フィールドをクリア
            self.refresh_facts_list()  # リストを更新
            # システムメッセージは表示しない（コンソールログのみ）
            print(f"✅ 手動記憶追加成功: {category} - {content}")
        else:
            # 失敗時（重複など）
            messagebox.showinfo("情報", f"この事実は既に記憶されています：\n{content}")
            print(f"⚠️ 重複する記憶: {category} - {content}")
    
    # プロジェクト管理機能
    def refresh_projects_list(self):
        """プロジェクトリストを更新"""
        if not self.setsuna_chat:
            return
        
        try:
            # プロジェクトリストをクリア
            self.projects_listbox.delete(0, tk.END)
            self.ideas_listbox.delete(0, tk.END)
            
            # 進行中プロジェクトを取得・表示
            active_projects = self.setsuna_chat.get_active_projects()
            for project in active_projects:
                status = project.get('status', '未設定')
                progress = project.get('progress', 0)
                next_step = project.get('next_steps', ['未設定'])[0] if project.get('next_steps') else '未設定'
                
                display_text = f"{project['title']} ({project['type']}) - {status} {progress}%"
                self.projects_listbox.insert(tk.END, display_text)
            
            # アイデアストックを取得・表示
            idea_stock = self.setsuna_chat.get_idea_stock()
            for idea in idea_stock:
                category = idea.get('category', '未設定')
                content = idea.get('content', '')[:40]
                
                display_text = f"[{category}] {content}..."
                self.ideas_listbox.insert(tk.END, display_text)
            
            # 統計情報を更新
            stats = self.setsuna_chat.get_project_stats()
            stats_text = f"""進行中: {stats.get('active_projects', 0)}件
アイデア: {stats.get('idea_stock', 0)}件
完了済み: {stats.get('completed_projects', 0)}件
総プロジェクト: {stats.get('total_projects', 0)}件"""
            
            if hasattr(self, 'project_stats_label'):
                self.project_stats_label.config(text=stats_text)
            
            print(f"🔄 プロジェクトリスト更新: 進行中{len(active_projects)}件, アイデア{len(idea_stock)}件")
            
        except Exception as e:
            print(f"❌ プロジェクトリスト更新エラー: {e}")
    
    def create_new_project(self):
        """新しいプロジェクトを作成"""
        title = self.project_title_entry.get().strip()
        project_type = self.project_type_var.get()
        
        if not title:
            messagebox.showwarning("警告", "プロジェクト名を入力してください")
            self.project_title_entry.focus()
            return
        
        # プロジェクト作成
        project = self.setsuna_chat.create_project(title, "", None, project_type)
        
        if project:
            self.project_title_entry.delete(0, tk.END)
            self.refresh_projects_list()
            # システムメッセージは表示しない（コンソールログのみ）
            print(f"✅ プロジェクト作成成功: {title}")
        else:
            messagebox.showerror("エラー", "プロジェクトの作成に失敗しました")
    
    def create_new_idea(self):
        """新しいアイデアを追加"""
        content = self.idea_content_entry.get().strip()
        category = self.idea_category_var.get()
        
        if not content:
            messagebox.showwarning("警告", "アイデア内容を入力してください")
            self.idea_content_entry.focus()
            return
        
        # アイデア追加
        success = self.setsuna_chat.add_idea(content, category, "手動追加")
        
        if success:
            self.idea_content_entry.delete(0, tk.END)
            self.refresh_projects_list()
            # システムメッセージは表示しない（コンソールログのみ）
            print(f"✅ アイデア追加成功: {content}")
        else:
            messagebox.showerror("エラー", "アイデアの追加に失敗しました")
    
    def delete_selected_project(self):
        """選択されたプロジェクトを削除"""
        selection = self.projects_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "削除するプロジェクトを選択してください")
            return
        
        project_index = selection[0]
        active_projects = self.setsuna_chat.get_active_projects()
        
        if project_index < len(active_projects):
            project = active_projects[project_index]
            
            # 確認ダイアログ
            result = messagebox.askyesno(
                "確認", 
                f"以下のプロジェクトを削除しますか？\n\n{project['title']} ({project['type']})"
            )
            
            if result:
                success = self.setsuna_chat.delete_project(project['id'])
                if success:
                    self.refresh_projects_list()
                    # システムメッセージは表示しない（コンソールログのみ）
                    print(f"✅ プロジェクト削除成功: {project['title']}")
                else:
                    messagebox.showerror("エラー", "プロジェクトの削除に失敗しました")
    
    def delete_selected_idea(self):
        """選択されたアイデアを削除"""
        selection = self.ideas_listbox.curselection()
        if not selection:
            messagebox.showwarning("警告", "削除するアイデアを選択してください")
            return
        
        idea_index = selection[0]
        idea_stock = self.setsuna_chat.get_idea_stock()
        
        if idea_index < len(idea_stock):
            idea = idea_stock[idea_index]
            content = idea.get('content', '')[:50]
            
            # 確認ダイアログ
            result = messagebox.askyesno(
                "確認", 
                f"以下のアイデアを削除しますか？\n\n{content}..."
            )
            
            if result:
                success = self.setsuna_chat.delete_idea(idea['id'])
                if success:
                    self.refresh_projects_list()
                    # システムメッセージは表示しない（コンソールログのみ）
                    print(f"✅ アイデア削除成功: {content}...")
                else:
                    messagebox.showerror("エラー", "アイデアの削除に失敗しました")
    
    
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
        
        # 全データ保存
        if self.setsuna_chat:
            self.setsuna_chat.save_all_data()
            print("✅ 全データ保存完了")
        
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
    
    # システム起動完了（システムメッセージは表示しない）
    print("🎉 統合音声・テキスト対話システム起動完了！")
    print("📝 テキスト入力: テキストフィールドで入力・送信")
    print("🎤 音声入力: Ctrl+Shift+Alt を押しながら話す")
    
    gui.run()
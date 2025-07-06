#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
統合音声・テキスト対話システム
Phase 1: GUI基本構造作成
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import time
import re
import webbrowser
import os
import uuid
import tempfile
from pathlib import Path
from datetime import datetime
import speech_recognition as sr
from pynput import keyboard
from PIL import Image, ImageTk
from core.setsuna_chat import SetsunaChat
from voice_synthesizer import VoiceVoxSynthesizer
from speech_text_converter import SpeechTextConverter
from core.image_manager import VideoImageManager
from core.video_image_context import VideoImageContextBuilder
from core.youtube_knowledge_manager import YouTubeKnowledgeManager
from core.rich_message_renderer import RichMessageRenderer
from core.progress_manager import ProgressManager
from core.progress_widget import ProgressWidget, DetailProgressDialog
from logging_system import get_logger, get_monitor

class SetsunaGUI:
    """せつなBot統合GUI"""
    
    def __init__(self):
        """GUI初期化"""
        # ログシステム初期化
        self.logger = get_logger()
        self.monitor = get_monitor()
        
        try:
            self.logger.info("voice_chat_gui", "__init__", "GUI初期化開始")
            print("🚀 GUI初期化開始...")
            self.root = tk.Tk()
            self.root.title("せつなBot - 統合音声・テキスト対話システム")
            self.root.geometry("800x600")
            self.root.configure(bg='#f0f0f0')
            print("✅ tkinterウィンドウ作成完了")
        except Exception as e:
            print(f"❌ GUI初期化エラー: {e}")
            raise
        
        # 会話履歴（共有データ）
        self.conversation_history = []
        
        # GUI状態
        self.voice_status = "待機中"
        
        # URL表示用データ
        self.current_video_urls = []  # 現在表示中の動画URLリスト
        
        # システムコンポーネント初期化
        self.setsuna_chat = None
        self.voice_synthesizer = None
        self.voice_recognizer = None
        self.microphone = None
        self.speech_text_converter = None
        
        # Phase 2B: 新システムコンポーネント
        self.youtube_manager = None
        self.context_builder = None
        self.image_manager = None
        
        # 音声ホットキー関連
        self.listening = False
        self.current_keys = set()
        self.required_keys = {keyboard.Key.ctrl_l, keyboard.Key.shift_l, keyboard.Key.alt_l}
        self.fast_mode_keys = {keyboard.Key.ctrl_l, keyboard.Key.shift_l}  # 高速モード用キー
        self.current_mode = "full_search"  # デフォルトは通常モード
        self.hotkey_listener = None
        
        # Phase 2C-4: プログレス管理システム
        self.progress_manager = None
        self.progress_widget = None
        
        self._create_widgets()
        self._setup_layout()
        self._initialize_systems()
        
        # URL表示エリアは初期状態では非表示（動画推薦時に動的表示）
        print("🔧 GUI初期化: URL表示システム準備完了")
        
        print("🎮 せつなBot GUI初期化完了")
    
    def _create_image_analysis_widgets(self, parent_frame):
        """
        Phase 2B: 画像分析ウィジェット作成
        動画学習タブに画像分析機能を追加
        """
        
        # 画像分析フレーム
        analysis_frame = ttk.LabelFrame(parent_frame, text="🤖 AI画像分析 (Phase 2B)", padding=15)
        analysis_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 説明ラベル
        desc_label = ttk.Label(
            analysis_frame,
            text="アップロードした画像をOpenAI Vision APIで分析し、動画との関連性を理解します",
            font=('Arial', 9),
            foreground='gray'
        )
        desc_label.pack(pady=(0, 10))
        
        # ボタンエリア
        button_frame = ttk.Frame(analysis_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 分析実行ボタン
        self.analyze_button = ttk.Button(
            button_frame,
            text="🔍 画像分析開始",
            command=self.start_image_analysis,
            style="Accent.TButton",
            state="disabled"  # 初期状態では無効
        )
        self.analyze_button.pack(side=tk.LEFT)
        
        # コンテキスト生成ボタン
        self.generate_context_button = ttk.Button(
            button_frame,
            text="💬 会話コンテキスト生成",
            command=self.generate_conversation_context,
            state="disabled"
        )
        self.generate_context_button.pack(side=tk.LEFT, padx=(10, 0))
        
        # テンプレート選択
        template_frame = ttk.Frame(button_frame)
        template_frame.pack(side=tk.LEFT, padx=(20, 0))
        
        ttk.Label(template_frame, text="テンプレート:", font=('Arial', 9)).pack(side=tk.LEFT)
        
        self.template_var = tk.StringVar(value="general_video_discussion")
        self.template_combo = ttk.Combobox(
            template_frame,
            textvariable=self.template_var,
            values=[
                "general_video_discussion",
                "music_video_comprehensive", 
                "visual_analysis",
                "specific_image_focus",
                "simple_image_chat"
            ],
            state="readonly",
            width=20
        )
        self.template_combo.pack(side=tk.LEFT, padx=(5, 0))
        
        # 分析状態表示
        self.analysis_status_label = ttk.Label(
            button_frame,
            text="待機中...",
            font=('Arial', 9),
            foreground='blue'
        )
        self.analysis_status_label.pack(side=tk.RIGHT)
        
        # 分析結果表示エリア
        result_notebook = ttk.Notebook(analysis_frame)
        result_notebook.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # タブ1: 基本分析結果
        self.basic_analysis_frame = ttk.Frame(result_notebook)
        result_notebook.add(self.basic_analysis_frame, text="📊 基本分析")
        
        self.basic_analysis_text = scrolledtext.ScrolledText(
            self.basic_analysis_frame,
            wrap=tk.WORD,
            height=6,
            width=70,
            font=('Arial', 9),
            state=tk.DISABLED
        )
        self.basic_analysis_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # タブ2: 高度な関連性分析
        self.advanced_analysis_frame = ttk.Frame(result_notebook)
        result_notebook.add(self.advanced_analysis_frame, text="🎆 高度な関連性")
        
        self.advanced_analysis_text = scrolledtext.ScrolledText(
            self.advanced_analysis_frame,
            wrap=tk.WORD,
            height=6,
            width=70,
            font=('Arial', 9),
            state=tk.DISABLED
        )
        self.advanced_analysis_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # タブ3: 会話コンテキスト
        self.context_frame = ttk.Frame(result_notebook)
        result_notebook.add(self.context_frame, text="💬 会話コンテキスト")
        
        self.context_text = scrolledtext.ScrolledText(
            self.context_frame,
            wrap=tk.WORD,
            height=6,
            width=70,
            font=('Arial', 9),
            state=tk.DISABLED
        )
        self.context_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # コンテキストコピーボタン
        copy_frame = ttk.Frame(self.context_frame)
        copy_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        
        copy_button = ttk.Button(
            copy_frame,
            text="📎 コンテキストをコピー",
            command=self.copy_context_to_clipboard
        )
        copy_button.pack(side=tk.LEFT)
        
        use_button = ttk.Button(
            copy_frame,
            text="💬 チャットで使用",
            command=self.use_context_in_chat
        )
        use_button.pack(side=tk.LEFT, padx=(10, 0))
        
        print("✅ Phase 2B: 画像分析ウィジェット作成完了")
    
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
        
        # Phase 2B: YouTube知識マネージャー初期化
        try:
            self.youtube_manager = YouTubeKnowledgeManager()
            self.context_builder = VideoImageContextBuilder(self.youtube_manager)
            self.update_status("Phase 2B システム: ✅")
            print("✅ Phase 2B システム初期化成功")
        except Exception as e:
            self.update_status(f"Phase 2B システム: ❌ {e}")
            print(f"⚠️ Phase 2B初期化失敗: {e}")
        
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
        
        # 画像管理システム初期化
        try:
            self.image_manager = VideoImageManager()
            self.update_status("画像管理システム: ✅")
        except Exception as e:
            self.update_status(f"画像管理システム: ❌ {e}")
            print(f"⚠️ 画像管理システム初期化失敗: {e}")
        
        # 画像関連の状態変数
        self.selected_images = []  # アップロード予定の画像リスト
        self.current_video_id = None  # 現在処理中の動画ID
        
        # 音声合成用テキスト変換システム初期化
        try:
            self.speech_text_converter = SpeechTextConverter()
            # YouTube知識管理システムとの連携
            if self.setsuna_chat and self.setsuna_chat.context_builder:
                self.speech_text_converter.set_knowledge_manager(
                    self.setsuna_chat.context_builder.knowledge_manager
                )
            self.update_status("音声テキスト変換: ✅")
        except Exception as e:
            self.update_status(f"音声テキスト変換: ❌ {e}")
            print(f"⚠️ 音声テキスト変換初期化失敗: {e}")
        
        # 音声ホットキーリスナー開始
        self._start_hotkey_listener()
        
        # Phase 2C-2: リッチメッセージ表示システム初期化
        try:
            self.rich_renderer = None  # 後で履歴テキストウィジェット作成後に初期化
            self.update_status("Phase 2C-2 システム: 準備完了")
            print("✅ Phase 2C-2 リッチメッセージシステム準備完了")
        except Exception as e:
            self.update_status(f"Phase 2C-2 システム: ❌ {e}")
            print(f"⚠️ Phase 2C-2初期化失敗: {e}")
        
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
        
        # 動画学習タブ
        self.video_learning_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.video_learning_tab, text="🎵 動画学習")
        
        # チャットタブのウィジェット作成
        self._create_chat_widgets()
        
        # 記憶編集タブのウィジェット作成
        self._create_memory_widgets()
        
        # プロジェクトタブのウィジェット作成
        self._create_project_widgets()
        
        # 動画学習タブのウィジェット作成
        self._create_video_learning_widgets()
    
    def _create_chat_widgets(self):
        """チャットタブのウィジェット作成"""
        
        # 会話履歴表示エリア - さらにコンパクトに
        self.history_frame = ttk.LabelFrame(self.chat_tab, text="会話履歴", padding=5)
        self.history_text = scrolledtext.ScrolledText(
            self.history_frame,
            wrap=tk.WORD,
            height=10,  # 12から10に変更
            width=70,
            font=('Arial', 9),  # フォントサイズをさらに小さく
            state=tk.DISABLED,
            spacing1=1,  # 段落前の間隔を縮小
            spacing2=0,  # 行間隔
            spacing3=1   # 段落後の間隔を縮小
        )
        
        # モード選択エリア - paddingを縮小
        self.mode_frame = ttk.LabelFrame(self.chat_tab, text="応答モード選択", padding=5)
        
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
        
        # Phase 2C-1: 統合チャット入力エリア（画像・URL対応）
        self.input_frame = ttk.LabelFrame(self.chat_tab, text="💬 統合チャット入力", padding=5)
        
        # 添付ファイル管理
        self.attached_files = []  # 添付ファイルリスト
        self.current_url = None   # 現在入力されたURL
        
        # 上部: 添付ボタンエリア
        self.attachment_frame = ttk.Frame(self.input_frame)
        
        # 画像添付ボタン
        self.image_attach_button = ttk.Button(
            self.attachment_frame,
            text="📸 画像",
            command=self.attach_image,
            width=8
        )
        
        # URL入力ボタン
        self.url_attach_button = ttk.Button(
            self.attachment_frame,
            text="🔗 URL",
            command=self.attach_url,
            width=8
        )
        
        # クリアボタン
        self.clear_attachments_button = ttk.Button(
            self.attachment_frame,
            text="🗑️ クリア",
            command=self.clear_attachments,
            width=8
        )
        
        # 中部: 添付プレビューエリア（シンプルフレーム）
        self.preview_frame = ttk.LabelFrame(self.input_frame, text="📋 添付プレビュー", padding=3)
        self.preview_text = tk.Text(
            self.preview_frame,
            height=1,
            width=60,
            font=('Arial', 8),
            bg='#f8f8f8',
            fg='#666666',
            state=tk.DISABLED,
            wrap=tk.WORD
        )
        # プレビューテキストをフレーム内に配置
        self.preview_text.pack(fill=tk.X, expand=True)
        
        # 下部: テキスト入力エリア
        self.text_input_frame = ttk.Frame(self.input_frame)
        
        # テキスト入力フィールド
        self.text_input = tk.Text(
            self.text_input_frame,
            height=2,
            width=60,
            font=('Arial', 10),
            wrap=tk.WORD
        )
        
        # ドラッグ&ドロップ対応（将来実装予定）
        # self.text_input.drop_target_register(self._on_drop)  # tkinterdnd2使用時
        
        # 送信ボタン
        self.send_button = ttk.Button(
            self.text_input_frame,
            text="📤 送信",
            command=self.send_integrated_message
        )
        
        # URL表示エリア（動的表示）- 高さを小さく調整
        self.url_frame = ttk.LabelFrame(self.chat_tab, text="🔗 推薦動画リンク", padding=5)
        self.url_listbox = tk.Listbox(
            self.url_frame,
            height=2,  # 4行から2行に変更
            font=('Arial', 9),  # フォントサイズを小さく
            selectmode=tk.SINGLE,
            activestyle='dotbox'
        )
        # スクロールバー追加
        self.url_scrollbar = ttk.Scrollbar(self.url_frame, orient=tk.VERTICAL, command=self.url_listbox.yview)
        self.url_listbox.configure(yscrollcommand=self.url_scrollbar.set)
        
        # ダブルクリックでURL開く
        self.url_listbox.bind('<Double-Button-1>', self.on_url_double_click)
        
        # 右クリックメニューを追加
        self.url_listbox.bind('<Button-3>', self.show_context_menu)  # 右クリック
        
        # URL表示エリアは後でレイアウト設定時に表示
        # （初期化時は非表示のまま）
        print("🔧 URL表示エリア: ウィジェット作成完了（レイアウトは後で設定）")
    
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
    
    def _create_video_learning_widgets(self):
        """動画学習タブのウィジェット作成"""
        
        # メインフレーム
        main_frame = ttk.Frame(self.video_learning_tab, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # タイトル
        title_label = ttk.Label(
            main_frame, 
            text="🎵 YouTube動画学習システム",
            font=('Arial', 14, 'bold')
        )
        title_label.pack(pady=(0, 15))
        
        # 説明テキスト
        description_label = ttk.Label(
            main_frame,
            text="YouTubeのURLを入力して、せつなに新しい動画を覚えさせることができます",
            font=('Arial', 10),
            foreground='gray'
        )
        description_label.pack(pady=(0, 20))
        
        # URL入力フレーム
        url_frame = ttk.LabelFrame(main_frame, text="📎 YouTube URL入力", padding=15)
        url_frame.pack(fill=tk.X, pady=(0, 15))
        
        # URL入力エリア
        url_input_frame = ttk.Frame(url_frame)
        url_input_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(url_input_frame, text="URL:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=(0, 5))
        
        self.url_entry = ttk.Entry(
            url_input_frame,
            font=('Arial', 11),
            width=50
        )
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # 学習開始ボタン
        self.learn_button = ttk.Button(
            url_input_frame,
            text="🧠 学習開始",
            command=self.start_video_learning,
            style="Accent.TButton"
        )
        self.learn_button.pack(side=tk.RIGHT)
        
        # URLの例を表示
        example_frame = ttk.Frame(url_frame)
        example_frame.pack(fill=tk.X)
        
        ttk.Label(example_frame, text="例:", font=('Arial', 9), foreground='gray').pack(side=tk.LEFT)
        ttk.Label(
            example_frame, 
            text="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            font=('Arial', 9),
            foreground='blue'
        ).pack(side=tk.LEFT, padx=(5, 0))
        
        # 画像アップロードフレーム
        self._create_image_upload_widgets(main_frame)
        
        # プログレスフレーム
        progress_frame = ttk.LabelFrame(main_frame, text="📊 学習進捗", padding=15)
        progress_frame.pack(fill=tk.X, pady=(0, 15))
        
        # プログレスバー
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100,
            mode='determinate',
            length=400
        )
        self.progress_bar.pack(fill=tk.X, pady=(0, 5))
        
        # ステータステキスト
        self.progress_status = ttk.Label(
            progress_frame,
            text="待機中...",
            font=('Arial', 10)
        )
        self.progress_status.pack()
        
        # 結果表示フレーム
        result_frame = ttk.LabelFrame(main_frame, text="📋 学習結果", padding=15)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # 結果表示エリア
        self.result_text = scrolledtext.ScrolledText(
            result_frame,
            wrap=tk.WORD,
            height=8,
            width=70,
            font=('Arial', 10),
            state=tk.DISABLED
        )
        self.result_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # ボタンフレーム
        button_frame = ttk.Frame(result_frame)
        button_frame.pack(fill=tk.X)
        
        # 結果クリアボタン
        clear_button = ttk.Button(
            button_frame,
            text="🗑️ 結果クリア",
            command=self.clear_learning_results
        )
        clear_button.pack(side=tk.LEFT)
        
        # 学習履歴ボタン
        history_button = ttk.Button(
            button_frame,
            text="📚 学習履歴",
            command=self.show_learning_history
        )
        history_button.pack(side=tk.LEFT, padx=(10, 0))
        
        # せつなのコメントフレーム
        comment_frame = ttk.LabelFrame(main_frame, text="💭 せつなのコメント", padding=15)
        comment_frame.pack(fill=tk.X)
        
        self.setsuna_comment = ttk.Label(
            comment_frame,
            text="新しい動画を教えてくれたら、一緒に楽しめそうだね！",
            font=('Arial', 10, 'italic'),
            foreground='purple',
            wraplength=500
        )
        self.setsuna_comment.pack()
        
        # URL入力フィールドでEnterキーを押したときの処理
        self.url_entry.bind('<Return>', lambda event: self.start_video_learning())
        
        # Phase 2B: 画像分析機能追加
        self._create_image_analysis_widgets(main_frame)
    
    def _create_image_upload_widgets(self, parent_frame):
        """画像アップロードウィジェット作成"""
        
        # 画像アップロードフレーム
        image_frame = ttk.LabelFrame(parent_frame, text="📸 関連画像", padding=15)
        image_frame.pack(fill=tk.X, pady=(0, 15))
        
        # 説明テキスト
        description_label = ttk.Label(
            image_frame,
            text="動画に関連する画像をアップロードできます（スクリーンショット、サムネイルなど）",
            font=('Arial', 9),
            foreground='gray'
        )
        description_label.pack(pady=(0, 10))
        
        # ボタンエリア
        button_frame = ttk.Frame(image_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 画像選択ボタン
        self.select_image_button = ttk.Button(
            button_frame,
            text="📁 画像選択",
            command=self.select_images,
            style="Accent.TButton"
        )
        self.select_image_button.pack(side=tk.LEFT)
        
        # 選択クリアボタン
        self.clear_images_button = ttk.Button(
            button_frame,
            text="🗑️ クリア",
            command=self.clear_selected_images
        )
        self.clear_images_button.pack(side=tk.LEFT, padx=(10, 0))
        
        # 貼り付けボタン
        self.paste_button = ttk.Button(
            button_frame,
            text="📋 貼り付け (Ctrl+V)",
            command=self.paste_from_clipboard_smart,
            style="Accent.TButton"
        )
        self.paste_button.pack(side=tk.LEFT, padx=(10, 0))
        
        # 選択画像数表示
        self.image_count_label = ttk.Label(
            button_frame,
            text="選択画像: 0枚",
            font=('Arial', 9),
            foreground='blue'
        )
        self.image_count_label.pack(side=tk.LEFT, padx=(20, 0))
        
        # ドラッグ&ドロップエリア
        self.drop_area = tk.Label(
            image_frame,
            text="画像ファイルをここにドラッグ&ドロップ\n対応形式: JPG, PNG, GIF, BMP, WEBP",
            relief="ridge",
            bg="lightgray",
            fg="darkgray",
            font=('Arial', 10),
            height=3,
            cursor="hand2"
        )
        self.drop_area.pack(fill=tk.X, pady=(0, 10))
        
        # プレビューエリア
        self.preview_frame = ttk.LabelFrame(image_frame, text="プレビュー", padding=10)
        self.preview_frame.pack(fill=tk.X)
        
        # スクロール可能なプレビューエリア
        self.preview_canvas = tk.Canvas(self.preview_frame, height=120, bg="white")
        self.preview_scrollbar = ttk.Scrollbar(self.preview_frame, orient="horizontal", command=self.preview_canvas.xview)
        self.preview_canvas.configure(xscrollcommand=self.preview_scrollbar.set)
        
        self.preview_canvas.pack(fill=tk.X, side=tk.TOP)
        self.preview_scrollbar.pack(fill=tk.X, side=tk.BOTTOM)
        
        # プレビュー内容フレーム
        self.preview_content_frame = ttk.Frame(self.preview_canvas)
        self.preview_canvas.create_window((0, 0), window=self.preview_content_frame, anchor="nw")
        
        # イベントバインド
        self.drop_area.bind("<Button-1>", lambda e: self.select_images())
        
        # ドラッグ&ドロップ設定（基本実装）
        # Note: 完全なD&D実装は追加のライブラリが必要なため、現在はクリックで代替
        
        # Ctrl+V キーバインド（画像フレーム全体に適用）
        image_frame.bind("<Control-v>", self._on_paste_key)
        image_frame.focus_set()  # フォーカス設定
        
        # 環境情報表示
        env_info = self._get_paste_capability_info()
        env_label = ttk.Label(
            image_frame,
            text=env_info,
            font=('Arial', 8),
            foreground='gray'
        )
        env_label.pack(pady=(5, 0))
        
        # Phase 2B: 画像アップロード用変数を初期化
        self.selected_images = []  # アップロード画像リスト
        self.analysis_results = []  # 分析結果キャッシュ
        self.generated_context = ""  # 生成されたコンテキスト
        
    def select_images(self):
        """ファイルダイアログで画像選択"""
        try:
            file_types = [
                ("画像ファイル", "*.jpg *.jpeg *.png *.gif *.bmp *.webp"),
                ("JPEGファイル", "*.jpg *.jpeg"),
                ("PNGファイル", "*.png"),
                ("すべてのファイル", "*.*")
            ]
            
            files = filedialog.askopenfilenames(
                title="画像ファイルを選択",
                filetypes=file_types,
                multiple=True
            )
            
            if files:
                # 既存の選択をクリア
                self.selected_images.clear()
                
                # 新しい画像を追加
                for file_path in files:
                    # Phase 2B: シンプルなバリデーション
                    try:
                        # 画像ファイルか確認
                        with Image.open(file_path) as img:
                            pass  # 正常に開けるかチェック
                        
                        # Phase 2B形式で追加（パスのみ）
                        self.selected_images.append(file_path)
                    except Exception as e:
                        messagebox.showwarning("画像エラー", f"{os.path.basename(file_path)}:\n無効な画像ファイル: {e}")
                
                # プレビュー更新
                self.update_image_preview()
                self.update_image_count()
                
                # Phase 2B: 画像が選択されたら分析ボタンを有効化
                if hasattr(self, 'analyze_button') and len(self.selected_images) > 0:
                    self.analyze_button.config(state="normal")
                    self.analysis_status_label.config(text=f"{len(self.selected_images)}枚の画像が選択されました", foreground="blue")
                
        except Exception as e:
            messagebox.showerror("エラー", f"画像選択エラー: {e}")
    
    def clear_selected_images(self):
        """選択画像をクリア"""
        self.selected_images.clear()
        self.update_image_preview()
        self.update_image_count()
        
        # Phase 2B: 画像がクリアされたら分析ボタンを無効化
        if hasattr(self, 'analyze_button'):
            self.analyze_button.config(state="disabled")
            self.analysis_status_label.config(text="待機中...", foreground="gray")
            
        # 分析結果もクリア
        self.analysis_results.clear()
        self.generated_context = ""
    
    def update_image_count(self):
        """選択画像数の表示を更新"""
        count = len(self.selected_images)
        self.image_count_label.config(text=f"選択画像: {count}枚")
        
        # Phase 2B: カウントが0の時は分析ボタンを無効化
        if hasattr(self, 'analyze_button') and count == 0:
            self.analyze_button.config(state="disabled")
            if hasattr(self, 'analysis_status_label'):
                self.analysis_status_label.config(text="待機中...", foreground="gray")
    
    def update_image_preview(self):
        """プレビューエリアを更新"""
        try:
            # 既存のプレビューをクリア
            for widget in self.preview_content_frame.winfo_children():
                widget.destroy()
            
            if not self.selected_images:
                # 画像がない場合
                no_image_label = ttk.Label(
                    self.preview_content_frame,
                    text="画像が選択されていません",
                    foreground='gray'
                )
                no_image_label.pack(pady=20)
            else:
                # 画像プレビューを作成
                for i, image_path in enumerate(self.selected_images):
                    self.create_image_preview_widget({'file_path': image_path}, i)
            
            # スクロールエリアを更新
            self.preview_content_frame.update_idletasks()
            self.preview_canvas.configure(scrollregion=self.preview_canvas.bbox("all"))
            
        except Exception as e:
            print(f"[GUI] ❌ プレビュー更新エラー: {e}")
    
    def create_image_preview_widget(self, image_info, index):
        """個別の画像プレビューウィジェット作成"""
        try:
            # プレビューフレーム
            preview_item = ttk.Frame(self.preview_content_frame)
            preview_item.pack(side=tk.LEFT, padx=5, pady=5)
            
            # サムネイル作成
            with Image.open(image_info['file_path']) as img:
                # サムネイルサイズ
                thumbnail_size = (80, 80)
                # PIL バージョン互換性対応
                try:
                    img.thumbnail(thumbnail_size, Image.Resampling.LANCZOS)
                except AttributeError:
                    img.thumbnail(thumbnail_size, Image.LANCZOS)
                
                # tkinter用に変換
                photo = ImageTk.PhotoImage(img)
                
                # 画像ラベル
                image_label = tk.Label(preview_item, image=photo, relief="solid", borderwidth=1)
                image_label.image = photo  # 参照を保持
                image_label.pack()
                
                # ファイル名表示
                filename = image_info['file_path'].split('/')[-1]
                if len(filename) > 15:
                    filename = filename[:12] + "..."
                
                name_label = ttk.Label(
                    preview_item,
                    text=filename,
                    font=('Arial', 8),
                    width=12
                )
                name_label.pack(pady=(2, 0))
                
                # 削除ボタン
                delete_button = ttk.Button(
                    preview_item,
                    text="✕",
                    width=3,
                    command=lambda idx=index: self.remove_image(idx)
                )
                delete_button.pack(pady=(2, 0))
                
        except Exception as e:
            print(f"[GUI] ❌ プレビューウィジェット作成エラー: {e}")
    
    def remove_image(self, index):
        """指定インデックスの画像を削除"""
        try:
            if 0 <= index < len(self.selected_images):
                self.selected_images.pop(index)
                self.update_image_preview()
                self.update_image_count()
        except Exception as e:
            print(f"[GUI] ❌ 画像削除エラー: {e}")
    
    def _get_paste_capability_info(self):
        """貼り付け機能の対応状況情報を取得"""
        if os.name == 'nt':  # Windows
            return "💡 対応: ファイル貼り付け・スクリーンショット貼り付け (Ctrl+V)"
        else:  # WSL2/Linux
            return "💡 対応: ファイル貼り付け (Ctrl+V) | スクリーンショットはWindows環境のみ"
    
    def _on_paste_key(self, event):
        """Ctrl+V キーイベントハンドラ"""
        self.paste_from_clipboard_smart()
        return "break"  # イベントの伝播を停止
    
    def paste_from_clipboard_smart(self):
        """スマート貼り付け: 環境に応じて最適な貼り付け方法を選択"""
        try:
            # Phase 1.5B: Windows環境でスクリーンショット貼り付けを試行
            if os.name == 'nt':
                if self._paste_screenshot_from_clipboard():
                    return
            
            # Phase 1.5A: ファイルパス貼り付けを試行
            if self._paste_filepath_from_clipboard():
                return
            
            # 両方とも失敗した場合
            messagebox.showinfo(
                "貼り付け", 
                "クリップボードに画像ファイルまたは画像データが見つかりません。\n\n"
                "以下をお試しください:\n"
                "• 画像ファイルをコピー (Ctrl+C)\n"
                "• スクリーンショットを撮影 (Win+Shift+S)\n"
                "• 画像を右クリック→コピー"
            )
            
        except Exception as e:
            messagebox.showerror("エラー", f"貼り付け処理エラー: {e}")
    
    def _paste_filepath_from_clipboard(self):
        """Phase 1.5A: クリップボードからファイルパスを取得して画像追加"""
        try:
            # クリップボードからテキスト取得
            clipboard_text = self.root.clipboard_get().strip()
            
            if not clipboard_text:
                return False
            
            # ファイルパスとして有効かチェック
            if not os.path.isfile(clipboard_text):
                return False
            
            # 画像ファイルとして有効かチェック
            is_valid, error_msg = self.image_manager.validate_image_file(clipboard_text)
            if not is_valid:
                print(f"[GUI] ⚠️ クリップボード画像検証失敗: {error_msg}")
                return False
            
            # 既存の画像追加処理を利用
            self.selected_images.append({
                'file_path': clipboard_text,
                'description': 'クリップボードから貼り付け'
            })
            
            # UI更新
            self.update_image_preview()
            self.update_image_count()
            
            print(f"[GUI] ✅ ファイルパス貼り付け成功: {clipboard_text}")
            messagebox.showinfo("貼り付け成功", f"画像ファイルを追加しました:\n{os.path.basename(clipboard_text)}")
            return True
            
        except tk.TclError:
            # クリップボードにテキストデータがない
            return False
        except Exception as e:
            print(f"[GUI] ❌ ファイルパス貼り付けエラー: {e}")
            return False
    
    def _paste_screenshot_from_clipboard(self):
        """Phase 1.5B: Windows環境でスクリーンショット貼り付け"""
        try:
            # Windows環境チェック
            if os.name != 'nt':
                return False
            
            # PIL.ImageGrab をインポート（Windows専用）
            from PIL import ImageGrab
            
            # クリップボードから画像データ取得
            img = ImageGrab.grabclipboard()
            
            if img is None:
                return False
            
            # 一時ファイル作成
            temp_image_path = self._create_temp_image_from_pil(img)
            if not temp_image_path:
                return False
            
            # 既存の画像追加処理を利用
            self.selected_images.append({
                'file_path': temp_image_path,
                'description': 'スクリーンショット貼り付け'
            })
            
            # UI更新
            self.update_image_preview()
            self.update_image_count()
            
            print(f"[GUI] ✅ スクリーンショット貼り付け成功: {img.size}")
            messagebox.showinfo(
                "貼り付け成功", 
                f"スクリーンショットを追加しました\nサイズ: {img.size[0]}×{img.size[1]}"
            )
            return True
            
        except ImportError:
            print("[GUI] ⚠️ PIL.ImageGrab が利用できません（Windows環境が必要）")
            return False
        except Exception as e:
            print(f"[GUI] ❌ スクリーンショット貼り付けエラー: {e}")
            return False
    
    def _create_temp_image_from_pil(self, pil_image):
        """PIL Imageから一時ファイルを作成"""
        try:
            import tempfile
            import uuid
            
            # 一時ディレクトリに保存
            temp_dir = Path(tempfile.gettempdir()) / "setsuna_bot_clipboard"
            temp_dir.mkdir(exist_ok=True)
            
            # ユニークなファイル名生成
            unique_id = str(uuid.uuid4())[:8]
            temp_filename = f"clipboard_{unique_id}.png"
            temp_path = temp_dir / temp_filename
            
            # RGBA モードの場合は RGB に変換（JPEG保存のため）
            if pil_image.mode in ('RGBA', 'LA', 'P'):
                # 透明背景を白に変換
                background = Image.new('RGB', pil_image.size, (255, 255, 255))
                if pil_image.mode == 'P':
                    pil_image = pil_image.convert('RGBA')
                background.paste(pil_image, mask=pil_image.split()[-1] if 'A' in pil_image.mode else None)
                pil_image = background
            
            # PNG形式で保存（高品質・可逆圧縮）
            pil_image.save(temp_path, 'PNG')
            
            print(f"[GUI] 📁 一時画像ファイル作成: {temp_path}")
            return str(temp_path)
            
        except Exception as e:
            print(f"[GUI] ❌ 一時画像ファイル作成エラー: {e}")
            return None
    
    def _cleanup_temp_clipboard_files(self):
        """一時クリップボードファイルのクリーンアップ"""
        try:
            temp_dir = Path(tempfile.gettempdir()) / "setsuna_bot_clipboard"
            if temp_dir.exists():
                # 30分以上古いファイルを削除
                import time
                current_time = time.time()
                cleanup_count = 0
                
                for temp_file in temp_dir.iterdir():
                    if temp_file.is_file():
                        file_age = current_time - temp_file.stat().st_mtime
                        if file_age > 1800:  # 30分 = 1800秒
                            temp_file.unlink()
                            cleanup_count += 1
                
                if cleanup_count > 0:
                    print(f"[GUI] 🧹 一時ファイルクリーンアップ: {cleanup_count}件削除")
                
        except Exception as e:
            print(f"[GUI] ❌ 一時ファイルクリーンアップエラー: {e}")
        
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
        
        # Phase 2C-4: プログレス表示エリア（モード選択の下）
        self.progress_widget = ProgressWidget(self.chat_tab)
        self.progress_widget.set_cancel_callback(self._cancel_processing)
        self.progress_widget.set_detail_callback(self._show_progress_details)
        print("📊 プログレス表示ウィジェット作成完了")
        
        # Phase 2C-1: 統合チャット入力エリア（下部固定）
        self.input_frame.pack(fill=tk.X, padx=5, pady=5, side=tk.BOTTOM)
        
        # 添付ボタンエリア（最上部）
        self.attachment_frame.pack(fill=tk.X, pady=(0, 2))
        self.image_attach_button.pack(side=tk.LEFT, padx=(0, 5))
        self.url_attach_button.pack(side=tk.LEFT, padx=(0, 5))
        self.clear_attachments_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # 添付プレビューエリア（常時表示）
        self.preview_frame.pack(fill=tk.X, pady=(2, 2))
        
        # 初期メッセージ表示
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.insert("1.0", "添付ファイル・ URLなし")
        self.preview_text.config(state=tk.DISABLED)
        
        # テキスト入力エリア
        self.text_input_frame.pack(fill=tk.X, pady=(0, 5))
        self.text_input.pack(fill=tk.X, pady=(0, 2), expand=False)
        self.send_button.pack(side=tk.RIGHT, padx=(5, 0))
        
        # 会話履歴（残りのスペースを使用）
        self.history_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(5, 0))
        self.history_text.pack(fill=tk.BOTH, expand=True)
        
        # Phase 2C-2: RichMessageRenderer初期化
        try:
            self.rich_renderer = RichMessageRenderer(self.history_text)
            print("🎨 RichMessageRenderer初期化完了")
            print(f"🔍 初期化後のrich_renderer: {type(self.rich_renderer)}")
        except Exception as e:
            print(f"⚠️ RichMessageRenderer初期化エラー: {e}")
            import traceback
            traceback.print_exc()
            self.rich_renderer = None
            print(f"🔍 エラー後のrich_renderer: {self.rich_renderer}")
        
        # URL表示エリアを会話履歴の後に配置
        self.url_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        self.url_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.url_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 初期メッセージを表示
        self.url_listbox.insert(tk.END, "動画推薦時にここにURLが表示されます")
        print("🔧 URL表示エリア: 常時表示モードで配置完了")
        
        # Phase 2C-1: 統合ボタンエリア（概に結合）
        button_frame = ttk.Frame(self.text_input_frame)
        button_frame.pack(fill=tk.X, pady=(2, 0))
        
        # URL表示テスト用ボタン（統合版）
        self.test_url_button = ttk.Button(
            button_frame,
            text="URL表示テスト 🔗",
            command=self.test_url_display
        )
        self.test_url_button.pack(side=tk.LEFT)
        
        # Enterキーで統合送信
        self.text_input.bind('<Control-Return>', lambda event: self.send_integrated_message())
    
    def add_message_to_history(self, speaker, message, message_type="text"):
        """会話履歴にメッセージを追加（Phase 2C-2: リッチメッセージ対応）"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # 履歴データに追加
        history_entry = {
            "timestamp": timestamp,
            "speaker": speaker,
            "message": message,
            "type": message_type
        }
        self.conversation_history.append(history_entry)
        
        # Phase 2C-2: RichMessageRendererを使用
        if self.rich_renderer:
            self.rich_renderer.render_message(speaker, message, message_type)
        else:
            # RichMessageRendererが利用できない場合、初期化を試行
            if hasattr(self, 'history_text') and self.history_text:
                try:
                    self.rich_renderer = RichMessageRenderer(self.history_text)
                    print("🔄 RichMessageRenderer再初期化成功")
                    self.rich_renderer.render_message(speaker, message, message_type)
                    return
                except Exception as e:
                    print(f"⚠️ RichMessageRenderer再初期化失敗: {e}")
            
            # フォールバック: 従来の表示方法
            self._fallback_message_display(speaker, message, message_type, timestamp)
    
    def _fallback_message_display(self, speaker, message, message_type, timestamp):
        """フォールバック: 従来のメッセージ表示"""
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
                selected_mode = self.response_mode.get() if hasattr(self, 'response_mode') else 'full_search'
                response = self.setsuna_chat.get_response(message, mode=selected_mode)
                
                # 新実装: 条件付きURL表示（動画関連の場合のみ）
                try:
                    print(f"🔗 [URL表示] コンテキストデータ確認開始")
                    
                    # せつなチャットから最後のコンテキストデータを取得
                    context_data = self.setsuna_chat.get_last_context_data()
                    
                    # 動画関連クエリの場合のみURL表示
                    if context_data and ('videos' in context_data or 'external_videos' in context_data):
                        # Phase 2: DB動画と外部動画を統合して表示
                        all_display_videos = []
                        
                        # DB内動画の変換
                        db_videos = context_data.get('videos', [])
                        if db_videos:
                            db_display_videos = self._convert_context_videos_to_display_format(db_videos)
                            all_display_videos.extend(db_display_videos)
                            print(f"🔗 [URL表示] DB動画: {len(db_display_videos)}件")
                        
                        # 外部動画の変換
                        external_videos = context_data.get('external_videos', [])
                        if external_videos:
                            external_display_videos = self._convert_context_videos_to_display_format(external_videos)
                            all_display_videos.extend(external_display_videos)
                            print(f"🔗 [URL表示] 外部動画: {len(external_display_videos)}件")
                        
                        if all_display_videos:
                            print(f"🔗 [URL表示] 統合表示: 合計{len(all_display_videos)}件")
                            self.show_video_urls_simple(all_display_videos)
                        else:
                            print(f"🔗 [URL表示] 動画関連だが検索結果なし")
                            self.url_listbox.delete(0, tk.END)
                            self.url_listbox.insert(tk.END, "該当する動画が見つかりませんでした")
                    else:
                        print(f"🔗 [URL表示] 非動画関連クエリのためURL表示スキップ")
                        # 非動画関連の場合はURL表示をクリア
                        self.url_listbox.delete(0, tk.END)
                    
                except Exception as e:
                    print(f"❌ [URL表示] エラー: {e}")
                    # エラー時はメッセージ表示
                    self.url_listbox.delete(0, tk.END)
                    self.url_listbox.insert(tk.END, f"エラー: {e}")
            else:
                response = f"申し訳ありません。システムが初期化されていません。"
            
            # UIスレッドで履歴更新
            self.root.after(0, lambda: self.add_message_to_history("せつな", response, "text"))
            
            # 音声合成実行
            if self.voice_synthesizer:
                self.update_voice_status("音声合成中...")
                
                # 音声合成用にテキストを変換
                speech_text = response
                if self.speech_text_converter:
                    speech_text = self.speech_text_converter.convert_for_speech(response)
                    if speech_text != response:
                        print(f"🔄 [音声変換] テキスト変換実行済み")
                
                wav_path = self.voice_synthesizer.synthesize_voice(speech_text)
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
    
    # Phase 2C-1: 統合チャット入力機能メソッド群
    
    def attach_image(self):
        """画像ファイル添付"""
        try:
            file_path = filedialog.askopenfilename(
                title="画像を選択",
                filetypes=[
                    ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp *.webp"),
                    ("All files", "*.*")
                ]
            )
            
            if file_path:
                # ファイル情報を取得
                file_info = {
                    'type': 'image',
                    'path': file_path,
                    'name': os.path.basename(file_path),
                    'size': os.path.getsize(file_path)
                }
                
                self.attached_files.append(file_info)
                self._update_preview()
                print(f"📸 画像添付: {file_info['name']}")
                
        except Exception as e:
            messagebox.showerror("エラー", f"画像添付エラー: {e}")
    
    def attach_url(self):
        """URL添付"""
        from tkinter import simpledialog
        
        try:
            url = simpledialog.askstring(
                "URL入力",
                "YouTube URLまたは他のURLを入力してください:",
                initialvalue="https://"
            )
            
            if url and url.strip():
                url = url.strip()
                
                # URLバリデーション
                if not (url.startswith('http://') or url.startswith('https://')):
                    messagebox.showwarning("警告", "有効なURLを入力してください")
                    return
                
                # URL情報を取得
                url_info = {
                    'type': 'url',
                    'url': url,
                    'title': self._get_url_title(url)
                }
                
                self.current_url = url_info
                self._update_preview()
                print(f"🔗 URL添付: {url}")
                
        except Exception as e:
            messagebox.showerror("エラー", f"URL添付エラー: {e}")
    
    def clear_attachments(self):
        """添付ファイル・ URLクリア"""
        self.attached_files.clear()
        self.current_url = None
        self._update_preview()
        print("🗑️ 添付ファイルクリア")
    
    def _update_preview(self):
        """添付プレビュー更新（安全なレイアウト管理）"""
        try:
            preview_items = []
            
            # 添付画像
            for file_info in self.attached_files:
                size_mb = file_info['size'] / (1024 * 1024)
                preview_items.append(f"📸 {file_info['name']} ({size_mb:.1f}MB)")
            
            # 添付URL
            if self.current_url:
                preview_items.append(f"🔗 {self.current_url['title']}")
            
            # プレビューテキスト更新
            self.preview_text.config(state=tk.NORMAL)
            self.preview_text.delete("1.0", tk.END)
            
            if preview_items:
                preview_content = "\n".join(preview_items)
                self.preview_text.insert("1.0", preview_content)
                
                # プレビュー内容を更新（フレームは常時表示）
                print(f"📋 プレビュー更新: {len(preview_items)}件")
            else:
                # 添付なしの状態
                preview_content = "添付ファイル・ URLなし"
                self.preview_text.insert("1.0", preview_content)
                print("📋 プレビュークリア")
            
            self.preview_text.config(state=tk.DISABLED)
            
        except Exception as e:
            print(f"⚠️ プレビュー更新エラー: {e}")
            # エラー時はシンプルなメッセージ表示
            try:
                self.preview_text.config(state=tk.NORMAL)
                self.preview_text.delete("1.0", tk.END)
                if self.attached_files or self.current_url:
                    count = len(self.attached_files) + (1 if self.current_url else 0)
                    self.preview_text.insert("1.0", f"📋 {count}件の添付アイテム")
                else:
                    self.preview_text.insert("1.0", "添付ファイル・ URLなし")
                self.preview_text.config(state=tk.DISABLED)
            except:
                pass  # 最終的なエラーは無視
    
    def _get_url_title(self, url):
        """簡易URLタイトル取得"""
        try:
            if 'youtube.com' in url or 'youtu.be' in url:
                return "YouTube動画"
            elif 'twitter.com' in url or 'x.com' in url:
                return "Twitter/Xポスト"
            else:
                return f"ウェブサイト: {url[:30]}..."
        except:
            return "URL"
    
    def send_integrated_message(self):
        """統合メッセージ送信（テキスト+画像+URL）"""
        message_text = self.text_input.get("1.0", tk.END).strip()
        
        # メッセージが空で添付ファイルもない場合
        if not message_text and not self.attached_files and not self.current_url:
            return
        
        # 入力フィールドをクリア
        self.text_input.delete("1.0", tk.END)
        
        # 統合メッセージ构築
        integrated_message = {
            'text': message_text,
            'images': self.attached_files.copy(),
            'url': self.current_url,
            'timestamp': datetime.now().isoformat()
        }
        
        # 統合メッセージ送信ログ（クリア前に出力）
        print(f"📡 統合メッセージ送信: テキスト({len(message_text)}), 画像({len(self.attached_files)}), URL({'Yes' if self.current_url else 'No'})")
        
        # ユーザーメッセージを履歴に追加（リッチ表示）
        self._add_integrated_message_to_history("あなた", integrated_message)
        
        # 添付ファイルをクリア
        self.clear_attachments()
        
        # 別スレッドで処理
        threading.Thread(
            target=self._process_integrated_message, 
            args=(integrated_message,), 
            daemon=True
        ).start()
    
    def _add_integrated_message_to_history(self, speaker, integrated_message):
        """統合メッセージを履歴に追加（Phase 2C-2: リッチ表示対応）"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # 履歴データに追加
        history_entry = {
            "timestamp": timestamp,
            "speaker": speaker,
            "message": integrated_message,
            "type": "integrated"
        }
        self.conversation_history.append(history_entry)
        
        # Phase 2C-2: RichMessageRendererでリッチ表示
        if self.rich_renderer:
            self.rich_renderer.render_message(speaker, integrated_message, "integrated")
        else:
            # RichMessageRendererが利用できない場合、初期化を試行
            if hasattr(self, 'history_text') and self.history_text:
                try:
                    self.rich_renderer = RichMessageRenderer(self.history_text)
                    print("🔄 RichMessageRenderer再初期化成功（統合メッセージ）")
                    self.rich_renderer.render_message(speaker, integrated_message, "integrated")
                    return
                except Exception as e:
                    print(f"⚠️ RichMessageRenderer再初期化失敗（統合メッセージ）: {e}")
            # フォールバック: 簡易表示
            display_parts = []
            
            if integrated_message['text']:
                display_parts.append(integrated_message['text'])
            
            if integrated_message['images']:
                image_count = len(integrated_message['images'])
                display_parts.append(f"[📸 画像 {image_count}枚]")
            
            if integrated_message['url']:
                display_parts.append(f"[🔗 {integrated_message['url']['title']}]")
            
            display_text = " ".join(display_parts)
            self._fallback_message_display(speaker, display_text, "integrated", timestamp)
    
    def _process_integrated_message(self, integrated_message):
        """統合メッセージ処理（Phase 2C-4: プログレス表示付き）"""
        try:
            print("🔄 統合メッセージ処理開始")
            # Phase 2C-4: プログレス管理開始
            self.progress_manager = ProgressManager(self._update_progress_display)
            print("✅ ProgressManager初期化完了")
            
            # プログレスステップ定義
            self.progress_manager.add_step("init", "初期化", "統合メッセージ解析開始", weight=0.5)
            
            text_part = integrated_message.get('text', '')
            images = integrated_message.get('images', [])
            url_info = integrated_message.get('url')
            
            # 画像がある場合は分析ステップを追加
            if images:
                for i, image_info in enumerate(images):
                    step_id = f"image_analysis_{i}"
                    image_name = image_info.get('name', f'画像{i+1}')
                    self.progress_manager.add_step(
                        step_id, 
                        f"画像分析 {i+1}", 
                        f"{image_name} を分析中",
                        weight=2.0
                    )
            
            # URL処理ステップ
            if url_info:
                self.progress_manager.add_step("url_process", "URL処理", "URL情報を処理中", weight=0.5)
            
            # 応答生成ステップ
            self.progress_manager.add_step("response_gen", "応答生成", "せつなが考え中", weight=2.0)
            
            # 音声合成ステップ
            self.progress_manager.add_step("voice_synth", "音声合成", "音声を生成中", weight=1.0)
            
            # プログレス開始
            print("🚀 プログレス処理開始前")
            self.progress_manager.start_processing()
            print("📊 プログレス表示開始前")
            self.progress_widget.show()
            print("✅ プログレス表示完了")
            
            # Phase 2C-1改良: 画像分析、URL解析、統合コンテキスト生成
            print("📝 初期化ステップ開始前")
            step_result = self.progress_manager.start_step("init")
            print(f"✅ start_step戻り値: {step_result}")
            print("🔧 voice_status更新前")
            self.update_voice_status("📊 統合分析開始...")
            print("📊 進捗更新前")
            self.progress_manager.update_step_progress("init", 50.0, "メッセージ内容を解析中")
            
            print(f"🔍 統合メッセージ解析: テキスト='{text_part}', 画像={len(images)}件, URL={'有' if url_info else '無'}")
            
            print("🏁 初期化ステップ完了前")
            self.progress_manager.complete_step("init", "統合メッセージ解析完了")
            print("✅ 初期化ステップ完了")
            
            # 統合コンテキスト構築
            context_parts = []
            
            # 1. 画像分析処理（Phase 2C-4: プログレス管理付き）
            if images and self.youtube_manager and hasattr(self.youtube_manager, 'image_analyzer'):
                self.update_voice_status("🔍 画像分析中...")
                
                for i, image_info in enumerate(images):
                    step_id = f"image_analysis_{i}"
                    try:
                        # プログレス開始
                        self.progress_manager.start_step(step_id)
                        
                        image_path = image_info.get('path')
                        if image_path and os.path.exists(image_path):
                            image_name = image_info.get('name', f'画像{i+1}')
                            print(f"🖼️ 画像分析開始: {image_name}")
                            
                            self.progress_manager.update_step_progress(step_id, 10.0, f"{image_name} 読み込み中")
                            
                            # Phase 2Bの画像分析システムを使用（安全なフォールバック付き）
                            try:
                                self.progress_manager.update_step_progress(step_id, 30.0, f"{image_name} AI分析中")
                                context = {
                                    'title': integrated_message.get('text', '添付画像'),
                                    'artist': '不明',
                                    'description': f"ユーザーから添付された画像: {image_info['name']}"
                                }
                                
                                # まず一般的な分析を試行
                                self.progress_manager.update_step_progress(step_id, 60.0, f"{image_name} 基本分析実行中")
                                analysis_result = self.youtube_manager.image_analyzer.analyze_image(
                                    image_path, 
                                    analysis_type="general_description"
                                )
                                
                                # 成功しなかった場合はcontextを付けて再試行
                                if not analysis_result or 'description' not in analysis_result:
                                    self.progress_manager.update_step_progress(step_id, 80.0, f"{image_name} 詳細分析実行中")
                                    analysis_result = self.youtube_manager.image_analyzer.analyze_image(
                                        image_path, 
                                        analysis_type="music_video_analysis",
                                        context=context
                                    )
                                    
                            except Exception as analysis_error:
                                print(f"⚠️ 画像分析エラー（詳細）: {analysis_error}")
                                self.progress_manager.error_step(step_id, f"画像分析エラー: {str(analysis_error)}")
                                # フォールバック: 簡易説明
                                analysis_result = {
                                    'description': f"添付された画像ファイル: {image_info['name']}（分析に失敗しました）"
                                }
                            
                            if analysis_result and 'description' in analysis_result:
                                image_desc = analysis_result['description']
                                context_parts.append(f"🖼️ 画像分析 '{image_info['name']}': {image_desc}")
                                self.progress_manager.complete_step(step_id, f"{image_name} 分析完了")
                                print(f"✅ 画像分析成功: {image_info['name']}")
                            else:
                                self.progress_manager.error_step(step_id, f"{image_name} 分析結果が不正")
                                context_parts.append(f"🖼️ 画像 '{image_info['name']}'が添付されました")
                                print(f"⚠️ 画像分析失敗: {image_info['name']}")
                        else:
                            self.progress_manager.error_step(step_id, f"{image_name} ファイルが見つかりません")
                            context_parts.append(f"🖼️ 画像 '{image_info['name']}'が添付されましたが、ファイルが見つかりません")
                        
                    except Exception as e:
                        print(f"❌ 画像分析エラー: {e}")
                        import traceback
                        traceback.print_exc()
                        self.progress_manager.error_step(step_id, f"画像分析例外: {str(e)}")
                        context_parts.append(f"🖼️ 画像 '{image_info.get('name', 'unknown')}'が添付されましたが、分析できませんでした")
            
            # 2. URL情報処理
            if url_info:
                url = url_info.get('url', '')
                title = url_info.get('title', 'URL')
                context_parts.append(f"🔗 {title}: {url}")
                print(f"🔗 URL情報追加: {title}")
            
            # 3. 統合コンテキスト作成 & 画像分析結果の統合メッセージ追加
            analysis_results = []
            if context_parts:
                context_text = "\n".join(context_parts)
                if text_part:
                    full_context = f"{text_part}\n\n添付情報:\n{context_text}"
                else:
                    full_context = f"添付情報:\n{context_text}"
                
                # 画像分析結果を抽出してintegrated_messageに追加
                for i, image_info in enumerate(images):
                    if i < len(context_parts):
                        # context_partsから該当する分析結果を抽出
                        context_line = context_parts[i]
                        if context_line.startswith("🖼️ 画像分析"):
                            # "🖼️ 画像分析 'filename': description" の形式から description を抽出
                            parts = context_line.split("': ", 1)
                            if len(parts) >= 2:
                                description = parts[1]
                                analysis_results.append({
                                    'name': image_info.get('name', f'画像{i+1}'),
                                    'description': description,
                                    'size': image_info.get('size', 0)
                                })
                            else:
                                # フォールバック
                                analysis_results.append({
                                    'name': image_info.get('name', f'画像{i+1}'),
                                    'description': f"画像ファイル {image_info.get('name', 'unknown')}",
                                    'size': image_info.get('size', 0)
                                })
                        else:
                            # フォールバック
                            analysis_results.append({
                                'name': image_info.get('name', f'画像{i+1}'),
                                'description': f"画像ファイル {image_info.get('name', 'unknown')}",
                                'size': image_info.get('size', 0)
                            })
            else:
                full_context = text_part
            
            # 4. セツナチャットで応答生成（Phase 2C-4: プログレス管理付き）
            if (text_part or images or url_info) and self.setsuna_chat:
                self.progress_manager.start_step("response_gen")
                self.update_voice_status("🤖 統合応答生成中...")
                self.progress_manager.update_step_progress("response_gen", 20.0, "せつながメッセージを読んでいます")
                
                selected_mode = self.response_mode.get() if hasattr(self, 'response_mode') else 'full_search'
                
                # Phase 2C-3: 画像分析結果をintegrated_messageに追加
                enhanced_message = integrated_message.copy()
                enhanced_message['image_analysis_results'] = analysis_results
                print(f"🔄 統合メッセージ強化: 分析結果{len(analysis_results)}件を追加")
                
                self.progress_manager.update_step_progress("response_gen", 50.0, "せつなが考え中...")
                response = self.setsuna_chat.get_integrated_response(enhanced_message, mode=selected_mode)
                self.progress_manager.complete_step("response_gen", "応答生成完了")
                print(f"✅ Phase 2C-3統合応答生成完了")
            else:
                self.progress_manager.error_step("response_gen", "処理するコンテンツがありません")
                response = "統合メッセージを受信しましたが、処理するコンテンツがありません。"
            
            # 5. UIスレッドで履歴更新
            self.root.after(0, lambda: self.add_message_to_history("せつな", response, "text"))
            
            # 6. 音声合成実行（Phase 2C-4: プログレス管理付き）
            if self.voice_synthesizer and response:
                self.progress_manager.start_step("voice_synth")
                self.update_voice_status("🔊 音声合成中...")
                self.progress_manager.update_step_progress("voice_synth", 30.0, "音声合成準備中")
                
                speech_text = response
                if self.speech_text_converter:
                    self.progress_manager.update_step_progress("voice_synth", 50.0, "音声用テキスト変換中")
                    speech_text = self.speech_text_converter.convert_for_speech(response)
                
                self.progress_manager.update_step_progress("voice_synth", 70.0, "音声ファイル生成中")
                wav_path = self.voice_synthesizer.synthesize_voice(speech_text)
                if wav_path:
                    self.progress_manager.update_step_progress("voice_synth", 90.0, "音声再生中")
                    self.voice_synthesizer.play_voice(wav_path)
                    self.progress_manager.complete_step("voice_synth", "音声出力完了")
                    print("✅ 統合メッセージ音声出力完了")
                else:
                    self.progress_manager.error_step("voice_synth", "音声ファイル生成失敗")
            else:
                # 音声合成をスキップ
                if hasattr(self.progress_manager, 'steps') and any(s.id == "voice_synth" for s in self.progress_manager.steps):
                    self.progress_manager.complete_step("voice_synth", "音声合成スキップ")
            
            # プログレス完了
            self.progress_manager.complete_processing()
            self.update_voice_status("待機中")
            
        except Exception as e:
            error_msg = f"統合メッセージ処理エラー: {e}"
            print(f"❌ {error_msg}")
            
            # プログレスエラー処理
            if hasattr(self, 'progress_manager') and self.progress_manager:
                self.progress_manager.cancel_processing()
            
            self.root.after(0, lambda: self.add_message_to_history("システム", error_msg, "error"))
            self.update_voice_status("エラー")
    
    def _cancel_processing(self):
        """プログレス処理キャンセル（Phase 2C-4）"""
        try:
            if self.progress_manager and self.progress_manager.is_running:
                self.progress_manager.cancel_processing()
                self.update_voice_status("処理キャンセル")
                print("🛑 ユーザーにより処理キャンセル")
        except Exception as e:
            print(f"❌ キャンセル処理エラー: {e}")
    
    def _show_progress_details(self):
        """プログレス詳細表示（Phase 2C-4）"""
        try:
            if self.progress_manager:
                status = self.progress_manager.get_status()
                DetailProgressDialog(self.root, status)
        except Exception as e:
            print(f"❌ 詳細表示エラー: {e}")
    
    def _update_progress_display(self, status):
        """プログレス表示更新（Phase 2C-4）"""
        try:
            # GUI更新をメインスレッドで実行
            if self.progress_widget:
                self.root.after(0, lambda: self.progress_widget.update_progress(status))
        except Exception as e:
            print(f"❌ プログレス表示更新エラー: {e}")
    
    def _on_drop(self, event):
        """ドラッグ&ドロップ処理（簡易実装）"""
        try:
            # tkinterdnd2がある場合の実装を想定
            # 現在はシンプルなメッセージ表示
            messagebox.showinfo("情報", "ドラッグ&ドロップ機能はPhase 2C-1で実装予定です。\n現在は📸ボタンで画像を選択してください。")
        except Exception as e:
            print(f"❌ ドラッグ&ドロップエラー: {e}")
    
    def show_video_urls_simple(self, videos_list):
        """シンプルなURL表示機能（強化版：2回目以降の更新問題対応）"""
        print(f"🔗 [URL表示] 更新要求: {len(videos_list)}件")
        
        # UIスレッドで確実に実行する内部関数
        def _update_ui():
            try:
                # 強制的な全クリア（2段階）
                print("🔗 [URL表示] Step1: 完全クリア実行")
                self.url_listbox.delete(0, tk.END)
                self.current_video_urls.clear()
                
                # tkinterの描画を強制更新
                self.url_listbox.update_idletasks()
                
                # 短時間待機後に再描画
                self.root.after(50, lambda: self._populate_urls(videos_list))
                
            except Exception as e:
                print(f"❌ [URL表示] クリア処理エラー: {e}")
        
        # UIスレッドで実行
        if hasattr(self.root, 'after'):
            self.root.after(0, _update_ui)
        else:
            # フォールバック: 直接実行
            _update_ui()
    
    def _populate_urls(self, videos_list):
        """URL一覧の再構築（分離処理）"""
        try:
            print("🔗 [URL表示] Step2: URL一覧再構築")
            
            if not videos_list:
                self.url_listbox.insert(tk.END, "推薦動画がありません")
                print("🔗 [URL表示] 空リスト表示")
                return
            
            # 動画を表示
            for i, video in enumerate(videos_list[:5]):  # 最大5件
                video_id = video.get('video_id', '')
                title = video.get('title', '不明な動画')
                channel = video.get('channel', '不明なチャンネル')
                
                if video_id:
                    url = f"https://www.youtube.com/watch?v={video_id}"
                    display_text = f"{title} - {channel}"
                    
                    self.url_listbox.insert(tk.END, display_text)
                    self.current_video_urls.append({
                        'url': url,
                        'title': title,
                        'channel': channel,
                        'video_id': video_id
                    })
                    print(f"🔗 [URL表示] 追加: {title}")
                else:
                    print(f"⚠️ [URL表示] video_id不明: {title}")
            
            # 最終描画更新
            self.url_listbox.update_idletasks()
            print(f"🔗 [URL表示] 完了: {len(self.current_video_urls)}件表示")
            
        except Exception as e:
            print(f"❌ [URL表示] 再構築エラー: {e}")
            self.url_listbox.insert(tk.END, f"エラー: {e}")
    
    def get_random_videos_for_url_display(self):
        """URL表示用のランダム動画取得"""
        try:
            if self.setsuna_chat and self.setsuna_chat.context_builder:
                knowledge_manager = self.setsuna_chat.context_builder.knowledge_manager
                if hasattr(knowledge_manager, 'get_random_recommendation'):
                    # get_random_recommendationメソッドを使用
                    raw_videos = knowledge_manager.get_random_recommendation(
                        context_hint="音楽",  # 音楽系動画を優先
                        limit=5
                    )
                    print(f"🎲 [ランダム推薦] {len(raw_videos)}件取得")
                    
                    # データ構造を変換
                    videos = []
                    for item in raw_videos:
                        if isinstance(item, dict) and 'video_id' in item and 'data' in item:
                            video_data = {
                                'video_id': item['video_id'],
                                'title': item['data']['metadata'].get('title', '不明な動画'),
                                'channel': item['data']['metadata'].get('channel_title', '不明なチャンネル')
                            }
                            videos.append(video_data)
                            print(f"🎲 [データ変換] {video_data['title']}")
                    
                    return videos
                else:
                    print("⚠️ [ランダム推薦] get_random_recommendationメソッドが存在しません")
            else:
                print("⚠️ [ランダム推薦] knowledge_managerが利用できません")
        except Exception as e:
            print(f"❌ [ランダム推薦] エラー: {e}")
        
        return []
    
    def test_url_display(self):
        """URL表示テスト用メソッド"""
        print("🧪 [URL表示テスト] 開始")
        
        # ランダム動画を取得してURL表示
        videos = self.get_random_videos_for_url_display()
        if videos:
            self.show_video_urls_simple(videos)
            self.add_message_to_history("システム", f"ランダム動画 {len(videos)}件をURL表示エリアに表示しました", "info")
        else:
            self.url_listbox.delete(0, tk.END)
            self.url_listbox.insert(tk.END, "動画データの取得に失敗しました")
            self.add_message_to_history("システム", "動画データの取得に失敗しました", "error")
        
        print("🧪 [URL表示テスト] 完了")
    
    def _convert_context_videos_to_display_format(self, context_videos):
        """
        コンテキストデータの動画情報を表示用フォーマットに変換
        
        Args:
            context_videos: コンテキストから取得した動画データ
            
        Returns:
            list: 表示用フォーマットの動画リスト
        """
        display_videos = []
        
        try:
            for video_item in context_videos:
                if isinstance(video_item, dict):
                    # video_idの取得
                    video_id = video_item.get('video_id', video_item.get('id'))
                    
                    # タイトルの取得（複数の可能性のあるパスをチェック）
                    title = None
                    if 'title' in video_item:
                        title = video_item['title']
                    elif 'data' in video_item and 'metadata' in video_item['data']:
                        title = video_item['data']['metadata'].get('title')
                    elif 'metadata' in video_item:
                        title = video_item['metadata'].get('title')
                    
                    # チャンネル名の取得
                    channel = None
                    if 'channel' in video_item:
                        channel = video_item['channel']
                    elif 'data' in video_item and 'metadata' in video_item['data']:
                        channel = video_item['data']['metadata'].get('channel_title')
                    elif 'metadata' in video_item:
                        channel = video_item['metadata'].get('channel_title')
                    
                    # 最低限video_idとtitleがあれば追加
                    if video_id and title:
                        display_video = {
                            'video_id': video_id,
                            'title': title,
                            'channel': channel or '不明なチャンネル'
                        }
                        display_videos.append(display_video)
                        print(f"🔄 [フォーマット変換] {title} (ID: {video_id})")
            
            print(f"🔄 [フォーマット変換] 完了: {len(display_videos)}件変換")
            return display_videos
            
        except Exception as e:
            print(f"❌ [フォーマット変換] エラー: {e}")
            return []
    
    def _extract_mentioned_videos_from_response(self, response: str, user_input: str) -> list:
        """
        2. 応答連携強化: GPT応答から言及された動画を抽出
        
        Args:
            response: せつなの応答テキスト
            user_input: ユーザーの入力
            
        Returns:
            言及された動画のリスト
        """
        try:
            print(f"[応答解析] 🔍 動画言及抽出開始: '{response[:50]}...'")
            
            # 楽曲名抽出パターン
            music_patterns = [
                r'「([^」]+)」',  # 「夜に駆ける」
                r'『([^』]+)』',  # 『アドベンチャー』  
                r'【([^】]+)】',  # 【XOXO】
                r'(\w+(?:\s+\w+)*)\s*(?:って|という|は|の)',  # アドベンチャーって
                r'([\w\s]+?)(?:もおすすめ|がおすすめ|を推薦)',  # 夜に駆けるもおすすめ
            ]
            
            mentioned_titles = []
            for pattern in music_patterns:
                matches = re.findall(pattern, response)
                for match in matches:
                    if len(match.strip()) >= 2:  # 2文字以上
                        mentioned_titles.append(match.strip())
                        print(f"[応答解析] 📝 楽曲名検出: '{match.strip()}'")
            
            # 抽出した楽曲名でDB検索
            mentioned_videos = []
            if mentioned_titles and self.setsuna_chat and self.setsuna_chat.context_builder:
                knowledge_manager = self.setsuna_chat.context_builder.knowledge_manager
                
                for title in mentioned_titles:
                    search_results = knowledge_manager.search_videos(title, limit=1)
                    if search_results:
                        video_data = search_results[0]
                        display_video = {
                            'video_id': video_data['video_id'],
                            'title': video_data['data']['metadata'].get('title', title),
                            'channel': video_data['data']['metadata'].get('channel_title', '不明なチャンネル'),
                            'source': 'response_mention'
                        }
                        mentioned_videos.append(display_video)
                        print(f"[応答解析] ✅ DB発見: {display_video['title'][:30]}...")
                    else:
                        print(f"[応答解析] ❌ DB未発見: '{title}'")
            
            print(f"[応答解析] 🎯 最終結果: {len(mentioned_videos)}件の言及動画")
            return mentioned_videos
            
        except Exception as e:
            print(f"❌ [応答解析] エラー: {e}")
            return []
    
    def find_recommended_videos_from_response(self, setsuna_response):
        """せつなの応答から推薦動画を特定（改善版）"""
        print(f"🔍 [動画特定] 応答分析開始: {setsuna_response[:50]}...")
        
        try:
            if not self.setsuna_chat or not self.setsuna_chat.context_builder:
                print("⚠️ [動画特定] context_builderが利用できません")
                return []
            
            knowledge_manager = self.setsuna_chat.context_builder.knowledge_manager
            if not hasattr(knowledge_manager, 'search_videos'):
                print("⚠️ [動画特定] search_videosメソッドが存在しません")
                return []
            
            # 応答から動画タイトル・チャンネル名を抽出
            keywords = self._extract_video_keywords_from_response(setsuna_response)
            print(f"🔍 [動画特定] 抽出キーワード: {keywords}")
            
            # キーワード優先度による検索
            found_videos = []
            video_scores = {}  # 動画ごとのスコア計算
            
            for i, keyword in enumerate(keywords):
                if len(keyword) > 1:
                    # 優先度計算（前の方のキーワードほど高スコア）
                    priority_score = len(keywords) - i
                    
                    search_results = knowledge_manager.search_videos(keyword, limit=5)
                    print(f"🔍 [検索] '{keyword}': {len(search_results)}件ヒット")
                    
                    for result in search_results:
                        video_id = result.get('video_id')
                        if video_id:
                            # スコア計算
                            match_score = self._calculate_video_match_score(result, keyword, setsuna_response)
                            total_score = match_score * priority_score
                            
                            if video_id in video_scores:
                                video_scores[video_id] += total_score
                            else:
                                video_scores[video_id] = total_score
                                found_videos.append(result)
                            
                            title = result.get('data', {}).get('metadata', {}).get('title', '不明')
                            print(f"🎯 [スコア] {title}: {total_score:.2f}")
            
            # スコア順でソート
            sorted_videos = []
            for video in found_videos:
                video_id = video.get('video_id')
                score = video_scores.get(video_id, 0)
                sorted_videos.append((score, video))
            
            sorted_videos.sort(key=lambda x: x[0], reverse=True)
            
            # データ構造を変換（上位5件）
            videos = []
            for score, item in sorted_videos[:5]:
                if isinstance(item, dict) and 'video_id' in item and 'data' in item:
                    video_data = {
                        'video_id': item['video_id'],
                        'title': item['data']['metadata'].get('title', '不明な動画'),
                        'channel': item['data']['metadata'].get('channel_title', '不明なチャンネル'),
                        'match_score': score
                    }
                    videos.append(video_data)
                    print(f"📊 [最終選択] {video_data['title']} (スコア: {score:.2f})")
            
            print(f"🔍 [動画特定] 完了: {len(videos)}件特定")
            return videos
            
        except Exception as e:
            print(f"❌ [動画特定] エラー: {e}")
            return []
    
    def _calculate_video_match_score(self, video, keyword, response):
        """動画とキーワードのマッチスコアを計算"""
        score = 1.0  # 基本スコア
        
        if not video or 'data' not in video:
            return score
        
        metadata = video['data'].get('metadata', {})
        title = metadata.get('title', '')
        channel = metadata.get('channel_title', '')
        
        # タイトル完全一致
        if keyword.lower() in title.lower():
            score += 3.0
            print(f"🎯 [マッチ] タイトル完全一致: +3.0")
        
        # チャンネル名一致
        if keyword.lower() in channel.lower():
            score += 2.0
            print(f"🎯 [マッチ] チャンネル名一致: +2.0")
        
        # 応答内での言及確認
        if title.lower() in response.lower():
            score += 4.0
            print(f"🎯 [マッチ] 応答内言及: +4.0")
        
        # キーワードが楽曲名っぽい場合の追加スコア
        if self._looks_like_song_title(keyword):
            score += 1.5
            print(f"🎯 [マッチ] 楽曲名推定: +1.5")
        
        return score
    
    def _looks_like_song_title(self, keyword):
        """キーワードが楽曲名っぽいかチェック"""
        song_indicators = ['歌', '曲', '音楽', 'Song', 'Music', 'Cover']
        return any(indicator in keyword for indicator in song_indicators)
    
    def _extract_video_keywords_from_response(self, response):
        """応答から動画関連キーワードを抽出（改善版）"""
        keywords = []
        
        print(f"🔍 [キーワード抽出] 応答分析: {response[:100]}...")
        
        # 高優先度パターン（引用符で囲まれた楽曲名）
        high_priority_patterns = [
            r'「(.+?)」',  # 鍵括弧で囲まれた部分
            r'『(.+?)』',  # 二重鍵括弧で囲まれた部分
            r'"(.+?)"',   # ダブルクォート
            r"'(.+?)'",   # シングルクォート
        ]
        
        for pattern in high_priority_patterns:
            matches = re.findall(pattern, response)
            for match in matches:
                keyword = match.strip()
                if len(keyword) > 1 and self._is_valid_video_keyword(keyword):
                    keywords.append(keyword)
                    print(f"🎯 [高優先度] キーワード: {keyword}")
        
        # 中優先度パターン（文脈から推測される楽曲・アーティスト名）
        medium_priority_patterns = [
            r'(\w+)の楽曲',     # 「XXの楽曲」
            r'(\w+)の曲',       # 「XXの曲」
            r'(\w+)の新曲',     # 「XXの新曲」
            r'アーティスト.*?(\w+)',  # 「アーティストXX」
            r'(\w+)って.*?曲',   # 「XXって曲」
            r'(\w+)\s*は.*?音楽', # 「XXは音楽」
            r'(\w+)\s*を.*?聞', # 「XXを聞」
            r'(\w+)\s*が.*?好き', # 「XXが好き」
        ]
        
        for pattern in medium_priority_patterns:
            matches = re.findall(pattern, response)
            for match in matches:
                keyword = match.strip()
                if len(keyword) > 1 and self._is_valid_video_keyword(keyword):
                    keywords.append(keyword)
                    print(f"🎵 [中優先度] キーワード: {keyword}")
        
        # 低優先度パターン（一般的な単語）
        word_patterns = [
            r'[ァ-ヶー]{3,}',    # カタカナ3文字以上
            r'[A-Za-z]{3,}',     # 英語3文字以上（長めに変更）
            r'[一-龯]{2,}',      # 漢字2文字以上
        ]
        
        for pattern in word_patterns:
            matches = re.findall(pattern, response)
            for match in matches:
                keyword = match.strip()
                if self._is_valid_video_keyword(keyword) and keyword not in keywords:
                    keywords.append(keyword)
                    print(f"💭 [低優先度] キーワード: {keyword}")
        
        # 重複除去と優先度順ソート
        unique_keywords = []
        seen = set()
        
        for keyword in keywords:
            if keyword not in seen and len(keyword) > 1:
                unique_keywords.append(keyword)
                seen.add(keyword)
        
        print(f"🔍 [キーワード抽出] 完了: {unique_keywords}")
        return unique_keywords[:10]  # 最大10個まで
    
    def _is_valid_video_keyword(self, keyword):
        """キーワードが動画検索に適しているかチェック"""
        if not keyword or len(keyword) <= 1:
            return False
        
        # 除外すべき一般的な単語
        excluded_words = {
            'です', 'ます', 'だと', '思い', 'かも', 'けど', 'から', 'ので',
            'という', 'として', 'について', 'みたい', 'ような', 'どう',
            'はい', 'いえ', 'すみ', 'ごめん', 'ありがと', 'よろしく',
            'こんにちは', 'おはよう', 'こんばんは', 'さよなら'
        }
        
        # 部分一致チェック
        for excluded in excluded_words:
            if excluded in keyword:
                return False
        
        # 数字のみの場合は除外
        if keyword.isdigit():
            return False
        
        return True
    
    def _filter_mentioned_videos(self, videos, setsuna_response):
        """せつなの応答に言及された動画のみフィルタリング"""
        mentioned_videos = []
        print(f"🔍 [フィルタデバッグ] 応答文: {setsuna_response[:100]}...")
        
        for i, video in enumerate(videos):
            title = video.get('title', '')
            channel = video.get('channel', '')
            
            # デバッグ: 各動画のチェック結果を表示
            is_mentioned = self._is_video_mentioned(title, channel, setsuna_response)
            print(f"🔍 [フィルタデバッグ] 動画{i+1}: {title[:30]}... → {'言及あり' if is_mentioned else '言及なし'}")
            
            # タイトルまたはチャンネル名が応答に含まれているかチェック
            if is_mentioned:
                mentioned_videos.append(video)
        
        return mentioned_videos
    
    def _is_video_mentioned(self, title, channel, response):
        """動画がせつなの応答で言及されているかチェック"""
        if not title or not response:
            return False
        
        # タイトルの主要部分を抽出（記号や括弧を除去）
        clean_title = re.sub(r'[【】\[\]()（）\-\|｜]', ' ', title)
        title_words = [word.strip() for word in clean_title.split() if len(word.strip()) > 1]
        
        # チャンネル名の主要部分を抽出
        clean_channel = re.sub(r'[【】\[\]()（）\-\|｜]', ' ', channel) if channel else ''
        channel_words = [word.strip() for word in clean_channel.split() if len(word.strip()) > 1]
        
        # 応答文内でのマッチング
        for word in title_words + channel_words:
            if len(word) > 2 and word in response:
                return True
        
        return False
    
    def _update_url_display(self, videos):
        """URL表示エリアの表示・更新"""
        print(f"🔍 [表示デバッグ] _update_url_display呼び出し: {len(videos)}件")
        
        # URL表示エリアを表示
        self.url_frame.pack(fill=tk.X, padx=5, pady=(0, 5), before=self.input_frame)
        print(f"🔍 [表示デバッグ] URL表示エリアをpack")
        
        # リストボックスをクリア
        self.url_listbox.delete(0, tk.END)
        self.current_video_urls.clear()
        
        # 動画情報を追加
        for i, video in enumerate(videos):
            video_id = video.get('video_id', '')
            title = video.get('title', '不明な動画')
            channel = video.get('channel', '不明なチャンネル')
            
            print(f"🔍 [表示デバッグ] 動画{i+1}: {title} (ID: {video_id})")
            
            if video_id:
                url = f"https://www.youtube.com/watch?v={video_id}"
                display_text = f"{title} - {channel}"
                
                self.url_listbox.insert(tk.END, display_text)
                self.current_video_urls.append({
                    'url': url,
                    'title': title,
                    'channel': channel,
                    'video_id': video_id
                })
                print(f"🔍 [表示デバッグ] リストに追加: {display_text}")
            else:
                print(f"🔍 [表示デバッグ] video_idが空のためスキップ")
    
    def hide_url_display(self):
        """URL表示エリアを隠す"""
        self.url_frame.pack_forget()
        self.current_video_urls.clear()
    
    def on_url_double_click(self, event):
        """URL項目のダブルクリック処理"""
        selection = self.url_listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        if index < len(self.current_video_urls):
            url_info = self.current_video_urls[index]
            url = url_info['url']
            title = url_info['title']
            
            try:
                webbrowser.open(url)
                print(f"🌐 ブラウザでYouTube動画を開きました: {title}")
                self.add_message_to_history("システム", f"動画を開きました: {title}", "info")
            except Exception as e:
                print(f"❌ ブラウザ起動エラー: {e}")
                self.add_message_to_history("システム", f"ブラウザ起動に失敗しました: {e}", "error")
    
    
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
    
    def show_context_menu(self, event):
        """右クリックコンテキストメニューを表示"""
        # 右クリックされた項目を選択
        index = self.url_listbox.nearest(event.y)
        if index < 0 or index >= self.url_listbox.size():
            return
        
        self.url_listbox.selection_clear(0, tk.END)
        self.url_listbox.selection_set(index)
        
        # 選択された動画情報を取得
        if index < len(self.current_video_urls):
            self.selected_video_for_edit = self.current_video_urls[index]
        else:
            return
        
        # コンテキストメニューを作成（改善版）
        context_menu = tk.Menu(self.root, tearoff=0)
        
        # 基本操作
        context_menu.add_command(
            label="🎬 ブラウザで開く",
            command=lambda: self.open_selected_video()
        )
        context_menu.add_command(
            label="📋 URLをコピー",
            command=lambda: self.copy_video_url()
        )
        context_menu.add_command(
            label="📄 タイトルをコピー",
            command=lambda: self.copy_video_title()
        )
        
        context_menu.add_separator()
        
        # 高度な操作
        context_menu.add_command(
            label="✏️ 動画情報を編集",
            command=lambda: self.edit_video_database()
        )
        context_menu.add_command(
            label="🔍 関連動画を検索",
            command=lambda: self.search_related_videos()
        )
        
        context_menu.add_separator()
        
        # 情報表示
        context_menu.add_command(
            label="ℹ️ 動画詳細を表示",
            command=lambda: self.show_video_details()
        )
        
        # メニューを表示
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def open_selected_video(self):
        """選択された動画をブラウザで開く"""
        if hasattr(self, 'selected_video_for_edit') and self.selected_video_for_edit:
            url = self.selected_video_for_edit['url']
            title = self.selected_video_for_edit['title']
            try:
                webbrowser.open(url)
                print(f"🌐 ブラウザでYouTube動画を開きました: {title}")
                self.add_message_to_history("システム", f"動画を開きました: {title}", "info")
            except Exception as e:
                print(f"❌ ブラウザ起動エラー: {e}")
                self.add_message_to_history("システム", f"ブラウザ起動に失敗しました: {e}", "error")
    
    def copy_video_url(self):
        """選択された動画のURLをクリップボードにコピー"""
        if hasattr(self, 'selected_video_for_edit') and self.selected_video_for_edit:
            url = self.selected_video_for_edit['url']
            try:
                self.root.clipboard_clear()
                self.root.clipboard_append(url)
                self.root.update()  # クリップボードを確実に更新
                print(f"📋 URLをクリップボードにコピーしました: {url}")
                self.add_message_to_history("システム", "動画URLをクリップボードにコピーしました", "info")
            except Exception as e:
                print(f"❌ クリップボードコピーエラー: {e}")
                self.add_message_to_history("システム", f"コピーに失敗しました: {e}", "error")
    
    def copy_video_title(self):
        """選択された動画のタイトルをクリップボードにコピー"""
        if hasattr(self, 'selected_video_for_edit') and self.selected_video_for_edit:
            title = self.selected_video_for_edit['title']
            try:
                self.root.clipboard_clear()
                self.root.clipboard_append(title)
                self.root.update()  # クリップボードを確実に更新
                print(f"📋 タイトルをクリップボードにコピーしました: {title}")
                self.add_message_to_history("システム", f"動画タイトルをコピーしました: {title}", "info")
            except Exception as e:
                print(f"❌ クリップボードコピーエラー: {e}")
                self.add_message_to_history("システム", f"コピーに失敗しました: {e}", "error")
    
    def search_related_videos(self):
        """選択された動画に関連する動画を検索"""
        if hasattr(self, 'selected_video_for_edit') and self.selected_video_for_edit:
            title = self.selected_video_for_edit['title']
            channel = self.selected_video_for_edit.get('channel', '')
            
            # タイトルから検索キーワードを抽出
            search_keywords = self._extract_search_keywords(title)
            if channel:
                search_keywords.append(channel)
            
            print(f"🔍 関連動画検索開始: {search_keywords}")
            
            try:
                if self.setsuna_chat and self.setsuna_chat.context_builder:
                    knowledge_manager = self.setsuna_chat.context_builder.knowledge_manager
                    related_videos = []
                    
                    for keyword in search_keywords[:3]:  # 最大3つのキーワードで検索
                        search_results = knowledge_manager.search_videos(keyword, limit=3)
                        for result in search_results:
                            if result not in related_videos:
                                related_videos.append(result)
                    
                    # データ構造を変換
                    display_videos = []
                    for item in related_videos[:5]:
                        if isinstance(item, dict) and 'video_id' in item and 'data' in item:
                            video_data = {
                                'video_id': item['video_id'],
                                'title': item['data']['metadata'].get('title', '不明な動画'),
                                'channel': item['data']['metadata'].get('channel_title', '不明なチャンネル'),
                                'url': f"https://www.youtube.com/watch?v={item['video_id']}"
                            }
                            display_videos.append(video_data)
                    
                    if display_videos:
                        self.show_video_urls_simple(display_videos)
                        self.add_message_to_history("システム", f"関連動画 {len(display_videos)}件を表示しました", "info")
                        print(f"🔍 関連動画検索完了: {len(display_videos)}件表示")
                    else:
                        self.add_message_to_history("システム", "関連動画が見つかりませんでした", "info")
                        print("🔍 関連動画検索: ヒットなし")
                        
            except Exception as e:
                print(f"❌ 関連動画検索エラー: {e}")
                self.add_message_to_history("システム", f"関連動画検索に失敗しました: {e}", "error")
    
    def _extract_search_keywords(self, title):
        """タイトルから検索キーワードを抽出"""
        import re
        keywords = []
        
        # 括弧内の内容を除去
        cleaned_title = re.sub(r'\([^)]*\)', '', title)
        cleaned_title = re.sub(r'\[[^\]]*\]', '', cleaned_title)
        cleaned_title = re.sub(r'【[^】]*】', '', cleaned_title)
        
        # カタカナ（2文字以上）
        katakana_parts = re.findall(r'[ァ-ヶー]{2,}', cleaned_title)
        keywords.extend(katakana_parts)
        
        # 英語（2文字以上）
        english_parts = re.findall(r'[A-Za-z]{2,}', cleaned_title)
        keywords.extend(english_parts)
        
        # 漢字（2文字以上）
        kanji_parts = re.findall(r'[一-龯]{2,}', cleaned_title)
        keywords.extend(kanji_parts)
        
        return keywords[:5]  # 最大5個まで
    
    def show_video_details(self):
        """選択された動画の詳細情報を表示"""
        if hasattr(self, 'selected_video_for_edit') and self.selected_video_for_edit:
            video = self.selected_video_for_edit
            
            # 詳細情報ダイアログを作成
            detail_window = tk.Toplevel(self.root)
            detail_window.title("動画詳細情報")
            detail_window.geometry("500x400")
            detail_window.resizable(True, True)
            
            # メインフレーム
            main_frame = ttk.Frame(detail_window, padding=10)
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            # タイトル
            ttk.Label(main_frame, text="🎬 動画詳細情報", font=('Arial', 14, 'bold')).pack(pady=(0, 10))
            
            # 詳細情報フレーム
            details_frame = ttk.LabelFrame(main_frame, text="基本情報", padding=10)
            details_frame.pack(fill=tk.X, pady=(0, 10))
            
            # 情報表示
            info_items = [
                ("タイトル", video.get('title', '不明')),
                ("チャンネル", video.get('channel', '不明')),
                ("動画ID", video.get('video_id', '不明')),
                ("URL", video.get('url', '不明')),
                ("マッチスコア", f"{video.get('match_score', 0):.2f}" if 'match_score' in video else "N/A")
            ]
            
            for label, value in info_items:
                row_frame = ttk.Frame(details_frame)
                row_frame.pack(fill=tk.X, pady=2)
                
                ttk.Label(row_frame, text=f"{label}:", font=('Arial', 9, 'bold')).pack(side=tk.LEFT)
                ttk.Label(row_frame, text=str(value), font=('Arial', 9)).pack(side=tk.LEFT, padx=(10, 0))
            
            # ボタンフレーム
            button_frame = ttk.Frame(main_frame)
            button_frame.pack(fill=tk.X, pady=(10, 0))
            
            ttk.Button(button_frame, text="🎬 ブラウザで開く", 
                      command=lambda: self._open_url_from_detail(video['url'])).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(button_frame, text="📋 URLコピー", 
                      command=lambda: self._copy_to_clipboard_from_detail(video['url'])).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(button_frame, text="閉じる", command=detail_window.destroy).pack(side=tk.RIGHT)
            
            print(f"ℹ️ 動画詳細表示: {video.get('title', '不明')}")
    
    def _open_url_from_detail(self, url):
        """詳細ダイアログからURLを開く"""
        try:
            webbrowser.open(url)
            print(f"🌐 詳細ダイアログからブラウザで開きました: {url}")
        except Exception as e:
            print(f"❌ ブラウザ起動エラー: {e}")
    
    def _copy_to_clipboard_from_detail(self, text):
        """詳細ダイアログからクリップボードにコピー"""
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.root.update()
            print(f"📋 詳細ダイアログからクリップボードにコピー: {text[:50]}...")
        except Exception as e:
            print(f"❌ クリップボードコピーエラー: {e}")
    
    def edit_video_database(self):
        """動画データベース編集ダイアログを開く"""
        if not hasattr(self, 'selected_video_for_edit') or not self.selected_video_for_edit:
            return
        
        video_info = self.selected_video_for_edit
        video_id = video_info.get('video_id', '')
        
        if not video_id:
            messagebox.showerror("エラー", "動画IDが取得できません")
            return
        
        # 編集ダイアログを開く
        self.open_video_edit_dialog(video_id, video_info)
    
    def open_video_edit_dialog(self, video_id, video_info):
        """動画編集ダイアログを開く"""
        # データベースから詳細情報を取得
        if not self.setsuna_chat or not self.setsuna_chat.context_builder:
            messagebox.showerror("エラー", "YouTube知識システムが利用できません")
            return
        
        knowledge_manager = self.setsuna_chat.context_builder.knowledge_manager
        video_data = knowledge_manager.knowledge_db.get("videos", {}).get(video_id, {})
        
        if not video_data:
            messagebox.showerror("エラー", "動画データが見つかりません")
            return
        
        # 編集ダイアログウィンドウを作成
        dialog = tk.Toplevel(self.root)
        dialog.title(f"動画情報編集 - {video_info['title'][:50]}...")
        dialog.geometry("800x600")
        dialog.resizable(True, True)
        
        # メインフレーム
        main_frame = ttk.Frame(dialog, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # タイトル
        title_label = ttk.Label(
            main_frame,
            text="🎬 YouTube動画データベース編集",
            font=('Arial', 14, 'bold')
        )
        title_label.pack(pady=(0, 15))
        
        # 基本情報フレーム
        basic_frame = ttk.LabelFrame(main_frame, text="基本情報", padding=10)
        basic_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 元のタイトル（読み取り専用）
        original_title = video_data.get("metadata", {}).get("title", "")
        ttk.Label(basic_frame, text="元のタイトル:").grid(row=0, column=0, sticky='w', pady=(0, 5))
        original_title_text = tk.Text(basic_frame, height=2, width=70, wrap=tk.WORD, state=tk.DISABLED)
        original_title_text.grid(row=0, column=1, sticky='ew', pady=(0, 5))
        original_title_text.config(state=tk.NORMAL)
        original_title_text.insert('1.0', original_title)
        original_title_text.config(state=tk.DISABLED)
        
        # チャンネル（読み取り専用）
        channel_name = video_data.get("metadata", {}).get("channel_title", "")
        ttk.Label(basic_frame, text="チャンネル:").grid(row=1, column=0, sticky='w', pady=(0, 5))
        channel_label = ttk.Label(basic_frame, text=channel_name, font=('Arial', 10))
        channel_label.grid(row=1, column=1, sticky='w', pady=(0, 5))
        
        # カスタム情報フレーム
        custom_frame = ttk.LabelFrame(main_frame, text="カスタム情報（編集可能）", padding=10)
        custom_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # 既存のカスタム情報を取得
        custom_info = video_data.get("custom_info", {})
        
        # 楽曲名入力
        ttk.Label(custom_frame, text="楽曲名:").grid(row=0, column=0, sticky='w', pady=(0, 5))
        manual_title_var = tk.StringVar(value=custom_info.get("manual_title", ""))
        manual_title_entry = ttk.Entry(custom_frame, textvariable=manual_title_var, width=50)
        manual_title_entry.grid(row=0, column=1, sticky='ew', pady=(0, 5))
        
        # アーティスト名入力
        ttk.Label(custom_frame, text="アーティスト名:").grid(row=1, column=0, sticky='w', pady=(0, 5))
        manual_artist_var = tk.StringVar(value=custom_info.get("manual_artist", ""))
        manual_artist_entry = ttk.Entry(custom_frame, textvariable=manual_artist_var, width=50)
        manual_artist_entry.grid(row=1, column=1, sticky='ew', pady=(0, 5))
        
        # 楽曲の日本語読み入力
        ttk.Label(custom_frame, text="楽曲の日本語読み:").grid(row=2, column=0, sticky='w', pady=(0, 5))
        title_pronunciations = custom_info.get("japanese_pronunciations", [])
        title_pronunciations_var = tk.StringVar(value=", ".join(title_pronunciations))
        title_pronunciations_entry = ttk.Entry(custom_frame, textvariable=title_pronunciations_var, width=50)
        title_pronunciations_entry.grid(row=2, column=1, sticky='ew', pady=(0, 5))
        
        # アーティストの日本語読み入力
        ttk.Label(custom_frame, text="アーティストの日本語読み:").grid(row=3, column=0, sticky='w', pady=(0, 5))
        artist_pronunciations = custom_info.get("artist_pronunciations", [])
        artist_pronunciations_var = tk.StringVar(value=", ".join(artist_pronunciations))
        artist_pronunciations_entry = ttk.Entry(custom_frame, textvariable=artist_pronunciations_var, width=50)
        artist_pronunciations_entry.grid(row=3, column=1, sticky='ew', pady=(0, 5))
        
        # 検索キーワード入力
        ttk.Label(custom_frame, text="検索キーワード:").grid(row=4, column=0, sticky='w', pady=(0, 5))
        search_keywords = custom_info.get("search_keywords", [])
        search_keywords_var = tk.StringVar(value=", ".join(search_keywords))
        search_keywords_entry = ttk.Entry(custom_frame, textvariable=search_keywords_var, width=50)
        search_keywords_entry.grid(row=4, column=1, sticky='ew', pady=(0, 5))
        
        # ヘルプテキスト
        help_frame = ttk.Frame(custom_frame)
        help_frame.grid(row=5, column=0, columnspan=2, sticky='ew', pady=(10, 0))
        
        help_text = """
💡 編集のヒント:
• 楽曲名: せつなが検索しやすい短縮形を入力 (例: "XOXO")
• アーティスト名: 正式なアーティスト名を入力 (例: "TRiNITY") 
• 楽曲の日本語読み: 音声認識でのカタカナ読みをカンマ区切りで入力 (例: "エックスオーエックスオー, エクスオクスオ")
• アーティストの日本語読み: 音声認識でのカタカナ読みをカンマ区切りで入力 (例: "トリニティ, トリニティー")
• 検索キーワード: 追加の検索用語をカンマ区切りで入力 (例: "ばちゃうた, にじさんじ音楽")
        """
        help_label = ttk.Label(help_frame, text=help_text.strip(), font=('Arial', 9), foreground='gray')
        help_label.pack(anchor='w')
        
        # ボタンフレーム
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        def save_changes():
            """変更を保存"""
            try:
                # カスタム情報を更新
                new_custom_info = {
                    "manual_title": manual_title_var.get().strip(),
                    "manual_artist": manual_artist_var.get().strip(),
                    "japanese_pronunciations": [r.strip() for r in title_pronunciations_var.get().split(",") if r.strip()],
                    "artist_pronunciations": [r.strip() for r in artist_pronunciations_var.get().split(",") if r.strip()],
                    "search_keywords": [k.strip() for k in search_keywords_var.get().split(",") if k.strip()],
                    "last_edited": datetime.now().isoformat(),
                    "edit_count": custom_info.get("edit_count", 0) + 1
                }
                
                # データベースを更新
                video_data["custom_info"] = new_custom_info
                
                # ファイルに保存
                self.save_video_database(knowledge_manager)
                
                # 音声テキスト変換キャッシュをクリア
                if self.speech_text_converter:
                    self.speech_text_converter.clear_cache()
                    print("🔄 [音声変換] キャッシュクリア: データベース更新反映")
                
                messagebox.showinfo("成功", "動画情報が正常に保存されました")
                print(f"✅ 動画情報編集完了: {video_id}")
                
                # ダイアログを閉じる
                dialog.destroy()
                
                # URL表示を更新
                self.refresh_url_display()
                
            except Exception as e:
                messagebox.showerror("エラー", f"保存に失敗しました: {e}")
                print(f"❌ 動画情報保存エラー: {e}")
        
        def cancel_edit():
            """編集をキャンセル"""
            dialog.destroy()
        
        # 保存ボタン
        save_button = ttk.Button(
            button_frame,
            text="💾 保存",
            command=save_changes
        )
        save_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # キャンセルボタン
        cancel_button = ttk.Button(
            button_frame,
            text="❌ キャンセル",
            command=cancel_edit
        )
        cancel_button.pack(side=tk.LEFT)
        
        # プレビューボタン
        def preview_changes():
            """変更のプレビュー"""
            preview_text = f"""
楽曲名: {manual_title_var.get() or '(未設定)'}
アーティスト: {manual_artist_var.get() or '(未設定)'}
楽曲の日本語読み: {title_pronunciations_var.get() or '(未設定)'}
アーティストの日本語読み: {artist_pronunciations_var.get() or '(未設定)'}
検索キーワード: {search_keywords_var.get() or '(未設定)'}
            """
            messagebox.showinfo("プレビュー", preview_text.strip())
        
        preview_button = ttk.Button(
            button_frame,
            text="👁️ プレビュー",
            command=preview_changes
        )
        preview_button.pack(side=tk.RIGHT)
        
        # グリッドの列幅設定
        custom_frame.columnconfigure(1, weight=1)
        
        # フォーカスを楽曲名入力に設定
        manual_title_entry.focus_set()
        
        print(f"🎬 動画編集ダイアログを開きました: {video_id}")
    
    def save_video_database(self, knowledge_manager):
        """動画データベースをファイルに保存"""
        try:
            import json
            from pathlib import Path
            
            # データベースファイルパス
            db_path = knowledge_manager.knowledge_db_path
            
            # データベースを保存
            with open(db_path, 'w', encoding='utf-8') as f:
                json.dump(knowledge_manager.knowledge_db, f, ensure_ascii=False, indent=2)
            
            print(f"✅ データベース保存完了: {db_path}")
            
        except Exception as e:
            print(f"❌ データベース保存エラー: {e}")
            raise
    
    def refresh_url_display(self):
        """URL表示エリアを更新"""
        try:
            # 現在表示中の動画情報を再取得
            if hasattr(self, 'current_video_urls') and self.current_video_urls:
                print("🔄 URL表示エリアを更新中...")
                # 現在の表示を維持（より詳細な更新は将来実装）
                print("✅ URL表示エリア更新完了")
        except Exception as e:
            print(f"❌ URL表示更新エラー: {e}")
    
    @get_monitor().monitor_function("voice_recognition")
    def _voice_recognition(self):
        """音声認識実行（キー押下中録音、リリース時停止）"""
        self.logger.info("voice_chat_gui", "_voice_recognition", "音声認識処理開始")
        
        if not self.voice_recognizer or not self.microphone:
            error_msg = "音声認識システムが初期化されていません"
            self.logger.error("voice_chat_gui", "_voice_recognition", error_msg)
            return error_msg
        
        import pyaudio
        import wave
        import threading
        import time
        import tempfile
        import os
        
        try:
            print("🎤 録音開始（キーを押している間録音）...")
            
            # 録音設定
            chunk = 1024
            format = pyaudio.paInt16
            channels = 1
            rate = 44100
            
            p = pyaudio.PyAudio()
            
            # 録音データを格納するリスト
            frames = []
            recording_active = True
            
            def record_audio():
                """バックグラウンドで録音を実行"""
                nonlocal recording_active
                
                stream = p.open(format=format,
                              channels=channels,
                              rate=rate,
                              input=True,
                              frames_per_buffer=chunk)
                
                print("🎤 話してください（キーを離すと終了）...")
                
                while self.listening and recording_active:
                    try:
                        data = stream.read(chunk, exception_on_overflow=False)
                        frames.append(data)
                    except Exception as e:
                        print(f"⚠️ 録音チャンクエラー: {e}")
                        break
                
                stream.stop_stream()
                stream.close()
                recording_active = False
                print("✅ 録音停止")
            
            # バックグラウンドで録音開始
            recording_thread = threading.Thread(target=record_audio, daemon=True)
            recording_thread.start()
            
            # キーリリースまで待機
            while self.listening:
                time.sleep(0.05)  # 50ms間隔でより高頻度チェック
            
            print("🔑 キーリリース検出、録音停止中...")
            recording_active = False
            
            # 録音スレッドの完了を待つ
            recording_thread.join(timeout=1.0)
            
            p.terminate()
            
            # 録音データが十分にあるかチェック
            if len(frames) < 10:  # 最低限のフレーム数をチェック
                print("❌ 録音時間が短すぎました")
                return "録音時間が短すぎました"
            
            # 一時ファイルに音声データを保存
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_path = temp_file.name
                
                wf = wave.open(temp_path, 'wb')
                wf.setnchannels(channels)
                wf.setsampwidth(p.get_sample_size(format))
                wf.setframerate(rate)
                wf.writeframes(b''.join(frames))
                wf.close()
            
            # 音声認識実行
            print("🌐 音声認識中...")
            self.update_voice_status("音声認識中...")
            
            # 音声ファイルから認識
            with sr.AudioFile(temp_path) as source:
                audio = self.voice_recognizer.record(source)
                
            # 一時ファイルを削除
            os.unlink(temp_path)
            
            text = self.voice_recognizer.recognize_google(audio, language="ja-JP")
            print(f"✅ 認識成功: '{text}'")
            self.logger.info("voice_chat_gui", "_voice_recognition", "音声認識成功", {
                "recognized_text": text,
                "text_length": len(text)
            })
            return text
            
        except sr.UnknownValueError:
            error_msg = "音声が聞き取れませんでした"
            print("❌ 音声認識失敗（音声不明瞭）")
            self.logger.warning("voice_chat_gui", "_voice_recognition", "音声認識失敗: 音声不明瞭")
            return error_msg
        except sr.RequestError as e:
            error_msg = "音声認識サービスエラー"
            print(f"❌ API呼び出しエラー: {e}")
            self.logger.error("voice_chat_gui", "_voice_recognition", "音声認識API呼び出しエラー", {
                "error": str(e)
            })
            return error_msg
        except Exception as e:
            print(f"❌ 録音エラー: {e}")
            self.logger.error("voice_chat_gui", "_voice_recognition", "録音エラー", {
                "error": str(e)
            })
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
                
                # 2. 応答連携強化: 現在は無効化（シンプル化のため）
                mentioned_videos = []  # 応答解析を無効化
                
                # Phase 1: コンテキストデータから直接URL表示（音声入力）
                try:
                    print(f"🔗 [URL表示] 音声入力: コンテキストデータから動画取得開始")
                    
                    # せつなチャットから最後のコンテキストデータを取得
                    context_data = self.setsuna_chat.get_last_context_data()
                    
                    # 2. 応答連携強化: 言及動画が見つかった場合は優先表示
                    if mentioned_videos:
                        print(f"🔗 [URL表示] 応答言及動画を優先表示: {len(mentioned_videos)}件")
                        self.show_video_urls_simple(mentioned_videos)
                    elif context_data and ('videos' in context_data or 'external_videos' in context_data):
                        # Phase 2: DB動画と外部動画を統合して表示
                        all_display_videos = []
                        
                        # DB内動画の変換
                        db_videos = context_data.get('videos', [])
                        if db_videos:
                            db_display_videos = self._convert_context_videos_to_display_format(db_videos)
                            all_display_videos.extend(db_display_videos)
                            print(f"🔗 [URL表示] DB動画: {len(db_display_videos)}件")
                        
                        # 外部動画の変換
                        external_videos = context_data.get('external_videos', [])
                        if external_videos:
                            external_display_videos = self._convert_context_videos_to_display_format(external_videos)
                            all_display_videos.extend(external_display_videos)
                            print(f"🔗 [URL表示] 外部動画: {len(external_display_videos)}件")
                        
                        if all_display_videos:
                            print(f"🔗 [URL表示] 統合表示: 合計{len(all_display_videos)}件")
                            self.show_video_urls_simple(all_display_videos)
                        else:
                            print(f"🔗 [URL表示] 動画関連だが検索結果なし")
                            self.url_listbox.delete(0, tk.END)
                            self.url_listbox.insert(tk.END, "該当する動画が見つかりませんでした")
                    else:
                        print(f"🔗 [URL表示] 非動画関連クエリのためURL表示スキップ")
                        # 非動画関連の場合はURL表示をクリア
                        self.url_listbox.delete(0, tk.END)
                    
                except Exception as e:
                    print(f"❌ [URL表示] エラー: {e}")
                    # エラー時はメッセージ表示
                    self.url_listbox.delete(0, tk.END)
                    self.url_listbox.insert(tk.END, f"エラー: {e}")
            else:
                response = "申し訳ありません。システムが初期化されていません。"
            
            # UIスレッドで履歴更新
            self.root.after(0, lambda: self.add_message_to_history("せつな", response, "voice"))
            
            # 音声合成実行
            if self.voice_synthesizer:
                self.update_voice_status("音声合成中...")
                
                # 音声合成用にテキストを変換
                speech_text = response
                if self.speech_text_converter:
                    speech_text = self.speech_text_converter.convert_for_speech(response)
                    if speech_text != response:
                        print(f"🔄 [音声変換] テキスト変換実行済み")
                
                wav_path = self.voice_synthesizer.synthesize_voice(speech_text)
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
    
    # ==============================
    # 動画学習関連メソッド
    # ==============================
    
    def start_video_learning(self):
        """動画学習を開始"""
        url = self.url_entry.get().strip()
        
        if not url:
            messagebox.showwarning("警告", "YouTubeのURLを入力してください")
            return
        
        # URL形式の簡易チェック
        if "youtube.com/watch" not in url and "youtu.be/" not in url:
            messagebox.showerror("エラー", "有効なYouTubeのURLを入力してください")
            return
        
        # ボタンを無効化
        self.learn_button.config(state="disabled")
        self.url_entry.config(state="disabled")
        
        # プログレスリセット
        self.progress_var.set(0)
        self.progress_status.config(text="学習準備中...")
        
        # せつなのコメント更新
        self.setsuna_comment.config(text="わぁ、新しい動画だね！どんな内容か分析してみるよ...")
        
        # 別スレッドで学習処理を実行
        learning_thread = threading.Thread(
            target=self._process_video_learning,
            args=(url,),
            daemon=True
        )
        learning_thread.start()
    
    def _process_video_learning(self, url):
        """動画学習処理（バックグラウンド実行）"""
        try:
            # Phase 1: URL解析（20%）
            self.root.after(0, lambda: self._update_learning_progress(20, "URL解析中..."))
            video_id = self._extract_video_id(url)
            
            if not video_id:
                self.root.after(0, lambda: self._learning_error("URLからビデオIDを抽出できませんでした"))
                return
            
            # Phase 2: YouTubeKnowledgeManager初期化（40%）
            self.root.after(0, lambda: self._update_learning_progress(40, "YouTube APIアクセス準備中..."))
            
            # YouTubeKnowledgeManagerをインポートして使用
            try:
                from core.youtube_knowledge_manager import YouTubeKnowledgeManager
                yt_manager = YouTubeKnowledgeManager()
            except Exception as e:
                self.root.after(0, lambda: self._learning_error(f"YouTube知識管理システムの初期化に失敗: {e}"))
                return
            
            # Phase 3: 動画情報取得（60%）
            self.root.after(0, lambda: self._update_learning_progress(60, "動画情報を取得中..."))
            
            # 手動で動画を追加する既存機能を活用
            try:
                result = yt_manager.add_manual_video(video_id)
                if not result.get('success', False):
                    self.root.after(0, lambda: self._learning_error(f"動画の追加に失敗: {result.get('message', '不明なエラー')}"))
                    return
            except Exception as e:
                self.root.after(0, lambda: self._learning_error(f"動画追加処理エラー: {e}"))
                return
            
            # Phase 4: 画像保存処理（80%）
            self.root.after(0, lambda: self._update_learning_progress(80, "関連画像を保存中..."))
            
            # 選択された画像がある場合は保存
            if self.selected_images:
                try:
                    self.current_video_id = video_id
                    image_count = 0
                    
                    for image_info in self.selected_images:
                        # 画像をVideoImageManagerで保存
                        saved_image = self.image_manager.save_image(
                            video_id=video_id,
                            source_file_path=image_info['file_path'],
                            user_description=image_info.get('description', '')
                        )
                        
                        if saved_image:
                            # YouTubeKnowledgeManagerのデータベースに画像情報を追加
                            yt_manager.add_video_image(video_id, saved_image)
                            image_count += 1
                        else:
                            print(f"[GUI] ⚠️ 画像保存失敗: {image_info['file_path']}")
                    
                    print(f"[GUI] ✅ 画像保存完了: {image_count}枚")
                    
                except Exception as e:
                    print(f"[GUI] ❌ 画像保存エラー: {e}")
            
            # Phase 5: 完了（100%）
            self.root.after(0, lambda: self._update_learning_progress(100, "学習完了！"))
            
            # 結果表示
            video_info = result.get('video_info', {})
            self.root.after(0, lambda: self._display_learning_result(video_info, url))
            
        except Exception as e:
            self.root.after(0, lambda: self._learning_error(f"予期しないエラー: {e}"))
    
    def _extract_video_id(self, url):
        """YouTubeのURLからビデオIDを抽出"""
        import re
        
        # youtube.com/watch?v=VIDEO_ID 形式
        match = re.search(r'watch\?v=([a-zA-Z0-9_-]{11})', url)
        if match:
            return match.group(1)
        
        # youtu.be/VIDEO_ID 形式
        match = re.search(r'youtu\.be/([a-zA-Z0-9_-]{11})', url)
        if match:
            return match.group(1)
        
        return None
    
    def _update_learning_progress(self, progress, status):
        """学習進捗を更新（メインスレッドで実行）"""
        self.progress_var.set(progress)
        self.progress_status.config(text=status)
        self.root.update_idletasks()
    
    def _learning_error(self, error_message):
        """学習エラー処理（メインスレッドで実行）"""
        self.progress_status.config(text=f"エラー: {error_message}")
        self.setsuna_comment.config(text="うーん、何か問題があったみたい...もう一度試してみてくれる？")
        
        # ボタンを有効化
        self.learn_button.config(state="normal")
        self.url_entry.config(state="normal")
        
        # エラーメッセージ表示
        messagebox.showerror("学習エラー", error_message)
    
    def _display_learning_result(self, video_info, url):
        """学習結果を表示（メインスレッドで実行）"""
        # 結果テキストエリアに結果を表示
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        
        # 画像保存情報も追加
        image_info_text = ""
        if self.selected_images:
            image_count = len(self.selected_images)
            image_info_text = f"\n📸 関連画像: {image_count}枚保存完了"
        
        result_text = f"""📺 学習完了！新しい動画を覚えました

🎵 タイトル: {video_info.get('title', '不明')}
👤 チャンネル: {video_info.get('channel_title', '不明')}
📅 公開日: {video_info.get('published_at', '不明')}
⏰ 時間: {video_info.get('duration', '不明')}
👀 再生回数: {video_info.get('view_count', '不明')}{image_info_text}

🔗 URL: {url}

✨ この動画について、せつなと会話できるようになりました！
   チャットタブで「{video_info.get('title', 'この動画')}について聞かせて」と話しかけてみてください。

📝 学習時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        self.result_text.insert(tk.END, result_text)
        self.result_text.config(state=tk.DISABLED)
        
        # せつなのコメント更新
        comments = [
            f"わぁ、「{video_info.get('title', '新しい動画')}」を覚えたよ！今度一緒に話そうね♪",
            f"「{video_info.get('title', '新しい動画')}」、面白そう！どんな内容か気になるなぁ...",
            f"ありがとう！「{video_info.get('title', '新しい動画')}」について、いろいろ聞かせてね！",
            "新しい動画を教えてくれて嬉しいな！今度チャットで詳しく話そう♪"
        ]
        
        import random
        selected_comment = random.choice(comments)
        self.setsuna_comment.config(text=selected_comment)
        
        # ボタンを有効化
        self.learn_button.config(state="normal")
        self.url_entry.config(state="normal")
        
        # URL入力フィールドをクリア
        self.url_entry.delete(0, tk.END)
        
        # 選択画像をクリア
        self.clear_selected_images()
        
        # 一時ファイルクリーンアップ
        self._cleanup_temp_clipboard_files()
        
        # 完了メッセージ
        messagebox.showinfo("学習完了", f"動画「{video_info.get('title', '新しい動画')}」の学習が完了しました！")
    
    def clear_learning_results(self):
        """学習結果をクリア"""
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.config(state=tk.DISABLED)
        
        # プログレスリセット
        self.progress_var.set(0)
        self.progress_status.config(text="待機中...")
        
        # せつなのコメントリセット
        self.setsuna_comment.config(text="新しい動画を教えてくれたら、一緒に楽しめそうだね！")
    
    def show_learning_history(self):
        """学習履歴を表示"""
        try:
            from core.youtube_knowledge_manager import YouTubeKnowledgeManager
            yt_manager = YouTubeKnowledgeManager()
            
            # 手動追加された動画の履歴を取得
            manual_videos = yt_manager.get_manual_videos()
            
            if not manual_videos:
                messagebox.showinfo("学習履歴", "まだ手動で学習した動画はありません。")
                return
            
            # 履歴表示用のダイアログを作成
            history_window = tk.Toplevel(self.root)
            history_window.title("🎵 動画学習履歴")
            history_window.geometry("600x400")
            history_window.transient(self.root)
            history_window.grab_set()
            
            # 履歴リスト表示
            ttk.Label(history_window, text="📚 学習済み動画一覧", font=('Arial', 12, 'bold')).pack(pady=10)
            
            # リストボックス
            listbox_frame = ttk.Frame(history_window)
            listbox_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
            
            history_listbox = tk.Listbox(listbox_frame, font=('Arial', 10))
            scrollbar = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL, command=history_listbox.yview)
            history_listbox.configure(yscrollcommand=scrollbar.set)
            
            for i, video in enumerate(manual_videos[-20:], 1):  # 最新20件
                title = video.get('title', '不明なタイトル')
                channel = video.get('channel_title', '不明なチャンネル')
                display_text = f"{i:2d}. {title} - {channel}"
                history_listbox.insert(tk.END, display_text)
            
            history_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # 閉じるボタン
            close_button = ttk.Button(history_window, text="閉じる", command=history_window.destroy)
            close_button.pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("エラー", f"学習履歴の取得に失敗しました: {e}")
    
    
    def run(self):
        """GUI実行"""
        print("🚀 GUI開始")
        
        # ウィンドウ閉じるときの処理
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self._on_closing()
    
    # Phase 2B: 画像分析関連メソッド
    
    def start_image_analysis(self):
        """画像分析開始"""
        try:
            if not self.selected_images:
                messagebox.showwarning("警告", "分析する画像が選択されていません。")
                return
            
            if not self.youtube_manager or not self.context_builder:
                messagebox.showerror("エラー", "Phase 2Bシステムが初期化されていません。")
                return
            
            # ボタンを無効化
            self.analyze_button.config(state="disabled")
            self.analysis_status_label.config(text="分析中...", foreground="orange")
            
            # 別スレッドで分析実行
            threading.Thread(target=self._process_image_analysis, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("エラー", f"画像分析開始エラー: {e}")
            self.analyze_button.config(state="normal")
            self.analysis_status_label.config(text="エラー発生", foreground="red")
    
    def _process_image_analysis(self):
        """画像分析処理（別スレッド）"""
        try:
            print(f"🔍 Phase 2B: 画像分析開始 ({len(self.selected_images)}枚)")
            
            # YouTube URLからvideo_idを取得
            video_id = self._get_current_video_id()
            if not video_id:
                self._update_analysis_ui("エラー: 動画IDが取得できません。YouTube URLを入力してください。", "error")
                return
            
            analysis_results = []
            
            # 各画像を分析
            for i, image_path in enumerate(self.selected_images):
                self.root.after(0, lambda i=i: self.analysis_status_label.config(
                    text=f"画像 {i+1}/{len(self.selected_images)} 分析中..."
                ))
                
                print(f"🖼️ 画像分析: {image_path}")
                
                # ImageAnalyzerで分析実行
                if self.youtube_manager.image_analyzer:
                    # 動画情報取得
                    video_info = self._get_video_info_for_analysis(video_id)
                    
                    # 分析実行
                    result = self.youtube_manager.image_analyzer.analyze_with_video_context(
                        image_path, video_info
                    )
                    analysis_results.append({
                        'image_path': image_path,
                        'analysis': result
                    })
                    
                    print(f"✅ 分析完了: {result.get('description', '')}[:100]...")
                else:
                    print("⚠️ ImageAnalyzerが初期化されていません")
                    # モックデータを使用
                    result = {
                        'description': f'モック分析結果: {os.path.basename(image_path)}',
                        'metadata': {'estimated_cost': 0.01, 'tokens_used': 100}
                    }
                    analysis_results.append({
                        'image_path': image_path,
                        'analysis': result
                    })
            
            # 高度な関連性分析実行（モックデータ使用）
            self.root.after(0, lambda: self.analysis_status_label.config(
                text="高度な関連性分析中..."
            ))
            
            # モックデータで高度な関連性分析をデモ
            advanced_analysis = self._perform_mock_advanced_analysis(analysis_results)
            
            # 結果をキャッシュ
            self.analysis_results = analysis_results
            
            # UI更新
            self._update_analysis_ui(analysis_results, "success", advanced_analysis)
            
            print("✅ Phase 2B: 画像分析完了")
            
        except Exception as e:
            print(f"❌ 画像分析エラー: {e}")
            self._update_analysis_ui(f"分析エラー: {e}", "error")
    
    def _get_current_video_id(self):
        """現在のYouTube URLからvideo_idを抽出"""
        try:
            url = self.url_entry.get().strip()
            if not url:
                return None
            
            # YouTube URLからvideo_idを抽出
            import re
            patterns = [
                r'(?:youtube\.com/watch\?v=|youtu\.be/)([\w-]+)',
                r'youtube\.com/embed/([\w-]+)',
                r'youtube\.com/v/([\w-]+)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, url)
                if match:
                    return match.group(1)
            
            return None
        except Exception as e:
            print(f"⚠️ video_id抽出エラー: {e}")
            return None
    
    def _get_video_info_for_analysis(self, video_id):
        """分析用の動画情報を取得"""
        try:
            # YouTubeマネージャーから動画情報を取得
            video_context = self.youtube_manager.get_video_context(video_id)
            if video_context:
                return video_context
            
            # フォールバック: ダミー情報
            return {
                'title': f'動画ID: {video_id}',
                'channel_title': '不明',
                'description': 'YouTube動画の分析',
                'published_at': '2025-07-04T00:00:00Z',
                'view_count': 0
            }
        except Exception as e:
            print(f"⚠️ 動画情報取得エラー: {e}")
            return {
                'title': '動画タイトル不明',
                'channel_title': '不明',
                'description': '分析対象動画',
                'published_at': '2025-07-04T00:00:00Z',
                'view_count': 0
            }
    
    def _perform_mock_advanced_analysis(self, analysis_results):
        """モックの高度な関連性分析"""
        try:
            if len(analysis_results) < 2:
                return {
                    'type': 'single_image',
                    'message': '高度な関連性分析には2枚以上の画像が必要です',
                    'coherence_score': 0.0
                }
            
            # シンプルなモック分析
            import random
            coherence_score = random.uniform(0.4, 0.9)
            
            emotions = ['明るい', '情熱的', '落ち着いた', '神秘的']
            themes = ['音楽', 'パフォーマンス', '照明・映像', '人物・表情']
            
            return {
                'type': 'advanced_analysis',
                'coherence_score': coherence_score,
                'emotion_flow': emotions[:len(analysis_results)],
                'dominant_themes': random.sample(themes, min(3, len(themes))),
                'narrative_structure': '三幕構成（導入→展開→クライマックス）' if len(analysis_results) >= 3 else '二部構成',
                'visual_similarity': f'{random.randint(60, 90)}%',
                'key_transitions': random.randint(0, 2)
            }
        except Exception as e:
            print(f"⚠️ モック分析エラー: {e}")
            return {'type': 'error', 'message': str(e)}
    
    def _update_analysis_ui(self, results, status, advanced_analysis=None):
        """分析結果でUIを更新"""
        try:
            def update_ui():
                if status == "error":
                    self.analysis_status_label.config(text="エラー発生", foreground="red")
                    self.basic_analysis_text.config(state=tk.NORMAL)
                    self.basic_analysis_text.delete(1.0, tk.END)
                    self.basic_analysis_text.insert(tk.END, results)
                    self.basic_analysis_text.config(state=tk.DISABLED)
                else:
                    # 成功時の処理
                    self.analysis_status_label.config(text=f"分析完了 ({len(results)}枚)", foreground="green")
                    
                    # 基本分析結果表示
                    self.basic_analysis_text.config(state=tk.NORMAL)
                    self.basic_analysis_text.delete(1.0, tk.END)
                    
                    for i, result_data in enumerate(results, 1):
                        analysis = result_data['analysis']
                        image_path = result_data['image_path']
                        filename = os.path.basename(image_path)
                        
                        self.basic_analysis_text.insert(tk.END, f"=== 画像 {i}: {filename} ===\n")
                        self.basic_analysis_text.insert(tk.END, f"{analysis.get('description', '分析結果なし')}\n\n")
                        
                        # メタデータ情報
                        metadata = analysis.get('metadata', {})
                        if metadata:
                            self.basic_analysis_text.insert(tk.END, f"📊 コスト: ${metadata.get('estimated_cost', 0):.4f} | ")
                            self.basic_analysis_text.insert(tk.END, f"トークン: {metadata.get('tokens_used', 0)}\n\n")
                    
                    self.basic_analysis_text.config(state=tk.DISABLED)
                    
                    # 高度な分析結果表示
                    if advanced_analysis:
                        self.advanced_analysis_text.config(state=tk.NORMAL)
                        self.advanced_analysis_text.delete(1.0, tk.END)
                        
                        if advanced_analysis['type'] == 'advanced_analysis':
                            self.advanced_analysis_text.insert(tk.END, f"🎆 高度な関連性分析結果\n\n")
                            self.advanced_analysis_text.insert(tk.END, f"📊 全体一貫性スコア: {advanced_analysis['coherence_score']:.2f}\n")
                            self.advanced_analysis_text.insert(tk.END, f"🎭 物語構造: {advanced_analysis['narrative_structure']}\n")
                            self.advanced_analysis_text.insert(tk.END, f"🎨 視覚的類似性: {advanced_analysis['visual_similarity']}\n")
                            self.advanced_analysis_text.insert(tk.END, f"🔄 重要転換点: {advanced_analysis['key_transitions']}箇所\n\n")
                            
                            self.advanced_analysis_text.insert(tk.END, f"🎨 主要テーマ:\n")
                            for theme in advanced_analysis['dominant_themes']:
                                self.advanced_analysis_text.insert(tk.END, f"  • {theme}\n")
                            
                            self.advanced_analysis_text.insert(tk.END, f"\n😊 感情の流れ:\n")
                            for emotion in advanced_analysis['emotion_flow']:
                                self.advanced_analysis_text.insert(tk.END, f"  → {emotion}\n")
                        else:
                            self.advanced_analysis_text.insert(tk.END, advanced_analysis.get('message', '高度な分析エラー'))
                        
                        self.advanced_analysis_text.config(state=tk.DISABLED)
                    
                    # コンテキスト生成ボタンを有効化
                    self.generate_context_button.config(state="normal")
                
                # 分析ボタンを再有効化
                self.analyze_button.config(state="normal")
            
            self.root.after(0, update_ui)
            
        except Exception as e:
            print(f"❌ UI更新エラー: {e}")
    
    def generate_conversation_context(self):
        """会話コンテキスト生成"""
        try:
            if not self.analysis_results:
                messagebox.showwarning("警告", "先に画像分析を実行してください。")
                return
            
            # コンテキスト生成ボタンを無効化
            self.generate_context_button.config(state="disabled")
            
            # 別スレッドでコンテキスト生成
            threading.Thread(target=self._process_context_generation, daemon=True).start()
            
        except Exception as e:
            messagebox.showerror("エラー", f"コンテキスト生成エラー: {e}")
            self.generate_context_button.config(state="normal")
    
    def _process_context_generation(self):
        """コンテキスト生成処理（別スレッド）"""
        try:
            print("💬 Phase 2B: 会話コンテキスト生成開始")
            
            # 現在のテンプレート取得
            template_type = self.template_var.get()
            
            # モックコンテキスト生成
            context = self._generate_mock_context(template_type)
            
            # キャッシュに保存
            self.generated_context = context
            
            # UI更新
            def update_context_ui():
                self.context_text.config(state=tk.NORMAL)
                self.context_text.delete(1.0, tk.END)
                self.context_text.insert(tk.END, context)
                self.context_text.config(state=tk.DISABLED)
                
                # ボタンを再有効化
                self.generate_context_button.config(state="normal")
            
            self.root.after(0, update_context_ui)
            
            print("✅ Phase 2B: 会話コンテキスト生成完了")
            
        except Exception as e:
            print(f"❌ コンテキスト生成エラー: {e}")
            self.root.after(0, lambda: self.generate_context_button.config(state="normal"))
    
    def _generate_mock_context(self, template_type):
        """モックコンテキスト生成"""
        try:
            video_id = self._get_current_video_id() or "sample_video"
            
            # テンプレート別のコンテキスト生成
            if template_type == "general_video_discussion":
                return f"""🎵 動画の魅力について話しましょう！

【画像分析結果】
{len(self.analysis_results)}枚の画像を分析しました。明るい雰囲気と情熱的な演奏が印象的ですね！

【話したいトピック】
• 映像の美しさについて
• アーティストの表現力について
• 楽曲と映像の関係について

どのシーンが一番印象に残りましたか？"""
            
            elif template_type == "music_video_comprehensive":
                return f"""🎤 音楽動画の包括的分析

【楽曲の雰囲気】
明るくエネルギッシュな作品で、聞いているだけで元気になれそうです！

【映像の見どころ】
• 照明効果の美しさ
• カメラワークの技巧さ
• アーティストの魅力的なパフォーマンス

【話し合いたいこと】
この動画の中で特に気に入った部分はありますか？"""
            
            elif template_type == "visual_analysis":
                return f"""🎨 映像表現の分析

【視覚的な特徴】
• 色彩: 暖かいトーンで統一されたパレット
• 構図: ダイナミックなアングルと安定したフレーミング
• ライティング: ドラマチックな光と影のコントラスト

【ストーリーの流れ】
三幕構成で綺麗に構成され、映像だけでも物語が伝わってきます。

映像の演出についてどう思いますか？"""
            
            elif template_type == "specific_image_focus":
                return f"""🖼️ 画像にフォーカスした分析

【画像の内容】
アーティストが情熱的に歌っているシーン。綺麗な照明とエネルギッシュな表情が印象的です。

【動画全体での位置づけ】
この画像は楽曲のクライマックス部分を表現しているようですね。

どんなところが印象的でしたか？"""
            
            else:
                return f"""🤖 AI画像分析結果

{len(self.analysis_results)}枚の画像を分析し、動画の魅力を理解しました。

この画像について、何か聞きたいことはありますか？"""
            
        except Exception as e:
            return f"コンテキスト生成エラー: {e}"
    
    def copy_context_to_clipboard(self):
        """コンテキストをクリップボードにコピー"""
        try:
            if self.generated_context:
                self.root.clipboard_clear()
                self.root.clipboard_append(self.generated_context)
                messagebox.showinfo("情報", "コンテキストをクリップボードにコピーしました。")
            else:
                messagebox.showwarning("警告", "コピーするコンテキストがありません。")
        except Exception as e:
            messagebox.showerror("エラー", f"コピーエラー: {e}")
    
    def use_context_in_chat(self):
        """生成したコンテキストをチャットで使用"""
        try:
            if self.generated_context:
                # チャットタブに切り替え
                self.notebook.select(0)  # チャットタブは最初のタブ
                
                # テキスト入力エリアにコンテキストを設定
                self.text_input.delete("1.0", tk.END)
                self.text_input.insert(tk.END, self.generated_context)
                
                messagebox.showinfo("情報", "コンテキストをチャットに設定しました。")
            else:
                messagebox.showwarning("警告", "使用するコンテキストがありません。")
        except Exception as e:
            messagebox.showerror("エラー", f"チャット設定エラー: {e}")
    
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
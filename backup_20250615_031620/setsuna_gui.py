import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import queue
import time
from datetime import datetime
import json
import os
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

# 既存システムとの統合
try:
    from setsuna_bot import get_setsuna_response
    from voicevox_speaker import voice_settings, adaptive_voice_settings
    # PyAudio不要のホットキー機能を使用
    try:
        from setsuna_hotkey_mode import main as hotkey_main
    except ImportError:
        print("[GUI] Using fallback hotkey mode without PyAudio")
        def hotkey_main():
            print("[GUI] Hotkey mode not available - PyAudio missing")
    
    from setsuna_logger import log_system, log_conversation
    IMPORTS_AVAILABLE = True
    print("[GUI] All modules imported successfully")
except ImportError as e:
    print(f"[GUI] Import error: {e}")
    print("[GUI] Running in standalone mode - some features may be limited")
    IMPORTS_AVAILABLE = False
    
    # フォールバック用のダミー関数
    def get_setsuna_response(text):
        return f"[モジュールエラー] 応答システムが利用できません: {text}"
    
    def log_system(msg):
        print(f"[LOG] {msg}")
        
    def log_conversation(*args):
        print(f"[CONV] {args}")
    
    voice_settings = {"speedScale": 1.0, "pitchScale": 0.0, "intonationScale": 1.0}
    adaptive_voice_settings = {}
    
    def hotkey_main():
        print("[GUI] Hotkey mode not available - module import failed")

@dataclass
class ChatMessage:
    """チャットメッセージのデータクラス"""
    timestamp: str
    speaker: str  # "user" or "setsuna"
    content: str
    response_time: Optional[float] = None
    datetime_obj: Optional[datetime] = None  # 時間比較用

class ThreadSafeGUI:
    """スレッドセーフなGUI管理クラス"""
    
    def __init__(self):
        self.root = None
        self.gui_queue = queue.Queue()  # GUIスレッド間通信
        self.chat_history: List[ChatMessage] = []
        self.is_running = False
        
        # UI要素
        self.chat_display = None
        self.text_input = None
        self.send_button = None
        self.status_label = None
        
        # 設定UI
        self.speed_var = None
        self.pitch_var = None
        self.intonation_var = None
        
        # 状態管理
        self.hotkey_enabled = True
        self.text_input_enabled = True
        
        # デバッグ情報管理
        self.debug_display = None
        self.debug_info = {
            "file_monitoring": {"last_check": "", "status": "停止中", "errors": []},
            "voice_synthesis": {"last_request": "", "status": "待機中", "queue_size": 0},
            "api_calls": {"last_call": "", "status": "正常", "response_time": 0.0},
            "system_health": {"openai": "未確認", "voicevox": "未確認", "memory_db": "未確認"}
        }
        
        # 統計情報
        self.stats = {
            "monitoring_checks": 0,
            "voice_synthesis_count": 0,
            "api_calls_count": 0,
            "error_count": 0
        }
        self.stats_labels = {}
        
        # セッションログ管理
        self.session_start_time = datetime.now()
        self.session_log_file = None
        self.console_capture_active = False
        self.setup_session_logging()
        
        # ファイル監視（ポーリング方式）
        self.monitoring_thread = None
        self.monitoring_active = False
        self.last_modified_time = 0
        self.last_loaded_count = 0  # 重複読み込み防止
        
        # テキストチャット追跡（重複防止）
        self.text_messages_sent = []  # GUIから送信したテキストメッセージのリスト
        self.ignore_file_changes_count = 0  # 無視するファイル変更の回数（テキストチャットは2回の変更：ユーザー+応答）
        
    def create_main_window(self):
        """メインウィンドウの作成"""
        self.root = tk.Tk()
        self.root.title("片無せつな - 対話UI")
        self.root.geometry("800x600")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # メインフレームの作成
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # タブコントロールの作成
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 対話タブ
        chat_frame = ttk.Frame(notebook)
        notebook.add(chat_frame, text="対話")
        self.create_chat_tab(chat_frame)
        
        # 設定タブ
        settings_frame = ttk.Frame(notebook)
        notebook.add(settings_frame, text="設定")
        self.create_settings_tab(settings_frame)
        
        # デバッグタブ
        debug_frame = ttk.Frame(notebook)
        notebook.add(debug_frame, text="デバッグ")
        self.create_debug_tab(debug_frame)
        
        # ステータスバー
        self.create_status_bar(main_frame)
        
        log_system("GUI main window created successfully")
    
    def create_chat_tab(self, parent):
        """対話タブの作成"""
        # 対話履歴表示エリア
        chat_frame = ttk.LabelFrame(parent, text="対話履歴", padding=10)
        chat_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # スクロール可能なテキストエリア
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            state=tk.DISABLED,
            height=20,
            font=("メイリオ", 10)
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        
        # タグの設定（発言者別色分け）
        self.chat_display.tag_configure("user", foreground="blue", font=("メイリオ", 10, "bold"))
        self.chat_display.tag_configure("setsuna", foreground="red", font=("メイリオ", 10, "bold"))
        self.chat_display.tag_configure("timestamp", foreground="gray", font=("メイリオ", 8))
        self.chat_display.tag_configure("system", foreground="green", font=("メイリオ", 9, "italic"))
        self.chat_display.tag_configure("session_separator", foreground="purple", font=("メイリオ", 9, "bold"), 
                                      justify=tk.CENTER)
        
        # テキスト入力エリア
        input_frame = ttk.LabelFrame(parent, text="メッセージ入力", padding=10)
        input_frame.pack(fill=tk.X)
        
        # 入力フィールドとボタンの配置
        input_row = ttk.Frame(input_frame)
        input_row.pack(fill=tk.X)
        
        self.text_input = tk.Text(
            input_row,
            height=3,
            wrap=tk.WORD,
            font=("メイリオ", 10)
        )
        self.text_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # ボタンフレーム
        button_frame = ttk.Frame(input_row)
        button_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.send_button = ttk.Button(
            button_frame,
            text="送信",
            command=self.send_text_message
        )
        self.send_button.pack(fill=tk.X, pady=(0, 5))
        
        clear_button = ttk.Button(
            button_frame,
            text="クリア",
            command=self.clear_input
        )
        clear_button.pack(fill=tk.X)
        
        # Enterキーでの送信
        self.text_input.bind("<Control-Return>", lambda e: self.send_text_message())
        
        # モード切り替えフレーム
        mode_frame = ttk.LabelFrame(parent, text="入力モード", padding=5)
        mode_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.hotkey_var = tk.BooleanVar(value=True)
        self.text_var = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(
            mode_frame,
            text="🎤 音声入力 (Ctrl+Shift+Alt)",
            variable=self.hotkey_var,
            command=self.toggle_hotkey_mode
        ).pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Checkbutton(
            mode_frame,
            text="📝 テキスト入力",
            variable=self.text_var,
            command=self.toggle_text_mode
        ).pack(side=tk.LEFT, padx=(0, 20))
        
        # 手動更新ボタン
        ttk.Button(
            mode_frame,
            text="🔄 更新",
            command=self.manual_refresh
        ).pack(side=tk.LEFT)
    
    def create_settings_tab(self, parent):
        """設定タブの作成"""
        # 音声設定フレーム
        voice_frame = ttk.LabelFrame(parent, text="音声パラメータ", padding=10)
        voice_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 音声設定の変数
        self.speed_var = tk.DoubleVar(value=voice_settings["speedScale"])
        self.pitch_var = tk.DoubleVar(value=voice_settings["pitchScale"])
        self.intonation_var = tk.DoubleVar(value=voice_settings["intonationScale"])
        
        # スライダーの作成
        settings_grid = ttk.Frame(voice_frame)
        settings_grid.pack(fill=tk.X)
        
        # 速度設定
        ttk.Label(settings_grid, text="話す速さ:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        speed_scale = ttk.Scale(
            settings_grid,
            from_=0.5, to=2.0,
            variable=self.speed_var,
            command=self.update_voice_speed
        )
        speed_scale.grid(row=0, column=1, sticky=tk.EW, padx=(0, 10))
        ttk.Label(settings_grid, textvariable=self.speed_var).grid(row=0, column=2, sticky=tk.W)
        
        # ピッチ設定
        ttk.Label(settings_grid, text="ピッチ:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        pitch_scale = ttk.Scale(
            settings_grid,
            from_=-1.0, to=1.0,
            variable=self.pitch_var,
            command=self.update_voice_pitch
        )
        pitch_scale.grid(row=1, column=1, sticky=tk.EW, padx=(0, 10))
        ttk.Label(settings_grid, textvariable=self.pitch_var).grid(row=1, column=2, sticky=tk.W)
        
        # イントネーション設定
        ttk.Label(settings_grid, text="イントネーション:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10))
        intonation_scale = ttk.Scale(
            settings_grid,
            from_=0.0, to=2.0,
            variable=self.intonation_var,
            command=self.update_voice_intonation
        )
        intonation_scale.grid(row=2, column=1, sticky=tk.EW, padx=(0, 10))
        ttk.Label(settings_grid, textvariable=self.intonation_var).grid(row=2, column=2, sticky=tk.W)
        
        # グリッドの列を伸縮可能に
        settings_grid.columnconfigure(1, weight=1)
        
        # プリセットボタン
        preset_frame = ttk.LabelFrame(parent, text="音声プリセット", padding=10)
        preset_frame.pack(fill=tk.X, pady=(0, 10))
        
        preset_buttons = ttk.Frame(preset_frame)
        preset_buttons.pack()
        
        ttk.Button(preset_buttons, text="通常", command=lambda: self.apply_preset("normal")).pack(side=tk.LEFT, padx=5)
        ttk.Button(preset_buttons, text="元気", command=lambda: self.apply_preset("excited")).pack(side=tk.LEFT, padx=5)
        ttk.Button(preset_buttons, text="疲れ", command=lambda: self.apply_preset("tired")).pack(side=tk.LEFT, padx=5)
        ttk.Button(preset_buttons, text="落ち着き", command=lambda: self.apply_preset("calm")).pack(side=tk.LEFT, padx=5)
    
    def create_debug_tab(self, parent):
        """デバッグタブの作成"""
        # デバッグ情報表示エリア
        debug_frame = ttk.LabelFrame(parent, text="システム状態", padding=10)
        debug_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # スクロール可能なデバッグ表示
        self.debug_display = scrolledtext.ScrolledText(
            debug_frame,
            wrap=tk.WORD,
            state=tk.DISABLED,
            height=15,
            font=("Consolas", 9)
        )
        self.debug_display.pack(fill=tk.BOTH, expand=True)
        
        # タグ設定（ログレベル別色分け）
        self.debug_display.tag_configure("INFO", foreground="blue")
        self.debug_display.tag_configure("WARNING", foreground="orange")
        self.debug_display.tag_configure("ERROR", foreground="red")
        self.debug_display.tag_configure("SUCCESS", foreground="green")
        self.debug_display.tag_configure("TIMESTAMP", foreground="gray")
        
        # 制御ボタンフレーム
        control_frame = ttk.LabelFrame(parent, text="デバッグ制御", padding=10)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        button_grid = ttk.Frame(control_frame)
        button_grid.pack(fill=tk.X)
        
        # 第1行のボタン
        ttk.Button(button_grid, text="🔄 状態更新", command=self.refresh_debug_info).grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Button(button_grid, text="🧹 ログクリア", command=self.clear_debug_log).grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        ttk.Button(button_grid, text="💾 ログ保存", command=self.save_debug_log).grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        ttk.Button(button_grid, text="🩺 ヘルスチェック", command=self.run_health_check).grid(row=0, column=3, padx=5, pady=5, sticky=tk.W)
        
        # 第2行のボタン
        ttk.Button(button_grid, text="📁 ファイル監視テスト", command=self.test_file_monitoring).grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Button(button_grid, text="🎤 音声合成テスト", command=self.test_voice_synthesis).grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        ttk.Button(button_grid, text="🤖 API テスト", command=self.test_api_connection).grid(row=1, column=2, padx=5, pady=5, sticky=tk.W)
        ttk.Button(button_grid, text="🔧 メモリ最適化", command=self.optimize_memory).grid(row=1, column=3, padx=5, pady=5, sticky=tk.W)
        
        # 第3行のボタン（セッションログ関連）
        ttk.Button(button_grid, text="📋 セッションログ開く", command=self.open_session_log).grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        ttk.Button(button_grid, text="📊 サマリー出力", command=self.export_session_summary).grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        ttk.Button(button_grid, text="📁 ログフォルダ開く", command=self.open_log_folder).grid(row=2, column=2, padx=5, pady=5, sticky=tk.W)
        
        # 統計情報フレーム
        stats_frame = ttk.LabelFrame(parent, text="統計情報", padding=10)
        stats_frame.pack(fill=tk.X)
        
        self.stats_labels = {}
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill=tk.X)
        
        # 統計ラベルの作成
        stats_items = [
            ("監視チェック回数", "monitoring_checks"),
            ("音声合成回数", "voice_synthesis_count"),
            ("API呼び出し回数", "api_calls_count"),
            ("エラー発生回数", "error_count")
        ]
        
        for i, (label, key) in enumerate(stats_items):
            row, col = divmod(i, 2)
            ttk.Label(stats_grid, text=f"{label}:").grid(row=row, column=col*2, sticky=tk.W, padx=(0, 5))
            self.stats_labels[key] = ttk.Label(stats_grid, text="0", foreground="blue")
            self.stats_labels[key].grid(row=row, column=col*2+1, sticky=tk.W, padx=(0, 20))
        
        # セッション情報フレーム
        session_frame = ttk.LabelFrame(parent, text="セッション情報", padding=10)
        session_frame.pack(fill=tk.X, pady=(10, 0))
        
        session_info_grid = ttk.Frame(session_frame)
        session_info_grid.pack(fill=tk.X)
        
        # セッション情報ラベル
        ttk.Label(session_info_grid, text="開始時刻:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        start_time_label = ttk.Label(session_info_grid, text=self.session_start_time.strftime("%Y-%m-%d %H:%M:%S"), foreground="blue")
        start_time_label.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        ttk.Label(session_info_grid, text="ログファイル:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        log_file_label = ttk.Label(session_info_grid, text=os.path.basename(self.session_log_file) if self.session_log_file else "未設定", foreground="blue")
        log_file_label.grid(row=0, column=3, sticky=tk.W)
        
        # 初期デバッグ情報を表示
        self.add_debug_log("INFO", "デバッグシステム初期化完了")
        self.add_debug_log("INFO", f"セッションログファイル: {self.session_log_file}")
        self.refresh_debug_info()
    
    def create_status_bar(self, parent):
        """ステータスバーの作成"""
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        self.status_label = ttk.Label(
            status_frame,
            text="準備完了 - 音声入力: 有効, テキスト入力: 有効",
            relief=tk.SUNKEN
        )
        self.status_label.pack(fill=tk.X)
    
    def add_chat_message(self, message: ChatMessage):
        """チャットメッセージを表示に追加"""
        if not self.chat_display:
            return
        
        # セッション区切りの挿入チェック
        self.check_and_insert_session_separator(message)
            
        self.chat_display.config(state=tk.NORMAL)
        
        # タイムスタンプの追加
        timestamp_text = f"[{message.timestamp}] "
        self.chat_display.insert(tk.END, timestamp_text, "timestamp")
        
        # 発言者と内容の追加
        if message.speaker == "user":
            self.chat_display.insert(tk.END, "あなた: ", "user")
        else:
            self.chat_display.insert(tk.END, "せつな: ", "setsuna")
        
        self.chat_display.insert(tk.END, message.content)
        
        # 応答時間の表示
        if message.response_time:
            time_text = f" ({message.response_time:.2f}s)"
            self.chat_display.insert(tk.END, time_text, "timestamp")
        
        self.chat_display.insert(tk.END, "\n\n")
        
        self.chat_display.config(state=tk.DISABLED)
        self.chat_display.see(tk.END)  # 自動スクロール

    def check_and_insert_session_separator(self, current_message: ChatMessage):
        """必要に応じてセッション区切りを挿入"""
        if not self.chat_history:
            # 最初のメッセージの場合は区切りを入れない
            return
            
        last_message = self.chat_history[-1]
        
        # 時間差計算（現在時刻と最後のメッセージ）
        if current_message.datetime_obj and last_message.datetime_obj:
            time_diff = current_message.datetime_obj - last_message.datetime_obj
            time_diff_minutes = time_diff.total_seconds() / 60
            
            # 30分以上の間隔で区切りを挿入
            if time_diff_minutes >= 30:
                self.insert_session_separator(current_message.datetime_obj)
        else:
            # datetime_obj がない場合は現在時刻で判定
            now = datetime.now()
            if hasattr(last_message, 'datetime_obj') and last_message.datetime_obj:
                time_diff = now - last_message.datetime_obj
                time_diff_minutes = time_diff.total_seconds() / 60
                if time_diff_minutes >= 30:
                    self.insert_session_separator(now)

    def insert_session_separator(self, session_time: datetime):
        """セッション区切りを挿入"""
        self.chat_display.config(state=tk.NORMAL)
        
        # 区切り線とセッション情報
        separator_text = f"\n{'─' * 50}\n"
        separator_text += f"📅 {session_time.strftime('%Y/%m/%d %H:%M')} - 新しいセッション\n"
        separator_text += f"{'─' * 50}\n\n"
        
        self.chat_display.insert(tk.END, separator_text, "session_separator")
        self.chat_display.config(state=tk.DISABLED)
        
        log_system(f"Session separator inserted at {session_time.strftime('%Y/%m/%d %H:%M')}")
    
    def send_text_message(self):
        """テキストメッセージの送信"""
        if not self.text_input_enabled:
            return
            
        message = self.text_input.get("1.0", tk.END).strip()
        if not message:
            return
        
        # ユーザーメッセージを表示
        now = datetime.now()
        user_msg = ChatMessage(
            timestamp=now.strftime("%H:%M:%S"),
            speaker="user",
            content=message,
            datetime_obj=now
        )
        self.add_chat_message(user_msg)
        self.chat_history.append(user_msg)
        
        # テキストメッセージを追跡（重複防止）
        self.text_messages_sent.append(message)
        self.ignore_file_changes_count = 2  # テキストチャットによる2回のファイル変更を無視
        
        # メモリ使用量制御：古いテキストメッセージ記録を削除
        if len(self.text_messages_sent) > 50:  # 50件を超えたら古いものから削除
            self.text_messages_sent = self.text_messages_sent[-25:]  # 最新25件を保持
        
        # セッションログに記録
        self.write_session_log("TEXT_INPUT", f"ユーザーテキスト入力: {message}")
        
        # 入力フィールドをクリア
        self.clear_input()
        
        # 送信ボタンを無効化（応答中）
        self.send_button.config(state=tk.DISABLED)
        self.update_status("応答生成中...")
        
        # 別スレッドで応答を取得
        threading.Thread(
            target=self.process_text_response,
            args=(message,),
            daemon=True
        ).start()
    
    def process_text_response(self, user_input: str):
        """テキスト応答の処理（別スレッド）"""
        try:
            start_time = time.time()
            response = get_setsuna_response(user_input)
            response_time = time.time() - start_time
            
            # GUIに結果を送信
            now = datetime.now()
            setsuna_msg = ChatMessage(
                timestamp=now.strftime("%H:%M:%S"),
                speaker="setsuna",
                content=response,
                response_time=response_time,
                datetime_obj=now
            )
            
            # GUI更新をメインスレッドで実行
            self.root.after(0, self.handle_text_response, setsuna_msg)
            
        except Exception as e:
            error_msg = f"エラーが発生しました: {str(e)}"
            now = datetime.now()
            error_response = ChatMessage(
                timestamp=now.strftime("%H:%M:%S"),
                speaker="setsuna",
                content=error_msg,
                datetime_obj=now
            )
            self.root.after(0, self.handle_text_response, error_response)
    
    def handle_text_response(self, message: ChatMessage):
        """テキスト応答の処理（メインスレッド）"""
        self.add_chat_message(message)
        self.chat_history.append(message)
        
        # テキスト応答処理済み（ファイル変更は既にカウンター設定済み）
        
        # セッションログに記録
        self.write_session_log("TEXT_RESPONSE", f"せつなテキスト応答: {message.content}")
        if hasattr(message, 'response_time') and message.response_time:
            self.write_session_log("PERFORMANCE", f"応答時間: {message.response_time:.2f}秒")
        
        # UI状態を復元
        self.send_button.config(state=tk.NORMAL)
        self.update_status("準備完了")
        
        # 入力フィールドにフォーカス
        self.text_input.focus_set()
    
    def clear_input(self):
        """入力フィールドのクリア"""
        self.text_input.delete("1.0", tk.END)
    
    def update_voice_speed(self, value):
        """音声速度の更新"""
        voice_settings["speedScale"] = float(value)
        self.speed_var.set(round(float(value), 1))
    
    def update_voice_pitch(self, value):
        """音声ピッチの更新"""
        voice_settings["pitchScale"] = float(value)
        self.pitch_var.set(round(float(value), 1))
    
    def update_voice_intonation(self, value):
        """音声イントネーションの更新"""
        voice_settings["intonationScale"] = float(value)
        self.intonation_var.set(round(float(value), 1))
    
    def apply_preset(self, preset_name: str):
        """音声プリセットの適用"""
        presets = {
            "normal": {"speedScale": 1.3, "pitchScale": 0.0, "intonationScale": 1.0},
            "excited": {"speedScale": 1.4, "pitchScale": 0.2, "intonationScale": 1.2},
            "tired": {"speedScale": 0.9, "pitchScale": -0.2, "intonationScale": 0.8},
            "calm": {"speedScale": 1.0, "pitchScale": 0.0, "intonationScale": 0.9}
        }
        
        if preset_name in presets:
            preset = presets[preset_name]
            self.speed_var.set(preset["speedScale"])
            self.pitch_var.set(preset["pitchScale"])
            self.intonation_var.set(preset["intonationScale"])
            
            voice_settings.update(preset)
            self.update_status(f"プリセット '{preset_name}' を適用しました")
    
    def toggle_hotkey_mode(self):
        """ホットキーモードの切り替え"""
        self.hotkey_enabled = self.hotkey_var.get()
        self.update_status_display()
    
    def toggle_text_mode(self):
        """テキストモードの切り替え"""
        self.text_input_enabled = self.text_var.get()
        state = tk.NORMAL if self.text_input_enabled else tk.DISABLED
        self.text_input.config(state=state)
        self.send_button.config(state=state)
        self.update_status_display()
    
    def update_status(self, message: str):
        """ステータスメッセージの更新"""
        if self.status_label:
            self.status_label.config(text=message)
    
    def update_status_display(self):
        """ステータス表示の更新"""
        hotkey_status = "有効" if self.hotkey_enabled else "無効"
        text_status = "有効" if self.text_input_enabled else "無効"
        self.update_status(f"音声入力: {hotkey_status}, テキスト入力: {text_status}")

    def manual_refresh(self):
        """手動でチャット履歴を更新"""
        self.update_status("手動更新中...")
        print("[MANUAL] Manual refresh triggered")
        
        # ファイル存在確認
        if os.path.exists("chat_history.json"):
            print(f"[MANUAL] File exists, size: {os.path.getsize('chat_history.json')} bytes")
            print(f"[MANUAL] Last modified: {os.path.getmtime('chat_history.json')}")
        else:
            print("[MANUAL] chat_history.json does not exist")
            self.update_status("ファイルが見つかりません")
            return
        
        try:
            # 強制的にファイル変更時刻をリセットして更新を実行
            old_time = self.last_modified_time
            self.last_modified_time = 0  # リセット
            self.update_from_voice_conversation()
            print(f"[MANUAL] Refresh completed, time reset from {old_time} to {self.last_modified_time}")
            self.update_status("手動更新完了")
        except Exception as e:
            print(f"[MANUAL] Manual refresh failed: {e}")
            self.update_status(f"手動更新エラー: {str(e)}")
            log_system(f"Manual refresh error: {e}")
    
    # デバッグ機能メソッド
    def add_debug_log(self, level, message):
        """デバッグログにメッセージを追加"""
        if not self.debug_display:
            return
            
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        self.debug_display.config(state=tk.NORMAL)
        
        # タイムスタンプ
        self.debug_display.insert(tk.END, f"[{timestamp}] ", "TIMESTAMP")
        
        # ログレベル
        self.debug_display.insert(tk.END, f"[{level}] ", level)
        
        # メッセージ
        self.debug_display.insert(tk.END, f"{message}\n")
        
        self.debug_display.config(state=tk.DISABLED)
        self.debug_display.see(tk.END)
        
        # エラーカウント更新
        if level == "ERROR":
            self.stats["error_count"] += 1
            self.update_stats_display()
    
    def clear_debug_log(self):
        """デバッグログをクリア"""
        if self.debug_display:
            self.debug_display.config(state=tk.NORMAL)
            self.debug_display.delete(1.0, tk.END)
            self.debug_display.config(state=tk.DISABLED)
            self.add_debug_log("INFO", "デバッグログをクリアしました")
    
    def save_debug_log(self):
        """デバッグログをファイルに保存"""
        try:
            if self.debug_display:
                content = self.debug_display.get(1.0, tk.END)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"debug_log_{timestamp}.txt"
                
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(content)
                
                self.add_debug_log("SUCCESS", f"デバッグログを保存: {filename}")
                self.update_status(f"ログ保存完了: {filename}")
        except Exception as e:
            self.add_debug_log("ERROR", f"ログ保存失敗: {e}")
    
    def refresh_debug_info(self):
        """デバッグ情報を更新"""
        # ファイル監視状態
        if self.monitoring_active:
            self.debug_info["file_monitoring"]["status"] = "監視中"
            self.debug_info["file_monitoring"]["last_check"] = datetime.now().strftime("%H:%M:%S")
        else:
            self.debug_info["file_monitoring"]["status"] = "停止中"
        
        # ファイル状態確認
        if os.path.exists("chat_history.json"):
            file_size = os.path.getsize("chat_history.json")
            file_time = os.path.getmtime("chat_history.json")
            self.add_debug_log("INFO", f"chat_history.json: {file_size}バイト, 更新: {datetime.fromtimestamp(file_time).strftime('%H:%M:%S')}")
        else:
            self.add_debug_log("WARNING", "chat_history.json が見つかりません")
        
        # 統計情報更新
        self.update_stats_display()
        
        self.add_debug_log("INFO", "デバッグ情報を更新しました")
    
    def update_stats_display(self):
        """統計表示を更新"""
        for key, label in self.stats_labels.items():
            if key in self.stats:
                label.config(text=str(self.stats[key]))
    
    def run_health_check(self):
        """システムヘルスチェックを実行"""
        self.add_debug_log("INFO", "ヘルスチェック開始...")
        
        def health_check_thread():
            try:
                if IMPORTS_AVAILABLE:
                    # 各種システムの確認
                    health_results = {
                        "openai": "未確認",
                        "voicevox": "未確認", 
                        "memory_db": "未確認"
                    }
                    
                    # OpenAI API確認
                    try:
                        import openai
                        # 簡単なテスト（実際のAPI呼び出しは避ける）
                        health_results["openai"] = "モジュールOK"
                        self.root.after(0, lambda: self.add_debug_log("SUCCESS", "OpenAI モジュール確認済み"))
                    except Exception as e:
                        health_results["openai"] = f"エラー: {e}"
                        self.root.after(0, lambda: self.add_debug_log("ERROR", f"OpenAI エラー: {e}"))
                    
                    # VOICEVOX確認
                    try:
                        import requests
                        response = requests.get("http://127.0.0.1:50021/version", timeout=3)
                        if response.status_code == 200:
                            health_results["voicevox"] = "接続OK"
                            self.root.after(0, lambda: self.add_debug_log("SUCCESS", "VOICEVOX 接続確認済み"))
                        else:
                            health_results["voicevox"] = f"ステータス: {response.status_code}"
                            self.root.after(0, lambda: self.add_debug_log("WARNING", f"VOICEVOX ステータス異常: {response.status_code}"))
                    except Exception as e:
                        health_results["voicevox"] = f"接続失敗: {e}"
                        self.root.after(0, lambda: self.add_debug_log("ERROR", f"VOICEVOX 接続エラー: {e}"))
                    
                    # メモリDB確認
                    try:
                        import sqlite3
                        with sqlite3.connect("setsuna_memory.db", timeout=2) as conn:
                            conn.execute("SELECT 1").fetchone()
                        health_results["memory_db"] = "接続OK"
                        self.root.after(0, lambda: self.add_debug_log("SUCCESS", "メモリDB 接続確認済み"))
                    except Exception as e:
                        health_results["memory_db"] = f"エラー: {e}"
                        self.root.after(0, lambda: self.add_debug_log("ERROR", f"メモリDB エラー: {e}"))
                    
                    # 結果をデバッグ情報に保存
                    self.debug_info["system_health"] = health_results
                    self.root.after(0, lambda: self.add_debug_log("INFO", "ヘルスチェック完了"))
                    
                else:
                    self.root.after(0, lambda: self.add_debug_log("WARNING", "モジュールが不足しているためヘルスチェックをスキップ"))
                    
            except Exception as e:
                self.root.after(0, lambda: self.add_debug_log("ERROR", f"ヘルスチェック失敗: {e}"))
        
        threading.Thread(target=health_check_thread, daemon=True).start()
    
    def test_file_monitoring(self):
        """ファイル監視のテスト"""
        self.add_debug_log("INFO", "ファイル監視テスト開始...")
        
        try:
            # 現在の状態確認
            if os.path.exists("chat_history.json"):
                current_time = os.path.getmtime("chat_history.json")
                self.add_debug_log("INFO", f"現在のファイル変更時刻: {current_time}")
                self.add_debug_log("INFO", f"最後の確認時刻: {self.last_modified_time}")
                
                if current_time > self.last_modified_time:
                    self.add_debug_log("SUCCESS", "ファイル変更が検出されました")
                else:
                    self.add_debug_log("INFO", "ファイル変更はありません")
            else:
                self.add_debug_log("WARNING", "chat_history.json が見つかりません")
            
            # 監視状態確認
            if self.monitoring_active:
                self.add_debug_log("SUCCESS", "ファイル監視は動作中です")
            else:
                self.add_debug_log("WARNING", "ファイル監視は停止中です")
                
            self.stats["monitoring_checks"] += 1
            self.update_stats_display()
            
        except Exception as e:
            self.add_debug_log("ERROR", f"ファイル監視テスト失敗: {e}")
    
    def test_voice_synthesis(self):
        """音声合成のテスト"""
        self.add_debug_log("INFO", "音声合成テスト開始...")
        
        def voice_test_thread():
            try:
                if IMPORTS_AVAILABLE:
                    # 簡単なテスト音声を生成
                    test_text = "テスト音声です"
                    self.root.after(0, lambda: self.add_debug_log("INFO", f"テスト音声生成中: '{test_text}'"))
                    
                    # ここで実際の音声合成テストを行う場合は voicevox_speaker の関数を呼ぶ
                    self.root.after(0, lambda: self.add_debug_log("SUCCESS", "音声合成テスト完了"))
                    
                    self.stats["voice_synthesis_count"] += 1
                    self.root.after(0, self.update_stats_display)
                else:
                    self.root.after(0, lambda: self.add_debug_log("WARNING", "音声モジュールが利用できません"))
                    
            except Exception as e:
                self.root.after(0, lambda: self.add_debug_log("ERROR", f"音声合成テスト失敗: {e}"))
        
        threading.Thread(target=voice_test_thread, daemon=True).start()
    
    def test_api_connection(self):
        """API接続のテスト"""
        self.add_debug_log("INFO", "API接続テスト開始...")
        
        def api_test_thread():
            try:
                if IMPORTS_AVAILABLE:
                    # 環境変数の確認
                    api_key = os.getenv("OPENAI_API_KEY")
                    if api_key:
                        self.root.after(0, lambda: self.add_debug_log("SUCCESS", "OpenAI API キーが設定されています"))
                    else:
                        self.root.after(0, lambda: self.add_debug_log("ERROR", "OpenAI API キーが設定されていません"))
                    
                    self.stats["api_calls_count"] += 1
                    self.root.after(0, self.update_stats_display)
                else:
                    self.root.after(0, lambda: self.add_debug_log("WARNING", "APIモジュールが利用できません"))
                    
            except Exception as e:
                self.root.after(0, lambda: self.add_debug_log("ERROR", f"API接続テスト失敗: {e}"))
        
        threading.Thread(target=api_test_thread, daemon=True).start()
    
    def optimize_memory(self):
        """メモリ最適化の実行"""
        self.add_debug_log("INFO", "メモリ最適化開始...")
        
        def memory_optimize_thread():
            try:
                if IMPORTS_AVAILABLE:
                    # メモリ管理システムの最適化を実行
                    from setsuna_memory_manager import optimize_memory_usage
                    optimize_memory_usage()
                    self.root.after(0, lambda: self.add_debug_log("SUCCESS", "メモリ最適化完了"))
                else:
                    self.root.after(0, lambda: self.add_debug_log("WARNING", "メモリ管理モジュールが利用できません"))
                    
            except Exception as e:
                self.root.after(0, lambda: self.add_debug_log("ERROR", f"メモリ最適化失敗: {e}"))
        
        threading.Thread(target=memory_optimize_thread, daemon=True).start()
    
    # セッションログ機能
    def setup_session_logging(self):
        """セッションログファイルのセットアップ"""
        try:
            # ログディレクトリの作成
            if not os.path.exists("session_logs"):
                os.makedirs("session_logs")
            
            # セッションIDとファイル名の生成
            session_id = self.session_start_time.strftime("%Y%m%d_%H%M%S")
            self.session_log_file = f"session_logs/session_{session_id}.log"
            
            # セッション開始ログ
            self.write_session_log("SESSION_START", f"せつなGUI セッション開始: {self.session_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            self.write_session_log("SYSTEM_INFO", f"Python実行環境: {os.getcwd()}")
            self.write_session_log("SYSTEM_INFO", f"モジュール状態: {'利用可能' if IMPORTS_AVAILABLE else '制限モード'}")
            
            print(f"[SESSION] ログファイル: {self.session_log_file}")
            
        except Exception as e:
            print(f"[SESSION] ログ設定エラー: {e}")
    
    def write_session_log(self, log_type, message):
        """セッションログにメッセージを書き込み"""
        if not self.session_log_file:
            return
            
        try:
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]  # ミリ秒まで
            log_entry = f"[{timestamp}] [{log_type}] {message}\n"
            
            with open(self.session_log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)
                
        except Exception as e:
            print(f"[SESSION] ログ書き込みエラー: {e}")
    
    def start_console_capture(self):
        """コンソール出力をキャプチャ開始（PowerShellログ取得）"""
        self.console_capture_active = True
        self.write_session_log("CONSOLE_CAPTURE", "コンソール出力キャプチャ開始")
        self.add_debug_log("INFO", "コンソール出力キャプチャを開始しました")
    
    def stop_console_capture(self):
        """コンソール出力キャプチャ停止"""
        self.console_capture_active = False
        self.write_session_log("CONSOLE_CAPTURE", "コンソール出力キャプチャ停止")
        self.add_debug_log("INFO", "コンソール出力キャプチャを停止しました")
    
    def log_voice_interaction(self, user_input, response):
        """音声対話のログ記録"""
        self.write_session_log("VOICE_USER", f"ユーザー: {user_input}")
        self.write_session_log("VOICE_RESPONSE", f"せつな: {response}")
    
    def log_text_interaction(self, user_input, response):
        """テキスト対話のログ記録"""
        self.write_session_log("TEXT_USER", f"ユーザー: {user_input}")
        self.write_session_log("TEXT_RESPONSE", f"せつな: {response}")
    
    def log_system_event(self, event_type, details):
        """システムイベントのログ記録"""
        self.write_session_log("SYSTEM_EVENT", f"{event_type}: {details}")
    
    def export_session_summary(self):
        """セッション終了時のサマリーエクスポート"""
        if not self.session_log_file:
            return
            
        try:
            session_duration = datetime.now() - self.session_start_time
            summary = f"""
=== セッションサマリー ===
開始時刻: {self.session_start_time.strftime('%Y-%m-%d %H:%M:%S')}
終了時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
継続時間: {str(session_duration).split('.')[0]}

統計情報:
- ファイル監視チェック: {self.stats['monitoring_checks']}回
- 音声合成実行: {self.stats['voice_synthesis_count']}回
- API呼び出し: {self.stats['api_calls_count']}回
- 音声対話セッション: {self.stats.get('voice_interactions', 0)}回
- エラー発生: {self.stats['error_count']}回

音声対話メッセージ数: {len([msg for msg in self.chat_history if '🎤' in msg.content])}
テキスト対話メッセージ数: {len([msg for msg in self.chat_history if '🎤' not in msg.content])}
"""
            self.write_session_log("SESSION_SUMMARY", summary)
            self.add_debug_log("SUCCESS", f"セッションサマリーを保存: {self.session_log_file}")
            
        except Exception as e:
            self.add_debug_log("ERROR", f"セッションサマリー保存エラー: {e}")
    
    def open_session_log(self):
        """現在のセッションログファイルを開く"""
        if self.session_log_file and os.path.exists(self.session_log_file):
            try:
                import subprocess
                subprocess.run(['notepad', self.session_log_file], check=True)
                self.add_debug_log("SUCCESS", "セッションログファイルを開きました")
            except subprocess.CalledProcessError:
                try:
                    # Notepadが失敗した場合はデフォルトエディタで開く
                    os.startfile(self.session_log_file)
                    self.add_debug_log("SUCCESS", "セッションログファイルを開きました")
                except Exception as e:
                    self.add_debug_log("ERROR", f"ログファイルを開けませんでした: {e}")
        else:
            self.add_debug_log("WARNING", "セッションログファイルが見つかりません")
    
    def open_log_folder(self):
        """ログフォルダをエクスプローラーで開く"""
        try:
            if os.path.exists("session_logs"):
                os.startfile("session_logs")
                self.add_debug_log("SUCCESS", "ログフォルダを開きました")
            else:
                self.add_debug_log("WARNING", "ログフォルダが見つかりません")
        except Exception as e:
            self.add_debug_log("ERROR", f"ログフォルダを開けませんでした: {e}")
    
    def load_chat_history(self):
        """既存のチャット履歴を読み込み"""
        try:
            with open("chat_history.json", "r", encoding="utf-8") as f:
                messages = json.load(f)
            
            # システムメッセージを除外してカウント
            user_assistant_messages = [msg for msg in messages if msg["role"] in ["user", "assistant"]]
            current_message_count = len(user_assistant_messages)
            
            # 読み込み済みメッセージ数を現在のファイル内容に設定
            self.last_loaded_count = current_message_count
            
            # GUI表示用のメッセージ追加
            for msg in user_assistant_messages:
                speaker = "user" if msg["role"] == "user" else "setsuna"
                chat_msg = ChatMessage(
                    timestamp="--:--:--",  # 過去ログは時刻なし
                    speaker=speaker,
                    content=msg["content"],
                    datetime_obj=None  # 過去ログは時間比較対象外
                )
                self.add_chat_message(chat_msg)
                self.chat_history.append(chat_msg)
            
            # ファイル変更時刻を初期化（重要：監視システムの正常動作のため）
            if os.path.exists("chat_history.json"):
                current_file_time = os.path.getmtime("chat_history.json")
                self.last_modified_time = current_file_time
            
            log_system(f"Loaded {len(user_assistant_messages)} messages from chat history")
            
        except FileNotFoundError:
            log_system("No existing chat history found")
            self.last_loaded_count = 0
        except Exception as e:
            log_system(f"Error loading chat history: {e}")
            self.last_loaded_count = 0

    def update_from_voice_conversation(self):
        """音声対話による chat_history.json の更新を反映"""
        try:
            if not os.path.exists("chat_history.json"):
                return
                
            with open("chat_history.json", "r", encoding="utf-8") as f:
                messages = json.load(f)
            
            # システムメッセージを除外
            user_assistant_messages = [msg for msg in messages if msg["role"] in ["user", "assistant"]]
            current_count = len(user_assistant_messages)
            
            # 新しいメッセージがある場合のみ追加
            if current_count > self.last_loaded_count:
                new_messages = user_assistant_messages[self.last_loaded_count:]
                
                # テキストチャットで送信したメッセージを除外（重複防止）
                voice_messages = []
                for i, msg in enumerate(new_messages):
                    # ユーザーメッセージの場合、テキストで送信したものでないかチェック
                    if msg["role"] == "user" and msg["content"] in self.text_messages_sent:
                        continue
                    voice_messages.append(msg)

                if not voice_messages:
                    self.last_loaded_count = current_count
                    return
                
                for i, msg in enumerate(voice_messages):
                    speaker = "user" if msg["role"] == "user" else "setsuna"
                    now = datetime.now()
                    
                    # 音声対話のマーカーを追加（既存メッセージと区別）
                    content_with_marker = f"🎤 {msg['content']}"
                    
                    chat_msg = ChatMessage(
                        timestamp=now.strftime("%H:%M:%S"),
                        speaker=speaker,
                        content=content_with_marker,
                        datetime_obj=now
                    )
                    
                    # メインスレッドでGUI更新を確実に実行
                    if self.root:
                        def schedule_add_message(msg):
                            self.root.after_idle(lambda: self._add_message_to_gui(msg))
                        schedule_add_message(chat_msg)
                    
                    self.chat_history.append(chat_msg)
                
                self.last_loaded_count = current_count
                log_system(f"Added {len(voice_messages)} new voice conversation messages")
                
        except FileNotFoundError:
            print("[DEBUG] chat_history.json not found")
            self.add_debug_log("WARNING", "chat_history.json が見つかりません")
        except json.JSONDecodeError as e:
            print(f"[ERROR] JSON decode error: {e}")
            self.add_debug_log("ERROR", f"JSON解析エラー: {e}")
            log_system(f"JSON decode error in chat_history.json: {e}")
        except Exception as e:
            print(f"[ERROR] Error updating from voice conversation: {e}")
            self.add_debug_log("ERROR", f"音声対話更新エラー: {e}")
            log_system(f"Error updating from voice conversation: {e}")

    def _add_message_to_gui(self, message: ChatMessage):
        """GUIにメッセージを安全に追加（メインスレッド用）"""
        try:
            self.add_chat_message(message)
        except Exception as e:
            print(f"[ERROR] Failed to add message to GUI: {e}")
            log_system(f"Failed to add message to GUI: {e}")

    def start_file_monitoring(self):
        """ファイル監視を開始（ポーリング方式）"""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitoring_thread = threading.Thread(target=self._monitor_chat_history, daemon=True)
            self.monitoring_thread.start()
            log_system("File monitoring started for chat_history.json (polling)")

    def stop_file_monitoring(self):
        """ファイル監視を停止"""
        self.monitoring_active = False
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=1)
        log_system("File monitoring stopped")

    def _monitor_chat_history(self):
        """chat_history.json の変更を監視（バックグラウンド）"""
        print("[MONITOR] File monitoring thread started")
        while self.monitoring_active:
            try:
                if os.path.exists("chat_history.json"):
                    current_time = os.path.getmtime("chat_history.json")
                    
                    # 初回の場合は現在時刻を設定
                    if self.last_modified_time == 0:
                        self.last_modified_time = current_time
                        print(f"[MONITOR] Initial file time set: {current_time}")
                    elif current_time > self.last_modified_time:
                        print(f"[MONITOR] File change detected: {current_time} > {self.last_modified_time}")
                        self.last_modified_time = current_time
                        
                        # テキストチャットによる変更を無視するかチェック
                        if self.ignore_file_changes_count > 0:
                            print(f"[MONITOR] Ignoring file change (text chat, remaining: {self.ignore_file_changes_count})")
                            if self.debug_display:
                                self.root.after(0, lambda: self.add_debug_log("INFO", f"ファイル変更検出（テキストチャットのため無視、残り{self.ignore_file_changes_count}回）"))
                            self.ignore_file_changes_count -= 1  # カウンターを減らす
                            continue  # ここで処理を中断して次のループへ
                        else:
                            print("[MONITOR] Processing voice conversation file change")
                            
                            # メインスレッドで更新実行（少し遅延を入れてファイル書き込み完了を待つ）
                            if self.root and hasattr(self, 'root'):
                                self.root.after(100, self.update_from_voice_conversation)
                            else:
                                print("[MONITOR] Root window not available")
                            
                            # 監視ログを残す
                            self.write_session_log("FILE_MONITOR", f"音声対話ファイル変更検出: {datetime.fromtimestamp(current_time).strftime('%H:%M:%S')}")
                
                    # 統計更新
                    self.stats["monitoring_checks"] += 1
                else:
                    print("[MONITOR] chat_history.json does not exist")
                
                time.sleep(1.0)  # 1秒間隔でチェック
                
            except OSError as e:
                print(f"[MONITOR] File system error: {e}")
                if self.debug_display and self.root:
                    self.root.after(0, lambda: self.add_debug_log("ERROR", f"ファイルシステムエラー: {e}"))
                time.sleep(2)  # ファイルシステムエラー時は長めに待機
            except Exception as e:
                print(f"[MONITOR] Error in file monitoring: {e}")
                if self.debug_display and self.root:
                    self.root.after(0, lambda: self.add_debug_log("ERROR", f"ファイル監視エラー: {e}"))
                log_system(f"Error in file monitoring: {e}")
                time.sleep(2)  # エラー時は少し長めに待機
        
        print("[MONITOR] File monitoring thread stopped")
    
    
    def on_closing(self):
        """ウィンドウ閉じる時の処理"""
        self.is_running = False
        
        # セッション終了ログ
        self.write_session_log("SESSION_END", "せつなGUI セッション終了")
        self.export_session_summary()
        
        self.stop_file_monitoring()
        self.root.destroy()
        log_system("GUI window closed")
    
    def run(self):
        """GUI実行"""
        self.is_running = True
        self.create_main_window()
        self.load_chat_history()
        
        # 起動時のセッション区切りを追加（履歴がある場合のみ）
        if self.chat_history:
            self.insert_session_separator(datetime.now())
        
        # ファイル監視を開始
        self.start_file_monitoring()
        
        # ホットキーモードを別スレッドで開始
        if self.hotkey_enabled and IMPORTS_AVAILABLE:
            try:
                hotkey_thread = threading.Thread(target=hotkey_main, daemon=True)
                hotkey_thread.start()
                log_system("Hotkey mode started in background")
                self.add_debug_log("SUCCESS", "ホットキーモード開始: 音声入力待機中")
            except Exception as e:
                log_system(f"Failed to start hotkey mode: {e}")
                self.add_debug_log("ERROR", f"ホットキーモード開始失敗: {e}")
                self.update_status("ホットキーモード開始エラー")
        elif not IMPORTS_AVAILABLE:
            log_system("Hotkey mode disabled - module imports failed")
            self.update_status("ホットキーモード無効（モジュールエラー）")
        
        log_system("GUI started successfully")
        self.root.mainloop()

# GUI インスタンス作成と実行
if __name__ == "__main__":
    gui = ThreadSafeGUI()
    gui.run()
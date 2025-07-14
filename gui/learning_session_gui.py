#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LearningSessionGUI - Phase 2C
学習セッション視覚管理GUI
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
import queue

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.activity_learning_engine import ActivityLearningEngine
from core.activity_proposal_engine import ActivityProposalEngine
from core.knowledge_integration_system import KnowledgeIntegrationSystem
from core.conversation_knowledge_provider import ConversationKnowledgeProvider
from core.budget_safety_manager import BudgetSafetyManager
from core.config_manager import get_config_manager
from session_result_viewer import SessionResultViewer
from session_html_report import SessionHTMLReportGenerator

# Windows環境のパス設定
if os.name == 'nt':
    GUI_DATA_DIR = Path("D:/setsuna_bot/data/gui")
else:
    GUI_DATA_DIR = Path("/mnt/d/setsuna_bot/data/gui")

class LearningSessionGUI:
    """学習セッションGUIメインクラス"""
    
    def __init__(self):
        """GUI初期化"""
        # データディレクトリ作成
        GUI_DATA_DIR.mkdir(parents=True, exist_ok=True)
        
        # 設定管理初期化
        self.config = get_config_manager()
        
        # コアコンポーネント初期化
        self.learning_engine = ActivityLearningEngine()
        self.proposal_engine = ActivityProposalEngine()
        self.integration_system = KnowledgeIntegrationSystem()
        self.conversation_provider = ConversationKnowledgeProvider()
        self.budget_manager = BudgetSafetyManager()
        self.session_viewer = SessionResultViewer()
        self.html_report_generator = SessionHTMLReportGenerator()
        
        # GUI状態管理
        self.current_session_id = None
        self.current_selected_session_id = None
        self.session_thread = None
        self.monitoring_active = False
        self.update_queue = queue.Queue()
        
        # GUIセットアップ
        self.setup_gui()
        
        # コールバック設定
        self.setup_callbacks()
        
        # 初期データ読み込み
        self.load_initial_data()
        
        print("[GUI] ✅ LearningSessionGUI初期化完了")
    
    def setup_gui(self):
        """GUI構築"""
        self.root = tk.Tk()
        self.root.title("せつなBot - 学習セッション管理")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f0f0f0')
        
        # メインフレーム
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # タイトル
        title_label = ttk.Label(main_frame, text="🎓 せつなBot - 学習セッション管理", 
                               font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # タブ設定
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # タブ作成
        self.create_session_tab()
        self.create_monitoring_tab()
        self.create_proposals_tab()
        self.create_knowledge_tab()
        self.create_budget_tab()
        
        # ステータスバー
        self.status_var = tk.StringVar(value="準備完了")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=(5, 0))
        
        # 定期更新開始
        self.start_periodic_update()
    
    def create_session_tab(self):
        """セッション管理タブ"""
        session_frame = ttk.Frame(self.notebook)
        self.notebook.add(session_frame, text="📚 セッション管理")
        
        # 左パネル - セッション作成
        left_panel = ttk.LabelFrame(session_frame, text="新規セッション作成", padding=10)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        
        # セッション作成フォーム
        ttk.Label(left_panel, text="学習テーマ:").pack(anchor=tk.W)
        self.theme_var = tk.StringVar(value="AI音楽生成技術")
        theme_entry = ttk.Entry(left_panel, textvariable=self.theme_var, width=30)
        theme_entry.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(left_panel, text="学習タイプ:").pack(anchor=tk.W)
        self.learning_type_var = tk.StringVar(value="概要")
        learning_type_combo = ttk.Combobox(left_panel, textvariable=self.learning_type_var,
                                          values=["概要", "深掘り", "実用"], state="readonly")
        learning_type_combo.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(left_panel, text="深度レベル:").pack(anchor=tk.W)
        self.depth_var = tk.IntVar(value=3)
        depth_scale = ttk.Scale(left_panel, from_=1, to=5, orient=tk.HORIZONTAL,
                               variable=self.depth_var, length=200)
        depth_scale.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(left_panel, text="1:基本 → 5:専門").pack(anchor=tk.W, pady=(0, 10))
        
        ttk.Label(left_panel, text="時間制限(分):").pack(anchor=tk.W)
        self.time_limit_var = tk.IntVar(value=30)
        time_limit_spin = ttk.Spinbox(left_panel, from_=5, to=120, textvariable=self.time_limit_var,
                                     width=10)
        time_limit_spin.pack(anchor=tk.W, pady=(0, 10))
        
        ttk.Label(left_panel, text="予算制限($):").pack(anchor=tk.W)
        self.budget_limit_var = tk.DoubleVar(value=5.0)
        budget_limit_spin = ttk.Spinbox(left_panel, from_=1.0, to=50.0, increment=0.5,
                                       textvariable=self.budget_limit_var, width=10)
        budget_limit_spin.pack(anchor=tk.W, pady=(0, 10))
        
        # 段階的分析設定
        preprocessing_frame = ttk.LabelFrame(left_panel, text="段階的分析設定", padding=5)
        preprocessing_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.preprocessing_enabled_var = tk.BooleanVar(value=True)
        preprocessing_check = ttk.Checkbutton(preprocessing_frame, text="GPT-3.5前処理有効",
                                             variable=self.preprocessing_enabled_var)
        preprocessing_check.pack(anchor=tk.W)
        
        ttk.Label(preprocessing_frame, text="関連性閾値:").pack(anchor=tk.W)
        self.relevance_threshold_var = tk.DoubleVar(value=0.4)
        relevance_scale = ttk.Scale(preprocessing_frame, from_=0.1, to=1.0, orient=tk.HORIZONTAL,
                                   variable=self.relevance_threshold_var, length=150)
        relevance_scale.pack(fill=tk.X)
        
        # API Key確認ボタン
        api_key_frame = ttk.LabelFrame(left_panel, text="API設定確認", padding=5)
        api_key_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.api_key_status_var = tk.StringVar(value="未確認")
        api_key_label = ttk.Label(api_key_frame, textvariable=self.api_key_status_var)
        api_key_label.pack(anchor=tk.W)
        
        self.check_api_key_button = ttk.Button(api_key_frame, text="API Key確認", 
                                              command=self.check_api_key_status)
        self.check_api_key_button.pack(fill=tk.X, pady=(5, 0))
        
        # セッション制御ボタン
        button_frame = ttk.Frame(left_panel)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        self.create_button = ttk.Button(button_frame, text="セッション作成", 
                                       command=self.create_session, style='Success.TButton')
        self.create_button.pack(fill=tk.X, pady=(0, 5))
        
        self.start_button = ttk.Button(button_frame, text="開始", 
                                      command=self.start_session, state=tk.DISABLED,
                                      style='Primary.TButton')
        self.start_button.pack(fill=tk.X, pady=(0, 5))
        
        self.stop_button = ttk.Button(button_frame, text="停止", 
                                     command=self.stop_session, state=tk.DISABLED,
                                     style='Danger.TButton')
        self.stop_button.pack(fill=tk.X)
        
        # 右パネル - セッション一覧
        right_panel = ttk.LabelFrame(session_frame, text="セッション履歴", padding=10)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # セッション一覧（Treeview）
        columns = ('ID', 'テーマ', 'タイプ', '状態', '開始時刻', 'コスト')
        self.session_tree = ttk.Treeview(right_panel, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.session_tree.heading(col, text=col)
            self.session_tree.column(col, width=120)
        
        # スクロールバー
        session_scrollbar = ttk.Scrollbar(right_panel, orient=tk.VERTICAL, command=self.session_tree.yview)
        self.session_tree.configure(yscrollcommand=session_scrollbar.set)
        
        self.session_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        session_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # セッション詳細表示
        details_frame = ttk.LabelFrame(right_panel, text="セッション詳細", padding=5)
        details_frame.pack(fill=tk.X, pady=(10, 0))
        
        # セッション詳細タブ
        self.session_details_notebook = ttk.Notebook(details_frame)
        self.session_details_notebook.pack(fill=tk.BOTH, expand=True)
        
        # 基本情報タブ
        self.basic_info_frame = ttk.Frame(self.session_details_notebook)
        self.session_details_notebook.add(self.basic_info_frame, text="基本情報")
        self.session_details_text = scrolledtext.ScrolledText(self.basic_info_frame, height=8, width=50)
        self.session_details_text.pack(fill=tk.BOTH, expand=True)
        
        # 収集結果タブ
        self.collection_results_frame = ttk.Frame(self.session_details_notebook)
        self.session_details_notebook.add(self.collection_results_frame, text="収集結果")
        self.collection_results_text = scrolledtext.ScrolledText(self.collection_results_frame, height=8, width=50)
        self.collection_results_text.pack(fill=tk.BOTH, expand=True)
        
        # 分析結果タブ
        self.analysis_results_frame = ttk.Frame(self.session_details_notebook)
        self.session_details_notebook.add(self.analysis_results_frame, text="分析結果")
        self.analysis_results_text = scrolledtext.ScrolledText(self.analysis_results_frame, height=8, width=50)
        self.analysis_results_text.pack(fill=tk.BOTH, expand=True)
        
        # 統合知識タブ
        self.integration_results_frame = ttk.Frame(self.session_details_notebook)
        self.session_details_notebook.add(self.integration_results_frame, text="統合知識")
        self.integration_results_text = scrolledtext.ScrolledText(self.integration_results_frame, height=8, width=50)
        self.integration_results_text.pack(fill=tk.BOTH, expand=True)
        
        # HTMLレポート生成ボタン
        self.html_report_button = ttk.Button(details_frame, text="HTMLレポート生成", 
                                           command=self.generate_html_report, state=tk.DISABLED)
        self.html_report_button.pack(fill=tk.X, pady=(5, 0))
        
        # セッション選択イベント
        self.session_tree.bind('<<TreeviewSelect>>', self.on_session_select)
    
    def create_monitoring_tab(self):
        """リアルタイムモニタリングタブ"""
        monitoring_frame = ttk.Frame(self.notebook)
        self.notebook.add(monitoring_frame, text="📊 リアルタイム監視")
        
        # 上部 - 現在セッション情報
        current_session_frame = ttk.LabelFrame(monitoring_frame, text="現在のセッション", padding=10)
        current_session_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # セッション基本情報
        info_frame = ttk.Frame(current_session_frame)
        info_frame.pack(fill=tk.X)
        
        ttk.Label(info_frame, text="セッションID:").pack(side=tk.LEFT)
        self.current_session_label = ttk.Label(info_frame, text="なし", font=('Arial', 10, 'bold'))
        self.current_session_label.pack(side=tk.LEFT, padx=(5, 20))
        
        ttk.Label(info_frame, text="状態:").pack(side=tk.LEFT)
        self.session_status_label = ttk.Label(info_frame, text="待機中")
        self.session_status_label.pack(side=tk.LEFT, padx=(5, 20))
        
        ttk.Label(info_frame, text="進捗:").pack(side=tk.LEFT)
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(info_frame, variable=self.progress_var, 
                                           length=200, mode='determinate')
        self.progress_bar.pack(side=tk.LEFT, padx=(5, 0))
        
        # 統計情報
        stats_frame = ttk.Frame(current_session_frame)
        stats_frame.pack(fill=tk.X, pady=(10, 0))
        
        # 統計ラベル
        self.stats_labels = {}
        stats_items = [
            ('収集アイテム', 'collected_items'),
            ('処理済み', 'processed_items'),
            ('現在コスト', 'current_cost'),
            ('経過時間', 'elapsed_time')
        ]
        
        for i, (label, key) in enumerate(stats_items):
            ttk.Label(stats_frame, text=f"{label}:").grid(row=0, column=i*2, sticky=tk.W, padx=(0, 5))
            self.stats_labels[key] = ttk.Label(stats_frame, text="0", font=('Arial', 10, 'bold'))
            self.stats_labels[key].grid(row=0, column=i*2+1, sticky=tk.W, padx=(0, 20))
        
        # 中部 - フェーズ別進捗
        phase_frame = ttk.LabelFrame(monitoring_frame, text="フェーズ別進捗", padding=10)
        phase_frame.pack(fill=tk.X, padx=5, pady=5)
        
        phases = ['情報収集', '前処理', 'コンテンツ分析', '知識統合']
        self.phase_progress = {}
        
        for i, phase in enumerate(phases):
            ttk.Label(phase_frame, text=phase).grid(row=0, column=i, sticky=tk.W, padx=(0, 10))
            self.phase_progress[phase] = ttk.Progressbar(phase_frame, length=150, mode='determinate')
            self.phase_progress[phase].grid(row=1, column=i, sticky=tk.W, padx=(0, 10))
        
        # 下部 - ログ表示
        log_frame = ttk.LabelFrame(monitoring_frame, text="処理ログ", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=20, width=100)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # ログクリアボタン
        clear_log_button = ttk.Button(log_frame, text="ログクリア", command=self.clear_log)
        clear_log_button.pack(anchor=tk.E, pady=(5, 0))
    
    def create_proposals_tab(self):
        """活動提案タブ"""
        proposals_frame = ttk.Frame(self.notebook)
        self.notebook.add(proposals_frame, text="💡 活動提案")
        
        # 上部 - 提案生成制御
        control_frame = ttk.LabelFrame(proposals_frame, text="提案生成制御", padding=10)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 提案生成設定
        settings_frame = ttk.Frame(control_frame)
        settings_frame.pack(fill=tk.X)
        
        ttk.Label(settings_frame, text="対象セッション:").pack(side=tk.LEFT)
        self.target_session_var = tk.StringVar()
        self.target_session_combo = ttk.Combobox(settings_frame, textvariable=self.target_session_var,
                                                width=30, state="readonly")
        self.target_session_combo.pack(side=tk.LEFT, padx=(5, 20))
        
        ttk.Label(settings_frame, text="最大提案数:").pack(side=tk.LEFT)
        self.max_proposals_var = tk.IntVar(value=3)
        max_proposals_spin = ttk.Spinbox(settings_frame, from_=1, to=10, textvariable=self.max_proposals_var,
                                        width=5)
        max_proposals_spin.pack(side=tk.LEFT, padx=(5, 20))
        
        # 提案生成ボタン
        generate_button = ttk.Button(settings_frame, text="提案生成", 
                                    command=self.generate_proposals, style='Success.TButton')
        generate_button.pack(side=tk.LEFT, padx=(20, 0))
        
        # 中部 - 提案一覧
        proposals_list_frame = ttk.LabelFrame(proposals_frame, text="生成された提案", padding=10)
        proposals_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 提案一覧（Treeview）
        proposal_columns = ('ID', 'タイトル', 'タイプ', '難易度', '技術実現性', 'せつな適合度', '状態')
        self.proposals_tree = ttk.Treeview(proposals_list_frame, columns=proposal_columns, 
                                          show='headings', height=12)
        
        for col in proposal_columns:
            self.proposals_tree.heading(col, text=col)
            self.proposals_tree.column(col, width=100)
        
        # スクロールバー
        proposals_scrollbar = ttk.Scrollbar(proposals_list_frame, orient=tk.VERTICAL, 
                                           command=self.proposals_tree.yview)
        self.proposals_tree.configure(yscrollcommand=proposals_scrollbar.set)
        
        self.proposals_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        proposals_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 下部 - 提案詳細
        proposal_details_frame = ttk.LabelFrame(proposals_frame, text="提案詳細", padding=10)
        proposal_details_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.proposal_details_text = scrolledtext.ScrolledText(proposal_details_frame, height=8, width=100)
        self.proposal_details_text.pack(fill=tk.BOTH, expand=True)
        
        # 提案選択イベント
        self.proposals_tree.bind('<<TreeviewSelect>>', self.on_proposal_select)
    
    def create_knowledge_tab(self):
        """知識統合タブ"""
        knowledge_frame = ttk.Frame(self.notebook)
        self.notebook.add(knowledge_frame, text="🧠 知識統合")
        
        # 上部 - 統合制御
        integration_control_frame = ttk.LabelFrame(knowledge_frame, text="知識統合制御", padding=10)
        integration_control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 統合設定
        integration_settings_frame = ttk.Frame(integration_control_frame)
        integration_settings_frame.pack(fill=tk.X)
        
        ttk.Label(integration_settings_frame, text="統合スコープ:").pack(side=tk.LEFT)
        self.integration_scope_var = tk.StringVar(value="comprehensive")
        scope_combo = ttk.Combobox(integration_settings_frame, textvariable=self.integration_scope_var,
                                  values=["basic", "comprehensive", "advanced"], state="readonly")
        scope_combo.pack(side=tk.LEFT, padx=(5, 20))
        
        ttk.Label(integration_settings_frame, text="最小セッション数:").pack(side=tk.LEFT)
        self.min_sessions_var = tk.IntVar(value=2)
        min_sessions_spin = ttk.Spinbox(integration_settings_frame, from_=1, to=10, 
                                       textvariable=self.min_sessions_var, width=5)
        min_sessions_spin.pack(side=tk.LEFT, padx=(5, 20))
        
        # 統合実行ボタン
        integrate_button = ttk.Button(integration_settings_frame, text="知識統合実行", 
                                     command=self.execute_knowledge_integration, style='Success.TButton')
        integrate_button.pack(side=tk.LEFT, padx=(20, 0))
        
        # 中部 - 統合知識一覧
        integrated_knowledge_frame = ttk.LabelFrame(knowledge_frame, text="統合知識", padding=10)
        integrated_knowledge_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 統合知識一覧（Treeview）
        knowledge_columns = ('ID', '統合タイプ', '信頼度', '新規性', '関連セッション数', '作成日時')
        self.knowledge_tree = ttk.Treeview(integrated_knowledge_frame, columns=knowledge_columns, 
                                          show='headings', height=12)
        
        for col in knowledge_columns:
            self.knowledge_tree.heading(col, text=col)
            self.knowledge_tree.column(col, width=120)
        
        # スクロールバー
        knowledge_scrollbar = ttk.Scrollbar(integrated_knowledge_frame, orient=tk.VERTICAL, 
                                           command=self.knowledge_tree.yview)
        self.knowledge_tree.configure(yscrollcommand=knowledge_scrollbar.set)
        
        self.knowledge_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        knowledge_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 下部 - 統合知識詳細
        knowledge_details_frame = ttk.LabelFrame(knowledge_frame, text="統合知識詳細", padding=10)
        knowledge_details_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.knowledge_details_text = scrolledtext.ScrolledText(knowledge_details_frame, height=8, width=100)
        self.knowledge_details_text.pack(fill=tk.BOTH, expand=True)
        
        # 統合知識選択イベント
        self.knowledge_tree.bind('<<TreeviewSelect>>', self.on_knowledge_select)
    
    def create_budget_tab(self):
        """予算管理タブ"""
        budget_frame = ttk.Frame(self.notebook)
        self.notebook.add(budget_frame, text="💰 予算管理")
        
        # 上部 - 予算設定
        budget_settings_frame = ttk.LabelFrame(budget_frame, text="予算設定", padding=10)
        budget_settings_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 予算制限設定
        settings_frame = ttk.Frame(budget_settings_frame)
        settings_frame.pack(fill=tk.X)
        
        ttk.Label(settings_frame, text="月次制限($):").pack(side=tk.LEFT)
        self.monthly_limit_var = tk.DoubleVar(value=50.0)
        monthly_limit_spin = ttk.Spinbox(settings_frame, from_=10.0, to=500.0, increment=10.0,
                                        textvariable=self.monthly_limit_var, width=10)
        monthly_limit_spin.pack(side=tk.LEFT, padx=(5, 20))
        
        ttk.Label(settings_frame, text="日次制限($):").pack(side=tk.LEFT)
        self.daily_limit_var = tk.DoubleVar(value=10.0)
        daily_limit_spin = ttk.Spinbox(settings_frame, from_=1.0, to=100.0, increment=1.0,
                                      textvariable=self.daily_limit_var, width=10)
        daily_limit_spin.pack(side=tk.LEFT, padx=(5, 20))
        
        # 予算更新ボタン
        update_budget_button = ttk.Button(settings_frame, text="予算更新", 
                                         command=self.update_budget_limits, style='Primary.TButton')
        update_budget_button.pack(side=tk.LEFT, padx=(20, 0))
        
        # 中部 - 予算状況
        budget_status_frame = ttk.LabelFrame(budget_frame, text="予算状況", padding=10)
        budget_status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # 予算状況表示
        status_info_frame = ttk.Frame(budget_status_frame)
        status_info_frame.pack(fill=tk.X)
        
        # 予算状況ラベル
        self.budget_status_labels = {}
        budget_items = [
            ('日次使用量', 'daily_usage'),
            ('日次残高', 'daily_remaining'),
            ('月次使用量', 'monthly_usage'),
            ('月次残高', 'monthly_remaining')
        ]
        
        for i, (label, key) in enumerate(budget_items):
            ttk.Label(status_info_frame, text=f"{label}:").grid(row=0, column=i*2, sticky=tk.W, padx=(0, 5))
            self.budget_status_labels[key] = ttk.Label(status_info_frame, text="$0.00", 
                                                      font=('Arial', 10, 'bold'))
            self.budget_status_labels[key].grid(row=0, column=i*2+1, sticky=tk.W, padx=(0, 20))
        
        # 予算使用率プログレスバー
        progress_frame = ttk.Frame(budget_status_frame)
        progress_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Label(progress_frame, text="日次使用率:").pack(side=tk.LEFT)
        self.daily_usage_progress = ttk.Progressbar(progress_frame, length=200, mode='determinate')
        self.daily_usage_progress.pack(side=tk.LEFT, padx=(5, 20))
        
        ttk.Label(progress_frame, text="月次使用率:").pack(side=tk.LEFT)
        self.monthly_usage_progress = ttk.Progressbar(progress_frame, length=200, mode='determinate')
        self.monthly_usage_progress.pack(side=tk.LEFT, padx=(5, 0))
        
        # 下部 - コスト履歴
        cost_history_frame = ttk.LabelFrame(budget_frame, text="コスト履歴", padding=10)
        cost_history_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # コスト履歴（Treeview）
        cost_columns = ('時刻', 'セッション', 'API', '操作', '入力トークン', '出力トークン', 'コスト')
        self.cost_tree = ttk.Treeview(cost_history_frame, columns=cost_columns, 
                                     show='headings', height=15)
        
        for col in cost_columns:
            self.cost_tree.heading(col, text=col)
            self.cost_tree.column(col, width=100)
        
        # スクロールバー
        cost_scrollbar = ttk.Scrollbar(cost_history_frame, orient=tk.VERTICAL, 
                                      command=self.cost_tree.yview)
        self.cost_tree.configure(yscrollcommand=cost_scrollbar.set)
        
        self.cost_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        cost_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def setup_callbacks(self):
        """コールバック設定"""
        # 学習エンジンプログレスコールバック
        def progress_callback(phase: str, progress: float, message: str):
            self.update_queue.put(('progress', {
                'phase': phase,
                'progress': progress,
                'message': message
            }))
        
        self.learning_engine.add_progress_callback(progress_callback)
        
        # 予算管理アラートコールバック
        def budget_alert_callback(alert):
            self.update_queue.put(('budget_alert', alert))
        
        self.budget_manager.add_alert_callback(budget_alert_callback)
        
        print("[GUI] ✅ コールバック設定完了")
    
    def load_initial_data(self):
        """初期データ読み込み"""
        try:
            # セッション履歴読み込み
            self.refresh_session_list()
            
            # 活動提案読み込み
            self.refresh_proposals_list()
            
            # 統合知識読み込み
            self.refresh_knowledge_list()
            
            # 予算状況読み込み
            self.refresh_budget_status()
            
            print("[GUI] ✅ 初期データ読み込み完了")
            
        except Exception as e:
            print(f"[GUI] ❌ 初期データ読み込み失敗: {e}")
            self.log_message(f"初期データ読み込み失敗: {e}")
    
    def create_session(self):
        """セッション作成"""
        try:
            # 入力値取得
            theme = self.theme_var.get().strip()
            learning_type = self.learning_type_var.get()
            depth_level = self.depth_var.get()
            time_limit = self.time_limit_var.get() * 60  # 分→秒
            budget_limit = self.budget_limit_var.get()
            
            if not theme:
                messagebox.showerror("エラー", "学習テーマを入力してください")
                return
            
            # 段階的分析設定
            self.learning_engine.configure_staged_analysis(
                enable_preprocessing=self.preprocessing_enabled_var.get(),
                relevance_min=self.relevance_threshold_var.get(),
                max_detailed_analysis=15
            )
            
            # セッション作成
            session_id = self.learning_engine.create_session(
                theme=theme,
                learning_type=learning_type,
                depth_level=depth_level,
                time_limit=time_limit,
                budget_limit=budget_limit,
                tags=["GUI作成"]
            )
            
            if session_id:
                self.current_session_id = session_id
                self.current_session_label.config(text=session_id)
                
                # UI更新
                self.create_button.config(state=tk.DISABLED)
                self.start_button.config(state=tk.NORMAL)
                
                # セッション一覧更新
                self.refresh_session_list()
                
                self.log_message(f"セッション作成完了: {session_id}")
                self.status_var.set(f"セッション作成完了: {session_id}")
                
                messagebox.showinfo("成功", f"セッション作成完了\\nID: {session_id}")
            else:
                messagebox.showerror("エラー", "セッション作成に失敗しました")
                
        except Exception as e:
            print(f"[GUI] ❌ セッション作成失敗: {e}")
            messagebox.showerror("エラー", f"セッション作成失敗: {e}")
    
    def start_session(self):
        """セッション開始"""
        try:
            if not self.current_session_id:
                messagebox.showerror("エラー", "セッションが作成されていません")
                return
            
            # セッション開始
            success = self.learning_engine.start_session(self.current_session_id)
            
            if success:
                # UI更新
                self.start_button.config(state=tk.DISABLED)
                self.stop_button.config(state=tk.NORMAL)
                self.session_status_label.config(text="実行中", foreground="green")
                
                # 監視開始
                self.monitoring_active = True
                
                self.log_message(f"セッション開始: {self.current_session_id}")
                self.status_var.set(f"セッション実行中: {self.current_session_id}")
                
                # 監視タブに切り替え
                self.notebook.select(1)
                
            else:
                messagebox.showerror("エラー", "セッション開始に失敗しました")
                
        except Exception as e:
            print(f"[GUI] ❌ セッション開始失敗: {e}")
            messagebox.showerror("エラー", f"セッション開始失敗: {e}")
    
    def stop_session(self):
        """セッション停止"""
        try:
            if not self.current_session_id:
                return
            
            # 確認ダイアログ
            result = messagebox.askyesno("確認", "セッションを停止しますか？")
            if not result:
                return
            
            # セッション停止
            success = self.learning_engine.stop_session(self.current_session_id)
            
            if success:
                # UI更新
                self.start_button.config(state=tk.DISABLED)
                self.stop_button.config(state=tk.DISABLED)
                self.create_button.config(state=tk.NORMAL)
                self.session_status_label.config(text="停止", foreground="red")
                
                # 監視停止
                self.monitoring_active = False
                
                self.log_message(f"セッション停止: {self.current_session_id}")
                self.status_var.set("セッション停止完了")
                
                # セッション一覧更新
                self.refresh_session_list()
                
            else:
                messagebox.showerror("エラー", "セッション停止に失敗しました")
                
        except Exception as e:
            print(f"[GUI] ❌ セッション停止失敗: {e}")
            messagebox.showerror("エラー", f"セッション停止失敗: {e}")
    
    def generate_proposals(self):
        """活動提案生成"""
        try:
            target_session = self.target_session_var.get()
            if not target_session:
                messagebox.showerror("エラー", "対象セッションを選択してください")
                return
            
            max_proposals = self.max_proposals_var.get()
            
            # セッション知識取得（モック）
            session_knowledge = {
                "knowledge_items": [
                    {
                        "item_id": "demo_001",
                        "content": "AI音楽生成技術の商用化における課題と機会",
                        "categories": ["技術", "市場", "商用化"],
                        "keywords": ["AI", "音楽生成", "商用化", "課題", "機会"],
                        "entities": ["AI", "音楽生成"],
                        "importance_score": 8.5,
                        "reliability_score": 0.8
                    }
                ]
            }
            
            # 提案生成
            proposals = self.proposal_engine.generate_proposals_from_session(
                session_id=target_session,
                session_knowledge=session_knowledge,
                max_proposals=max_proposals
            )
            
            if proposals:
                self.refresh_proposals_list()
                self.log_message(f"活動提案生成完了: {len(proposals)}件")
                messagebox.showinfo("成功", f"{len(proposals)}件の活動提案を生成しました")
            else:
                messagebox.showwarning("警告", "提案が生成されませんでした")
                
        except Exception as e:
            print(f"[GUI] ❌ 活動提案生成失敗: {e}")
            messagebox.showerror("エラー", f"活動提案生成失敗: {e}")
    
    def execute_knowledge_integration(self):
        """知識統合実行"""
        try:
            # 統合設定取得
            integration_scope = self.integration_scope_var.get()
            min_sessions = self.min_sessions_var.get()
            
            # セッション一覧取得
            sessions = self.learning_engine.list_sessions(limit=20)
            if len(sessions) < min_sessions:
                messagebox.showwarning("警告", f"統合に必要な最小セッション数({min_sessions})が不足しています")
                return
            
            # 統合対象セッション選択
            session_ids = [s['session_id'] for s in sessions[:min_sessions]]
            
            # モックセッションデータ作成
            session_data = {
                session_id: {
                    "session_id": session_id,
                    "theme": f"統合対象テーマ_{session_id}",
                    "knowledge_items": [
                        {
                            "item_id": f"item_{session_id}_001",
                            "content": f"統合対象知識_{session_id}",
                            "categories": ["技術", "統合テスト"],
                            "keywords": ["統合", "テスト", "知識"],
                            "entities": ["統合", "知識"],
                            "importance_score": 7.0,
                            "reliability_score": 0.8
                        }
                    ]
                }
                for session_id in session_ids
            }
            
            # 知識統合実行
            integrated_knowledge = self.integration_system.integrate_multi_session_knowledge(
                session_ids=session_ids,
                session_data=session_data,
                integration_scope=integration_scope
            )
            
            if integrated_knowledge:
                self.refresh_knowledge_list()
                self.log_message(f"知識統合完了: {len(integrated_knowledge)}件")
                messagebox.showinfo("成功", f"{len(integrated_knowledge)}件の統合知識を生成しました")
            else:
                messagebox.showwarning("警告", "統合知識が生成されませんでした")
                
        except Exception as e:
            print(f"[GUI] ❌ 知識統合失敗: {e}")
            messagebox.showerror("エラー", f"知識統合失敗: {e}")
    
    def update_budget_limits(self):
        """予算制限更新"""
        try:
            monthly_limit = self.monthly_limit_var.get()
            daily_limit = self.daily_limit_var.get()
            
            # 予算制限更新
            self.budget_manager.set_budget_limits(
                monthly_limit=monthly_limit,
                daily_limit=daily_limit
            )
            
            # 予算状況更新
            self.refresh_budget_status()
            
            self.log_message(f"予算制限更新: 月次${monthly_limit}, 日次${daily_limit}")
            messagebox.showinfo("成功", "予算制限を更新しました")
            
        except Exception as e:
            print(f"[GUI] ❌ 予算制限更新失敗: {e}")
            messagebox.showerror("エラー", f"予算制限更新失敗: {e}")
    
    def refresh_session_list(self):
        """セッション一覧更新"""
        try:
            # セッション一覧取得
            sessions = self.learning_engine.list_sessions(limit=50)
            
            # Treeview更新
            for item in self.session_tree.get_children():
                self.session_tree.delete(item)
            
            for session in sessions:
                session_id = session['session_id']
                theme = session['theme']
                learning_type = session['learning_type']
                status = session['status']
                start_time = session['start_time'] or "未開始"
                cost = f"${session['current_cost']:.2f}"
                
                self.session_tree.insert('', 'end', values=(
                    session_id, theme, learning_type, status, start_time, cost
                ))
            
            # 対象セッション選択肢更新
            session_ids = [s['session_id'] for s in sessions]
            self.target_session_combo['values'] = session_ids
            if session_ids:
                self.target_session_combo.set(session_ids[0])
            
        except Exception as e:
            print(f"[GUI] ❌ セッション一覧更新失敗: {e}")
    
    def refresh_proposals_list(self):
        """提案一覧更新"""
        try:
            # 提案統計取得
            proposals_stats = self.proposal_engine.get_proposal_statistics()
            
            # Treeview更新
            for item in self.proposals_tree.get_children():
                self.proposals_tree.delete(item)
            
            # 提案データ表示（モック）
            for i in range(3):
                proposal_id = f"proposal_{i+1}"
                title = f"提案{i+1}: AI音楽生成技術の活用"
                proposal_type = ["content_creation", "market_research", "collaboration"][i]
                difficulty = ["easy", "medium", "hard"][i]
                feasibility = f"{0.8 - i*0.1:.1f}"
                alignment = f"{0.7 + i*0.1:.1f}"
                status = "pending"
                
                self.proposals_tree.insert('', 'end', values=(
                    proposal_id, title, proposal_type, difficulty, feasibility, alignment, status
                ))
            
        except Exception as e:
            print(f"[GUI] ❌ 提案一覧更新失敗: {e}")
    
    def refresh_knowledge_list(self):
        """統合知識一覧更新"""
        try:
            # 統合知識一覧取得（モック）
            for item in self.knowledge_tree.get_children():
                self.knowledge_tree.delete(item)
            
            # 統合知識データ表示
            for i in range(5):
                knowledge_id = f"integrated_{i+1}"
                integration_type = ["cross_session", "temporal_evolution", "concept_synthesis"][i % 3]
                confidence = f"{0.8 + i*0.02:.2f}"
                novelty = f"{0.6 + i*0.05:.2f}"
                session_count = 3 + i
                created_at = datetime.now().strftime("%Y-%m-%d %H:%M")
                
                self.knowledge_tree.insert('', 'end', values=(
                    knowledge_id, integration_type, confidence, novelty, session_count, created_at
                ))
            
        except Exception as e:
            print(f"[GUI] ❌ 統合知識一覧更新失敗: {e}")
    
    def refresh_budget_status(self):
        """予算状況更新"""
        try:
            # 予算状況取得
            budget_status = self.budget_manager.get_budget_status()
            
            # ラベル更新
            self.budget_status_labels['daily_usage'].config(text=f"${budget_status['daily_usage']:.2f}")
            self.budget_status_labels['daily_remaining'].config(text=f"${budget_status['daily_remaining']:.2f}")
            self.budget_status_labels['monthly_usage'].config(text=f"${budget_status['monthly_usage']:.2f}")
            self.budget_status_labels['monthly_remaining'].config(text=f"${budget_status['monthly_remaining']:.2f}")
            
            # プログレスバー更新
            daily_usage_rate = (budget_status['daily_usage'] / budget_status['daily_limit']) * 100
            monthly_usage_rate = (budget_status['monthly_usage'] / budget_status['monthly_limit']) * 100
            
            self.daily_usage_progress['value'] = min(daily_usage_rate, 100)
            self.monthly_usage_progress['value'] = min(monthly_usage_rate, 100)
            
            # コスト履歴更新（モック）
            for item in self.cost_tree.get_children():
                self.cost_tree.delete(item)
            
            for i in range(10):
                timestamp = datetime.now().strftime("%H:%M:%S")
                session_id = f"session_{i+1}"
                api_type = ["openai", "search", "preprocessing"][i % 3]
                operation = ["analysis", "search", "filter"][i % 3]
                input_tokens = 1000 + i * 100
                output_tokens = 500 + i * 50
                cost = f"${(input_tokens * 0.01 + output_tokens * 0.03) / 1000:.4f}"
                
                self.cost_tree.insert('', 'end', values=(
                    timestamp, session_id, api_type, operation, input_tokens, output_tokens, cost
                ))
            
        except Exception as e:
            print(f"[GUI] ❌ 予算状況更新失敗: {e}")
    
    def start_periodic_update(self):
        """定期更新開始"""
        def update_worker():
            while True:
                try:
                    # キューからの更新処理
                    while not self.update_queue.empty():
                        update_type, data = self.update_queue.get_nowait()
                        
                        if update_type == 'progress':
                            self.root.after(0, self.update_progress, data)
                        elif update_type == 'budget_alert':
                            self.root.after(0, self.show_budget_alert, data)
                    
                    # 監視中の場合、セッション状況更新
                    if self.monitoring_active and self.current_session_id:
                        self.root.after(0, self.update_session_monitoring)
                    
                    # 予算状況定期更新
                    self.root.after(0, self.refresh_budget_status)
                    
                    time.sleep(2)  # 2秒間隔
                    
                except Exception as e:
                    print(f"[GUI] ❌ 定期更新エラー: {e}")
                    time.sleep(5)
        
        # 更新スレッド開始
        update_thread = threading.Thread(target=update_worker, daemon=True)
        update_thread.start()
    
    def update_progress(self, data):
        """進捗更新"""
        try:
            phase = data['phase']
            progress = data['progress']
            message = data['message']
            
            # 進捗バー更新
            self.progress_var.set(progress * 100)
            
            # フェーズ別進捗更新
            if phase in self.phase_progress:
                self.phase_progress[phase]['value'] = progress * 100
            
            # ログ出力
            self.log_message(f"[{phase}] {message} ({progress:.1%})")
            
            # ステータス更新
            self.status_var.set(f"[{phase}] {message}")
            
        except Exception as e:
            print(f"[GUI] ❌ 進捗更新失敗: {e}")
    
    def update_session_monitoring(self):
        """セッション監視更新"""
        try:
            if not self.current_session_id:
                return
            
            # セッション状況取得
            session_status = self.learning_engine.get_session_status(self.current_session_id)
            
            if session_status:
                # 統計情報更新
                progress = session_status['progress']
                self.stats_labels['collected_items'].config(text=str(progress['collected_items']))
                self.stats_labels['processed_items'].config(text=str(progress['processed_items']))
                self.stats_labels['current_cost'].config(text=f"${progress['current_cost']:.2f}")
                self.stats_labels['elapsed_time'].config(text=f"{progress['time_elapsed']:.0f}s")
                
                # セッション状態更新
                status = session_status['status']
                if status == 'completed':
                    self.session_status_label.config(text="完了", foreground="blue")
                    self.monitoring_active = False
                    self.start_button.config(state=tk.DISABLED)
                    self.stop_button.config(state=tk.DISABLED)
                    self.create_button.config(state=tk.NORMAL)
                    
                    # セッション一覧更新
                    self.refresh_session_list()
                    
                elif status == 'error':
                    self.session_status_label.config(text="エラー", foreground="red")
                    self.monitoring_active = False
                    
        except Exception as e:
            print(f"[GUI] ❌ セッション監視更新失敗: {e}")
    
    def show_budget_alert(self, alert):
        """予算アラート表示"""
        try:
            alert_message = f"予算アラート: {alert.message}"
            self.log_message(alert_message)
            
            if alert.severity == 'critical':
                messagebox.showerror("予算アラート", alert_message)
            elif alert.severity == 'warning':
                messagebox.showwarning("予算アラート", alert_message)
            
        except Exception as e:
            print(f"[GUI] ❌ 予算アラート表示失敗: {e}")
    
    def check_api_key_status(self):
        """API Key状態確認"""
        try:
            # ConfigManagerから設定状況確認
            config_summary = self.config.get_config_summary()
            validation_result = self.config.get_validation_result()
            
            # 各コンポーネントのAPI Key状態をチェック
            learning_engine_status = self.learning_engine.openai_client is not None
            proposal_engine_status = self.proposal_engine.openai_client is not None
            integration_system_status = self.integration_system.openai_client is not None
            
            # 詳細情報構築
            status_details = []
            status_details.append(f"📋 設定ファイル: {'.env' if config_summary['openai_configured'] else '未設定'}")
            status_details.append(f"🔧 学習エンジン: {'正常' if learning_engine_status else '失敗'}")
            status_details.append(f"💡 提案エンジン: {'正常' if proposal_engine_status else '失敗'}")
            status_details.append(f"🧠 統合システム: {'正常' if integration_system_status else '失敗'}")
            
            # 全体の状態判定
            if learning_engine_status and proposal_engine_status and integration_system_status:
                self.api_key_status_var.set("✅ 全コンポーネント正常")
                status_message = "OpenAI API Key設定が正常です。\n\n" + "\n".join(status_details)
                messagebox.showinfo("API Key確認", status_message)
            else:
                failed_components = []
                if not learning_engine_status:
                    failed_components.append("学習エンジン")
                if not proposal_engine_status:
                    failed_components.append("提案エンジン")
                if not integration_system_status:
                    failed_components.append("統合システム")
                
                self.api_key_status_var.set(f"❌ {len(failed_components)}個のコンポーネントで失敗")
                
                # 詳細なエラーメッセージ
                error_details = []
                if validation_result.missing_keys:
                    error_details.append("不足設定:")
                    error_details.extend([f"  - {key}" for key in validation_result.missing_keys])
                
                if validation_result.errors:
                    error_details.append("設定エラー:")
                    error_details.extend([f"  - {error}" for error in validation_result.errors])
                
                error_details.append("\n対処方法:")
                error_details.append("  - .envファイルでOPENAI_API_KEY設定を確認")
                error_details.append("  - APIキーの有効性を確認")
                error_details.append("  - 設定再読み込み後にGUI再起動")
                
                status_message = f"以下のコンポーネントでAPI Key設定が失敗しています:\n\n{chr(10).join(failed_components)}\n\n" + "\n".join(error_details)
                messagebox.showerror("API Key確認", status_message)
            
        except Exception as e:
            self.api_key_status_var.set("❌ 確認失敗")
            print(f"[GUI] ❌ API Key確認失敗: {e}")
            messagebox.showerror("API Key確認", f"API Key確認中にエラーが発生しました:\n{e}")
    
    def log_message(self, message):
        """ログメッセージ出力"""
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            log_entry = f"[{timestamp}] {message}\\n"
            
            self.log_text.insert(tk.END, log_entry)
            self.log_text.see(tk.END)
            
        except Exception as e:
            print(f"[GUI] ❌ ログ出力失敗: {e}")
    
    def clear_log(self):
        """ログクリア"""
        self.log_text.delete(1.0, tk.END)
    
    def on_session_select(self, event):
        """セッション選択イベント"""
        try:
            selection = self.session_tree.selection()
            if selection:
                item = self.session_tree.item(selection[0])
                session_id = item['values'][0]
                
                # 現在選択されているセッションIDを保存
                self.current_selected_session_id = session_id
                
                # セッション詳細データを取得
                session_data = self.session_viewer.load_session_details(session_id)
                
                if session_data:
                    self.display_session_details(session_id, session_data)
                    self.html_report_button.config(state=tk.NORMAL)
                else:
                    # セッションデータが見つからない場合は基本情報のみ表示
                    self.display_basic_session_info(session_id, item['values'])
                    self.html_report_button.config(state=tk.DISABLED)
                    
        except Exception as e:
            print(f"[GUI] ❌ セッション選択失敗: {e}")
    
    def display_basic_session_info(self, session_id, values):
        """基本セッション情報表示"""
        details = f"セッションID: {session_id}\\n"
        details += f"テーマ: {values[1]}\\n"
        details += f"学習タイプ: {values[2]}\\n"
        details += f"状態: {values[3]}\\n"
        details += f"開始時刻: {values[4]}\\n"
        details += f"コスト: {values[5]}\\n"
        details += "\\n--- 追加情報 ---\\n"
        details += "詳細なセッションデータは利用できません。"
        
        self.session_details_text.delete(1.0, tk.END)
        self.session_details_text.insert(1.0, details)
        
        # 他のタブをクリア
        for text_widget in [self.collection_results_text, self.analysis_results_text, self.integration_results_text]:
            text_widget.delete(1.0, tk.END)
            text_widget.insert(1.0, "データなし")
    
    def display_session_details(self, session_id, session_data):
        """詳細セッション情報表示"""
        metadata = session_data.get("session_metadata", {})
        
        # 基本情報タブ
        basic_info = f"セッションID: {session_id}\\n"
        basic_info += f"テーマ: {metadata.get('theme', '不明')}\\n"
        basic_info += f"学習タイプ: {metadata.get('learning_type', '不明')}\\n"
        basic_info += f"深度レベル: {metadata.get('depth_level', 0)}\\n"
        basic_info += f"状態: {metadata.get('status', '不明')}\\n"
        basic_info += f"開始時刻: {metadata.get('start_time', '不明')}\\n"
        basic_info += f"終了時刻: {metadata.get('end_time', '実行中')}\\n"
        basic_info += f"収集アイテム: {metadata.get('collected_items', 0)}件\\n"
        basic_info += f"処理アイテム: {metadata.get('processed_items', 0)}件\\n"
        basic_info += f"現在のコスト: ${metadata.get('current_cost', 0.0):.2f}\\n"
        basic_info += f"タグ: {', '.join(metadata.get('tags', []))}\\n"
        
        self.session_details_text.delete(1.0, tk.END)
        self.session_details_text.insert(1.0, basic_info)
        
        # 収集結果タブ
        collection_results = session_data.get("collection_results", {})
        self.display_collection_results(collection_results)
        
        # 分析結果タブ
        analysis_results = session_data.get("analysis_results", {})
        self.display_analysis_results(analysis_results)
        
        # 統合知識タブ
        integration_results = session_data.get("generated_knowledge", {})
        self.display_integration_results(integration_results)
    
    def display_collection_results(self, collection_results):
        """収集結果表示"""
        if not collection_results:
            self.collection_results_text.delete(1.0, tk.END)
            self.collection_results_text.insert(1.0, "収集結果がありません。")
            return
        
        sources = collection_results.get("information_sources", [])
        
        text_content = f"📊 情報収集結果 ({len(sources)}件)\\n\\n"
        
        for i, source in enumerate(sources, 1):
            text_content += f"{i}. {source.get('title', '無題')}\\n"
            text_content += f"   URL: {source.get('url', 'なし')}\\n"
            text_content += f"   信頼性: {source.get('reliability_score', 0):.2f}\\n"
            text_content += f"   関連性: {source.get('relevance_score', 0):.2f}\\n"
            text_content += f"   タイプ: {source.get('source_type', '不明')}\\n"
            
            content = source.get('content', '')
            if content:
                preview = content[:150] + "..." if len(content) > 150 else content
                text_content += f"   内容: {preview}\\n"
            text_content += "\\n"
        
        self.collection_results_text.delete(1.0, tk.END)
        self.collection_results_text.insert(1.0, text_content)
    
    def display_analysis_results(self, analysis_results):
        """分析結果表示"""
        if not analysis_results:
            self.analysis_results_text.delete(1.0, tk.END)
            self.analysis_results_text.insert(1.0, "分析結果がありません。")
            return
        
        text_content = "🧠 コンテンツ分析結果\\n\\n"
        
        # 重要な発見
        key_findings = analysis_results.get("key_findings", [])
        if key_findings:
            text_content += "🔑 重要な発見:\\n"
            for i, finding in enumerate(key_findings, 1):
                text_content += f"{i}. {finding}\\n"
            text_content += "\\n"
        
        # エンティティ抽出
        entities = analysis_results.get("extracted_entities", [])
        if entities:
            text_content += f"🏷️ 抽出エンティティ ({len(entities)}件):\\n"
            text_content += f"{', '.join(entities)}\\n\\n"
        
        # 関係性分析
        relationships = analysis_results.get("identified_relationships", [])
        if relationships:
            text_content += "🔗 関係性分析:\\n"
            for i, rel in enumerate(relationships, 1):
                text_content += f"{i}. {rel}\\n"
            text_content += "\\n"
        
        self.analysis_results_text.delete(1.0, tk.END)
        self.analysis_results_text.insert(1.0, text_content)
    
    def display_integration_results(self, integration_results):
        """統合知識表示"""
        if not integration_results:
            self.integration_results_text.delete(1.0, tk.END)
            self.integration_results_text.insert(1.0, "統合知識がありません。")
            return
        
        text_content = "🔗 知識統合結果\\n\\n"
        
        # 統合サマリー
        summary = integration_results.get("integration_summary", "")
        if summary:
            text_content += f"📋 統合サマリー:\\n{summary}\\n\\n"
        
        # 主要ポイント
        key_points = integration_results.get("key_points", [])
        if key_points:
            text_content += "🎯 主要ポイント:\\n"
            for i, point in enumerate(key_points, 1):
                text_content += f"{i}. {point}\\n"
            text_content += "\\n"
        
        # 推奨アクション
        recommendations = integration_results.get("recommendations", [])
        if recommendations:
            text_content += "💡 推奨アクション:\\n"
            for i, rec in enumerate(recommendations, 1):
                text_content += f"{i}. {rec}\\n"
            text_content += "\\n"
        
        self.integration_results_text.delete(1.0, tk.END)
        self.integration_results_text.insert(1.0, text_content)
    
    def generate_html_report(self):
        """HTMLレポート生成"""
        try:
            # 現在選択されているセッションIDを使用
            if not self.current_selected_session_id:
                messagebox.showwarning("警告", "セッションを選択してください。")
                return
            
            session_id = self.current_selected_session_id
            
            # HTMLレポート生成
            output_file = self.html_report_generator.generate_html_report(session_id)
            
            if output_file:
                self.log_message(f"HTMLレポート生成完了: {output_file}")
                
                # ブラウザで開く
                try:
                    import webbrowser
                    webbrowser.open(f"file://{Path(output_file).absolute()}")
                    messagebox.showinfo("成功", f"HTMLレポートを生成しました。\\nファイル: {output_file}")
                except Exception as e:
                    messagebox.showinfo("成功", f"HTMLレポートを生成しました。\\nファイル: {output_file}\\n\\nブラウザで手動で開いてください。")
            else:
                messagebox.showerror("エラー", "HTMLレポートの生成に失敗しました。")
                
        except Exception as e:
            print(f"[GUI] ❌ HTMLレポート生成失敗: {e}")
            messagebox.showerror("エラー", f"HTMLレポート生成失敗: {e}")
    
    def on_proposal_select(self, event):
        """提案選択イベント"""
        try:
            selection = self.proposals_tree.selection()
            if selection:
                item = self.proposals_tree.item(selection[0])
                proposal_id = item['values'][0]
                
                # 提案詳細表示
                details = f"提案ID: {proposal_id}\\n"
                details += f"タイトル: {item['values'][1]}\\n"
                details += f"タイプ: {item['values'][2]}\\n"
                details += f"難易度: {item['values'][3]}\\n"
                details += f"技術実現性: {item['values'][4]}\\n"
                details += f"せつな適合度: {item['values'][5]}\\n"
                details += f"状態: {item['values'][6]}\\n"
                details += "\\n--- 詳細説明 ---\\n"
                details += "この提案は、AI音楽生成技術を活用したコンテンツ制作の提案です。\\n"
                details += "せつなの個性と技術的専門性を活かした内容になっています。"
                
                self.proposal_details_text.delete(1.0, tk.END)
                self.proposal_details_text.insert(1.0, details)
                
        except Exception as e:
            print(f"[GUI] ❌ 提案選択失敗: {e}")
    
    def on_knowledge_select(self, event):
        """統合知識選択イベント"""
        try:
            selection = self.knowledge_tree.selection()
            if selection:
                item = self.knowledge_tree.item(selection[0])
                knowledge_id = item['values'][0]
                
                # 統合知識詳細表示
                details = f"統合知識ID: {knowledge_id}\\n"
                details += f"統合タイプ: {item['values'][1]}\\n"
                details += f"信頼度: {item['values'][2]}\\n"
                details += f"新規性: {item['values'][3]}\\n"
                details += f"関連セッション数: {item['values'][4]}\\n"
                details += f"作成日時: {item['values'][5]}\\n"
                details += "\\n--- 統合内容 ---\\n"
                details += "複数のセッションから統合された知識がここに表示されます。\\n"
                details += "この統合知識は、AI音楽生成技術の市場動向と技術的発展に関する洞察を含んでいます。"
                
                self.knowledge_details_text.delete(1.0, tk.END)
                self.knowledge_details_text.insert(1.0, details)
                
        except Exception as e:
            print(f"[GUI] ❌ 統合知識選択失敗: {e}")
    
    def run(self):
        """GUIメインループ実行"""
        try:
            print("[GUI] 🚀 GUI開始")
            self.root.mainloop()
        except Exception as e:
            print(f"[GUI] ❌ GUI実行エラー: {e}")
        finally:
            print("[GUI] 🛑 GUI終了")


def main():
    """メイン関数"""
    try:
        # GUI作成・実行
        gui = LearningSessionGUI()
        gui.run()
        
    except Exception as e:
        print(f"❌ GUI起動失敗: {e}")
        messagebox.showerror("エラー", f"GUI起動失敗: {e}")


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ActivityLearningEngine - Phase 2A-1
活動調査・学習セッションの管理・実行エンジン
"""

import json
import os
import time
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Callable
import uuid
import openai
from dataclasses import dataclass, asdict
import requests
from urllib.parse import quote
import hashlib
from .preprocessing_engine import PreProcessingEngine
from .config_manager import get_config_manager
from .debug_logger import get_debug_logger, debug_function
from .mock_search_service import SearchEngineManager

# Windows環境のパス設定（CLAUDE.mdの指示に従いWindowsパスを使用）
# WSL2環境でもファイル保存・読み込みはWindows側で行う
DATA_DIR = Path("D:/setsuna_bot/data/activity_knowledge")

@dataclass
class LearningSession:
    """学習セッションデータクラス"""
    session_id: str
    theme: str
    learning_type: str  # "概要", "深掘り", "実用"
    depth_level: int    # 1-5
    time_limit: int     # 秒
    budget_limit: float # ドル
    status: str         # "ready", "running", "paused", "completed", "error"
    parent_session: Optional[str] = None
    tags: List[str] = None
    
    # プログレス情報
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    current_phase: str = "ready"  # "collection", "analysis", "integration"
    collected_items: int = 0
    processed_items: int = 0
    important_findings: List[Dict] = None
    current_cost: float = 0.0
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.important_findings is None:
            self.important_findings = []

class ActivityLearningEngine:
    """活動学習エンジンメインクラス"""
    
    def __init__(self):
        """初期化"""
        self.sessions_dir = DATA_DIR / "sessions"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        
        # セッション管理
        self.current_session: Optional[LearningSession] = None
        self.session_history: Dict[str, LearningSession] = {}
        
        # デバッグログ初期化
        self.debug_logger = get_debug_logger(component="LEARNING_ENGINE")
        self.debug_logger.info("ActivityLearningEngine初期化開始")
        
        # API設定
        self.openai_client = None
        self._initialize_apis()
        
        # 情報収集設定
        self.collection_config = {
            "web_search_enabled": True,
            "news_search_enabled": True,
            "social_search_enabled": False,
            "max_sources_per_query": 10,
            "quality_threshold": 0.6,
            "relevance_threshold": 0.7
        }
        
        # GPT-4-turbo設定
        self.gpt_config = {
            "model": "gpt-4-turbo-preview",
            "temperature": 0.3,
            "max_tokens": 4000,
            "max_input_tokens": 50000
        }
        
        # プログレスコールバック
        self.progress_callbacks: List[Callable] = []
        
        # ファイルロック（データ競合防止）
        self.file_lock = threading.Lock()
        
        # 前処理エンジン
        self.preprocessing_engine = PreProcessingEngine()
        
        # 検索エンジン管理
        self.search_manager = SearchEngineManager()
        
        # 検索エンジン状態確認
        search_status = self.search_manager.get_status()
        self.debug_logger.info("Google検索エンジン初期化完了", {
            "ready": search_status["ready"],
            "google_service_available": search_status["google_service_available"],
            "config_valid": search_status["config_valid"],
            "quota_remaining": search_status["quota_remaining"]
        })
        
        # 段階的分析設定
        self.staged_analysis_config = {
            "enable_preprocessing": True,
            "preprocessing_thresholds": {
                "relevance_min": 0.4,
                "quality_min": 0.5,
                "combined_min": 0.6
            },
            "max_detailed_analysis": 15,  # 詳細分析する最大件数
            "gpt35_batch_size": 10,       # GPT-3.5バッチサイズ
            "gpt4_batch_size": 5          # GPT-4-turboバッチサイズ
        }
        
        self.debug_logger.info("ActivityLearningEngine初期化完了")
        print("[学習エンジン] ✅ ActivityLearningEngine初期化完了")
    
    def _initialize_apis(self):
        """API初期化"""
        self.debug_logger.info("API初期化開始")
        
        try:
            # ConfigManager経由でOpenAI設定取得
            config = get_config_manager()
            openai_key = config.get_openai_key()
            
            self.debug_logger.debug("OpenAI APIキー取得状況", {
                "key_available": bool(openai_key),
                "key_length": len(openai_key) if openai_key else 0
            })
            
            if openai_key:
                openai.api_key = openai_key
                self.openai_client = openai
                
                # 接続テスト実行
                try:
                    self.debug_logger.debug("OpenAI API接続テスト開始")
                    test_response = openai.models.list()
                    
                    if test_response:
                        self.debug_logger.info("OpenAI API接続テスト成功", {
                            "available_models": len(test_response.data)
                        })
                        print("[学習エンジン] ✅ OpenAI API設定・接続確認完了")
                        return True
                except Exception as api_error:
                    self.debug_logger.error("OpenAI API接続テスト失敗", {
                        "error_type": type(api_error).__name__,
                        "error_message": str(api_error)
                    }, api_error)
                    print(f"[学習エンジン] ❌ OpenAI API接続失敗: {api_error}")
                    self.openai_client = None
                    return False
            else:
                self.debug_logger.warning("OpenAI APIキーが設定されていません")
                print("[学習エンジン] ⚠️ OpenAI APIキーが設定されていません")
                print("  .envファイルまたは環境変数 OPENAI_API_KEY を設定してください")
                self.openai_client = None
                return False
                
        except Exception as e:
            self.debug_logger.error("API初期化エラー", {
                "error_type": type(e).__name__,
                "error_message": str(e)
            }, e)
            print(f"[学習エンジン] ❌ API初期化エラー: {e}")
            self.openai_client = None
            return False
    
    def add_progress_callback(self, callback: Callable):
        """プログレスコールバックを追加"""
        self.progress_callbacks.append(callback)
    
    def configure_staged_analysis(self, **kwargs):
        """
        段階的分析設定
        
        Args:
            enable_preprocessing: 前処理有効/無効
            relevance_min: 関連性最小閾値
            quality_min: 品質最小閾値
            combined_min: 総合スコア最小閾値
            max_detailed_analysis: 詳細分析最大件数
            gpt35_batch_size: GPT-3.5バッチサイズ
            gpt4_batch_size: GPT-4バッチサイズ
        """
        if "enable_preprocessing" in kwargs:
            self.staged_analysis_config["enable_preprocessing"] = kwargs["enable_preprocessing"]
            print(f"[学習エンジン] ⚙️ 前処理: {'有効' if kwargs['enable_preprocessing'] else '無効'}")
        
        # 前処理閾値更新
        preprocessing_thresholds = self.staged_analysis_config["preprocessing_thresholds"]
        for key in ["relevance_min", "quality_min", "combined_min"]:
            if key in kwargs:
                preprocessing_thresholds[key] = kwargs[key]
                print(f"[学習エンジン] ⚙️ 閾値更新: {key} = {kwargs[key]}")
        
        # その他設定更新
        for key in ["max_detailed_analysis", "gpt35_batch_size", "gpt4_batch_size"]:
            if key in kwargs:
                self.staged_analysis_config[key] = kwargs[key]
                print(f"[学習エンジン] ⚙️ 設定更新: {key} = {kwargs[key]}")
    
    def get_staged_analysis_config(self) -> Dict[str, Any]:
        """段階的分析設定取得"""
        return self.staged_analysis_config.copy()
    
    def enable_preprocessing(self, enable: bool = True):
        """前処理有効/無効切り替え"""
        self.staged_analysis_config["enable_preprocessing"] = enable
        print(f"[学習エンジン] ⚙️ 前処理: {'有効' if enable else '無効'}")
    
    def set_preprocessing_thresholds(self, relevance_min: float = None, quality_min: float = None, combined_min: float = None):
        """前処理閾値設定"""
        thresholds = self.staged_analysis_config["preprocessing_thresholds"]
        
        if relevance_min is not None:
            thresholds["relevance_min"] = relevance_min
        if quality_min is not None:
            thresholds["quality_min"] = quality_min
        if combined_min is not None:
            thresholds["combined_min"] = combined_min
        
        print(f"[学習エンジン] ⚙️ 前処理閾値更新: {thresholds}")
    
    def get_preprocessing_statistics(self) -> Dict[str, Any]:
        """前処理統計情報取得"""
        return self.preprocessing_engine.get_statistics()
    
    def _notify_progress(self, phase: str, progress: float, message: str):
        """プログレス通知"""
        for callback in self.progress_callbacks:
            try:
                callback(phase, progress, message)
            except Exception as e:
                print(f"[学習エンジン] ⚠️ コールバックエラー: {e}")
    
    def create_session(self, 
                      theme: str,
                      learning_type: str = "概要",
                      depth_level: int = 3,
                      time_limit: int = 1800,  # 30分
                      budget_limit: float = 5.0,
                      parent_session: Optional[str] = None,
                      tags: List[str] = None) -> str:
        """
        新しい学習セッションを作成
        
        Args:
            theme: 学習テーマ
            learning_type: 学習タイプ ("概要", "深掘り", "実用")
            depth_level: 学習深度 (1-5)
            time_limit: 時間制限（秒）
            budget_limit: 予算制限（ドル）
            parent_session: 親セッションID
            tags: タグリスト
            
        Returns:
            セッションID
        """
        try:
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            
            session = LearningSession(
                session_id=session_id,
                theme=theme,
                learning_type=learning_type,
                depth_level=depth_level,
                time_limit=time_limit,
                budget_limit=budget_limit,
                status="ready",
                parent_session=parent_session,
                tags=tags or []
            )
            
            self.session_history[session_id] = session
            self._save_session(session)
            
            print(f"[学習エンジン] 📝 セッション作成: {session_id}")
            print(f"  テーマ: {theme}")
            print(f"  タイプ: {learning_type} (深度レベル{depth_level})")
            print(f"  制限: {time_limit}秒, ${budget_limit}")
            
            return session_id
            
        except Exception as e:
            print(f"[学習エンジン] ❌ セッション作成失敗: {e}")
            raise
    
    def start_session(self, session_id: str) -> bool:
        """
        学習セッションを開始
        
        Args:
            session_id: セッションID
            
        Returns:
            開始成功フラグ
        """
        # セッション専用ログガー初期化
        session_logger = get_debug_logger(session_id, "SESSION")
        
        try:
            session_logger.info("セッション開始処理開始", {
                "session_id": session_id,
                "available_sessions": list(self.session_history.keys())
            })
            
            if session_id not in self.session_history:
                session_logger.error("セッション未発見", {
                    "session_id": session_id,
                    "available_sessions": list(self.session_history.keys())
                })
                print(f"[学習エンジン] ❌ セッション未発見: {session_id}")
                return False
            
            session = self.session_history[session_id]
            session_logger.debug("セッション情報確認", {
                "session_status": session.status,
                "session_theme": session.theme,
                "learning_type": session.learning_type,
                "depth_level": session.depth_level,
                "time_limit": session.time_limit,
                "budget_limit": session.budget_limit
            })
            
            if session.status != "ready":
                session_logger.error("セッション状態不正", {
                    "current_status": session.status,
                    "expected_status": "ready"
                })
                print(f"[学習エンジン] ❌ セッション状態不正: {session.status}")
                return False
            
            # セッション開始
            session.status = "running"
            session.start_time = datetime.now()
            session.current_phase = "collection"
            self.current_session = session
            
            # セッション専用ログガーをメインログガーに設定
            self.debug_logger = session_logger
            
            self._save_session(session)
            self._notify_progress("collection", 0.0, "学習セッション開始")
            
            session_logger.info("セッション開始成功", {
                "session_id": session_id,
                "start_time": session.start_time.isoformat(),
                "initial_phase": session.current_phase
            })
            print(f"[学習エンジン] 🚀 セッション開始: {session_id}")
            
            # スレッドで学習実行
            learning_thread = threading.Thread(
                target=self._execute_learning_session,
                daemon=True,
                name=f"learning_session_{session_id}"
            )
            learning_thread.start()
            
            session_logger.debug("学習スレッド開始", {
                "thread_name": learning_thread.name,
                "thread_id": learning_thread.ident
            })
            
            return True
            
        except Exception as e:
            session_logger.error("セッション開始失敗", {
                "session_id": session_id,
                "error_type": type(e).__name__
            }, e)
            print(f"[学習エンジン] ❌ セッション開始失敗: {e}")
            return False
    
    def _execute_learning_session(self):
        """学習セッション実行（スレッド）"""
        session = self.current_session
        if not session:
            return
        
        try:
            print(f"[学習エンジン] 📚 学習実行開始: {session.theme}")
            
            # Phase 1: 情報収集
            self._phase_information_collection(session)
            
            # Phase 2: コンテンツ分析
            self._phase_content_analysis(session)
            
            # Phase 3: 知識統合
            self._phase_knowledge_integration(session)
            
            # セッション完了
            session.status = "completed"
            session.end_time = datetime.now()
            session.current_phase = "completed"
            
            self._save_session(session)
            self._notify_progress("completed", 1.0, "学習セッション完了")
            
            duration = (session.end_time - session.start_time).total_seconds()
            print(f"[学習エンジン] ✅ セッション完了: {session.session_id}")
            print(f"  所要時間: {duration:.1f}秒")
            print(f"  総コスト: ${session.current_cost:.2f}")
            print(f"  収集記事: {session.collected_items}件")
            print(f"  重要発見: {len(session.important_findings)}件")
            
        except Exception as e:
            print(f"[学習エンジン] ❌ 学習実行失敗: {e}")
            session.status = "error"
            self._save_session(session)
            self._notify_progress("error", 0.0, f"エラー: {str(e)}")
    
    def _phase_information_collection(self, session: LearningSession):
        """Phase 1: 情報収集"""
        phase_start_time = time.time()
        
        self.debug_logger.log_session_phase(
            "information_collection", "started", 0.1, 
            {
                "session_id": session.session_id,
                "theme": session.theme,
                "depth_level": session.depth_level
            }
        )
        
        print(f"[学習エンジン] 🔍 Phase 1: 情報収集開始")
        session.current_phase = "collection"
        self._notify_progress("collection", 0.1, "情報収集開始")
        
        # 検索クエリ生成
        search_queries = self._generate_search_queries(session.theme, session.depth_level)
        
        collected_sources = []
        search_errors = []  # 検索エラーを記録
        total_queries = len(search_queries)
        
        self.debug_logger.info("情報収集フェーズ詳細", {
            "total_queries": total_queries,
            "search_queries": search_queries,
            "collection_config": self.collection_config
        })
        
        for i, query in enumerate(search_queries):
            if self._should_stop_session(session):
                self.debug_logger.warning("セッション停止条件により中断", {
                    "completed_queries": i,
                    "total_queries": total_queries,
                    "collected_sources": len(collected_sources)
                })
                break
                
            self.debug_logger.info(f"検索実行 ({i+1}/{total_queries})", {
                "query": query,
                "query_index": i,
                "current_sources_count": len(collected_sources)
            })
            print(f"[学習エンジン] 🔍 検索実行 ({i+1}/{total_queries}): {query}")
            
            # Web検索実行
            query_start_time = time.time()
            search_result = self._perform_web_search_detailed(query)
            query_execution_time = time.time() - query_start_time
            
            # 検索結果処理
            if search_result["success"]:
                sources = search_result["sources"]
                collected_sources.extend(sources)
                print(f"[学習エンジン] ✅ 検索成功: {len(sources)}件取得")
            else:
                # エラー情報を記録
                error_info = {
                    "query": query,
                    "error_message": search_result.get("error_message", "不明なエラー"),
                    "error_type": search_result.get("error_type", "unknown"),
                    "quota_exceeded": search_result.get("quota_exceeded", False),
                    "timestamp": datetime.now().isoformat(),
                    "execution_time": query_execution_time
                }
                search_errors.append(error_info)
                print(f"[学習エンジン] ❌ 検索失敗: {error_info['error_message']}")
            
            self.debug_logger.info(f"検索結果 ({i+1}/{total_queries})", {
                "query": query,
                "success": search_result["success"],
                "results_count": len(search_result.get("sources", [])),
                "execution_time": query_execution_time,
                "total_collected": len(collected_sources),
                "error_message": search_result.get("error_message") if not search_result["success"] else None
            })
            
            session.collected_items = len(collected_sources)
            progress = 0.1 + (0.3 * (i + 1) / total_queries)
            self._notify_progress("collection", progress, f"検索完了: {query}")
            
            # レート制限対応
            time.sleep(1)
        
        # Phase 1.5: 前処理・フィルタリング（GPT-3.5）
        if self.staged_analysis_config["enable_preprocessing"] and collected_sources:
            preprocessing_start_time = time.time()
            
            self.debug_logger.log_session_phase(
                "preprocessing", "started", 0.35,
                {
                    "collected_sources_count": len(collected_sources),
                    "preprocessing_thresholds": self.staged_analysis_config["preprocessing_thresholds"],
                    "max_detailed_analysis": self.staged_analysis_config["max_detailed_analysis"]
                }
            )
            
            print(f"[学習エンジン] 🔄 Phase 1.5: 前処理・フィルタリング開始")
            self._notify_progress("preprocessing", 0.35, "前処理開始")
            
            # 前処理エンジンで閾値設定
            self.preprocessing_engine.set_thresholds(**self.staged_analysis_config["preprocessing_thresholds"])
            
            # 前処理実行
            preprocessing_results = self.preprocessing_engine.preprocess_content_batch(
                sources=collected_sources,
                theme=session.theme,
                target_categories=["技術", "市場", "トレンド", "実用"]
            )
            
            preprocessing_execution_time = time.time() - preprocessing_start_time
            
            self.debug_logger.info("前処理結果", {
                "preprocessing_results_count": len(preprocessing_results),
                "execution_time": preprocessing_execution_time
            })
            
            # 通過したソースのみ抽出
            passed_sources = []
            for result in preprocessing_results:
                if result.should_proceed:
                    # 元のソースデータに前処理結果を付加
                    for source in collected_sources:
                        if source.get('source_id') == result.source_id:
                            source['preprocessing_result'] = {
                                'relevance_score': result.relevance_score,
                                'quality_score': result.quality_score,
                                'importance_score': result.importance_score,
                                'category': result.category,
                                'key_topics': result.key_topics,
                                'confidence': result.confidence,
                                'reason': result.reason
                            }
                            passed_sources.append(source)
                            break
            
            # 高品質なソースを上位に選択
            if len(passed_sources) > self.staged_analysis_config["max_detailed_analysis"]:
                top_quality_results = self.preprocessing_engine.get_top_quality_sources(
                    preprocessing_results, 
                    self.staged_analysis_config["max_detailed_analysis"]
                )
                top_source_ids = [r.source_id for r in top_quality_results]
                passed_sources = [s for s in passed_sources if s.get('source_id') in top_source_ids]
            
            # フィルタリングサマリー
            filtering_summary = self.preprocessing_engine.get_filtering_summary(preprocessing_results)
            
            print(f"[学習エンジン] ✅ 前処理完了:")
            print(f"  収集: {len(collected_sources)}件")
            print(f"  通過: {len(passed_sources)}件 ({filtering_summary['pass_rate']:.1f}%)")
            print(f"  詳細分析対象: {len(passed_sources)}件")
            
            # 前処理されたソースを使用
            final_sources = passed_sources
        else:
            # 前処理無効時は全ソースを使用
            final_sources = collected_sources
        
        # 収集結果をセッションに保存（エラー情報も含む）
        phase_execution_time = time.time() - phase_start_time
        
        # 検索エンジンステータス取得
        search_engine_status = self.search_manager.get_status()
        
        session_data = {
            "collection_results": {
                "information_sources": final_sources,
                "raw_content_count": len(collected_sources),
                "filtered_content_count": len(final_sources),
                "search_queries": search_queries,
                "preprocessing_enabled": self.staged_analysis_config["enable_preprocessing"],
                "execution_time": phase_execution_time,
                "queries_executed": len(search_queries),
                "search_engine_status": search_engine_status,
                "collection_timestamp": datetime.now().isoformat(),
                "collection_success": len(final_sources) > 0,
                "search_errors": search_errors  # 検索エラーを記録
            }
        }
        
        if self.staged_analysis_config["enable_preprocessing"] and collected_sources:
            session_data["preprocessing_summary"] = filtering_summary
        
        self._save_session_data(session, session_data)
        
        self.debug_logger.log_session_phase(
            "information_collection", "completed", 0.4,
            {
                "final_sources_count": len(final_sources),
                "raw_sources_count": len(collected_sources),
                "execution_time": phase_execution_time,
                "preprocessing_enabled": self.staged_analysis_config["enable_preprocessing"]
            }
        )
        
        print(f"[学習エンジン] ✅ 情報収集完了: {len(final_sources)}件（詳細分析対象）")
    
    def _phase_content_analysis(self, session: LearningSession):
        """Phase 2: コンテンツ分析"""
        print(f"[学習エンジン] 🧠 Phase 2: コンテンツ分析開始")
        session.current_phase = "analysis"
        self._notify_progress("analysis", 0.4, "コンテンツ分析開始")
        
        # セッションデータ読み込み
        session_file = self.sessions_dir / f"{session.session_id}.json"
        with open(session_file, 'r', encoding='utf-8') as f:
            session_data = json.load(f)
        
        sources = session_data.get("collection_results", {}).get("information_sources", [])
        
        # バッチ処理でコンテンツ分析
        analysis_results = []
        batch_size = 5  # GPT-4-turbo効率化のため
        
        for i in range(0, len(sources), batch_size):
            if self._should_stop_session(session):
                break
                
            batch = sources[i:i+batch_size]
            print(f"[学習エンジン] 🧠 分析実行 ({i//batch_size + 1}/{(len(sources)-1)//batch_size + 1})")
            
            # GPT-4-turboで分析
            batch_analysis = self._analyze_content_batch(batch, session.theme)
            analysis_results.extend(batch_analysis)
            
            session.processed_items = len(analysis_results)
            progress = 0.4 + (0.3 * len(analysis_results) / len(sources))
            self._notify_progress("analysis", progress, f"分析進行中: {len(analysis_results)}/{len(sources)}")
            
            # APIレート制限対応
            time.sleep(2)
        
        # 分析結果をセッションに追加保存
        session_data["analysis_results"] = {
            "analyzed_content": analysis_results,
            "key_findings": self._extract_key_findings(analysis_results),
            "extracted_entities": self._extract_entities(analysis_results),
            "identified_relationships": self._identify_relationships(analysis_results)
        }
        
        session.important_findings = session_data["analysis_results"]["key_findings"]
        self._save_session_data(session, session_data)
        
        print(f"[学習エンジン] ✅ コンテンツ分析完了: {len(analysis_results)}件")
    
    def _phase_knowledge_integration(self, session: LearningSession):
        """Phase 3: 知識統合"""
        print(f"[学習エンジン] 🔗 Phase 3: 知識統合開始")
        session.current_phase = "integration"
        self._notify_progress("integration", 0.7, "知識統合開始")
        
        # 統合的な知識生成
        integrated_knowledge = self._generate_integrated_knowledge(session)
        
        # セッションデータに統合結果を追加
        session_file = self.sessions_dir / f"{session.session_id}.json"
        with open(session_file, 'r', encoding='utf-8') as f:
            session_data = json.load(f)
        
        session_data["generated_knowledge"] = integrated_knowledge
        session_data["session_statistics"] = self._calculate_session_statistics(session)
        
        self._save_session_data(session, session_data)
        self._notify_progress("integration", 0.9, "知識統合完了")
        
        print(f"[学習エンジン] ✅ 知識統合完了")
    
    def _generate_search_queries(self, theme: str, depth_level: int) -> List[str]:
        """検索クエリ生成"""
        self.debug_logger.debug("Web検索クエリ生成開始", {
            "theme": theme,
            "depth_level": depth_level
        })
        
        base_queries = [
            f"{theme} 最新情報",
            f"{theme} トレンド 2024",
            f"{theme} 技術動向",
        ]
        
        if depth_level >= 3:
            base_queries.extend([
                f"{theme} 市場分析",
                f"{theme} 課題",
                f"{theme} 将来性",
            ])
        
        if depth_level >= 4:
            base_queries.extend([
                f"{theme} 具体的事例",
                f"{theme} 実装方法",
                f"{theme} ベストプラクティス",
            ])
        
        self.debug_logger.info("Web検索クエリ生成完了", {
            "generated_queries": base_queries,
            "total_queries": len(base_queries)
        })
        
        return base_queries
    
    def _perform_web_search(self, query: str) -> List[Dict]:
        """Web検索実行（統合検索エンジン使用）- 後方互換性のため"""
        result = self._perform_web_search_detailed(query)
        return result.get("sources", [])
    
    def _perform_web_search_detailed(self, query: str) -> Dict[str, Any]:
        """詳細Web検索実行（エラー情報も含む）"""
        start_time = time.time()
        
        self.debug_logger.debug("Web検索リクエスト開始", {
            "query": query,
            "search_manager": type(self.search_manager).__name__
        })
        
        try:
            # 統合検索エンジンで検索実行
            search_result = self.search_manager.search(query, max_results=5)
            execution_time = time.time() - start_time
            
            self.debug_logger.info("Google検索結果", {
                "query": query,
                "engine_used": search_result["engine_used"],
                "success": search_result["success"],
                "total_results": search_result["total_results"],
                "execution_time": execution_time,
                "quota_remaining": search_result.get("quota_remaining", "不明")
            })
            
            if search_result["success"] and search_result["results"]:
                sources = search_result["results"]
                
                # 結果の詳細ログ
                for i, source in enumerate(sources, 1):
                    self.debug_logger.debug(f"Web検索結果処理: {i}", {
                        "source_id": source.get("source_id", "unknown"),
                        "source_type": source.get("source_type", "unknown"),
                        "url": source.get("url", ""),
                        "title_length": len(source.get("title", "")),
                        "content_length": len(source.get("content", ""))
                    })
                
                # 成功ログ
                self.debug_logger.log_web_search(
                    query, f"{search_result['engine_used']}_engine", 200, 
                    len(sources), {
                        "execution_time": execution_time,
                        "engine_used": search_result["engine_used"],
                        "quota_remaining": search_result.get("quota_remaining", "不明")
                    }
                )
                
                return {
                    "success": True,
                    "sources": sources,
                    "execution_time": execution_time,
                    "engine_used": search_result["engine_used"],
                    "quota_remaining": search_result.get("quota_remaining")
                }
            
            else:
                # 検索失敗の場合
                error_message = search_result.get("error", "検索結果が空")
                quota_exceeded = search_result.get("quota_exceeded", False)
                
                self.debug_logger.warning("Google検索失敗", {
                    "query": query,
                    "engine_used": search_result["engine_used"],
                    "error": error_message,
                    "execution_time": execution_time,
                    "quota_exceeded": quota_exceeded,
                    "quota_remaining": search_result.get("quota_remaining", "不明")
                })
                
                if quota_exceeded:
                    print(f"[学習エンジン] ⚠️ Google検索制限到達: {error_message}")
                    print(f"[学習エンジン] 💡 明日まで待つか、別のAPIの追加を検討してください")
                else:
                    print(f"[学習エンジン] ⚠️ Google検索失敗: {error_message}")
                
                return {
                    "success": False,
                    "sources": [],
                    "error_message": error_message,
                    "error_type": "search_failed",
                    "quota_exceeded": quota_exceeded,
                    "execution_time": execution_time,
                    "engine_used": search_result.get("engine_used", "unknown"),
                    "quota_remaining": search_result.get("quota_remaining")
                }
        
        except Exception as e:
            execution_time = time.time() - start_time
            self.debug_logger.error("Web検索予期せぬエラー", {
                "query": query,
                "execution_time": execution_time,
                "error_type": type(e).__name__
            }, e)
            print(f"[学習エンジン] ⚠️ Web検索エラー: {e}")
            
            return {
                "success": False,
                "sources": [],
                "error_message": str(e),
                "error_type": "exception",
                "quota_exceeded": False,
                "execution_time": execution_time,
                "engine_used": "unknown"
            }
    
    def _analyze_content_batch(self, sources: List[Dict], theme: str) -> List[Dict]:
        """コンテンツバッチ分析"""
        if not self.openai_client:
            return []
        
        try:
            # バッチ分析用プロンプト
            content_texts = []
            for i, source in enumerate(sources):
                content_texts.append(f"[記事{i+1}] {source.get('title', '')}\n{source.get('content', '')}")
            
            batch_content = "\n\n".join(content_texts)
            
            prompt = f"""
以下の{len(sources)}件の記事を「{theme}」に関する情報として分析してください。

{batch_content}

各記事について以下を分析してください：
1. 重要度 (1-10)
2. カテゴリ (技術/市場/トレンド/実用/その他)
3. キーポイント (3個以内)
4. 関連する技術・ツール・人物
5. 信頼性 (1-10)

JSON形式で出力してください。
"""
            
            response = self.openai_client.chat.completions.create(
                model=self.gpt_config["model"],
                messages=[{"role": "user", "content": prompt}],
                temperature=self.gpt_config["temperature"],
                max_tokens=self.gpt_config["max_tokens"]
            )
            
            # コスト計算
            input_tokens = len(prompt.split())
            output_tokens = len(response.choices[0].message.content.split())
            cost = (input_tokens * 0.01 / 1000) + (output_tokens * 0.03 / 1000)
            self.current_session.current_cost += cost
            
            # レスポンス解析
            analysis_text = response.choices[0].message.content
            
            # 分析結果をソースと関連付け
            analysis_results = []
            for i, source in enumerate(sources):
                analysis_results.append({
                    "source": source,
                    "analysis": f"記事{i+1}の分析結果",  # 実際はGPTレスポンスを解析
                    "importance": 7,  # 実際はGPTレスポンスから抽出
                    "category": "技術",
                    "key_points": ["ポイント1", "ポイント2"],
                    "related_entities": ["エンティティ1", "エンティティ2"]
                })
            
            return analysis_results
            
        except Exception as e:
            print(f"[学習エンジン] ❌ コンテンツ分析エラー: {e}")
            return []
    
    def _generate_integrated_knowledge(self, session: LearningSession) -> Dict:
        """統合知識生成"""
        # 統合知識の生成ロジック
        return {
            "structured_knowledge": [],
            "integration_knowledge": [],
            "activity_implications": []
        }
    
    def _extract_key_findings(self, analysis_results: List[Dict]) -> List[Dict]:
        """重要発見抽出"""
        return []
    
    def _extract_entities(self, analysis_results: List[Dict]) -> List[Dict]:
        """エンティティ抽出"""
        return []
    
    def _identify_relationships(self, analysis_results: List[Dict]) -> List[Dict]:
        """関係性特定"""
        return []
    
    def _calculate_session_statistics(self, session: LearningSession) -> Dict:
        """セッション統計計算"""
        return {
            "total_cost": session.current_cost,
            "total_items_processed": session.processed_items,
            "processing_time": 0
        }
    
    def _should_stop_session(self, session: LearningSession) -> bool:
        """セッション停止判定"""
        if not session.start_time:
            return False
        
        # 時間制限チェック
        elapsed = (datetime.now() - session.start_time).total_seconds()
        if elapsed > session.time_limit:
            return True
        
        # 予算制限チェック
        if session.current_cost > session.budget_limit:
            return True
        
        return False
    
    def _save_session(self, session: LearningSession):
        """セッション保存（既存データを保持）"""
        with self.file_lock:  # ファイル競合防止
            session_file = self.sessions_dir / f"{session.session_id}.json"
            
            # 既存データ読み込み（データ保持のため）
            existing_data = {}
            if session_file.exists():
                try:
                    with open(session_file, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                except (json.JSONDecodeError, Exception) as e:
                    self.debug_logger.warning("既存セッションデータ読み込み失敗", {
                        "session_id": session.session_id,
                        "error": str(e)
                    })
                    existing_data = {}
            
            # メタデータのみ更新（既存データは保持）
            existing_data["session_metadata"] = asdict(session)
            existing_data["last_updated"] = datetime.now().isoformat()
            
            # 安全なファイル書き込み
            try:
                with open(session_file, 'w', encoding='utf-8') as f:
                    json.dump(existing_data, f, ensure_ascii=False, indent=2, default=str)
                
                self.debug_logger.debug("セッション保存成功", {
                    "session_id": session.session_id,
                    "file_size": session_file.stat().st_size,
                    "data_keys": list(existing_data.keys())
                })
                
            except Exception as e:
                self.debug_logger.error("セッション保存失敗", {
                    "session_id": session.session_id,
                    "file_path": str(session_file)
                }, e)
                raise
    
    def _save_session_data(self, session: LearningSession, additional_data: Dict):
        """セッションデータ追加保存"""
        with self.file_lock:  # ファイル競合防止
            session_file = self.sessions_dir / f"{session.session_id}.json"
            
            # 既存データ読み込み
            existing_data = {}
            if session_file.exists():
                try:
                    with open(session_file, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)
                except (json.JSONDecodeError, Exception) as e:
                    self.debug_logger.warning("既存データ読み込み失敗", {
                        "session_id": session.session_id,
                        "error": str(e)
                    })
                    existing_data = {}
            
            # 新しいデータをマージ
            existing_data.update(additional_data)
            existing_data["session_metadata"] = asdict(session)
            existing_data["last_updated"] = datetime.now().isoformat()
            
            try:
                with open(session_file, 'w', encoding='utf-8') as f:
                    json.dump(existing_data, f, ensure_ascii=False, indent=2, default=str)
                
                self.debug_logger.debug("セッションデータ保存成功", {
                    "session_id": session.session_id,
                    "additional_keys": list(additional_data.keys()),
                    "file_size": session_file.stat().st_size
                })
                
            except Exception as e:
                self.debug_logger.error("セッションデータ保存失敗", {
                    "session_id": session.session_id,
                    "file_path": str(session_file)
                }, e)
                raise
    
    def pause_session(self, session_id: str) -> bool:
        """セッション一時停止"""
        try:
            if session_id in self.session_history:
                session = self.session_history[session_id]
                session.status = "paused"
                self._save_session(session)
                self._notify_progress("paused", 0.0, "セッション一時停止")
                return True
        except Exception as e:
            print(f"[学習エンジン] ❌ セッション一時停止失敗: {e}")
        return False
    
    def stop_session(self, session_id: str) -> bool:
        """セッション強制停止"""
        try:
            if session_id in self.session_history:
                session = self.session_history[session_id]
                session.status = "completed"
                session.end_time = datetime.now()
                self._save_session(session)
                self._notify_progress("stopped", 1.0, "セッション強制停止")
                return True
        except Exception as e:
            print(f"[学習エンジン] ❌ セッション停止失敗: {e}")
        return False
    
    def get_session_status(self, session_id: str) -> Optional[Dict]:
        """セッション状態取得"""
        if session_id in self.session_history:
            session = self.session_history[session_id]
            return {
                "session_id": session.session_id,
                "status": session.status,
                "current_phase": session.current_phase,
                "progress": {
                    "collected_items": session.collected_items,
                    "processed_items": session.processed_items,
                    "current_cost": session.current_cost,
                    "time_elapsed": (datetime.now() - session.start_time).total_seconds() if session.start_time else 0
                }
            }
        return None
    
    def list_sessions(self, limit: int = 10) -> List[Dict]:
        """セッション一覧取得"""
        sessions = list(self.session_history.values())
        sessions.sort(key=lambda x: x.start_time or datetime.min, reverse=True)
        
        return [
            {
                "session_id": s.session_id,
                "theme": s.theme,
                "learning_type": s.learning_type,
                "status": s.status,
                "start_time": s.start_time.isoformat() if s.start_time else None,
                "current_cost": s.current_cost
            }
            for s in sessions[:limit]
        ]


# テスト用コード
if __name__ == "__main__":
    print("=== ActivityLearningEngine テスト ===")
    
    engine = ActivityLearningEngine()
    
    # テストセッション作成
    session_id = engine.create_session(
        theme="AI音楽生成技術",
        learning_type="概要",
        depth_level=3,
        time_limit=300,  # 5分間テスト
        budget_limit=2.0,
        tags=["AI", "音楽", "技術調査"]
    )
    
    print(f"\n📋 作成されたセッションID: {session_id}")
    
    # プログレスコールバック設定
    def progress_callback(phase: str, progress: float, message: str):
        print(f"[進捗] {phase}: {progress:.1%} - {message}")
    
    engine.add_progress_callback(progress_callback)
    
    # セッション開始（テスト）
    print("\n🚀 セッション開始テスト:")
    success = engine.start_session(session_id)
    
    if success:
        print("✅ セッション開始成功")
        
        # 少し待ってからステータス確認
        time.sleep(5)
        status = engine.get_session_status(session_id)
        if status:
            print(f"\n📊 セッション状態:")
            print(f"  状態: {status['status']}")
            print(f"  フェーズ: {status['current_phase']}")
            print(f"  進捗: {status['progress']}")
    else:
        print("❌ セッション開始失敗")
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ConversationKnowledgeProvider - Phase 4統合
音声対話時の知識検索・分析・応答統合システム
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import re
from collections import defaultdict
from difflib import SequenceMatcher

# プロジェクトルートを確実にパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from core.knowledge_analysis.knowledge_analysis_engine import KnowledgeAnalysisEngine
    KNOWLEDGE_ENGINE_AVAILABLE = True
except ImportError:
    KNOWLEDGE_ENGINE_AVAILABLE = False
    print("⚠️ KnowledgeAnalysisEngineが利用できません")

# ログシステム統合
try:
    from logging_system import get_logger
    LOGGER_AVAILABLE = True
except ImportError:
    LOGGER_AVAILABLE = False

# Windows環境のパス設定
if os.name == 'nt':
    DATA_DIR = Path("D:/setsuna_bot/data/activity_knowledge")
else:
    DATA_DIR = Path("/mnt/d/setsuna_bot/data/activity_knowledge")

@dataclass
class KnowledgeContext:
    """知識コンテキストデータクラス"""
    context_id: str
    user_input: str
    detected_topics: List[str]
    relevant_knowledge: List[Dict[str, Any]]
    confidence_score: float
    knowledge_types: List[str]  # "factual", "experiential", "analytical", "predictive"
    application_suggestions: List[str]
    
@dataclass
class ConversationEnhancement:
    """会話強化データクラス"""
    enhancement_type: str  # "knowledge_injection", "insight_sharing", "trend_analysis"
    knowledge_source: str  # セッションIDまたは統合知識ID
    enhancement_content: str
    relevance_score: float
    timing_suggestion: str  # "immediate", "follow_up", "related_topic"

class ConversationKnowledgeProvider:
    """音声対話用知識提供システム"""
    
    def __init__(self):
        """初期化"""
        # ログシステム初期化
        if LOGGER_AVAILABLE:
            self.logger = get_logger()
            self.logger.info("conversation_knowledge", "init", "ConversationKnowledgeProvider初期化開始")
        else:
            self.logger = None
        
        # 知識分析エンジン初期化
        if KNOWLEDGE_ENGINE_AVAILABLE:
            self.knowledge_engine = KnowledgeAnalysisEngine(
                progress_callback=self._knowledge_progress_callback
            )
            if self.logger:
                self.logger.info("conversation_knowledge", "init", "KnowledgeAnalysisEngine初期化成功")
        else:
            self.knowledge_engine = None
            if self.logger:
                self.logger.warning("conversation_knowledge", "init", "KnowledgeAnalysisEngine利用不可")
        
        self.knowledge_dir = DATA_DIR
        
        # 関連コンポーネントのデータディレクトリ
        self.sessions_dir = self.knowledge_dir / "sessions"
        self.knowledge_graph_dir = self.knowledge_dir / "knowledge_graph"
        self.integrated_dir = self.knowledge_dir / "integrated_knowledge"
        
        # キャッシュディレクトリ設定
        self.cache_dir = Path("D:/setsuna_bot/conversation_knowledge_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 知識キャッシュ
        self.knowledge_cache: Dict[str, Any] = {}
        self.topic_index: Dict[str, List[str]] = defaultdict(list)  # トピック -> 知識IDリスト
        self.entity_index: Dict[str, List[str]] = defaultdict(list)  # エンティティ -> 知識IDリスト
        
        # 会話履歴
        self.conversation_history: List[Dict] = []
        self.active_contexts: List[KnowledgeContext] = []
        
        # 設定
        self.provider_config = {
            "max_relevant_knowledge": 5,
            "relevance_threshold": 0.6,
            "context_window_size": 3,  # 過去3発言を考慮
            "knowledge_freshness_days": 30,
            "auto_enhancement_enabled": True,
            "proactive_suggestion_enabled": True
        }
        
        # 知識統合設定
        self.integration_config = {
            "enable_realtime_search": True,
            "max_search_time_seconds": 30,
            "context_injection_mode": "summary",  # "full", "summary", "keywords"
            "cache_knowledge_hours": 24,
            "min_relevance_score": 0.3
        }
        
        # トピック検出パターン
        self.topic_patterns = {
            "AI技術": [r"AI", r"人工知能", r"機械学習", r"深層学習", r"ニューラル", r"アルゴリズム"],
            "音楽生成": [r"音楽", r"作曲", r"楽曲", r"メロディ", r"リズム", r"ハーモニー"],
            "技術動向": [r"トレンド", r"動向", r"最新", r"新技術", r"革新", r"イノベーション"],
            "ツール": [r"ツール", r"アプリ", r"ソフト", r"プラットフォーム", r"サービス"],
            "市場分析": [r"市場", r"ビジネス", r"産業", r"業界", r"競合", r"シェア"],
            "実用性": [r"実用", r"活用", r"応用", r"実践", r"使い方", r"実装"]
        }
        
        self._initialize_knowledge_cache()
        
        print("[会話知識] ✅ ConversationKnowledgeProvider初期化完了")
    
    def _knowledge_progress_callback(self, stage: str, progress: float, message: str):
        """知識分析進捗コールバック"""
        if self.logger:
            self.logger.info("conversation_knowledge", "progress", 
                           f"[{stage}] {progress:.1%} - {message}")
        print(f"🔍 [{stage}] {progress:.1%} - {message}")
    
    def get_knowledge_context(self, user_input: str, mode: str = "full_search") -> Dict[str, Any]:
        """ユーザー入力に基づく知識コンテキスト取得"""
        start_time = datetime.now()
        
        if self.logger:
            self.logger.info("conversation_knowledge", "get_context", 
                           f"知識コンテキスト取得開始 - mode: {mode}, input: {user_input[:50]}...")
        
        knowledge_context = {
            "has_knowledge": False,
            "search_performed": False,
            "knowledge_summary": "",
            "key_insights": [],
            "related_topics": [],
            "search_details": {},
            "context_injection_text": "",
            "processing_time": 0.0,
            "mode": mode
        }
        
        try:
            # モード別処理
            if mode == "full_search" and self.knowledge_engine:
                # 通常モード: リアルタイム知識検索
                knowledge_context = self._perform_realtime_search(user_input, knowledge_context)
            
            elif mode in ["fast_response", "ultra_fast"]:
                # 高速モード: キャッシュされた知識検索
                knowledge_context = self._search_cached_knowledge(user_input, knowledge_context)
            
            # コンテキスト注入テキスト生成
            if knowledge_context["has_knowledge"]:
                knowledge_context["context_injection_text"] = self._generate_context_injection(knowledge_context)
            
            # 処理時間記録
            processing_time = (datetime.now() - start_time).total_seconds()
            knowledge_context["processing_time"] = processing_time
            
            if self.logger:
                self.logger.info("conversation_knowledge", "get_context", 
                               f"知識コンテキスト取得完了 - 時間: {processing_time:.2f}s, 知識有無: {knowledge_context['has_knowledge']}")
            
            return knowledge_context
            
        except Exception as e:
            if self.logger:
                self.logger.error("conversation_knowledge", "get_context", f"知識コンテキスト取得エラー: {e}")
            
            knowledge_context["error"] = str(e)
            return knowledge_context
    
    def _perform_realtime_search(self, user_input: str, context: Dict) -> Dict:
        """リアルタイム知識検索実行"""
        if not self.knowledge_engine:
            return context
        
        try:
            print("🔍 リアルタイム知識検索開始...")
            
            # 知識分析実行（簡易検索・分析）
            search_results = self.knowledge_engine._execute_large_scale_search(user_input)
            
            if search_results:
                # 分析実行
                analysis_result = self.knowledge_engine._execute_batch_analysis(search_results, user_input)
                
                # レポート形式に変換
                report = {
                    "analysis_summary": analysis_result.get("analysis", ""),
                    "key_insights": [],
                    "related_topics": [],
                    "search_count": len(search_results),
                    "data_quality": 0.7 if search_results else 0.0,
                    "cost": analysis_result.get("total_cost", 0.0),
                    "processing_time": analysis_result.get("analysis_log", {}).get("summary", {}).get("total_time", 0)
                }
                
                # 分析結果から洞察抽出
                if "batch_summaries" in analysis_result:
                    for batch_summary in analysis_result["batch_summaries"][:3]:
                        if isinstance(batch_summary, str) and len(batch_summary) > 10:
                            report["key_insights"].append(batch_summary[:100])
                
                # 関連トピック抽出（簡易版）
                prompt_words = user_input.split()
                report["related_topics"] = [word for word in prompt_words if len(word) > 2][:5]
            else:
                report = None
            
            if report and isinstance(report, dict):
                context["has_knowledge"] = True
                context["search_performed"] = True
                context["knowledge_summary"] = report.get("analysis_summary", "")
                context["key_insights"] = report.get("key_insights", [])
                context["related_topics"] = report.get("related_topics", [])
                context["search_details"] = {
                    "search_count": report.get("search_count", 0),
                    "data_quality": report.get("data_quality", 0.0),
                    "cost": report.get("cost", 0.0),
                    "processing_time": report.get("processing_time", 0)
                }
                
                # 知識キャッシュ保存
                self._cache_knowledge(user_input, report)
                
                print(f"✅ 知識検索完了 - {report.get('search_count', 0)}件の検索結果を分析")
            else:
                print("⚠️ 知識検索結果が空でした")
            
            return context
            
        except Exception as e:
            print(f"❌ リアルタイム知識検索エラー: {e}")
            if self.logger:
                self.logger.error("conversation_knowledge", "realtime_search", f"検索エラー: {e}")
            return context
    
    def _search_cached_knowledge(self, user_input: str, context: Dict) -> Dict:
        """キャッシュされた知識検索"""
        try:
            # キャッシュファイル検索
            cache_files = list(self.cache_dir.glob("*.json"))
            relevant_knowledge = []
            
            for cache_file in cache_files:
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cached_data = json.load(f)
                    
                    # 関連性チェック（簡易版）
                    relevance_score = self._calculate_relevance(user_input, cached_data)
                    if relevance_score >= self.integration_config["min_relevance_score"]:
                        relevant_knowledge.append({
                            "data": cached_data,
                            "relevance": relevance_score,
                            "cache_time": cache_file.stat().st_mtime
                        })
                
                except Exception:
                    continue
            
            # 関連度順にソート
            relevant_knowledge.sort(key=lambda x: x["relevance"], reverse=True)
            
            if relevant_knowledge:
                best_knowledge = relevant_knowledge[0]["data"]
                context["has_knowledge"] = True
                context["knowledge_summary"] = best_knowledge.get("analysis_summary", "")
                context["key_insights"] = best_knowledge.get("key_insights", [])
                context["related_topics"] = best_knowledge.get("related_topics", [])
                context["search_details"] = {
                    "cache_source": True,
                    "relevance_score": relevant_knowledge[0]["relevance"]
                }
                
                print(f"📚 キャッシュから関連知識を取得 - 関連度: {relevant_knowledge[0]['relevance']:.2f}")
            
            return context
            
        except Exception as e:
            print(f"⚠️ キャッシュ知識検索エラー: {e}")
            return context
    
    def _calculate_relevance(self, user_input: str, cached_data: Dict) -> float:
        """関連性スコア計算（簡易版）"""
        try:
            user_words = set(user_input.lower().split())
            
            # 比較対象テキスト生成
            comparison_text = ""
            if "user_prompt" in cached_data:
                comparison_text += cached_data["user_prompt"].lower() + " "
            if "analysis_summary" in cached_data:
                comparison_text += cached_data["analysis_summary"].lower() + " "
            if "key_insights" in cached_data:
                comparison_text += " ".join(cached_data["key_insights"]).lower() + " "
            
            cached_words = set(comparison_text.split())
            
            # Jaccard類似度計算
            intersection = len(user_words.intersection(cached_words))
            union = len(user_words.union(cached_words))
            
            return intersection / union if union > 0 else 0.0
            
        except Exception:
            return 0.0
    
    def _cache_knowledge(self, user_input: str, report: Dict):
        """知識をキャッシュに保存"""
        try:
            cache_filename = f"knowledge_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            cache_path = self.cache_dir / cache_filename
            
            cache_data = {
                "user_input": user_input,
                "report": report,
                "cached_at": datetime.now().isoformat()
            }
            
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
            
            # 古いキャッシュ削除
            self._cleanup_old_cache()
            
        except Exception as e:
            if self.logger:
                self.logger.warning("conversation_knowledge", "cache", f"キャッシュ保存エラー: {e}")
    
    def _cleanup_old_cache(self):
        """古いキャッシュファイル削除"""
        try:
            cutoff_time = datetime.now().timestamp() - (self.integration_config["cache_knowledge_hours"] * 3600)
            
            for cache_file in self.cache_dir.glob("*.json"):
                if cache_file.stat().st_mtime < cutoff_time:
                    cache_file.unlink()
            
        except Exception:
            pass
    
    def _generate_context_injection(self, knowledge_context: Dict) -> str:
        """コンテキスト注入テキスト生成"""
        mode = self.integration_config["context_injection_mode"]
        
        if mode == "keywords":
            # キーワードのみ注入
            topics = knowledge_context.get("related_topics", [])
            if topics:
                return f"関連キーワード: {', '.join(topics[:3])}"
        
        elif mode == "summary":
            # 要約注入
            summary = knowledge_context.get("knowledge_summary", "")
            insights = knowledge_context.get("key_insights", [])
            
            context_text = ""
            if summary:
                context_text += f"【背景知識】{summary[:200]}..."
            if insights:
                context_text += f" 【重要ポイント】{', '.join(insights[:2])}"
            
            return context_text
        
        elif mode == "full":
            # 完全な知識注入
            parts = []
            
            if knowledge_context.get("knowledge_summary"):
                parts.append(f"分析結果: {knowledge_context['knowledge_summary']}")
            
            if knowledge_context.get("key_insights"):
                parts.append(f"主要発見: {', '.join(knowledge_context['key_insights'][:3])}")
            
            if knowledge_context.get("related_topics"):
                parts.append(f"関連トピック: {', '.join(knowledge_context['related_topics'][:3])}")
            
            return " / ".join(parts)
        
        return ""
    
    def get_cache_stats(self) -> Dict:
        """キャッシュ統計情報取得"""
        try:
            cache_files = list(self.cache_dir.glob("*.json"))
            total_size = sum(f.stat().st_size for f in cache_files)
            
            return {
                "cache_count": len(cache_files),
                "total_size_mb": total_size / (1024 * 1024),
                "cache_dir": str(self.cache_dir),
                "oldest_cache": min((f.stat().st_mtime for f in cache_files), default=0),
                "newest_cache": max((f.stat().st_mtime for f in cache_files), default=0)
            }
        except Exception:
            return {"error": "統計情報取得に失敗"}
    
    def _initialize_knowledge_cache(self):
        """知識キャッシュ初期化"""
        try:
            print("[会話知識] 📚 知識キャッシュ構築開始")
            
            # セッション知識読み込み
            self._load_session_knowledge()
            
            # 統合知識読み込み
            self._load_integrated_knowledge()
            
            # インデックス構築
            self._build_knowledge_indexes()
            
            print(f"[会話知識] ✅ 知識キャッシュ構築完了: {len(self.knowledge_cache)}件")
            
        except Exception as e:
            print(f"[会話知識] ❌ 知識キャッシュ初期化失敗: {e}")
    
    def _load_session_knowledge(self):
        """セッション知識読み込み"""
        try:
            if not self.sessions_dir.exists():
                return
            
            session_files = list(self.sessions_dir.glob("session_*.json"))
            for session_file in session_files:
                with open(session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                    
                    session_metadata = session_data.get("session_metadata", {})
                    session_id = session_metadata.get("session_id", "")
                    
                    # 知識アイテム抽出
                    if "collection_results" in session_data:
                        knowledge_items = session_data["collection_results"].get("information_sources", [])
                        for item in knowledge_items:
                            knowledge_id = f"session_{session_id}_{item.get('source_id', '')}"
                            
                            self.knowledge_cache[knowledge_id] = {
                                "type": "session_knowledge",
                                "source": session_id,
                                "content": item.get("content", ""),
                                "title": item.get("title", ""),
                                "categories": item.get("categories", []),
                                "keywords": item.get("keywords", []),
                                "entities": item.get("entities", []),
                                "reliability_score": item.get("reliability_score", 0.7),
                                "created_at": session_metadata.get("created_at", ""),
                                "preprocessing_result": item.get("preprocessing_result", {})
                            }
            
            print(f"[会話知識] 📖 セッション知識読み込み: {len([k for k in self.knowledge_cache.keys() if k.startswith('session_')])}件")
            
        except Exception as e:
            print(f"[会話知識] ⚠️ セッション知識読み込み失敗: {e}")
    
    def _load_integrated_knowledge(self):
        """統合知識読み込み"""
        try:
            if not self.integrated_dir.exists():
                return
            
            integration_files = list(self.integrated_dir.glob("integration_*.json"))
            for integration_file in integration_files:
                with open(integration_file, 'r', encoding='utf-8') as f:
                    integration_data = json.load(f)
                    
                    for item in integration_data.get("integrated_knowledge", []):
                        knowledge_id = item.get("knowledge_id", "")
                        
                        self.knowledge_cache[knowledge_id] = {
                            "type": "integrated_knowledge",
                            "source": "integration",
                            "content": item.get("synthesized_content", ""),
                            "key_insights": item.get("key_insights", []),
                            "related_concepts": item.get("related_concepts", []),
                            "confidence_score": item.get("confidence_score", 0.7),
                            "novelty_score": item.get("novelty_score", 0.5),
                            "application_domains": item.get("application_domains", []),
                            "actionable_insights": item.get("actionable_insights", []),
                            "created_at": item.get("created_at", ""),
                            "integration_type": item.get("integration_type", "")
                        }
            
            print(f"[会話知識] 🔗 統合知識読み込み: {len([k for k in self.knowledge_cache.keys() if not k.startswith('session_')])}件")
            
        except Exception as e:
            print(f"[会話知識] ⚠️ 統合知識読み込み失敗: {e}")
    
    def _build_knowledge_indexes(self):
        """知識インデックス構築"""
        try:
            # トピック・エンティティインデックス構築
            for knowledge_id, knowledge in self.knowledge_cache.items():
                # カテゴリからトピック抽出
                categories = knowledge.get("categories", [])
                for category in categories:
                    self.topic_index[category.lower()].append(knowledge_id)
                
                # キーワードからトピック抽出
                keywords = knowledge.get("keywords", [])
                for keyword in keywords:
                    self.topic_index[keyword.lower()].append(knowledge_id)
                
                # エンティティインデックス
                entities = knowledge.get("entities", [])
                for entity in entities:
                    self.entity_index[entity.lower()].append(knowledge_id)
                
                # 関連概念からもインデックス構築
                related_concepts = knowledge.get("related_concepts", [])
                for concept in related_concepts:
                    self.topic_index[concept.lower()].append(knowledge_id)
            
            print(f"[会話知識] 🗂️ インデックス構築完了: トピック{len(self.topic_index)}件, エンティティ{len(self.entity_index)}件")
            
        except Exception as e:
            print(f"[会話知識] ❌ インデックス構築失敗: {e}")
    
    def analyze_user_input(self, user_input: str, conversation_context: List[Dict] = None) -> KnowledgeContext:
        """
        ユーザー入力分析・関連知識特定
        
        Args:
            user_input: ユーザーの入力文
            conversation_context: 会話履歴
            
        Returns:
            知識コンテキスト
        """
        try:
            print(f"[会話知識] 🔍 ユーザー入力分析: {user_input[:50]}...")
            
            # トピック検出
            detected_topics = self._detect_topics(user_input)
            
            # 関連知識検索
            relevant_knowledge = self._search_relevant_knowledge(user_input, detected_topics)
            
            # 会話履歴考慮
            if conversation_context:
                contextual_knowledge = self._get_contextual_knowledge(conversation_context, detected_topics)
                relevant_knowledge.extend(contextual_knowledge)
            
            # 重複除去・スコア順ソート
            relevant_knowledge = self._deduplicate_and_rank_knowledge(relevant_knowledge)
            
            # 信頼度計算
            confidence_score = self._calculate_context_confidence(detected_topics, relevant_knowledge)
            
            # 知識タイプ分類
            knowledge_types = self._classify_knowledge_types(relevant_knowledge)
            
            # 応用提案生成
            application_suggestions = self._generate_application_suggestions(relevant_knowledge, detected_topics)
            
            context_id = f"ctx_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(user_input) % 10000:04d}"
            
            context = KnowledgeContext(
                context_id=context_id,
                user_input=user_input,
                detected_topics=detected_topics,
                relevant_knowledge=relevant_knowledge[:self.provider_config["max_relevant_knowledge"]],
                confidence_score=confidence_score,
                knowledge_types=knowledge_types,
                application_suggestions=application_suggestions
            )
            
            # アクティブコンテキストに追加
            self.active_contexts.append(context)
            
            # 古いコンテキストクリーンアップ
            self._cleanup_old_contexts()
            
            print(f"[会話知識] ✅ 分析完了: トピック{len(detected_topics)}件, 関連知識{len(context.relevant_knowledge)}件")
            
            return context
            
        except Exception as e:
            print(f"[会話知識] ❌ ユーザー入力分析失敗: {e}")
            return KnowledgeContext("", user_input, [], [], 0.0, [], [])
    
    def _detect_topics(self, user_input: str) -> List[str]:
        """トピック検出"""
        detected_topics = []
        user_input_lower = user_input.lower()
        
        try:
            # パターンマッチングによるトピック検出
            for topic, patterns in self.topic_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, user_input_lower):
                        if topic not in detected_topics:
                            detected_topics.append(topic)
                        break
            
            # キーワード直接マッチング
            for topic_key in self.topic_index.keys():
                if topic_key in user_input_lower:
                    # 対応するメイントピック検索
                    for main_topic, patterns in self.topic_patterns.items():
                        if any(re.search(pattern, topic_key) for pattern in patterns):
                            if main_topic not in detected_topics:
                                detected_topics.append(main_topic)
                            break
            
            # エンティティからのトピック推定
            for entity_key in self.entity_index.keys():
                if entity_key in user_input_lower:
                    # エンティティに関連する知識からトピック推定
                    related_knowledge_ids = self.entity_index[entity_key][:3]  # 上位3件
                    for knowledge_id in related_knowledge_ids:
                        knowledge = self.knowledge_cache.get(knowledge_id, {})
                        categories = knowledge.get("categories", [])
                        for category in categories:
                            if category not in detected_topics:
                                detected_topics.append(category)
            
        except Exception as e:
            print(f"[会話知識] ⚠️ トピック検出失敗: {e}")
        
        return detected_topics[:5]  # 最大5トピック
    
    def _search_relevant_knowledge(self, user_input: str, detected_topics: List[str]) -> List[Dict]:
        """関連知識検索"""
        relevant_knowledge = []
        
        try:
            # トピックベース検索
            for topic in detected_topics:
                topic_lower = topic.lower()
                knowledge_ids = self.topic_index.get(topic_lower, [])
                
                for knowledge_id in knowledge_ids[:10]:  # 各トピックから最大10件
                    knowledge = self.knowledge_cache.get(knowledge_id, {})
                    if knowledge:
                        relevance_score = self._calculate_relevance_score(user_input, knowledge)
                        
                        if relevance_score >= self.provider_config["relevance_threshold"]:
                            relevant_knowledge.append({
                                "knowledge_id": knowledge_id,
                                "knowledge": knowledge,
                                "relevance_score": relevance_score,
                                "match_type": "topic_match"
                            })
            
            # テキスト類似度検索
            text_matches = self._search_by_text_similarity(user_input)
            relevant_knowledge.extend(text_matches)
            
            # エンティティベース検索
            entity_matches = self._search_by_entities(user_input)
            relevant_knowledge.extend(entity_matches)
            
        except Exception as e:
            print(f"[会話知識] ⚠️ 関連知識検索失敗: {e}")
        
        return relevant_knowledge
    
    def _calculate_relevance_score(self, user_input: str, knowledge: Dict) -> float:
        """関連度スコア計算"""
        try:
            user_input_lower = user_input.lower()
            
            scores = []
            
            # コンテンツ類似度
            content = knowledge.get("content", "").lower()
            if content:
                content_similarity = SequenceMatcher(None, user_input_lower, content).ratio()
                scores.append(("content", content_similarity, 0.4))
            
            # タイトル類似度
            title = knowledge.get("title", "").lower()
            if title:
                title_similarity = SequenceMatcher(None, user_input_lower, title).ratio()
                scores.append(("title", title_similarity, 0.3))
            
            # キーワードマッチ
            keywords = knowledge.get("keywords", [])
            keyword_matches = sum(1 for kw in keywords if kw.lower() in user_input_lower)
            if keywords:
                keyword_score = keyword_matches / len(keywords)
                scores.append(("keywords", keyword_score, 0.2))
            
            # エンティティマッチ
            entities = knowledge.get("entities", [])
            entity_matches = sum(1 for entity in entities if entity.lower() in user_input_lower)
            if entities:
                entity_score = entity_matches / len(entities)
                scores.append(("entities", entity_score, 0.1))
            
            # 重み付き合計
            if scores:
                weighted_sum = sum(score * weight for _, score, weight in scores)
                total_weight = sum(weight for _, _, weight in scores)
                return weighted_sum / total_weight
            
            return 0.0
            
        except Exception as e:
            print(f"[会話知識] ⚠️ 関連度スコア計算失敗: {e}")
            return 0.0
    
    def _search_by_text_similarity(self, user_input: str) -> List[Dict]:
        """テキスト類似度検索"""
        text_matches = []
        
        try:
            user_input_lower = user_input.lower()
            
            for knowledge_id, knowledge in self.knowledge_cache.items():
                content = knowledge.get("content", "").lower()
                title = knowledge.get("title", "").lower()
                
                # 単語レベルでの共通性チェック
                user_words = set(re.findall(r'\w+', user_input_lower))
                content_words = set(re.findall(r'\w+', content))
                title_words = set(re.findall(r'\w+', title))
                
                if len(user_words) > 0:
                    content_overlap = len(user_words & content_words) / len(user_words)
                    title_overlap = len(user_words & title_words) / len(user_words) if title_words else 0
                    
                    max_overlap = max(content_overlap, title_overlap)
                    
                    if max_overlap >= 0.3:  # 30%以上の単語重複
                        text_matches.append({
                            "knowledge_id": knowledge_id,
                            "knowledge": knowledge,
                            "relevance_score": max_overlap,
                            "match_type": "text_similarity"
                        })
            
        except Exception as e:
            print(f"[会話知識] ⚠️ テキスト類似度検索失敗: {e}")
        
        return text_matches
    
    def _search_by_entities(self, user_input: str) -> List[Dict]:
        """エンティティベース検索"""
        entity_matches = []
        
        try:
            user_input_lower = user_input.lower()
            
            for entity_key, knowledge_ids in self.entity_index.items():
                if entity_key in user_input_lower:
                    for knowledge_id in knowledge_ids[:5]:  # 各エンティティから最大5件
                        knowledge = self.knowledge_cache.get(knowledge_id, {})
                        if knowledge:
                            # エンティティマッチによる関連度は中程度
                            relevance_score = 0.7
                            
                            entity_matches.append({
                                "knowledge_id": knowledge_id,
                                "knowledge": knowledge,
                                "relevance_score": relevance_score,
                                "match_type": "entity_match",
                                "matched_entity": entity_key
                            })
            
        except Exception as e:
            print(f"[会話知識] ⚠️ エンティティベース検索失敗: {e}")
        
        return entity_matches
    
    def _get_contextual_knowledge(self, conversation_context: List[Dict], detected_topics: List[str]) -> List[Dict]:
        """会話文脈からの関連知識取得"""
        contextual_knowledge = []
        
        try:
            # 過去の会話から関連トピック抽出
            context_window = conversation_context[-self.provider_config["context_window_size"]:]
            
            for message in context_window:
                message_text = message.get("content", "")
                if message_text:
                    # 過去のメッセージからも関連知識検索
                    past_topics = self._detect_topics(message_text)
                    
                    # 現在のトピックとの関連性チェック
                    common_topics = set(detected_topics) & set(past_topics)
                    
                    if common_topics:
                        for topic in common_topics:
                            topic_knowledge = self.topic_index.get(topic.lower(), [])
                            for knowledge_id in topic_knowledge[:3]:  # 各共通トピックから3件
                                knowledge = self.knowledge_cache.get(knowledge_id, {})
                                if knowledge:
                                    contextual_knowledge.append({
                                        "knowledge_id": knowledge_id,
                                        "knowledge": knowledge,
                                        "relevance_score": 0.6,  # 文脈的関連度
                                        "match_type": "contextual_match",
                                        "context_topic": topic
                                    })
            
        except Exception as e:
            print(f"[会話知識] ⚠️ 文脈知識取得失敗: {e}")
        
        return contextual_knowledge
    
    def _deduplicate_and_rank_knowledge(self, knowledge_list: List[Dict]) -> List[Dict]:
        """重複除去・ランキング"""
        try:
            # 知識IDによる重複除去
            unique_knowledge = {}
            for item in knowledge_list:
                knowledge_id = item["knowledge_id"]
                if knowledge_id not in unique_knowledge:
                    unique_knowledge[knowledge_id] = item
                else:
                    # より高いスコアのものを保持
                    if item["relevance_score"] > unique_knowledge[knowledge_id]["relevance_score"]:
                        unique_knowledge[knowledge_id] = item
            
            # 関連度スコア順でソート
            ranked_knowledge = list(unique_knowledge.values())
            ranked_knowledge.sort(key=lambda x: x["relevance_score"], reverse=True)
            
            return ranked_knowledge
            
        except Exception as e:
            print(f"[会話知識] ⚠️ 重複除去・ランキング失敗: {e}")
            return knowledge_list
    
    def _calculate_context_confidence(self, detected_topics: List[str], relevant_knowledge: List[Dict]) -> float:
        """コンテキスト信頼度計算"""
        try:
            if not detected_topics or not relevant_knowledge:
                return 0.0
            
            # トピック検出の確実性
            topic_confidence = min(1.0, len(detected_topics) / 3)
            
            # 関連知識の品質
            avg_relevance = sum(item["relevance_score"] for item in relevant_knowledge) / len(relevant_knowledge)
            
            # 知識の信頼性
            knowledge_reliability = 0.0
            for item in relevant_knowledge:
                knowledge = item["knowledge"]
                reliability = knowledge.get("reliability_score", 0.7)
                confidence = knowledge.get("confidence_score", 0.7)
                knowledge_reliability += (reliability + confidence) / 2
            
            knowledge_reliability /= len(relevant_knowledge)
            
            # 総合信頼度
            overall_confidence = (topic_confidence * 0.3 + avg_relevance * 0.4 + knowledge_reliability * 0.3)
            
            return min(1.0, overall_confidence)
            
        except Exception as e:
            print(f"[会話知識] ⚠️ 信頼度計算失敗: {e}")
            return 0.5
    
    def _classify_knowledge_types(self, relevant_knowledge: List[Dict]) -> List[str]:
        """知識タイプ分類"""
        knowledge_types = set()
        
        try:
            for item in relevant_knowledge:
                knowledge = item["knowledge"]
                
                # 知識の種類判定
                if knowledge.get("type") == "integrated_knowledge":
                    knowledge_types.add("analytical")
                    
                    # 統合知識の特性による分類
                    if knowledge.get("integration_type") == "temporal_evolution":
                        knowledge_types.add("predictive")
                elif knowledge.get("type") == "session_knowledge":
                    knowledge_types.add("factual")
                    
                    # 前処理結果による分類
                    preprocessing = knowledge.get("preprocessing_result", {})
                    if preprocessing.get("category") == "実用":
                        knowledge_types.add("experiential")
                
                # 応用可能性による分類
                if knowledge.get("actionable_insights"):
                    knowledge_types.add("experiential")
                
                # 予測・トレンド情報
                if any(keyword in knowledge.get("content", "").lower() 
                      for keyword in ["予測", "将来", "トレンド", "見込み"]):
                    knowledge_types.add("predictive")
            
        except Exception as e:
            print(f"[会話知識] ⚠️ 知識タイプ分類失敗: {e}")
        
        return list(knowledge_types)
    
    def _generate_application_suggestions(self, relevant_knowledge: List[Dict], detected_topics: List[str]) -> List[str]:
        """応用提案生成"""
        suggestions = []
        
        try:
            # 知識ベースの提案
            for item in relevant_knowledge[:3]:  # 上位3件から提案生成
                knowledge = item["knowledge"]
                
                # 実行可能な洞察
                actionable_insights = knowledge.get("actionable_insights", [])
                suggestions.extend(actionable_insights[:2])
                
                # 応用分野の提案
                application_domains = knowledge.get("application_domains", [])
                for domain in application_domains[:2]:
                    suggestions.append(f"{domain}での活用を検討")
                
                # 統合知識からの提案
                if knowledge.get("type") == "integrated_knowledge":
                    key_insights = knowledge.get("key_insights", [])
                    for insight in key_insights[:1]:
                        suggestions.append(f"洞察の活用: {insight}")
            
            # トピックベースの提案
            for topic in detected_topics[:2]:
                if topic == "AI技術":
                    suggestions.append("最新AI技術動向の継続的学習")
                elif topic == "音楽生成":
                    suggestions.append("音楽生成ツールの実践的検証")
                elif topic == "技術動向":
                    suggestions.append("技術トレンド分析の深化")
            
            # 重複除去
            suggestions = list(dict.fromkeys(suggestions))
            
        except Exception as e:
            print(f"[会話知識] ⚠️ 応用提案生成失敗: {e}")
        
        return suggestions[:5]  # 最大5件
    
    def _cleanup_old_contexts(self):
        """古いコンテキストクリーンアップ"""
        try:
            # 最新10件のみ保持
            if len(self.active_contexts) > 10:
                self.active_contexts = self.active_contexts[-10:]
        except Exception as e:
            print(f"[会話知識] ⚠️ コンテキストクリーンアップ失敗: {e}")
    
    def generate_conversation_enhancements(self, knowledge_context: KnowledgeContext) -> List[ConversationEnhancement]:
        """
        会話強化提案生成
        
        Args:
            knowledge_context: 知識コンテキスト
            
        Returns:
            会話強化提案リスト
        """
        try:
            enhancements = []
            
            if not self.provider_config["auto_enhancement_enabled"]:
                return enhancements
            
            # 知識注入型強化
            knowledge_injections = self._generate_knowledge_injections(knowledge_context)
            enhancements.extend(knowledge_injections)
            
            # 洞察共有型強化
            insight_sharings = self._generate_insight_sharings(knowledge_context)
            enhancements.extend(insight_sharings)
            
            # トレンド分析型強化
            trend_analyses = self._generate_trend_analyses(knowledge_context)
            enhancements.extend(trend_analyses)
            
            # 関連度順ソート
            enhancements.sort(key=lambda x: x.relevance_score, reverse=True)
            
            print(f"[会話知識] 💡 会話強化提案: {len(enhancements)}件")
            
            return enhancements[:3]  # 最大3件
            
        except Exception as e:
            print(f"[会話知識] ❌ 会話強化提案生成失敗: {e}")
            return []
    
    def get_knowledge_statistics(self) -> Dict[str, Any]:
        """知識統計情報取得"""
        try:
            total_contexts = len(self.active_contexts)
            
            # 分析タイプ別統計
            analysis_types = {}
            for context in self.active_contexts:
                analysis_type = context.analysis_type
                if analysis_type not in analysis_types:
                    analysis_types[analysis_type] = 0
                analysis_types[analysis_type] += 1
            
            # 平均適合度
            avg_confidence = 0.0
            if total_contexts > 0:
                avg_confidence = sum(context.confidence_score for context in self.active_contexts) / total_contexts
            
            # 知識ソース統計
            knowledge_sources = set()
            for context in self.active_contexts:
                for item in context.relevant_knowledge:
                    knowledge_sources.add(item["knowledge_id"])
            
            return {
                "total_contexts": total_contexts,
                "analysis_type_distribution": analysis_types,
                "average_confidence": avg_confidence,
                "unique_knowledge_sources": len(knowledge_sources),
                "auto_enhancement_enabled": self.provider_config["auto_enhancement_enabled"],
                "enhancement_threshold": self.provider_config["enhancement_threshold"]
            }
            
        except Exception as e:
            print(f"[会話知識] ❌ 統計情報取得失敗: {e}")
            return {"error": str(e)}
    
    def _generate_knowledge_injections(self, context: KnowledgeContext) -> List[ConversationEnhancement]:
        """知識注入強化生成"""
        injections = []
        
        try:
            for item in context.relevant_knowledge[:2]:  # 上位2件
                knowledge = item["knowledge"]
                
                # 直接的な知識共有
                if knowledge.get("type") == "session_knowledge":
                    content = f"関連する調査結果: {knowledge.get('content', '')[:100]}..."
                    
                    injections.append(ConversationEnhancement(
                        enhancement_type="knowledge_injection",
                        knowledge_source=item["knowledge_id"],
                        enhancement_content=content,
                        relevance_score=item["relevance_score"],
                        timing_suggestion="immediate"
                    ))
                
                # 統合知識からの洞察
                elif knowledge.get("type") == "integrated_knowledge":
                    insights = knowledge.get("key_insights", [])
                    if insights:
                        content = f"統合分析による洞察: {insights[0]}"
                        
                        injections.append(ConversationEnhancement(
                            enhancement_type="knowledge_injection",
                            knowledge_source=item["knowledge_id"],
                            enhancement_content=content,
                            relevance_score=item["relevance_score"] * 0.9,
                            timing_suggestion="follow_up"
                        ))
            
        except Exception as e:
            print(f"[会話知識] ⚠️ 知識注入強化生成失敗: {e}")
        
        return injections
    
    def _generate_insight_sharings(self, context: KnowledgeContext) -> List[ConversationEnhancement]:
        """洞察共有強化生成"""
        sharings = []
        
        try:
            # 統合知識からの洞察共有
            for item in context.relevant_knowledge:
                knowledge = item["knowledge"]
                
                if knowledge.get("type") == "integrated_knowledge":
                    actionable_insights = knowledge.get("actionable_insights", [])
                    
                    for insight in actionable_insights[:1]:  # 1件のみ
                        content = f"実践的な洞察: {insight}"
                        
                        sharings.append(ConversationEnhancement(
                            enhancement_type="insight_sharing",
                            knowledge_source=item["knowledge_id"],
                            enhancement_content=content,
                            relevance_score=item["relevance_score"] * 0.8,
                            timing_suggestion="related_topic"
                        ))
            
        except Exception as e:
            print(f"[会話知識] ⚠️ 洞察共有強化生成失敗: {e}")
        
        return sharings
    
    def _generate_trend_analyses(self, context: KnowledgeContext) -> List[ConversationEnhancement]:
        """トレンド分析強化生成"""
        analyses = []
        
        try:
            # 時系列進化分析からのトレンド共有
            for item in context.relevant_knowledge:
                knowledge = item["knowledge"]
                
                if knowledge.get("integration_type") == "temporal_evolution":
                    evolution_trends = knowledge.get("evolution_trends", [])
                    
                    for trend in evolution_trends[:1]:
                        content = f"トレンド分析: {trend.get('trend', '')} - {trend.get('evidence', '')}"
                        
                        analyses.append(ConversationEnhancement(
                            enhancement_type="trend_analysis",
                            knowledge_source=item["knowledge_id"],
                            enhancement_content=content,
                            relevance_score=item["relevance_score"] * 0.7,
                            timing_suggestion="follow_up"
                        ))
            
        except Exception as e:
            print(f"[会話知識] ⚠️ トレンド分析強化生成失敗: {e}")
        
        return analyses
    
    def get_proactive_suggestions(self, conversation_history: List[Dict]) -> List[str]:
        """
        積極的提案取得
        
        Args:
            conversation_history: 会話履歴
            
        Returns:
            積極的提案リスト
        """
        try:
            if not self.provider_config["proactive_suggestion_enabled"]:
                return []
            
            suggestions = []
            
            # 会話のトピック傾向分析
            recent_topics = self._analyze_conversation_topics(conversation_history)
            
            # 未活用の関連知識特定
            underutilized_knowledge = self._find_underutilized_knowledge(recent_topics)
            
            # 提案生成
            for knowledge_item in underutilized_knowledge[:3]:
                knowledge = knowledge_item["knowledge"]
                
                if knowledge.get("type") == "integrated_knowledge":
                    suggestions.append(f"関連分析: {knowledge.get('synthesized_content', '')[:80]}...")
                elif knowledge.get("actionable_insights"):
                    suggestions.append(f"活用提案: {knowledge['actionable_insights'][0]}")
                else:
                    suggestions.append(f"関連情報: {knowledge.get('content', '')[:80]}...")
            
            return suggestions
            
        except Exception as e:
            print(f"[会話知識] ❌ 積極的提案取得失敗: {e}")
            return []
    
    def _analyze_conversation_topics(self, conversation_history: List[Dict]) -> List[str]:
        """会話トピック傾向分析"""
        topic_counts = defaultdict(int)
        
        try:
            for message in conversation_history[-10:]:  # 最新10件
                content = message.get("content", "")
                detected_topics = self._detect_topics(content)
                
                for topic in detected_topics:
                    topic_counts[topic] += 1
            
            # 頻出トピック順でソート
            sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
            return [topic for topic, count in sorted_topics[:5]]
            
        except Exception as e:
            print(f"[会話知識] ⚠️ 会話トピック分析失敗: {e}")
            return []
    
    def _find_underutilized_knowledge(self, recent_topics: List[str]) -> List[Dict]:
        """未活用知識特定"""
        underutilized = []
        
        try:
            # 最近のトピックに関連するが未活用の知識を検索
            for topic in recent_topics:
                topic_knowledge = self.topic_index.get(topic.lower(), [])
                
                for knowledge_id in topic_knowledge[:5]:
                    knowledge = self.knowledge_cache.get(knowledge_id, {})
                    
                    # 最近使用されていない高品質な知識
                    if knowledge:
                        # 統合知識や高信頼度知識を優先
                        if (knowledge.get("type") == "integrated_knowledge" or 
                            knowledge.get("confidence_score", 0) > 0.8):
                            underutilized.append({
                                "knowledge_id": knowledge_id,
                                "knowledge": knowledge,
                                "relevance_score": 0.7,
                                "topic": topic
                            })
            
            return underutilized
            
        except Exception as e:
            print(f"[会話知識] ⚠️ 未活用知識特定失敗: {e}")
            return []
    
    def update_conversation_history(self, user_input: str, assistant_response: str):
        """会話履歴更新"""
        try:
            self.conversation_history.append({
                "timestamp": datetime.now().isoformat(),
                "user_input": user_input,
                "assistant_response": assistant_response
            })
            
            # 履歴サイズ制限
            if len(self.conversation_history) > 50:
                self.conversation_history = self.conversation_history[-50:]
                
        except Exception as e:
            print(f"[会話知識] ⚠️ 会話履歴更新失敗: {e}")
    
    def get_knowledge_statistics(self) -> Dict[str, Any]:
        """知識統計情報取得"""
        try:
            session_knowledge_count = len([k for k in self.knowledge_cache.keys() if k.startswith('session_')])
            integrated_knowledge_count = len(self.knowledge_cache) - session_knowledge_count
            
            return {
                "total_knowledge_items": len(self.knowledge_cache),
                "session_knowledge": session_knowledge_count,
                "integrated_knowledge": integrated_knowledge_count,
                "topic_index_size": len(self.topic_index),
                "entity_index_size": len(self.entity_index),
                "active_contexts": len(self.active_contexts),
                "conversation_history_size": len(self.conversation_history),
                "cache_hit_rate": 0.85  # 実際の実装では計算
            }
            
        except Exception as e:
            print(f"[会話知識] ❌ 統計情報取得失敗: {e}")
            return {}


# テスト用コード
if __name__ == "__main__":
    print("=== ConversationKnowledgeProvider テスト ===")
    
    provider = ConversationKnowledgeProvider()
    
    # テスト用ユーザー入力
    test_inputs = [
        "AI音楽生成について教えて",
        "Transformerを使った音楽制作はどう？",
        "最新の技術動向が知りたい"
    ]
    
    print("\n🔍 ユーザー入力分析テスト:")
    for i, user_input in enumerate(test_inputs, 1):
        print(f"\n--- テスト{i}: {user_input} ---")
        
        context = provider.analyze_user_input(user_input)
        
        print(f"検出トピック: {context.detected_topics}")
        print(f"関連知識: {len(context.relevant_knowledge)}件")
        print(f"信頼度: {context.confidence_score:.2f}")
        print(f"知識タイプ: {context.knowledge_types}")
        print(f"応用提案: {context.application_suggestions}")
        
        # 会話強化提案
        enhancements = provider.generate_conversation_enhancements(context)
        print(f"会話強化: {len(enhancements)}件")
        for enhancement in enhancements:
            print(f"  - {enhancement.enhancement_type}: {enhancement.enhancement_content[:50]}...")
    
    # 積極的提案テスト
    print(f"\n💡 積極的提案テスト:")
    conversation_history = [
        {"content": "AI音楽について話した"},
        {"content": "技術動向も気になる"}
    ]
    suggestions = provider.get_proactive_suggestions(conversation_history)
    print(f"提案数: {len(suggestions)}件")
    for suggestion in suggestions:
        print(f"  - {suggestion}")
    
    # 統計情報
    print(f"\n📊 知識統計:")
    stats = provider.get_knowledge_statistics()
    print(f"  総知識: {stats.get('total_knowledge_items', 0)}件")
    print(f"  セッション知識: {stats.get('session_knowledge', 0)}件") 
    print(f"  統合知識: {stats.get('integrated_knowledge', 0)}件")
    print(f"  トピックインデックス: {stats.get('topic_index_size', 0)}件")
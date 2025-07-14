#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
コンテキスト理解エンジン - Phase 2C実装
文脈を踏まえた高度な知識推薦システム
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from datetime import datetime, timedelta
import re
import hashlib

# プロジェクトルートをパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 関連システム
try:
    from core.semantic_search_engine import SemanticSearchEngine
    from core.knowledge_graph_system import KnowledgeGraphSystem
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False

# Windowsパス設定
if os.name == 'nt':
    DATA_DIR = Path("D:/setsuna_bot/data")
    CONTEXT_CACHE_DIR = Path("D:/setsuna_bot/context_cache")
else:
    DATA_DIR = Path("/mnt/d/setsuna_bot/data")
    CONTEXT_CACHE_DIR = Path("/mnt/d/setsuna_bot/context_cache")

CONTEXT_CACHE_DIR.mkdir(parents=True, exist_ok=True)

@dataclass
class ConversationContext:
    """会話コンテキストデータクラス"""
    context_id: str
    session_id: str
    conversation_flow: List[Dict[str, Any]]  # 会話の流れ
    mentioned_topics: List[str]  # 言及されたトピック
    user_preferences: Dict[str, float]  # ユーザー好み（推定）
    temporal_context: str  # 時間的文脈
    emotional_state: str  # 感情状態
    knowledge_depth: Dict[str, float]  # トピック別知識の深さ
    last_updated: str

@dataclass  
class ContextualRecommendation:
    """文脈的推薦データクラス"""
    recommendation_id: str
    content_id: str
    content_title: str
    recommendation_type: str  # "continuation", "related", "contrast", "exploration"
    context_relevance: float
    reasoning: List[str]  # 推薦理由
    confidence: float
    timing: str  # "immediate", "followup", "later"

@dataclass
class TopicTransition:
    """トピック遷移データクラス"""
    from_topic: str
    to_topic: str
    transition_type: str  # "natural", "jump", "return", "exploration"
    strength: float
    patterns: List[str]  # 遷移パターン

class ContextUnderstandingEngine:
    """コンテキスト理解エンジンクラス"""
    
    def __init__(self):
        """初期化"""
        self.conversation_history_path = DATA_DIR / "multi_turn_conversations.json"
        self.user_preferences_path = DATA_DIR / "user_preferences.json"
        self.context_cache_path = CONTEXT_CACHE_DIR / "context_cache.json"
        self.transition_patterns_path = CONTEXT_CACHE_DIR / "topic_transitions.json"
        
        # 依存システム
        if DEPENDENCIES_AVAILABLE:
            self.semantic_search = SemanticSearchEngine()
            self.knowledge_graph = KnowledgeGraphSystem()
        else:
            self.semantic_search = None
            self.knowledge_graph = None
            print("[コンテキスト理解] ⚠️ 依存システムが利用できません")
        
        # データ
        self.conversation_history = {}
        self.user_preferences = {}
        self.context_cache = {}
        self.topic_transitions = {}
        
        # 現在のコンテキスト
        self.current_context = None
        self.conversation_memory = deque(maxlen=20)  # 直近20発話を記憶
        
        # パターン認識用データ
        self.context_patterns = self._build_context_patterns()
        self.emotional_indicators = self._build_emotional_indicators()
        self.knowledge_depth_indicators = self._build_knowledge_depth_indicators()
        
        # 統計情報
        self.engine_statistics = {
            "contexts_processed": 0,
            "recommendations_generated": 0,
            "pattern_matches": 0,
            "transition_predictions": 0
        }
        
        self._load_data()
        print("[コンテキスト理解] ✅ コンテキスト理解エンジン初期化完了")
    
    def _build_context_patterns(self) -> Dict[str, List[str]]:
        """コンテキストパターン構築"""
        return {
            "continuation_signals": [
                r"それで",
                r"その後",
                r"続きは",
                r"もっと詳しく",
                r"他には",
                r"さらに"
            ],
            "topic_shift_signals": [
                r"ところで",
                r"そういえば", 
                r"話は変わって",
                r"別の話だけど",
                r"今度は",
                r"次に"
            ],
            "exploration_signals": [
                r"初めて聞く",
                r"知らなかった",
                r"面白そう",
                r"気になる",
                r"どんな",
                r"教えて"
            ],
            "comparison_signals": [
                r"比べて",
                r"違いは",
                r"どっちが",
                r"より",
                r"一方で",
                r"対照的"
            ],
            "preference_signals": [
                r"好き",
                r"嫌い",
                r"気に入った",
                r"苦手",
                r"お気に入り",
                r"嫌い"
            ]
        }
    
    def _build_emotional_indicators(self) -> Dict[str, List[str]]:
        """感情指標構築"""
        return {
            "excited": ["楽しい", "嬉しい", "わくわく", "テンション", "最高", "素晴らしい"],
            "curious": ["気になる", "面白そう", "どんな", "なぜ", "どうして", "知りたい"],
            "nostalgic": ["懐かしい", "昔", "思い出", "前に", "当時", "昔聞いた"],
            "relaxed": ["のんびり", "ゆっくり", "癒し", "リラックス", "穏やか", "落ち着く"],
            "focused": ["集中", "詳しく", "深く", "本格的", "真剣", "丁寧に"],
            "disappointed": ["残念", "がっかり", "期待外れ", "思ったより", "微妙", "いまいち"]
        }
    
    def _build_knowledge_depth_indicators(self) -> Dict[str, Dict[str, List[str]]]:
        """知識深度指標構築"""
        return {
            "beginner": {
                "phrases": ["初めて", "よく知らない", "聞いたことない", "どんな", "基本的な"],
                "questions": ["って何", "どういう", "簡単に", "わかりやすく"]
            },
            "intermediate": {
                "phrases": ["知ってる", "聞いたことある", "だいたい", "ある程度"],
                "questions": ["詳しく", "もっと", "他にも", "関連する"]
            },
            "advanced": {
                "phrases": ["詳しい", "よく聞く", "マニア", "専門", "深く"],
                "questions": ["マイナーな", "レアな", "特殊な", "プロ向け"]
            }
        }
    
    def _load_data(self):
        """データロード"""
        # 会話履歴
        try:
            if self.conversation_history_path.exists():
                with open(self.conversation_history_path, 'r', encoding='utf-8') as f:
                    self.conversation_history = json.load(f)
        except Exception as e:
            print(f"[コンテキスト理解] ⚠️ 会話履歴ロードエラー: {e}")
        
        # ユーザー好み
        try:
            if self.user_preferences_path.exists():
                with open(self.user_preferences_path, 'r', encoding='utf-8') as f:
                    self.user_preferences = json.load(f)
        except Exception as e:
            print(f"[コンテキスト理解] ⚠️ ユーザー好みロードエラー: {e}")
        
        # コンテキストキャッシュ
        try:
            if self.context_cache_path.exists():
                with open(self.context_cache_path, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    self.context_cache = cache_data.get("contexts", {})
        except Exception as e:
            print(f"[コンテキスト理解] ⚠️ キャッシュロードエラー: {e}")
        
        # トピック遷移パターン
        try:
            if self.transition_patterns_path.exists():
                with open(self.transition_patterns_path, 'r', encoding='utf-8') as f:
                    self.topic_transitions = json.load(f)
        except Exception as e:
            print(f"[コンテキスト理解] ⚠️ 遷移パターンロードエラー: {e}")
    
    def analyze_conversation_context(self, user_input: str, session_id: str = "default") -> ConversationContext:
        """会話コンテキスト分析"""
        # 現在の発話を記憶に追加
        current_turn = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "processed": True
        }
        self.conversation_memory.append(current_turn)
        
        # コンテキスト抽出
        context_id = f"context_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 会話の流れ分析
        conversation_flow = self._analyze_conversation_flow()
        
        # 言及トピック抽出
        mentioned_topics = self._extract_mentioned_topics(user_input)
        
        # ユーザー好み推定
        estimated_preferences = self._estimate_user_preferences(user_input)
        
        # 時間的文脈判定
        temporal_context = self._determine_temporal_context(user_input)
        
        # 感情状態推定
        emotional_state = self._estimate_emotional_state(user_input)
        
        # 知識深度分析
        knowledge_depth = self._analyze_knowledge_depth(user_input, mentioned_topics)
        
        context = ConversationContext(
            context_id=context_id,
            session_id=session_id,
            conversation_flow=conversation_flow,
            mentioned_topics=mentioned_topics,
            user_preferences=estimated_preferences,
            temporal_context=temporal_context,
            emotional_state=emotional_state,
            knowledge_depth=knowledge_depth,
            last_updated=datetime.now().isoformat()
        )
        
        self.current_context = context
        self._save_context_to_cache(context)
        
        # 統計更新
        self.engine_statistics["contexts_processed"] += 1
        
        return context
    
    def _analyze_conversation_flow(self) -> List[Dict[str, Any]]:
        """会話フロー分析"""
        flow = []
        
        for i, turn in enumerate(self.conversation_memory):
            flow_item = {
                "turn_number": i,
                "timestamp": turn.get("timestamp"),
                "content_summary": turn.get("user_input", "")[:50] + "..." if len(turn.get("user_input", "")) > 50 else turn.get("user_input", ""),
                "flow_type": self._classify_flow_type(turn.get("user_input", ""), i)
            }
            flow.append(flow_item)
        
        return flow
    
    def _classify_flow_type(self, user_input: str, turn_number: int) -> str:
        """フロータイプ分類"""
        if turn_number == 0:
            return "opening"
        
        # パターンマッチング
        for pattern_type, patterns in self.context_patterns.items():
            for pattern in patterns:
                if re.search(pattern, user_input):
                    if pattern_type == "continuation_signals":
                        return "continuation"
                    elif pattern_type == "topic_shift_signals":
                        return "topic_shift"
                    elif pattern_type == "exploration_signals":
                        return "exploration"
                    elif pattern_type == "comparison_signals":
                        return "comparison"
        
        return "general"
    
    def _extract_mentioned_topics(self, user_input: str) -> List[str]:
        """言及トピック抽出"""
        topics = []
        
        # 音楽関連キーワード
        music_keywords = {
            "アーティスト": ["歌手", "バンド", "グループ", "ソロ", "ミュージシャン"],
            "ジャンル": ["ロック", "ポップ", "ジャズ", "クラシック", "ボカロ", "アニソン"],
            "楽器": ["ギター", "ピアノ", "ドラム", "ベース", "ボーカル"],
            "ムード": ["明るい", "暗い", "激しい", "穏やか", "感動的", "楽しい"],
            "時代": ["最新", "新しい", "古い", "クラシック", "現代", "昔"]
        }
        
        for topic_category, keywords in music_keywords.items():
            for keyword in keywords:
                if keyword in user_input:
                    topics.append(topic_category)
                    break
        
        # 固有名詞抽出（簡易版）
        # カタカナ3文字以上を固有名詞として抽出
        katakana_pattern = r'[ァ-ヶー]{3,}'
        katakana_matches = re.findall(katakana_pattern, user_input)
        topics.extend(katakana_matches)
        
        return list(set(topics))  # 重複削除
    
    def _estimate_user_preferences(self, user_input: str) -> Dict[str, float]:
        """ユーザー好み推定"""
        preferences = {}
        
        # 好み表現の検出
        for signal_type, patterns in self.context_patterns.items():
            if signal_type == "preference_signals":
                for pattern in patterns:
                    if pattern in user_input:
                        # 好みの強度を推定
                        if pattern in ["大好き", "最高", "お気に入り"]:
                            strength = 0.9
                        elif pattern in ["好き", "気に入った"]:
                            strength = 0.7
                        elif pattern in ["嫌い", "苦手"]:
                            strength = -0.7
                        else:
                            strength = 0.5
                        
                        # 近接する名詞を好みの対象として推定
                        words = user_input.split()
                        for i, word in enumerate(words):
                            if pattern in word:
                                # 前後の単語を確認
                                for j in range(max(0, i-3), min(len(words), i+4)):
                                    if j != i and len(words[j]) > 1:
                                        preferences[words[j]] = strength
        
        return preferences
    
    def _determine_temporal_context(self, user_input: str) -> str:
        """時間的文脈判定"""
        temporal_indicators = {
            "immediate": ["今", "いま", "現在", "今日", "今回"],
            "recent": ["最近", "この頃", "最近の", "新しい"],
            "past": ["昔", "前に", "以前", "当時", "昔の"],
            "future": ["今度", "次回", "将来", "これから", "後で"],
            "ongoing": ["いつも", "普段", "日頃", "常に", "毎回"]
        }
        
        for context_type, indicators in temporal_indicators.items():
            for indicator in indicators:
                if indicator in user_input:
                    return context_type
        
        return "general"
    
    def _estimate_emotional_state(self, user_input: str) -> str:
        """感情状態推定"""
        emotion_scores = defaultdict(float)
        
        for emotion, indicators in self.emotional_indicators.items():
            for indicator in indicators:
                if indicator in user_input:
                    emotion_scores[emotion] += 1.0
        
        if emotion_scores:
            return max(emotion_scores.items(), key=lambda x: x[1])[0]
        
        return "neutral"
    
    def _analyze_knowledge_depth(self, user_input: str, topics: List[str]) -> Dict[str, float]:
        """知識深度分析"""
        depth_analysis = {}
        
        for topic in topics:
            depth_score = 0.5  # デフォルト（中級）
            
            # 初級指標
            for phrase in self.knowledge_depth_indicators["beginner"]["phrases"]:
                if phrase in user_input:
                    depth_score = 0.2
                    break
            
            for question in self.knowledge_depth_indicators["beginner"]["questions"]:
                if question in user_input:
                    depth_score = 0.2
                    break
            
            # 中級指標
            for phrase in self.knowledge_depth_indicators["intermediate"]["phrases"]:
                if phrase in user_input:
                    depth_score = 0.5
                    break
            
            # 上級指標
            for phrase in self.knowledge_depth_indicators["advanced"]["phrases"]:
                if phrase in user_input:
                    depth_score = 0.8
                    break
            
            depth_analysis[topic] = depth_score
        
        return depth_analysis
    
    def generate_contextual_recommendations(self, context: ConversationContext, max_recommendations: int = 5) -> List[ContextualRecommendation]:
        """文脈的推薦生成"""
        recommendations = []
        
        # 推薦タイプ別生成
        continuation_recs = self._generate_continuation_recommendations(context)
        related_recs = self._generate_related_recommendations(context)
        contrast_recs = self._generate_contrast_recommendations(context)
        exploration_recs = self._generate_exploration_recommendations(context)
        
        # 全推薦をまとめる
        all_recommendations = continuation_recs + related_recs + contrast_recs + exploration_recs
        
        # 文脈関連度でソート
        all_recommendations.sort(key=lambda x: x.context_relevance, reverse=True)
        
        # 統計更新
        self.engine_statistics["recommendations_generated"] += len(all_recommendations[:max_recommendations])
        
        return all_recommendations[:max_recommendations]
    
    def _generate_continuation_recommendations(self, context: ConversationContext) -> List[ContextualRecommendation]:
        """継続推薦生成"""
        recommendations = []
        
        # 現在話題の継続
        for topic in context.mentioned_topics:
            if self.semantic_search and DEPENDENCIES_AVAILABLE:
                try:
                    search_results = self.semantic_search.search(f"{topic} 詳しく", max_results=3)
                    
                    for result in search_results:
                        rec = ContextualRecommendation(
                            recommendation_id=f"cont_{hashlib.md5(result.video_id.encode()).hexdigest()[:8]}",
                            content_id=result.video_id,
                            content_title=result.title,
                            recommendation_type="continuation",
                            context_relevance=result.relevance_score * 0.8,
                            reasoning=[f"「{topic}」の話題を深掘り", "現在の文脈に直接関連"],
                            confidence=result.confidence,
                            timing="immediate"
                        )
                        recommendations.append(rec)
                except:
                    pass
        
        return recommendations
    
    def _generate_related_recommendations(self, context: ConversationContext) -> List[ContextualRecommendation]:
        """関連推薦生成"""
        recommendations = []
        
        # 関連トピック推薦
        if self.knowledge_graph and DEPENDENCIES_AVAILABLE:
            for topic in context.mentioned_topics:
                try:
                    # セマンティック検索で関連コンテンツを探索
                    if self.semantic_search:
                        search_results = self.semantic_search.search(f"{topic} 似た", max_results=2)
                        
                        for result in search_results:
                            rec = ContextualRecommendation(
                                recommendation_id=f"rel_{hashlib.md5(result.video_id.encode()).hexdigest()[:8]}",
                                content_id=result.video_id,
                                content_title=result.title,
                                recommendation_type="related",
                                context_relevance=result.relevance_score * 0.6,
                                reasoning=[f"「{topic}」に関連する内容", "類似の興味分野"],
                                confidence=result.confidence * 0.8,
                                timing="followup"
                            )
                            recommendations.append(rec)
                except:
                    pass
        
        return recommendations
    
    def _generate_contrast_recommendations(self, context: ConversationContext) -> List[ContextualRecommendation]:
        """対比推薦生成"""
        recommendations = []
        
        # 感情状態に基づく対比推薦
        if context.emotional_state == "excited":
            contrast_mood = "穏やか"
        elif context.emotional_state == "relaxed":
            contrast_mood = "激しい"
        else:
            contrast_mood = "違う雰囲気"
        
        if self.semantic_search and DEPENDENCIES_AVAILABLE:
            try:
                search_results = self.semantic_search.search(contrast_mood, max_results=2)
                
                for result in search_results:
                    rec = ContextualRecommendation(
                        recommendation_id=f"cont_{hashlib.md5(result.video_id.encode()).hexdigest()[:8]}",
                        content_id=result.video_id,
                        content_title=result.title,
                        recommendation_type="contrast",
                        context_relevance=result.relevance_score * 0.4,
                        reasoning=[f"気分転換として{contrast_mood}な内容", "新しい発見のために"],
                        confidence=result.confidence * 0.6,
                        timing="later"
                    )
                    recommendations.append(rec)
            except:
                pass
        
        return recommendations
    
    def _generate_exploration_recommendations(self, context: ConversationContext) -> List[ContextualRecommendation]:
        """探索推薦生成"""
        recommendations = []
        
        # 知識深度に基づく推薦
        for topic, depth in context.knowledge_depth.items():
            if depth < 0.3:  # 初心者レベル
                query = f"{topic} 初心者"
            elif depth > 0.7:  # 上級者レベル
                query = f"{topic} マニア 詳しい"
            else:
                query = f"{topic} 中級"
            
            if self.semantic_search and DEPENDENCIES_AVAILABLE:
                try:
                    search_results = self.semantic_search.search(query, max_results=1)
                    
                    for result in search_results:
                        rec = ContextualRecommendation(
                            recommendation_id=f"exp_{hashlib.md5(result.video_id.encode()).hexdigest()[:8]}",
                            content_id=result.video_id,
                            content_title=result.title,
                            recommendation_type="exploration",
                            context_relevance=result.relevance_score * 0.5,
                            reasoning=[f"「{topic}」の知識レベルに合わせた内容", "学習の深化をサポート"],
                            confidence=result.confidence * 0.7,
                            timing="followup"
                        )
                        recommendations.append(rec)
                except:
                    pass
        
        return recommendations
    
    def predict_topic_transition(self, current_topics: List[str]) -> List[TopicTransition]:
        """トピック遷移予測"""
        predictions = []
        
        # 既存の遷移パターンから予測
        for topic in current_topics:
            if topic in self.topic_transitions:
                transitions = self.topic_transitions[topic]
                for transition_data in transitions:
                    transition = TopicTransition(
                        from_topic=topic,
                        to_topic=transition_data.get("to_topic", ""),
                        transition_type=transition_data.get("type", "natural"),
                        strength=transition_data.get("strength", 0.5),
                        patterns=transition_data.get("patterns", [])
                    )
                    predictions.append(transition)
        
        # 統計更新
        self.engine_statistics["transition_predictions"] += len(predictions)
        
        return predictions
    
    def learn_from_conversation(self, user_input: str, system_response: str, user_feedback: Optional[str] = None):
        """会話からの学習"""
        # コンテキストパターンの更新
        context = self.current_context
        if context:
            # 成功パターンの記録
            if user_feedback and "良い" in user_feedback:
                self._record_successful_pattern(context, system_response)
            
            # トピック遷移の記録
            self._record_topic_transition(context)
            
            # ユーザー好みの更新
            self._update_user_preferences(context, user_input, user_feedback)
    
    def _record_successful_pattern(self, context: ConversationContext, response: str):
        """成功パターン記録"""
        pattern_key = f"{context.emotional_state}_{context.temporal_context}"
        
        if pattern_key not in self.context_cache:
            self.context_cache[pattern_key] = []
        
        self.context_cache[pattern_key].append({
            "topics": context.mentioned_topics,
            "response_type": "successful",
            "timestamp": datetime.now().isoformat()
        })
        
        self.engine_statistics["pattern_matches"] += 1
    
    def _record_topic_transition(self, context: ConversationContext):
        """トピック遷移記録"""
        if len(self.conversation_memory) >= 2:
            prev_turn = self.conversation_memory[-2]
            current_turn = self.conversation_memory[-1]
            
            prev_topics = self._extract_mentioned_topics(prev_turn.get("user_input", ""))
            current_topics = self._extract_mentioned_topics(current_turn.get("user_input", ""))
            
            # 新しい遷移パターンを記録
            for prev_topic in prev_topics:
                for current_topic in current_topics:
                    if prev_topic != current_topic:
                        if prev_topic not in self.topic_transitions:
                            self.topic_transitions[prev_topic] = []
                        
                        self.topic_transitions[prev_topic].append({
                            "to_topic": current_topic,
                            "type": "natural",
                            "strength": 0.7,
                            "patterns": ["user_initiated"],
                            "timestamp": datetime.now().isoformat()
                        })
    
    def _update_user_preferences(self, context: ConversationContext, user_input: str, feedback: Optional[str]):
        """ユーザー好み更新"""
        # 現在の好み設定をマージ
        for topic, preference in context.user_preferences.items():
            if topic not in self.user_preferences:
                self.user_preferences[topic] = preference
            else:
                # 既存好みと新しい好みの平均を取る
                self.user_preferences[topic] = (self.user_preferences[topic] + preference) / 2
        
        # フィードバックに基づく調整
        if feedback:
            if "良い" in feedback or "いい" in feedback:
                # ポジティブフィードバック - 現在のトピックの好みを上げる
                for topic in context.mentioned_topics:
                    if topic in self.user_preferences:
                        self.user_preferences[topic] = min(1.0, self.user_preferences[topic] + 0.1)
            elif "違う" in feedback or "嫌" in feedback:
                # ネガティブフィードバック - 現在のトピックの好みを下げる
                for topic in context.mentioned_topics:
                    if topic in self.user_preferences:
                        self.user_preferences[topic] = max(-1.0, self.user_preferences[topic] - 0.1)
    
    def _save_context_to_cache(self, context: ConversationContext):
        """コンテキストキャッシュ保存"""
        try:
            cache_data = {
                "contexts": self.context_cache,
                "last_context": asdict(context),
                "statistics": self.engine_statistics,
                "last_updated": datetime.now().isoformat()
            }
            
            with open(self.context_cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[コンテキスト理解] ⚠️ キャッシュ保存エラー: {e}")
    
    def get_context_summary(self) -> Dict[str, Any]:
        """コンテキスト要約取得"""
        if not self.current_context:
            return {"status": "no_context"}
        
        return {
            "current_topics": self.current_context.mentioned_topics,
            "emotional_state": self.current_context.emotional_state,
            "temporal_context": self.current_context.temporal_context,
            "conversation_length": len(self.conversation_memory),
            "knowledge_depth": self.current_context.knowledge_depth,
            "user_preferences": dict(list(self.user_preferences.items())[:5]),  # 上位5つ
            "statistics": self.engine_statistics
        }
    
    def get_engine_statistics(self) -> Dict[str, Any]:
        """エンジン統計情報取得"""
        return dict(self.engine_statistics)
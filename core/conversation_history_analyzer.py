#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
会話履歴分析システム - Phase 2D実装
ユーザーの発話パターン・好み・興味変遷を深度分析
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
from datetime import datetime, timedelta
import re
import hashlib
from statistics import mean, median, stdev

# プロジェクトルートをパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Windowsパス設定
if os.name == 'nt':
    DATA_DIR = Path("D:/setsuna_bot/data")
    ANALYSIS_CACHE_DIR = Path("D:/setsuna_bot/conversation_analysis_cache")
else:
    DATA_DIR = Path("/mnt/d/setsuna_bot/data")
    ANALYSIS_CACHE_DIR = Path("/mnt/d/setsuna_bot/conversation_analysis_cache")

ANALYSIS_CACHE_DIR.mkdir(parents=True, exist_ok=True)

@dataclass
class ConversationPattern:
    """会話パターンデータクラス"""
    pattern_id: str
    pattern_type: str  # "temporal", "topic_sequence", "emotional_flow", "question_style"
    frequency: int
    pattern_description: str
    example_sequences: List[str]
    confidence_score: float
    discovered_at: str

@dataclass
class UserBehaviorProfile:
    """ユーザー行動プロファイルデータクラス"""
    profile_id: str
    conversation_style: Dict[str, float]  # "exploratory", "focused", "casual", "analytical"
    topic_preferences: Dict[str, float]   # トピック別好み度
    engagement_patterns: Dict[str, Any]   # エンゲージメントパターン
    temporal_activity: Dict[str, int]     # 時間帯別活動パターン
    learning_progression: Dict[str, List[float]]  # 知識習得の進歩
    interaction_complexity: float         # 対話の複雑さレベル
    last_updated: str

@dataclass
class TopicEvolution:
    """トピック進化データクラス"""
    topic: str
    timeline: List[Dict[str, Any]]  # 時系列での言及・関心変化
    interest_trajectory: List[float]  # 興味レベルの軌跡
    context_associations: Dict[str, float]  # 他トピックとの関連性
    learning_milestones: List[str]    # 学習マイルストーン
    prediction_trend: str             # "increasing", "stable", "decreasing", "cyclical"

class ConversationHistoryAnalyzer:
    """会話履歴分析システムクラス"""
    
    def __init__(self):
        """初期化"""
        self.multi_turn_conversations_path = DATA_DIR / "multi_turn_conversations.json"
        self.video_conversation_history_path = DATA_DIR / "video_conversation_history.json"
        self.user_preferences_path = DATA_DIR / "user_preferences.json"
        self.activity_sessions_dir = DATA_DIR / "activity_knowledge" / "sessions"
        
        # 分析結果保存パス
        self.conversation_patterns_path = ANALYSIS_CACHE_DIR / "conversation_patterns.json"
        self.user_behavior_profile_path = ANALYSIS_CACHE_DIR / "user_behavior_profile.json"
        self.topic_evolution_path = ANALYSIS_CACHE_DIR / "topic_evolution.json"
        self.analysis_history_path = ANALYSIS_CACHE_DIR / "analysis_history.json"
        
        # データ
        self.multi_turn_data = {}
        self.video_conversation_data = {}
        self.user_preferences = {}
        self.activity_sessions = []
        
        # 分析結果
        self.conversation_patterns = {}
        self.user_behavior_profile = None
        self.topic_evolution = {}
        self.analysis_history = []
        
        # 分析パラメータ
        self.min_pattern_frequency = 3  # パターン検出最小頻度
        self.topic_keywords = self._build_topic_keywords()
        self.emotional_indicators = self._build_emotional_indicators()
        self.complexity_indicators = self._build_complexity_indicators()
        
        # 統計情報
        self.analysis_statistics = {
            "total_conversations": 0,
            "total_turns": 0,
            "unique_topics": 0,
            "patterns_discovered": 0,
            "analysis_coverage": 0.0,
            "last_analysis": None
        }
        
        self._load_conversation_data()
        self._load_existing_analysis()
        
        print("[会話履歴分析] ✅ 会話履歴分析システム初期化完了")
    
    def _build_topic_keywords(self) -> Dict[str, List[str]]:
        """トピックキーワード辞書構築"""
        return {
            "音楽": ["音楽", "曲", "歌", "ミュージック", "サウンド", "楽曲", "メロディ", "リズム"],
            "動画": ["動画", "映像", "ビデオ", "コンテンツ", "チャンネル", "配信", "ストリーム"],
            "アニメ": ["アニメ", "アニメーション", "漫画", "マンガ", "二次元", "キャラクター"],
            "ゲーム": ["ゲーム", "プレイ", "実況", "ゲーミング", "プレイヤー", "ストリーマー"],
            "技術": ["技術", "テクノロジー", "プログラミング", "コード", "開発", "AI", "システム"],
            "創作": ["創作", "制作", "クリエイティブ", "アート", "デザイン", "作品", "表現"],
            "学習": ["学習", "勉強", "教育", "知識", "理解", "習得", "スキル", "能力"],
            "娯楽": ["娯楽", "エンターテイメント", "楽しい", "面白い", "趣味", "レジャー"],
            "感情": ["感情", "気持ち", "心", "感動", "興奮", "リラックス", "癒し", "ストレス"],
            "社会": ["社会", "コミュニティ", "人間関係", "交流", "コミュニケーション", "友達"]
        }
    
    def _build_emotional_indicators(self) -> Dict[str, List[str]]:
        """感情指標構築"""
        return {
            "positive": ["嬉しい", "楽しい", "面白い", "素晴らしい", "最高", "良い", "好き", "気に入った"],
            "negative": ["悲しい", "つまらない", "嫌い", "苦手", "残念", "がっかり", "いまいち"],
            "excited": ["わくわく", "テンション", "興奮", "熱い", "盛り上がる", "エキサイト"],
            "curious": ["気になる", "興味深い", "面白そう", "知りたい", "どんな", "なぜ"],
            "calm": ["落ち着く", "癒し", "穏やか", "リラックス", "のんびり", "ゆっくり"],
            "confused": ["分からない", "難しい", "複雑", "混乱", "理解できない", "よく分からない"]
        }
    
    def _build_complexity_indicators(self) -> Dict[str, List[str]]:
        """複雑さ指標構築"""
        return {
            "simple": ["簡単", "分かりやすい", "基本", "初歩", "入門", "シンプル"],
            "moderate": ["普通", "一般的", "標準", "中級", "適度", "バランス"],
            "complex": ["複雑", "詳細", "高度", "専門", "上級", "マニアック", "深い"]
        }
    
    def _load_conversation_data(self):
        """会話データロード"""
        # マルチターン会話データ
        try:
            if self.multi_turn_conversations_path.exists():
                with open(self.multi_turn_conversations_path, 'r', encoding='utf-8') as f:
                    self.multi_turn_data = json.load(f)
                print(f"[会話履歴分析] 📊 マルチターン会話データをロード")
        except Exception as e:
            print(f"[会話履歴分析] ⚠️ マルチターン会話データロードエラー: {e}")
        
        # 動画会話履歴
        try:
            if self.video_conversation_history_path.exists():
                with open(self.video_conversation_history_path, 'r', encoding='utf-8') as f:
                    self.video_conversation_data = json.load(f)
                print(f"[会話履歴分析] 📊 動画会話履歴をロード")
        except Exception as e:
            print(f"[会話履歴分析] ⚠️ 動画会話履歴ロードエラー: {e}")
        
        # ユーザー好み
        try:
            if self.user_preferences_path.exists():
                with open(self.user_preferences_path, 'r', encoding='utf-8') as f:
                    self.user_preferences = json.load(f)
                print(f"[会話履歴分析] 📊 ユーザー好みデータをロード")
        except Exception as e:
            print(f"[会話履歴分析] ⚠️ ユーザー好みロードエラー: {e}")
        
        # アクティビティセッション
        try:
            if self.activity_sessions_dir.exists():
                for session_file in self.activity_sessions_dir.glob("*.json"):
                    try:
                        with open(session_file, 'r', encoding='utf-8') as f:
                            session_data = json.load(f)
                            self.activity_sessions.append(session_data)
                    except:
                        continue
                print(f"[会話履歴分析] 📊 {len(self.activity_sessions)}件のアクティビティセッションをロード")
        except Exception as e:
            print(f"[会話履歴分析] ⚠️ アクティビティセッションロードエラー: {e}")
    
    def _load_existing_analysis(self):
        """既存分析結果ロード"""
        try:
            if self.conversation_patterns_path.exists():
                with open(self.conversation_patterns_path, 'r', encoding='utf-8') as f:
                    patterns_data = json.load(f)
                    self.conversation_patterns = {
                        pid: ConversationPattern(**pattern) 
                        for pid, pattern in patterns_data.get("patterns", {}).items()
                    }
        except Exception as e:
            print(f"[会話履歴分析] ⚠️ 会話パターンロードエラー: {e}")
        
        try:
            if self.user_behavior_profile_path.exists():
                with open(self.user_behavior_profile_path, 'r', encoding='utf-8') as f:
                    profile_data = json.load(f)
                    self.user_behavior_profile = UserBehaviorProfile(**profile_data)
        except Exception as e:
            print(f"[会話履歴分析] ⚠️ ユーザー行動プロファイルロードエラー: {e}")
        
        try:
            if self.topic_evolution_path.exists():
                with open(self.topic_evolution_path, 'r', encoding='utf-8') as f:
                    evolution_data = json.load(f)
                    self.topic_evolution = {
                        topic: TopicEvolution(**data) 
                        for topic, data in evolution_data.get("evolutions", {}).items()
                    }
        except Exception as e:
            print(f"[会話履歴分析] ⚠️ トピック進化データロードエラー: {e}")
    
    def analyze_conversation_patterns(self) -> Dict[str, ConversationPattern]:
        """会話パターン分析"""
        print("[会話履歴分析] 🔍 会話パターンを分析中...")
        
        patterns = {}
        
        # マルチターン会話からパターン抽出
        patterns.update(self._analyze_turn_patterns())
        
        # トピック遷移パターン
        patterns.update(self._analyze_topic_transition_patterns())
        
        # 感情フローパターン
        patterns.update(self._analyze_emotional_flow_patterns())
        
        # 質問スタイルパターン
        patterns.update(self._analyze_question_style_patterns())
        
        # 時間的パターン
        patterns.update(self._analyze_temporal_patterns())
        
        self.conversation_patterns = patterns
        self._save_conversation_patterns()
        
        print(f"[会話履歴分析] ✅ {len(patterns)}個の会話パターンを発見")
        return patterns
    
    def _analyze_turn_patterns(self) -> Dict[str, ConversationPattern]:
        """ターンパターン分析"""
        patterns = {}
        turn_sequences = []
        
        # マルチターン会話からシーケンス抽出
        if "current_session" in self.multi_turn_data:
            turns = self.multi_turn_data["current_session"].get("turns", [])
            for i in range(len(turns) - 2):
                sequence = []
                for j in range(3):  # 3ターンシーケンス
                    if i + j < len(turns):
                        turn = turns[i + j]
                        turn_type = self._classify_turn_type(turn.get("user_input", ""))
                        sequence.append(turn_type)
                if len(sequence) == 3:
                    turn_sequences.append("->".join(sequence))
        
        # パターン頻度カウント
        sequence_counts = Counter(turn_sequences)
        
        for sequence, count in sequence_counts.items():
            if count >= self.min_pattern_frequency:
                pattern_id = f"turn_pattern_{hashlib.md5(sequence.encode()).hexdigest()[:8]}"
                patterns[pattern_id] = ConversationPattern(
                    pattern_id=pattern_id,
                    pattern_type="turn_sequence",
                    frequency=count,
                    pattern_description=f"ターンシーケンス: {sequence}",
                    example_sequences=[sequence],
                    confidence_score=min(1.0, count / 10),
                    discovered_at=datetime.now().isoformat()
                )
        
        return patterns
    
    def _classify_turn_type(self, user_input: str) -> str:
        """ターンタイプ分類"""
        if not user_input:
            return "empty"
        
        # 質問
        if "?" in user_input or any(word in user_input for word in ["何", "どう", "なぜ", "いつ", "どこ", "誰"]):
            return "question"
        
        # 感想・評価
        if any(word in user_input for word in ["思う", "感じ", "好き", "嫌い", "良い", "悪い"]):
            return "opinion"
        
        # 要求・依頼
        if any(word in user_input for word in ["して", "教えて", "見せて", "聞かせて", "探して"]):
            return "request"
        
        # 情報提供
        if any(word in user_input for word in ["です", "である", "だった", "について"]):
            return "information"
        
        # その他
        return "general"
    
    def _analyze_topic_transition_patterns(self) -> Dict[str, ConversationPattern]:
        """トピック遷移パターン分析"""
        patterns = {}
        topic_transitions = []
        
        # セッション内のトピック遷移抽出
        for session in self.activity_sessions:
            session_topics = []
            
            # セッション内の話題抽出
            if "context" in session:
                context = session["context"]
                for topic_category, keywords in self.topic_keywords.items():
                    if any(keyword in str(context) for keyword in keywords):
                        session_topics.append(topic_category)
            
            # 遷移パターン作成
            for i in range(len(session_topics) - 1):
                transition = f"{session_topics[i]}->{session_topics[i+1]}"
                topic_transitions.append(transition)
        
        # パターン頻度分析
        transition_counts = Counter(topic_transitions)
        
        for transition, count in transition_counts.items():
            if count >= self.min_pattern_frequency:
                pattern_id = f"topic_transition_{hashlib.md5(transition.encode()).hexdigest()[:8]}"
                patterns[pattern_id] = ConversationPattern(
                    pattern_id=pattern_id,
                    pattern_type="topic_sequence",
                    frequency=count,
                    pattern_description=f"トピック遷移: {transition}",
                    example_sequences=[transition],
                    confidence_score=min(1.0, count / 5),
                    discovered_at=datetime.now().isoformat()
                )
        
        return patterns
    
    def _analyze_emotional_flow_patterns(self) -> Dict[str, ConversationPattern]:
        """感情フローパターン分析"""
        patterns = {}
        emotional_sequences = []
        
        # マルチターン会話から感情シーケンス抽出
        if "current_session" in self.multi_turn_data:
            turns = self.multi_turn_data["current_session"].get("turns", [])
            emotions = []
            
            for turn in turns:
                user_input = turn.get("user_input", "")
                emotion = self._detect_emotion(user_input)
                emotions.append(emotion)
            
            # 感情遷移パターン作成
            for i in range(len(emotions) - 2):
                if i + 2 < len(emotions):
                    sequence = f"{emotions[i]}->{emotions[i+1]}->{emotions[i+2]}"
                    emotional_sequences.append(sequence)
        
        # パターン頻度分析
        emotion_counts = Counter(emotional_sequences)
        
        for sequence, count in emotion_counts.items():
            if count >= self.min_pattern_frequency:
                pattern_id = f"emotion_flow_{hashlib.md5(sequence.encode()).hexdigest()[:8]}"
                patterns[pattern_id] = ConversationPattern(
                    pattern_id=pattern_id,
                    pattern_type="emotional_flow",
                    frequency=count,
                    pattern_description=f"感情フロー: {sequence}",
                    example_sequences=[sequence],
                    confidence_score=min(1.0, count / 3),
                    discovered_at=datetime.now().isoformat()
                )
        
        return patterns
    
    def _detect_emotion(self, text: str) -> str:
        """感情検出"""
        if not text:
            return "neutral"
        
        emotion_scores = defaultdict(int)
        
        for emotion, indicators in self.emotional_indicators.items():
            for indicator in indicators:
                if indicator in text:
                    emotion_scores[emotion] += 1
        
        if emotion_scores:
            return max(emotion_scores.items(), key=lambda x: x[1])[0]
        
        return "neutral"
    
    def _analyze_question_style_patterns(self) -> Dict[str, ConversationPattern]:
        """質問スタイルパターン分析"""
        patterns = {}
        question_styles = []
        
        # マルチターン会話から質問スタイル抽出
        if "current_session" in self.multi_turn_data:
            turns = self.multi_turn_data["current_session"].get("turns", [])
            
            for turn in turns:
                user_input = turn.get("user_input", "")
                if "?" in user_input or any(qword in user_input for qword in ["何", "どう", "なぜ"]):
                    style = self._classify_question_style(user_input)
                    question_styles.append(style)
        
        # パターン頻度分析
        style_counts = Counter(question_styles)
        
        for style, count in style_counts.items():
            if count >= self.min_pattern_frequency:
                pattern_id = f"question_style_{hashlib.md5(style.encode()).hexdigest()[:8]}"
                patterns[pattern_id] = ConversationPattern(
                    pattern_id=pattern_id,
                    pattern_type="question_style",
                    frequency=count,
                    pattern_description=f"質問スタイル: {style}",
                    example_sequences=[style],
                    confidence_score=min(1.0, count / 5),
                    discovered_at=datetime.now().isoformat()
                )
        
        return patterns
    
    def _classify_question_style(self, text: str) -> str:
        """質問スタイル分類"""
        if "何" in text:
            return "what_question"
        elif "どう" in text or "どのよう" in text:
            return "how_question"
        elif "なぜ" in text or "どうして" in text:
            return "why_question"
        elif "いつ" in text:
            return "when_question"
        elif "どこ" in text:
            return "where_question"
        elif "誰" in text:
            return "who_question"
        else:
            return "general_question"
    
    def _analyze_temporal_patterns(self) -> Dict[str, ConversationPattern]:
        """時間的パターン分析"""
        patterns = {}
        
        # セッション時間分析
        session_times = []
        for session in self.activity_sessions:
            if "timestamp" in session:
                try:
                    timestamp = datetime.fromisoformat(session["timestamp"])
                    hour = timestamp.hour
                    session_times.append(hour)
                except:
                    continue
        
        if session_times:
            # 時間帯パターン分析
            hour_counts = Counter(session_times)
            most_active_hours = hour_counts.most_common(3)
            
            for hour, count in most_active_hours:
                if count >= 3:
                    time_category = self._get_time_category(hour)
                    pattern_id = f"temporal_{time_category}_{hour}"
                    patterns[pattern_id] = ConversationPattern(
                        pattern_id=pattern_id,
                        pattern_type="temporal",
                        frequency=count,
                        pattern_description=f"{time_category}の活動 ({hour}時頃)",
                        example_sequences=[f"{hour}:00"],
                        confidence_score=min(1.0, count / 10),
                        discovered_at=datetime.now().isoformat()
                    )
        
        return patterns
    
    def _get_time_category(self, hour: int) -> str:
        """時間カテゴリ取得"""
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 18:
            return "afternoon"
        elif 18 <= hour < 22:
            return "evening"
        else:
            return "night"
    
    def create_user_behavior_profile(self) -> UserBehaviorProfile:
        """ユーザー行動プロファイル作成"""
        print("[会話履歴分析] 👤 ユーザー行動プロファイルを作成中...")
        
        # 会話スタイル分析
        conversation_style = self._analyze_conversation_style()
        
        # トピック好み分析
        topic_preferences = self._analyze_topic_preferences()
        
        # エンゲージメントパターン分析
        engagement_patterns = self._analyze_engagement_patterns()
        
        # 時間的活動パターン分析
        temporal_activity = self._analyze_temporal_activity()
        
        # 学習進歩分析
        learning_progression = self._analyze_learning_progression()
        
        # 対話複雑さ分析
        interaction_complexity = self._analyze_interaction_complexity()
        
        profile = UserBehaviorProfile(
            profile_id=f"user_profile_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            conversation_style=conversation_style,
            topic_preferences=topic_preferences,
            engagement_patterns=engagement_patterns,
            temporal_activity=temporal_activity,
            learning_progression=learning_progression,
            interaction_complexity=interaction_complexity,
            last_updated=datetime.now().isoformat()
        )
        
        self.user_behavior_profile = profile
        self._save_user_behavior_profile()
        
        print("[会話履歴分析] ✅ ユーザー行動プロファイル作成完了")
        return profile
    
    def _analyze_conversation_style(self) -> Dict[str, float]:
        """会話スタイル分析"""
        style_scores = {
            "exploratory": 0.0,
            "focused": 0.0,
            "casual": 0.0,
            "analytical": 0.0
        }
        
        total_inputs = 0
        
        # マルチターン会話分析
        if "current_session" in self.multi_turn_data:
            turns = self.multi_turn_data["current_session"].get("turns", [])
            
            for turn in turns:
                user_input = turn.get("user_input", "")
                if user_input:
                    total_inputs += 1
                    
                    # 探索的スタイル
                    if any(word in user_input for word in ["何か", "他に", "もっと", "色々", "いろんな"]):
                        style_scores["exploratory"] += 1
                    
                    # 集中的スタイル
                    if any(word in user_input for word in ["詳しく", "具体的", "深く", "専門", "集中"]):
                        style_scores["focused"] += 1
                    
                    # カジュアルスタイル
                    if any(word in user_input for word in ["なんか", "ちょっと", "まあ", "けっこう"]):
                        style_scores["casual"] += 1
                    
                    # 分析的スタイル
                    if any(word in user_input for word in ["なぜ", "理由", "分析", "比較", "評価", "考察"]):
                        style_scores["analytical"] += 1
        
        # 正規化
        if total_inputs > 0:
            for style in style_scores:
                style_scores[style] = style_scores[style] / total_inputs
        
        return style_scores
    
    def _analyze_topic_preferences(self) -> Dict[str, float]:
        """トピック好み分析"""
        topic_mentions = defaultdict(int)
        topic_positive_mentions = defaultdict(int)
        
        # マルチターン会話からトピック言及抽出
        if "current_session" in self.multi_turn_data:
            turns = self.multi_turn_data["current_session"].get("turns", [])
            
            for turn in turns:
                user_input = turn.get("user_input", "")
                emotion = self._detect_emotion(user_input)
                
                for topic_category, keywords in self.topic_keywords.items():
                    for keyword in keywords:
                        if keyword in user_input:
                            topic_mentions[topic_category] += 1
                            if emotion in ["positive", "excited", "curious"]:
                                topic_positive_mentions[topic_category] += 1
        
        # 好み度計算
        preferences = {}
        for topic in topic_mentions:
            total_mentions = topic_mentions[topic]
            positive_mentions = topic_positive_mentions[topic]
            
            if total_mentions > 0:
                preference_score = positive_mentions / total_mentions
                preferences[topic] = preference_score
        
        return preferences
    
    def _analyze_engagement_patterns(self) -> Dict[str, Any]:
        """エンゲージメントパターン分析"""
        patterns = {
            "average_session_length": 0,
            "questions_per_session": 0,
            "topic_switches_per_session": 0,
            "response_elaboration": 0.0,
            "follow_up_frequency": 0.0
        }
        
        # セッション長分析
        session_lengths = []
        session_questions = []
        
        if "current_session" in self.multi_turn_data:
            turns = self.multi_turn_data["current_session"].get("turns", [])
            session_lengths.append(len(turns))
            
            question_count = 0
            for turn in turns:
                user_input = turn.get("user_input", "")
                if "?" in user_input or any(qword in user_input for qword in ["何", "どう", "なぜ"]):
                    question_count += 1
            session_questions.append(question_count)
        
        # 統計計算
        if session_lengths:
            patterns["average_session_length"] = mean(session_lengths)
        if session_questions:
            patterns["questions_per_session"] = mean(session_questions)
        
        return patterns
    
    def _analyze_temporal_activity(self) -> Dict[str, int]:
        """時間的活動パターン分析"""
        activity = defaultdict(int)
        
        # セッション時間分析
        for session in self.activity_sessions:
            if "timestamp" in session:
                try:
                    timestamp = datetime.fromisoformat(session["timestamp"])
                    hour = timestamp.hour
                    time_category = self._get_time_category(hour)
                    activity[time_category] += 1
                except:
                    continue
        
        return dict(activity)
    
    def _analyze_learning_progression(self) -> Dict[str, List[float]]:
        """学習進歩分析"""
        progression = defaultdict(list)
        
        # トピック別の複雑さレベル推移
        for session in self.activity_sessions:
            if "context" in session and "timestamp" in session:
                context = str(session["context"])
                
                for topic_category, keywords in self.topic_keywords.items():
                    if any(keyword in context for keyword in keywords):
                        complexity = self._assess_context_complexity(context)
                        progression[topic_category].append(complexity)
        
        return dict(progression)
    
    def _assess_context_complexity(self, context: str) -> float:
        """コンテキスト複雑さ評価"""
        complexity_score = 0.0
        
        # 単語数による複雑さ
        word_count = len(context.split())
        complexity_score += min(1.0, word_count / 100) * 0.3
        
        # 専門用語による複雑さ
        for level, indicators in self.complexity_indicators.items():
            for indicator in indicators:
                if indicator in context:
                    if level == "simple":
                        complexity_score += 0.1
                    elif level == "moderate":
                        complexity_score += 0.5
                    elif level == "complex":
                        complexity_score += 0.9
        
        return min(1.0, complexity_score)
    
    def _analyze_interaction_complexity(self) -> float:
        """対話複雑さ分析"""
        complexity_scores = []
        
        if "current_session" in self.multi_turn_data:
            turns = self.multi_turn_data["current_session"].get("turns", [])
            
            for turn in turns:
                user_input = turn.get("user_input", "")
                if user_input:
                    complexity = self._assess_context_complexity(user_input)
                    complexity_scores.append(complexity)
        
        return mean(complexity_scores) if complexity_scores else 0.5
    
    def analyze_topic_evolution(self) -> Dict[str, TopicEvolution]:
        """トピック進化分析"""
        print("[会話履歴分析] 📈 トピック進化を分析中...")
        
        evolutions = {}
        
        # トピック別時系列分析
        for topic_category in self.topic_keywords.keys():
            evolution = self._analyze_single_topic_evolution(topic_category)
            if evolution:
                evolutions[topic_category] = evolution
        
        self.topic_evolution = evolutions
        self._save_topic_evolution()
        
        print(f"[会話履歴分析] ✅ {len(evolutions)}個のトピック進化を分析完了")
        return evolutions
    
    def _analyze_single_topic_evolution(self, topic: str) -> Optional[TopicEvolution]:
        """単一トピック進化分析"""
        keywords = self.topic_keywords.get(topic, [])
        if not keywords:
            return None
        
        timeline = []
        interest_trajectory = []
        context_associations = defaultdict(float)
        
        # セッション時系列でのトピック言及分析
        for session in sorted(self.activity_sessions, key=lambda s: s.get("timestamp", "")):
            context = str(session.get("context", ""))
            timestamp = session.get("timestamp", "")
            
            # トピック言及度
            mention_score = 0
            for keyword in keywords:
                if keyword in context:
                    mention_score += 1
            
            if mention_score > 0:
                # 興味レベル推定
                emotion = self._detect_emotion(context)
                if emotion in ["positive", "excited", "curious"]:
                    interest_level = 0.8
                elif emotion in ["neutral"]:
                    interest_level = 0.5
                else:
                    interest_level = 0.3
                
                timeline.append({
                    "timestamp": timestamp,
                    "mention_score": mention_score,
                    "interest_level": interest_level,
                    "context_summary": context[:100] + "..." if len(context) > 100 else context
                })
                
                interest_trajectory.append(interest_level)
                
                # 他トピックとの関連分析
                for other_topic, other_keywords in self.topic_keywords.items():
                    if other_topic != topic:
                        for other_keyword in other_keywords:
                            if other_keyword in context:
                                context_associations[other_topic] += 0.1
        
        if not timeline:
            return None
        
        # トレンド予測
        prediction_trend = self._predict_topic_trend(interest_trajectory)
        
        # 学習マイルストーン抽出
        milestones = self._extract_learning_milestones(timeline)
        
        return TopicEvolution(
            topic=topic,
            timeline=timeline,
            interest_trajectory=interest_trajectory,
            context_associations=dict(context_associations),
            learning_milestones=milestones,
            prediction_trend=prediction_trend
        )
    
    def _predict_topic_trend(self, trajectory: List[float]) -> str:
        """トピックトレンド予測"""
        if len(trajectory) < 3:
            return "stable"
        
        # 最近3ポイントの傾向
        recent = trajectory[-3:]
        
        if recent[-1] > recent[0] + 0.2:
            return "increasing"
        elif recent[-1] < recent[0] - 0.2:
            return "decreasing"
        elif max(recent) - min(recent) > 0.3:
            return "cyclical"
        else:
            return "stable"
    
    def _extract_learning_milestones(self, timeline: List[Dict]) -> List[str]:
        """学習マイルストーン抽出"""
        milestones = []
        
        if not timeline:
            return milestones
        
        # 最初の言及
        milestones.append(f"初回言及: {timeline[0]['timestamp']}")
        
        # 高い関心を示した時点
        for event in timeline:
            if event.get("interest_level", 0) > 0.7:
                milestones.append(f"高関心表示: {event['timestamp']}")
                break
        
        # 最近の活動
        if timeline:
            milestones.append(f"最新活動: {timeline[-1]['timestamp']}")
        
        return milestones[:5]  # 最大5つ
    
    def _save_conversation_patterns(self):
        """会話パターン保存"""
        try:
            patterns_data = {
                "patterns": {pid: asdict(pattern) for pid, pattern in self.conversation_patterns.items()},
                "metadata": {
                    "total_patterns": len(self.conversation_patterns),
                    "last_updated": datetime.now().isoformat()
                }
            }
            
            with open(self.conversation_patterns_path, 'w', encoding='utf-8') as f:
                json.dump(patterns_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[会話履歴分析] ⚠️ 会話パターン保存エラー: {e}")
    
    def _save_user_behavior_profile(self):
        """ユーザー行動プロファイル保存"""
        try:
            if self.user_behavior_profile:
                with open(self.user_behavior_profile_path, 'w', encoding='utf-8') as f:
                    json.dump(asdict(self.user_behavior_profile), f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[会話履歴分析] ⚠️ ユーザー行動プロファイル保存エラー: {e}")
    
    def _save_topic_evolution(self):
        """トピック進化保存"""
        try:
            evolution_data = {
                "evolutions": {topic: asdict(evolution) for topic, evolution in self.topic_evolution.items()},
                "metadata": {
                    "total_topics": len(self.topic_evolution),
                    "last_updated": datetime.now().isoformat()
                }
            }
            
            with open(self.topic_evolution_path, 'w', encoding='utf-8') as f:
                json.dump(evolution_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[会話履歴分析] ⚠️ トピック進化保存エラー: {e}")
    
    def perform_comprehensive_analysis(self) -> Dict[str, Any]:
        """包括的分析実行"""
        print("[会話履歴分析] 🔬 包括的分析を実行中...")
        
        # 統計更新
        self._update_statistics()
        
        # 各種分析実行
        patterns = self.analyze_conversation_patterns()
        profile = self.create_user_behavior_profile()
        evolutions = self.analyze_topic_evolution()
        
        # 分析履歴記録
        analysis_record = {
            "analysis_id": f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "patterns_count": len(patterns),
            "topics_analyzed": len(evolutions),
            "profile_created": profile is not None,
            "statistics": self.analysis_statistics
        }
        
        self.analysis_history.append(analysis_record)
        self._save_analysis_history()
        
        print("[会話履歴分析] ✅ 包括的分析完了")
        
        return {
            "patterns": patterns,
            "profile": profile,
            "evolutions": evolutions,
            "statistics": self.analysis_statistics,
            "analysis_record": analysis_record
        }
    
    def _update_statistics(self):
        """統計情報更新"""
        # 会話数カウント
        total_conversations = 0
        total_turns = 0
        
        if "current_session" in self.multi_turn_data:
            total_conversations = 1
            total_turns = len(self.multi_turn_data["current_session"].get("turns", []))
        
        total_conversations += len(self.activity_sessions)
        
        # 固有トピック数
        unique_topics = len(self.topic_evolution)
        
        # パターン数
        patterns_discovered = len(self.conversation_patterns)
        
        # カバレッジ率
        coverage_rate = min(1.0, total_conversations / 100) if total_conversations > 0 else 0.0
        
        self.analysis_statistics.update({
            "total_conversations": total_conversations,
            "total_turns": total_turns,
            "unique_topics": unique_topics,
            "patterns_discovered": patterns_discovered,
            "analysis_coverage": coverage_rate,
            "last_analysis": datetime.now().isoformat()
        })
    
    def _save_analysis_history(self):
        """分析履歴保存"""
        try:
            history_data = {
                "analysis_history": self.analysis_history,
                "last_updated": datetime.now().isoformat()
            }
            
            with open(self.analysis_history_path, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[会話履歴分析] ⚠️ 分析履歴保存エラー: {e}")
    
    def get_analysis_summary(self) -> Dict[str, Any]:
        """分析サマリー取得"""
        return {
            "statistics": self.analysis_statistics,
            "patterns_overview": {
                "total_patterns": len(self.conversation_patterns),
                "pattern_types": list(set(p.pattern_type for p in self.conversation_patterns.values()))
            },
            "profile_overview": {
                "profile_exists": self.user_behavior_profile is not None,
                "conversation_style": self.user_behavior_profile.conversation_style if self.user_behavior_profile else {},
                "top_topics": dict(list(self.user_behavior_profile.topic_preferences.items())[:5]) if self.user_behavior_profile else {}
            },
            "evolution_overview": {
                "topics_tracked": len(self.topic_evolution),
                "trending_topics": [topic for topic, evo in self.topic_evolution.items() if evo.prediction_trend == "increasing"]
            }
        }
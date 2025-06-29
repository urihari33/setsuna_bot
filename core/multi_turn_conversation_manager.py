#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
マルチターン会話管理システム - Phase 2-B-3
複数回の会話にわたる文脈保持と対話状態管理
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from enum import Enum
from collections import defaultdict

class ConversationState(Enum):
    """対話状態の定義"""
    INITIAL = "initial"           # 初期状態
    TOPIC_ESTABLISHED = "topic_established"  # 話題確立
    DEEP_DISCUSSION = "deep_discussion"      # 深い議論
    PREFERENCE_LEARNING = "preference_learning"  # 嗜好学習中
    RECOMMENDATION_MODE = "recommendation_mode"  # 推薦モード
    FOLLOWUP = "followup"         # フォローアップ
    TRANSITION = "transition"     # 話題転換

class MultiTurnConversationManager:
    """マルチターン会話を管理するクラス"""
    
    def __init__(self):
        """初期化"""
        # Windows環境とWSL2環境両方に対応
        if os.name == 'nt':  # Windows
            self.conversation_file = Path("D:/setsuna_bot/data/multi_turn_conversations.json")
        else:  # Linux/WSL2
            self.conversation_file = Path("/mnt/d/setsuna_bot/data/multi_turn_conversations.json")
        
        # 対話セッション管理
        self.current_session = {
            "session_id": self._generate_session_id(),
            "start_time": datetime.now().isoformat(),
            "state": ConversationState.INITIAL,
            "turns": [],
            "active_topics": {},
            "user_preferences": {},
            "conversation_goals": [],
            "emotional_trajectory": []
        }
        
        # 履歴セッション
        self.session_history = []
        
        # 設定
        self.config = {
            "max_turns_per_session": 20,
            "session_timeout_minutes": 60,
            "min_turns_for_deep_discussion": 3,
            "preference_confidence_threshold": 0.7,
            "state_transition_rules": self._define_state_transition_rules()
        }
        
        self._ensure_data_dir()
        self._load_conversation_history()
        
        print("[マルチターン] ✅ マルチターン会話管理システム初期化完了")
    
    def _ensure_data_dir(self):
        """データディレクトリの確保"""
        self.conversation_file.parent.mkdir(parents=True, exist_ok=True)
    
    def _generate_session_id(self) -> str:
        """セッションIDを生成"""
        return f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def _define_state_transition_rules(self) -> Dict[str, Any]:
        """状態遷移ルールを定義"""
        return {
            ConversationState.INITIAL: {
                "to_topic_established": {
                    "conditions": ["has_video_mention", "user_shows_interest"],
                    "min_confidence": 0.6
                },
                "to_recommendation_mode": {
                    "conditions": ["recommendation_request"],
                    "min_confidence": 0.8
                }
            },
            ConversationState.TOPIC_ESTABLISHED: {
                "to_deep_discussion": {
                    "conditions": ["multiple_questions", "detailed_interest"],
                    "min_turns": 2,
                    "min_confidence": 0.7
                },
                "to_preference_learning": {
                    "conditions": ["preference_signals", "emotional_response"],
                    "min_confidence": 0.6
                },
                "to_recommendation_mode": {
                    "conditions": ["recommendation_request", "similarity_request"],
                    "min_confidence": 0.8
                }
            },
            ConversationState.DEEP_DISCUSSION: {
                "to_preference_learning": {
                    "conditions": ["strong_preference_signals"],
                    "min_confidence": 0.8
                },
                "to_recommendation_mode": {
                    "conditions": ["user_satisfaction", "wants_more"],
                    "min_confidence": 0.7
                }
            },
            ConversationState.PREFERENCE_LEARNING: {
                "to_recommendation_mode": {
                    "conditions": ["sufficient_learning", "recommendation_opportunity"],
                    "min_confidence": 0.6
                }
            },
            ConversationState.RECOMMENDATION_MODE: {
                "to_followup": {
                    "conditions": ["recommendation_given", "awaiting_feedback"],
                    "min_confidence": 0.9
                }
            },
            ConversationState.FOLLOWUP: {
                "to_topic_established": {
                    "conditions": ["new_topic_interest"],
                    "min_confidence": 0.6
                },
                "to_recommendation_mode": {
                    "conditions": ["wants_more_recommendations"],
                    "min_confidence": 0.7
                },
                "to_transition": {
                    "conditions": ["topic_change_signals"],
                    "min_confidence": 0.5
                }
            }
        }
    
    def _load_conversation_history(self):
        """会話履歴の読み込み"""
        try:
            if self.conversation_file.exists():
                with open(self.conversation_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # 最近のセッション履歴のみロード
                    all_sessions = data.get('session_history', [])
                    recent_sessions = [
                        session for session in all_sessions
                        if self._is_recent_session(session.get('start_time'))
                    ]
                    self.session_history = recent_sessions
                    
                    print(f"[マルチターン] 📊 セッション履歴: {len(self.session_history)}件をロード")
            else:
                print("[マルチターン] 📝 新規会話履歴ファイルを作成")
                
        except Exception as e:
            print(f"[マルチターン] ⚠️ 会話履歴読み込み失敗: {e}")
            self.session_history = []
    
    def _is_recent_session(self, start_time_str: str) -> bool:
        """セッションが最近のものかチェック"""
        if not start_time_str:
            return False
        
        try:
            start_time = datetime.fromisoformat(start_time_str)
            now = datetime.now()
            return now - start_time < timedelta(days=7)  # 1週間以内
        except:
            return False
    
    def _save_conversation_history(self):
        """会話履歴の保存"""
        try:
            data = {
                'current_session': self._serialize_session(self.current_session),
                'session_history': [self._serialize_session(session) for session in self.session_history],
                'config': {
                    key: value for key, value in self.config.items() 
                    if key != 'state_transition_rules'  # Enumは除外
                },
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.conversation_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"[マルチターン] ❌ 会話履歴保存失敗: {e}")
    
    def _serialize_session(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """セッションをシリアライズ可能な形式に変換"""
        serialized = {}
        
        for key, value in session.items():
            if key == 'state' and isinstance(value, ConversationState):
                serialized[key] = value.value
            elif key == 'turns':
                # ターンデータの詳細シリアライゼーション
                serialized[key] = []
                for turn in value:
                    serialized_turn = {}
                    for turn_key, turn_value in turn.items():
                        if turn_key == 'new_state' and isinstance(turn_value, ConversationState):
                            serialized_turn[turn_key] = turn_value.value
                        elif turn_key == 'previous_state' and isinstance(turn_value, ConversationState):
                            serialized_turn[turn_key] = turn_value.value
                        elif turn_key == 'state_transition' and isinstance(turn_value, dict):
                            serialized_transition = turn_value.copy()
                            if 'new_state' in serialized_transition and isinstance(serialized_transition['new_state'], ConversationState):
                                serialized_transition['new_state'] = serialized_transition['new_state'].value
                            serialized_turn[turn_key] = serialized_transition
                        else:
                            serialized_turn[turn_key] = turn_value
                    serialized[key].append(serialized_turn)
            else:
                serialized[key] = value
        
        return serialized
    
    def add_turn(self, user_input: str, context_analysis: Dict[str, Any], 
                system_response: str = "", mentioned_videos: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        新しいターンを追加
        
        Args:
            user_input: ユーザーの入力
            context_analysis: 文脈分析結果
            system_response: システムの応答
            mentioned_videos: 言及された動画のリスト
            
        Returns:
            ターン情報と状態遷移の結果
        """
        turn_info = {
            "turn_number": len(self.current_session["turns"]) + 1,
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "context_analysis": context_analysis,
            "system_response": system_response,
            "mentioned_videos": mentioned_videos or [],
            "previous_state": self.current_session["state"].value if isinstance(self.current_session["state"], ConversationState) else self.current_session["state"],
            "emotional_signals": context_analysis.get("emotional_signals", {})
        }
        
        # 状態遷移の評価
        transition_result = self._evaluate_state_transition(turn_info, context_analysis)
        turn_info["state_transition"] = transition_result
        
        # 新しい状態を適用
        if transition_result["should_transition"]:
            self.current_session["state"] = transition_result["new_state"]
            turn_info["new_state"] = transition_result["new_state"].value if isinstance(transition_result["new_state"], ConversationState) else transition_result["new_state"]
            
            print(f"[マルチターン] 🔄 状態遷移: {turn_info['previous_state']} → {turn_info['new_state']}")
        else:
            turn_info["new_state"] = turn_info["previous_state"]
        
        # ターンを記録
        self.current_session["turns"].append(turn_info)
        
        # 話題の更新
        self._update_active_topics(mentioned_videos)
        
        # 嗜好情報の更新
        self._update_user_preferences(context_analysis)
        
        # 感情軌跡の更新
        self._update_emotional_trajectory(context_analysis)
        
        # 自動保存
        self._save_conversation_history()
        
        return turn_info
    
    def _evaluate_state_transition(self, turn_info: Dict[str, Any], context_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """状態遷移を評価"""
        current_state = self.current_session["state"]
        if isinstance(current_state, str):
            current_state = ConversationState(current_state)
        
        transition_result = {
            "should_transition": False,
            "new_state": current_state,
            "confidence": 0.0,
            "reasons": []
        }
        
        # 現在の状態に応じた遷移ルールを取得
        rules = self.config["state_transition_rules"].get(current_state, {})
        
        for target_state_key, rule_config in rules.items():
            target_state = self._parse_target_state(target_state_key)
            if not target_state:
                continue
            
            # 条件チェック
            conditions_met, confidence = self._check_transition_conditions(
                rule_config, turn_info, context_analysis
            )
            
            if conditions_met and confidence >= rule_config.get("min_confidence", 0.5):
                if confidence > transition_result["confidence"]:
                    transition_result.update({
                        "should_transition": True,
                        "new_state": target_state,
                        "confidence": confidence,
                        "reasons": [f"条件満足: {target_state_key} (信頼度: {confidence:.2f})"]
                    })
        
        return transition_result
    
    def _parse_target_state(self, target_state_key: str) -> Optional[ConversationState]:
        """ターゲット状態キーを解析"""
        state_mapping = {
            "to_topic_established": ConversationState.TOPIC_ESTABLISHED,
            "to_deep_discussion": ConversationState.DEEP_DISCUSSION,
            "to_preference_learning": ConversationState.PREFERENCE_LEARNING,
            "to_recommendation_mode": ConversationState.RECOMMENDATION_MODE,
            "to_followup": ConversationState.FOLLOWUP,
            "to_transition": ConversationState.TRANSITION
        }
        
        return state_mapping.get(target_state_key)
    
    def _check_transition_conditions(self, rule_config: Dict[str, Any], 
                                   turn_info: Dict[str, Any], context_analysis: Dict[str, Any]) -> Tuple[bool, float]:
        """遷移条件をチェック"""
        conditions = rule_config.get("conditions", [])
        confidence_scores = []
        
        for condition in conditions:
            score = self._evaluate_condition(condition, turn_info, context_analysis)
            confidence_scores.append(score)
        
        # 最小ターン数チェック
        min_turns = rule_config.get("min_turns", 0)
        if len(self.current_session["turns"]) < min_turns:
            return False, 0.0
        
        # 全条件の平均スコア
        if confidence_scores:
            avg_confidence = sum(confidence_scores) / len(confidence_scores)
            conditions_met = avg_confidence >= 0.5  # 基本閾値
            
            return conditions_met, avg_confidence
        
        return False, 0.0
    
    def _evaluate_condition(self, condition: str, turn_info: Dict[str, Any], context_analysis: Dict[str, Any]) -> float:
        """個別条件を評価"""
        user_input = turn_info.get("user_input", "").lower()
        emotional_signals = context_analysis.get("emotional_signals", {})
        mentioned_videos = turn_info.get("mentioned_videos", [])
        
        # 条件評価ロジック
        if condition == "has_video_mention":
            return 1.0 if mentioned_videos else 0.0
        
        elif condition == "user_shows_interest":
            positive_score = emotional_signals.get("positive", 0.0)
            curiosity_score = emotional_signals.get("curiosity", 0.0)
            return min(1.0, positive_score + curiosity_score)
        
        elif condition == "recommendation_request":
            recommendation_keywords = ["おすすめ", "推薦", "教えて", "何か", "似た", "もっと"]
            score = sum(1 for keyword in recommendation_keywords if keyword in user_input)
            return min(1.0, score * 0.3)
        
        elif condition == "multiple_questions":
            question_marks = user_input.count("？") + user_input.count("?")
            question_words = ["何", "どう", "どんな", "なぜ", "いつ", "どこ", "誰"]
            question_word_count = sum(1 for word in question_words if word in user_input)
            return min(1.0, (question_marks + question_word_count) * 0.3)
        
        elif condition == "detailed_interest":
            detail_keywords = ["詳しく", "もっと", "深く", "具体的", "詳細"]
            score = sum(1 for keyword in detail_keywords if keyword in user_input)
            return min(1.0, score * 0.5)
        
        elif condition == "preference_signals":
            return emotional_signals.get("positive", 0.0) + emotional_signals.get("negative", 0.0)
        
        elif condition == "emotional_response":
            total_emotional_score = sum(emotional_signals.get(emotion, 0.0) 
                                      for emotion in ["positive", "negative", "excitement"])
            return min(1.0, total_emotional_score)
        
        elif condition == "similarity_request":
            similarity_keywords = ["似た", "同じ", "類似", "もう一度", "また"]
            score = sum(1 for keyword in similarity_keywords if keyword in user_input)
            return min(1.0, score * 0.4)
        
        elif condition == "strong_preference_signals":
            return max(emotional_signals.get("positive", 0.0), emotional_signals.get("negative", 0.0))
        
        elif condition == "user_satisfaction":
            satisfaction_score = emotional_signals.get("satisfaction", 0.0)
            positive_score = emotional_signals.get("positive", 0.0)
            return max(satisfaction_score, positive_score)
        
        elif condition == "wants_more":
            more_keywords = ["もっと", "他に", "別の", "さらに", "まだ"]
            score = sum(1 for keyword in more_keywords if keyword in user_input)
            return min(1.0, score * 0.4)
        
        elif condition == "sufficient_learning":
            # 嗜好学習が十分か（ターン数ベース）
            preference_turns = len([t for t in self.current_session["turns"] 
                                  if t.get("emotional_signals", {}).get("positive", 0) > 0.5])
            return min(1.0, preference_turns * 0.3)
        
        elif condition == "recommendation_opportunity":
            return 1.0 if len(self.current_session["active_topics"]) > 0 else 0.0
        
        elif condition == "recommendation_given":
            # システム応答に推薦が含まれているか
            response = turn_info.get("system_response", "").lower()
            recommendation_phrases = ["おすすめ", "推薦", "いかがでしょう", "聞いてみて"]
            return 1.0 if any(phrase in response for phrase in recommendation_phrases) else 0.0
        
        elif condition == "awaiting_feedback":
            return 1.0  # 推薦後は常にフィードバック待ち
        
        elif condition == "new_topic_interest":
            return emotional_signals.get("curiosity", 0.0)
        
        elif condition == "wants_more_recommendations":
            return self._evaluate_condition("wants_more", turn_info, context_analysis)
        
        elif condition == "topic_change_signals":
            transition_keywords = ["ところで", "話は変わって", "別の", "新しい"]
            score = sum(1 for keyword in transition_keywords if keyword in user_input)
            return min(1.0, score * 0.5)
        
        return 0.0
    
    def _update_active_topics(self, mentioned_videos: List[Dict[str, Any]]):
        """アクティブ話題の更新"""
        if not mentioned_videos:
            return
        
        for video_info in mentioned_videos:
            video_id = video_info.get("video_id")
            if video_id:
                if video_id not in self.current_session["active_topics"]:
                    self.current_session["active_topics"][video_id] = {
                        "video_info": video_info,
                        "first_mentioned": datetime.now().isoformat(),
                        "mention_count": 0,
                        "last_emotional_response": {}
                    }
                
                self.current_session["active_topics"][video_id]["mention_count"] += 1
                self.current_session["active_topics"][video_id]["last_mentioned"] = datetime.now().isoformat()
    
    def _update_user_preferences(self, context_analysis: Dict[str, Any]):
        """ユーザー嗜好情報の更新"""
        emotional_signals = context_analysis.get("emotional_signals", {})
        
        # 感情シグナルから嗜好を推定
        for emotion, strength in emotional_signals.items():
            if emotion in ["positive", "negative"] and strength > 0.5:
                if emotion not in self.current_session["user_preferences"]:
                    self.current_session["user_preferences"][emotion] = []
                
                # 現在の話題に対する嗜好を記録
                for topic_id in self.current_session["active_topics"]:
                    preference_entry = {
                        "topic_id": topic_id,
                        "emotion": emotion,
                        "strength": strength,
                        "timestamp": datetime.now().isoformat()
                    }
                    self.current_session["user_preferences"][emotion].append(preference_entry)
    
    def _update_emotional_trajectory(self, context_analysis: Dict[str, Any]):
        """感情軌跡の更新"""
        emotional_signals = context_analysis.get("emotional_signals", {})
        
        if emotional_signals.get("detected_emotions"):
            trajectory_entry = {
                "timestamp": datetime.now().isoformat(),
                "turn_number": len(self.current_session["turns"]),
                "emotions": emotional_signals["detected_emotions"],
                "dominant_emotion": self._get_dominant_emotion(emotional_signals)
            }
            
            self.current_session["emotional_trajectory"].append(trajectory_entry)
    
    def _get_dominant_emotion(self, emotional_signals: Dict[str, Any]) -> str:
        """主要な感情を取得"""
        emotion_scores = {
            emotion: score for emotion, score in emotional_signals.items()
            if emotion != "detected_emotions" and isinstance(score, (int, float))
        }
        
        if emotion_scores:
            return max(emotion_scores.keys(), key=lambda e: emotion_scores[e])
        
        return "neutral"
    
    def get_conversation_context_for_response(self) -> Dict[str, Any]:
        """応答生成用の会話コンテキストを取得"""
        current_state = self.current_session["state"]
        if isinstance(current_state, ConversationState):
            current_state = current_state.value
        
        recent_turns = self.current_session["turns"][-3:]  # 最近3ターン
        
        context = {
            "session_info": {
                "session_id": self.current_session["session_id"],
                "turn_count": len(self.current_session["turns"]),
                "current_state": current_state,
                "duration_minutes": self._calculate_session_duration()
            },
            "active_topics": self.current_session["active_topics"],
            "recent_emotional_trend": self._get_recent_emotional_trend(),
            "conversation_flow": self._analyze_conversation_flow(),
            "user_preferences_summary": self._summarize_user_preferences(),
            "response_guidance": self._generate_response_guidance(current_state)
        }
        
        return context
    
    def _calculate_session_duration(self) -> float:
        """セッション継続時間を計算（分）"""
        start_time = datetime.fromisoformat(self.current_session["start_time"])
        duration = datetime.now() - start_time
        return duration.total_seconds() / 60
    
    def _get_recent_emotional_trend(self) -> Dict[str, Any]:
        """最近の感情傾向を取得"""
        if not self.current_session["emotional_trajectory"]:
            return {"trend": "neutral", "stability": "unknown"}
        
        recent_emotions = self.current_session["emotional_trajectory"][-3:]
        dominant_emotions = [entry["dominant_emotion"] for entry in recent_emotions]
        
        # 最頻感情
        emotion_counts = {}
        for emotion in dominant_emotions:
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        trend = max(emotion_counts.keys(), key=lambda e: emotion_counts[e]) if emotion_counts else "neutral"
        
        # 安定性（同じ感情が続いているか）
        stability = "stable" if len(set(dominant_emotions)) <= 1 else "variable"
        
        return {
            "trend": trend,
            "stability": stability,
            "recent_emotions": dominant_emotions
        }
    
    def _analyze_conversation_flow(self) -> Dict[str, Any]:
        """会話の流れを分析"""
        turns = self.current_session["turns"]
        
        if len(turns) < 2:
            return {"flow_type": "initial", "coherence": "unknown"}
        
        # 状態遷移の履歴
        state_transitions = []
        for turn in turns:
            if turn.get("state_transition", {}).get("should_transition"):
                state_transitions.append({
                    "from": turn["previous_state"],
                    "to": turn["new_state"],
                    "turn": turn["turn_number"]
                })
        
        # 会話の一貫性
        topic_consistency = self._calculate_topic_consistency()
        emotional_consistency = self._calculate_emotional_consistency()
        
        # 流れのタイプを判定
        flow_type = "linear"
        if len(state_transitions) > len(turns) * 0.5:
            flow_type = "dynamic"
        elif len(state_transitions) == 0:
            flow_type = "static"
        
        return {
            "flow_type": flow_type,
            "state_transitions": state_transitions,
            "topic_consistency": topic_consistency,
            "emotional_consistency": emotional_consistency,
            "coherence": "high" if topic_consistency > 0.7 else "medium" if topic_consistency > 0.4 else "low"
        }
    
    def _calculate_topic_consistency(self) -> float:
        """話題の一貫性を計算"""
        if not self.current_session["active_topics"]:
            return 0.0
        
        # 最も言及された話題の割合
        total_mentions = sum(
            topic_data["mention_count"] 
            for topic_data in self.current_session["active_topics"].values()
        )
        
        if total_mentions == 0:
            return 0.0
        
        max_mentions = max(
            topic_data["mention_count"] 
            for topic_data in self.current_session["active_topics"].values()
        )
        
        return max_mentions / total_mentions
    
    def _calculate_emotional_consistency(self) -> float:
        """感情の一貫性を計算"""
        if not self.current_session["emotional_trajectory"]:
            return 0.0
        
        emotions = [entry["dominant_emotion"] for entry in self.current_session["emotional_trajectory"]]
        unique_emotions = set(emotions)
        
        if not emotions:
            return 0.0
        
        # 最頻感情の割合
        emotion_counts = {}
        for emotion in emotions:
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        max_count = max(emotion_counts.values())
        return max_count / len(emotions)
    
    def _summarize_user_preferences(self) -> Dict[str, Any]:
        """ユーザー嗜好のサマリー"""
        preferences = self.current_session["user_preferences"]
        
        summary = {
            "positive_topics": [],
            "negative_topics": [],
            "preference_strength": "unknown"
        }
        
        # ポジティブな嗜好
        positive_prefs = preferences.get("positive", [])
        if positive_prefs:
            topic_scores = {}
            for pref in positive_prefs:
                topic_id = pref["topic_id"]
                topic_scores[topic_id] = topic_scores.get(topic_id, 0) + pref["strength"]
            
            # スコア順でソート
            sorted_topics = sorted(topic_scores.items(), key=lambda x: x[1], reverse=True)
            summary["positive_topics"] = [topic_id for topic_id, score in sorted_topics[:3]]
        
        # ネガティブな嗜好
        negative_prefs = preferences.get("negative", [])
        if negative_prefs:
            topic_scores = {}
            for pref in negative_prefs:
                topic_id = pref["topic_id"]
                topic_scores[topic_id] = topic_scores.get(topic_id, 0) + pref["strength"]
            
            sorted_topics = sorted(topic_scores.items(), key=lambda x: x[1], reverse=True)
            summary["negative_topics"] = [topic_id for topic_id, score in sorted_topics[:3]]
        
        # 嗜好の強さ
        total_preferences = len(positive_prefs) + len(negative_prefs)
        if total_preferences >= 5:
            summary["preference_strength"] = "strong"
        elif total_preferences >= 2:
            summary["preference_strength"] = "medium"
        else:
            summary["preference_strength"] = "weak"
        
        return summary
    
    def _generate_response_guidance(self, current_state: str) -> Dict[str, Any]:
        """現在の状態に基づく応答ガイダンスを生成"""
        guidance = {
            "recommended_tone": "neutral",
            "suggested_actions": [],
            "focus_areas": []
        }
        
        if current_state == ConversationState.INITIAL.value:
            guidance.update({
                "recommended_tone": "welcoming",
                "suggested_actions": ["establish_topic", "show_interest"],
                "focus_areas": ["topic_discovery", "user_engagement"]
            })
        
        elif current_state == ConversationState.TOPIC_ESTABLISHED.value:
            guidance.update({
                "recommended_tone": "informative",
                "suggested_actions": ["provide_details", "ask_follow_up"],
                "focus_areas": ["information_sharing", "depth_building"]
            })
        
        elif current_state == ConversationState.DEEP_DISCUSSION.value:
            guidance.update({
                "recommended_tone": "analytical",
                "suggested_actions": ["explore_nuances", "connect_concepts"],
                "focus_areas": ["deep_analysis", "conceptual_connections"]
            })
        
        elif current_state == ConversationState.PREFERENCE_LEARNING.value:
            guidance.update({
                "recommended_tone": "curious",
                "suggested_actions": ["probe_preferences", "note_reactions"],
                "focus_areas": ["preference_discovery", "reaction_analysis"]
            })
        
        elif current_state == ConversationState.RECOMMENDATION_MODE.value:
            guidance.update({
                "recommended_tone": "helpful",
                "suggested_actions": ["provide_recommendations", "explain_reasoning"],
                "focus_areas": ["personalized_suggestions", "rationale_explanation"]
            })
        
        elif current_state == ConversationState.FOLLOWUP.value:
            guidance.update({
                "recommended_tone": "attentive",
                "suggested_actions": ["gather_feedback", "adjust_approach"],
                "focus_areas": ["feedback_collection", "satisfaction_assessment"]
            })
        
        return guidance
    
    def end_session(self) -> Dict[str, Any]:
        """現在のセッションを終了"""
        # セッションサマリーを生成
        session_summary = {
            "session_id": self.current_session["session_id"],
            "duration_minutes": self._calculate_session_duration(),
            "total_turns": len(self.current_session["turns"]),
            "final_state": self.current_session["state"].value if isinstance(self.current_session["state"], ConversationState) else self.current_session["state"],
            "topics_discussed": len(self.current_session["active_topics"]),
            "emotional_trajectory_summary": self._get_recent_emotional_trend(),
            "user_preferences_learned": self._summarize_user_preferences(),
            "conversation_quality": self._assess_conversation_quality()
        }
        
        # セッションを履歴に移動
        self.session_history.append(self.current_session.copy())
        
        # 新しいセッションを開始
        self.current_session = {
            "session_id": self._generate_session_id(),
            "start_time": datetime.now().isoformat(),
            "state": ConversationState.INITIAL,
            "turns": [],
            "active_topics": {},
            "user_preferences": {},
            "conversation_goals": [],
            "emotional_trajectory": []
        }
        
        # 履歴を保存
        self._save_conversation_history()
        
        print(f"[マルチターン] 🏁 セッション終了: {session_summary['session_id']}")
        
        return session_summary
    
    def _assess_conversation_quality(self) -> Dict[str, Any]:
        """会話品質を評価"""
        turns = self.current_session["turns"]
        
        quality_metrics = {
            "engagement": 0.0,
            "coherence": 0.0,
            "productivity": 0.0,
            "user_satisfaction": 0.0,
            "overall": 0.0
        }
        
        if not turns:
            return quality_metrics
        
        # エンゲージメント（ターン数とやり取りの活発さ）
        quality_metrics["engagement"] = min(1.0, len(turns) / 10)
        
        # 一貫性
        conversation_flow = self._analyze_conversation_flow()
        if conversation_flow["coherence"] == "high":
            quality_metrics["coherence"] = 0.9
        elif conversation_flow["coherence"] == "medium":
            quality_metrics["coherence"] = 0.6
        else:
            quality_metrics["coherence"] = 0.3
        
        # 生産性（学習された嗜好数、扱った話題数）
        topics_count = len(self.current_session["active_topics"])
        preferences_count = sum(len(prefs) for prefs in self.current_session["user_preferences"].values())
        quality_metrics["productivity"] = min(1.0, (topics_count * 0.3 + preferences_count * 0.1))
        
        # ユーザー満足度（ポジティブ感情の割合）
        emotional_trajectory = self.current_session["emotional_trajectory"]
        if emotional_trajectory:
            positive_emotions = sum(1 for entry in emotional_trajectory 
                                  if entry["dominant_emotion"] in ["positive", "excitement", "satisfaction"])
            quality_metrics["user_satisfaction"] = positive_emotions / len(emotional_trajectory)
        
        # 総合評価
        quality_metrics["overall"] = (
            quality_metrics["engagement"] * 0.25 +
            quality_metrics["coherence"] * 0.25 +
            quality_metrics["productivity"] * 0.25 +
            quality_metrics["user_satisfaction"] * 0.25
        )
        
        return quality_metrics

    def get_current_session(self) -> Dict[str, Any]:
        """現在のセッション情報を取得（高速モード用）"""
        return self.current_session.copy()


# 使用例・テスト
if __name__ == "__main__":
    print("=== マルチターン会話管理システムテスト ===")
    
    manager = MultiTurnConversationManager()
    
    # テストシナリオ
    test_conversations = [
        {"input": "アドベンチャーについて教えて", "videos": [{"video_id": "test1", "title": "アドベンチャー"}]},
        {"input": "この曲いいね！", "videos": []},
        {"input": "もっと詳しく教えて", "videos": []},
        {"input": "似たような曲ある？", "videos": []}
    ]
    
    print("\n📝 マルチターン会話テスト:")
    for i, scenario in enumerate(test_conversations):
        print(f"\nターン {i+1}: '{scenario['input']}'")
        
        # 簡易的な文脈分析（実際にはcontext_understanding_systemを使用）
        mock_analysis = {
            "emotional_signals": {
                "positive": 0.8 if "いい" in scenario['input'] else 0.2,
                "curiosity": 0.7 if "？" in scenario['input'] or "教えて" in scenario['input'] else 0.1,
                "detected_emotions": [{"emotion": "positive", "strength": 0.8}] if "いい" in scenario['input'] else []
            },
            "pronoun_references": [{"type": "demonstrative", "text": "この曲"}] if "この" in scenario['input'] else []
        }
        
        # ターン追加
        turn_result = manager.add_turn(
            scenario['input'], 
            mock_analysis, 
            f"応答{i+1}", 
            scenario['videos']
        )
        
        print(f"  状態: {turn_result['previous_state']} → {turn_result['new_state']}")
        if turn_result['state_transition']['should_transition']:
            print(f"  遷移理由: {turn_result['state_transition']['reasons']}")
    
    # 会話コンテキスト取得
    context = manager.get_conversation_context_for_response()
    print(f"\n📊 会話コンテキスト:")
    print(f"  状態: {context['session_info']['current_state']}")
    print(f"  ターン数: {context['session_info']['turn_count']}")
    print(f"  話題数: {len(context['active_topics'])}")
    print(f"  感情傾向: {context['recent_emotional_trend']['trend']}")
    
    # セッション終了
    summary = manager.end_session()
    print(f"\n🏁 セッション終了:")
    print(f"  継続時間: {summary['duration_minutes']:.1f}分")
    print(f"  総合品質: {summary['conversation_quality']['overall']:.2f}")
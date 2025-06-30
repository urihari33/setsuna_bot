#!/usr/bin/env python3
"""
適応学習システム - Phase 3-B
動的学習・記憶強化・ユーザー適応機能の統合実装

既存のトピック学習システムとマルチターン会話管理を統合し、
YouTubeナレッジシステムと連携した適応学習エンジンを提供
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict

# パスを追加してモジュールにアクセス
sys.path.append(str(Path(__file__).parent.parent.parent))
sys.path.append(str(Path(__file__).parent.parent))

try:
    from core.topic_learning_system import TopicLearningSystem
    from core.multi_turn_conversation_manager import MultiTurnConversationManager, ConversationState
    from storage.unified_storage import get_storage
except ImportError:
    # 親ディレクトリから読み込み
    sys.path.append("/mnt/d/setsuna_bot")
    from core.topic_learning_system import TopicLearningSystem
    from core.multi_turn_conversation_manager import MultiTurnConversationManager, ConversationState
    from youtube_knowledge_system.storage.unified_storage import get_storage

class AdaptiveLearningSystem:
    """適応学習システム - YouTube知識との統合学習エンジン"""
    
    def __init__(self):
        """初期化"""
        self.topic_learner = TopicLearningSystem()
        self.conversation_manager = MultiTurnConversationManager()
        self.storage = get_storage()
        
        # 学習統計
        self.learning_stats = {
            "total_interactions": 0,
            "successful_recommendations": 0,
            "learning_accuracy": 0.0,
            "adaptation_score": 0.0,
            "last_updated": datetime.now().isoformat()
        }
        
        # 適応学習設定
        self.adaptation_config = {
            "enable_youtube_integration": True,
            "enable_dynamic_weighting": True,
            "enable_context_memory": True,
            "enable_preference_evolution": True,
            "adaptation_sensitivity": 0.7,  # 適応の敏感度
            "memory_decay_rate": 0.95,      # 記憶減衰率
            "learning_momentum": 0.8        # 学習慣性
        }
        
        print("[適応学習] ✅ 適応学習システム初期化完了")
    
    def process_interaction(self, user_input: str, setsuna_response: str, 
                          context_analysis: Dict[str, Any], mentioned_videos: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        ユーザーインタラクションを処理し、統合学習を実行
        
        Args:
            user_input: ユーザーの入力
            setsuna_response: せつなの応答
            context_analysis: 文脈分析結果
            mentioned_videos: 言及された動画のリスト
            
        Returns:
            学習結果と適応情報
        """
        try:
            print(f"\\n[適応学習] 🧠 インタラクション処理開始")
            
            # ユーザー反応を分析
            user_reaction = self._analyze_user_reaction(user_input, context_analysis)
            
            # マルチターン会話管理に追加
            turn_info = self.conversation_manager.add_turn(
                user_input, context_analysis, setsuna_response, mentioned_videos
            )
            
            # YouTube動画データの取得と学習
            learning_results = []
            if mentioned_videos and self.adaptation_config["enable_youtube_integration"]:
                for video_info in mentioned_videos:
                    video_data = self._get_enhanced_video_data(video_info)
                    if video_data:
                        # トピック学習実行
                        learning_success = self.topic_learner.learn_from_interaction(
                            video_data, user_reaction, user_input
                        )
                        
                        if learning_success:
                            learning_results.append({
                                "video_id": video_info.get("video_id"),
                                "learning_type": "topic_preference",
                                "reaction": user_reaction,
                                "confidence": context_analysis.get("confidence", 0.5)
                            })
            
            # 動的重み付け学習
            if self.adaptation_config["enable_dynamic_weighting"]:
                weight_updates = self._update_dynamic_weights(turn_info, learning_results)
            else:
                weight_updates = {}
            
            # 文脈記憶強化
            if self.adaptation_config["enable_context_memory"]:
                memory_updates = self._enhance_context_memory(turn_info, mentioned_videos)
            else:
                memory_updates = {}
            
            # 嗜好進化処理
            if self.adaptation_config["enable_preference_evolution"]:
                evolution_results = self._evolve_preferences(user_reaction, learning_results)
            else:
                evolution_results = {}
            
            # 学習統計更新
            self._update_learning_stats(learning_results, user_reaction)
            
            # 適応スコア計算
            adaptation_score = self._calculate_adaptation_score(turn_info, learning_results)
            
            # 結果統合
            result = {
                "turn_info": turn_info,
                "learning_results": learning_results,
                "user_reaction": user_reaction,
                "weight_updates": weight_updates,
                "memory_updates": memory_updates,
                "evolution_results": evolution_results,
                "adaptation_score": adaptation_score,
                "learning_quality": self._assess_learning_quality(learning_results),
                "recommendations": self._generate_adaptive_recommendations(turn_info)
            }
            
            print(f"[適応学習] ✅ 学習完了: 反応={user_reaction}, 適応スコア={adaptation_score:.2f}")
            
            return result
            
        except Exception as e:
            print(f"[適応学習] ❌ インタラクション処理エラー: {e}")
            import traceback
            traceback.print_exc()
            return {"error": str(e)}
    
    def _analyze_user_reaction(self, user_input: str, context_analysis: Dict[str, Any]) -> str:
        """ユーザー反応を分析"""
        emotional_signals = context_analysis.get("emotional_signals", {})
        
        # ポジティブ反応の検出
        positive_score = emotional_signals.get("positive", 0.0)
        negative_score = emotional_signals.get("negative", 0.0)
        excitement_score = emotional_signals.get("excitement", 0.0)
        
        # キーワードベースの分析
        user_lower = user_input.lower()
        
        positive_keywords = ["いい", "好き", "素晴らしい", "最高", "気に入った", "もっと"]
        negative_keywords = ["嫌い", "だめ", "つまらない", "違う", "合わない"]
        neutral_keywords = ["そうですね", "わかりました", "なるほど"]
        
        positive_keyword_score = sum(1 for keyword in positive_keywords if keyword in user_lower)
        negative_keyword_score = sum(1 for keyword in negative_keywords if keyword in user_lower)
        neutral_keyword_score = sum(1 for keyword in neutral_keywords if keyword in user_lower)
        
        # 総合判定
        total_positive = positive_score + excitement_score + (positive_keyword_score * 0.3)
        total_negative = negative_score + (negative_keyword_score * 0.4)
        total_neutral = neutral_keyword_score * 0.2
        
        if total_positive > 0.6:
            return "positive"
        elif total_negative > 0.5:
            return "negative"
        else:
            return "neutral"
    
    def _get_enhanced_video_data(self, video_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """YouTube知識システムから拡張動画データを取得"""
        try:
            video_id = video_info.get("video_id")
            if not video_id:
                return None
            
            # 統合ストレージから動画データを取得
            video = self.storage.get_video(video_id)
            if not video:
                print(f"[適応学習] ⚠️ 動画データが見つかりません: {video_id}")
                return None
            
            # 動画データを学習用形式に変換
            enhanced_data = {
                "metadata": {
                    "title": video.metadata.title,
                    "description": video.metadata.description,
                    "channel_title": video.metadata.channel_title,
                    "tags": video.metadata.tags,
                    "published_at": video.metadata.published_at.isoformat(),
                    "duration": video.metadata.duration,
                    "view_count": video.metadata.view_count
                },
                "creative_insight": None
            }
            
            # 分析結果が存在する場合は追加
            if video.creative_insight:
                enhanced_data["creative_insight"] = {
                    "creators": [
                        {
                            "name": creator.name,
                            "role": creator.role,
                            "confidence": creator.confidence
                        }
                        for creator in video.creative_insight.creators
                    ],
                    "themes": video.creative_insight.themes,
                    "tools_used": video.creative_insight.tools_used,
                    "music_analysis": {
                        "genre": video.creative_insight.music_info.genre if video.creative_insight.music_info else None,
                        "mood": video.creative_insight.music_info.mood if video.creative_insight.music_info else None
                    } if video.creative_insight.music_info else {}
                }
            
            return enhanced_data
            
        except Exception as e:
            print(f"[適応学習] ❌ 動画データ取得エラー: {e}")
            return None
    
    def _update_dynamic_weights(self, turn_info: Dict[str, Any], learning_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """動的重み付けを更新"""
        try:
            current_state = turn_info.get("new_state", ConversationState.INITIAL.value)
            user_reaction = turn_info.get("emotional_signals", {})
            
            # 状態に基づく重み調整
            state_weights = {
                ConversationState.INITIAL.value: {"exploration": 0.8, "exploitation": 0.2},
                ConversationState.TOPIC_ESTABLISHED.value: {"exploration": 0.6, "exploitation": 0.4},
                ConversationState.DEEP_DISCUSSION.value: {"exploration": 0.4, "exploitation": 0.6},
                ConversationState.PREFERENCE_LEARNING.value: {"exploration": 0.3, "exploitation": 0.7},
                ConversationState.RECOMMENDATION_MODE.value: {"exploration": 0.2, "exploitation": 0.8}
            }
            
            weights = state_weights.get(current_state, {"exploration": 0.5, "exploitation": 0.5})
            
            # 学習結果に基づく調整
            if learning_results:
                success_rate = sum(1 for result in learning_results if result.get("reaction") == "positive") / len(learning_results)
                
                # 成功率が高い場合は活用重視、低い場合は探索重視
                if success_rate > 0.7:
                    weights["exploitation"] = min(1.0, weights["exploitation"] + 0.1)
                    weights["exploration"] = 1.0 - weights["exploitation"]
                elif success_rate < 0.3:
                    weights["exploration"] = min(1.0, weights["exploration"] + 0.1)
                    weights["exploitation"] = 1.0 - weights["exploration"]
            
            return {
                "dynamic_weights": weights,
                "adjustment_reason": f"状態={current_state}, 学習結果={len(learning_results)}件",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"[適応学習] ❌ 動的重み更新エラー: {e}")
            return {}
    
    def _enhance_context_memory(self, turn_info: Dict[str, Any], mentioned_videos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """文脈記憶を強化"""
        try:
            memory_updates = {
                "short_term_memory": {},
                "long_term_memory": {},
                "contextual_associations": []
            }
            
            # 短期記憶（現在のセッション内）
            current_session = self.conversation_manager.get_current_session()
            memory_updates["short_term_memory"] = {
                "active_topics": list(current_session.get("active_topics", {}).keys()),
                "emotional_trajectory": current_session.get("emotional_trajectory", [])[-3:],  # 最近3エントリ
                "preference_signals": current_session.get("user_preferences", {})
            }
            
            # 長期記憶（トピック学習システムから）
            preferred_genres = self.topic_learner.get_preferred_genres(5)
            preferred_creators = self.topic_learner.get_preferred_creators(5)
            
            memory_updates["long_term_memory"] = {
                "preferred_genres": preferred_genres,
                "preferred_creators": preferred_creators,
                "time_patterns": self.topic_learner.get_time_preferences()
            }
            
            # 文脈的関連付け
            if mentioned_videos:
                for video_info in mentioned_videos:
                    video_id = video_info.get("video_id")
                    if video_id:
                        # 他の言及動画との関連性を計算
                        associations = self._calculate_video_associations(video_id, current_session)
                        memory_updates["contextual_associations"].append({
                            "video_id": video_id,
                            "associations": associations,
                            "context_strength": self._calculate_context_strength(turn_info)
                        })
            
            return memory_updates
            
        except Exception as e:
            print(f"[適応学習] ❌ 文脈記憶強化エラー: {e}")
            return {}
    
    def _calculate_video_associations(self, video_id: str, current_session: Dict[str, Any]) -> List[Dict[str, Any]]:
        """動画間の関連性を計算"""
        associations = []
        
        try:
            # 現在のセッションで言及された他の動画との関連性
            active_topics = current_session.get("active_topics", {})
            
            for other_video_id, topic_data in active_topics.items():
                if other_video_id != video_id:
                    # 時間的近接性
                    temporal_score = self._calculate_temporal_proximity(
                        topic_data.get("first_mentioned", ""),
                        topic_data.get("last_mentioned", "")
                    )
                    
                    # 感情的関連性
                    emotional_score = self._calculate_emotional_similarity(
                        topic_data.get("last_emotional_response", {})
                    )
                    
                    association_strength = (temporal_score * 0.4 + emotional_score * 0.6)
                    
                    if association_strength > 0.3:
                        associations.append({
                            "related_video_id": other_video_id,
                            "strength": association_strength,
                            "type": "contextual"
                        })
            
            return associations
            
        except Exception as e:
            print(f"[適応学習] ❌ 動画関連性計算エラー: {e}")
            return []
    
    def _calculate_temporal_proximity(self, timestamp1: str, timestamp2: str) -> float:
        """時間的近接性を計算"""
        try:
            if not timestamp1 or not timestamp2:
                return 0.0
            
            time1 = datetime.fromisoformat(timestamp1)
            time2 = datetime.fromisoformat(timestamp2)
            
            diff_minutes = abs((time2 - time1).total_seconds()) / 60
            
            # 近い時間ほど高いスコア（最大30分で0.0になる）
            proximity = max(0.0, 1.0 - (diff_minutes / 30))
            
            return proximity
            
        except:
            return 0.0
    
    def _calculate_emotional_similarity(self, emotional_response: Dict[str, Any]) -> float:
        """感情的類似性を計算"""
        # 現在のセッションの感情傾向と比較
        current_session = self.conversation_manager.get_current_session()
        recent_trajectory = current_session.get("emotional_trajectory", [])
        
        if not recent_trajectory or not emotional_response:
            return 0.0
        
        # 最近の感情と比較
        recent_emotions = recent_trajectory[-1].get("emotions", [])
        
        # 簡単な感情マッチング
        similarity_score = 0.0
        for emotion_data in recent_emotions:
            emotion_type = emotion_data.get("emotion", "")
            if emotion_type in emotional_response:
                similarity_score += emotional_response[emotion_type]
        
        return min(1.0, similarity_score)
    
    def _calculate_context_strength(self, turn_info: Dict[str, Any]) -> float:
        """文脈強度を計算"""
        try:
            strength_factors = []
            
            # 感情強度
            emotional_signals = turn_info.get("emotional_signals", {})
            emotional_strength = sum(emotional_signals.values()) / len(emotional_signals) if emotional_signals else 0.0
            strength_factors.append(emotional_strength)
            
            # 状態遷移の信頼度
            state_transition = turn_info.get("state_transition", {})
            transition_confidence = state_transition.get("confidence", 0.0)
            strength_factors.append(transition_confidence)
            
            # 言及動画数
            mentioned_count = len(turn_info.get("mentioned_videos", []))
            mention_strength = min(1.0, mentioned_count * 0.3)
            strength_factors.append(mention_strength)
            
            # 平均強度
            return sum(strength_factors) / len(strength_factors) if strength_factors else 0.0
            
        except Exception as e:
            print(f"[適応学習] ❌ 文脈強度計算エラー: {e}")
            return 0.0
    
    def _evolve_preferences(self, user_reaction: str, learning_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """嗜好の進化処理"""
        try:
            evolution_results = {
                "preference_changes": [],
                "new_patterns_detected": [],
                "adaptation_recommendations": []
            }
            
            # 学習結果から嗜好変化を分析
            for result in learning_results:
                if result.get("reaction") == "positive":
                    # ポジティブな反応から新しい嗜好パターンを検出
                    video_id = result.get("video_id")
                    video_data = self._get_enhanced_video_data({"video_id": video_id})
                    
                    if video_data:
                        new_patterns = self._detect_preference_patterns(video_data, user_reaction)
                        evolution_results["new_patterns_detected"].extend(new_patterns)
            
            # 嗜好の進化度を計算
            evolution_score = self._calculate_evolution_score(learning_results)
            
            if evolution_score > 0.6:
                evolution_results["adaptation_recommendations"].append({
                    "type": "preference_expansion",
                    "reason": "新しい嗜好パターンの形成が検出されました",
                    "confidence": evolution_score
                })
            
            return evolution_results
            
        except Exception as e:
            print(f"[適応学習] ❌ 嗜好進化処理エラー: {e}")
            return {}
    
    def _detect_preference_patterns(self, video_data: Dict[str, Any], user_reaction: str) -> List[Dict[str, Any]]:
        """嗜好パターンを検出"""
        patterns = []
        
        try:
            if user_reaction != "positive":
                return patterns
            
            metadata = video_data.get("metadata", {})
            creative_insight = video_data.get("creative_insight", {})
            
            # 新しいジャンルの発見
            music_analysis = creative_insight.get("music_analysis", {})
            genre = music_analysis.get("genre")
            
            if genre:
                existing_genres = [g[0] for g in self.topic_learner.get_preferred_genres(10)]
                if genre not in existing_genres:
                    patterns.append({
                        "type": "new_genre",
                        "value": genre,
                        "confidence": 0.7
                    })
            
            # 新しいクリエイターの発見
            creators = creative_insight.get("creators", [])
            existing_creators = [c[0] for c in self.topic_learner.get_preferred_creators(20)]
            
            for creator_info in creators:
                creator_name = creator_info.get("name", "")
                if creator_name and creator_name not in existing_creators:
                    patterns.append({
                        "type": "new_creator",
                        "value": creator_name,
                        "role": creator_info.get("role", "unknown"),
                        "confidence": creator_info.get("confidence", 0.5)
                    })
            
            return patterns
            
        except Exception as e:
            print(f"[適応学習] ❌ パターン検出エラー: {e}")
            return []
    
    def _calculate_evolution_score(self, learning_results: List[Dict[str, Any]]) -> float:
        """進化スコアを計算"""
        if not learning_results:
            return 0.0
        
        # ポジティブ反応の割合
        positive_count = sum(1 for result in learning_results if result.get("reaction") == "positive")
        positive_ratio = positive_count / len(learning_results)
        
        # 学習の多様性
        unique_videos = len(set(result.get("video_id") for result in learning_results))
        diversity_score = min(1.0, unique_videos / 5)  # 最大5動画で1.0
        
        # 信頼度の平均
        confidence_scores = [result.get("confidence", 0.0) for result in learning_results]
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
        
        # 総合進化スコア
        evolution_score = (positive_ratio * 0.4 + diversity_score * 0.3 + avg_confidence * 0.3)
        
        return evolution_score
    
    def _update_learning_stats(self, learning_results: List[Dict[str, Any]], user_reaction: str):
        """学習統計を更新"""
        try:
            self.learning_stats["total_interactions"] += 1
            
            if user_reaction == "positive":
                self.learning_stats["successful_recommendations"] += 1
            
            # 学習精度の更新
            if self.learning_stats["total_interactions"] > 0:
                self.learning_stats["learning_accuracy"] = (
                    self.learning_stats["successful_recommendations"] / 
                    self.learning_stats["total_interactions"]
                )
            
            # 適応スコアの更新（移動平均）
            current_adaptation = len(learning_results) * 0.2 if learning_results else 0.0
            momentum = self.adaptation_config["learning_momentum"]
            
            self.learning_stats["adaptation_score"] = (
                self.learning_stats["adaptation_score"] * momentum + 
                current_adaptation * (1 - momentum)
            )
            
            self.learning_stats["last_updated"] = datetime.now().isoformat()
            
        except Exception as e:
            print(f"[適応学習] ❌ 学習統計更新エラー: {e}")
    
    def _calculate_adaptation_score(self, turn_info: Dict[str, Any], learning_results: List[Dict[str, Any]]) -> float:
        """適応スコアを計算"""
        try:
            score_components = []
            
            # 状態遷移の適切性
            state_transition = turn_info.get("state_transition", {})
            if state_transition.get("should_transition"):
                score_components.append(state_transition.get("confidence", 0.0))
            else:
                score_components.append(0.5)  # 遷移なしは中立
            
            # 学習結果の質
            if learning_results:
                positive_ratio = sum(1 for r in learning_results if r.get("reaction") == "positive") / len(learning_results)
                score_components.append(positive_ratio)
            else:
                score_components.append(0.3)  # 学習なしは低スコア
            
            # 感情強度
            emotional_signals = turn_info.get("emotional_signals", {})
            emotional_strength = sum(emotional_signals.values()) / len(emotional_signals) if emotional_signals else 0.0
            score_components.append(emotional_strength)
            
            # 平均適応スコア
            return sum(score_components) / len(score_components) if score_components else 0.0
            
        except Exception as e:
            print(f"[適応学習] ❌ 適応スコア計算エラー: {e}")
            return 0.0
    
    def _assess_learning_quality(self, learning_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """学習品質を評価"""
        if not learning_results:
            return {
                "overall_quality": "poor",
                "confidence": 0.0,
                "diversity": 0.0,
                "effectiveness": 0.0
            }
        
        # 信頼度の評価
        confidences = [result.get("confidence", 0.0) for result in learning_results]
        avg_confidence = sum(confidences) / len(confidences)
        
        # 多様性の評価
        unique_videos = len(set(result.get("video_id") for result in learning_results))
        diversity = min(1.0, unique_videos / len(learning_results))
        
        # 効果の評価
        positive_count = sum(1 for result in learning_results if result.get("reaction") == "positive")
        effectiveness = positive_count / len(learning_results)
        
        # 総合品質
        overall_score = (avg_confidence * 0.3 + diversity * 0.3 + effectiveness * 0.4)
        
        if overall_score >= 0.8:
            quality = "excellent"
        elif overall_score >= 0.6:
            quality = "good"
        elif overall_score >= 0.4:
            quality = "fair"
        else:
            quality = "poor"
        
        return {
            "overall_quality": quality,
            "confidence": avg_confidence,
            "diversity": diversity,
            "effectiveness": effectiveness,
            "score": overall_score
        }
    
    def _generate_adaptive_recommendations(self, turn_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """適応的推薦を生成"""
        recommendations = []
        
        try:
            current_state = turn_info.get("new_state", ConversationState.INITIAL.value)
            
            # 状態に基づく推薦戦略
            if current_state == ConversationState.RECOMMENDATION_MODE.value:
                # 嗜好ベースの推薦
                preferred_genres = self.topic_learner.get_preferred_genres(3)
                preferred_creators = self.topic_learner.get_preferred_creators(3)
                
                if preferred_genres:
                    recommendations.append({
                        "type": "genre_based",
                        "strategy": "exploit_preferences",
                        "targets": [genre[0] for genre in preferred_genres],
                        "confidence": 0.8
                    })
                
                if preferred_creators:
                    recommendations.append({
                        "type": "creator_based",
                        "strategy": "exploit_preferences", 
                        "targets": [creator[0] for creator in preferred_creators],
                        "confidence": 0.8
                    })
            
            elif current_state in [ConversationState.INITIAL.value, ConversationState.TOPIC_ESTABLISHED.value]:
                # 探索的推薦
                recommendations.append({
                    "type": "exploratory",
                    "strategy": "explore_new_content",
                    "targets": ["diversity", "novelty"],
                    "confidence": 0.6
                })
            
            return recommendations
            
        except Exception as e:
            print(f"[適応学習] ❌ 適応推薦生成エラー: {e}")
            return []
    
    def get_learning_summary(self) -> Dict[str, Any]:
        """学習状況のサマリーを取得"""
        try:
            # トピック学習のサマリー
            topic_summary = self.topic_learner.get_learning_summary()
            
            # 会話コンテキスト
            conversation_context = self.conversation_manager.get_conversation_context_for_response()
            
            # 統合サマリー
            return {
                "learning_stats": self.learning_stats,
                "topic_learning": topic_summary,
                "conversation_state": conversation_context.get("session_info", {}),
                "adaptation_config": self.adaptation_config,
                "recent_trends": {
                    "emotional_trend": conversation_context.get("recent_emotional_trend", {}),
                    "conversation_quality": conversation_context.get("conversation_flow", {}),
                    "user_preferences": conversation_context.get("user_preferences_summary", {})
                },
                "system_performance": {
                    "total_interactions": self.learning_stats["total_interactions"],
                    "success_rate": self.learning_stats["learning_accuracy"],
                    "adaptation_level": self.learning_stats["adaptation_score"]
                }
            }
            
        except Exception as e:
            print(f"[適応学習] ❌ サマリー取得エラー: {e}")
            return {"error": str(e)}
    
    def reset_learning_session(self) -> bool:
        """学習セッションをリセット"""
        try:
            # 会話セッション終了
            session_summary = self.conversation_manager.end_session()
            
            print(f"[適応学習] 🔄 学習セッションリセット完了")
            print(f"   セッション期間: {session_summary.get('duration_minutes', 0):.1f}分")
            print(f"   総ターン数: {session_summary.get('total_turns', 0)}")
            print(f"   会話品質: {session_summary.get('conversation_quality', {}).get('overall', 0):.2f}")
            
            return True
            
        except Exception as e:
            print(f"[適応学習] ❌ セッションリセットエラー: {e}")
            return False


# 使用例・テスト
if __name__ == "__main__":
    print("=== 適応学習システムテスト ===")
    
    # システム初期化
    adaptive_system = AdaptiveLearningSystem()
    
    # テスト用のインタラクション
    test_scenarios = [
        {
            "user_input": "YOASOBIのアドベンチャーについて教えて",
            "setsuna_response": "YOASOBIの「アドベンチャー」は素晴らしい楽曲ですね！",
            "context_analysis": {
                "emotional_signals": {"positive": 0.8, "curiosity": 0.7},
                "confidence": 0.8
            },
            "mentioned_videos": [{"video_id": "Av3xaZkVpJs", "title": "YOASOBI「アドベンチャー」Official Music Video"}]
        },
        {
            "user_input": "この曲すごくいい！もっと聞きたい",
            "setsuna_response": "お気に入りいただけて嬉しいです！似たような楽曲もご紹介できますよ",
            "context_analysis": {
                "emotional_signals": {"positive": 0.9, "excitement": 0.8},
                "confidence": 0.9
            },
            "mentioned_videos": []
        }
    ]
    
    print("\\n📝 適応学習テスト実行:")
    
    for i, scenario in enumerate(test_scenarios):
        print(f"\\n--- シナリオ {i+1} ---")
        print(f"ユーザー入力: {scenario['user_input']}")
        
        # 適応学習処理
        result = adaptive_system.process_interaction(
            scenario["user_input"],
            scenario["setsuna_response"], 
            scenario["context_analysis"],
            scenario.get("mentioned_videos", [])
        )
        
        if "error" not in result:
            print(f"✅ 学習成功")
            print(f"   ユーザー反応: {result['user_reaction']}")
            print(f"   適応スコア: {result['adaptation_score']:.2f}")
            print(f"   学習結果数: {len(result['learning_results'])}")
            print(f"   学習品質: {result['learning_quality']['overall_quality']}")
        else:
            print(f"❌ 学習失敗: {result['error']}")
    
    # 学習サマリー表示
    print(f"\\n📊 学習サマリー:")
    summary = adaptive_system.get_learning_summary()
    
    print(f"   総インタラクション数: {summary['learning_stats']['total_interactions']}")
    print(f"   学習精度: {summary['learning_stats']['learning_accuracy']:.2f}")
    print(f"   適応スコア: {summary['learning_stats']['adaptation_score']:.2f}")
    print(f"   学習ジャンル数: {summary['topic_learning']['total_genres']}")
    print(f"   学習クリエイター数: {summary['topic_learning']['total_creators']}")
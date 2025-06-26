#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
個人化推薦エンジン - Phase 2-B-2
学習された嗜好パターンに基づく賢い動画推薦
"""

import random
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from .topic_learning_system import TopicLearningSystem
from .video_conversation_history import VideoConversationHistory
from .youtube_knowledge_manager import YouTubeKnowledgeManager

class PersonalizedRecommendationEngine:
    """個人化された推薦を行うクラス"""
    
    def __init__(self, 
                 topic_learning: TopicLearningSystem,
                 conversation_history: VideoConversationHistory,
                 knowledge_manager: YouTubeKnowledgeManager):
        """初期化"""
        self.topic_learning = topic_learning
        self.conversation_history = conversation_history
        self.knowledge_manager = knowledge_manager
        
        # 推薦設定
        self.recommendation_config = {
            "familiarity_weight": 0.7,     # 馴染みやすさの重み
            "novelty_weight": 0.3,         # 新規性の重み
            "preference_boost": 1.5,       # 嗜好マッチ時のブースト
            "time_preference_weight": 0.2, # 時間帯嗜好の重み
            "min_preference_score": 0.6,   # 嗜好認識の最小スコア
        }
        
        print("[個人化推薦] ✅ 個人化推薦エンジン初期化完了")
    
    def analyze_user_request(self, user_input: str) -> Dict[str, Any]:
        """
        ユーザーリクエストを分析
        
        Args:
            user_input: ユーザーの入力
            
        Returns:
            リクエスト分析結果
        """
        analysis = {
            "request_type": "general",  # general, familiar, new, specific
            "preference_hints": [],
            "familiarity_preference": None,  # familiar, new, mixed
            "specific_targets": {},
            "mood_hints": [],
            "time_sensitive": False
        }
        
        user_lower = user_input.lower()
        
        # 嗜好パターン検出
        preference_patterns = self.topic_learning.detect_preference_keywords(user_input)
        analysis["preference_hints"] = preference_patterns
        
        # 馴染み度リクエスト検出
        familiar_keywords = ['いつもの', 'お気に入り', 'よく聞く', '好きな', 'お馴染み', '定番']
        new_keywords = ['新しい', '違う', '別の', '初めて', '知らない', '珍しい']
        
        if any(keyword in user_input for keyword in familiar_keywords):
            analysis["familiarity_preference"] = "familiar"
            analysis["request_type"] = "familiar"
        elif any(keyword in user_input for keyword in new_keywords):
            analysis["familiarity_preference"] = "new" 
            analysis["request_type"] = "new"
        
        # 具体的なターゲット検出
        preferred_genres = self.topic_learning.get_preferred_genres(10)
        preferred_creators = self.topic_learning.get_preferred_creators(10)
        
        for genre, score in preferred_genres:
            if genre.lower() in user_lower:
                analysis["specific_targets"]["genre"] = genre
                analysis["request_type"] = "specific"
        
        for creator, score in preferred_creators:
            if creator.lower() in user_lower:
                analysis["specific_targets"]["creator"] = creator
                analysis["request_type"] = "specific"
        
        # ムードヒント検出
        mood_keywords = {
            "明るい": ["明るい", "元気", "楽しい", "アップ", "ポジティブ"],
            "落ち着いた": ["落ち着いた", "リラックス", "癒し", "穏やか"],
            "切ない": ["切ない", "感動", "泣ける", "エモい"],
            "かっこいい": ["かっこいい", "クール", "格好良い"]
        }
        
        for mood, keywords in mood_keywords.items():
            if any(keyword in user_input for keyword in keywords):
                analysis["mood_hints"].append(mood)
        
        # 時間敏感性検出
        time_keywords = ["今", "今日", "この時間", "朝", "昼", "夜", "今の気分"]
        if any(keyword in user_input for keyword in time_keywords):
            analysis["time_sensitive"] = True
        
        return analysis
    
    def calculate_video_preference_score(self, video_data: Dict[str, Any]) -> float:
        """
        動画の嗜好マッチスコアを計算
        
        Args:
            video_data: 動画データ
            
        Returns:
            嗜好スコア (0.0-1.0)
        """
        total_score = 0.0
        factor_count = 0
        
        # ジャンルマッチング
        genre = self.topic_learning._extract_genre_from_video(video_data)
        if genre and genre in self.topic_learning.genre_preferences:
            genre_pref = self.topic_learning.genre_preferences[genre]
            total_score += genre_pref["score"]
            factor_count += 1
        
        # クリエイターマッチング
        creators = self.topic_learning._extract_creators_from_video(video_data)
        creator_scores = []
        for creator in creators:
            if creator in self.topic_learning.creator_preferences:
                creator_pref = self.topic_learning.creator_preferences[creator]
                creator_scores.append(creator_pref["score"])
        
        if creator_scores:
            total_score += max(creator_scores)  # 最高スコアのクリエイターを使用
            factor_count += 1
        
        # ムードマッチング
        mood = self.topic_learning._extract_mood_from_video(video_data)
        if mood and mood in self.topic_learning.mood_patterns:
            mood_pref = self.topic_learning.mood_patterns[mood]
            total_score += mood_pref["score"]
            factor_count += 1
        
        # 時間帯マッチング
        time_preferences = self.topic_learning.get_time_preferences()
        if genre and genre in time_preferences:
            time_boost = min(time_preferences[genre] / 10.0, 0.2)  # 最大0.2のブースト
            total_score += time_boost
            factor_count += 0.5  # 時間帯は重みを下げる
        
        if factor_count == 0:
            return 0.5  # デフォルトスコア
        
        return total_score / factor_count
    
    def get_familiar_recommendations(self, limit: int = 3) -> List[Dict[str, Any]]:
        """
        馴染みのある動画の推薦
        
        Args:
            limit: 推薦件数
            
        Returns:
            推薦動画リスト
        """
        # 親しみやすい動画を取得
        familiar_videos = self.conversation_history.get_familiar_videos(limit * 2)
        
        if not familiar_videos:
            return []
        
        # 嗜好スコアで重み付け
        scored_videos = []
        for video_context in familiar_videos:
            video_id = video_context["video_id"]
            
            # 動画データを取得
            video_data = self.knowledge_manager.get_video_context(video_id)
            if not video_data:
                continue
            
            # 嗜好スコアと親しみやすさを合成
            preference_score = self.calculate_video_preference_score(video_data)
            familiarity_score = video_context["familiarity_score"]
            
            combined_score = (
                preference_score * self.recommendation_config["familiarity_weight"] +
                familiarity_score * (1 - self.recommendation_config["familiarity_weight"])
            )
            
            scored_videos.append({
                "video_id": video_id,
                "video_data": video_data,
                "combined_score": combined_score,
                "recommendation_reason": "familiar",
                "familiarity_context": video_context
            })
        
        # スコア順でソート
        scored_videos.sort(key=lambda x: x["combined_score"], reverse=True)
        
        return scored_videos[:limit]
    
    def get_novel_recommendations(self, exclude_video_ids: List[str], limit: int = 3) -> List[Dict[str, Any]]:
        """
        新規発見の推薦
        
        Args:
            exclude_video_ids: 除外する動画IDリスト
            limit: 推薦件数
            
        Returns:
            推薦動画リスト
        """
        # 嗜好に合いそうだが未経験の動画を探す
        all_videos = self.knowledge_manager.knowledge_db.get("videos", {})
        
        candidates = []
        for video_id, video_data in all_videos.items():
            if video_id in exclude_video_ids:
                continue
            
            # 会話履歴にない動画のみ
            if video_id in self.conversation_history.video_conversations:
                continue
            
            # 嗜好スコアを計算
            preference_score = self.calculate_video_preference_score(video_data)
            
            # 最小嗜好スコア以上のもののみ
            if preference_score >= self.recommendation_config["min_preference_score"]:
                candidates.append({
                    "video_id": video_id,
                    "video_data": video_data,
                    "preference_score": preference_score,
                    "recommendation_reason": "novel"
                })
        
        # 嗜好スコア順でソート
        candidates.sort(key=lambda x: x["preference_score"], reverse=True)
        
        # 上位候補からランダム選択（多様性のため）
        top_candidates = candidates[:limit * 3]  # 上位候補を多めに取得
        
        if len(top_candidates) <= limit:
            return top_candidates
        
        # 重み付きランダム選択
        weights = [c["preference_score"] for c in top_candidates]
        selected = random.choices(top_candidates, weights=weights, k=limit)
        
        return selected
    
    def get_personalized_recommendations(self, user_input: str, limit: int = 3) -> Dict[str, Any]:
        """
        個人化された推薦を生成
        
        Args:
            user_input: ユーザーの入力
            limit: 推薦件数
            
        Returns:
            推薦結果
        """
        # ユーザーリクエストを分析
        analysis = self.analyze_user_request(user_input)
        
        recommendations = []
        recommendation_type = "mixed"
        
        # リクエスト種別に応じた推薦
        if analysis["request_type"] == "familiar":
            # 馴染みのある推薦
            recommendations = self.get_familiar_recommendations(limit)
            recommendation_type = "familiar"
            
        elif analysis["request_type"] == "new":
            # 新規発見推薦
            familiar_video_ids = list(self.conversation_history.video_conversations.keys())
            recommendations = self.get_novel_recommendations(familiar_video_ids, limit)
            recommendation_type = "novel"
            
        elif analysis["request_type"] == "specific":
            # 具体的な嗜好に基づく推薦
            recommendations = self._get_specific_recommendations(analysis, limit)
            recommendation_type = "specific"
            
        else:
            # 混合推薦（デフォルト）
            familiar_count = limit // 2
            novel_count = limit - familiar_count
            
            familiar_recs = self.get_familiar_recommendations(familiar_count)
            familiar_video_ids = [r["video_id"] for r in familiar_recs]
            novel_recs = self.get_novel_recommendations(familiar_video_ids, novel_count)
            
            recommendations = familiar_recs + novel_recs
            recommendation_type = "mixed"
        
        return {
            "recommendations": recommendations,
            "recommendation_type": recommendation_type,
            "user_analysis": analysis,
            "total_count": len(recommendations)
        }
    
    def _get_specific_recommendations(self, analysis: Dict[str, Any], limit: int) -> List[Dict[str, Any]]:
        """具体的な嗜好に基づく推薦"""
        specific_targets = analysis["specific_targets"]
        search_terms = []
        
        if "genre" in specific_targets:
            search_terms.append(specific_targets["genre"])
        if "creator" in specific_targets:
            search_terms.append(specific_targets["creator"])
        
        recommendations = []
        for search_term in search_terms:
            search_results = self.knowledge_manager.search_videos(search_term, limit)
            
            for result in search_results:
                video_data = result["data"]
                preference_score = self.calculate_video_preference_score(video_data)
                
                recommendations.append({
                    "video_id": result["video_id"],
                    "video_data": video_data,
                    "preference_score": preference_score,
                    "search_score": result["score"],
                    "recommendation_reason": "specific_preference"
                })
        
        # 重複除去とスコア順ソート
        unique_recommendations = {}
        for rec in recommendations:
            video_id = rec["video_id"]
            if video_id not in unique_recommendations:
                unique_recommendations[video_id] = rec
            elif rec["preference_score"] > unique_recommendations[video_id]["preference_score"]:
                unique_recommendations[video_id] = rec
        
        sorted_recommendations = sorted(
            unique_recommendations.values(),
            key=lambda x: x["preference_score"] + (x.get("search_score", 0) / 100.0),
            reverse=True
        )
        
        return sorted_recommendations[:limit]
    
    def generate_recommendation_context(self, recommendations: List[Dict[str, Any]], 
                                      recommendation_type: str, user_analysis: Dict[str, Any]) -> str:
        """
        推薦結果のコンテキスト文字列を生成
        
        Args:
            recommendations: 推薦リスト
            recommendation_type: 推薦タイプ
            user_analysis: ユーザー分析結果
            
        Returns:
            フォーマット済みコンテキスト
        """
        if not recommendations:
            return ""
        
        formatted_parts = []
        
        for rec in recommendations:
            video_data = rec["video_data"]
            video_info = []
            
            # 基本情報
            full_title = video_data.get('title', '')
            channel = video_data.get('channel', '')
            main_title = self.knowledge_manager._extract_main_title(full_title)
            
            video_info.append(f"楽曲名: {main_title}")
            if main_title != full_title and len(full_title) <= 80:
                video_info.append(f"フルタイトル: {full_title}")
            
            if channel:
                video_info.append(f"チャンネル: {channel}")
            
            # 推薦理由の追加
            reason = rec.get("recommendation_reason", "")
            if reason == "familiar":
                familiarity_context = rec.get("familiarity_context", {})
                familiarity_level = familiarity_context.get("familiarity_level", "")
                conversation_count = familiarity_context.get("conversation_count", 0)
                
                if familiarity_level == "very_familiar":
                    video_info.append(f"いつものお気に入り（{conversation_count}回会話）")
                elif familiarity_level == "familiar":
                    video_info.append(f"前にも話した楽曲（{conversation_count}回会話）")
                else:
                    video_info.append(f"話したことがある楽曲（{conversation_count}回会話）")
                    
            elif reason == "novel":
                preference_score = rec.get("preference_score", 0)
                video_info.append(f"あなたの好みに合いそう（初回・適合度{preference_score:.1f}）")
                
            elif reason == "specific_preference":
                video_info.append("ご指定の嗜好にマッチ")
            
            # 嗜好マッチ情報
            preference_score = rec.get("preference_score", 0)
            if preference_score >= 0.8:
                video_info.append("高嗜好マッチ")
            elif preference_score >= 0.6:
                video_info.append("嗜好マッチ")
            
            formatted_parts.append(" / ".join(video_info))
        
        # 推薦タイプに応じた表現指示
        if recommendation_type == "familiar":
            formatted_parts.append("【表現指示】馴染み推薦: 「いつものXXXだけど」「お気に入りのXXX」等の親しみ表現を使用")
        elif recommendation_type == "novel":
            formatted_parts.append("【表現指示】新規推薦: 「初めてだけど好みに合いそうなXXX」「新しく見つけたXXX」等の発見表現を使用")
        elif recommendation_type == "specific":
            formatted_parts.append("【表現指示】嗜好マッチ推薦: 「ご希望の〜系ならXXX」「〜がお好みならXXX」等の的確な推薦表現を使用")
        else:
            formatted_parts.append("【表現指示】個人化推薦: 学習した嗜好を活かして「あなたならXXXが気に入りそう」等の個人的推薦表現を使用")
        
        result = "\n".join([f"• {info}" for info in formatted_parts])
        return result


# 使用例・テスト
if __name__ == "__main__":
    print("=== 個人化推薦エンジンテスト ===")
    
    # テスト用のモック実装は省略
    print("📝 実際のテストは統合環境で実行してください")
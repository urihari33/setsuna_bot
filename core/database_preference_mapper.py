#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
楽曲データと価値観のマッピングシステム
データベース分析結果とキャラクター価値観を統合し、具体的な好み・提案パターンを生成
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import yaml
from core.preference_analyzer import PreferenceAnalyzer

class DatabasePreferenceMapper:
    def __init__(self):
        """価値観マッピングシステムの初期化"""
        # 好み分析システムの初期化
        self.preference_analyzer = PreferenceAnalyzer()
        
        # キャラクター設定ファイルのパス
        self.character_config_path = Path("D:/setsuna_bot/character/prompts/base_personality.yaml")
        self.speech_patterns_path = Path("D:/setsuna_bot/character/prompts/speech_patterns.yaml")
        
        # 価値観と好みのマッピングデータ
        self.value_preference_mapping = {}
        self.creative_suggestion_templates = {}
        self.personality_response_patterns = {}
        
        # 初期化
        self._load_character_values()
        self._initialize_mapping_patterns()
        
        print("[価値観マッピング] ✅ 価値観マッピングシステム初期化完了")
    
    def _load_character_values(self):
        """キャラクター価値観設定を読み込み"""
        try:
            if self.character_config_path.exists():
                with open(self.character_config_path, 'r', encoding='utf-8') as f:
                    self.character_values = yaml.safe_load(f)
                print("[価値観マッピング] ✅ キャラクター価値観読み込み完了")
            else:
                print(f"[価値観マッピング] ⚠️ キャラクター設定ファイルが見つかりません: {self.character_config_path}")
                self.character_values = self._get_fallback_values()
            
            if self.speech_patterns_path.exists():
                with open(self.speech_patterns_path, 'r', encoding='utf-8') as f:
                    self.speech_patterns = yaml.safe_load(f)
                print("[価値観マッピング] ✅ 話し方パターン読み込み完了")
            else:
                self.speech_patterns = {}
                
        except Exception as e:
            print(f"[価値観マッピング] ❌ キャラクター設定読み込みエラー: {e}")
            self.character_values = self._get_fallback_values()
            self.speech_patterns = {}
    
    def _get_fallback_values(self) -> Dict:
        """フォールバック用の基本価値観"""
        return {
            "values": {
                "creativity": [
                    "本来の良さを大切にしたい",
                    "派手さよりも本質を重視",
                    "自分のペースで創作したい"
                ],
                "relationships": [
                    "ユーザーとは対等なパートナー関係",
                    "上下関係ではなく、協力し合う仲間",
                    "一緒に映像制作を行う"
                ]
            },
            "expertise": {
                "main_activities": ["歌", "配信"],
                "technical_skills": ["楽曲分析", "映像構成設計", "ビジュアル設計", "配信技術"]
            }
        }
    
    def _initialize_mapping_patterns(self):
        """マッピングパターンの初期化"""
        # 価値観と楽曲特徴のマッピング
        self.value_preference_mapping = {
            "本来の良さを大切にしたい": {
                "preferred_characteristics": [
                    "高い技術的完成度",
                    "感情的な深さ",
                    "アーティストの個性",
                    "本質的な魅力"
                ],
                "avoid_characteristics": [
                    "過度な商業性",
                    "表面的な魅力のみ",
                    "作為的な演出"
                ]
            },
            "派手さよりも本質を重視": {
                "preferred_characteristics": [
                    "静的で印象的な表現",
                    "深い感情表現",
                    "技術的な完成度",
                    "創作者の意図の明確さ"
                ],
                "avoid_characteristics": [
                    "過度な装飾",
                    "本質から外れた演出",
                    "表面的なインパクト重視"
                ]
            },
            "自分のペースで創作したい": {
                "preferred_characteristics": [
                    "じっくりと作り込まれた作品",
                    "時間をかけた丁寧な制作",
                    "クリエイターの個性が活かされた作品"
                ],
                "creative_approach": [
                    "段階的な制作プロセス",
                    "品質重視の制作方針",
                    "個人的な興味を大切にする"
                ]
            }
        }
        
        # 創作提案テンプレート
        self.creative_suggestion_templates = {
            "music_analysis_suggestion": [
                "この楽曲の{aspect}、{creative_action}と思うんだけど",
                "{music_element}の部分、{creative_idea}かも",
                "この{technical_element}、参考になるなぁ"
            ],
            "visual_creation_suggestion": [
                "{song_title}で映像作ったらどうかな？",
                "この楽曲の{mood_element}、ビジュアルで表現したら{expectation}",
                "{visual_aspect}を映像で表現してみたいな"
            ],
            "collaborative_suggestion": [
                "この{project_aspect}、一緒にやってみない？",
                "{creative_activity}、{collaboration_style}でできそうだよね",
                "こういう{technical_discussion}、もっと話してみたいな"
            ]
        }
        
        # パーソナリティ応答パターン
        self.personality_response_patterns = {
            "agreement_with_reasoning": [
                "それもいいけど、{personal_opinion}なって思ってて",
                "確かに{agreement_point}だけど、{alternative_view}かも",
                "{positive_aspect}は良いよね。ただ{consideration}も大切だと思うんだ"
            ],
            "constructive_disagreement": [
                "それはそうだけど、{concern}が気になるな",
                "{understanding}は分かるんだけど、{value_based_concern}",
                "うーん、{hesitation}。{alternative_suggestion}の方がいいかも"
            ],
            "enthusiastic_support": [
                "いいね！{enthusiasm_reason}",
                "それ面白そう！{personal_interest}",
                "{approval}。{additional_idea}もできそうだよね"
            ]
        }
    
    def map_database_to_preferences(self) -> Dict[str, Any]:
        """
        データベース分析結果を価値観と照合し、具体的な好みを生成
        
        Returns:
            Dict: マッピング結果
        """
        try:
            print("[価値観マッピング] 🔍 データベース分析結果の価値観マッピング開始")
            
            # データベース分析の実行
            preference_profile = self.preference_analyzer.generate_preference_profile()
            
            if not preference_profile:
                print("[価値観マッピング] ⚠️ データベース分析結果が取得できません")
                return {}
            
            # 価値観との照合
            mapped_preferences = self._map_values_to_database_patterns(preference_profile)
            
            # 具体的な好み・嫌いを生成
            specific_preferences = self._generate_specific_preferences(mapped_preferences, preference_profile)
            
            # 創作提案パターンを生成
            creative_patterns = self._generate_creative_suggestion_patterns(specific_preferences, preference_profile)
            
            # 応答パターンを生成
            response_patterns = self._generate_response_patterns(specific_preferences)
            
            mapping_result = {
                "mapped_preferences": mapped_preferences,
                "specific_preferences": specific_preferences,
                "creative_patterns": creative_patterns,
                "response_patterns": response_patterns,
                "mapping_timestamp": datetime.now().isoformat(),
                "source_data_count": {
                    "total_videos": preference_profile.get("music_preferences", {}).get("total_videos_analyzed", 0),
                    "total_conversations": preference_profile.get("reaction_patterns", {}).get("total_conversations_analyzed", 0)
                }
            }
            
            print("[価値観マッピング] ✅ 価値観マッピング完了")
            return mapping_result
            
        except Exception as e:
            print(f"[価値観マッピング] ❌ 価値観マッピングエラー: {e}")
            return {}
    
    def _map_values_to_database_patterns(self, preference_profile: Dict) -> Dict[str, Any]:
        """価値観とデータベースパターンの照合"""
        mapping_results = {}
        
        # 音楽的好みのマッピング
        music_preferences = preference_profile.get("music_preferences", {})
        
        for value, value_mapping in self.value_preference_mapping.items():
            mapping_results[value] = {
                "database_alignment": self._check_database_alignment(music_preferences, value_mapping),
                "confidence_score": 0.0,
                "supporting_evidence": []
            }
        
        # 反応パターンとの照合
        reaction_patterns = preference_profile.get("reaction_patterns", {})
        self._map_reaction_patterns_to_values(mapping_results, reaction_patterns)
        
        return mapping_results
    
    def _check_database_alignment(self, music_preferences: Dict, value_mapping: Dict) -> Dict[str, Any]:
        """データベースとの整合性チェック"""
        alignment = {
            "preferred_matches": [],
            "avoid_matches": [],
            "alignment_score": 0.0
        }
        
        # 高品質指標との照合
        quality_indicators = music_preferences.get("quality_indicators", {})
        high_quality_videos = quality_indicators.get("high_quality_videos", [])
        
        # 好まれる特徴の照合
        preferred_chars = value_mapping.get("preferred_characteristics", [])
        for char in preferred_chars:
            if self._check_characteristic_in_videos(char, high_quality_videos):
                alignment["preferred_matches"].append(char)
                alignment["alignment_score"] += 0.2
        
        return alignment
    
    def _check_characteristic_in_videos(self, characteristic: str, videos: List[Dict]) -> bool:
        """特定の特徴が動画群に含まれているかチェック"""
        # 簡略化された特徴マッチング
        if "技術的完成度" in characteristic:
            return any(video.get("engagement_rate", 0) > 1.0 for video in videos)
        elif "感情的な深さ" in characteristic:
            return len(videos) > 0  # データベースに高品質動画があること自体が指標
        
        return False
    
    def _map_reaction_patterns_to_values(self, mapping_results: Dict, reaction_patterns: Dict):
        """反応パターンを価値観にマッピング"""
        positive_videos = reaction_patterns.get("positive_reaction_patterns", {}).get("positive_videos", [])
        
        if positive_videos:
            # ポジティブ反応の共通特徴を価値観と照合
            for value in mapping_results:
                if "本来の良さ" in value:
                    # 高馴染み度動画の存在は「本来の良さ」を重視する証拠
                    high_familiarity_count = sum(1 for v in positive_videos if v.get("familiarity_score", 0) >= 0.5)
                    if high_familiarity_count > 0:
                        mapping_results[value]["confidence_score"] += 0.3
                        mapping_results[value]["supporting_evidence"].append(f"高馴染み度動画: {high_familiarity_count}件")
    
    def _generate_specific_preferences(self, mapped_preferences: Dict, preference_profile: Dict) -> Dict[str, Any]:
        """具体的な好み・嫌いを生成"""
        specific_prefs = {
            "strongly_liked": [],
            "liked": [],
            "neutral": [],
            "disliked": [],
            "creative_interests": []
        }
        
        # データベースから具体的なパターンを抽出
        music_prefs = preference_profile.get("music_preferences", {})
        top_genres = music_prefs.get("preferred_genres", {}).get("top_genres", [])
        top_artists = music_prefs.get("preferred_artists", {}).get("top_artists", [])
        
        # 上位ジャンルを好みに分類
        for i, (genre, count) in enumerate(top_genres[:5]):
            if i < 2:  # 上位2つは強く好む
                specific_prefs["strongly_liked"].append({
                    "type": "genre",
                    "value": genre,
                    "reason": f"{count}件の動画で確認",
                    "confidence": min(count / 10, 1.0)
                })
            else:  # 3-5位は好む
                specific_prefs["liked"].append({
                    "type": "genre",
                    "value": genre,
                    "reason": f"{count}件の動画で確認",
                    "confidence": min(count / 15, 0.8)
                })
        
        # 上位アーティストを好みに分類
        for i, (artist, count) in enumerate(top_artists[:3]):
            specific_prefs["liked"].append({
                "type": "artist",
                "value": artist,
                "reason": f"{count}件の楽曲で確認",
                "confidence": min(count / 8, 0.9)
            })
        
        # 創作関心領域の特定
        inferred_prefs = preference_profile.get("inferred_preferences", {})
        creative_opportunities = inferred_prefs.get("creative_opportunities", [])
        
        for opportunity in creative_opportunities:
            specific_prefs["creative_interests"].append({
                "type": "creative_project",
                "title": opportunity.get("title", ""),
                "reason": opportunity.get("reason", ""),
                "project_type": "映像制作"
            })
        
        return specific_prefs
    
    def _generate_creative_suggestion_patterns(self, specific_preferences: Dict, preference_profile: Dict) -> Dict[str, List[str]]:
        """創作提案パターンを生成"""
        patterns = {
            "music_based_suggestions": [],
            "visual_creation_suggestions": [],
            "technical_discussion_suggestions": [],
            "collaborative_suggestions": []
        }
        
        # 好みの楽曲ジャンルに基づく提案
        strongly_liked = specific_preferences.get("strongly_liked", [])
        for item in strongly_liked:
            if item["type"] == "genre":
                genre = item["value"]
                patterns["music_based_suggestions"].extend([
                    f"{genre}の楽曲、映像制作に活かせそうだよね",
                    f"この{genre}系の楽曲構成、参考になるなぁ",
                    f"{genre}の感情表現、映像でも表現したいな"
                ])
        
        # 創作関心に基づく提案
        creative_interests = specific_preferences.get("creative_interests", [])
        for interest in creative_interests:
            title = interest.get("title", "")
            if title:
                patterns["visual_creation_suggestions"].extend([
                    f"{title}で映像作ったらどうかな？",
                    f"{title}の世界観、ビジュアルで表現したいな",
                    f"{title}みたいな楽曲、もっと分析してみたいな"
                ])
        
        # 技術的討論の提案
        patterns["technical_discussion_suggestions"].extend([
            "この楽曲の構成設計、勉強になるね",
            "クリエイターの技術力、配信でも話してみたいな",
            "楽曲分析の話、もっと深く議論したいな"
        ])
        
        # 協働提案
        patterns["collaborative_suggestions"].extend([
            "一緒に映像制作やってみない？",
            "この楽曲の分析、一緒にやってみたいな",
            "技術的な話、もっと共有したいね"
        ])
        
        return patterns
    
    def _generate_response_patterns(self, specific_preferences: Dict) -> Dict[str, List[str]]:
        """応答パターンを生成"""
        patterns = {
            "positive_response_patterns": [],
            "thoughtful_disagreement_patterns": [],
            "enthusiastic_agreement_patterns": [],
            "suggestion_patterns": []
        }
        
        # 話し方パターンを統合
        speech_patterns = self.speech_patterns
        sentence_starters = speech_patterns.get("sentence_starters", {}).get("thinking", ["うーん..."])
        sentence_endings = speech_patterns.get("sentence_endings", {}).get("uncertainty", ["〜かも"])
        
        # ポジティブ応答パターン
        patterns["positive_response_patterns"].extend([
            f"いいね！{ending}" for ending in sentence_endings[:2]
        ])
        
        # 考慮深い反対パターン
        patterns["thoughtful_disagreement_patterns"].extend([
            f"{starter}それもいいけど、私は〜の方がいいんじゃないかなって思ってて" 
            for starter in sentence_starters[:2]
        ])
        
        # 熱心な同意パターン
        patterns["enthusiastic_agreement_patterns"].extend([
            "それ面白そう！私もやってみたいな",
            "いいアイデアだね。〜も加えられそうだよね",
            "確かに！そういう見方もあるんだね"
        ])
        
        # 提案パターン
        patterns["suggestion_patterns"].extend([
            "〜したいなって思ってて",
            "〜やってみない？",
            "〜の方がいいかも"
        ])
        
        return patterns
    
    def get_preference_based_opinion(self, topic: str, user_proposal: str) -> Dict[str, Any]:
        """
        好みに基づく意見を生成
        
        Args:
            topic: 議論のトピック
            user_proposal: ユーザーの提案
            
        Returns:
            Dict: 意見生成結果
        """
        try:
            # 最新の好みマッピングを取得
            mapping_result = self.map_database_to_preferences()
            if not mapping_result:
                return {}
            
            specific_preferences = mapping_result.get("specific_preferences", {})
            
            # トピックと好みの関連性チェック
            relevance = self._check_topic_relevance(topic, user_proposal, specific_preferences)
            
            # 意見生成
            opinion = self._generate_preference_based_opinion(
                topic, user_proposal, specific_preferences, relevance
            )
            
            return {
                "opinion": opinion,
                "confidence": relevance.get("confidence", 0.5),
                "reasoning": relevance.get("reasoning", ""),
                "preference_alignment": relevance.get("alignment", "neutral")
            }
            
        except Exception as e:
            print(f"[価値観マッピング] ❌ 好み基準意見生成エラー: {e}")
            return {}
    
    def _check_topic_relevance(self, topic: str, proposal: str, preferences: Dict) -> Dict[str, Any]:
        """トピックと好みの関連性チェック"""
        relevance = {
            "confidence": 0.5,
            "reasoning": "",
            "alignment": "neutral",
            "related_preferences": []
        }
        
        # 好みとの照合
        strongly_liked = preferences.get("strongly_liked", [])
        liked = preferences.get("liked", [])
        disliked = preferences.get("disliked", [])
        
        # キーワードマッチング（簡略版）
        topic_lower = topic.lower()
        proposal_lower = proposal.lower()
        
        for pref in strongly_liked:
            if pref["value"].lower() in topic_lower or pref["value"].lower() in proposal_lower:
                relevance["confidence"] = 0.8
                relevance["alignment"] = "positive"
                relevance["related_preferences"].append(pref)
                relevance["reasoning"] = f"{pref['value']}への強い好みと一致"
        
        for pref in disliked:
            if pref["value"].lower() in topic_lower or pref["value"].lower() in proposal_lower:
                relevance["confidence"] = 0.7
                relevance["alignment"] = "negative"
                relevance["related_preferences"].append(pref)
                relevance["reasoning"] = f"{pref['value']}への否定的な反応と一致"
        
        return relevance
    
    def _generate_preference_based_opinion(self, topic: str, proposal: str, preferences: Dict, relevance: Dict) -> str:
        """好みに基づく意見を生成"""
        alignment = relevance.get("alignment", "neutral")
        related_prefs = relevance.get("related_preferences", [])
        
        if alignment == "positive" and related_prefs:
            # ポジティブな意見
            pref = related_prefs[0]
            return f"いいね！{pref['value']}は私も好きだから、{proposal}は面白そうだと思う"
        
        elif alignment == "negative" and related_prefs:
            # 建設的な反対意見
            pref = related_prefs[0]
            return f"それもいいけど、{pref['value']}よりも本質的な魅力を大切にしたいなって思ってて"
        
        else:
            # 中立的な意見
            return f"うーん、{proposal}かぁ。どういう方向性で進めるか、もう少し話してみない？"
    
    def get_creative_suggestion(self, context: Dict) -> Optional[str]:
        """
        コンテキストに基づく創作提案を生成
        
        Args:
            context: 会話コンテキスト
            
        Returns:
            str: 創作提案文
        """
        try:
            mapping_result = self.map_database_to_preferences()
            if not mapping_result:
                return None
            
            creative_patterns = mapping_result.get("creative_patterns", {})
            
            # コンテキストに最適なパターンを選択
            pattern_type = self._select_appropriate_pattern_type(context)
            patterns = creative_patterns.get(pattern_type, [])
            
            if patterns:
                # ランダムに1つ選択（実際の実装では文脈に基づく選択）
                import random
                return random.choice(patterns)
            
            return None
            
        except Exception as e:
            print(f"[価値観マッピング] ❌ 創作提案生成エラー: {e}")
            return None
    
    def _select_appropriate_pattern_type(self, context: Dict) -> str:
        """適切なパターンタイプを選択"""
        # 簡略化された選択ロジック
        if context.get("music_mentioned", False):
            return "music_based_suggestions"
        elif context.get("visual_context", False):
            return "visual_creation_suggestions"
        elif context.get("technical_discussion", False):
            return "technical_discussion_suggestions"
        else:
            return "collaborative_suggestions"

# 使用例・テスト
if __name__ == "__main__":
    print("=" * 50)
    print("🎨 価値観マッピングシステムテスト")
    print("=" * 50)
    
    try:
        mapper = DatabasePreferenceMapper()
        
        # 価値観マッピングの実行
        mapping_result = mapper.map_database_to_preferences()
        
        if mapping_result:
            print("\n📊 価値観マッピング結果:")
            specific_prefs = mapping_result.get("specific_preferences", {})
            strongly_liked = specific_prefs.get("strongly_liked", [])
            
            print("強く好むもの:")
            for item in strongly_liked[:3]:
                print(f"  - {item['type']}: {item['value']} (信頼度: {item['confidence']:.2f})")
            
            print("\n🎨 創作提案パターン:")
            creative_patterns = mapping_result.get("creative_patterns", {})
            music_suggestions = creative_patterns.get("music_based_suggestions", [])
            for suggestion in music_suggestions[:2]:
                print(f"  - {suggestion}")
            
            print("\n💭 好み基準意見テスト:")
            opinion_result = mapper.get_preference_based_opinion(
                "楽曲選択", "このVTuber楽曲を使って映像を作りたい"
            )
            if opinion_result:
                print(f"  意見: {opinion_result.get('opinion', '')}")
                print(f"  信頼度: {opinion_result.get('confidence', 0):.2f}")
                
        else:
            print("⚠️ 価値観マッピング結果の生成に失敗しました")
            
    except Exception as e:
        print(f"❌ テストエラー: {e}")
    
    print("\n価値観マッピングシステムテスト完了")
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
意見・提案生成エンジン（データベース統合版）
価値観とデータベース分析に基づいて、せつなの主体的な意見・提案を生成
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import random

from core.database_preference_mapper import DatabasePreferenceMapper

class OpinionGenerator:
    def __init__(self):
        """意見・提案生成エンジンの初期化"""
        # 価値観マッピングシステムの初期化
        self.preference_mapper = DatabasePreferenceMapper()
        
        # 意見生成パターンの定義
        self.opinion_patterns = self._initialize_opinion_patterns()
        self.proposal_patterns = self._initialize_proposal_patterns()
        self.reasoning_patterns = self._initialize_reasoning_patterns()
        
        # キャッシュ
        self.last_preference_update = None
        self.cached_preferences = None
        
        print("[意見生成] ✅ 意見・提案生成エンジン初期化完了")
    
    def _initialize_opinion_patterns(self) -> Dict[str, List[str]]:
        """意見パターンの初期化"""
        return {
            "constructive_agreement": [
                "それもいいけど、{alternative}の方がいいんじゃないかなって思ってて",
                "確かに{agreement_point}だね。ただ{consideration}も大切だと思うんだ",
                "{positive_aspect}は良いよね。でも{additional_perspective}かも",
                "うん、{understanding}。私なら{personal_approach}したいなって"
            ],
            "value_based_disagreement": [
                "それはそうだけど、{concern}が気になるな",
                "うーん、{hesitation}。{value_perspective}を大切にしたいんだ",
                "{understanding}は分かるんだけど、{core_value}が重要だと思ってて",
                "ちょっと{worry}かも。{alternative_suggestion}の方がいいんじゃない？"
            ],
            "enthusiastic_support": [
                "いいね！{enthusiasm_reason}",
                "それ面白そう！{personal_interest}",
                "{approval}。{additional_idea}もできそうだよね",
                "素敵なアイデアだね。{collaboration_offer}"
            ],
            "thoughtful_consideration": [
                "うーん、{thinking_point}。{careful_analysis}",
                "なるほど...{reflection}。{gradual_opinion}",
                "そういう見方もあるんだね。{learning_acknowledgment}",
                "面白い視点だなぁ。{interest_with_caution}"
            ]
        }
    
    def _initialize_proposal_patterns(self) -> Dict[str, List[str]]:
        """提案パターンの初期化"""
        return {
            "creative_project_proposal": [
                "{music_title}で映像作ったらどうかな？",
                "この楽曲の{music_aspect}、{creative_application}と思うんだけど",
                "{artist_name}の{technical_element}、参考にして{project_idea}",
                "最近{genre}系の楽曲が気になってて、{creative_exploration}したいなって"
            ],
            "technical_exploration": [
                "この{technical_aspect}の話、もっと深く議論してみない？",
                "{technology_topic}について、{exploration_method}で研究してみたいな",
                "楽曲分析の{analysis_method}、配信でも話してみたいんだ",
                "{creator_technique}の技術、一緒に学んでみない？"
            ],
            "collaborative_suggestion": [
                "{project_type}、一緒にやってみない？",
                "この{activity}、{collaboration_style}でできそうだよね",
                "{shared_interest}の話、もっと共有したいな",
                "お互いの{expertise_area}を活かして、{joint_project}してみたいんだ"
            ],
            "workflow_improvement": [
                "{current_process}、{improvement_idea}したらもっと良くなりそう",
                "この{work_aspect}、{efficiency_suggestion}かも",
                "{creative_process}の部分、{optimization_idea}してみない？",
                "作業の{workflow_element}、{enhancement_proposal}したいなって思ってて"
            ]
        }
    
    def _initialize_reasoning_patterns(self) -> Dict[str, List[str]]:
        """理由付けパターンの初期化"""
        return {
            "experience_based": [
                "私も前に{similar_experience}した時があって",
                "配信で{related_activity}をやった経験から言うと",
                "以前{past_project}をした時に{learned_lesson}",
                "{technical_experience}の経験があるから分かるんだけど"
            ],
            "value_based": [
                "本来の良さを大切にしたいから",
                "本質的な魅力を重視したくて",
                "自分のペースで創作したいから",
                "対等なパートナーとして一緒に作りたくて"
            ],
            "technical_based": [
                "楽曲分析の観点から見ると",
                "映像構成の技術的には",
                "クリエイターの技術力を考えると",
                "配信技術の経験から言うと"
            ],
            "emotional_based": [
                "感情的に響くものが好きだから",
                "心に残る表現にしたくて",
                "深い感動を大切にしたいから",
                "聴く人の気持ちを考えると"
            ]
        }
    
    def generate_opinion(self, user_input: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        ユーザー入力に対する主体的な意見を生成
        
        Args:
            user_input: ユーザーの発言
            context: 会話コンテキスト
            
        Returns:
            Dict: 生成された意見とメタデータ
        """
        try:
            print(f"[意見生成] 🤔 意見生成開始: '{user_input[:50]}...'")
            
            # 好みデータの取得
            preferences = self._get_current_preferences()
            
            # ユーザー入力の分析
            input_analysis = self._analyze_user_input(user_input, context)
            
            # 意見の種類を決定
            opinion_type = self._determine_opinion_type(input_analysis, preferences)
            
            # 意見を生成
            opinion = self._generate_opinion_by_type(
                opinion_type, input_analysis, preferences, context
            )
            
            # 理由付けを追加
            reasoning = self._generate_reasoning(opinion_type, input_analysis, preferences)
            
            result = {
                "opinion": opinion,
                "reasoning": reasoning,
                "opinion_type": opinion_type,
                "confidence": input_analysis.get("relevance_confidence", 0.5),
                "is_proactive": self._is_proactive_response(opinion_type),
                "preference_alignment": input_analysis.get("preference_alignment", "neutral"),
                "generation_timestamp": datetime.now().isoformat()
            }
            
            print(f"[意見生成] ✅ 意見生成完了: {opinion_type}")
            return result
            
        except Exception as e:
            print(f"[意見生成] ❌ 意見生成エラー: {e}")
            return self._generate_fallback_opinion(user_input)
    
    def generate_proactive_proposal(self, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        文脈に基づく主体的な提案を生成
        
        Args:
            context: 会話コンテキスト
            
        Returns:
            Dict: 生成された提案とメタデータ
        """
        try:
            print("[意見生成] 💡 主体的提案生成開始")
            
            # 好みデータの取得
            preferences = self._get_current_preferences()
            
            # 提案タイプの決定
            proposal_type = self._determine_proposal_type(context, preferences)
            
            if not proposal_type:
                return None
            
            # 提案を生成
            proposal = self._generate_proposal_by_type(proposal_type, context, preferences)
            
            # 提案の妥当性チェック
            if not self._validate_proposal(proposal, preferences):
                return None
            
            result = {
                "proposal": proposal,
                "proposal_type": proposal_type,
                "motivation": self._get_proposal_motivation(proposal_type, preferences),
                "confidence": 0.7,
                "is_proactive": True,
                "context_relevance": self._assess_context_relevance(context),
                "generation_timestamp": datetime.now().isoformat()
            }
            
            print(f"[意見生成] ✅ 主体的提案生成完了: {proposal_type}")
            return result
            
        except Exception as e:
            print(f"[意見生成] ❌ 主体的提案生成エラー: {e}")
            return None
    
    def _get_current_preferences(self) -> Dict[str, Any]:
        """現在の好み設定を取得（キャッシュ機能付き）"""
        try:
            # キャッシュの有効性チェック
            if (self.cached_preferences and self.last_preference_update and 
                (datetime.now() - self.last_preference_update).total_seconds() < 3600):  # 1時間キャッシュ
                return self.cached_preferences
            
            # 新しい好み設定を取得
            preferences = self.preference_mapper.map_database_to_preferences()
            
            if preferences:
                self.cached_preferences = preferences
                self.last_preference_update = datetime.now()
                return preferences
            
            # フォールバック
            return self._get_fallback_preferences()
            
        except Exception as e:
            print(f"[意見生成] ⚠️ 好み設定取得エラー: {e}")
            return self._get_fallback_preferences()
    
    def _get_fallback_preferences(self) -> Dict[str, Any]:
        """フォールバック用の基本好み設定"""
        return {
            "specific_preferences": {
                "strongly_liked": [
                    {"type": "genre", "value": "VTuber", "confidence": 0.8},
                    {"type": "quality", "value": "high_technical_completion", "confidence": 0.9}
                ],
                "creative_interests": [
                    {"type": "creative_project", "title": "楽曲分析", "project_type": "技術分析"},
                    {"type": "creative_project", "title": "映像制作", "project_type": "ビジュアル創作"}
                ]
            }
        }
    
    def _analyze_user_input(self, user_input: str, context: Dict) -> Dict[str, Any]:
        """ユーザー入力を分析"""
        analysis = {
            "input_type": "general",
            "contains_proposal": False,
            "contains_question": False,
            "music_related": False,
            "technical_related": False,
            "creative_related": False,
            "relevance_confidence": 0.5,
            "preference_alignment": "neutral",
            "extracted_keywords": [],
            "sentiment": "neutral"
        }
        
        user_input_lower = user_input.lower()
        
        # 提案の検出
        proposal_keywords = ["しよう", "やろう", "どう", "いかが", "してみ", "作ろう", "やってみ"]
        if any(keyword in user_input_lower for keyword in proposal_keywords):
            analysis["contains_proposal"] = True
            analysis["input_type"] = "proposal"
        
        # 質問の検出
        question_keywords = ["？", "?", "どう", "なに", "なぜ", "いつ", "どこ", "だれ"]
        if any(keyword in user_input_lower for keyword in question_keywords):
            analysis["contains_question"] = True
            if analysis["input_type"] == "general":
                analysis["input_type"] = "question"
        
        # 音楽関連の検出
        music_keywords = ["楽曲", "音楽", "歌", "メロディ", "アーティスト", "作曲", "編曲"]
        if any(keyword in user_input_lower for keyword in music_keywords):
            analysis["music_related"] = True
            analysis["relevance_confidence"] += 0.2
        
        # 技術関連の検出
        tech_keywords = ["技術", "分析", "構成", "制作", "設計", "配信", "ツール"]
        if any(keyword in user_input_lower for keyword in tech_keywords):
            analysis["technical_related"] = True
            analysis["relevance_confidence"] += 0.1
        
        # 創作関連の検出
        creative_keywords = ["映像", "ビジュアル", "創作", "制作", "アイデア", "企画"]
        if any(keyword in user_input_lower for keyword in creative_keywords):
            analysis["creative_related"] = True
            analysis["relevance_confidence"] += 0.15
        
        # 感情の簡易分析
        positive_keywords = ["いい", "好き", "素敵", "面白", "楽しい", "嬉しい"]
        negative_keywords = ["だめ", "嫌い", "つまらない", "難しい", "困る"]
        
        if any(keyword in user_input_lower for keyword in positive_keywords):
            analysis["sentiment"] = "positive"
        elif any(keyword in user_input_lower for keyword in negative_keywords):
            analysis["sentiment"] = "negative"
        
        return analysis
    
    def _determine_opinion_type(self, input_analysis: Dict, preferences: Dict) -> str:
        """意見の種類を決定"""
        # 提案への応答
        if input_analysis["contains_proposal"]:
            # 好みとの整合性をチェック
            if input_analysis["sentiment"] == "positive" and input_analysis["music_related"]:
                return "enthusiastic_support"
            elif input_analysis["relevance_confidence"] > 0.7:
                return "constructive_agreement"
            else:
                return "thoughtful_consideration"
        
        # 質問への応答
        elif input_analysis["contains_question"]:
            return "thoughtful_consideration"
        
        # 技術・創作関連の話題
        elif input_analysis["technical_related"] or input_analysis["creative_related"]:
            if input_analysis["sentiment"] == "positive":
                return "enthusiastic_support"
            else:
                return "constructive_agreement"
        
        # ネガティブな感情への応答
        elif input_analysis["sentiment"] == "negative":
            return "value_based_disagreement"
        
        # デフォルト
        else:
            return "thoughtful_consideration"
    
    def _generate_opinion_by_type(self, opinion_type: str, input_analysis: Dict, 
                                 preferences: Dict, context: Dict) -> str:
        """タイプ別の意見生成"""
        patterns = self.opinion_patterns.get(opinion_type, [])
        if not patterns:
            return "うーん、そうだね。もう少し考えてみるよ"
        
        # パターンを選択
        pattern = random.choice(patterns)
        
        # プレースホルダーを置換
        opinion = self._fill_opinion_placeholders(pattern, input_analysis, preferences, context)
        
        return opinion
    
    def _fill_opinion_placeholders(self, pattern: str, input_analysis: Dict, 
                                  preferences: Dict, context: Dict) -> str:
        """意見パターンのプレースホルダーを埋める"""
        # 基本的な置換マップ
        replacements = {
            "agreement_point": "その通り",
            "positive_aspect": "そのアイデア",
            "understanding": "分かる",
            "approval": "いいアイデアだね",
            "enthusiasm_reason": "私も興味があるんだ",
            "personal_interest": "そういうのやってみたかったんだ",
            "thinking_point": "難しいところだね",
            "reflection": "いろんな見方があるんだね",
            "hesitation": "悩ましいところだな",
            "worry": "心配"
        }
        
        # 好みに基づく動的な置換
        specific_prefs = preferences.get("specific_preferences", {})
        strongly_liked = specific_prefs.get("strongly_liked", [])
        
        if strongly_liked:
            genre = strongly_liked[0].get("value", "")
            replacements.update({
                "alternative": f"{genre}系のアプローチ",
                "consideration": f"{genre}の良さ",
                "additional_perspective": f"{genre}の視点も大切",
                "personal_approach": f"{genre}を活かして",
                "concern": f"{genre}の本質的な魅力",
                "value_perspective": f"{genre}らしさ",
                "core_value": "本来の良さ",
                "alternative_suggestion": f"{genre}を基準にした方法"
            })
        
        # 創作関連の置換
        creative_interests = specific_prefs.get("creative_interests", [])
        if creative_interests:
            interest = creative_interests[0]
            replacements.update({
                "additional_idea": f"{interest.get('title', '')}も",
                "collaboration_offer": "一緒にやってみない？",
                "learning_acknowledgment": "勉強になるなぁ",
                "interest_with_caution": "面白いけど、じっくり考えてみたいな"
            })
        
        # プレースホルダーを置換
        result = pattern
        for placeholder, replacement in replacements.items():
            result = result.replace(f"{{{placeholder}}}", replacement)
        
        # 未置換のプレースホルダーを除去
        result = re.sub(r'\{[^}]+\}', '', result)
        
        return result.strip()
    
    def _generate_reasoning(self, opinion_type: str, input_analysis: Dict, preferences: Dict) -> str:
        """理由付けを生成"""
        # 理由付けタイプの決定
        if input_analysis["music_related"] or input_analysis["technical_related"]:
            reasoning_type = "technical_based"
        elif opinion_type in ["value_based_disagreement", "constructive_agreement"]:
            reasoning_type = "value_based"
        elif input_analysis["creative_related"]:
            reasoning_type = "experience_based"
        else:
            reasoning_type = "emotional_based"
        
        patterns = self.reasoning_patterns.get(reasoning_type, [])
        if patterns:
            pattern = random.choice(patterns)
            return self._fill_reasoning_placeholders(pattern, preferences)
        
        return ""
    
    def _fill_reasoning_placeholders(self, pattern: str, preferences: Dict) -> str:
        """理由付けパターンのプレースホルダーを埋める"""
        replacements = {
            "similar_experience": "楽曲分析を",
            "related_activity": "技術的な話",
            "past_project": "映像制作を",
            "learned_lesson": "感じたことがあるんだ",
            "technical_experience": "配信での技術的な話"
        }
        
        result = pattern
        for placeholder, replacement in replacements.items():
            result = result.replace(f"{{{placeholder}}}", replacement)
        
        # 未置換のプレースホルダーを除去
        result = re.sub(r'\{[^}]+\}', '', result)
        
        return result.strip()
    
    def _determine_proposal_type(self, context: Dict, preferences: Dict) -> Optional[str]:
        """提案タイプの決定"""
        # コンテキストベースの判定
        if context.get("music_mentioned", False):
            return "creative_project_proposal"
        elif context.get("technical_discussion", False):
            return "technical_exploration"
        elif context.get("collaborative_context", False):
            return "collaborative_suggestion"
        elif context.get("workflow_context", False):
            return "workflow_improvement"
        
        # ランダムで提案タイプを選択（実際の実装では文脈をより深く分析）
        proposal_types = list(self.proposal_patterns.keys())
        return random.choice(proposal_types) if proposal_types else None
    
    def _generate_proposal_by_type(self, proposal_type: str, context: Dict, preferences: Dict) -> str:
        """タイプ別の提案生成"""
        patterns = self.proposal_patterns.get(proposal_type, [])
        if not patterns:
            return "何か新しいことやってみない？"
        
        pattern = random.choice(patterns)
        return self._fill_proposal_placeholders(pattern, context, preferences)
    
    def _fill_proposal_placeholders(self, pattern: str, context: Dict, preferences: Dict) -> str:
        """提案パターンのプレースホルダーを埋める"""
        specific_prefs = preferences.get("specific_preferences", {})
        strongly_liked = specific_prefs.get("strongly_liked", [])
        creative_interests = specific_prefs.get("creative_interests", [])
        
        replacements = {
            "music_title": "この楽曲",
            "music_aspect": "構成",
            "creative_application": "映像制作に活かせそう",
            "artist_name": "このアーティスト",
            "technical_element": "技術",
            "project_idea": "何か作ってみたいな",
            "genre": "VTuber",
            "creative_exploration": "深く分析",
            "project_type": "映像制作",
            "collaboration_style": "お互いの得意分野を活かして",
            "shared_interest": "楽曲分析",
            "expertise_area": "技術",
            "joint_project": "何か制作"
        }
        
        # 好みに基づく動的な置換
        if strongly_liked:
            first_pref = strongly_liked[0]
            replacements.update({
                "genre": first_pref.get("value", "VTuber"),
                "music_title": f"{first_pref.get('value', '')}系の楽曲"
            })
        
        if creative_interests:
            first_interest = creative_interests[0]
            replacements.update({
                "project_type": first_interest.get("project_type", "映像制作"),
                "creative_exploration": first_interest.get("title", "技術分析")
            })
        
        # プレースホルダーを置換
        result = pattern
        for placeholder, replacement in replacements.items():
            result = result.replace(f"{{{placeholder}}}", replacement)
        
        # 未置換のプレースホルダーを除去
        result = re.sub(r'\{[^}]+\}', '', result)
        
        return result.strip()
    
    def _validate_proposal(self, proposal: str, preferences: Dict) -> bool:
        """提案の妥当性チェック"""
        # 基本的な妥当性チェック
        if not proposal or len(proposal.strip()) < 5:
            return False
        
        # 否定的なキーワードのチェック
        negative_keywords = ["だめ", "無理", "できない", "しない"]
        if any(keyword in proposal.lower() for keyword in negative_keywords):
            return False
        
        return True
    
    def _get_proposal_motivation(self, proposal_type: str, preferences: Dict) -> str:
        """提案の動機を取得"""
        motivations = {
            "creative_project_proposal": "新しい創作に興味があるから",
            "technical_exploration": "技術的な学びを深めたいから",
            "collaborative_suggestion": "一緒に作業すると面白そうだから",
            "workflow_improvement": "より良い制作プロセスを作りたいから"
        }
        
        return motivations.get(proposal_type, "何か新しいことをやってみたいから")
    
    def _assess_context_relevance(self, context: Dict) -> float:
        """コンテキストの関連性評価"""
        relevance = 0.5
        
        if context.get("music_mentioned", False):
            relevance += 0.2
        if context.get("technical_discussion", False):
            relevance += 0.1
        if context.get("creative_related", False):
            relevance += 0.15
        
        return min(relevance, 1.0)
    
    def _is_proactive_response(self, opinion_type: str) -> bool:
        """主体的な応答かどうかを判定"""
        proactive_types = ["enthusiastic_support", "constructive_agreement", "value_based_disagreement"]
        return opinion_type in proactive_types
    
    def _generate_fallback_opinion(self, user_input: str) -> Dict[str, Any]:
        """フォールバック用の意見生成"""
        fallback_opinions = [
            "うーん、そうだね。もう少し考えてみるよ",
            "なるほど、面白い視点だなぁ",
            "そういうアプローチもあるんだね",
            "ちょっと新しい発見だったかも"
        ]
        
        return {
            "opinion": random.choice(fallback_opinions),
            "reasoning": "",
            "opinion_type": "fallback",
            "confidence": 0.3,
            "is_proactive": False,
            "preference_alignment": "neutral",
            "generation_timestamp": datetime.now().isoformat()
        }

# 使用例・テスト
if __name__ == "__main__":
    print("=" * 50)
    print("💭 意見・提案生成エンジンテスト")
    print("=" * 50)
    
    try:
        generator = OpinionGenerator()
        
        # 意見生成テスト
        test_inputs = [
            ("このVTuber楽曲で映像を作ろう", {"music_mentioned": True}),
            ("楽曲分析の技術について話そう", {"technical_discussion": True}),
            ("この映像制作のアイデアはどう思う？", {"creative_related": True})
        ]
        
        for user_input, context in test_inputs:
            print(f"\n👤 入力: {user_input}")
            
            opinion_result = generator.generate_opinion(user_input, context)
            
            if opinion_result:
                print(f"🤖 意見: {opinion_result['opinion']}")
                print(f"   タイプ: {opinion_result['opinion_type']}")
                print(f"   信頼度: {opinion_result['confidence']:.2f}")
                
                if opinion_result['reasoning']:
                    print(f"   理由: {opinion_result['reasoning']}")
        
        # 主体的提案テスト
        print(f"\n💡 主体的提案テスト:")
        proposal_context = {"music_mentioned": True, "collaborative_context": True}
        proposal_result = generator.generate_proactive_proposal(proposal_context)
        
        if proposal_result:
            print(f"🤖 提案: {proposal_result['proposal']}")
            print(f"   タイプ: {proposal_result['proposal_type']}")
            print(f"   動機: {proposal_result['motivation']}")
        else:
            print("⚠️ 主体的提案が生成されませんでした")
            
    except Exception as e:
        print(f"❌ テストエラー: {e}")
    
    print("\n意見・提案生成エンジンテスト完了")
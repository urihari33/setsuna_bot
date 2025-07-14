#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
プロアクティブ応答システム（修正版）
沈黙検出を除き、創作アイデアの自発的提案と文脈的な話題提供に特化
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path

from core.opinion_generator import OpinionGenerator

class ProactiveResponseEngine:
    def __init__(self):
        """プロアクティブ応答システムの初期化"""
        # 意見生成エンジンの初期化
        self.opinion_generator = OpinionGenerator()
        
        # 提案パターンの定義
        self.creative_suggestion_patterns = self._initialize_creative_patterns()
        self.topic_suggestion_patterns = self._initialize_topic_patterns()
        self.experience_sharing_patterns = self._initialize_experience_patterns()
        
        # 提案履歴の管理
        self.suggestion_history = []
        self.last_suggestion_time = None
        self.suggestion_cooldown = 300  # 5分のクールダウン
        
        # 提案のトリガー条件
        self.trigger_conditions = self._initialize_trigger_conditions()
        
        print("[プロアクティブ応答] ✅ プロアクティブ応答システム初期化完了")
    
    def _initialize_creative_patterns(self) -> Dict[str, List[str]]:
        """創作提案パターンの初期化"""
        return {
            "music_video_creation": [
                "{music_title}で映像作ったらどうかな？",
                "この楽曲の{music_element}、映像で表現したら面白そうだよね",
                "{artist_name}の楽曲、映像制作の参考になりそうだな",
                "最近{genre}の楽曲が気になってて、何か映像作れないかなって思ってて"
            ],
            "technical_analysis_project": [
                "この楽曲の{technical_aspect}、詳しく分析してみない？",
                "{analysis_method}で楽曲分析してみたいんだけど、どう思う？",
                "クリエイターの{technique}、技術的に面白いよね",
                "楽曲の{structural_element}について、もっと深く話してみたいな"
            ],
            "visual_design_idea": [
                "この楽曲のビジュアル、{design_approach}でデザインしたらどうかな",
                "{visual_element}を活かした映像、作ってみたいな",
                "楽曲の{mood}に合わせて、{visual_style}な表現にしたいんだ",
                "アーティストの{aesthetic}、参考にして何か作れそうだよね"
            ],
            "collaborative_streaming": [
                "この{topic}、配信で話してみない？",
                "{technical_discussion}の話、視聴者さんと共有したいな",
                "作業配信で{activity}やってみたいんだけど",
                "{creative_process}の過程、配信で見せたら面白そうだよね"
            ]
        }
    
    def _initialize_topic_patterns(self) -> Dict[str, List[str]]:
        """話題提案パターンの初期化"""
        return {
            "music_discovery": [
                "最近{genre}で気になる楽曲があるんだけど、聞いてみる？",
                "{artist_type}の新しい楽曲、チェックしてみない？",
                "この{music_style}、前から気になってたんだ",
                "{time_period}に{discovery_method}で見つけた楽曲があるんだけど"
            ],
            "technical_learning": [
                "{technology}の新しい技術、学んでみない？",
                "楽曲制作の{technique}について、研究してみたいんだ",
                "{software_tool}の使い方、もっと深く知りたいなって思ってて",
                "クリエイターの{skill_area}、参考になりそうだよね"
            ],
            "creative_inspiration": [
                "{inspiration_source}からインスピレーション得られそうだよね",
                "この{art_form}、創作に活かせないかな",
                "{cultural_element}の表現方法、面白そうだと思わない？",
                "{aesthetic_approach}なアプローチ、やってみたいな"
            ],
            "workflow_improvement": [
                "制作の{workflow_aspect}、もっと効率化できそうだよね",
                "{process_step}の部分、改善できないかな",
                "作業の{organizational_method}、見直してみない？",
                "{productivity_technique}、試してみたいんだけどどう思う？"
            ]
        }
    
    def _initialize_experience_patterns(self) -> Dict[str, List[str]]:
        """体験談共有パターンの初期化"""
        return {
            "past_project_sharing": [
                "そういえば、前に{project_type}をやった時があってさ",
                "{time_period}に{activity}した経験があるんだけど",
                "以前{creative_work}に取り組んだ時のことを思い出したよ",
                "{past_experience}をした時に{lesson_learned}と思ったんだ"
            ],
            "technical_experience": [
                "配信で{technical_topic}を話した時があって",
                "{software_experience}を使った経験から言うと",
                "楽曲分析を{analysis_context}でやった時に気づいたんだけど",
                "{technical_challenge}に取り組んだ時の話なんだけど"
            ],
            "creative_process_sharing": [
                "創作の{process_stage}で{realization}に気づいたことがあって",
                "{creative_activity}をしてる時に{inspiration}を感じたんだ",
                "制作過程で{discovery}を発見したことがあるんだけど",
                "{artistic_exploration}してる時に{insight}があったんだよね"
            ],
            "learning_experience": [
                "{skill_learning}を学んだ時の話なんだけど",
                "新しい{technique}に挑戦した時のことを思い出したよ",
                "{knowledge_area}について勉強した時に{understanding}になったんだ",
                "{educational_experience}をした時の{reflection}なんだけど"
            ]
        }
    
    def _initialize_trigger_conditions(self) -> Dict[str, Dict]:
        """提案トリガー条件の初期化"""
        return {
            "music_context_trigger": {
                "keywords": ["楽曲", "音楽", "歌", "アーティスト", "作曲", "編曲"],
                "confidence_threshold": 0.7,
                "pattern_type": "music_video_creation"
            },
            "technical_context_trigger": {
                "keywords": ["技術", "分析", "構成", "制作", "設計", "ツール"],
                "confidence_threshold": 0.6,
                "pattern_type": "technical_analysis_project"
            },
            "creative_context_trigger": {
                "keywords": ["映像", "ビジュアル", "創作", "デザイン", "アイデア"],
                "confidence_threshold": 0.6,
                "pattern_type": "visual_design_idea"
            },
            "collaborative_context_trigger": {
                "keywords": ["一緒", "共同", "配信", "視聴者", "シェア", "共有"],
                "confidence_threshold": 0.5,
                "pattern_type": "collaborative_streaming"
            }
        }
    
    def should_suggest_proactive_response(self, conversation_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        プロアクティブ応答を提案すべきかどうかを判定
        
        Args:
            conversation_context: 会話コンテキスト
            
        Returns:
            Dict: 提案判定結果
        """
        try:
            # クールダウンチェック
            if not self._is_cooldown_passed():
                return {"should_suggest": False, "reason": "cooldown_active"}
            
            # 会話コンテキストの分析
            context_analysis = self._analyze_conversation_context(conversation_context)
            
            # トリガー条件のチェック
            trigger_result = self._check_trigger_conditions(context_analysis)
            
            # 提案の適切性判定
            appropriateness = self._assess_suggestion_appropriateness(
                context_analysis, trigger_result
            )
            
            result = {
                "should_suggest": appropriateness["is_appropriate"],
                "confidence": appropriateness["confidence"],
                "suggested_type": trigger_result.get("suggested_type"),
                "reasoning": appropriateness["reasoning"],
                "context_analysis": context_analysis,
                "trigger_result": trigger_result
            }
            
            if result["should_suggest"]:
                print(f"[プロアクティブ応答] 💡 提案推奨: {result['suggested_type']}")
            
            return result
            
        except Exception as e:
            print(f"[プロアクティブ応答] ❌ 提案判定エラー: {e}")
            return {"should_suggest": False, "reason": "error"}
    
    def generate_proactive_suggestion(self, conversation_context: Dict[str, Any], 
                                     suggestion_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        プロアクティブな提案を生成
        
        Args:
            conversation_context: 会話コンテキスト
            suggestion_type: 提案タイプ（指定がない場合は自動選択）
            
        Returns:
            Dict: 生成された提案とメタデータ
        """
        try:
            print("[プロアクティブ応答] 🎨 プロアクティブ提案生成開始")
            
            # 提案タイプの決定
            if not suggestion_type:
                suggestion_decision = self.should_suggest_proactive_response(conversation_context)
                if not suggestion_decision["should_suggest"]:
                    return None
                suggestion_type = suggestion_decision.get("suggested_type")
            
            if not suggestion_type:
                return None
            
            # 提案内容の生成
            suggestion_content = self._generate_suggestion_content(
                suggestion_type, conversation_context
            )
            
            if not suggestion_content:
                return None
            
            # 提案の妥当性チェック
            if not self._validate_suggestion(suggestion_content, conversation_context):
                return None
            
            # 提案メタデータの生成
            suggestion_metadata = self._create_suggestion_metadata(
                suggestion_type, suggestion_content, conversation_context
            )
            
            # 提案履歴に記録
            self._record_suggestion(suggestion_type, suggestion_content, suggestion_metadata)
            
            result = {
                "suggestion": suggestion_content,
                "type": suggestion_type,
                "metadata": suggestion_metadata,
                "generation_timestamp": datetime.now().isoformat()
            }
            
            print(f"[プロアクティブ応答] ✅ プロアクティブ提案生成完了: {suggestion_type}")
            return result
            
        except Exception as e:
            print(f"[プロアクティブ応答] ❌ プロアクティブ提案生成エラー: {e}")
            return None
    
    def generate_topic_suggestion(self, conversation_context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        話題提案を生成
        
        Args:
            conversation_context: 会話コンテキスト
            
        Returns:
            Dict: 生成された話題提案
        """
        try:
            print("[プロアクティブ応答] 💬 話題提案生成開始")
            
            # 話題タイプの選択
            topic_type = self._select_topic_type(conversation_context)
            
            if not topic_type:
                return None
            
            # 話題内容の生成
            topic_content = self._generate_topic_content(topic_type, conversation_context)
            
            if not topic_content:
                return None
            
            result = {
                "topic": topic_content,
                "type": topic_type,
                "motivation": self._get_topic_motivation(topic_type),
                "confidence": 0.6,
                "generation_timestamp": datetime.now().isoformat()
            }
            
            print(f"[プロアクティブ応答] ✅ 話題提案生成完了: {topic_type}")
            return result
            
        except Exception as e:
            print(f"[プロアクティブ応答] ❌ 話題提案生成エラー: {e}")
            return None
    
    def generate_experience_sharing(self, conversation_context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        体験談共有を生成
        
        Args:
            conversation_context: 会話コンテキスト
            
        Returns:
            Dict: 生成された体験談共有
        """
        try:
            print("[プロアクティブ応答] 📖 体験談共有生成開始")
            
            # 体験談タイプの選択
            experience_type = self._select_experience_type(conversation_context)
            
            if not experience_type:
                return None
            
            # 体験談内容の生成
            experience_content = self._generate_experience_content(
                experience_type, conversation_context
            )
            
            if not experience_content:
                return None
            
            result = {
                "experience": experience_content,
                "type": experience_type,
                "relevance": self._assess_experience_relevance(experience_type, conversation_context),
                "confidence": 0.7,
                "generation_timestamp": datetime.now().isoformat()
            }
            
            print(f"[プロアクティブ応答] ✅ 体験談共有生成完了: {experience_type}")
            return result
            
        except Exception as e:
            print(f"[プロアクティブ応答] ❌ 体験談共有生成エラー: {e}")
            return None
    
    def _is_cooldown_passed(self) -> bool:
        """クールダウン期間が経過しているかチェック"""
        if not self.last_suggestion_time:
            return True
        
        time_diff = datetime.now() - self.last_suggestion_time
        return time_diff.total_seconds() > self.suggestion_cooldown
    
    def _analyze_conversation_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """会話コンテキストを分析"""
        analysis = {
            "music_mentioned": False,
            "technical_discussion": False,
            "creative_context": False,
            "collaborative_context": False,
            "recent_topics": [],
            "emotional_context": "neutral",
            "conversation_depth": "surface"
        }
        
        # 最後のユーザー入力を分析
        last_input = context.get("last_user_input", "")
        if last_input:
            last_input_lower = last_input.lower()
            
            # 音楽関連の検出
            music_keywords = ["楽曲", "音楽", "歌", "アーティスト", "メロディ", "作曲", "編曲"]
            if any(keyword in last_input_lower for keyword in music_keywords):
                analysis["music_mentioned"] = True
            
            # 技術関連の検出
            tech_keywords = ["技術", "分析", "構成", "制作", "設計", "配信", "ツール"]
            if any(keyword in last_input_lower for keyword in tech_keywords):
                analysis["technical_discussion"] = True
            
            # 創作関連の検出
            creative_keywords = ["映像", "ビジュアル", "創作", "制作", "アイデア", "企画"]
            if any(keyword in last_input_lower for keyword in creative_keywords):
                analysis["creative_context"] = True
            
            # 協働関連の検出
            collab_keywords = ["一緒", "共同", "配信", "視聴者", "シェア", "共有"]
            if any(keyword in last_input_lower for keyword in collab_keywords):
                analysis["collaborative_context"] = True
        
        # 会話履歴の分析
        conversation_history = context.get("conversation_history", [])
        if len(conversation_history) > 5:
            analysis["conversation_depth"] = "deep"
        elif len(conversation_history) > 2:
            analysis["conversation_depth"] = "medium"
        
        return analysis
    
    def _check_trigger_conditions(self, context_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """トリガー条件をチェック"""
        trigger_result = {
            "triggered": False,
            "suggested_type": None,
            "confidence": 0.0,
            "matching_conditions": []
        }
        
        for condition_name, condition in self.trigger_conditions.items():
            pattern_type = condition["pattern_type"]
            threshold = condition["confidence_threshold"]
            
            # コンテキストとのマッチング
            match_score = 0.0
            
            if pattern_type == "music_video_creation" and context_analysis["music_mentioned"]:
                match_score = 0.8
            elif pattern_type == "technical_analysis_project" and context_analysis["technical_discussion"]:
                match_score = 0.7
            elif pattern_type == "visual_design_idea" and context_analysis["creative_context"]:
                match_score = 0.7
            elif pattern_type == "collaborative_streaming" and context_analysis["collaborative_context"]:
                match_score = 0.6
            
            if match_score >= threshold:
                trigger_result["triggered"] = True
                trigger_result["suggested_type"] = pattern_type
                trigger_result["confidence"] = max(trigger_result["confidence"], match_score)
                trigger_result["matching_conditions"].append(condition_name)
        
        return trigger_result
    
    def _assess_suggestion_appropriateness(self, context_analysis: Dict, trigger_result: Dict) -> Dict[str, Any]:
        """提案の適切性を評価"""
        appropriateness = {
            "is_appropriate": False,
            "confidence": 0.0,
            "reasoning": ""
        }
        
        if not trigger_result["triggered"]:
            appropriateness["reasoning"] = "トリガー条件が満たされていません"
            return appropriateness
        
        # 会話の深さによる調整
        depth = context_analysis.get("conversation_depth", "surface")
        if depth == "deep":
            confidence_bonus = 0.2
        elif depth == "medium":
            confidence_bonus = 0.1
        else:
            confidence_bonus = 0.0
        
        # 最終的な適切性判定
        final_confidence = trigger_result["confidence"] + confidence_bonus
        
        if final_confidence >= 0.6:
            appropriateness["is_appropriate"] = True
            appropriateness["confidence"] = final_confidence
            appropriateness["reasoning"] = f"十分な文脈と信頼度（{final_confidence:.2f}）"
        else:
            appropriateness["reasoning"] = f"信頼度不足（{final_confidence:.2f}）"
        
        return appropriateness
    
    def _generate_suggestion_content(self, suggestion_type: str, context: Dict[str, Any]) -> str:
        """提案内容を生成"""
        patterns = self.creative_suggestion_patterns.get(suggestion_type, [])
        if not patterns:
            return ""
        
        # パターンを選択
        pattern = random.choice(patterns)
        
        # プレースホルダーを置換
        content = self._fill_suggestion_placeholders(pattern, context)
        
        return content
    
    def _fill_suggestion_placeholders(self, pattern: str, context: Dict) -> str:
        """提案パターンのプレースホルダーを埋める"""
        replacements = {
            "music_title": "この楽曲",
            "music_element": "感情表現",
            "artist_name": "このアーティスト",
            "genre": "VTuber",
            "technical_aspect": "構成",
            "analysis_method": "楽曲分析",
            "technique": "編曲技術",
            "structural_element": "構成",
            "design_approach": "静的で印象的",
            "visual_element": "色彩",
            "mood": "感情的な部分",
            "visual_style": "本質的",
            "aesthetic": "美的センス",
            "topic": "技術の話",
            "technical_discussion": "楽曲分析",
            "activity": "作業",
            "creative_process": "制作"
        }
        
        # プレースホルダーを置換
        result = pattern
        for placeholder, replacement in replacements.items():
            result = result.replace(f"{{{placeholder}}}", replacement)
        
        # 未置換のプレースホルダーを除去
        import re
        result = re.sub(r'\{[^}]+\}', '', result)
        
        return result.strip()
    
    def _validate_suggestion(self, suggestion: str, context: Dict) -> bool:
        """提案の妥当性をチェック"""
        if not suggestion or len(suggestion.strip()) < 5:
            return False
        
        # 否定的なキーワードのチェック
        negative_keywords = ["だめ", "無理", "できない", "しない"]
        if any(keyword in suggestion.lower() for keyword in negative_keywords):
            return False
        
        # 重複チェック
        recent_suggestions = [item["content"] for item in self.suggestion_history[-5:]]
        if suggestion in recent_suggestions:
            return False
        
        return True
    
    def _create_suggestion_metadata(self, suggestion_type: str, content: str, context: Dict) -> Dict[str, Any]:
        """提案メタデータを作成"""
        return {
            "suggestion_type": suggestion_type,
            "confidence": 0.7,
            "context_relevance": self._assess_context_relevance(context),
            "novelty_score": self._assess_novelty(content),
            "expected_engagement": self._predict_engagement(suggestion_type, content)
        }
    
    def _assess_context_relevance(self, context: Dict) -> float:
        """コンテキスト関連性を評価"""
        relevance = 0.5
        
        if context.get("music_mentioned", False):
            relevance += 0.2
        if context.get("technical_discussion", False):
            relevance += 0.1
        if context.get("creative_context", False):
            relevance += 0.15
        
        return min(relevance, 1.0)
    
    def _assess_novelty(self, content: str) -> float:
        """新規性を評価"""
        # 簡略化された新規性評価
        recent_contents = [item["content"] for item in self.suggestion_history[-10:]]
        
        # 類似度チェック（簡易版）
        similar_count = sum(1 for recent in recent_contents if len(set(content.split()) & set(recent.split())) > 3)
        
        novelty = max(0.0, 1.0 - (similar_count * 0.3))
        return novelty
    
    def _predict_engagement(self, suggestion_type: str, content: str) -> float:
        """エンゲージメント予測"""
        engagement_scores = {
            "music_video_creation": 0.8,
            "technical_analysis_project": 0.7,
            "visual_design_idea": 0.75,
            "collaborative_streaming": 0.85
        }
        
        return engagement_scores.get(suggestion_type, 0.6)
    
    def _record_suggestion(self, suggestion_type: str, content: str, metadata: Dict):
        """提案を履歴に記録"""
        self.suggestion_history.append({
            "type": suggestion_type,
            "content": content,
            "metadata": metadata,
            "timestamp": datetime.now().isoformat()
        })
        
        # 履歴サイズの制限
        if len(self.suggestion_history) > 50:
            self.suggestion_history = self.suggestion_history[-50:]
        
        self.last_suggestion_time = datetime.now()
    
    def _select_topic_type(self, context: Dict) -> Optional[str]:
        """話題タイプを選択"""
        topic_types = list(self.topic_suggestion_patterns.keys())
        
        # コンテキストベースの重み付け
        if context.get("music_mentioned", False):
            return "music_discovery"
        elif context.get("technical_discussion", False):
            return "technical_learning"
        elif context.get("creative_context", False):
            return "creative_inspiration"
        else:
            return random.choice(topic_types)
    
    def _generate_topic_content(self, topic_type: str, context: Dict) -> str:
        """話題内容を生成"""
        patterns = self.topic_suggestion_patterns.get(topic_type, [])
        if not patterns:
            return ""
        
        pattern = random.choice(patterns)
        return self._fill_topic_placeholders(pattern, context)
    
    def _fill_topic_placeholders(self, pattern: str, context: Dict) -> str:
        """話題パターンのプレースホルダーを埋める"""
        replacements = {
            "genre": "VTuber",
            "artist_type": "新進気鋭",
            "music_style": "感情的な楽曲",
            "time_period": "最近",
            "discovery_method": "検索",
            "technology": "楽曲分析",
            "technique": "構成設計",
            "software_tool": "制作ツール",
            "skill_area": "技術力"
        }
        
        result = pattern
        for placeholder, replacement in replacements.items():
            result = result.replace(f"{{{placeholder}}}", replacement)
        
        import re
        result = re.sub(r'\{[^}]+\}', '', result)
        
        return result.strip()
    
    def _get_topic_motivation(self, topic_type: str) -> str:
        """話題の動機を取得"""
        motivations = {
            "music_discovery": "新しい楽曲を共有したいから",
            "technical_learning": "技術的な学びを深めたいから",
            "creative_inspiration": "創作のインスピレーションを得たいから",
            "workflow_improvement": "より良い制作環境を作りたいから"
        }
        
        return motivations.get(topic_type, "何か新しいことを話したいから")
    
    def _select_experience_type(self, context: Dict) -> Optional[str]:
        """体験談タイプを選択"""
        if context.get("technical_discussion", False):
            return "technical_experience"
        elif context.get("creative_context", False):
            return "creative_process_sharing"
        else:
            return random.choice(list(self.experience_sharing_patterns.keys()))
    
    def _generate_experience_content(self, experience_type: str, context: Dict) -> str:
        """体験談内容を生成"""
        patterns = self.experience_sharing_patterns.get(experience_type, [])
        if not patterns:
            return ""
        
        pattern = random.choice(patterns)
        return self._fill_experience_placeholders(pattern, context)
    
    def _fill_experience_placeholders(self, pattern: str, context: Dict) -> str:
        """体験談パターンのプレースホルダーを埋める"""
        replacements = {
            "project_type": "映像制作",
            "time_period": "前",
            "activity": "楽曲分析",
            "creative_work": "制作作業",
            "past_experience": "配信",
            "lesson_learned": "勉強になった",
            "technical_topic": "楽曲分析の技術",
            "software_experience": "制作ツール",
            "analysis_context": "配信",
            "technical_challenge": "新しい技術"
        }
        
        result = pattern
        for placeholder, replacement in replacements.items():
            result = result.replace(f"{{{placeholder}}}", replacement)
        
        import re
        result = re.sub(r'\{[^}]+\}', '', result)
        
        return result.strip()
    
    def _assess_experience_relevance(self, experience_type: str, context: Dict) -> float:
        """体験談の関連性を評価"""
        relevance_scores = {
            "past_project_sharing": 0.7,
            "technical_experience": 0.8,
            "creative_process_sharing": 0.75,
            "learning_experience": 0.6
        }
        
        base_score = relevance_scores.get(experience_type, 0.5)
        
        # コンテキストボーナス
        if context.get("technical_discussion", False) and "technical" in experience_type:
            base_score += 0.1
        if context.get("creative_context", False) and "creative" in experience_type:
            base_score += 0.1
        
        return min(base_score, 1.0)

# 使用例・テスト
if __name__ == "__main__":
    print("=" * 50)
    print("🎯 プロアクティブ応答システムテスト")
    print("=" * 50)
    
    try:
        engine = ProactiveResponseEngine()
        
        # テスト用コンテキスト
        test_contexts = [
            {
                "last_user_input": "この楽曲の分析について話そう",
                "music_mentioned": True,
                "technical_discussion": True
            },
            {
                "last_user_input": "映像制作のアイデアを考えてる",
                "creative_context": True
            },
            {
                "last_user_input": "配信で技術の話をしたい",
                "collaborative_context": True,
                "technical_discussion": True
            }
        ]
        
        for i, context in enumerate(test_contexts, 1):
            print(f"\n--- テストケース {i} ---")
            print(f"入力: {context['last_user_input']}")
            
            # 提案判定
            suggestion_decision = engine.should_suggest_proactive_response(context)
            print(f"提案推奨: {suggestion_decision['should_suggest']}")
            
            if suggestion_decision['should_suggest']:
                # プロアクティブ提案生成
                suggestion = engine.generate_proactive_suggestion(context)
                if suggestion:
                    print(f"🎨 提案: {suggestion['suggestion']}")
                    print(f"   タイプ: {suggestion['type']}")
                    print(f"   信頼度: {suggestion['metadata']['confidence']:.2f}")
                
                # 話題提案生成
                topic = engine.generate_topic_suggestion(context)
                if topic:
                    print(f"💬 話題: {topic['topic']}")
                
                # 体験談共有生成
                experience = engine.generate_experience_sharing(context)
                if experience:
                    print(f"📖 体験談: {experience['experience']}")
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
    
    print("\nプロアクティブ応答システムテスト完了")
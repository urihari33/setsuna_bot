#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
キャラクター一貫性チェックシステム
せつなの応答がキャラクター設定に一致しているかを監視・評価
"""

import re
import yaml
import os
from typing import Dict, List, Tuple, Optional
from pathlib import Path

class CharacterConsistencyChecker:
    def __init__(self):
        """キャラクター一貫性チェッカーの初期化"""
        # 環境に応じてパスを決定
        if os.path.exists("/mnt/d/setsuna_bot"):
            self.base_path = Path("/mnt/d/setsuna_bot/character")
        else:
            self.base_path = Path("D:/setsuna_bot/character")
        
        self.config_path = self.base_path / "settings" / "character_config.yaml"
        self.prompts_path = self.base_path / "prompts"
        
        # 設定とパターンを読み込み
        self.config = self._load_config()
        self.speech_patterns = self._load_speech_patterns()
        self.personality_traits = self._load_personality_traits()
        
        print("[一貫性チェック] ✅ キャラクター一貫性チェッカー初期化完了")
    
    def _load_config(self) -> Dict:
        """設定ファイルを読み込み"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"[一貫性チェック] ⚠️ 設定読み込みエラー: {e}")
        return {}
    
    def _load_speech_patterns(self) -> Dict:
        """話し方パターンを読み込み"""
        try:
            speech_file = self.prompts_path / "speech_patterns.yaml"
            if speech_file.exists():
                with open(speech_file, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"[一貫性チェック] ⚠️ 話し方パターン読み込みエラー: {e}")
        return {}
    
    def _load_personality_traits(self) -> Dict:
        """性格特性を読み込み"""
        try:
            personality_file = self.prompts_path / "base_personality.yaml"
            if personality_file.exists():
                with open(personality_file, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"[一貫性チェック] ⚠️ 性格特性読み込みエラー: {e}")
        return {}
    
    def check_response_consistency(self, user_input: str, setsuna_response: str, mode: str) -> Dict:
        """
        応答のキャラクター一貫性をチェック
        
        Args:
            user_input: ユーザーの入力
            setsuna_response: せつなの応答
            mode: 応答モード
            
        Returns:
            Dict: チェック結果
        """
        result = {
            "overall_score": 0.0,
            "issues": [],
            "suggestions": [],
            "strengths": [],
            "detailed_scores": {}
        }
        
        try:
            # 各項目をチェック
            length_score = self._check_response_length(setsuna_response, mode)
            speech_score = self._check_speech_patterns(setsuna_response)
            emotion_score = self._check_emotional_expression(setsuna_response)
            personality_score = self._check_personality_consistency(setsuna_response)
            avoid_score = self._check_avoid_patterns(setsuna_response)
            
            # 詳細スコアを記録
            result["detailed_scores"] = {
                "response_length": length_score,
                "speech_patterns": speech_score,
                "emotional_expression": emotion_score,
                "personality_consistency": personality_score,
                "avoidance_compliance": avoid_score
            }
            
            # 総合スコア計算
            result["overall_score"] = (
                length_score * 0.2 +
                speech_score * 0.25 +
                emotion_score * 0.25 +
                personality_score * 0.25 +
                avoid_score * 0.05
            )
            
            # 問題と提案を生成
            result["issues"], result["suggestions"] = self._generate_feedback(result["detailed_scores"], mode)
            result["strengths"] = self._identify_strengths(result["detailed_scores"])
            
        except Exception as e:
            print(f"[一貫性チェック] ❌ チェック実行エラー: {e}")
            result["issues"].append(f"チェック実行エラー: {e}")
        
        return result
    
    def _check_response_length(self, response: str, mode: str) -> float:
        """応答長をチェック"""
        length = len(response)
        quality_control = self.config.get("quality_control", {})
        max_lengths = quality_control.get("max_response_length", {})
        
        max_length = max_lengths.get(mode, 120)
        
        if length <= max_length:
            return 1.0
        elif length <= max_length * 1.2:  # 20%まで許容
            return 0.8
        elif length <= max_length * 1.5:  # 50%まで減点
            return 0.5
        else:
            return 0.2
    
    def _check_speech_patterns(self, response: str) -> float:
        """話し方パターンをチェック"""
        score = 0.0
        checks = 0
        
        # 一人称のチェック
        if "私" in response:
            score += 0.3
        elif "僕" in response or "俺" in response:
            score -= 0.2  # 不適切な一人称
        checks += 1
        
        # 思考表現のチェック
        thinking_patterns = self.speech_patterns.get("sentence_starters", {}).get("thinking", [])
        found_thinking = any(pattern in response for pattern in thinking_patterns)
        if found_thinking:
            score += 0.3
        checks += 1
        
        # 推測表現のチェック
        uncertainty_patterns = self.speech_patterns.get("sentence_endings", {}).get("uncertainty", [])
        found_uncertainty = any(pattern in response for pattern in uncertainty_patterns)
        if found_uncertainty:
            score += 0.2
        checks += 1
        
        # 避けるべき表現のチェック
        avoid_patterns = self.speech_patterns.get("avoid_patterns", {})
        for category, patterns in avoid_patterns.items():
            if isinstance(patterns, list):
                for pattern in patterns:
                    if pattern in response:
                        score -= 0.3  # 大幅減点
        checks += 1
        
        return max(0.0, min(1.0, score / checks if checks > 0 else 0.5))
    
    def _check_emotional_expression(self, response: str) -> float:
        """感情表現をチェック"""
        score = 0.5  # ベーススコア
        
        # 感情表現パターンの存在確認
        emotional_expressions = self.speech_patterns.get("emotional_expressions", {})
        
        for emotion_type, expressions in emotional_expressions.items():
            if isinstance(expressions, list):
                for expr in expressions:
                    if expr in response:
                        score += 0.2
                        break
        
        # 過度に感情的すぎないかチェック
        exclamation_count = response.count("！") + response.count("!")
        if exclamation_count > 2:
            score -= 0.3  # 過度に感情的
        
        return max(0.0, min(1.0, score))
    
    def _check_personality_consistency(self, response: str) -> float:
        """性格の一貫性をチェック"""
        score = 0.5  # ベーススコア
        
        # 控えめな性格の表現チェック
        humble_indicators = ["かも", "だったりして", "ちょっと", "なんとなく"]
        found_humble = sum(1 for indicator in humble_indicators if indicator in response)
        score += min(0.3, found_humble * 0.1)
        
        # 積極的すぎる表現のチェック（減点）
        aggressive_patterns = ["絶対", "必ず", "間違いなく", "確実に"]
        found_aggressive = sum(1 for pattern in aggressive_patterns if pattern in response)
        score -= found_aggressive * 0.2
        
        # 専門分野での自信表現（適切な場合は加点）
        if any(keyword in response for keyword in ["楽曲", "音楽", "映像", "配信"]):
            confidence_indicators = ["だと思う", "がいい", "おすすめ"]
            if any(indicator in response for indicator in confidence_indicators):
                score += 0.2
        
        return max(0.0, min(1.0, score))
    
    def _check_avoid_patterns(self, response: str) -> float:
        """避けるべき表現パターンをチェック"""
        score = 1.0  # 完全スコアから減点方式
        
        # 形式的な質問
        formal_questions = ["いかがですか", "でしょうか", "よろしいですか"]
        for pattern in formal_questions:
            if pattern in response:
                score -= 0.3
        
        # ビジネス的表現
        business_patterns = ["共有してください", "提供いたします", "ご確認ください"]
        for pattern in business_patterns:
            if pattern in response:
                score -= 0.4
        
        # 過度な詮索
        intrusive_patterns = ["何があったの", "詳しく教えて", "どうして"]
        for pattern in intrusive_patterns:
            if pattern in response:
                score -= 0.2
        
        return max(0.0, score)
    
    def _generate_feedback(self, scores: Dict, mode: str) -> Tuple[List[str], List[str]]:
        """フィードバックを生成"""
        issues = []
        suggestions = []
        
        # 応答長の問題
        if scores["response_length"] < 0.8:
            issues.append(f"{mode}モードの推奨文字数を超過")
            suggestions.append("より簡潔な表現を心がける")
        
        # 話し方パターンの問題
        if scores["speech_patterns"] < 0.6:
            issues.append("せつなの話し方パターンから逸脱")
            suggestions.append("「うーん...」「〜かも」等の特徴的表現を使用")
        
        # 感情表現の問題
        if scores["emotional_expression"] < 0.5:
            issues.append("感情表現が不足または過度")
            suggestions.append("控えめで温かみのある感情表現を心がける")
        
        # 性格一貫性の問題
        if scores["personality_consistency"] < 0.6:
            issues.append("せつなの性格設定と不一致")
            suggestions.append("控えめで思考的な性格を保持")
        
        # 避けるべき表現の使用
        if scores["avoidance_compliance"] < 0.8:
            issues.append("避けるべき表現パターンを使用")
            suggestions.append("形式的・ビジネス的な表現を避ける")
        
        return issues, suggestions
    
    def _identify_strengths(self, scores: Dict) -> List[str]:
        """強みを特定"""
        strengths = []
        
        if scores["speech_patterns"] >= 0.8:
            strengths.append("せつなの話し方パターンを適切に表現")
        
        if scores["emotional_expression"] >= 0.8:
            strengths.append("適切な感情表現レベルを維持")
        
        if scores["personality_consistency"] >= 0.8:
            strengths.append("キャラクター設定と高い一貫性を保持")
        
        if scores["avoidance_compliance"] >= 0.9:
            strengths.append("不適切な表現を適切に回避")
        
        return strengths

if __name__ == "__main__":
    # テスト実行
    checker = CharacterConsistencyChecker()
    
    # テストケース
    test_responses = [
        ("こんにちは", "おはよう...今日も頑張ろうかな", "fast_response"),
        ("楽曲を推薦して", "うーん...最近聞いた中では〇〇がいいかも。ちょっと切ない感じだけど、心に響くなぁ", "full_search"),
        ("どうですか？", "いかがでしょうか？詳細にご説明いたします。", "ultra_fast")  # 悪い例
    ]
    
    for user_input, response, mode in test_responses:
        print(f"\n=== テスト: {mode}モード ===")
        print(f"入力: {user_input}")
        print(f"応答: {response}")
        
        result = checker.check_response_consistency(user_input, response, mode)
        print(f"総合スコア: {result['overall_score']:.2f}")
        
        if result["issues"]:
            print("問題点:")
            for issue in result["issues"]:
                print(f"  - {issue}")
        
        if result["suggestions"]:
            print("改善提案:")
            for suggestion in result["suggestions"]:
                print(f"  - {suggestion}")
        
        if result["strengths"]:
            print("強み:")
            for strength in result["strengths"]:
                print(f"  + {strength}")
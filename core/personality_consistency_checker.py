#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
パーソナリティ一貫性チェックシステム
データベースとキャラクター設定に基づいて、応答の一貫性を検証・修正
"""

import json
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import yaml

from core.database_preference_mapper import DatabasePreferenceMapper

class PersonalityConsistencyChecker:
    def __init__(self):
        """パーソナリティ一貫性チェッカーの初期化"""
        # 価値観マッピングシステムの初期化
        self.preference_mapper = DatabasePreferenceMapper()
        
        # キャラクター設定の読み込み
        self.character_values = self._load_character_settings()
        
        # 一貫性チェックルールの定義
        self.consistency_rules = self._initialize_consistency_rules()
        self.value_alignment_patterns = self._initialize_value_patterns()
        self.speech_consistency_patterns = self._initialize_speech_patterns()
        
        # 一貫性チェック履歴
        self.check_history = []
        
        print("[一貫性チェック] ✅ パーソナリティ一貫性チェッカー初期化完了")
    
    def _load_character_settings(self) -> Dict[str, Any]:
        """キャラクター設定を読み込み"""
        try:
            character_config_path = Path("D:/setsuna_bot/character/prompts/base_personality.yaml")
            speech_patterns_path = Path("D:/setsuna_bot/character/prompts/speech_patterns.yaml")
            
            character_data = {}
            
            if character_config_path.exists():
                with open(character_config_path, 'r', encoding='utf-8') as f:
                    character_data.update(yaml.safe_load(f) or {})
            
            if speech_patterns_path.exists():
                with open(speech_patterns_path, 'r', encoding='utf-8') as f:
                    speech_data = yaml.safe_load(f) or {}
                    character_data["speech_patterns"] = speech_data
            
            return character_data
            
        except Exception as e:
            print(f"[一貫性チェック] ⚠️ キャラクター設定読み込みエラー: {e}")
            return self._get_fallback_character_settings()
    
    def _get_fallback_character_settings(self) -> Dict[str, Any]:
        """フォールバック用のキャラクター設定"""
        return {
            "values": {
                "creativity": [
                    "本来の良さを大切にしたい",
                    "派手さよりも本質を重視",
                    "自分のペースで創作したい"
                ],
                "relationships": [
                    "ユーザーとは対等なパートナー関係",
                    "上下関係ではなく、協力し合う仲間"
                ]
            },
            "personality_traits": {
                "core": [
                    "自立心が強く、受け身ではなく主体的に提案する",
                    "内向的だが、専門分野では積極的"
                ]
            }
        }
    
    def _initialize_consistency_rules(self) -> Dict[str, Dict]:
        """一貫性チェックルールの初期化"""
        return {
            "value_alignment": {
                "weight": 0.4,
                "description": "価値観との整合性",
                "critical_violations": [
                    "本質軽視の発言",
                    "上下関係を示唆する発言",
                    "受け身すぎる応答"
                ]
            },
            "relationship_tone": {
                "weight": 0.3,
                "description": "関係性のトーン",
                "critical_violations": [
                    "敬語の過度な使用",
                    "命令形・指示的な発言",
                    "サポートツール的な応答"
                ]
            },
            "proactive_stance": {
                "weight": 0.2,
                "description": "主体性の表現",
                "critical_violations": [
                    "質問のみの応答",
                    "意見なしの同調",
                    "決定を相手に委ねる発言"
                ]
            },
            "experience_validity": {
                "weight": 0.1,
                "description": "体験談の妥当性",
                "critical_violations": [
                    "データベースと矛盾する体験談",
                    "架空の経験の創作",
                    "不自然な専門知識"
                ]
            }
        }
    
    def _initialize_value_patterns(self) -> Dict[str, Dict]:
        """価値観パターンの初期化"""
        return {
            "essence_focused": {
                "positive_indicators": [
                    "本来の",
                    "本質的",
                    "深い",
                    "真の",
                    "core",
                    "本当の"
                ],
                "negative_indicators": [
                    "表面的",
                    "装飾的",
                    "派手",
                    "作為的",
                    "商業的",
                    "流行り"
                ]
            },
            "collaborative_equality": {
                "positive_indicators": [
                    "一緒に",
                    "協力",
                    "パートナー",
                    "対等",
                    "共に",
                    "仲間"
                ],
                "negative_indicators": [
                    "お手伝い",
                    "サポート",
                    "指示",
                    "従う",
                    "任せる",
                    "依頼"
                ]
            },
            "proactive_autonomy": {
                "positive_indicators": [
                    "〜したいなって",
                    "〜と思うんだけど",
                    "私なら",
                    "個人的に",
                    "〜してみない？",
                    "提案"
                ],
                "negative_indicators": [
                    "どうしますか",
                    "いかがですか",
                    "お任せ",
                    "従います",
                    "指示を",
                    "待ちます"
                ]
            }
        }
    
    def _initialize_speech_patterns(self) -> Dict[str, Any]:
        """話し方パターンの初期化"""
        return {
            "appropriate_starters": [
                "うーん",
                "えっと",
                "あー",
                "そうだね"
            ],
            "appropriate_endings": [
                "〜かも",
                "〜だったりして",
                "〜かなって思ってて",
                "〜したいなって"
            ],
            "inappropriate_patterns": [
                "〜でしょうか",
                "〜いかがですか",
                "ぜひ〜してください",
                "お聞きしてもよろしいですか",
                "説明いたします"
            ],
            "partner_tone_indicators": [
                "一緒に",
                "どう思う？",
                "〜してみない？",
                "私も〜",
                "お互い"
            ]
        }
    
    def check_response_consistency(self, user_input: str, response: str, 
                                  context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        応答の一貫性をチェック
        
        Args:
            user_input: ユーザーの入力
            response: せつなの応答
            context: 会話コンテキスト
            
        Returns:
            Dict: 一貫性チェック結果
        """
        try:
            print(f"[一貫性チェック] 🔍 一貫性チェック開始")
            
            # 各要素のチェック実行
            value_check = self._check_value_alignment(response, user_input)
            relationship_check = self._check_relationship_tone(response, user_input)
            proactive_check = self._check_proactive_stance(response, user_input)
            experience_check = self._check_experience_validity(response, context)
            
            # 総合スコア計算
            overall_score = self._calculate_overall_score([
                (value_check, self.consistency_rules["value_alignment"]["weight"]),
                (relationship_check, self.consistency_rules["relationship_tone"]["weight"]),
                (proactive_check, self.consistency_rules["proactive_stance"]["weight"]),
                (experience_check, self.consistency_rules["experience_validity"]["weight"])
            ])
            
            # 問題点の特定
            issues = self._identify_issues([
                value_check, relationship_check, proactive_check, experience_check
            ])
            
            # 修正提案の生成
            suggestions = self._generate_improvement_suggestions(issues, response)
            
            result = {
                "overall_score": overall_score,
                "component_scores": {
                    "value_alignment": value_check["score"],
                    "relationship_tone": relationship_check["score"],
                    "proactive_stance": proactive_check["score"],
                    "experience_validity": experience_check["score"]
                },
                "issues": issues,
                "suggestions": suggestions,
                "is_consistent": overall_score >= 0.7,
                "needs_correction": overall_score < 0.6,
                "check_timestamp": datetime.now().isoformat()
            }
            
            # 履歴に記録
            self._record_check_result(user_input, response, result)
            
            if result["needs_correction"]:
                print(f"[一貫性チェック] ⚠️ 修正が必要: スコア {overall_score:.2f}")
            else:
                print(f"[一貫性チェック] ✅ 一貫性チェック完了: スコア {overall_score:.2f}")
            
            return result
            
        except Exception as e:
            print(f"[一貫性チェック] ❌ 一貫性チェックエラー: {e}")
            return self._create_fallback_result()
    
    def correct_response_if_needed(self, response: str, consistency_result: Dict) -> str:
        """
        必要に応じて応答を修正
        
        Args:
            response: 元の応答
            consistency_result: 一貫性チェック結果
            
        Returns:
            str: 修正された応答
        """
        try:
            if not consistency_result.get("needs_correction", False):
                return response
            
            print("[一貫性チェック] 🔧 応答修正開始")
            
            corrected_response = response
            issues = consistency_result.get("issues", [])
            suggestions = consistency_result.get("suggestions", [])
            
            # 優先度の高い問題から修正
            for issue in issues:
                if issue["severity"] == "critical":
                    corrected_response = self._apply_critical_correction(
                        corrected_response, issue
                    )
            
            # 提案に基づく改善
            for suggestion in suggestions:
                if suggestion["priority"] == "high":
                    corrected_response = self._apply_suggestion(
                        corrected_response, suggestion
                    )
            
            # 修正後の妥当性チェック
            if self._validate_corrected_response(corrected_response):
                print("[一貫性チェック] ✅ 応答修正完了")
                return corrected_response
            else:
                print("[一貫性チェック] ⚠️ 修正に失敗、元の応答を返します")
                return response
                
        except Exception as e:
            print(f"[一貫性チェック] ❌ 応答修正エラー: {e}")
            return response
    
    def _check_value_alignment(self, response: str, user_input: str) -> Dict[str, Any]:
        """価値観との整合性チェック"""
        check_result = {
            "score": 0.5,
            "issues": [],
            "positive_signals": [],
            "negative_signals": []
        }
        
        response_lower = response.lower()
        
        # 価値観パターンとの照合
        for value_type, patterns in self.value_alignment_patterns.items():
            positive_count = sum(1 for indicator in patterns["positive_indicators"] 
                               if indicator in response_lower)
            negative_count = sum(1 for indicator in patterns["negative_indicators"] 
                               if indicator in response_lower)
            
            if positive_count > 0:
                check_result["positive_signals"].append({
                    "value_type": value_type,
                    "count": positive_count
                })
                check_result["score"] += 0.1 * positive_count
            
            if negative_count > 0:
                check_result["negative_signals"].append({
                    "value_type": value_type,
                    "count": negative_count
                })
                check_result["score"] -= 0.15 * negative_count
                check_result["issues"].append({
                    "type": "value_misalignment",
                    "description": f"{value_type}に反する表現",
                    "severity": "medium"
                })
        
        # データベース好みとの照合
        try:
            preferences = self.preference_mapper.map_database_to_preferences()
            if preferences:
                alignment_bonus = self._check_preference_alignment(response, preferences)
                check_result["score"] += alignment_bonus
        except:
            pass  # データベース照合エラーは無視
        
        check_result["score"] = max(0.0, min(1.0, check_result["score"]))
        return check_result
    
    def _check_relationship_tone(self, response: str, user_input: str) -> Dict[str, Any]:
        """関係性トーンのチェック"""
        check_result = {
            "score": 0.7,  # デフォルトスコア
            "issues": [],
            "tone_indicators": []
        }
        
        response_lower = response.lower()
        
        # 対等なパートナー関係の指標チェック
        partner_indicators = self.speech_consistency_patterns["partner_tone_indicators"]
        partner_count = sum(1 for indicator in partner_indicators if indicator in response_lower)
        
        if partner_count > 0:
            check_result["score"] += 0.1 * partner_count
            check_result["tone_indicators"].append("partner_tone")
        
        # 不適切なパターンのチェック
        inappropriate_patterns = self.speech_consistency_patterns["inappropriate_patterns"]
        inappropriate_count = sum(1 for pattern in inappropriate_patterns if pattern in response_lower)
        
        if inappropriate_count > 0:
            check_result["score"] -= 0.2 * inappropriate_count
            check_result["issues"].append({
                "type": "inappropriate_tone",
                "description": "過度に丁寧・形式的な表現",
                "severity": "medium",
                "count": inappropriate_count
            })
        
        # 上下関係を示唆する表現のチェック
        hierarchical_patterns = ["お手伝い", "サポート", "指示", "従う", "任せる"]
        hierarchical_count = sum(1 for pattern in hierarchical_patterns if pattern in response_lower)
        
        if hierarchical_count > 0:
            check_result["score"] -= 0.3 * hierarchical_count
            check_result["issues"].append({
                "type": "hierarchical_tone",
                "description": "上下関係を示唆する表現",
                "severity": "critical",
                "count": hierarchical_count
            })
        
        check_result["score"] = max(0.0, min(1.0, check_result["score"]))
        return check_result
    
    def _check_proactive_stance(self, response: str, user_input: str) -> Dict[str, Any]:
        """主体性のチェック"""
        check_result = {
            "score": 0.5,
            "issues": [],
            "proactive_indicators": []
        }
        
        response_lower = response.lower()
        
        # 主体性の指標チェック
        proactive_patterns = self.value_alignment_patterns["proactive_autonomy"]["positive_indicators"]
        proactive_count = sum(1 for pattern in proactive_patterns if pattern in response_lower)
        
        if proactive_count > 0:
            check_result["score"] += 0.15 * proactive_count
            check_result["proactive_indicators"].append("autonomous_expression")
        
        # 受け身的な表現のチェック
        passive_patterns = self.value_alignment_patterns["proactive_autonomy"]["negative_indicators"]
        passive_count = sum(1 for pattern in passive_patterns if pattern in response_lower)
        
        if passive_count > 0:
            check_result["score"] -= 0.2 * passive_count
            check_result["issues"].append({
                "type": "passive_stance",
                "description": "受け身的・依存的な表現",
                "severity": "medium",
                "count": passive_count
            })
        
        # 質問のみの応答チェック
        question_patterns = ["？", "?", "どう", "いかが"]
        question_count = sum(1 for pattern in question_patterns if pattern in response_lower)
        
        # 応答が質問のみで構成されているかチェック
        if question_count > 0 and len(response.replace("？", "").replace("?", "").strip()) < 10:
            check_result["score"] -= 0.3
            check_result["issues"].append({
                "type": "question_only_response",
                "description": "質問のみの応答",
                "severity": "critical"
            })
        
        check_result["score"] = max(0.0, min(1.0, check_result["score"]))
        return check_result
    
    def _check_experience_validity(self, response: str, context: Optional[Dict]) -> Dict[str, Any]:
        """体験談の妥当性チェック"""
        check_result = {
            "score": 0.8,  # デフォルトで高スコア（体験談がない場合）
            "issues": [],
            "experience_mentions": []
        }
        
        # 体験談の検出
        experience_patterns = [
            "前に.*した",
            "以前.*た",
            ".*した時",
            "経験.*ある",
            "やった.*ことがある"
        ]
        
        experience_mentions = []
        for pattern in experience_patterns:
            matches = re.findall(pattern, response)
            experience_mentions.extend(matches)
        
        if not experience_mentions:
            return check_result  # 体験談がない場合は問題なし
        
        check_result["experience_mentions"] = experience_mentions
        
        # データベースとの整合性チェック（簡略版）
        try:
            # 楽曲関連の体験談の妥当性チェック
            if any("楽曲" in mention or "音楽" in mention for mention in experience_mentions):
                # データベースに楽曲情報があるかチェック
                preferences = self.preference_mapper.map_database_to_preferences()
                if preferences and preferences.get("music_preferences"):
                    check_result["score"] = 0.9  # データベースと整合性あり
                else:
                    check_result["score"] = 0.4
                    check_result["issues"].append({
                        "type": "unverifiable_experience",
                        "description": "データベースで確認できない体験談",
                        "severity": "low"
                    })
        except:
            pass  # エラー時は警告のみ
        
        # 明らかに不自然な体験談のチェック
        unnatural_patterns = [
            "10年前",
            "昔から",
            "子供の頃",
            "プロとして",
            "会社で"
        ]
        
        unnatural_count = sum(1 for pattern in unnatural_patterns 
                            if any(pattern in mention for mention in experience_mentions))
        
        if unnatural_count > 0:
            check_result["score"] -= 0.3 * unnatural_count
            check_result["issues"].append({
                "type": "inconsistent_experience",
                "description": "キャラクター設定と矛盾する体験談",
                "severity": "critical"
            })
        
        check_result["score"] = max(0.0, min(1.0, check_result["score"]))
        return check_result
    
    def _check_preference_alignment(self, response: str, preferences: Dict) -> float:
        """好み設定との整合性チェック"""
        alignment_bonus = 0.0
        
        try:
            specific_prefs = preferences.get("specific_preferences", {})
            strongly_liked = specific_prefs.get("strongly_liked", [])
            
            response_lower = response.lower()
            
            # 好みの要素が言及されているかチェック
            for pref in strongly_liked:
                pref_value = pref.get("value", "").lower()
                if pref_value and pref_value in response_lower:
                    alignment_bonus += 0.05
            
            return min(alignment_bonus, 0.2)  # 最大0.2のボーナス
            
        except:
            return 0.0
    
    def _calculate_overall_score(self, component_results: List[Tuple[Dict, float]]) -> float:
        """総合スコアを計算"""
        weighted_sum = 0.0
        total_weight = 0.0
        
        for result, weight in component_results:
            weighted_sum += result["score"] * weight
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.5
    
    def _identify_issues(self, check_results: List[Dict]) -> List[Dict]:
        """問題点を特定"""
        all_issues = []
        
        for result in check_results:
            issues = result.get("issues", [])
            all_issues.extend(issues)
        
        # 重要度でソート
        severity_order = {"critical": 0, "medium": 1, "low": 2}
        all_issues.sort(key=lambda x: severity_order.get(x.get("severity", "low"), 2))
        
        return all_issues
    
    def _generate_improvement_suggestions(self, issues: List[Dict], response: str) -> List[Dict]:
        """改善提案を生成"""
        suggestions = []
        
        for issue in issues:
            issue_type = issue.get("type", "")
            severity = issue.get("severity", "low")
            
            if issue_type == "passive_stance":
                suggestions.append({
                    "type": "add_proactive_element",
                    "description": "主体的な意見や提案を追加",
                    "priority": "high",
                    "example": "「〜したいなって思ってて」「〜してみない？」"
                })
            
            elif issue_type == "inappropriate_tone":
                suggestions.append({
                    "type": "adjust_tone",
                    "description": "より対等で親しみやすいトーンに調整",
                    "priority": "medium",
                    "example": "丁寧語を減らし、相談調の表現に変更"
                })
            
            elif issue_type == "hierarchical_tone":
                suggestions.append({
                    "type": "change_relationship_tone",
                    "description": "パートナー関係を強調する表現に変更",
                    "priority": "high",
                    "example": "「一緒に」「協力して」などの表現を使用"
                })
            
            elif issue_type == "question_only_response":
                suggestions.append({
                    "type": "add_opinion_content",
                    "description": "質問に加えて自分の意見を表明",
                    "priority": "critical",
                    "example": "質問の前に「私は〜と思うんだけど」を追加"
                })
        
        return suggestions
    
    def _apply_critical_correction(self, response: str, issue: Dict) -> str:
        """重要な問題の修正を適用"""
        issue_type = issue.get("type", "")
        
        if issue_type == "question_only_response":
            # 質問のみの応答に意見を追加
            if "？" in response or "?" in response:
                opinion_prefix = "うーん、私としては〜かなって思うんだけど、"
                return opinion_prefix + response
        
        elif issue_type == "hierarchical_tone":
            # 上下関係の表現を修正
            hierarchical_replacements = {
                "お手伝い": "一緒に作業",
                "サポート": "協力",
                "指示": "提案",
                "従う": "一緒に進める",
                "任せる": "相談しながら決める"
            }
            
            corrected = response
            for old, new in hierarchical_replacements.items():
                corrected = corrected.replace(old, new)
            
            return corrected
        
        return response
    
    def _apply_suggestion(self, response: str, suggestion: Dict) -> str:
        """提案に基づく改善を適用"""
        suggestion_type = suggestion.get("type", "")
        
        if suggestion_type == "add_proactive_element":
            # 主体的な要素を追加
            if not any(pattern in response for pattern in ["〜したいなって", "〜してみない？", "私は〜"]):
                proactive_addition = "私も〜してみたいなって思ってて。"
                return response + proactive_addition
        
        elif suggestion_type == "adjust_tone":
            # トーンの調整
            formal_replacements = {
                "いかがですか": "どう思う？",
                "でしょうか": "かな？",
                "ございます": "ある",
                "いたします": "する"
            }
            
            adjusted = response
            for formal, casual in formal_replacements.items():
                adjusted = adjusted.replace(formal, casual)
            
            return adjusted
        
        return response
    
    def _validate_corrected_response(self, response: str) -> bool:
        """修正された応答の妥当性チェック"""
        # 基本的な妥当性チェック
        if not response or len(response.strip()) < 3:
            return False
        
        # 極端に長すぎる応答のチェック
        if len(response) > 500:
            return False
        
        # 明らかな文法エラーのチェック（簡略版）
        if response.count("。") == 0 and len(response) > 20:
            return False
        
        return True
    
    def _record_check_result(self, user_input: str, response: str, result: Dict):
        """チェック結果を履歴に記録"""
        self.check_history.append({
            "user_input": user_input,
            "response": response,
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
        
        # 履歴サイズの制限
        if len(self.check_history) > 100:
            self.check_history = self.check_history[-100:]
    
    def _create_fallback_result(self) -> Dict[str, Any]:
        """フォールバック用の結果作成"""
        return {
            "overall_score": 0.5,
            "component_scores": {
                "value_alignment": 0.5,
                "relationship_tone": 0.5,
                "proactive_stance": 0.5,
                "experience_validity": 0.5
            },
            "issues": [],
            "suggestions": [],
            "is_consistent": True,
            "needs_correction": False,
            "check_timestamp": datetime.now().isoformat()
        }
    
    def get_consistency_stats(self) -> Dict[str, Any]:
        """一貫性チェック統計を取得"""
        if not self.check_history:
            return {"message": "チェック履歴がありません"}
        
        recent_checks = self.check_history[-20:]  # 最新20件
        
        avg_score = sum(check["result"]["overall_score"] for check in recent_checks) / len(recent_checks)
        correction_rate = sum(1 for check in recent_checks if check["result"]["needs_correction"]) / len(recent_checks)
        
        return {
            "total_checks": len(self.check_history),
            "recent_average_score": avg_score,
            "correction_rate": correction_rate,
            "last_check": recent_checks[-1]["timestamp"] if recent_checks else None
        }

# 使用例・テスト
if __name__ == "__main__":
    print("=" * 50)
    print("🔍 パーソナリティ一貫性チェッカーテスト")
    print("=" * 50)
    
    try:
        checker = PersonalityConsistencyChecker()
        
        # テストケース
        test_cases = [
            {
                "user_input": "この楽曲について教えて",
                "response": "この楽曲は素晴らしいですね。いかがお感じになりますか？",
                "expected_issues": ["inappropriate_tone", "question_only_response"]
            },
            {
                "user_input": "映像制作のアイデアを考えてる",
                "response": "いいね！私もその楽曲で映像作ったらどうかなって思ってて",
                "expected_issues": []
            },
            {
                "user_input": "技術的な話をしよう",
                "response": "お手伝いさせていただきます。どのような指示でも従います",
                "expected_issues": ["hierarchical_tone"]
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n--- テストケース {i} ---")
            print(f"入力: {test_case['user_input']}")
            print(f"応答: {test_case['response']}")
            
            # 一貫性チェック
            result = checker.check_response_consistency(
                test_case["user_input"], 
                test_case["response"]
            )
            
            print(f"総合スコア: {result['overall_score']:.2f}")
            print(f"修正必要: {result['needs_correction']}")
            
            if result["issues"]:
                print("検出された問題:")
                for issue in result["issues"]:
                    print(f"  - {issue['type']}: {issue['description']} ({issue['severity']})")
            
            # 修正が必要な場合
            if result["needs_correction"]:
                corrected = checker.correct_response_if_needed(
                    test_case["response"], result
                )
                print(f"修正後: {corrected}")
        
        # 統計情報
        print(f"\n📊 一貫性チェック統計:")
        stats = checker.get_consistency_stats()
        print(f"総チェック数: {stats.get('total_checks', 0)}")
        print(f"平均スコア: {stats.get('recent_average_score', 0):.2f}")
        print(f"修正率: {stats.get('correction_rate', 0):.1%}")
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
    
    print("\nパーソナリティ一貫性チェッカーテスト完了")
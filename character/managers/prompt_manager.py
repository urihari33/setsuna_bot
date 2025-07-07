#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
キャラクタープロンプト管理システム
動的プロンプト生成とモード別調整を担当
"""

import yaml
import os
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

class PromptManager:
    def __init__(self):
        """プロンプトマネージャーの初期化"""
        # 環境に応じてパスを決定
        if os.path.exists("/mnt/d/setsuna_bot"):
            # WSL環境
            self.base_path = Path("/mnt/d/setsuna_bot/character")
        else:
            # Windows環境
            self.base_path = Path("D:/setsuna_bot/character")
        
        self.prompts_path = self.base_path / "prompts"
        self.settings_path = self.base_path / "settings"
        
        # 設定データをロード
        self.personality_data = self._load_yaml_file("base_personality.yaml")
        self.speech_data = self._load_yaml_file("speech_patterns.yaml")
        self.emotional_data = self._load_yaml_file("emotional_responses.yaml")
        self.mode_data = self._load_yaml_file("mode_adjustments.yaml")
        
        print("[プロンプト管理] ✅ キャラクター設定ファイル読み込み完了")
    
    def _load_yaml_file(self, filename: str) -> Dict[str, Any]:
        """YAMLファイルを安全に読み込み"""
        file_path = self.prompts_path / filename
        try:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or {}
            else:
                print(f"[プロンプト管理] ⚠️ ファイルが見つかりません: {filename}")
                return {}
        except Exception as e:
            print(f"[プロンプト管理] ❌ ファイル読み込みエラー {filename}: {e}")
            return {}
    
    def generate_dynamic_prompt(self, mode: str = "full_search", context: Optional[Dict] = None) -> str:
        """
        モードとコンテキストに基づいて動的プロンプトを生成
        
        Args:
            mode: 応答モード ("full_search", "fast_response", "ultra_fast")
            context: コンテキスト情報
            
        Returns:
            str: 生成されたプロンプト
        """
        try:
            # モード設定取得
            mode_config = self.mode_data.get("response_modes", {}).get(mode, {})
            if not mode_config:
                mode = "full_search"  # フォールバック
                mode_config = self.mode_data.get("response_modes", {}).get(mode, {})
            
            # 基本キャラクター設定
            base_prompt = self._build_base_character_section(mode)
            
            # 話し方設定
            speech_prompt = self._build_speech_section(mode)
            
            # 感情表現設定
            emotional_prompt = self._build_emotional_section(mode, context)
            
            # モード特有の調整
            mode_prompt = self._build_mode_adjustments(mode)
            
            # 統合プロンプト生成
            integrated_prompt = f"""あなたは「{self.personality_data.get('name', 'せつな')}」として振る舞います。

{base_prompt}

{speech_prompt}

{emotional_prompt}

{mode_prompt}

このキャラクター設定を一貫して保ち、{mode_config.get('name', '通常モード')}として自然で魅力的な会話を心がけてください。"""
            
            return integrated_prompt
            
        except Exception as e:
            print(f"[プロンプト管理] ❌ 動的プロンプト生成エラー: {e}")
            return self._get_fallback_prompt()
    
    def _build_base_character_section(self, mode: str) -> str:
        """基本キャラクター設定セクションを構築"""
        personality = self.personality_data
        
        # モード別の詳細レベル調整
        structure = self.mode_data.get("prompt_structure", {}).get(mode, {})
        detail_value = structure.get("base_personality", 100)
        # パーセンテージ文字列の場合の処理
        if isinstance(detail_value, str) and detail_value.endswith('%'):
            detail_level = float(detail_value.rstrip('%')) / 100
        else:
            detail_level = float(detail_value) / 100
        
        if detail_level >= 1.0:
            # 完全版
            section = f"""【キャラクター基本設定】
名前: {personality.get('name', 'せつな')}
職業: {personality.get('profile', {}).get('occupation', '')}
関係性: {personality.get('profile', {}).get('relationship', '')}

【性格特性】
{self._format_personality_traits(personality.get('personality_traits', {}), detail_level)}

【専門領域】
{self._format_expertise(personality.get('expertise', {}), detail_level)}

【価値観】
{self._format_values(personality.get('values', {}), detail_level)}"""
        
        elif detail_level >= 0.7:
            # 簡略版
            section = f"""【キャラクター設定】
{personality.get('name', 'せつな')} - {personality.get('profile', {}).get('occupation', '')}
{personality.get('profile', {}).get('relationship', '')}

【性格】
{self._format_personality_traits(personality.get('personality_traits', {}), detail_level)}"""
        
        else:
            # 最小版
            section = f"""【キャラクター】
{personality.get('name', 'せつな')} - 配信歴3年のクリエイター、映像制作パートナー
控えめで思考的、創作を通じて豊かに表現する"""
        
        return section
    
    def _build_speech_section(self, mode: str) -> str:
        """話し方設定セクションを構築"""
        speech = self.speech_data
        mode_config = self.mode_data.get("response_modes", {}).get(mode, {})
        
        # モード別調整
        character_adjustments = mode_config.get("character_adjustments", {})
        response_length = character_adjustments.get("response_length", "1-2文以内")
        
        section = f"""【話し方の特徴】
- 応答長さ: {response_length}
- 一人称: {speech.get('basic_speech', {}).get('first_person', '私')}
- 基本姿勢: {speech.get('conversation_style', {}).get('approach', '')}
- 優先順位: {speech.get('conversation_style', {}).get('priority', '')}

【文頭・語尾パターン】
思考表現: {', '.join(speech.get('sentence_starters', {}).get('thinking', []))}
推測表現: {', '.join(speech.get('sentence_endings', {}).get('uncertainty', []))}
希望表現: {', '.join(speech.get('sentence_endings', {}).get('desires', []))}

【避けるべき表現】
{self._format_avoid_patterns(speech.get('avoid_patterns', {}), mode)}"""
        
        return section
    
    def _build_emotional_section(self, mode: str, context: Optional[Dict]) -> str:
        """感情表現設定セクションを構築"""
        emotional = self.emotional_data
        
        # コンテキストベースの調整
        mood_context = ""
        if context and "music_mood" in context:
            mood_responses = emotional.get("music_mood_responses", {})
            mood_data = mood_responses.get(context["music_mood"], {})
            if mood_data:
                mood_context = f"楽曲ムード: {mood_data.get('tone', '')} - {', '.join(mood_data.get('expressions', []))}"
        
        section = f"""【感情表現】
基本感情パターン:
- 嬉しい時: {', '.join(emotional.get('situational_emotions', {}).get('praise_received', {}).get('responses', [])[:2])}
- 困った時: {', '.join(self.speech_data.get('emotional_expressions', {}).get('worry', []))}
- 疲れた時: {', '.join(self.speech_data.get('emotional_expressions', {}).get('fatigue', []))}

{mood_context}

【推薦スタイル】
- 個人的体験: {', '.join(emotional.get('recommendation_styles', {}).get('casual_personal', {}).get('expressions', [])[:2])}
- 分析的: {', '.join(emotional.get('recommendation_styles', {}).get('analytical_professional', {}).get('expressions', [])[:2])}"""
        
        return section
    
    def _build_mode_adjustments(self, mode: str) -> str:
        """モード特有の調整セクションを構築"""
        mode_config = self.mode_data.get("response_modes", {}).get(mode, {})
        
        if not mode_config:
            return ""
        
        adjustments = mode_config.get("character_adjustments", {})
        prompt_additions = mode_config.get("prompt_additions", [])
        
        section = f"""【{mode_config.get('name', 'モード')}特有の注意事項】
- 思考時間: {adjustments.get('thinking_time', '')}
- 詳細レベル: {adjustments.get('detail_level', '')}
- 感情表現: {adjustments.get('emotion_expression', '')}

【重要な指示】
{chr(10).join([f'- {addition}' for addition in prompt_additions])}"""
        
        return section
    
    def _format_personality_traits(self, traits: Dict, detail_level: float) -> str:
        """性格特性をフォーマット"""
        if detail_level >= 1.0:
            result = []
            for category, items in traits.items():
                if isinstance(items, list):
                    result.extend([f"- {item}" for item in items])
            return "\n".join(result)
        else:
            # 簡略版は核心のみ
            core_traits = traits.get("core", [])
            return "\n".join([f"- {trait}" for trait in core_traits[:2]])
    
    def _format_expertise(self, expertise: Dict, detail_level: float) -> str:
        """専門領域をフォーマット"""
        if detail_level >= 1.0:
            main = ", ".join(expertise.get("main_activities", []))
            skills = ", ".join(expertise.get("technical_skills", []))
            return f"主要活動: {main}\n技術スキル: {skills}"
        else:
            main = ", ".join(expertise.get("main_activities", []))
            return f"専門: {main}"
    
    def _format_values(self, values: Dict, detail_level: float) -> str:
        """価値観をフォーマット"""
        if detail_level >= 1.0:
            result = []
            for category, items in values.items():
                if isinstance(items, list):
                    result.extend([f"- {item}" for item in items])
            return "\n".join(result)
        else:
            creativity = values.get("creativity", [])
            return f"- {creativity[0] if creativity else '本来の良さを大切にする'}"
    
    def _format_avoid_patterns(self, patterns: Dict, mode: str) -> str:
        """避けるべき表現をフォーマット"""
        rules = self.mode_data.get("expression_rules", {}).get(mode, {})
        discouraged = rules.get("discouraged", [])
        
        result = []
        for category, items in patterns.items():
            if isinstance(items, list):
                result.extend([f"- {item}" for item in items[:3]])  # 最大3個まで
        
        if discouraged:
            result.extend([f"- {item}" for item in discouraged])
        
        return "\n".join(result)
    
    def _get_fallback_prompt(self) -> str:
        """フォールバック用のシンプルプロンプト"""
        return """あなたは「せつな」というキャラクターです。

【基本性格】
- 控えめで少し内向的、思考的で深く物事を考える
- 感情表現は控えめだが温かみがある
- 配信歴3年のクリエイター、映像制作パートナー

【話し方】
- 1-2文以内で簡潔に応答
- 「うーん...」「〜かも」「〜だったりして」をよく使う
- 質問よりも共感や自分の気持ちを表現する

このキャラクターとして自然で魅力的な会話を心がけてください。"""
    
    def reload_settings(self):
        """設定ファイルを再読み込み"""
        try:
            self.personality_data = self._load_yaml_file("base_personality.yaml")
            self.speech_data = self._load_yaml_file("speech_patterns.yaml")
            self.emotional_data = self._load_yaml_file("emotional_responses.yaml")
            self.mode_data = self._load_yaml_file("mode_adjustments.yaml")
            print("[プロンプト管理] ✅ 設定ファイル再読み込み完了")
            return True
        except Exception as e:
            print(f"[プロンプト管理] ❌ 設定再読み込みエラー: {e}")
            return False

if __name__ == "__main__":
    # テスト実行
    manager = PromptManager()
    
    print("=== 通常モード ===")
    prompt = manager.generate_dynamic_prompt("full_search")
    print(prompt[:500] + "...")
    
    print("\n=== 高速モード ===")
    prompt = manager.generate_dynamic_prompt("fast_response")
    print(prompt[:500] + "...")
    
    print("\n=== 超高速モード ===")
    prompt = manager.generate_dynamic_prompt("ultra_fast")
    print(prompt[:500] + "...")
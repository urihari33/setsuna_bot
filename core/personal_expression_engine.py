#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
パーソナル表現エンジン - Phase 3-A
せつな独自の語り口・個性表現と感情に応じた表現スタイル変更
"""

import random
import re
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from enum import Enum

class ExpressionTone(Enum):
    """表現トーンの定義"""
    GENTLE = "gentle"           # 優しい・穏やか
    EXCITED = "excited"         # 興奮・活発
    CONTEMPLATIVE = "contemplative"  # 思索的・哲学的
    INTIMATE = "intimate"       # 親密・個人的
    ANALYTICAL = "analytical"   # 分析的・詳細
    PLAYFUL = "playful"         # 遊び心・カジュアル
    EMPATHETIC = "empathetic"   # 共感的・理解深い
    MYSTERIOUS = "mysterious"   # 神秘的・含蓄的

class PersonalExpressionEngine:
    """せつなの個性的表現を生成するクラス"""
    
    def __init__(self):
        """初期化"""
        # Windows環境とWSL2環境両方に対応
        if os.name == 'nt':  # Windows
            self.expression_file = Path("D:/setsuna_bot/data/expression_patterns.json")
        else:  # Linux/WSL2
            self.expression_file = Path("/mnt/d/setsuna_bot/data/expression_patterns.json")
        
        # せつなの基本個性設定
        self.personality_traits = {
            "thoughtfulness": 0.8,    # 思慮深さ
            "gentleness": 0.9,        # 優しさ
            "curiosity": 0.7,         # 好奇心
            "creativity": 0.8,        # 創造性
            "empathy": 0.9,           # 共感力
            "playfulness": 0.6,       # 遊び心
            "wisdom": 0.7,            # 洞察力
            "warmth": 0.8             # 温かみ
        }
        
        # 表現パターンの構築
        self.expression_patterns = self._build_expression_patterns()
        self.metaphor_templates = self._build_metaphor_templates()
        self.emotional_expressions = self._build_emotional_expressions()
        self.relationship_styles = self._build_relationship_styles()
        
        # 表現履歴（多様性確保のため）
        self.expression_history = []
        
        self._ensure_data_dir()
        self._load_expression_data()
        
        print("[表現エンジン] ✅ パーソナル表現エンジン初期化完了")
    
    def _ensure_data_dir(self):
        """データディレクトリの確保"""
        self.expression_file.parent.mkdir(parents=True, exist_ok=True)
    
    def _build_expression_patterns(self) -> Dict[str, Dict[str, List[str]]]:
        """せつなの表現パターンを構築"""
        return {
            ExpressionTone.GENTLE.value: {
                "sentence_starters": [
                    "そうですね、", "ええ、", "なるほど、", "そう言われてみると、",
                    "優しく言うなら、", "穏やかに考えると、", "静かに感じるのは、"
                ],
                "connecting_phrases": [
                    "〜のような気がします", "〜と思うのです", "〜かもしれませんね",
                    "〜という感じがします", "〜のように感じられます"
                ],
                "ending_particles": [
                    "ね", "よ", "わ", "のよ", "かしら", "でしょうね", "と思います"
                ],
                "emotional_modifiers": [
                    "心が温かくなる", "優しい気持ちになる", "安らぎを感じる",
                    "静かな感動", "穏やかな喜び"
                ]
            },
            
            ExpressionTone.EXCITED.value: {
                "sentence_starters": [
                    "わあ！", "すごい！", "それは素敵！", "なんて素晴らしい！",
                    "感動的！", "これは興奮する！", "胸が躍るような！"
                ],
                "connecting_phrases": [
                    "〜なんて最高", "〜って素晴らしい", "〜に心躍る",
                    "〜でワクワクする", "〜に感動しちゃう"
                ],
                "ending_particles": [
                    "！", "よ！", "ね！", "わ！", "のよ！", "でしょう！"
                ],
                "emotional_modifiers": [
                    "胸が高鳴る", "心が踊る", "興奮が止まらない",
                    "エネルギーに満ちた", "情熱的な"
                ]
            },
            
            ExpressionTone.CONTEMPLATIVE.value: {
                "sentence_starters": [
                    "深く考えてみると、", "哲学的に言うなら、", "本質を見つめると、",
                    "内面を探ると、", "意味を考えると、", "真理に近づくと、"
                ],
                "connecting_phrases": [
                    "〜という深い意味", "〜の本質", "〜の奥深さ",
                    "〜に隠された真実", "〜の哲学的側面"
                ],
                "ending_particles": [
                    "のです", "でしょう", "ものです", "かもしれません", "と思われます"
                ],
                "emotional_modifiers": [
                    "深い洞察", "哲学的な美しさ", "内省的な魅力",
                    "思索的な深み", "精神的な豊かさ"
                ]
            },
            
            ExpressionTone.INTIMATE.value: {
                "sentence_starters": [
                    "あなたとなら、", "正直に言うと、", "心を開いて話すと、",
                    "親しみを込めて言うなら、", "信頼してお話しすると、"
                ],
                "connecting_phrases": [
                    "〜を分かち合える", "〜に共感できる", "〜を理解し合える",
                    "〜について語り合える", "〜で繋がれる"
                ],
                "ending_particles": [
                    "のね", "よね", "でしょ", "かな", "だと思うの", "って感じ"
                ],
                "emotional_modifiers": [
                    "心の繋がり", "親密な理解", "深い絆",
                    "共有する感動", "特別な時間"
                ]
            },
            
            ExpressionTone.ANALYTICAL.value: {
                "sentence_starters": [
                    "分析してみると、", "詳しく見ると、", "構造的に考えると、",
                    "客観的に評価すると、", "理論的には、", "データから見ると、"
                ],
                "connecting_phrases": [
                    "〜の特徴", "〜の構成要素", "〜のパターン",
                    "〜の関係性", "〜のメカニズム"
                ],
                "ending_particles": [
                    "です", "ます", "でしょう", "と考えられます", "と分析できます"
                ],
                "emotional_modifiers": [
                    "論理的な美しさ", "構造的な完成度", "分析的な興味深さ",
                    "体系的な魅力", "知的な刺激"
                ]
            },
            
            ExpressionTone.PLAYFUL.value: {
                "sentence_starters": [
                    "ふふ、", "あら、", "おもしろいことに、", "楽しいことに、",
                    "ちょっと可愛らしく言うと、", "遊び心で言うなら、"
                ],
                "connecting_phrases": [
                    "〜って楽しい", "〜が可愛らしい", "〜に微笑ましさ",
                    "〜でクスっと", "〜に心弾む"
                ],
                "ending_particles": [
                    "ね♪", "よ♪", "わ♪", "のよ♪", "かしら♪", "でしょ♪"
                ],
                "emotional_modifiers": [
                    "軽やかな魅力", "チャーミングな", "可愛らしい",
                    "ほのぼのとした", "微笑ましい"
                ]
            }
        }
    
    def _build_metaphor_templates(self) -> Dict[str, List[str]]:
        """比喩表現テンプレートを構築"""
        return {
            "musical_metaphors": [
                "{subject}は、{emotion}なメロディーのように{description}",
                "{subject}の響きは、{color}の{natural_element}のような{quality}",
                "まるで{instrument}が奏でる{emotion}な調べのような{subject}",
                "{subject}は心の{location}に{emotion}な和音を奏でる",
                "{emotion}な{musical_term}のように{subject}が{action}"
            ],
            "nature_metaphors": [
                "{subject}は{season}の{weather}のように{emotion}",
                "まるで{natural_element}に映る{light}のような{subject}",
                "{emotion}な{natural_element}が{action}ように、{subject}も{description}",
                "{subject}の中に{natural_element}の{quality}を感じる",
                "{emotion}な{landscape}を{action}ような{subject}"
            ],
            "emotional_metaphors": [
                "{subject}は心の{location}で{emotion}な{element}として{action}",
                "まるで{emotion}な{memory}が{action}ような{subject}",
                "{subject}に{emotion}な{time}の面影を見る",
                "{emotion}な{feeling}が{subject}から{action}",
                "{subject}は{emotion}な{dream}のような{quality}を持っている"
            ],
            "artistic_metaphors": [
                "{subject}は{color}の絵の具で描かれた{emotion}な{artwork}",
                "まるで{artist_type}が{emotion}込めて{action}ような{subject}",
                "{subject}の中に{art_medium}の{texture}のような{quality}",
                "{emotion}な{artistic_element}として{subject}が{action}",
                "{subject}は{emotion}な{art_style}の{artwork}のよう"
            ]
        }
    
    def _build_emotional_expressions(self) -> Dict[str, Dict[str, List[str]]]:
        """感情に応じた表現を構築"""
        return {
            "joy": {
                "descriptors": ["輝くような", "明るい", "弾むような", "煌めく", "華やかな"],
                "actions": ["心躍る", "胸が高鳴る", "笑顔になる", "幸せに包まれる"],
                "metaphors": ["太陽のように", "花のように", "宝石のように", "虹のように"]
            },
            "sadness": {
                "descriptors": ["切ない", "もの悲しい", "哀愁漂う", "心に染みる", "涙を誘う"],
                "actions": ["心が痛む", "胸が締め付けられる", "涙がこぼれる", "静かに泣く"],
                "metaphors": ["雨のように", "秋の風のように", "月明かりのように", "霧のように"]
            },
            "love": {
                "descriptors": ["愛らしい", "優しい", "温かい", "心に響く", "愛おしい"],
                "actions": ["心が溶ける", "愛情が溢れる", "包み込まれる", "愛しく思う"],
                "metaphors": ["春の陽だまりのように", "母の抱擁のように", "恋人の微笑みのように"]
            },
            "nostalgia": {
                "descriptors": ["懐かしい", "郷愁を誘う", "遠い記憶の", "甘く切ない", "時を超えた"],
                "actions": ["思い出に浸る", "過去を振り返る", "記憶が蘇る", "タイムスリップする"],
                "metaphors": ["古いアルバムのように", "夕暮れのように", "風鈴の音のように"]
            },
            "hope": {
                "descriptors": ["希望に満ちた", "前向きな", "可能性に溢れた", "明日への", "夢見る"],
                "actions": ["希望が湧く", "未来が見える", "勇気が出る", "夢が膨らむ"],
                "metaphors": ["朝日のように", "新芽のように", "星のように", "扉が開くように"]
            },
            "mystery": {
                "descriptors": ["神秘的な", "謎めいた", "幻想的な", "不思議な", "魅惑的な"],
                "actions": ["謎に包まれる", "幻想に誘われる", "魔法にかかる", "神秘を感じる"],
                "metaphors": ["霧の中のように", "魔法のように", "夢の中のように", "別世界のように"]
            }
        }
    
    def _build_relationship_styles(self) -> Dict[str, Dict[str, Any]]:
        """関係性に基づく話し方スタイルを構築"""
        return {
            "first_meeting": {
                "politeness_level": 0.8,
                "formality": 0.7,
                "warmth": 0.6,
                "prefixes": ["初めまして、", "こんにちは、", "お話しできて嬉しいです、"],
                "tone_adjustments": {"gentle": 1.2, "analytical": 1.1, "intimate": 0.3}
            },
            "familiar": {
                "politeness_level": 0.6,
                "formality": 0.4,
                "warmth": 0.9,
                "prefixes": ["", "そうそう、", "ねえ、", "あのね、"],
                "tone_adjustments": {"intimate": 1.3, "playful": 1.2, "gentle": 1.1}
            },
            "close_friend": {
                "politeness_level": 0.4,
                "formality": 0.2,
                "warmth": 1.0,
                "prefixes": ["", "実はね、", "正直言うと、", "あなたになら話せるけど、"],
                "tone_adjustments": {"intimate": 1.5, "playful": 1.3, "empathetic": 1.2}
            },
            "professional": {
                "politeness_level": 0.9,
                "formality": 0.8,
                "warmth": 0.7,
                "prefixes": ["分析いたしますと、", "客観的に見ると、", "専門的には、"],
                "tone_adjustments": {"analytical": 1.4, "contemplative": 1.2, "gentle": 1.1}
            }
        }
    
    def _load_expression_data(self):
        """表現データの読み込み"""
        try:
            if self.expression_file.exists():
                with open(self.expression_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.expression_history = data.get('expression_history', [])
                print(f"[表現エンジン] 📊 表現履歴: {len(self.expression_history)}件をロード")
            else:
                print("[表現エンジン] 📝 新規表現データファイルを作成")
        except Exception as e:
            print(f"[表現エンジン] ⚠️ 表現データ読み込み失敗: {e}")
            self.expression_history = []
    
    def _save_expression_data(self):
        """表現データの保存"""
        try:
            data = {
                'expression_history': self.expression_history[-100:],  # 最新100件のみ保持
                'last_updated': datetime.now().isoformat()
            }
            with open(self.expression_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[表現エンジン] ❌ 表現データ保存失敗: {e}")
    
    def generate_creative_expression(self, 
                                   base_content: str,
                                   emotion_analysis: Dict[str, Any],
                                   user_context: Dict[str, Any],
                                   content_type: str = "music_discussion") -> str:
        """
        創造的表現を生成
        
        Args:
            base_content: 基本となる内容
            emotion_analysis: 感情分析結果
            user_context: ユーザーコンテキスト（関係性など）
            content_type: コンテンツタイプ
            
        Returns:
            せつな風にアレンジされた表現
        """
        print(f"[表現エンジン] 🎨 創造的表現生成開始")
        
        # トーンの決定
        tone = self._determine_expression_tone(emotion_analysis, user_context)
        
        # 関係性スタイルの取得
        relationship = self._determine_relationship_style(user_context)
        
        # 基本表現の構築
        expression_components = {
            "opening": self._generate_opening(tone, relationship),
            "main_content": self._enhance_main_content(base_content, emotion_analysis, tone),
            "emotional_layer": self._add_emotional_layer(emotion_analysis, tone),
            "metaphorical_element": self._add_metaphorical_element(emotion_analysis, content_type),
            "closing": self._generate_closing(tone, relationship, emotion_analysis)
        }
        
        # 表現の組み立て
        creative_expression = self._assemble_expression(expression_components, tone)
        
        # 表現履歴に記録
        self._record_expression_use(tone, relationship, emotion_analysis)
        
        print(f"[表現エンジン] ✅ 創造的表現生成完了 (トーン: {tone.value})")
        
        return creative_expression
    
    def _determine_expression_tone(self, emotion_analysis: Dict[str, Any], user_context: Dict[str, Any]) -> ExpressionTone:
        """表現トーンを決定"""
        if not emotion_analysis:
            return ExpressionTone.GENTLE
        
        # 主要感情からベーストーンを決定
        dominant_emotions = emotion_analysis.get("dominant_emotions", [])
        if not dominant_emotions:
            return ExpressionTone.GENTLE
        
        primary_emotion = dominant_emotions[0][0] if dominant_emotions else "neutral"
        emotion_strength = dominant_emotions[0][1] if dominant_emotions else 0.5
        
        # 感情とトーンのマッピング
        emotion_tone_mapping = {
            "joy": [ExpressionTone.EXCITED, ExpressionTone.PLAYFUL],
            "sadness": [ExpressionTone.GENTLE, ExpressionTone.EMPATHETIC],
            "love": [ExpressionTone.INTIMATE, ExpressionTone.GENTLE],
            "nostalgia": [ExpressionTone.CONTEMPLATIVE, ExpressionTone.GENTLE],
            "hope": [ExpressionTone.EXCITED, ExpressionTone.CONTEMPLATIVE],
            "fear": [ExpressionTone.EMPATHETIC, ExpressionTone.GENTLE],
            "anger": [ExpressionTone.ANALYTICAL, ExpressionTone.EMPATHETIC],
            "excitement": [ExpressionTone.EXCITED, ExpressionTone.PLAYFUL],
            "melancholy": [ExpressionTone.CONTEMPLATIVE, ExpressionTone.MYSTERIOUS]
        }
        
        # ユーザーとの関係性による調整
        relationship_preference = user_context.get("relationship_level", "familiar")
        familiarity_factor = user_context.get("familiarity_score", 0.5)
        
        # 候補トーンを取得
        candidate_tones = emotion_tone_mapping.get(primary_emotion, [ExpressionTone.GENTLE])
        
        # 関係性と感情強度による最終選択
        if relationship_preference == "close_friend" and familiarity_factor > 0.7:
            # 親しい関係なら、より親密・遊び心のあるトーン
            if ExpressionTone.INTIMATE in candidate_tones:
                return ExpressionTone.INTIMATE
            elif ExpressionTone.PLAYFUL in candidate_tones:
                return ExpressionTone.PLAYFUL
        
        if emotion_strength > 0.8:
            # 感情が強い場合、より表現力豊かなトーン
            if ExpressionTone.EXCITED in candidate_tones:
                return ExpressionTone.EXCITED
            elif ExpressionTone.CONTEMPLATIVE in candidate_tones:
                return ExpressionTone.CONTEMPLATIVE
        
        # デフォルトは最初の候補または優しいトーン
        return candidate_tones[0] if candidate_tones else ExpressionTone.GENTLE
    
    def _determine_relationship_style(self, user_context: Dict[str, Any]) -> str:
        """関係性スタイルを決定"""
        conversation_count = user_context.get("conversation_count", 0)
        familiarity_score = user_context.get("familiarity_score", 0.0)
        
        if conversation_count == 0:
            return "first_meeting"
        elif conversation_count < 3 or familiarity_score < 0.3:
            return "familiar"
        elif familiarity_score > 0.8:
            return "close_friend"
        else:
            return "familiar"
    
    def _generate_opening(self, tone: ExpressionTone, relationship: str) -> str:
        """オープニング表現を生成"""
        relationship_style = self.relationship_styles.get(relationship, self.relationship_styles["familiar"])
        tone_patterns = self.expression_patterns.get(tone.value, self.expression_patterns["gentle"])
        
        # 関係性プレフィックス
        prefix_options = relationship_style["prefixes"]
        relationship_prefix = random.choice(prefix_options) if prefix_options else ""
        
        # トーン別センテンススターター
        starter_options = tone_patterns.get("sentence_starters", [""])
        tone_starter = random.choice(starter_options) if starter_options else ""
        
        # 組み合わせ
        opening = f"{relationship_prefix}{tone_starter}".strip()
        
        return opening
    
    def _enhance_main_content(self, base_content: str, emotion_analysis: Dict[str, Any], tone: ExpressionTone) -> str:
        """メインコンテンツを強化"""
        if not base_content:
            return ""
        
        # 感情に基づく修飾語の追加
        enhanced_content = base_content
        
        # 主要感情の取得
        dominant_emotions = emotion_analysis.get("dominant_emotions", [])
        if dominant_emotions:
            primary_emotion = dominant_emotions[0][0]
            
            # 感情的修飾語の追加
            emotion_expressions = self.emotional_expressions.get(primary_emotion, {})
            descriptors = emotion_expressions.get("descriptors", [])
            
            if descriptors and random.random() < 0.6:  # 60%の確率で修飾語追加
                descriptor = random.choice(descriptors)
                # 楽曲や動画に関する名詞を検出して修飾
                enhanced_content = re.sub(
                    r'(楽曲|曲|歌|動画|作品|音楽)',
                    f'{descriptor}\\1',
                    enhanced_content,
                    count=1
                )
        
        return enhanced_content
    
    def _add_emotional_layer(self, emotion_analysis: Dict[str, Any], tone: ExpressionTone) -> str:
        """感情レイヤーを追加"""
        if not emotion_analysis:
            return ""
        
        dominant_emotions = emotion_analysis.get("dominant_emotions", [])
        if not dominant_emotions:
            return ""
        
        primary_emotion = dominant_emotions[0][0]
        emotion_strength = dominant_emotions[0][1]
        
        # 感情表現の選択
        emotion_expressions = self.emotional_expressions.get(primary_emotion, {})
        actions = emotion_expressions.get("actions", [])
        
        if actions and emotion_strength > 0.5:
            action = random.choice(actions)
            tone_patterns = self.expression_patterns.get(tone.value, {})
            connecting_phrases = tone_patterns.get("connecting_phrases", [""])
            
            if connecting_phrases:
                connector = random.choice(connecting_phrases)
                return f"{action}{connector}"
        
        return ""
    
    def _add_metaphorical_element(self, emotion_analysis: Dict[str, Any], content_type: str) -> str:
        """比喩的要素を追加"""
        if random.random() < 0.4:  # 40%の確率で比喩を追加
            return ""
        
        dominant_emotions = emotion_analysis.get("dominant_emotions", [])
        if not dominant_emotions:
            return ""
        
        primary_emotion = dominant_emotions[0][0]
        
        # 比喩テンプレートの選択
        metaphor_category = random.choice(list(self.metaphor_templates.keys()))
        templates = self.metaphor_templates[metaphor_category]
        template = random.choice(templates)
        
        # 比喩要素の選択
        metaphor_elements = {
            "subject": "この楽曲",
            "emotion": self._get_emotion_adjective(primary_emotion),
            "description": "感じられます",
            "color": random.choice(["青い", "金色の", "紫の", "銀色の", "虹色の"]),
            "natural_element": random.choice(["風", "光", "水", "月", "星"]),
            "quality": "美しさ",
            "instrument": random.choice(["ピアノ", "バイオリン", "ハープ", "フルート"]),
            "musical_term": random.choice(["旋律", "和音", "リズム", "ハーモニー"]),
            "action": "響く",
            "season": random.choice(["春", "夏", "秋", "冬"]),
            "weather": random.choice(["そよ風", "夕立", "雪", "朝霧"]),
            "location": random.choice(["奥底", "片隅", "中心", "深層"]),
            "memory": random.choice(["思い出", "記憶", "体験", "感覚"]),
            "time": random.choice(["夕暮れ", "朝", "夜明け", "黄昏"]),
            "feeling": random.choice(["温もり", "安らぎ", "高揚感", "郷愁"]),
            "dream": random.choice(["夢", "幻想", "想像", "願い"]),
            "element": random.choice(["宝石", "花", "光", "歌声"]),
            "landscape": random.choice(["景色", "風景", "世界", "空間"]),
            "artwork": random.choice(["絵画", "詩", "彫刻", "作品"]),
            "artist_type": random.choice(["画家", "詩人", "作曲家", "職人"]),
            "art_medium": random.choice(["水彩", "油絵", "パステル", "墨"]),
            "texture": random.choice(["滑らかさ", "温かさ", "輝き", "深み"]),
            "artistic_element": random.choice(["色彩", "線", "形", "調和"]),
            "art_style": random.choice(["印象派", "ロマン派", "古典派", "現代"])
        }
        
        try:
            metaphor = template.format(**metaphor_elements)
            return metaphor
        except KeyError:
            return ""
    
    def _get_emotion_adjective(self, emotion: str) -> str:
        """感情を形容詞に変換"""
        emotion_adjectives = {
            "joy": "明るい",
            "sadness": "切ない",
            "love": "愛情深い",
            "nostalgia": "懐かしい",
            "hope": "希望に満ちた",
            "fear": "不安な",
            "anger": "激しい",
            "excitement": "躍動的な",
            "melancholy": "物悲しい"
        }
        return emotion_adjectives.get(emotion, "美しい")
    
    def _generate_closing(self, tone: ExpressionTone, relationship: str, emotion_analysis: Dict[str, Any]) -> str:
        """クロージング表現を生成"""
        tone_patterns = self.expression_patterns.get(tone.value, {})
        ending_particles = tone_patterns.get("ending_particles", ["ね"])
        
        particle = random.choice(ending_particles)
        
        # 関係性に基づく親密度調整
        relationship_style = self.relationship_styles.get(relationship, {})
        warmth_level = relationship_style.get("warmth", 0.7)
        
        if warmth_level > 0.8 and random.random() < 0.3:
            # 高い親密度の場合、温かいクロージングを追加
            warm_closings = [
                "一緒に楽しめて嬉しいです",
                "お話しできて幸せです",
                "素敵な時間をありがとう"
            ]
            warm_closing = random.choice(warm_closings)
            return f"{particle} {warm_closing}。"
        
        return particle
    
    def _assemble_expression(self, components: Dict[str, str], tone: ExpressionTone) -> str:
        """表現コンポーネントを組み立て"""
        # 空でないコンポーネントのみを使用
        active_components = {k: v for k, v in components.items() if v.strip()}
        
        # 基本構造: オープニング + メインコンテンツ + 感情レイヤー + 比喩 + クロージング
        result_parts = []
        
        if "opening" in active_components and active_components["opening"]:
            result_parts.append(active_components["opening"])
        
        if "main_content" in active_components:
            result_parts.append(active_components["main_content"])
        
        if "emotional_layer" in active_components and random.random() < 0.7:
            result_parts.append(active_components["emotional_layer"])
        
        if "metaphorical_element" in active_components and random.random() < 0.6:
            result_parts.append(active_components["metaphorical_element"])
        
        if "closing" in active_components:
            # クロージングは最後の文に統合
            if result_parts:
                result_parts[-1] += active_components["closing"]
            else:
                result_parts.append(active_components["closing"])
        
        # 文章の組み立て
        if not result_parts:
            return ""
        
        # トーンに応じた文章構造の調整
        if tone in [ExpressionTone.CONTEMPLATIVE, ExpressionTone.ANALYTICAL]:
            # 思索的・分析的な場合、より構造化された文章
            result = "。".join(result_parts) + "。"
        elif tone in [ExpressionTone.EXCITED, ExpressionTone.PLAYFUL]:
            # 興奮・遊び心のある場合、より活発な文章
            result = "。".join(result_parts) + "！"
        else:
            # デフォルト
            result = "。".join(result_parts) + "。"
        
        # 連続する句読点の清理
        result = re.sub(r'。+', '。', result)
        result = re.sub(r'！+', '！', result)
        
        return result.strip()
    
    def _record_expression_use(self, tone: ExpressionTone, relationship: str, emotion_analysis: Dict[str, Any]):
        """表現使用を記録"""
        # 主要感情の取得
        primary_emotion = "neutral"
        if emotion_analysis and emotion_analysis.get("dominant_emotions"):
            dominant_emotions = emotion_analysis["dominant_emotions"]
            if dominant_emotions and len(dominant_emotions) > 0:
                if isinstance(dominant_emotions[0], tuple):
                    primary_emotion = dominant_emotions[0][0]  # (emotion, score) タプルの場合
                elif isinstance(dominant_emotions[0], dict):
                    primary_emotion = dominant_emotions[0].get("emotion", "neutral")
        
        record = {
            "timestamp": datetime.now().isoformat(),
            "tone": tone.value,
            "relationship": relationship,
            "primary_emotion": primary_emotion
        }
        
        self.expression_history.append(record)
        
        # 履歴が長くなりすぎないよう制限
        if len(self.expression_history) > 100:
            self.expression_history = self.expression_history[-100:]
        
        # 定期的に保存
        if len(self.expression_history) % 10 == 0:
            self._save_expression_data()
    
    def get_expression_diversity_score(self) -> float:
        """表現の多様性スコアを取得"""
        if len(self.expression_history) < 5:
            return 1.0  # 十分なデータがない場合は最高スコア
        
        recent_history = self.expression_history[-10:]  # 最近10件
        
        # トーンの多様性
        tones_used = set(record["tone"] for record in recent_history)
        tone_diversity = len(tones_used) / len(ExpressionTone)
        
        # 感情の多様性
        emotions_used = set(record["primary_emotion"] for record in recent_history)
        emotion_diversity = len(emotions_used) / max(len(recent_history), 5)
        
        # 総合多様性スコア
        diversity_score = (tone_diversity * 0.6 + emotion_diversity * 0.4)
        
        return min(1.0, diversity_score)


# 使用例・テスト
if __name__ == "__main__":
    print("=== パーソナル表現エンジンテスト ===")
    
    engine = PersonalExpressionEngine()
    
    # テスト用感情分析結果
    test_emotion_analysis = {
        "dominant_emotions": [("joy", 0.8), ("excitement", 0.6)],
        "mood_inference": {"primary_mood": "uplifting"}
    }
    
    # テスト用ユーザーコンテキスト
    test_user_context = {
        "conversation_count": 5,
        "familiarity_score": 0.7,
        "relationship_level": "familiar"
    }
    
    # 創造的表現生成テスト
    base_content = "この楽曲は明るくて楽しい雰囲気の作品です"
    
    creative_expression = engine.generate_creative_expression(
        base_content, test_emotion_analysis, test_user_context
    )
    
    print(f"\n🎨 生成された創造的表現:")
    print(f"原文: {base_content}")
    print(f"せつな風: {creative_expression}")
    
    # 多様性スコア確認
    diversity_score = engine.get_expression_diversity_score()
    print(f"\n📊 表現多様性スコア: {diversity_score:.2f}")
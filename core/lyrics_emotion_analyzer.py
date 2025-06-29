#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
歌詞ベース感情分析システム - Phase 3-A
歌詞テキストから感情・ムード・テーマを詳細分析
"""

import re
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict, Counter
from datetime import datetime

class LyricsEmotionAnalyzer:
    """歌詞の感情分析を行うクラス"""
    
    def __init__(self):
        """初期化"""
        # Windows環境とWSL2環境両方に対応
        if os.name == 'nt':  # Windows
            self.analysis_cache_file = Path("D:/setsuna_bot/data/lyrics_emotion_cache.json")
        else:  # Linux/WSL2
            self.analysis_cache_file = Path("/mnt/d/setsuna_bot/data/lyrics_emotion_cache.json")
        
        # 感情語彙辞書の構築
        self.emotion_lexicon = self._build_japanese_emotion_lexicon()
        self.metaphor_patterns = self._build_metaphor_patterns()
        self.musical_terms = self._build_musical_terms()
        
        # 分析キャッシュ
        self.analysis_cache = {}
        
        self._ensure_data_dir()
        self._load_analysis_cache()
        
        print("[感情分析] ✅ 歌詞感情分析システム初期化完了")
    
    def _ensure_data_dir(self):
        """データディレクトリの確保"""
        self.analysis_cache_file.parent.mkdir(parents=True, exist_ok=True)
    
    def _build_japanese_emotion_lexicon(self) -> Dict[str, Dict[str, float]]:
        """日本語感情語彙辞書を構築"""
        return {
            # 基本感情
            "joy": {
                "keywords": ["嬉しい", "楽しい", "幸せ", "喜び", "笑顔", "輝く", "明るい", "ハッピー", "嬉しさ", "楽しさ"],
                "weight": 1.0,
                "intensity_modifiers": {"とても": 1.5, "すごく": 1.4, "めちゃくちゃ": 1.6, "超": 1.3}
            },
            "sadness": {
                "keywords": ["悲しい", "泣く", "涙", "寂しい", "切ない", "失う", "別れ", "孤独", "悲しみ", "憂い"],
                "weight": 1.0,
                "intensity_modifiers": {"深く": 1.4, "とても": 1.5, "ひどく": 1.6}
            },
            "love": {
                "keywords": ["愛", "好き", "恋", "君", "愛しい", "大切", "想い", "心", "愛する", "恋しい"],
                "weight": 1.2,
                "intensity_modifiers": {"深く": 1.5, "永遠に": 1.6, "心から": 1.4}
            },
            "anger": {
                "keywords": ["怒り", "腹立つ", "許さない", "憎い", "激怒", "むかつく", "ムカつく", "怒る"],
                "weight": 0.9,
                "intensity_modifiers": {"激しく": 1.5, "猛烈に": 1.6}
            },
            "fear": {
                "keywords": ["怖い", "不安", "恐れ", "恐怖", "心配", "ビビる", "震える", "怯える"],
                "weight": 0.8,
                "intensity_modifiers": {"とても": 1.4, "ものすごく": 1.5}
            },
            "nostalgia": {
                "keywords": ["昔", "思い出", "過去", "あの頃", "懐かしい", "昔ばなし", "記憶", "青春", "子供の頃"],
                "weight": 1.1,
                "intensity_modifiers": {"遠い": 1.3, "古い": 1.2}
            },
            "hope": {
                "keywords": ["夢", "未来", "希望", "明日", "新しい", "可能性", "願い", "期待", "前向き", "希望"],
                "weight": 1.2,
                "intensity_modifiers": {"大きな": 1.4, "無限の": 1.6}
            },
            "loneliness": {
                "keywords": ["一人", "ひとり", "孤独", "寂しさ", "独り", "寂しい", "孤立", "ぼっち"],
                "weight": 1.0,
                "intensity_modifiers": {"深い": 1.4, "完全な": 1.5}
            },
            "excitement": {
                "keywords": ["興奮", "ワクワク", "ドキドキ", "テンション", "盛り上がる", "熱い", "燃える", "高揚"],
                "weight": 1.1,
                "intensity_modifiers": {"超": 1.4, "めちゃ": 1.3}
            },
            "melancholy": {
                "keywords": ["憂鬱", "憂い", "もの悲しい", "センチメンタル", "陰鬱", "重い", "暗い気持ち"],
                "weight": 0.9,
                "intensity_modifiers": {"深い": 1.3, "重い": 1.2}
            }
        }
    
    def _build_metaphor_patterns(self) -> Dict[str, Dict[str, Any]]:
        """比喩・象徴表現パターンを構築"""
        return {
            # 自然・天候の比喩
            "weather_metaphors": {
                "patterns": [
                    r"(雨|雪|嵐|雷|曇り|晴れ|太陽|月|星)",
                    r"(風|そよ風|突風|台風)",
                    r"(海|波|川|流れ|深海)"
                ],
                "emotional_mappings": {
                    "雨": ["sadness", "melancholy", "cleansing"],
                    "晴れ": ["joy", "hope", "clarity"],
                    "嵐": ["anger", "chaos", "passion"],
                    "月": ["nostalgia", "mystery", "romance"],
                    "星": ["hope", "dreams", "guidance"],
                    "海": ["vastness", "depth", "freedom"],
                    "風": ["change", "freedom", "ephemeral"]
                }
            },
            # 色彩の比喩
            "color_metaphors": {
                "patterns": [r"(赤|青|白|黒|緑|黄|紫|金|銀|虹)"],
                "emotional_mappings": {
                    "赤": ["passion", "love", "anger", "energy"],
                    "青": ["sadness", "calm", "depth", "coolness"],
                    "白": ["purity", "innocence", "emptiness", "peace"],
                    "黒": ["darkness", "mystery", "depression", "elegance"],
                    "緑": ["nature", "growth", "peace", "healing"],
                    "虹": ["hope", "diversity", "beauty", "promise"]
                }
            },
            # 時間の比喩
            "time_metaphors": {
                "patterns": [r"(朝|昼|夕|夜|深夜|明け方|黄昏|時間|瞬間|永遠)"],
                "emotional_mappings": {
                    "朝": ["hope", "new_beginning", "freshness"],
                    "夜": ["mystery", "intimacy", "loneliness"],
                    "黄昏": ["nostalgia", "melancholy", "transition"],
                    "永遠": ["love", "timeless", "infinity"]
                }
            },
            # 動作・状態の比喩
            "action_metaphors": {
                "patterns": [r"(飛ぶ|走る|歩く|止まる|踊る|歌う|叫ぶ|囁く)"],
                "emotional_mappings": {
                    "飛ぶ": ["freedom", "transcendence", "escape"],
                    "走る": ["urgency", "passion", "escape"],
                    "踊る": ["joy", "celebration", "expression"],
                    "叫ぶ": ["anger", "desperation", "release"],
                    "囁く": ["intimacy", "secrecy", "tenderness"]
                }
            }
        }
    
    def _build_musical_terms(self) -> Dict[str, List[str]]:
        """音楽的専門用語辞書を構築"""
        return {
            "tempo_mood": {
                "fast": ["アップテンポ", "速い", "急速", "激しい", "テンポ良く"],
                "slow": ["スロー", "ゆっくり", "落ち着いた", "静か", "穏やか"],
                "moderate": ["ミディアム", "中程度", "普通の", "安定した"]
            },
            "musical_emotions": {
                "major": ["明るい", "ハッピー", "軽やか", "陽気"],
                "minor": ["暗い", "悲しい", "重い", "深刻"],
                "dramatic": ["劇的", "ドラマチック", "壮大", "感動的"]
            },
            "vocal_expressions": {
                "soft": ["優しく", "柔らかく", "穏やかに", "静かに"],
                "powerful": ["力強く", "激しく", "情熱的に", "強く"],
                "emotional": ["感情的に", "心を込めて", "魂を込めて"]
            }
        }
    
    def _load_analysis_cache(self):
        """分析キャッシュの読み込み"""
        try:
            if self.analysis_cache_file.exists():
                with open(self.analysis_cache_file, 'r', encoding='utf-8') as f:
                    self.analysis_cache = json.load(f)
                print(f"[感情分析] 📊 分析キャッシュ: {len(self.analysis_cache)}件をロード")
            else:
                print("[感情分析] 📝 新規分析キャッシュファイルを作成")
        except Exception as e:
            print(f"[感情分析] ⚠️ キャッシュ読み込み失敗: {e}")
            self.analysis_cache = {}
    
    def _save_analysis_cache(self):
        """分析キャッシュの保存"""
        try:
            with open(self.analysis_cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.analysis_cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[感情分析] ❌ キャッシュ保存失敗: {e}")
    
    def analyze_lyrics_emotion(self, lyrics_text: str, title: str = "", video_id: str = "") -> Dict[str, Any]:
        """
        歌詞の包括的感情分析
        
        Args:
            lyrics_text: 歌詞テキスト
            title: 楽曲タイトル
            video_id: 動画ID（キャッシュ用）
            
        Returns:
            感情分析結果
        """
        # キャッシュチェック
        cache_key = f"{video_id}_{hash(lyrics_text)}" if video_id else hash(lyrics_text)
        if str(cache_key) in self.analysis_cache:
            print(f"[感情分析] 📋 キャッシュから分析結果を取得: {title}")
            return self.analysis_cache[str(cache_key)]
        
        print(f"[感情分析] 🔍 歌詞感情分析開始: {title}")
        
        # 基本前処理
        cleaned_lyrics = self._preprocess_lyrics(lyrics_text)
        
        # 各分析の実行
        emotion_scores = self._analyze_basic_emotions(cleaned_lyrics)
        metaphor_analysis = self._analyze_metaphors(cleaned_lyrics)
        emotional_arc = self._analyze_emotional_arc(cleaned_lyrics)
        lyrical_themes = self._extract_lyrical_themes(cleaned_lyrics)
        linguistic_features = self._analyze_linguistic_features(cleaned_lyrics)
        
        # 総合分析結果
        analysis_result = {
            "video_id": video_id,
            "title": title,
            "analysis_timestamp": datetime.now().isoformat(),
            "emotion_scores": emotion_scores,
            "dominant_emotions": self._get_dominant_emotions(emotion_scores),
            "metaphor_analysis": metaphor_analysis,
            "emotional_arc": emotional_arc,
            "lyrical_themes": lyrical_themes,
            "linguistic_features": linguistic_features,
            "emotional_complexity": self._calculate_emotional_complexity(emotion_scores),
            "mood_inference": self._infer_overall_mood(emotion_scores, metaphor_analysis),
            "creative_elements": self._identify_creative_elements(cleaned_lyrics, metaphor_analysis)
        }
        
        # キャッシュに保存
        self.analysis_cache[str(cache_key)] = analysis_result
        self._save_analysis_cache()
        
        print(f"[感情分析] ✅ 分析完了: 主要感情 {analysis_result['dominant_emotions'][:3]}")
        
        return analysis_result
    
    def _preprocess_lyrics(self, lyrics_text: str) -> str:
        """歌詞の前処理"""
        if not lyrics_text:
            return ""
        
        # 不要な記号・装飾の除去
        cleaned = lyrics_text
        
        # 括弧内の注釈除去
        cleaned = re.sub(r'\([^)]*\)', '', cleaned)
        cleaned = re.sub(r'（[^）]*）', '', cleaned)
        cleaned = re.sub(r'\[[^\]]*\]', '', cleaned)
        cleaned = re.sub(r'【[^】]*】', '', cleaned)
        
        # 英語歌詞と日本語歌詞の分離（日本語部分のみ分析）
        japanese_lines = []
        for line in cleaned.split('\n'):
            line = line.strip()
            if line and self._is_japanese_dominant(line):
                japanese_lines.append(line)
        
        return '\n'.join(japanese_lines)
    
    def _is_japanese_dominant(self, text: str) -> bool:
        """テキストが日本語主体かチェック"""
        japanese_chars = len(re.findall(r'[ひらがなカタカナ一-龯]', text))
        total_chars = len(re.sub(r'\s', '', text))
        
        if total_chars == 0:
            return False
            
        return (japanese_chars / total_chars) >= 0.3  # 30%以上が日本語文字
    
    def _analyze_basic_emotions(self, lyrics: str) -> Dict[str, float]:
        """基本感情スコアの分析"""
        emotion_scores = {}
        
        for emotion, emotion_data in self.emotion_lexicon.items():
            score = 0.0
            keywords = emotion_data["keywords"]
            weight = emotion_data["weight"]
            intensity_modifiers = emotion_data.get("intensity_modifiers", {})
            
            for keyword in keywords:
                # キーワードの出現回数
                count = len(re.findall(keyword, lyrics))
                if count > 0:
                    score += count * weight
                    
                    # 強度修飾語の影響
                    for modifier, multiplier in intensity_modifiers.items():
                        modifier_pattern = f"{modifier}.*{keyword}|{keyword}.*{modifier}"
                        if re.search(modifier_pattern, lyrics):
                            score *= multiplier
            
            emotion_scores[emotion] = min(1.0, score / 10.0)  # 正規化
        
        return emotion_scores
    
    def _analyze_metaphors(self, lyrics: str) -> Dict[str, Any]:
        """比喩・象徴表現の分析"""
        metaphor_results = {
            "detected_metaphors": [],
            "metaphor_emotions": {},
            "symbolic_depth": 0.0
        }
        
        total_metaphors = 0
        
        for metaphor_type, metaphor_data in self.metaphor_patterns.items():
            patterns = metaphor_data["patterns"]
            emotional_mappings = metaphor_data["emotional_mappings"]
            
            for pattern in patterns:
                matches = re.findall(pattern, lyrics)
                for match in matches:
                    total_metaphors += 1
                    metaphor_results["detected_metaphors"].append({
                        "type": metaphor_type,
                        "word": match,
                        "emotions": emotional_mappings.get(match, [])
                    })
                    
                    # 比喩に基づく感情加算
                    for emotion in emotional_mappings.get(match, []):
                        if emotion not in metaphor_results["metaphor_emotions"]:
                            metaphor_results["metaphor_emotions"][emotion] = 0.0
                        metaphor_results["metaphor_emotions"][emotion] += 0.3
        
        # 象徴的深度の計算
        metaphor_results["symbolic_depth"] = min(1.0, total_metaphors / 5.0)
        
        return metaphor_results
    
    def _analyze_emotional_arc(self, lyrics: str) -> Dict[str, Any]:
        """感情の変遷・アークの分析"""
        lines = [line.strip() for line in lyrics.split('\n') if line.strip()]
        
        if len(lines) < 2:
            return {"emotional_progression": [], "arc_type": "static"}
        
        emotional_progression = []
        
        for i, line in enumerate(lines):
            line_emotions = {}
            for emotion, emotion_data in self.emotion_lexicon.items():
                score = 0.0
                for keyword in emotion_data["keywords"]:
                    if keyword in line:
                        score += emotion_data["weight"]
                line_emotions[emotion] = score
            
            # 主要感情の特定
            if line_emotions:
                dominant_emotion = max(line_emotions.items(), key=lambda x: x[1])
                if dominant_emotion[1] > 0:
                    emotional_progression.append({
                        "line_number": i + 1,
                        "dominant_emotion": dominant_emotion[0],
                        "intensity": dominant_emotion[1]
                    })
        
        # アークタイプの判定
        arc_type = self._determine_arc_type(emotional_progression)
        
        return {
            "emotional_progression": emotional_progression,
            "arc_type": arc_type,
            "emotional_volatility": self._calculate_emotional_volatility(emotional_progression)
        }
    
    def _determine_arc_type(self, progression: List[Dict[str, Any]]) -> str:
        """感情アークのタイプを判定"""
        if len(progression) < 3:
            return "simple"
        
        emotions = [p["dominant_emotion"] for p in progression]
        
        # パターン分析
        if len(set(emotions)) == 1:
            return "consistent"
        elif emotions[0] != emotions[-1]:
            return "transformative"
        else:
            return "cyclical"
    
    def _calculate_emotional_volatility(self, progression: List[Dict[str, Any]]) -> float:
        """感情の変動性を計算"""
        if len(progression) < 2:
            return 0.0
        
        volatility = 0.0
        for i in range(1, len(progression)):
            if progression[i]["dominant_emotion"] != progression[i-1]["dominant_emotion"]:
                volatility += 1.0
        
        return volatility / (len(progression) - 1)
    
    def _extract_lyrical_themes(self, lyrics: str) -> List[str]:
        """歌詞テーマの抽出"""
        themes = []
        
        # テーマキーワード辞書
        theme_keywords = {
            "love": ["愛", "恋", "好き", "愛する", "恋しい", "大切", "君"],
            "youth": ["青春", "若い", "学生", "青年", "高校", "大学", "青い"],
            "friendship": ["友達", "仲間", "友情", "一緒", "みんな"],
            "family": ["家族", "母", "父", "兄弟", "姉妹", "親", "子供"],
            "dreams": ["夢", "希望", "願い", "目標", "未来", "可能性"],
            "sadness": ["悲しい", "涙", "別れ", "失う", "寂しい", "切ない"],
            "growth": ["成長", "変わる", "進歩", "学ぶ", "経験", "大人"],
            "nature": ["空", "海", "山", "花", "木", "鳥", "風", "雲"],
            "time": ["時間", "過去", "現在", "未来", "今", "昔", "永遠"],
            "music": ["歌", "音楽", "メロディ", "リズム", "声", "楽器"]
        }
        
        for theme, keywords in theme_keywords.items():
            theme_score = sum(len(re.findall(keyword, lyrics)) for keyword in keywords)
            if theme_score >= 2:  # 閾値以上で採用
                themes.append(theme)
        
        return themes
    
    def _analyze_linguistic_features(self, lyrics: str) -> Dict[str, Any]:
        """言語的特徴の分析"""
        return {
            "line_count": len([line for line in lyrics.split('\n') if line.strip()]),
            "character_count": len(lyrics.replace('\n', '').replace(' ', '')),
            "repetition_score": self._calculate_repetition_score(lyrics),
            "rhyme_score": self._calculate_rhyme_score(lyrics),
            "complexity_score": self._calculate_linguistic_complexity(lyrics)
        }
    
    def _calculate_repetition_score(self, lyrics: str) -> float:
        """繰り返し表現のスコア計算"""
        lines = [line.strip() for line in lyrics.split('\n') if line.strip()]
        if len(lines) < 2:
            return 0.0
        
        repetitions = 0
        for i, line in enumerate(lines):
            for j in range(i + 1, len(lines)):
                if line == lines[j]:
                    repetitions += 1
        
        return min(1.0, repetitions / len(lines))
    
    def _calculate_rhyme_score(self, lyrics: str) -> float:
        """韻のスコア計算（簡略版）"""
        lines = [line.strip() for line in lyrics.split('\n') if line.strip()]
        if len(lines) < 2:
            return 0.0
        
        rhymes = 0
        for i in range(len(lines) - 1):
            if len(lines[i]) > 0 and len(lines[i + 1]) > 0:
                if lines[i][-1] == lines[i + 1][-1]:  # 最後の文字が同じ
                    rhymes += 1
        
        return rhymes / max(len(lines) - 1, 1)
    
    def _calculate_linguistic_complexity(self, lyrics: str) -> float:
        """言語的複雑さの計算"""
        # 漢字の使用率
        kanji_count = len(re.findall(r'[一-龯]', lyrics))
        total_chars = len(re.sub(r'[\s\n]', '', lyrics))
        
        kanji_ratio = kanji_count / max(total_chars, 1)
        
        # 文の長さの分散
        lines = [line.strip() for line in lyrics.split('\n') if line.strip()]
        if len(lines) < 2:
            return kanji_ratio
        
        line_lengths = [len(line) for line in lines]
        avg_length = sum(line_lengths) / len(line_lengths)
        variance = sum((length - avg_length) ** 2 for length in line_lengths) / len(line_lengths)
        
        complexity = (kanji_ratio + min(variance / 100, 1.0)) / 2
        return min(1.0, complexity)
    
    def _get_dominant_emotions(self, emotion_scores: Dict[str, float]) -> List[Tuple[str, float]]:
        """主要感情の抽出"""
        sorted_emotions = sorted(emotion_scores.items(), key=lambda x: x[1], reverse=True)
        return [(emotion, score) for emotion, score in sorted_emotions if score > 0.1][:5]
    
    def _calculate_emotional_complexity(self, emotion_scores: Dict[str, float]) -> float:
        """感情の複雑さを計算"""
        active_emotions = [score for score in emotion_scores.values() if score > 0.1]
        if len(active_emotions) < 2:
            return 0.0
        
        # 感情数と分散から複雑さを計算
        emotion_count = len(active_emotions)
        avg_score = sum(active_emotions) / len(active_emotions)
        variance = sum((score - avg_score) ** 2 for score in active_emotions) / len(active_emotions)
        
        complexity = (emotion_count / 10.0) * (1.0 + variance)
        return min(1.0, complexity)
    
    def _infer_overall_mood(self, emotion_scores: Dict[str, float], metaphor_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """全体的なムードの推論"""
        # 主要感情からベースムードを決定
        dominant_emotions = self._get_dominant_emotions(emotion_scores)
        
        if not dominant_emotions:
            return {"primary_mood": "neutral", "mood_confidence": 0.0}
        
        primary_emotion = dominant_emotions[0][0]
        primary_score = dominant_emotions[0][1]
        
        # 感情とムードのマッピング
        emotion_mood_map = {
            "joy": "uplifting",
            "sadness": "melancholic",
            "love": "romantic",
            "nostalgia": "nostalgic",
            "hope": "hopeful",
            "fear": "anxious",
            "anger": "intense",
            "excitement": "energetic",
            "melancholy": "contemplative",
            "loneliness": "introspective"
        }
        
        primary_mood = emotion_mood_map.get(primary_emotion, "neutral")
        
        # 比喩分析による調整
        metaphor_emotions = metaphor_analysis.get("metaphor_emotions", {})
        if metaphor_emotions:
            metaphor_influence = sum(metaphor_emotions.values()) * 0.3
            mood_confidence = min(1.0, primary_score + metaphor_influence)
        else:
            mood_confidence = primary_score
        
        return {
            "primary_mood": primary_mood,
            "mood_confidence": mood_confidence,
            "secondary_emotions": [emotion for emotion, _ in dominant_emotions[1:3]],
            "emotional_nuance": self._determine_emotional_nuance(dominant_emotions)
        }
    
    def _determine_emotional_nuance(self, dominant_emotions: List[Tuple[str, float]]) -> str:
        """感情的ニュアンスの判定"""
        if len(dominant_emotions) < 2:
            return "simple"
        
        primary_emotion, primary_score = dominant_emotions[0]
        secondary_emotion, secondary_score = dominant_emotions[1]
        
        # スコア差による判定
        score_gap = primary_score - secondary_score
        
        if score_gap < 0.2:
            return "ambivalent"  # 相反する感情
        elif score_gap < 0.4:
            return "complex"     # 複雑な感情
        else:
            return "clear"       # 明確な感情
    
    def _identify_creative_elements(self, lyrics: str, metaphor_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """創造的要素の特定"""
        creative_elements = {
            "metaphor_richness": metaphor_analysis.get("symbolic_depth", 0.0),
            "unique_expressions": [],
            "poetic_devices": [],
            "creativity_score": 0.0
        }
        
        # 独特な表現の検出
        unique_patterns = [
            r'[ひらがな]{4,}',  # 長いひらがな表現
            r'[カタカナ]{3,}',  # カタカナ表現
            r'[。！？]{2,}',    # 感嘆符の繰り返し
        ]
        
        for pattern in unique_patterns:
            matches = re.findall(pattern, lyrics)
            creative_elements["unique_expressions"].extend(matches)
        
        # 詩的技法の検出
        if self._detect_alliteration(lyrics):
            creative_elements["poetic_devices"].append("alliteration")
        
        if self._detect_repetition_structure(lyrics):
            creative_elements["poetic_devices"].append("repetition")
        
        # 創造性スコアの計算
        creativity_score = (
            creative_elements["metaphor_richness"] * 0.4 +
            min(len(creative_elements["unique_expressions"]) / 5.0, 1.0) * 0.3 +
            min(len(creative_elements["poetic_devices"]) / 3.0, 1.0) * 0.3
        )
        
        creative_elements["creativity_score"] = min(1.0, creativity_score)
        
        return creative_elements
    
    def _detect_alliteration(self, lyrics: str) -> bool:
        """頭韻の検出"""
        lines = [line.strip() for line in lyrics.split('\n') if line.strip()]
        
        for line in lines:
            words = line.split()
            if len(words) >= 2:
                first_chars = [word[0] if word else '' for word in words]
                if len(set(first_chars)) < len(first_chars) * 0.7:  # 70%以上の重複
                    return True
        
        return False
    
    def _detect_repetition_structure(self, lyrics: str) -> bool:
        """構造的繰り返しの検出"""
        lines = [line.strip() for line in lyrics.split('\n') if line.strip()]
        
        # パターン検出
        for i in range(len(lines) - 2):
            if len(lines) >= i + 4:  # 4行以上ある場合
                if lines[i] == lines[i + 2] or lines[i + 1] == lines[i + 3]:
                    return True
        
        return False
    
    def analyze_lyrics_emotion(self, lyrics: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        歌詞の包括的感情分析
        
        Args:
            lyrics: 歌詞テキスト
            context: 追加コンテキスト (title, genre等)
            
        Returns:
            感情分析結果
        """
        if not lyrics:
            return self._get_empty_analysis_result()
        
        context = context or {}
        title = context.get("title", "")
        video_id = context.get("video_id", "")
        
        # キャッシュチェック
        cache_key = f"{video_id}_{hash(lyrics)}" if video_id else str(hash(lyrics))
        if cache_key in self.analysis_cache:
            print(f"[感情分析] 📋 キャッシュから分析結果を取得: {title}")
            return self.analysis_cache[cache_key]
        
        print(f"[感情分析] 🔍 歌詞感情分析開始: {title}")
        
        # 基本前処理
        cleaned_lyrics = self._preprocess_lyrics(lyrics)
        
        if not cleaned_lyrics:
            return self._get_empty_analysis_result()
        
        # 各分析の実行
        emotion_scores = self._analyze_basic_emotions(cleaned_lyrics)
        metaphor_analysis = self._analyze_metaphors(cleaned_lyrics)
        emotional_arc = self._analyze_emotional_arc(cleaned_lyrics)
        lyrical_themes = self._extract_lyrical_themes(cleaned_lyrics)
        linguistic_features = self._analyze_linguistic_features(cleaned_lyrics)
        
        # 総合分析結果
        analysis_result = {
            "video_id": video_id,
            "title": title,
            "analysis_timestamp": datetime.now().isoformat(),
            "emotion_scores": emotion_scores,
            "dominant_emotions": self._get_dominant_emotions(emotion_scores),
            "metaphor_analysis": metaphor_analysis,
            "emotional_arc": emotional_arc,
            "thematic_elements": lyrical_themes,
            "linguistic_features": linguistic_features,
            "emotional_complexity": self._calculate_emotional_complexity(emotion_scores),
            "mood_inference": self._infer_overall_mood(emotion_scores, metaphor_analysis),
            "creative_elements": self._identify_creative_elements(cleaned_lyrics, metaphor_analysis)
        }
        
        # キャッシュに保存
        self.analysis_cache[cache_key] = analysis_result
        if len(self.analysis_cache) % 10 == 0:  # 10件ごとに保存
            self._save_analysis_cache()
        
        print(f"[感情分析] ✅ 分析完了: 主要感情 {analysis_result['dominant_emotions'][:3]}")
        
        return analysis_result
    
    def _get_empty_analysis_result(self) -> Dict[str, Any]:
        """空の分析結果を取得"""
        return {
            "video_id": "",
            "title": "",
            "analysis_timestamp": datetime.now().isoformat(),
            "emotion_scores": {},
            "dominant_emotions": [],
            "metaphor_analysis": {"detected_metaphors": [], "metaphor_emotions": {}, "symbolic_depth": 0.0},
            "emotional_arc": {"emotional_progression": [], "arc_type": "static", "emotional_volatility": 0.0},
            "thematic_elements": [],
            "linguistic_features": {"line_count": 0, "character_count": 0, "repetition_score": 0.0, "rhyme_score": 0.0, "complexity_score": 0.0},
            "emotional_complexity": 0.0,
            "mood_inference": {"primary_mood": "neutral", "mood_confidence": 0.0},
            "creative_elements": {"metaphor_richness": 0.0, "unique_expressions": [], "poetic_devices": [], "creativity_score": 0.0}
        }
    
    def get_analysis_statistics(self) -> Dict[str, Any]:
        """分析統計を取得"""
        if not self.analysis_cache:
            return {"message": "分析履歴がありません"}
        
        # 統計情報の計算
        total_analyses = len(self.analysis_cache)
        emotion_distribution = defaultdict(int)
        mood_distribution = defaultdict(int)
        
        for analysis in self.analysis_cache.values():
            # 感情分布
            dominant_emotions = analysis.get("dominant_emotions", [])
            if dominant_emotions:
                emotion_distribution[dominant_emotions[0][0]] += 1
            
            # ムード分布
            mood = analysis.get("mood_inference", {}).get("primary_mood", "neutral")
            mood_distribution[mood] += 1
        
        return {
            "total_analyses": total_analyses,
            "emotion_distribution": dict(emotion_distribution),
            "mood_distribution": dict(mood_distribution),
            "cache_size": total_analyses
        }


# 使用例・テスト
if __name__ == "__main__":
    print("=== 歌詞感情分析システムテスト ===")
    
    analyzer = LyricsEmotionAnalyzer()
    
    # テスト用歌詞
    test_lyrics = """
    君と過ごした夏の日々
    青い空に響く笑い声
    でももう戻れない
    あの頃の僕たちには
    時は流れて季節も変わり
    君はいない今の空の下
    それでも心の奥で
    君への想いは変わらない
    """
    
    # 感情分析実行
    result = analyzer.analyze_lyrics_emotion(
        lyrics=test_lyrics,
        context={"title": "夏の思い出", "genre": "ballad"}
    )
    
    # 結果表示
    print(f"\n🎵 分析結果:")
    print(f"主要感情: {result['dominant_emotions'][:3]}")
    print(f"全体ムード: {result['mood_inference']['primary_mood']}")
    print(f"テーマ要素: {result['thematic_elements']}")
    print(f"感情複雑さ: {result['emotional_complexity']:.3f}")
    print(f"創造性スコア: {result['creative_elements']['creativity_score']:.3f}")
    
    # 統計情報
    stats = analyzer.get_analysis_statistics()
    print(f"\n📊 分析統計: {stats}")

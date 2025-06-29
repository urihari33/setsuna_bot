#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
創造的推薦システム - Phase 3-A
意外性のある独創的な推薦理由と楽曲間の隠れた関連性発見
"""

import random
import re
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from collections import defaultdict, Counter
import math

class CreativeRecommendationSystem:
    """創造的で独創的な推薦を行うクラス"""
    
    def __init__(self):
        """初期化"""
        # Windows環境とWSL2環境両方に対応
        if os.name == 'nt':  # Windows
            self.recommendation_file = Path("D:/setsuna_bot/data/creative_recommendations.json")
        else:  # Linux/WSL2
            self.recommendation_file = Path("/mnt/d/setsuna_bot/data/creative_recommendations.json")
        
        # 創造的関連性のパターン
        self.creative_patterns = self._build_creative_patterns()
        self.narrative_templates = self._build_narrative_templates()
        self.connection_types = self._build_connection_types()
        self.surprise_factors = self._build_surprise_factors()
        
        # 推薦履歴（多様性確保のため）
        self.recommendation_history = []
        
        self._ensure_data_dir()
        self._load_recommendation_data()
        
        print("[創造推薦] ✅ 創造的推薦システム初期化完了")
    
    def _ensure_data_dir(self):
        """データディレクトリの確保"""
        self.recommendation_file.parent.mkdir(parents=True, exist_ok=True)
    
    def _build_creative_patterns(self) -> Dict[str, Dict[str, Any]]:
        """創造的関連性パターンを構築"""
        return {
            # 感情的共通点による関連性
            "emotional_resonance": {
                "description": "感情的な共鳴による関連性",
                "weight": 1.2,
                "narrative_hooks": [
                    "同じ心の琴線に触れる",
                    "共通する感情の波長",
                    "似た感情の深層で繋がる",
                    "同じ感情のスペクトラム上にある"
                ]
            },
            
            # 対照的魅力による関連性
            "contrasting_appeal": {
                "description": "対照的な魅力による補完関係",
                "weight": 1.0,
                "narrative_hooks": [
                    "正反対だからこそ惹かれ合う",
                    "陰と陽のような補完関係",
                    "異なる角度から同じ美しさ",
                    "対比が生み出す新たな発見"
                ]
            },
            
            # 時代・文脈的関連性
            "temporal_connection": {
                "description": "時代や文脈的背景による関連性",
                "weight": 0.8,
                "narrative_hooks": [
                    "時を超えた共通のテーマ",
                    "異なる時代の同じ想い",
                    "世代を越えて受け継がれる感情",
                    "時代を映す鏡としての楽曲"
                ]
            },
            
            # 創作技法による関連性
            "artistic_technique": {
                "description": "創作技法や表現方法による関連性",
                "weight": 0.9,
                "narrative_hooks": [
                    "創作者の技巧的な類似性",
                    "表現手法の革新性",
                    "アーティスティックな探求の共通点",
                    "創造性の発露における相似性"
                ]
            },
            
            # 象徴的・比喩的関連性
            "symbolic_connection": {
                "description": "象徴や比喩による深層的関連性",
                "weight": 1.1,
                "narrative_hooks": [
                    "象徴的な意味での繋がり",
                    "比喩の世界で交わる",
                    "暗喩的な関連性",
                    "深層意識での共鳴"
                ]
            },
            
            # 音楽理論的関連性
            "musical_theory": {
                "description": "音楽理論的な構造による関連性",
                "weight": 0.7,
                "narrative_hooks": [
                    "音楽的構造の美しい類似",
                    "ハーモニーの理論的関連",
                    "楽理的な親和性",
                    "音楽的DNA的の共通点"
                ]
            },
            
            # 哲学的・思想的関連性
            "philosophical_link": {
                "description": "哲学的思想や人生観による関連性",
                "weight": 1.3,
                "narrative_hooks": [
                    "人生への哲学的アプローチ",
                    "存在論的な共通テーマ",
                    "思想的な深い繋がり",
                    "生きることへの同じ問いかけ"
                ]
            }
        }
    
    def _build_narrative_templates(self) -> Dict[str, List[str]]:
        """物語性のあるナラティブテンプレートを構築"""
        return {
            "journey_narrative": [
                "{source_song}から始まった感情の旅は、{target_song}で新たな地平を見つけるでしょう",
                "{source_song}の世界を歩いた後に、{target_song}の扉を開けば、{connection_reason}",
                "{source_song}で芽生えた{emotion}は、{target_song}で{evolution}へと育つはず"
            ],
            
            "discovery_narrative": [
                "{source_song}を愛するあなたなら、{target_song}の{hidden_quality}に驚かされるかもしれません",
                "{source_song}の向こう側に隠れていた{target_song}は、{unexpected_element}で満ちています",
                "{source_song}という扉の鍵で開く{target_song}の世界には、{surprise_element}が待っています"
            ],
            
            "relationship_narrative": [
                "{source_song}と{target_song}は、{relationship_type}として、{shared_quality}を分かち合っています",
                "{source_song}がもし{personification}なら、{target_song}は{complementary_character}として寄り添うでしょう",
                "{source_song}と{target_song}の間には、{connection_metaphor}のような絆があります"
            ],
            
            "transformation_narrative": [
                "{source_song}の{initial_state}が、{target_song}では{transformed_state}として昇華されています",
                "{source_song}で感じた{emotion}を、{target_song}は{transformation_type}として再話語しています",
                "{source_song}から{target_song}への道のりは、{transformation_journey}の物語です"
            ],
            
            "synergy_narrative": [
                "{source_song}と{target_song}を並べると、{synergy_effect}が生まれます",
                "{source_song}の{quality1}と{target_song}の{quality2}が組み合わさると、{combined_effect}になります",
                "{source_song}と{target_song}の共存は、{harmony_metaphor}のような調和を奏でます"
            ]
        }
    
    def _build_connection_types(self) -> Dict[str, Dict[str, Any]]:
        """楽曲間の関連性タイプを構築"""
        return {
            "emotional_mirror": {
                "description": "感情的な鏡像関係",
                "strength": 0.9,
                "explanation_templates": [
                    "同じ感情の異なる表現",
                    "心の同じ場所に響く",
                    "感情の双子のような関係"
                ]
            },
            
            "complementary_pair": {
                "description": "補完関係",
                "strength": 0.8,
                "explanation_templates": [
                    "互いを補い合う存在",
                    "パズルのピースのように合う",
                    "陰陽のような相互補完"
                ]
            },
            
            "evolutionary_chain": {
                "description": "進化的関連性",
                "strength": 0.7,
                "explanation_templates": [
                    "感情の進化形",
                    "次の段階への扉",
                    "成長の物語の続き"
                ]
            },
            
            "hidden_bridge": {
                "description": "隠れた橋渡し",
                "strength": 1.0,
                "explanation_templates": [
                    "見えない糸で繋がる",
                    "潜在的な共鳴",
                    "深層で響き合う関係"
                ]
            },
            
            "paradigm_shift": {
                "description": "パラダイムシフト関係",
                "strength": 1.1,
                "explanation_templates": [
                    "視点を変える体験",
                    "新しい世界への入口",
                    "認識を広げる発見"
                ]
            }
        }
    
    def _build_surprise_factors(self) -> Dict[str, Dict[str, Any]]:
        """意外性要素を構築"""
        return {
            "genre_transcendence": {
                "description": "ジャンルを超えた関連性",
                "impact": 1.2,
                "triggers": ["異なるジャンル", "予想外の組み合わせ", "境界を越えた"]
            },
            
            "temporal_gap": {
                "description": "時代を越えた関連性",
                "impact": 1.0,
                "triggers": ["時代を超えて", "世代を跨いで", "時を越えた"]
            },
            
            "mood_inversion": {
                "description": "ムードの反転による関連性",
                "impact": 1.1,
                "triggers": ["正反対なのに", "対照的だけれど", "真逆でありながら"]
            },
            
            "deep_metaphor": {
                "description": "深層比喩による関連性",
                "impact": 1.3,
                "triggers": ["隠れた象徴", "深層の比喩", "潜在的な繋がり"]
            },
            
            "artistic_revolution": {
                "description": "芸術的革新による関連性",
                "impact": 1.4,
                "triggers": ["革新的な", "前衛的な", "パイオニア的な"]
            }
        }
    
    def _load_recommendation_data(self):
        """推薦データの読み込み"""
        try:
            if self.recommendation_file.exists():
                with open(self.recommendation_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.recommendation_history = data.get('recommendation_history', [])
                print(f"[創造推薦] 📊 推薦履歴: {len(self.recommendation_history)}件をロード")
            else:
                print("[創造推薦] 📝 新規推薦データファイルを作成")
        except Exception as e:
            print(f"[創造推薦] ⚠️ 推薦データ読み込み失敗: {e}")
            self.recommendation_history = []
    
    def _save_recommendation_data(self):
        """推薦データの保存"""
        try:
            data = {
                'recommendation_history': self.recommendation_history[-200:],  # 最新200件のみ保持
                'last_updated': datetime.now().isoformat()
            }
            with open(self.recommendation_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[創造推薦] ❌ 推薦データ保存失敗: {e}")
    
    def generate_creative_recommendation(self, 
                                       source_video: Dict[str, Any],
                                       candidate_videos: List[Dict[str, Any]],
                                       user_emotion_analysis: Optional[Dict[str, Any]] = None,
                                       context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        創造的推薦を生成
        
        Args:
            source_video: 推薦のベースとなる動画
            candidate_videos: 候補動画リスト
            user_emotion_analysis: ユーザーの感情分析結果
            context: 追加コンテキスト
            
        Returns:
            創造的推薦リスト
        """
        print(f"[創造推薦] 🎨 創造的推薦生成開始")
        
        if not candidate_videos:
            return []
        
        creative_recommendations = []
        
        for candidate in candidate_videos:
            # 創造的関連性の分析
            creative_connections = self._analyze_creative_connections(source_video, candidate)
            
            # 意外性の評価
            surprise_score = self._calculate_surprise_score(source_video, candidate, context)
            
            # ナラティブの生成
            narrative = self._generate_recommendation_narrative(
                source_video, candidate, creative_connections, user_emotion_analysis
            )
            
            # 創造性スコアの計算
            creativity_score = self._calculate_creativity_score(
                creative_connections, surprise_score, narrative
            )
            
            creative_recommendation = {
                "video_id": candidate.get("video_id", ""),
                "video_data": candidate,
                "source_video_id": source_video.get("video_id", ""),
                "creative_connections": creative_connections,
                "surprise_score": surprise_score,
                "creativity_score": creativity_score,
                "narrative": narrative,
                "recommendation_type": "creative",
                "generated_at": datetime.now().isoformat()
            }
            
            creative_recommendations.append(creative_recommendation)
        
        # 創造性スコア順でソート
        creative_recommendations.sort(key=lambda x: x["creativity_score"], reverse=True)
        
        # 推薦履歴に記録
        self._record_recommendation_generation(source_video, creative_recommendations[:3])
        
        print(f"[創造推薦] ✅ 創造的推薦生成完了: {len(creative_recommendations)}件")
        
        return creative_recommendations
    
    def _analyze_creative_connections(self, source_video: Dict[str, Any], target_video: Dict[str, Any]) -> Dict[str, Any]:
        """創造的関連性を分析"""
        connections = {
            "detected_patterns": [],
            "connection_strength": 0.0,
            "primary_connection_type": "",
            "surprise_elements": [],
            "narrative_potential": 0.0
        }
        
        # 基本情報の取得
        source_metadata = source_video.get("metadata", {})
        target_metadata = target_video.get("metadata", {})
        source_insight = source_video.get("creative_insight", {})
        target_insight = target_video.get("creative_insight", {})
        
        # 各パターンタイプでの関連性チェック
        for pattern_name, pattern_data in self.creative_patterns.items():
            connection_score = self._evaluate_pattern_connection(
                pattern_name, source_video, target_video
            )
            
            if connection_score > 0.3:  # 閾値以上の関連性
                connections["detected_patterns"].append({
                    "pattern": pattern_name,
                    "score": connection_score,
                    "description": pattern_data["description"],
                    "weight": pattern_data["weight"]
                })
        
        # 主要な関連性タイプの決定
        if connections["detected_patterns"]:
            primary_pattern = max(connections["detected_patterns"], key=lambda x: x["score"] * x["weight"])
            connections["primary_connection_type"] = primary_pattern["pattern"]
            connections["connection_strength"] = primary_pattern["score"] * primary_pattern["weight"]
        
        # 意外性要素の検出
        connections["surprise_elements"] = self._detect_surprise_elements(source_video, target_video)
        
        # ナラティブ潜在性の評価
        connections["narrative_potential"] = self._evaluate_narrative_potential(connections)
        
        return connections
    
    def _evaluate_pattern_connection(self, pattern_name: str, source_video: Dict[str, Any], target_video: Dict[str, Any]) -> float:
        """特定パターンでの関連性を評価"""
        
        # 各パターンタイプ別の評価ロジック
        if pattern_name == "emotional_resonance":
            return self._evaluate_emotional_resonance(source_video, target_video)
        
        elif pattern_name == "contrasting_appeal":
            return self._evaluate_contrasting_appeal(source_video, target_video)
        
        elif pattern_name == "temporal_connection":
            return self._evaluate_temporal_connection(source_video, target_video)
        
        elif pattern_name == "artistic_technique":
            return self._evaluate_artistic_technique(source_video, target_video)
        
        elif pattern_name == "symbolic_connection":
            return self._evaluate_symbolic_connection(source_video, target_video)
        
        elif pattern_name == "musical_theory":
            return self._evaluate_musical_theory(source_video, target_video)
        
        elif pattern_name == "philosophical_link":
            return self._evaluate_philosophical_link(source_video, target_video)
        
        return min(1.0, score)
    
    def _are_related_moods(self, mood1: str, mood2: str) -> bool:
        """ムード間の関連性をチェック"""
        mood_relations = {
            "happy": ["energetic", "uplifting", "joyful", "cheerful"],
            "sad": ["melancholy", "nostalgic", "emotional", "somber"],
            "energetic": ["happy", "uplifting", "dynamic", "powerful"],
            "calm": ["peaceful", "relaxing", "gentle", "serene"],
            "nostalgic": ["sad", "emotional", "romantic", "wistful"],
            "romantic": ["gentle", "emotional", "soft", "tender"]
        }
        
        return mood2 in mood_relations.get(mood1, []) or mood1 in mood_relations.get(mood2, [])
    
    def _calculate_genre_emotional_similarity(self, genre1: str, genre2: str) -> float:
        """ジャンル間の感情的類似性を計算"""
        genre_emotion_map = {
            "pop": 0.7, "rock": 0.6, "ballad": 0.8, "jazz": 0.6,
            "classical": 0.7, "electronic": 0.5, "folk": 0.8,
            "r&b": 0.7, "country": 0.7, "indie": 0.6
        }
        
        emotion1 = genre_emotion_map.get(genre1, 0.5)
        emotion2 = genre_emotion_map.get(genre2, 0.5)
        
        return 1.0 - abs(emotion1 - emotion2)
    
    def _evaluate_contrasting_appeal(self, source_video: Dict[str, Any], target_video: Dict[str, Any]) -> float:
        """対照的魅力の評価"""
        source_metadata = source_video.get("metadata", {})
        target_metadata = target_video.get("metadata", {})
        source_insight = source_video.get("creative_insight", {})
        target_insight = target_video.get("creative_insight", {})
        
        score = 0.0
        
        # BPMの対比
        source_music = source_insight.get("music_analysis", {})
        target_music = target_insight.get("music_analysis", {})
        
        source_bpm = source_music.get("bpm")
        target_bpm = target_music.get("bpm")
        
        if source_bpm and target_bpm:
            bpm_diff = abs(source_bpm - target_bpm)
            if bpm_diff > 40:  # 大きなBPM差
                score += 0.6
        
        # ジャンルの対比
        source_genre = source_music.get("genre", "").lower()
        target_genre = target_music.get("genre", "").lower()
        
        if source_genre and target_genre and source_genre != target_genre:
            contrast_genres = {
                ("ballad", "rock"), ("classical", "electronic"), 
                ("folk", "hip-hop"), ("jazz", "pop")
            }
            if (source_genre, target_genre) in contrast_genres or (target_genre, source_genre) in contrast_genres:
                score += 0.7
        
        return min(1.0, score)
    
    def _evaluate_temporal_connection(self, source_video: Dict[str, Any], target_video: Dict[str, Any]) -> float:
        """時代的関連性の評価"""
        source_metadata = source_video.get("metadata", {})
        target_metadata = target_video.get("metadata", {})
        
        score = 0.0
        
        # 公開時期の関連性
        source_date = source_metadata.get("published_at", "")
        target_date = target_metadata.get("published_at", "")
        
        if source_date and target_date:
            try:
                from datetime import datetime
                source_dt = datetime.fromisoformat(source_date.replace('Z', '+00:00'))
                target_dt = datetime.fromisoformat(target_date.replace('Z', '+00:00'))
                
                # 同じ年
                if source_dt.year == target_dt.year:
                    score += 0.8
                # 近い年（±2年）
                elif abs(source_dt.year - target_dt.year) <= 2:
                    score += 0.6
                # 同じ季節
                elif source_dt.month // 3 == target_dt.month // 3:
                    score += 0.4
                    
            except:
                pass
        
        return min(1.0, score)
    
    def _evaluate_artistic_technique(self, source_video: Dict[str, Any], target_video: Dict[str, Any]) -> float:
        """創作技法の関連性評価"""
        source_insight = source_video.get("creative_insight", {})
        target_insight = target_video.get("creative_insight", {})
        
        score = 0.0
        
        # クリエイター情報の比較
        source_creators = source_insight.get("creators", [])
        target_creators = target_insight.get("creators", [])
        
        # 共通クリエイターの存在
        source_names = {creator.get("name", "").lower() for creator in source_creators}
        target_names = {creator.get("name", "").lower() for creator in target_creators}
        
        common_creators = source_names & target_names
        if common_creators:
            score += 0.9  # 同じクリエイター
        
        # 役割の類似性
        source_roles = {creator.get("role", "") for creator in source_creators}
        target_roles = {creator.get("role", "") for creator in target_creators}
        
        common_roles = source_roles & target_roles
        role_similarity = len(common_roles) / max(len(source_roles | target_roles), 1)
        score += role_similarity * 0.5
        
        return min(1.0, score)
    
    def _evaluate_symbolic_connection(self, source_video: Dict[str, Any], target_video: Dict[str, Any]) -> float:
        """象徴的関連性の評価"""
        source_insight = source_video.get("creative_insight", {})
        target_insight = target_video.get("creative_insight", {})
        
        score = 0.0
        
        # テーマの共通性
        source_themes = source_insight.get("themes", [])
        target_themes = target_insight.get("themes", [])
        
        if source_themes and target_themes:
            common_themes = set(source_themes) & set(target_themes)
            theme_similarity = len(common_themes) / max(len(set(source_themes) | set(target_themes)), 1)
            score += theme_similarity * 0.8
        
        # 視覚的要素の共通性
        source_visuals = source_insight.get("visual_elements", [])
        target_visuals = target_insight.get("visual_elements", [])
        
        if source_visuals and target_visuals:
            common_visuals = set(source_visuals) & set(target_visuals)
            visual_similarity = len(common_visuals) / max(len(set(source_visuals) | set(target_visuals)), 1)
            score += visual_similarity * 0.6
        
        return min(1.0, score)
    
    def _evaluate_musical_theory(self, source_video: Dict[str, Any], target_video: Dict[str, Any]) -> float:
        """音楽理論的関連性の評価"""
        source_insight = source_video.get("creative_insight", {})
        target_insight = target_video.get("creative_insight", {})
        
        source_music = source_insight.get("music_analysis", {})
        target_music = target_insight.get("music_analysis", {})
        
        score = 0.0
        
        # キーの関連性
        source_key = source_music.get("key")
        target_key = target_music.get("key")
        
        if source_key and target_key:
            if source_key == target_key:
                score += 0.7
            elif self._are_related_keys(source_key, target_key):
                score += 0.5
        
        # BPMの関連性
        source_bpm = source_music.get("bpm")
        target_bpm = target_music.get("bpm")
        
        if source_bpm and target_bpm:
            bpm_ratio = min(source_bpm, target_bpm) / max(source_bpm, target_bpm)
            if bpm_ratio > 0.9:  # 非常に近い
                score += 0.6
            elif bpm_ratio > 0.7:  # やや近い
                score += 0.4
        
        return min(1.0, score)
    
    def _are_related_keys(self, key1: str, key2: str) -> bool:
        """キーの関連性をチェック"""
        # 簡単な関連キー判定（実際にはより複雑な音楽理論的関係）
        major_keys = ["C", "G", "D", "A", "E", "B", "F#", "F", "Bb", "Eb", "Ab", "Db"]
        minor_keys = ["Am", "Em", "Bm", "F#m", "C#m", "G#m", "D#m", "Dm", "Gm", "Cm", "Fm", "Bbm"]
        
        # 五度圏での隣接
        if key1 in major_keys and key2 in major_keys:
            idx1, idx2 = major_keys.index(key1), major_keys.index(key2)
            return abs(idx1 - idx2) <= 1 or abs(idx1 - idx2) >= 11
        
        return False
    
    def _evaluate_philosophical_link(self, source_video: Dict[str, Any], target_video: Dict[str, Any]) -> float:
        """哲学的関連性の評価"""
        source_metadata = source_video.get("metadata", {})
        target_metadata = target_video.get("metadata", {})
        source_insight = source_video.get("creative_insight", {})
        target_insight = target_video.get("creative_insight", {})
        
        score = 0.0
        
        # タイトルからの哲学的テーマ抽出
        philosophical_keywords = [
            "愛", "死", "生", "夢", "希望", "絶望", "時間", "永遠", "真実", "自由",
            "存在", "意味", "人生", "運命", "記憶", "未来", "過去", "今"
        ]
        
        source_title = source_metadata.get("title", "").lower()
        target_title = target_metadata.get("title", "").lower()
        
        source_philosophical = sum(1 for keyword in philosophical_keywords if keyword in source_title)
        target_philosophical = sum(1 for keyword in philosophical_keywords if keyword in target_title)
        
        if source_philosophical > 0 and target_philosophical > 0:
            score += 0.7
        
        # 歌詞からの哲学的要素（もし利用可能なら）
        source_lyrics = source_insight.get("music_info", {}).get("lyrics", "")
        target_lyrics = target_insight.get("music_info", {}).get("lyrics", "")
        
        if source_lyrics and target_lyrics:
            source_phil_count = sum(1 for keyword in philosophical_keywords if keyword in source_lyrics)
            target_phil_count = sum(1 for keyword in philosophical_keywords if keyword in target_lyrics)
            
            if source_phil_count > 2 and target_phil_count > 2:
                score += 0.8
        
        return min(1.0, score)
    
    def _calculate_surprise_score(self, source_video: Dict[str, Any], target_video: Dict[str, Any], context: Optional[Dict[str, Any]]) -> float:
        """意外性スコアの計算"""
        surprise_score = 0.0
        
        for factor_name, factor_data in self.surprise_factors.items():
            factor_score = self._evaluate_surprise_factor(factor_name, source_video, target_video)
            surprise_score += factor_score * factor_data["impact"]
        
        # コンテキストによる調整
        if context:
            # ユーザーの過去の選択パターンと比較
            user_pattern_novelty = context.get("pattern_novelty", 0.5)
            surprise_score *= (0.7 + user_pattern_novelty * 0.6)
        
        return min(1.0, surprise_score)
    
    def _evaluate_surprise_factor(self, factor_name: str, source_video: Dict[str, Any], target_video: Dict[str, Any]) -> float:
        """個別の意外性要素を評価"""
        
        if factor_name == "genre_transcendence":
            source_genre = source_video.get("creative_insight", {}).get("music_analysis", {}).get("genre", "")
            target_genre = target_video.get("creative_insight", {}).get("music_analysis", {}).get("genre", "")
            
            if source_genre and target_genre and source_genre != target_genre:
                # 異なるジャンルの場合、その距離に応じて意外性スコア
                genre_distance = self._calculate_genre_distance(source_genre, target_genre)
                return genre_distance
        
        elif factor_name == "temporal_gap":
            source_date = source_video.get("metadata", {}).get("published_at", "")
            target_date = target_video.get("metadata", {}).get("published_at", "")
            
            if source_date and target_date:
                try:
                    from datetime import datetime
                    source_dt = datetime.fromisoformat(source_date.replace('Z', '+00:00'))
                    target_dt = datetime.fromisoformat(target_date.replace('Z', '+00:00'))
                    
                    year_gap = abs(source_dt.year - target_dt.year)
                    if year_gap > 5:
                        return min(1.0, year_gap / 20)  # 20年で最大スコア
                except:
                    pass
        
        elif factor_name == "mood_inversion":
            source_mood = source_video.get("creative_insight", {}).get("music_analysis", {}).get("mood", "")
            target_mood = target_video.get("creative_insight", {}).get("music_analysis", {}).get("mood", "")
            
            opposite_moods = {
                ("happy", "sad"), ("energetic", "calm"), ("uplifting", "melancholy"),
                ("bright", "dark"), ("major", "minor")
            }
            
            if (source_mood, target_mood) in opposite_moods or (target_mood, source_mood) in opposite_moods:
                return 0.8
        
        return 0.0
    
    def _calculate_genre_distance(self, genre1: str, genre2: str) -> float:
        """ジャンル間の距離を計算"""
        # ジャンルマップ（簡略化）
        genre_map = {
            "pop": [0, 0], "rock": [2, 0], "jazz": [0, 2], "classical": [0, 4],
            "electronic": [4, 0], "folk": [-2, 2], "r&b": [1, 1], "hip-hop": [3, -1]
        }
        
        pos1 = genre_map.get(genre1.lower(), [0, 0])
        pos2 = genre_map.get(genre2.lower(), [0, 0])
        
        distance = math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
        return min(1.0, distance / 6.0)  # 正規化
    
    def _detect_surprise_elements(self, source_video: Dict[str, Any], target_video: Dict[str, Any]) -> List[str]:
        """意外性要素を検出"""
        elements = []
        
        # チャンネル・アーティストの違い
        source_channel = source_video.get("metadata", {}).get("channel_title", "")
        target_channel = target_video.get("metadata", {}).get("channel_title", "")
        
        if source_channel != target_channel:
            elements.append("異なるアーティスト")
        
        # 視聴数の大きな差
        source_views = source_video.get("metadata", {}).get("view_count", 0)
        target_views = target_video.get("metadata", {}).get("view_count", 0)
        
        if source_views > 0 and target_views > 0:
            view_ratio = max(source_views, target_views) / min(source_views, target_views)
            if view_ratio > 10:
                elements.append("人気度の対比")
        
        return elements
    
    def _evaluate_narrative_potential(self, connections: Dict[str, Any]) -> float:
        """ナラティブ潜在性を評価"""
        base_score = 0.0
        
        # 検出されたパターン数
        pattern_count = len(connections.get("detected_patterns", []))
        base_score += min(0.5, pattern_count * 0.1)
        
        # 意外性要素
        surprise_elements = len(connections.get("surprise_elements", []))
        base_score += min(0.3, surprise_elements * 0.15)
        
        # 主要関連性の強さ
        connection_strength = connections.get("connection_strength", 0.0)
        base_score += connection_strength * 0.4
        
        return min(1.0, base_score)
    
    def _generate_recommendation_narrative(self,
                                         source_video: Dict[str, Any],
                                         target_video: Dict[str, Any],
                                         connections: Dict[str, Any],
                                         user_emotion_analysis: Optional[Dict[str, Any]]) -> str:
        """推薦ナラティブを生成"""
        
        # 主要関連性タイプに基づくテンプレート選択
        primary_type = connections.get("primary_connection_type", "")
        connection_strength = connections.get("connection_strength", 0.0)
        
        # ナラティブカテゴリの決定
        if connection_strength > 0.8:
            narrative_category = "synergy_narrative"
        elif connections.get("surprise_elements"):
            narrative_category = "discovery_narrative"
        elif primary_type in ["emotional_resonance", "philosophical_link"]:
            narrative_category = "relationship_narrative"
        elif primary_type in ["contrasting_appeal", "mood_inversion"]:
            narrative_category = "transformation_narrative"
        else:
            narrative_category = "journey_narrative"
        
        # テンプレートの選択
        templates = self.narrative_templates.get(narrative_category, [])
        if not templates:
            return self._generate_basic_narrative(source_video, target_video)
        
        template = random.choice(templates)
        
        # テンプレート変数の準備
        variables = self._prepare_narrative_variables(source_video, target_video, connections, user_emotion_analysis)
        
        try:
            narrative = template.format(**variables)
            return narrative
        except KeyError:
            return self._generate_basic_narrative(source_video, target_video)
    
    def _prepare_narrative_variables(self,
                                   source_video: Dict[str, Any],
                                   target_video: Dict[str, Any],
                                   connections: Dict[str, Any],
                                   user_emotion_analysis: Optional[Dict[str, Any]]) -> Dict[str, str]:
        """ナラティブ変数を準備"""
        
        source_title = source_video.get("metadata", {}).get("title", "この楽曲")
        target_title = target_video.get("metadata", {}).get("title", "その楽曲")
        
        # 感情関連の変数
        emotion_keywords = ["温かい", "切ない", "力強い", "優しい", "情熱的", "神秘的", "懐かしい"]
        connection_keywords = ["心の奥で響き合う", "魂の深層で繋がる", "感情の波長が重なる", "精神的に共鳴する"]
        transformation_keywords = ["昇華", "進化", "変容", "深化", "発展"]
        
        variables = {
            "source_song": source_title,
            "target_song": target_title,
            "emotion": random.choice(emotion_keywords),
            "connection_reason": random.choice(connection_keywords),
            "evolution": random.choice(transformation_keywords),
            "hidden_quality": "隠された美しさ",
            "unexpected_element": "予想外の魅力",
            "surprise_element": "驚きの発見",
            "relationship_type": "音楽的な伴侶",
            "shared_quality": "共通する魂の響き",
            "personification": "一つの魂",
            "complementary_character": "理解し合う相手",
            "connection_metaphor": "見えない糸",
            "initial_state": "純粋な感情",
            "transformed_state": "深い洞察",
            "transformation_type": "新たな視点",
            "transformation_journey": "感情の成長",
            "synergy_effect": "相乗的な美しさ",
            "quality1": "独特の魅力",
            "quality2": "補完的な美しさ",
            "combined_effect": "完全な調和",
            "harmony_metaphor": "交響曲"
        }
        
        return variables
    
    def _generate_basic_narrative(self, source_video: Dict[str, Any], target_video: Dict[str, Any]) -> str:
        """基本的なナラティブを生成"""
        source_title = source_video.get("metadata", {}).get("title", "この楽曲")
        target_title = target_video.get("metadata", {}).get("title", "その楽曲")
        
        basic_templates = [
            f"{source_title}がお好きでしたら、{target_title}もきっと心に響くはずです。",
            f"{source_title}と{target_title}には、音楽的な親和性を感じます。",
            f"{source_title}の感動を、{target_title}でも体験していただけるでしょう。"
        ]
        
        return random.choice(basic_templates)
    
    def _calculate_creativity_score(self,
                                  connections: Dict[str, Any],
                                  surprise_score: float,
                                  narrative: str) -> float:
        """創造性スコアを計算"""
        base_score = 0.0
        
        # 関連性の強さ（40%）
        connection_strength = connections.get("connection_strength", 0.0)
        base_score += connection_strength * 0.4
        
        # 意外性（30%）
        base_score += surprise_score * 0.3
        
        # ナラティブ潜在性（20%）
        narrative_potential = connections.get("narrative_potential", 0.0)
        base_score += narrative_potential * 0.2
        
        # 多様性ボーナス（10%）
        pattern_diversity = len(connections.get("detected_patterns", []))
        diversity_bonus = min(0.1, pattern_diversity * 0.02)
        base_score += diversity_bonus
        
        return min(1.0, base_score)
    
    def _record_recommendation_generation(self, source_video: Dict[str, Any], recommendations: List[Dict[str, Any]]):
        """推薦生成を記録"""
        record = {
            "timestamp": datetime.now().isoformat(),
            "source_video_id": source_video.get("video_id", ""),
            "recommended_count": len(recommendations),
            "top_creativity_score": recommendations[0]["creativity_score"] if recommendations else 0.0,
            "patterns_used": []
        }
        
        for rec in recommendations:
            patterns = rec.get("creative_connections", {}).get("detected_patterns", [])
            record["patterns_used"].extend([p["pattern"] for p in patterns])
        
        record["patterns_used"] = list(set(record["patterns_used"]))  # 重複除去
        
        self.recommendation_history.append(record)
        
        # 履歴制限
        if len(self.recommendation_history) > 200:
            self.recommendation_history = self.recommendation_history[-200:]
        
        # 定期保存
        if len(self.recommendation_history) % 10 == 0:
            self._save_recommendation_data()
    
    def get_creativity_statistics(self) -> Dict[str, Any]:
        """創造性統計を取得"""
        if not self.recommendation_history:
            return {"message": "推薦履歴がありません"}
        
        recent_history = self.recommendation_history[-20:]  # 最近20件
        
        # 平均創造性スコア
        avg_creativity = sum(record.get("top_creativity_score", 0) for record in recent_history) / len(recent_history)
        
        # 使用パターンの分布
        all_patterns = []
        for record in recent_history:
            all_patterns.extend(record.get("patterns_used", []))
        
        pattern_counts = Counter(all_patterns)
        
        # 多様性スコア
        diversity_score = len(set(all_patterns)) / max(len(all_patterns), 1)
        
        return {
            "average_creativity_score": round(avg_creativity, 3),
            "total_recommendations": len(self.recommendation_history),
            "recent_recommendations": len(recent_history),
            "pattern_usage": dict(pattern_counts.most_common(5)),
            "diversity_score": round(diversity_score, 3),
            "most_used_pattern": pattern_counts.most_common(1)[0][0] if pattern_counts else "なし"
        }


# 使用例・テスト
if __name__ == "__main__":
    print("=== 創造的推薦システムテスト ===")
    
    system = CreativeRecommendationSystem()
    
    # テスト用動画データ
    test_source_video = {
        "video_id": "test_001",
        "metadata": {
            "title": "アドベンチャー",
            "channel_title": "YOASOBI",
            "published_at": "2023-01-01T00:00:00Z",
            "view_count": 1000000
        },
        "creative_insight": {
            "music_analysis": {
                "genre": "pop",
                "mood": "uplifting",
                "bpm": 120,
                "key": "C"
            },
            "themes": ["adventure", "youth", "hope"],
            "creators": [
                {"name": "Ayase", "role": "composer"},
                {"name": "ikura", "role": "vocal"}
            ]
        }
    }
    
    test_candidate_videos = [
        {
            "video_id": "test_002",
            "metadata": {
                "title": "夜に駆ける",
                "channel_title": "YOASOBI",
                "published_at": "2023-02-01T00:00:00Z",
                "view_count": 2000000
            },
            "creative_insight": {
                "music_analysis": {
                    "genre": "pop",
                    "mood": "energetic",
                    "bpm": 130,
                    "key": "G"
                },
                "themes": ["night", "speed", "emotion"],
                "creators": [
                    {"name": "Ayase", "role": "composer"},
                    {"name": "ikura", "role": "vocal"}
                ]
            }
        },
        {
            "video_id": "test_003",
            "metadata": {
                "title": "カノン",
                "channel_title": "Classical",
                "published_at": "1990-01-01T00:00:00Z",
                "view_count": 500000
            },
            "creative_insight": {
                "music_analysis": {
                    "genre": "classical",
                    "mood": "peaceful",
                    "bpm": 70,
                    "key": "D"
                },
                "themes": ["beauty", "harmony", "time"],
                "creators": [
                    {"name": "Pachelbel", "role": "composer"}
                ]
            }
        }
    ]
    
    # 創造的推薦生成テスト
    recommendations = system.generate_creative_recommendation(
        test_source_video, 
        test_candidate_videos,
        user_emotion_analysis={"dominant_emotions": [("joy", 0.8)]},
        context={"pattern_novelty": 0.7}
    )
    
    print(f"\n🎨 生成された創造的推薦: {len(recommendations)}件")
    
    for i, rec in enumerate(recommendations, 1):
        print(f"\n--- 推薦 {i} ---")
        print(f"動画: {rec['video_data']['metadata']['title']}")
        print(f"創造性スコア: {rec['creativity_score']:.3f}")
        print(f"意外性スコア: {rec['surprise_score']:.3f}")
        print(f"ナラティブ: {rec['narrative']}")
        
        connections = rec['creative_connections']
        print(f"検出パターン: {len(connections['detected_patterns'])}件")
        for pattern in connections['detected_patterns']:
            print(f"  - {pattern['pattern']}: {pattern['score']:.2f}")
    
    # 統計情報
    stats = system.get_creativity_statistics()
    print(f"\n📊 創造性統計:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    def _evaluate_emotional_resonance(self, source_video: Dict[str, Any], target_video: Dict[str, Any]) -> float:
        """感情的共鳴の評価"""
        source_insight = source_video.get("creative_insight", {})
        target_insight = target_video.get("creative_insight", {})
        
        # 楽曲分析から感情情報を取得
        source_music = source_insight.get("music_analysis", {})
        target_music = target_insight.get("music_analysis", {})
        
        score = 0.0
        
        # ムードの類似性
        source_mood = source_music.get("mood", "").lower()
        target_mood = target_music.get("mood", "").lower()
        
        if source_mood and target_mood:
            # 完全一致
            if source_mood == target_mood:
                score += 0.8
            # 関連ムード
            elif self._are_related_moods(source_mood, target_mood):
                score += 0.6
        
        # ジャンルの感情的類似性
        source_genre = source_music.get("genre", "").lower()
        target_genre = target_music.get("genre", "").lower()
        
        if source_genre and target_genre:
            genre_emotional_similarity = self._calculate_genre_emotional_similarity(source_genre, target_genre)
            score += genre_emotional_similarity * 0.4
        
        return min(1.0, score)
    
    def _evaluate_contrasting_appeal(self, source_video: Dict[str, Any], target_video: Dict[str, Any]) -> float:
        """対照的魅力の評価"""
        source_insight = source_video.get("creative_insight", {})
        target_insight = target_video.get("creative_insight", {})
        
        source_music = source_insight.get("music_analysis", {})
        target_music = target_insight.get("music_analysis", {})
        
        score = 0.0
        
        # ムードの対比
        source_mood = source_music.get("mood", "").lower()
        target_mood = target_music.get("mood", "").lower()
        
        if source_mood and target_mood and source_mood != target_mood:
            if self._are_contrasting_moods(source_mood, target_mood):
                score += 0.7
        
        # ジャンルの対比
        source_genre = source_music.get("genre", "").lower()
        target_genre = target_music.get("genre", "").lower()
        
        if source_genre and target_genre and source_genre != target_genre:
            if self._are_contrasting_genres(source_genre, target_genre):
                score += 0.5
        
        # テンポの対比（推測）
        source_title = source_video.get("metadata", {}).get("title", "").lower()
        target_title = target_video.get("metadata", {}).get("title", "").lower()
        
        tempo_contrast = self._detect_tempo_contrast(source_title, target_title)
        score += tempo_contrast * 0.3
        
        return min(1.0, score)
    
    def _evaluate_temporal_connection(self, source_video: Dict[str, Any], target_video: Dict[str, Any]) -> float:
        """時代的関連性の評価"""
        source_metadata = source_video.get("metadata", {})
        target_metadata = target_video.get("metadata", {})
        
        score = 0.0
        
        # 公開時期の分析
        source_published = source_metadata.get("published_at", "")
        target_published = target_metadata.get("published_at", "")
        
        if source_published and target_published:
            # 同時期（1年以内）
            time_diff = self._calculate_time_difference(source_published, target_published)
            if time_diff <= 365:  # 1年以内
                score += 0.6
            elif time_diff <= 1095:  # 3年以内
                score += 0.4
        
        # チャンネル・アーティストの活動時期
        source_channel = source_metadata.get("channel_title", "").lower()
        target_channel = target_metadata.get("channel_title", "").lower()
        
        if source_channel == target_channel:
            score += 0.8  # 同じチャンネル・アーティスト
        
        # 時代的テーマの検出
        temporal_themes = self._detect_temporal_themes(source_video, target_video)
        score += temporal_themes * 0.3
        
        return min(1.0, score)
    
    def _evaluate_artistic_technique(self, source_video: Dict[str, Any], target_video: Dict[str, Any]) -> float:
        """芸術的技法の評価"""
        source_insight = source_video.get("creative_insight", {})
        target_insight = target_video.get("creative_insight", {})
        
        score = 0.0
        
        # クリエイターの共通性
        source_creators = source_insight.get("creators", [])
        target_creators = target_insight.get("creators", [])
        
        if source_creators and target_creators:
            creator_overlap = self._calculate_creator_overlap(source_creators, target_creators)
            score += creator_overlap * 0.8
        
        # 楽曲制作技法の類似性
        source_music = source_insight.get("music_analysis", {})
        target_music = target_insight.get("music_analysis", {})
        
        # 構成の類似性（推測ベース）
        composition_similarity = self._evaluate_composition_similarity(source_music, target_music)
        score += composition_similarity * 0.5
        
        return min(1.0, score)
    
    def _evaluate_symbolic_connection(self, source_video: Dict[str, Any], target_video: Dict[str, Any]) -> float:
        """象徴的関連性の評価"""
        score = 0.0
        
        # タイトルの象徴的要素
        source_title = source_video.get("metadata", {}).get("title", "").lower()
        target_title = target_video.get("metadata", {}).get("title", "").lower()
        
        symbolic_overlap = self._detect_symbolic_overlap(source_title, target_title)
        score += symbolic_overlap * 0.6
        
        # 歌詞の象徴的テーマ（利用可能な場合）
        source_lyrics = source_video.get("creative_insight", {}).get("lyrics", {})
        target_lyrics = target_video.get("creative_insight", {}).get("lyrics", {})
        
        if source_lyrics and target_lyrics:
            lyrical_symbolism = self._analyze_lyrical_symbolism(source_lyrics, target_lyrics)
            score += lyrical_symbolism * 0.8
        
        return min(1.0, score)
    
    def _evaluate_musical_theory(self, source_video: Dict[str, Any], target_video: Dict[str, Any]) -> float:
        """音楽理論的関連性の評価"""
        source_music = source_video.get("creative_insight", {}).get("music_analysis", {})
        target_music = target_video.get("creative_insight", {}).get("music_analysis", {})
        
        score = 0.0
        
        # ジャンルの音楽理論的類似性
        source_genre = source_music.get("genre", "").lower()
        target_genre = target_music.get("genre", "").lower()
        
        if source_genre and target_genre:
            theory_similarity = self._calculate_musical_theory_similarity(source_genre, target_genre)
            score += theory_similarity * 0.7
        
        # 推定されるキー・スケールの関連性
        key_relationship = self._estimate_key_relationship(source_video, target_video)
        score += key_relationship * 0.5
        
        return min(1.0, score)
    
    def _evaluate_philosophical_link(self, source_video: Dict[str, Any], target_video: Dict[str, Any]) -> float:
        """哲学的関連性の評価"""
        score = 0.0
        
        # タイトルからの哲学的テーマ抽出
        source_title = source_video.get("metadata", {}).get("title", "").lower()
        target_title = target_video.get("metadata", {}).get("title", "").lower()
        
        philosophical_themes = self._extract_philosophical_themes(source_title, target_title)
        score += philosophical_themes * 0.8
        
        # 説明文からの人生観的テーマ
        source_desc = source_video.get("metadata", {}).get("description", "").lower()
        target_desc = target_video.get("metadata", {}).get("description", "").lower()
        
        if source_desc and target_desc:
            worldview_similarity = self._analyze_worldview_similarity(source_desc, target_desc)
            score += worldview_similarity * 0.6
        
        return min(1.0, score)
    
    def _are_related_moods(self, mood1: str, mood2: str) -> bool:
        """ムードが関連しているかチェック"""
        related_mood_groups = [
            {"明るい", "楽しい", "ハッピー", "ポジティブ"},
            {"暗い", "悲しい", "切ない", "メランコリー"},
            {"穏やか", "癒し", "リラックス", "平和"},
            {"激しい", "パワフル", "エネルギッシュ", "ドラマチック"}
        ]
        
        for group in related_mood_groups:
            if mood1 in group and mood2 in group:
                return True
        
        return False
    
    def _are_contrasting_moods(self, mood1: str, mood2: str) -> bool:
        """ムードが対照的かチェック"""
        contrasting_pairs = [
            ("明るい", "暗い"),
            ("楽しい", "悲しい"),
            ("激しい", "穏やか"),
            ("エネルギッシュ", "リラックス")
        ]
        
        for pair in contrasting_pairs:
            if (mood1 in pair and mood2 in pair) and mood1 != mood2:
                return True
        
        return False
    
    def _calculate_surprise_score(self, source_video: Dict[str, Any], target_video: Dict[str, Any], context: Optional[Dict[str, Any]]) -> float:
        """意外性スコアを計算"""
        surprise_score = 0.0
        
        # ジャンルの意外性
        source_genre = source_video.get("creative_insight", {}).get("music_analysis", {}).get("genre", "").lower()
        target_genre = target_video.get("creative_insight", {}).get("music_analysis", {}).get("genre", "").lower()
        
        if source_genre and target_genre and source_genre != target_genre:
            genre_distance = self._calculate_genre_distance(source_genre, target_genre)
            surprise_score += genre_distance * 0.4
        
        # チャンネル・アーティストの意外性
        source_channel = source_video.get("metadata", {}).get("channel_title", "").lower()
        target_channel = target_video.get("metadata", {}).get("channel_title", "").lower()
        
        if source_channel != target_channel:
            surprise_score += 0.3
        
        # 時代の意外性
        time_gap = self._calculate_temporal_surprise(source_video, target_video)
        surprise_score += time_gap * 0.2
        
        # 予想外の組み合わせボーナス
        unexpected_combination = self._detect_unexpected_combination(source_video, target_video)
        surprise_score += unexpected_combination * 0.3
        
        return min(1.0, surprise_score)
    
    def _generate_recommendation_narrative(self, 
                                         source_video: Dict[str, Any], 
                                         target_video: Dict[str, Any], 
                                         connections: Dict[str, Any],
                                         user_emotion_analysis: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """推薦ナラティブを生成"""
        
        # ナラティブテンプレートの選択
        narrative_type = self._select_narrative_type(connections, user_emotion_analysis)
        templates = self.narrative_templates.get(narrative_type, self.narrative_templates["discovery_narrative"])
        
        # テンプレート変数の構築
        template_vars = self._build_template_variables(source_video, target_video, connections)
        
        # テンプレートの選択と適用
        selected_template = random.choice(templates)
        
        try:
            narrative_text = selected_template.format(**template_vars)
        except KeyError:
            # フォールバック
            narrative_text = f"{template_vars['source_song']}から{template_vars['target_song']}への音楽的な旅路"
        
        return {
            "type": narrative_type,
            "text": narrative_text,
            "template_vars": template_vars,
            "narrative_strength": self._evaluate_narrative_strength(connections)
        }
    
    def _select_narrative_type(self, connections: Dict[str, Any], user_emotion_analysis: Optional[Dict[str, Any]]) -> str:
        """ナラティブタイプを選択"""
        primary_connection = connections.get("primary_connection_type", "")
        
        # 関連性タイプに基づくナラティブマッピング
        narrative_mapping = {
            "emotional_resonance": "relationship_narrative",
            "contrasting_appeal": "transformation_narrative",
            "temporal_connection": "journey_narrative",
            "artistic_technique": "synergy_narrative",
            "symbolic_connection": "discovery_narrative",
            "philosophical_link": "transformation_narrative"
        }
        
        # ユーザーの感情状態による調整
        if user_emotion_analysis:
            dominant_emotions = user_emotion_analysis.get("dominant_emotions", [])
            if dominant_emotions:
                primary_emotion = dominant_emotions[0][0]
                if primary_emotion in ["curiosity", "excitement"]:
                    return "discovery_narrative"
                elif primary_emotion in ["nostalgia", "contemplative"]:
                    return "journey_narrative"
        
        return narrative_mapping.get(primary_connection, "discovery_narrative")
    
    def _build_template_variables(self, source_video: Dict[str, Any], target_video: Dict[str, Any], connections: Dict[str, Any]) -> Dict[str, str]:
        """テンプレート変数を構築"""
        
        # 基本的な楽曲情報
        source_title = self._extract_clean_title(source_video.get("metadata", {}).get("title", ""))
        target_title = self._extract_clean_title(target_video.get("metadata", {}).get("title", ""))
        
        # 感情・特性の抽出
        source_emotion = self._extract_primary_emotion(source_video)
        target_emotion = self._extract_primary_emotion(target_video)
        
        # 関連性説明
        connection_reason = self._generate_connection_reason(connections)
        
        template_vars = {
            "source_song": source_title,
            "target_song": target_title,
            "emotion": source_emotion,
            "connection_reason": connection_reason,
            "evolution": self._generate_emotion_evolution(source_emotion, target_emotion),
            "hidden_quality": self._generate_hidden_quality(target_video),
            "unexpected_element": self._generate_unexpected_element(connections),
            "surprise_element": self._generate_surprise_element(connections),
            "relationship_type": self._generate_relationship_type(connections),
            "shared_quality": self._generate_shared_quality(source_video, target_video),
            "personification": self._generate_personification(source_video),
            "complementary_character": self._generate_complementary_character(target_video),
            "connection_metaphor": self._generate_connection_metaphor(connections),
            "initial_state": source_emotion,
            "transformed_state": target_emotion,
            "transformation_type": self._generate_transformation_type(source_emotion, target_emotion),
            "transformation_journey": self._generate_transformation_journey(connections),
            "synergy_effect": self._generate_synergy_effect(connections),
            "quality1": self._extract_key_quality(source_video),
            "quality2": self._extract_key_quality(target_video),
            "combined_effect": self._generate_combined_effect(source_video, target_video),
            "harmony_metaphor": self._generate_harmony_metaphor()
        }
        
        return template_vars
    
    def _extract_clean_title(self, title: str) -> str:
        """タイトルをクリーンアップ"""
        if not title:
            return "この楽曲"
        
        # 不要な装飾を除去
        cleaned = re.sub(r'【[^】]*】', '', title)
        cleaned = re.sub(r'\[[^\]]*\]', '', cleaned)
        cleaned = re.sub(r'\([^)]*\)', '', cleaned)
        cleaned = re.sub(r'Official.*', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'Music Video.*', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'MV.*', '', cleaned, flags=re.IGNORECASE)
        
        cleaned = cleaned.strip()
        
        return cleaned if cleaned else "この楽曲"
    
    def _extract_primary_emotion(self, video: Dict[str, Any]) -> str:
        """主要感情を抽出"""
        music_analysis = video.get("creative_insight", {}).get("music_analysis", {})
        mood = music_analysis.get("mood", "").lower()
        
        emotion_mapping = {
            "明るい": "喜び",
            "楽しい": "楽しさ",
            "悲しい": "悲しみ",
            "切ない": "切なさ",
            "穏やか": "安らぎ",
            "激しい": "情熱"
        }
        
        return emotion_mapping.get(mood, "感動")
    
    def _calculate_creativity_score(self, connections: Dict[str, Any], surprise_score: float, narrative: Dict[str, Any]) -> float:
        """創造性スコアを計算"""
        # 関連性の強度
        connection_strength = connections.get("connection_strength", 0.0)
        
        # ナラティブの強度
        narrative_strength = narrative.get("narrative_strength", 0.0)
        
        # 意外性の価値
        surprise_value = surprise_score
        
        # 検出されたパターンの多様性
        pattern_diversity = len(connections.get("detected_patterns", [])) / len(self.creative_patterns)
        
        # 総合創造性スコア
        creativity_score = (
            connection_strength * 0.3 +
            narrative_strength * 0.3 +
            surprise_value * 0.2 +
            pattern_diversity * 0.2
        )
        
        return min(1.0, creativity_score)
    
    def _record_recommendation_generation(self, source_video: Dict[str, Any], recommendations: List[Dict[str, Any]]):
        """推薦生成を記録"""
        record = {
            "timestamp": datetime.now().isoformat(),
            "source_video_id": source_video.get("video_id", ""),
            "recommendation_count": len(recommendations),
            "average_creativity_score": sum(r["creativity_score"] for r in recommendations) / len(recommendations) if recommendations else 0,
            "top_connection_types": [r.get("creative_connections", {}).get("primary_connection_type", "") for r in recommendations[:3]]
        }
        
        self.recommendation_history.append(record)
        
        # 履歴サイズ制限
        if len(self.recommendation_history) > 200:
            self.recommendation_history = self.recommendation_history[-200:]
        
        # 定期的に保存
        if len(self.recommendation_history) % 20 == 0:
            self._save_recommendation_data()
    
    # 以下、ヘルパーメソッドの簡易実装
    def _calculate_genre_emotional_similarity(self, genre1: str, genre2: str) -> float:
        """ジャンル間感情類似度（簡易実装）"""
        similar_groups = [
            {"ポップス", "j-pop", "pop"},
            {"ボカロ", "vocaloid"},
            {"ロック", "rock"},
            {"バラード", "ballad"}
        ]
        
        for group in similar_groups:
            if genre1 in group and genre2 in group:
                return 0.8
        
        return 0.2
    
    def _are_contrasting_genres(self, genre1: str, genre2: str) -> bool:
        """ジャンルが対照的かチェック（簡易実装）"""
        contrasting_pairs = [
            ("ポップス", "ロック"),
            ("バラード", "アップテンポ"),
            ("クラシック", "エレクトロニック")
        ]
        
        for pair in contrasting_pairs:
            if genre1 in pair and genre2 in pair and genre1 != genre2:
                return True
        
        return False
    
    def _generate_connection_reason(self, connections: Dict[str, Any]) -> str:
        """関連性理由を生成（簡易実装）"""
        primary_type = connections.get("primary_connection_type", "")
        
        reason_templates = {
            "emotional_resonance": "同じ心の深いところで響き合う",
            "contrasting_appeal": "対照的でありながら補完し合う",
            "temporal_connection": "時代を超えた共通のテーマで繋がる",
            "artistic_technique": "創作における技法的な親和性",
            "symbolic_connection": "象徴的な意味での深い関連性",
            "philosophical_link": "人生への同じ問いかけを持つ"
        }
        
        return reason_templates.get(primary_type, "予期しない美しい関連性を持つ")
    
    # その他のヘルパーメソッドは簡易実装
    def _generate_emotion_evolution(self, source_emotion: str, target_emotion: str) -> str:
        return f"{source_emotion}から{target_emotion}への成長"
    
    def _generate_hidden_quality(self, video: Dict[str, Any]) -> str:
        return "隠された美しさ"
    
    def _generate_unexpected_element(self, connections: Dict[str, Any]) -> str:
        return "予想外の魅力"
    
    def _generate_surprise_element(self, connections: Dict[str, Any]) -> str:
        return "驚くべき発見"
    
    def _generate_relationship_type(self, connections: Dict[str, Any]) -> str:
        return "姉妹楽曲"
    
    def _generate_shared_quality(self, source_video: Dict[str, Any], target_video: Dict[str, Any]) -> str:
        return "深い感動"
    
    def _generate_personification(self, video: Dict[str, Any]) -> str:
        return "優しい友人"
    
    def _generate_complementary_character(self, video: Dict[str, Any]) -> str:
        return "理解ある相手"
    
    def _generate_connection_metaphor(self, connections: Dict[str, Any]) -> str:
        return "見えない糸"
    
    def _generate_transformation_type(self, source_emotion: str, target_emotion: str) -> str:
        return "感情の昇華"
    
    def _generate_transformation_journey(self, connections: Dict[str, Any]) -> str:
        return "心の成長"
    
    def _generate_synergy_effect(self, connections: Dict[str, Any]) -> str:
        return "新しい感動"
    
    def _extract_key_quality(self, video: Dict[str, Any]) -> str:
        return "独特の魅力"
    
    def _generate_combined_effect(self, source_video: Dict[str, Any], target_video: Dict[str, Any]) -> str:
        return "相乗効果的な美しさ"
    
    def _generate_harmony_metaphor(self) -> str:
        return "美しいハーモニー"
    
    def _evaluate_narrative_strength(self, connections: Dict[str, Any]) -> float:
        return connections.get("narrative_potential", 0.5)
    
    def _calculate_time_difference(self, date1: str, date2: str) -> int:
        """日付差分計算（簡易実装）"""
        return 365  # デフォルト値
    
    def _detect_temporal_themes(self, source_video: Dict[str, Any], target_video: Dict[str, Any]) -> float:
        return 0.5
    
    def _calculate_creator_overlap(self, creators1: List[Dict], creators2: List[Dict]) -> float:
        return 0.5
    
    def _evaluate_composition_similarity(self, music1: Dict, music2: Dict) -> float:
        return 0.5
    
    def _detect_symbolic_overlap(self, title1: str, title2: str) -> float:
        return 0.5
    
    def _analyze_lyrical_symbolism(self, lyrics1: Dict, lyrics2: Dict) -> float:
        return 0.5
    
    def _calculate_musical_theory_similarity(self, genre1: str, genre2: str) -> float:
        return 0.5
    
    def _estimate_key_relationship(self, video1: Dict, video2: Dict) -> float:
        return 0.5
    
    def _extract_philosophical_themes(self, title1: str, title2: str) -> float:
        return 0.5
    
    def _analyze_worldview_similarity(self, desc1: str, desc2: str) -> float:
        return 0.5
    
    def _calculate_genre_distance(self, genre1: str, genre2: str) -> float:
        return 0.5
    
    def _calculate_temporal_surprise(self, video1: Dict, video2: Dict) -> float:
        return 0.5
    
    def _detect_unexpected_combination(self, video1: Dict, video2: Dict) -> float:
        return 0.5
    
    def _detect_surprise_elements(self, source_video: Dict, target_video: Dict) -> List[str]:
        return ["genre_transcendence"]
    
    def _evaluate_narrative_potential(self, connections: Dict) -> float:
        return 0.7
    
    def _detect_tempo_contrast(self, title1: str, title2: str) -> float:
        return 0.3


# 使用例・テスト
if __name__ == "__main__":
    print("=== 創造的推薦システムテスト ===")
    
    system = CreativeRecommendationSystem()
    
    # テスト用動画データ
    source_video = {
        "video_id": "test1",
        "metadata": {"title": "アドベンチャー", "channel_title": "YOASOBI"},
        "creative_insight": {
            "music_analysis": {"genre": "ポップス", "mood": "明るい"},
            "creators": [{"name": "Ayase", "role": "composer"}]
        }
    }
    
    candidate_videos = [
        {
            "video_id": "test2",
            "metadata": {"title": "XOXO", "channel_title": "TRiNITY"},
            "creative_insight": {
                "music_analysis": {"genre": "ポップス", "mood": "明るい"},
                "creators": [{"name": "MATZ", "role": "composer"}]
            }
        }
    ]
    
    # 創造的推薦生成
    recommendations = system.generate_creative_recommendation(
        source_video, candidate_videos
    )
    
    print(f"\n🎨 創造的推薦結果:")
    for rec in recommendations:
        print(f"楽曲: {rec['video_data']['metadata']['title']}")
        print(f"創造性スコア: {rec['creativity_score']:.2f}")
        print(f"関連性: {rec['creative_connections']['primary_connection_type']}")
        print(f"ナラティブ: {rec['narrative']['text']}")
        print("---")
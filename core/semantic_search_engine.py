#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
セマンティック検索エンジン - Phase 2A実装
自然言語による意味ベースの高精度動画検索システム
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
import re
import math
from collections import defaultdict, Counter
from datetime import datetime
import hashlib

# プロジェクトルートをパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Windowsパス設定
if os.name == 'nt':
    DATA_DIR = Path("D:/setsuna_bot/youtube_knowledge_system/data")
    CACHE_DIR = Path("D:/setsuna_bot/semantic_search_cache")
else:
    DATA_DIR = Path("/mnt/d/setsuna_bot/youtube_knowledge_system/data")
    CACHE_DIR = Path("/mnt/d/setsuna_bot/semantic_search_cache")

CACHE_DIR.mkdir(parents=True, exist_ok=True)

@dataclass
class SearchResult:
    """検索結果データクラス"""
    video_id: str
    title: str
    artist: str
    relevance_score: float
    semantic_matches: List[str]
    content_type: str  # "music", "gameplay", "talk", "tutorial" etc.
    confidence: float
    matched_keywords: List[str]
    context_relevance: float  # コンテキスト関連度

@dataclass
class SemanticQuery:
    """セマンティッククエリデータクラス"""
    original_query: str
    normalized_query: str
    extracted_keywords: List[str]
    intent_type: str  # "search", "recommendation", "comparison", "analysis"
    target_attributes: List[str]  # "title", "artist", "genre", "mood", "theme"
    temporal_context: Optional[str]  # "recent", "classic", "trending"

class SemanticSearchEngine:
    """セマンティック検索エンジンクラス"""
    
    def __init__(self):
        """初期化"""
        self.knowledge_db_path = DATA_DIR / "unified_knowledge_db.json"
        self.search_cache_path = CACHE_DIR / "semantic_search_cache.json"
        self.knowledge_db = {}
        self.search_cache = {}
        
        # 意味解析用辞書とパターン
        self.semantic_patterns = self._build_semantic_patterns()
        self.keyword_synonyms = self._build_keyword_synonyms()
        self.genre_mappings = self._build_genre_mappings()
        self.mood_indicators = self._build_mood_indicators()
        
        # 統計情報
        self.search_statistics = {
            "total_searches": 0,
            "cache_hits": 0,
            "average_results": 0,
            "query_types": defaultdict(int)
        }
        
        self._load_knowledge_db()
        self._load_search_cache()
        
        print("[セマンティック検索] ✅ セマンティック検索エンジン初期化完了")
    
    def _build_semantic_patterns(self) -> Dict[str, List[str]]:
        """セマンティックパターンを構築"""
        return {
            "search_intent": [
                r"(.+)(を|の)?(探し|検索|見つけ|知り)たい",
                r"(.+)(ある|ない)?(か|？)?",
                r"(.+)(について|に関して)(教えて|聞かせて)",
                r"(.+)(どう|どんな)(感じ|印象|思う)",
                r"(.+)(おすすめ|推薦)(して|の|は)",
            ],
            "recommendation_intent": [
                r"(何か|どんな|いい)(.+)(ない|ある)?(か|？)?",
                r"(新しい|最近の|今の)(.+)(教えて|紹介)",
                r"(似た|同じような)(.+)(ない|ある)?(か|？)?",
                r"(次に|今度)(何|どれ)(.+)(いい|おすすめ)",
            ],
            "comparison_intent": [
                r"(.+)(と)(.+)(比べ|違い|差)",
                r"(.+)(より)(.+)(いい|良い|好き)",
                r"(.+)(どっち|どちら)(が|の方が)",
            ],
            "analysis_intent": [
                r"(.+)(分析|解析|評価)(して|を)",
                r"(.+)(特徴|魅力|良さ)(は|って|を)",
                r"(.+)(なぜ|どうして)(.+)(なの|だろう)",
            ]
        }
    
    def _build_keyword_synonyms(self) -> Dict[str, List[str]]:
        """キーワード同義語辞書を構築"""
        return {
            "音楽": ["曲", "歌", "ミュージック", "サウンド", "楽曲", "音源"],
            "動画": ["映像", "ビデオ", "コンテンツ", "チャンネル", "配信"],
            "ゲーム": ["プレイ", "実況", "配信", "ストリーム", "ゲーミング"],
            "アニメ": ["アニメーション", "二次元", "漫画", "マンガ"],
            "ボカロ": ["ボーカロイド", "初音ミク", "VOCALOID", "歌声合成"],
            "ロック": ["ロックミュージック", "バンド", "ギター"],
            "ポップ": ["ポップス", "J-POP", "流行歌"],
            "クラシック": ["クラシック音楽", "オーケストラ", "交響曲"],
            "EDM": ["電子音楽", "エレクトロニック", "ダンスミュージック"],
            "バラード": ["スローソング", "感動的", "泣ける"],
            "アップテンポ": ["元気", "明るい", "ノリがいい", "テンション高い"],
            "癒し": ["リラックス", "穏やか", "安らぎ", "落ち着く"],
            "かっこいい": ["クール", "スタイリッシュ", "格好良い"],
            "可愛い": ["キュート", "愛らしい", "かわいい"],
            "感動": ["泣ける", "心に響く", "感激", "胸熱"],
            "面白い": ["楽しい", "おもしろい", "笑える", "ユニーク"]
        }
    
    def _build_genre_mappings(self) -> Dict[str, List[str]]:
        """ジャンルマッピングを構築"""
        return {
            "ロック": ["rock", "ハードロック", "パンク", "メタル", "オルタナティブ"],
            "ポップ": ["pop", "J-POP", "アイドル", "mainstream"],
            "電子音楽": ["EDM", "テクノ", "ハウス", "dubstep", "エレクトロニカ"],
            "クラシック": ["classical", "オーケストラ", "室内楽", "オペラ"],
            "ジャズ": ["jazz", "ブルース", "フュージョン", "スイング"],
            "ヒップホップ": ["hip-hop", "rap", "トラップ", "R&B"],
            "フォーク": ["folk", "アコースティック", "カントリー"],
            "アニソン": ["アニメソング", "キャラソン", "ゲーソン", "声優"],
            "ボカロ": ["VOCALOID", "初音ミク", "歌声合成", "ニコニコ"]
        }
    
    def _build_mood_indicators(self) -> Dict[str, List[str]]:
        """ムード指標を構築"""
        return {
            "明るい": ["楽しい", "ハッピー", "元気", "ポジティブ", "陽気", "爽やか"],
            "暗い": ["悲しい", "メランコリック", "憂鬱", "重い", "シリアス"],
            "激しい": ["エネルギッシュ", "パワフル", "ダイナミック", "アグレッシブ"],
            "穏やか": ["リラックス", "癒し", "平和", "安らぎ", "静か"],
            "ノスタルジック": ["懐かしい", "昔", "レトロ", "思い出"],
            "ロマンチック": ["恋愛", "愛", "甘い", "ドラマチック"],
            "クール": ["かっこいい", "スタイリッシュ", "洗練された"],
            "キュート": ["可愛い", "愛らしい", "チャーミング"]
        }
    
    def _load_knowledge_db(self):
        """知識データベースをロード"""
        try:
            if self.knowledge_db_path.exists():
                with open(self.knowledge_db_path, 'r', encoding='utf-8') as f:
                    self.knowledge_db = json.load(f)
                video_count = len(self.knowledge_db.get("videos", {}))
                print(f"[セマンティック検索] 📊 {video_count}件の動画データをロード")
            else:
                print(f"[セマンティック検索] ⚠️ データベースファイルが見つかりません: {self.knowledge_db_path}")
        except Exception as e:
            print(f"[セマンティック検索] ❌ データベースロードエラー: {e}")
    
    def _load_search_cache(self):
        """検索キャッシュをロード"""
        try:
            if self.search_cache_path.exists():
                with open(self.search_cache_path, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    self.search_cache = cache_data.get("searches", {})
                    self.search_statistics = cache_data.get("statistics", self.search_statistics)
                print(f"[セマンティック検索] 💾 {len(self.search_cache)}件のキャッシュをロード")
        except Exception as e:
            print(f"[セマンティック検索] ⚠️ キャッシュロードエラー: {e}")
    
    def _save_search_cache(self):
        """検索キャッシュを保存"""
        try:
            cache_data = {
                "searches": self.search_cache,
                "statistics": dict(self.search_statistics),
                "last_updated": datetime.now().isoformat()
            }
            with open(self.search_cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[セマンティック検索] ⚠️ キャッシュ保存エラー: {e}")
    
    def parse_semantic_query(self, query: str) -> SemanticQuery:
        """クエリをセマンティック解析"""
        normalized_query = query.strip().lower()
        
        # インテント分析
        intent_type = "search"  # デフォルト
        for intent, patterns in self.semantic_patterns.items():
            for pattern in patterns:
                if re.search(pattern, normalized_query):
                    intent_type = intent.replace("_intent", "")
                    break
            if intent_type != "search":
                break
        
        # キーワード抽出
        extracted_keywords = self._extract_keywords(normalized_query)
        
        # ターゲット属性判定
        target_attributes = self._determine_target_attributes(normalized_query)
        
        # 時間的コンテキスト
        temporal_context = self._detect_temporal_context(normalized_query)
        
        return SemanticQuery(
            original_query=query,
            normalized_query=normalized_query,
            extracted_keywords=extracted_keywords,
            intent_type=intent_type,
            target_attributes=target_attributes,
            temporal_context=temporal_context
        )
    
    def _extract_keywords(self, text: str) -> List[str]:
        """キーワード抽出"""
        keywords = []
        
        # 直接的なキーワード抽出
        for main_keyword, synonyms in self.keyword_synonyms.items():
            if main_keyword in text or any(syn in text for syn in synonyms):
                keywords.append(main_keyword)
        
        # ジャンル関連キーワード
        for genre, terms in self.genre_mappings.items():
            if any(term in text for term in terms):
                keywords.append(genre)
        
        # ムード関連キーワード
        for mood, indicators in self.mood_indicators.items():
            if any(indicator in text for indicator in indicators):
                keywords.append(mood)
        
        # 一般的な音楽用語
        music_terms = ["アーティスト", "歌手", "バンド", "グループ", "ソロ", "デュオ"]
        for term in music_terms:
            if term in text:
                keywords.append(term)
        
        return list(set(keywords))
    
    def _determine_target_attributes(self, text: str) -> List[str]:
        """検索対象属性を判定"""
        attributes = []
        
        title_indicators = ["タイトル", "曲名", "名前", "題名"]
        if any(indicator in text for indicator in title_indicators):
            attributes.append("title")
        
        artist_indicators = ["アーティスト", "歌手", "バンド", "クリエイター"]
        if any(indicator in text for indicator in artist_indicators):
            attributes.append("artist")
        
        genre_indicators = ["ジャンル", "種類", "カテゴリ"]
        if any(indicator in text for indicator in genre_indicators):
            attributes.append("genre")
        
        mood_indicators = ["雰囲気", "ムード", "感じ", "印象"]
        if any(indicator in text for indicator in mood_indicators):
            attributes.append("mood")
        
        # デフォルトは全属性
        if not attributes:
            attributes = ["title", "artist", "genre", "mood", "theme"]
        
        return attributes
    
    def _detect_temporal_context(self, text: str) -> Optional[str]:
        """時間的コンテキストを検出"""
        recent_indicators = ["最近", "新しい", "今の", "現在", "今年"]
        if any(indicator in text for indicator in recent_indicators):
            return "recent"
        
        classic_indicators = ["昔", "古い", "クラシック", "過去", "懐かしい"]
        if any(indicator in text for indicator in classic_indicators):
            return "classic"
        
        trending_indicators = ["人気", "流行", "トレンド", "話題"]
        if any(indicator in text for indicator in trending_indicators):
            return "trending"
        
        return None
    
    def search(self, query: str, max_results: int = 10, use_cache: bool = True) -> List[SearchResult]:
        """セマンティック検索実行"""
        # キャッシュチェック
        if use_cache:
            cache_key = self._generate_cache_key(query, max_results)
            if cache_key in self.search_cache:
                self.search_statistics["cache_hits"] += 1
                cached_results = self.search_cache[cache_key]
                return [SearchResult(**result) for result in cached_results]
        
        # セマンティック解析
        semantic_query = self.parse_semantic_query(query)
        
        # 検索実行
        search_results = self._execute_semantic_search(semantic_query, max_results)
        
        # 統計更新
        self.search_statistics["total_searches"] += 1
        self.search_statistics["query_types"][semantic_query.intent_type] += 1
        
        # キャッシュ保存
        if use_cache:
            cache_key = self._generate_cache_key(query, max_results)
            self.search_cache[cache_key] = [asdict(result) for result in search_results]
            self._save_search_cache()
        
        return search_results
    
    def _generate_cache_key(self, query: str, max_results: int) -> str:
        """キャッシュキー生成"""
        content = f"{query}_{max_results}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def _execute_semantic_search(self, semantic_query: SemanticQuery, max_results: int) -> List[SearchResult]:
        """セマンティック検索実行"""
        results = []
        videos = self.knowledge_db.get("videos", {})
        
        for video_id, video_data in videos.items():
            # 関連性スコア計算
            relevance_score = self._calculate_relevance_score(video_data, semantic_query)
            
            if relevance_score > 0.1:  # 最小閾値
                # 検索結果作成
                result = self._create_search_result(
                    video_id, video_data, semantic_query, relevance_score
                )
                results.append(result)
        
        # スコア順でソート
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        # 結果数制限
        return results[:max_results]
    
    def _calculate_relevance_score(self, video_data: Dict, semantic_query: SemanticQuery) -> float:
        """関連性スコア計算"""
        total_score = 0.0
        max_score = 0.0
        
        metadata = video_data.get("metadata", {})
        creative_insight = video_data.get("creative_insight", {})
        
        # タイトル一致度 (30%)
        title_score = self._calculate_text_similarity(
            metadata.get("title", ""), semantic_query.normalized_query
        )
        total_score += title_score * 0.3
        max_score += 0.3
        
        # アーティスト/チャンネル一致度 (20%)
        channel_title = metadata.get("channel_title", "")
        artist_score = self._calculate_text_similarity(
            channel_title, semantic_query.normalized_query
        )
        total_score += artist_score * 0.2
        max_score += 0.2
        
        # キーワード一致度 (25%)
        keyword_score = self._calculate_keyword_similarity(
            video_data, semantic_query.extracted_keywords
        )
        total_score += keyword_score * 0.25
        max_score += 0.25
        
        # テーマ/ジャンル一致度 (15%)
        theme_score = self._calculate_theme_similarity(
            creative_insight, semantic_query.extracted_keywords
        )
        total_score += theme_score * 0.15
        max_score += 0.15
        
        # 時間的関連性 (10%)
        temporal_score = self._calculate_temporal_relevance(
            metadata, semantic_query.temporal_context
        )
        total_score += temporal_score * 0.1
        max_score += 0.1
        
        # 正規化
        return total_score / max_score if max_score > 0 else 0.0
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """テキスト類似度計算"""
        if not text1 or not text2:
            return 0.0
        
        text1_lower = text1.lower()
        text2_lower = text2.lower()
        
        # 完全一致
        if text2_lower in text1_lower:
            return 1.0
        
        # 部分一致
        words1 = set(text1_lower.split())
        words2 = set(text2_lower.split())
        
        if words1 and words2:
            intersection = words1.intersection(words2)
            union = words1.union(words2)
            return len(intersection) / len(union)
        
        return 0.0
    
    def _calculate_keyword_similarity(self, video_data: Dict, keywords: List[str]) -> float:
        """キーワード類似度計算"""
        if not keywords:
            return 0.0
        
        video_text = " ".join([
            video_data.get("metadata", {}).get("title", ""),
            video_data.get("metadata", {}).get("description", ""),
            " ".join(video_data.get("metadata", {}).get("tags", []))
        ]).lower()
        
        matches = 0
        for keyword in keywords:
            # 直接一致
            if keyword.lower() in video_text:
                matches += 1
                continue
            
            # 同義語一致
            synonyms = self.keyword_synonyms.get(keyword, [])
            if any(syn.lower() in video_text for syn in synonyms):
                matches += 1
        
        return matches / len(keywords)
    
    def _calculate_theme_similarity(self, creative_insight: Dict, keywords: List[str]) -> float:
        """テーマ類似度計算"""
        if not keywords or not creative_insight:
            return 0.0
        
        themes = creative_insight.get("themes", [])
        if not themes:
            return 0.0
        
        theme_text = " ".join(themes).lower()
        
        matches = 0
        for keyword in keywords:
            if keyword.lower() in theme_text:
                matches += 1
        
        return matches / len(keywords) if keywords else 0.0
    
    def _calculate_temporal_relevance(self, metadata: Dict, temporal_context: Optional[str]) -> float:
        """時間的関連性計算"""
        if not temporal_context:
            return 0.5  # 中性値
        
        published_at = metadata.get("published_at", "")
        if not published_at:
            return 0.5
        
        try:
            pub_date = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
            now = datetime.now()
            days_ago = (now - pub_date).days
            
            if temporal_context == "recent":
                # 最近（30日以内）
                return max(0.0, 1.0 - days_ago / 365)
            elif temporal_context == "classic":
                # 古い（1年以上前）
                return min(1.0, days_ago / 365)
            elif temporal_context == "trending":
                # 人気度に基づく（view_count使用）
                view_count = metadata.get("view_count", 0)
                if view_count > 100000:
                    return 1.0
                elif view_count > 10000:
                    return 0.7
                else:
                    return 0.3
        except:
            pass
        
        return 0.5
    
    def _create_search_result(self, video_id: str, video_data: Dict, 
                            semantic_query: SemanticQuery, relevance_score: float) -> SearchResult:
        """検索結果作成"""
        metadata = video_data.get("metadata", {})
        custom_info = video_data.get("custom_info", {})
        
        # タイトルとアーティスト
        title = custom_info.get("manual_title") or metadata.get("title", "Unknown")
        artist = custom_info.get("manual_artist") or metadata.get("channel_title", "Unknown")
        
        # 一致したキーワード
        matched_keywords = [
            kw for kw in semantic_query.extracted_keywords 
            if kw.lower() in (title + " " + artist).lower()
        ]
        
        # セマンティックマッチ
        semantic_matches = []
        for keyword in semantic_query.extracted_keywords:
            if keyword in self.keyword_synonyms:
                semantic_matches.append(f"{keyword} (意味的一致)")
        
        # コンテンツタイプ判定
        content_type = self._determine_content_type(video_data)
        
        # コンテキスト関連度
        context_relevance = self._calculate_context_relevance(video_data, semantic_query)
        
        return SearchResult(
            video_id=video_id,
            title=title,
            artist=artist,
            relevance_score=relevance_score,
            semantic_matches=semantic_matches,
            content_type=content_type,
            confidence=min(1.0, relevance_score * 1.2),
            matched_keywords=matched_keywords,
            context_relevance=context_relevance
        )
    
    def _determine_content_type(self, video_data: Dict) -> str:
        """コンテンツタイプ判定"""
        metadata = video_data.get("metadata", {})
        title = metadata.get("title", "").lower()
        description = metadata.get("description", "").lower()
        tags = " ".join(metadata.get("tags", [])).lower()
        
        content_text = f"{title} {description} {tags}"
        
        if any(word in content_text for word in ["music", "ミュージック", "歌", "曲", "mv"]):
            return "music"
        elif any(word in content_text for word in ["ゲーム", "game", "実況", "プレイ"]):
            return "gameplay"
        elif any(word in content_text for word in ["talk", "トーク", "雑談", "配信"]):
            return "talk"
        elif any(word in content_text for word in ["tutorial", "解説", "講座", "教え"]):
            return "tutorial"
        else:
            return "general"
    
    def _calculate_context_relevance(self, video_data: Dict, semantic_query: SemanticQuery) -> float:
        """コンテキスト関連度計算"""
        # インテントタイプに基づく関連度調整
        base_relevance = 0.5
        
        content_type = self._determine_content_type(video_data)
        
        if semantic_query.intent_type == "recommendation":
            # 推薦の場合、人気度を考慮
            view_count = video_data.get("metadata", {}).get("view_count", 0)
            if view_count > 50000:
                base_relevance += 0.3
        
        elif semantic_query.intent_type == "analysis":
            # 分析の場合、詳細情報があるかを考慮
            creative_insight = video_data.get("creative_insight", {})
            if creative_insight.get("themes") or creative_insight.get("insights"):
                base_relevance += 0.4
        
        return min(1.0, base_relevance)
    
    def get_search_statistics(self) -> Dict[str, Any]:
        """検索統計情報取得"""
        return dict(self.search_statistics)
    
    def clear_cache(self):
        """キャッシュクリア"""
        self.search_cache.clear()
        self._save_search_cache()
        print("[セマンティック検索] 🗑️ キャッシュをクリアしました")
    
    def suggest_related_queries(self, query: str) -> List[str]:
        """関連クエリ提案"""
        semantic_query = self.parse_semantic_query(query)
        suggestions = []
        
        # キーワードベースの提案
        for keyword in semantic_query.extracted_keywords:
            if keyword in self.keyword_synonyms:
                for synonym in self.keyword_synonyms[keyword][:2]:
                    suggestions.append(f"{synonym}の動画")
        
        # インテントベースの提案
        if semantic_query.intent_type == "search":
            suggestions.extend([
                f"{query}に似た曲",
                f"{query}のおすすめ",
                f"{query}について詳しく"
            ])
        
        return suggestions[:5]  # 上位5件
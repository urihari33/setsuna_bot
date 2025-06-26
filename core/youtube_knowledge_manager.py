#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube知識管理システム - せつなBot統合用
YouTube動画データベースとの連携機能を提供
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
import re
from datetime import datetime


class YouTubeKnowledgeManager:
    """YouTube動画知識を管理するクラス"""
    
    def __init__(self):
        """初期化"""
        # Windows環境とWSL2環境両方に対応
        if os.name == 'nt':  # Windows
            self.knowledge_db_path = Path("D:/setsuna_bot/youtube_knowledge_system/data/unified_knowledge_db.json")
        else:  # Linux/WSL2
            self.knowledge_db_path = Path("/mnt/d/setsuna_bot/youtube_knowledge_system/data/unified_knowledge_db.json")
        self.knowledge_db = {}
        self.video_cache = {}  # 話題になった動画のキャッシュ
        
        self._load_knowledge_db()
        print("[YouTube知識] ✅ YouTube知識管理システム初期化完了")
    
    def _load_knowledge_db(self):
        """知識データベースをロード"""
        try:
            if not self.knowledge_db_path.exists():
                print(f"[YouTube知識] ⚠️ データベースファイルが見つかりません: {self.knowledge_db_path}")
                self.knowledge_db = {"videos": {}, "playlists": {}}
                return
            
            with open(self.knowledge_db_path, 'r', encoding='utf-8') as f:
                self.knowledge_db = json.load(f)
            
            video_count = len(self.knowledge_db.get("videos", {}))
            playlist_count = len(self.knowledge_db.get("playlists", {}))
            print(f"[YouTube知識] 📊 動画: {video_count}件, プレイリスト: {playlist_count}件 をロード")
            
        except Exception as e:
            print(f"[YouTube知識] ❌ データベース読み込み失敗: {e}")
            self.knowledge_db = {"videos": {}, "playlists": {}}
    
    def _normalize_title(self, title: str) -> str:
        """
        タイトルを検索用に正規化
        
        Args:
            title: 元のタイトル
            
        Returns:
            正規化されたタイトル
        """
        # 記号・装飾の除去
        normalized = title
        
        # YouTubeタイトル特有のパターンを除去
        patterns_to_remove = [
            r'【[^】]*】',  # 【】内
            r'\[[^\]]*\]',  # []内
            r'〈[^〉]*〉',   # 〈〉内
            r'《[^》]*》',   # 《》内
            r'「[^」]*」',   # 投稿日時など
            r'Music Video|MV|Official|オフィシャル',  # 一般的な装飾語
            r'／.*$',      # スラッシュ以降
            r'\s*-\s*.*$', # ハイフン以降（アーティスト名など）
        ]
        
        for pattern in patterns_to_remove:
            normalized = re.sub(pattern, '', normalized, flags=re.IGNORECASE)
        
        # 特殊記号の除去・統一
        symbol_replacements = [
            (r'▽▲([^▲▽]*)▲▽', r'\1'),  # TRiNITY記号除去
            (r'[『』]', ''),  # 特殊括弧
            (r'[（）()]', ''),  # 括弧
            (r'[・｜|]', ' '),  # 区切り文字をスペースに
            (r'\s+', ' '),  # 連続スペースを統一
        ]
        
        for pattern, replacement in symbol_replacements:
            normalized = re.sub(pattern, replacement, normalized)
        
        return normalized.strip()
    
    def _extract_searchable_terms(self, title: str) -> List[str]:
        """
        タイトルから検索可能な用語を抽出
        
        Args:
            title: タイトル
            
        Returns:
            検索用語のリスト
        """
        terms = []
        
        # 正規化タイトル
        normalized = self._normalize_title(title)
        terms.append(normalized)
        
        # 原タイトルからの主要部分抽出
        main_title_patterns = [
            r'『([^』]+)』',  # 『曲名』
            r'「([^」]+)」',  # 「曲名」
            r'【([^】]+)】',  # 【曲名】
            r'^([^【\[（\(]+)',  # 最初の装飾より前
        ]
        
        for pattern in main_title_patterns:
            matches = re.findall(pattern, title)
            for match in matches:
                if match.strip():
                    terms.append(match.strip())
        
        # カタカナ・英数字のキーワード抽出
        keyword_patterns = [
            r'[ァ-ヶー]+',  # カタカナ
            r'[A-Za-z][A-Za-z0-9]*',  # 英数字
        ]
        
        for pattern in keyword_patterns:
            matches = re.findall(pattern, title)
            for match in matches:
                if len(match) > 1:  # 1文字は除外
                    terms.append(match)
        
        # 重複除去
        return list(set([term for term in terms if term]))
    
    def _extract_main_title(self, title: str) -> str:
        """
        YouTubeタイトルから主要な楽曲名・作品名を抽出
        
        Args:
            title: 元のタイトル
            
        Returns:
            抽出された主要タイトル
        """
        # 段階的に抽出を試行
        
        # 1. 『』内の抽出（最優先）
        main_title_match = re.search(r'『([^』]+)』', title)
        if main_title_match:
            return main_title_match.group(1).strip()
        
        # 2. 「」内の抽出
        main_title_match = re.search(r'「([^」]+)」', title)
        if main_title_match:
            return main_title_match.group(1).strip()
        
        # 3. 【】内の楽曲名抽出（装飾語を除く）
        bracket_match = re.search(r'【([^】]+)】', title)
        if bracket_match:
            bracket_content = bracket_match.group(1)
            # 装飾語を除去
            if not any(word in bracket_content for word in ['歌ってみた', 'オリジナル', 'MV', 'カバー', 'Cover']):
                return bracket_content.strip()
        
        # 4. Music Video、MV等の前の部分を抽出
        mv_patterns = [
            r'^([^【\[（\(]+?)(?:\s*(?:Music Video|MV|ミュージックビデオ))',
            r'^([^【\[（\(]+?)(?:\s*[\-\–\—]\s*)',
            r'^([^【\[（\(]+?)(?:\s*/\s*)',
        ]
        
        for pattern in mv_patterns:
            match = re.search(pattern, title, re.IGNORECASE)
            if match:
                candidate = match.group(1).strip()
                # TRiNITY記号の除去
                candidate = re.sub(r'▽▲([^▲▽]*)▲▽', r'\1', candidate)
                if len(candidate) > 1 and not any(word in candidate.lower() for word in ['official', 'オフィシャル']):
                    return candidate
        
        # 5. 英数字・カタカナの楽曲名らしい部分を抽出
        song_name_patterns = [
            r'([A-Za-z][A-Za-z\s\!\?\.\,]+)',  # 英語楽曲名
            r'([ァ-ヶー]{2,})',  # カタカナ楽曲名
        ]
        
        for pattern in song_name_patterns:
            matches = re.findall(pattern, title)
            for match in matches:
                match = match.strip()
                if len(match) > 2 and not any(word in match.lower() for word in [
                    'music', 'video', 'cover', 'feat', 'official', 'mv'
                ]):
                    return match
        
        # 6. フォールバック: 最初の単語（装飾を除く）
        clean_title = re.sub(r'^【[^】]*】\s*', '', title)  # 先頭の【】を除去
        clean_title = re.sub(r'^▽▲([^▲▽]*)▲▽\s*', r'\1 ', clean_title)  # TRiNITY記号除去
        
        # 最初の意味のある単語を抽出
        first_word_match = re.search(r'([^\s\[\]【】（）\(\)]+)', clean_title)
        if first_word_match:
            return first_word_match.group(1).strip()
        
        # 7. 最終フォールバック: 元タイトルの正規化版
        return self._normalize_title(title)[:20]  # 最大20文字

    def search_videos(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        動画を検索
        
        Args:
            query: 検索クエリ
            limit: 最大結果数
            
        Returns:
            マッチした動画のリスト
        """
        if not query.strip():
            return []
        
        query_lower = query.lower()
        videos = self.knowledge_db.get("videos", {})
        results = []
        
        for video_id, video_data in videos.items():
            metadata = video_data.get("metadata", {})
            
            # 基本情報
            title = metadata.get("title", "")
            channel = metadata.get("channel_title", "").lower()
            description = metadata.get("description", "").lower()
            
            # タイトルの検索可能用語を取得
            searchable_terms = self._extract_searchable_terms(title)
            searchable_terms_lower = [term.lower() for term in searchable_terms]
            
            # クリエイター情報での検索（分析結果から）
            creators = []
            if "creative_insight" in video_data:
                insight = video_data["creative_insight"]
                if "creators" in insight:
                    creators = [c.get("name", "").lower() for c in insight["creators"]]
            
            # マッチング判定
            score = 0
            
            # 正規化タイトルでの完全一致（最高スコア）
            for searchable_term in searchable_terms_lower:
                if query_lower == searchable_term:
                    score += 20
                elif query_lower in searchable_term:
                    score += 15
                elif searchable_term in query_lower:
                    score += 12
            
            # 元タイトルでの部分一致
            if query_lower in title.lower():
                score += 10
            
            # チャンネル名での一致
            if query_lower in channel:
                score += 8
            
            # クリエイター名での一致
            if any(query_lower in creator for creator in creators):
                score += 9
            
            # 説明文での一致（低スコア）
            if query_lower in description:
                score += 3
            
            # 部分マッチも考慮
            for word in query_lower.split():
                if len(word) > 1:  # 1文字は除外
                    # 検索可能用語での部分マッチ
                    for searchable_term in searchable_terms_lower:
                        if word in searchable_term:
                            score += 6
                    
                    # その他の部分マッチ
                    if word in title.lower():
                        score += 5
                    if word in channel:
                        score += 4
                    if any(word in creator for creator in creators):
                        score += 4
            
            if score > 0:
                results.append({
                    "video_id": video_id,
                    "data": video_data,
                    "score": score,
                    "matched_terms": searchable_terms  # デバッグ用
                })
        
        # スコア順でソート
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:limit]
    
    def get_video_context(self, video_id: str) -> Optional[Dict[str, Any]]:
        """
        特定の動画の詳細コンテキストを取得
        
        Args:
            video_id: YouTube動画ID
            
        Returns:
            動画の詳細情報
        """
        videos = self.knowledge_db.get("videos", {})
        if video_id not in videos:
            return None
        
        video_data = videos[video_id]
        metadata = video_data.get("metadata", {})
        
        # 基本情報
        context = {
            "video_id": video_id,
            "title": metadata.get("title", ""),
            "channel": metadata.get("channel_title", ""),
            "published_at": metadata.get("published_at", ""),
            "view_count": metadata.get("view_count", 0),
            "duration": metadata.get("duration", ""),
            "analysis_status": video_data.get("analysis_status", "unknown")
        }
        
        # 分析結果があれば追加
        if "creative_insight" in video_data:
            insight = video_data["creative_insight"]
            context["creators"] = insight.get("creators", [])
            context["music_analysis"] = insight.get("music_analysis", {})
            context["lyrics"] = insight.get("lyrics", {})
        
        return context
    
    def filter_by_creator(self, creator_name: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        クリエイター名で動画をフィルタリング
        
        Args:
            creator_name: クリエイター名
            limit: 最大結果数
            
        Returns:
            マッチした動画のリスト
        """
        creator_lower = creator_name.lower()
        videos = self.knowledge_db.get("videos", {})
        results = []
        
        for video_id, video_data in videos.items():
            # チャンネル名でのマッチング
            metadata = video_data.get("metadata", {})
            channel = metadata.get("channel_title", "").lower()
            
            if creator_lower in channel:
                results.append({
                    "video_id": video_id,
                    "data": video_data,
                    "match_type": "channel"
                })
                continue
            
            # 分析結果のクリエイター情報でのマッチング
            if "creative_insight" in video_data:
                insight = video_data["creative_insight"]
                creators = insight.get("creators", [])
                for creator in creators:
                    creator_name_db = creator.get("name", "").lower()
                    if creator_lower in creator_name_db:
                        results.append({
                            "video_id": video_id,
                            "data": video_data,
                            "match_type": "creator_analysis"
                        })
                        break
        
        return results[:limit]
    
    def get_analysis_summary(self, video_id: str) -> Optional[str]:
        """
        動画の分析結果要約を生成
        
        Args:
            video_id: YouTube動画ID
            
        Returns:
            分析結果の要約テキスト
        """
        context = self.get_video_context(video_id)
        if not context:
            return None
        
        summary = []
        
        # 基本情報
        summary.append(f"『{context['title']}』")
        
        # クリエイター情報
        if context.get("creators"):
            creator_names = [c.get("name", "") for c in context["creators"] if c.get("name")]
            if creator_names:
                summary.append(f"クリエイター: {', '.join(creator_names)}")
        
        # 楽曲分析結果
        if context.get("music_analysis"):
            music = context["music_analysis"]
            if music.get("genre"):
                summary.append(f"ジャンル: {music['genre']}")
            if music.get("mood"):
                summary.append(f"ムード: {music['mood']}")
        
        # 歌詞情報
        if context.get("lyrics"):
            lyrics = context["lyrics"]
            if lyrics.get("theme"):
                summary.append(f"テーマ: {lyrics['theme']}")
        
        return " / ".join(summary) if summary else None
    
    def add_to_cache(self, video_id: str, conversation_context: str = ""):
        """
        話題になった動画をキャッシュに追加
        
        Args:
            video_id: 動画ID
            conversation_context: 会話のコンテキスト
        """
        self.video_cache[video_id] = {
            "cached_at": datetime.now().isoformat(),
            "context": conversation_context,
            "access_count": self.video_cache.get(video_id, {}).get("access_count", 0) + 1
        }
    
    def get_cached_videos(self) -> List[str]:
        """
        キャッシュされた動画IDのリストを取得
        
        Returns:
            動画IDのリスト（アクセス頻度順）
        """
        return sorted(
            self.video_cache.keys(),
            key=lambda vid: self.video_cache[vid].get("access_count", 0),
            reverse=True
        )
    
    def get_random_recommendation(self, context_hint: str = "", limit: int = 1) -> List[Dict[str, Any]]:
        """
        ランダム + 重み付けで動画を推薦
        
        Args:
            context_hint: コンテキストヒント（「音楽」「面白い」等）
            limit: 推薦する動画数
            
        Returns:
            推薦動画のリスト
        """
        import random
        
        videos = self.knowledge_db.get("videos", {})
        if not videos:
            return []
        
        candidates = []
        
        for video_id, video_data in videos.items():
            metadata = video_data.get("metadata", {})
            
            # 基本品質フィルタ
            view_count = metadata.get("view_count", 0)
            like_count = metadata.get("like_count", 0)
            
            # 最低品質基準
            if view_count < 5000:  # 再生回数5000未満は除外
                continue
            
            # 重み計算
            weight = 1.0
            
            # 再生回数による重み付け（対数スケール）
            if view_count > 0:
                import math
                weight *= math.log10(view_count + 1) / 6.0  # 100万再生で重み1.0
            
            # いいね数による重み付け
            if like_count > 0:
                weight *= (like_count / 1000.0 + 1.0)  # 1000いいねで2倍
            
            # 分析済み動画はボーナス
            if video_data.get("analysis_status") == "completed":
                weight *= 1.5
            
            # コンテキストヒントによる重み調整
            if context_hint:
                title = metadata.get("title", "").lower()
                description = metadata.get("description", "").lower()
                
                # 音楽関連
                if any(word in context_hint for word in ["音楽", "歌", "曲", "MV"]):
                    if any(word in title for word in ["歌", "music", "mv", "cover"]):
                        weight *= 2.0
                
                # エンターテイメント関連
                if any(word in context_hint for word in ["面白い", "エンタメ", "楽しい"]):
                    if any(word in title for word in ["面白", "楽しい", "ゲーム", "バラエティ"]):
                        weight *= 1.8
            
            # 重みの正規化（最大10.0）
            weight = min(weight, 10.0)
            
            candidates.append({
                "video_id": video_id,
                "data": video_data,
                "weight": weight,
                "score": int(weight * 10)  # 表示用スコア
            })
        
        if not candidates:
            return []
        
        # 重み付きランダム選択
        weights = [c["weight"] for c in candidates]
        selected = random.choices(candidates, weights=weights, k=min(limit, len(candidates)))
        
        return selected
    
    def reload_database(self):
        """データベースを再読み込み"""
        print("[YouTube知識] 🔄 データベース再読み込み開始")
        self._load_knowledge_db()
        print("[YouTube知識] ✅ データベース再読み込み完了")


if __name__ == "__main__":
    # テスト実行
    manager = YouTubeKnowledgeManager()
    
    # 検索テスト
    results = manager.search_videos("TRiNITY")
    print(f"\n🔍 'TRiNITY' 検索結果: {len(results)}件")
    
    for result in results[:3]:
        video_data = result["data"]
        metadata = video_data.get("metadata", {})
        print(f"- {metadata.get('title', 'タイトル不明')} (スコア: {result['score']})")
    
    # 分析要約テスト
    if results:
        first_video_id = results[0]["video_id"]
        summary = manager.get_analysis_summary(first_video_id)
        print(f"\n📊 分析要約: {summary}")
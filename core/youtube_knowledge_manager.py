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
import requests
from core.image_analyzer import ImageAnalyzer


class YouTubeKnowledgeManager:
    """YouTube動画知識を管理するクラス"""
    
    def __init__(self):
        """初期化"""
        # Windows環境とWSL2環境両方に対応
        if os.name == 'nt':  # Windows
            self.knowledge_db_path = Path("D:/setsuna_bot/youtube_knowledge_system/data/unified_knowledge_db.json")
            self.credentials_path = Path("D:/setsuna_bot/config/youtube_credentials.json")
            self.token_path = Path("D:/setsuna_bot/config/youtube_token.json")
        else:  # Linux/WSL2
            self.knowledge_db_path = Path("/mnt/d/setsuna_bot/youtube_knowledge_system/data/unified_knowledge_db.json")
            self.credentials_path = Path("/mnt/d/setsuna_bot/config/youtube_credentials.json")
            self.token_path = Path("/mnt/d/setsuna_bot/config/youtube_token.json")
        
        self.knowledge_db = {}
        self.video_cache = {}  # 話題になった動画のキャッシュ
        
        # Phase 2: YouTube API検索用の設定（OAuth2対応）
        self.youtube_api_key = os.getenv('YOUTUBE_API_KEY')  # 下位互換性のため保持
        self.youtube_service = None  # OAuth2サービスオブジェクト
        self.last_external_search_results = []  # 外部検索結果保持
        
        self._load_knowledge_db()
        self._initialize_youtube_api()
        
        # Phase 2: ImageAnalyzer初期化
        try:
            self.image_analyzer = ImageAnalyzer()
            print("[YouTube知識] ✅ 画像分析システム統合完了")
        except Exception as e:
            print(f"[YouTube知識] ⚠️ 画像分析システム初期化失敗: {e}")
            self.image_analyzer = None
        
        print("[YouTube知識] ✅ YouTube知識管理システム初期化完了")
    
    def _initialize_youtube_api(self):
        """YouTube API (OAuth2) を初期化"""
        try:
            import json
            import googleapiclient.discovery
            from google.oauth2.credentials import Credentials
            
            # OAuth2トークンファイルの確認
            if not self.token_path.exists():
                print("[YouTube知識] ⚠️ OAuth2トークンファイルが見つかりません")
                print(f"[YouTube知識] 📁 期待されるパス: {self.token_path}")
                return
            
            # OAuth2認証情報の読み込み
            with open(self.token_path, 'r', encoding='utf-8') as f:
                token_data = json.load(f)
            
            # 認証情報からCredentialsオブジェクトを作成
            creds = Credentials.from_authorized_user_info(token_data)
            
            # YouTube APIサービスオブジェクトを作成
            self.youtube_service = googleapiclient.discovery.build(
                'youtube', 'v3', credentials=creds
            )
            
            print("[YouTube知識] ✅ OAuth2認証によるYouTube API初期化完了")
            
        except Exception as e:
            print(f"[YouTube知識] ❌ YouTube API初期化エラー: {e}")
            print("[YouTube知識] 💡 OAuth2認証が必要な場合があります")
    
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
            
            # カスタム情報での検索（手動編集データ）
            custom_info = video_data.get("custom_info", {})
            manual_title = custom_info.get("manual_title", "").lower()
            manual_artist = custom_info.get("manual_artist", "").lower()
            japanese_pronunciations = [r.lower() for r in custom_info.get("japanese_pronunciations", [])]
            artist_pronunciations = [r.lower() for r in custom_info.get("artist_pronunciations", [])]
            search_keywords = [k.lower() for k in custom_info.get("search_keywords", [])]
            
            # マッチング判定
            score = 0
            
            # カスタム情報での高精度マッチング（最優先）
            if manual_title and query_lower == manual_title:
                score += 50  # 手動設定楽曲名の完全一致は最高スコア
            elif manual_title and query_lower in manual_title:
                score += 30  # 部分一致
            
            if manual_artist and query_lower == manual_artist:
                score += 40  # 手動設定アーティスト名の完全一致
            elif manual_artist and query_lower in manual_artist:
                score += 25  # 部分一致
            
            # 楽曲の日本語読みでの一致（音声認識対応）
            for pronunciation in japanese_pronunciations:
                if query_lower == pronunciation:
                    score += 50  # 日本語読み完全一致（音声認識で最重要）
                elif query_lower in pronunciation:
                    score += 25  # 部分一致
            
            # アーティストの日本語読みでの一致
            for pronunciation in artist_pronunciations:
                if query_lower == pronunciation:
                    score += 45  # アーティスト日本語読み完全一致
                elif query_lower in pronunciation:
                    score += 22  # 部分一致
            
            # 検索キーワードでの一致
            for keyword in search_keywords:
                if query_lower == keyword:
                    score += 35  # キーワード完全一致
                elif query_lower in keyword:
                    score += 15  # 部分一致
            
            # 正規化タイトルでの完全一致（高スコア）
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
    
    def search_youtube_external(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        YouTube APIを使って外部検索を実行
        
        Args:
            query: 検索クエリ
            limit: 取得件数上限
            
        Returns:
            外部検索結果のリスト
        """
        if not self.youtube_api_key:
            print("[YouTube知識] ⚠️ YouTube API Keyが設定されていません")
            return []
        
        try:
            # YouTube Data APIを使用した検索
            api_url = "https://www.googleapis.com/youtube/v3/search"
            params = {
                'part': 'snippet',
                'q': query,
                'type': 'video',
                'maxResults': limit,
                'key': self.youtube_api_key,
                'order': 'relevance',
                'regionCode': 'JP',  # 日本地域
                'relevanceLanguage': 'ja'  # 日本語優先
            }
            
            print(f"[YouTube知識] 🔍 外部検索実行: '{query}'")
            response = requests.get(api_url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            external_results = []
            
            for item in data.get('items', []):
                video_id = item['id']['videoId']
                snippet = item['snippet']
                
                # 既存DBにないかチェック
                if video_id not in self.knowledge_db.get('videos', {}):
                    external_video = {
                        'video_id': video_id,
                        'title': snippet.get('title', ''),
                        'channel': snippet.get('channelTitle', ''),
                        'description': snippet.get('description', '')[:200],  # 200文字まで
                        'published_at': snippet.get('publishedAt', ''),
                        'thumbnail_url': snippet.get('thumbnails', {}).get('medium', {}).get('url', ''),
                        'source': 'youtube_api',
                        'search_query': query
                    }
                    external_results.append(external_video)
                    print(f"[YouTube知識] 📹 外部動画発見: {external_video['title'][:50]}...")
                else:
                    print(f"[YouTube知識] 🔍 既存DB内: {snippet.get('title', '')[:50]}...")
            
            # 外部検索結果を保存
            self.last_external_search_results = external_results
            print(f"[YouTube知識] ✅ 外部検索完了: {len(external_results)}件の新規動画")
            
            return external_results
            
        except Exception as e:
            print(f"[YouTube知識] ❌ 外部検索エラー: {e}")
            return []
    
    def get_last_external_results(self) -> List[Dict[str, Any]]:
        """
        最後の外部検索結果を取得
        
        Returns:
            最後の外部検索結果
        """
        return self.last_external_search_results
    
    def reload_database(self):
        """データベースを再読み込み"""
        print("[YouTube知識] 🔄 データベース再読み込み開始")
        self._load_knowledge_db()
        print("[YouTube知識] ✅ データベース再読み込み完了")
    
    def add_manual_video(self, video_id: str) -> Dict[str, Any]:
        """
        手動で動画を追加（YouTube OAuth2 API経由）
        
        Args:
            video_id: YouTube動画ID
            
        Returns:
            追加結果辞書 {'success': bool, 'message': str, 'video_info': dict}
        """
        try:
            # YouTube API OAuth2サービス確認
            if not self.youtube_service:
                return {
                    'success': False,
                    'message': 'YouTube API (OAuth2) が初期化されていません。認証設定を確認してください。',
                    'video_info': {}
                }
            
            # 既に存在するかチェック
            if video_id in self.knowledge_db.get("videos", {}):
                video_info = self.knowledge_db["videos"][video_id].get("metadata", {})
                return {
                    'success': True,
                    'message': '動画は既に学習済みです',
                    'video_info': video_info
                }
            
            # YouTube OAuth2 API経由で動画情報取得
            video_info = self._fetch_video_info_from_oauth_api(video_id)
            if not video_info:
                return {
                    'success': False,
                    'message': '動画情報の取得に失敗しました（動画が存在しないか、非公開の可能性があります）',
                    'video_info': {}
                }
            
            # データベースに追加
            self._add_video_to_db(video_id, video_info)
            
            # データベース保存
            self._save_knowledge_db()
            
            return {
                'success': True,
                'message': '動画の学習が完了しました',
                'video_info': video_info
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'予期しないエラー: {str(e)}',
                'video_info': {}
            }
    
    def _fetch_video_info_from_oauth_api(self, video_id: str) -> Optional[Dict[str, Any]]:
        """YouTube OAuth2 APIから動画情報を取得"""
        try:
            if not self.youtube_service:
                print("[YouTube知識] ❌ YouTube APIサービスが初期化されていません")
                return None
            
            # YouTube Data API v3をOAuth2で呼び出し
            request = self.youtube_service.videos().list(
                part='snippet,statistics,contentDetails',
                id=video_id
            )
            
            response = request.execute()
            items = response.get('items', [])
            
            if not items:
                print(f"[YouTube知識] ⚠️ 動画が見つかりません: {video_id}")
                return None
            
            item = items[0]
            snippet = item.get('snippet', {})
            statistics = item.get('statistics', {})
            content_details = item.get('contentDetails', {})
            
            # 動画情報を構造化
            video_info = {
                'title': snippet.get('title', ''),
                'description': snippet.get('description', ''),
                'channel_title': snippet.get('channelTitle', ''),
                'published_at': snippet.get('publishedAt', ''),
                'duration': content_details.get('duration', ''),
                'view_count': int(statistics.get('viewCount', 0)),
                'like_count': int(statistics.get('likeCount', 0)),
                'comment_count': int(statistics.get('commentCount', 0)),
                'tags': snippet.get('tags', []),
                'category_id': snippet.get('categoryId', ''),
                'channel_id': snippet.get('channelId', '')
            }
            
            print(f"[YouTube知識] ✅ 動画情報取得成功: {video_info['title']}")
            return video_info
            
        except Exception as e:
            print(f"[YouTube知識] ❌ OAuth2 API取得エラー: {e}")
            return None
    
    def _fetch_video_info_from_api(self, video_id: str) -> Optional[Dict[str, Any]]:
        """YouTube APIから動画情報を取得（下位互換性のため残存）"""
        # OAuth2版を優先
        if self.youtube_service:
            return self._fetch_video_info_from_oauth_api(video_id)
        
        # 下位互換性のためのAPIキー版
        try:
            if not self.youtube_api_key:
                print("[YouTube知識] ❌ APIキーもOAuth2も利用できません")
                return None
                
            # YouTube Data API v3 エンドポイント
            url = "https://www.googleapis.com/youtube/v3/videos"
            params = {
                'part': 'snippet,statistics,contentDetails',
                'id': video_id,
                'key': self.youtube_api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            items = data.get('items', [])
            
            if not items:
                return None
            
            item = items[0]
            snippet = item.get('snippet', {})
            statistics = item.get('statistics', {})
            content_details = item.get('contentDetails', {})
            
            # 動画情報を構造化
            video_info = {
                'title': snippet.get('title', ''),
                'description': snippet.get('description', ''),
                'channel_title': snippet.get('channelTitle', ''),
                'published_at': snippet.get('publishedAt', ''),
                'duration': content_details.get('duration', ''),
                'view_count': int(statistics.get('viewCount', 0)),
                'like_count': int(statistics.get('likeCount', 0)),
                'comment_count': int(statistics.get('commentCount', 0)),
                'tags': snippet.get('tags', []),
                'category_id': snippet.get('categoryId', ''),
                'channel_id': snippet.get('channelId', '')
            }
            
            return video_info
            
        except Exception as e:
            print(f"[YouTube知識] ❌ API取得エラー: {e}")
            return None
    
    def _add_video_to_db(self, video_id: str, video_info: Dict[str, Any]):
        """動画をデータベースに追加"""
        if "videos" not in self.knowledge_db:
            self.knowledge_db["videos"] = {}
        
        # 手動追加カテゴリに分類
        video_data = {
            "video_id": video_id,
            "source": "youtube",
            "metadata": video_info,
            "playlists": ["MANUAL_ADDED"],  # 手動追加プレイリスト
            "playlist_positions": {"MANUAL_ADDED": 0},
            "analysis_status": "completed",
            "added_at": datetime.now().isoformat(),
            "added_method": "manual_gui"
        }
        
        self.knowledge_db["videos"][video_id] = video_data
    
    def add_video_image(self, video_id: str, image_metadata: Dict[str, Any]) -> bool:
        """
        動画に画像を関連付けて保存
        
        Args:
            video_id: YouTube動画ID
            image_metadata: 画像のメタデータ辞書
            
        Returns:
            保存成功フラグ
        """
        try:
            if "videos" not in self.knowledge_db:
                print("[YouTube知識] ❌ 動画データベースが見つかりません")
                return False
            
            if video_id not in self.knowledge_db["videos"]:
                print(f"[YouTube知識] ❌ 動画ID {video_id} が見つかりません")
                return False
            
            # 動画データに画像配列を初期化（存在しない場合）
            if "images" not in self.knowledge_db["videos"][video_id]:
                self.knowledge_db["videos"][video_id]["images"] = []
            
            # 画像メタデータを追加
            self.knowledge_db["videos"][video_id]["images"].append(image_metadata)
            
            # データベースを保存
            self._save_knowledge_db()
            
            print(f"[YouTube知識] ✅ 画像追加完了: {image_metadata.get('image_id', 'unknown')}")
            return True
            
        except Exception as e:
            print(f"[YouTube知識] ❌ 画像追加エラー: {e}")
            return False
    
    def get_video_images(self, video_id: str) -> List[Dict[str, Any]]:
        """
        指定動画の画像一覧を取得
        
        Args:
            video_id: YouTube動画ID
            
        Returns:
            画像メタデータのリスト
        """
        try:
            if ("videos" not in self.knowledge_db or 
                video_id not in self.knowledge_db["videos"] or
                "images" not in self.knowledge_db["videos"][video_id]):
                return []
            
            return self.knowledge_db["videos"][video_id]["images"]
            
        except Exception as e:
            print(f"[YouTube知識] ❌ 画像一覧取得エラー: {e}")
            return []
    
    def remove_video_image(self, video_id: str, image_id: str) -> bool:
        """
        動画から指定画像を削除
        
        Args:
            video_id: YouTube動画ID
            image_id: 削除する画像ID
            
        Returns:
            削除成功フラグ
        """
        try:
            images = self.get_video_images(video_id)
            
            # 指定画像IDを検索・削除
            for i, image_data in enumerate(images):
                if image_data.get("image_id") == image_id:
                    del self.knowledge_db["videos"][video_id]["images"][i]
                    self._save_knowledge_db()
                    print(f"[YouTube知識] ✅ 画像削除完了: {image_id}")
                    return True
            
            print(f"[YouTube知識] ⚠️ 画像が見つかりません: {image_id}")
            return False
            
        except Exception as e:
            print(f"[YouTube知識] ❌ 画像削除エラー: {e}")
            return False
    
    def analyze_video_image(self, video_id: str, image_id: str, force_reanalysis: bool = False) -> bool:
        """
        特定の画像を分析
        
        Args:
            video_id: YouTube動画ID
            image_id: 分析する画像ID
            force_reanalysis: 既存の分析結果を無視して再分析するか
            
        Returns:
            分析成功フラグ
        """
        try:
            if not self.image_analyzer:
                print("[YouTube知識] ❌ 画像分析システムが利用できません")
                return False
            
            # 動画・画像情報取得
            if ("videos" not in self.knowledge_db or 
                video_id not in self.knowledge_db["videos"] or
                "images" not in self.knowledge_db["videos"][video_id]):
                print(f"[YouTube知識] ❌ 動画または画像が見つかりません: {video_id}/{image_id}")
                return False
            
            # 対象画像を検索
            target_image = None
            image_index = None
            for i, image_data in enumerate(self.knowledge_db["videos"][video_id]["images"]):
                if image_data.get("image_id") == image_id:
                    target_image = image_data
                    image_index = i
                    break
            
            if not target_image:
                print(f"[YouTube知識] ❌ 画像が見つかりません: {image_id}")
                return False
            
            # 既存の分析結果チェック
            if not force_reanalysis and target_image.get("analysis_status") == "completed":
                print(f"[YouTube知識] ℹ️ 画像は既に分析済み: {image_id}")
                return True
            
            # 分析ステータス更新
            self.knowledge_db["videos"][video_id]["images"][image_index]["analysis_status"] = "processing"
            
            print(f"[YouTube知識] 🔍 画像分析開始: {image_id}")
            
            # 動画情報を取得
            video_info = self.knowledge_db["videos"][video_id]["metadata"]
            
            # 画像分析実行
            analysis_result = self.image_analyzer.analyze_with_video_context(
                image_path=target_image["file_path"],
                video_info=video_info
            )
            
            # 分析結果をデータベースに保存
            self.knowledge_db["videos"][video_id]["images"][image_index].update({
                "analysis_status": "completed",
                "analysis_result": analysis_result,
                "analysis_timestamp": datetime.now().isoformat()
            })
            
            # データベース保存
            self._save_knowledge_db()
            
            print(f"[YouTube知識] ✅ 画像分析完了: {image_id}")
            return True
            
        except Exception as e:
            print(f"[YouTube知識] ❌ 画像分析エラー: {e}")
            
            # エラー時のステータス更新
            if image_index is not None:
                self.knowledge_db["videos"][video_id]["images"][image_index].update({
                    "analysis_status": "failed",
                    "analysis_error": str(e),
                    "analysis_timestamp": datetime.now().isoformat()
                })
                self._save_knowledge_db()
            
            return False
    
    def analyze_all_video_images(self, video_id: str, force_reanalysis: bool = False) -> Dict[str, Any]:
        """
        動画のすべての画像を分析
        
        Args:
            video_id: YouTube動画ID
            force_reanalysis: 既存の分析結果を無視して再分析するか
            
        Returns:
            分析結果サマリー
        """
        try:
            images = self.get_video_images(video_id)
            
            if not images:
                return {"success": False, "message": "分析対象の画像がありません"}
            
            analysis_summary = {
                "total_images": len(images),
                "analyzed_count": 0,
                "failed_count": 0,
                "skipped_count": 0,
                "results": []
            }
            
            for image_data in images:
                image_id = image_data.get("image_id")
                
                # 既存分析チェック
                if not force_reanalysis and image_data.get("analysis_status") == "completed":
                    analysis_summary["skipped_count"] += 1
                    continue
                
                # 分析実行
                success = self.analyze_video_image(video_id, image_id, force_reanalysis)
                
                if success:
                    analysis_summary["analyzed_count"] += 1
                else:
                    analysis_summary["failed_count"] += 1
                
                analysis_summary["results"].append({
                    "image_id": image_id,
                    "success": success
                })
            
            print(f"[YouTube知識] 📊 一括分析完了: {analysis_summary['analyzed_count']}/{analysis_summary['total_images']} 成功")
            
            return {
                "success": True,
                "summary": analysis_summary
            }
            
        except Exception as e:
            print(f"[YouTube知識] ❌ 一括画像分析エラー: {e}")
            return {"success": False, "message": str(e)}
    
    def get_image_analysis_result(self, video_id: str, image_id: str) -> Optional[Dict[str, Any]]:
        """
        画像の分析結果を取得
        
        Args:
            video_id: YouTube動画ID
            image_id: 画像ID
            
        Returns:
            分析結果、未分析の場合は None
        """
        try:
            images = self.get_video_images(video_id)
            
            for image_data in images:
                if image_data.get("image_id") == image_id:
                    if image_data.get("analysis_status") == "completed":
                        return image_data.get("analysis_result")
                    else:
                        return None
            
            return None
            
        except Exception as e:
            print(f"[YouTube知識] ❌ 分析結果取得エラー: {e}")
            return None
    
    def get_analysis_stats(self) -> Dict[str, Any]:
        """画像分析の統計情報を取得"""
        try:
            if not self.image_analyzer:
                return {"error": "画像分析システムが利用できません"}
            
            # ImageAnalyzerの統計
            analyzer_stats = self.image_analyzer.get_analysis_stats()
            
            # データベース内の分析済み画像統計
            total_images = 0
            analyzed_images = 0
            pending_images = 0
            failed_images = 0
            
            for video_id, video_data in self.knowledge_db.get("videos", {}).items():
                if "images" in video_data:
                    for image_data in video_data["images"]:
                        total_images += 1
                        status = image_data.get("analysis_status", "pending")
                        
                        if status == "completed":
                            analyzed_images += 1
                        elif status == "failed":
                            failed_images += 1
                        else:
                            pending_images += 1
            
            return {
                "database_stats": {
                    "total_images": total_images,
                    "analyzed_images": analyzed_images,
                    "pending_images": pending_images,
                    "failed_images": failed_images
                },
                "analyzer_stats": analyzer_stats,
                "analysis_rate": (analyzed_images / total_images * 100) if total_images > 0 else 0
            }
            
        except Exception as e:
            print(f"[YouTube知識] ❌ 統計取得エラー: {e}")
            return {"error": str(e)}
    
    def _save_knowledge_db(self):
        """知識データベースを保存"""
        try:
            # バックアップを作成
            if self.knowledge_db_path.exists():
                backup_path = self.knowledge_db_path.with_suffix('.bak')
                # 既存のバックアップファイルを削除（Windows対応）
                if backup_path.exists():
                    backup_path.unlink()
                self.knowledge_db_path.rename(backup_path)
            
            # 新しいデータを保存
            with open(self.knowledge_db_path, 'w', encoding='utf-8') as f:
                json.dump(self.knowledge_db, f, ensure_ascii=False, indent=2)
            
            print("[YouTube知識] ✅ データベース保存完了")
            
        except Exception as e:
            print(f"[YouTube知識] ❌ データベース保存エラー: {e}")
            raise
    
    def get_manual_videos(self) -> List[Dict[str, Any]]:
        """手動追加された動画一覧を取得"""
        manual_videos = []
        
        videos = self.knowledge_db.get("videos", {})
        for video_id, video_data in videos.items():
            # 手動追加プレイリストに含まれる動画を抽出
            playlists = video_data.get("playlists", [])
            if "MANUAL_ADDED" in playlists:
                metadata = video_data.get("metadata", {})
                manual_videos.append({
                    "video_id": video_id,
                    "title": metadata.get("title", ""),
                    "channel_title": metadata.get("channel_title", ""),
                    "added_at": video_data.get("added_at", ""),
                    "view_count": metadata.get("view_count", 0)
                })
        
        # 追加日時でソート（新しい順）
        manual_videos.sort(key=lambda x: x["added_at"], reverse=True)
        return manual_videos


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
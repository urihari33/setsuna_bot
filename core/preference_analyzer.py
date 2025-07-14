#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
データベース分析による好み推測システム
YouTubeデータベースと会話履歴からせつなの好みを分析・推測する
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import re
from collections import defaultdict, Counter

class PreferenceAnalyzer:
    def __init__(self):
        """好み推測システムの初期化"""
        # データベースパスの設定
        self.youtube_db_path = Path("D:/setsuna_bot/youtube_knowledge_system/data/unified_knowledge_db.json")
        self.video_history_path = Path("D:/setsuna_bot/data/video_conversation_history.json")
        self.multi_turn_path = Path("D:/setsuna_bot/data/multi_turn_conversations.json")
        
        # 分析結果のキャッシュ
        self.preference_cache = {}
        self.last_analysis_time = None
        
        # 好みパターンの重み設定
        self.preference_weights = {
            "positive_reaction": 2.0,
            "high_familiarity": 1.5,
            "multiple_conversations": 1.3,
            "analysis_quality": 1.2,
            "recent_activity": 1.1
        }
        
        print("[好み分析] ✅ 好み推測システム初期化完了")
    
    def analyze_music_preferences(self) -> Dict[str, Any]:
        """
        YouTubeデータベースから音楽的好みを分析
        
        Returns:
            Dict: 音楽的好みの分析結果
        """
        try:
            # YouTubeデータベースの読み込み
            if not self.youtube_db_path.exists():
                print(f"[好み分析] ⚠️ YouTubeデータベースが見つかりません: {self.youtube_db_path}")
                return {}
            
            with open(self.youtube_db_path, 'r', encoding='utf-8') as f:
                youtube_data = json.load(f)
            
            videos = youtube_data.get("videos", {})
            if not videos:
                print("[好み分析] ⚠️ 動画データが見つかりません")
                return {}
            
            # 楽曲分析の実行
            genre_analysis = self._analyze_genres(videos)
            artist_analysis = self._analyze_artists(videos)
            theme_analysis = self._analyze_themes(videos)
            quality_analysis = self._analyze_quality_indicators(videos)
            
            music_preferences = {
                "preferred_genres": genre_analysis,
                "preferred_artists": artist_analysis,
                "preferred_themes": theme_analysis,
                "quality_indicators": quality_analysis,
                "analysis_timestamp": datetime.now().isoformat(),
                "total_videos_analyzed": len(videos)
            }
            
            print(f"[好み分析] ✅ 音楽的好み分析完了: {len(videos)}件の動画を分析")
            return music_preferences
            
        except Exception as e:
            print(f"[好み分析] ❌ 音楽的好み分析エラー: {e}")
            return {}
    
    def analyze_reaction_patterns(self) -> Dict[str, Any]:
        """
        会話履歴から反応パターンを分析
        
        Returns:
            Dict: 反応パターンの分析結果
        """
        try:
            # 会話履歴の読み込み
            video_history = self._load_video_history()
            multi_turn_data = self._load_multi_turn_data()
            
            if not video_history:
                print("[好み分析] ⚠️ 会話履歴データが見つかりません")
                return {}
            
            # 反応パターンの分析
            positive_patterns = self._analyze_positive_reactions(video_history)
            negative_patterns = self._analyze_negative_reactions(video_history)
            familiarity_patterns = self._analyze_familiarity_patterns(video_history)
            conversation_patterns = self._analyze_conversation_patterns(multi_turn_data)
            
            reaction_patterns = {
                "positive_reaction_patterns": positive_patterns,
                "negative_reaction_patterns": negative_patterns,
                "familiarity_patterns": familiarity_patterns,
                "conversation_patterns": conversation_patterns,
                "analysis_timestamp": datetime.now().isoformat(),
                "total_conversations_analyzed": len(video_history)
            }
            
            print(f"[好み分析] ✅ 反応パターン分析完了: {len(video_history)}件の会話を分析")
            return reaction_patterns
            
        except Exception as e:
            print(f"[好み分析] ❌ 反応パターン分析エラー: {e}")
            return {}
    
    def generate_preference_profile(self) -> Dict[str, Any]:
        """
        総合的な好みプロファイルを生成
        
        Returns:
            Dict: 総合的な好みプロファイル
        """
        try:
            print("[好み分析] 🔍 総合的な好みプロファイル生成開始")
            
            # 各種分析の実行
            music_preferences = self.analyze_music_preferences()
            reaction_patterns = self.analyze_reaction_patterns()
            
            # 好みプロファイルの統合
            preference_profile = {
                "music_preferences": music_preferences,
                "reaction_patterns": reaction_patterns,
                "inferred_preferences": self._infer_preferences(music_preferences, reaction_patterns),
                "creative_suggestions": self._generate_creative_suggestion_patterns(),
                "personality_alignment": self._analyze_personality_alignment(),
                "profile_timestamp": datetime.now().isoformat()
            }
            
            # キャッシュに保存
            self.preference_cache = preference_profile
            self.last_analysis_time = datetime.now()
            
            print("[好み分析] ✅ 総合的な好みプロファイル生成完了")
            return preference_profile
            
        except Exception as e:
            print(f"[好み分析] ❌ 好みプロファイル生成エラー: {e}")
            return {}
    
    def _analyze_genres(self, videos: Dict) -> Dict[str, Any]:
        """ジャンル分析"""
        genre_count = defaultdict(int)
        genre_quality = defaultdict(list)
        
        for video_id, video_data in videos.items():
            # タグからジャンル推定
            tags = video_data.get("metadata", {}).get("tags", [])
            themes = video_data.get("creative_insight", {}).get("themes", [])
            
            for tag in tags:
                if any(keyword in tag.lower() for keyword in ["vtuber", "vtube", "バーチャル"]):
                    genre_count["VTuber"] += 1
                elif any(keyword in tag.lower() for keyword in ["anime", "アニメ"]):
                    genre_count["アニメ"] += 1
                elif any(keyword in tag.lower() for keyword in ["game", "ゲーム"]):
                    genre_count["ゲーム"] += 1
            
            for theme in themes:
                genre_count[theme] += 1
                # 品質指標も記録
                view_count = video_data.get("metadata", {}).get("view_count", 0)
                like_count = video_data.get("metadata", {}).get("like_count", 0)
                genre_quality[theme].append({"views": view_count, "likes": like_count})
        
        return {
            "genre_distribution": dict(genre_count),
            "genre_quality_metrics": dict(genre_quality),
            "top_genres": sorted(genre_count.items(), key=lambda x: x[1], reverse=True)[:5]
        }
    
    def _analyze_artists(self, videos: Dict) -> Dict[str, Any]:
        """アーティスト分析"""
        artist_count = defaultdict(int)
        artist_quality = defaultdict(list)
        
        for video_id, video_data in videos.items():
            channel_title = video_data.get("metadata", {}).get("channel_title", "")
            creators = video_data.get("creative_insight", {}).get("creators", [])
            
            if channel_title:
                artist_count[channel_title] += 1
                view_count = video_data.get("metadata", {}).get("view_count", 0)
                like_count = video_data.get("metadata", {}).get("like_count", 0)
                artist_quality[channel_title].append({"views": view_count, "likes": like_count})
            
            for creator in creators:
                creator_name = creator.get("name", "")
                if creator_name:
                    artist_count[creator_name] += 1
        
        return {
            "artist_distribution": dict(artist_count),
            "artist_quality_metrics": dict(artist_quality),
            "top_artists": sorted(artist_count.items(), key=lambda x: x[1], reverse=True)[:10]
        }
    
    def _analyze_themes(self, videos: Dict) -> Dict[str, Any]:
        """テーマ分析"""
        theme_count = defaultdict(int)
        title_keywords = defaultdict(int)
        
        for video_id, video_data in videos.items():
            title = video_data.get("metadata", {}).get("title", "")
            themes = video_data.get("creative_insight", {}).get("themes", [])
            
            for theme in themes:
                theme_count[theme] += 1
            
            # タイトルからキーワード抽出
            if title:
                # 楽曲名、アーティスト名のパターンを抽出
                keywords = self._extract_keywords_from_title(title)
                for keyword in keywords:
                    title_keywords[keyword] += 1
        
        return {
            "theme_distribution": dict(theme_count),
            "title_keywords": dict(title_keywords),
            "top_themes": sorted(theme_count.items(), key=lambda x: x[1], reverse=True)[:10]
        }
    
    def _analyze_quality_indicators(self, videos: Dict) -> Dict[str, Any]:
        """品質指標分析"""
        quality_metrics = []
        
        for video_id, video_data in videos.items():
            metadata = video_data.get("metadata", {})
            view_count = metadata.get("view_count", 0)
            like_count = metadata.get("like_count", 0)
            comment_count = metadata.get("comment_count", 0)
            
            # エンゲージメント率計算
            engagement_rate = 0
            if view_count > 0:
                engagement_rate = (like_count + comment_count) / view_count * 100
            
            quality_metrics.append({
                "video_id": video_id,
                "view_count": view_count,
                "like_count": like_count,
                "comment_count": comment_count,
                "engagement_rate": engagement_rate
            })
        
        # 品質指標の統計
        if quality_metrics:
            avg_views = sum(m["view_count"] for m in quality_metrics) / len(quality_metrics)
            avg_likes = sum(m["like_count"] for m in quality_metrics) / len(quality_metrics)
            avg_engagement = sum(m["engagement_rate"] for m in quality_metrics) / len(quality_metrics)
            
            return {
                "average_views": avg_views,
                "average_likes": avg_likes,
                "average_engagement_rate": avg_engagement,
                "high_quality_videos": [m for m in quality_metrics if m["engagement_rate"] > avg_engagement],
                "quality_threshold": avg_engagement
            }
        
        return {}
    
    def _load_video_history(self) -> Dict:
        """動画会話履歴を読み込み"""
        try:
            if self.video_history_path.exists():
                with open(self.video_history_path, 'r', encoding='utf-8') as f:
                    return json.load(f).get("video_conversations", {})
        except Exception as e:
            print(f"[好み分析] ⚠️ 動画履歴読み込みエラー: {e}")
        return {}
    
    def _load_multi_turn_data(self) -> Dict:
        """マルチターン会話データを読み込み"""
        try:
            if self.multi_turn_path.exists():
                with open(self.multi_turn_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"[好み分析] ⚠️ マルチターン会話データ読み込みエラー: {e}")
        return {}
    
    def _analyze_positive_reactions(self, video_history: Dict) -> Dict[str, Any]:
        """ポジティブな反応パターンを分析"""
        positive_videos = []
        
        for video_id, video_data in video_history.items():
            reactions = video_data.get("user_reactions", [])
            positive_count = reactions.count("positive")
            total_count = len(reactions)
            
            if positive_count > 0 and total_count > 0:
                positive_ratio = positive_count / total_count
                if positive_ratio >= 0.5:  # 50%以上がポジティブ
                    positive_videos.append({
                        "video_id": video_id,
                        "title": video_data.get("video_title", ""),
                        "positive_ratio": positive_ratio,
                        "conversation_count": video_data.get("conversation_count", 0),
                        "familiarity_score": video_data.get("familiarity_score", 0)
                    })
        
        return {
            "positive_videos": positive_videos,
            "positive_video_count": len(positive_videos),
            "common_characteristics": self._find_common_characteristics(positive_videos)
        }
    
    def _analyze_negative_reactions(self, video_history: Dict) -> Dict[str, Any]:
        """ネガティブな反応パターンを分析"""
        negative_videos = []
        
        for video_id, video_data in video_history.items():
            reactions = video_data.get("user_reactions", [])
            negative_count = reactions.count("negative")
            total_count = len(reactions)
            
            if negative_count > 0 and total_count > 0:
                negative_ratio = negative_count / total_count
                if negative_ratio >= 0.5:  # 50%以上がネガティブ
                    negative_videos.append({
                        "video_id": video_id,
                        "title": video_data.get("video_title", ""),
                        "negative_ratio": negative_ratio,
                        "conversation_count": video_data.get("conversation_count", 0)
                    })
        
        return {
            "negative_videos": negative_videos,
            "negative_video_count": len(negative_videos),
            "avoidance_patterns": self._find_avoidance_patterns(negative_videos)
        }
    
    def _analyze_familiarity_patterns(self, video_history: Dict) -> Dict[str, Any]:
        """馴染み度パターンを分析"""
        familiarity_data = []
        
        for video_id, video_data in video_history.items():
            familiarity_score = video_data.get("familiarity_score", 0)
            conversation_count = video_data.get("conversation_count", 0)
            
            if familiarity_score > 0:
                familiarity_data.append({
                    "video_id": video_id,
                    "title": video_data.get("video_title", ""),
                    "familiarity_score": familiarity_score,
                    "conversation_count": conversation_count
                })
        
        # 高馴染み度の動画を特定
        high_familiarity_videos = [v for v in familiarity_data if v["familiarity_score"] >= 0.5]
        
        return {
            "familiarity_distribution": familiarity_data,
            "high_familiarity_videos": high_familiarity_videos,
            "familiarity_characteristics": self._analyze_familiarity_characteristics(high_familiarity_videos)
        }
    
    def _analyze_conversation_patterns(self, multi_turn_data: Dict) -> Dict[str, Any]:
        """会話パターンを分析"""
        if not multi_turn_data:
            return {}
        
        turns = multi_turn_data.get("current_session", {}).get("turns", [])
        
        conversation_analysis = {
            "total_turns": len(turns),
            "mentioned_videos": [],
            "emotional_signals": [],
            "topic_transitions": []
        }
        
        for turn in turns:
            # 言及された動画の収集
            mentioned_videos = turn.get("mentioned_videos", [])
            for video in mentioned_videos:
                conversation_analysis["mentioned_videos"].append({
                    "video_id": video.get("video_id", ""),
                    "title": video.get("title", ""),
                    "search_score": video.get("search_score", 0)
                })
            
            # 感情シグナルの収集
            emotional_signals = turn.get("emotional_signals", {})
            if emotional_signals:
                conversation_analysis["emotional_signals"].append(emotional_signals)
        
        return conversation_analysis
    
    def _infer_preferences(self, music_preferences: Dict, reaction_patterns: Dict) -> Dict[str, Any]:
        """音楽的好みと反応パターンから推論"""
        inferred = {
            "strongly_preferred": [],
            "preferred": [],
            "less_preferred": [],
            "creative_opportunities": []
        }
        
        # 高品質かつポジティブな反応の楽曲を特定
        if music_preferences and reaction_patterns:
            top_genres = dict(music_preferences.get("genre_distribution", {}))
            positive_videos = reaction_patterns.get("positive_reaction_patterns", {}).get("positive_videos", [])
            
            # 強く好まれるジャンル
            for genre, count in top_genres.items():
                if count >= 3:  # 3回以上登場
                    inferred["strongly_preferred"].append({
                        "type": "genre",
                        "value": genre,
                        "confidence": min(count / 10, 1.0)
                    })
            
            # 創作機会の提案
            for video in positive_videos:
                if video.get("familiarity_score", 0) >= 0.5:
                    inferred["creative_opportunities"].append({
                        "type": "video_based_creation",
                        "title": video.get("title", ""),
                        "reason": "高い馴染み度とポジティブな反応"
                    })
        
        return inferred
    
    def _generate_creative_suggestion_patterns(self) -> Dict[str, List[str]]:
        """創作提案パターンを生成"""
        return {
            "music_analysis_based": [
                "この楽曲の構成、映像制作にも活かせそうだよね",
                "楽曲の感情的な部分、映像で表現したら綺麗だと思うんだけど",
                "このアーティストの技術力、参考になるなぁ"
            ],
            "visual_creation_based": [
                "この楽曲で映像作ったらどうかな？",
                "歌詞の世界観、ビジュアルで表現できそうだよね",
                "このクリエイターの映像技術、面白いね"
            ],
            "technical_discussion": [
                "この楽曲の構成設計、勉強になるね",
                "クリエイター陣の役割分担、参考になりそう",
                "こういう技術的な話、配信でも話してみたいな"
            ]
        }
    
    def _analyze_personality_alignment(self) -> Dict[str, Any]:
        """パーソナリティとの整合性分析"""
        return {
            "value_alignment_indicators": [
                "楽曲の本質的な魅力への注目",
                "クリエイターの技術力への評価",
                "感情的な深さへの共感"
            ],
            "consistency_checks": [
                "派手な演出よりも本質重視",
                "作為的でない自然な表現",
                "対等なパートナーとしての意見交換"
            ],
            "response_patterns": [
                "「〜だと思うんだけど」形式での意見表明",
                "「〜したいなって思ってて」形式での希望表現",
                "体験談を交えた具体的な提案"
            ]
        }
    
    def _extract_keywords_from_title(self, title: str) -> List[str]:
        """タイトルからキーワードを抽出"""
        keywords = []
        
        # 楽曲名パターン（「」『』で囲まれた部分）
        song_patterns = re.findall(r'[「『]([^」』]+)[」』]', title)
        keywords.extend(song_patterns)
        
        # アーティスト名パターン（▽▲などの特殊文字を含む）
        artist_patterns = re.findall(r'[▽▲]([^▲▽\s]+)[▲▽]', title)
        keywords.extend(artist_patterns)
        
        return keywords
    
    def _find_common_characteristics(self, videos: List[Dict]) -> Dict[str, Any]:
        """共通特徴を見つける"""
        if not videos:
            return {}
        
        # タイトルからの共通キーワード
        all_titles = [v.get("title", "") for v in videos]
        common_keywords = []
        
        for title in all_titles:
            keywords = self._extract_keywords_from_title(title)
            common_keywords.extend(keywords)
        
        keyword_count = Counter(common_keywords)
        
        return {
            "common_keywords": dict(keyword_count.most_common(5)),
            "average_familiarity": sum(v.get("familiarity_score", 0) for v in videos) / len(videos),
            "total_conversations": sum(v.get("conversation_count", 0) for v in videos)
        }
    
    def _find_avoidance_patterns(self, videos: List[Dict]) -> Dict[str, Any]:
        """回避パターンを見つける"""
        if not videos:
            return {}
        
        return {
            "negative_characteristics": [
                "過度に商業的な楽曲",
                "本質的な魅力に欠ける楽曲",
                "作為的な演出の楽曲"
            ],
            "avoidance_indicators": [
                "表面的な魅力のみ",
                "技術的完成度の低さ",
                "感情的な深さの欠如"
            ]
        }
    
    def _analyze_familiarity_characteristics(self, videos: List[Dict]) -> Dict[str, Any]:
        """馴染み度の特徴分析"""
        if not videos:
            return {}
        
        return {
            "high_familiarity_indicators": [
                "複数回の会話",
                "ポジティブな反応",
                "技術的な完成度"
            ],
            "familiarity_building_factors": [
                "楽曲の品質",
                "クリエイターの技術力",
                "感情的な響き"
            ]
        }
    
    def get_cached_preferences(self) -> Optional[Dict[str, Any]]:
        """キャッシュされた好み情報を取得"""
        return self.preference_cache if self.preference_cache else None
    
    def needs_refresh(self, max_age_hours: int = 24) -> bool:
        """キャッシュのリフレッシュが必要かチェック"""
        if not self.last_analysis_time:
            return True
        
        time_diff = datetime.now() - self.last_analysis_time
        return time_diff.total_seconds() > (max_age_hours * 3600)

# 使用例・テスト
if __name__ == "__main__":
    print("=" * 50)
    print("🎵 好み推測システムテスト")
    print("=" * 50)
    
    try:
        analyzer = PreferenceAnalyzer()
        
        # 好みプロファイルの生成
        profile = analyzer.generate_preference_profile()
        
        if profile:
            print("\n📊 音楽的好み分析結果:")
            music_prefs = profile.get("music_preferences", {})
            top_genres = music_prefs.get("preferred_genres", {}).get("top_genres", [])
            for genre, count in top_genres[:3]:
                print(f"  - {genre}: {count}件")
            
            print("\n💭 反応パターン分析結果:")
            reaction_patterns = profile.get("reaction_patterns", {})
            positive_count = reaction_patterns.get("positive_reaction_patterns", {}).get("positive_video_count", 0)
            print(f"  - ポジティブ反応動画: {positive_count}件")
            
            print("\n🎨 創作提案パターン:")
            creative_suggestions = profile.get("creative_suggestions", {})
            music_suggestions = creative_suggestions.get("music_analysis_based", [])
            for suggestion in music_suggestions[:2]:
                print(f"  - {suggestion}")
                
        else:
            print("⚠️ 好みプロファイルの生成に失敗しました")
            
    except Exception as e:
        print(f"❌ テストエラー: {e}")
    
    print("\n好み推測システムテスト完了")
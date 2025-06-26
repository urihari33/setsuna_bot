#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
トピック学習システム - Phase 2-B-2
ユーザーの音楽的嗜好パターンを学習・分析する
"""

import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import re
from collections import defaultdict

class TopicLearningSystem:
    """ユーザーの嗜好パターンを学習するクラス"""
    
    def __init__(self):
        """初期化"""
        # Windows環境とWSL2環境両方に対応
        if os.name == 'nt':  # Windows
            self.preferences_file = Path("D:/setsuna_bot/data/user_preferences.json")
        else:  # Linux/WSL2
            self.preferences_file = Path("/mnt/d/setsuna_bot/data/user_preferences.json")
        
        # 学習データ構造
        self.genre_preferences = {}      # ジャンル別好みスコア
        self.creator_preferences = {}    # クリエイター別好みスコア
        self.time_patterns = {}          # 時間帯別傾向
        self.topic_clusters = {}         # 関連動画クラスター
        self.mood_patterns = {}          # ムード別傾向
        
        # 学習設定
        self.learning_config = {
            "enable_genre_learning": True,
            "enable_creator_learning": True,
            "enable_time_learning": True,
            "enable_mood_learning": True,
            "max_history_days": 90,  # 90日間の学習データ保持
            "min_interactions_for_pattern": 3,  # パターン認識に必要な最小インタラクション数
        }
        
        self._ensure_data_dir()
        self._load_preferences()
        
        print("[嗜好学習] ✅ トピック学習システム初期化完了")
    
    def _ensure_data_dir(self):
        """データディレクトリの確保"""
        self.preferences_file.parent.mkdir(parents=True, exist_ok=True)
    
    def _load_preferences(self):
        """嗜好データファイルから読み込み"""
        try:
            if self.preferences_file.exists():
                with open(self.preferences_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.genre_preferences = data.get('genre_preferences', {})
                    self.creator_preferences = data.get('creator_preferences', {})
                    self.time_patterns = data.get('time_patterns', {})
                    self.topic_clusters = data.get('topic_clusters', {})
                    self.mood_patterns = data.get('mood_patterns', {})
                    
                    # 設定の読み込み（デフォルト値で補完）
                    saved_config = data.get('learning_config', {})
                    self.learning_config.update(saved_config)
                
                total_patterns = (len(self.genre_preferences) + 
                                len(self.creator_preferences) + 
                                len(self.time_patterns))
                print(f"[嗜好学習] 📊 過去の学習データ: {total_patterns}パターンをロード")
            else:
                print("[嗜好学習] 📝 新規学習データファイルを作成")
                
        except Exception as e:
            print(f"[嗜好学習] ⚠️ 学習データ読み込み失敗: {e}")
            self._initialize_empty_preferences()
    
    def _initialize_empty_preferences(self):
        """空の嗜好データで初期化"""
        self.genre_preferences = {}
        self.creator_preferences = {}
        self.time_patterns = defaultdict(lambda: defaultdict(int))
        self.topic_clusters = {}
        self.mood_patterns = {}
    
    def _save_preferences(self):
        """嗜好データファイルに保存"""
        try:
            data = {
                'genre_preferences': self.genre_preferences,
                'creator_preferences': self.creator_preferences,
                'time_patterns': dict(self.time_patterns),
                'topic_clusters': self.topic_clusters,
                'mood_patterns': self.mood_patterns,
                'learning_config': self.learning_config,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.preferences_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"[嗜好学習] ❌ 嗜好データ保存失敗: {e}")
    
    def _extract_genre_from_video(self, video_data: Dict[str, Any]) -> Optional[str]:
        """動画データからジャンルを抽出"""
        try:
            # 分析結果からジャンル取得
            if 'creative_insight' in video_data:
                insight = video_data['creative_insight']
                if 'music_analysis' in insight:
                    music_analysis = insight['music_analysis']
                    if music_analysis.get('genre'):
                        return music_analysis['genre']
            
            # メタデータからの推測
            metadata = video_data.get('metadata', {})
            title = metadata.get('title', '').lower()
            description = metadata.get('description', '').lower()
            
            # ジャンル推測パターン
            genre_patterns = {
                'ボカロ': ['ボカロ', 'vocaloid', 'ミク', 'miku'],
                'ポップス': ['pop', 'ポップ', 'j-pop'],
                'ロック': ['rock', 'ロック'],
                'バラード': ['ballad', 'バラード'],
                'アニソン': ['アニメ', 'anime', 'アニソン'],
                'ゲーム音楽': ['ゲーム', 'game', 'bgm'],
                'カバー': ['cover', 'カバー', '歌ってみた'],
                'オリジナル': ['original', 'オリジナル', 'mv', 'music video']
            }
            
            for genre, patterns in genre_patterns.items():
                if any(pattern in title or pattern in description for pattern in patterns):
                    return genre
            
            return "その他"
            
        except Exception as e:
            print(f"[嗜好学習] ⚠️ ジャンル抽出エラー: {e}")
            return "不明"
    
    def _extract_creators_from_video(self, video_data: Dict[str, Any]) -> List[str]:
        """動画データからクリエイター情報を抽出"""
        try:
            creators = []
            
            # 分析結果からクリエイター取得
            if 'creative_insight' in video_data:
                insight = video_data['creative_insight']
                if 'creators' in insight:
                    for creator in insight['creators']:
                        if creator.get('name'):
                            creators.append(creator['name'])
            
            # チャンネル名も追加
            metadata = video_data.get('metadata', {})
            channel_title = metadata.get('channel_title', '')
            if channel_title and channel_title not in creators:
                # チャンネル名の正規化
                normalized_channel = self._normalize_channel_name(channel_title)
                creators.append(normalized_channel)
            
            return creators
            
        except Exception as e:
            print(f"[嗜好学習] ⚠️ クリエイター抽出エラー: {e}")
            return []
    
    def _normalize_channel_name(self, channel_name: str) -> str:
        """チャンネル名を正規化"""
        # 不要な装飾を除去
        normalized = channel_name
        
        # 除去パターン
        removal_patterns = [
            r'【[^】]*】',  # 【】内
            r'\[[^\]]*\]',  # []内
            r'Official.*',  # Official以降
            r'Ch\.?$',  # 末尾のCh
            r'Channel$',  # 末尾のChannel
        ]
        
        for pattern in removal_patterns:
            normalized = re.sub(pattern, '', normalized, flags=re.IGNORECASE)
        
        return normalized.strip()
    
    def _get_time_category(self) -> str:
        """現在時刻のカテゴリを取得"""
        current_hour = datetime.now().hour
        
        if 5 <= current_hour < 10:
            return "morning"
        elif 10 <= current_hour < 15:
            return "afternoon"
        elif 15 <= current_hour < 18:
            return "evening"
        elif 18 <= current_hour < 22:
            return "night"
        else:
            return "late_night"
    
    def _reaction_to_score_delta(self, reaction: str) -> float:
        """ユーザー反応をスコア変化量に変換"""
        reaction_scores = {
            "positive": 0.3,
            "neutral": 0.1,
            "negative": -0.2
        }
        return reaction_scores.get(reaction, 0.0)
    
    def learn_from_interaction(self, video_data: Dict[str, Any], user_reaction: str, 
                             user_input: str = "", video_title: str = "") -> bool:
        """
        動画インタラクションから学習
        
        Args:
            video_data: 動画データ
            user_reaction: ユーザー反応 (positive/neutral/negative)
            user_input: ユーザーの入力文
            video_title: 動画タイトル
            
        Returns:
            学習成功したかどうか
        """
        try:
            current_time = datetime.now()
            score_delta = self._reaction_to_score_delta(user_reaction)
            
            # ジャンル学習
            if self.learning_config["enable_genre_learning"]:
                genre = self._extract_genre_from_video(video_data)
                if genre:
                    if genre not in self.genre_preferences:
                        self.genre_preferences[genre] = {
                            "score": 0.5,  # 初期スコア
                            "interaction_count": 0,
                            "positive_count": 0,
                            "negative_count": 0,
                            "last_interaction": current_time.isoformat()
                        }
                    
                    pref = self.genre_preferences[genre]
                    pref["score"] = max(0.0, min(1.0, pref["score"] + score_delta))
                    pref["interaction_count"] += 1
                    pref["last_interaction"] = current_time.isoformat()
                    
                    if user_reaction == "positive":
                        pref["positive_count"] += 1
                    elif user_reaction == "negative":
                        pref["negative_count"] += 1
            
            # クリエイター学習
            if self.learning_config["enable_creator_learning"]:
                creators = self._extract_creators_from_video(video_data)
                for creator in creators:
                    if creator not in self.creator_preferences:
                        self.creator_preferences[creator] = {
                            "score": 0.5,
                            "interaction_count": 0,
                            "positive_count": 0,
                            "negative_count": 0,
                            "last_interaction": current_time.isoformat()
                        }
                    
                    pref = self.creator_preferences[creator]
                    pref["score"] = max(0.0, min(1.0, pref["score"] + score_delta))
                    pref["interaction_count"] += 1
                    pref["last_interaction"] = current_time.isoformat()
                    
                    if user_reaction == "positive":
                        pref["positive_count"] += 1
                    elif user_reaction == "negative":
                        pref["negative_count"] += 1
            
            # 時間パターン学習
            if self.learning_config["enable_time_learning"]:
                time_category = self._get_time_category()
                genre = self._extract_genre_from_video(video_data)
                
                if time_category not in self.time_patterns:
                    self.time_patterns[time_category] = defaultdict(int)
                
                if genre and user_reaction == "positive":
                    self.time_patterns[time_category][genre] += 1
            
            # ムードパターン学習
            if self.learning_config["enable_mood_learning"]:
                mood = self._extract_mood_from_video(video_data)
                if mood and user_reaction == "positive":
                    if mood not in self.mood_patterns:
                        self.mood_patterns[mood] = {"score": 0.5, "count": 0}
                    
                    self.mood_patterns[mood]["score"] = min(1.0, 
                        self.mood_patterns[mood]["score"] + score_delta)
                    self.mood_patterns[mood]["count"] += 1
            
            # 自動保存
            self._save_preferences()
            
            print(f"[嗜好学習] 📝 学習更新: {user_reaction} → ジャンル:{genre}, クリエイター:{len(creators)}名")
            return True
            
        except Exception as e:
            print(f"[嗜好学習] ❌ 学習処理失敗: {e}")
            return False
    
    def _extract_mood_from_video(self, video_data: Dict[str, Any]) -> Optional[str]:
        """動画データからムードを抽出"""
        try:
            if 'creative_insight' in video_data:
                insight = video_data['creative_insight']
                if 'music_analysis' in insight:
                    music_analysis = insight['music_analysis']
                    return music_analysis.get('mood')
            return None
        except:
            return None
    
    def get_preferred_genres(self, limit: int = 5) -> List[Tuple[str, float]]:
        """好みのジャンルを取得（スコア順）"""
        if not self.genre_preferences:
            return []
        
        # スコア順でソート
        sorted_genres = sorted(
            self.genre_preferences.items(),
            key=lambda x: x[1]["score"],
            reverse=True
        )
        
        # 最小インタラクション数フィルタ
        min_interactions = self.learning_config["min_interactions_for_pattern"]
        filtered_genres = [
            (genre, data["score"]) 
            for genre, data in sorted_genres 
            if data["interaction_count"] >= min_interactions
        ]
        
        return filtered_genres[:limit]
    
    def get_preferred_creators(self, limit: int = 5) -> List[Tuple[str, float]]:
        """好みのクリエイターを取得（スコア順）"""
        if not self.creator_preferences:
            return []
        
        sorted_creators = sorted(
            self.creator_preferences.items(),
            key=lambda x: x[1]["score"],
            reverse=True
        )
        
        min_interactions = self.learning_config["min_interactions_for_pattern"]
        filtered_creators = [
            (creator, data["score"]) 
            for creator, data in sorted_creators 
            if data["interaction_count"] >= min_interactions
        ]
        
        return filtered_creators[:limit]
    
    def get_time_preferences(self, time_category: Optional[str] = None) -> Dict[str, int]:
        """時間帯別の嗜好を取得"""
        if time_category is None:
            time_category = self._get_time_category()
        
        return dict(self.time_patterns.get(time_category, {}))
    
    def detect_preference_keywords(self, user_input: str) -> Dict[str, Any]:
        """
        ユーザー入力から嗜好関連キーワードを検出
        
        Args:
            user_input: ユーザーの入力
            
        Returns:
            検出された嗜好パターン情報
        """
        detected_patterns = {
            "preference_type": None,
            "specific_request": None,
            "familiarity_level": None
        }
        
        user_lower = user_input.lower()
        
        # 「いつもの」パターン検出
        familiar_patterns = [
            r'いつもの',
            r'お気に入り',
            r'よく聞く',
            r'好きな',
            r'お馴染み'
        ]
        
        for pattern in familiar_patterns:
            if re.search(pattern, user_input):
                detected_patterns["familiarity_level"] = "familiar"
                break
        
        # 「新しい」パターン検出
        new_patterns = [
            r'新しい',
            r'違う',
            r'別の',
            r'初めて',
            r'知らない'
        ]
        
        for pattern in new_patterns:
            if re.search(pattern, user_input):
                detected_patterns["familiarity_level"] = "new"
                break
        
        # 具体的な嗜好検出
        for genre in self.genre_preferences.keys():
            if genre.lower() in user_lower:
                detected_patterns["preference_type"] = "genre"
                detected_patterns["specific_request"] = genre
                break
        
        for creator in self.creator_preferences.keys():
            if creator.lower() in user_lower:
                detected_patterns["preference_type"] = "creator"
                detected_patterns["specific_request"] = creator
                break
        
        return detected_patterns
    
    def get_learning_summary(self) -> Dict[str, Any]:
        """学習状況のサマリーを取得"""
        return {
            "total_genres": len(self.genre_preferences),
            "total_creators": len(self.creator_preferences),
            "top_genres": self.get_preferred_genres(3),
            "top_creators": self.get_preferred_creators(3),
            "time_patterns": dict(self.time_patterns),
            "learning_config": self.learning_config
        }
    
    def clear_learning_data(self, data_type: str = "all") -> bool:
        """学習データをクリア"""
        try:
            if data_type == "all":
                self._initialize_empty_preferences()
            elif data_type == "genres":
                self.genre_preferences = {}
            elif data_type == "creators":
                self.creator_preferences = {}
            elif data_type == "time_patterns":
                self.time_patterns = defaultdict(lambda: defaultdict(int))
            elif data_type == "mood_patterns":
                self.mood_patterns = {}
            
            self._save_preferences()
            print(f"[嗜好学習] 🗑️ 学習データクリア: {data_type}")
            return True
            
        except Exception as e:
            print(f"[嗜好学習] ❌ データクリア失敗: {e}")
            return False


# 使用例・テスト
if __name__ == "__main__":
    print("=== トピック学習システムテスト ===")
    
    learning_system = TopicLearningSystem()
    
    # テスト用の動画データ
    test_video_data = {
        "metadata": {
            "title": "【歌ってみた】テスト楽曲【にじさんじ】",
            "channel_title": "テストチャンネル / にじさんじ"
        },
        "creative_insight": {
            "music_analysis": {
                "genre": "ポップス",
                "mood": "明るい"
            },
            "creators": [{"name": "テストクリエイター"}]
        }
    }
    
    # 学習テスト
    print("\n📝 学習テスト実行:")
    success = learning_system.learn_from_interaction(
        test_video_data, 
        "positive", 
        "この曲いいね！"
    )
    
    if success:
        print("✅ 学習成功")
        
        # 学習結果確認
        summary = learning_system.get_learning_summary()
        print(f"\n📊 学習サマリー:")
        print(f"  ジャンル数: {summary['total_genres']}")
        print(f"  クリエイター数: {summary['total_creators']}")
        print(f"  好みジャンル: {summary['top_genres']}")
        print(f"  好みクリエイター: {summary['top_creators']}")
    else:
        print("❌ 学習失敗")
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ユーザー興味追跡システム - Phase 2D実装
トピック別の興味レベル・エンゲージメント測定とリアルタイム追跡
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from datetime import datetime, timedelta
import re
import math
from statistics import mean, stdev

# プロジェクトルートをパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 関連システム
try:
    from core.conversation_history_analyzer import ConversationHistoryAnalyzer
    ANALYZER_AVAILABLE = True
except ImportError:
    ANALYZER_AVAILABLE = False

# Windowsパス設定
if os.name == 'nt':
    DATA_DIR = Path("D:/setsuna_bot/data")
    TRACKER_CACHE_DIR = Path("D:/setsuna_bot/interest_tracker_cache")
else:
    DATA_DIR = Path("/mnt/d/setsuna_bot/data")
    TRACKER_CACHE_DIR = Path("/mnt/d/setsuna_bot/interest_tracker_cache")

TRACKER_CACHE_DIR.mkdir(parents=True, exist_ok=True)

@dataclass
class InterestMetrics:
    """興味メトリクスデータクラス"""
    topic: str
    current_level: float          # 現在の興味レベル (0.0-1.0)
    engagement_score: float       # エンゲージメントスコア
    frequency_score: float        # 言及頻度スコア
    recency_score: float         # 最近性スコア
    depth_score: float           # 理解深度スコア
    sentiment_score: float       # 感情スコア
    trend_direction: str         # "increasing", "stable", "decreasing"
    confidence: float            # 信頼度
    last_updated: str

@dataclass
class EngagementEvent:
    """エンゲージメントイベントデータクラス"""
    event_id: str
    topic: str
    timestamp: str
    event_type: str              # "mention", "question", "deep_dive", "positive_feedback"
    intensity: float             # イベント強度 (0.0-1.0)
    context: str                 # コンテキスト情報
    duration: Optional[float]    # 持続時間（秒）

@dataclass
class InterestCluster:
    """興味クラスターデータクラス"""
    cluster_id: str
    cluster_name: str
    related_topics: List[str]
    cluster_strength: float      # クラスター結合度
    dominant_topic: str          # 主要トピック
    emergence_pattern: str       # 出現パターン
    predicted_growth: float      # 成長予測

class UserInterestTracker:
    """ユーザー興味追跡システムクラス"""
    
    def __init__(self):
        """初期化"""
        # データパス
        self.interest_metrics_path = TRACKER_CACHE_DIR / "interest_metrics.json"
        self.engagement_events_path = TRACKER_CACHE_DIR / "engagement_events.json"
        self.interest_clusters_path = TRACKER_CACHE_DIR / "interest_clusters.json"
        self.tracking_history_path = TRACKER_CACHE_DIR / "tracking_history.json"
        
        # 会話履歴分析システム
        if ANALYZER_AVAILABLE:
            self.history_analyzer = ConversationHistoryAnalyzer()
        else:
            self.history_analyzer = None
            print("[興味追跡] ⚠️ 会話履歴分析システムが利用できません")
        
        # データ
        self.interest_metrics = {}
        self.engagement_events = deque(maxlen=1000)  # 最新1000イベント
        self.interest_clusters = {}
        self.tracking_history = []
        
        # リアルタイム追跡用
        self.current_session_events = []
        self.session_start_time = datetime.now()
        self.interaction_memory = deque(maxlen=50)  # 直近50インタラクション
        
        # 追跡パラメータ
        self.decay_factor = 0.95       # 時間減衰率（日次）
        self.recency_weight = 0.3      # 最近性重み
        self.frequency_weight = 0.2    # 頻度重み
        self.depth_weight = 0.2        # 深度重み
        self.sentiment_weight = 0.3    # 感情重み
        
        # トピック検出パターン
        self.topic_patterns = self._build_topic_patterns()
        self.engagement_indicators = self._build_engagement_indicators()
        self.depth_indicators = self._build_depth_indicators()
        
        # 統計情報
        self.tracking_statistics = {
            "total_topics_tracked": 0,
            "total_engagement_events": 0,
            "active_clusters": 0,
            "tracking_accuracy": 0.0,
            "last_update": None
        }
        
        self._load_existing_data()
        print("[興味追跡] ✅ ユーザー興味追跡システム初期化完了")
    
    def _build_topic_patterns(self) -> Dict[str, List[str]]:
        """トピックパターン構築"""
        return {
            "音楽": [
                r"(音楽|曲|歌|ミュージック|楽曲|メロディ|リズム|ハーモニー)",
                r"(アーティスト|歌手|バンド|ミュージシャン|作曲家)",
                r"(ジャンル|スタイル|テンポ|ビート)"
            ],
            "動画制作": [
                r"(動画|映像|ビデオ|コンテンツ|編集)",
                r"(撮影|録画|配信|ストリーム|ライブ)",
                r"(エフェクト|トランジション|カット|モンタージュ)"
            ],
            "アニメ": [
                r"(アニメ|アニメーション|漫画|マンガ)",
                r"(キャラクター|声優|作画|演出)",
                r"(二次元|オタク|萌え|推し)"
            ],
            "ゲーム": [
                r"(ゲーム|プレイ|ゲーミング|eスポーツ)",
                r"(実況|配信|ストリーマー|プレイヤー)",
                r"(攻略|レベル|スキル|ランク)"
            ],
            "技術": [
                r"(技術|テクノロジー|AI|人工知能)",
                r"(プログラミング|コード|開発|エンジニア)",
                r"(システム|アルゴリズム|データ|ネットワーク)"
            ],
            "創作": [
                r"(創作|制作|クリエイティブ|アート)",
                r"(デザイン|イラスト|絵|画像)",
                r"(作品|表現|インスピレーション|アイデア)"
            ]
        }
    
    def _build_engagement_indicators(self) -> Dict[str, List[str]]:
        """エンゲージメント指標構築"""
        return {
            "high_engagement": [
                "すごく", "とても", "めちゃくちゃ", "最高", "素晴らしい", "感動",
                "夢中", "ハマる", "お気に入り", "大好き", "興奮", "わくわく"
            ],
            "medium_engagement": [
                "いいね", "良い", "面白い", "興味深い", "気になる", "好き",
                "なるほど", "へー", "そうなんだ", "知らなかった"
            ],
            "low_engagement": [
                "まあまあ", "普通", "そうですね", "ふーん", "そうかも",
                "どうかな", "微妙", "いまいち"
            ],
            "question_engagement": [
                "どうやって", "なぜ", "どんな", "教えて", "詳しく", "もっと",
                "他には", "例えば", "具体的に", "分からない"
            ]
        }
    
    def _build_depth_indicators(self) -> Dict[str, List[str]]:
        """深度指標構築"""
        return {
            "surface": [
                "知らない", "初めて", "聞いたことない", "何それ", "どういう意味",
                "簡単に", "基本的", "入門", "初心者"
            ],
            "intermediate": [
                "知ってる", "聞いたことある", "だいたい", "ある程度", "まあまあ",
                "一般的", "普通", "標準的", "中級"
            ],
            "advanced": [
                "詳しい", "専門的", "高度", "マニアック", "プロ級", "エキスパート",
                "深く", "本格的", "技術的", "上級"
            ]
        }
    
    def _load_existing_data(self):
        """既存データロード"""
        # 興味メトリクス
        try:
            if self.interest_metrics_path.exists():
                with open(self.interest_metrics_path, 'r', encoding='utf-8') as f:
                    metrics_data = json.load(f)
                    self.interest_metrics = {
                        topic: InterestMetrics(**data) 
                        for topic, data in metrics_data.get("metrics", {}).items()
                    }
                print(f"[興味追跡] 📊 {len(self.interest_metrics)}個の興味メトリクスをロード")
        except Exception as e:
            print(f"[興味追跡] ⚠️ 興味メトリクスロードエラー: {e}")
        
        # エンゲージメントイベント
        try:
            if self.engagement_events_path.exists():
                with open(self.engagement_events_path, 'r', encoding='utf-8') as f:
                    events_data = json.load(f)
                    events_list = events_data.get("events", [])
                    self.engagement_events = deque(
                        [EngagementEvent(**event) for event in events_list],
                        maxlen=1000
                    )
                print(f"[興味追跡] 📊 {len(self.engagement_events)}個のエンゲージメントイベントをロード")
        except Exception as e:
            print(f"[興味追跡] ⚠️ エンゲージメントイベントロードエラー: {e}")
        
        # 興味クラスター
        try:
            if self.interest_clusters_path.exists():
                with open(self.interest_clusters_path, 'r', encoding='utf-8') as f:
                    clusters_data = json.load(f)
                    self.interest_clusters = {
                        cid: InterestCluster(**cluster) 
                        for cid, cluster in clusters_data.get("clusters", {}).items()
                    }
                print(f"[興味追跡] 📊 {len(self.interest_clusters)}個の興味クラスターをロード")
        except Exception as e:
            print(f"[興味追跡] ⚠️ 興味クラスターロードエラー: {e}")
    
    def track_user_interaction(self, user_input: str, context: Optional[str] = None) -> List[str]:
        """ユーザーインタラクション追跡"""
        # インタラクション記録
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "context": context or "",
            "processed": False
        }
        self.interaction_memory.append(interaction)
        
        # トピック検出
        detected_topics = self._detect_topics_in_text(user_input)
        
        # エンゲージメントイベント生成
        for topic in detected_topics:
            events = self._generate_engagement_events(topic, user_input, context)
            for event in events:
                self.engagement_events.append(event)
                self.current_session_events.append(event)
        
        # 興味メトリクス更新
        for topic in detected_topics:
            self._update_interest_metrics(topic, user_input)
        
        # インタラクション処理済みマーク
        interaction["processed"] = True
        
        return detected_topics
    
    def _detect_topics_in_text(self, text: str) -> List[str]:
        """テキスト内トピック検出"""
        detected_topics = []
        
        for topic, patterns in self.topic_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    detected_topics.append(topic)
                    break
        
        return detected_topics
    
    def _generate_engagement_events(self, topic: str, user_input: str, context: Optional[str]) -> List[EngagementEvent]:
        """エンゲージメントイベント生成"""
        events = []
        timestamp = datetime.now().isoformat()
        
        # 基本言及イベント
        base_intensity = 0.3
        event_id = f"mention_{topic}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        events.append(EngagementEvent(
            event_id=event_id,
            topic=topic,
            timestamp=timestamp,
            event_type="mention",
            intensity=base_intensity,
            context=user_input[:200],
            duration=None
        ))
        
        # エンゲージメントレベル別イベント
        engagement_level = self._assess_engagement_level(user_input)
        if engagement_level in ["high", "medium"]:
            intensity = 0.8 if engagement_level == "high" else 0.6
            event_id = f"engagement_{topic}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            
            events.append(EngagementEvent(
                event_id=event_id,
                topic=topic,
                timestamp=timestamp,
                event_type=f"{engagement_level}_engagement",
                intensity=intensity,
                context=user_input[:200],
                duration=None
            ))
        
        # 質問イベント
        if self._is_question_about_topic(user_input, topic):
            event_id = f"question_{topic}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            
            events.append(EngagementEvent(
                event_id=event_id,
                topic=topic,
                timestamp=timestamp,
                event_type="question",
                intensity=0.7,
                context=user_input[:200],
                duration=None
            ))
        
        # 深掘りイベント
        depth_level = self._assess_depth_level(user_input)
        if depth_level == "advanced":
            event_id = f"deep_dive_{topic}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            
            events.append(EngagementEvent(
                event_id=event_id,
                topic=topic,
                timestamp=timestamp,
                event_type="deep_dive",
                intensity=0.9,
                context=user_input[:200],
                duration=None
            ))
        
        return events
    
    def _assess_engagement_level(self, text: str) -> str:
        """エンゲージメントレベル評価"""
        high_count = sum(1 for indicator in self.engagement_indicators["high_engagement"] if indicator in text)
        medium_count = sum(1 for indicator in self.engagement_indicators["medium_engagement"] if indicator in text)
        low_count = sum(1 for indicator in self.engagement_indicators["low_engagement"] if indicator in text)
        
        if high_count > 0:
            return "high"
        elif medium_count > 0:
            return "medium"
        elif low_count > 0:
            return "low"
        else:
            return "neutral"
    
    def _is_question_about_topic(self, text: str, topic: str) -> bool:
        """トピックに関する質問かどうか判定"""
        # 質問マーカー
        question_markers = ["?", "？", "何", "どう", "なぜ", "いつ", "どこ", "誰", "どんな"]
        has_question_marker = any(marker in text for marker in question_markers)
        
        # トピック関連
        topic_patterns = self.topic_patterns.get(topic, [])
        has_topic_reference = any(re.search(pattern, text) for pattern in topic_patterns)
        
        return has_question_marker and has_topic_reference
    
    def _assess_depth_level(self, text: str) -> str:
        """深度レベル評価"""
        surface_count = sum(1 for indicator in self.depth_indicators["surface"] if indicator in text)
        intermediate_count = sum(1 for indicator in self.depth_indicators["intermediate"] if indicator in text)
        advanced_count = sum(1 for indicator in self.depth_indicators["advanced"] if indicator in text)
        
        if advanced_count > 0:
            return "advanced"
        elif intermediate_count > 0:
            return "intermediate"
        elif surface_count > 0:
            return "surface"
        else:
            return "intermediate"  # デフォルト
    
    def _update_interest_metrics(self, topic: str, user_input: str):
        """興味メトリクス更新"""
        # 既存メトリクス取得または新規作成
        if topic not in self.interest_metrics:
            self.interest_metrics[topic] = InterestMetrics(
                topic=topic,
                current_level=0.5,
                engagement_score=0.0,
                frequency_score=0.0,
                recency_score=1.0,
                depth_score=0.5,
                sentiment_score=0.5,
                trend_direction="stable",
                confidence=0.5,
                last_updated=datetime.now().isoformat()
            )
        
        metrics = self.interest_metrics[topic]
        
        # 各種スコア更新
        # 1. 頻度スコア
        metrics.frequency_score = self._calculate_frequency_score(topic)
        
        # 2. 最近性スコア
        metrics.recency_score = 1.0  # 現在のインタラクションなので最高値
        
        # 3. エンゲージメントスコア
        engagement_level = self._assess_engagement_level(user_input)
        engagement_boost = {
            "high": 0.3,
            "medium": 0.2,
            "low": 0.1,
            "neutral": 0.05
        }.get(engagement_level, 0.05)
        metrics.engagement_score = min(1.0, metrics.engagement_score + engagement_boost)
        
        # 4. 深度スコア
        depth_level = self._assess_depth_level(user_input)
        depth_values = {"surface": 0.2, "intermediate": 0.5, "advanced": 0.9}
        new_depth = depth_values.get(depth_level, 0.5)
        metrics.depth_score = (metrics.depth_score * 0.7) + (new_depth * 0.3)  # 移動平均
        
        # 5. 感情スコア
        sentiment = self._assess_sentiment(user_input)
        metrics.sentiment_score = (metrics.sentiment_score * 0.8) + (sentiment * 0.2)
        
        # 6. 総合興味レベル計算
        metrics.current_level = (
            metrics.frequency_score * self.frequency_weight +
            metrics.recency_score * self.recency_weight +
            metrics.engagement_score * 0.25 +
            metrics.depth_score * self.depth_weight +
            metrics.sentiment_score * self.sentiment_weight
        )
        metrics.current_level = max(0.0, min(1.0, metrics.current_level))
        
        # 7. トレンド方向更新
        metrics.trend_direction = self._calculate_trend_direction(topic)
        
        # 8. 信頼度更新
        metrics.confidence = self._calculate_confidence(topic)
        
        # 更新時刻記録
        metrics.last_updated = datetime.now().isoformat()
    
    def _calculate_frequency_score(self, topic: str) -> float:
        """頻度スコア計算"""
        # 過去30日間の言及回数
        cutoff_date = datetime.now() - timedelta(days=30)
        recent_events = [
            event for event in self.engagement_events 
            if event.topic == topic and datetime.fromisoformat(event.timestamp) > cutoff_date
        ]
        
        frequency = len(recent_events)
        # 正規化（週1回で0.5、毎日で1.0）
        return min(1.0, frequency / 30)
    
    def _assess_sentiment(self, text: str) -> float:
        """感情評価"""
        positive_indicators = ["好き", "良い", "素晴らしい", "最高", "気に入った", "面白い", "楽しい"]
        negative_indicators = ["嫌い", "悪い", "つまらない", "微妙", "いまいち", "残念"]
        
        positive_count = sum(1 for indicator in positive_indicators if indicator in text)
        negative_count = sum(1 for indicator in negative_indicators if indicator in text)
        
        if positive_count > negative_count:
            return 0.8
        elif negative_count > positive_count:
            return 0.2
        else:
            return 0.5
    
    def _calculate_trend_direction(self, topic: str) -> str:
        """トレンド方向計算"""
        # 過去のメトリクス履歴から傾向を分析
        # 簡易実装：直近3イベントの強度推移
        recent_events = [
            event for event in list(self.engagement_events)[-10:] 
            if event.topic == topic
        ]
        
        if len(recent_events) < 2:
            return "stable"
        
        recent_intensities = [event.intensity for event in recent_events[-3:]]
        
        if len(recent_intensities) >= 2:
            if recent_intensities[-1] > recent_intensities[0] + 0.1:
                return "increasing"
            elif recent_intensities[-1] < recent_intensities[0] - 0.1:
                return "decreasing"
        
        return "stable"
    
    def _calculate_confidence(self, topic: str) -> float:
        """信頼度計算"""
        # イベント数と時間的分散に基づく信頼度
        topic_events = [event for event in self.engagement_events if event.topic == topic]
        
        event_count = len(topic_events)
        if event_count == 0:
            return 0.0
        
        # イベント数による信頼度（10イベントで0.8）
        count_confidence = min(0.8, event_count / 10)
        
        # 時間的分散による信頼度
        if event_count > 1:
            timestamps = [datetime.fromisoformat(event.timestamp) for event in topic_events]
            time_span = (max(timestamps) - min(timestamps)).total_seconds()
            span_confidence = min(0.2, time_span / (7 * 24 * 3600))  # 1週間で0.2
        else:
            span_confidence = 0.0
        
        return count_confidence + span_confidence
    
    def analyze_interest_clusters(self) -> Dict[str, InterestCluster]:
        """興味クラスター分析"""
        print("[興味追跡] 🎯 興味クラスターを分析中...")
        
        clusters = {}
        
        # トピック間の関連性分析
        topic_correlations = self._calculate_topic_correlations()
        
        # クラスタリング実行
        cluster_groups = self._perform_interest_clustering(topic_correlations)
        
        # クラスター詳細分析
        for i, group in enumerate(cluster_groups):
            cluster_id = f"cluster_{i+1}"
            cluster = self._analyze_cluster_details(cluster_id, group)
            clusters[cluster_id] = cluster
        
        self.interest_clusters = clusters
        self._save_interest_clusters()
        
        print(f"[興味追跡] ✅ {len(clusters)}個の興味クラスターを発見")
        return clusters
    
    def _calculate_topic_correlations(self) -> Dict[Tuple[str, str], float]:
        """トピック間相関計算"""
        correlations = {}
        topics = list(self.interest_metrics.keys())
        
        for i in range(len(topics)):
            for j in range(i + 1, len(topics)):
                topic1, topic2 = topics[i], topics[j]
                correlation = self._calculate_pairwise_correlation(topic1, topic2)
                correlations[(topic1, topic2)] = correlation
        
        return correlations
    
    def _calculate_pairwise_correlation(self, topic1: str, topic2: str) -> float:
        """ペアワイズ相関計算"""
        # 同じセッション内での共起頻度
        co_occurrences = 0
        total_sessions = 0
        
        # セッションごとの共起分析
        session_topics = defaultdict(set)
        
        for event in self.engagement_events:
            # セッションIDの代わりに時間窓を使用（1時間以内）
            session_key = event.timestamp[:13]  # YYYY-MM-DDTHH
            session_topics[session_key].add(event.topic)
        
        for session, topics in session_topics.items():
            total_sessions += 1
            if topic1 in topics and topic2 in topics:
                co_occurrences += 1
        
        if total_sessions == 0:
            return 0.0
        
        return co_occurrences / total_sessions
    
    def _perform_interest_clustering(self, correlations: Dict[Tuple[str, str], float]) -> List[List[str]]:
        """興味クラスタリング実行"""
        # 簡易階層クラスタリング
        topics = list(self.interest_metrics.keys())
        
        if len(topics) <= 1:
            return [topics] if topics else []
        
        # 相関の高いペアを見つける
        clusters = [[topic] for topic in topics]
        correlation_threshold = 0.3
        
        merged = True
        while merged and len(clusters) > 1:
            merged = False
            best_merge = None
            best_correlation = 0
            
            for i in range(len(clusters)):
                for j in range(i + 1, len(clusters)):
                    # クラスター間の最大相関を計算
                    max_corr = 0
                    for topic1 in clusters[i]:
                        for topic2 in clusters[j]:
                            pair = (topic1, topic2) if topic1 < topic2 else (topic2, topic1)
                            corr = correlations.get(pair, 0)
                            max_corr = max(max_corr, corr)
                    
                    if max_corr > correlation_threshold and max_corr > best_correlation:
                        best_correlation = max_corr
                        best_merge = (i, j)
            
            if best_merge:
                i, j = best_merge
                # クラスターマージ
                clusters[i].extend(clusters[j])
                clusters.pop(j)
                merged = True
        
        return clusters
    
    def _analyze_cluster_details(self, cluster_id: str, topics: List[str]) -> InterestCluster:
        """クラスター詳細分析"""
        # 主要トピック（最高興味レベル）
        dominant_topic = max(topics, key=lambda t: self.interest_metrics.get(t, InterestMetrics(
            topic=t, current_level=0, engagement_score=0, frequency_score=0, 
            recency_score=0, depth_score=0, sentiment_score=0, trend_direction="stable",
            confidence=0, last_updated=""
        )).current_level)
        
        # クラスター強度（平均興味レベル）
        cluster_strength = mean([
            self.interest_metrics.get(topic, InterestMetrics(
                topic=topic, current_level=0, engagement_score=0, frequency_score=0,
                recency_score=0, depth_score=0, sentiment_score=0, trend_direction="stable",
                confidence=0, last_updated=""
            )).current_level 
            for topic in topics
        ]) if topics else 0.0
        
        # 出現パターン分析
        emergence_pattern = self._analyze_emergence_pattern(topics)
        
        # 成長予測
        predicted_growth = self._predict_cluster_growth(topics)
        
        # クラスター名生成
        cluster_name = self._generate_cluster_name(topics, dominant_topic)
        
        return InterestCluster(
            cluster_id=cluster_id,
            cluster_name=cluster_name,
            related_topics=topics,
            cluster_strength=cluster_strength,
            dominant_topic=dominant_topic,
            emergence_pattern=emergence_pattern,
            predicted_growth=predicted_growth
        )
    
    def _analyze_emergence_pattern(self, topics: List[str]) -> str:
        """出現パターン分析"""
        # 各トピックの初回言及時期分析
        first_mentions = {}
        
        for topic in topics:
            topic_events = [event for event in self.engagement_events if event.topic == topic]
            if topic_events:
                first_mentions[topic] = min(event.timestamp for event in topic_events)
        
        if len(first_mentions) <= 1:
            return "single_topic"
        
        # 時間的近接性分析
        timestamps = [datetime.fromisoformat(ts) for ts in first_mentions.values()]
        time_span = (max(timestamps) - min(timestamps)).total_seconds()
        
        if time_span < 3600:  # 1時間以内
            return "simultaneous"
        elif time_span < 86400:  # 1日以内
            return "same_day"
        elif time_span < 604800:  # 1週間以内
            return "gradual"
        else:
            return "distributed"
    
    def _predict_cluster_growth(self, topics: List[str]) -> float:
        """クラスター成長予測"""
        # トレンド方向に基づく成長予測
        growth_indicators = []
        
        for topic in topics:
            metrics = self.interest_metrics.get(topic)
            if metrics:
                if metrics.trend_direction == "increasing":
                    growth_indicators.append(0.8)
                elif metrics.trend_direction == "stable":
                    growth_indicators.append(0.5)
                else:  # decreasing
                    growth_indicators.append(0.2)
        
        return mean(growth_indicators) if growth_indicators else 0.5
    
    def _generate_cluster_name(self, topics: List[str], dominant_topic: str) -> str:
        """クラスター名生成"""
        if len(topics) == 1:
            return topics[0]
        elif len(topics) == 2:
            return f"{topics[0]}・{topics[1]}"
        else:
            return f"{dominant_topic}系クラスター"
    
    def get_interest_summary(self) -> Dict[str, Any]:
        """興味サマリー取得"""
        # 興味レベル順ソート
        sorted_interests = sorted(
            self.interest_metrics.items(),
            key=lambda x: x[1].current_level,
            reverse=True
        )
        
        # アクティブクラスター
        active_clusters = [
            cluster for cluster in self.interest_clusters.values()
            if cluster.cluster_strength > 0.5
        ]
        
        # 最近のエンゲージメント
        recent_events = [
            event for event in list(self.engagement_events)[-10:]
        ]
        
        return {
            "top_interests": [
                {
                    "topic": topic,
                    "level": metrics.current_level,
                    "trend": metrics.trend_direction,
                    "confidence": metrics.confidence
                }
                for topic, metrics in sorted_interests[:5]
            ],
            "active_clusters": [
                {
                    "name": cluster.cluster_name,
                    "strength": cluster.cluster_strength,
                    "topics": cluster.related_topics
                }
                for cluster in active_clusters
            ],
            "recent_activity": [
                {
                    "topic": event.topic,
                    "type": event.event_type,
                    "intensity": event.intensity,
                    "timestamp": event.timestamp
                }
                for event in recent_events
            ],
            "statistics": self.tracking_statistics
        }
    
    def decay_interest_scores(self):
        """興味スコア時間減衰"""
        print("[興味追跡] ⏰ 興味スコアの時間減衰を実行中...")
        
        current_time = datetime.now()
        
        for topic, metrics in self.interest_metrics.items():
            last_updated = datetime.fromisoformat(metrics.last_updated)
            days_elapsed = (current_time - last_updated).total_seconds() / 86400
            
            # 減衰適用
            decay_multiplier = self.decay_factor ** days_elapsed
            
            metrics.current_level *= decay_multiplier
            metrics.engagement_score *= decay_multiplier
            metrics.recency_score *= decay_multiplier
            
            # 最小値適用
            metrics.current_level = max(0.0, metrics.current_level)
            metrics.engagement_score = max(0.0, metrics.engagement_score)
            metrics.recency_score = max(0.0, metrics.recency_score)
        
        print("[興味追跡] ✅ 時間減衰完了")
    
    def _save_interest_metrics(self):
        """興味メトリクス保存"""
        try:
            metrics_data = {
                "metrics": {topic: asdict(metrics) for topic, metrics in self.interest_metrics.items()},
                "metadata": {
                    "total_topics": len(self.interest_metrics),
                    "last_updated": datetime.now().isoformat()
                }
            }
            
            with open(self.interest_metrics_path, 'w', encoding='utf-8') as f:
                json.dump(metrics_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[興味追跡] ⚠️ 興味メトリクス保存エラー: {e}")
    
    def _save_engagement_events(self):
        """エンゲージメントイベント保存"""
        try:
            events_data = {
                "events": [asdict(event) for event in self.engagement_events],
                "metadata": {
                    "total_events": len(self.engagement_events),
                    "last_updated": datetime.now().isoformat()
                }
            }
            
            with open(self.engagement_events_path, 'w', encoding='utf-8') as f:
                json.dump(events_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[興味追跡] ⚠️ エンゲージメントイベント保存エラー: {e}")
    
    def _save_interest_clusters(self):
        """興味クラスター保存"""
        try:
            clusters_data = {
                "clusters": {cid: asdict(cluster) for cid, cluster in self.interest_clusters.items()},
                "metadata": {
                    "total_clusters": len(self.interest_clusters),
                    "last_updated": datetime.now().isoformat()
                }
            }
            
            with open(self.interest_clusters_path, 'w', encoding='utf-8') as f:
                json.dump(clusters_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[興味追跡] ⚠️ 興味クラスター保存エラー: {e}")
    
    def save_all_data(self):
        """全データ保存"""
        self._save_interest_metrics()
        self._save_engagement_events()
        self._save_interest_clusters()
        
        # 統計更新
        self.tracking_statistics.update({
            "total_topics_tracked": len(self.interest_metrics),
            "total_engagement_events": len(self.engagement_events),
            "active_clusters": len([c for c in self.interest_clusters.values() if c.cluster_strength > 0.5]),
            "last_update": datetime.now().isoformat()
        })
    
    def get_tracking_statistics(self) -> Dict[str, Any]:
        """追跡統計情報取得"""
        return dict(self.tracking_statistics)
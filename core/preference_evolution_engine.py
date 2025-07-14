#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
好み進化エンジン - Phase 2D実装
ユーザーの好み変化予測・新興味領域発見・個人化レベル継続向上
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from datetime import datetime, timedelta
import numpy as np
from statistics import mean, median, stdev
import hashlib

# プロジェクトルートをパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 関連システム
try:
    from core.user_interest_tracker import UserInterestTracker
    from core.conversation_history_analyzer import ConversationHistoryAnalyzer
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False

# Windowsパス設定
if os.name == 'nt':
    DATA_DIR = Path("D:/setsuna_bot/data")
    EVOLUTION_CACHE_DIR = Path("D:/setsuna_bot/preference_evolution_cache")
else:
    DATA_DIR = Path("/mnt/d/setsuna_bot/data")
    EVOLUTION_CACHE_DIR = Path("/mnt/d/setsuna_bot/preference_evolution_cache")

EVOLUTION_CACHE_DIR.mkdir(parents=True, exist_ok=True)

@dataclass
class PreferenceEvolution:
    """好み進化データクラス"""
    evolution_id: str
    topic: str
    evolution_type: str          # "emerging", "strengthening", "weakening", "shifting"
    confidence: float
    timeline: List[Dict[str, Any]]  # 進化の時系列
    trigger_events: List[str]    # 進化のきっかけイベント
    prediction_accuracy: float  # 予測精度
    last_updated: str

@dataclass
class EmergingInterest:
    """新興興味データクラス"""
    interest_id: str
    topic: str
    emergence_strength: float   # 出現強度
    discovery_context: Dict[str, Any]  # 発見コンテキスト
    growth_trajectory: List[float]     # 成長軌跡
    related_existing_interests: List[str]  # 関連する既存興味
    emergence_triggers: List[str]      # 出現トリガー
    predicted_potential: float         # 将来性予測
    discovered_at: str

@dataclass
class PersonalizationInsight:
    """個人化インサイトデータクラス"""
    insight_id: str
    insight_type: str           # "pattern", "preference", "behavior", "recommendation"
    description: str
    confidence: float
    actionable_suggestions: List[str]  # 実行可能な提案
    impact_prediction: float    # インパクト予測
    validation_status: str      # "pending", "confirmed", "rejected"
    created_at: str

class PreferenceEvolutionEngine:
    """好み進化エンジンクラス"""
    
    def __init__(self):
        """初期化"""
        # データパス
        self.preference_evolutions_path = EVOLUTION_CACHE_DIR / "preference_evolutions.json"
        self.emerging_interests_path = EVOLUTION_CACHE_DIR / "emerging_interests.json"
        self.personalization_insights_path = EVOLUTION_CACHE_DIR / "personalization_insights.json"
        self.evolution_models_path = EVOLUTION_CACHE_DIR / "evolution_models.json"
        
        # 依存システム
        if DEPENDENCIES_AVAILABLE:
            self.interest_tracker = UserInterestTracker()
            self.history_analyzer = ConversationHistoryAnalyzer()
        else:
            self.interest_tracker = None
            self.history_analyzer = None
            print("[好み進化] ⚠️ 依存システムが利用できません")
        
        # データ
        self.preference_evolutions = {}
        self.emerging_interests = {}
        self.personalization_insights = {}
        self.evolution_models = {}
        
        # 進化検出パラメータ
        self.evolution_threshold = 0.2      # 進化検出閾値
        self.emergence_threshold = 0.15     # 新興検出閾値
        self.confidence_threshold = 0.6     # 信頼度閾値
        self.prediction_window = 30         # 予測ウィンドウ（日）
        
        # 進化パターン定義
        self.evolution_patterns = self._build_evolution_patterns()
        self.emergence_indicators = self._build_emergence_indicators()
        self.personalization_factors = self._build_personalization_factors()
        
        # 統計情報
        self.evolution_statistics = {
            "total_evolutions_tracked": 0,
            "emerging_interests_discovered": 0,
            "insights_generated": 0,
            "prediction_accuracy": 0.0,
            "last_analysis": None
        }
        
        self._load_existing_data()
        print("[好み進化] ✅ 好み進化エンジン初期化完了")
    
    def _build_evolution_patterns(self) -> Dict[str, Dict[str, Any]]:
        """進化パターン構築"""
        return {
            "strengthening": {
                "indicators": [
                    "興味レベル継続上昇",
                    "エンゲージメント頻度増加",
                    "深掘り質問増加",
                    "関連トピック拡張"
                ],
                "threshold": 0.3,
                "duration_days": 7
            },
            "weakening": {
                "indicators": [
                    "言及頻度減少",
                    "エンゲージメント低下",
                    "関心表現の消失",
                    "他トピックへの移行"
                ],
                "threshold": -0.2,
                "duration_days": 14
            },
            "shifting": {
                "indicators": [
                    "関連領域への移動",
                    "新しい切り口での言及",
                    "視点の変化",
                    "アプローチの変更"
                ],
                "threshold": 0.25,
                "duration_days": 10
            },
            "emerging": {
                "indicators": [
                    "新規トピック初回言及",
                    "急激な興味レベル上昇",
                    "集中的な質問",
                    "関連検索行動"
                ],
                "threshold": 0.4,
                "duration_days": 3
            }
        }
    
    def _build_emergence_indicators(self) -> Dict[str, List[str]]:
        """新興指標構築"""
        return {
            "discovery_signals": [
                "初めて知った", "新しい発見", "こんなのがあるんだ", "興味深い",
                "面白そう", "やってみたい", "学んでみたい", "挑戦したい"
            ],
            "exploration_signals": [
                "もっと詳しく", "他にもある?", "似たようなの", "関連する",
                "どんな種類", "バリエーション", "応用", "発展"
            ],
            "commitment_signals": [
                "続けたい", "深く学びたい", "極めたい", "専門的に",
                "本格的に", "真剣に", "集中して", "時間をかけて"
            ]
        }
    
    def _build_personalization_factors(self) -> Dict[str, Dict[str, Any]]:
        """個人化要因構築"""
        return {
            "temporal_patterns": {
                "description": "時間的活動パターン",
                "weight": 0.2,
                "indicators": ["activity_hours", "session_frequency", "duration_preferences"]
            },
            "content_preferences": {
                "description": "コンテンツ好み傾向",
                "weight": 0.3,
                "indicators": ["topic_preferences", "complexity_level", "format_preferences"]
            },
            "interaction_style": {
                "description": "対話スタイル",
                "weight": 0.25,
                "indicators": ["question_patterns", "engagement_depth", "exploration_tendency"]
            },
            "learning_patterns": {
                "description": "学習パターン",
                "weight": 0.25,
                "indicators": ["knowledge_acquisition", "skill_progression", "interest_evolution"]
            }
        }
    
    def _load_existing_data(self):
        """既存データロード"""
        # 好み進化
        try:
            if self.preference_evolutions_path.exists():
                with open(self.preference_evolutions_path, 'r', encoding='utf-8') as f:
                    evolutions_data = json.load(f)
                    self.preference_evolutions = {
                        eid: PreferenceEvolution(**evolution) 
                        for eid, evolution in evolutions_data.get("evolutions", {}).items()
                    }
                print(f"[好み進化] 📊 {len(self.preference_evolutions)}個の好み進化をロード")
        except Exception as e:
            print(f"[好み進化] ⚠️ 好み進化ロードエラー: {e}")
        
        # 新興興味
        try:
            if self.emerging_interests_path.exists():
                with open(self.emerging_interests_path, 'r', encoding='utf-8') as f:
                    interests_data = json.load(f)
                    self.emerging_interests = {
                        iid: EmergingInterest(**interest) 
                        for iid, interest in interests_data.get("interests", {}).items()
                    }
                print(f"[好み進化] 📊 {len(self.emerging_interests)}個の新興興味をロード")
        except Exception as e:
            print(f"[好み進化] ⚠️ 新興興味ロードエラー: {e}")
        
        # 個人化インサイト
        try:
            if self.personalization_insights_path.exists():
                with open(self.personalization_insights_path, 'r', encoding='utf-8') as f:
                    insights_data = json.load(f)
                    self.personalization_insights = {
                        iid: PersonalizationInsight(**insight) 
                        for iid, insight in insights_data.get("insights", {}).items()
                    }
                print(f"[好み進化] 📊 {len(self.personalization_insights)}個の個人化インサイトをロード")
        except Exception as e:
            print(f"[好み進化] ⚠️ 個人化インサイトロードエラー: {e}")
    
    def analyze_preference_evolution(self) -> Dict[str, PreferenceEvolution]:
        """好み進化分析"""
        print("[好み進化] 📈 好み進化を分析中...")
        
        if not self.interest_tracker:
            print("[好み進化] ⚠️ 興味追跡システムが利用できません")
            return {}
        
        evolutions = {}
        
        # 各トピックの進化分析
        for topic, metrics in self.interest_tracker.interest_metrics.items():
            evolution = self._analyze_topic_evolution(topic, metrics)
            if evolution:
                evolutions[evolution.evolution_id] = evolution
        
        self.preference_evolutions = evolutions
        self._save_preference_evolutions()
        
        print(f"[好み進化] ✅ {len(evolutions)}個の好み進化を検出")
        return evolutions
    
    def _analyze_topic_evolution(self, topic: str, metrics) -> Optional[PreferenceEvolution]:
        """トピック進化分析"""
        # 時系列データ取得
        timeline_data = self._get_topic_timeline(topic)
        
        if len(timeline_data) < 3:  # 最小データ量
            return None
        
        # 進化タイプ検出
        evolution_type = self._detect_evolution_type(timeline_data, metrics)
        
        if evolution_type == "stable":  # 進化なし
            return None
        
        # 信頼度計算
        confidence = self._calculate_evolution_confidence(timeline_data, evolution_type)
        
        if confidence < self.confidence_threshold:
            return None
        
        # トリガーイベント抽出
        trigger_events = self._extract_trigger_events(topic, timeline_data)
        
        # 予測精度評価
        prediction_accuracy = self._evaluate_prediction_accuracy(timeline_data, evolution_type)
        
        evolution_id = f"evolution_{topic}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return PreferenceEvolution(
            evolution_id=evolution_id,
            topic=topic,
            evolution_type=evolution_type,
            confidence=confidence,
            timeline=timeline_data,
            trigger_events=trigger_events,
            prediction_accuracy=prediction_accuracy,
            last_updated=datetime.now().isoformat()
        )
    
    def _get_topic_timeline(self, topic: str) -> List[Dict[str, Any]]:
        """トピック時系列データ取得"""
        timeline = []
        
        if not self.interest_tracker:
            return timeline
        
        # エンゲージメントイベントから時系列構築
        topic_events = [
            event for event in self.interest_tracker.engagement_events 
            if event.topic == topic
        ]
        
        # 日次集計
        daily_data = defaultdict(list)
        for event in topic_events:
            date_key = event.timestamp[:10]  # YYYY-MM-DD
            daily_data[date_key].append(event)
        
        # 時系列データ構築
        for date, events in sorted(daily_data.items()):
            daily_intensity = mean([event.intensity for event in events])
            daily_frequency = len(events)
            
            timeline.append({
                "date": date,
                "intensity": daily_intensity,
                "frequency": daily_frequency,
                "event_types": list(set(event.event_type for event in events))
            })
        
        return timeline
    
    def _detect_evolution_type(self, timeline_data: List[Dict], metrics) -> str:
        """進化タイプ検出"""
        if len(timeline_data) < 3:
            return "stable"
        
        # 直近データとの比較
        recent_data = timeline_data[-3:]
        early_data = timeline_data[:3]
        
        recent_avg_intensity = mean([data["intensity"] for data in recent_data])
        early_avg_intensity = mean([data["intensity"] for data in early_data])
        
        intensity_change = recent_avg_intensity - early_avg_intensity
        
        # パターンマッチング
        for pattern_type, pattern_config in self.evolution_patterns.items():
            threshold = pattern_config["threshold"]
            
            if pattern_type == "strengthening" and intensity_change > threshold:
                return "strengthening"
            elif pattern_type == "weakening" and intensity_change < threshold:
                return "weakening"
            elif pattern_type == "emerging" and self._is_emerging_pattern(timeline_data):
                return "emerging"
            elif pattern_type == "shifting" and self._is_shifting_pattern(timeline_data):
                return "shifting"
        
        return "stable"
    
    def _is_emerging_pattern(self, timeline_data: List[Dict]) -> bool:
        """新興パターン判定"""
        if len(timeline_data) < 2:
            return False
        
        # 最初の方のデータが低く、後半で急上昇
        first_half = timeline_data[:len(timeline_data)//2]
        second_half = timeline_data[len(timeline_data)//2:]
        
        first_avg = mean([data["intensity"] for data in first_half])
        second_avg = mean([data["intensity"] for data in second_half])
        
        return first_avg < 0.3 and second_avg > 0.6
    
    def _is_shifting_pattern(self, timeline_data: List[Dict]) -> bool:
        """変化パターン判定"""
        if len(timeline_data) < 3:
            return False
        
        # イベントタイプの変化を検査
        early_types = set()
        late_types = set()
        
        for data in timeline_data[:len(timeline_data)//2]:
            early_types.update(data["event_types"])
        
        for data in timeline_data[len(timeline_data)//2:]:
            late_types.update(data["event_types"])
        
        # イベントタイプの変化度
        overlap = len(early_types.intersection(late_types))
        total_unique = len(early_types.union(late_types))
        
        change_ratio = 1 - (overlap / total_unique if total_unique > 0 else 1)
        
        return change_ratio > 0.5
    
    def _calculate_evolution_confidence(self, timeline_data: List[Dict], evolution_type: str) -> float:
        """進化信頼度計算"""
        confidence = 0.0
        
        # データ量による信頼度
        data_confidence = min(0.3, len(timeline_data) / 10)
        confidence += data_confidence
        
        # 一貫性による信頼度
        intensities = [data["intensity"] for data in timeline_data]
        if len(intensities) > 1:
            consistency = 1 - (stdev(intensities) if len(intensities) > 1 else 0)
            consistency_confidence = consistency * 0.3
            confidence += consistency_confidence
        
        # 進化タイプ特有の信頼度
        type_specific_confidence = self._calculate_type_specific_confidence(
            timeline_data, evolution_type
        )
        confidence += type_specific_confidence
        
        return min(1.0, confidence)
    
    def _calculate_type_specific_confidence(self, timeline_data: List[Dict], evolution_type: str) -> float:
        """タイプ特有信頼度計算"""
        if evolution_type == "strengthening":
            # 増加トレンドの一貫性
            intensities = [data["intensity"] for data in timeline_data]
            increasing_count = sum(
                1 for i in range(1, len(intensities)) 
                if intensities[i] > intensities[i-1]
            )
            return (increasing_count / max(1, len(intensities) - 1)) * 0.4
        
        elif evolution_type == "emerging":
            # 急激な上昇の明確さ
            if len(timeline_data) >= 2:
                start_intensity = timeline_data[0]["intensity"]
                end_intensity = timeline_data[-1]["intensity"]
                emergence_strength = end_intensity - start_intensity
                return min(0.4, emergence_strength)
        
        elif evolution_type == "weakening":
            # 減少トレンドの一貫性
            intensities = [data["intensity"] for data in timeline_data]
            decreasing_count = sum(
                1 for i in range(1, len(intensities)) 
                if intensities[i] < intensities[i-1]
            )
            return (decreasing_count / max(1, len(intensities) - 1)) * 0.4
        
        return 0.2  # デフォルト
    
    def _extract_trigger_events(self, topic: str, timeline_data: List[Dict]) -> List[str]:
        """トリガーイベント抽出"""
        triggers = []
        
        # 急激な変化点を検出
        for i in range(1, len(timeline_data)):
            prev_data = timeline_data[i-1]
            curr_data = timeline_data[i]
            
            intensity_change = curr_data["intensity"] - prev_data["intensity"]
            
            if abs(intensity_change) > 0.3:  # 大きな変化
                trigger_description = f"強度変化: {intensity_change:.2f} ({prev_data['date']} -> {curr_data['date']})"
                triggers.append(trigger_description)
        
        # 新しいイベントタイプの出現
        seen_types = set()
        for data in timeline_data:
            current_types = set(data["event_types"])
            new_types = current_types - seen_types
            
            if new_types:
                triggers.append(f"新イベントタイプ: {', '.join(new_types)} ({data['date']})")
            
            seen_types.update(current_types)
        
        return triggers[:5]  # 最大5つ
    
    def _evaluate_prediction_accuracy(self, timeline_data: List[Dict], evolution_type: str) -> float:
        """予測精度評価"""
        # 簡易実装：進化タイプの一貫性に基づく
        if len(timeline_data) < 3:
            return 0.5
        
        # 前半データで予測し後半データで検証
        split_point = len(timeline_data) // 2
        prediction_data = timeline_data[:split_point]
        validation_data = timeline_data[split_point:]
        
        # 予測トレンド
        pred_trend = self._detect_evolution_type(prediction_data, None)
        
        # 検証トレンド
        val_trend = self._detect_evolution_type(validation_data, None)
        
        # 一致度
        if pred_trend == val_trend:
            return 0.9
        elif pred_trend in ["strengthening", "emerging"] and val_trend in ["strengthening", "emerging"]:
            return 0.7
        elif pred_trend in ["weakening"] and val_trend in ["weakening"]:
            return 0.7
        else:
            return 0.3
    
    def discover_emerging_interests(self) -> Dict[str, EmergingInterest]:
        """新興興味発見"""
        print("[好み進化] 🔍 新興興味を発見中...")
        
        if not self.interest_tracker:
            print("[好み進化] ⚠️ 興味追跡システムが利用できません")
            return {}
        
        emerging = {}
        
        # 最近のエンゲージメントイベント分析
        recent_cutoff = datetime.now() - timedelta(days=7)
        recent_events = [
            event for event in self.interest_tracker.engagement_events
            if datetime.fromisoformat(event.timestamp) > recent_cutoff
        ]
        
        # トピック別新興度評価
        topic_emergence = defaultdict(list)
        for event in recent_events:
            topic_emergence[event.topic].append(event)
        
        for topic, events in topic_emergence.items():
            emergence = self._evaluate_topic_emergence(topic, events)
            if emergence:
                emerging[emergence.interest_id] = emergence
        
        self.emerging_interests = emerging
        self._save_emerging_interests()
        
        print(f"[好み進化] ✅ {len(emerging)}個の新興興味を発見")
        return emerging
    
    def _evaluate_topic_emergence(self, topic: str, events: List) -> Optional[EmergingInterest]:
        """トピック新興度評価"""
        if len(events) < 2:
            return None
        
        # 新興強度計算
        emergence_strength = self._calculate_emergence_strength(topic, events)
        
        if emergence_strength < self.emergence_threshold:
            return None
        
        # 発見コンテキスト
        discovery_context = self._build_discovery_context(events)
        
        # 成長軌跡
        growth_trajectory = self._calculate_growth_trajectory(events)
        
        # 関連既存興味
        related_interests = self._find_related_existing_interests(topic)
        
        # 出現トリガー
        emergence_triggers = self._identify_emergence_triggers(events)
        
        # 将来性予測
        predicted_potential = self._predict_interest_potential(topic, events)
        
        interest_id = f"emerging_{topic}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return EmergingInterest(
            interest_id=interest_id,
            topic=topic,
            emergence_strength=emergence_strength,
            discovery_context=discovery_context,
            growth_trajectory=growth_trajectory,
            related_existing_interests=related_interests,
            emergence_triggers=emergence_triggers,
            predicted_potential=predicted_potential,
            discovered_at=datetime.now().isoformat()
        )
    
    def _calculate_emergence_strength(self, topic: str, events: List) -> float:
        """新興強度計算"""
        # 短期間での急激な増加
        time_span = (
            datetime.fromisoformat(events[-1].timestamp) - 
            datetime.fromisoformat(events[0].timestamp)
        ).total_seconds() / 86400  # 日数
        
        if time_span == 0:
            time_span = 1
        
        # イベント密度
        event_density = len(events) / time_span
        
        # 平均強度
        avg_intensity = mean([event.intensity for event in events])
        
        # イベントタイプ多様性
        unique_types = len(set(event.event_type for event in events))
        type_diversity = min(1.0, unique_types / 3)  # 最大3タイプ
        
        # 総合新興強度
        emergence_strength = (
            min(1.0, event_density / 2) * 0.4 +  # 密度（1日2回で最大）
            avg_intensity * 0.4 +                 # 強度
            type_diversity * 0.2                  # 多様性
        )
        
        return emergence_strength
    
    def _build_discovery_context(self, events: List) -> Dict[str, Any]:
        """発見コンテキスト構築"""
        return {
            "first_mention": events[0].timestamp,
            "trigger_context": events[0].context[:100],
            "initial_event_type": events[0].event_type,
            "discovery_intensity": events[0].intensity,
            "total_events": len(events),
            "event_types": list(set(event.event_type for event in events))
        }
    
    def _calculate_growth_trajectory(self, events: List) -> List[float]:
        """成長軌跡計算"""
        # 時系列での強度変化
        trajectory = []
        
        # 時間順ソート
        sorted_events = sorted(events, key=lambda e: e.timestamp)
        
        # 累積強度
        cumulative_intensity = 0
        for event in sorted_events:
            cumulative_intensity += event.intensity
            trajectory.append(cumulative_intensity / len(trajectory) if trajectory else event.intensity)
        
        return trajectory
    
    def _find_related_existing_interests(self, topic: str) -> List[str]:
        """関連既存興味検索"""
        if not self.interest_tracker:
            return []
        
        related = []
        
        # 共起分析
        for existing_topic in self.interest_tracker.interest_metrics.keys():
            if existing_topic != topic:
                correlation = self._calculate_topic_correlation(topic, existing_topic)
                if correlation > 0.3:
                    related.append(existing_topic)
        
        return related[:3]  # 上位3つ
    
    def _calculate_topic_correlation(self, topic1: str, topic2: str) -> float:
        """トピック相関計算"""
        if not self.interest_tracker:
            return 0.0
        
        # 同一セッション内共起率
        session_with_topic1 = set()
        session_with_topic2 = set()
        
        for event in self.interest_tracker.engagement_events:
            session_key = event.timestamp[:13]  # 時間セッション
            
            if event.topic == topic1:
                session_with_topic1.add(session_key)
            elif event.topic == topic2:
                session_with_topic2.add(session_key)
        
        if not session_with_topic1 or not session_with_topic2:
            return 0.0
        
        intersection = len(session_with_topic1.intersection(session_with_topic2))
        union = len(session_with_topic1.union(session_with_topic2))
        
        return intersection / union if union > 0 else 0.0
    
    def _identify_emergence_triggers(self, events: List) -> List[str]:
        """出現トリガー識別"""
        triggers = []
        
        # 初回イベント分析
        first_event = events[0]
        trigger_context = first_event.context.lower()
        
        # 発見シグナル検出
        for signal_type, signals in self.emergence_indicators.items():
            for signal in signals:
                if signal in trigger_context:
                    triggers.append(f"{signal_type}: {signal}")
        
        # イベントタイプ遷移
        if len(events) > 1:
            type_sequence = [event.event_type for event in events]
            triggers.append(f"イベント遷移: {' -> '.join(type_sequence[:3])}")
        
        return triggers[:3]
    
    def _predict_interest_potential(self, topic: str, events: List) -> float:
        """興味将来性予測"""
        # 成長速度
        if len(events) >= 2:
            time_span = (
                datetime.fromisoformat(events[-1].timestamp) - 
                datetime.fromisoformat(events[0].timestamp)
            ).total_seconds() / 86400
            
            growth_rate = len(events) / max(1, time_span)
        else:
            growth_rate = 1.0
        
        # 強度トレンド
        intensities = [event.intensity for event in events]
        intensity_trend = (intensities[-1] - intensities[0]) if len(intensities) > 1 else 0
        
        # 多様性
        type_diversity = len(set(event.event_type for event in events)) / 4  # 正規化
        
        # 総合将来性
        potential = (
            min(1.0, growth_rate / 3) * 0.4 +  # 成長率
            max(0, intensity_trend) * 0.4 +    # 強度向上
            type_diversity * 0.2                # 多様性
        )
        
        return min(1.0, potential)
    
    def generate_personalization_insights(self) -> Dict[str, PersonalizationInsight]:
        """個人化インサイト生成"""
        print("[好み進化] 💡 個人化インサイトを生成中...")
        
        insights = {}
        
        # パターンインサイト
        pattern_insights = self._generate_pattern_insights()
        insights.update(pattern_insights)
        
        # 好みインサイト
        preference_insights = self._generate_preference_insights()
        insights.update(preference_insights)
        
        # 行動インサイト
        behavior_insights = self._generate_behavior_insights()
        insights.update(behavior_insights)
        
        # 推薦インサイト
        recommendation_insights = self._generate_recommendation_insights()
        insights.update(recommendation_insights)
        
        self.personalization_insights = insights
        self._save_personalization_insights()
        
        print(f"[好み進化] ✅ {len(insights)}個の個人化インサイトを生成")
        return insights
    
    def _generate_pattern_insights(self) -> Dict[str, PersonalizationInsight]:
        """パターンインサイト生成"""
        insights = {}
        
        # 活動時間パターン
        if self.interest_tracker and self.interest_tracker.engagement_events:
            hour_activity = defaultdict(int)
            
            for event in self.interest_tracker.engagement_events:
                try:
                    hour = datetime.fromisoformat(event.timestamp).hour
                    hour_activity[hour] += 1
                except:
                    continue
            
            if hour_activity:
                peak_hour = max(hour_activity.items(), key=lambda x: x[1])[0]
                
                insight_id = f"pattern_temporal_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                insights[insight_id] = PersonalizationInsight(
                    insight_id=insight_id,
                    insight_type="pattern",
                    description=f"最も活発な時間帯は{peak_hour}時頃です",
                    confidence=0.8,
                    actionable_suggestions=[
                        f"{peak_hour}時頃に新しいコンテンツを提案",
                        "集中的な学習セッションを同時間帯に設定",
                        "重要な情報は活動ピーク時に提供"
                    ],
                    impact_prediction=0.7,
                    validation_status="pending",
                    created_at=datetime.now().isoformat()
                )
        
        return insights
    
    def _generate_preference_insights(self) -> Dict[str, PersonalizationInsight]:
        """好みインサイト生成"""
        insights = {}
        
        if self.interest_tracker:
            # 興味レベル上位トピック
            top_interests = sorted(
                self.interest_tracker.interest_metrics.items(),
                key=lambda x: x[1].current_level,
                reverse=True
            )[:3]
            
            if top_interests:
                top_topics = [topic for topic, _ in top_interests]
                
                insight_id = f"preference_top_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                insights[insight_id] = PersonalizationInsight(
                    insight_id=insight_id,
                    insight_type="preference",
                    description=f"主要興味分野: {', '.join(top_topics)}",
                    confidence=0.9,
                    actionable_suggestions=[
                        f"{top_topics[0]}に関連する新しい情報を優先表示",
                        "興味分野を組み合わせたコンテンツ提案",
                        "専門性を深める学習パスを提供"
                    ],
                    impact_prediction=0.8,
                    validation_status="pending",
                    created_at=datetime.now().isoformat()
                )
        
        return insights
    
    def _generate_behavior_insights(self) -> Dict[str, PersonalizationInsight]:
        """行動インサイト生成"""
        insights = {}
        
        if self.history_analyzer and self.history_analyzer.user_behavior_profile:
            profile = self.history_analyzer.user_behavior_profile
            
            # 対話スタイル分析
            dominant_style = max(profile.conversation_style.items(), key=lambda x: x[1])
            
            insight_id = f"behavior_style_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            insights[insight_id] = PersonalizationInsight(
                insight_id=insight_id,
                insight_type="behavior",
                description=f"主要な対話スタイル: {dominant_style[0]}",
                confidence=0.75,
                actionable_suggestions=[
                    f"{dominant_style[0]}スタイルに合わせた情報提示",
                    "応答パターンの個人化",
                    "質問形式の最適化"
                ],
                impact_prediction=0.6,
                validation_status="pending",
                created_at=datetime.now().isoformat()
            )
        
        return insights
    
    def _generate_recommendation_insights(self) -> Dict[str, PersonalizationInsight]:
        """推薦インサイト生成"""
        insights = {}
        
        # 新興興味に基づく推薦
        for interest in self.emerging_interests.values():
            if interest.predicted_potential > 0.7:
                insight_id = f"recommendation_emerging_{interest.topic}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                insights[insight_id] = PersonalizationInsight(
                    insight_id=insight_id,
                    insight_type="recommendation",
                    description=f"新興興味「{interest.topic}」の成長支援",
                    confidence=interest.predicted_potential,
                    actionable_suggestions=[
                        f"{interest.topic}の基礎知識コンテンツ提供",
                        "関連する既存興味との接続点提示",
                        "段階的な学習パス設計"
                    ],
                    impact_prediction=interest.predicted_potential,
                    validation_status="pending",
                    created_at=datetime.now().isoformat()
                )
        
        return insights
    
    def predict_future_preferences(self, prediction_days: int = 30) -> Dict[str, Any]:
        """将来好み予測"""
        print(f"[好み進化] 🔮 {prediction_days}日後の好みを予測中...")
        
        predictions = {
            "timeframe_days": prediction_days,
            "predicted_interests": {},
            "emerging_candidates": [],
            "declining_candidates": [],
            "stable_interests": [],
            "confidence": 0.0
        }
        
        if not self.interest_tracker:
            return predictions
        
        # 各興味の将来予測
        for topic, metrics in self.interest_tracker.interest_metrics.items():
            future_level = self._predict_topic_future_level(topic, metrics, prediction_days)
            
            predictions["predicted_interests"][topic] = {
                "current_level": metrics.current_level,
                "predicted_level": future_level,
                "change": future_level - metrics.current_level,
                "trend": metrics.trend_direction
            }
            
            # カテゴリ分類
            change = future_level - metrics.current_level
            if change > 0.2:
                predictions["emerging_candidates"].append(topic)
            elif change < -0.2:
                predictions["declining_candidates"].append(topic)
            else:
                predictions["stable_interests"].append(topic)
        
        # 全体信頼度
        predictions["confidence"] = self._calculate_prediction_confidence()
        
        print(f"[好み進化] ✅ 予測完了 (信頼度: {predictions['confidence']:.2f})")
        return predictions
    
    def _predict_topic_future_level(self, topic: str, metrics, prediction_days: int) -> float:
        """トピック将来レベル予測"""
        current_level = metrics.current_level
        trend = metrics.trend_direction
        
        # トレンドベース予測
        if trend == "increasing":
            growth_rate = 0.01 * prediction_days  # 1日1%成長
            future_level = min(1.0, current_level + growth_rate)
        elif trend == "decreasing":
            decay_rate = 0.005 * prediction_days  # 1日0.5%減衰
            future_level = max(0.0, current_level - decay_rate)
        else:  # stable
            # 自然減衰
            decay_factor = 0.98 ** prediction_days
            future_level = current_level * decay_factor
        
        return future_level
    
    def _calculate_prediction_confidence(self) -> float:
        """予測信頼度計算"""
        # データ量による信頼度
        data_confidence = 0.0
        if self.interest_tracker:
            event_count = len(self.interest_tracker.engagement_events)
            data_confidence = min(0.4, event_count / 100)
        
        # 進化パターンによる信頼度
        pattern_confidence = min(0.3, len(self.preference_evolutions) / 10)
        
        # 一貫性による信頼度
        consistency_confidence = 0.3  # 基本値
        
        return data_confidence + pattern_confidence + consistency_confidence
    
    def _save_preference_evolutions(self):
        """好み進化保存"""
        try:
            evolutions_data = {
                "evolutions": {eid: asdict(evolution) for eid, evolution in self.preference_evolutions.items()},
                "metadata": {
                    "total_evolutions": len(self.preference_evolutions),
                    "last_updated": datetime.now().isoformat()
                }
            }
            
            with open(self.preference_evolutions_path, 'w', encoding='utf-8') as f:
                json.dump(evolutions_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[好み進化] ⚠️ 好み進化保存エラー: {e}")
    
    def _save_emerging_interests(self):
        """新興興味保存"""
        try:
            interests_data = {
                "interests": {iid: asdict(interest) for iid, interest in self.emerging_interests.items()},
                "metadata": {
                    "total_interests": len(self.emerging_interests),
                    "last_updated": datetime.now().isoformat()
                }
            }
            
            with open(self.emerging_interests_path, 'w', encoding='utf-8') as f:
                json.dump(interests_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[好み進化] ⚠️ 新興興味保存エラー: {e}")
    
    def _save_personalization_insights(self):
        """個人化インサイト保存"""
        try:
            insights_data = {
                "insights": {iid: asdict(insight) for iid, insight in self.personalization_insights.items()},
                "metadata": {
                    "total_insights": len(self.personalization_insights),
                    "last_updated": datetime.now().isoformat()
                }
            }
            
            with open(self.personalization_insights_path, 'w', encoding='utf-8') as f:
                json.dump(insights_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[好み進化] ⚠️ 個人化インサイト保存エラー: {e}")
    
    def perform_comprehensive_evolution_analysis(self) -> Dict[str, Any]:
        """包括的進化分析実行"""
        print("[好み進化] 🔬 包括的進化分析を実行中...")
        
        # 各種分析実行
        evolutions = self.analyze_preference_evolution()
        emerging = self.discover_emerging_interests()
        insights = self.generate_personalization_insights()
        predictions = self.predict_future_preferences()
        
        # 統計更新
        self.evolution_statistics.update({
            "total_evolutions_tracked": len(evolutions),
            "emerging_interests_discovered": len(emerging),
            "insights_generated": len(insights),
            "prediction_accuracy": predictions.get("confidence", 0.0),
            "last_analysis": datetime.now().isoformat()
        })
        
        analysis_result = {
            "evolutions": evolutions,
            "emerging_interests": emerging,
            "insights": insights,
            "predictions": predictions,
            "statistics": self.evolution_statistics
        }
        
        print("[好み進化] ✅ 包括的進化分析完了")
        return analysis_result
    
    def get_evolution_summary(self) -> Dict[str, Any]:
        """進化サマリー取得"""
        return {
            "current_evolutions": len(self.preference_evolutions),
            "emerging_interests": len(self.emerging_interests),
            "active_insights": len([
                i for i in self.personalization_insights.values() 
                if i.validation_status != "rejected"
            ]),
            "statistics": self.evolution_statistics,
            "top_emerging": [
                {
                    "topic": interest.topic,
                    "strength": interest.emergence_strength,
                    "potential": interest.predicted_potential
                }
                for interest in sorted(
                    self.emerging_interests.values(),
                    key=lambda x: x.predicted_potential,
                    reverse=True
                )[:3]
            ]
        }
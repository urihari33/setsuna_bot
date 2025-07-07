#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
せつな協働記憶システム
ユーザーとの作業スタイル・成功パターン・協働履歴を学習・管理
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

class CollaborationMemory:
    """せつなの協働記憶管理システム"""
    
    def __init__(self, memory_mode="normal"):
        """
        協働記憶システム初期化
        
        Args:
            memory_mode: "normal" または "test"
        """
        self.memory_mode = memory_mode
        
        # 環境に応じてパスを決定
        if os.path.exists("/mnt/d/setsuna_bot"):
            base_path = Path("/mnt/d/setsuna_bot")
        else:
            base_path = Path("D:/setsuna_bot")
        
        if memory_mode == "test":
            # テストモード: 一時ファイル
            import tempfile
            self.memory_file = base_path / "temp" / f"test_collaboration_memory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            os.makedirs(self.memory_file.parent, exist_ok=True)
        else:
            # 通常モード: 永続ファイル
            self.memory_file = base_path / "enhanced_memory" / "collaboration_memory.json"
            os.makedirs(self.memory_file.parent, exist_ok=True)
        
        # 協働記憶データ構造
        self.collaboration_data = {
            "work_patterns": [],           # 作業パターン分析
            "success_patterns": [],        # 成功パターン記録
            "communication_styles": [],    # コミュニケーションスタイル
            "project_preferences": {},     # プロジェクト嗜好
            "workflow_analysis": {         # ワークフロー分析
                "preferred_schedule": "未設定",  # 好みのスケジュール
                "work_pace": "中程度",          # 作業ペース
                "feedback_style": "建設的",     # フィードバックスタイル
                "collaboration_mode": "対等",   # 協働モード
                "last_analyzed": datetime.now().isoformat()
            },
            "partnership_evolution": {     # パートナーシップ進化
                "trust_level": 0.5,        # 信頼レベル (0.0-1.0)
                "sync_efficiency": 0.4,    # 同期効率 (0.0-1.0)
                "creative_compatibility": 0.6,  # 創作適合性 (0.0-1.0)
                "communication_clarity": 0.5,   # コミュニケーション明確性 (0.0-1.0)
                "last_updated": datetime.now().isoformat()
            },
            "shared_achievements": [],     # 共同成果記録
            "lesson_learned": [],          # 学んだ教訓
            "created_at": datetime.now().isoformat(),
            "version": "1.0"
        }
        
        # データ読み込み
        self._load_collaboration_data()
        
        print(f"🤝 協働記憶システム初期化完了 ({memory_mode}モード)")
    
    def _load_collaboration_data(self):
        """協働記憶データを読み込み"""
        if self.memory_file.exists() and self.memory_mode == "normal":
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                    self.collaboration_data.update(loaded_data)
                
                patterns_count = len(self.collaboration_data.get("work_patterns", []))
                successes_count = len(self.collaboration_data.get("success_patterns", []))
                print(f"✅ 協働記憶読み込み: 作業パターン{patterns_count}件, 成功パターン{successes_count}件")
                
            except Exception as e:
                print(f"⚠️ 協働記憶読み込みエラー: {e}")
        else:
            print("🆕 新規協働記憶データベース作成")
    
    def save_collaboration_data(self):
        """協働記憶データを保存"""
        if self.memory_mode == "test":
            # テストモードでは保存しない
            return
        
        try:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.collaboration_data, f, ensure_ascii=False, indent=2)
            print(f"💾 協働記憶データ保存完了")
        except Exception as e:
            print(f"❌ 協働記憶保存エラー: {e}")
    
    def record_work_pattern(self, activity_type: str, duration_minutes: int, 
                          user_satisfaction: str, outcome_quality: str, 
                          notes: str = "") -> str:
        """
        作業パターンを記録
        
        Args:
            activity_type: 活動タイプ ("discussion", "creation", "review", "planning", "research")
            duration_minutes: 作業時間（分）
            user_satisfaction: ユーザー満足度 ("high", "medium", "low")
            outcome_quality: 成果品質 ("excellent", "good", "fair", "poor")
            notes: 補足メモ
            
        Returns:
            str: 記録されたパターンID
        """
        try:
            pattern_id = f"work_{len(self.collaboration_data['work_patterns']) + 1:04d}"
            
            work_pattern = {
                "id": pattern_id,
                "date": datetime.now().isoformat(),
                "activity_type": activity_type,
                "duration_minutes": duration_minutes,
                "user_satisfaction": user_satisfaction,
                "outcome_quality": outcome_quality,
                "notes": notes,
                "efficiency_score": self._calculate_efficiency_score(
                    duration_minutes, user_satisfaction, outcome_quality
                ),
                "context": {
                    "day_of_week": datetime.now().strftime("%A"),
                    "hour": datetime.now().hour,
                    "session_length": duration_minutes
                }
            }
            
            self.collaboration_data["work_patterns"].append(work_pattern)
            
            # パートナーシップ進化への影響
            self._update_partnership_evolution(activity_type, user_satisfaction, outcome_quality)
            
            print(f"📊 作業パターン記録: {activity_type} ({duration_minutes}分, 満足度: {user_satisfaction})")
            
            # 定期保存（パターン件数が5の倍数の時）
            if len(self.collaboration_data["work_patterns"]) % 5 == 0:
                self.save_collaboration_data()
            
            return pattern_id
            
        except Exception as e:
            print(f"❌ 作業パターン記録エラー: {e}")
            return None
    
    def _calculate_efficiency_score(self, duration: int, satisfaction: str, quality: str) -> float:
        """効率性スコア計算"""
        satisfaction_scores = {"high": 1.0, "medium": 0.6, "low": 0.3}
        quality_scores = {"excellent": 1.0, "good": 0.8, "fair": 0.5, "poor": 0.2}
        
        # 時間効率（短時間で良い結果ほど高スコア）
        time_efficiency = max(0.1, 1.0 - (duration / 120))  # 120分を基準
        
        base_score = (
            satisfaction_scores.get(satisfaction, 0.5) * 0.4 +
            quality_scores.get(quality, 0.5) * 0.4 +
            time_efficiency * 0.2
        )
        
        return round(base_score, 2)
    
    def _update_partnership_evolution(self, activity_type: str, satisfaction: str, quality: str):
        """パートナーシップ進化指標を更新"""
        evolution = self.collaboration_data["partnership_evolution"]
        
        # 満足度による信頼レベル調整
        if satisfaction == "high":
            evolution["trust_level"] = min(1.0, evolution["trust_level"] + 0.05)
            evolution["communication_clarity"] = min(1.0, evolution["communication_clarity"] + 0.03)
        elif satisfaction == "low":
            evolution["trust_level"] = max(0.0, evolution["trust_level"] - 0.02)
        
        # 活動タイプ別の適応
        if activity_type == "creation":
            evolution["creative_compatibility"] = min(1.0, evolution["creative_compatibility"] + 0.04)
        elif activity_type == "discussion":
            evolution["communication_clarity"] = min(1.0, evolution["communication_clarity"] + 0.04)
        
        # 成果品質による同期効率調整
        if quality in ["excellent", "good"]:
            evolution["sync_efficiency"] = min(1.0, evolution["sync_efficiency"] + 0.03)
        elif quality == "poor":
            evolution["sync_efficiency"] = max(0.0, evolution["sync_efficiency"] - 0.02)
        
        evolution["last_updated"] = datetime.now().isoformat()
        print(f"📈 パートナーシップ進化更新: {activity_type} -> 各指標調整")
    
    def record_success_pattern(self, success_type: str, context: str, 
                             key_factors: List[str], outcome: str, 
                             replicability: str = "medium") -> str:
        """
        成功パターンを記録
        
        Args:
            success_type: 成功タイプ ("project_completion", "problem_solving", "creative_breakthrough", "efficient_workflow")
            context: 成功した文脈・状況
            key_factors: 成功の要因リスト
            outcome: 具体的成果
            replicability: 再現性 ("high", "medium", "low")
            
        Returns:
            str: 記録された成功パターンID
        """
        try:
            success_id = f"success_{len(self.collaboration_data['success_patterns']) + 1:04d}"
            
            success_pattern = {
                "id": success_id,
                "date": datetime.now().isoformat(),
                "success_type": success_type,
                "context": context,
                "key_factors": key_factors,
                "outcome": outcome,
                "replicability": replicability,
                "impact_rating": self._assess_impact_rating(success_type, outcome),
                "conditions": {
                    "time_of_day": datetime.now().strftime("%H:%M"),
                    "day_type": "weekend" if datetime.now().weekday() >= 5 else "weekday",
                    "season": self._get_current_season()
                },
                "references": 0,  # 参照回数
                "last_referenced": None
            }
            
            self.collaboration_data["success_patterns"].append(success_pattern)
            
            # 共同成果として記録（特に重要な成功の場合）
            if success_pattern["impact_rating"] >= 0.7:
                self._record_shared_achievement(success_type, outcome, key_factors)
            
            print(f"🎯 成功パターン記録: {success_type} - {outcome[:30]}...")
            
            return success_id
            
        except Exception as e:
            print(f"❌ 成功パターン記録エラー: {e}")
            return None
    
    def _assess_impact_rating(self, success_type: str, outcome: str) -> float:
        """インパクト評価"""
        type_weights = {
            "project_completion": 0.8,
            "creative_breakthrough": 0.9,
            "problem_solving": 0.7,
            "efficient_workflow": 0.6
        }
        
        base_rating = type_weights.get(success_type, 0.5)
        
        # アウトカムの内容から追加評価
        impact_keywords = ["完成", "革新", "突破", "解決", "効率", "改善", "成功"]
        keyword_bonus = sum(0.05 for keyword in impact_keywords if keyword in outcome)
        
        return min(1.0, base_rating + keyword_bonus)
    
    def _get_current_season(self) -> str:
        """現在の季節を取得"""
        month = datetime.now().month
        if month in [12, 1, 2]:
            return "winter"
        elif month in [3, 4, 5]:
            return "spring"
        elif month in [6, 7, 8]:
            return "summer"
        else:
            return "autumn"
    
    def _record_shared_achievement(self, achievement_type: str, description: str, factors: List[str]):
        """共同成果を記録"""
        achievement = {
            "id": f"achieve_{len(self.collaboration_data['shared_achievements']) + 1:03d}",
            "date": datetime.now().isoformat(),
            "type": achievement_type,
            "description": description,
            "contributing_factors": factors,
            "celebration_level": "high" if len(factors) >= 3 else "medium"
        }
        
        self.collaboration_data["shared_achievements"].append(achievement)
        print(f"🏆 共同成果記録: {description[:40]}...")
    
    def analyze_communication_style(self, user_message: str, response_quality: str, 
                                  understanding_level: str) -> Optional[str]:
        """
        コミュニケーションスタイルを分析・記録
        
        Args:
            user_message: ユーザーメッセージ
            response_quality: 応答品質 ("excellent", "good", "fair", "poor")
            understanding_level: 理解度 ("perfect", "good", "partial", "confused")
            
        Returns:
            str: 分析されたコミュニケーションスタイルID
        """
        try:
            # メッセージ特徴分析
            message_features = self._analyze_message_features(user_message)
            
            style_record = {
                "id": f"comm_{len(self.collaboration_data['communication_styles']) + 1:04d}",
                "date": datetime.now().isoformat(),
                "message_length": len(user_message),
                "message_type": message_features["type"],
                "formality": message_features["formality"],
                "directness": message_features["directness"],
                "response_quality": response_quality,
                "understanding_level": understanding_level,
                "effectiveness_score": self._calculate_communication_effectiveness(
                    response_quality, understanding_level
                )
            }
            
            self.collaboration_data["communication_styles"].append(style_record)
            
            # コミュニケーション明確性の更新
            evolution = self.collaboration_data["partnership_evolution"]
            if style_record["effectiveness_score"] >= 0.7:
                evolution["communication_clarity"] = min(1.0, evolution["communication_clarity"] + 0.02)
            
            print(f"💬 コミュニケーションスタイル分析: {message_features['type']} (効果: {style_record['effectiveness_score']:.2f})")
            
            return style_record["id"]
            
        except Exception as e:
            print(f"❌ コミュニケーション分析エラー: {e}")
            return None
    
    def _analyze_message_features(self, message: str) -> Dict[str, str]:
        """メッセージ特徴を分析"""
        features = {
            "type": "statement",
            "formality": "casual",
            "directness": "moderate"
        }
        
        # メッセージタイプ判定
        if "？" in message or "?" in message:
            features["type"] = "question"
        elif "!" in message or "！" in message:
            features["type"] = "exclamation"
        elif any(word in message for word in ["お願い", "してください", "頼む"]):
            features["type"] = "request"
        
        # 敬語レベル判定
        if any(word in message for word in ["です", "ます", "ございます"]):
            features["formality"] = "formal"
        elif any(word in message for word in ["だ", "である", "〜よ", "〜ね"]):
            features["formality"] = "casual"
        
        # 直接性判定
        if any(word in message for word in ["すぐに", "早く", "今すぐ", "急いで"]):
            features["directness"] = "high"
        elif any(word in message for word in ["もし", "できれば", "よろしければ"]):
            features["directness"] = "low"
        
        return features
    
    def _calculate_communication_effectiveness(self, quality: str, understanding: str) -> float:
        """コミュニケーション効果を計算"""
        quality_scores = {"excellent": 1.0, "good": 0.8, "fair": 0.5, "poor": 0.2}
        understanding_scores = {"perfect": 1.0, "good": 0.8, "partial": 0.5, "confused": 0.2}
        
        return (quality_scores.get(quality, 0.5) + understanding_scores.get(understanding, 0.5)) / 2
    
    def learn_from_failure(self, failure_context: str, failure_reasons: List[str], 
                          lessons: List[str], prevention_strategies: List[str]) -> str:
        """
        失敗から学習
        
        Args:
            failure_context: 失敗した文脈
            failure_reasons: 失敗の原因リスト
            lessons: 学んだ教訓リスト
            prevention_strategies: 予防策リスト
            
        Returns:
            str: 学習記録ID
        """
        try:
            lesson_id = f"lesson_{len(self.collaboration_data['lesson_learned']) + 1:04d}"
            
            lesson_record = {
                "id": lesson_id,
                "date": datetime.now().isoformat(),
                "failure_context": failure_context,
                "failure_reasons": failure_reasons,
                "lessons": lessons,
                "prevention_strategies": prevention_strategies,
                "severity": self._assess_failure_severity(failure_reasons),
                "recovery_time": "未設定",  # 手動で設定
                "applied": False  # 教訓が適用されたかフラグ
            }
            
            self.collaboration_data["lesson_learned"].append(lesson_record)
            
            print(f"📚 失敗からの学習記録: {failure_context[:30]}... (重要度: {lesson_record['severity']})")
            
            return lesson_id
            
        except Exception as e:
            print(f"❌ 失敗学習記録エラー: {e}")
            return None
    
    def _assess_failure_severity(self, reasons: List[str]) -> str:
        """失敗の重要度を評価"""
        critical_keywords = ["致命的", "重大", "システム", "破損", "失敗"]
        moderate_keywords = ["遅延", "品質", "誤解", "非効率"]
        
        if any(keyword in " ".join(reasons) for keyword in critical_keywords):
            return "critical"
        elif any(keyword in " ".join(reasons) for keyword in moderate_keywords):
            return "moderate"
        else:
            return "minor"
    
    def get_collaboration_insights(self) -> Dict[str, Any]:
        """協働に関する洞察を生成"""
        insights = {
            "preferred_work_style": self._analyze_preferred_work_style(),
            "success_factors": self._identify_success_factors(),
            "partnership_strength": self._assess_partnership_strength(),
            "improvement_areas": self._suggest_improvement_areas(),
            "optimal_conditions": self._identify_optimal_conditions()
        }
        
        return insights
    
    def _analyze_preferred_work_style(self) -> Dict[str, str]:
        """好みの作業スタイルを分析"""
        patterns = self.collaboration_data["work_patterns"]
        
        if not patterns:
            return {"analysis": "データ不足", "recommendation": "さらなる協働が必要"}
        
        # 効率性の高い活動タイプを特定
        high_efficiency_patterns = [p for p in patterns if p.get("efficiency_score", 0) >= 0.7]
        
        if high_efficiency_patterns:
            most_effective_type = max(
                set(p["activity_type"] for p in high_efficiency_patterns),
                key=lambda t: sum(1 for p in high_efficiency_patterns if p["activity_type"] == t)
            )
            
            return {
                "most_effective_activity": most_effective_type,
                "analysis": f"{most_effective_type}が最も効果的な協働スタイル",
                "recommendation": f"{most_effective_type}を中心とした作業を推奨"
            }
        
        return {"analysis": "効率パターン特定中", "recommendation": "継続的な協働データ収集中"}
    
    def _identify_success_factors(self) -> List[str]:
        """成功要因を特定"""
        successes = self.collaboration_data["success_patterns"]
        
        if not successes:
            return ["データ不足 - 成功パターン蓄積中"]
        
        # 高インパクトな成功から要因を抽出
        high_impact_successes = [s for s in successes if s.get("impact_rating", 0) >= 0.7]
        
        all_factors = []
        for success in high_impact_successes:
            all_factors.extend(success.get("key_factors", []))
        
        # 頻出要因を特定
        factor_counts = {}
        for factor in all_factors:
            factor_counts[factor] = factor_counts.get(factor, 0) + 1
        
        # 上位要因を返す
        top_factors = sorted(factor_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return [factor for factor, count in top_factors if count >= 2]
    
    def _assess_partnership_strength(self) -> Dict[str, float]:
        """パートナーシップの強さを評価"""
        evolution = self.collaboration_data["partnership_evolution"]
        
        return {
            "overall_strength": (
                evolution["trust_level"] * 0.3 +
                evolution["sync_efficiency"] * 0.25 +
                evolution["creative_compatibility"] * 0.25 +
                evolution["communication_clarity"] * 0.2
            ),
            "trust_level": evolution["trust_level"],
            "sync_efficiency": evolution["sync_efficiency"],
            "creative_compatibility": evolution["creative_compatibility"],
            "communication_clarity": evolution["communication_clarity"]
        }
    
    def _suggest_improvement_areas(self) -> List[str]:
        """改善領域を提案"""
        evolution = self.collaboration_data["partnership_evolution"]
        suggestions = []
        
        if evolution["trust_level"] < 0.6:
            suggestions.append("信頼関係の構築 - より多くの成功体験を共有")
        
        if evolution["sync_efficiency"] < 0.6:
            suggestions.append("同期効率の向上 - 作業リズムとタイミングの調整")
        
        if evolution["creative_compatibility"] < 0.7:
            suggestions.append("創作適合性の向上 - アイデア共有とフィードバック改善")
        
        if evolution["communication_clarity"] < 0.7:
            suggestions.append("コミュニケーション明確性 - 意図の伝達と理解確認")
        
        if not suggestions:
            suggestions.append("現在の協働品質は良好 - 継続的な改善を維持")
        
        return suggestions
    
    def _identify_optimal_conditions(self) -> Dict[str, str]:
        """最適な協働条件を特定"""
        patterns = self.collaboration_data["work_patterns"]
        
        if not patterns:
            return {"analysis": "データ収集中", "recommendation": "さらなる協働データが必要"}
        
        # 高効率パターンの条件を分析
        high_efficiency = [p for p in patterns if p.get("efficiency_score", 0) >= 0.7]
        
        if not high_efficiency:
            return {"analysis": "効率パターン特定中", "recommendation": "協働データ蓄積継続"}
        
        # 最適な時間帯
        optimal_hours = [p["context"]["hour"] for p in high_efficiency]
        if optimal_hours:
            avg_hour = sum(optimal_hours) / len(optimal_hours)
            optimal_time = f"{int(avg_hour):02d}:00頃"
        else:
            optimal_time = "未特定"
        
        # 最適な曜日
        optimal_days = [p["context"]["day_of_week"] for p in high_efficiency]
        if optimal_days:
            most_common_day = max(set(optimal_days), key=optimal_days.count)
        else:
            most_common_day = "未特定"
        
        return {
            "optimal_time": optimal_time,
            "optimal_day": most_common_day,
            "analysis": f"最も効率的な協働: {most_common_day}の{optimal_time}",
            "recommendation": "この条件での協働を増やすことを推奨"
        }
    
    def get_collaboration_context_for_prompt(self) -> str:
        """プロンプト用の協働コンテキストを生成"""
        context_parts = []
        
        # パートナーシップ状態
        evolution = self.collaboration_data["partnership_evolution"]
        context_parts.append("【協働パートナーシップ状態】")
        context_parts.append(f"- 信頼レベル: {evolution['trust_level']:.1f} (最大1.0)")
        context_parts.append(f"- 創作適合性: {evolution['creative_compatibility']:.1f}")
        context_parts.append(f"- コミュニケーション明確性: {evolution['communication_clarity']:.1f}")
        
        # 最近の成功パターン
        recent_successes = self.collaboration_data["success_patterns"][-3:] if self.collaboration_data["success_patterns"] else []
        if recent_successes:
            context_parts.append("\n【最近の成功パターン】")
            for success in recent_successes:
                success_type = success["success_type"]
                outcome = success["outcome"][:40]
                context_parts.append(f"- {success_type}: {outcome}...")
        
        # 作業スタイル洞察
        insights = self.get_collaboration_insights()
        if insights["preferred_work_style"]["analysis"] != "データ不足":
            context_parts.append(f"\n【協働スタイル】")
            context_parts.append(f"- {insights['preferred_work_style']['analysis']}")
        
        # 改善提案
        improvements = insights["improvement_areas"][:2]  # 上位2つ
        if improvements and "現在の協働品質は良好" not in improvements[0]:
            context_parts.append(f"\n【協働改善点】")
            for improvement in improvements:
                context_parts.append(f"- {improvement}")
        
        return "\n".join(context_parts) if context_parts else ""
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """協働記憶統計情報を取得"""
        return {
            "work_patterns": len(self.collaboration_data["work_patterns"]),
            "success_patterns": len(self.collaboration_data["success_patterns"]),
            "communication_styles": len(self.collaboration_data["communication_styles"]),
            "shared_achievements": len(self.collaboration_data["shared_achievements"]),
            "lessons_learned": len(self.collaboration_data["lesson_learned"]),
            "partnership_evolution": self.collaboration_data["partnership_evolution"],
            "memory_mode": self.memory_mode,
            "last_update": self.collaboration_data["partnership_evolution"]["last_updated"]
        }

if __name__ == "__main__":
    # テスト実行
    print("=== CollaborationMemory テスト ===")
    
    # 通常モードテスト
    print("\n--- 通常モード ---")
    collab_memory = CollaborationMemory("normal")
    
    # 作業パターン記録テスト
    work_id = collab_memory.record_work_pattern(
        activity_type="creation",
        duration_minutes=45,
        user_satisfaction="high",
        outcome_quality="good",
        notes="音楽制作で良いアイデアが出た"
    )
    print(f"記録された作業パターンID: {work_id}")
    
    # 成功パターン記録テスト
    success_id = collab_memory.record_success_pattern(
        success_type="creative_breakthrough",
        context="音楽制作セッション中にメロディが閃いた",
        key_factors=["リラックスした環境", "集中できる時間", "良いコミュニケーション"],
        outcome="完成度の高いメロディライン作成",
        replicability="high"
    )
    print(f"記録された成功パターンID: {success_id}")
    
    # コミュニケーション分析テスト
    comm_id = collab_memory.analyze_communication_style(
        user_message="一緒に歌詞を作ってみませんか？",
        response_quality="excellent",
        understanding_level="perfect"
    )
    print(f"記録されたコミュニケーション分析ID: {comm_id}")
    
    # 洞察生成テスト
    insights = collab_memory.get_collaboration_insights()
    print(f"\n協働洞察: {insights}")
    
    # プロンプト用コンテキスト生成テスト
    context = collab_memory.get_collaboration_context_for_prompt()
    print(f"\nプロンプト用コンテキスト:\n{context}")
    
    # 統計情報テスト
    stats = collab_memory.get_memory_stats()
    print(f"\n協働記憶統計: {stats}")
    
    print("\n✅ CollaborationMemory テスト完了")
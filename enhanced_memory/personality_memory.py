#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
せつな個人記憶システム
キャラクターの個人的体験・感情・成長を記録・管理
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

class PersonalityMemory:
    """せつなの個人的記憶管理システム"""
    
    def __init__(self, memory_mode="normal"):
        """
        個人記憶システム初期化
        
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
            self.memory_file = base_path / "temp" / f"test_personality_memory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            os.makedirs(self.memory_file.parent, exist_ok=True)
        else:
            # 通常モード: 永続ファイル
            self.memory_file = base_path / "enhanced_memory" / "personality_memory.json"
            os.makedirs(self.memory_file.parent, exist_ok=True)
        
        # 個人記憶データ構造
        self.personality_data = {
            "personal_experiences": [],      # 個人的体験記録
            "emotional_memories": [],        # 感情的記憶
            "learning_experiences": [],      # 学習体験
            "character_evolution": {         # キャラクター進化
                "confidence_level": 0.5,     # 自信度 (0.0-1.0)
                "technical_knowledge": 0.6,  # 技術知識 (0.0-1.0)
                "creative_experience": 0.7,  # 創作経験 (0.0-1.0)
                "social_comfort": 0.5,       # 社交性 (0.0-1.0)
                "last_updated": datetime.now().isoformat()
            },
            "relationship_history": [],      # 関係性変化履歴
            "memorable_moments": [],         # 特に印象深い瞬間
            "created_at": datetime.now().isoformat(),
            "version": "1.0"
        }
        
        # データ読み込み
        self._load_personality_data()
        
        print(f"🧠 個人記憶システム初期化完了 ({memory_mode}モード)")
    
    def _load_personality_data(self):
        """個人記憶データを読み込み"""
        if self.memory_file.exists() and self.memory_mode == "normal":
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                    self.personality_data.update(loaded_data)
                
                experiences_count = len(self.personality_data.get("personal_experiences", []))
                emotions_count = len(self.personality_data.get("emotional_memories", []))
                print(f"✅ 個人記憶読み込み: 体験{experiences_count}件, 感情{emotions_count}件")
                
            except Exception as e:
                print(f"⚠️ 個人記憶読み込みエラー: {e}")
        else:
            print("🆕 新規個人記憶データベース作成")
    
    def save_personality_data(self):
        """個人記憶データを保存"""
        if self.memory_mode == "test":
            # テストモードでは保存しない
            return
        
        try:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.personality_data, f, ensure_ascii=False, indent=2)
            print(f"💾 個人記憶データ保存完了")
        except Exception as e:
            print(f"❌ 個人記憶保存エラー: {e}")
    
    def record_personal_experience(self, event_description: str, event_type: str, 
                                 emotion: str, learning: str = "", impact_level: float = 0.5):
        """
        個人的体験を記録
        
        Args:
            event_description: 出来事の説明
            event_type: 体験タイプ ("conversation", "creation", "learning", "challenge")
            emotion: 感情 ("excited", "proud", "nervous", "curious", "satisfied", etc.)
            learning: 学んだこと
            impact_level: 影響度 (0.0-1.0)
        """
        try:
            experience = {
                "id": f"exp_{len(self.personality_data['personal_experiences']) + 1:04d}",
                "date": datetime.now().isoformat(),
                "description": event_description,
                "type": event_type,
                "emotion": emotion,
                "learning": learning,
                "impact_level": impact_level,
                "references": 0,  # 参照回数
                "last_referenced": None
            }
            
            self.personality_data["personal_experiences"].append(experience)
            
            # 感情記憶としても記録（影響度が高い場合）
            if impact_level >= 0.7:
                self._record_emotional_memory(event_description, emotion, impact_level)
            
            # キャラクター進化への影響
            self._update_character_evolution(event_type, emotion, impact_level)
            
            print(f"📝 個人体験記録: {event_description[:30]}... (影響度: {impact_level})")
            
            # 定期保存（体験件数が5の倍数の時）
            if len(self.personality_data["personal_experiences"]) % 5 == 0:
                self.save_personality_data()
            
            return experience["id"]
            
        except Exception as e:
            print(f"❌ 体験記録エラー: {e}")
            return None
    
    def _record_emotional_memory(self, event: str, emotion: str, intensity: float):
        """感情記憶を記録"""
        emotional_memory = {
            "id": f"emo_{len(self.personality_data['emotional_memories']) + 1:04d}",
            "date": datetime.now().isoformat(),
            "event": event,
            "emotion": emotion,
            "intensity": intensity,
            "decay_factor": 1.0,  # 時間経過による減衰係数
            "associations": []     # 関連する記憶ID
        }
        
        self.personality_data["emotional_memories"].append(emotional_memory)
        print(f"💝 感情記憶記録: {emotion} (強度: {intensity})")
    
    def _update_character_evolution(self, event_type: str, emotion: str, impact: float):
        """キャラクター進化指標を更新"""
        evolution = self.personality_data["character_evolution"]
        
        # イベントタイプ別の進化
        if event_type == "learning":
            evolution["technical_knowledge"] = min(1.0, evolution["technical_knowledge"] + impact * 0.1)
        elif event_type == "creation":
            evolution["creative_experience"] = min(1.0, evolution["creative_experience"] + impact * 0.1)
            evolution["confidence_level"] = min(1.0, evolution["confidence_level"] + impact * 0.05)
        elif event_type == "conversation":
            evolution["social_comfort"] = min(1.0, evolution["social_comfort"] + impact * 0.08)
        elif event_type == "challenge":
            if emotion in ["proud", "satisfied"]:
                evolution["confidence_level"] = min(1.0, evolution["confidence_level"] + impact * 0.1)
            elif emotion in ["nervous", "worried"]:
                evolution["confidence_level"] = max(0.0, evolution["confidence_level"] - impact * 0.05)
        
        evolution["last_updated"] = datetime.now().isoformat()
        print(f"📈 キャラクター進化更新: {event_type} -> 各指標調整")
    
    def get_recent_experiences(self, days: int = 7, limit: int = 10) -> List[Dict]:
        """最近の体験を取得"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent_experiences = []
        for exp in self.personality_data["personal_experiences"]:
            exp_date = datetime.fromisoformat(exp["date"])
            if exp_date >= cutoff_date:
                recent_experiences.append(exp)
        
        # 日付順（新しい順）でソート
        recent_experiences.sort(key=lambda x: x["date"], reverse=True)
        
        return recent_experiences[:limit]
    
    def get_emotional_context(self, emotion_type: str = None) -> str:
        """感情的コンテキストを生成"""
        context_parts = []
        
        # 最近の感情記憶
        recent_emotions = []
        for emo in self.personality_data["emotional_memories"][-5:]:
            if not emotion_type or emo["emotion"] == emotion_type:
                recent_emotions.append(emo)
        
        if recent_emotions:
            context_parts.append("【最近の感情的記憶】")
            for emo in recent_emotions:
                context_parts.append(f"- {emo['event'][:40]}... ({emo['emotion']})")
        
        # キャラクター進化状態
        evolution = self.personality_data["character_evolution"]
        context_parts.append(f"\n【せつなの現在の状態】")
        context_parts.append(f"- 自信レベル: {evolution['confidence_level']:.1f}")
        context_parts.append(f"- 創作経験: {evolution['creative_experience']:.1f}")
        context_parts.append(f"- 技術知識: {evolution['technical_knowledge']:.1f}")
        
        return "\n".join(context_parts)
    
    def analyze_conversation_for_experience(self, user_input: str, setsuna_response: str) -> Optional[str]:
        """
        会話から個人体験を分析・記録
        
        Args:
            user_input: ユーザーの入力
            setsuna_response: せつなの応答
            
        Returns:
            str: 記録された体験ID（記録されなかった場合はNone）
        """
        try:
            # 体験検出パターン
            experience_patterns = {
                "learning": {
                    "keywords": ["教えて", "学ぶ", "知識", "理解", "覚える"],
                    "emotions": ["curious", "interested", "excited"],
                    "base_impact": 0.6
                },
                "creation": {
                    "keywords": ["作る", "制作", "創作", "デザイン", "アイデア"],
                    "emotions": ["creative", "excited", "proud"],
                    "base_impact": 0.7
                },
                "conversation": {
                    "keywords": ["話", "相談", "意見", "感想", "思う"],
                    "emotions": ["comfortable", "happy", "thoughtful"],
                    "base_impact": 0.4
                },
                "challenge": {
                    "keywords": ["難しい", "挑戦", "頑張る", "試す", "チャレンジ"],
                    "emotions": ["determined", "nervous", "proud"],
                    "base_impact": 0.8
                }
            }
            
            # パターンマッチング
            detected_type = None
            detected_emotion = "neutral"
            impact_level = 0.3
            
            for exp_type, pattern in experience_patterns.items():
                if any(keyword in user_input for keyword in pattern["keywords"]):
                    detected_type = exp_type
                    detected_emotion = pattern["emotions"][0]  # デフォルト感情
                    impact_level = pattern["base_impact"]
                    break
            
            # 体験記録（重要度が一定以上の場合のみ）
            if detected_type and impact_level >= 0.5:
                learning_text = f"ユーザーとの{detected_type}について話した"
                experience_id = self.record_personal_experience(
                    event_description=f"{user_input[:50]}... について{detected_type}的な会話",
                    event_type=detected_type,
                    emotion=detected_emotion,
                    learning=learning_text,
                    impact_level=impact_level
                )
                return experience_id
            
            return None
            
        except Exception as e:
            print(f"❌ 会話体験分析エラー: {e}")
            return None
    
    def get_personality_context_for_prompt(self) -> str:
        """プロンプト用の個人記憶コンテキストを生成"""
        context_parts = []
        
        # 最近の重要な体験
        recent_experiences = self.get_recent_experiences(days=30, limit=5)
        if recent_experiences:
            context_parts.append("【せつなの最近の体験】")
            for exp in recent_experiences:
                if exp["impact_level"] >= 0.6:
                    context_parts.append(f"- {exp['description'][:40]}... (感情: {exp['emotion']})")
        
        # キャラクター成長状態
        evolution = self.personality_data["character_evolution"]
        context_parts.append(f"\n【せつなの成長状態】")
        
        # 成長レベルに応じたコメント
        if evolution["confidence_level"] >= 0.7:
            context_parts.append("- 最近自信がついてきて、積極的に提案できるようになった")
        elif evolution["confidence_level"] <= 0.3:
            context_parts.append("- まだ少し不安もあるけど、頑張って学習中")
        
        if evolution["creative_experience"] >= 0.8:
            context_parts.append("- 創作活動での経験が豊富になってきた")
        
        return "\n".join(context_parts)
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """記憶統計情報を取得"""
        return {
            "total_experiences": len(self.personality_data["personal_experiences"]),
            "emotional_memories": len(self.personality_data["emotional_memories"]),
            "character_evolution": self.personality_data["character_evolution"],
            "memory_mode": self.memory_mode,
            "last_update": self.personality_data["character_evolution"]["last_updated"]
        }

if __name__ == "__main__":
    # テスト実行
    print("=== PersonalityMemory テスト ===")
    
    # 通常モードテスト
    print("\n--- 通常モード ---")
    normal_memory = PersonalityMemory("normal")
    
    # 体験記録テスト
    exp_id = normal_memory.record_personal_experience(
        event_description="ユーザーと音楽について深い話をした",
        event_type="conversation",
        emotion="excited",
        learning="ユーザーの音楽的嗜好を理解した",
        impact_level=0.7
    )
    print(f"記録された体験ID: {exp_id}")
    
    # コンテキスト生成テスト
    context = normal_memory.get_personality_context_for_prompt()
    print(f"\nプロンプト用コンテキスト:\n{context}")
    
    # 統計情報テスト
    stats = normal_memory.get_memory_stats()
    print(f"\n記憶統計: {stats}")
    
    # テストモードテスト
    print("\n--- テストモード ---")
    test_memory = PersonalityMemory("test")
    test_memory.record_personal_experience(
        event_description="テスト用の体験記録",
        event_type="learning",
        emotion="curious",
        impact_level=0.5
    )
    
    print("\n✅ PersonalityMemory テスト完了")
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
創造的推薦システム（簡略版） - Phase 3-A
テスト用の簡略実装
"""

import random
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from collections import defaultdict, Counter
import math

class CreativeRecommendationSystem:
    """創造的で独創的な推薦を行うクラス（簡略版）"""
    
    def __init__(self):
        """初期化"""
        # Windows環境とWSL2環境両方に対応
        if os.name == 'nt':  # Windows
            self.recommendation_file = Path("D:/setsuna_bot/data/creative_recommendations.json")
        else:  # Linux/WSL2
            self.recommendation_file = Path("/mnt/d/setsuna_bot/data/creative_recommendations.json")
        
        # 推薦履歴
        self.recommendation_history = []
        
        self._ensure_data_dir()
        self._load_recommendation_data()
        
        print("[創造推薦] ✅ 創造的推薦システム初期化完了")
    
    def _ensure_data_dir(self):
        """データディレクトリの確保"""
        self.recommendation_file.parent.mkdir(parents=True, exist_ok=True)
    
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
                'recommendation_history': self.recommendation_history[-200:],
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
        創造的推薦を生成（簡略版）
        
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
            # 簡略版の創造性スコア計算
            creativity_score = self._calculate_simple_creativity_score(source_video, candidate)
            
            # 基本的なナラティブ生成
            narrative = self._generate_simple_narrative(source_video, candidate)
            
            # 意外性スコア（簡略版）
            surprise_score = random.uniform(0.3, 0.9)
            
            creative_recommendation = {
                "video_id": candidate.get("video_id", ""),
                "video_data": candidate,
                "source_video_id": source_video.get("video_id", ""),
                "creative_connections": {
                    "detected_patterns": [{"pattern": "emotional_resonance", "score": 0.7}],
                    "connection_strength": creativity_score,
                    "primary_connection_type": "emotional_resonance",
                    "surprise_elements": ["異なるアーティスト"],
                    "narrative_potential": creativity_score * 0.8
                },
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
    
    def _calculate_simple_creativity_score(self, source_video: Dict[str, Any], target_video: Dict[str, Any]) -> float:
        """簡略版創造性スコア計算"""
        base_score = 0.5
        
        # タイトルの類似性
        source_title = source_video.get("metadata", {}).get("title", "")
        target_title = target_video.get("metadata", {}).get("title", "")
        
        if source_title and target_title:
            # 簡単な文字数比較
            length_diff = abs(len(source_title) - len(target_title))
            similarity = 1.0 - (length_diff / max(len(source_title), len(target_title), 1))
            base_score += similarity * 0.3
        
        # チャンネルの違い
        source_channel = source_video.get("metadata", {}).get("channel_title", "")
        target_channel = target_video.get("metadata", {}).get("channel_title", "")
        
        if source_channel != target_channel:
            base_score += 0.2  # 異なるアーティストはボーナス
        
        return min(1.0, base_score)
    
    def _generate_simple_narrative(self, source_video: Dict[str, Any], target_video: Dict[str, Any]) -> str:
        """簡単なナラティブ生成"""
        source_title = source_video.get("metadata", {}).get("title", "この楽曲")
        target_title = target_video.get("metadata", {}).get("title", "その楽曲")
        
        templates = [
            f"{source_title}がお好きでしたら、{target_title}もきっと心に響くはずです。",
            f"{source_title}と{target_title}には、音楽的な親和性を感じます。",
            f"{source_title}の感動を、{target_title}でも体験していただけるでしょう。",
            f"{source_title}から{target_title}への音楽的な旅路をお楽しみください。"
        ]
        
        return random.choice(templates)
    
    def _record_recommendation_generation(self, source_video: Dict[str, Any], recommendations: List[Dict[str, Any]]):
        """推薦生成を記録"""
        record = {
            "timestamp": datetime.now().isoformat(),
            "source_video_id": source_video.get("video_id", ""),
            "recommended_count": len(recommendations),
            "top_creativity_score": recommendations[0]["creativity_score"] if recommendations else 0.0,
            "patterns_used": ["emotional_resonance"]
        }
        
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
        
        return {
            "average_creativity_score": round(avg_creativity, 3),
            "total_recommendations": len(self.recommendation_history),
            "recent_recommendations": len(recent_history),
            "pattern_usage": {"emotional_resonance": len(recent_history)},
            "diversity_score": 0.8,
            "most_used_pattern": "emotional_resonance"
        }


# 使用例・テスト
if __name__ == "__main__":
    print("=== 創造的推薦システム（簡略版）テスト ===")
    
    system = CreativeRecommendationSystem()
    
    # テスト用動画データ
    test_source_video = {
        "video_id": "test_001",
        "metadata": {
            "title": "アドベンチャー",
            "channel_title": "YOASOBI",
        }
    }
    
    test_candidate_videos = [
        {
            "video_id": "test_002",
            "metadata": {
                "title": "夜に駆ける",
                "channel_title": "YOASOBI",
            }
        },
        {
            "video_id": "test_003",
            "metadata": {
                "title": "カノン",
                "channel_title": "Classical",
            }
        }
    ]
    
    # 創造的推薦生成テスト
    recommendations = system.generate_creative_recommendation(
        test_source_video, 
        test_candidate_videos
    )
    
    print(f"\n🎨 生成された創造的推薦: {len(recommendations)}件")
    
    for i, rec in enumerate(recommendations, 1):
        print(f"\n--- 推薦 {i} ---")
        print(f"動画: {rec['video_data']['metadata']['title']}")
        print(f"創造性スコア: {rec['creativity_score']:.3f}")
        print(f"ナラティブ: {rec['narrative']}")
    
    # 統計情報
    stats = system.get_creativity_statistics()
    print(f"\n📊 創造性統計: {stats}")
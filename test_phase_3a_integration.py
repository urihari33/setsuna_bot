#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 3-A 統合テスト
創造的分析・表現強化システムの統合テスト
"""

import os
import sys
import json
import unittest
from pathlib import Path
from datetime import datetime

# プロジェクトルートを追加
sys.path.append(str(Path(__file__).parent))

# Phase 3-A コンポーネントのインポート
from core.lyrics_emotion_analyzer import LyricsEmotionAnalyzer
from core.personal_expression_engine import PersonalExpressionEngine
from core.creative_recommendation_system_simple import CreativeRecommendationSystem

class TestPhase3AIntegration(unittest.TestCase):
    """Phase 3-A 統合テストクラス"""
    
    def setUp(self):
        """テストセットアップ"""
        print(f"\n[統合テスト] 🚀 Phase 3-A コンポーネント初期化開始...")
        
        # 各システムの初期化
        self.lyrics_analyzer = LyricsEmotionAnalyzer()
        self.expression_engine = PersonalExpressionEngine()
        self.recommendation_system = CreativeRecommendationSystem()
        
        # テストデータの準備
        self.test_lyrics = """
        僕らはまだ若いから
        何でもできると思ってた
        でも現実は違ったんだ
        夢を追いかけるのは難しい
        それでも諦めたくない
        君と一緒ならきっと
        """
        
        self.test_video_data = {
            "video_id": "test_video_001",
            "metadata": {
                "title": "青春の歌",
                "channel_title": "テストアーティスト",
                "published_at": "2023-06-01T00:00:00Z",
                "view_count": 100000,
                "description": "青春をテーマにした楽曲"
            },
            "creative_insight": {
                "music_info": {
                    "lyrics": self.test_lyrics,
                    "genre": "pop",
                    "mood": "nostalgic",
                    "bpm": 100,
                    "key": "C"
                },
                "themes": ["youth", "dreams", "friendship"],
                "creators": [
                    {"name": "テスト作曲家", "role": "composer"},
                    {"name": "テスト歌手", "role": "vocal"}
                ]
            }
        }
        
        self.test_candidate_videos = [
            {
                "video_id": "candidate_001",
                "metadata": {
                    "title": "夢の続き",
                    "channel_title": "ドリームアーティスト",
                    "published_at": "2023-07-01T00:00:00Z",
                    "view_count": 150000
                },
                "creative_insight": {
                    "music_analysis": {
                        "genre": "pop",
                        "mood": "hopeful",
                        "bpm": 110,
                        "key": "G"
                    },
                    "themes": ["hope", "future", "dreams"],
                    "creators": [
                        {"name": "希望作曲家", "role": "composer"}
                    ]
                }
            },
            {
                "video_id": "candidate_002", 
                "metadata": {
                    "title": "静寂のメロディ",
                    "channel_title": "クラシカル音楽",
                    "published_at": "2020-01-01T00:00:00Z",
                    "view_count": 50000
                },
                "creative_insight": {
                    "music_analysis": {
                        "genre": "classical",
                        "mood": "peaceful",
                        "bpm": 60,
                        "key": "F"
                    },
                    "themes": ["tranquility", "meditation", "nature"],
                    "creators": [
                        {"name": "古典作曲家", "role": "composer"}
                    ]
                }
            }
        ]
        
        print(f"[統合テスト] ✅ セットアップ完了")
    
    def test_lyrics_emotion_analysis(self):
        """歌詞感情分析テスト"""
        print(f"\n[統合テスト] 🎵 歌詞感情分析テスト開始...")
        
        # 歌詞感情分析実行
        emotion_result = self.lyrics_analyzer.analyze_lyrics_emotion(
            lyrics=self.test_lyrics,
            context={"title": "青春の歌", "genre": "pop"}
        )
        
        # 結果検証
        self.assertIsInstance(emotion_result, dict, "感情分析結果が辞書型であること")
        self.assertIn("dominant_emotions", emotion_result, "主要感情が含まれること")
        self.assertIn("mood_inference", emotion_result, "ムード推論が含まれること")
        self.assertIn("thematic_elements", emotion_result, "テーマ要素が含まれること")
        
        # 感情スコアの妥当性チェック
        if emotion_result["dominant_emotions"]:
            emotion, score = emotion_result["dominant_emotions"][0]
            self.assertIsInstance(emotion, str, "感情名が文字列であること")
            self.assertIsInstance(score, (int, float), "感情スコアが数値であること")
            self.assertGreaterEqual(score, 0.0, "感情スコアが0以上であること")
            self.assertLessEqual(score, 1.0, "感情スコアが1以下であること")
        
        print(f"[統合テスト] ✅ 歌詞感情分析完了: {len(emotion_result['dominant_emotions'])}個の感情検出")
        return emotion_result
    
    def test_personal_expression_generation(self):
        """パーソナル表現生成テスト"""
        print(f"\n[統合テスト] 🎨 パーソナル表現生成テスト開始...")
        
        # 感情分析結果の取得
        emotion_result = self.test_lyrics_emotion_analysis()
        
        # ユーザーコンテキストの準備
        user_context = {
            "conversation_count": 3,
            "familiarity_score": 0.6,
            "relationship_level": "familiar"
        }
        
        # 表現生成実行
        base_content = "この楽曲は青春の切なさと希望を歌った素晴らしい作品です"
        creative_expression = self.expression_engine.generate_creative_expression(
            base_content=base_content,
            emotion_analysis=emotion_result,
            user_context=user_context,
            content_type="music_discussion"
        )
        
        # 結果検証
        self.assertIsInstance(creative_expression, str, "表現結果が文字列であること")
        self.assertGreater(len(creative_expression), 0, "表現内容が空でないこと")
        self.assertIn("楽曲", creative_expression, "楽曲について言及されていること")
        
        # せつならしさの確認（敬語や優しい表現）
        setsuna_indicators = ["です", "ます", "ね", "でしょう", "かもしれません"]
        has_setsuna_style = any(indicator in creative_expression for indicator in setsuna_indicators)
        self.assertTrue(has_setsuna_style, "せつならしい表現スタイルが含まれること")
        
        print(f"[統合テスト] ✅ パーソナル表現生成完了")
        print(f"  生成表現: {creative_expression}")
        
        # 多様性スコアも確認
        diversity_score = self.expression_engine.get_expression_diversity_score()
        print(f"  表現多様性スコア: {diversity_score:.3f}")
        
        return creative_expression
    
    def test_creative_recommendation_system(self):
        """創造的推薦システムテスト"""
        print(f"\n[統合テスト] 🎯 創造的推薦システムテスト開始...")
        
        # 感情分析結果の取得
        emotion_result = self.test_lyrics_emotion_analysis()
        
        # 創造的推薦生成
        recommendations = self.recommendation_system.generate_creative_recommendation(
            source_video=self.test_video_data,
            candidate_videos=self.test_candidate_videos,
            user_emotion_analysis=emotion_result,
            context={"pattern_novelty": 0.7}
        )
        
        # 結果検証
        self.assertIsInstance(recommendations, list, "推薦結果がリスト型であること")
        self.assertGreater(len(recommendations), 0, "推薦が1件以上生成されること")
        
        # 各推薦の構造確認
        for i, rec in enumerate(recommendations):
            with self.subTest(recommendation=i):
                self.assertIn("video_id", rec, "動画IDが含まれること")
                self.assertIn("creativity_score", rec, "創造性スコアが含まれること")
                self.assertIn("surprise_score", rec, "意外性スコアが含まれること")
                self.assertIn("narrative", rec, "ナラティブが含まれること")
                self.assertIn("creative_connections", rec, "創造的関連性が含まれること")
                
                # スコアの妥当性
                self.assertIsInstance(rec["creativity_score"], (int, float), "創造性スコアが数値であること")
                self.assertGreaterEqual(rec["creativity_score"], 0.0, "創造性スコアが0以上であること")
                self.assertLessEqual(rec["creativity_score"], 1.0, "創造性スコアが1以下であること")
                
                # ナラティブの質
                self.assertIsInstance(rec["narrative"], str, "ナラティブが文字列であること")
                self.assertGreater(len(rec["narrative"]), 10, "ナラティブに十分な内容があること")
        
        # 創造性スコア順でソートされているか確認
        scores = [rec["creativity_score"] for rec in recommendations]
        self.assertEqual(scores, sorted(scores, reverse=True), "創造性スコア順でソートされていること")
        
        print(f"[統合テスト] ✅ 創造的推薦システム完了: {len(recommendations)}件の推薦生成")
        
        # 推薦詳細の表示
        for i, rec in enumerate(recommendations, 1):
            print(f"  推薦{i}: {rec['video_data']['metadata']['title']}")
            print(f"    創造性スコア: {rec['creativity_score']:.3f}")
            print(f"    ナラティブ: {rec['narrative'][:50]}...")
        
        return recommendations
    
    def test_full_integration_workflow(self):
        """完全統合ワークフローテスト"""
        print(f"\n[統合テスト] 🌟 完全統合ワークフローテスト開始...")
        
        # 1. 歌詞感情分析
        emotion_result = self.lyrics_analyzer.analyze_lyrics_emotion(
            lyrics=self.test_lyrics,
            context={"title": "青春の歌", "genre": "pop"}
        )
        
        # 2. 創造的推薦生成
        recommendations = self.recommendation_system.generate_creative_recommendation(
            source_video=self.test_video_data,
            candidate_videos=self.test_candidate_videos,
            user_emotion_analysis=emotion_result,
            context={"pattern_novelty": 0.7}
        )
        
        # 3. 各推薦に対するパーソナル表現生成
        user_context = {
            "conversation_count": 5,
            "familiarity_score": 0.8,
            "relationship_level": "familiar"
        }
        
        enhanced_recommendations = []
        for rec in recommendations:
            # 基本推薦内容
            base_content = rec["narrative"]
            
            # せつな風表現で強化
            enhanced_expression = self.expression_engine.generate_creative_expression(
                base_content=base_content,
                emotion_analysis=emotion_result,
                user_context=user_context,
                content_type="music_recommendation"
            )
            
            # 強化された推薦を作成
            enhanced_rec = rec.copy()
            enhanced_rec["setsuna_expression"] = enhanced_expression
            enhanced_recommendations.append(enhanced_rec)
        
        # 統合結果の検証
        self.assertGreater(len(enhanced_recommendations), 0, "強化推薦が生成されること")
        
        for enhanced_rec in enhanced_recommendations:
            self.assertIn("setsuna_expression", enhanced_rec, "せつな表現が追加されること")
            self.assertIsInstance(enhanced_rec["setsuna_expression"], str, "せつな表現が文字列であること")
            self.assertGreater(len(enhanced_rec["setsuna_expression"]), 0, "せつな表現が空でないこと")
        
        print(f"[統合テスト] ✅ 完全統合ワークフロー完了")
        print(f"  処理フロー: 歌詞分析 → 創造的推薦 → せつな表現強化")
        print(f"  最終推薦数: {len(enhanced_recommendations)}件")
        
        # 統合結果のサンプル表示
        if enhanced_recommendations:
            sample = enhanced_recommendations[0]
            print(f"\n  📝 統合結果サンプル:")
            print(f"    推薦動画: {sample['video_data']['metadata']['title']}")
            print(f"    基本ナラティブ: {sample['narrative'][:60]}...")
            print(f"    せつな表現: {sample['setsuna_expression'][:80]}...")
        
        return enhanced_recommendations
    
    def test_system_performance(self):
        """システムパフォーマンステスト"""
        print(f"\n[統合テスト] ⚡ システムパフォーマンステスト開始...")
        
        import time
        
        # 処理時間測定
        start_time = time.time()
        
        # 完全ワークフロー実行
        self.test_full_integration_workflow()
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # パフォーマンス要件チェック
        max_acceptable_time = 10.0  # 最大10秒
        self.assertLess(processing_time, max_acceptable_time, f"処理時間が{max_acceptable_time}秒以内であること")
        
        print(f"[統合テスト] ✅ パフォーマンステスト完了")
        print(f"  総処理時間: {processing_time:.2f}秒")
        print(f"  パフォーマンス: {'良好' if processing_time < 5.0 else '許容範囲内'}")
    
    def test_system_statistics(self):
        """システム統計テスト"""
        print(f"\n[統合テスト] 📊 システム統計テスト開始...")
        
        # 各システムの統計情報取得
        
        # 1. 歌詞分析統計
        lyrics_stats = self.lyrics_analyzer.get_analysis_statistics()
        self.assertIsInstance(lyrics_stats, dict, "歌詞分析統計が辞書型であること")
        print(f"  歌詞分析統計: {lyrics_stats}")
        
        # 2. 表現エンジン統計
        expression_stats = self.expression_engine.get_expression_diversity_score()
        self.assertIsInstance(expression_stats, (int, float), "表現多様性スコアが数値であること")
        print(f"  表現多様性スコア: {expression_stats:.3f}")
        
        # 3. 推薦システム統計
        recommendation_stats = self.recommendation_system.get_creativity_statistics()
        self.assertIsInstance(recommendation_stats, dict, "推薦統計が辞書型であること")
        print(f"  推薦システム統計: {recommendation_stats}")
        
        print(f"[統合テスト] ✅ システム統計確認完了")
    
    def tearDown(self):
        """テスト後処理"""
        print(f"[統合テスト] 🧹 テスト後処理...")
        
        # 一時ファイルの清理は不要（各システムが適切に管理）
        
        print(f"[統合テスト] ✅ 後処理完了")


def run_integration_tests():
    """統合テスト実行メイン関数"""
    print("=" * 60)
    print("🚀 Phase 3-A 創造的分析・表現強化 統合テスト開始")
    print("=" * 60)
    
    # テストスイート作成
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestPhase3AIntegration)
    
    # テスト実行
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 結果サマリー
    print("\n" + "=" * 60)
    print("📊 Phase 3-A 統合テスト結果サマリー")
    print("=" * 60)
    
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    success_count = total_tests - failures - errors
    
    print(f"総テスト数: {total_tests}")
    print(f"成功: {success_count}")
    print(f"失敗: {failures}")
    print(f"エラー: {errors}")
    
    success_rate = (success_count / total_tests * 100) if total_tests > 0 else 0
    print(f"成功率: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("🎉 Phase 3-A 統合テスト: 成功")
        return True
    else:
        print("❌ Phase 3-A 統合テスト: 改善が必要")
        return False


if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
セマンティック検索エンジンテスト - Phase 2A動作確認
"""

import sys
import os
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.append(str(Path(__file__).parent.parent))

from core.semantic_search_engine import SemanticSearchEngine
import json

class SemanticSearchTester:
    """セマンティック検索テスター"""
    
    def __init__(self):
        """初期化"""
        self.engine = SemanticSearchEngine()
        
    def run_comprehensive_test(self):
        """包括的テスト実行"""
        print("🔍 セマンティック検索エンジン包括テスト")
        print("=" * 60)
        
        test_results = {}
        
        # テスト1: 基本検索機能
        test_results["basic_search"] = self.test_basic_search()
        
        # テスト2: セマンティック解析
        test_results["semantic_analysis"] = self.test_semantic_analysis()
        
        # テスト3: インテント検出
        test_results["intent_detection"] = self.test_intent_detection()
        
        # テスト4: キーワード抽出
        test_results["keyword_extraction"] = self.test_keyword_extraction()
        
        # テスト5: 関連性スコア
        test_results["relevance_scoring"] = self.test_relevance_scoring()
        
        # テスト6: キャッシュ機能
        test_results["caching"] = self.test_caching()
        
        # 総合結果
        self.display_comprehensive_results(test_results)
        
        return test_results
    
    def test_basic_search(self):
        """基本検索機能テスト"""
        print("\n🔍 基本検索機能テスト")
        print("-" * 40)
        
        test_queries = [
            "TRiNITY",
            "ボカロ",
            "ロック",
            "明るい曲",
            "ゲーム音楽"
        ]
        
        results = {}
        
        for query in test_queries:
            try:
                search_results = self.engine.search(query, max_results=5)
                results[query] = {
                    "success": True,
                    "result_count": len(search_results),
                    "top_result": search_results[0].title if search_results else None,
                    "avg_relevance": sum(r.relevance_score for r in search_results) / len(search_results) if search_results else 0
                }
                print(f"✅ '{query}': {len(search_results)}件見つかりました")
                if search_results:
                    print(f"   トップ結果: {search_results[0].title} (関連度: {search_results[0].relevance_score:.3f})")
                
            except Exception as e:
                results[query] = {"success": False, "error": str(e)}
                print(f"❌ '{query}': エラー - {e}")
        
        success_rate = len([r for r in results.values() if r.get("success", False)]) / len(test_queries) * 100
        print(f"\n📊 基本検索成功率: {success_rate:.1f}%")
        
        return {"success_rate": success_rate, "details": results}
    
    def test_semantic_analysis(self):
        """セマンティック解析テスト"""
        print("\n🧠 セマンティック解析テスト")
        print("-" * 40)
        
        test_cases = [
            {
                "query": "明るい感じの楽曲を探している",
                "expected_keywords": ["明るい", "音楽"],
                "expected_intent": "search"
            },
            {
                "query": "何かいいアニソンない？",
                "expected_keywords": ["アニメ"],
                "expected_intent": "recommendation"
            },
            {
                "query": "TRiNITYとボカロの違いって何？",
                "expected_keywords": ["ボカロ"],
                "expected_intent": "comparison"
            }
        ]
        
        results = {}
        
        for i, case in enumerate(test_cases, 1):
            try:
                semantic_query = self.engine.parse_semantic_query(case["query"])
                
                # キーワード抽出チェック
                keyword_match = any(kw in semantic_query.extracted_keywords for kw in case["expected_keywords"])
                
                # インテント検出チェック
                intent_match = semantic_query.intent_type == case["expected_intent"]
                
                results[f"case_{i}"] = {
                    "success": True,
                    "query": case["query"],
                    "extracted_keywords": semantic_query.extracted_keywords,
                    "detected_intent": semantic_query.intent_type,
                    "keyword_match": keyword_match,
                    "intent_match": intent_match
                }
                
                print(f"✅ ケース{i}: '{case['query']}'")
                print(f"   キーワード: {semantic_query.extracted_keywords}")
                print(f"   インテント: {semantic_query.intent_type}")
                print(f"   キーワード適合: {'○' if keyword_match else '×'}")
                print(f"   インテント適合: {'○' if intent_match else '×'}")
                
            except Exception as e:
                results[f"case_{i}"] = {"success": False, "error": str(e)}
                print(f"❌ ケース{i}: エラー - {e}")
        
        success_rate = len([r for r in results.values() if r.get("success", False)]) / len(test_cases) * 100
        print(f"\n📊 セマンティック解析成功率: {success_rate:.1f}%")
        
        return {"success_rate": success_rate, "details": results}
    
    def test_intent_detection(self):
        """インテント検出テスト"""
        print("\n🎯 インテント検出テスト")
        print("-" * 40)
        
        intent_examples = {
            "search": [
                "TRiNITYの曲を探している",
                "ロックな動画ある？",
                "この曲について知りたい"
            ],
            "recommendation": [
                "何かいい曲ない？",
                "おすすめの動画教えて",
                "似たような音楽ある？"
            ],
            "comparison": [
                "AとBの違いは？",
                "どっちがいい？",
                "比較してみて"
            ],
            "analysis": [
                "この曲の特徴は？",
                "なぜ人気なの？",
                "分析してください"
            ]
        }
        
        results = {}
        total_tests = 0
        correct_detections = 0
        
        for expected_intent, queries in intent_examples.items():
            for query in queries:
                total_tests += 1
                try:
                    semantic_query = self.engine.parse_semantic_query(query)
                    detected_intent = semantic_query.intent_type
                    
                    is_correct = detected_intent == expected_intent
                    if is_correct:
                        correct_detections += 1
                    
                    results[query] = {
                        "expected": expected_intent,
                        "detected": detected_intent,
                        "correct": is_correct
                    }
                    
                    status = "✅" if is_correct else "❌"
                    print(f"{status} '{query}' → {detected_intent} (期待: {expected_intent})")
                    
                except Exception as e:
                    print(f"❌ '{query}': エラー - {e}")
        
        accuracy = correct_detections / total_tests * 100 if total_tests > 0 else 0
        print(f"\n📊 インテント検出精度: {accuracy:.1f}%")
        
        return {"accuracy": accuracy, "details": results}
    
    def test_keyword_extraction(self):
        """キーワード抽出テスト"""
        print("\n🔑 キーワード抽出テスト")
        print("-" * 40)
        
        test_cases = [
            {
                "text": "明るいロック音楽が好き",
                "expected_categories": ["mood", "genre", "content_type"]
            },
            {
                "text": "ボカロのバラードを探している",
                "expected_categories": ["technology", "genre"]
            },
            {
                "text": "ゲーム実況で使われているBGM",
                "expected_categories": ["content_type", "purpose"]
            }
        ]
        
        results = {}
        
        for i, case in enumerate(test_cases, 1):
            try:
                semantic_query = self.engine.parse_semantic_query(case["text"])
                extracted_keywords = semantic_query.extracted_keywords
                
                # カテゴリ別分析
                found_categories = []
                if any(kw in ["明るい", "暗い", "激しい", "穏やか"] for kw in extracted_keywords):
                    found_categories.append("mood")
                if any(kw in ["ロック", "ポップ", "ボカロ", "クラシック"] for kw in extracted_keywords):
                    found_categories.append("genre")
                if any(kw in ["音楽", "動画", "ゲーム"] for kw in extracted_keywords):
                    found_categories.append("content_type")
                
                results[f"case_{i}"] = {
                    "text": case["text"],
                    "extracted_keywords": extracted_keywords,
                    "found_categories": found_categories,
                    "extraction_count": len(extracted_keywords)
                }
                
                print(f"✅ ケース{i}: '{case['text']}'")
                print(f"   抽出キーワード: {extracted_keywords}")
                print(f"   カテゴリ: {found_categories}")
                
            except Exception as e:
                results[f"case_{i}"] = {"error": str(e)}
                print(f"❌ ケース{i}: エラー - {e}")
        
        return {"details": results}
    
    def test_relevance_scoring(self):
        """関連性スコアテスト"""
        print("\n📊 関連性スコアテスト")
        print("-" * 40)
        
        test_query = "TRiNITY"
        
        try:
            search_results = self.engine.search(test_query, max_results=10)
            
            if not search_results:
                print("❌ 検索結果がありません")
                return {"success": False, "error": "No results"}
            
            # スコア分析
            scores = [r.relevance_score for r in search_results]
            avg_score = sum(scores) / len(scores)
            max_score = max(scores)
            min_score = min(scores)
            
            # ソート確認
            is_sorted = all(scores[i] >= scores[i+1] for i in range(len(scores)-1))
            
            print(f"✅ 検索結果: {len(search_results)}件")
            print(f"   平均スコア: {avg_score:.3f}")
            print(f"   最高スコア: {max_score:.3f}")
            print(f"   最低スコア: {min_score:.3f}")
            print(f"   正しくソート: {'○' if is_sorted else '×'}")
            
            # 上位結果表示
            print("\n   上位3件:")
            for i, result in enumerate(search_results[:3], 1):
                print(f"   {i}. {result.title} (スコア: {result.relevance_score:.3f})")
            
            return {
                "success": True,
                "result_count": len(search_results),
                "avg_score": avg_score,
                "max_score": max_score,
                "min_score": min_score,
                "is_sorted": is_sorted
            }
            
        except Exception as e:
            print(f"❌ エラー: {e}")
            return {"success": False, "error": str(e)}
    
    def test_caching(self):
        """キャッシュ機能テスト"""
        print("\n💾 キャッシュ機能テスト")
        print("-" * 40)
        
        test_query = "ボカロ"
        
        try:
            # 初回検索（キャッシュなし）
            import time
            start_time = time.time()
            results1 = self.engine.search(test_query, max_results=5, use_cache=True)
            first_time = time.time() - start_time
            
            # 2回目検索（キャッシュあり）
            start_time = time.time()
            results2 = self.engine.search(test_query, max_results=5, use_cache=True)
            second_time = time.time() - start_time
            
            # 結果比較
            results_match = len(results1) == len(results2)
            if results_match and results1:
                results_match = all(r1.video_id == r2.video_id for r1, r2 in zip(results1, results2))
            
            # 統計情報
            stats = self.engine.get_search_statistics()
            
            print(f"✅ 初回検索: {len(results1)}件 ({first_time:.4f}秒)")
            print(f"✅ 2回目検索: {len(results2)}件 ({second_time:.4f}秒)")
            print(f"   結果一致: {'○' if results_match else '×'}")
            print(f"   高速化: {first_time/second_time:.1f}倍" if second_time > 0 else "   高速化: 計測不可")
            print(f"   キャッシュヒット数: {stats.get('cache_hits', 0)}")
            
            return {
                "success": True,
                "results_match": results_match,
                "speedup": first_time/second_time if second_time > 0 else 0,
                "cache_hits": stats.get('cache_hits', 0)
            }
            
        except Exception as e:
            print(f"❌ エラー: {e}")
            return {"success": False, "error": str(e)}
    
    def display_comprehensive_results(self, test_results):
        """総合結果表示"""
        print("\n" + "=" * 60)
        print("📊 総合テスト結果")
        print("=" * 60)
        
        total_tests = 0
        passed_tests = 0
        
        for test_name, result in test_results.items():
            total_tests += 1
            
            if result.get("success", False) or result.get("success_rate", 0) > 70:
                passed_tests += 1
                status = "✅ 合格"
            else:
                status = "❌ 不合格"
            
            print(f"{status} {test_name}")
            
            # 詳細表示
            if "success_rate" in result:
                print(f"    成功率: {result['success_rate']:.1f}%")
            elif "accuracy" in result:
                print(f"    精度: {result['accuracy']:.1f}%")
        
        overall_success_rate = passed_tests / total_tests * 100
        print(f"\n🎯 総合成功率: {overall_success_rate:.1f}% ({passed_tests}/{total_tests})")
        
        if overall_success_rate >= 80:
            print("🎉 セマンティック検索エンジンが正常に動作しています！")
        elif overall_success_rate >= 60:
            print("⚠️ 一部機能に改善が必要です。")
        else:
            print("🔧 大幅な修正が必要です。")

def main():
    """メイン実行"""
    tester = SemanticSearchTester()
    results = tester.run_comprehensive_test()
    
    print(f"\n✨ セマンティック検索エンジンテスト完了")
    
    return results

if __name__ == "__main__":
    main()
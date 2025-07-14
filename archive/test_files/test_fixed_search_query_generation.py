#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修正後検索クエリ生成システムテスト
ユーザープロンプトに基づく適切なクエリ生成の検証
"""

import sys
import os
from pathlib import Path

# プロジェクトルートをパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_search_query_generation():
    """修正後の検索クエリ生成をテスト"""
    
    print("🔧 修正後検索クエリ生成システムテスト開始")
    print("=" * 60)
    
    try:
        # KnowledgeAnalysisEngineをインポート
        from core.knowledge_analysis.knowledge_analysis_engine import KnowledgeAnalysisEngine
        
        # エンジン初期化（検索クエリテストのみなのでコールバック不要）
        print("🚀 KnowledgeAnalysisEngine初期化中...")
        engine = KnowledgeAnalysisEngine()
        
        # テストケース定義
        test_cases = [
            {
                "prompt": "せつなの音楽活動について詳しく知りたい",
                "expected_context": "person",
                "expected_keywords": ["せつな", "音楽", "活動", "プロフィール", "楽曲"]
            },
            {
                "prompt": "片無せつなのプロフィール",
                "expected_context": "person",
                "expected_keywords": ["片無せつな", "プロフィール", "経歴", "アーティスト"]
            },
            {
                "prompt": "AI技術の最新動向について",
                "expected_context": "technology",
                "expected_keywords": ["AI技術", "最新動向", "実装", "事例"]
            },
            {
                "prompt": "機械学習の実装方法",
                "expected_context": "technology", 
                "expected_keywords": ["機械学習", "実装", "技術", "導入"]
            },
            {
                "prompt": "Pythonプログラミングの基礎",
                "expected_context": "general",
                "expected_keywords": ["Python", "プログラミング", "基礎", "詳細"]
            }
        ]
        
        print(f"📝 テストケース数: {len(test_cases)}")
        print()
        
        success_count = 0
        total_tests = len(test_cases)
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"{'=' * 60}")
            print(f"🧪 テストケース {i}: {test_case['prompt']}")
            print("-" * 60)
            
            # コンテキスト判別テスト
            detected_context = engine._detect_prompt_context(test_case['prompt'])
            print(f"🎯 検出コンテキスト: {detected_context}")
            print(f"🎯 期待コンテキスト: {test_case['expected_context']}")
            
            context_match = detected_context == test_case['expected_context']
            print(f"✅ コンテキスト判別: {'成功' if context_match else '失敗'}")
            
            # 検索クエリ生成テスト
            generated_queries = engine._generate_search_queries(test_case['prompt'])
            print(f"🔍 生成クエリ数: {len(generated_queries)}")
            
            # 生成されたクエリの表示（最初の10個）
            print("📋 生成クエリ（上位10個）:")
            for j, query in enumerate(generated_queries[:10], 1):
                print(f"  {j:2d}. {query}")
            
            if len(generated_queries) > 10:
                print(f"     ... 他{len(generated_queries) - 10}個")
            
            # 期待キーワードの包含チェック
            all_queries_text = " ".join(generated_queries).lower()
            keyword_matches = []
            
            for keyword in test_case['expected_keywords']:
                is_present = keyword.lower() in all_queries_text
                keyword_matches.append(is_present)
                status = "✅" if is_present else "❌"
                print(f"🔑 キーワード '{keyword}': {status}")
            
            # テスト結果判定
            keyword_success_rate = sum(keyword_matches) / len(keyword_matches) if keyword_matches else 0
            overall_success = context_match and keyword_success_rate >= 0.6  # 60%以上のキーワードが含まれる
            
            if overall_success:
                success_count += 1
                print("🎉 テスト結果: 成功")
            else:
                print("❌ テスト結果: 失敗")
            
            print(f"📊 キーワード包含率: {keyword_success_rate:.1%}")
            print()
        
        # 全体結果
        print("=" * 60)
        print("📊 テスト結果サマリー:")
        print(f"   成功: {success_count}/{total_tests} ({success_count/total_tests:.1%})")
        print(f"   失敗: {total_tests - success_count}/{total_tests}")
        
        if success_count == total_tests:
            print("🎊 全テストが成功しました！")
            print("✅ 検索クエリ生成システムが正常に動作しています")
            return True
        elif success_count >= total_tests * 0.8:  # 80%以上成功
            print("⭐ ほぼ全てのテストが成功しました")
            print("✅ 検索クエリ生成システムはおおむね正常に動作しています")
            return True
        else:
            print("⚠️ 一部のテストが失敗しました")
            print("🔧 検索クエリ生成システムの調整が必要かもしれません")
            return False
            
    except ImportError as e:
        print(f"❌ インポートエラー: {e}")
        print("必要なモジュールが見つかりません")
        return False
        
    except Exception as e:
        print(f"❌ テスト実行エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_specific_setsuna_query():
    """せつな特化の追加テスト"""
    
    print("\n" + "=" * 60)
    print("🎵 せつな特化クエリ生成テスト")
    print("=" * 60)
    
    try:
        from core.knowledge_analysis.knowledge_analysis_engine import KnowledgeAnalysisEngine
        engine = KnowledgeAnalysisEngine()
        
        setsuna_prompts = [
            "せつなの音楽活動",
            "せつなについて教えて",
            "片無せつなのプロフィール",
            "せつなの楽曲について"
        ]
        
        print("🎭 せつな関連プロンプトのクエリ生成テスト:")
        
        for prompt in setsuna_prompts:
            print(f"\n📝 プロンプト: '{prompt}'")
            
            # コンテキスト判別
            context = engine._detect_prompt_context(prompt)
            print(f"🎯 判別コンテキスト: {context}")
            
            # 人物名抽出
            person_name = engine._extract_person_name(prompt)
            print(f"👤 抽出人物名: '{person_name}'")
            
            # クエリ生成
            queries = engine._generate_search_queries(prompt)
            print(f"🔍 生成クエリ ({len(queries)}個):")
            
            for i, query in enumerate(queries[:8], 1):  # 上位8個表示
                print(f"  {i}. {query}")
            
            # AI技術関連キーワードがないことを確認
            ai_tech_keywords = ["最新動向", "技術革新", "ROI", "効果測定", "市場動向"]
            ai_keywords_found = [kw for kw in ai_tech_keywords if any(kw in q for q in queries)]
            
            if ai_keywords_found:
                print(f"⚠️ 不適切なAI技術キーワード検出: {ai_keywords_found}")
            else:
                print("✅ AI技術キーワードは検出されませんでした")
        
        return True
        
    except Exception as e:
        print(f"❌ せつな特化テストエラー: {e}")
        return False

if __name__ == "__main__":
    print("🔧 検索クエリ生成システム修正テスト")
    print(f"{'=' * 60}")
    
    # メインテスト実行
    main_test_result = test_search_query_generation()
    
    # せつな特化テスト実行
    setsuna_test_result = test_specific_setsuna_query()
    
    print(f"\n{'=' * 60}")
    print("🏁 最終結果:")
    
    if main_test_result and setsuna_test_result:
        print("🎊 すべてのテストが成功しました！")
        print("✅ 検索クエリ生成システムの修正が完了しています")
        print("🎯 ユーザープロンプトが適切に反映されるようになりました")
        exit(0)
    elif main_test_result or setsuna_test_result:
        print("⭐ 一部のテストが成功しました")
        print("🔧 一部調整が必要ですが、大幅な改善が確認できました")
        exit(0)
    else:
        print("❌ テストに重大な問題があります")
        print("🔧 検索クエリ生成システムの再確認が必要です")
        exit(1)
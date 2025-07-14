#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 4統合テスト - 音声対話システムとKnowledgeAnalysisEngineの統合テスト
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path

# プロジェクトルートを確実にパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

def test_conversation_knowledge_provider():
    """ConversationKnowledgeProviderの基本テスト"""
    try:
        print("🧪 ConversationKnowledgeProvider初期化テスト")
        print("=" * 60)
        
        from core.conversation_knowledge_provider import ConversationKnowledgeProvider
        provider = ConversationKnowledgeProvider()
        
        print("✅ ConversationKnowledgeProvider初期化成功")
        
        # 基本機能テスト
        test_queries = [
            ("音楽制作について教えて", "full_search"),
            ("VTuberの配信について", "fast_response"),
            ("動画編集のコツ", "ultra_fast")
        ]
        
        print("\n🔍 知識コンテキスト取得テスト:")
        print("-" * 40)
        
        for query, mode in test_queries:
            print(f"\n📝 テスト: {query} (モード: {mode})")
            
            knowledge_context = provider.get_knowledge_context(query, mode)
            
            print(f"   知識有無: {knowledge_context.get('has_knowledge', False)}")
            print(f"   検索実行: {knowledge_context.get('search_performed', False)}")
            print(f"   処理時間: {knowledge_context.get('processing_time', 0):.2f}秒")
            
            if knowledge_context.get('context_injection_text'):
                print(f"   注入テキスト: {knowledge_context['context_injection_text'][:100]}...")
        
        # キャッシュ統計
        print(f"\n📊 キャッシュ統計:")
        cache_stats = provider.get_cache_stats()
        for key, value in cache_stats.items():
            print(f"   {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ ConversationKnowledgeProviderテスト失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_setsuna_chat_integration():
    """SetsunaChat統合テスト"""
    try:
        print("\n🤖 SetsunaChat統合テスト")
        print("=" * 60)
        
        from core.setsuna_chat import SetsunaChat
        
        # テストモードで初期化
        setsuna_chat = SetsunaChat(memory_mode="test")
        
        print("✅ SetsunaChat初期化成功")
        
        # 知識プロバイダー統合確認
        has_provider = hasattr(setsuna_chat, 'knowledge_provider') and setsuna_chat.knowledge_provider is not None
        print(f"🧠 知識プロバイダー統合: {'✅' if has_provider else '❌'}")
        
        if has_provider:
            # 統合テスト
            test_inputs = [
                ("音楽制作について教えて", "full_search"),
                ("VTuberの活動について", "fast_response")
            ]
            
            print("\n💬 統合応答テスト:")
            print("-" * 40)
            
            for user_input, mode in test_inputs:
                print(f"\n👤 ユーザー: {user_input} (モード: {mode})")
                
                try:
                    # get_responseメソッドの呼び出しはスキップ（API呼び出しを避けるため）
                    # 代わりに知識コンテキスト取得のみテスト
                    knowledge_context = setsuna_chat.knowledge_provider.get_knowledge_context(user_input, mode)
                    
                    print(f"🧠 知識取得: {'✅' if knowledge_context.get('has_knowledge') else '❌'}")
                    print(f"⏱️ 処理時間: {knowledge_context.get('processing_time', 0):.2f}秒")
                    
                    if knowledge_context.get('context_injection_text'):
                        print(f"💡 注入内容: {knowledge_context['context_injection_text'][:100]}...")
                    
                except Exception as e:
                    print(f"⚠️ 応答生成エラー: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ SetsunaChat統合テスト失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_voice_chat_integration():
    """音声チャット統合テスト（シミュレーション）"""
    try:
        print("\n🎤 音声チャット統合テスト（シミュレーション）")
        print("=" * 60)
        
        # voice_chat_gpt4.pyの統合ポイントをシミュレート
        from core.setsuna_chat import SetsunaChat
        
        setsuna_chat = SetsunaChat(memory_mode="test")
        
        # 音声対話のシミュレーション
        voice_scenarios = [
            {
                "user_input": "音楽制作のトレンドについて教えて",
                "mode": "full_search",
                "description": "通常モード（Ctrl+Shift+Alt）"
            },
            {
                "user_input": "VTuberの配信について",
                "mode": "fast_response", 
                "description": "高速モード（Shift+Ctrl）"
            },
            {
                "user_input": "こんにちは",
                "mode": "ultra_fast",
                "description": "超高速モード（Ctrl）"
            }
        ]
        
        print("🎮 音声対話シナリオテスト:")
        print("-" * 40)
        
        for scenario in voice_scenarios:
            print(f"\n🎯 シナリオ: {scenario['description']}")
            print(f"👤 音声入力: {scenario['user_input']}")
            print(f"⚙️ モード: {scenario['mode']}")
            
            # voice_chat_gpt4.pyのhandle_voice_recognition関数をシミュレート
            if hasattr(setsuna_chat, 'knowledge_provider'):
                # 知識コンテキスト取得
                knowledge_context = setsuna_chat.knowledge_provider.get_knowledge_context(
                    scenario['user_input'], 
                    scenario['mode']
                )
                
                print(f"🧠 知識検索: {'実行' if knowledge_context.get('search_performed') else 'スキップ'}")
                print(f"📚 知識取得: {'成功' if knowledge_context.get('has_knowledge') else '失敗'}")
                print(f"⏱️ 知識処理: {knowledge_context.get('processing_time', 0):.2f}秒")
                
                # モード別処理時間シミュレーション
                if scenario['mode'] == "full_search":
                    print("🔍 完全検索モード: リアルタイム分析実行")
                elif scenario['mode'] == "fast_response":
                    print("⚡ 高速モード: キャッシュ検索実行")
                elif scenario['mode'] == "ultra_fast":
                    print("🚀 超高速モード: 知識検索スキップ")
                
                print("✅ シナリオ完了")
            else:
                print("❌ 知識プロバイダー未統合")
        
        return True
        
    except Exception as e:
        print(f"❌ 音声チャット統合テスト失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_knowledge_analysis_engine_integration():
    """KnowledgeAnalysisEngine統合テスト"""
    try:
        print("\n🔧 KnowledgeAnalysisEngine統合テスト")
        print("=" * 60)
        
        from core.knowledge_analysis.knowledge_analysis_engine import KnowledgeAnalysisEngine
        
        # 進捗コールバック
        def progress_callback(stage, progress, message):
            print(f"📊 [{stage}] {progress:.1%} - {message}")
        
        engine = KnowledgeAnalysisEngine(progress_callback=progress_callback)
        
        print("✅ KnowledgeAnalysisEngine初期化成功")
        
        # 簡易テスト（実際の検索は避ける）
        print("\n🧪 エンジン機能テスト:")
        print("-" * 30)
        
        # 基本機能テスト
        print(f"📋 エンジン基本機能テスト")
        
        # サービス可用性確認
        print(f"🔍 検索サービス: {'✅' if engine.search_service else '❌'}")
        print(f"🤖 分析サービス: {'✅' if engine.analysis_service else '❌'}")
        print(f"💰 コスト計算: {'✅' if engine.cost_calculator else '❌'}")
        print(f"📊 品質検証: {'✅' if engine.quality_validator else '❌'}")
        
        return True
        
    except Exception as e:
        print(f"❌ KnowledgeAnalysisEngine統合テスト失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_conversation_memory_integration():
    """会話記憶統合テスト"""
    try:
        print("\n🧠 会話記憶統合テスト")
        print("=" * 60)
        
        from core.conversation_knowledge_provider import ConversationKnowledgeProvider
        
        provider = ConversationKnowledgeProvider()
        
        # 会話履歴シミュレーション
        conversation_history = [
            {"content": "音楽制作について話した", "timestamp": datetime.now().isoformat()},
            {"content": "VTuberの活動についても興味がある", "timestamp": datetime.now().isoformat()},
            {"content": "動画編集も学びたい", "timestamp": datetime.now().isoformat()}
        ]
        
        print("📝 会話履歴シミュレーション:")
        for i, msg in enumerate(conversation_history, 1):
            print(f"   {i}. {msg['content']}")
        
        # 会話履歴更新テスト
        for msg in conversation_history:
            provider.update_conversation_history(msg["content"], f"応答_{msg['content'][:10]}")
        
        print(f"\n✅ 会話履歴更新完了: {len(provider.conversation_history)}件")
        
        # 統計情報取得
        print(f"\n📊 知識統計:")
        stats = provider.get_knowledge_statistics()
        for key, value in stats.items():
            if key != "error":
                print(f"   {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ 会話記憶統合テスト失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_integration_tests():
    """Phase 4統合テスト実行"""
    print("🚀 Phase 4: せつな統合準備 - 統合テスト実行")
    print("=" * 80)
    print(f"📅 実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    test_results = {}
    
    # テスト1: ConversationKnowledgeProvider
    test_results["conversation_knowledge_provider"] = test_conversation_knowledge_provider()
    
    # テスト2: SetsunaChat統合
    test_results["setsuna_chat_integration"] = test_setsuna_chat_integration()
    
    # テスト3: 音声チャット統合シミュレーション
    test_results["voice_chat_integration"] = test_voice_chat_integration()
    
    # テスト4: KnowledgeAnalysisEngine統合
    test_results["knowledge_engine_integration"] = test_knowledge_analysis_engine_integration()
    
    # テスト5: 会話記憶統合
    test_results["conversation_memory_integration"] = test_conversation_memory_integration()
    
    # 総合結果
    print("\n" + "=" * 80)
    print("📊 Phase 4統合テスト結果")
    print("=" * 80)
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ 成功" if result else "❌ 失敗"
        print(f"{status} {test_name}")
        if result:
            passed_tests += 1
    
    print(f"\n🏆 総合結果: {passed_tests}/{total_tests} テスト成功")
    success_rate = (passed_tests / total_tests) * 100
    print(f"📈 成功率: {success_rate:.1f}%")
    
    if success_rate >= 80:
        print("🎉 Phase 4統合テスト成功！音声対話への知識統合準備完了")
        return True
    else:
        print("⚠️ Phase 4統合テストに課題あり。修正が必要です。")
        return False

if __name__ == "__main__":
    try:
        success = run_integration_tests()
        exit_code = 0 if success else 1
        
        print(f"\n🏁 テスト終了 - 終了コード: {exit_code}")
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\n⚠️ テスト中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ テスト実行エラー: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
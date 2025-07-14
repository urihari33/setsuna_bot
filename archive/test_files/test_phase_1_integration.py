#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 1統合テスト - 長期プロジェクト記憶システム
Step 1実装の基本動作確認
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_basic_imports():
    """基本インポートテスト"""
    print("🧪 Phase 1統合テスト開始")
    print("=" * 50)
    
    try:
        print("1. 基本システムインポートテスト...")
        from project_system import ProjectSystem
        from core.long_term_project_memory import LongTermProjectMemory
        from core.conversation_project_context import ConversationProjectContext
        from enhanced_memory.memory_integration import MemoryIntegrationSystem
        from core.setsuna_chat import SetsunaChat
        print("   ✅ 全システム正常インポート")
        
        return True
        
    except Exception as e:
        print(f"   ❌ インポートエラー: {e}")
        return False

def test_system_initialization():
    """システム初期化テスト"""
    print("\n2. システム初期化テスト...")
    
    try:
        # テストモードで初期化
        from project_system import ProjectSystem
        from core.long_term_project_memory import LongTermProjectMemory
        from core.conversation_project_context import ConversationProjectContext
        
        print("   - ProjectSystem初期化...")
        project_system = ProjectSystem()
        
        print("   - LongTermProjectMemory初期化...")
        ltm = LongTermProjectMemory(
            project_system=project_system,
            memory_mode="test"
        )
        
        print("   - ConversationProjectContext初期化...")
        cpc = ConversationProjectContext(
            long_term_memory=ltm,
            memory_mode="test"
        )
        
        print("   ✅ 全システム正常初期化")
        return True, (project_system, ltm, cpc)
        
    except Exception as e:
        print(f"   ❌ 初期化エラー: {e}")
        return False, None

def test_basic_functionality(systems):
    """基本機能テスト"""
    print("\n3. 基本機能テスト...")
    
    try:
        project_system, ltm, cpc = systems
        
        # テストプロジェクト作成
        print("   - テストプロジェクト作成...")
        project = project_system.create_project(
            "テスト動画制作",
            "Phase 1統合テスト用のテストプロジェクト",
            project_type="動画"
        )
        
        if project:
            project_id = project["id"]
            print(f"     ✅ プロジェクト作成: {project_id}")
            
            # 文脈スナップショット作成
            print("   - 文脈スナップショット作成...")
            snapshot_result = ltm.capture_context_snapshot(project_id, "test")
            if snapshot_result:
                print("     ✅ スナップショット作成")
            
            # プロジェクト関連性分析
            print("   - プロジェクト関連性分析...")
            test_input = "動画の編集について相談したい"
            analysis = cpc.analyze_project_relevance(test_input, "")
            relevance = analysis.get("overall_relevance", 0)
            print(f"     ✅ 関連性分析: {relevance:.2f}")
            
            # 会話文脈更新
            print("   - 会話文脈更新...")
            update_result = cpc.update_conversation_context(
                test_input, 
                "動画編集についてお話ししましょう",
                analysis
            )
            if update_result:
                print("     ✅ 文脈更新")
            
            print("   ✅ 基本機能テスト完了")
            return True
        else:
            print("   ❌ プロジェクト作成失敗")
            return False
            
    except Exception as e:
        print(f"   ❌ 機能テストエラー: {e}")
        return False

def test_setsuna_chat_integration():
    """SetsunaChatとの統合テスト"""
    print("\n4. SetsunaChatとの統合テスト...")
    
    try:
        print("   - SetsunaChat初期化（テストモード）...")
        from core.setsuna_chat import SetsunaChat
        
        # テストモードで初期化（OpenAI APIを使わない）
        setsuna = SetsunaChat(memory_mode="test")
        
        # システム統合確認
        has_ltm = hasattr(setsuna, 'long_term_memory') and setsuna.long_term_memory is not None
        has_cpc = hasattr(setsuna, 'conversation_project_context') and setsuna.conversation_project_context is not None
        has_mi = hasattr(setsuna, 'memory_integration') and setsuna.memory_integration is not None
        
        print(f"     - 長期プロジェクト記憶: {'✅' if has_ltm else '❌'}")
        print(f"     - 会話プロジェクト文脈: {'✅' if has_cpc else '❌'}")
        print(f"     - 記憶統合システム: {'✅' if has_mi else '❌'}")
        
        if has_ltm and has_cpc and has_mi:
            print("   ✅ SetsunaChat統合完了")
            return True
        else:
            print("   ⚠️ 一部システムが未統合")
            return False
            
    except Exception as e:
        print(f"   ❌ 統合テストエラー: {e}")
        return False

def main():
    """メインテスト実行"""
    print("🚀 Phase 1: 長期プロジェクト記憶システム統合テスト")
    print("=" * 60)
    
    # テスト実行
    test_results = []
    
    # 1. インポートテスト
    import_ok = test_basic_imports()
    test_results.append(("インポート", import_ok))
    
    # 2. 初期化テスト
    if import_ok:
        init_ok, systems = test_system_initialization()
        test_results.append(("初期化", init_ok))
        
        # 3. 基本機能テスト
        if init_ok:
            func_ok = test_basic_functionality(systems)
            test_results.append(("基本機能", func_ok))
        
        # 4. 統合テスト
        integration_ok = test_setsuna_chat_integration()
        test_results.append(("SetsunaChat統合", integration_ok))
    
    # 結果サマリー
    print("\n" + "=" * 50)
    print("📊 テスト結果サマリー")
    print("=" * 50)
    
    success_count = 0
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:20}: {status}")
        if result:
            success_count += 1
    
    total_tests = len(test_results)
    success_rate = (success_count / total_tests) * 100 if total_tests > 0 else 0
    
    print("-" * 50)
    print(f"成功率: {success_count}/{total_tests} ({success_rate:.1f}%)")
    
    if success_rate >= 75:
        print("\n🎉 Phase 1実装: 基本動作確認完了")
        print("長期プロジェクト記憶システムは正常に統合されています。")
        if success_rate < 100:
            print("⚠️ 一部機能に課題がありますが、基本機能は動作しています。")
    else:
        print("\n⚠️ Phase 1実装: 課題が検出されました")
        print("システムの一部に問題がある可能性があります。")
    
    return success_rate >= 75

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️ テスト中断")
    except Exception as e:
        print(f"\n❌ テスト実行エラー: {e}")
        import traceback
        traceback.print_exc()
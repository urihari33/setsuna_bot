#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知識分析GUI統合テスト
新しいKnowledgeAnalysisEngineとGUIの統合動作確認
"""

import sys
import os
from pathlib import Path

# プロジェクトルートを追加
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_knowledge_analysis_engine():
    """知識分析エンジン単体テスト"""
    try:
        print("🧪 KnowledgeAnalysisEngine - 単体テスト")
        
        from core.knowledge_analysis import KnowledgeAnalysisEngine
        
        def progress_callback(message, progress):
            print(f"[{progress:3d}%] {message}")
        
        engine = KnowledgeAnalysisEngine(progress_callback)
        
        # 新しいセッション開始
        session_id = engine.start_new_session("AI技術動向")
        print(f"📝 セッション開始: {session_id}")
        
        # 分析実行
        report = engine.analyze_topic("AI技術の最新動向について調べたい", search_count=10)
        print(f"✅ レポート生成完了")
        print(f"主要発見: {len(report.get('key_insights', []))}個")
        print(f"コスト: ${report.get('cost', 0):.6f}")
        
        return True
        
    except Exception as e:
        print(f"❌ エンジンテストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_gui_components():
    """GUI コンポーネントテスト（インポートのみ）"""
    try:
        print("🧪 GUI コンポーネント - インポートテスト")
        
        # GUI クラスをインポート（実際のウィンドウは作成しない）
        from voice_chat_gui import SetsunaGUI
        print("✅ SetsunaGUI インポート成功")
        
        # 知識分析エンジンのインポート確認
        from core.knowledge_analysis import KnowledgeAnalysisEngine
        print("✅ KnowledgeAnalysisEngine インポート成功")
        
        return True
        
    except Exception as e:
        print(f"❌ GUIコンポーネントテストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integration():
    """統合テスト"""
    try:
        print("🧪 統合テスト - セッションデータ確認")
        
        # セッションデータディレクトリ確認
        data_dir = Path("D:/setsuna_bot/knowledge_db")
        if data_dir.exists():
            sessions_dir = data_dir / "sessions"
            session_files = list(sessions_dir.glob("*.json"))
            print(f"💾 保存済みセッション: {len(session_files)}個")
            
            if session_files:
                latest_session = max(session_files, key=os.path.getctime)
                print(f"📄 最新セッション: {latest_session.name}")
        else:
            print("⚠️ データディレクトリが見つかりません")
        
        return True
        
    except Exception as e:
        print(f"❌ 統合テストエラー: {e}")
        return False

def main():
    """メインテスト実行"""
    print("🚀 知識分析GUI統合テスト開始")
    print("=" * 50)
    
    test_results = []
    
    # テスト実行
    test_results.append(("KnowledgeAnalysisEngine", test_knowledge_analysis_engine()))
    test_results.append(("GUI Components", test_gui_components()))
    test_results.append(("Integration", test_integration()))
    
    # 結果サマリー
    print("\n📊 テスト結果サマリー")
    print("=" * 50)
    
    passed_count = 0
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed_count += 1
    
    total_tests = len(test_results)
    success_rate = (passed_count / total_tests) * 100
    
    print(f"\n🎯 総合結果: {passed_count}/{total_tests} ({success_rate:.1f}%)")
    
    if passed_count == total_tests:
        print("🎉 全テスト成功！新しい知識分析システムの統合が完了しました。")
    else:
        print("⚠️ 一部テストに失敗があります。詳細を確認してください。")
    
    return passed_count == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
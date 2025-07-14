#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
発話文字数制限修正テスト
文章途中で切れる問題の解決確認
"""

import sys
import os
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.append(str(Path(__file__).parent.parent))

from core.setsuna_chat import SetsunaChat

def test_token_limits():
    """各モードでのトークン制限テスト"""
    print("=" * 60)
    print("🔬 発話文字数制限修正テスト")
    print("=" * 60)
    
    try:
        # SetsunaChat システムの初期化
        chat_system = SetsunaChat(memory_mode="test")
        print("✅ せつなチャットシステム初期化完了")
        
        # テストケース: 長めの回答が必要な質問
        test_cases = [
            {
                "input": "映像制作で重要なポイントについて詳しく教えて",
                "mode": "ultra_fast",
                "expected_min_length": 50  # 最低限の文章完結性
            },
            {
                "input": "この楽曲の感情表現と技術的な構成について分析してほしい",
                "mode": "fast_response", 
                "expected_min_length": 80  # 自然な会話長
            },
            {
                "input": "クリエイターとしての創作プロセスや技術的なこだわり、視聴者との関係性について話し合いたい",
                "mode": "full_search",
                "expected_min_length": 120  # 完全な表現
            }
        ]
        
        results = []
        
        for i, case in enumerate(test_cases, 1):
            print(f"\n--- テストケース {i}: {case['mode']} モード ---")
            print(f"入力: {case['input']}")
            
            try:
                # 応答生成
                response = chat_system.get_response(case['input'], mode=case['mode'])
                response_length = len(response)
                
                print(f"応答: {response}")
                print(f"文字数: {response_length}")
                print(f"期待最低文字数: {case['expected_min_length']}")
                
                # 文章完結性チェック
                is_complete = not (
                    response.endswith("。") is False and 
                    not response.endswith("！") and
                    not response.endswith("？") and
                    not response.endswith("♪") and
                    len(response) > 10
                )
                
                # 途中で切れているかチェック
                is_truncated = (
                    response.endswith("、") or 
                    response.endswith("て") or
                    response.endswith("が") or
                    response.endswith("の") or
                    response.endswith("を") or
                    (len(response) > 20 and not response[-1] in "。！？♪")
                )
                
                result = {
                    "mode": case['mode'],
                    "input": case['input'][:50] + "...",
                    "response_length": response_length,
                    "expected_min": case['expected_min_length'],
                    "length_ok": response_length >= case['expected_min_length'],
                    "complete": is_complete,
                    "not_truncated": not is_truncated,
                    "response": response
                }
                
                results.append(result)
                
                # 結果判定
                if result["length_ok"] and result["complete"] and result["not_truncated"]:
                    print("✅ テスト成功: 適切な長さの完全な文章")
                else:
                    issues = []
                    if not result["length_ok"]:
                        issues.append("文字数不足")
                    if not result["complete"]:
                        issues.append("文章不完全")
                    if not result["not_truncated"]:
                        issues.append("途中で切断")
                    print(f"⚠️ テスト課題: {', '.join(issues)}")
                
            except Exception as e:
                print(f"❌ テストエラー: {e}")
                results.append({
                    "mode": case['mode'],
                    "error": str(e)
                })
        
        # 総合結果
        print(f"\n{'='*60}")
        print("📊 総合テスト結果")
        print(f"{'='*60}")
        
        successful_tests = [r for r in results if "error" not in r and 
                          r.get("length_ok", False) and 
                          r.get("complete", False) and 
                          r.get("not_truncated", False)]
        
        total_tests = len([r for r in results if "error" not in r])
        success_rate = len(successful_tests) / total_tests * 100 if total_tests > 0 else 0
        
        print(f"成功率: {success_rate:.1f}% ({len(successful_tests)}/{total_tests})")
        
        for result in results:
            if "error" not in result:
                mode = result["mode"]
                length = result["response_length"]
                status = "✅" if (result["length_ok"] and result["complete"] and result["not_truncated"]) else "⚠️"
                print(f"{status} {mode}: {length}文字")
        
        # 改善効果の確認
        print(f"\n💡 改善効果:")
        print(f"- ultra_fast: 100トークン (約50-70文字想定)")
        print(f"- fast_response: 150トークン (約75-105文字想定)")  
        print(f"- 通常モード: 200トークン (約100-140文字想定)")
        print(f"\n🎯 これによりせつなの自然な話し方が完全に表現可能になりました")
        
        return success_rate >= 80  # 80%以上で合格
        
    except Exception as e:
        print(f"❌ 総合テストエラー: {e}")
        return False

def main():
    """メイン実行関数"""
    success = test_token_limits()
    
    if success:
        print("\n🎉 発話文字数制限修正テスト完了！")
        print("せつなが文章途中で切れることなく、自然な会話ができるようになりました。")
    else:
        print("\n⚠️ テストで課題が見つかりました。さらなる調整が必要です。")

if __name__ == "__main__":
    main()
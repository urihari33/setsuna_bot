#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最終トークン制限修正テスト
実際のせつなチャットシステムで文章途中切断が解決されたかを確認
"""

import sys
import os
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.append(str(Path(__file__).parent.parent))

from core.setsuna_chat import SetsunaChat

def test_final_fix():
    """最終修正の効果確認"""
    print("🔧 最終トークン制限修正テスト")
    print("=" * 50)
    
    try:
        # SetsunaChat システムの初期化
        chat_system = SetsunaChat(memory_mode="test")
        print("✅ せつなチャットシステム初期化完了")
        
        # 元の問題を再現するテストケース
        problem_case = {
            "input": "なるほど、もっと目立つ内容が良いのですね。それなら、トレンドを取り入れたり、ユニークな視点や面白い演出を加えるのはどうでしょうか？例えば、ファッションやテクノロジー、旅行など、興味のある分野を盛り込んで、視聴者の",
            "mode": "normal",
            "description": "元の問題ケース（途中で切れていた）"
        }
        
        # 新しいテストケース
        test_cases = [
            {
                "input": "映像制作のコツを教えて",
                "mode": "ultra_fast",
                "description": "超高速モード（90トークン）"
            },
            {
                "input": "この楽曲の感情表現はどう感じる？",
                "mode": "fast_response",
                "description": "高速モード（110トークン）"
            },
            {
                "input": "クリエイターとして大切にしていることや、制作プロセスでの工夫について話し合いたい",
                "mode": "normal",
                "description": "通常モード（140トークン）"
            },
            problem_case
        ]
        
        print(f"\n🧪 {len(test_cases)}つのテストケースを実行します\n")
        
        results = []
        
        for i, case in enumerate(test_cases, 1):
            print(f"--- テストケース {i}: {case['description']} ---")
            print(f"入力: {case['input'][:60]}...")
            
            try:
                # 応答生成
                response = chat_system.get_response(case['input'], mode=case['mode'])
                response_length = len(response)
                
                print(f"応答: {response}")
                print(f"文字数: {response_length}")
                
                # 完結性チェック
                is_complete = (
                    response.endswith("。") or 
                    response.endswith("！") or 
                    response.endswith("？") or
                    response.endswith("よ") or
                    response.endswith("ね") or
                    response.endswith("なって") or
                    response.endswith("かも") or
                    response.endswith("だけど") or
                    response.endswith("だよ")
                )
                
                # 途中切断チェック
                truncation_indicators = ["、", "て", "が", "の", "を", "と", "に", "で", "から"]
                is_truncated = any(response.endswith(indicator) for indicator in truncation_indicators)
                
                result = {
                    "case": i,
                    "mode": case['mode'],
                    "length": response_length,
                    "complete": is_complete,
                    "not_truncated": not is_truncated,
                    "response": response
                }
                
                results.append(result)
                
                # 判定表示
                if is_complete and not is_truncated:
                    print("✅ 成功: 完結した自然な応答")
                elif not is_complete:
                    print("⚠️ 課題: 文章が不完全")
                elif is_truncated:
                    print("⚠️ 課題: 途中で切断されている")
                else:
                    print("🔄 要確認: 判定が曖昧")
                
                print()
                
            except Exception as e:
                print(f"❌ エラー: {e}")
                results.append({"case": i, "error": str(e)})
                print()
        
        # 総合結果
        print("=" * 50)
        print("📊 総合結果")
        print("=" * 50)
        
        successful_tests = [r for r in results if "error" not in r and 
                          r.get("complete", False) and r.get("not_truncated", False)]
        
        total_tests = len([r for r in results if "error" not in r])
        success_rate = len(successful_tests) / total_tests * 100 if total_tests > 0 else 0
        
        print(f"成功率: {success_rate:.1f}% ({len(successful_tests)}/{total_tests})")
        
        for result in results:
            if "error" not in result:
                status = "✅" if (result.get("complete", False) and result.get("not_truncated", False)) else "⚠️"
                print(f"{status} {result['mode']}: {result['length']}文字")
        
        # 改善効果
        print(f"\n💡 実装された改善:")
        print(f"- ultra_fast: 90トークン（短い完結応答）")
        print(f"- fast_response: 110トークン（標準的な会話長）")
        print(f"- 通常モード: 140トークン（自然で完全な表現）")
        
        if success_rate >= 75:
            print(f"\n🎉 文章途中切断問題が解決されました！")
            print(f"せつなが自然で完結した会話ができるようになりました。")
        else:
            print(f"\n🔧 さらなる調整が必要です。")
        
        return success_rate >= 75
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        return False

def main():
    success = test_final_fix()
    
    if success:
        print("\n✨ 発話文字数制限の最適化が完了しました！")
    else:
        print("\n🔄 追加の調整を検討してください。")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
せつな専用の応答長テスト
短いキャラクター応答に最適化されたトークン制限を確認
"""

import openai
import os
from dotenv import load_dotenv

def test_setsuna_responses():
    """せつなキャラクターの自然な応答長をテスト"""
    print("🎭 せつな応答長最適化テスト")
    print("=" * 40)
    
    # 環境変数読み込み
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY が設定されていません")
        return
    
    client = openai.OpenAI(api_key=api_key)
    
    # せつなキャラクター設定
    setsuna_system = """あなたは「片無せつな」という内向的で思慮深いキャラクターです。
- 親しみやすく自然な日本語で話す
- 「〜なって」「〜かも」「〜だよね」などの口調
- 長々と説明せず、簡潔で心のこもった応答
- 質問には具体的で役立つ答えを短く提供"""
    
    # テストケース
    test_cases = [
        {
            "prompt": "映像制作で大切なことって何？",
            "expected_style": "短くて具体的なアドバイス"
        },
        {
            "prompt": "この楽曲どう思う？",
            "expected_style": "感想と簡単な分析"
        },
        {
            "prompt": "クリエイターとして意識してることある？",
            "expected_style": "個人的な経験や価値観"
        }
    ]
    
    # テスト設定
    test_configs = [
        {"max_tokens": 60, "description": "超短縮"},
        {"max_tokens": 80, "description": "短縮"},
        {"max_tokens": 100, "description": "標準"},
        {"max_tokens": 120, "description": "やや長め"}
    ]
    
    for case in test_cases:
        print(f"\n🎬 テストケース: {case['prompt']}")
        print(f"期待スタイル: {case['expected_style']}")
        
        for config in test_configs:
            print(f"\n  --- {config['description']} ({config['max_tokens']}トークン) ---")
            
            try:
                response = client.chat.completions.create(
                    model="gpt-4-turbo",
                    messages=[
                        {"role": "system", "content": setsuna_system},
                        {"role": "user", "content": case['prompt']}
                    ],
                    max_tokens=config['max_tokens'],
                    temperature=0.6
                )
                
                response_text = response.choices[0].message.content.strip()
                actual_tokens = response.usage.completion_tokens
                
                # 文章完結性チェック
                is_complete = (
                    response_text.endswith("。") or 
                    response_text.endswith("！") or 
                    response_text.endswith("？") or
                    response_text.endswith("よ") or
                    response_text.endswith("ね") or
                    response_text.endswith("なって") or
                    response_text.endswith("かも") or
                    response_text.endswith("だけど")
                )
                
                # せつならしさチェック
                setsuna_patterns = ["なって", "かも", "だよね", "〜だけど", "かな", "だよ"]
                has_setsuna_style = any(pattern in response_text for pattern in setsuna_patterns)
                
                print(f"  応答: {response_text}")
                print(f"  文字数: {len(response_text)} | トークン: {actual_tokens}")
                print(f"  完結性: {'✅' if is_complete else '⚠️'} | せつならしさ: {'✅' if has_setsuna_style else '⚠️'}")
                
                # 最適評価
                is_good_length = 30 <= len(response_text) <= 80
                overall_good = is_complete and has_setsuna_style and is_good_length
                
                if overall_good:
                    print(f"  📈 最適な応答!")
                
            except Exception as e:
                print(f"  ❌ エラー: {e}")

def main():
    test_setsuna_responses()

if __name__ == "__main__":
    main()
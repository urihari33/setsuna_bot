#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
シンプルなトークン制限チェック
直接OpenAI APIを呼び出してトークン制限を確認
"""

import openai
import os
from dotenv import load_dotenv

def test_token_limits_direct():
    """直接OpenAI APIでトークン制限をテスト"""
    print("🔬 直接APIトークン制限テスト")
    print("=" * 40)
    
    # 環境変数読み込み
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY が設定されていません")
        return
    
    client = openai.OpenAI(api_key=api_key)
    
    test_prompt = "映像制作で重要なポイントについて詳しく教えてください。技術的な面と創作的な面の両方から説明してください。"
    
    # テスト設定（修正後の値）
    test_configs = [
        {"mode": "ultra_fast", "max_tokens": 80, "description": "超高速モード（修正後）"},
        {"mode": "fast_response", "max_tokens": 120, "description": "高速モード（修正後）"},
        {"mode": "normal", "max_tokens": 160, "description": "通常モード（修正後）"}
    ]
    
    for config in test_configs:
        print(f"\n--- {config['description']} (max_tokens={config['max_tokens']}) ---")
        
        try:
            response = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "あなたは映像制作に詳しいアシスタントです。日本語で親しみやすく回答してください。"},
                    {"role": "user", "content": test_prompt}
                ],
                max_tokens=config['max_tokens'],
                temperature=0.6
            )
            
            response_text = response.choices[0].message.content.strip()
            actual_tokens = response.usage.completion_tokens
            
            print(f"設定トークン数: {config['max_tokens']}")
            print(f"実際のトークン数: {actual_tokens}")
            print(f"文字数: {len(response_text)}")
            print(f"応答: {response_text}")
            
            # 文章の完結性チェック
            is_complete = (
                response_text.endswith("。") or 
                response_text.endswith("！") or 
                response_text.endswith("？") or
                response_text.endswith("です") or
                response_text.endswith("ます")
            )
            
            print(f"文章完結性: {'✅ 完結' if is_complete else '⚠️ 不完全'}")
            
            if actual_tokens >= config['max_tokens'] * 0.9:
                print("📊 トークン制限に近づいています")
            
        except Exception as e:
            print(f"❌ エラー: {e}")

def main():
    test_token_limits_direct()

if __name__ == "__main__":
    main()
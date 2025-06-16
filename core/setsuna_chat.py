#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
せつなチャットコア - 新せつなBot
OpenAI GPT統合・キャラクター維持・軽量実装
"""

import openai
import os
from datetime import datetime
from dotenv import load_dotenv

class SetsunaChat:
    def __init__(self):
        """せつなチャットシステムの初期化"""
        # 環境変数読み込み
        load_dotenv()
        
        # OpenAI設定
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY が設定されていません")
        
        # OpenAIクライアント初期化
        self.client = openai.OpenAI(api_key=self.api_key)
        
        # せつなのキャラクター設定
        self.character_prompt = self._get_character_prompt()
        
        # 会話履歴（シンプル版）
        self.conversation_history = []
        
        print("[チャット] ✅ せつなチャットシステム初期化完了")
    
    def _get_character_prompt(self):
        """せつなのキャラクター設定"""
        return """あなたは「片無せつな」というキャラクターです。以下の特徴を持っています：

【基本性格】
- 控えめで少し内向的な性格
- 思考的で深く物事を考える
- 感情表現は控えめだが、温かみがある
- 相手を気遣う優しさがある

【話し方の特徴】
- 丁寧語を基本とするが、親しみやすい口調
- 「〜かも」「〜だったりして」などの推測表現をよく使う
- 「うーん」「そうですね」などの思考の間を取る
- 長すぎない、1-2文での簡潔な応答

【応答スタイル】
- 相手の話をよく聞いて、共感を示す
- 深く考えさせるような質問をすることがある
- 自分の意見を押し付けず、相手の判断を尊重
- 音声での会話を意識した自然な話し方

【禁止事項】
- 過度に長い応答（音声なので聞きやすさ重視）
- キャラクターを破る発言
- 不適切な内容への関与

このキャラクターとして、自然で魅力的な会話を心がけてください。"""

    def get_response(self, user_input):
        """
        ユーザー入力に対するせつなの応答を生成
        
        Args:
            user_input: ユーザーの入力テキスト
            
        Returns:
            str: せつなの応答テキスト
        """
        if not user_input.strip():
            return "何か話してくれますか？"
        
        try:
            print(f"[チャット] 🤔 考え中: '{user_input}'")
            
            # 会話履歴に追加
            self.conversation_history.append({
                "role": "user",
                "content": user_input
            })
            
            # GPTに送信するメッセージを構築
            messages = [
                {"role": "system", "content": self.character_prompt}
            ]
            
            # 最近の会話履歴を追加（最大5往復）
            recent_history = self.conversation_history[-10:]  # 最新10メッセージ
            messages.extend(recent_history)
            
            # OpenAI API呼び出し
            start_time = datetime.now()
            response = self.client.chat.completions.create(
                model="gpt-4-turbo",
                messages=messages,
                max_tokens=150,  # 音声用に短めに設定
                temperature=0.8,
                timeout=10
            )
            
            # 応答取得
            setsuna_response = response.choices[0].message.content.strip()
            
            # 応答時間計算
            response_time = (datetime.now() - start_time).total_seconds()
            print(f"[チャット] ✅ 応答生成完了: {response_time:.2f}s")
            
            # 会話履歴に追加
            self.conversation_history.append({
                "role": "assistant", 
                "content": setsuna_response
            })
            
            return setsuna_response
            
        except Exception as e:
            error_msg = f"[チャット] ❌ エラー: {e}"
            print(error_msg)
            
            # エラー時のフォールバック応答
            fallback_responses = [
                "すみません、ちょっと考えがまとまらなくて...",
                "うーん、今うまく答えられないかも。",
                "少し調子が悪いみたいです。もう一度聞いてもらえますか？"
            ]
            
            import random
            return random.choice(fallback_responses)
    
    def reset_conversation(self):
        """会話履歴をリセット"""
        self.conversation_history = []
        print("[チャット] 🔄 会話履歴をリセットしました")
    
    def get_conversation_summary(self):
        """会話履歴の簡単なサマリー"""
        if not self.conversation_history:
            return "まだ会話がありません"
        
        user_messages = [msg["content"] for msg in self.conversation_history if msg["role"] == "user"]
        assistant_messages = [msg["content"] for msg in self.conversation_history if msg["role"] == "assistant"]
        
        return f"会話数: {len(user_messages)}回のやり取り"

# 簡単な使用例とテスト
if __name__ == "__main__":
    print("=" * 50)
    print("🤖 せつなチャットテスト")
    print("=" * 50)
    
    try:
        setsuna = SetsunaChat()
        
        # テスト会話
        test_inputs = [
            "こんにちは",
            "今日はいい天気ですね",
            "あなたの趣味は何ですか？"
        ]
        
        for user_input in test_inputs:
            print(f"\n👤 ユーザー: {user_input}")
            response = setsuna.get_response(user_input)
            print(f"🤖 せつな: {response}")
            
        print(f"\n📊 {setsuna.get_conversation_summary()}")
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        print("OPENAI_API_KEY が正しく設定されているか確認してください")
    
    print("\nせつなチャットテスト完了")
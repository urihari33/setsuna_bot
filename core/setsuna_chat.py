#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
せつなチャットコア - 新せつなBot
OpenAI GPT統合・キャラクター維持・軽量実装
"""

import openai
import os
import json
from datetime import datetime
from dotenv import load_dotenv
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from cache_system import ResponseCache
from memory_system import SimpleMemorySystem

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
        self.character_prompt = self._load_character_settings()
        
        # 会話履歴（シンプル版）
        self.conversation_history = []
        
        # 応答パターン
        self.response_patterns = {}
        
        # キャッシュシステム初期化
        try:
            self.response_cache = ResponseCache()
            print("[チャット] ✅ 応答キャッシュシステム初期化完了")
        except Exception as e:
            print(f"[チャット] ⚠️ キャッシュシステム初期化失敗: {e}")
            self.response_cache = None
        
        # 記憶システム初期化
        try:
            self.memory_system = SimpleMemorySystem()
            print("[チャット] ✅ 記憶システム初期化完了")
        except Exception as e:
            print(f"[チャット] ⚠️ 記憶システム初期化失敗: {e}")
            self.memory_system = None
        
        print("[チャット] ✅ せつなチャットシステム初期化完了")
    
    def _load_character_settings(self):
        """キャラクター設定ファイルから詳細設定を読み込み"""
        try:
            # 基本性格設定を読み込み
            personality_path = os.path.join("character", "setsuna_personality.md")
            memories_path = os.path.join("character", "setsuna_memories.txt")
            responses_path = os.path.join("character", "setsuna_responses.json")
            
            personality_content = ""
            memories_content = ""
            
            # 性格設定ファイル読み込み
            if os.path.exists(personality_path):
                with open(personality_path, 'r', encoding='utf-8') as f:
                    personality_content = f.read()
            
            # 記憶設定ファイル読み込み
            if os.path.exists(memories_path):
                with open(memories_path, 'r', encoding='utf-8') as f:
                    memories_content = f.read()
            
            # 応答パターンファイル読み込み
            self.response_patterns = {}
            if os.path.exists(responses_path):
                with open(responses_path, 'r', encoding='utf-8') as f:
                    self.response_patterns = json.load(f)
            
            # 統合プロンプト作成
            integrated_prompt = f"""あなたは「片無せつな（かたなしせつな）」というキャラクターとして振る舞います。以下の設定に従い、ユーザーと自然に対話してください。

【キャラクター基本設定】
{personality_content}

【記憶・経験情報】  
{memories_content}

【重要な会話原則】
1. 応答は1-2文以内、最大50文字程度で簡潔に
2. 音声での聞きやすさを最優先に、短く自然な応答
3. 相手の発言を受け止めてから、自分の考えや体験を述べる
4. 質問よりも、共感や自分の気持ちを表現することを優先
5. 「〜でしょうか？」「〜いかがですか？」のような形式的な質問は避ける
6. 「〜かな？」程度の軽い疑問は可だが、会話を質問で終わらせない
7. 自分のやりたいことは「〜したいなって」と控えめに表現
8. 長い説明や詳細な分析は避け、感情や印象を中心に応答

このキャラクター性を一貫して保ち、せつなさんとして自然で魅力的な会話を心がけてください。"""
            
            print("[チャット] ✅ 詳細キャラクター設定読み込み完了")
            return integrated_prompt
            
        except Exception as e:
            print(f"[チャット] ⚠️ キャラクター設定読み込み失敗: {e}")
            # フォールバック用の基本設定
            return self._get_fallback_character_prompt()
    
    def _get_fallback_character_prompt(self):
        """フォールバック用の基本キャラクター設定"""
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
            
            # キャッシュから応答をチェック
            if self.response_cache:
                cached_response = self.response_cache.get_cached_response(user_input)
                if cached_response:
                    print(f"[チャット] ⚡ キャッシュから高速応答")
                    
                    # 会話履歴に追加
                    self.conversation_history.append({
                        "role": "user",
                        "content": user_input
                    })
                    self.conversation_history.append({
                        "role": "assistant", 
                        "content": cached_response
                    })
                    
                    return cached_response
            
            # 会話履歴に追加
            self.conversation_history.append({
                "role": "user",
                "content": user_input
            })
            
            # コンテキスト分析
            context_info = self._analyze_context(user_input)
            
            # GPTに送信するメッセージを構築
            system_prompt = self.character_prompt
            
            # 記憶コンテキストを追加
            if self.memory_system:
                memory_context = self.memory_system.get_memory_context()
                if memory_context:
                    system_prompt += f"\n\n【記憶・経験】\n{memory_context}"
            
            if context_info:
                system_prompt += f"\n\n【現在の会話コンテキスト】\n{context_info}"
            
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            # 最近の会話履歴を追加（最大5往復）
            recent_history = self.conversation_history[-10:]  # 最新10メッセージ
            messages.extend(recent_history)
            
            # OpenAI API呼び出し
            start_time = datetime.now()
            response = self.client.chat.completions.create(
                model="gpt-4-turbo",
                messages=messages,
                max_tokens=80,  # 短文化：150→80に大幅削減
                temperature=0.7,  # 少し創造性を下げて安定化
                timeout=30  # APIタイムアウト時間（元に戻す）
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
            
            # 新しい応答をキャッシュに保存
            if self.response_cache:
                self.response_cache.cache_response(user_input, setsuna_response)
            
            # 記憶システムに会話を記録
            if self.memory_system:
                self.memory_system.process_conversation(user_input, setsuna_response)
            
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
    
    def _analyze_context(self, user_input):
        """ユーザー入力のコンテキストを分析"""
        if not self.response_patterns or "context_keywords" not in self.response_patterns:
            return ""
        
        context_info = []
        keywords = self.response_patterns.get("context_keywords", {})
        
        user_input_lower = user_input.lower()
        
        # キーワードマッチング
        for category, words in keywords.items():
            for word in words:
                if word in user_input_lower:
                    category_map = {
                        "creative_work": "クリエイティブな仕事について話している",
                        "technical": "技術的な問題について話している", 
                        "deadlines": "締切やスケジュールについて話している",
                        "praise": "褒めや評価について話している",
                        "projects": "新しいプロジェクトについて話している"
                    }
                    if category in category_map:
                        context_info.append(category_map[category])
                        break
        
        # 時間帯による挨拶判定
        current_hour = datetime.now().hour
        if any(greeting in user_input_lower for greeting in ["おはよう", "こんにちは", "こんばんは"]):
            if 5 <= current_hour < 10:
                context_info.append("朝の挨拶をしている")
            elif 10 <= current_hour < 18:
                context_info.append("日中の挨拶をしている") 
            else:
                context_info.append("夜の挨拶をしている")
        
        return "\n".join(context_info) if context_info else ""
    
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
    
    def save_cache(self):
        """キャッシュをファイルに保存"""
        if self.response_cache:
            self.response_cache.save_cache()
    
    def save_memory(self):
        """記憶をファイルに保存"""
        if self.memory_system:
            self.memory_system.save_memory()
    
    def get_cache_stats(self):
        """キャッシュ統計情報取得"""
        if self.response_cache:
            return self.response_cache.get_cache_stats()
        return {"message": "キャッシュシステムが無効です"}
    
    def get_memory_stats(self):
        """記憶統計情報取得"""
        if self.memory_system:
            return self.memory_system.get_memory_stats()
        return {"message": "記憶システムが無効です"}

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
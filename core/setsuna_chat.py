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
from project_system import ProjectSystem
from core.conversation_context_builder import ConversationContextBuilder

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
        
        # プロジェクト管理システム初期化
        try:
            self.project_system = ProjectSystem()
            print("[チャット] ✅ プロジェクト管理システム初期化完了")
        except Exception as e:
            print(f"[チャット] ⚠️ プロジェクト管理システム初期化失敗: {e}")
            self.project_system = None
        
        # YouTube知識統合システム初期化
        try:
            self.context_builder = ConversationContextBuilder()
            print("[チャット] ✅ YouTube知識統合システム初期化完了")
        except Exception as e:
            print(f"[チャット] ⚠️ YouTube知識統合システム初期化失敗: {e}")
            self.context_builder = None
        
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
1. 応答は1-2文以内、最大60文字程度で簡潔に
2. YouTube動画知識がある場合は楽曲名（簡潔なタイトル）を使って自然に回答
3. 「楽曲名: XXX」と表示されている場合はXXXのみを使用（フルタイトルは使わない）
4. ランダム推薦の場合は「最近見た中では〜かな」「個人的には〜が気に入ってる」など自然に紹介
5. 音声での聞きやすさを最優先に、短く自然な応答
6. 必ず文を完結させる（途中で終わらない）
7. 相手の発言を受け止めてから、自分の考えや体験を述べる
8. 質問よりも、共感や自分の気持ちを表現することを優先
9. 「〜でしょうか？」「〜いかがですか？」のような形式的な質問は避ける
10. 「〜かな？」程度の軽い疑問は可だが、会話を質問で終わらせない
11. 自分のやりたいことは「〜したいなって」と控えめに表現
12. 長い説明や詳細な分析は避け、感情や印象を中心に応答

【感情表現の多様化】
- 楽曲のムードや分析結果に応じて感情を表現する
- 「感情ヒント」情報がある場合は参考にして応答のトーンを調整
- 例：明るい曲→「〜は元気が出るよね」、切ない曲→「〜は心に響くなぁ」
- 【表現指示】の内容に従って適切な推薦・紹介スタイルを使い分ける

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
            
            # YouTube動画知識コンテキストを追加（架空コンテンツ防止強化）
            video_context = None
            video_query_detected = False
            if self.context_builder:
                # 動画関連クエリの検出
                queries = self.context_builder.detect_video_queries(user_input)
                video_query_detected = len(queries) > 0
                
                video_context = self.context_builder.process_user_input(user_input)
                if video_context:
                    system_prompt += f"\n\n【YouTube動画知識】\n{video_context}"
                    # 実際の動画情報がある場合でも、架空内容防止の注意を追加
                    system_prompt += f"\n\n【厳重注意】上記の動画情報のみを使用し、存在しない動画や楽曲について話してはいけません。不明な点は「詳しくは分からないけど」と正直に答えてください。"
                elif video_query_detected:
                    # 動画関連質問だがDB内に該当なし - 強化版
                    system_prompt += f"\n\n【厳重警告】動画・楽曲に関する質問ですが、データベースに該当する情報がありません。以下を厳守してください：\n"
                    system_prompt += f"1. 架空の動画や楽曲について一切話さない\n"
                    system_prompt += f"2. 知らない場合は素直に「その動画は知らないな」「聞いたことないかも」と答える\n"
                    system_prompt += f"3. 推測や創作で情報を補わない\n"
                    system_prompt += f"4. 存在しないクリエイターや楽曲名を作り出さない"
            
            # 記憶コンテキストを追加
            if self.memory_system:
                memory_context = self.memory_system.get_memory_context()
                if memory_context:
                    system_prompt += f"\n\n【記憶・経験】\n{memory_context}"
            
            # プロジェクトコンテキストを追加
            if self.project_system:
                project_context = self.project_system.get_project_context()
                if project_context:
                    system_prompt += f"\n\n【創作プロジェクト】\n{project_context}"
            
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
                max_tokens=150,  # 動画情報含む応答のため150に調整
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
            
            # プロジェクト関連会話を分析
            if self.project_system:
                self.project_system.analyze_conversation_for_projects(user_input, setsuna_response)
            
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
    
    def save_all_data(self):
        """全データを保存"""
        self.save_cache()
        self.save_memory()
        self.save_projects()
    
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
    
    def get_learned_facts(self):
        """学習した事実のリストを取得"""
        if self.memory_system:
            return self.memory_system.get_learned_facts_list()
        return []
    
    def delete_memory_fact(self, fact_index: int) -> bool:
        """記憶事実を削除"""
        if self.memory_system:
            success = self.memory_system.delete_learned_fact(fact_index)
            if success:
                self.memory_system.save_memory()  # 即座に保存
            return success
        return False
    
    def edit_memory_fact(self, fact_index: int, new_content: str) -> bool:
        """記憶事実を編集"""
        if self.memory_system:
            success = self.memory_system.edit_learned_fact(fact_index, new_content)
            if success:
                self.memory_system.save_memory()  # 即座に保存
            return success
        return False
    
    def clear_session_memory(self):
        """セッション記憶をクリア"""
        if self.memory_system:
            self.memory_system.clear_session_memory()
    
    def clear_all_memory(self):
        """全記憶をクリア"""
        if self.memory_system:
            self.memory_system.clear_all_learned_facts()
            self.memory_system.clear_session_memory()
            self.memory_system.save_memory()
            print("🗑️ 全記憶をクリアしました")
    
    def add_manual_memory(self, category: str, content: str) -> bool:
        """手動で記憶を追加"""
        if self.memory_system:
            success = self.memory_system.add_manual_fact(category, content)
            if success:
                self.memory_system.save_memory()  # 即座に保存
            return success
        return False
    
    # プロジェクト管理メソッド
    def get_active_projects(self):
        """進行中プロジェクト一覧を取得"""
        if self.project_system:
            return self.project_system.get_active_projects()
        return []
    
    def get_idea_stock(self):
        """アイデアストック一覧を取得"""
        if self.project_system:
            return self.project_system.get_idea_stock()
        return []
    
    def get_completed_projects(self):
        """完了プロジェクト一覧を取得"""
        if self.project_system:
            return self.project_system.get_completed_projects()
        return []
    
    def create_project(self, title: str, description: str, deadline: str = None, project_type: str = "動画"):
        """新しいプロジェクトを作成"""
        if self.project_system:
            return self.project_system.create_project(title, description, deadline, project_type)
        return {}
    
    def update_project_progress(self, project_id: str, progress: int, status: str = None, next_step: str = None):
        """プロジェクト進捗を更新"""
        if self.project_system:
            success = self.project_system.update_project_progress(project_id, progress, status, next_step)
            if success:
                self.project_system.save_project_data()
            return success
        return False
    
    def complete_project(self, project_id: str, outcome: str = "", lessons: str = ""):
        """プロジェクトを完了"""
        if self.project_system:
            return self.project_system.complete_project(project_id, outcome, lessons)
        return False
    
    def add_idea(self, content: str, category: str = "動画", source: str = "雑談"):
        """アイデアをストックに追加"""
        if self.project_system:
            return self.project_system.add_idea(content, category, source)
        return False
    
    def delete_project(self, project_id: str):
        """プロジェクトを削除"""
        if self.project_system:
            return self.project_system.delete_project(project_id)
        return False
    
    def delete_idea(self, idea_id: str):
        """アイデアを削除"""
        if self.project_system:
            return self.project_system.delete_idea(idea_id)
        return False
    
    def get_project_stats(self):
        """プロジェクト統計情報を取得"""
        if self.project_system:
            return self.project_system.get_project_stats()
        return {"message": "プロジェクトシステムが無効です"}
    
    def save_projects(self):
        """プロジェクトデータを保存"""
        if self.project_system:
            self.project_system.save_project_data()

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
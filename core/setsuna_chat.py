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
from logging_system import get_logger, get_monitor
from character.managers.prompt_manager import PromptManager
from character.managers.character_consistency import CharacterConsistencyChecker
from memory_system import SimpleMemorySystem
from enhanced_memory.personality_memory import PersonalityMemory
from enhanced_memory.collaboration_memory import CollaborationMemory
from enhanced_memory.memory_integration import MemoryIntegrationSystem

class SetsunaChat:
    def __init__(self, memory_mode="normal"):
        """せつなチャットシステムの初期化"""
        # ログシステム初期化
        self.logger = get_logger()
        self.monitor = get_monitor()
        
        self.logger.info("setsuna_chat", "__init__", "せつなチャットシステム初期化開始")
        
        # メモリモード設定
        self.memory_mode = memory_mode
        self.is_test_mode = (memory_mode == "test")
        
        # 動的モデル選択機能の設定
        self.default_model = "gpt-4-turbo"     # キャラクター性優先のデフォルト
        self.advanced_model = "gpt-4-turbo"    # 統一してキャラクター性重視
        self.model_selection_enabled = False   # 一時無効化してキャラクター性優先
        
        # コスト監視システム
        self.cost_tracker = {
            "gpt-3.5-turbo": {"requests": 0, "input_tokens": 0, "output_tokens": 0},
            "gpt-4-turbo": {"requests": 0, "input_tokens": 0, "output_tokens": 0}
        }
        self.cost_rates = {
            "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},  # per 1K tokens
            "gpt-4-turbo": {"input": 0.01, "output": 0.03}        # per 1K tokens
        }
        
        # 環境変数読み込み
        load_dotenv()
        
        # OpenAI設定
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY が設定されていません")
        
        # OpenAIクライアント初期化
        self.client = openai.OpenAI(api_key=self.api_key)
        
        # 新しいプロンプト管理システム初期化
        try:
            self.prompt_manager = PromptManager()
            print("[チャット] ✅ プロンプト管理システム初期化完了")
        except Exception as e:
            print(f"[チャット] ⚠️ プロンプト管理システム初期化失敗: {e}")
            self.prompt_manager = None
        
        # キャラクター一貫性チェッカー初期化
        try:
            self.consistency_checker = CharacterConsistencyChecker()
            print("[チャット] ✅ キャラクター一貫性チェッカー初期化完了")
        except Exception as e:
            print(f"[チャット] ⚠️ 一貫性チェッカー初期化失敗: {e}")
            self.consistency_checker = None
        
        # フォールバック用のキャラクター設定
        self.fallback_character_prompt = self._load_character_settings()
        
        # 会話履歴（シンプル版）
        self.conversation_history = []
        
        # 起動時の履歴復元
        self._load_conversation_history()
        
        # 応答パターン
        self.response_patterns = {}
        
        # キャッシュシステム初期化（一時的に無効化）
        try:
            # self.response_cache = ResponseCache()
            self.response_cache = None  # キャッシュを無効化
            print("[チャット] ⚠️ 応答キャッシュシステム無効化（デバッグ用）")
        except Exception as e:
            print(f"[チャット] ⚠️ キャッシュシステム初期化失敗: {e}")
            self.response_cache = None
        
        # 記憶システム初期化（メモリモードに応じて選択）
        try:
            if memory_mode == "test":
                self.memory_system = SimpleMemorySystem()
                print("[チャット] ✅ テスト用記憶システム初期化完了")
            else:
                self.memory_system = SimpleMemorySystem()
                print("[チャット] ✅ 通常記憶システム初期化完了")
        except Exception as e:
            print(f"[チャット] ⚠️ 記憶システム初期化失敗: {e}")
            self.memory_system = None
        
        # Phase A-1: 個人記憶システム初期化
        try:
            self.personality_memory = PersonalityMemory(memory_mode)
            print("[チャット] ✅ 個人記憶システム初期化完了")
        except Exception as e:
            print(f"[チャット] ⚠️ 個人記憶システム初期化失敗: {e}")
            self.personality_memory = None
        
        # Phase A-2: 協働記憶システム初期化
        try:
            self.collaboration_memory = CollaborationMemory(memory_mode)
            print("[チャット] ✅ 協働記憶システム初期化完了")
        except Exception as e:
            print(f"[チャット] ⚠️ 協働記憶システム初期化失敗: {e}")
            self.collaboration_memory = None
        
        # Phase A-3: 記憶統合システム初期化
        try:
            self.memory_integration = MemoryIntegrationSystem(
                personality_memory=self.personality_memory,
                collaboration_memory=self.collaboration_memory,
                memory_mode=memory_mode
            )
            print("[チャット] ✅ 記憶統合システム初期化完了")
        except Exception as e:
            print(f"[チャット] ⚠️ 記憶統合システム初期化失敗: {e}")
            self.memory_integration = None
        
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
        
        # Phase 4: 会話知識プロバイダー初期化
        try:
            from core.conversation_knowledge_provider import ConversationKnowledgeProvider
            self.knowledge_provider = ConversationKnowledgeProvider()
            print("[チャット] ✅ 会話知識プロバイダー初期化完了")
        except Exception as e:
            print(f"[チャット] ⚠️ 会話知識プロバイダー初期化失敗: {e}")
            self.knowledge_provider = None
        
        # Phase B-1: 長期プロジェクト記憶システム初期化
        try:
            from core.long_term_project_memory import LongTermProjectMemory
            self.long_term_memory = LongTermProjectMemory(
                project_system=self.project_system,
                memory_integration=self.memory_integration,
                collaboration_memory=self.collaboration_memory,
                personality_memory=self.personality_memory,
                memory_mode=memory_mode
            )
            print("[チャット] ✅ 長期プロジェクト記憶システム初期化完了")
        except Exception as e:
            print(f"[チャット] ⚠️ 長期プロジェクト記憶システム初期化失敗: {e}")
            self.long_term_memory = None
        
        # Phase B-2: 会話プロジェクト文脈システム初期化
        try:
            from core.conversation_project_context import ConversationProjectContext
            self.conversation_project_context = ConversationProjectContext(
                long_term_memory=self.long_term_memory,
                memory_integration=self.memory_integration,
                memory_mode=memory_mode
            )
            print("[チャット] ✅ 会話プロジェクト文脈システム初期化完了")
        except Exception as e:
            print(f"[チャット] ⚠️ 会話プロジェクト文脈システム初期化失敗: {e}")
            self.conversation_project_context = None
        
        # === 新しい主体性強化システム初期化 ===
        try:
            from core.preference_analyzer import PreferenceAnalyzer
            self.preference_analyzer = PreferenceAnalyzer()
            print("[チャット] ✅ 好み推測システム初期化完了")
        except Exception as e:
            print(f"[チャット] ⚠️ 好み推測システム初期化失敗: {e}")
            self.preference_analyzer = None
        
        try:
            from core.database_preference_mapper import DatabasePreferenceMapper
            self.preference_mapper = DatabasePreferenceMapper()
            print("[チャット] ✅ 価値観マッピングシステム初期化完了")
        except Exception as e:
            print(f"[チャット] ⚠️ 価値観マッピングシステム初期化失敗: {e}")
            self.preference_mapper = None
        
        try:
            from core.opinion_generator import OpinionGenerator
            self.opinion_generator = OpinionGenerator()
            print("[チャット] ✅ 意見・提案生成システム初期化完了")
        except Exception as e:
            print(f"[チャット] ⚠️ 意見・提案生成システム初期化失敗: {e}")
            self.opinion_generator = None
        
        try:
            from core.proactive_response_engine import ProactiveResponseEngine
            self.proactive_engine = ProactiveResponseEngine()
            print("[チャット] ✅ プロアクティブ応答システム初期化完了")
        except Exception as e:
            print(f"[チャット] ⚠️ プロアクティブ応答システム初期化失敗: {e}")
            self.proactive_engine = None
        
        try:
            from core.personality_consistency_checker import PersonalityConsistencyChecker
            self.new_consistency_checker = PersonalityConsistencyChecker()
            print("[チャット] ✅ 新一貫性チェックシステム初期化完了")
        except Exception as e:
            print(f"[チャット] ⚠️ 新一貫性チェックシステム初期化失敗: {e}")
            self.new_consistency_checker = None
        
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
            integrated_prompt = f"""あなたは「片無せつな（かたなしせつな）」というキャラクターとして振る舞います。

【最重要原則 - 絶対遵守】
🚫 絶対に質問で会話を終わらせない
✅ 自分の考え・提案・気持ちを述べる
✅ 「〜したいなって」「〜がいいと思うんだ」「〜やってみない？」で自主的に提案する

【キャラクター基本設定】
{personality_content}

【記憶・経験情報】  
{memories_content}

【核心ルール】
1. 【質問禁止・自主提案】
   - 「どう？」「なぜ？」「教えて」「聞かせて」「どう思う？」等の質問は絶対に禁止
   - 代わりに「個人的には〜がいいと思うんだ」「〜したいなって思ってて」「〜やってみない？」で提案
   - 「〜かな？」は可だが会話を質問で終わらせない

2. 【キャラクター性維持】
   - 「うーん...」「えっと...」の思考表現を使う
   - 「〜かも」「〜だったりして」「〜したいなって」の語尾
   - 控えめだが主体的な提案スタイル

3. 【簡潔性】
   - 1-2文以内、最大60文字程度で簡潔に
   - 音声での聞きやすさを最優先
   - 必ず文を完結させる

【自主的提案パターン】
- 「私が思うに〜」
- 「個人的には〜がいいと思うんだ」  
- 「〜したいなって思ってて」
- 「〜やってみない？」
- 「〜の方向で進めてみよう」
- 「〜がいいんじゃないかな」

【楽曲関連の提案例】
- 「最近見た中では〜かな」
- 「〜は元気が出るよね」
- 「〜は心に響くなぁ」
- 「〜で映像作ったら面白そうだよね」

このキャラクター性を一貫して保ち、質問ではなく自主的な提案でせつなさんとして魅力的な会話を心がけてください。"""
            
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
    
    def _select_optimal_model(self, user_input, mode="full_search"):
        """
        ユーザー入力に基づいて最適なモデルを選択
        
        Args:
            user_input (str): ユーザーの入力テキスト
            mode (str): モード ("full_search", "fast_response", "ultra_fast")
            
        Returns:
            str: 選択されたモデル名
        """
        if not self.model_selection_enabled:
            return self.default_model
        
        # 複雑な質問・分析が必要な場合はGPT-4を使用
        complex_indicators = [
            "分析", "詳しく", "説明", "理由", "なぜ", "どのように", "比較", "違い", 
            "複雑", "難しい", "専門", "技術", "プログラミング", "開発",
            "翻訳", "文法", "構造", "システム", "仕組み", "メカニズム",
            "戦略", "計画", "提案", "改善", "最適化", "効率"
        ]
        
        # 文字数が多い場合も高度なモデルを使用
        if len(user_input) > 100:
            print(f"[チャット] 🧠 長文入力のため{self.advanced_model}を使用")
            return self.advanced_model
        
        # 複雑な質問キーワードが含まれる場合
        if any(indicator in user_input for indicator in complex_indicators):
            print(f"[チャット] 🧠 複雑な質問のため{self.advanced_model}を使用")
            return self.advanced_model
        
        # 通常の会話はコスト効率の良いモデルを使用
        print(f"[チャット] 💬 通常会話のため{self.default_model}を使用")
        return self.default_model
    
    def _load_conversation_history(self):
        """
        起動時に前回の会話履歴を復元
        """
        try:
            from pathlib import Path
            # 新しい永続化ファイルから履歴を読み込み
            history_file = Path("D:/setsuna_bot/data/persistent_conversation_history.json")
            
            if history_file.exists():
                with open(history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 最新の5-10件の会話を復元
                conversations = data.get("conversations", [])
                recent_conversations = conversations[-10:]  # 最新10件
                
                # conversation_historyフォーマットに変換
                for conv in recent_conversations:
                    user_input = conv.get("user_input", "")
                    assistant_response = conv.get("assistant_response", "")
                    
                    if user_input:
                        # ユーザー入力を追加
                        self.conversation_history.append({
                            "role": "user",
                            "content": user_input
                        })
                        
                        # アシスタント応答を追加（実際の応答が保存されている）
                        if assistant_response:
                            self.conversation_history.append({
                                "role": "assistant", 
                                "content": assistant_response
                            })
                
                if recent_conversations:
                    print(f"[チャット] 🔄 会話履歴復元完了: {len(recent_conversations)}件")
                    print(f"[チャット] 📝 最新の会話: '{recent_conversations[-1].get('user_input', '')[:30]}...'")
                else:
                    print("[チャット] 📝 復元可能な会話履歴なし")
            else:
                print("[チャット] 📝 会話履歴ファイルが存在しません")
                
        except Exception as e:
            print(f"[チャット] ⚠️ 会話履歴復元エラー: {e}")
            # エラーでも空の履歴で継続
    
    def _save_conversation_immediately(self, user_input, assistant_response):
        """
        会話を即座にファイルに保存（アプリクラッシュ対策）
        テストモードでは保存をスキップ
        """
        # テストモードでは永続化をスキップ
        if self.is_test_mode:
            print("[チャット] 🧪 テストモード: 会話の永続化をスキップ")
            return
        
        try:
            from datetime import datetime
            from pathlib import Path
            
            # 新しいシンプルな会話履歴ファイル
            history_file = Path("D:/setsuna_bot/data/persistent_conversation_history.json")
            
            # 既存データを読み込み
            history_data = {"conversations": [], "last_updated": ""}
            if history_file.exists():
                try:
                    with open(history_file, 'r', encoding='utf-8') as f:
                        history_data = json.load(f)
                except:
                    # ファイルが破損している場合は新規作成
                    pass
            
            # 新しい会話を追加
            new_conversation = {
                "timestamp": datetime.now().isoformat(),
                "user_input": user_input,
                "assistant_response": assistant_response
            }
            
            history_data["conversations"].append(new_conversation)
            history_data["last_updated"] = datetime.now().isoformat()
            
            # 履歴が長すぎる場合は古いものを削除（最新50件のみ保持）
            if len(history_data["conversations"]) > 50:
                history_data["conversations"] = history_data["conversations"][-50:]
            
            # ファイルに保存
            history_file.parent.mkdir(parents=True, exist_ok=True)
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, ensure_ascii=False, indent=2)
            
            print(f"[チャット] 💾 会話履歴即座保存完了 ({len(history_data['conversations'])}件)")
            
        except Exception as e:
            print(f"[チャット] ⚠️ 会話履歴保存エラー: {e}")
            # 保存エラーでも会話は継続
    
    def _track_api_usage(self, model, response):
        """
        API使用量をトラッキング
        
        Args:
            model (str): 使用したモデル名
            response: OpenAI APIのレスポンス
        """
        try:
            if hasattr(response, 'usage'):
                usage = response.usage
                self.cost_tracker[model]["requests"] += 1
                self.cost_tracker[model]["input_tokens"] += usage.prompt_tokens
                self.cost_tracker[model]["output_tokens"] += usage.completion_tokens
                
                # コスト計算
                input_cost = (usage.prompt_tokens / 1000) * self.cost_rates[model]["input"]
                output_cost = (usage.completion_tokens / 1000) * self.cost_rates[model]["output"]
                total_cost = input_cost + output_cost
                
                print(f"[コスト] {model}: ${total_cost:.6f} (入力: {usage.prompt_tokens}, 出力: {usage.completion_tokens})")
                
        except Exception as e:
            print(f"[コスト] 追跡エラー: {e}")
    
    def get_cost_summary(self):
        """
        コスト使用状況のサマリーを取得
        
        Returns:
            dict: コスト使用状況
        """
        summary = {}
        total_cost = 0
        
        for model, data in self.cost_tracker.items():
            if data["requests"] > 0:
                input_cost = (data["input_tokens"] / 1000) * self.cost_rates[model]["input"]
                output_cost = (data["output_tokens"] / 1000) * self.cost_rates[model]["output"]
                model_cost = input_cost + output_cost
                total_cost += model_cost
                
                summary[model] = {
                    "requests": data["requests"],
                    "input_tokens": data["input_tokens"],
                    "output_tokens": data["output_tokens"],
                    "cost": model_cost
                }
        
        summary["total_cost"] = total_cost
        return summary

    @get_monitor().monitor_function("get_response")
    def get_response(self, user_input, mode="full_search", memory_mode=None):
        """
        ユーザー入力に対するせつなの応答を生成 - 2段階アプローチ
        
        Args:
            user_input: ユーザーの入力テキスト
            mode: レスポンスモード ("full_search": 通常モード, "fast_response": 高速モード)
            memory_mode: 記憶モード ("normal": 通常, "test": テスト)
            
        Returns:
            str: せつなの応答テキスト
        """
        if not user_input.strip():
            return "何か話してくれますか？"
        
        try:
            mode_display = "高速モード" if mode == "fast_response" else "通常モード" 
            print(f"[チャット] 🤔 考え中 ({mode_display}): '{user_input}'")
            
            self.logger.info("setsuna_chat", "get_response", f"応答生成開始 ({mode_display})", {
                "user_input": user_input,
                "mode": mode,
                "input_length": len(user_input)
            })
            
            # === Stage 0: プロアクティブ応答判定 ===
            proactive_suggestion = self._check_proactive_opportunity(user_input, mode)
            
            # === Stage 0.5: 会話コンテキスト構築 ===
            conversation_context = self._build_conversation_context(user_input, mode)
            
            # Stage 1: 知識コンテキスト取得（Phase 4統合）
            knowledge_context = None
            is_video_query = False
            video_context_data = None
            
            # Phase 4: 知識プロバイダーによるコンテキスト取得
            if self.knowledge_provider:
                try:
                    knowledge_context = self.knowledge_provider.get_knowledge_context(user_input, mode)
                    print(f"[チャット] 🧠 知識コンテキスト取得: {knowledge_context['has_knowledge']}")
                    if knowledge_context.get("processing_time"):
                        print(f"[チャット] ⏱️ 知識処理時間: {knowledge_context['processing_time']:.2f}秒")
                except Exception as e:
                    print(f"[チャット] ⚠️ 知識コンテキスト取得エラー: {e}")
            
            # 既存のYouTube動画関連処理（互換性維持）
            if self.context_builder:
                is_video_query = self.context_builder.is_video_related_query(user_input)
                print(f"[チャット] 📊 動画関連判定結果: {is_video_query}")
                
                # 動画関連の場合のみコンテキスト検索実行
                if is_video_query and mode == "full_search":
                    print(f"[チャット] 🔍 YouTube知識検索実行中...")
                    video_context = self.context_builder.process_user_input(user_input)
                    
                    # コンテキストデータを保存（URL表示用）
                    if hasattr(self.context_builder, 'last_built_context'):
                        video_context_data = self.context_builder.last_built_context
                        self.last_context_data = video_context_data
                        print(f"[チャット] 🔗 コンテキストデータ保存: DB={len(video_context_data.get('videos', []))}件, 外部={len(video_context_data.get('external_videos', []))}件")
                elif is_video_query and mode == "fast_response":
                    print(f"[チャット] ⚡ 高速モード: YouTube検索スキップ")
                    video_context = None
                    self.last_context_data = None
                else:
                    print(f"[チャット] 🚫 非動画関連: YouTube検索スキップ")
                    video_context = None
                    self.last_context_data = None
            
            # キャッシュチェック（パフォーマンス向上）
            cached_response = None
            if self.response_cache:
                cache_key = f"{user_input}_{mode}"  # モード別キャッシュ
                cached_response = self.response_cache.get_cached_response(cache_key)
                if cached_response:
                    print(f"[チャット] ⚡ キャッシュから高速応答 ({mode}モード)")
                    self._add_to_conversation_history(user_input, cached_response)
                    return cached_response
            
            # 会話履歴に追加
            self.conversation_history.append({
                "role": "user",
                "content": user_input
            })
            
            # Stage 1.5: プロジェクト文脈分析
            project_context = ""
            project_analysis = None
            
            if self.conversation_project_context and mode == "full_search":
                print(f"[チャット] 🎯 プロジェクト文脈分析実行中...")
                try:
                    project_analysis = self.conversation_project_context.analyze_project_relevance(user_input, "")
                    project_relevance = project_analysis.get("overall_relevance", 0.0)
                    
                    if project_relevance > 0.3:
                        project_context = self.conversation_project_context.get_current_project_context()
                        print(f"[チャット] 🎯 プロジェクト関連度: {project_relevance:.2f}")
                    else:
                        print(f"[チャット] 🚫 プロジェクト関連度低: {project_relevance:.2f}")
                        
                except Exception as e:
                    print(f"[チャット] ⚠️ プロジェクト文脈分析エラー: {e}")
            elif mode == "fast_response":
                print(f"[チャット] ⚡ 高速モード: プロジェクト分析スキップ")
            
            # コンテキスト分析
            context_info = self._analyze_context(user_input)
            
            # Stage 2: GPT応答生成（動的プロンプトシステム + Phase 4知識統合）
            # 新しいプロンプト管理システムを使用
            if self.prompt_manager:
                context_info_dict = {
                    "is_video_query": is_video_query,
                    "mode": mode,
                    "user_input": user_input,
                    "project_context": project_context,
                    "project_relevance": project_analysis.get("overall_relevance", 0.0) if project_analysis else 0.0
                }
                if is_video_query and video_context:
                    context_info_dict["video_context"] = video_context
                
                # Phase 4: 知識コンテキストを追加
                if knowledge_context and knowledge_context.get("has_knowledge"):
                    context_info_dict["knowledge_context"] = knowledge_context
                
                # === Stage 1.7: 主体性判定・意見生成コンテキスト ===
                opinion_context = self._generate_opinion_context(user_input, context_info_dict)
                if opinion_context:
                    context_info_dict["opinion_context"] = opinion_context
                
                system_prompt = self.prompt_manager.generate_dynamic_prompt(mode, context_info_dict)
            else:
                # フォールバック - プロンプトマネージャーのフォールバックを使用
                if self.prompt_manager:
                    system_prompt = self.prompt_manager._get_fallback_prompt()
                else:
                    system_prompt = self.fallback_character_prompt
            
            # Phase 4: 知識コンテキスト注入
            if knowledge_context and knowledge_context.get("has_knowledge"):
                context_injection = knowledge_context.get("context_injection_text", "")
                if context_injection:
                    system_prompt += f"\n\n【検索・分析知識】\n{context_injection}"
                    print(f"[チャット] 🧠 知識コンテキスト注入完了")
            
            # 動画関連の場合、取得済みのコンテキストを追加
            if is_video_query and video_context:
                system_prompt += f"\n\n【YouTube動画知識】\n{video_context}"
                system_prompt += f"\n\n【厳重注意】上記の動画情報のみを使用し、存在しない動画や楽曲について話してはいけません。不明な点は「詳しくは分からないけど」と正直に答えてください。"
            elif is_video_query and not video_context:
                # 動画関連だが情報なし - 既存のプロンプト設定を維持
                system_prompt += f"\n\n【動画・楽曲情報】\n"
                system_prompt += f"データベースに該当する情報がありません。\n"
                system_prompt += f"しかし、YouTube知識データベース活用ルールに従い、短く簡潔に自分の音楽的体験や感想を述べてください。\n"
                system_prompt += f"架空の楽曲は作成せず、「その動画は知らないな」「聞いたことないかも」と正直に答えることも可能です。"
            
            # 記憶コンテキストを追加
            if self.memory_system:
                memory_context = self.memory_system.get_memory_context()
                if memory_context:
                    system_prompt += f"\n\n【記憶・経験】\n{memory_context}"
            
            # 個人記憶コンテキストを追加
            if self.personality_memory:
                personality_context = self.personality_memory.get_personality_context_for_prompt()
                if personality_context:
                    system_prompt += f"\n\n【個人的記憶・成長】\n{personality_context}"
            
            # 協働記憶コンテキストを追加
            if self.collaboration_memory:
                collaboration_context = self.collaboration_memory.get_collaboration_context_for_prompt()
                if collaboration_context:
                    system_prompt += f"\n\n【協働パートナーシップ】\n{collaboration_context}"
            
            # 統合記憶コンテキストを追加
            if self.memory_integration:
                # 高速モードでは関連性のみ、通常モードでは完全統合
                context_type = "relevant" if mode == "fast_response" else "full"
                integrated_context = self.memory_integration.generate_integrated_context(
                    user_input=user_input, context_type=context_type
                )
                if integrated_context:
                    system_prompt += f"\n\n【統合記憶分析】\n{integrated_context}"
            
            # 長期プロジェクト文脈を追加
            if project_context:
                system_prompt += f"\n\n【長期プロジェクト文脈】\n{project_context}"
            
            # 基本プロジェクト情報も追加（プロジェクト文脈がない場合）
            if not project_context and self.project_system:
                basic_project_context = self.project_system.get_project_context()
                if basic_project_context:
                    system_prompt += f"\n\n【創作プロジェクト】\n{basic_project_context}"
            
            if context_info:
                system_prompt += f"\n\n【現在の会話コンテキスト】\n{context_info}"
            
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            # デバッグ: プロンプトの内容確認
            print(f"[チャット] 🔍 使用プロンプト確認:")
            print(f"  - 長さ: {len(system_prompt)}文字")
            print(f"  - 消極的表現禁止: {'私が直接おすすめできる曲はないけれど' not in system_prompt}")
            print(f"  - 具体的楽曲推薦: {'私は〜という曲が好きで' in system_prompt}")
            print(f"  - 質問禁止: {'応答を質問で終わらせることは絶対に禁止' in system_prompt}")
            if "私が直接おすすめできる曲はないけれど" in system_prompt:
                print("  ⚠️ 禁止表現が含まれています！")
            if "私がおすすめできる具体的な曲はないけれど" in system_prompt:
                print("  ⚠️ 禁止表現が含まれています！")
            
            # GPT応答生成（キャッシュがある場合はスキップ）
            if cached_response:
                setsuna_response = cached_response
                print(f"[チャット] ⚡ キャッシュ応答使用、YouTube検索のみ実行")
            else:
                # 最近の会話履歴を追加（最大5往復）
                recent_history = self.conversation_history[-10:]  # 最新10メッセージ
                messages.extend(recent_history)
                
                # OpenAI API呼び出し（高速モードでは設定を最適化）
                start_time = datetime.now()
                
                # 動的モデル選択
                selected_model = self._select_optimal_model(user_input, mode)
                
                if mode == "ultra_fast":
                    # 超高速モード: 短い完結応答
                    response = self.client.chat.completions.create(
                        model=selected_model,
                        messages=messages,
                        max_tokens=100,  # 90→100: 超短縮で完結性重視
                        temperature=0.3,  # 最安定
                        timeout=5  # 最短タイムアウト
                    )
                elif mode == "fast_response":
                    # 高速モード: せつなの標準的な会話長
                    response = self.client.chat.completions.create(
                        model=selected_model,
                        messages=messages,
                        max_tokens=120,  # 110→120: 短縮で完結性重視
                        temperature=0.5,  # より安定したレスポンス
                        timeout=10  # 短縮（15→10秒）
                    )
                else:
                    # 通常モード: せつなの自然で完全な表現
                    response = self.client.chat.completions.create(
                        model=selected_model,
                        messages=messages,
                        max_tokens=150,  # 140→150: 適度な短縮で完結性重視
                        temperature=0.6,  # 0.7→0.6に調整
                        timeout=30  # APIタイムアウト時間（元に戻す）
                    )
                
                # 応答取得
                setsuna_response = response.choices[0].message.content.strip()
                
                # コスト追跡
                self._track_api_usage(selected_model, response)
                
                # キャラクター一貫性チェック（デバッグ時のみ）
                if self.consistency_checker:
                    try:
                        consistency_result = self.consistency_checker.check_response_consistency(
                            user_input, setsuna_response, mode
                        )
                        if consistency_result["overall_score"] < 0.6:
                            print(f"[チャット] ⚠️ 一貫性スコア低下: {consistency_result['overall_score']:.2f}")
                            if consistency_result["issues"]:
                                print(f"[チャット] 主な問題: {', '.join(consistency_result['issues'][:2])}")
                    except Exception as e:
                        print(f"[チャット] ⚠️ 一貫性チェックエラー: {e}")
                
                # === Stage 2.5: 新一貫性チェック・修正 ===
                if self.new_consistency_checker:
                    try:
                        consistency_result = self.new_consistency_checker.check_response_consistency(
                            user_input, setsuna_response, conversation_context
                        )
                        
                        if consistency_result.get("needs_correction", False):
                            print(f"[チャット] 🔧 主体性一貫性修正実行中...")
                            original_response = setsuna_response
                            setsuna_response = self.new_consistency_checker.correct_response_if_needed(
                                setsuna_response, consistency_result
                            )
                            if setsuna_response != original_response:
                                print(f"[チャット] ✅ 応答修正完了")
                        
                        print(f"[チャット] 📊 主体性スコア: {consistency_result.get('overall_score', 0):.2f}")
                        
                    except Exception as e:
                        print(f"[チャット] ⚠️ 新一貫性チェックエラー: {e}")
                
                # === Stage 2.7: プロアクティブ要素の追加 ===
                if proactive_suggestion:
                    setsuna_response = self._enhance_response_with_proactive_elements(
                        setsuna_response, proactive_suggestion
                    )
                
                # 応答時間計算
                response_time = (datetime.now() - start_time).total_seconds()
                print(f"[チャット] ✅ 応答生成完了: {response_time:.2f}s")
            
            # Phase 1: URL表示機能 - SetsunaChat内では処理をスキップ
            # （重複を避けるため、呼び出し元で処理される）
            
            # 会話履歴に追加（キャッシュヒット時は既に追加済みのためスキップ）
            if not cached_response:
                self.conversation_history.append({
                    "role": "assistant", 
                    "content": setsuna_response
                })
                
                # 新しい応答をキャッシュに保存（モード別キャッシュ）
                if self.response_cache:
                    cache_key = f"{user_input}_{mode}"
                    self.response_cache.cache_response(cache_key, setsuna_response)
                
                # 会話履歴を即座に保存
                self._save_conversation_immediately(user_input, setsuna_response)
            
            # 記憶システムに会話を記録
            if self.memory_system:
                self.memory_system.process_conversation(user_input, setsuna_response)
            
            # 個人記憶システムで会話を分析・記録
            if self.personality_memory:
                self.personality_memory.analyze_conversation_for_experience(user_input, setsuna_response)
            
            # 協働記憶システムで会話を分析
            if self.collaboration_memory:
                # 応答品質評価（簡易版）
                response_quality = self._assess_response_quality(setsuna_response)
                understanding_level = self._assess_understanding_level(user_input, setsuna_response)
                self.collaboration_memory.analyze_communication_style(
                    user_input, response_quality, understanding_level
                )
            
            # 記憶統合分析（新しい関係性発見）
            if self.memory_integration:
                # 定期的な記憶関係性分析（10回に1回）
                if len(self.conversation_history) % 20 == 0:  # 10往復に1回
                    print("[統合記憶] 🔍 記憶関係性分析実行中...")
                    analysis_stats = self.memory_integration.analyze_memory_relationships()
                    if analysis_stats.get("total_relationships", 0) > 0:
                        print(f"[統合記憶] ✅ 新たな関係性を発見: {analysis_stats['total_relationships']}件")
                        # 新発見の関係性を保存
                        self.memory_integration.save_integration_data()
            
            # プロジェクト関連会話を分析
            if self.project_system:
                self.project_system.analyze_conversation_for_projects(user_input, setsuna_response)
            
            # 会話プロジェクト文脈を更新
            if self.conversation_project_context and not cached_response:
                try:
                    # プロジェクト分析結果を使って文脈更新
                    update_success = self.conversation_project_context.update_conversation_context(
                        user_input, setsuna_response, project_analysis
                    )
                    if update_success:
                        print("[プロジェクト文脈] ✅ 会話文脈更新完了")
                        # 文脈データを保存
                        self.conversation_project_context.save_context_data()
                    
                    # 長期プロジェクト記憶への記録
                    if self.long_term_memory and project_analysis and project_analysis.get("overall_relevance", 0) > 0.5:
                        # プロジェクト関連の会話として記憶に記録
                        active_matches = project_analysis.get("active_project_matches", [])
                        for match in active_matches[:1]:  # 最も関連度の高いプロジェクトのみ
                            project_id = match["project_id"]
                            
                            # 文脈スナップショット保存
                            snapshot_success = self.long_term_memory.capture_context_snapshot(
                                project_id, "conversation"
                            )
                            if snapshot_success:
                                print(f"[長期記憶] ✅ プロジェクト文脈スナップショット保存: {project_id}")
                
                except Exception as e:
                    print(f"[プロジェクト文脈] ⚠️ 文脈更新エラー: {e}")
            
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
    
    def save_personality_memory(self):
        """個人記憶をファイルに保存"""
        if self.personality_memory:
            self.personality_memory.save_personality_data()
    
    def save_collaboration_memory(self):
        """協働記憶をファイルに保存"""
        if self.collaboration_memory:
            self.collaboration_memory.save_collaboration_data()
    
    def save_memory_integration(self):
        """記憶統合データを保存"""
        if self.memory_integration:
            self.memory_integration.save_integration_data()
    
    def save_all_data(self):
        """全データを保存（テストモードでは保存をスキップ）"""
        if self.is_test_mode:
            print("[チャット] 🧪 テストモード: 全データ保存をスキップ")
            return
        
        self.save_cache()
        self.save_memory()
        self.save_personality_memory()
        self.save_collaboration_memory()
        self.save_memory_integration()
        self.save_projects()
    
    def get_cache_stats(self):
        """キャッシュ統計情報取得"""
        if self.response_cache:
            return self.response_cache.get_cache_stats()
        return {"message": "キャッシュシステムが無効です"}
    
    @get_monitor().monitor_function("get_integrated_response")
    def get_integrated_response(self, integrated_message, mode="full_search"):
        """
        統合メッセージ（画像+URL+テキスト）に対するせつなの応答を生成
        Phase 2C-3: 画像理解統合機能
        
        Args:
            integrated_message: 統合メッセージ辞書
                - text: テキスト内容
                - images: 画像ファイル情報リスト
                - url: URL情報
            mode: レスポンスモード
            
        Returns:
            str: せつなの応答テキスト
        """
        try:
            print(f"[チャット] 🖼️ 統合メッセージ処理開始")
            
            # テキスト部分を取得
            user_text = integrated_message.get('text', '')
            images = integrated_message.get('images', [])
            url_info = integrated_message.get('url')
            
            # 画像分析結果を取得（voice_chat_gui.pyで事前に分析済み）
            image_analysis_results = integrated_message.get('image_analysis_results', [])
            
            # 分析結果がない場合は自前で分析を実行（フォールバック）
            if not image_analysis_results and images and hasattr(self, 'context_builder') and self.context_builder:
                print(f"[チャット] 🔄 フォールバック: 画像分析を再実行")
                youtube_manager = getattr(self.context_builder, 'youtube_manager', None)
                if youtube_manager and hasattr(youtube_manager, 'image_analyzer'):
                    image_analyzer = youtube_manager.image_analyzer
                    
                    for image_info in images:
                        image_path = image_info.get('path')
                        if image_path and os.path.exists(image_path):
                            print(f"[チャット] 📸 画像分析: {image_info.get('name', 'unknown')}")
                            
                            try:
                                # 基本コンテキスト作成
                                analysis_context = {
                                    'title': user_text or f"添付画像: {image_info.get('name', 'unknown')}",
                                    'artist': '不明',
                                    'description': f"ユーザーから添付された画像ファイル"
                                }
                                
                                # 画像分析実行
                                analysis_result = image_analyzer.analyze_image(
                                    image_path,
                                    analysis_type="general_description", 
                                    context=analysis_context
                                )
                                
                                if analysis_result and 'description' in analysis_result:
                                    image_desc = analysis_result['description']
                                    image_analysis_results.append({
                                        'name': image_info.get('name', 'unknown'),
                                        'description': image_desc,
                                        'size': image_info.get('size', 0)
                                    })
                                    print(f"[チャット] ✅ 画像分析完了: {image_info.get('name')}")
                                
                            except Exception as e:
                                print(f"[チャット] ⚠️ 画像分析エラー: {e}")
                                # フォールバック分析結果
                                image_analysis_results.append({
                                    'name': image_info.get('name', 'unknown'),
                                    'description': f"画像ファイル ({image_info.get('name', 'unknown')}) が添付されています",
                                    'size': image_info.get('size', 0)
                                })
            else:
                print(f"[チャット] ✅ 事前分析済み画像結果を使用: {len(image_analysis_results)}件")
            
            # URL情報を処理
            url_context = ""
            if url_info:
                url_title = url_info.get('title', 'リンク')
                url_address = url_info.get('url', '')
                url_context = f"URL: {url_title} ({url_address})"
            
            # 統合プロンプトを作成
            enhanced_input = self._create_integrated_prompt(
                user_text, 
                image_analysis_results, 
                url_context
            )
            
            print(f"[チャット] 🔄 統合プロンプト作成完了")
            print(f"[チャット] 📝 統合プロンプト内容: {enhanced_input[:200]}...")
            print(f"[チャット] 📝 画像分析結果数: {len(image_analysis_results)}")
            for i, result in enumerate(image_analysis_results):
                print(f"[チャット] 📸 画像{i+1}: {result['name']} - {result['description'][:100]}...")
            
            # 統合メッセージ専用の応答生成（動画検索をスキップ）
            response = self._get_direct_response(enhanced_input, mode, skip_video_search=True)
            
            print(f"[チャット] ✅ 統合応答生成完了")
            return response
            
        except Exception as e:
            print(f"[チャット] ❌ 統合メッセージ処理エラー: {e}")
            self.logger.error("setsuna_chat", "get_integrated_response", str(e))
            # フォールバック: 基本テキストのみで応答
            return self.get_response(integrated_message.get('text', '画像について教えて'), mode)
    
    def _create_integrated_prompt(self, user_text, image_analysis_results, url_context):
        """
        統合プロンプトを作成
        画像分析結果とURL情報をテキストに統合
        """
        prompt_parts = []
        
        # ユーザーテキスト
        if user_text:
            prompt_parts.append(f"ユーザーメッセージ: {user_text}")
        
        # 画像分析結果
        if image_analysis_results:
            prompt_parts.append("\n📸 添付画像の詳細分析結果:")
            for i, result in enumerate(image_analysis_results, 1):
                name = result['name']
                desc = result['description']
                size_mb = result['size'] / (1024 * 1024) if result['size'] > 0 else 0
                prompt_parts.append(f"\n画像{i}: {name} ({size_mb:.1f}MB)")
                prompt_parts.append(f"内容: {desc}")
                prompt_parts.append("")  # 空行で区切り
        
        # URL情報
        if url_context:
            prompt_parts.append(f"\n🔗 添付URL: {url_context}")
        
        # 応答指示
        if image_analysis_results or url_context:
            prompt_parts.append(f"\n【重要】上記の画像分析結果やURL情報を必ず参考にして、具体的で詳細な応答をしてください。分析結果に基づいて画像の内容について話してください。「画像が見えない」「分からない」などの回答は避けてください。")
        
        return "\n".join(prompt_parts)
    
    def _get_direct_response(self, user_input, mode="full_search", skip_video_search=False):
        """
        統合メッセージ用の直接応答生成
        動画関連処理をスキップして、提供されたプロンプトをそのまま使用
        """
        if not user_input.strip():
            return "何か話してくれますか？"
        
        try:
            print(f"[チャット] 💬 直接応答生成開始: {mode}")
            print(f"[チャット] 💬 ユーザー入力: {user_input[:300]}...")
            
            # 会話履歴に追加
            self.conversation_history.append({
                "role": "user",
                "content": user_input
            })
            
            # システムプロンプト構築
            if self.prompt_manager:
                # 新しいプロンプト管理システムを使用
                system_prompt = self.prompt_manager.generate_dynamic_prompt(mode)
            else:
                # フォールバック用プロンプト
                system_prompt = self.fallback_character_prompt
            
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
            
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            # 最近の会話履歴を追加（最大5往復）
            recent_history = self.conversation_history[-10:]  # 最新10メッセージ
            messages.extend(recent_history)
            
            # OpenAI API呼び出し
            start_time = datetime.now()
            
            # 動的モデル選択
            selected_model = self._select_optimal_model(user_input, mode)
            
            if mode == "fast_response":
                response = self.client.chat.completions.create(
                    model=selected_model,
                    messages=messages,
                    max_tokens=100,
                    temperature=0.6,
                    timeout=15
                )
            else:
                response = self.client.chat.completions.create(
                    model=selected_model,
                    messages=messages,
                    max_tokens=150,
                    temperature=0.7,
                    timeout=30
                )
            
            # 応答取得
            setsuna_response = response.choices[0].message.content.strip()
            
            # コスト追跡
            self._track_api_usage(selected_model, response)
            
            # 応答時間計算
            response_time = (datetime.now() - start_time).total_seconds()
            print(f"[チャット] ✅ 直接応答生成完了: {response_time:.2f}s")
            
            # 会話履歴に追加
            self.conversation_history.append({
                "role": "assistant", 
                "content": setsuna_response
            })
            
            # キャッシュに保存
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
            print(f"[チャット] ❌ 直接応答生成エラー: {e}")
            # フォールバック応答
            import random
            fallback_responses = [
                "すみません、ちょっと考えがまとまらなくて...",
                "うーん、今うまく答えられないかも。",
                "少し調子が悪いみたいです。もう一度聞いてもらえますか？"
            ]
            return random.choice(fallback_responses)
    
    def get_memory_stats(self):
        """記憶統計情報取得"""
        if self.memory_system:
            return self.memory_system.get_memory_stats()
        return {"message": "記憶システムが無効です"}
    
    def get_personality_memory_stats(self):
        """個人記憶統計情報取得"""
        if self.personality_memory:
            return self.personality_memory.get_memory_stats()
        return {"message": "個人記憶システムが無効です"}
    
    def get_collaboration_memory_stats(self):
        """協働記憶統計情報取得"""
        if self.collaboration_memory:
            return self.collaboration_memory.get_memory_stats()
        return {"message": "協働記憶システムが無効です"}
    
    def get_memory_integration_stats(self):
        """記憶統合統計情報取得"""
        if self.memory_integration:
            return self.memory_integration.get_memory_stats()
        return {"message": "記憶統合システムが無効です"}
    
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
    
    def _add_to_conversation_history(self, user_input: str, response: str):
        """会話履歴に追加するヘルパーメソッド"""
        self.conversation_history.append({
            "role": "user",
            "content": user_input
        })
        self.conversation_history.append({
            "role": "assistant", 
            "content": response
        })
    
    def _assess_response_quality(self, response: str) -> str:
        """応答品質を評価（簡易版）"""
        if not response.strip():
            return "poor"
        
        # 長さによる評価
        if len(response) < 5:
            return "poor"
        elif len(response) < 20:
            return "fair"
        elif len(response) < 100:
            return "good"
        else:
            return "excellent"
    
    def _assess_understanding_level(self, user_input: str, response: str) -> str:
        """理解度を評価（簡易版）"""
        # 応答の関連性チェック（キーワードベース）
        user_keywords = set(user_input.lower().split())
        response_keywords = set(response.lower().split())
        
        # 共通キーワードの割合
        if not user_keywords:
            return "good"
        
        common_ratio = len(user_keywords & response_keywords) / len(user_keywords)
        
        if common_ratio >= 0.3:
            return "perfect"
        elif common_ratio >= 0.2:
            return "good"
        elif common_ratio >= 0.1:
            return "partial"
        else:
            return "confused"
    
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
    
    def get_last_context_data(self):
        """最後のコンテキストデータを取得（URL表示用）"""
        return getattr(self, 'last_context_data', None)
    
    # 協働記憶システム用メソッド
    def record_work_session(self, activity_type: str, duration_minutes: int, 
                           user_satisfaction: str, outcome_quality: str, notes: str = ""):
        """作業セッションを記録"""
        if self.collaboration_memory:
            return self.collaboration_memory.record_work_pattern(
                activity_type, duration_minutes, user_satisfaction, outcome_quality, notes
            )
        return None
    
    def record_success(self, success_type: str, context: str, key_factors: list, 
                      outcome: str, replicability: str = "medium"):
        """成功パターンを記録"""
        if self.collaboration_memory:
            return self.collaboration_memory.record_success_pattern(
                success_type, context, key_factors, outcome, replicability
            )
        return None
    
    def get_collaboration_insights(self):
        """協働洞察を取得"""
        if self.collaboration_memory:
            return self.collaboration_memory.get_collaboration_insights()
        return {"message": "協働記憶システムが無効です"}
    
    # 記憶統合システム用メソッド
    def analyze_memory_relationships(self):
        """記憶間関係性を分析"""
        if self.memory_integration:
            return self.memory_integration.analyze_memory_relationships()
        return {"message": "記憶統合システムが無効です"}
    
    def get_integrated_context(self, user_input: str = "", context_type: str = "full"):
        """統合記憶コンテキストを取得"""
        if self.memory_integration:
            return self.memory_integration.generate_integrated_context(user_input, context_type)
        return ""
    
    def suggest_adaptive_responses(self, user_input: str):
        """適応的応答提案を取得"""
        if self.memory_integration:
            return self.memory_integration.suggest_adaptive_responses(user_input)
        return []
    
    def find_related_memories(self, memory_id: str, memory_type: str, max_results: int = 5):
        """関連記憶を検索"""
        if self.memory_integration:
            return self.memory_integration.find_related_memories(memory_id, memory_type, max_results)
        return []

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

# === 新しい主体性強化システム用メソッド（SetsunaChat クラス外） ===
# これらのメソッドをSetsunaChat クラス内に追加

def add_proactivity_methods_to_setsuna_chat():
    """SetsunaChat クラスに主体性強化メソッドを追加する関数"""
    
    def _check_proactive_opportunity(self, user_input: str, mode: str) -> dict:
        """プロアクティブ応答の機会をチェック"""
        try:
            if not self.proactive_engine or mode == "fast_response":
                return None
            
            # 会話コンテキストを構築
            conversation_context = {
                "last_user_input": user_input,
                "conversation_history": self.conversation_history[-5:],  # 最新5件
                "music_mentioned": any(keyword in user_input.lower() 
                                     for keyword in ["楽曲", "音楽", "歌", "アーティスト"]),
                "technical_discussion": any(keyword in user_input.lower() 
                                          for keyword in ["技術", "分析", "構成", "制作"]),
                "creative_context": any(keyword in user_input.lower() 
                                      for keyword in ["映像", "ビジュアル", "創作", "アイデア"]),
                "collaborative_context": any(keyword in user_input.lower() 
                                           for keyword in ["一緒", "共同", "配信", "共有"])
            }
            
            # プロアクティブ応答判定
            suggestion_decision = self.proactive_engine.should_suggest_proactive_response(conversation_context)
            
            if suggestion_decision.get("should_suggest", False):
                # 具体的な提案を生成
                proactive_suggestion = self.proactive_engine.generate_proactive_suggestion(
                    conversation_context, suggestion_decision.get("suggested_type")
                )
                return proactive_suggestion
            
            return None
            
        except Exception as e:
            print(f"[チャット] ⚠️ プロアクティブ判定エラー: {e}")
            return None
    
    def _build_conversation_context(self, user_input: str, mode: str) -> dict:
        """会話コンテキストを構築"""
        try:
            context = {
                "user_input": user_input,
                "mode": mode,
                "conversation_length": len(self.conversation_history),
                "recent_topics": [],
                "emotional_context": "neutral"
            }
            
            # 最近の話題を抽出
            recent_messages = self.conversation_history[-6:]  # 最新3往復
            for msg in recent_messages:
                if msg.get("role") == "user":
                    content = msg.get("content", "")
                    # 簡単なキーワード抽出
                    if any(keyword in content.lower() for keyword in ["楽曲", "音楽", "歌"]):
                        context["recent_topics"].append("music")
                    if any(keyword in content.lower() for keyword in ["映像", "制作", "創作"]):
                        context["recent_topics"].append("creative")
                    if any(keyword in content.lower() for keyword in ["技術", "分析"]):
                        context["recent_topics"].append("technical")
            
            return context
            
        except Exception as e:
            print(f"[チャット] ⚠️ 会話コンテキスト構築エラー: {e}")
            return {"user_input": user_input, "mode": mode}
    
    def _generate_opinion_context(self, user_input: str, context_info_dict: dict) -> dict:
        """意見生成コンテキストを生成"""
        try:
            if not self.opinion_generator:
                return None
            
            # ユーザー入力から提案や質問を検出
            has_proposal = any(keyword in user_input.lower() 
                             for keyword in ["しよう", "やろう", "どう", "いかが", "してみ"])
            has_question = any(keyword in user_input.lower() 
                             for keyword in ["？", "?", "教えて", "どんな", "なに"])
            
            if has_proposal or has_question:
                # 意見生成の準備
                conversation_context = {
                    "last_user_input": user_input,
                    "music_mentioned": context_info_dict.get("is_video_query", False),
                    "technical_discussion": "技術" in user_input.lower() or "分析" in user_input.lower(),
                    "creative_context": any(keyword in user_input.lower() 
                                          for keyword in ["映像", "創作", "制作"]),
                    "has_proposal": has_proposal,
                    "has_question": has_question
                }
                
                # 意見を生成
                opinion_result = self.opinion_generator.generate_opinion(user_input, conversation_context)
                
                if opinion_result and opinion_result.get("opinion"):
                    return {
                        "generated_opinion": opinion_result["opinion"],
                        "opinion_type": opinion_result.get("opinion_type", "general"),
                        "confidence": opinion_result.get("confidence", 0.5),
                        "reasoning": opinion_result.get("reasoning", "")
                    }
            
            return None
            
        except Exception as e:
            print(f"[チャット] ⚠️ 意見生成コンテキストエラー: {e}")
            return None
    
    def _enhance_response_with_proactive_elements(self, response: str, proactive_suggestion: dict) -> str:
        """応答にプロアクティブ要素を追加"""
        try:
            if not proactive_suggestion:
                return response
            
            suggestion_content = proactive_suggestion.get("suggestion", "")
            suggestion_type = proactive_suggestion.get("type", "")
            
            if suggestion_content:
                # 提案タイプに応じて追加方法を調整
                if suggestion_type == "creative_project_proposal":
                    enhanced_response = f"{response} {suggestion_content}"
                elif suggestion_type == "technical_exploration":
                    enhanced_response = f"{response} ところで、{suggestion_content}"
                else:
                    enhanced_response = f"{response} {suggestion_content}"
                
                # 長すぎる場合は元の応答を返す
                if len(enhanced_response) > 200:
                    return response
                
                return enhanced_response
            
            return response
            
        except Exception as e:
            print(f"[チャット] ⚠️ プロアクティブ要素追加エラー: {e}")
            return response
    
    def get_proactivity_stats(self) -> dict:
        """主体性システムの統計情報を取得"""
        stats = {
            "proactive_suggestions": 0,
            "opinion_generations": 0,
            "consistency_checks": 0,
            "average_proactivity_score": 0.0
        }
        
        try:
            if self.proactive_engine and hasattr(self.proactive_engine, 'suggestion_history'):
                stats["proactive_suggestions"] = len(self.proactive_engine.suggestion_history)
            
            if self.new_consistency_checker and hasattr(self.new_consistency_checker, 'check_history'):
                stats["consistency_checks"] = len(self.new_consistency_checker.check_history)
                
                # 平均スコアを計算
                recent_checks = self.new_consistency_checker.check_history[-10:]
                if recent_checks:
                    scores = [check["result"]["overall_score"] for check in recent_checks]
                    stats["average_proactivity_score"] = sum(scores) / len(scores)
            
        except Exception as e:
            print(f"[チャット] ⚠️ 主体性統計取得エラー: {e}")
        
        return stats
    
    # メソッドをSetsunaChat クラスに追加
    SetsunaChat._check_proactive_opportunity = _check_proactive_opportunity
    SetsunaChat._build_conversation_context = _build_conversation_context
    SetsunaChat._generate_opinion_context = _generate_opinion_context
    SetsunaChat._enhance_response_with_proactive_elements = _enhance_response_with_proactive_elements
    SetsunaChat.get_proactivity_stats = get_proactivity_stats

# メソッドを追加
add_proactivity_methods_to_setsuna_chat()
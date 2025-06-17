#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
せつな記憶システム - シンプル版
セッション内記憶とユーザープロファイル学習
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional

class SimpleMemorySystem:
    """シンプル版記憶システム"""
    
    def __init__(self):
        self.memory_file = "character/setsuna_memory_data.json"
        
        # セッション記憶（メモリ内）
        self.session_memory = {
            "user_inputs": [],
            "conversation_topics": [],
            "user_preferences": {},
            "session_start": datetime.now().isoformat()
        }
        
        # 永続記憶（ファイル保存）
        self.persistent_memory = {
            "user_profile": {},
            "conversation_history": [],
            "learned_facts": [],
            "relationship_level": 1
        }
        
        self._load_persistent_memory()
        print("🧠 シンプル記憶システム初期化完了")
    
    def _load_persistent_memory(self):
        """永続記憶をファイルから読み込み"""
        os.makedirs("character", exist_ok=True)
        
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    self.persistent_memory.update(json.load(f))
                print(f"✅ 既存記憶読み込み: {len(self.persistent_memory['learned_facts'])}件の事実")
            except Exception as e:
                print(f"⚠️ 記憶読み込みエラー: {e}")
    
    def process_conversation(self, user_input: str, setsuna_response: str):
        """会話を処理して記憶に追加"""
        timestamp = datetime.now().isoformat()
        
        # セッション記憶に追加
        self.session_memory["user_inputs"].append({
            "input": user_input,
            "response": setsuna_response,
            "timestamp": timestamp
        })
        
        # 重要な情報を抽出
        self._extract_important_info(user_input, setsuna_response)
        
        print(f"🧠 会話を記憶に追加: '{user_input[:20]}...'")
    
    def _extract_important_info(self, user_input: str, setsuna_response: str):
        """重要な情報を抽出（シンプル版 - キーワードベース）"""
        user_lower = user_input.lower()
        
        # 自己紹介や個人情報の検出
        personal_keywords = {
            "名前": ["名前", "呼んで", "です", "といいます"],
            "趣味": ["趣味", "好き", "よく", "やってる"],
            "仕事": ["仕事", "職業", "働いて", "会社"],
            "年齢": ["歳", "年齢", "才"],
            "住んでいる": ["住んで", "住所", "どこに"]
        }
        
        for category, keywords in personal_keywords.items():
            for keyword in keywords:
                if keyword in user_input:
                    # 新しい事実として記録
                    fact = {
                        "category": category,
                        "content": user_input,
                        "timestamp": datetime.now().isoformat(),
                        "confidence": 0.8
                    }
                    
                    # 重複チェック
                    if not self._is_duplicate_fact(fact):
                        self.persistent_memory["learned_facts"].append(fact)
                        print(f"💡 新しい事実を学習: {category} - {user_input[:30]}...")
                    break
    
    def _is_duplicate_fact(self, new_fact: Dict) -> bool:
        """重複する事実かチェック"""
        for existing_fact in self.persistent_memory["learned_facts"]:
            if (existing_fact["category"] == new_fact["category"] and 
                existing_fact["content"] == new_fact["content"]):
                return True
        return False
    
    def get_memory_context(self) -> str:
        """記憶をプロンプト用のコンテキストとして生成"""
        context_parts = []
        
        # セッション内の最近の会話
        if self.session_memory["user_inputs"]:
            recent_conversations = self.session_memory["user_inputs"][-3:]  # 最新3つ
            context_parts.append("【今回のセッションでの会話】")
            for conv in recent_conversations:
                context_parts.append(f"- ユーザー: {conv['input'][:50]}...")
        
        # 学習した事実
        if self.persistent_memory["learned_facts"]:
            context_parts.append("\n【ユーザーについて学んだこと】")
            for fact in self.persistent_memory["learned_facts"][-5:]:  # 最新5つ
                context_parts.append(f"- {fact['category']}: {fact['content'][:50]}...")
        
        # 関係性レベル
        rel_level = self.persistent_memory.get("relationship_level", 1)
        if rel_level > 1:
            context_parts.append(f"\n【関係性】親密度レベル: {rel_level}")
        
        return "\n".join(context_parts)
    
    def save_memory(self):
        """記憶をファイルに保存"""
        try:
            # セッション終了時に重要な会話を永続記憶に移行
            session_summary = {
                "date": self.session_memory["session_start"][:10],
                "conversation_count": len(self.session_memory["user_inputs"]),
                "topics": list(set(self.session_memory["conversation_topics"])),
                "timestamp": datetime.now().isoformat()
            }
            
            self.persistent_memory["conversation_history"].append(session_summary)
            
            # 記憶件数制限（シンプル版: 最大50件）
            if len(self.persistent_memory["learned_facts"]) > 50:
                self.persistent_memory["learned_facts"] = self.persistent_memory["learned_facts"][-50:]
            
            if len(self.persistent_memory["conversation_history"]) > 20:
                self.persistent_memory["conversation_history"] = self.persistent_memory["conversation_history"][-20:]
            
            # ファイル保存
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.persistent_memory, f, ensure_ascii=False, indent=2)
            
            print("💾 記憶をファイルに保存しました")
            
        except Exception as e:
            print(f"❌ 記憶保存エラー: {e}")
    
    def get_memory_stats(self) -> Dict:
        """記憶統計情報を取得"""
        return {
            "session_conversations": len(self.session_memory["user_inputs"]),
            "learned_facts": len(self.persistent_memory["learned_facts"]),
            "conversation_sessions": len(self.persistent_memory["conversation_history"]),
            "relationship_level": self.persistent_memory.get("relationship_level", 1)
        }
    
    def clear_session_memory(self):
        """セッション記憶をクリア（永続記憶は保持）"""
        self.session_memory = {
            "user_inputs": [],
            "conversation_topics": [],
            "user_preferences": {},
            "session_start": datetime.now().isoformat()
        }
        print("🗑️ セッション記憶をクリアしました")
    
    def get_learned_facts_list(self) -> List[Dict]:
        """学習した事実のリストを取得（編集用）"""
        return self.persistent_memory.get("learned_facts", [])
    
    def delete_learned_fact(self, fact_index: int) -> bool:
        """指定インデックスの学習事実を削除"""
        try:
            if 0 <= fact_index < len(self.persistent_memory["learned_facts"]):
                deleted_fact = self.persistent_memory["learned_facts"].pop(fact_index)
                print(f"🗑️ 事実を削除: {deleted_fact['category']} - {deleted_fact['content'][:30]}...")
                return True
            return False
        except Exception as e:
            print(f"❌ 事実削除エラー: {e}")
            return False
    
    def edit_learned_fact(self, fact_index: int, new_content: str) -> bool:
        """指定インデックスの学習事実を編集"""
        try:
            if 0 <= fact_index < len(self.persistent_memory["learned_facts"]):
                old_fact = self.persistent_memory["learned_facts"][fact_index]
                old_fact["content"] = new_content
                old_fact["timestamp"] = datetime.now().isoformat()
                print(f"✏️ 事実を編集: {old_fact['category']} - {new_content[:30]}...")
                return True
            return False
        except Exception as e:
            print(f"❌ 事実編集エラー: {e}")
            return False
    
    def clear_all_learned_facts(self):
        """全ての学習事実をクリア"""
        count = len(self.persistent_memory["learned_facts"])
        self.persistent_memory["learned_facts"] = []
        print(f"🗑️ 全ての学習事実をクリア: {count}件削除")
    
    def add_manual_fact(self, category: str, content: str) -> bool:
        """手動で事実を追加"""
        try:
            fact = {
                "category": category,
                "content": content,
                "timestamp": datetime.now().isoformat(),
                "confidence": 1.0,  # 手動追加は信頼度100%
                "manual": True
            }
            
            if not self._is_duplicate_fact(fact):
                self.persistent_memory["learned_facts"].append(fact)
                print(f"➕ 手動で事実を追加: {category} - {content[:30]}...")
                return True
            else:
                print(f"⚠️ 重複する事実: {category} - {content[:30]}...")
                return False
        except Exception as e:
            print(f"❌ 手動事実追加エラー: {e}")
            return False

# テスト用
if __name__ == "__main__":
    print("=" * 50)
    print("🧪 シンプル記憶システムテスト")
    print("=" * 50)
    
    memory = SimpleMemorySystem()
    
    # テスト会話
    test_conversations = [
        ("私の名前は田中です", "田中さん、よろしくお願いします"),
        ("趣味は写真撮影です", "写真撮影、素敵な趣味ですね"),
        ("仕事はプログラマーをしています", "プログラマーなんですね、技術的なお話もできそう"),
    ]
    
    for user_input, setsuna_response in test_conversations:
        print(f"\n👤 ユーザー: {user_input}")
        print(f"🤖 せつな: {setsuna_response}")
        memory.process_conversation(user_input, setsuna_response)
    
    # 記憶コンテキスト表示
    print(f"\n🧠 記憶コンテキスト:")
    print(memory.get_memory_context())
    
    # 統計表示
    stats = memory.get_memory_stats()
    print(f"\n📊 記憶統計:")
    for key, value in stats.items():
        print(f"   - {key}: {value}")
    
    # 手動追加テスト
    print(f"\n🔧 手動追加テスト:")
    manual_facts = [
        ("好み", "コーヒーが好き"),
        ("特徴", "早起きが得意"),
        ("好み", "コーヒーが好き"),  # 重複テスト
    ]
    
    for category, content in manual_facts:
        print(f"\n🔧 手動追加: {category} - {content}")
        success = memory.add_manual_fact(category, content)
        if success:
            print("  ✅ 追加成功")
        else:
            print("  ⚠️ 追加失敗（重複）")
    
    # 最終統計
    final_stats = memory.get_memory_stats()
    print(f"\n📊 最終統計:")
    for key, value in final_stats.items():
        print(f"   - {key}: {value}")
    
    # 記憶保存
    memory.save_memory()
    print("\n✅ テスト完了")
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
テスト用記憶システム
セッション限りの記憶（ファイル保存なし）
"""

import json
from datetime import datetime
from typing import Dict, List, Optional
from memory_system import SimpleMemorySystem

class TestMemorySystem(SimpleMemorySystem):
    """テスト用記憶システム（セッション限り）"""
    
    def __init__(self):
        """テスト用記憶システムの初期化"""
        # ファイルパスは設定しない（保存無効）
        self.memory_file = None
        
        # セッション記憶（メモリ内のみ）
        self.session_memory = {
            "user_inputs": [],
            "conversation_topics": [],
            "user_preferences": {},
            "session_start": datetime.now().isoformat(),
            "test_mode": True
        }
        
        # 永続記憶は空で開始（テストモードでは蓄積しない）
        self.persistent_memory = {
            "user_profile": {},
            "conversation_history": [],
            "learned_facts": [],
            "relationship_level": 1,
            "test_session": True
        }
        
        print("🧪 テスト用記憶システム初期化完了（ファイル保存無効）")
    
    def _load_persistent_memory(self):
        """永続記憶の読み込み（テストモードでは何もしない）"""
        # テストモードでは既存の記憶を読み込まない
        # 完全にクリーンな状態で開始
        print("🧪 テストモード: 既存記憶の読み込みをスキップ")
        pass
    
    def save_memory(self):
        """記憶の保存（テストモードでは何もしない）"""
        # ファイル保存は一切行わない
        print("🧪 テストモード: 記憶保存をスキップ（セッション終了時に自動削除）")
        pass
    
    def process_conversation(self, user_input: str, setsuna_response: str):
        """
        会話を処理（セッション内記憶のみ更新）
        
        Args:
            user_input: ユーザーの入力
            setsuna_response: せつなの応答
        """
        # セッション内記憶に追加
        conversation_entry = {
            "timestamp": datetime.now().isoformat(),
            "input": user_input,
            "response": setsuna_response,
            "test_session": True
        }
        
        self.session_memory["user_inputs"].append(conversation_entry)
        
        # セッション内記憶の件数制限（メモリ節約）
        if len(self.session_memory["user_inputs"]) > 20:
            self.session_memory["user_inputs"] = self.session_memory["user_inputs"][-20:]
        
        # 簡単な話題抽出（テスト用の簡素版）
        topics = self._extract_simple_topics(user_input)
        for topic in topics:
            if topic not in self.session_memory["conversation_topics"]:
                self.session_memory["conversation_topics"].append(topic)
        
        print(f"🧪 [TEST] 会話記録: {len(self.session_memory['user_inputs'])}件（セッション限り）")
    
    def _extract_simple_topics(self, text: str) -> List[str]:
        """簡単な話題抽出（テスト用）"""
        topics = []
        
        # 基本的なキーワードマッチング
        topic_keywords = {
            "音楽": ["音楽", "楽曲", "歌", "曲", "BGM"],
            "動画": ["動画", "映像", "YouTube", "配信"],
            "創作": ["創作", "制作", "作品", "プロジェクト"],
            "技術": ["開発", "プログラム", "システム", "技術"]
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in text for keyword in keywords):
                topics.append(topic)
        
        return topics
    
    def get_memory_context(self) -> str:
        """記憶をプロンプト用のコンテキストとして生成（テスト版）"""
        context_parts = []
        
        # テストセッション表示
        context_parts.append("【テストセッション中】")
        
        # セッション内の最近の会話
        if self.session_memory["user_inputs"]:
            recent_conversations = self.session_memory["user_inputs"][-3:]  # 最新3つ
            context_parts.append("【このテストセッションでの会話】")
            for conv in recent_conversations:
                context_parts.append(f"- ユーザー: {conv['input'][:50]}...")
        
        # セッション内の話題
        if self.session_memory["conversation_topics"]:
            context_parts.append(f"\n【話題】{', '.join(self.session_memory['conversation_topics'])}")
        
        # テストモード注意書き
        context_parts.append("\n【注意】テストセッション中のため、この会話は保存されません")
        
        return "\n".join(context_parts)
    
    def get_session_summary(self) -> Dict:
        """セッションの要約を取得（テスト用）"""
        return {
            "mode": "test",
            "session_start": self.session_memory["session_start"],
            "conversation_count": len(self.session_memory["user_inputs"]),
            "topics": self.session_memory["conversation_topics"],
            "duration_info": "セッション終了時に自動削除",
            "persistent_save": False
        }
    
    def clear_session(self):
        """セッションデータをクリア"""
        self.session_memory["user_inputs"].clear()
        self.session_memory["conversation_topics"].clear()
        self.session_memory["user_preferences"].clear()
        print("🧪 テストセッションデータをクリアしました")

if __name__ == "__main__":
    # テスト実行
    print("=== TestMemorySystem テスト ===")
    
    test_memory = TestMemorySystem()
    
    # テスト会話を処理
    test_memory.process_conversation("音楽について教えて", "音楽は素晴らしいものですね")
    test_memory.process_conversation("YouTubeの動画を見ている", "どんな動画を見ているんですか？")
    
    # コンテキスト表示
    print("\n--- メモリコンテキスト ---")
    print(test_memory.get_memory_context())
    
    # セッション要約表示
    print("\n--- セッション要約 ---")
    summary = test_memory.get_session_summary()
    for key, value in summary.items():
        print(f"{key}: {value}")
    
    # セッションクリア
    test_memory.clear_session()
    print(f"\nクリア後の会話数: {len(test_memory.session_memory['user_inputs'])}")
    
    print("\n✅ テスト完了")
"""
会話ログ記録システム
Claude Codeとの会話を自動的にテキストファイルに保存する
"""
import os
import datetime
import json
from typing import List, Dict, Any

class ConversationLogger:
    def __init__(self, log_directory: str = "claude_conversation_logs"):
        self.log_directory = log_directory
        self.current_conversation = []
        self.conversation_count = 0
        
        # ログディレクトリが存在しない場合は作成
        if not os.path.exists(self.log_directory):
            os.makedirs(self.log_directory)
    
    def add_user_message(self, message: str):
        """ユーザーのメッセージを記録"""
        self.current_conversation.append({
            "type": "user",
            "timestamp": datetime.datetime.now().isoformat(),
            "message": message
        })
    
    def add_claude_response(self, response: str):
        """Claudeの応答を記録"""
        self.current_conversation.append({
            "type": "claude",
            "timestamp": datetime.datetime.now().isoformat(),
            "message": response
        })
    
    def save_conversation(self):
        """現在の会話をファイルに保存"""
        if not self.current_conversation:
            return
        
        # タイムスタンプとファイル名の生成
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"conversation_{timestamp}.txt"
        filepath = os.path.join(self.log_directory, filename)
        
        # テキストファイルとして保存
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"=== Claude Code 会話ログ ===\n")
            f.write(f"開始時刻: {self.current_conversation[0]['timestamp']}\n")
            f.write(f"終了時刻: {self.current_conversation[-1]['timestamp']}\n")
            f.write(f"総メッセージ数: {len(self.current_conversation)}\n")
            f.write("=" * 50 + "\n\n")
            
            for entry in self.current_conversation:
                if entry["type"] == "user":
                    f.write(f"[ユーザー] {entry['timestamp']}\n")
                    f.write(f"{entry['message']}\n\n")
                else:
                    f.write(f"[Claude] {entry['timestamp']}\n")
                    f.write(f"{entry['message']}\n\n")
                f.write("-" * 30 + "\n\n")
        
        print(f"会話ログを保存しました: {filepath}")
        self.conversation_count += 1
        self.current_conversation = []
    
    def start_new_conversation(self):
        """新しい会話を開始（前の会話を保存）"""
        if self.current_conversation:
            self.save_conversation()
        self.current_conversation = []
    
    def get_conversation_summary(self):
        """現在の会話の概要を取得"""
        if not self.current_conversation:
            return "会話はまだ開始されていません"
        
        user_messages = len([msg for msg in self.current_conversation if msg["type"] == "user"])
        claude_messages = len([msg for msg in self.current_conversation if msg["type"] == "claude"])
        
        return f"現在の会話: ユーザー{user_messages}メッセージ, Claude{claude_messages}メッセージ"

# グローバルインスタンス
conversation_logger = ConversationLogger()

def log_user_message(message: str):
    """ユーザーメッセージをログに記録"""
    conversation_logger.add_user_message(message)

def log_claude_response(response: str):
    """Claude応答をログに記録"""
    conversation_logger.add_claude_response(response)

def save_current_conversation():
    """現在の会話を保存"""
    conversation_logger.save_conversation()

def start_new_conversation():
    """新しい会話を開始"""
    conversation_logger.start_new_conversation()

if __name__ == "__main__":
    # テスト実行
    logger = ConversationLogger()
    
    # サンプル会話を記録
    logger.add_user_message("こんにちは、Claude")
    logger.add_claude_response("こんにちは！何かお手伝いできることはありますか？")
    logger.add_user_message("会話ログ機能のテストです")
    logger.add_claude_response("会話ログ機能が正常に動作していることを確認しました。")
    
    # 会話を保存
    logger.save_conversation()
    print("テスト会話を保存しました")
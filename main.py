#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
せつなBot メインエントリーポイント
音声中心の対話システム
"""

import sys
import os

# coreモジュールのパスを追加
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from core.voice_conversation import VoiceConversation
except ImportError as e:
    print(f"⚠️ インポートエラー: {e}")
    print("PyAudio問題の可能性があります。test_system.py を使用してください。")
    exit(1)

def main():
    """メイン関数"""
    print("🤖 せつなBot - 音声対話システム")
    print("=" * 50)
    
    try:
        # 音声対話システムの初期化と実行
        voice_conversation = VoiceConversation()
        voice_conversation.conversation_loop()
        
    except KeyboardInterrupt:
        print("\n👋 プログラムを終了しました")
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
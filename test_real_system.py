#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
実システムでのログ機能テスト
音声認識・チャット機能でのログ出力確認
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.setsuna_chat import SetsunaChat
from logging_system import get_logger

def test_setsuna_chat_logging():
    """せつなチャットシステムでのログ確認"""
    print("🧪 実システムテスト: せつなチャット機能")
    print("=" * 50)
    
    try:
        # せつなチャット初期化（ログ統合済み）
        chat = SetsunaChat()
        logger = get_logger()
        
        print("✅ せつなチャットシステム初期化完了")
        
        # テスト用メッセージ
        test_messages = [
            "こんにちは",
            "最近のおすすめの動画ある？",
            "ありがとう"
        ]
        
        print("🔄 テストメッセージでログ記録確認中...")
        
        for i, message in enumerate(test_messages, 1):
            print(f"\n📝 テスト {i}/3: '{message}'")
            
            # 通常モードでテスト
            response = chat.get_response(message, mode="fast_response")
            print(f"   応答: {response[:50]}...")
            
            # ログ記録確認用の情報出力
            logger.info("test_real_system", "test_setsuna_chat_logging", 
                       f"テストメッセージ完了 {i}/3", {
                           "message": message,
                           "response_length": len(response)
                       })
        
        print("\n✅ 実システムテスト完了")
        
        # ログファイル確認
        log_files = list(logger.log_dir.glob("*.log"))
        if log_files:
            latest_log = log_files[0]
            print(f"📄 最新ログファイル: {latest_log.name}")
            
            # ファイルサイズ確認
            file_size = latest_log.stat().st_size
            print(f"📏 ログファイルサイズ: {file_size/1024:.1f}KB")
        
        return True
        
    except Exception as e:
        print(f"❌ 実システムテストエラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_log_content():
    """ログ内容の詳細確認"""
    print("\n🔍 ログ内容確認")
    print("=" * 50)
    
    logger = get_logger()
    log_files = list(logger.log_dir.glob("*.log"))
    
    if not log_files:
        print("❌ ログファイルが見つかりません")
        return False
    
    latest_log = log_files[0]
    
    try:
        with open(latest_log, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print(f"📊 ログエントリ総数: {len(lines)}")
        
        # 最新5件のログを表示
        print("\n📋 最新ログエントリ（最新5件）:")
        for i, line in enumerate(lines[-5:], 1):
            try:
                import json
                entry = json.loads(line.strip())
                timestamp = entry.get('local_time', '')[:19]  # 秒まで
                level = entry.get('level', '')
                module = entry.get('module', '')
                message = entry.get('message', '')
                
                print(f"{i}. [{level}] {timestamp} {module}: {message}")
                
            except json.JSONDecodeError:
                print(f"{i}. [解析エラー] {line[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ ログ確認エラー: {e}")
        return False

if __name__ == "__main__":
    print("🎯 実システムログ機能テスト開始")
    print("=" * 60)
    
    # せつなチャットテスト
    chat_success = test_setsuna_chat_logging()
    
    # ログ内容確認
    log_success = check_log_content()
    
    print("\n" + "=" * 60)
    print("📋 実システムテスト結果")
    print("=" * 60)
    print(f"せつなチャット統合: {'✅ 成功' if chat_success else '❌ 失敗'}")
    print(f"ログ内容確認: {'✅ 成功' if log_success else '❌ 失敗'}")
    
    if chat_success and log_success:
        print("\n🎉 実システムでのログ機能統合成功！")
        print("   実際のせつなBotでログが正常に記録されています。")
    else:
        print("\n⚠️ 一部テストが失敗しました。")
    
    print("\n📝 次のステップ:")
    print("   1. 実際のvoice_chat_gui.pyを起動してテスト")
    print("   2. 音声認識でのログ記録確認") 
    print("   3. Phase 2（バックアップシステム）の開始")
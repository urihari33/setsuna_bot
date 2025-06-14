#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音声対話統合システム - 新せつなBot
音声入力→GPT対話→音声出力の完全パイプライン
"""

import time
from datetime import datetime
try:
    from .voice_input import VoiceInput
except ImportError:
    try:
        # 相対インポートが失敗した場合の絶対インポート
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from voice_input import VoiceInput
    except:
        # PyAudio問題がある場合はモックを使用
        print("[音声] PyAudio問題によりモック音声入力を使用")
        from voice_input_mock import VoiceInput

try:
    from .voice_output import VoiceOutput
except ImportError:
    from voice_output import VoiceOutput

try:
    from .setsuna_chat import SetsunaChat
except ImportError:
    from setsuna_chat import SetsunaChat

class VoiceConversation:
    def __init__(self):
        """音声対話システムの初期化"""
        print("=" * 60)
        print("🤖 せつなBot 音声対話システム初期化中...")
        print("=" * 60)
        
        try:
            # 各モジュールの初期化
            print("[初期化] 音声入力システム...")
            self.voice_input = VoiceInput()
            
            print("[初期化] 音声出力システム...")
            self.voice_output = VoiceOutput()
            
            print("[初期化] チャットシステム...")
            self.setsuna_chat = SetsunaChat()
            
            # 状態管理
            self.is_listening = False
            self.conversation_count = 0
            
            print("✅ せつなBot 初期化完了！")
            
        except Exception as e:
            print(f"❌ 初期化エラー: {e}")
            raise
    
    def single_conversation(self):
        """
        1回の音声対話を実行
        
        Returns:
            bool: 対話が成功したかどうか
        """
        if self.is_listening:
            return False
        
        self.is_listening = True
        conversation_start = time.time()
        
        try:
            print("\n" + "=" * 40)
            print(f"💬 音声対話開始 (#{self.conversation_count + 1})")
            print("=" * 40)
            
            # 1. 音声入力
            print("🎤 音声入力待機中...")
            user_input = self.voice_input.listen(timeout=10, phrase_limit=15)
            
            if not user_input:
                print("⏰ 音声が認識されませんでした")
                return False
            
            print(f"👤 ユーザー: {user_input}")
            
            # 2. GPT応答生成
            print("🤔 せつなが考え中...")
            setsuna_response = self.setsuna_chat.get_response(user_input)
            
            if not setsuna_response:
                print("❌ 応答生成に失敗しました")
                return False
            
            print(f"🤖 せつな: {setsuna_response}")
            
            # 3. 音声出力
            print("🔊 音声合成・再生中...")
            self.voice_output.speak(setsuna_response)
            
            # 統計情報
            conversation_time = time.time() - conversation_start
            self.conversation_count += 1
            
            print(f"✅ 対話完了 (処理時間: {conversation_time:.2f}秒)")
            
            return True
            
        except Exception as e:
            print(f"❌ 対話エラー: {e}")
            return False
            
        finally:
            self.is_listening = False
    
    def conversation_loop(self, max_conversations=None):
        """
        連続音声対話ループ
        
        Args:
            max_conversations: 最大対話回数（Noneで無限）
        """
        print("\n🚀 音声対話ループ開始")
        print("話しかけてください（無音で10秒経過すると待機状態に戻ります）")
        print("Ctrl+C で終了")
        
        try:
            while True:
                # 最大対話数チェック
                if max_conversations and self.conversation_count >= max_conversations:
                    print(f"📊 最大対話数 ({max_conversations}) に到達しました")
                    break
                
                # 1回の対話実行
                success = self.single_conversation()
                
                if success:
                    print("\n⏳ 次の音声入力をお待ちしています...")
                else:
                    print("\n⏳ 音声入力をお待ちしています...")
                
                # 少し間隔を空ける
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n\n👋 音声対話を終了します")
        except Exception as e:
            print(f"\n❌ システムエラー: {e}")
        
        finally:
            self._show_summary()
    
    def _show_summary(self):
        """対話セッションのサマリー表示"""
        print("\n" + "=" * 50)
        print("📊 対話セッション サマリー")
        print("=" * 50)
        print(f"総対話数: {self.conversation_count}回")
        print(f"チャット履歴: {self.setsuna_chat.get_conversation_summary()}")
        print("👋 ありがとうございました！")
    
    def test_all_systems(self):
        """全システムの動作テスト"""
        print("\n🧪 システム動作テスト開始")
        
        tests = [
            ("音声入力", self._test_voice_input),
            ("音声出力", self._test_voice_output), 
            ("チャット", self._test_chat)
        ]
        
        results = []
        for name, test_func in tests:
            print(f"\n--- {name} テスト ---")
            try:
                result = test_func()
                results.append((name, result))
                status = "✅ 成功" if result else "❌ 失敗"
                print(f"{name}: {status}")
            except Exception as e:
                results.append((name, False))
                print(f"{name}: ❌ エラー - {e}")
        
        # 結果サマリー
        print("\n" + "=" * 30)
        print("🧪 テスト結果")
        print("=" * 30)
        for name, result in results:
            status = "✅" if result else "❌"
            print(f"{status} {name}")
        
        success_count = sum(1 for _, result in results if result)
        print(f"\n成功: {success_count}/{len(results)}")
        
        return success_count == len(results)
    
    def _test_voice_input(self):
        """音声入力テスト"""
        print("5秒間の音声入力テスト（何か話してください）")
        result = self.voice_input.listen(timeout=5, phrase_limit=5)
        return bool(result)
    
    def _test_voice_output(self):
        """音声出力テスト"""
        test_text = "音声出力のテストです。"
        self.voice_output.speak(test_text)
        return True
    
    def _test_chat(self):
        """チャットテスト"""
        response = self.setsuna_chat.get_response("テストです")
        return bool(response)

# メイン実行部分
if __name__ == "__main__":
    try:
        # 音声対話システム起動
        voice_conversation = VoiceConversation()
        
        # システムテスト（オプション）
        print("\nシステムテストを実行しますか？ (y/N): ", end="")
        if input().lower().startswith('y'):
            if voice_conversation.test_all_systems():
                print("\n🎉 全テスト成功！音声対話を開始します")
            else:
                print("\n⚠️  一部テスト失敗。続行しますか？ (y/N): ", end="")
                if not input().lower().startswith('y'):
                    exit(1)
        
        # 音声対話ループ開始
        voice_conversation.conversation_loop()
        
    except Exception as e:
        print(f"\n❌ システムエラー: {e}")
        exit(1)
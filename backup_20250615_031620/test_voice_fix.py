#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音声設定修正のテスト
"""

import sys
import os
sys.path.append('core')

from voice_output import VoiceOutput

def test_voice_settings_fix():
    """音声設定の修正をテスト"""
    print("🔊 音声設定修正テスト開始")
    print("=" * 40)
    
    try:
        # 音声出力システム初期化
        voice_output = VoiceOutput()
        print("✅ 音声出力システム初期化成功")
        
        # 初期設定確認
        print(f"📊 初期設定: {voice_output.voice_settings}")
        
        # 設定更新テスト（修正済みメソッド使用）
        print("\n🔧 設定更新テスト...")
        voice_output.update_settings(
            speed=1.3,
            pitch=0.05,
            intonation=1.2
        )
        print(f"📊 更新後設定: {voice_output.voice_settings}")
        
        # 音声合成テスト
        print("\n🎤 音声合成テスト...")
        test_text = "設定が正しく更新されました。"
        audio_path = voice_output.synthesize(test_text)
        
        if audio_path:
            print(f"✅ 音声合成成功: {audio_path}")
            
            # 再度設定変更テスト
            print("\n🔧 再度設定変更テスト...")
            voice_output.update_settings(speed=1.5)
            print(f"📊 再変更後設定: {voice_output.voice_settings}")
            
            # 再度音声合成
            test_text2 = "速度を変更してテストしています。"
            audio_path2 = voice_output.synthesize(test_text2)
            
            if audio_path2:
                print(f"✅ 再合成成功: {audio_path2}")
                print("\n🎉 すべてのテストが成功しました！")
            else:
                print("❌ 再合成失敗")
        else:
            print("❌ 音声合成失敗")
            
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_voice_settings_fix()

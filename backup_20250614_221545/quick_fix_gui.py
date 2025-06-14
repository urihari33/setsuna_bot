#!/usr/bin/env python3
"""
GUI問題の簡単修正スクリプト
"""

def fix_gui_imports():
    """GUIファイルのインポート問題を修正"""
    
    # speech_inputに音声認識のフォールバック機能を追加
    speech_input_fix = '''import speech_recognition as sr
import time

def get_voice_input(timeout=15, phrase_time_limit=15):
    """
    音声入力を取得する統一関数（PyAudio代替対応）
    """
    recognizer = sr.Recognizer()
    
    try:
        # マイクロフォンの初期化（PyAudio不要）
        with sr.Microphone() as source:
            print("[SPEECH] マイク調整中...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            
            print(f"[SPEECH] 音声入力待機中... (最大{timeout}秒)")
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            
        print("[SPEECH] 音声認識処理中...")
        text = recognizer.recognize_google(audio, language="ja-JP")
        print(f"[SPEECH] 認識結果: {text}")
        return text
        
    except sr.WaitTimeoutError:
        print("[SPEECH] タイムアウト: 音声が検出されませんでした")
        return ""
    except sr.UnknownValueError:
        print("[SPEECH] エラー: 音声を認識できませんでした")
        return ""
    except sr.RequestError as e:
        print(f"[SPEECH] サービスエラー: {e}")
        return ""
    except Exception as e:
        print(f"[SPEECH] 音声入力エラー: {e}")
        # フォールバック: テキスト入力
        try:
            fallback_text = input("[FALLBACK] 音声認識失敗。テキストで入力してください: ")
            return fallback_text
        except:
            return ""

# 下位互換性のためのエイリアス
def recognize_speech():
    """下位互換性のためのエイリアス関数"""
    return get_voice_input()

if __name__ == "__main__":
    print("音声入力テスト開始")
    result = get_voice_input()
    if result:
        print(f"テスト結果: {result}")
    else:
        print("音声認識に失敗しました")
'''
    
    # ファイルを書き込み
    with open('/mnt/d/setsuna_bot/speech_input.py', 'w', encoding='utf-8') as f:
        f.write(speech_input_fix)
    
    print("✅ speech_input.py を修正しました")
    
    # ホットキーモードにフォールバック機能を追加
    hotkey_fix = '''import threading
import time
from pynput import keyboard
from setsuna_bot import get_setsuna_response
from speech_input import get_voice_input
from voicevox_speaker import speak_with_voicevox
from setsuna_logger import log_voice_operation, log_error, log_system

# ホットキー制御変数
listening = False
current_keys = set()
required_keys = {keyboard.Key.ctrl_l, keyboard.Key.shift_l, keyboard.Key.alt_l}

def process_voice_interaction():
    """音声対話の処理（フォールバック対応）"""
    global listening
    
    if listening:
        return  # 既に処理中の場合はスキップ
    
    listening = True
    log_system("音声対話処理開始")
    
    try:
        print("\\n🎤 音声入力を開始します...")
        print("話してください（最大15秒）...")
        
        # 音声入力取得
        user_input = get_voice_input(timeout=15, phrase_time_limit=15)
        
        if user_input.strip():
            print(f"\\n👤 ユーザー: {user_input}")
            log_voice_operation("user_input", user_input)
            
            # せつなの応答生成
            print("🤖 せつなが考えています...")
            response = get_setsuna_response(user_input)
            
            if response:
                print(f"🤖 せつな: {response}")
                log_voice_operation("bot_response", response)
                
                # 音声で応答
                print("🔊 音声合成中...")
                speak_with_voicevox(response)
                print("✅ 音声対話完了")
            else:
                print("❌ 応答生成に失敗しました")
                speak_with_voicevox("すみません、うまく応答できませんでした。")
        else:
            print("❌ 音声が認識できませんでした")
            speak_with_voicevox("音声が聞こえませんでした。")
            
    except Exception as e:
        error_msg = f"音声対話エラー: {e}"
        print(f"❌ {error_msg}")
        log_error(error_msg)
        speak_with_voicevox("エラーが発生しました。")
    
    finally:
        listening = False
        log_system("音声対話処理終了")

def on_key_press(key):
    """キー押下時の処理"""
    global current_keys
    current_keys.add(key)
    
    # 必要なキーがすべて押されているかチェック
    if required_keys.issubset(current_keys):
        if not listening:
            print("\\n🚀 ホットキー検出！音声対話を開始します...")
            log_system("ホットキー検出 - 音声対話開始")
            
            # 別スレッドで音声処理を実行
            thread = threading.Thread(target=process_voice_interaction, daemon=True)
            thread.start()

def on_key_release(key):
    """キー解放時の処理"""
    global current_keys
    current_keys.discard(key)
    
    # ESCキーで終了
    if key == keyboard.Key.esc:
        print("\\n👋 アプリケーションを終了します...")
        log_system("アプリケーション終了")
        return False

def main():
    """メイン関数"""
    print("=" * 60)
    print("🤖 Setsuna Bot ホットキーモード")
    print("=" * 60)
    print("🎯 ホットキー: Ctrl + Shift + Alt (左キー)")
    print("🛑 終了: ESCキー")
    print("=" * 60)
    
    log_system("ホットキーモード開始")
    
    try:
        # キーボードリスナー開始
        with keyboard.Listener(
            on_press=on_key_press,
            on_release=on_key_release
        ) as listener:
            print("✅ キーボード監視開始 - ホットキーを待機中...")
            listener.join()
            
    except KeyboardInterrupt:
        print("\\n👋 Ctrl+C で終了しました")
    except Exception as e:
        error_msg = f"ホットキーモードエラー: {e}"
        print(f"❌ {error_msg}")
        log_error(error_msg)
    finally:
        log_system("ホットキーモード終了")

if __name__ == "__main__":
    main()
'''
    
    with open('/mnt/d/setsuna_bot/setsuna_hotkey_mode.py', 'w', encoding='utf-8') as f:
        f.write(hotkey_fix)
    
    print("✅ setsuna_hotkey_mode.py を修正しました")
    print("✅ すべての修正が完了しました")

if __name__ == "__main__":
    fix_gui_imports()
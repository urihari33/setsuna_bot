import threading
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
    """音声対話の処理（簡略化版）"""
    global listening
    
    if listening:
        return  # 既に処理中の場合はスキップ
    
    listening = True
    log_system("音声対話処理開始")
    
    try:
        print("\n🎤 音声入力を開始します...")
        print("話してください（最大15秒）...")
        
        # 音声入力取得
        user_input = get_voice_input(timeout=15, phrase_time_limit=15)
        
        if user_input.strip():
            print(f"\n👤 ユーザー: {user_input}")
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
            print("\n🚀 ホットキー検出！音声対話を開始します...")
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
        print("\n👋 アプリケーションを終了します...")
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
        print("\n👋 Ctrl+C で終了しました")
    except Exception as e:
        error_msg = f"ホットキーモードエラー: {e}"
        print(f"❌ {error_msg}")
        log_error(error_msg)
    finally:
        log_system("ホットキーモード終了")

if __name__ == "__main__":
    main()
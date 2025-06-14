import speech_recognition as sr
import time

def get_voice_input(timeout=10, phrase_time_limit=10):
    """
    音声入力を取得する統一関数（エラー音声なし）
    Args:
        timeout: 音声入力待機のタイムアウト（秒）
        phrase_time_limit: 音声フレーズの最大長（秒）
    Returns:
        str: 認識された音声テキスト（エラー時は空文字列、エラー音声なし）
    """
    recognizer = sr.Recognizer()
    
    try:
        with sr.Microphone() as source:
            # 環境音調整を短縮
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            # 音声待機（タイムアウト短縮）
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            
        # 音声認識実行
        text = recognizer.recognize_google(audio, language="ja-JP")
        if text.strip():
            print(f"[SPEECH] 認識結果: {text}")
            return text
        else:
            return ""
        
    except sr.WaitTimeoutError:
        # タイムアウト時は静かに空文字を返す（エラー音声なし）
        return ""
    except sr.UnknownValueError:
        # 認識失敗時も静かに空文字を返す（エラー音声なし）
        return ""
    except sr.RequestError:
        # サービスエラー時も静かに空文字を返す（エラー音声なし）
        return ""
    except Exception:
        # 予期しないエラー時も静かに空文字を返す（エラー音声なし）
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

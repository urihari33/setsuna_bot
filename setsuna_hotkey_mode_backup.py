import threading
import time
import speech_recognition as sr
from pynput import keyboard
from setsuna_bot import get_setsuna_response
from threading import Lock, Event
from setsuna_logger import log_voice_operation, log_error, log_system
from speech_input import get_voice_input

listening = False
current_keys = set()
required_keys = {keyboard.Key.ctrl_l, keyboard.Key.shift_l, keyboard.Key.alt_l}

# 音声認識用の設定
recognizer = sr.Recognizer()
microphone = sr.Microphone()

# 録音制御用の変数
recording_thread = None
recording_event = Event()  # 録音停止シグナル
recording_lock = Lock()

def simple_voice_input():
    """簡略化された音声入力（PyAudio不使用）"""
    
    with recording_lock:
        audio_frames = []  # 録音データをリセット
        
    try:
        # pyaudioの初期化
        p = pyaudio.PyAudio()
        
        # 録音ストリームを開く
        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )
        
        print("[INFO] リアルタイム録音開始")
        log_voice_operation("REALTIME_RECORDING_START", "Key-controlled recording started")
        
        # キーが押されている間は録音継続
        while not recording_event.is_set():
            try:
                data = stream.read(CHUNK, exception_on_overflow=False)
                with recording_lock:
                    audio_frames.append(data)
            except Exception as e:
                log_error("realtime_recording", f"Stream read error: {e}", e)
                break
                
        # ストリームを閉じる
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        print("[INFO] リアルタイム録音完了")
        log_voice_operation("REALTIME_RECORDING_END", f"Recorded {len(audio_frames)} audio chunks")
        
    except Exception as e:
        error_msg = f"リアルタイム録音失敗: {e}"
        print(f"[ERROR] {error_msg}")
        log_error("hotkey_mode", error_msg, e)
        with recording_lock:
            audio_frames = []

def on_key_press(key):
    global listening, recording_thread
    current_keys.add(key)
    
    if required_keys.issubset(current_keys) and not listening:
        # 既存の録音スレッドが実行中なら待機
        if recording_thread and recording_thread.is_alive():
            return
            
        listening = True
        recording_event.clear()  # 録音停止シグナルをリセット
        print("音声認識待機中（キーを離すまで録音）")
        
        # リアルタイム録音スレッドを開始
        recording_thread = threading.Thread(target=realtime_record_audio, daemon=True)
        recording_thread.start()

def convert_frames_to_audio_data():
    """録音したフレームをspeech_recognition用のAudioDataに変換"""
    global audio_frames
    
    with recording_lock:
        if not audio_frames:
            return None
            
        # 音声データを結合
        raw_data = b''.join(audio_frames)
        
    # WAVファイル形式でラップ
    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, 'wb') as wav_file:
        wav_file.setnchannels(CHANNELS)
        wav_file.setsampwidth(pyaudio.get_sample_size(FORMAT))
        wav_file.setframerate(RATE)
        wav_file.writeframes(raw_data)
    
    wav_buffer.seek(0)
    
    # speech_recognitionのAudioDataオブジェクトとして作成
    wav_data = wav_buffer.read()
    return sr.AudioData(wav_data, RATE, 2)  # 2 = 16bit

def on_key_release(key):
    global listening, recording_thread

    if key in current_keys:
        current_keys.remove(key)

    if listening and not required_keys.issubset(current_keys):
        print("[INFO] キーが離されたため録音停止 → 音声認識へ")
        listening = False  # ここでフラグを先に落とす（2重実行防止）
        
        # 録音停止をシグナル
        recording_event.set()

        def wait_and_process():
            # 録音スレッドの完了を待つ
            if recording_thread:
                recording_thread.join()
            
            # 録音データをAudioDataに変換
            audio_data = convert_frames_to_audio_data()
            
            if audio_data:
                text = None
                try:
                    recognizer = sr.Recognizer()
                    text = recognizer.recognize_google(audio_data, language="ja-JP")
                    print(f"あなた: {text}")
                except sr.UnknownValueError:
                    error_msg = "音声を認識できませんでした。"
                    print(f"[ERROR] {error_msg}")
                    log_voice_operation("RECOGNITION_FAILED", error_msg)
                except sr.RequestError as e:
                    error_msg = f"音声認識サービスに接続できませんでした: {e}"
                    print(f"[ERROR] {error_msg}")
                    log_error("hotkey_mode", error_msg, e)

                if text:
                    log_voice_operation("RECOGNITION_SUCCESS", f"Recognized: {text}")
                    def respond():
                        response = get_setsuna_response(text)
                        print(f"せつな: {response}")
                        
                        # chat_history.jsonに音声対話を保存してGUIに反映させる
                        try:
                            import json
                            import os
                            
                            history_file = "chat_history.json"
                            messages = []
                            
                            # 既存の履歴を読み込み
                            if os.path.exists(history_file):
                                with open(history_file, "r", encoding="utf-8") as f:
                                    messages = json.load(f)
                            
                            # ユーザー入力と応答を追加（get_setsuna_responseで既に追加されている可能性があるが念のため）
                            # 重複チェック: 最後のメッセージが同じでないかチェック
                            if not messages or messages[-1].get("content") != response:
                                # ユーザー入力がまだ追加されていない場合は追加
                                user_exists = (len(messages) >= 2 and 
                                             messages[-2].get("role") == "user" and 
                                             messages[-2].get("content") == text)
                                if not user_exists:
                                    messages.append({"role": "user", "content": text})
                                
                                # 応答がまだ追加されていない場合は追加
                                if not messages or messages[-1].get("content") != response:
                                    messages.append({"role": "assistant", "content": response})
                                
                                # ファイルに保存
                                with open(history_file, "w", encoding="utf-8") as f:
                                    json.dump(messages, f, ensure_ascii=False, indent=2)
                                
                                log_voice_operation("SAVE_SUCCESS", f"Voice conversation saved to {history_file}")
                            else:
                                log_voice_operation("SAVE_SKIP", "Conversation already saved by get_setsuna_response")
                                
                        except Exception as e:
                            log_error("voice_save", f"Failed to save voice conversation: {e}", e)
                    
                    threading.Thread(target=respond, daemon=True).start()
            else:
                print("[WARN] 音声データが空です。")
                log_voice_operation("NO_AUDIO_DATA", "No audio frames recorded")

        threading.Thread(target=wait_and_process, daemon=True).start()



def main():
    print("ホットキーモード起動中（Ctrl + Shift + Alt を同時押しで話しかける）")
    log_system("Hotkey mode started (Ctrl + Shift + Alt)")
    with keyboard.Listener(on_press=on_key_press, on_release=on_key_release) as listener:
        listener.join()

if __name__ == "__main__":
    main()

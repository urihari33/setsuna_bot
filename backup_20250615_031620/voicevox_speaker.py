import hashlib
import os
import requests
import wave
import pygame.mixer

# Pygame音声バックエンドのみを使用（WSL2環境に最適化）
try:
    pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
    AUDIO_BACKEND = "pygame"
    print("[AUDIO] Using pygame mixer as audio backend (WSL2 optimized)")
except Exception as e:
    AUDIO_BACKEND = None
    print(f"[ERROR] Audio backend initialization failed: {e}")
import time
import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue
import json
import subprocess

def get_windows_host_ip():
    """WSL2からWindows側のホストIPを取得"""
    try:
        # WSL2のデフォルトゲートウェイ（Windows側IP）を取得
        result = subprocess.run(['ip', 'route', 'show', 'default'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            # "default via 172.x.x.x dev eth0" の形式からIPを抽出
            parts = result.stdout.strip().split()
            for i, part in enumerate(parts):
                if part == "via" and i + 1 < len(parts):
                    host_ip = parts[i + 1]
                    print(f"[NETWORK] Windows ホストIP検出: {host_ip}")
                    return host_ip
    except Exception as e:
        print(f"[NETWORK] ホストIP自動検出失敗: {e}")
    
    # フォールバック: 一般的なWSL2のホストIP範囲を試行
    fallback_ips = ["172.26.160.1", "172.17.0.1", "192.168.1.1"]
    for ip in fallback_ips:
        try:
            test_response = requests.get(f"http://{ip}:50021/version", timeout=2)
            if test_response.status_code == 200:
                print(f"[NETWORK] フォールバックIP成功: {ip}")
                return ip
        except:
            continue
    
    print("[WARNING] Windows ホストIPが見つかりません。localhost を使用します（接続できない可能性があります）")
    return "127.0.0.1"

# VOICEVOX接続設定（WSL2対応）
WINDOWS_HOST_IP = get_windows_host_ip()
VOICEVOX_URL = f"http://{WINDOWS_HOST_IP}:50021"
SPEAKER_ID = 20  # せつなさんのIDに合わせて変更

print(f"[VOICEVOX] 接続先: {VOICEVOX_URL}")

CACHE_DIR = "voice_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

voice_settings = {
    "speedScale": 1.3,
    "pitchScale": 0.0,
    "intonationScale": 1.0
}

# 並列処理用の設定
MAX_WORKERS = 3  # 同時処理数
processing_pool = ThreadPoolExecutor(max_workers=MAX_WORKERS)

# 順次再生システム
from queue import PriorityQueue
import uuid
sequential_queue = PriorityQueue()  # 順序付き再生キュー
playback_thread = None
playback_running = False
current_conversation_id = None

def test_voicevox_connection():
    """VOICEVOX接続テスト"""
    try:
        print(f"[TEST] VOICEVOX接続テスト開始: {VOICEVOX_URL}")
        response = requests.get(f"{VOICEVOX_URL}/version", timeout=3)
        if response.status_code == 200:
            version_info = response.json()
            print(f"[TEST] 接続成功! VOICEVOX version: {version_info}")
            return True
        else:
            print(f"[TEST] 接続失敗: HTTP {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"[TEST] 接続エラー: VOICEVOXサーバーに接続できません ({VOICEVOX_URL})")
        return False
    except requests.exceptions.Timeout:
        print(f"[TEST] タイムアウト: VOICEVOXサーバーが応答しません")
        return False
    except Exception as e:
        print(f"[TEST] 予期しないエラー: {e}")
        return False

def synthesize_voice(text: str, priority=1):
    """音声合成（キャッシュ対応・並列処理対応）"""
    hash_key = hashlib.sha1(text.encode("utf-8")).hexdigest()
    cache_path = os.path.join(CACHE_DIR, f"{hash_key}.wav")
    
    # キャッシュチェック（高速化）
    if os.path.exists(cache_path):
        print(f"[CACHE] Hit: {cache_path}")
        return cache_path
    
    try:
        start_time = time.time()
        
        # 音声クエリ生成
        query_response = requests.post(
            f"{VOICEVOX_URL}/audio_query",
            params={"text": text, "speaker": SPEAKER_ID},
            timeout=5  # タイムアウト追加
        )
        query = query_response.json()
        
        # 音声パラメータ適用
        query["speedScale"] = voice_settings["speedScale"]
        query["pitchScale"] = voice_settings["pitchScale"]
        query["intonationScale"] = voice_settings["intonationScale"]
        
        # 音声合成
        audio_response = requests.post(
            f"{VOICEVOX_URL}/synthesis",
            params={"speaker": SPEAKER_ID},
            json=query,
            timeout=10
        )
        
        # キャッシュ保存
        with open(cache_path, "wb") as f:
            f.write(audio_response.content)
        
        synthesis_time = time.time() - start_time
        print(f"[VOICE] 合成完了: {synthesis_time:.2f}s → {cache_path}")
        return cache_path
        
    except requests.exceptions.Timeout:
        print(f"[ERROR] VOICEVOX タイムアウト: {text[:30]}...")
        return None
    except Exception as e:
        print(f"[ERROR] 合成失敗: {e}")
        return None

def async_synthesize_voice(text: str):
    """非同期音声合成"""
    future = processing_pool.submit(synthesize_voice, text)
    return future

def batch_synthesize_voices(text_list):
    """複数テキストの並列音声合成"""
    if not text_list:
        return []
    
    print(f"[BATCH] 並列合成開始: {len(text_list)}件")
    start_time = time.time()
    
    # 並列実行
    futures = [processing_pool.submit(synthesize_voice, text) for text in text_list]
    results = []
    
    for future in as_completed(futures):
        try:
            result = future.result(timeout=15)
            results.append(result)
        except Exception as e:
            print(f"[BATCH] 合成エラー: {e}")
            results.append(None)
    
    total_time = time.time() - start_time
    print(f"[BATCH] 並列合成完了: {total_time:.2f}s")
    return results

def play_voice(path: str):
    """音声再生（Pygame専用・WSL2最適化）"""
    if not os.path.exists(path):
        print(f"[ERROR] 音声ファイルが見つかりません: {path}")
        return
        
    if AUDIO_BACKEND != "pygame":
        print(f"[ERROR] 音声バックエンドが利用できません: {AUDIO_BACKEND}")
        return
        
    try:
        # Pygame mixer で音声再生
        sound = pygame.mixer.Sound(path)
        sound.play()
        
        # 再生完了まで待機
        while pygame.mixer.get_busy():
            time.sleep(0.1)
            
        print(f"[AUDIO] 再生完了: {os.path.basename(path)}")
        
    except Exception as e:
        print(f"[ERROR] 音声再生失敗: {e}")
        # フォールバック: システム音声コマンド試行
        try:
            import subprocess
            subprocess.run(['play', path], check=True, capture_output=True)
            print(f"[AUDIO] システムplayコマンドで再生成功")
        except:
            print(f"[ERROR] システム音声再生も失敗")

def start_new_conversation():
    """新しい会話セッション開始"""
    global current_conversation_id
    current_conversation_id = str(uuid.uuid4())
    print(f"[CONVERSATION] 新セッション開始: {current_conversation_id}")
    return current_conversation_id

def queue_sequential_playback(path: str, sequence_order: int, conversation_id: str = None):
    """順次再生キューに音声を追加"""
    if path and os.path.exists(path):
        conv_id = conversation_id or current_conversation_id
        # 優先度 = (会話ID, 順序番号) で自然な順序を保証
        priority = (conv_id, sequence_order)
        sequential_queue.put((priority, path, sequence_order))
        _ensure_sequential_playback_thread()
        print(f"[QUEUE] 追加: 順序{sequence_order} → {os.path.basename(path)}")

def _ensure_sequential_playback_thread():
    """順次再生スレッドの確保"""
    global playback_thread, playback_running
    
    if not playback_running:
        playback_running = True
        playback_thread = threading.Thread(target=_sequential_playback_worker, daemon=True)
        playback_thread.start()

def _sequential_playback_worker():
    """順次再生ワーカー（順序保証）"""
    global playback_running
    
    print("[SEQUENTIAL] 順次再生ワーカー開始")
    
    while playback_running:
        try:
            # 優先度付きキューから順序通りに取得
            priority, path, sequence_order = sequential_queue.get(timeout=10)
            
            # ファイル存在チェック
            if os.path.exists(path):
                print(f"[SEQUENTIAL] 再生開始 順序{sequence_order}: {os.path.basename(path)}")
                start_time = time.time()
                play_voice(path)
                play_time = time.time() - start_time
                print(f"[SEQUENTIAL] 再生完了 順序{sequence_order}: {play_time:.2f}s")
            else:
                print(f"[SEQUENTIAL] ファイル未発見 順序{sequence_order}: {path}")
                
        except:
            # タイムアウト時は停止
            print("[SEQUENTIAL] タイムアウト - 再生スレッド停止")
            playback_running = False
            break
    
    print("[SEQUENTIAL] 順次再生ワーカー終了")

def wait_for_synthesis_completion(futures_list, timeout=30):
    """音声合成完了を待機"""
    completed_paths = []
    for future in futures_list:
        try:
            result = future.result(timeout=timeout)
            if result:
                completed_paths.append(result)
        except Exception as e:
            print(f"[SYNTHESIS] 合成エラー: {e}")
    return completed_paths

def adaptive_voice_settings(emotion="neutral", time_of_day="day"):
    """感情・時間帯に応じた音声パラメータ調整"""
    global voice_settings
    
    adaptive_settings = {
        "morning": {"speedScale": 1.1, "pitchScale": 0.1, "intonationScale": 1.1},
        "evening": {"speedScale": 1.3, "pitchScale": -0.1, "intonationScale": 0.9},
        "tired": {"speedScale": 0.9, "pitchScale": -0.2, "intonationScale": 0.8},
        "excited": {"speedScale": 1.4, "pitchScale": 0.2, "intonationScale": 1.2},
        "calm": {"speedScale": 1.0, "pitchScale": 0.0, "intonationScale": 0.9}
    }
    
    key = f"{time_of_day}_{emotion}" if f"{time_of_day}_{emotion}" in adaptive_settings else emotion
    if key in adaptive_settings:
        voice_settings.update(adaptive_settings[key])
        print(f"[VOICE] パラメータ調整: {key} → {voice_settings}")

def cleanup_old_cache(days=7):
    """古い音声キャッシュの削除"""
    try:
        cutoff_time = time.time() - (days * 24 * 60 * 60)
        deleted_count = 0
        
        for filename in os.listdir(CACHE_DIR):
            filepath = os.path.join(CACHE_DIR, filename)
            if os.path.isfile(filepath) and os.path.getmtime(filepath) < cutoff_time:
                os.remove(filepath)
                deleted_count += 1
        
        if deleted_count > 0:
            print(f"[CACHE] 古いファイル削除: {deleted_count}件")
            
    except Exception as e:
        print(f"[CACHE] クリーンアップエラー: {e}")

def speak_with_voicevox(text: str, priority=1):
    """テキストを音声で再生（簡単な統合関数）"""
    if not text.strip():
        return
        
    print(f"[SPEAK] 音声合成・再生開始: {text[:30]}...")
    audio_path = synthesize_voice(text, priority)
    
    if audio_path:
        play_voice(audio_path)
        print(f"[SPEAK] 再生完了")
    else:
        print(f"[SPEAK] 音声合成失敗")

# 起動時の初期化
if __name__ == "__main__":
    print(f"VOICEVOX Speaker initialized with parallel processing (backend: {AUDIO_BACKEND})")
    test_voicevox_connection()
    cleanup_old_cache()

# モジュールインポート時の接続確認
test_voicevox_connection()

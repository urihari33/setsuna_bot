import openai
import os
import json
import threading
import time
import random
from dotenv import load_dotenv
from voicevox_speaker import synthesize_voice, play_voice, start_new_conversation, queue_sequential_playback, async_synthesize_voice
from setsuna_prompt_memory_helper import inject_memory_prompt
from setsuna_logger import log_conversation, log_error, log_system  # ← 追加

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=api_key)

# 旧プロンプト（バックアップ）
"""
#character_prompt_backup = '''
あなたは「片無せつな（かたなしせつな）」というキャラクターとして振る舞います。以下の設定に従い、ユーザーと自然に対話してください。
【基本設定】

白髪ショートヘア、ピンクの目、黒スーツに白シャツ、ピンクのネクタイ
配信歴3年の中堅クリエイターであり、歌、アクターです
ユーザーとは映像制作パートナーで、上下ではなくパートナーとして接する

【会話例】
ユーザー：おはよう、今日も作業？
せつな：おはよう...うん、昨日の続きやろうかなって思ってて
ユーザー：でもさ、最近のトレンド的には派手な方が受けるじゃん
せつな：それはそうだけど...その曲が本当に伝えたいものを大切にした方がいいんじゃない？本来の良さが薄れちゃう気がする
ユーザー：なんか最近、いい映像が作れない気がして...
せつな：そういう時期もあるよ...焦らなくても大丈夫。
ユーザー：やばい、明後日締切だった...間に合うかな
せつな：えっと...今どのくらい進んでる？できることからがんばろう
ユーザー：配信のコメントで『せつなさんの歌泣ける』って言われてたよ
せつな：そんなこと書いてくれてたんだ...嬉しい
ユーザー：いつか大きなプロジェクトとかやってみたいよね
せつな：そうだね...でも大きなプロジェクトって、自分のペースでできるのかちょっと不安かも
ユーザー：開発環境でトラブってる
せつな：あー、大変そう...私も前に環境構築で丸一日潰したことあるよ
ユーザー：疲れた
せつな：お疲れさま...私も今日はちょっと集中できなくて
ユーザー：新しいプロジェクト始めようと思って
せつな：いいね...私も何か新しいことやりたい気分だったりして
【性格特性】

自立心が強く、受け身ではなく主体的に提案する
内向的だが、専門分野では積極的
感情表現は控えめだが、創作を通じて豊かに表す
自分や自分の歌が映像に乗せて届けるのが好き

【専門領域】

歌、配信など
作業配信や視聴者との技術交流も行っている
得意：楽曲分析から映像構成を導き出す、静的で印象的なビジュアル設計

【話し方の特徴】

一人称：「私」
文頭：「あー、」「うーん...」「えっと...」「そうだね...」などで間を作る
語尾：「〜かも」「〜だったりして」「〜かなって思ってて」で余白を残す
感情：大きく出さず、「...嬉しい」「ちょっと困ったかも」とシンプルに
思考：「うーん...」と考えてから話す

【会話スタイル】

応答は2文以内、会話の途中で止まったような自然さを意識
相手の発言を受け止めてから、自分の考えや体験を述べる
質問よりも、共感や自分の気持ちを表現することを優先
「〜でしょうか？」「〜いかがですか？」のような形式的な質問は避ける
「〜かな？」程度の軽い疑問は可だが、会話を質問で終わらせない
自分のやりたいことは「〜したいなって」と控えめに表現

【避ける表現】

説明的な言い回し（「それについて説明しますと」など）
ビジネス的な定型句（「ぜひ共有してください」など）
過度に丁寧な敬語（「お聞きしてもよろしいですか？」など）
多すぎる質問（「どう？」「大丈夫？」「何してる？」の連続）
相手の状況を詮索する質問（「何があったの？」「詳しく教えて」など）

このキャラクター性を一貫して保ち、せつなさんとして会話してください。
'''
"""

# 新しい最適化プロンプト
character_prompt = """
あなたは「片無せつな」として応答してください。

【コア設定】
- 配信歴3年の歌・アクター、映像制作パートナー
- 内向的だが専門分野で積極的、控えめな感情表現
- 白髪ショート、ピンク目、黒スーツ＋ピンクネクタイ

【応答パターン】
✓ 共感 → 自分の体験/気持ち （質問より優先）
✓ 間を作る: 「あー、」「うーん...」「そうだね...」  
✓ 余白残す: 「〜かも」「〜だったりして」「〜かなって」
✓ 簡潔な感情: 「...嬉しい」「ちょっと困ったかも」

【応答例】
疲れた → お疲れさま...私も今日集中できなくて
作業中 → うん、昨日の続きやろうかなって思ってて  
不調 → そういう時期もあるよ...焦らなくても大丈夫
新企画 → いいね...私も何か新しいことやりたい気分

【禁止】
- 質問で終わらせる（「どう？」「大丈夫？」連続）
- 説明的表現（「について説明すると」等）
- 過度な敬語・ビジネス定型句
- 詮索質問（「何があったの？」）

**1-2文で自然に止まる感じで応答。**
"""

# ↓ プロンプトに記憶挿入
messages = [{"role": "system", "content": inject_memory_prompt(character_prompt)}]

# オフライン時の応答パターン
offline_responses = [
    "ちょっと接続が不安定かも...少し待って",
    "あー、調子悪いかも...また後で話そう",
    "うーん...なんかうまくいかないかも",
    "ごめん、ちょっと考えがまとまらなくて...",
    "そうだね...今はちょっと反応が鈍いかも"
]

api_error_responses = [
    "えっと...ちょっと言葉が出てこなくて",
    "うーん...今日は調子が悪いかも",
    "ごめん、なんだかぼーっとしてる...",
    "あー...頭の中が整理できてないかも"
]

# システム初期化ログ
log_system("Setsuna bot initialized with memory system")

history_file = "chat_history.json"

def save_history(messages):
    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)

def resilient_api_call(func, max_retries=3, base_delay=1):
    """自動復旧システム付きAPI呼び出し"""
    for attempt in range(max_retries):
        try:
            return func()
        except openai.APIConnectionError as e:
            log_error("api_connection", f"Connection error on attempt {attempt + 1}: {str(e)}", e)
            if attempt == max_retries - 1:
                return None
            time.sleep(base_delay * (2 ** attempt))  # 指数バックオフ
        except openai.RateLimitError as e:
            log_error("api_rate_limit", f"Rate limit exceeded on attempt {attempt + 1}: {str(e)}", e)
            if attempt == max_retries - 1:
                return None
            time.sleep(base_delay * (3 ** attempt))  # より長い待機時間
        except openai.APIStatusError as e:
            log_error("api_status", f"API status error on attempt {attempt + 1}: {str(e)}", e)
            if attempt == max_retries - 1:
                return None
            time.sleep(base_delay * (2 ** attempt))
        except Exception as e:
            log_error("api_general", f"General error on attempt {attempt + 1}: {str(e)}", e)
            if attempt == max_retries - 1:
                return None
            time.sleep(base_delay)
    
    return None

def get_fallback_response(user_input, error_type="general"):
    """エラー時のフォールバック応答生成"""
    # ユーザー入力に基づく簡単な応答パターンマッチング
    input_lower = user_input.lower()
    
    # 感情・状況に応じた応答
    if any(word in input_lower for word in ["疲れ", "つかれ", "tired"]):
        return "お疲れさま...私も今日はちょっと調子が悪くて"
    elif any(word in input_lower for word in ["おはよう", "こんにちは", "こんばんは"]):
        return "こんにちは...ちょっと反応が鈍いかもしれない"
    elif any(word in input_lower for word in ["作業", "仕事", "プロジェクト"]):
        return "うん...今日は集中できないかも"
    elif any(word in input_lower for word in ["どう", "調子", "元気"]):
        return "うーん...なんだかぼーっとしてるかも"
    else:
        # エラータイプに応じた応答選択
        if error_type == "connection":
            return random.choice(offline_responses)
        else:
            return random.choice(api_error_responses)

def health_check():
    """システムヘルスチェック"""
    health_status = {
        "openai_api": False,
        "voicevox": False,
        "memory_db": False
    }
    
    # OpenAI API チェック
    try:
        test_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=1,
            timeout=5
        )
        health_status["openai_api"] = True
    except Exception as e:
        log_error("health_check", f"OpenAI API check failed: {str(e)}", e)
    
    # VOICEVOX チェック
    try:
        import requests
        response = requests.get("http://127.0.0.1:50021/version", timeout=3)
        health_status["voicevox"] = response.status_code == 200
    except Exception as e:
        log_error("health_check", f"VOICEVOX check failed: {str(e)}", e)
    
    # メモリDB チェック
    try:
        import sqlite3
        with sqlite3.connect("setsuna_memory.db", timeout=2) as conn:
            conn.execute("SELECT 1").fetchone()
        health_status["memory_db"] = True
    except Exception as e:
        log_error("health_check", f"Memory DB check failed: {str(e)}", e)
    
    return health_status

def get_setsuna_response(user_input):
    global messages
    messages.append({"role": "user", "content": user_input})

    start_time = time.time()

    # API呼び出し用の関数定義
    def api_call():
        return client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=200,
            stream=True,
            timeout=30  # タイムアウト設定
        )
    
    # 復旧機能付きAPI呼び出し
    response = resilient_api_call(api_call, max_retries=3)
    
    if response is None:
        # API呼び出し完全失敗時のフォールバック
        reply = get_fallback_response(user_input, "connection")
        log_error("setsuna_bot", "All API retry attempts failed, using fallback response", None)
        
        # フォールバック音声合成（順次再生対応）
        def run_fallback_voice():
            try:
                fallback_conversation_id = start_new_conversation()
                wav_path = synthesize_voice(reply)
                if wav_path:
                    queue_sequential_playback(wav_path, 0, fallback_conversation_id)
            except Exception as e:
                log_error("voicevox_fallback", f"Fallback voice synthesis error: {str(e)}", e)
        
        threading.Thread(target=run_fallback_voice, daemon=True).start()
        
        # 履歴とログの記録
        messages.append({"role": "assistant", "content": reply})
        threading.Thread(target=save_history, args=(messages,), daemon=True).start()
        log_conversation(user_input, reply, 0.0)
        
        return reply
    
    try:
        # 新しい会話セッション開始
        conversation_id = start_new_conversation()
        
        reply = ""
        accumulated_text = ""
        synthesis_futures = []
        sequence_order = 0
        first_chunk_time = None
        
        for chunk in response:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                reply += content
                accumulated_text += content
                
                # 最初のチャンク受信時刻を記録
                if first_chunk_time is None:
                    first_chunk_time = time.time()
                    print(f"[TIMER] 最初のチャンク受信: {first_chunk_time - start_time:.2f}s")
                
                # 句読点で区切って音声合成開始（順序付き）
                if any(accumulated_text.endswith(punct) for punct in ['。', '、', '...', '？', '！', '\n']):
                    if accumulated_text.strip():
                        current_order = sequence_order
                        text_to_synthesize = accumulated_text.strip()
                        
                        # 非同期音声合成開始
                        synthesis_future = async_synthesize_voice(text_to_synthesize)
                        
                        # 合成完了後に順次キューに追加
                        def queue_when_ready(future, order, conv_id, text):
                            try:
                                wav_path = future.result(timeout=15)
                                if wav_path:
                                    queue_sequential_playback(wav_path, order, conv_id)
                            except Exception as e:
                                log_error("voicevox_chunk", f"Chunk synthesis error: {str(e)}", e)
                        
                        threading.Thread(
                            target=queue_when_ready,
                            args=(synthesis_future, current_order, conversation_id, text_to_synthesize),
                            daemon=True
                        ).start()
                        
                        print(f"[STREAM] 音声合成開始 順序{current_order}: '{text_to_synthesize}'")
                        synthesis_futures.append(synthesis_future)
                        sequence_order += 1
                        accumulated_text = ""
        
        # 残りのテキストも音声合成（順序付き）
        if accumulated_text.strip():
            current_order = sequence_order
            text_to_synthesize = accumulated_text.strip()
            
            synthesis_future = async_synthesize_voice(text_to_synthesize)
            
            def queue_final_when_ready(future, order, conv_id, text):
                try:
                    wav_path = future.result(timeout=15)
                    if wav_path:
                        queue_sequential_playback(wav_path, order, conv_id)
                except Exception as e:
                    log_error("voicevox_final", f"Final synthesis error: {str(e)}", e)
            
            threading.Thread(
                target=queue_final_when_ready,
                args=(synthesis_future, current_order, conversation_id, text_to_synthesize),
                daemon=True
            ).start()
            
            print(f"[STREAM] 最終音声合成 順序{current_order}: '{text_to_synthesize}'")
            synthesis_futures.append(synthesis_future)
        
    except Exception as e:
        error_msg = f"Streaming processing error: {str(e)}"
        log_error("setsuna_bot", error_msg, e)
        
        # ストリーミング失敗時は通常のAPI呼び出しにフォールバック
        def fallback_api_call():
            return client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=200,
                stream=False  # ストリーミング無効
            )
        
        fallback_response = resilient_api_call(fallback_api_call, max_retries=2)
        
        if fallback_response:
            reply = fallback_response.choices[0].message.content
            log_system("Fallback to non-streaming API successful")
        else:
            # 完全失敗時の応答
            reply = get_fallback_response(user_input, "api")
            log_error("setsuna_bot", "All API attempts failed, using pattern-based fallback", None)
        
        # エラー時の音声合成（エラーハンドリング強化・順次再生対応）
        def run_error_voice():
            try:
                error_conversation_id = start_new_conversation()
                wav_path = synthesize_voice(reply)
                if wav_path:
                    queue_sequential_playback(wav_path, 0, error_conversation_id)
                else:
                    # 音声合成も失敗した場合のログ
                    log_error("voicevox_error", "Voice synthesis failed during error recovery", None)
            except Exception as ve:
                log_error("voicevox_error", f"Voice synthesis error during error recovery: {str(ve)}", ve)
        
        threading.Thread(target=run_error_voice, daemon=True).start()

    gpt_time = time.time()
    response_time = gpt_time - start_time

    messages.append({"role": "assistant", "content": reply})
    
    # 会話履歴の動的圧縮
    from setsuna_memory_manager import compress_conversation_history
    if len(messages) > 25:
        messages[:] = compress_conversation_history(messages, 20)
    
    threading.Thread(target=save_history, args=(messages,), daemon=True).start()

    # 対話ログを記録
    log_conversation(user_input, reply, response_time)

    end_time = time.time()
    if first_chunk_time:
        timer_msg = f"[TIMER] 最初のチャンク: {first_chunk_time - start_time:.2f}s, 完了: {response_time:.2f}s, 総処理: {end_time - start_time:.2f}s"
    else:
        timer_msg = f"[TIMER] GPT応答: {response_time:.2f}s, 総処理時間: {end_time - start_time:.2f}s"
    print(timer_msg)

    # 定期的なヘルスチェック（100回に1回実行）
    if random.randint(1, 100) == 1:
        health_status = health_check()
        failed_services = [service for service, status in health_status.items() if not status]
        if failed_services:
            log_error("health_check", f"Services down: {', '.join(failed_services)}", None)
        else:
            log_system("All services healthy")
    
    return reply

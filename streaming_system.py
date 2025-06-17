#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GPT-4ストリーミング応答システム
リアルタイム応答生成と並列音声合成
"""

import asyncio
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, List, Callable
import re

class StreamTextProcessor:
    """ストリーミングテキストの分割処理"""
    
    def __init__(self):
        self.buffer = ""
        self.sentence_delimiters = ["。", "！", "？", ".", "!", "?"]
        self.pause_markers = ["、", ",", "...", "〜"]
        self.min_sentence_length = 8  # 最小文字数
        self.max_sentence_length = 80  # 最大文字数
        
    def process_chunk(self, chunk_text: str) -> List[str]:
        """チャンクテキストを処理して完成した文章を返す"""
        self.buffer += chunk_text
        sentences = self._extract_complete_sentences()
        return sentences
    
    def _extract_complete_sentences(self) -> List[str]:
        """完成した文章を抽出"""
        sentences = []
        
        # 文章区切りで分割
        for delimiter in self.sentence_delimiters:
            if delimiter in self.buffer:
                parts = self.buffer.split(delimiter, 1)  # 最初の区切りのみ
                sentence = parts[0] + delimiter
                
                # 文字数チェック
                if len(sentence.strip()) >= self.min_sentence_length:
                    sentences.append(sentence.strip())
                    self.buffer = parts[1] if len(parts) > 1 else ""
                    break
        
        # 長すぎる場合は強制分割
        if len(self.buffer) > self.max_sentence_length:
            # 句読点で分割を試行
            for marker in self.pause_markers:
                if marker in self.buffer:
                    parts = self.buffer.split(marker, 1)
                    sentence = parts[0] + marker
                    if len(sentence.strip()) >= self.min_sentence_length:
                        sentences.append(sentence.strip())
                        self.buffer = parts[1] if len(parts) > 1 else ""
                        break
        
        return sentences
    
    def get_remaining_buffer(self) -> str:
        """残りのバッファを取得してクリア"""
        remaining = self.buffer.strip()
        self.buffer = ""
        return remaining
    
    def clear_buffer(self):
        """バッファをクリア"""
        self.buffer = ""

class ParallelVoiceSynthesis:
    """並列音声合成システム"""
    
    def __init__(self, voice_synthesizer, max_workers: int = 3):
        self.voice_synthesizer = voice_synthesizer
        self.synthesis_queue = asyncio.Queue()
        self.playback_queue = asyncio.Queue()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.is_running = False
        self.synthesis_task = None
        self.playback_task = None
        
        print(f"🎵 並列音声合成システム初期化（ワーカー数: {max_workers}）")
    
    async def start_workers(self):
        """ワーカータスクを開始"""
        if self.is_running:
            return
        
        self.is_running = True
        self.synthesis_task = asyncio.create_task(self._synthesis_worker())
        self.playback_task = asyncio.create_task(self._playback_worker())
        print("🚀 音声合成ワーカー開始")
    
    async def stop_workers(self):
        """ワーカータスクを停止"""
        self.is_running = False
        
        if self.synthesis_task:
            self.synthesis_task.cancel()
        if self.playback_task:
            self.playback_task.cancel()
        
        # キューをクリア
        while not self.synthesis_queue.empty():
            try:
                self.synthesis_queue.get_nowait()
                self.synthesis_queue.task_done()
            except asyncio.QueueEmpty:
                break
        
        while not self.playback_queue.empty():
            try:
                self.playback_queue.get_nowait()
                self.playback_queue.task_done()
            except asyncio.QueueEmpty:
                break
        
        print("⏹️ 音声合成ワーカー停止")
    
    async def add_sentence_for_synthesis(self, sentence: str):
        """音声合成キューに文章追加"""
        if self.is_running:
            await self.synthesis_queue.put(sentence)
            print(f"📝 音声合成キューイング: {sentence[:30]}...")
    
    async def _synthesis_worker(self):
        """音声合成ワーカー"""
        while self.is_running:
            try:
                sentence = await asyncio.wait_for(
                    self.synthesis_queue.get(), 
                    timeout=1.0
                )
                
                # 別スレッドで音声合成実行
                loop = asyncio.get_event_loop()
                start_time = time.time()
                
                wav_path = await loop.run_in_executor(
                    self.executor,
                    self.voice_synthesizer.synthesize_voice,
                    sentence
                )
                
                synthesis_time = time.time() - start_time
                
                if wav_path:
                    await self.playback_queue.put((wav_path, sentence))
                    print(f"✅ 音声合成完了: {synthesis_time:.2f}s")
                else:
                    print(f"❌ 音声合成失敗: {sentence[:30]}...")
                
                self.synthesis_queue.task_done()
                
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"❌ 音声合成ワーカーエラー: {e}")
    
    async def _playback_worker(self):
        """音声再生ワーカー"""
        while self.is_running:
            try:
                wav_path, sentence = await asyncio.wait_for(
                    self.playback_queue.get(),
                    timeout=1.0
                )
                
                # 音声再生
                loop = asyncio.get_event_loop()
                start_time = time.time()
                
                success = await loop.run_in_executor(
                    self.executor,
                    self.voice_synthesizer.play_voice,
                    wav_path
                )
                
                playback_time = time.time() - start_time
                
                if success:
                    print(f"🔊 音声再生完了: {playback_time:.2f}s")
                else:
                    print(f"❌ 音声再生失敗: {sentence[:30]}...")
                
                self.playback_queue.task_done()
                
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"❌ 音声再生ワーカーエラー: {e}")
    
    async def wait_completion(self):
        """全ての処理完了を待機"""
        await self.synthesis_queue.join()
        await self.playback_queue.join()
        print("✅ 全音声処理完了")

class StreamingResponseSystem:
    """ストリーミング応答統合システム"""
    
    def __init__(self, setsuna_chat, voice_synthesizer):
        self.setsuna_chat = setsuna_chat
        self.voice_synthesizer = voice_synthesizer
        self.text_processor = StreamTextProcessor()
        self.parallel_synthesis = ParallelVoiceSynthesis(voice_synthesizer)
        self.gui_callback = None
        
        print("🌊 ストリーミング応答システム初期化完了")
    
    def set_gui_callback(self, callback: Callable[[str], None]):
        """GUIコールバック設定"""
        self.gui_callback = callback
    
    async def get_streaming_response(self, user_input: str) -> str:
        """ストリーミング応答のメイン処理"""
        print(f"🌊 ストリーミング応答開始: {user_input}")
        
        # テキスト処理器リセット
        self.text_processor.clear_buffer()
        
        # 並列音声合成開始
        await self.parallel_synthesis.start_workers()
        
        full_response = ""
        sentence_count = 0
        
        try:
            # GPT-4ストリーミング開始
            stream_start_time = time.time()
            stream = self.setsuna_chat.get_streaming_response_internal(user_input)
            
            print("📡 GPT-4ストリーミング開始")
            
            async for chunk_text in stream:
                if chunk_text:
                    full_response += chunk_text
                    
                    # GUIに部分更新通知
                    if self.gui_callback:
                        self.gui_callback(f"受信中: {full_response[-50:]}")
                    
                    # 文章分割・音声合成キューイング
                    complete_sentences = self.text_processor.process_chunk(chunk_text)
                    
                    for sentence in complete_sentences:
                        await self.parallel_synthesis.add_sentence_for_synthesis(sentence)
                        sentence_count += 1
            
            # 残りのバッファ処理
            remaining = self.text_processor.get_remaining_buffer()
            if remaining.strip():
                await self.parallel_synthesis.add_sentence_for_synthesis(remaining)
                sentence_count += 1
            
            stream_time = time.time() - stream_start_time
            print(f"📡 ストリーミング受信完了: {stream_time:.2f}s, {sentence_count}文")
            
            # 最終GUI更新
            if self.gui_callback:
                self.gui_callback(full_response)
            
            # 全音声処理完了を待機
            await self.parallel_synthesis.wait_completion()
            
        except Exception as e:
            print(f"❌ ストリーミング処理エラー: {e}")
        finally:
            # ワーカー停止
            await self.parallel_synthesis.stop_workers()
        
        print(f"🌊 ストリーミング応答完了: {len(full_response)}文字")
        return full_response

class AsyncGUIIntegration:
    """非同期GUIシステム統合"""
    
    def __init__(self, gui):
        self.gui = gui
        self.streaming_system = None
        
    def initialize_streaming(self):
        """ストリーミングシステム初期化"""
        if self.gui.setsuna_chat and self.gui.voice_synthesizer:
            self.streaming_system = StreamingResponseSystem(
                self.gui.setsuna_chat,
                self.gui.voice_synthesizer
            )
            
            # GUIコールバック設定
            self.streaming_system.set_gui_callback(self._update_gui_partial)
            print("🔗 非同期GUI統合完了")
        else:
            print("❌ ストリーミング初期化失敗: システムコンポーネント不足")
    
    def _update_gui_partial(self, partial_text: str):
        """部分テキストのGUI更新"""
        # メインスレッドで実行
        self.gui.root.after(0, lambda: self.gui.update_voice_status(f"受信中: {len(partial_text)}文字"))
    
    def start_streaming_response(self, user_input: str):
        """ストリーミング応答開始"""
        if not self.streaming_system:
            print("❌ ストリーミングシステムが初期化されていません")
            return
        
        # 別スレッドで非同期処理実行
        threading.Thread(
            target=self._run_async_response,
            args=(user_input,),
            daemon=True
        ).start()
    
    def _run_async_response(self, user_input: str):
        """別スレッドで非同期処理実行"""
        try:
            asyncio.run(self._async_response_handler(user_input))
        except Exception as e:
            print(f"❌ 非同期応答エラー: {e}")
            # エラー時のGUI更新
            self.gui.root.after(0, lambda: self.gui.update_voice_status("エラー"))
    
    async def _async_response_handler(self, user_input: str):
        """非同期応答処理"""
        try:
            response = await self.streaming_system.get_streaming_response(user_input)
            
            # 最終GUI更新
            self.gui.root.after(0, lambda: self.gui.add_message_to_history(
                "せつな", response, "text"
            ))
            self.gui.root.after(0, lambda: self.gui.update_voice_status("完了"))
            
        except Exception as e:
            print(f"❌ 非同期応答処理エラー: {e}")
            self.gui.root.after(0, lambda: self.gui.update_voice_status("エラー"))

# テスト用
if __name__ == "__main__":
    print("="*60)
    print("🧪 ストリーミングシステムテスト")
    print("="*60)
    
    # 簡単なテスト
    processor = StreamTextProcessor()
    
    test_chunks = [
        "こんに", "ちは！", "今日は", "いい天気", "ですね。",
        "どのよう", "なお手伝い", "ができる", "でしょうか？"
    ]
    
    print("📝 文章分割テスト:")
    for chunk in test_chunks:
        sentences = processor.process_chunk(chunk)
        for sentence in sentences:
            print(f"  → 完成文章: {sentence}")
    
    # 残りバッファ
    remaining = processor.get_remaining_buffer()
    if remaining:
        print(f"  → 残りバッファ: {remaining}")
    
    print("\n✅ テスト完了")
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
クラウド音声認識サービス統合
WSL2環境でも動作する音声入力の代替手段
"""

import asyncio
import aiohttp
import base64
import json
import tempfile
import os
from typing import Optional

class CloudVoiceInput:
    """クラウドベース音声認識"""
    
    def __init__(self):
        self.google_api_key = os.getenv('GOOGLE_CLOUD_API_KEY')
        self.recognition_url = "https://speech.googleapis.com/v1/speech:recognize"
    
    async def recognize_from_url(self, audio_url: str) -> Optional[str]:
        """音声URLから認識"""
        try:
            # 音声ファイルをダウンロード
            async with aiohttp.ClientSession() as session:
                async with session.get(audio_url) as response:
                    if response.status == 200:
                        audio_data = await response.read()
                        return await self._recognize_audio_data(audio_data)
            return None
        except Exception as e:
            print(f"❌ URL音声認識エラー: {e}")
            return None
    
    async def recognize_from_file(self, file_path: str) -> Optional[str]:
        """ローカルファイルから認識"""
        try:
            with open(file_path, 'rb') as audio_file:
                audio_data = audio_file.read()
            return await self._recognize_audio_data(audio_data)
        except Exception as e:
            print(f"❌ ファイル音声認識エラー: {e}")
            return None
    
    async def _recognize_audio_data(self, audio_data: bytes) -> Optional[str]:
        """音声データから認識"""
        try:
            if not self.google_api_key:
                print("⚠️ Google Cloud API Key が設定されていません")
                return "クラウド音声認識テスト"
            
            # Base64エンコード
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')
            
            # リクエスト作成
            request_data = {
                "config": {
                    "encoding": "WEBM_OPUS",
                    "sampleRateHertz": 48000,
                    "languageCode": "ja-JP",
                    "enableAutomaticPunctuation": True,
                    "model": "latest_long"
                },
                "audio": {
                    "content": audio_base64
                }
            }
            
            # Google Cloud Speech-to-Text API呼び出し
            async with aiohttp.ClientSession() as session:
                url = f"{self.recognition_url}?key={self.google_api_key}"
                async with session.post(url, json=request_data) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        if 'results' in result and len(result['results']) > 0:
                            transcript = result['results'][0]['alternatives'][0]['transcript']
                            print(f"✅ クラウド音声認識: {transcript}")
                            return transcript.strip()
                    else:
                        error_text = await response.text()
                        print(f"❌ API エラー: {response.status} - {error_text}")
            
            return None
            
        except Exception as e:
            print(f"❌ クラウド音声認識エラー: {e}")
            return None

# テスト用
if __name__ == "__main__":
    import asyncio
    
    async def test_cloud_voice():
        cloud_voice = CloudVoiceInput()
        
        # テスト
        result = await cloud_voice._recognize_audio_data(b"dummy_audio_data")
        print(f"テスト結果: {result}")
    
    asyncio.run(test_cloud_voice())
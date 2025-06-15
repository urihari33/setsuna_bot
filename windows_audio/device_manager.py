#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows音声デバイス管理
音声入力・出力デバイスの検出・選択・設定
"""

import pyaudio
import sounddevice as sd
import json
import os
from typing import List, Dict, Optional, Tuple


class WindowsAudioDeviceManager:
    """Windows音声デバイス管理クラス"""
    
    def __init__(self):
        self.pyaudio_instance = None
        self.input_devices = []
        self.output_devices = []
        self.default_input_device = None
        self.default_output_device = None
        
        # 設定ファイルパス
        self.config_dir = os.path.expandvars('%APPDATA%\\SetsunaBot')
        self.config_file = os.path.join(self.config_dir, 'audio_config.json')
        
        self._ensure_config_dir()
        self._initialize_pyaudio()
        self._discover_devices()
        self._load_saved_settings()
    
    def _ensure_config_dir(self):
        """設定ディレクトリ作成"""
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
            print(f"📁 設定ディレクトリ作成: {self.config_dir}")
    
    def _initialize_pyaudio(self):
        """PyAudio初期化"""
        try:
            self.pyaudio_instance = pyaudio.PyAudio()
            print("✅ PyAudio初期化成功")
            return True
        except Exception as e:
            print(f"❌ PyAudio初期化失敗: {e}")
            return False
    
    def _discover_devices(self):
        """音声デバイス検出"""
        if not self.pyaudio_instance:
            print("⚠️  PyAudio未初期化のためデバイス検出をスキップ")
            return
        
        try:
            # PyAudioデバイス情報取得
            device_count = self.pyaudio_instance.get_device_count()
            print(f"🔍 検出されたデバイス数: {device_count}")
            
            self.input_devices = []
            self.output_devices = []
            
            for i in range(device_count):
                device_info = self.pyaudio_instance.get_device_info_by_index(i)
                
                # 入力デバイス
                if device_info['maxInputChannels'] > 0:
                    input_device = {
                        'index': i,
                        'name': device_info['name'],
                        'channels': device_info['maxInputChannels'],
                        'sample_rate': int(device_info['defaultSampleRate']),
                        'is_default': i == self.pyaudio_instance.get_default_input_device_info()['index']
                    }
                    self.input_devices.append(input_device)
                    
                    if input_device['is_default']:
                        self.default_input_device = input_device
                
                # 出力デバイス
                if device_info['maxOutputChannels'] > 0:
                    output_device = {
                        'index': i,
                        'name': device_info['name'],
                        'channels': device_info['maxOutputChannels'],
                        'sample_rate': int(device_info['defaultSampleRate']),
                        'is_default': i == self.pyaudio_instance.get_default_output_device_info()['index']
                    }
                    self.output_devices.append(output_device)
                    
                    if output_device['is_default']:
                        self.default_output_device = output_device
            
            print(f"🎤 入力デバイス: {len(self.input_devices)}個")
            print(f"🔊 出力デバイス: {len(self.output_devices)}個")
            
        except Exception as e:
            print(f"❌ デバイス検出エラー: {e}")
    
    def get_input_devices(self) -> List[Dict]:
        """入力デバイス一覧取得"""
        return self.input_devices.copy()
    
    def get_output_devices(self) -> List[Dict]:
        """出力デバイス一覧取得"""
        return self.output_devices.copy()
    
    def get_default_input_device(self) -> Optional[Dict]:
        """デフォルト入力デバイス取得"""
        return self.default_input_device
    
    def get_default_output_device(self) -> Optional[Dict]:
        """デフォルト出力デバイス取得"""
        return self.default_output_device
    
    def print_device_info(self):
        """デバイス情報表示"""
        print("\n🎤 === 入力デバイス ===")
        for device in self.input_devices:
            default_mark = " [デフォルト]" if device['is_default'] else ""
            print(f"  {device['index']}: {device['name']}{default_mark}")
            print(f"      チャンネル: {device['channels']}, サンプリングレート: {device['sample_rate']}Hz")
        
        print("\n🔊 === 出力デバイス ===")
        for device in self.output_devices:
            default_mark = " [デフォルト]" if device['is_default'] else ""
            print(f"  {device['index']}: {device['name']}{default_mark}")
            print(f"      チャンネル: {device['channels']}, サンプリングレート: {device['sample_rate']}Hz")
        print()
    
    def test_input_device(self, device_index: Optional[int] = None) -> bool:
        """入力デバイステスト"""
        if not self.pyaudio_instance:
            return False
        
        if device_index is None:
            if self.default_input_device:
                device_index = self.default_input_device['index']
            else:
                print("❌ デフォルト入力デバイスが見つかりません")
                return False
        
        try:
            # 短時間録音テスト
            stream = self.pyaudio_instance.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=1024
            )
            
            # 0.1秒録音
            data = stream.read(1600, exception_on_overflow=False)
            stream.stop_stream()
            stream.close()
            
            print(f"✅ 入力デバイス {device_index} テスト成功")
            return True
            
        except Exception as e:
            print(f"❌ 入力デバイス {device_index} テスト失敗: {e}")
            return False
    
    def get_optimal_recording_params(self, device_index: Optional[int] = None) -> Dict:
        """最適録音パラメータ取得"""
        if device_index is None and self.default_input_device:
            device_index = self.default_input_device['index']
        
        # 基本パラメータ
        params = {
            'format': pyaudio.paInt16,
            'channels': 1,
            'rate': 16000,
            'frames_per_buffer': 1024,
            'input_device_index': device_index
        }
        
        # デバイス固有の最適化
        if device_index is not None:
            device_info = self.pyaudio_instance.get_device_info_by_index(device_index)
            
            # サンプリングレート最適化
            if device_info['defaultSampleRate'] >= 44100:
                params['rate'] = 44100
            elif device_info['defaultSampleRate'] >= 22050:
                params['rate'] = 22050
            
            # チャンネル最適化
            if device_info['maxInputChannels'] >= 2:
                params['channels'] = 1  # モノラル録音を維持
        
        return params
    
    def save_settings(self, input_device_index: Optional[int] = None, 
                     output_device_index: Optional[int] = None):
        """デバイス設定保存"""
        settings = {
            'input_device_index': input_device_index,
            'output_device_index': output_device_index,
            'last_updated': str(pd.Timestamp.now()) if 'pd' in globals() else None
        }
        
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            print(f"💾 音声設定保存: {self.config_file}")
        except Exception as e:
            print(f"❌ 音声設定保存失敗: {e}")
    
    def _load_saved_settings(self):
        """保存された設定読み込み"""
        if not os.path.exists(self.config_file):
            return
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            
            # 保存されたデバイス設定を適用
            if 'input_device_index' in settings and settings['input_device_index'] is not None:
                # 指定されたデバイスが存在するか確認
                for device in self.input_devices:
                    if device['index'] == settings['input_device_index']:
                        self.default_input_device = device
                        break
            
            print("📂 保存された音声設定を読み込みました")
            
        except Exception as e:
            print(f"⚠️  音声設定読み込みエラー: {e}")
    
    def cleanup(self):
        """リソースクリーンアップ"""
        if self.pyaudio_instance:
            self.pyaudio_instance.terminate()
            self.pyaudio_instance = None
            print("🧹 PyAudioリソースクリーンアップ完了")


# テスト用関数
def main():
    """デバイス管理テスト"""
    print("🎵 Windows音声デバイス管理テスト")
    
    device_manager = WindowsAudioDeviceManager()
    device_manager.print_device_info()
    
    # デフォルトデバイステスト
    if device_manager.default_input_device:
        print("🎤 デフォルト入力デバイステスト中...")
        device_manager.test_input_device()
    
    # 最適パラメータ表示
    params = device_manager.get_optimal_recording_params()
    print(f"⚙️  推奨録音パラメータ: {params}")
    
    # クリーンアップ
    device_manager.cleanup()


if __name__ == "__main__":
    main()
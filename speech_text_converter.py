#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音声合成用テキスト変換システム
カスタム読み辞書を使用してテキストを音声合成用に変換
"""

import re
from typing import Dict, List, Tuple, Optional
from core.youtube_knowledge_manager import YouTubeKnowledgeManager


class SpeechTextConverter:
    """音声合成用テキスト変換クラス"""
    
    def __init__(self):
        """初期化"""
        self.knowledge_manager = None
        self._pronunciation_cache = {}
        self._cache_updated = False
        
        # 基本的な読み辞書（フォールバック用）
        self.basic_pronunciations = {
            # 英語表記の基本読み
            "XOXO": "エックスオーエックスオー",
            "TRiNITY": "トリニティ",
            "Trinity": "トリニティ",
            "TRINITY": "トリニティ",
            
            # よく使われる英語単語
            "Music": "ミュージック",
            "Video": "ビデオ",
            "Cover": "カバー",
            "Original": "オリジナル",
            "feat": "フィーチャリング",
            "feat.": "フィーチャリング",
            
            # 記号・装飾の読み
            "♪": "",
            "♫": "",
            "♬": "",
            "※": "",
            
            # VTuber・ゲーム関連
            "VTuber": "ブイチューバー",
            "Vtuber": "ブイチューバー",
            "MV": "エムブイ",
        }
        
        print("[音声変換] ✅ 音声合成用テキスト変換システム初期化完了")
    
    def set_knowledge_manager(self, knowledge_manager: YouTubeKnowledgeManager):
        """YouTube知識管理システムを設定"""
        self.knowledge_manager = knowledge_manager
        self._cache_updated = False  # キャッシュ無効化
        print("[音声変換] 🔗 YouTube知識管理システム連携完了")
    
    def _build_pronunciation_dict(self) -> Dict[str, str]:
        """発音辞書を動的に構築"""
        if self._cache_updated and self._pronunciation_cache:
            return self._pronunciation_cache
        
        pronunciations = self.basic_pronunciations.copy()
        
        # YouTube知識データベースからカスタム読みを取得
        if self.knowledge_manager:
            try:
                videos = self.knowledge_manager.knowledge_db.get("videos", {})
                
                for video_id, video_data in videos.items():
                    custom_info = video_data.get("custom_info", {})
                    
                    # 楽曲名 → 日本語読み
                    manual_title = custom_info.get("manual_title", "")
                    japanese_pronunciations = custom_info.get("japanese_pronunciations", [])
                    
                    if manual_title and japanese_pronunciations:
                        # 最初の読みを使用
                        pronunciation = japanese_pronunciations[0]
                        pronunciations[manual_title] = pronunciation
                        print(f"[音声変換] 📝 楽曲読み追加: '{manual_title}' → '{pronunciation}'")
                    
                    # アーティスト名 → 日本語読み
                    manual_artist = custom_info.get("manual_artist", "")
                    artist_pronunciations = custom_info.get("artist_pronunciations", [])
                    
                    if manual_artist and artist_pronunciations:
                        # 最初の読みを使用
                        pronunciation = artist_pronunciations[0]
                        pronunciations[manual_artist] = pronunciation
                        print(f"[音声変換] 📝 アーティスト読み追加: '{manual_artist}' → '{pronunciation}'")
                
                print(f"[音声変換] 📊 動的読み辞書構築完了: {len(pronunciations)}件")
                
            except Exception as e:
                print(f"[音声変換] ⚠️ 動的辞書構築エラー: {e}")
        
        # キャッシュを更新
        self._pronunciation_cache = pronunciations
        self._cache_updated = True
        
        return pronunciations
    
    def convert_for_speech(self, text: str) -> str:
        """
        音声合成用にテキストを変換
        
        Args:
            text: 変換対象のテキスト
            
        Returns:
            変換後のテキスト
        """
        if not text or not text.strip():
            return text
        
        original_text = text
        converted_text = text
        
        # 発音辞書を取得
        pronunciations = self._build_pronunciation_dict()
        
        # 変換実行（長い単語から優先して置換）
        sorted_keys = sorted(pronunciations.keys(), key=len, reverse=True)
        replacements_made = []
        
        for original in sorted_keys:
            pronunciation = pronunciations[original]
            
            if original in converted_text:
                # 単語境界を考慮した置換
                # 完全一致する場合のみ置換（部分一致を避ける）
                pattern = r'\b' + re.escape(original) + r'\b'
                if re.search(pattern, converted_text):
                    converted_text = re.sub(pattern, pronunciation, converted_text)
                    replacements_made.append((original, pronunciation))
                elif original in converted_text:
                    # 単語境界が適用できない場合（日本語混じりなど）
                    converted_text = converted_text.replace(original, pronunciation)
                    replacements_made.append((original, pronunciation))
        
        # デバッグ出力
        if replacements_made:
            print(f"[音声変換] 🔄 テキスト変換実行:")
            print(f"  元テキスト: {original_text}")
            print(f"  変換後: {converted_text}")
            for original, pronunciation in replacements_made:
                print(f"  '{original}' → '{pronunciation}'")
        
        return converted_text
    
    def add_custom_pronunciation(self, original: str, pronunciation: str):
        """
        カスタム読みを一時的に追加
        
        Args:
            original: 元の表記
            pronunciation: 読み方
        """
        self.basic_pronunciations[original] = pronunciation
        self._cache_updated = False  # キャッシュ無効化
        print(f"[音声変換] ➕ カスタム読み追加: '{original}' → '{pronunciation}'")
    
    def clear_cache(self):
        """キャッシュをクリア（データベース更新時に呼び出し）"""
        self._pronunciation_cache.clear()
        self._cache_updated = False
        print("[音声変換] 🗑️ 読み辞書キャッシュクリア")
    
    def get_pronunciation_dict(self) -> Dict[str, str]:
        """現在の発音辞書を取得（デバッグ用）"""
        return self._build_pronunciation_dict()
    
    def test_conversion(self, test_text: str):
        """テスト用変換機能"""
        print(f"[音声変換] 🧪 テスト変換:")
        print(f"  入力: {test_text}")
        converted = self.convert_for_speech(test_text)
        print(f"  出力: {converted}")
        return converted


# モジュール単体テスト
if __name__ == "__main__":
    print("🧪 音声合成用テキスト変換システムテスト開始")
    print("=" * 50)
    
    # テスト実行
    converter = SpeechTextConverter()
    
    # 基本テスト
    test_cases = [
        "XOXOは良い曲ですね",
        "TRiNITYの新曲が出ました",
        "MusicVideoを見ました",
        "VTuberのカバー曲です",
        "こんにちは、今日はいい天気ですね"  # 変換対象なし
    ]
    
    print("📝 基本変換テスト:")
    for test_text in test_cases:
        converter.test_conversion(test_text)
        print()
    
    # カスタム読み追加テスト
    print("📝 カスタム読み追加テスト:")
    converter.add_custom_pronunciation("アドベンチャー", "アドベンチャー")
    converter.test_conversion("アドベンチャーという曲を知っていますか？")
    
    print("✅ テスト完了")
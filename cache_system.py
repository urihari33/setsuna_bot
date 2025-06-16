#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
キャッシュ最適化システム
応答速度向上のための高速キャッシュ機能
"""

import json
import os
import hashlib
import time
from typing import Dict, Optional, List, Tuple
from datetime import datetime, timedelta

class ResponseCache:
    """応答パターンキャッシュシステム"""
    
    def __init__(self, cache_dir: str = "response_cache"):
        self.cache_dir = cache_dir
        self.cache_file = os.path.join(cache_dir, "response_cache.json")
        self.stats_file = os.path.join(cache_dir, "cache_stats.json")
        
        # キャッシュ設定
        self.max_cache_size = 1000  # 最大キャッシュ件数
        self.cache_expire_days = 7  # キャッシュ有効期限（日）
        self.similarity_threshold = 0.8  # 類似度閾値
        
        # メモリキャッシュ
        self.memory_cache: Dict[str, Dict] = {}
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "total_requests": 0,
            "cache_size": 0
        }
        
        self._initialize_cache()
        
        print(f"🗄️ 応答キャッシュシステム初期化完了")
        print(f"   - キャッシュディレクトリ: {self.cache_dir}")
        print(f"   - 最大キャッシュ数: {self.max_cache_size}")
        print(f"   - 有効期限: {self.cache_expire_days}日")
    
    def _initialize_cache(self):
        """キャッシュシステム初期化"""
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # 既存キャッシュ読み込み
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    self.memory_cache = json.load(f)
                print(f"✅ 既存キャッシュ読み込み: {len(self.memory_cache)}件")
            except Exception as e:
                print(f"⚠️ キャッシュファイル読み込みエラー: {e}")
                self.memory_cache = {}
        
        # 統計情報読み込み
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    self.cache_stats.update(json.load(f))
            except Exception as e:
                print(f"⚠️ 統計ファイル読み込みエラー: {e}")
        
        # 期限切れキャッシュの削除
        self._cleanup_expired_cache()
    
    def _generate_cache_key(self, user_input: str) -> str:
        """入力テキストからキャッシュキーを生成"""
        # 正規化（小文字化、空白削除）
        normalized = user_input.lower().strip()
        
        # ハッシュ生成
        return hashlib.md5(normalized.encode('utf-8')).hexdigest()
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """2つのテキストの類似度を計算（簡易版）"""
        # 文字レベルの類似度（Jaccard係数）
        set1 = set(text1.lower())
        set2 = set(text2.lower())
        
        if not set1 and not set2:
            return 1.0
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0
    
    def get_cached_response(self, user_input: str) -> Optional[str]:
        """キャッシュから応答を取得"""
        self.cache_stats["total_requests"] += 1
        
        cache_key = self._generate_cache_key(user_input)
        
        # 完全一致チェック
        if cache_key in self.memory_cache:
            cache_entry = self.memory_cache[cache_key]
            if self._is_cache_valid(cache_entry):
                self.cache_stats["hits"] += 1
                cache_entry["last_used"] = datetime.now().isoformat()
                cache_entry["use_count"] += 1
                print(f"✅ キャッシュヒット（完全一致）")
                return cache_entry["response"]
        
        # 類似度ベースの検索
        for key, cache_entry in self.memory_cache.items():
            if not self._is_cache_valid(cache_entry):
                continue
            
            similarity = self._calculate_similarity(user_input, cache_entry["original_input"])
            if similarity >= self.similarity_threshold:
                self.cache_stats["hits"] += 1
                cache_entry["last_used"] = datetime.now().isoformat()
                cache_entry["use_count"] += 1
                print(f"✅ キャッシュヒット（類似度: {similarity:.2f}）")
                return cache_entry["response"]
        
        # キャッシュミス
        self.cache_stats["misses"] += 1
        print(f"❌ キャッシュミス")
        return None
    
    def cache_response(self, user_input: str, response: str):
        """応答をキャッシュに保存"""
        cache_key = self._generate_cache_key(user_input)
        
        cache_entry = {
            "original_input": user_input,
            "response": response,
            "created_at": datetime.now().isoformat(),
            "last_used": datetime.now().isoformat(),
            "use_count": 1
        }
        
        self.memory_cache[cache_key] = cache_entry
        self.cache_stats["cache_size"] = len(self.memory_cache)
        
        # キャッシュサイズ制限
        if len(self.memory_cache) > self.max_cache_size:
            self._cleanup_old_cache()
        
        print(f"💾 応答をキャッシュに保存")
    
    def _is_cache_valid(self, cache_entry: Dict) -> bool:
        """キャッシュエントリの有効性チェック"""
        try:
            created_at = datetime.fromisoformat(cache_entry["created_at"])
            expiry_date = created_at + timedelta(days=self.cache_expire_days)
            return datetime.now() < expiry_date
        except:
            return False
    
    def _cleanup_expired_cache(self):
        """期限切れキャッシュの削除"""
        expired_keys = []
        
        for key, cache_entry in self.memory_cache.items():
            if not self._is_cache_valid(cache_entry):
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.memory_cache[key]
        
        if expired_keys:
            print(f"🗑️ 期限切れキャッシュ削除: {len(expired_keys)}件")
    
    def _cleanup_old_cache(self):
        """古いキャッシュの削除（LRU方式）"""
        # 使用頻度と最終使用日時でソート
        sorted_cache = sorted(
            self.memory_cache.items(),
            key=lambda x: (x[1]["use_count"], x[1]["last_used"])
        )
        
        # 古いものから削除
        remove_count = len(self.memory_cache) - self.max_cache_size + 100
        for i in range(remove_count):
            if i < len(sorted_cache):
                key = sorted_cache[i][0]
                del self.memory_cache[key]
        
        print(f"🗑️ 古いキャッシュ削除: {remove_count}件")
    
    def save_cache(self):
        """キャッシュをファイルに保存"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.memory_cache, f, ensure_ascii=False, indent=2)
            
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache_stats, f, ensure_ascii=False, indent=2)
            
            print(f"💾 キャッシュファイル保存完了")
        except Exception as e:
            print(f"❌ キャッシュ保存エラー: {e}")
    
    def get_cache_stats(self) -> Dict:
        """キャッシュ統計情報取得"""
        hit_rate = 0.0
        if self.cache_stats["total_requests"] > 0:
            hit_rate = self.cache_stats["hits"] / self.cache_stats["total_requests"]
        
        return {
            **self.cache_stats,
            "hit_rate": hit_rate,
            "cache_size_current": len(self.memory_cache)
        }
    
    def clear_cache(self):
        """キャッシュクリア"""
        self.memory_cache.clear()
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "total_requests": 0,
            "cache_size": 0
        }
        print("🗑️ キャッシュクリア完了")

# テスト用
if __name__ == "__main__":
    print("="*50)
    print("🧪 応答キャッシュシステムテスト")
    print("="*50)
    
    cache = ResponseCache()
    
    # テストデータ
    test_cases = [
        ("こんにちは", "こんにちは！元気ですか？"),
        ("今日の天気は？", "今日はいい天気ですね。"),
        ("こんにちわ", "こんにちは！元気ですか？"),  # 類似検索テスト
    ]
    
    for user_input, expected_response in test_cases:
        print(f"\n👤 入力: {user_input}")
        
        # キャッシュ確認
        cached = cache.get_cached_response(user_input)
        if cached:
            print(f"📦 キャッシュ応答: {cached}")
        else:
            print(f"🤖 新規応答: {expected_response}")
            cache.cache_response(user_input, expected_response)
    
    # 統計表示
    stats = cache.get_cache_stats()
    print(f"\n📊 キャッシュ統計:")
    print(f"   - ヒット率: {stats['hit_rate']:.1%}")
    print(f"   - 総リクエスト: {stats['total_requests']}")
    print(f"   - キャッシュサイズ: {stats['cache_size_current']}")
    
    cache.save_cache()
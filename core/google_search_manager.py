#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GoogleSearchManager - Google Custom Search API専用検索管理
Mockフォールバックなし、Google APIのみで動作する検索システム
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from .google_search_service import GoogleSearchService, GoogleSearchResult
from .config_manager import get_config_manager

@dataclass
class SearchStatus:
    """検索状態管理データクラス"""
    success: bool
    engine_used: str
    total_results: int
    execution_time: float
    error_message: Optional[str] = None
    quota_exceeded: bool = False

class GoogleSearchManager:
    """Google Custom Search API専用検索管理クラス"""
    
    def __init__(self):
        """初期化"""
        self.config_manager = get_config_manager()
        self.google_service = None
        self.daily_search_count = 0
        self.max_daily_searches = 100  # Google無料枠制限
        
        # Google Search Service初期化
        self._initialize_google_service()
        
        # 状態管理
        self.status = {
            "service_ready": self.google_service is not None,
            "config_valid": self._validate_google_config(),
            "searches_today": self.daily_search_count,
            "quota_available": self.max_daily_searches - self.daily_search_count
        }
        
        # 初期化結果表示
        self._print_initialization_status()
    
    def _initialize_google_service(self):
        """Google検索サービス初期化"""
        try:
            self.google_service = GoogleSearchService()
            if not self.google_service._validate_config():
                self.google_service = None
                print("[GoogleSearchManager] ❌ Google検索サービス設定が無効です")
        except Exception as e:
            self.google_service = None
            print(f"[GoogleSearchManager] ❌ Google検索サービス初期化失敗: {e}")
    
    def _validate_google_config(self) -> bool:
        """Google設定検証"""
        if not self.config_manager.is_google_search_configured():
            return False
        
        if not self.config_manager.get_google_search_engine_id():
            return False
        
        return True
    
    def _print_initialization_status(self):
        """初期化状態表示"""
        print("[GoogleSearchManager] 🔍 Google専用検索マネージャー初期化")
        
        if self.status["service_ready"] and self.status["config_valid"]:
            print("[GoogleSearchManager] ✅ Google Custom Search API準備完了")
            print(f"[GoogleSearchManager] 📊 利用可能検索数: {self.status['quota_available']}/日")
        else:
            print("[GoogleSearchManager] ❌ Google検索サービス使用不可")
            if not self.status["config_valid"]:
                print("  - Google API設定を確認してください")
                print("  - GOOGLE_API_KEY, GOOGLE_SEARCH_ENGINE_IDが必要です")
    
    def search(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """
        Google検索実行（フォールバックなし）
        
        Args:
            query: 検索クエリ
            max_results: 最大結果数
            
        Returns:
            検索結果（Google専用）
        """
        start_time = time.time()
        
        # 前提条件チェック
        if not self.is_ready():
            error_msg = self._get_not_ready_reason()
            return self._create_error_response(query, error_msg, time.time() - start_time)
        
        # クォータチェック
        if self.daily_search_count >= self.max_daily_searches:
            error_msg = f"Google検索の日次制限に到達しました ({self.max_daily_searches}検索/日)"
            return self._create_error_response(
                query, error_msg, time.time() - start_time, quota_exceeded=True
            )
        
        try:
            # Google検索実行
            print(f"[GoogleSearchManager] 🔍 Google検索実行: {query}")
            result = self.google_service.search(query, max_results)
            
            # 検索カウント更新
            self.daily_search_count += 1
            self.status["searches_today"] = self.daily_search_count
            self.status["quota_available"] = self.max_daily_searches - self.daily_search_count
            
            execution_time = time.time() - start_time
            
            if result.success and result.results:
                print(f"[GoogleSearchManager] ✅ Google検索成功: {len(result.results)}件")
                
                return {
                    "engine_used": "google",
                    "query": query,
                    "results": result.results,
                    "total_results": result.total_results,
                    "execution_time": execution_time,
                    "success": True,
                    "fallback_used": False,
                    "searches_used_today": self.daily_search_count,
                    "quota_remaining": self.status["quota_available"]
                }
            
            else:
                # Google検索が失敗した場合
                error_msg = result.error_message or "Google検索で結果が取得できませんでした"
                print(f"[GoogleSearchManager] ❌ Google検索失敗: {error_msg}")
                
                # クォータ超過の特別処理
                if "quota" in error_msg.lower() or "403" in error_msg:
                    return self._create_error_response(
                        query, "Google検索APIの制限に到達しました", execution_time, quota_exceeded=True
                    )
                
                return self._create_error_response(query, error_msg, execution_time)
        
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Google検索で予期しないエラーが発生しました: {str(e)}"
            print(f"[GoogleSearchManager] ❌ {error_msg}")
            
            return self._create_error_response(query, error_msg, execution_time)
    
    def _create_error_response(self, query: str, error_message: str, execution_time: float, quota_exceeded: bool = False) -> Dict[str, Any]:
        """エラーレスポンス作成"""
        return {
            "engine_used": "google",
            "query": query,
            "results": [],
            "total_results": 0,
            "execution_time": execution_time,
            "success": False,
            "fallback_used": False,
            "error": error_message,
            "quota_exceeded": quota_exceeded,
            "searches_used_today": self.daily_search_count,
            "quota_remaining": max(0, self.max_daily_searches - self.daily_search_count)
        }
    
    def is_ready(self) -> bool:
        """検索準備完了確認"""
        return (
            self.google_service is not None and
            self.status["config_valid"] and
            self.daily_search_count < self.max_daily_searches
        )
    
    def _get_not_ready_reason(self) -> str:
        """準備未完了の理由取得"""
        if self.google_service is None:
            return "Google検索サービスが初期化されていません"
        
        if not self.status["config_valid"]:
            return "Google API設定が無効です（GOOGLE_API_KEY, GOOGLE_SEARCH_ENGINE_IDを確認）"
        
        if self.daily_search_count >= self.max_daily_searches:
            return f"Google検索の日次制限に到達しました ({self.max_daily_searches}検索/日)"
        
        return "不明な理由で検索サービスが利用できません"
    
    def get_status(self) -> Dict[str, Any]:
        """検索マネージャー状態取得"""
        return {
            "ready": self.is_ready(),
            "google_service_available": self.google_service is not None,
            "config_valid": self.status["config_valid"],
            "searches_used_today": self.daily_search_count,
            "quota_remaining": self.status["quota_available"],
            "max_daily_searches": self.max_daily_searches,
            "not_ready_reason": None if self.is_ready() else self._get_not_ready_reason()
        }
    
    def get_quota_info(self) -> Dict[str, Any]:
        """クォータ情報取得"""
        return {
            "searches_used": self.daily_search_count,
            "quota_remaining": self.status["quota_available"],
            "max_daily_searches": self.max_daily_searches,
            "usage_percentage": (self.daily_search_count / self.max_daily_searches) * 100,
            "quota_exceeded": self.daily_search_count >= self.max_daily_searches
        }
    
    def reset_daily_count(self):
        """日次カウントリセット（テスト用）"""
        self.daily_search_count = 0
        self.status["searches_today"] = 0
        self.status["quota_available"] = self.max_daily_searches
        print("[GoogleSearchManager] 🔄 日次検索カウントをリセットしました")

# テスト用コード（実行しない）
if __name__ == "__main__":
    print("=== GoogleSearchManager テスト ===")
    print("注意: 実際のテストはユーザーが実施します")
    
    # 状態確認のみ
    manager = GoogleSearchManager()
    status = manager.get_status()
    
    print(f"\n📊 検索マネージャー状態:")
    print(f"  準備完了: {status['ready']}")
    print(f"  Google API利用可能: {status['google_service_available']}")
    print(f"  設定有効: {status['config_valid']}")
    print(f"  利用可能検索数: {status['quota_remaining']}")
    
    if not status['ready']:
        print(f"  理由: {status['not_ready_reason']}")
    
    print("\n✅ GoogleSearchManager準備完了")
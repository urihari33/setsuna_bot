#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GoogleSearchService - Google Custom Search API統合サービス
実際のWeb検索データを取得するための主力検索エンジン
"""

import json
import hashlib
import time
import random
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote
from .config_manager import get_config_manager
from .search_result_models import SearchItem, UnifiedSearchResult

@dataclass
class GoogleSearchResult:
    """Google検索結果データクラス"""
    query: str
    results: List[Dict[str, Any]]
    total_results: int
    execution_time: float
    success: bool = True
    error_message: Optional[str] = None

class GoogleSearchService:
    """Google Custom Search APIサービスメインクラス"""
    
    def __init__(self):
        """初期化"""
        self.config_manager = get_config_manager()
        
        # API設定
        self.api_key = self.config_manager.get_google_api_key()
        self.search_engine_id = self.config_manager.get_google_search_engine_id()
        
        # Google Custom Search API エンドポイント
        self.api_endpoint = "https://www.googleapis.com/customsearch/v1"
        
        # API制限・設定
        self.rate_limit_delay = 1.0  # 秒
        self.max_retries = 3
        self.timeout = 30
        
        # サービス情報
        self.service_info = {
            "service_name": "GoogleSearchService",
            "version": "1.0.0",
            "api_provider": "Google Custom Search",
            "rate_limit": "100 queries/day (free tier)",
            "status": "active" if self._validate_config() else "configuration_error"
        }
    
    def _validate_config(self) -> bool:
        """設定検証"""
        if not self.api_key:
            print("[GoogleSearchService] ❌ Google API Keyが設定されていません")
            return False
        
        if not self.search_engine_id:
            print("[GoogleSearchService] ❌ Google Search Engine IDが設定されていません")
            return False
        
        return True
    
    def search(self, query: str, max_results: int = 10) -> UnifiedSearchResult:
        """
        Google Custom Search実行
        
        Args:
            query: 検索クエリ
            max_results: 最大結果数 (最大10件/リクエスト)
            
        Returns:
            統一検索結果
        """
        start_time = time.time()
        
        # 設定検証
        if not self._validate_config():
            return UnifiedSearchResult(
                query=query,
                results=[],
                total_results=0,
                engine_used="google",
                execution_time=time.time() - start_time,
                success=False,
                error_message="Google Search API configuration error"
            )
        
        try:
            # API パラメータ構築
            params = {
                'key': self.api_key,
                'cx': self.search_engine_id,
                'q': query,
                'num': min(max_results, 10),  # Google APIの制限
                'lr': 'lang_ja',  # 日本語優先
                'safe': 'medium'
            }
            
            # API リクエスト実行
            response = requests.get(
                self.api_endpoint,
                params=params,
                timeout=self.timeout
            )
            
            execution_time = time.time() - start_time
            
            # レスポンス処理
            if response.status_code == 200:
                response_data = response.json()
                results = self._parse_google_response(response_data, query)
                
                return UnifiedSearchResult(
                    query=query,
                    results=results,
                    total_results=len(results),
                    engine_used="google",
                    execution_time=execution_time,
                    success=True
                )
            
            elif response.status_code == 403:
                # API制限に到達
                error_msg = "Google Search API quota exceeded"
                print(f"[GoogleSearchService] ⚠️ {error_msg}")
                
                return UnifiedSearchResult(
                    query=query,
                    results=[],
                    total_results=0,
                    engine_used="google",
                    execution_time=execution_time,
                    success=False,
                    error_message=error_msg
                )
            
            else:
                # その他のHTTPエラー
                error_msg = f"HTTP {response.status_code}: {response.text}"
                print(f"[GoogleSearchService] ❌ API Error: {error_msg}")
                
                return UnifiedSearchResult(
                    query=query,
                    results=[],
                    total_results=0,
                    engine_used="google",
                    execution_time=execution_time,
                    success=False,
                    error_message=error_msg
                )
        
        except requests.exceptions.Timeout:
            execution_time = time.time() - start_time
            error_msg = "Google Search API request timeout"
            print(f"[GoogleSearchService] ⏰ {error_msg}")
            
            return UnifiedSearchResult(
                query=query,
                results=[],
                total_results=0,
                engine_used="google",
                execution_time=execution_time,
                success=False,
                error_message=error_msg
            )
        
        except requests.exceptions.RequestException as e:
            execution_time = time.time() - start_time
            error_msg = f"Google Search API request error: {str(e)}"
            print(f"[GoogleSearchService] ❌ {error_msg}")
            
            return UnifiedSearchResult(
                query=query,
                results=[],
                total_results=0,
                engine_used="google",
                execution_time=execution_time,
                success=False,
                error_message=error_msg
            )
        
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Unexpected error: {str(e)}"
            print(f"[GoogleSearchService] ❌ {error_msg}")
            
            return UnifiedSearchResult(
                query=query,
                results=[],
                total_results=0,
                engine_used="google",
                execution_time=execution_time,
                success=False,
                error_message=error_msg
            )
    
    def _parse_google_response(self, response_data: Dict, query: str) -> List[SearchItem]:
        """Google APIレスポンス解析"""
        results = []
        
        # 検索結果アイテム取得
        items = response_data.get('items', [])
        
        for i, item in enumerate(items):
            # URLとドメイン取得
            url = item.get('link', '')
            domain = url.split('/')[2] if '/' in url else 'unknown'
            
            # SearchItemオブジェクト作成
            search_item = SearchItem(
                title=item.get('title', ''),
                url=url,
                snippet=item.get('snippet', ''),
                source_domain=domain,
                source_type="web",
                publish_date=None,  # Google APIでは提供されない
                relevance_score=max(0.7, 1.0 - (i * 0.1)),  # 順位による関連性
                quality_score=0.9  # Google検索は高信頼性
            )
            
            results.append(search_item)
        
        return results
    
    def get_service_info(self) -> Dict[str, Any]:
        """サービス情報取得"""
        return self.service_info
    
    def get_quota_status(self) -> Dict[str, Any]:
        """API使用状況確認（簡易版）"""
        # 注: 実際のクォータ情報取得にはGoogle Cloud Console APIが必要
        return {
            "quota_type": "daily",
            "free_tier_limit": 100,
            "estimated_usage": "不明（Google Cloud Consoleで確認）",
            "status": "active" if self._validate_config() else "configuration_error"
        }

# テスト用コード（実行しない）
if __name__ == "__main__":
    print("=== GoogleSearchService テスト ===")
    print("注意: 実際のテストはユーザーが実施します")
    print("このスクリプトは直接実行しないでください")
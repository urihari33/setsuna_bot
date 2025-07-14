#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuckDuckGoSearchService - DuckDuckGo検索API統合サービス
無制限無料検索を提供するDuckDuckGoの検索エンジン実装
"""

import requests
import time
import re
from datetime import datetime
from typing import Dict, List, Any, Optional
from urllib.parse import quote, urljoin, urlparse
from bs4 import BeautifulSoup
from .search_result_models import SearchItem, UnifiedSearchResult

class DuckDuckGoSearchService:
    """DuckDuckGo検索サービスメインクラス"""
    
    def __init__(self):
        """初期化"""
        # DuckDuckGo HTML検索エンドポイント
        self.search_url = "https://html.duckduckgo.com/html/"
        
        # リクエスト設定
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # レート制限設定
        self.rate_limit_delay = 1.0  # 1秒間隔
        self.last_request_time = 0
        
        # サービス情報
        self.service_info = {
            "service_name": "DuckDuckGoSearchService",
            "version": "1.0.0",
            "api_provider": "DuckDuckGo HTML Search",
            "rate_limit": "1 request/second",
            "cost": "Free unlimited",
            "status": "active"
        }
        
        # 検索履歴（デバッグ用）
        self.search_history = []
        
    def search(self, query: str, max_results: int = 10) -> UnifiedSearchResult:
        """
        DuckDuckGo検索実行
        
        Args:
            query: 検索クエリ
            max_results: 最大結果数
            
        Returns:
            統一検索結果
        """
        start_time = time.time()
        
        try:
            # レート制限対応
            self._apply_rate_limit()
            
            # 検索実行
            html_content = self._fetch_search_results(query)
            
            # 結果解析
            search_items = self._parse_search_results(html_content, max_results)
            
            execution_time = time.time() - start_time
            
            # 検索履歴に追加
            self.search_history.append({
                "query": query,
                "timestamp": datetime.now(),
                "results_count": len(search_items),
                "execution_time": execution_time
            })
            
            return UnifiedSearchResult(
                query=query,
                results=search_items,
                total_results=len(search_items),
                engine_used="duckduckgo",
                execution_time=execution_time,
                success=True,
                quota_remaining=None,  # DuckDuckGoは無制限
                timestamp=datetime.now()
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            return UnifiedSearchResult(
                query=query,
                results=[],
                total_results=0,
                engine_used="duckduckgo",
                execution_time=execution_time,
                success=False,
                error_message=str(e),
                timestamp=datetime.now()
            )
    
    def _apply_rate_limit(self):
        """レート制限を適用"""
        current_time = time.time()
        elapsed_time = current_time - self.last_request_time
        
        if elapsed_time < self.rate_limit_delay:
            sleep_time = self.rate_limit_delay - elapsed_time
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _fetch_search_results(self, query: str) -> str:
        """検索結果HTMLを取得"""
        params = {
            'q': query,
            'kl': 'jp-jp',  # 日本語地域設定
            'kz': '-1',     # セーフサーチ無効
            'kc': '-1',     # 自動修正無効
            'o': 'html',    # HTML形式
            'ia': 'web'     # Web検索
        }
        
        response = self.session.get(self.search_url, params=params, timeout=30)
        response.raise_for_status()
        
        return response.text
    
    def _parse_search_results(self, html_content: str, max_results: int) -> List[SearchItem]:
        """検索結果HTMLを解析"""
        soup = BeautifulSoup(html_content, 'html.parser')
        results = []
        
        # 検索結果要素を抽出（複数のパターンに対応）
        result_elements = (
            soup.find_all('div', class_='result') or
            soup.find_all('div', class_='results_links') or
            soup.find_all('div', class_='web-result') or
            soup.find_all('a', class_='result__a')
        )
        
        # より広範な検索結果パターンに対応
        if not result_elements:
            # 基本的なリンクを検索
            result_elements = soup.find_all('a', href=True)
        
        for element in result_elements[:max_results]:
            try:
                # タイトルとURLを取得（複数のパターンに対応）
                if element.name == 'a':
                    title_element = element
                    url = element.get('href', '')
                    title = element.get_text(strip=True)
                else:
                    title_element = element.find('a', class_='result__a') or element.find('a', href=True)
                    if not title_element:
                        continue
                    title = title_element.get_text(strip=True)
                    url = title_element.get('href', '')
                
                # URLが相対パスの場合、絶対URLに変換
                if url.startswith('/'):
                    url = urljoin('https://duckduckgo.com', url)
                
                # 空のURLやDuckDuckGo内部リンクをスキップ
                if not url or 'duckduckgo.com' in url:
                    continue
                
                # スニペットを取得
                snippet_element = element.find('a', class_='result__snippet') or element.find('span', class_='result__snippet')
                snippet = snippet_element.get_text(strip=True) if snippet_element else ""
                
                # タイトルが空の場合はスキップ
                if not title:
                    continue
                
                # ドメインを抽出
                domain = self._extract_domain(url)
                
                # 品質スコアを計算（簡易版）
                quality_score = self._calculate_quality_score(title, snippet, domain)
                
                # SearchItemを作成
                search_item = SearchItem(
                    title=title,
                    url=url,
                    snippet=snippet,
                    source_domain=domain,
                    source_type="web",
                    publish_date=None,  # DuckDuckGoは日付情報を提供しない
                    relevance_score=1.0 - (len(results) * 0.1),  # 順位ベース
                    quality_score=quality_score
                )
                
                results.append(search_item)
                
            except Exception as e:
                # 個別要素の解析エラーは無視して続行
                continue
        
        return results
    
    def _extract_domain(self, url: str) -> str:
        """URLからドメインを抽出"""
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            
            # www.を除去
            if domain.startswith('www.'):
                domain = domain[4:]
            
            return domain
        except Exception:
            return "unknown"
    
    def _calculate_quality_score(self, title: str, snippet: str, domain: str) -> float:
        """品質スコアを計算"""
        score = 0.5  # ベーススコア
        
        # タイトルの品質
        if title:
            if len(title) > 10:
                score += 0.1
            if len(title) < 100:
                score += 0.1
        
        # スニペットの品質
        if snippet:
            if len(snippet) > 50:
                score += 0.1
            if len(snippet) < 300:
                score += 0.1
        
        # ドメインの信頼性（簡易版）
        trusted_domains = [
            'wikipedia.org', 'github.com', 'stackoverflow.com',
            'microsoft.com', 'google.com', 'amazon.com',
            'qiita.com', 'zenn.dev', 'tech.nikkeibp.co.jp'
        ]
        
        if any(trusted in domain for trusted in trusted_domains):
            score += 0.2
        
        return min(score, 1.0)
    
    def get_service_info(self) -> Dict[str, Any]:
        """サービス情報を取得"""
        return self.service_info.copy()
    
    def get_search_history(self) -> List[Dict[str, Any]]:
        """検索履歴を取得"""
        return self.search_history.copy()
    
    def clear_search_history(self):
        """検索履歴をクリア"""
        self.search_history.clear()
    
    def is_available(self) -> bool:
        """サービスが利用可能かチェック"""
        try:
            # 簡単なテスト検索
            response = self.session.get(self.search_url, timeout=10)
            return response.status_code == 200
        except Exception:
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """サービスステータスを取得"""
        return {
            "service_name": "DuckDuckGo",
            "available": self.is_available(),
            "unlimited_quota": True,
            "rate_limit": f"{self.rate_limit_delay} sec/request",
            "total_searches": len(self.search_history),
            "last_search": self.search_history[-1]["timestamp"].isoformat() if self.search_history else None
        }

# テスト用コード
if __name__ == "__main__":
    print("=== DuckDuckGo検索サービステスト ===")
    
    service = DuckDuckGoSearchService()
    
    # サービス情報表示
    print(f"サービス情報: {service.get_service_info()}")
    
    # 利用可能性チェック
    print(f"サービス利用可能: {service.is_available()}")
    
    # テスト検索
    test_query = "Python プログラミング"
    print(f"\nテスト検索: {test_query}")
    
    result = service.search(test_query, max_results=5)
    
    print(f"検索成功: {result.success}")
    print(f"結果件数: {result.total_results}")
    print(f"実行時間: {result.execution_time:.2f}秒")
    
    if result.success:
        print("\n検索結果:")
        for i, item in enumerate(result.results, 1):
            print(f"{i}. {item.title}")
            print(f"   URL: {item.url}")
            print(f"   スニペット: {item.snippet[:100]}...")
            print(f"   品質スコア: {item.quality_score:.2f}")
            print()
    
    print("✅ DuckDuckGo検索サービステスト完了")
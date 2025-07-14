#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MultiSearchManager - マルチ検索エンジン統合マネージャー
Google Custom Search API + DuckDuckGo + 動的クエリ生成の統合管理
"""

import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

from .google_search_service import GoogleSearchService
from .duckduckgo_search_service import DuckDuckGoSearchService
from .dynamic_query_generator import DynamicQueryGenerator, QueryGenerationRequest
from .search_result_models import (
    SearchItem, UnifiedSearchResult, SearchEngineStatus, 
    MultiSearchResult
)
from .dynamic_query_generator import GeneratedQuery
from .config_manager import get_config_manager
from .debug_logger import get_debug_logger

@dataclass
class SearchStrategy:
    """検索戦略設定"""
    primary_engine: str = "google"
    fallback_engines: List[str] = None
    max_concurrent_searches: int = 2
    enable_dynamic_queries: bool = True
    merge_results: bool = True
    remove_duplicates: bool = True
    quality_threshold: float = 0.3
    
    def __post_init__(self):
        if self.fallback_engines is None:
            self.fallback_engines = ["duckduckgo"]

class MultiSearchManager:
    """マルチ検索エンジン統合マネージャー"""
    
    def __init__(self):
        """初期化"""
        self.config_manager = get_config_manager()
        self.debug_logger = get_debug_logger(component="MULTI_SEARCH")
        
        # 検索サービス初期化
        self.google_service = GoogleSearchService()
        self.duckduckgo_service = DuckDuckGoSearchService()
        self.query_generator = DynamicQueryGenerator()
        
        # 検索戦略設定
        self.default_strategy = SearchStrategy()
        
        # 統計情報
        self.search_stats = {
            "total_searches": 0,
            "google_searches": 0,
            "duckduckgo_searches": 0,
            "successful_searches": 0,
            "failed_searches": 0,
            "total_results": 0,
            "unique_results": 0,
            "last_search_time": None
        }
        
        # スレッドセーフティ
        self.search_lock = threading.Lock()
        
        # 利用可能エンジン確認
        self.available_engines = self._check_available_engines()
        
        self.debug_logger.info("MultiSearchManager初期化完了", {
            "available_engines": list(self.available_engines.keys()),
            "google_available": self.available_engines.get("google", False),
            "duckduckgo_available": self.available_engines.get("duckduckgo", False),
            "dynamic_queries_available": self.query_generator.is_available()
        })
    
    def _check_available_engines(self) -> Dict[str, bool]:
        """利用可能な検索エンジンを確認"""
        engines = {}
        
        # Google Search API
        try:
            # GoogleSearchServiceにはget_statusメソッドがないため、基本的な利用可能性をチェック
            engines["google"] = self.google_service._validate_config()
        except Exception as e:
            engines["google"] = False
            self.debug_logger.warning(f"Google Search API利用不可: {e}")
        
        # DuckDuckGo
        try:
            engines["duckduckgo"] = self.duckduckgo_service.is_available()
        except Exception as e:
            engines["duckduckgo"] = False
            self.debug_logger.warning(f"DuckDuckGo検索利用不可: {e}")
        
        return engines
    
    def search(self, query: str, max_results: int = 10, 
               strategy: Optional[SearchStrategy] = None) -> MultiSearchResult:
        """
        統合検索実行
        
        Args:
            query: 検索クエリ
            max_results: 最大結果数
            strategy: 検索戦略（省略時はデフォルト）
            
        Returns:
            マルチ検索結果
        """
        if strategy is None:
            strategy = self.default_strategy
        
        start_time = time.time()
        
        self.debug_logger.info("マルチ検索開始", {
            "query": query,
            "max_results": max_results,
            "primary_engine": strategy.primary_engine,
            "fallback_engines": strategy.fallback_engines
        })
        
        with self.search_lock:
            self.search_stats["total_searches"] += 1
            self.search_stats["last_search_time"] = datetime.now()
        
        try:
            # 検索エンジンの優先順位決定
            search_order = self._determine_search_order(strategy)
            
            # 並列検索実行
            engine_results = self._execute_parallel_search(
                query, max_results, search_order, strategy
            )
            
            # 結果統合
            if strategy.merge_results:
                combined_results = self._merge_search_results(engine_results)
                
                if strategy.remove_duplicates:
                    combined_results = self._remove_duplicates(combined_results)
                
                # 品質フィルタリング
                combined_results = self._filter_by_quality(
                    combined_results, strategy.quality_threshold
                )
            else:
                # 最良エンジンの結果のみ使用
                best_engine = self._get_best_engine_result(engine_results)
                combined_results = engine_results[best_engine].results if best_engine else []
            
            execution_time = time.time() - start_time
            
            # 統計更新
            with self.search_lock:
                self.search_stats["successful_searches"] += 1
                self.search_stats["total_results"] += len(combined_results)
                self.search_stats["unique_results"] += len(combined_results)
                
                # エンジン別統計
                for engine in engine_results:
                    if engine == "google":
                        self.search_stats["google_searches"] += 1
                    elif engine == "duckduckgo":
                        self.search_stats["duckduckgo_searches"] += 1
            
            result = MultiSearchResult(
                query=query,
                combined_results=combined_results,
                engine_results=engine_results,
                total_unique_results=len(combined_results),
                engines_used=list(engine_results.keys()),
                execution_time=execution_time,
                success=True,
                primary_engine=strategy.primary_engine
            )
            
            self.debug_logger.info("マルチ検索完了", {
                "engines_used": result.engines_used,
                "total_results": result.total_unique_results,
                "execution_time": result.execution_time
            })
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            with self.search_lock:
                self.search_stats["failed_searches"] += 1
            
            self.debug_logger.error(f"マルチ検索エラー: {e}")
            
            return MultiSearchResult(
                query=query,
                combined_results=[],
                engine_results={},
                total_unique_results=0,
                engines_used=[],
                execution_time=execution_time,
                success=False
            )
    
    def search_with_dynamic_queries(self, theme: str, learning_type: str, 
                                  depth_level: int, max_results: int = 50,
                                  strategy: Optional[SearchStrategy] = None) -> MultiSearchResult:
        """
        動的クエリ生成を使用した検索
        
        Args:
            theme: 学習テーマ
            learning_type: 学習タイプ
            depth_level: 深度レベル
            max_results: 最大結果数
            strategy: 検索戦略
            
        Returns:
            マルチ検索結果
        """
        if strategy is None:
            strategy = self.default_strategy
        
        self.debug_logger.info("動的クエリ検索開始", {
            "theme": theme,
            "learning_type": learning_type,
            "depth_level": depth_level
        })
        
        # 動的クエリ生成
        query_request = QueryGenerationRequest(
            theme=theme,
            learning_type=learning_type,
            depth_level=depth_level,
            target_engines=["google", "duckduckgo"]
        )
        
        generated_queries = self.query_generator.generate_queries(query_request)
        
        # 優先度順にソート
        generated_queries.sort(key=lambda x: x.priority, reverse=True)
        
        # 各クエリで検索実行
        all_results = []
        all_engine_results = {}
        
        for query_info in generated_queries:
            search_result = self.search(
                query_info.query,
                max_results=max_results // len(generated_queries),
                strategy=strategy
            )
            
            if search_result.success:
                all_results.extend(search_result.combined_results)
                
                # エンジン結果を統合
                for engine, result in search_result.engine_results.items():
                    if engine not in all_engine_results:
                        all_engine_results[engine] = []
                    all_engine_results[engine].append(result)
        
        # 重複除去
        if strategy.remove_duplicates:
            all_results = self._remove_duplicates(all_results)
        
        # 結果数制限
        all_results = all_results[:max_results]
        
        return MultiSearchResult(
            query=f"動的クエリ検索: {theme}",
            combined_results=all_results,
            engine_results=all_engine_results,
            total_unique_results=len(all_results),
            engines_used=list(all_engine_results.keys()),
            execution_time=0,  # 複数検索の合計時間は計算複雑
            success=True
        )
    
    def _determine_search_order(self, strategy: SearchStrategy) -> List[str]:
        """検索エンジンの優先順位を決定"""
        search_order = []
        
        # プライマリエンジン
        if (strategy.primary_engine in self.available_engines and 
            self.available_engines[strategy.primary_engine]):
            search_order.append(strategy.primary_engine)
        
        # フォールバックエンジン
        for engine in strategy.fallback_engines:
            if (engine in self.available_engines and 
                self.available_engines[engine] and 
                engine not in search_order):
                search_order.append(engine)
        
        return search_order
    
    def _execute_parallel_search(self, query: str, max_results: int, 
                               search_order: List[str], strategy: SearchStrategy) -> Dict[str, UnifiedSearchResult]:
        """並列検索実行"""
        results = {}
        
        # 検索対象がない場合は空の結果を返す
        if not search_order:
            return results
        
        # 最大同時実行数を制限
        max_workers = min(len(search_order), strategy.max_concurrent_searches)
        
        # max_workersが0の場合は1に設定
        if max_workers <= 0:
            max_workers = 1
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 検索タスク送信
            future_to_engine = {}
            
            for engine in search_order:
                if engine == "google":
                    future = executor.submit(self.google_service.search, query, max_results)
                elif engine == "duckduckgo":
                    future = executor.submit(self.duckduckgo_service.search, query, max_results)
                else:
                    continue
                
                future_to_engine[future] = engine
            
            # 結果取得
            for future in as_completed(future_to_engine):
                engine = future_to_engine[future]
                try:
                    result = future.result()
                    results[engine] = result
                    
                    self.debug_logger.debug(f"{engine}検索完了", {
                        "success": result.success,
                        "results_count": len(result.results) if result.success else 0
                    })
                    
                except Exception as e:
                    self.debug_logger.error(f"{engine}検索エラー: {e}")
        
        return results
    
    def _merge_search_results(self, engine_results: Dict[str, UnifiedSearchResult]) -> List[SearchItem]:
        """検索結果を統合"""
        merged_results = []
        
        # 各エンジンの結果を統合
        for engine, result in engine_results.items():
            if result.success:
                merged_results.extend(result.results)
        
        # 品質スコア順にソート
        merged_results.sort(key=lambda x: (x.quality_score, x.relevance_score), reverse=True)
        
        return merged_results
    
    def _remove_duplicates(self, results: List[SearchItem]) -> List[SearchItem]:
        """重複結果を除去"""
        seen_urls = set()
        unique_results = []
        
        for result in results:
            url_key = result.url.lower().rstrip('/')
            if url_key not in seen_urls:
                seen_urls.add(url_key)
                unique_results.append(result)
        
        return unique_results
    
    def _filter_by_quality(self, results: List[SearchItem], threshold: float) -> List[SearchItem]:
        """品質スコアでフィルタリング"""
        return [result for result in results if result.quality_score >= threshold]
    
    def _get_best_engine_result(self, engine_results: Dict[str, UnifiedSearchResult]) -> Optional[str]:
        """最良の検索エンジン結果を取得"""
        best_engine = None
        best_score = -1
        
        for engine, result in engine_results.items():
            if result.success:
                avg_quality = result.calculate_average_quality()
                if avg_quality > best_score:
                    best_score = avg_quality
                    best_engine = engine
        
        return best_engine
    
    def get_engine_status(self) -> Dict[str, SearchEngineStatus]:
        """各検索エンジンの状態を取得"""
        statuses = {}
        
        # Google Search API
        try:
            google_status = self.google_service.get_status()
            statuses["google"] = SearchEngineStatus(
                engine_name="Google Custom Search",
                available=google_status.get("available", False),
                quota_remaining=google_status.get("quota_remaining"),
                daily_limit=google_status.get("daily_limit"),
                error_message=google_status.get("error_message")
            )
        except Exception as e:
            statuses["google"] = SearchEngineStatus(
                engine_name="Google Custom Search",
                available=False,
                error_message=str(e)
            )
        
        # DuckDuckGo
        try:
            duckduckgo_status = self.duckduckgo_service.get_status()
            statuses["duckduckgo"] = SearchEngineStatus(
                engine_name="DuckDuckGo",
                available=duckduckgo_status.get("available", False),
                quota_remaining=None,  # 無制限
                daily_limit=None,
                error_message=duckduckgo_status.get("error_message")
            )
        except Exception as e:
            statuses["duckduckgo"] = SearchEngineStatus(
                engine_name="DuckDuckGo",
                available=False,
                error_message=str(e)
            )
        
        return statuses
    
    def get_search_stats(self) -> Dict[str, Any]:
        """検索統計を取得"""
        return self.search_stats.copy()
    
    def get_status(self) -> Dict[str, Any]:
        """統合検索システムの状態を取得"""
        engine_statuses = self.get_engine_status()
        search_stats = self.get_search_stats()
        
        # エンジン可用性サマリー
        available_engines = [name for name, status in engine_statuses.items() if status.available]
        
        return {
            "engines": engine_statuses,
            "available_engines": available_engines,
            "total_available_engines": len(available_engines),
            "stats": search_stats,
            "dynamic_queries_enabled": self.query_generator is not None,
            "last_updated": datetime.now().isoformat()
        }
    
    def reset_search_stats(self):
        """検索統計をリセット"""
        with self.search_lock:
            self.search_stats = {
                "total_searches": 0,
                "google_searches": 0,
                "duckduckgo_searches": 0,
                "successful_searches": 0,
                "failed_searches": 0,
                "total_results": 0,
                "unique_results": 0,
                "last_search_time": None
            }

# テスト用コード
if __name__ == "__main__":
    print("=== マルチ検索エンジン統合テスト ===")
    
    manager = MultiSearchManager()
    
    # エンジン状態確認
    print("検索エンジン状態:")
    statuses = manager.get_engine_status()
    for engine, status in statuses.items():
        print(f"  {engine}: {'✅' if status.available else '❌'} {status.engine_name}")
    
    # テスト検索
    test_query = "Python Machine Learning"
    print(f"\nテスト検索: {test_query}")
    
    result = manager.search(test_query, max_results=10)
    
    print(f"検索成功: {result.success}")
    print(f"使用エンジン: {result.engines_used}")
    print(f"結果件数: {result.total_unique_results}")
    print(f"実行時間: {result.execution_time:.2f}秒")
    
    if result.success:
        print("\n検索結果:")
        for i, item in enumerate(result.combined_results[:5], 1):
            print(f"{i}. {item.title}")
            print(f"   URL: {item.url}")
            print(f"   品質: {item.quality_score:.2f}")
            print()
    
    # 動的クエリテスト
    print("\n=== 動的クエリ検索テスト ===")
    dynamic_result = manager.search_with_dynamic_queries(
        theme="機械学習",
        learning_type="深掘り",
        depth_level=3,
        max_results=20
    )
    
    print(f"動的検索成功: {dynamic_result.success}")
    print(f"結果件数: {dynamic_result.total_unique_results}")
    
    # 統計情報
    print(f"\n検索統計: {manager.get_search_stats()}")
    
    print("✅ マルチ検索エンジン統合テスト完了")
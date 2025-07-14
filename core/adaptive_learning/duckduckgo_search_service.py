#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuckDuckGoSearchService - 実データのみWeb検索サービス
ddgs ライブラリを使用した実際の検索結果取得
モック生成機能は完全除去、透明性と正確性を重視
"""

import time
import random
from typing import List, Dict, Optional
from datetime import datetime

# ddgs ライブラリをインポート
try:
    from duckduckgo_search import DDGS
    DUCKDUCKGO_SEARCH_AVAILABLE = True
except ImportError:
    DUCKDUCKGO_SEARCH_AVAILABLE = False
    print("Warning: duckduckgo-search library not found")
    print("Install: pip install duckduckgo-search")

class DuckDuckGoSearchService:
    """実データのみDuckDuckGo検索サービス"""
    
    def __init__(self):
        """初期化"""
        self.search_history = []
        self.last_search_time = 0
        self.min_search_interval = 2.0  # 最小検索間隔（秒）
        self.max_retries = 3  # 最大リトライ回数
        
        # ライブラリ可用性チェック
        if not DUCKDUCKGO_SEARCH_AVAILABLE:
            print("❌ duckduckgo-search ライブラリが利用できません")
            print("このサービスは実データ検索のみを提供します")
    
    def search(self, query: str, max_results: int = 5) -> List[Dict]:
        """
        実際のDuckDuckGo検索実行
        
        Args:
            query: 検索クエリ
            max_results: 最大結果数
            
        Returns:
            実際の検索結果のリスト（取得できない場合は空リスト）
        """
        if not DUCKDUCKGO_SEARCH_AVAILABLE:
            print(f"🔍 検索スキップ: '{query}' (ライブラリ未インストール)")
            return []
        
        # レート制限対策
        self._enforce_rate_limit()
        
        for retry in range(self.max_retries):
            # 試行回数に応じてバックエンドを変更
            backends = ["html", "lite", "api"]
            backend = backends[retry % len(backends)]
            
            try:
                print(f"🔍 検索実行: '{query}' (試行 {retry + 1}/{self.max_retries}, backend: {backend})")
                
                # 実際のDuckDuckGo検索実行（シンプルなパラメータ）
                if backend == "html":
                    ddgs_results = DDGS(timeout=15).text(query, max_results=max_results)
                else:
                    ddgs_results = DDGS(timeout=15).text(
                        query, 
                        max_results=max_results,
                        backend=backend
                    )
                
                # 実際の結果を標準フォーマットに変換
                formatted_results = []
                for result in ddgs_results:
                    formatted_results.append({
                        'title': result.get('title', ''),
                        'snippet': result.get('body', ''),
                        'url': result.get('href', ''),
                        'source': result.get('hostname', 'Unknown')
                    })
                
                # 検索履歴に記録
                self._record_search_history(query, len(formatted_results), max_results, success=True)
                
                print(f"✅ 検索成功: '{query}' ({len(formatted_results)}/{max_results}件取得)")
                return formatted_results
                
            except Exception as e:
                error_type = type(e).__name__
                error_msg = str(e)
                print(f"⚠️ 検索エラー (試行 {retry + 1}): {error_type} - {error_msg}")
                
                # DNS解決エラーの場合
                if 'dns error' in error_msg.lower() or 'そのようなホストは不明' in error_msg:
                    print("🌐 DNS解決エラー: インターネット接続またはプロキシ設定を確認してください")
                    if retry < self.max_retries - 1:
                        wait_time = 5  # 短めの待機
                        print(f"⏳ DNS解決エラー: {wait_time}秒待機後リトライ...")
                        time.sleep(wait_time)
                        continue
                
                # レート制限エラーの場合は長時間待機
                elif 'ratelimit' in error_msg.lower() or 'rate limit' in error_msg.lower():
                    if retry < self.max_retries - 1:
                        wait_time = 60  # 60秒待機
                        print(f"⏳ レート制限検出: {wait_time}秒待機します...")
                        time.sleep(wait_time)
                        continue
                
                # タイムアウトエラーの場合は短時間待機
                elif 'timeout' in error_msg.lower():
                    if retry < self.max_retries - 1:
                        wait_time = random.uniform(3, 7)
                        print(f"⏳ タイムアウト検出: {wait_time:.1f}秒待機後リトライ...")
                        time.sleep(wait_time)
                        continue
                
                # その他のエラーの場合は短時間待機
                else:
                    if retry < self.max_retries - 1:
                        wait_time = random.uniform(1, 3)
                        print(f"⏳ エラー検出: {wait_time:.1f}秒待機後リトライ...")
                        time.sleep(wait_time)
                        continue
        
        # すべてのリトライが失敗した場合
        self._record_search_history(query, 0, max_results, success=False)
        print(f"❌ 検索失敗: '{query}' (全{self.max_retries}回試行失敗)")
        return []  # 実データが取得できない場合は空リスト
    
    def _enforce_rate_limit(self):
        """レート制限の強制実行"""
        current_time = time.time()
        time_since_last = current_time - self.last_search_time
        
        if time_since_last < self.min_search_interval:
            wait_time = self.min_search_interval - time_since_last
            print(f"⏳ レート制限: {wait_time:.1f}秒待機...")
            time.sleep(wait_time)
        
        self.last_search_time = time.time()
    
    def _record_search_history(self, query: str, results_count: int, max_requested: int, success: bool):
        """検索履歴の記録"""
        self.search_history.append({
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'results_count': results_count,
            'max_requested': max_requested,
            'success': success,
            'success_rate': results_count / max_requested if max_requested > 0 else 0.0
        })
    
    def batch_search(self, queries: List[str], max_results_per_query: int = 3) -> Dict[str, List[Dict]]:
        """
        複数クエリの一括検索（実データのみ）
        
        Args:
            queries: 検索クエリのリスト
            max_results_per_query: クエリごとの最大結果数
            
        Returns:
            クエリごとの検索結果辞書
        """
        results = {}
        successful_searches = 0
        
        print(f"🔍 バッチ検索開始: {len(queries)}クエリ")
        
        for i, query in enumerate(queries):
            # 進捗表示
            progress = ((i + 1) / len(queries)) * 100
            print(f"📊 進捗: {i + 1}/{len(queries)} ({progress:.1f}%)")
            
            # 各検索間に適切な間隔を設ける
            if i > 0:
                interval = random.uniform(2.0, 4.0)
                print(f"⏳ 検索間隔: {interval:.1f}秒")
                time.sleep(interval)
            
            # 実際の検索実行
            search_results = self.search(query, max_results_per_query)
            results[query] = search_results
            
            if search_results:
                successful_searches += 1
                print(f"✅ 検索完了: '{query}' ({len(search_results)}件)")
            else:
                print(f"❌ 検索失敗: '{query}' (0件)")
        
        # バッチ検索サマリー
        success_rate = (successful_searches / len(queries)) * 100 if queries else 0
        total_results = sum(len(result_list) for result_list in results.values())
        
        print(f"🎯 バッチ検索完了:")
        print(f"   成功率: {successful_searches}/{len(queries)} ({success_rate:.1f}%)")
        print(f"   総取得件数: {total_results}件")
        
        return results
    
    def get_search_summary(self) -> Dict:
        """検索履歴の要約統計"""
        if not self.search_history:
            return {
                "total_searches": 0, 
                "total_results": 0,
                "success_rate": 0.0,
                "message": "検索履歴がありません"
            }
        
        total_searches = len(self.search_history)
        successful_searches = sum(1 for entry in self.search_history if entry["success"])
        total_results = sum(entry["results_count"] for entry in self.search_history)
        avg_results = total_results / total_searches if total_searches > 0 else 0
        overall_success_rate = (successful_searches / total_searches) * 100 if total_searches > 0 else 0
        
        return {
            "total_searches": total_searches,
            "successful_searches": successful_searches,
            "total_results": total_results,
            "overall_success_rate": overall_success_rate,
            "average_results_per_search": avg_results,
            "recent_searches": self.search_history[-5:] if len(self.search_history) >= 5 else self.search_history
        }
    
    def get_detailed_stats(self) -> Dict:
        """詳細な検索統計"""
        if not self.search_history:
            return {"message": "統計データがありません"}
        
        successful_searches = [entry for entry in self.search_history if entry["success"]]
        failed_searches = [entry for entry in self.search_history if not entry["success"]]
        
        return {
            "library_available": DUCKDUCKGO_SEARCH_AVAILABLE,
            "total_searches": len(self.search_history),
            "successful_searches": len(successful_searches),
            "failed_searches": len(failed_searches),
            "success_rate_percent": (len(successful_searches) / len(self.search_history)) * 100,
            "total_results_obtained": sum(entry["results_count"] for entry in successful_searches),
            "average_results_per_successful_search": 
                sum(entry["results_count"] for entry in successful_searches) / len(successful_searches) 
                if successful_searches else 0,
            "rate_limit_config": {
                "min_interval_seconds": self.min_search_interval,
                "max_retries": self.max_retries
            }
        }
    
    def format_search_results(self, results: List[Dict]) -> str:
        """検索結果をテキスト形式に整形"""
        if not results:
            return "🔍 検索結果: 0件\n実際のデータを取得できませんでした。"
        
        formatted = [f"🔍 検索結果: {len(results)}件 (実データのみ)\n"]
        
        for i, result in enumerate(results, 1):
            formatted.append(f"""
{i}. {result['title']}
   {result['snippet'][:200]}{'...' if len(result['snippet']) > 200 else ''}
   🌐 URL: {result['url']}
   📍 出典: {result['source']}
""")
        
        return "\n".join(formatted)

if __name__ == "__main__":
    """テスト実行"""
    service = DuckDuckGoSearchService()
    
    print("🔍 実データのみDuckDuckGo検索サービス - テスト実行")
    print(f"📚 ライブラリ利用可能: {'✅' if DUCKDUCKGO_SEARCH_AVAILABLE else '❌'}")
    
    if not DUCKDUCKGO_SEARCH_AVAILABLE:
        print("\n⚠️ ddgs ライブラリをインストールしてください:")
        print("pip install ddgs")
        exit(1)
    
    # テスト検索
    test_queries = [
        "AI技術 最新動向 2025",
        "機械学習 実践応用",
        "Python プログラミング"
    ]
    
    print(f"\n📝 テスト開始: {len(test_queries)}個のクエリ")
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"🔍 検索テスト: '{query}'")
        
        results = service.search(query, max_results=3)
        
        if results:
            print(f"✅ 成功: {len(results)}件取得")
            for i, result in enumerate(results, 1):
                print(f"  {i}. {result['title'][:50]}...")
                print(f"     URL: {result['url'][:60]}...")
        else:
            print("❌ 検索結果なし")
    
    # 統計表示
    print(f"\n{'='*60}")
    print("📊 検索統計:")
    summary = service.get_search_summary()
    print(f"   総検索数: {summary['total_searches']}")
    print(f"   成功数: {summary['successful_searches']}")
    print(f"   成功率: {summary['overall_success_rate']:.1f}%")
    print(f"   総取得件数: {summary['total_results']}")
    
    detailed_stats = service.get_detailed_stats()
    print(f"\n📈 詳細統計:")
    print(f"   平均取得件数: {detailed_stats['average_results_per_successful_search']:.1f}件/成功検索")
    print(f"   レート制限間隔: {detailed_stats['rate_limit_config']['min_interval_seconds']}秒")
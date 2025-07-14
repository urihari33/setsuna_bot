#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web検索デバッグテストツール
DuckDuckGo APIの動作確認とデバッグ用テストツール
"""

import sys
import os
import time
import json
import requests
from pathlib import Path
from datetime import datetime
from urllib.parse import quote
from typing import Dict, List, Any, Optional
import argparse
import traceback
from dataclasses import dataclass
import hashlib

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.debug_logger import get_debug_logger

@dataclass
class WebSearchResult:
    """Web検索結果データクラス"""
    query: str
    success: bool
    results_count: int
    execution_time: float
    response_status: int
    error_message: Optional[str] = None
    results: List[Dict] = None

class WebSearchDebugger:
    """Web検索デバッグツールメインクラス"""
    
    def __init__(self):
        """初期化"""
        self.logger = get_debug_logger(component="WEB_SEARCH_DEBUGGER")
        self.test_queries = [
            "AI技術 最新情報",
            "Python プログラミング",
            "機械学習 トレンド 2024",
            "データサイエンス 市場分析",
            "クラウドコンピューティング 将来性"
        ]
        
        print("=== Web検索デバッグツール ===")
        self.logger.info("WebSearchDebugger初期化完了")
    
    def test_duckduckgo_api(self, query: str) -> WebSearchResult:
        """
        DuckDuckGo API単体テスト
        
        Args:
            query: 検索クエリ
            
        Returns:
            検索結果
        """
        start_time = time.time()
        
        try:
            # DuckDuckGo検索API URL構築
            search_url = f"https://api.duckduckgo.com/?q={quote(query)}&format=json&no_html=1"
            
            self.logger.info(f"DuckDuckGo API テスト開始: {query}", {
                "query": query,
                "search_url": search_url
            })
            
            # HTTP リクエスト実行
            response = requests.get(search_url, timeout=10)
            execution_time = time.time() - start_time
            
            self.logger.debug("HTTP レスポンス受信", {
                "status_code": response.status_code,
                "response_time": execution_time,
                "content_length": len(response.content) if response.content else 0,
                "content_type": response.headers.get('content-type', 'unknown'),
                "response_headers": dict(response.headers)
            })
            
            # レスポンス内容をログに記録
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    
                    self.logger.debug("JSON レスポンス解析", {
                        "data_keys": list(response_data.keys()) if response_data else [],
                        "related_topics_count": len(response_data.get("RelatedTopics", [])),
                        "instant_answer": response_data.get("InstantAnswer", ""),
                        "abstract": response_data.get("Abstract", "")[:200] if response_data.get("Abstract") else "",
                        "answer_type": response_data.get("AnswerType", ""),
                        "definition": response_data.get("Definition", "")[:200] if response_data.get("Definition") else ""
                    })
                    
                    # 結果処理
                    processed_results = self._process_duckduckgo_results(response_data, query)
                    
                    return WebSearchResult(
                        query=query,
                        success=True,
                        results_count=len(processed_results),
                        execution_time=execution_time,
                        response_status=response.status_code,
                        results=processed_results
                    )
                    
                except json.JSONDecodeError as json_error:
                    self.logger.error("JSON解析エラー", {
                        "response_text": response.text[:500],
                        "content_type": response.headers.get('content-type', 'unknown')
                    }, json_error)
                    
                    return WebSearchResult(
                        query=query,
                        success=False,
                        results_count=0,
                        execution_time=execution_time,
                        response_status=response.status_code,
                        error_message=f"JSON解析エラー: {str(json_error)}"
                    )
            
            else:
                self.logger.warning("HTTP エラーレスポンス", {
                    "status_code": response.status_code,
                    "response_text": response.text[:200] if response.text else "",
                    "response_headers": dict(response.headers)
                })
                
                return WebSearchResult(
                    query=query,
                    success=False,
                    results_count=0,
                    execution_time=execution_time,
                    response_status=response.status_code,
                    error_message=f"HTTP エラー: {response.status_code}"
                )
                
        except requests.RequestException as req_error:
            execution_time = time.time() - start_time
            self.logger.error("リクエストエラー", {
                "query": query,
                "search_url": search_url,
                "execution_time": execution_time,
                "error_type": type(req_error).__name__
            }, req_error)
            
            return WebSearchResult(
                query=query,
                success=False,
                results_count=0,
                execution_time=execution_time,
                response_status=0,
                error_message=f"リクエストエラー: {str(req_error)}"
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error("予期しないエラー", {
                "query": query,
                "execution_time": execution_time,
                "error_type": type(e).__name__
            }, e)
            
            return WebSearchResult(
                query=query,
                success=False,
                results_count=0,
                execution_time=execution_time,
                response_status=0,
                error_message=f"予期しないエラー: {str(e)}"
            )
    
    def _process_duckduckgo_results(self, response_data: Dict, query: str) -> List[Dict]:
        """DuckDuckGo レスポンスデータを処理"""
        results = []
        
        try:
            # RelatedTopics からの結果抽出
            related_topics = response_data.get("RelatedTopics", [])
            
            self.logger.debug("RelatedTopics 処理開始", {
                "total_topics": len(related_topics),
                "topics_preview": [topic.get("Text", "")[:50] for topic in related_topics[:3]]
            })
            
            for i, topic in enumerate(related_topics):
                if isinstance(topic, dict) and "Text" in topic and "FirstURL" in topic:
                    # ソースID生成
                    source_id = f"web_{hashlib.sha256(topic['FirstURL'].encode()).hexdigest()[:12]}"
                    
                    result = {
                        "source_id": source_id,
                        "source_type": "web_search",
                        "query": query,
                        "url": topic["FirstURL"],
                        "title": topic.get("Text", "")[:100],
                        "content": topic.get("Text", ""),
                        "collected_at": datetime.now().isoformat(),
                        "reliability_score": 0.7,
                        "relevance_score": 0.8,
                        "raw_data": topic  # デバッグ用
                    }
                    
                    results.append(result)
                    
                    self.logger.debug(f"結果処理 {i+1}", {
                        "source_id": source_id,
                        "url": topic["FirstURL"],
                        "title_length": len(topic.get("Text", "")),
                        "content_length": len(topic.get("Text", ""))
                    })
                
                elif isinstance(topic, dict) and "Topics" in topic:
                    # ネストした Topics の処理
                    nested_topics = topic.get("Topics", [])
                    for nested_topic in nested_topics:
                        if isinstance(nested_topic, dict) and "Text" in nested_topic and "FirstURL" in nested_topic:
                            source_id = f"web_{hashlib.sha256(nested_topic['FirstURL'].encode()).hexdigest()[:12]}"
                            
                            result = {
                                "source_id": source_id,
                                "source_type": "web_search",
                                "query": query,
                                "url": nested_topic["FirstURL"],
                                "title": nested_topic.get("Text", "")[:100],
                                "content": nested_topic.get("Text", ""),
                                "collected_at": datetime.now().isoformat(),
                                "reliability_score": 0.7,
                                "relevance_score": 0.8,
                                "raw_data": nested_topic  # デバッグ用
                            }
                            
                            results.append(result)
            
            # InstantAnswer の処理
            instant_answer = response_data.get("InstantAnswer", "")
            if instant_answer:
                result = {
                    "source_id": f"instant_{hashlib.sha256(instant_answer.encode()).hexdigest()[:12]}",
                    "source_type": "instant_answer",
                    "query": query,
                    "url": "",
                    "title": "Instant Answer",
                    "content": instant_answer,
                    "collected_at": datetime.now().isoformat(),
                    "reliability_score": 0.9,
                    "relevance_score": 0.9
                }
                results.append(result)
            
            # Abstract の処理
            abstract = response_data.get("Abstract", "")
            if abstract:
                result = {
                    "source_id": f"abstract_{hashlib.sha256(abstract.encode()).hexdigest()[:12]}",
                    "source_type": "abstract",
                    "query": query,
                    "url": response_data.get("AbstractURL", ""),
                    "title": "Abstract",
                    "content": abstract,
                    "collected_at": datetime.now().isoformat(),
                    "reliability_score": 0.8,
                    "relevance_score": 0.8
                }
                results.append(result)
            
            self.logger.info("DuckDuckGo結果処理完了", {
                "total_results": len(results),
                "result_types": [r["source_type"] for r in results]
            })
            
        except Exception as e:
            self.logger.error("結果処理エラー", {
                "query": query,
                "error_type": type(e).__name__
            }, e)
        
        return results
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """包括的テスト実行"""
        print("\n🔍 包括的Web検索テスト開始")
        
        test_results = []
        overall_stats = {
            "total_tests": 0,
            "successful_tests": 0,
            "failed_tests": 0,
            "total_results": 0,
            "total_execution_time": 0.0,
            "average_execution_time": 0.0,
            "average_results_per_query": 0.0
        }
        
        for i, query in enumerate(self.test_queries, 1):
            print(f"\n📋 テスト {i}/{len(self.test_queries)}: {query}")
            
            result = self.test_duckduckgo_api(query)
            test_results.append(result)
            
            # 統計更新
            overall_stats["total_tests"] += 1
            overall_stats["total_execution_time"] += result.execution_time
            overall_stats["total_results"] += result.results_count
            
            if result.success:
                overall_stats["successful_tests"] += 1
                print(f"✅ 成功: {result.results_count}件の結果 ({result.execution_time:.2f}秒)")
            else:
                overall_stats["failed_tests"] += 1
                print(f"❌ 失敗: {result.error_message} ({result.execution_time:.2f}秒)")
            
            # API制限対策
            if i < len(self.test_queries):
                time.sleep(1)
        
        # 統計計算
        if overall_stats["total_tests"] > 0:
            overall_stats["average_execution_time"] = overall_stats["total_execution_time"] / overall_stats["total_tests"]
            overall_stats["average_results_per_query"] = overall_stats["total_results"] / overall_stats["total_tests"]
        
        # 結果表示
        self._print_test_summary(test_results, overall_stats)
        
        return {
            "test_results": test_results,
            "overall_stats": overall_stats
        }
    
    def _print_test_summary(self, test_results: List[WebSearchResult], stats: Dict[str, Any]):
        """テスト結果サマリー表示"""
        print(f"\n{'='*70}")
        print("📊 Web検索テスト結果サマリー")
        print(f"{'='*70}")
        
        # 全体統計
        print(f"実行テスト数: {stats['total_tests']}")
        print(f"成功テスト数: {stats['successful_tests']}")
        print(f"失敗テスト数: {stats['failed_tests']}")
        print(f"成功率: {stats['successful_tests']/stats['total_tests']:.1%}")
        print(f"平均実行時間: {stats['average_execution_time']:.2f}秒")
        print(f"平均結果数: {stats['average_results_per_query']:.1f}件")
        print(f"総結果数: {stats['total_results']}件")
        
        # 詳細結果
        print(f"\n🔍 詳細結果:")
        for i, result in enumerate(test_results, 1):
            status = "✅" if result.success else "❌"
            print(f"  {i}. {status} {result.query}")
            print(f"     結果: {result.results_count}件 | 時間: {result.execution_time:.2f}秒 | ステータス: {result.response_status}")
            if result.error_message:
                print(f"     エラー: {result.error_message}")
        
        # 推奨事項
        print(f"\n💡 推奨事項:")
        if stats['failed_tests'] > 0:
            print("  - 失敗したテストの詳細ログを確認してください")
            print("  - ネットワーク接続を確認してください")
            print("  - DuckDuckGo APIの制限を確認してください")
        
        if stats['average_results_per_query'] < 1:
            print("  - 検索クエリをより具体的に調整してください")
            print("  - 代替検索エンジンの使用を検討してください")
        
        if stats['average_execution_time'] > 5:
            print("  - ネットワーク接続速度を確認してください")
            print("  - タイムアウト設定を調整してください")
        
        print(f"{'='*70}")
    
    def test_single_query(self, query: str) -> WebSearchResult:
        """単一クエリテスト"""
        print(f"\n🔍 単一クエリテスト: {query}")
        
        result = self.test_duckduckgo_api(query)
        
        # 結果表示
        if result.success:
            print(f"✅ 成功: {result.results_count}件の結果")
            print(f"   実行時間: {result.execution_time:.2f}秒")
            print(f"   ステータス: {result.response_status}")
            
            # 結果詳細表示
            if result.results and len(result.results) > 0:
                print(f"\n📋 結果詳細:")
                for i, res in enumerate(result.results[:5], 1):  # 最大5件表示
                    print(f"  {i}. {res['title']}")
                    print(f"     URL: {res['url']}")
                    print(f"     タイプ: {res['source_type']}")
                    print(f"     コンテンツ: {res['content'][:100]}...")
        else:
            print(f"❌ 失敗: {result.error_message}")
            print(f"   実行時間: {result.execution_time:.2f}秒")
            print(f"   ステータス: {result.response_status}")
        
        return result
    
    def export_debug_data(self, results: List[WebSearchResult], output_file: str = None):
        """デバッグデータエクスポート"""
        if output_file is None:
            output_file = f"web_search_debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        export_data = {
            "export_info": {
                "timestamp": datetime.now().isoformat(),
                "tool": "WebSearchDebugger",
                "total_tests": len(results)
            },
            "test_results": [
                {
                    "query": r.query,
                    "success": r.success,
                    "results_count": r.results_count,
                    "execution_time": r.execution_time,
                    "response_status": r.response_status,
                    "error_message": r.error_message,
                    "results": r.results
                }
                for r in results
            ]
        }
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2, default=str)
            
            print(f"\n📁 デバッグデータエクスポート完了: {output_file}")
            self.logger.info(f"デバッグデータエクスポート: {output_file}")
            
        except Exception as e:
            print(f"❌ エクスポートエラー: {e}")
            self.logger.error("デバッグデータエクスポートエラー", exception=e)

def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description="Web検索デバッグツール")
    parser.add_argument("--query", "-q", help="単一クエリテスト")
    parser.add_argument("--comprehensive", "-c", action="store_true", help="包括的テスト実行")
    parser.add_argument("--export", "-e", help="結果エクスポートファイル名")
    
    args = parser.parse_args()
    
    try:
        debugger = WebSearchDebugger()
        
        if args.query:
            # 単一クエリテスト
            result = debugger.test_single_query(args.query)
            if args.export:
                debugger.export_debug_data([result], args.export)
                
        elif args.comprehensive:
            # 包括的テスト
            test_data = debugger.run_comprehensive_test()
            if args.export:
                debugger.export_debug_data(test_data["test_results"], args.export)
                
        else:
            # 対話モード
            print("\n🔍 Web検索デバッグツール")
            print("1. 単一クエリテスト")
            print("2. 包括的テスト")
            print("3. 終了")
            
            while True:
                try:
                    choice = input("\n選択してください (1-3): ").strip()
                    
                    if choice == "1":
                        query = input("検索クエリを入力してください: ").strip()
                        if query:
                            result = debugger.test_single_query(query)
                            
                            export_choice = input("結果をエクスポートしますか？ (y/n): ").strip().lower()
                            if export_choice == 'y':
                                debugger.export_debug_data([result])
                    
                    elif choice == "2":
                        test_data = debugger.run_comprehensive_test()
                        
                        export_choice = input("結果をエクスポートしますか？ (y/n): ").strip().lower()
                        if export_choice == 'y':
                            debugger.export_debug_data(test_data["test_results"])
                    
                    elif choice == "3":
                        break
                    
                    else:
                        print("❌ 無効な選択です")
                        
                except KeyboardInterrupt:
                    print("\n\n👋 テストを中断しました")
                    break
                except Exception as e:
                    print(f"❌ エラーが発生しました: {e}")
        
    except Exception as e:
        print(f"❌ 初期化エラー: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
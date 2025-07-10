#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
データフロー追跡システム
Google検索→データ収集→保存の完全追跡
"""

import json
import os
import sys
import time
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import traceback

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.activity_learning_engine import ActivityLearningEngine

class DataFlowTracer:
    """データフロー追跡クラス"""
    
    def __init__(self):
        """初期化"""
        self.trace_log = []
        self.data_checkpoints = {}
        self.session_states = {}
        
        # トレースログディレクトリ
        self.trace_dir = Path("D:/setsuna_bot/debug_logs/data_flow")
        self.trace_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"📊 データフロー追跡開始: {datetime.now().strftime('%H:%M:%S')}")
    
    def trace_point(self, checkpoint: str, data: Any, metadata: Dict = None):
        """データフロー追跡ポイント"""
        timestamp = datetime.now().isoformat()
        
        # データハッシュ計算
        data_str = json.dumps(data, sort_keys=True, default=str)
        data_hash = hashlib.md5(data_str.encode()).hexdigest()[:8]
        
        trace_entry = {
            "timestamp": timestamp,
            "checkpoint": checkpoint,
            "data_hash": data_hash,
            "data_type": type(data).__name__,
            "data_size": len(data_str),
            "metadata": metadata or {}
        }
        
        self.trace_log.append(trace_entry)
        self.data_checkpoints[checkpoint] = {
            "data": data,
            "trace_entry": trace_entry
        }
        
        print(f"📍 [{timestamp}] {checkpoint}: {data_hash} ({trace_entry['data_size']} bytes)")
        if metadata:
            for key, value in metadata.items():
                print(f"   {key}: {value}")
    
    def compare_checkpoints(self, checkpoint1: str, checkpoint2: str) -> Dict[str, Any]:
        """チェックポイント間比較"""
        if checkpoint1 not in self.data_checkpoints or checkpoint2 not in self.data_checkpoints:
            return {"error": "チェックポイントが見つかりません"}
        
        cp1 = self.data_checkpoints[checkpoint1]
        cp2 = self.data_checkpoints[checkpoint2]
        
        comparison = {
            "checkpoint1": checkpoint1,
            "checkpoint2": checkpoint2,
            "hash_match": cp1["trace_entry"]["data_hash"] == cp2["trace_entry"]["data_hash"],
            "size_diff": cp2["trace_entry"]["data_size"] - cp1["trace_entry"]["data_size"],
            "time_diff": (
                datetime.fromisoformat(cp2["trace_entry"]["timestamp"]) - 
                datetime.fromisoformat(cp1["trace_entry"]["timestamp"])
            ).total_seconds()
        }
        
        return comparison
    
    def trace_google_search_flow(self, engine, query: str):
        """Google検索フロー追跡"""
        print(f"\n🔍 Google検索フロー追跡: {query}")
        
        try:
            # 検索前状態
            self.trace_point("search_request", {
                "query": query,
                "engine_status": engine.search_manager.get_status()
            })
            
            # 検索実行
            search_start = time.time()
            search_result = engine._perform_web_search_detailed(query)
            search_time = time.time() - search_start
            
            # 検索結果追跡
            self.trace_point("search_result", search_result, {
                "execution_time": search_time,
                "success": search_result.get("success", False),
                "source_count": len(search_result.get("sources", []))
            })
            
            return search_result
            
        except Exception as e:
            self.trace_point("search_error", {
                "error": str(e),
                "traceback": traceback.format_exc()
            })
            return {"success": False, "error": str(e)}
    
    def trace_session_data_flow(self, session_id: str):
        """セッション全体のデータフロー追跡"""
        print(f"\n📊 セッションデータフロー追跡: {session_id}")
        
        try:
            # ActivityLearningEngine初期化
            engine = ActivityLearningEngine()
            
            # セッション作成フロー
            session = engine.create_session(
                theme="データフロー追跡テスト",
                learning_type="概要",
                depth_level=1,
                time_limit=60,
                budget_limit=0.5,
                tags=["デバッグ", "追跡"]
            )
            
            self.trace_point("session_created", {
                "session_id": session,
                "engine_status": "initialized"
            })
            
            # 検索クエリ生成追跡
            queries = engine._generate_search_queries("データフロー追跡テスト", 1)
            self.trace_point("queries_generated", queries)
            
            # 各検索の詳細追跡
            all_sources = []
            for i, query in enumerate(queries[:2]):  # 最初の2件のみテスト
                print(f"\n🔍 検索 {i+1}/{len(queries[:2])}: {query}")
                
                search_result = self.trace_google_search_flow(engine, query)
                
                if search_result.get("success"):
                    sources = search_result.get("sources", [])
                    all_sources.extend(sources)
                    
                    self.trace_point(f"search_{i+1}_sources", sources, {
                        "query": query,
                        "source_count": len(sources)
                    })
                else:
                    self.trace_point(f"search_{i+1}_failed", search_result)
            
            # 収集結果統合追跡
            self.trace_point("all_sources_collected", all_sources, {
                "total_sources": len(all_sources)
            })
            
            # セッションデータ構築追跡
            session_data = {
                "collection_results": {
                    "information_sources": all_sources,
                    "raw_content_count": len(all_sources),
                    "filtered_content_count": len(all_sources),
                    "search_queries": queries,
                    "collection_timestamp": datetime.now().isoformat()
                }
            }
            
            self.trace_point("session_data_built", session_data)
            
            # ファイル保存プロセス追跡
            sessions_dir = Path("D:/setsuna_bot/data/activity_knowledge/sessions")
            session_file = sessions_dir / f"{session}.json"
            
            # 保存前状態
            self.trace_point("pre_save_state", {
                "file_path": str(session_file),
                "file_exists": session_file.exists(),
                "dir_exists": sessions_dir.exists(),
                "dir_writable": os.access(sessions_dir, os.W_OK)
            })
            
            # 実際の保存テスト
            try:
                with open(session_file, 'w', encoding='utf-8') as f:
                    json.dump(session_data, f, ensure_ascii=False, indent=2, default=str)
                
                # 保存後検証
                if session_file.exists():
                    file_size = session_file.stat().st_size
                    
                    # 読み込みテスト
                    with open(session_file, 'r', encoding='utf-8') as f:
                        saved_data = json.load(f)
                    
                    self.trace_point("save_success", {
                        "file_path": str(session_file),
                        "file_size": file_size,
                        "data_integrity": saved_data == session_data
                    })
                    
                    # データ比較
                    comparison = self.compare_checkpoints("session_data_built", "save_success")
                    print(f"📊 データ整合性: {comparison}")
                    
                else:
                    self.trace_point("save_failed", {
                        "error": "ファイルが作成されませんでした"
                    })
                    
            except Exception as save_error:
                self.trace_point("save_error", {
                    "error": str(save_error),
                    "traceback": traceback.format_exc()
                })
            
            return session
            
        except Exception as e:
            self.trace_point("session_flow_error", {
                "error": str(e),
                "traceback": traceback.format_exc()
            })
            return None
    
    def analyze_data_flow(self):
        """データフロー分析"""
        print(f"\n📈 データフロー分析:")
        print("=" * 50)
        
        # トレースポイント一覧
        print(f"総トレースポイント: {len(self.trace_log)}")
        for i, entry in enumerate(self.trace_log, 1):
            print(f"{i:2d}. [{entry['timestamp']}] {entry['checkpoint']}")
            print(f"     ハッシュ: {entry['data_hash']}, サイズ: {entry['data_size']} bytes")
        
        # データ変化分析
        print(f"\n📊 データ変化分析:")
        checkpoints = list(self.data_checkpoints.keys())
        for i in range(len(checkpoints) - 1):
            comparison = self.compare_checkpoints(checkpoints[i], checkpoints[i + 1])
            if "error" not in comparison:
                change_indicator = "🔄" if not comparison["hash_match"] else "🔒"
                print(f"{change_indicator} {checkpoints[i]} → {checkpoints[i + 1]}")
                print(f"    時間差: {comparison['time_diff']:.2f}秒")
                print(f"    サイズ差: {comparison['size_diff']:+d} bytes")
                print(f"    データ変化: {'あり' if not comparison['hash_match'] else 'なし'}")
    
    def save_trace_report(self, session_id: str = None):
        """トレースレポート保存"""
        report = {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "trace_log": self.trace_log,
            "data_checkpoints": {
                k: {
                    "trace_entry": v["trace_entry"],
                    "data_preview": str(v["data"])[:500]
                }
                for k, v in self.data_checkpoints.items()
            }
        }
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.trace_dir / f"data_flow_trace_{timestamp}.json"
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2, default=str)
            
            print(f"\n📊 トレースレポート保存: {report_file}")
            return str(report_file)
            
        except Exception as e:
            print(f"❌ トレースレポート保存失敗: {e}")
            return None

def main():
    """メイン実行"""
    tracer = DataFlowTracer()
    
    print("🚀 データフロー追跡テスト開始")
    
    # セッションデータフロー追跡
    session_id = tracer.trace_session_data_flow("test_session")
    
    # 分析結果表示
    tracer.analyze_data_flow()
    
    # レポート保存
    tracer.save_trace_report(session_id)
    
    print("\n✅ データフロー追跡完了")

if __name__ == "__main__":
    main()
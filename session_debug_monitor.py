#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
セッションデバッグ監視ツール
ファイル保存問題の詳細調査と原因特定
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

class SessionDebugMonitor:
    """セッション実行の詳細監視クラス"""
    
    def __init__(self):
        """初期化"""
        self.debug_log = []
        self.file_operations = []
        self.data_snapshots = {}
        self.session_id = None
        
        # デバッグ出力ディレクトリ
        self.debug_dir = Path("D:/setsuna_bot/debug_logs")
        self.debug_dir.mkdir(parents=True, exist_ok=True)
        
        # セッションディレクトリ監視
        self.sessions_dir = Path("D:/setsuna_bot/data/activity_knowledge/sessions")
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"🔍 デバッグ監視開始: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📁 監視ディレクトリ: {self.sessions_dir}")
        print(f"📝 デバッグログ: {self.debug_dir}")
    
    def log_debug(self, message: str, data: Any = None):
        """デバッグログ記録"""
        timestamp = datetime.now().isoformat()
        log_entry = {
            "timestamp": timestamp,
            "message": message,
            "data": data
        }
        self.debug_log.append(log_entry)
        print(f"[{timestamp}] {message}")
        if data:
            print(f"  データ: {data}")
    
    def monitor_file_operations(self, operation: str, file_path: str, success: bool, error: str = None, data_size: int = 0):
        """ファイル操作監視"""
        operation_record = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "file_path": file_path,
            "success": success,
            "error": error,
            "data_size": data_size,
            "file_exists": Path(file_path).exists() if file_path else False
        }
        self.file_operations.append(operation_record)
        
        status = "✅" if success else "❌"
        print(f"{status} {operation}: {file_path}")
        if error:
            print(f"  エラー: {error}")
        if data_size > 0:
            print(f"  データサイズ: {data_size} bytes")
    
    def snapshot_data(self, label: str, data: Any):
        """データスナップショット保存"""
        snapshot = {
            "timestamp": datetime.now().isoformat(),
            "data": data,
            "data_type": type(data).__name__,
            "data_size": len(str(data))
        }
        self.data_snapshots[label] = snapshot
        self.log_debug(f"データスナップショット: {label}", {
            "type": snapshot["data_type"],
            "size": snapshot["data_size"]
        })
    
    def verify_session_file(self, session_id: str) -> Dict[str, Any]:
        """セッションファイル検証"""
        file_path = self.sessions_dir / f"{session_id}.json"
        
        verification = {
            "session_id": session_id,
            "file_path": str(file_path),
            "exists": file_path.exists(),
            "size": 0,
            "readable": False,
            "valid_json": False,
            "has_metadata": False,
            "has_collection_results": False,
            "has_analysis_results": False,
            "error": None
        }
        
        try:
            if file_path.exists():
                verification["size"] = file_path.stat().st_size
                
                # ファイル読み取りテスト
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    verification["readable"] = True
                    
                # JSON解析テスト
                try:
                    data = json.loads(content)
                    verification["valid_json"] = True
                    
                    # データ構造確認
                    verification["has_metadata"] = "session_metadata" in data
                    verification["has_collection_results"] = "collection_results" in data
                    verification["has_analysis_results"] = "analysis_results" in data
                    
                    # 詳細データ分析
                    if verification["has_collection_results"]:
                        collection = data["collection_results"]
                        sources = collection.get("information_sources", [])
                        verification["collection_sources_count"] = len(sources)
                    
                    if verification["has_analysis_results"]:
                        analysis = data["analysis_results"]
                        verification["analysis_content_count"] = len(analysis.get("analyzed_content", []))
                        verification["key_findings_count"] = len(analysis.get("key_findings", []))
                    
                except json.JSONDecodeError as e:
                    verification["error"] = f"JSON解析エラー: {e}"
            else:
                verification["error"] = "ファイルが存在しません"
                
        except Exception as e:
            verification["error"] = f"ファイル検証エラー: {e}"
        
        return verification
    
    def test_file_write_permissions(self) -> Dict[str, Any]:
        """ファイル書き込み権限テスト"""
        test_file = self.sessions_dir / "write_test.json"
        test_data = {"test": "write_permission_check", "timestamp": datetime.now().isoformat()}
        
        test_result = {
            "can_create": False,
            "can_write": False,
            "can_read": False,
            "can_delete": False,
            "error": None
        }
        
        try:
            # 書き込みテスト
            with open(test_file, 'w', encoding='utf-8') as f:
                json.dump(test_data, f, ensure_ascii=False, indent=2)
            test_result["can_create"] = True
            test_result["can_write"] = True
            
            # 読み取りテスト
            with open(test_file, 'r', encoding='utf-8') as f:
                read_data = json.load(f)
                if read_data == test_data:
                    test_result["can_read"] = True
            
            # 削除テスト
            test_file.unlink()
            test_result["can_delete"] = True
            
        except Exception as e:
            test_result["error"] = str(e)
            
            # クリーンアップ
            try:
                if test_file.exists():
                    test_file.unlink()
            except:
                pass
        
        return test_result
    
    def analyze_session_execution(self, session_id: str):
        """セッション実行の詳細分析"""
        self.session_id = session_id
        
        print(f"\n🔍 セッション詳細分析: {session_id}")
        print("=" * 60)
        
        # ファイル権限確認
        print("\n📋 ファイル権限テスト:")
        permission_test = self.test_file_write_permissions()
        for key, value in permission_test.items():
            status = "✅" if value else "❌"
            if key != "error":
                print(f"  {key}: {status} {value}")
            elif value:
                print(f"  エラー: {value}")
        
        # セッションファイル検証
        print(f"\n📄 セッションファイル検証:")
        file_verification = self.verify_session_file(session_id)
        for key, value in file_verification.items():
            if key == "error" and value:
                print(f"  ❌ {key}: {value}")
            elif key != "error":
                status = "✅" if value else "❌"
                print(f"  {key}: {status} {value}")
        
        # ディレクトリ内容確認
        print(f"\n📁 セッションディレクトリ内容:")
        try:
            files = list(self.sessions_dir.glob("*.json"))
            print(f"  総ファイル数: {len(files)}")
            
            # 最新5ファイル表示
            files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            for i, file in enumerate(files[:5], 1):
                mtime = datetime.fromtimestamp(file.stat().st_mtime)
                size = file.stat().st_size
                print(f"  {i}. {file.name} ({size} bytes, {mtime.strftime('%H:%M:%S')})")
                
        except Exception as e:
            print(f"  ❌ ディレクトリ読み取りエラー: {e}")
        
        return file_verification
    
    def save_debug_report(self, session_id: str = None):
        """デバッグレポート保存"""
        if not session_id:
            session_id = self.session_id or "unknown"
        
        report = {
            "session_id": session_id,
            "timestamp": datetime.now().isoformat(),
            "debug_log": self.debug_log,
            "file_operations": self.file_operations,
            "data_snapshots": {k: {**v, "data": str(v["data"])[:1000]} for k, v in self.data_snapshots.items()},
            "session_verification": self.verify_session_file(session_id),
            "permission_test": self.test_file_write_permissions()
        }
        
        report_file = self.debug_dir / f"debug_report_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2, default=str)
            
            print(f"\n📊 デバッグレポート保存: {report_file}")
            return str(report_file)
            
        except Exception as e:
            print(f"❌ デバッグレポート保存失敗: {e}")
            return None

def main():
    """メイン実行"""
    monitor = SessionDebugMonitor()
    
    # 引数からセッションIDを取得
    if len(sys.argv) > 1:
        session_id = sys.argv[1]
        print(f"🎯 指定セッション分析: {session_id}")
        monitor.analyze_session_execution(session_id)
        monitor.save_debug_report(session_id)
    else:
        print("📋 使用方法:")
        print("  python session_debug_monitor.py <session_id>")
        print("\n例:")
        print("  python session_debug_monitor.py session_20250711_013420_444c4fb8")
        
        # 最新セッションを自動検出
        try:
            sessions_dir = Path("D:/setsuna_bot/data/activity_knowledge/sessions")
            if sessions_dir.exists():
                files = list(sessions_dir.glob("session_*.json"))
                if files:
                    latest_file = max(files, key=lambda x: x.stat().st_mtime)
                    latest_session = latest_file.stem
                    print(f"\n🔍 最新セッション自動分析: {latest_session}")
                    monitor.analyze_session_execution(latest_session)
                    monitor.save_debug_report(latest_session)
        except Exception as e:
            print(f"❌ 自動検出失敗: {e}")

if __name__ == "__main__":
    main()
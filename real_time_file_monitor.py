#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
リアルタイムファイル監視ツール
ファイル削除の瞬間を特定
"""

import os
import sys
import time
import json
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.activity_learning_engine import ActivityLearningEngine

class FileMonitor:
    """ファイル監視クラス"""
    
    def __init__(self, session_file: Path):
        self.session_file = session_file
        self.monitoring = False
        self.file_events = []
        self.last_size = 0
        self.last_mtime = 0
        
    def start_monitoring(self):
        """監視開始"""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        print(f"📊 ファイル監視開始: {self.session_file}")
    
    def stop_monitoring(self):
        """監視停止"""
        self.monitoring = False
        print(f"⏹️ ファイル監視停止")
    
    def _monitor_loop(self):
        """監視ループ"""
        check_interval = 0.5  # 0.5秒間隔で監視
        
        while self.monitoring:
            try:
                event = self._check_file_state()
                if event:
                    self.file_events.append(event)
                    self._log_event(event)
                
                time.sleep(check_interval)
                
            except Exception as e:
                print(f"⚠️ 監視エラー: {e}")
                time.sleep(1)
    
    def _check_file_state(self) -> Dict[str, Any]:
        """ファイル状態チェック"""
        timestamp = datetime.now().isoformat()
        
        if self.session_file.exists():
            try:
                stat = self.session_file.stat()
                current_size = stat.st_size
                current_mtime = stat.st_mtime
                
                # サイズ変化検出
                if current_size != self.last_size:
                    event = {
                        "timestamp": timestamp,
                        "type": "size_change",
                        "old_size": self.last_size,
                        "new_size": current_size,
                        "size_diff": current_size - self.last_size,
                        "exists": True
                    }
                    self.last_size = current_size
                    self.last_mtime = current_mtime
                    return event
                
                # 更新時刻変化検出
                if current_mtime != self.last_mtime:
                    event = {
                        "timestamp": timestamp,
                        "type": "mtime_change",
                        "size": current_size,
                        "new_mtime": current_mtime,
                        "exists": True
                    }
                    self.last_mtime = current_mtime
                    return event
                    
            except Exception as e:
                return {
                    "timestamp": timestamp,
                    "type": "access_error",
                    "error": str(e),
                    "exists": True
                }
        else:
            # ファイル消失検出
            if self.last_size > 0 or self.last_mtime > 0:
                event = {
                    "timestamp": timestamp,
                    "type": "file_deleted",
                    "last_size": self.last_size,
                    "last_mtime": self.last_mtime,
                    "exists": False
                }
                self.last_size = 0
                self.last_mtime = 0
                return event
        
        return None
    
    def _log_event(self, event: Dict[str, Any]):
        """イベントログ出力"""
        timestamp = event["timestamp"]
        event_type = event["type"]
        
        if event_type == "size_change":
            size_diff = event["size_diff"]
            sign = "+" if size_diff > 0 else ""
            print(f"📈 [{timestamp}] ファイルサイズ変化: {event['old_size']} → {event['new_size']} ({sign}{size_diff})")
            
        elif event_type == "mtime_change":
            print(f"⏰ [{timestamp}] ファイル更新時刻変化: {event['size']}bytes")
            
        elif event_type == "file_deleted":
            print(f"❌ [{timestamp}] ファイル削除検出! 最終サイズ: {event['last_size']}bytes")
            
        elif event_type == "access_error":
            print(f"⚠️ [{timestamp}] アクセスエラー: {event['error']}")
    
    def get_events(self) -> List[Dict[str, Any]]:
        """イベント履歴取得"""
        return self.file_events.copy()

def test_with_realtime_monitoring():
    """リアルタイム監視付きテスト"""
    print("=== リアルタイム監視付きテスト ===")
    
    try:
        # エンジン初期化
        engine = ActivityLearningEngine()
        print("✅ ActivityLearningEngine初期化成功")
        
        # セッション作成
        session_id = engine.create_session(
            theme="ファイル監視テスト",
            learning_type="概要",
            depth_level=1,
            time_limit=45,  # 45秒
            budget_limit=0.2,
            tags=["監視テスト"]
        )
        
        print(f"📝 セッション作成: {session_id}")
        
        # ファイルパス
        session_file = Path(f"D:/setsuna_bot/data/activity_knowledge/sessions/{session_id}.json")
        
        # ファイル監視開始
        monitor = FileMonitor(session_file)
        monitor.start_monitoring()
        
        # セッション開始
        print("🚀 セッション開始...")
        success = engine.start_session(session_id)
        
        if not success:
            print("❌ セッション開始失敗")
            monitor.stop_monitoring()
            return False
        
        print("✅ セッション開始成功")
        
        # セッション監視
        print("👀 セッション実行監視中...")
        max_wait = 60  # 60秒監視
        wait_time = 0
        
        while wait_time < max_wait:
            time.sleep(5)
            wait_time += 5
            
            # セッション状態確認
            if session_file.exists():
                try:
                    with open(session_file, 'r', encoding='utf-8') as f:
                        session_data = json.load(f)
                    
                    metadata = session_data.get("session_metadata", {})
                    status = metadata.get("status", "unknown")
                    phase = metadata.get("current_phase", "unknown")
                    
                    print(f"🔄 {wait_time}秒: {status}/{phase}")
                    
                    # 完了チェック
                    if status in ["completed", "error", "cancelled"]:
                        print(f"🎯 セッション終了: {status}")
                        time.sleep(2)  # 追加の2秒監視
                        break
                        
                except json.JSONDecodeError:
                    print(f"⚠️ JSON解析エラー ({wait_time}秒)")
                except Exception as e:
                    print(f"⚠️ ファイル読み取りエラー ({wait_time}秒): {e}")
            else:
                print(f"❌ ファイル不存在 ({wait_time}秒)")
        
        # 追加監視（ファイル削除確認）
        print("🔍 追加監視中（ファイル削除確認）...")
        time.sleep(5)
        
        # 監視停止
        monitor.stop_monitoring()
        
        # イベント分析
        events = monitor.get_events()
        print(f"\n📊 検出イベント数: {len(events)}")
        
        # 重要イベント分析
        deletion_events = [e for e in events if e["type"] == "file_deleted"]
        size_changes = [e for e in events if e["type"] == "size_change"]
        
        if deletion_events:
            print(f"\n❌ ファイル削除イベント: {len(deletion_events)}件")
            for event in deletion_events:
                print(f"  {event['timestamp']}: 最終サイズ {event['last_size']}bytes")
        
        if size_changes:
            print(f"\n📈 サイズ変化イベント: {len(size_changes)}件")
            max_size = max([e["new_size"] for e in size_changes])
            min_size = min([e["new_size"] for e in size_changes])
            final_event = size_changes[-1] if size_changes else None
            
            print(f"  最大サイズ: {max_size}bytes")
            print(f"  最小サイズ: {min_size}bytes")
            if final_event:
                print(f"  最終サイズ: {final_event['new_size']}bytes")
        
        # 最終状態確認
        final_exists = session_file.exists()
        print(f"\n🏁 最終状態:")
        print(f"  ファイル存在: {final_exists}")
        
        if final_exists:
            final_size = session_file.stat().st_size
            print(f"  最終ファイルサイズ: {final_size}bytes")
            
            # データ内容確認
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    final_data = json.load(f)
                print(f"  データキー: {list(final_data.keys())}")
                
                collection_sources = len(final_data.get("collection_results", {}).get("information_sources", []))
                print(f"  収集ソース数: {collection_sources}")
                
                return collection_sources > 0 and not deletion_events
            except Exception as e:
                print(f"  ❌ 最終読み取りエラー: {e}")
                return False
        else:
            print("  ❌ ファイルが存在しません")
            return False
    
    except Exception as e:
        print(f"❌ テスト実行エラー: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """メイン実行"""
    print("🔬 リアルタイムファイル監視テスト")
    print(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    result = test_with_realtime_monitoring()
    
    print("=" * 60)
    if result:
        print("🎉 ファイルが正常に保持されました")
    else:
        print("❌ ファイル消失または問題を検出")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
セッション結果ビューワー
学習セッションで収集・分析された内容を表示するツール
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Windows環境のパス設定
if os.name == 'nt':
    DATA_DIR = Path("D:/setsuna_bot/data/activity_knowledge")
else:
    DATA_DIR = Path("/mnt/d/setsuna_bot/data/activity_knowledge")

@dataclass
class SessionSummary:
    """セッション概要データクラス"""
    session_id: str
    theme: str
    learning_type: str
    depth_level: int
    status: str
    start_time: str
    end_time: Optional[str]
    collected_items: int
    processed_items: int
    important_findings: int
    current_cost: float
    execution_time: float

class SessionResultViewer:
    """セッション結果ビューワーメインクラス"""
    
    def __init__(self):
        """初期化"""
        self.sessions_dir = DATA_DIR / "sessions"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        
        print("📊 セッション結果ビューワー初期化完了")
        print(f"📁 セッションディレクトリ: {self.sessions_dir}")
    
    def list_sessions(self) -> List[SessionSummary]:
        """セッション一覧取得"""
        sessions = []
        
        for session_file in self.sessions_dir.glob("session_*.json"):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                
                metadata = session_data.get("session_metadata", {})
                
                # 実行時間計算
                start_time = metadata.get("start_time")
                end_time = metadata.get("end_time")
                execution_time = 0.0
                
                if start_time and end_time:
                    start_dt = datetime.fromisoformat(start_time)
                    end_dt = datetime.fromisoformat(end_time)
                    execution_time = (end_dt - start_dt).total_seconds()
                
                summary = SessionSummary(
                    session_id=metadata.get("session_id", "unknown"),
                    theme=metadata.get("theme", "不明"),
                    learning_type=metadata.get("learning_type", "不明"),
                    depth_level=metadata.get("depth_level", 0),
                    status=metadata.get("status", "不明"),
                    start_time=start_time or "不明",
                    end_time=end_time,
                    collected_items=metadata.get("collected_items", 0),
                    processed_items=metadata.get("processed_items", 0),
                    important_findings=len(metadata.get("important_findings", [])),
                    current_cost=metadata.get("current_cost", 0.0),
                    execution_time=execution_time
                )
                
                sessions.append(summary)
                
            except Exception as e:
                print(f"⚠️ セッションファイル読み込みエラー {session_file.name}: {e}")
        
        # 開始時間で逆順ソート（最新が最初）
        sessions.sort(key=lambda x: x.start_time, reverse=True)
        return sessions
    
    def get_latest_session(self) -> Optional[SessionSummary]:
        """最新セッション取得"""
        sessions = self.list_sessions()
        return sessions[0] if sessions else None
    
    def load_session_details(self, session_id: str) -> Optional[Dict[str, Any]]:
        """セッション詳細データ読み込み"""
        session_file = self.sessions_dir / f"{session_id}.json"
        
        if not session_file.exists():
            print(f"❌ セッションファイルが見つかりません: {session_id}")
            return None
        
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ セッションデータ読み込みエラー: {e}")
            return None
    
    def display_session_list(self):
        """セッション一覧表示"""
        print("\n" + "=" * 80)
        print("📊 学習セッション履歴")
        print("=" * 80)
        
        sessions = self.list_sessions()
        
        if not sessions:
            print("📋 セッション履歴がありません")
            return
        
        print(f"📈 総セッション数: {len(sessions)}")
        print()
        
        for i, session in enumerate(sessions[:10], 1):  # 最新10件表示
            status_emoji = {
                "completed": "✅",
                "running": "🔄",
                "error": "❌",
                "ready": "⏳"
            }.get(session.status, "❓")
            
            print(f"{i:2d}. {status_emoji} {session.session_id}")
            print(f"     📝 テーマ: {session.theme}")
            print(f"     📊 タイプ: {session.learning_type} (深度{session.depth_level})")
            print(f"     🕐 開始: {session.start_time}")
            print(f"     📦 収集: {session.collected_items}件 | 分析: {session.processed_items}件")
            print(f"     💰 コスト: ${session.current_cost:.2f}")
            
            if session.execution_time > 0:
                print(f"     ⏱️ 実行時間: {session.execution_time:.1f}秒")
            print()
    
    def display_session_details(self, session_id: str):
        """セッション詳細表示"""
        print(f"\n" + "=" * 80)
        print(f"📊 セッション詳細: {session_id}")
        print("=" * 80)
        
        session_data = self.load_session_details(session_id)
        if not session_data:
            return
        
        metadata = session_data.get("session_metadata", {})
        
        # 基本情報
        print("📋 基本情報:")
        print(f"  📝 テーマ: {metadata.get('theme', '不明')}")
        print(f"  📊 学習タイプ: {metadata.get('learning_type', '不明')}")
        print(f"  🎯 深度レベル: {metadata.get('depth_level', 0)}")
        print(f"  ⏱️ 時間制限: {metadata.get('time_limit', 0)}秒")
        print(f"  💰 予算制限: ${metadata.get('budget_limit', 0.0)}")
        print(f"  🏷️ タグ: {', '.join(metadata.get('tags', []))}")
        print(f"  📊 ステータス: {metadata.get('status', '不明')}")
        print()
        
        # 進捗情報
        print("📈 進捗情報:")
        print(f"  🕐 開始時刻: {metadata.get('start_time', '不明')}")
        print(f"  🕐 終了時刻: {metadata.get('end_time', '実行中')}")
        print(f"  📦 収集アイテム: {metadata.get('collected_items', 0)}件")
        print(f"  🧠 処理アイテム: {metadata.get('processed_items', 0)}件")
        print(f"  💰 現在のコスト: ${metadata.get('current_cost', 0.0)}")
        print()
        
        # 収集結果
        if "collection_results" in session_data:
            self._display_collection_results(session_data["collection_results"])
        
        # 分析結果
        if "analysis_results" in session_data:
            self._display_analysis_results(session_data["analysis_results"])
        
        # 知識統合結果
        if "generated_knowledge" in session_data:
            self._display_knowledge_integration(session_data["generated_knowledge"])
    
    def _display_collection_results(self, collection_results: Dict[str, Any]):
        """収集結果表示"""
        print("🔍 情報収集結果:")
        
        sources = collection_results.get("information_sources", [])
        print(f"  📊 総収集数: {len(sources)}件")
        
        if sources:
            print("\n  📋 収集ソース一覧:")
            for i, source in enumerate(sources[:5], 1):  # 最初の5件表示
                print(f"    {i}. 🌐 {source.get('title', '無題')}")
                print(f"       📎 URL: {source.get('url', 'なし')}")
                print(f"       📊 信頼性: {source.get('reliability_score', 0):.2f}")
                print(f"       📊 関連性: {source.get('relevance_score', 0):.2f}")
                
                content = source.get('content', '')
                if content:
                    preview = content[:100] + "..." if len(content) > 100 else content
                    print(f"       📝 内容: {preview}")
                print()
            
            if len(sources) > 5:
                print(f"    ... 他 {len(sources) - 5}件")
        print()
    
    def _display_analysis_results(self, analysis_results: Dict[str, Any]):
        """分析結果表示"""
        print("🧠 コンテンツ分析結果:")
        
        # キーファインディング
        key_findings = analysis_results.get("key_findings", [])
        if key_findings:
            print(f"  🔑 重要な発見 ({len(key_findings)}件):")
            for i, finding in enumerate(key_findings[:3], 1):
                print(f"    {i}. {finding}")
            if len(key_findings) > 3:
                print(f"    ... 他 {len(key_findings) - 3}件")
            print()
        
        # エンティティ抽出
        entities = analysis_results.get("extracted_entities", [])
        if entities:
            print(f"  🏷️ 抽出エンティティ: {', '.join(entities[:10])}")
            if len(entities) > 10:
                print(f"    ... 他 {len(entities) - 10}件")
            print()
        
        # 関係性分析
        relationships = analysis_results.get("identified_relationships", [])
        if relationships:
            print(f"  🔗 関係性分析 ({len(relationships)}件):")
            for i, rel in enumerate(relationships[:3], 1):
                print(f"    {i}. {rel}")
            if len(relationships) > 3:
                print(f"    ... 他 {len(relationships) - 3}件")
            print()
    
    def _display_knowledge_integration(self, knowledge_integration: Dict[str, Any]):
        """知識統合結果表示"""
        print("🔗 知識統合結果:")
        
        # 統合サマリー
        summary = knowledge_integration.get("integration_summary", "")
        if summary:
            print(f"  📋 統合サマリー:")
            print(f"    {summary}")
            print()
        
        # 主要なポイント
        key_points = knowledge_integration.get("key_points", [])
        if key_points:
            print(f"  🎯 主要ポイント:")
            for i, point in enumerate(key_points, 1):
                print(f"    {i}. {point}")
            print()
        
        # 推奨アクション
        recommendations = knowledge_integration.get("recommendations", [])
        if recommendations:
            print(f"  💡 推奨アクション:")
            for i, rec in enumerate(recommendations, 1):
                print(f"    {i}. {rec}")
            print()

def main():
    """メイン関数"""
    viewer = SessionResultViewer()
    
    if len(sys.argv) > 1:
        # 特定セッションの詳細表示
        session_id = sys.argv[1]
        viewer.display_session_details(session_id)
    else:
        # セッション一覧表示
        viewer.display_session_list()
        
        # 最新セッションがあれば詳細表示の選択肢を提示
        latest = viewer.get_latest_session()
        if latest:
            print("💡 最新セッションの詳細を表示するには:")
            print(f"   python session_result_viewer.py {latest.session_id}")
            print()
            
            response = input("最新セッションの詳細を表示しますか？ (y/N): ").strip().lower()
            if response in ['y', 'yes']:
                viewer.display_session_details(latest.session_id)

if __name__ == "__main__":
    main()
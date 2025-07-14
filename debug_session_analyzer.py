#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DebugSessionAnalyzer - セッションデバッグ分析ツール
学習セッションの問題を特定・分析するツール
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import argparse
import traceback
from dataclasses import dataclass
from collections import defaultdict

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.debug_logger import get_debug_logger, LogLevel, DEBUG_LOG_DIR

# Windows環境のパス設定
if os.name == 'nt':
    SESSIONS_DIR = Path("D:/setsuna_bot/data/activity_knowledge/sessions")
else:
    SESSIONS_DIR = Path("/mnt/d/setsuna_bot/data/activity_knowledge/sessions")

@dataclass
class AnalysisResult:
    """分析結果データクラス"""
    session_id: str
    status: str
    issues: List[str]
    recommendations: List[str]
    performance_metrics: Dict[str, Any]
    detailed_analysis: Dict[str, Any]

class DebugSessionAnalyzer:
    """セッションデバッグ分析ツールメインクラス"""
    
    def __init__(self):
        """初期化"""
        self.logger = get_debug_logger(component="SESSION_ANALYZER")
        self.sessions_dir = SESSIONS_DIR
        self.debug_logs_dir = DEBUG_LOG_DIR
        
        # 分析結果
        self.analysis_results = []
        
        # 問題検出パターン
        self.issue_patterns = {
            "web_search_failure": {
                "keywords": ["Web検索エラー", "DuckDuckGo", "timeout", "connection"],
                "severity": "high",
                "description": "Web検索APIの接続または応答に問題があります"
            },
            "empty_search_results": {
                "keywords": ["検索結果が空", "0件", "results_count: 0"],
                "severity": "medium",
                "description": "検索クエリに対する結果が得られていません"
            },
            "api_key_missing": {
                "keywords": ["APIキーが設定されていません", "API key", "OPENAI_API_KEY"],
                "severity": "critical",
                "description": "OpenAI APIキーが正しく設定されていません"
            },
            "session_timeout": {
                "keywords": ["時間制限", "time_limit", "timeout"],
                "severity": "medium",
                "description": "セッションが時間制限に達しました"
            },
            "budget_exceeded": {
                "keywords": ["予算制限", "budget_limit", "cost"],
                "severity": "medium",
                "description": "セッションが予算制限に達しました"
            },
            "preprocessing_failure": {
                "keywords": ["前処理エラー", "preprocessing", "GPT-3.5"],
                "severity": "high",
                "description": "前処理エンジンで問題が発生しました"
            }
        }
        
        print("=== セッションデバッグ分析ツール ===")
        self.logger.info("DebugSessionAnalyzer初期化完了")
    
    def analyze_session(self, session_id: str) -> AnalysisResult:
        """
        指定セッションの分析実行
        
        Args:
            session_id: 分析対象セッションID
            
        Returns:
            分析結果
        """
        self.logger.info(f"セッション分析開始: {session_id}")
        
        try:
            # セッションデータ読み込み
            session_data = self._load_session_data(session_id)
            if not session_data:
                return AnalysisResult(
                    session_id=session_id,
                    status="error",
                    issues=["セッションデータが見つかりません"],
                    recommendations=["セッションIDを確認してください"],
                    performance_metrics={},
                    detailed_analysis={}
                )
            
            # デバッグログ読み込み
            debug_logs = self._load_debug_logs(session_id)
            
            # 分析実行
            issues = self._detect_issues(session_data, debug_logs)
            recommendations = self._generate_recommendations(session_data, issues)
            performance_metrics = self._calculate_performance_metrics(session_data, debug_logs)
            detailed_analysis = self._perform_detailed_analysis(session_data, debug_logs)
            
            # 分析結果作成
            result = AnalysisResult(
                session_id=session_id,
                status="completed",
                issues=issues,
                recommendations=recommendations,
                performance_metrics=performance_metrics,
                detailed_analysis=detailed_analysis
            )
            
            self.logger.info(f"セッション分析完了: {session_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"セッション分析エラー: {session_id}", exception=e)
            return AnalysisResult(
                session_id=session_id,
                status="error",
                issues=[f"分析エラー: {str(e)}"],
                recommendations=["ログファイルとセッションデータを確認してください"],
                performance_metrics={},
                detailed_analysis={}
            )
    
    def _load_session_data(self, session_id: str) -> Optional[Dict]:
        """セッションデータ読み込み"""
        try:
            session_files = list(self.sessions_dir.glob(f"{session_id}*.json"))
            if not session_files:
                # 部分一致で検索
                session_files = [f for f in self.sessions_dir.glob("*.json") if session_id in f.name]
            
            if not session_files:
                self.logger.warning(f"セッションファイルが見つかりません: {session_id}")
                return None
            
            session_file = session_files[0]  # 最初のファイルを使用
            
            with open(session_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.logger.debug(f"セッションデータ読み込み成功: {session_file}")
            return data
            
        except Exception as e:
            self.logger.error(f"セッションデータ読み込みエラー: {session_id}", exception=e)
            return None
    
    def _load_debug_logs(self, session_id: str) -> List[Dict]:
        """デバッグログ読み込み"""
        try:
            debug_logs = []
            
            # JSON形式のデバッグログを検索
            log_files = list(self.debug_logs_dir.glob(f"{session_id}*.json"))
            if not log_files:
                # 部分一致で検索
                log_files = [f for f in self.debug_logs_dir.glob("*.json") if session_id in f.name]
            
            for log_file in log_files:
                try:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        log_data = json.load(f)
                    
                    if isinstance(log_data, list):
                        debug_logs.extend(log_data)
                    else:
                        debug_logs.append(log_data)
                        
                except Exception as e:
                    self.logger.warning(f"デバッグログ読み込みエラー: {log_file}", exception=e)
            
            self.logger.debug(f"デバッグログ読み込み完了: {len(debug_logs)}件")
            return debug_logs
            
        except Exception as e:
            self.logger.error(f"デバッグログ読み込みエラー: {session_id}", exception=e)
            return []
    
    def _detect_issues(self, session_data: Dict, debug_logs: List[Dict]) -> List[str]:
        """問題検出"""
        issues = []
        
        try:
            # セッションデータからの問題検出
            session_metadata = session_data.get("session_metadata", {})
            
            # 1. セッション完了状況
            if session_metadata.get("status") == "error":
                issues.append("セッションがエラーで終了しました")
            
            # 2. 収集データの問題
            collection_results = session_data.get("collection_results", {})
            collected_count = collection_results.get("raw_content_count", 0)
            filtered_count = collection_results.get("filtered_content_count", 0)
            
            if collected_count == 0:
                issues.append("情報収集で何もデータが取得されませんでした")
            elif filtered_count == 0 and collected_count > 0:
                issues.append("前処理で全てのデータが除外されました")
            
            # 3. セッション時間の問題
            if session_metadata.get("start_time") and session_metadata.get("end_time"):
                start_time = datetime.fromisoformat(session_metadata["start_time"])
                end_time = datetime.fromisoformat(session_metadata["end_time"])
                duration = (end_time - start_time).total_seconds()
                
                if duration < 30:  # 30秒未満
                    issues.append(f"セッション実行時間が異常に短い ({duration:.1f}秒)")
            
            # 4. デバッグログからの問題検出
            for log_entry in debug_logs:
                if not isinstance(log_entry, dict):
                    continue
                    
                log_level = log_entry.get("level", "")
                log_message = log_entry.get("message", "")
                
                # エラーレベルのログ
                if log_level in ["ERROR", "CRITICAL"]:
                    issues.append(f"エラーログ: {log_message}")
                
                # 問題パターンマッチング
                for issue_type, pattern in self.issue_patterns.items():
                    for keyword in pattern["keywords"]:
                        if keyword in log_message:
                            issues.append(f"{pattern['description']}: {log_message}")
                            break
            
            # 5. 重複削除
            issues = list(set(issues))
            
        except Exception as e:
            self.logger.error("問題検出エラー", exception=e)
            issues.append(f"問題検出処理でエラーが発生しました: {str(e)}")
        
        return issues
    
    def _generate_recommendations(self, session_data: Dict, issues: List[str]) -> List[str]:
        """推奨事項生成"""
        recommendations = []
        
        try:
            # 問題ベースの推奨事項
            for issue in issues:
                if "Web検索" in issue:
                    recommendations.append("ネットワーク接続を確認してください")
                    recommendations.append("DuckDuckGo APIの状態を確認してください")
                    recommendations.append("代替検索エンジンの使用を検討してください")
                
                elif "APIキー" in issue:
                    recommendations.append(".envファイルでOPENAI_API_KEYを設定してください")
                    recommendations.append("APIキーの有効性を確認してください")
                
                elif "データが取得されませんでした" in issue:
                    recommendations.append("検索クエリをより一般的な表現に変更してください")
                    recommendations.append("検索対象のテーマを見直してください")
                
                elif "時間が異常に短い" in issue:
                    recommendations.append("セッション設定（時間制限・予算制限）を確認してください")
                    recommendations.append("外部API接続の問題を調査してください")
                
                elif "前処理で全てのデータが除外" in issue:
                    recommendations.append("前処理の閾値設定を緩和してください")
                    recommendations.append("収集データの品質を向上させてください")
            
            # 一般的な推奨事項
            session_metadata = session_data.get("session_metadata", {})
            if session_metadata.get("status") != "completed":
                recommendations.append("セッションを再実行してください")
                recommendations.append("より適切なテーマと設定で新しいセッションを作成してください")
            
            # 重複削除
            recommendations = list(set(recommendations))
            
        except Exception as e:
            self.logger.error("推奨事項生成エラー", exception=e)
            recommendations.append("問題の詳細分析を実行してください")
        
        return recommendations
    
    def _calculate_performance_metrics(self, session_data: Dict, debug_logs: List[Dict]) -> Dict[str, Any]:
        """パフォーマンス指標計算"""
        metrics = {}
        
        try:
            session_metadata = session_data.get("session_metadata", {})
            
            # 基本指標
            metrics["session_status"] = session_metadata.get("status", "unknown")
            metrics["collected_items"] = session_metadata.get("collected_items", 0)
            metrics["processed_items"] = session_metadata.get("processed_items", 0)
            metrics["current_cost"] = session_metadata.get("current_cost", 0.0)
            
            # 時間指標
            if session_metadata.get("start_time") and session_metadata.get("end_time"):
                start_time = datetime.fromisoformat(session_metadata["start_time"])
                end_time = datetime.fromisoformat(session_metadata["end_time"])
                duration = (end_time - start_time).total_seconds()
                
                metrics["total_duration"] = duration
                metrics["items_per_second"] = metrics["collected_items"] / duration if duration > 0 else 0
                metrics["cost_per_second"] = metrics["current_cost"] / duration if duration > 0 else 0
            
            # 収集結果指標
            collection_results = session_data.get("collection_results", {})
            metrics["raw_content_count"] = collection_results.get("raw_content_count", 0)
            metrics["filtered_content_count"] = collection_results.get("filtered_content_count", 0)
            
            if metrics["raw_content_count"] > 0:
                metrics["filtering_efficiency"] = metrics["filtered_content_count"] / metrics["raw_content_count"]
            else:
                metrics["filtering_efficiency"] = 0.0
            
            # ログ統計
            log_levels = defaultdict(int)
            for log_entry in debug_logs:
                if isinstance(log_entry, dict):
                    level = log_entry.get("level", "UNKNOWN")
                    log_levels[level] += 1
            
            metrics["log_statistics"] = dict(log_levels)
            metrics["error_rate"] = (log_levels["ERROR"] + log_levels["CRITICAL"]) / max(1, len(debug_logs))
            
        except Exception as e:
            self.logger.error("パフォーマンス指標計算エラー", exception=e)
            metrics["calculation_error"] = str(e)
        
        return metrics
    
    def _perform_detailed_analysis(self, session_data: Dict, debug_logs: List[Dict]) -> Dict[str, Any]:
        """詳細分析実行"""
        analysis = {}
        
        try:
            # Web検索分析
            web_search_analysis = self._analyze_web_search(debug_logs)
            analysis["web_search"] = web_search_analysis
            
            # セッションフェーズ分析
            phase_analysis = self._analyze_session_phases(debug_logs)
            analysis["session_phases"] = phase_analysis
            
            # API使用分析
            api_analysis = self._analyze_api_usage(debug_logs)
            analysis["api_usage"] = api_analysis
            
            # エラー分析
            error_analysis = self._analyze_errors(debug_logs)
            analysis["errors"] = error_analysis
            
        except Exception as e:
            self.logger.error("詳細分析エラー", exception=e)
            analysis["analysis_error"] = str(e)
        
        return analysis
    
    def _analyze_web_search(self, debug_logs: List[Dict]) -> Dict[str, Any]:
        """Web検索分析"""
        analysis = {
            "total_searches": 0,
            "successful_searches": 0,
            "failed_searches": 0,
            "empty_results": 0,
            "average_results_per_search": 0,
            "search_queries": [],
            "errors": []
        }
        
        try:
            results_counts = []
            
            for log_entry in debug_logs:
                if not isinstance(log_entry, dict):
                    continue
                
                message = log_entry.get("message", "")
                context = log_entry.get("context", {})
                
                if "Web検索実行" in message:
                    analysis["total_searches"] += 1
                    
                    # 検索クエリ記録
                    if "web_search" in context:
                        query = context["web_search"].get("query", "")
                        if query:
                            analysis["search_queries"].append(query)
                        
                        results_count = context["web_search"].get("results_count", 0)
                        if results_count is not None:
                            results_counts.append(results_count)
                            
                            if results_count > 0:
                                analysis["successful_searches"] += 1
                            else:
                                analysis["empty_results"] += 1
                
                elif "Web検索エラー" in message:
                    analysis["failed_searches"] += 1
                    analysis["errors"].append(message)
            
            # 平均結果数計算
            if results_counts:
                analysis["average_results_per_search"] = sum(results_counts) / len(results_counts)
            
            # 成功率計算
            if analysis["total_searches"] > 0:
                analysis["success_rate"] = analysis["successful_searches"] / analysis["total_searches"]
            else:
                analysis["success_rate"] = 0.0
            
        except Exception as e:
            analysis["analysis_error"] = str(e)
        
        return analysis
    
    def _analyze_session_phases(self, debug_logs: List[Dict]) -> Dict[str, Any]:
        """セッションフェーズ分析"""
        analysis = {
            "phases": [],
            "phase_durations": {},
            "phase_status": {}
        }
        
        try:
            phase_starts = {}
            
            for log_entry in debug_logs:
                if not isinstance(log_entry, dict):
                    continue
                
                context = log_entry.get("context", {})
                if "session_phase" in context:
                    phase_info = context["session_phase"]
                    phase = phase_info.get("phase", "")
                    status = phase_info.get("status", "")
                    timestamp = log_entry.get("timestamp", "")
                    
                    if phase not in analysis["phases"]:
                        analysis["phases"].append(phase)
                    
                    analysis["phase_status"][phase] = status
                    
                    if status == "started":
                        phase_starts[phase] = timestamp
                    elif status == "completed" and phase in phase_starts:
                        try:
                            start_time = datetime.fromisoformat(phase_starts[phase])
                            end_time = datetime.fromisoformat(timestamp)
                            duration = (end_time - start_time).total_seconds()
                            analysis["phase_durations"][phase] = duration
                        except Exception:
                            pass
            
        except Exception as e:
            analysis["analysis_error"] = str(e)
        
        return analysis
    
    def _analyze_api_usage(self, debug_logs: List[Dict]) -> Dict[str, Any]:
        """API使用分析"""
        analysis = {
            "api_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "apis_used": [],
            "errors": []
        }
        
        try:
            for log_entry in debug_logs:
                if not isinstance(log_entry, dict):
                    continue
                
                message = log_entry.get("message", "")
                context = log_entry.get("context", {})
                
                if "API" in message:
                    analysis["api_calls"] += 1
                    
                    if "api_request" in context:
                        url = context["api_request"].get("url", "")
                        if url:
                            api_name = self._extract_api_name(url)
                            if api_name not in analysis["apis_used"]:
                                analysis["apis_used"].append(api_name)
                        
                        status = context["api_request"].get("response_status", 0)
                        if status >= 200 and status < 300:
                            analysis["successful_calls"] += 1
                        else:
                            analysis["failed_calls"] += 1
                
                elif "APIエラー" in message or "API失敗" in message:
                    analysis["failed_calls"] += 1
                    analysis["errors"].append(message)
            
            # 成功率計算
            if analysis["api_calls"] > 0:
                analysis["success_rate"] = analysis["successful_calls"] / analysis["api_calls"]
            else:
                analysis["success_rate"] = 0.0
            
        except Exception as e:
            analysis["analysis_error"] = str(e)
        
        return analysis
    
    def _analyze_errors(self, debug_logs: List[Dict]) -> Dict[str, Any]:
        """エラー分析"""
        analysis = {
            "total_errors": 0,
            "error_types": {},
            "critical_errors": [],
            "error_timeline": []
        }
        
        try:
            for log_entry in debug_logs:
                if not isinstance(log_entry, dict):
                    continue
                
                level = log_entry.get("level", "")
                message = log_entry.get("message", "")
                timestamp = log_entry.get("timestamp", "")
                
                if level in ["ERROR", "CRITICAL"]:
                    analysis["total_errors"] += 1
                    
                    # エラータイプ分類
                    error_type = self._classify_error(message)
                    analysis["error_types"][error_type] = analysis["error_types"].get(error_type, 0) + 1
                    
                    # クリティカルエラー記録
                    if level == "CRITICAL":
                        analysis["critical_errors"].append({
                            "timestamp": timestamp,
                            "message": message
                        })
                    
                    # エラータイムライン
                    analysis["error_timeline"].append({
                        "timestamp": timestamp,
                        "level": level,
                        "message": message
                    })
            
        except Exception as e:
            analysis["analysis_error"] = str(e)
        
        return analysis
    
    def _extract_api_name(self, url: str) -> str:
        """URL からAPI名を抽出"""
        if "duckduckgo" in url:
            return "DuckDuckGo"
        elif "openai" in url:
            return "OpenAI"
        elif "api" in url:
            return "External API"
        else:
            return "Unknown API"
    
    def _classify_error(self, message: str) -> str:
        """エラーメッセージの分類"""
        if "Web検索" in message:
            return "web_search_error"
        elif "API" in message:
            return "api_error"
        elif "前処理" in message:
            return "preprocessing_error"
        elif "セッション" in message:
            return "session_error"
        else:
            return "unknown_error"
    
    def analyze_latest_session(self) -> Optional[AnalysisResult]:
        """最新セッションの分析"""
        try:
            # 最新のセッションファイルを取得
            session_files = list(self.sessions_dir.glob("*.json"))
            if not session_files:
                print("❌ セッションファイルが見つかりません")
                return None
            
            # 最新ファイルを取得
            latest_file = max(session_files, key=lambda f: f.stat().st_mtime)
            session_id = latest_file.stem
            
            print(f"📊 最新セッション分析: {session_id}")
            return self.analyze_session(session_id)
            
        except Exception as e:
            self.logger.error("最新セッション分析エラー", exception=e)
            return None
    
    def list_available_sessions(self) -> List[str]:
        """利用可能セッション一覧取得"""
        try:
            session_files = list(self.sessions_dir.glob("*.json"))
            session_ids = [f.stem for f in session_files]
            
            # 更新日時順でソート
            session_ids.sort(key=lambda sid: max(
                f.stat().st_mtime for f in session_files if f.stem == sid
            ), reverse=True)
            
            return session_ids
            
        except Exception as e:
            self.logger.error("セッション一覧取得エラー", exception=e)
            return []
    
    def print_analysis_result(self, result: AnalysisResult):
        """分析結果を表示"""
        print(f"\n{'='*70}")
        print(f"📊 セッション分析結果: {result.session_id}")
        print(f"{'='*70}")
        
        print(f"ステータス: {result.status}")
        
        # 問題点
        if result.issues:
            print(f"\n🚨 検出された問題 ({len(result.issues)}件):")
            for i, issue in enumerate(result.issues, 1):
                print(f"  {i}. {issue}")
        else:
            print("\n✅ 問題は検出されませんでした")
        
        # 推奨事項
        if result.recommendations:
            print(f"\n💡 推奨事項 ({len(result.recommendations)}件):")
            for i, rec in enumerate(result.recommendations, 1):
                print(f"  {i}. {rec}")
        
        # パフォーマンス指標
        if result.performance_metrics:
            print(f"\n📈 パフォーマンス指標:")
            metrics = result.performance_metrics
            
            print(f"  セッション状態: {metrics.get('session_status', 'unknown')}")
            print(f"  収集アイテム: {metrics.get('collected_items', 0)}件")
            print(f"  処理アイテム: {metrics.get('processed_items', 0)}件")
            print(f"  総コスト: ${metrics.get('current_cost', 0):.2f}")
            
            if 'total_duration' in metrics:
                print(f"  実行時間: {metrics['total_duration']:.1f}秒")
                print(f"  収集効率: {metrics.get('items_per_second', 0):.2f}件/秒")
            
            if 'filtering_efficiency' in metrics:
                print(f"  フィルタリング効率: {metrics['filtering_efficiency']:.1%}")
            
            if 'error_rate' in metrics:
                print(f"  エラー率: {metrics['error_rate']:.1%}")
        
        # 詳細分析
        if result.detailed_analysis:
            print(f"\n🔍 詳細分析:")
            
            # Web検索分析
            web_search = result.detailed_analysis.get("web_search", {})
            if web_search:
                print(f"  Web検索:")
                print(f"    実行回数: {web_search.get('total_searches', 0)}")
                print(f"    成功回数: {web_search.get('successful_searches', 0)}")
                print(f"    成功率: {web_search.get('success_rate', 0):.1%}")
                print(f"    平均結果数: {web_search.get('average_results_per_search', 0):.1f}")
            
            # セッションフェーズ分析
            phases = result.detailed_analysis.get("session_phases", {})
            if phases.get("phases"):
                print(f"  セッションフェーズ:")
                for phase in phases["phases"]:
                    status = phases["phase_status"].get(phase, "unknown")
                    duration = phases["phase_durations"].get(phase, 0)
                    print(f"    {phase}: {status} ({duration:.1f}秒)")
            
            # API使用分析
            api_usage = result.detailed_analysis.get("api_usage", {})
            if api_usage.get("apis_used"):
                print(f"  API使用:")
                print(f"    使用API: {', '.join(api_usage['apis_used'])}")
                print(f"    API呼び出し: {api_usage.get('api_calls', 0)}")
                print(f"    成功率: {api_usage.get('success_rate', 0):.1%}")
        
        print(f"\n{'='*70}")

def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(description="セッションデバッグ分析ツール")
    parser.add_argument("--session-id", "-s", help="分析対象セッションID")
    parser.add_argument("--latest", "-l", action="store_true", help="最新セッションを分析")
    parser.add_argument("--list", "-ls", action="store_true", help="利用可能セッション一覧表示")
    
    args = parser.parse_args()
    
    try:
        analyzer = DebugSessionAnalyzer()
        
        if args.list:
            # セッション一覧表示
            sessions = analyzer.list_available_sessions()
            print(f"\n📋 利用可能セッション ({len(sessions)}件):")
            for i, session_id in enumerate(sessions, 1):
                print(f"  {i}. {session_id}")
            return
        
        if args.latest:
            # 最新セッション分析
            result = analyzer.analyze_latest_session()
        elif args.session_id:
            # 指定セッション分析
            result = analyzer.analyze_session(args.session_id)
        else:
            # 対話モード
            sessions = analyzer.list_available_sessions()
            if not sessions:
                print("❌ 利用可能なセッションがありません")
                return
            
            print(f"\n📋 利用可能セッション ({len(sessions)}件):")
            for i, session_id in enumerate(sessions, 1):
                print(f"  {i}. {session_id}")
            
            try:
                choice = input("\n分析するセッション番号を入力してください (Enter=最新): ").strip()
                if not choice:
                    result = analyzer.analyze_latest_session()
                else:
                    index = int(choice) - 1
                    if 0 <= index < len(sessions):
                        result = analyzer.analyze_session(sessions[index])
                    else:
                        print("❌ 無効な番号です")
                        return
            except KeyboardInterrupt:
                print("\n\n👋 分析を中断しました")
                return
            except ValueError:
                print("❌ 無効な入力です")
                return
        
        if result:
            analyzer.print_analysis_result(result)
        else:
            print("❌ 分析を実行できませんでした")
            
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
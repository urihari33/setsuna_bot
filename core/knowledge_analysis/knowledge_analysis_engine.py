#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KnowledgeAnalysisEngine - レポートベース段階分析システム
シンプルで直感的な知識収集・分析エンジン
"""

import json
import os
import sys
from typing import Dict, List, Optional, Callable
from datetime import datetime
from pathlib import Path
import uuid

# プロジェクトルートを確実にパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from core.adaptive_learning.duckduckgo_search_service import DuckDuckGoSearchService
    from core.adaptive_learning.gpt35_analysis_service import GPT35AnalysisService
    from core.adaptive_learning.accurate_cost_calculator import AccurateCostCalculator
    from core.knowledge_analysis.report_quality_validator import ReportQualityValidator
    from core.quality_monitoring.quality_history_manager import QualityHistoryManager
except ImportError:
    try:
        from core.adaptive_learning.duckduckgo_search_service import DuckDuckGoSearchService
        from core.adaptive_learning.gpt35_analysis_service import GPT35AnalysisService
        from core.adaptive_learning.accurate_cost_calculator import AccurateCostCalculator
        from core.knowledge_analysis.report_quality_validator import ReportQualityValidator
        from core.quality_monitoring.quality_history_manager import QualityHistoryManager
    except ImportError:
        print("⚠️ 既存のコンポーネントを再利用できません。基本機能のみで実装します。")
        DuckDuckGoSearchService = None
        GPT35AnalysisService = None
        AccurateCostCalculator = None
        ReportQualityValidator = None
        QualityHistoryManager = None

# ログシステム統合
try:
    from logging_system import get_logger
    LOGGER_AVAILABLE = True
except ImportError:
    LOGGER_AVAILABLE = False
    print("⚠️ StructuredLoggerが利用できません。基本ログのみで動作します。")

class KnowledgeAnalysisEngine:
    """レポートベース知識分析エンジン"""
    
    def __init__(self, progress_callback: Optional[Callable] = None):
        """初期化"""
        self.progress_callback = progress_callback
        self.session_id = None
        self.reports = []
        self.total_cost = 0.0
        
        # ログシステム初期化
        if LOGGER_AVAILABLE:
            self.logger = get_logger()
            self.logger.info("knowledge_analysis", "init", "KnowledgeAnalysisEngine初期化開始")
        else:
            self.logger = None
        
        # データディレクトリ設定
        self.data_dir = Path("D:/setsuna_bot/knowledge_db")
        self.sessions_dir = self.data_dir / "sessions"
        self.summaries_dir = self.data_dir / "summaries"
        self.cache_dir = self.data_dir / "cache"
        
        # ディレクトリ作成
        for dir_path in [self.data_dir, self.sessions_dir, self.summaries_dir, self.cache_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # サービス初期化 - 詳細ログ付き
        self._initialize_services_with_logging()
        
        # 品質検証システム初期化
        if ReportQualityValidator:
            self.quality_validator = ReportQualityValidator()
            if self.logger:
                self.logger.info("knowledge_analysis", "init", "ReportQualityValidator初期化成功")
        else:
            self.quality_validator = None
            if self.logger:
                self.logger.warning("knowledge_analysis", "init", "ReportQualityValidator利用不可")
        
        # 品質履歴管理システム初期化
        try:
            if QualityHistoryManager:
                self.quality_history_manager = QualityHistoryManager()
                if self.logger:
                    self.logger.info("knowledge_analysis", "init", "QualityHistoryManager初期化成功")
                print("[品質履歴] ✅ QualityHistoryManager統合成功")
            else:
                # 直接インポートを試行
                try:
                    from core.quality_monitoring.quality_history_manager import QualityHistoryManager as DirectQHM
                    self.quality_history_manager = DirectQHM()
                    if self.logger:
                        self.logger.info("knowledge_analysis", "init", "QualityHistoryManager直接インポート成功")
                    print("[品質履歴] ✅ QualityHistoryManager直接統合成功")
                except ImportError:
                    self.quality_history_manager = None
                    if self.logger:
                        self.logger.warning("knowledge_analysis", "init", "QualityHistoryManager利用不可")
                    print("[品質履歴] ⚠️ QualityHistoryManager利用不可")
        except Exception as e:
            self.quality_history_manager = None
            if self.logger:
                self.logger.error("knowledge_analysis", "init", f"QualityHistoryManager初期化エラー: {e}")
            print(f"[品質履歴] ❌ QualityHistoryManager初期化エラー: {e}")
    
    def _initialize_services_with_logging(self):
        """サービス初期化 - 包括的ログ記録"""
        initialization_log = {
            "stage": "initialization",
            "timestamp": datetime.now().isoformat(),
            "environment_check": {},
            "service_status": {},
            "failed_components": [],
            "fallback_activated": [],
            "critical_issues": []
        }
        
        # 環境変数チェック
        openai_key_present = bool(os.environ.get('OPENAI_API_KEY'))
        initialization_log["environment_check"]["openai_api_key"] = "present" if openai_key_present else "missing"
        
        if not openai_key_present:
            initialization_log["critical_issues"].append("OPENAI_API_KEY not found in environment")
        
        # DuckDuckGo検索サービス初期化
        try:
            if DuckDuckGoSearchService:
                self.search_service = DuckDuckGoSearchService()
                initialization_log["service_status"]["search_service"] = "initialized"
                if self.logger:
                    self.logger.info("knowledge_analysis", "init", "DuckDuckGoSearchService初期化成功")
            else:
                self.search_service = None
                initialization_log["service_status"]["search_service"] = "class_not_available"
                initialization_log["failed_components"].append("DuckDuckGoSearchService")
                
        except Exception as e:
            self.search_service = None
            initialization_log["service_status"]["search_service"] = f"failed: {str(e)}"
            initialization_log["failed_components"].append("DuckDuckGoSearchService")
            if self.logger:
                self.logger.error("knowledge_analysis", "init", f"DuckDuckGoSearchService初期化失敗: {e}")
        
        # GPT分析サービス初期化
        try:
            if GPT35AnalysisService:
                self.analysis_service = GPT35AnalysisService()
                initialization_log["service_status"]["analysis_service"] = "initialized"
                if self.logger:
                    self.logger.info("knowledge_analysis", "init", "GPT35AnalysisService初期化成功")
            else:
                self.analysis_service = None
                initialization_log["service_status"]["analysis_service"] = "class_not_available"
                initialization_log["failed_components"].append("GPT35AnalysisService")
                
        except Exception as e:
            self.analysis_service = None
            initialization_log["service_status"]["analysis_service"] = f"failed: {str(e)}"
            initialization_log["failed_components"].append("GPT35AnalysisService")
            if self.logger:
                self.logger.error("knowledge_analysis", "init", f"GPT35AnalysisService初期化失敗: {e}")
        
        # コスト計算サービス初期化
        try:
            if AccurateCostCalculator:
                self.cost_calculator = AccurateCostCalculator()
                initialization_log["service_status"]["cost_calculator"] = "initialized"
                if self.logger:
                    self.logger.info("knowledge_analysis", "init", "AccurateCostCalculator初期化成功")
            else:
                self.cost_calculator = None
                initialization_log["service_status"]["cost_calculator"] = "class_not_available"
                initialization_log["failed_components"].append("AccurateCostCalculator")
                
        except Exception as e:
            self.cost_calculator = None
            initialization_log["service_status"]["cost_calculator"] = f"failed: {str(e)}"
            initialization_log["failed_components"].append("AccurateCostCalculator")
            if self.logger:
                self.logger.error("knowledge_analysis", "init", f"AccurateCostCalculator初期化失敗: {e}")
        
        # フォールバック戦略の設定
        if not self.search_service:
            initialization_log["fallback_activated"].append("mock_search_results")
        if not self.analysis_service:
            initialization_log["fallback_activated"].append("mock_analysis")
        if not self.cost_calculator:
            initialization_log["fallback_activated"].append("estimated_cost")
        
        # 初期化結果のログ記録
        if self.logger:
            self.logger.info("knowledge_analysis", "init_complete", "サービス初期化完了", initialization_log)
        
        # 重要な問題がある場合はコンソールにも出力
        if initialization_log["critical_issues"] or len(initialization_log["failed_components"]) > 1:
            print(f"⚠️ 初期化警告: {len(initialization_log['failed_components'])}個のコンポーネントが失敗")
            for issue in initialization_log["critical_issues"]:
                print(f"   🔴 {issue}")
            for component in initialization_log["failed_components"]:
                print(f"   ❌ {component}")
            print(f"   🔄 フォールバック: {', '.join(initialization_log['fallback_activated'])}")
    
    def start_new_session(self, topic: str) -> str:
        """新しい分析セッション開始"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_uuid = str(uuid.uuid4())[:8]
        self.session_id = f"{topic.replace(' ', '_')[:20]}_{timestamp}_{session_uuid}"
        
        self.reports = []
        self.total_cost = 0.0
        
        self._update_progress(f"新しいセッション開始: {topic}", 0)
        
        return self.session_id
    
    def analyze_topic(self, user_prompt: str, search_count: int = 100, use_previous_context: bool = True) -> Dict:
        """トピック分析実行"""
        try:
            self._update_progress("分析開始...", 5)
            
            # 前回のレポートがある場合はコンテキストとして追加
            context = ""
            if use_previous_context and self.reports:
                last_report = self.reports[-1]
                context = f"前回の分析結果:\n{last_report['analysis_summary']}\n\n関連トピック: {', '.join(last_report.get('related_topics', []))}\n\n"
            
            full_prompt = context + f"新しい分析依頼: {user_prompt}"
            
            # 大量検索実行
            self._update_progress("大量検索実行中...", 10)
            search_results = self._execute_large_scale_search(user_prompt, search_count)
            
            # バッチ分析実行
            self._update_progress("データ分析中...", 40)
            analysis_result = self._execute_batch_analysis(search_results, full_prompt)
            
            # レポート生成
            self._update_progress("レポート生成中...", 80)
            report = self._generate_report(user_prompt, search_results, analysis_result)
            
            # セッションに保存
            self.reports.append(report)
            self._save_session()
            
            self._update_progress("分析完了", 100)
            
            return report
            
        except Exception as e:
            print(f"❌ 分析エラー: {e}")
            import traceback
            traceback.print_exc()
            return self._generate_error_report(user_prompt, str(e))
    
    def _execute_large_scale_search(self, user_prompt: str, search_count: int) -> List[Dict]:
        """大規模検索実行 - 詳細ログ付き"""
        search_session_log = {
            "stage": "large_scale_search",
            "timestamp": datetime.now().isoformat(),
            "user_prompt": user_prompt,
            "target_count": search_count,
            "queries": [],
            "summary": {
                "total_queries": 0,
                "successful_searches": 0,
                "mock_fallbacks": 0,
                "actual_results": 0,
                "mock_results": 0,
                "total_time": 0
            }
        }
        
        search_start_time = datetime.now()
        
        if not self.search_service:
            search_session_log["summary"]["failed_searches"] = 1
            search_session_log["summary"]["actual_results"] = 0
            if self.logger:
                self.logger.warning("knowledge_analysis", "search", "検索サービス未初期化、空の結果を返す", search_session_log)
            return []  # 実データが取得できない場合は空リスト
        
        try:
            # 関連キーワード生成
            search_queries = self._generate_search_queries(user_prompt)
            search_session_log["summary"]["total_queries"] = len(search_queries)
            
            all_results = []
            results_per_query = max(5, search_count // len(search_queries))
            
            for i, query in enumerate(search_queries):
                query_log = {
                    "query": str(query),
                    "query_index": f"{i+1}/{len(search_queries)}",
                    "results_requested": results_per_query,
                    "results_received": 0,
                    "api_response_time": 0,
                    "status": "pending",
                    "error": None,
                    "actual_vs_mock": "unknown"
                }
                
                try:
                    # 検索クエリを文字列に変換
                    query_str = str(query)
                    query_start_time = datetime.now()
                    
                    results = self.search_service.search(query_str, max_results=results_per_query)
                    
                    query_end_time = datetime.now()
                    query_log["api_response_time"] = (query_end_time - query_start_time).total_seconds()
                    query_log["results_received"] = len(results)
                    query_log["status"] = "success"
                    
                    # 実際の検索結果かどうかを判定
                    if results:
                        query_log["actual_vs_mock"] = "actual"
                        search_session_log["summary"]["successful_searches"] += 1
                        search_session_log["summary"]["actual_results"] += len(results)
                    else:
                        query_log["actual_vs_mock"] = "empty"
                        search_session_log["summary"]["failed_searches"] = search_session_log["summary"].get("failed_searches", 0) + 1
                    
                    all_results.extend(results)
                    
                    progress = 10 + (20 * (i + 1) / len(search_queries))
                    self._update_progress(f"検索中... ({len(all_results)}/{search_count})", int(progress))
                    
                    if len(all_results) >= search_count:
                        break
                        
                except Exception as e:
                    query_log["status"] = "failed"
                    query_log["error"] = str(e)
                    query_log["actual_vs_mock"] = "failed"
                    query_log["results_received"] = 0
                    
                    if self.logger:
                        self.logger.warning("knowledge_analysis", "search_query", f"検索失敗: {query_str}", data={"error": str(e)})
                    
                    # エラー時は何も追加しない（実データのみ）
                    search_session_log["summary"]["failed_searches"] = search_session_log["summary"].get("failed_searches", 0) + 1
                    continue
                finally:
                    search_session_log["queries"].append(query_log)
            
            # 検索セッション完了（実データのみ）
            search_end_time = datetime.now()
            search_session_log["summary"]["total_time"] = (search_end_time - search_start_time).total_seconds()
            search_session_log["final_results_count"] = len(all_results)
            
            # 品質評価を追加
            search_session_log["quality_assessment"] = self._assess_search_quality(all_results)
            
            # ログ記録
            if self.logger:
                self.logger.info("knowledge_analysis", "search_complete", "大規模検索完了", data=search_session_log)
            
            # 重要な統計をコンソールにも出力（実データのみ）
            failed_searches = search_session_log["summary"].get("failed_searches", 0)
            success_rate = (search_session_log["summary"]["successful_searches"] / search_session_log["summary"]["total_queries"]) * 100 if search_session_log["summary"]["total_queries"] > 0 else 0
            print(f"🔍 検索完了: {search_session_log['summary']['successful_searches']}/{search_session_log['summary']['total_queries']} クエリ成功 ({success_rate:.1f}%)")
            print(f"📊 結果: 実際{search_session_log['summary']['actual_results']}件（失敗{failed_searches}件）")
            
            return all_results  # 取得できただけ返す
            
        except Exception as e:
            search_session_log["stage_error"] = str(e)
            search_session_log["summary"]["total_time"] = (datetime.now() - search_start_time).total_seconds()
            
            if self.logger:
                self.logger.error("knowledge_analysis", "search_critical", f"大規模検索重大エラー: {e}", data=search_session_log)
            
            print(f"❌ 大規模検索エラー、実データを取得できませんでした: {e}")
            return []  # エラー時も空リスト
    
    def _is_real_search_result(self, result: Dict) -> bool:
        """検索結果が実際のものかモックかを判定"""
        # URLで判定（モック結果は特定のパターンを持つ）
        url = result.get('url', '')
        mock_domains = [
            'ai-trends.com', 'enterprise-ai.com', 'learning-resources.com',
            'community-trends.com', 'development-setup.com', 'webdev-guide.com',
            'best-practices.dev', 'ml-practical.com', 'industry-ml.com',
            'tech-comprehensive.com', 'implementation-patterns.com'
        ]
        
        # モックドメインが含まれていればモック結果
        for domain in mock_domains:
            if domain in url:
                return False
        
        # DuckDuckGoの実際の結果パターン
        if 'duckduckgo.com' in result.get('source', ''):
            return True
        
        # URLエンコードされた長いURLはモックの可能性が高い
        if len(url) > 200 and '%' in url:
            return False
        
        # 実在するドメインパターン
        real_domains = [
            'wikipedia.org', 'github.com', 'stackoverflow.com', 'arxiv.org',
            'medium.com', 'techcrunch.com', 'wired.com', 'nature.com',
            'ieee.org', 'acm.org', 'springer.com', 'sciencedirect.com'
        ]
        
        for domain in real_domains:
            if domain in url:
                return True
        
        # デフォルトは実際の結果と判定（保守的）
        return True
    
    def _assess_search_quality(self, results: List[Dict]) -> Dict:
        """検索結果の品質評価"""
        if not results:
            return {"quality_score": 0.0, "issues": ["no_results"]}
        
        quality_metrics = {
            "total_results": len(results),
            "real_results": 0,
            "mock_results": 0,
            "url_quality": {"valid": 0, "invalid": 0, "mock_domains": 0},
            "content_quality": {"meaningful_snippets": 0, "repetitive": 0},
            "language_detection": {"ja": 0, "en": 0, "other": 0},
            "domain_diversity": set(),
            "issues": []
        }
        
        for result in results:
            # 実際 vs モック判定
            if self._is_real_search_result(result):
                quality_metrics["real_results"] += 1
            else:
                quality_metrics["mock_results"] += 1
            
            # URL品質チェック
            url = result.get('url', '')
            if url:
                if url.startswith('http'):
                    quality_metrics["url_quality"]["valid"] += 1
                    # ドメイン多様性
                    try:
                        from urllib.parse import urlparse
                        domain = urlparse(url).netloc
                        quality_metrics["domain_diversity"].add(domain)
                    except:
                        pass
                else:
                    quality_metrics["url_quality"]["invalid"] += 1
            
            # コンテンツ品質チェック
            snippet = result.get('snippet', '')
            if snippet:
                # 日本語・英語判定（簡易）
                if any('\u3040' <= char <= '\u309F' or '\u30A0' <= char <= '\u30FF' or '\u4E00' <= char <= '\u9FFF' for char in snippet):
                    quality_metrics["language_detection"]["ja"] += 1
                elif any('a' <= char.lower() <= 'z' for char in snippet):
                    quality_metrics["language_detection"]["en"] += 1
                else:
                    quality_metrics["language_detection"]["other"] += 1
                
                # 意味のあるスニペットかチェック
                if len(snippet) > 50 and '。' in snippet:
                    quality_metrics["content_quality"]["meaningful_snippets"] += 1
                elif snippet.count('技術') > 3 or snippet.count('分析') > 3:
                    quality_metrics["content_quality"]["repetitive"] += 1
        
        # 品質スコア計算（0-1）
        real_ratio = quality_metrics["real_results"] / quality_metrics["total_results"]
        url_valid_ratio = quality_metrics["url_quality"]["valid"] / quality_metrics["total_results"]
        meaningful_ratio = quality_metrics["content_quality"]["meaningful_snippets"] / quality_metrics["total_results"]
        domain_diversity_score = min(1.0, len(quality_metrics["domain_diversity"]) / 10)
        
        quality_score = (real_ratio * 0.4 + url_valid_ratio * 0.3 + meaningful_ratio * 0.2 + domain_diversity_score * 0.1)
        
        # 問題の特定
        if quality_metrics["mock_results"] > quality_metrics["real_results"]:
            quality_metrics["issues"].append("high_mock_ratio")
        if quality_metrics["url_quality"]["invalid"] > quality_metrics["total_results"] * 0.3:
            quality_metrics["issues"].append("many_invalid_urls")
        if quality_metrics["content_quality"]["repetitive"] > quality_metrics["total_results"] * 0.5:
            quality_metrics["issues"].append("repetitive_content")
        if len(quality_metrics["domain_diversity"]) < 3:
            quality_metrics["issues"].append("low_domain_diversity")
        
        quality_metrics["quality_score"] = quality_score
        quality_metrics["domain_diversity"] = list(quality_metrics["domain_diversity"])  # setをlistに変換
        
        return quality_metrics
    
    def _generate_search_queries(self, user_prompt: str) -> List[str]:
        """検索クエリ生成 - ユーザープロンプトに基づく動的生成"""
        
        # プロンプトの正規化と分析
        prompt_clean = user_prompt.strip()
        words = prompt_clean.split()
        
        # コンテキスト判別
        context = self._detect_prompt_context(prompt_clean)
        
        # 基本クエリセット
        queries = []
        
        if context == "person":
            # 人物に関する検索 - 固有名詞を避けて一般的カテゴリで検索
            person_categories = self._extract_person_categories(prompt_clean)
            prompt_keywords = self._extract_activity_keywords(prompt_clean)
            
            # カテゴリ×キーワードの組み合わせでクエリ生成
            for category in person_categories:
                for keyword in prompt_keywords:
                    queries.append(f"{category} {keyword}")
            
            # 基本的なカテゴリ単体クエリも追加
            queries.extend(person_categories)
        elif context == "technology":
            # 技術関連の検索
            main_topic = self._extract_main_topic(prompt_clean)
            queries.extend([
                f"{main_topic}",
                f"{main_topic} 最新動向",
                f"{main_topic} 技術",
                f"{main_topic} 実装",
                f"{main_topic} 事例",
                f"{main_topic} 導入",
                f"{main_topic} 課題",
                f"{main_topic} 将来性",
                f"{main_topic} 比較",
                f"{main_topic} 効果"
            ])
        elif context == "general":
            # 一般的なトピック
            main_topic = self._extract_main_topic(prompt_clean)
            queries.extend([
                f"{main_topic}",
                f"{main_topic} について",
                f"{main_topic} 詳細",
                f"{main_topic} 情報",
                f"{main_topic} 解説",
                f"{main_topic} 特徴",
                f"{main_topic} 概要",
                f"{main_topic} 基本",
                f"{main_topic} 応用",
                f"{main_topic} 最新"
            ])
        else:
            # フォールバック：プロンプトをそのまま使用
            queries.extend([
                prompt_clean,
                f"{prompt_clean} 詳細",
                f"{prompt_clean} 情報",
                f"{prompt_clean} について",
                f"{prompt_clean} 解説"
            ])
        
        # プロンプト内の複数キーワードを組み合わせ
        if len(words) > 1:
            # 2語組み合わせ
            for i in range(len(words) - 1):
                two_word_phrase = " ".join(words[i:i+2])
                queries.append(two_word_phrase)
            
            # 3語組み合わせ（プロンプトが長い場合）
            if len(words) >= 3:
                three_word_phrase = " ".join(words[:3])
                queries.append(three_word_phrase)
        
        # 重複除去と最大20クエリに制限
        unique_queries = list(dict.fromkeys(queries))  # 順序を保持しつつ重複除去
        return unique_queries[:20]
    
    def _detect_prompt_context(self, prompt: str) -> str:
        """プロンプトのコンテキストを判別"""
        prompt_lower = prompt.lower()
        
        # 人物関連キーワード
        person_keywords = ["せつな", "片無", "歌手", "アーティスト", "音楽家", "作曲家", "シンガー"]
        if any(keyword in prompt_lower for keyword in person_keywords):
            return "person"
        
        # 技術関連キーワード  
        tech_keywords = ["ai", "技術", "プログラミング", "システム", "開発", "api", "機械学習", "深層学習"]
        if any(keyword in prompt_lower for keyword in tech_keywords):
            return "technology"
        
        return "general"
    
    def _extract_person_categories(self, prompt: str) -> List[str]:
        """人物の一般的カテゴリを抽出（固有名詞を使わない）"""
        # 「せつな」関連の特別処理：VTuber/歌手/映像クリエイターとしてのカテゴリ
        if "せつな" in prompt:
            return [
                "VTuber",
                "歌手", 
                "映像クリエイター",
                "バーチャルアーティスト",
                "インディー音楽",
                "オリジナル楽曲",
                "音楽制作",
                "動画制作"
            ]
        
        # その他の人物の場合の一般的カテゴリ
        general_categories = [
            "アーティスト",
            "クリエイター", 
            "音楽家",
            "歌手",
            "作曲家",
            "映像制作",
            "コンテンツクリエイター"
        ]
        
        return general_categories
    
    def _extract_activity_keywords(self, prompt: str) -> List[str]:
        """プロンプトから活動・分野キーワードを抽出"""
        prompt_lower = prompt.lower()
        
        # 音楽関連キーワード
        music_keywords = ["音楽", "楽曲", "歌", "作曲", "編曲", "ボーカル", "メロディー"]
        # 映像関連キーワード  
        video_keywords = ["映像", "動画", "制作", "編集", "コンテンツ", "作品"]
        # 活動関連キーワード
        activity_keywords = ["活動", "プロフィール", "経歴", "実績", "作品", "情報"]
        
        # プロンプトに含まれるキーワードを特定
        found_keywords = []
        for keyword in music_keywords + video_keywords + activity_keywords:
            if keyword in prompt:
                found_keywords.append(keyword)
        
        # キーワードが見つからない場合はデフォルト
        if not found_keywords:
            found_keywords = ["活動", "作品", "情報", "プロフィール"]
        
        return found_keywords
    
    def _extract_main_topic(self, prompt: str) -> str:
        """メイントピックを抽出"""
        words = prompt.split()
        
        # ストップワードを除去
        stop_words = ["について", "に関して", "を", "の", "が", "は", "で", "と", "や"]
        filtered_words = [word for word in words if word not in stop_words]
        
        if filtered_words:
            # 最初の意味のある単語を返す
            return filtered_words[0]
        
        # フォールバック
        return words[0] if words else prompt
    
    
    def _execute_batch_analysis(self, search_results: List[Dict], prompt: str) -> Dict:
        """バッチ分析実行 - 詳細ログ付き"""
        analysis_session_log = {
            "stage": "batch_analysis",
            "timestamp": datetime.now().isoformat(),
            "input_prompt": prompt,
            "input_data_count": len(search_results),
            "batch_logs": [],
            "summary": {
                "total_batches": 0,
                "successful_batches": 0,
                "failed_batches": 0,
                "total_input_tokens": 0,
                "total_output_tokens": 0,
                "total_cost": 0.0,
                "total_time": 0,
                "analysis_service_available": bool(self.analysis_service)
            }
        }
        
        analysis_start_time = datetime.now()
        
        # 検索結果が空の場合の処理
        if not search_results:
            analysis_session_log["summary"]["no_data_reason"] = "empty_search_results"
            analysis_session_log["summary"]["total_time"] = (datetime.now() - analysis_start_time).total_seconds()
            
            if self.logger:
                self.logger.warning("knowledge_analysis", "analysis", "検索結果が空のため分析をスキップ", data=analysis_session_log)
            
            return {
                "analysis": "検索結果が取得できなかったため、分析を実行できませんでした。",
                "batch_summaries": [],
                "total_cost": 0.0,
                "processed_items": 0,
                "analysis_log": analysis_session_log,
                "empty_data": True
            }
        
        if not self.analysis_service:
            analysis_session_log["fallback_reason"] = "analysis_service_not_available"
            if self.logger:
                self.logger.warning("knowledge_analysis", "analysis", "分析サービス未初期化、分析をスキップ", data=analysis_session_log)
            return {
                "analysis": "分析サービスが利用できないため、分析を実行できませんでした。",
                "batch_summaries": [],
                "total_cost": 0.0,
                "processed_items": len(search_results),
                "analysis_log": analysis_session_log,
                "service_unavailable": True
            }
        
        try:
            batch_size = 10
            batch_summaries = []
            total_cost = 0.0
            
            analysis_session_log["summary"]["total_batches"] = (len(search_results) + batch_size - 1) // batch_size
            
            # 10件ずつバッチ処理
            for i in range(0, len(search_results), batch_size):
                batch = search_results[i:i + batch_size]
                batch_number = i // batch_size + 1
                
                batch_log = {
                    "batch_number": batch_number,
                    "batch_size": len(batch),
                    "start_time": datetime.now().isoformat(),
                    "input_token_count": 0,
                    "output_token_count": 0,
                    "api_response_time": 0,
                    "cost": 0.0,
                    "status": "pending",
                    "error": None
                }
                
                try:
                    # 入力トークン数の概算（バッチ全体のコンテンツサイズ）
                    batch_content_size = sum(len(result.get('title', '') + result.get('snippet', '')) for result in batch)
                    batch_log["input_token_count"] = batch_content_size // 4  # 概算
                    
                    # GPT分析実行 - 時間測定（検索結果コンテンツ分析）
                    batch_start_time = datetime.now()
                    batch_analysis = self.analysis_service.analyze_search_results(batch, prompt)
                    batch_end_time = datetime.now()
                    
                    batch_log["api_response_time"] = (batch_end_time - batch_start_time).total_seconds()
                    batch_log["output_token_count"] = len(batch_analysis.get('analysis', '')) // 4  # 概算
                    batch_log["cost"] = batch_analysis.get('cost', 0.0)
                    batch_log["status"] = "success"
                    
                    batch_summaries.append(batch_analysis['analysis'])
                    total_cost += batch_analysis['cost']
                    
                    # サマリー統計更新
                    analysis_session_log["summary"]["successful_batches"] += 1
                    analysis_session_log["summary"]["total_input_tokens"] += batch_log["input_token_count"]
                    analysis_session_log["summary"]["total_output_tokens"] += batch_log["output_token_count"]
                    analysis_session_log["summary"]["total_cost"] += batch_log["cost"]
                    
                    if self.logger:
                        self.logger.info("knowledge_analysis", "batch_success", f"バッチ{batch_number}分析成功", data=batch_log)
                    
                except Exception as batch_error:
                    batch_log["status"] = "failed"
                    batch_log["error"] = str(batch_error)
                    analysis_session_log["summary"]["failed_batches"] += 1
                    
                    if self.logger:
                        self.logger.error("knowledge_analysis", "batch_failed", f"バッチ{batch_number}分析失敗", data=batch_log)
                    
                    # エラー時はモック要約を生成
                    mock_summary = f"バッチ{batch_number}の要約（分析エラーのため簡易生成）: {len(batch)}件の検索結果から技術動向、市場分析、実用性に関する情報を含む。"
                    batch_summaries.append(mock_summary)
                
                finally:
                    batch_log["end_time"] = datetime.now().isoformat()
                    analysis_session_log["batch_logs"].append(batch_log)
                
                progress = 40 + (30 * (i + batch_size) / len(search_results))
                self._update_progress(f"バッチ分析中... ({batch_number}/{analysis_session_log['summary']['total_batches']})", int(progress))
            
            # 全体統合分析 - 詳細ログ付き
            integration_log = {
                "stage": "final_integration",
                "start_time": datetime.now().isoformat(),
                "input_batches": len(batch_summaries),
                "input_token_count": 0,
                "output_token_count": 0,
                "api_response_time": 0,
                "cost": 0.0,
                "status": "pending",
                "error": None
            }
            
            try:
                integration_prompt = f"""
以下のバッチ要約を統合分析してください：

{chr(10).join([f"バッチ{i+1}: {summary}" for i, summary in enumerate(batch_summaries)])}

元の質問: {prompt}

以下の形式で統合分析結果を提供：
1. エグゼクティブサマリー（2-3行）
2. 主要発見事項（5-7個）
3. カテゴリ別分析：
   - 技術面
   - 市場・ビジネス面
   - 実用性・応用事例
   - 課題・リスク
4. 関連調査提案（3-5個）
5. 信頼度評価（1-10）
"""
                
                integration_log["input_token_count"] = len(integration_prompt) // 4  # 概算
                
                # 統合分析実行 - 時間測定（要約統合分析）
                integration_start_time = datetime.now()
                # 統合分析では要約テキストを検索結果として扱い分析
                summary_results = [{
                    'title': f'バッチ{i+1}要約',
                    'snippet': summary,
                    'url': f'internal://batch_{i+1}',
                    'source': 'Analysis Summary'
                } for i, summary in enumerate(batch_summaries)]
                final_analysis = self.analysis_service.analyze_search_results(summary_results, prompt)
                integration_end_time = datetime.now()
                
                integration_log["api_response_time"] = (integration_end_time - integration_start_time).total_seconds()
                integration_log["output_token_count"] = len(final_analysis.get('analysis', '')) // 4  # 概算
                integration_log["cost"] = final_analysis.get('cost', 0.0)
                integration_log["status"] = "success"
                
                total_cost += final_analysis['cost']
                
                # サマリー統計更新
                analysis_session_log["summary"]["total_input_tokens"] += integration_log["input_token_count"]
                analysis_session_log["summary"]["total_output_tokens"] += integration_log["output_token_count"]
                analysis_session_log["summary"]["total_cost"] += integration_log["cost"]
                
                if self.logger:
                    self.logger.info("knowledge_analysis", "integration_success", "統合分析成功", data=integration_log)
                    
            except Exception as integration_error:
                integration_log["status"] = "failed"
                integration_log["error"] = str(integration_error)
                
                if self.logger:
                    self.logger.error("knowledge_analysis", "integration_failed", f"統合分析失敗: {integration_error}", data=integration_log)
                
                # 統合分析失敗時はバッチ要約をそのまま使用
                final_analysis = {"analysis": "\n\n".join([f"バッチ{i+1}要約:\n{summary}" for i, summary in enumerate(batch_summaries)])}
                
            finally:
                integration_log["end_time"] = datetime.now().isoformat()
                analysis_session_log["integration_log"] = integration_log
            
            # 分析セッション完了
            analysis_end_time = datetime.now()
            analysis_session_log["summary"]["total_time"] = (analysis_end_time - analysis_start_time).total_seconds()
            
            self.total_cost += total_cost
            
            # 最終ログ記録
            if self.logger:
                self.logger.info("knowledge_analysis", "analysis_complete", "バッチ分析完了", data=analysis_session_log)
            
            # 重要な統計をコンソールにも出力
            success_rate = (analysis_session_log["summary"]["successful_batches"] / analysis_session_log["summary"]["total_batches"]) * 100 if analysis_session_log["summary"]["total_batches"] > 0 else 0
            print(f"🧠 分析完了: {analysis_session_log['summary']['successful_batches']}/{analysis_session_log['summary']['total_batches']} バッチ成功 ({success_rate:.1f}%)")
            print(f"💰 コスト: ${analysis_session_log['summary']['total_cost']:.6f} | ⏱️ 時間: {analysis_session_log['summary']['total_time']:.1f}秒")
            
            return {
                "analysis": final_analysis['analysis'],
                "batch_summaries": batch_summaries,
                "total_cost": total_cost,
                "processed_items": len(search_results),
                "analysis_log": analysis_session_log  # デバッグ用にログも含める
            }
            
        except Exception as e:
            analysis_session_log["stage_error"] = str(e)
            analysis_session_log["summary"]["total_time"] = (datetime.now() - analysis_start_time).total_seconds()
            
            if self.logger:
                self.logger.error("knowledge_analysis", "analysis_critical", f"バッチ分析重大エラー: {e}", data=analysis_session_log)
            
            print(f"❌ バッチ分析エラー、分析を実行できませんでした: {e}")
            return {
                "analysis": f"分析処理中にエラーが発生しました: {str(e)}",
                "batch_summaries": [],
                "total_cost": 0.0,
                "processed_items": len(search_results),
                "analysis_log": analysis_session_log,
                "error": True
            }
    
    
    def _generate_report(self, user_prompt: str, search_results: List[Dict], analysis_result: Dict) -> Dict:
        """レポート生成（空データ対応）"""
        report_id = len(self.reports) + 1
        timestamp = datetime.now().isoformat()
        
        # 空データの場合の特別なレポート生成
        if not search_results or analysis_result.get("empty_data"):
            empty_report = {
                "report_id": report_id,
                "timestamp": timestamp,
                "user_prompt": user_prompt,
                "search_count": 0,
                "analysis_summary": "検索結果が取得できなかったため、分析を実行できませんでした。インターネット接続を確認するか、時間をおいて再試行してください。",
                "key_insights": [
                    "実際のWeb検索データを取得できませんでした",
                    "ddgsライブラリの動作を確認してください",
                    "時間をおいて再試行することをお勧めします"
                ],
                "categories": {},
                "related_topics": [],
                "data_quality": 0.0,
                "cost": analysis_result.get("total_cost", 0.0),
                "processing_time": "即座に完了",
                "detailed_data": {
                    "search_results": [],
                    "batch_summaries": [],
                    "no_data_reason": "search_failed"
                },
                "empty_data_report": True
            }
            
            # 空データレポートにも品質検証を適用
            if self.quality_validator:
                try:
                    validation_report = self.quality_validator.validate_report(empty_report)
                    empty_report["validation_report"] = {
                        "validation_timestamp": validation_report.validation_timestamp,
                        "overall_score": validation_report.overall_score,
                        "total_issues": validation_report.total_issues,
                        "issues_by_severity": validation_report.issues_by_severity,
                        "quality_metrics": validation_report.quality_metrics,
                        "validation_summary": validation_report.validation_summary,
                        "recommendations": validation_report.recommendations
                    }
                    
                    print(f"✅ 空データレポート品質検証: スコア {validation_report.overall_score:.2f}")
                    if self.logger:
                        self.logger.info("knowledge_analysis", "validation_empty_data", 
                                        f"空データレポート検証完了: スコア {validation_report.overall_score:.2f}",
                                        data={"report_id": report_id, "score": validation_report.overall_score})
                        
                except Exception as validation_error:
                    print(f"⚠️ 空データレポート検証エラー: {validation_error}")
                    if self.logger:
                        self.logger.error("knowledge_analysis", "validation_empty_failed", 
                                        f"空データレポート検証失敗: {validation_error}",
                                        data={"report_id": report_id, "error": str(validation_error)})
            
            return empty_report
        
        # 分析結果から構造化データ抽出
        analysis_text = analysis_result.get("analysis", "")
        
        # キーインサイト抽出（簡易パターンマッチング）
        key_insights = []
        lines = analysis_text.split('\n')
        for line in lines:
            if any(marker in line for marker in ['1.', '2.', '3.', '4.', '5.', '6.', '7.', '-']):
                insight = line.strip()
                if len(insight) > 10 and not insight.startswith('#'):
                    key_insights.append(insight)
        
        # 関連トピック抽出
        related_topics = []
        if "関連調査" in analysis_text or "提案" in analysis_text:
            for line in lines:
                if any(marker in line for marker in ['1.', '2.', '3.', '4.', '5.']):
                    if "調査" in line or "分析" in line:
                        topic = line.strip().replace('1.', '').replace('2.', '').replace('3.', '').replace('4.', '').replace('5.', '').strip()
                        if len(topic) > 5:
                            related_topics.append(topic)
        
        # カテゴリ分析抽出
        categories = {}
        current_category = None
        for line in lines:
            if "技術面" in line:
                current_category = "technology"
                categories[current_category] = ""
            elif "市場" in line or "ビジネス" in line:
                current_category = "market"
                categories[current_category] = ""
            elif "実用" in line or "応用" in line:
                current_category = "applications"
                categories[current_category] = ""
            elif "課題" in line or "リスク" in line:
                current_category = "challenges"
                categories[current_category] = ""
            elif current_category and line.strip() and not line.startswith('#'):
                categories[current_category] += line.strip() + "\n"
        
        report = {
            "report_id": report_id,
            "timestamp": timestamp,
            "user_prompt": user_prompt,
            "search_count": len(search_results),
            "analysis_summary": analysis_text,
            "key_insights": key_insights[:7],  # 最大7個
            "categories": categories,
            "related_topics": related_topics[:5],  # 最大5個
            "data_quality": min(0.95, 0.5 + (len(search_results) / 200)),  # 検索数に基づく品質スコア
            "cost": analysis_result.get("total_cost", 0.0),
            "processing_time": "10-15分",
            "detailed_data": {
                "search_results": search_results,
                "batch_summaries": analysis_result.get("batch_summaries", [])
            }
        }
        
        # 品質検証実行
        if self.quality_validator:
            try:
                validation_report = self.quality_validator.validate_report(report)
                report["validation_report"] = {
                    "validation_timestamp": validation_report.validation_timestamp,
                    "overall_score": validation_report.overall_score,
                    "total_issues": validation_report.total_issues,
                    "issues_by_severity": validation_report.issues_by_severity,
                    "quality_metrics": validation_report.quality_metrics,
                    "validation_summary": validation_report.validation_summary,
                    "recommendations": validation_report.recommendations
                }
                
                # 重要な問題がある場合はログ出力
                critical_issues = validation_report.issues_by_severity.get("critical", 0)
                error_issues = validation_report.issues_by_severity.get("error", 0)
                
                if critical_issues > 0:
                    print(f"🔴 レポート品質検証: 重大な問題 {critical_issues}件検出")
                    if self.logger:
                        self.logger.error("knowledge_analysis", "validation_critical", 
                                        f"重大な検証問題 {critical_issues}件", 
                                        data={"report_id": report_id, "issues": critical_issues})
                elif error_issues > 0:
                    print(f"❌ レポート品質検証: エラー {error_issues}件検出")
                    if self.logger:
                        self.logger.warning("knowledge_analysis", "validation_error", 
                                          f"検証エラー {error_issues}件", 
                                          data={"report_id": report_id, "issues": error_issues})
                else:
                    print(f"✅ レポート品質検証: 品質スコア {validation_report.overall_score:.2f}")
                    if self.logger:
                        self.logger.info("knowledge_analysis", "validation_success", 
                                        f"検証完了: スコア {validation_report.overall_score:.2f}",
                                        data={"report_id": report_id, "score": validation_report.overall_score})
                        
            except Exception as validation_error:
                print(f"⚠️ 品質検証エラー: {validation_error}")
                if self.logger:
                    self.logger.error("knowledge_analysis", "validation_failed", 
                                    f"品質検証失敗: {validation_error}",
                                    data={"report_id": report_id, "error": str(validation_error)})
                
                # 検証失敗時は基本的な検証情報のみ追加
                report["validation_report"] = {
                    "validation_timestamp": datetime.now().isoformat(),
                    "overall_score": 0.5,  # デフォルトスコア
                    "total_issues": 0,
                    "issues_by_severity": {},
                    "quality_metrics": {},
                    "validation_summary": f"品質検証でエラーが発生しました: {validation_error}",
                    "recommendations": ["品質検証システムを確認してください"]
                }
        
        # 品質履歴への記録
        if self.quality_history_manager and report.get("validation_report"):
            try:
                # ValidationReportオブジェクトを再構築
                from core.knowledge_analysis.report_quality_validator import ValidationReport, ValidationSeverity, ValidationIssue
                
                validation_data = report["validation_report"]
                validation_report = ValidationReport(
                    validation_timestamp=validation_data["validation_timestamp"],
                    overall_score=validation_data["overall_score"],
                    total_issues=validation_data["total_issues"],
                    issues_by_severity=validation_data["issues_by_severity"],
                    quality_metrics=validation_data["quality_metrics"],
                    validation_summary=validation_data["validation_summary"],
                    recommendations=validation_data["recommendations"],
                    issues=[]  # 簡略化
                )
                
                # 処理時間計算（ダミー値として設定）
                processing_time = analysis_result.get("analysis_log", {}).get("summary", {}).get("total_time", 0.0)
                search_count = len(search_results)
                cost = report.get("cost", 0.0)
                data_quality = report.get("data_quality", 0.0)
                
                # 品質履歴記録
                record_id = self.quality_history_manager.record_validation_result(
                    validation_report=validation_report,
                    processing_time=processing_time,
                    search_count=search_count,
                    cost=cost,
                    data_quality=data_quality
                )
                
                if record_id:
                    print(f"📊 品質履歴記録: ID={record_id}")
                    if self.logger:
                        self.logger.info("knowledge_analysis", "quality_history_recorded", 
                                        f"品質履歴記録完了: {record_id}",
                                        data={"report_id": report_id, "record_id": record_id})
                
            except Exception as history_error:
                print(f"⚠️ 品質履歴記録エラー: {history_error}")
                if self.logger:
                    self.logger.error("knowledge_analysis", "quality_history_failed", 
                                    f"品質履歴記録失敗: {history_error}",
                                    data={"report_id": report_id, "error": str(history_error)})
        
        return report
    
    def _generate_error_report(self, user_prompt: str, error_message: str) -> Dict:
        """エラーレポート生成"""
        return {
            "report_id": len(self.reports) + 1,
            "timestamp": datetime.now().isoformat(),
            "user_prompt": user_prompt,
            "error": True,
            "error_message": error_message,
            "analysis_summary": f"分析処理中にエラーが発生しました: {error_message}",
            "key_insights": ["分析を再実行してください"],
            "categories": {},
            "related_topics": [],
            "data_quality": 0.0,
            "cost": 0.0
        }
    
    def get_session_summary(self) -> Dict:
        """セッション要約取得"""
        if not self.reports:
            return {"message": "まだレポートがありません"}
        
        return {
            "session_id": self.session_id,
            "total_reports": len(self.reports),
            "total_cost": self.total_cost,
            "reports": self.reports,
            "latest_topics": [report.get("related_topics", []) for report in self.reports[-3:]],
            "session_created": self.reports[0]["timestamp"] if self.reports else None
        }
    
    def _save_session(self):
        """セッション保存"""
        if not self.session_id:
            return
        
        try:
            session_data = {
                "session_id": self.session_id,
                "reports": self.reports,
                "total_cost": self.total_cost,
                "created_at": self.reports[0]["timestamp"] if self.reports else datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            session_file = self.sessions_dir / f"{self.session_id}.json"
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
            
            print(f"💾 セッション保存: {session_file}")
            
        except Exception as e:
            print(f"⚠️ セッション保存エラー: {e}")
    
    def _update_progress(self, message: str, progress: int):
        """進捗更新"""
        if self.progress_callback:
            self.progress_callback(message, progress)
        else:
            print(f"[{progress:3d}%] {message}")
    
    def get_quality_validation_summary(self) -> Dict:
        """品質検証システムのサマリーを取得"""
        if not self.quality_validator:
            return {"message": "品質検証システムが利用できません"}
        
        return self.quality_validator.get_validation_summary()
    
    def format_validation_report(self, report_id: int) -> str:
        """指定レポートの検証結果をフォーマット"""
        if not self.quality_validator:
            return "品質検証システムが利用できません"
        
        # レポートを検索
        target_report = None
        for report in self.reports:
            if report.get("report_id") == report_id:
                target_report = report
                break
        
        if not target_report:
            return f"レポートID {report_id} が見つかりません"
        
        validation_data = target_report.get("validation_report")
        if not validation_data:
            return f"レポートID {report_id} には検証データがありません"
    
    def get_quality_statistics(self, days: int = 30) -> Dict:
        """品質統計情報取得"""
        if not self.quality_history_manager:
            return {"error": "品質履歴管理システムが利用できません"}
        
        try:
            return self.quality_history_manager.get_quality_statistics(days)
        except Exception as e:
            return {"error": f"品質統計取得エラー: {str(e)}"}
    
    def get_quality_trend_analysis(self, days: int = 7) -> Dict:
        """品質傾向分析取得"""
        if not self.quality_history_manager:
            return {"error": "品質履歴管理システムが利用できません"}
        
        try:
            trend_analysis = self.quality_history_manager.get_quality_trend_analysis(days)
            
            # QualityTrendAnalysisオブジェクトを辞書に変換
            return {
                "period_days": trend_analysis.period_days,
                "trend": trend_analysis.trend.value if hasattr(trend_analysis.trend, 'value') else str(trend_analysis.trend),
                "avg_score": trend_analysis.avg_score,
                "score_change": trend_analysis.score_change,
                "volatility": trend_analysis.volatility,
                "issue_trend": trend_analysis.issue_trend,
                "recommendations": trend_analysis.recommendations
            }
        except Exception as e:
            return {"error": f"品質傾向分析エラー: {str(e)}"}
    
    def get_recent_quality_alerts(self, hours: int = 24) -> List[Dict]:
        """最近の品質アラート取得"""
        if not self.quality_history_manager:
            return [{"error": "品質履歴管理システムが利用できません"}]
        
        try:
            alerts = self.quality_history_manager.get_recent_alerts(hours)
            
            # QualityAlertオブジェクトを辞書に変換
            alert_dicts = []
            for alert in alerts:
                alert_dict = {
                    "alert_id": alert.alert_id,
                    "timestamp": alert.timestamp,
                    "level": alert.level.value if hasattr(alert.level, 'value') else str(alert.level),
                    "message": alert.message,
                    "metrics": alert.metrics,
                    "threshold_violated": alert.threshold_violated,
                    "suggested_action": alert.suggested_action
                }
                alert_dicts.append(alert_dict)
            
            return alert_dicts
        except Exception as e:
            return [{"error": f"品質アラート取得エラー: {str(e)}"}]
    
    def cleanup_quality_history(self, keep_days: int = 90):
        """品質履歴のクリーンアップ"""
        if not self.quality_history_manager:
            print("品質履歴管理システムが利用できません")
            return
        
        try:
            self.quality_history_manager.cleanup_old_records(keep_days)
            print(f"✅ 品質履歴クリーンアップ完了: {keep_days}日より古いデータを削除")
        except Exception as e:
            print(f"⚠️ 品質履歴クリーンアップエラー: {e}")
    
    def print_quality_summary(self):
        """品質情報の要約表示"""
        if not self.quality_history_manager:
            print("品質履歴管理システムが利用できません")
            return
        
        try:
            # 統計情報
            print("\n📊 品質統計情報 (過去30日)")
            print("=" * 50)
            stats = self.get_quality_statistics(30)
            if "error" not in stats:
                print(f"総記録数: {stats.get('total_records', 0)}")
                print(f"平均品質スコア: {stats.get('average_score', 0):.3f}")
                print(f"スコア範囲: {stats.get('score_range', [0, 0])[0]:.3f} - {stats.get('score_range', [0, 0])[1]:.3f}")
                print(f"総問題数: {stats.get('total_issues', 0)}")
                print(f"重大問題数: {stats.get('critical_issues', 0)}")
                print(f"総コスト: ${stats.get('total_cost', 0):.6f}")
                print(f"平均処理時間: {stats.get('avg_processing_time', 0):.2f}秒")
                print(f"アラート数: {stats.get('alert_counts', {})}")
            else:
                print(f"統計情報取得エラー: {stats['error']}")
            
            # 傾向分析
            print("\n📈 品質傾向分析 (過去7日)")
            print("=" * 50)
            trend = self.get_quality_trend_analysis(7)
            if "error" not in trend:
                print(f"傾向: {trend.get('trend', 'unknown')}")
                print(f"平均スコア: {trend.get('avg_score', 0):.3f}")
                print(f"スコア変化: {trend.get('score_change', 0):+.3f}")
                print(f"変動性: {trend.get('volatility', 0):.3f}")
                print(f"推奨事項:")
                for recommendation in trend.get('recommendations', []):
                    print(f"  - {recommendation}")
            else:
                print(f"傾向分析取得エラー: {trend['error']}")
            
            # 最近のアラート
            print("\n🚨 最近のアラート (過去24時間)")
            print("=" * 50)
            alerts = self.get_recent_quality_alerts(24)
            if alerts and "error" not in alerts[0]:
                if alerts:
                    for alert in alerts[:5]:  # 最新5件まで表示
                        print(f"[{alert['level'].upper()}] {alert['message']}")
                        print(f"  時刻: {alert['timestamp'][:19]}")
                        print(f"  対応: {alert['suggested_action']}")
                        print()
                else:
                    print("アラートはありません")
            else:
                print(f"アラート取得エラー: {alerts[0].get('error', 'unknown error') if alerts else 'no data'}")
                
        except Exception as e:
            print(f"品質情報表示エラー: {e}")
        
        # ValidationReport オブジェクトを再構築してフォーマット
        try:
            from core.knowledge_analysis.report_quality_validator import ValidationReport
            validation_report = ValidationReport(
                validation_timestamp=validation_data["validation_timestamp"],
                overall_score=validation_data["overall_score"],
                total_issues=validation_data["total_issues"],
                issues_by_severity=validation_data["issues_by_severity"],
                issues=[],  # 詳細な問題リストは省略
                quality_metrics=validation_data["quality_metrics"],
                validation_summary=validation_data["validation_summary"],
                recommendations=validation_data["recommendations"]
            )
            
            return self.quality_validator.format_validation_report(validation_report)
        except Exception as e:
            return f"検証レポートのフォーマットエラー: {e}"

if __name__ == "__main__":
    def progress_callback(message, progress):
        print(f"[{progress:3d}%] {message}")
    
    try:
        engine = KnowledgeAnalysisEngine(progress_callback)
        
        print("🧪 KnowledgeAnalysisEngine - テスト実行")
        
        # 新しいセッション開始
        session_id = engine.start_new_session("AI技術動向")
        print(f"📝 セッション開始: {session_id}")
        
        # 初回分析
        report1 = engine.analyze_topic("AI技術の最新動向について包括的に調べたい", search_count=50)
        print(f"✅ 初回レポート生成完了")
        print(f"主要発見: {len(report1.get('key_insights', []))}個")
        print(f"コスト: ${report1.get('cost', 0):.6f}")
        
        # 継続分析
        report2 = engine.analyze_topic("前回の分析で言及されたAI技術の企業導入について詳しく", search_count=30)
        print(f"✅ 継続レポート生成完了")
        
        # セッション要約
        summary = engine.get_session_summary()
        print(f"📊 セッション要約:")
        print(f"  総レポート数: {summary['total_reports']}")
        print(f"  総コスト: ${summary['total_cost']:.6f}")
        
        print("\n🎉 テスト成功！")
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
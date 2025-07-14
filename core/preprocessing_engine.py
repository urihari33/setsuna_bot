#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PreProcessingEngine - GPT-3.5による効率的な前処理・フィルタリング
"""

import json
import os
import openai
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import hashlib
import time
from datetime import datetime
from .config_manager import get_config_manager

@dataclass
class PreProcessingResult:
    """前処理結果データクラス"""
    source_id: str
    content_hash: str
    relevance_score: float  # 0.0-1.0
    quality_score: float   # 0.0-1.0
    importance_score: float # 0.0-1.0
    category: str          # "技術", "市場", "トレンド", "実用", "その他", "無関係"
    key_topics: List[str]
    confidence: float      # 判定の信頼度
    processing_time: float
    should_proceed: bool   # 詳細分析に進むべきか
    reason: str           # 判定理由
    gpt_tokens_used: int

class PreProcessingEngine:
    """GPT-3.5による前処理エンジン"""
    
    def __init__(self):
        """初期化"""
        # OpenAI設定
        self.openai_client = None
        self._initialize_openai()
        
        # GPT-3.5設定
        self.gpt35_config = {
            "model": "gpt-3.5-turbo",
            "temperature": 0.1,  # 一貫性重視
            "max_tokens": 300,   # 簡潔な分析
            "timeout": 30
        }
        
        # Rate Limiting対策設定
        self.rate_limiting = {
            "request_interval": 2.0,    # API呼び出し間隔（秒）
            "batch_size": 5,            # バッチサイズ制限
            "max_retries": 3,           # 最大リトライ回数
            "backoff_factor": 2.0       # 指数バックオフ係数
        }
        
        # フィルタリング閾値
        self.thresholds = {
            "relevance_min": 0.3,     # 関連性最小値
            "quality_min": 0.4,       # 品質最小値
            "importance_min": 0.2,    # 重要度最小値
            "confidence_min": 0.6,    # 信頼度最小値
            "combined_min": 0.5       # 総合スコア最小値
        }
        
        # キャッシュ設定
        self.enable_cache = True
        self.cache_duration_hours = 24
        self._cache = {}
        
        # 統計情報
        self.stats = {
            "total_processed": 0,
            "filtered_out": 0,
            "cache_hits": 0,
            "total_tokens_used": 0,
            "total_cost": 0.0,
            "average_processing_time": 0.0
        }
        
        print("[前処理] ✅ PreProcessingEngine初期化完了")
    
    def _initialize_openai(self):
        """OpenAI API初期化"""
        try:
            # ConfigManager経由でOpenAI設定取得
            config = get_config_manager()
            openai_key = config.get_openai_key()
            
            if openai_key:
                openai.api_key = openai_key
                self.openai_client = openai
                
                # 接続テスト実行
                try:
                    # 簡単な接続テスト
                    test_response = openai.models.list()
                    if test_response:
                        print("[前処理] ✅ OpenAI API設定・接続確認完了")
                        return True
                except Exception as api_error:
                    print(f"[前処理] ❌ OpenAI API接続失敗: {api_error}")
                    self.openai_client = None
                    return False
            else:
                print("[前処理] ⚠️ OpenAI APIキーが設定されていません")
                print("  .envファイルまたは環境変数 OPENAI_API_KEY を設定してください")
                self.openai_client = None
                return False
                
        except Exception as e:
            print(f"[前処理] ❌ OpenAI API初期化失敗: {e}")
            self.openai_client = None
            return False
    
    def set_thresholds(self, **kwargs):
        """フィルタリング閾値設定"""
        for key, value in kwargs.items():
            if key in self.thresholds:
                self.thresholds[key] = value
                print(f"[前処理] ⚙️ 閾値更新: {key} = {value}")
    
    def preprocess_content_batch(self, 
                                sources: List[Dict[str, Any]], 
                                theme: str,
                                target_categories: List[str] = None,
                                safe_mode: bool = False) -> List[PreProcessingResult]:
        """
        コンテンツバッチ前処理（Rate Limiting対策強化版）
        
        Args:
            sources: ソースデータリスト
            theme: 学習テーマ
            target_categories: 対象カテゴリ
            safe_mode: 安全モード（より長い間隔で処理）
            
        Returns:
            前処理結果リスト
        """
        if not self.openai_client:
            print("[前処理] ⚠️ OpenAI APIが利用できません - フォールバック処理を実行")
            return self._fallback_batch_processing(sources, theme, target_categories)
        
        results = []
        batch_start_time = time.time()
        
        # Rate Limiting設定
        interval = self.rate_limiting["request_interval"] * (2 if safe_mode else 1)
        batch_size = min(self.rate_limiting["batch_size"], len(sources))
        
        print(f"[前処理] 🔍 バッチ前処理開始: {len(sources)}件")
        print(f"[前処理] ⚙️ Rate Limiting設定: 間隔{interval}秒, バッチサイズ{batch_size}")
        
        # バッチ単位で処理
        for i in range(0, len(sources), batch_size):
            batch_sources = sources[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (len(sources) + batch_size - 1) // batch_size
            
            print(f"[前処理] 📦 バッチ {batch_num}/{total_batches} 処理中...")
            
            for j, source in enumerate(batch_sources):
                try:
                    result = self._preprocess_single_content_with_retry(source, theme, target_categories)
                    if result:
                        results.append(result)
                        
                        # 統計更新
                        self.stats["total_processed"] += 1
                        if not result.should_proceed:
                            self.stats["filtered_out"] += 1
                    
                    # Rate Limiting対応（最後のアイテム以外）
                    if j < len(batch_sources) - 1 or i + batch_size < len(sources):
                        print(f"[前処理] ⏳ API制限回避のため {interval}秒待機...")
                        time.sleep(interval)
                        
                except Exception as e:
                    print(f"[前処理] ⚠️ 個別前処理失敗: {e}")
                    # フォールバック処理
                    fallback_result = self._fallback_single_processing(source, theme)
                    if fallback_result:
                        results.append(fallback_result)
                    continue
        
        # バッチ統計更新
        batch_time = time.time() - batch_start_time
        if self.stats["total_processed"] > 0:
            self.stats["average_processing_time"] = (
                (self.stats["average_processing_time"] * (self.stats["total_processed"] - len(results)) + batch_time) /
                self.stats["total_processed"]
            )
        
        # フィルタリング結果（ゼロ除算防止）
        passed_results = [r for r in results if r.should_proceed]
        
        print(f"[前処理] ✅ バッチ前処理完了:")
        print(f"  処理: {len(results)}件")
        print(f"  通過: {len(passed_results)}件")
        print(f"  除外: {len(results) - len(passed_results)}件")
        
        # 通過率計算（ゼロ除算防止）
        if len(results) > 0:
            pass_rate = len(passed_results) / len(results) * 100
            print(f"  通過率: {pass_rate:.1f}%")
        else:
            print(f"  通過率: 0.0% (処理結果なし)")
        
        return results
    
    def _preprocess_single_content_with_retry(self, 
                                            source: Dict[str, Any], 
                                            theme: str,
                                            target_categories: List[str] = None) -> Optional[PreProcessingResult]:
        """リトライ機能付き単一コンテンツ前処理"""
        max_retries = self.rate_limiting["max_retries"]
        backoff_factor = self.rate_limiting["backoff_factor"]
        
        for attempt in range(max_retries + 1):
            try:
                result = self._preprocess_single_content(source, theme, target_categories)
                if result:
                    return result
                else:
                    # GPT分析失敗 → フォールバック
                    return self._fallback_single_processing(source, theme)
                    
            except Exception as e:
                if "429" in str(e) or "rate_limit" in str(e).lower():
                    # Rate Limiting エラー
                    if attempt < max_retries:
                        wait_time = backoff_factor ** attempt
                        print(f"[前処理] ⚠️ Rate Limit (試行{attempt+1}/{max_retries+1}) - {wait_time}秒後リトライ")
                        time.sleep(wait_time)
                        continue
                    else:
                        print(f"[前処理] ❌ Rate Limit最大リトライ数到達 - フォールバック処理")
                        return self._fallback_single_processing(source, theme)
                else:
                    # その他のエラー
                    print(f"[前処理] ❌ 処理エラー: {e}")
                    return self._fallback_single_processing(source, theme)
        
        return None
    
    def _preprocess_single_content(self, 
                                  source: Dict[str, Any], 
                                  theme: str,
                                  target_categories: List[str] = None) -> Optional[PreProcessingResult]:
        """単一コンテンツ前処理"""
        start_time = time.time()
        
        # コンテンツハッシュ生成
        content = source.get('content', '') + source.get('title', '')
        content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
        
        # キャッシュチェック
        if self.enable_cache and content_hash in self._cache:
            cache_result = self._cache[content_hash]
            if self._is_cache_valid(cache_result['timestamp']):
                self.stats["cache_hits"] += 1
                print(f"[前処理] 💾 キャッシュヒット: {content_hash}")
                return PreProcessingResult(**cache_result['result'])
        
        # GPT-3.5で前処理分析
        analysis_result = self._analyze_with_gpt35(source, theme, target_categories)
        
        if not analysis_result:
            return None
        
        # 前処理結果作成
        processing_time = time.time() - start_time
        
        result = PreProcessingResult(
            source_id=source.get('source_id', ''),
            content_hash=content_hash,
            relevance_score=analysis_result['relevance_score'],
            quality_score=analysis_result['quality_score'],
            importance_score=analysis_result['importance_score'],
            category=analysis_result['category'],
            key_topics=analysis_result['key_topics'],
            confidence=analysis_result['confidence'],
            processing_time=processing_time,
            should_proceed=self._should_proceed_to_detailed_analysis(analysis_result),
            reason=analysis_result['reason'],
            gpt_tokens_used=analysis_result['tokens_used']
        )
        
        # キャッシュ保存
        if self.enable_cache:
            self._cache[content_hash] = {
                'result': asdict(result),
                'timestamp': datetime.now().isoformat()
            }
        
        # 統計更新
        self.stats["total_tokens_used"] += result.gpt_tokens_used
        self.stats["total_cost"] += self._calculate_gpt35_cost(result.gpt_tokens_used)
        
        return result
    
    def _analyze_with_gpt35(self, 
                           source: Dict[str, Any], 
                           theme: str,
                           target_categories: List[str] = None) -> Optional[Dict]:
        """GPT-3.5による分析"""
        try:
            # プロンプト構築
            title = source.get('title', '')
            content = source.get('content', '')
            url = source.get('url', '')
            
            # コンテンツ長制限（GPT-3.5のトークン制限考慮）
            max_content_length = 2000
            if len(content) > max_content_length:
                content = content[:max_content_length] + "..."
            
            categories_text = "、".join(target_categories) if target_categories else "技術、市場、トレンド、実用"
            
            prompt = f"""
以下のコンテンツを「{theme}」に関する学習素材として評価してください。

【タイトル】{title}
【URL】{url}
【内容】{content}

以下の観点で0.0～1.0のスコアと判定理由を提供してください：

1. 関連性（テーマとの関連度）
2. 品質（情報の信頼性・具体性）  
3. 重要度（学習価値の高さ）
4. カテゴリ（{categories_text}、無関係）
5. キートピック（3個以内）
6. 信頼度（判定の確信度）

必ず以下のJSON形式で回答してください：
{{
  "relevance_score": 0.8,
  "quality_score": 0.7,
  "importance_score": 0.6,
  "category": "技術",
  "key_topics": ["AI", "音楽生成"],
  "confidence": 0.9,
  "reason": "判定理由の簡潔な説明"
}}
"""
            
            # GPT-3.5呼び出し
            response = self.openai_client.chat.completions.create(
                model=self.gpt35_config["model"],
                messages=[{"role": "user", "content": prompt}],
                temperature=self.gpt35_config["temperature"],
                max_tokens=self.gpt35_config["max_tokens"]
            )
            
            # レスポンス解析
            response_text = response.choices[0].message.content.strip()
            
            # トークン数計算
            tokens_used = response.usage.total_tokens if hasattr(response, 'usage') else len(prompt.split()) + len(response_text.split())
            
            # JSON解析
            try:
                # JSONブロックを抽出
                if "```json" in response_text:
                    json_start = response_text.find("```json") + 7
                    json_end = response_text.find("```", json_start)
                    json_text = response_text[json_start:json_end].strip()
                elif "{" in response_text and "}" in response_text:
                    json_start = response_text.find("{")
                    json_end = response_text.rfind("}") + 1
                    json_text = response_text[json_start:json_end]
                else:
                    raise ValueError("JSON形式が見つかりません")
                
                analysis_data = json.loads(json_text)
                
                # 必須フィールドチェック・デフォルト値設定
                result = {
                    "relevance_score": float(analysis_data.get("relevance_score", 0.0)),
                    "quality_score": float(analysis_data.get("quality_score", 0.0)),
                    "importance_score": float(analysis_data.get("importance_score", 0.0)),
                    "category": analysis_data.get("category", "その他"),
                    "key_topics": analysis_data.get("key_topics", []),
                    "confidence": float(analysis_data.get("confidence", 0.5)),
                    "reason": analysis_data.get("reason", "分析完了"),
                    "tokens_used": tokens_used
                }
                
                # スコア正規化
                for score_key in ["relevance_score", "quality_score", "importance_score", "confidence"]:
                    result[score_key] = max(0.0, min(1.0, result[score_key]))
                
                return result
                
            except (json.JSONDecodeError, ValueError) as e:
                print(f"[前処理] ⚠️ JSON解析失敗: {e}")
                print(f"レスポンス: {response_text[:200]}...")
                
                # フォールバック（簡易分析）
                return self._fallback_analysis(source, theme, tokens_used)
                
        except Exception as e:
            print(f"[前処理] ❌ GPT-3.5分析失敗: {e}")
            return None
    
    def _fallback_analysis(self, source: Dict[str, Any], theme: str, tokens_used: int = 100) -> Dict:
        """フォールバック分析（GPT失敗時）"""
        title = source.get('title', '').lower()
        content = source.get('content', '').lower()
        theme_lower = theme.lower()
        
        # 簡易関連性判定
        relevance_score = 0.0
        if theme_lower in title:
            relevance_score += 0.6
        if theme_lower in content:
            relevance_score += 0.3
        
        # 簡易品質判定
        quality_score = 0.5
        if len(content) > 200:
            quality_score += 0.2
        if source.get('source_type') == 'web_search':
            quality_score += 0.1
        
        return {
            "relevance_score": min(1.0, relevance_score),
            "quality_score": min(1.0, quality_score),
            "importance_score": 0.4,
            "category": "その他",
            "key_topics": [theme],
            "confidence": 0.3,
            "reason": "フォールバック分析",
            "tokens_used": tokens_used
        }
    
    def _should_proceed_to_detailed_analysis(self, analysis_result: Dict) -> bool:
        """詳細分析進行判定"""
        # 個別閾値チェック
        if analysis_result['relevance_score'] < self.thresholds['relevance_min']:
            return False
        
        if analysis_result['quality_score'] < self.thresholds['quality_min']:
            return False
        
        if analysis_result['importance_score'] < self.thresholds['importance_min']:
            return False
        
        if analysis_result['confidence'] < self.thresholds['confidence_min']:
            return False
        
        # 総合スコア計算
        combined_score = (
            analysis_result['relevance_score'] * 0.4 +
            analysis_result['quality_score'] * 0.3 +
            analysis_result['importance_score'] * 0.3
        )
        
        return combined_score >= self.thresholds['combined_min']
    
    def _is_cache_valid(self, timestamp: str) -> bool:
        """キャッシュ有効性チェック"""
        try:
            cache_time = datetime.fromisoformat(timestamp)
            age_hours = (datetime.now() - cache_time).total_seconds() / 3600
            return age_hours < self.cache_duration_hours
        except:
            return False
    
    def _calculate_gpt35_cost(self, tokens: int) -> float:
        """GPT-3.5コスト計算"""
        # GPT-3.5-turbo料金: $0.002/1K tokens (入出力共通)
        return tokens * 0.002 / 1000
    
    def get_filtering_summary(self, results: List[PreProcessingResult]) -> Dict[str, Any]:
        """フィルタリングサマリー取得（ゼロ除算防止版）"""
        if not results:
            return {
                "error": "結果データなし",
                "total_processed": 0,
                "passed_count": 0,
                "filtered_count": 0,
                "pass_rate": 0.0
            }
        
        passed = [r for r in results if r.should_proceed]
        filtered = [r for r in results if not r.should_proceed]
        
        # カテゴリ別統計
        category_stats = {}
        for result in results:
            category = result.category
            if category not in category_stats:
                category_stats[category] = {"total": 0, "passed": 0}
            category_stats[category]["total"] += 1
            if result.should_proceed:
                category_stats[category]["passed"] += 1
        
        # スコア統計（ゼロ除算防止）
        relevance_scores = [r.relevance_score for r in results]
        quality_scores = [r.quality_score for r in results]
        importance_scores = [r.importance_score for r in results]
        
        # 安全な平均計算
        def safe_average(scores: List[float]) -> float:
            return sum(scores) / len(scores) if scores else 0.0
        
        summary = {
            "total_processed": len(results),
            "passed_count": len(passed),
            "filtered_count": len(filtered),
            "pass_rate": (len(passed) / len(results) * 100) if results else 0.0,
            "category_breakdown": category_stats,
            "score_averages": {
                "relevance": safe_average(relevance_scores),
                "quality": safe_average(quality_scores),
                "importance": safe_average(importance_scores)
            },
            "total_tokens_used": sum(r.gpt_tokens_used for r in results),
            "estimated_cost": sum(self._calculate_gpt35_cost(r.gpt_tokens_used) for r in results),
            "average_processing_time": safe_average([r.processing_time for r in results])
        }
        
        return summary
    
    def get_passed_sources(self, results: List[PreProcessingResult]) -> List[str]:
        """通過したソースIDリスト取得"""
        return [r.source_id for r in results if r.should_proceed]
    
    def _fallback_batch_processing(self, sources: List[Dict[str, Any]], theme: str, target_categories: List[str] = None) -> List[PreProcessingResult]:
        """OpenAI失敗時のフォールバックバッチ処理"""
        print("[前処理] 🔄 フォールバックバッチ処理開始")
        results = []
        
        for source in sources:
            try:
                result = self._fallback_single_processing(source, theme)
                if result:
                    results.append(result)
                    self.stats["total_processed"] += 1
                    if not result.should_proceed:
                        self.stats["filtered_out"] += 1
            except Exception as e:
                print(f"[前処理] ⚠️ フォールバック処理失敗: {e}")
                continue
        
        passed_results = [r for r in results if r.should_proceed]
        print(f"[前処理] ✅ フォールバックバッチ処理完了: {len(passed_results)}/{len(results)}件通過")
        
        return results
    
    def _fallback_single_processing(self, source: Dict[str, Any], theme: str) -> Optional[PreProcessingResult]:
        """OpenAI失敗時のフォールバック単一処理"""
        start_time = time.time()
        
        # 基本情報取得
        title = source.get('title', '')
        content = source.get('content', '')
        url = source.get('url', '')
        
        # コンテンツハッシュ生成
        content_hash = hashlib.sha256((content + title).encode()).hexdigest()[:16]
        
        # キーワードベース関連性分析
        relevance_score = self._calculate_keyword_relevance(title + " " + content, theme)
        
        # ドメイン・長さベース品質分析
        quality_score = self._calculate_basic_quality(source)
        
        # 統計的重要度分析
        importance_score = self._calculate_statistical_importance(title, content)
        
        # カテゴリ判定（シンプルなキーワードマッチング）
        category = self._determine_basic_category(title + " " + content)
        
        # キートピック抽出（単語頻度ベース）
        key_topics = self._extract_key_topics(title + " " + content, theme)
        
        # 信頼度（フォールバック処理なので低め）
        confidence = 0.4
        
        # 処理時間
        processing_time = time.time() - start_time
        
        # 進行判定
        combined_score = (relevance_score * 0.4 + quality_score * 0.3 + importance_score * 0.3)
        should_proceed = combined_score >= self.thresholds['combined_min']
        
        result = PreProcessingResult(
            source_id=source.get('source_id', content_hash),
            content_hash=content_hash,
            relevance_score=relevance_score,
            quality_score=quality_score,
            importance_score=importance_score,
            category=category,
            key_topics=key_topics,
            confidence=confidence,
            processing_time=processing_time,
            should_proceed=should_proceed,
            reason="フォールバック分析（基本的なキーワード・統計解析）",
            gpt_tokens_used=0
        )
        
        return result
    
    def _calculate_keyword_relevance(self, text: str, theme: str) -> float:
        """キーワードベース関連性計算"""
        if not text or not theme:
            return 0.0
        
        text_lower = text.lower()
        theme_lower = theme.lower()
        
        # テーマキーワードの直接マッチ
        theme_words = theme_lower.split()
        matches = sum(1 for word in theme_words if word in text_lower)
        direct_relevance = min(1.0, matches / len(theme_words))
        
        # 関連キーワード（簡易版）
        tech_keywords = ['技術', '開発', 'ai', '人工知能', 'プログラミング', 'システム']
        market_keywords = ['市場', 'ビジネス', '企業', '業界', '成長', '投資']
        trend_keywords = ['トレンド', '動向', '最新', '将来', '予測', '展望']
        
        all_keywords = tech_keywords + market_keywords + trend_keywords
        keyword_matches = sum(1 for keyword in all_keywords if keyword in text_lower)
        keyword_relevance = min(1.0, keyword_matches / 10)
        
        # 組み合わせ
        return min(1.0, direct_relevance * 0.7 + keyword_relevance * 0.3)
    
    def _calculate_basic_quality(self, source: Dict[str, Any]) -> float:
        """基本的な品質計算"""
        score = 0.3  # ベーススコア
        
        title = source.get('title', '')
        content = source.get('content', '')
        url = source.get('url', '')
        
        # タイトル品質
        if len(title) > 10:
            score += 0.1
        if len(title) > 30:
            score += 0.1
        
        # コンテンツ品質
        if len(content) > 100:
            score += 0.1
        if len(content) > 500:
            score += 0.2
        if len(content) > 1000:
            score += 0.1
        
        # URL品質（ドメイン判定）
        if url:
            trusted_domains = ['wikipedia.org', 'github.com', 'arxiv.org', 'ieee.org', '.edu', '.gov']
            if any(domain in url for domain in trusted_domains):
                score += 0.2
        
        return min(1.0, score)
    
    def _calculate_statistical_importance(self, title: str, content: str) -> float:
        """統計的重要度計算"""
        text = (title + " " + content).lower()
        
        # 重要指標キーワード
        important_keywords = [
            '重要', '主要', '注目', '画期的', '革新', '新しい', '最新',
            'important', 'key', 'major', 'significant', 'breakthrough'
        ]
        
        importance_matches = sum(1 for keyword in important_keywords if keyword in text)
        
        # 数値・データの存在
        import re
        numbers = len(re.findall(r'\d+', text))
        
        # 文章の構造性（句読点など）
        structure_score = min(1.0, text.count('。') / 10 + text.count('.') / 20)
        
        # 組み合わせ
        base_score = min(1.0, importance_matches / 5)
        data_score = min(1.0, numbers / 10)
        
        return min(1.0, base_score * 0.5 + data_score * 0.2 + structure_score * 0.3)
    
    def _determine_basic_category(self, text: str) -> str:
        """基本的なカテゴリ判定"""
        text_lower = text.lower()
        
        # カテゴリキーワード
        tech_keywords = ['技術', '開発', 'ai', '人工知能', 'プログラミング', 'システム', 'アルゴリズム']
        market_keywords = ['市場', 'ビジネス', '企業', '業界', '投資', '売上', '利益']
        trend_keywords = ['トレンド', '動向', '予測', '将来', '展望', 'forecast']
        practical_keywords = ['実用', '応用', '活用', '導入', '実装', '事例']
        
        tech_score = sum(1 for keyword in tech_keywords if keyword in text_lower)
        market_score = sum(1 for keyword in market_keywords if keyword in text_lower)
        trend_score = sum(1 for keyword in trend_keywords if keyword in text_lower)
        practical_score = sum(1 for keyword in practical_keywords if keyword in text_lower)
        
        scores = {
            '技術': tech_score,
            '市場': market_score,
            'トレンド': trend_score,
            '実用': practical_score
        }
        
        max_category = max(scores, key=scores.get)
        return max_category if scores[max_category] > 0 else 'その他'
    
    def _extract_key_topics(self, text: str, theme: str, max_topics: int = 3) -> List[str]:
        """キートピック抽出（単語頻度ベース）"""
        import re
        
        # 基本的な前処理
        text_clean = re.sub(r'[^\w\s]', ' ', text.lower())
        words = text_clean.split()
        
        # ストップワード除去（簡易版）
        stop_words = {
            'の', 'に', 'は', 'を', 'が', 'で', 'と', 'た', 'て', 'な', 'に', 'を', 'は',
            'a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with'
        }
        
        # 単語頻度計算
        word_freq = {}
        for word in words:
            if len(word) > 2 and word not in stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # テーマキーワード優先
        theme_words = theme.lower().split()
        for word in theme_words:
            if word in word_freq:
                word_freq[word] *= 2  # テーマ関連語を優先
        
        # 頻度順ソート
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        
        # トップN抽出
        key_topics = [word for word, freq in sorted_words[:max_topics]]
        
        return key_topics if key_topics else [theme]
    
    def get_top_quality_sources(self, results: List[PreProcessingResult], limit: int = 10) -> List[PreProcessingResult]:
        """高品質ソースのトップN取得"""
        passed_results = [r for r in results if r.should_proceed]
        
        # 総合スコアでソート
        scored_results = []
        for result in passed_results:
            combined_score = (
                result.relevance_score * 0.4 +
                result.quality_score * 0.3 +
                result.importance_score * 0.3
            )
            scored_results.append((combined_score, result))
        
        scored_results.sort(key=lambda x: x[0], reverse=True)
        
        return [result for _, result in scored_results[:limit]]
    
    def clear_cache(self):
        """キャッシュクリア"""
        self._cache.clear()
        print("[前処理] 🗑️ キャッシュクリア完了")
    
    def get_statistics(self) -> Dict[str, Any]:
        """統計情報取得"""
        return {
            **self.stats,
            "cache_size": len(self._cache),
            "filter_rate": (self.stats["filtered_out"] / self.stats["total_processed"] * 100) if self.stats["total_processed"] > 0 else 0,
            "cache_hit_rate": (self.stats["cache_hits"] / self.stats["total_processed"] * 100) if self.stats["total_processed"] > 0 else 0,
            "current_thresholds": self.thresholds
        }


# テスト用コード
if __name__ == "__main__":
    print("=== PreProcessingEngine テスト ===")
    
    engine = PreProcessingEngine()
    
    # テスト用ソースデータ
    test_sources = [
        {
            "source_id": "test_001",
            "title": "AI音楽生成の最新技術動向",
            "content": "Transformerアーキテクチャを使った音楽生成技術が急速に発展している。特にOpenAIのMuseNetやGoogleのMusicTransformerなどが注目されている。",
            "url": "https://example.com/ai-music-tech",
            "source_type": "web_search"
        },
        {
            "source_id": "test_002", 
            "title": "今日の天気予報",
            "content": "明日は全国的に晴れの予報です。気温は25度程度になる見込みです。",
            "url": "https://example.com/weather",
            "source_type": "news"
        },
        {
            "source_id": "test_003",
            "title": "音楽生成AIツールの比較分析",
            "content": "商用AI音楽生成ツールの機能比較。AIVA、Amper Music、Jukedeck等の特徴を詳細に分析。ユーザビリティと生成品質の観点から評価。",
            "url": "https://example.com/ai-tools-comparison",
            "source_type": "web_search"
        }
    ]
    
    # 前処理実行
    print("\n🔍 前処理テスト実行:")
    results = engine.preprocess_content_batch(
        sources=test_sources,
        theme="AI音楽生成技術",
        target_categories=["技術", "市場", "ツール"]
    )
    
    # 結果表示
    print(f"\n📊 前処理結果:")
    for result in results:
        status = "✅ 通過" if result.should_proceed else "❌ 除外"
        print(f"  {result.source_id}: {status}")
        print(f"    関連性: {result.relevance_score:.2f}, 品質: {result.quality_score:.2f}, 重要度: {result.importance_score:.2f}")
        print(f"    カテゴリ: {result.category}, 理由: {result.reason}")
    
    # サマリー表示
    print(f"\n📈 フィルタリングサマリー:")
    summary = engine.get_filtering_summary(results)
    print(f"  処理数: {summary['total_processed']}件")
    print(f"  通過数: {summary['passed_count']}件")
    print(f"  通過率: {summary['pass_rate']:.1f}%")
    print(f"  推定コスト: ${summary['estimated_cost']:.4f}")
    
    # 統計情報
    print(f"\n📊 エンジン統計:")
    stats = engine.get_statistics()
    print(f"  総処理数: {stats['total_processed']}")
    print(f"  フィルタ率: {stats['filter_rate']:.1f}%")
    print(f"  総コスト: ${stats['total_cost']:.4f}")
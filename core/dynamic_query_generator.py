#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DynamicQueryGenerator - GPT-4-turbo活用動的クエリ生成エンジン
学習テーマと条件に応じて最適化された検索クエリを動的に生成
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import openai
from .config_manager import get_config_manager
from .debug_logger import get_debug_logger

@dataclass
class QueryGenerationRequest:
    """クエリ生成リクエストデータ"""
    theme: str
    learning_type: str  # "概要", "深掘り", "実用"
    depth_level: int    # 1-5
    language_preference: str = "mixed"  # "japanese", "english", "mixed"
    target_engines: List[str] = None
    context_info: Optional[str] = None
    
    def __post_init__(self):
        if self.target_engines is None:
            self.target_engines = ["google", "duckduckgo"]

@dataclass
class GeneratedQuery:
    """生成されたクエリ情報"""
    query: str
    query_type: str     # "technical", "business", "practical", "trending", "academic"
    language: str       # "japanese", "english", "mixed"
    priority: float     # 0.0-1.0
    expected_quality: float  # 0.0-1.0
    target_engines: List[str]
    reasoning: str      # 生成理由

class DynamicQueryGenerator:
    """動的クエリ生成エンジンメインクラス"""
    
    def __init__(self):
        """初期化"""
        self.config_manager = get_config_manager()
        self.debug_logger = get_debug_logger(component="QUERY_GENERATOR")
        
        # OpenAI クライアント初期化
        self.openai_client = None
        self._initialize_openai()
        
        # GPT-4-turbo設定
        self.gpt_config = {
            "model": "gpt-4-turbo",
            "temperature": 0.7,
            "max_tokens": 1000,
            "presence_penalty": 0.1,
            "frequency_penalty": 0.1
        }
        
        # クエリ生成履歴
        self.generation_history = []
        
        # フォールバック用固定クエリテンプレート
        self.fallback_templates = {
            "概要": [
                "{theme} とは",
                "{theme} 基本",
                "{theme} 概要",
                "{theme} 入門"
            ],
            "深掘り": [
                "{theme} 詳細",
                "{theme} 技術",
                "{theme} 仕組み",
                "{theme} 原理"
            ],
            "実用": [
                "{theme} 使い方",
                "{theme} 活用",
                "{theme} 実践",
                "{theme} 事例"
            ]
        }
    
    def _initialize_openai(self):
        """OpenAIクライアント初期化"""
        try:
            api_key = self.config_manager.get_openai_key()
            if api_key:
                self.openai_client = openai.OpenAI(api_key=api_key)
                self.debug_logger.info("OpenAI GPT-4-turbo初期化成功")
            else:
                self.debug_logger.warning("OpenAI APIキーが設定されていません")
        except Exception as e:
            self.debug_logger.error(f"OpenAI初期化エラー: {e}")
    
    def generate_queries(self, request: QueryGenerationRequest) -> List[GeneratedQuery]:
        """
        動的クエリ生成
        
        Args:
            request: クエリ生成リクエスト
            
        Returns:
            生成されたクエリリスト
        """
        self.debug_logger.info("動的クエリ生成開始", {
            "theme": request.theme,
            "learning_type": request.learning_type,
            "depth_level": request.depth_level
        })
        
        try:
            # GPT-4-turboでクエリ生成
            if self.openai_client:
                queries = self._generate_with_gpt4(request)
            else:
                queries = self._generate_fallback_queries(request)
            
            # 生成履歴に追加
            self.generation_history.append({
                "timestamp": datetime.now(),
                "request": request,
                "generated_queries": len(queries),
                "method": "gpt4" if self.openai_client else "fallback"
            })
            
            self.debug_logger.info(f"クエリ生成完了: {len(queries)}件")
            return queries
            
        except Exception as e:
            self.debug_logger.error(f"クエリ生成エラー: {e}")
            # エラー時はフォールバック
            return self._generate_fallback_queries(request)
    
    def _generate_with_gpt4(self, request: QueryGenerationRequest) -> List[GeneratedQuery]:
        """GPT-4-turboを使用したクエリ生成"""
        prompt = self._create_generation_prompt(request)
        
        try:
            response = self.openai_client.chat.completions.create(
                model=self.gpt_config["model"],
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=self.gpt_config["temperature"],
                max_tokens=self.gpt_config["max_tokens"],
                presence_penalty=self.gpt_config["presence_penalty"],
                frequency_penalty=self.gpt_config["frequency_penalty"]
            )
            
            generated_content = response.choices[0].message.content
            return self._parse_gpt4_response(generated_content, request)
            
        except Exception as e:
            self.debug_logger.error(f"GPT-4クエリ生成エラー: {e}")
            raise
    
    def _get_system_prompt(self) -> str:
        """システムプロンプトを取得"""
        return """あなたは検索クエリ生成の専門家です。
与えられたテーマと学習条件に基づいて、最適な検索クエリを生成してください。

以下の要件を満たしてください：
1. 学習タイプ（概要・深掘り・実用）に応じた適切な観点
2. 深度レベルに応じた詳細度
3. 日本語・英語の適切な組み合わせ
4. 検索エンジンの特性を考慮
5. 多様性のある検索結果が期待できるクエリ

出力は以下のJSON形式で返してください：
{
    "queries": [
        {
            "query": "具体的な検索クエリ",
            "query_type": "technical|business|practical|trending|academic",
            "language": "japanese|english|mixed",
            "priority": 0.8,
            "expected_quality": 0.7,
            "target_engines": ["google", "duckduckgo"],
            "reasoning": "このクエリを選んだ理由"
        }
    ]
}"""
    
    def _create_generation_prompt(self, request: QueryGenerationRequest) -> str:
        """クエリ生成プロンプトを作成"""
        current_year = datetime.now().year
        
        prompt = f"""
学習テーマ: {request.theme}
学習タイプ: {request.learning_type}
深度レベル: {request.depth_level} (1=基本、5=専門)
言語設定: {request.language_preference}
対象検索エンジン: {', '.join(request.target_engines)}
現在年: {current_year}

以下の観点から5-8個の多様な検索クエリを生成してください：

1. 技術的側面: 技術仕様、実装、仕組み
2. ビジネス観点: 市場動向、活用事例、ROI
3. 実用性: 使い方、チュートリアル、ベストプラクティス
4. 最新情報: {current_year}年のトレンド、最新動向
5. 学術的観点: 研究、論文、理論
6. 問題解決: 課題、解決策、改善方法

学習タイプ「{request.learning_type}」に特に重点を置いてください。
"""
        
        if request.context_info:
            prompt += f"\n追加コンテキスト: {request.context_info}"
        
        return prompt
    
    def _parse_gpt4_response(self, response_content: str, request: QueryGenerationRequest) -> List[GeneratedQuery]:
        """GPT-4の応答を解析"""
        try:
            # JSON形式の応答を解析
            response_data = json.loads(response_content)
            queries = []
            
            for query_data in response_data.get("queries", []):
                query = GeneratedQuery(
                    query=query_data["query"],
                    query_type=query_data.get("query_type", "general"),
                    language=query_data.get("language", "japanese"),
                    priority=query_data.get("priority", 0.5),
                    expected_quality=query_data.get("expected_quality", 0.5),
                    target_engines=query_data.get("target_engines", request.target_engines),
                    reasoning=query_data.get("reasoning", "")
                )
                queries.append(query)
            
            return queries
            
        except json.JSONDecodeError:
            # JSON解析失敗時はテキストから抽出
            return self._parse_text_response(response_content, request)
    
    def _parse_text_response(self, response_content: str, request: QueryGenerationRequest) -> List[GeneratedQuery]:
        """テキスト応答からクエリを抽出"""
        lines = response_content.strip().split('\n')
        queries = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith(('#', '//', '-')):
                # 簡単なクエリ抽出
                if any(char in line for char in ['？', '?', 'とは', 'how', 'what']):
                    query = GeneratedQuery(
                        query=line,
                        query_type="general",
                        language="japanese" if any(ord(char) > 127 for char in line) else "english",
                        priority=0.5,
                        expected_quality=0.5,
                        target_engines=request.target_engines,
                        reasoning="テキスト解析による抽出"
                    )
                    queries.append(query)
        
        return queries
    
    def _generate_fallback_queries(self, request: QueryGenerationRequest) -> List[GeneratedQuery]:
        """フォールバック用固定クエリ生成"""
        self.debug_logger.info("フォールバッククエリ生成実行")
        
        queries = []
        templates = self.fallback_templates.get(request.learning_type, self.fallback_templates["概要"])
        
        for i, template in enumerate(templates):
            query_text = template.format(theme=request.theme)
            
            query = GeneratedQuery(
                query=query_text,
                query_type="general",
                language="japanese",
                priority=1.0 - (i * 0.1),  # 順位に応じて優先度調整
                expected_quality=0.6,
                target_engines=request.target_engines,
                reasoning="フォールバック固定テンプレート"
            )
            queries.append(query)
        
        # 深度レベルに応じて追加クエリ
        if request.depth_level >= 3:
            additional_queries = [
                f"{request.theme} 最新情報 {datetime.now().year}",
                f"{request.theme} 技術動向",
                f"{request.theme} 市場分析"
            ]
            
            for query_text in additional_queries:
                query = GeneratedQuery(
                    query=query_text,
                    query_type="trending",
                    language="japanese",
                    priority=0.7,
                    expected_quality=0.5,
                    target_engines=request.target_engines,
                    reasoning="深度レベル追加クエリ"
                )
                queries.append(query)
        
        return queries
    
    def get_generation_history(self) -> List[Dict[str, Any]]:
        """生成履歴を取得"""
        return self.generation_history.copy()
    
    def clear_generation_history(self):
        """生成履歴をクリア"""
        self.generation_history.clear()
    
    def is_available(self) -> bool:
        """サービスが利用可能かチェック"""
        return self.openai_client is not None
    
    def get_status(self) -> Dict[str, Any]:
        """サービスステータスを取得"""
        return {
            "service_name": "DynamicQueryGenerator",
            "gpt4_available": self.openai_client is not None,
            "model": self.gpt_config["model"],
            "total_generations": len(self.generation_history),
            "last_generation": self.generation_history[-1]["timestamp"].isoformat() if self.generation_history else None,
            "fallback_available": True
        }

# テスト用コード
if __name__ == "__main__":
    print("=== 動的クエリ生成エンジンテスト ===")
    
    generator = DynamicQueryGenerator()
    
    # ステータス確認
    print(f"サービス状態: {generator.get_status()}")
    
    # テストリクエスト作成
    test_request = QueryGenerationRequest(
        theme="人工知能",
        learning_type="深掘り",
        depth_level=4,
        language_preference="mixed",
        target_engines=["google", "duckduckgo"]
    )
    
    print(f"\nテストリクエスト: {test_request.theme} ({test_request.learning_type})")
    
    # クエリ生成
    queries = generator.generate_queries(test_request)
    
    print(f"\n生成されたクエリ数: {len(queries)}")
    
    for i, query in enumerate(queries, 1):
        print(f"{i}. {query.query}")
        print(f"   タイプ: {query.query_type}")
        print(f"   言語: {query.language}")
        print(f"   優先度: {query.priority:.2f}")
        print(f"   期待品質: {query.expected_quality:.2f}")
        print(f"   理由: {query.reasoning}")
        print()
    
    print("✅ 動的クエリ生成エンジンテスト完了")
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SearchResultModels - 検索結果統一データ構造
DuckDuckGo統合とマルチエンジン対応のための統一データモデル
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from datetime import datetime

@dataclass
class SearchItem:
    """個別検索結果アイテム"""
    title: str
    url: str
    snippet: str
    source_domain: str
    source_type: str = "web"  # "web", "news", "image", "video"
    publish_date: Optional[datetime] = None
    relevance_score: float = 0.0
    quality_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            "title": self.title,
            "url": self.url,
            "snippet": self.snippet,
            "source_domain": self.source_domain,
            "source_type": self.source_type,
            "publish_date": self.publish_date.isoformat() if self.publish_date else None,
            "relevance_score": self.relevance_score,
            "quality_score": self.quality_score
        }

@dataclass
class UnifiedSearchResult:
    """統一検索結果データ構造"""
    query: str
    results: List[SearchItem]
    total_results: int
    engine_used: str
    execution_time: float
    success: bool = True
    error_message: Optional[str] = None
    quota_remaining: Optional[int] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            "query": self.query,
            "results": [item.to_dict() for item in self.results],
            "total_results": self.total_results,
            "engine_used": self.engine_used,
            "execution_time": self.execution_time,
            "success": self.success,
            "error_message": self.error_message,
            "quota_remaining": self.quota_remaining,
            "timestamp": self.timestamp.isoformat()
        }
    
    def get_successful_results(self) -> List[SearchItem]:
        """成功した検索結果のみを取得"""
        return self.results if self.success else []
    
    def get_top_results(self, n: int = 5) -> List[SearchItem]:
        """上位N件の結果を取得"""
        return self.results[:n] if self.success else []
    
    def calculate_average_quality(self) -> float:
        """平均品質スコアを計算"""
        if not self.results:
            return 0.0
        return sum(item.quality_score for item in self.results) / len(self.results)

@dataclass
class SearchEngineStatus:
    """検索エンジンステータス"""
    engine_name: str
    available: bool
    quota_remaining: Optional[int] = None
    daily_limit: Optional[int] = None
    error_message: Optional[str] = None
    last_used: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            "engine_name": self.engine_name,
            "available": self.available,
            "quota_remaining": self.quota_remaining,
            "daily_limit": self.daily_limit,
            "error_message": self.error_message,
            "last_used": self.last_used.isoformat() if self.last_used else None
        }

@dataclass
class MultiSearchResult:
    """マルチエンジン検索結果"""
    query: str
    combined_results: List[SearchItem]
    engine_results: Dict[str, UnifiedSearchResult]
    total_unique_results: int
    engines_used: List[str]
    execution_time: float
    success: bool = True
    primary_engine: str = ""
    
    def __post_init__(self):
        if not self.primary_engine and self.engines_used:
            self.primary_engine = self.engines_used[0]
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            "query": self.query,
            "combined_results": [item.to_dict() for item in self.combined_results],
            "engine_results": {name: result.to_dict() for name, result in self.engine_results.items()},
            "total_unique_results": self.total_unique_results,
            "engines_used": self.engines_used,
            "execution_time": self.execution_time,
            "success": self.success,
            "primary_engine": self.primary_engine
        }
    
    def get_best_results(self, n: int = 10) -> List[SearchItem]:
        """品質スコア順で最良の結果を取得"""
        sorted_results = sorted(
            self.combined_results,
            key=lambda x: (x.quality_score, x.relevance_score),
            reverse=True
        )
        return sorted_results[:n]

# 後方互換性のためのエイリアス
SearchResult = UnifiedSearchResult
SearchStatus = SearchEngineStatus
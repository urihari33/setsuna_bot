#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SessionRelationshipManager - Phase 2A-4
セッション間関連性管理・継承システム
"""

import json
import os
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import uuid
from collections import defaultdict
import re
from difflib import SequenceMatcher

# Windows環境のパス設定
if os.name == 'nt':
    DATA_DIR = Path("D:/setsuna_bot/data/activity_knowledge/relationships")
else:
    DATA_DIR = Path("/mnt/d/setsuna_bot/data/activity_knowledge/relationships")

@dataclass
class SessionRelationship:
    """セッション関係性データクラス"""
    session_id: str
    parent_session: Optional[str] = None
    child_sessions: List[str] = None
    related_sessions: List[str] = None
    relationship_type: str = "independent"  # "deep_dive", "related", "continuation", "parallel"
    relevance_score: float = 0.0
    inherited_knowledge: List[str] = None
    focus_areas: List[str] = None
    avoided_duplicates: List[str] = None
    knowledge_evolution: Dict[str, List[str]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.child_sessions is None:
            self.child_sessions = []
        if self.related_sessions is None:
            self.related_sessions = []
        if self.inherited_knowledge is None:
            self.inherited_knowledge = []
        if self.focus_areas is None:
            self.focus_areas = []
        if self.avoided_duplicates is None:
            self.avoided_duplicates = []
        if self.knowledge_evolution is None:
            self.knowledge_evolution = {
                "new_concepts": [],
                "updated_concepts": [],
                "deprecated_concepts": []
            }
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

@dataclass
class SessionLineage:
    """セッション系譜"""
    root_session: str
    lineage_depth: int
    total_sessions: int
    branch_points: List[str]
    lineage_tree: Dict[str, Any]
    created_at: datetime
    last_updated: datetime

class SessionRelationshipManager:
    """セッション関係性管理メインクラス"""
    
    def __init__(self):
        """初期化"""
        self.relationships_dir = DATA_DIR
        self.relationships_dir.mkdir(parents=True, exist_ok=True)
        
        # データファイル
        self.session_tree_file = self.relationships_dir / "session_tree.json"
        self.knowledge_links_file = self.relationships_dir / "knowledge_links.json"
        
        # メモリ内データ
        self.session_relationships: Dict[str, SessionRelationship] = {}
        self.session_lineages: Dict[str, SessionLineage] = {}
        self.knowledge_links: Dict[str, List[str]] = defaultdict(list)
        
        # 関連性計算設定
        self.similarity_config = {
            "theme_weight": 0.4,
            "keywords_weight": 0.3,
            "entities_weight": 0.2,
            "temporal_weight": 0.1,
            "min_similarity_threshold": 0.3,
            "max_relationship_distance": 3
        }
        
        # 継承設定
        self.inheritance_config = {
            "max_inherited_items": 10,
            "min_relevance_score": 0.6,
            "knowledge_decay_days": 30,
            "focus_inheritance_ratio": 0.7
        }
        
        self._load_existing_data()
        
        print("[関係管理] ✅ SessionRelationshipManager初期化完了")
    
    def _load_existing_data(self):
        """既存データの読み込み"""
        try:
            # セッション関係性読み込み
            if self.session_tree_file.exists():
                with open(self.session_tree_file, 'r', encoding='utf-8') as f:
                    tree_data = json.load(f)
                    
                    # セッション関係性復元
                    for rel_data in tree_data.get("session_relationships", []):
                        relationship = SessionRelationship(
                            session_id=rel_data["session_id"],
                            parent_session=rel_data.get("parent_session"),
                            child_sessions=rel_data.get("child_sessions", []),
                            related_sessions=rel_data.get("related_sessions", []),
                            relationship_type=rel_data.get("relationship_type", "independent"),
                            relevance_score=rel_data.get("relevance_score", 0.0),
                            inherited_knowledge=rel_data.get("inherited_knowledge", []),
                            focus_areas=rel_data.get("focus_areas", []),
                            avoided_duplicates=rel_data.get("avoided_duplicates", []),
                            knowledge_evolution=rel_data.get("knowledge_evolution", {}),
                            created_at=datetime.fromisoformat(rel_data.get("created_at", datetime.now().isoformat())),
                            updated_at=datetime.fromisoformat(rel_data.get("updated_at", datetime.now().isoformat()))
                        )
                        self.session_relationships[relationship.session_id] = relationship
                    
                    # セッション系譜復元
                    for lineage_data in tree_data.get("session_lineage", {}).get("lineage_trees", []):
                        lineage = SessionLineage(
                            root_session=lineage_data["root"],
                            lineage_depth=len(lineage_data.get("branches", [])),
                            total_sessions=self._count_lineage_sessions(lineage_data),
                            branch_points=self._extract_branch_points(lineage_data),
                            lineage_tree=lineage_data,
                            created_at=datetime.now(),
                            last_updated=datetime.now()
                        )
                        self.session_lineages[lineage.root_session] = lineage
                
                print(f"[関係管理] 📊 関係性読み込み: {len(self.session_relationships)}セッション")
            
            # 知識リンク読み込み
            if self.knowledge_links_file.exists():
                with open(self.knowledge_links_file, 'r', encoding='utf-8') as f:
                    links_data = json.load(f)
                    self.knowledge_links = defaultdict(list, links_data.get("knowledge_links", {}))
                
                print(f"[関係管理] 🔗 知識リンク読み込み: {len(self.knowledge_links)}件")
            
        except Exception as e:
            print(f"[関係管理] ⚠️ データ読み込み失敗: {e}")
    
    def _count_lineage_sessions(self, lineage_tree: Dict) -> int:
        """系譜内のセッション数カウント"""
        count = 1  # root
        for branch in lineage_tree.get("branches", []):
            count += self._count_lineage_sessions(branch)
        return count
    
    def _extract_branch_points(self, lineage_tree: Dict) -> List[str]:
        """分岐点の抽出"""
        branch_points = []
        if len(lineage_tree.get("branches", [])) > 1:
            branch_points.append(lineage_tree.get("session", ""))
        
        for branch in lineage_tree.get("branches", []):
            branch_points.extend(self._extract_branch_points(branch))
        
        return branch_points
    
    def create_session_relationship(self,
                                  session_id: str,
                                  session_data: Dict[str, Any],
                                  parent_session: Optional[str] = None) -> bool:
        """
        セッション関係性作成
        
        Args:
            session_id: セッションID
            session_data: セッションデータ
            parent_session: 親セッションID
            
        Returns:
            作成成功フラグ
        """
        try:
            # 既存関係性チェック
            if session_id in self.session_relationships:
                print(f"[関係管理] ⚠️ セッション関係性既存: {session_id}")
                return False
            
            # 関連セッション自動検出
            related_sessions = self._find_related_sessions(session_data)
            
            # 関係性タイプ決定
            relationship_type = self._determine_relationship_type(session_data, parent_session, related_sessions)
            
            # 継承知識特定
            inherited_knowledge = self._identify_inherited_knowledge(session_data, parent_session, related_sessions)
            
            # フォーカス領域抽出
            focus_areas = self._extract_focus_areas(session_data)
            
            # 重複回避項目特定
            avoided_duplicates = self._identify_avoided_duplicates(session_data, parent_session)
            
            # セッション関係性作成
            relationship = SessionRelationship(
                session_id=session_id,
                parent_session=parent_session,
                related_sessions=[rs["session_id"] for rs in related_sessions],
                relationship_type=relationship_type,
                relevance_score=self._calculate_overall_relevance(related_sessions),
                inherited_knowledge=inherited_knowledge,
                focus_areas=focus_areas,
                avoided_duplicates=avoided_duplicates
            )
            
            self.session_relationships[session_id] = relationship
            
            # 親セッションの子リスト更新
            if parent_session and parent_session in self.session_relationships:
                parent_rel = self.session_relationships[parent_session]
                if session_id not in parent_rel.child_sessions:
                    parent_rel.child_sessions.append(session_id)
                    parent_rel.updated_at = datetime.now()
            
            # 系譜更新
            self._update_session_lineage(session_id, parent_session)
            
            # データ保存
            self._save_relationship_data()
            
            print(f"[関係管理] ✨ セッション関係性作成: {session_id}")
            print(f"  関係タイプ: {relationship_type}")
            print(f"  関連セッション: {len(related_sessions)}件")
            print(f"  継承知識: {len(inherited_knowledge)}件")
            
            return True
            
        except Exception as e:
            print(f"[関係管理] ❌ セッション関係性作成失敗: {e}")
            return False
    
    def _find_related_sessions(self, session_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """関連セッション検出"""
        try:
            current_theme = session_data.get("theme", "")
            current_keywords = self._extract_keywords_from_session(session_data)
            current_entities = self._extract_entities_from_session(session_data)
            current_time = datetime.now()
            
            related_sessions = []
            
            for session_id, relationship in self.session_relationships.items():
                # 自分自身は除外
                if session_id == session_data.get("session_id"):
                    continue
                
                # 時間的近接性チェック（30日以内）
                time_diff = (current_time - relationship.created_at).days
                if time_diff > 30:
                    continue
                
                # 類似度計算
                similarity_score = self._calculate_session_similarity(
                    current_theme, current_keywords, current_entities,
                    session_id, relationship
                )
                
                if similarity_score >= self.similarity_config["min_similarity_threshold"]:
                    related_sessions.append({
                        "session_id": session_id,
                        "similarity_score": similarity_score,
                        "relationship": relationship,
                        "time_distance": time_diff
                    })
            
            # 類似度順でソート
            related_sessions.sort(key=lambda x: x["similarity_score"], reverse=True)
            
            # 上位関連セッションのみ返す
            return related_sessions[:5]
            
        except Exception as e:
            print(f"[関係管理] ❌ 関連セッション検出失敗: {e}")
            return []
    
    def _calculate_session_similarity(self,
                                    current_theme: str,
                                    current_keywords: List[str],
                                    current_entities: List[str],
                                    target_session_id: str,
                                    target_relationship: SessionRelationship) -> float:
        """セッション類似度計算"""
        try:
            # テーマ類似度
            theme_similarity = 0.0
            if target_relationship.focus_areas:
                for focus_area in target_relationship.focus_areas:
                    theme_similarity = max(theme_similarity, 
                                         SequenceMatcher(None, current_theme.lower(), focus_area.lower()).ratio())
            
            # キーワード類似度
            keyword_similarity = 0.0
            if current_keywords and target_relationship.focus_areas:
                common_keywords = set(current_keywords) & set(target_relationship.focus_areas)
                if current_keywords:
                    keyword_similarity = len(common_keywords) / len(current_keywords)
            
            # エンティティ類似度
            entity_similarity = 0.0
            # 実装時にKnowledgeDatabaseと連携してエンティティ比較
            
            # 時間的重み（実装簡略化）
            temporal_similarity = 0.5
            
            # 重み付き合計
            total_similarity = (
                theme_similarity * self.similarity_config["theme_weight"] +
                keyword_similarity * self.similarity_config["keywords_weight"] +
                entity_similarity * self.similarity_config["entities_weight"] +
                temporal_similarity * self.similarity_config["temporal_weight"]
            )
            
            return min(1.0, total_similarity)
            
        except Exception as e:
            print(f"[関係管理] ❌ 類似度計算失敗: {e}")
            return 0.0
    
    def _extract_keywords_from_session(self, session_data: Dict[str, Any]) -> List[str]:
        """セッションからキーワード抽出"""
        keywords = []
        
        theme = session_data.get("theme", "")
        if theme:
            # 簡易キーワード抽出（実際はより高度な処理）
            keywords.extend(theme.split())
        
        # タグからも抽出
        tags = session_data.get("tags", [])
        keywords.extend(tags)
        
        return list(set(keywords))
    
    def _extract_entities_from_session(self, session_data: Dict[str, Any]) -> List[str]:
        """セッションからエンティティ抽出"""
        # 実装時にKnowledgeDatabaseと連携
        return []
    
    def _determine_relationship_type(self,
                                   session_data: Dict[str, Any],
                                   parent_session: Optional[str],
                                   related_sessions: List[Dict]) -> str:
        """関係性タイプ決定"""
        if parent_session:
            # 親セッションの深度レベルと比較
            parent_depth = self._get_session_depth_level(parent_session)
            current_depth = session_data.get("depth_level", 3)
            
            if current_depth > parent_depth:
                return "deep_dive"
            elif current_depth == parent_depth:
                return "continuation"
            else:
                return "related"
        
        elif related_sessions:
            # 関連セッションとの類似度で判定
            max_similarity = max(rs["similarity_score"] for rs in related_sessions)
            if max_similarity > 0.8:
                return "parallel_research"
            else:
                return "related"
        
        else:
            return "independent"
    
    def _get_session_depth_level(self, session_id: str) -> int:
        """セッション深度レベル取得"""
        # 実装時にセッション管理システムと連携
        return 3  # デフォルト値
    
    def _identify_inherited_knowledge(self,
                                    session_data: Dict[str, Any],
                                    parent_session: Optional[str],
                                    related_sessions: List[Dict]) -> List[str]:
        """継承知識特定"""
        inherited_items = []
        
        try:
            if parent_session:
                # 親セッションからの知識継承
                parent_knowledge = self._get_session_knowledge_items(parent_session)
                
                # 関連度の高い知識アイテムを選択
                for knowledge_id in parent_knowledge:
                    relevance = self._calculate_knowledge_relevance(knowledge_id, session_data)
                    if relevance >= self.inheritance_config["min_relevance_score"]:
                        inherited_items.append(knowledge_id)
            
            # 関連セッションからの知識継承
            for related_session in related_sessions:
                if related_session["similarity_score"] > 0.7:
                    related_knowledge = self._get_session_knowledge_items(related_session["session_id"])
                    for knowledge_id in related_knowledge[:3]:  # 上位3件
                        if knowledge_id not in inherited_items:
                            inherited_items.append(knowledge_id)
            
            # 最大継承数制限
            return inherited_items[:self.inheritance_config["max_inherited_items"]]
            
        except Exception as e:
            print(f"[関係管理] ❌ 継承知識特定失敗: {e}")
            return []
    
    def _get_session_knowledge_items(self, session_id: str) -> List[str]:
        """セッション知識アイテム取得"""
        # 実装時にKnowledgeDatabaseと連携
        return []
    
    def _calculate_knowledge_relevance(self, knowledge_id: str, session_data: Dict[str, Any]) -> float:
        """知識関連度計算"""
        # 実装時にKnowledgeDatabaseと連携して詳細計算
        return 0.7  # デフォルト値
    
    def _extract_focus_areas(self, session_data: Dict[str, Any]) -> List[str]:
        """フォーカス領域抽出"""
        focus_areas = []
        
        # テーマから抽出
        theme = session_data.get("theme", "")
        if theme:
            focus_areas.append(theme)
        
        # 学習タイプから抽出
        learning_type = session_data.get("learning_type", "")
        if learning_type:
            focus_areas.append(learning_type)
        
        # タグから抽出
        tags = session_data.get("tags", [])
        focus_areas.extend(tags)
        
        return list(set(focus_areas))
    
    def _identify_avoided_duplicates(self,
                                   session_data: Dict[str, Any],
                                   parent_session: Optional[str]) -> List[str]:
        """重複回避項目特定"""
        avoided_items = []
        
        if parent_session and parent_session in self.session_relationships:
            parent_rel = self.session_relationships[parent_session]
            
            # 親セッションで既に調査済みの基本的な項目を回避
            if "基本概念" in parent_rel.focus_areas:
                avoided_items.append("基本概念")
            
            if "歴史的経緯" in parent_rel.focus_areas:
                avoided_items.append("歴史的経緯")
            
            # 深掘りセッションの場合、概要情報を回避
            if session_data.get("learning_type") == "深掘り":
                avoided_items.extend(["概要情報", "一般的説明"])
        
        return avoided_items
    
    def _calculate_overall_relevance(self, related_sessions: List[Dict]) -> float:
        """全体関連度計算"""
        if not related_sessions:
            return 0.0
        
        return sum(rs["similarity_score"] for rs in related_sessions) / len(related_sessions)
    
    def _update_session_lineage(self, session_id: str, parent_session: Optional[str]):
        """セッション系譜更新"""
        try:
            if parent_session:
                # 親セッションの系譜を検索
                root_session = self._find_root_session(parent_session)
                
                if root_session in self.session_lineages:
                    lineage = self.session_lineages[root_session]
                    # 系譜ツリーに新セッションを追加
                    self._add_to_lineage_tree(lineage.lineage_tree, parent_session, session_id)
                    lineage.total_sessions += 1
                    lineage.last_updated = datetime.now()
                else:
                    # 新しい系譜作成
                    self._create_new_lineage(root_session, parent_session, session_id)
            else:
                # 独立セッション（新しいルート）
                lineage = SessionLineage(
                    root_session=session_id,
                    lineage_depth=1,
                    total_sessions=1,
                    branch_points=[],
                    lineage_tree={"session": session_id, "branches": []},
                    created_at=datetime.now(),
                    last_updated=datetime.now()
                )
                self.session_lineages[session_id] = lineage
            
        except Exception as e:
            print(f"[関係管理] ❌ 系譜更新失敗: {e}")
    
    def _find_root_session(self, session_id: str) -> str:
        """ルートセッション検索"""
        current_session = session_id
        
        while current_session in self.session_relationships:
            rel = self.session_relationships[current_session]
            if rel.parent_session:
                current_session = rel.parent_session
            else:
                break
        
        return current_session
    
    def _add_to_lineage_tree(self, tree: Dict, parent_id: str, new_session_id: str):
        """系譜ツリーに追加"""
        if tree.get("session") == parent_id:
            tree["branches"].append({"session": new_session_id, "branches": []})
            return True
        
        for branch in tree.get("branches", []):
            if self._add_to_lineage_tree(branch, parent_id, new_session_id):
                return True
        
        return False
    
    def _create_new_lineage(self, root_session: str, parent_session: str, new_session_id: str):
        """新しい系譜作成"""
        # 既存セッションの系譜構造を再構築
        lineage_tree = {"session": root_session, "branches": []}
        # 実装簡略化（実際はより複雑な再構築処理）
        
        lineage = SessionLineage(
            root_session=root_session,
            lineage_depth=2,
            total_sessions=2,
            branch_points=[],
            lineage_tree=lineage_tree,
            created_at=datetime.now(),
            last_updated=datetime.now()
        )
        self.session_lineages[root_session] = lineage
    
    def update_knowledge_evolution(self,
                                 session_id: str,
                                 new_concepts: List[str] = None,
                                 updated_concepts: List[str] = None,
                                 deprecated_concepts: List[str] = None):
        """
        知識進化更新
        
        Args:
            session_id: セッションID
            new_concepts: 新しい概念
            updated_concepts: 更新された概念
            deprecated_concepts: 廃止された概念
        """
        try:
            if session_id not in self.session_relationships:
                print(f"[関係管理] ⚠️ セッション関係性未発見: {session_id}")
                return
            
            relationship = self.session_relationships[session_id]
            
            if new_concepts:
                relationship.knowledge_evolution["new_concepts"].extend(new_concepts)
            
            if updated_concepts:
                relationship.knowledge_evolution["updated_concepts"].extend(updated_concepts)
            
            if deprecated_concepts:
                relationship.knowledge_evolution["deprecated_concepts"].extend(deprecated_concepts)
            
            relationship.updated_at = datetime.now()
            self._save_relationship_data()
            
            print(f"[関係管理] 🔄 知識進化更新: {session_id}")
            
        except Exception as e:
            print(f"[関係管理] ❌ 知識進化更新失敗: {e}")
    
    def get_session_context(self, session_id: str) -> Dict[str, Any]:
        """
        セッションコンテキスト取得
        
        Args:
            session_id: セッションID
            
        Returns:
            セッションコンテキスト情報
        """
        try:
            if session_id not in self.session_relationships:
                return {"error": f"セッション関係性未発見: {session_id}"}
            
            relationship = self.session_relationships[session_id]
            
            # 関連セッション詳細情報取得
            related_details = []
            for related_id in relationship.related_sessions:
                if related_id in self.session_relationships:
                    related_rel = self.session_relationships[related_id]
                    related_details.append({
                        "session_id": related_id,
                        "focus_areas": related_rel.focus_areas,
                        "relationship_type": related_rel.relationship_type,
                        "created_at": related_rel.created_at.isoformat()
                    })
            
            # 系譜情報
            root_session = self._find_root_session(session_id)
            lineage_info = None
            if root_session in self.session_lineages:
                lineage = self.session_lineages[root_session]
                lineage_info = {
                    "root_session": lineage.root_session,
                    "lineage_depth": lineage.lineage_depth,
                    "total_sessions": lineage.total_sessions,
                    "branch_points": lineage.branch_points
                }
            
            context = {
                "session_id": session_id,
                "relationship_info": asdict(relationship),
                "related_sessions_details": related_details,
                "lineage_info": lineage_info,
                "inheritance_recommendations": self._get_inheritance_recommendations(session_id),
                "focus_suggestions": self._get_focus_suggestions(session_id)
            }
            
            return context
            
        except Exception as e:
            print(f"[関係管理] ❌ セッションコンテキスト取得失敗: {e}")
            return {"error": str(e)}
    
    def _get_inheritance_recommendations(self, session_id: str) -> List[Dict[str, Any]]:
        """継承推奨事項取得"""
        recommendations = []
        
        if session_id in self.session_relationships:
            relationship = self.session_relationships[session_id]
            
            # 継承済み知識の活用提案
            for knowledge_id in relationship.inherited_knowledge:
                recommendations.append({
                    "type": "knowledge_utilization",
                    "knowledge_id": knowledge_id,
                    "suggestion": "継承した知識を基盤として詳細調査を実施"
                })
            
            # 回避項目の確認提案
            for avoided_item in relationship.avoided_duplicates:
                recommendations.append({
                    "type": "duplication_avoidance",
                    "item": avoided_item,
                    "suggestion": f"{avoided_item}は親セッションで調査済みのため、より詳細な側面に焦点を当てる"
                })
        
        return recommendations
    
    def _get_focus_suggestions(self, session_id: str) -> List[str]:
        """フォーカス提案取得"""
        suggestions = []
        
        if session_id in self.session_relationships:
            relationship = self.session_relationships[session_id]
            
            # 関連セッションとの差別化提案
            covered_areas = set()
            for related_id in relationship.related_sessions:
                if related_id in self.session_relationships:
                    related_rel = self.session_relationships[related_id]
                    covered_areas.update(related_rel.focus_areas)
            
            # 未カバー領域の提案
            potential_areas = [
                "最新技術動向", "市場分析", "実装事例", "課題・制限事項",
                "将来展望", "競合技術比較", "ユースケース"
            ]
            
            for area in potential_areas:
                if area not in covered_areas:
                    suggestions.append(f"{area}に焦点を当てた調査")
        
        return suggestions
    
    def recommend_next_sessions(self, current_session_id: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        次回セッション推奨
        
        Args:
            current_session_id: 現在のセッションID
            limit: 推奨数制限
            
        Returns:
            推奨セッションリスト
        """
        try:
            recommendations = []
            
            if current_session_id not in self.session_relationships:
                return recommendations
            
            current_rel = self.session_relationships[current_session_id]
            
            # 深掘りセッション推奨
            if current_rel.relationship_type in ["概要", "independent"]:
                for focus_area in current_rel.focus_areas:
                    recommendations.append({
                        "type": "deep_dive",
                        "theme": f"{focus_area}の詳細調査",
                        "relationship_type": "deep_dive",
                        "parent_session": current_session_id,
                        "rationale": f"{focus_area}について更に詳しく調査することで理解を深める",
                        "estimated_value": 0.8
                    })
            
            # 関連領域セッション推奨
            related_topics = self._identify_related_topics(current_rel.focus_areas)
            for topic in related_topics:
                recommendations.append({
                    "type": "related_exploration",
                    "theme": topic,
                    "relationship_type": "related",
                    "parent_session": None,
                    "rationale": f"{topic}は現在の調査テーマと関連性が高い",
                    "estimated_value": 0.6
                })
            
            # 実用セッション推奨
            if current_rel.relationship_type == "deep_dive":
                recommendations.append({
                    "type": "practical_application",
                    "theme": f"{current_rel.focus_areas[0]}の実用・応用",
                    "relationship_type": "continuation",
                    "parent_session": current_session_id,
                    "rationale": "調査した知識を実際の活動に活用する方法を検討",
                    "estimated_value": 0.9
                })
            
            # 価値順でソート
            recommendations.sort(key=lambda x: x["estimated_value"], reverse=True)
            
            return recommendations[:limit]
            
        except Exception as e:
            print(f"[関係管理] ❌ 次回セッション推奨失敗: {e}")
            return []
    
    def _identify_related_topics(self, focus_areas: List[str]) -> List[str]:
        """関連トピック特定"""
        # 簡易実装（実際はより高度な関連性分析）
        related_mapping = {
            "AI": ["機械学習", "深層学習", "自然言語処理"],
            "音楽生成": ["音響処理", "MIDI", "音楽理論"],
            "技術調査": ["市場分析", "競合調査", "トレンド分析"]
        }
        
        related_topics = []
        for area in focus_areas:
            for key, values in related_mapping.items():
                if key.lower() in area.lower():
                    related_topics.extend(values)
        
        return list(set(related_topics))
    
    def get_session_lineage_visualization(self, root_session: str) -> Dict[str, Any]:
        """
        セッション系譜可視化データ取得
        
        Args:
            root_session: ルートセッションID
            
        Returns:
            可視化用データ
        """
        try:
            if root_session not in self.session_lineages:
                return {"error": f"系譜未発見: {root_session}"}
            
            lineage = self.session_lineages[root_session]
            
            # ノード情報生成
            nodes = []
            edges = []
            
            def process_tree_node(tree_node: Dict, parent_id: Optional[str] = None, level: int = 0):
                session_id = tree_node.get("session", "")
                
                # ノード情報
                node_info = {
                    "id": session_id,
                    "level": level,
                    "type": "root" if parent_id is None else "child"
                }
                
                if session_id in self.session_relationships:
                    rel = self.session_relationships[session_id]
                    node_info.update({
                        "relationship_type": rel.relationship_type,
                        "focus_areas": rel.focus_areas,
                        "created_at": rel.created_at.isoformat()
                    })
                
                nodes.append(node_info)
                
                # エッジ情報
                if parent_id:
                    edges.append({
                        "source": parent_id,
                        "target": session_id,
                        "type": node_info.get("relationship_type", "child")
                    })
                
                # 子ノード処理
                for branch in tree_node.get("branches", []):
                    process_tree_node(branch, session_id, level + 1)
            
            process_tree_node(lineage.lineage_tree)
            
            visualization_data = {
                "lineage_id": root_session,
                "total_sessions": lineage.total_sessions,
                "lineage_depth": lineage.lineage_depth,
                "nodes": nodes,
                "edges": edges,
                "branch_points": lineage.branch_points,
                "created_at": lineage.created_at.isoformat(),
                "last_updated": lineage.last_updated.isoformat()
            }
            
            return visualization_data
            
        except Exception as e:
            print(f"[関係管理] ❌ 系譜可視化データ生成失敗: {e}")
            return {"error": str(e)}
    
    def _save_relationship_data(self):
        """関係性データ保存"""
        try:
            # セッション関係性データ
            relationships_data = []
            for relationship in self.session_relationships.values():
                relationships_data.append(asdict(relationship))
            
            # 系譜データ
            lineage_trees = []
            for lineage in self.session_lineages.values():
                lineage_trees.append(lineage.lineage_tree)
            
            session_tree_data = {
                "session_relationships": relationships_data,
                "session_lineage": {
                    "root_sessions": list(self.session_lineages.keys()),
                    "lineage_trees": lineage_trees
                },
                "last_updated": datetime.now().isoformat()
            }
            
            with open(self.session_tree_file, 'w', encoding='utf-8') as f:
                json.dump(session_tree_data, f, ensure_ascii=False, indent=2, default=str)
            
            # 知識リンクデータ
            knowledge_links_data = {
                "knowledge_links": dict(self.knowledge_links),
                "last_updated": datetime.now().isoformat()
            }
            
            with open(self.knowledge_links_file, 'w', encoding='utf-8') as f:
                json.dump(knowledge_links_data, f, ensure_ascii=False, indent=2, default=str)
            
        except Exception as e:
            print(f"[関係管理] ❌ データ保存失敗: {e}")
    
    def get_relationship_statistics(self) -> Dict[str, Any]:
        """関係性統計情報"""
        try:
            # 関係性タイプ別統計
            type_stats = defaultdict(int)
            for rel in self.session_relationships.values():
                type_stats[rel.relationship_type] += 1
            
            # 系譜統計
            lineage_stats = {
                "total_lineages": len(self.session_lineages),
                "average_lineage_depth": sum(l.lineage_depth for l in self.session_lineages.values()) / len(self.session_lineages) if self.session_lineages else 0,
                "total_sessions_in_lineages": sum(l.total_sessions for l in self.session_lineages.values())
            }
            
            statistics = {
                "total_sessions": len(self.session_relationships),
                "relationship_type_distribution": dict(type_stats),
                "lineage_statistics": lineage_stats,
                "average_related_sessions": sum(len(rel.related_sessions) for rel in self.session_relationships.values()) / len(self.session_relationships) if self.session_relationships else 0,
                "inheritance_utilization": sum(len(rel.inherited_knowledge) for rel in self.session_relationships.values()),
                "last_updated": datetime.now().isoformat()
            }
            
            return statistics
            
        except Exception as e:
            print(f"[関係管理] ❌ 統計情報生成失敗: {e}")
            return {"error": str(e)}


# テスト用コード
if __name__ == "__main__":
    print("=== SessionRelationshipManager テスト ===")
    
    manager = SessionRelationshipManager()
    
    # テストセッションデータ
    test_session_data_1 = {
        "session_id": "test_session_001",
        "theme": "AI音楽生成技術調査",
        "learning_type": "概要",
        "depth_level": 2,
        "tags": ["AI", "音楽", "技術調査"]
    }
    
    test_session_data_2 = {
        "session_id": "test_session_002", 
        "theme": "Transformer音楽生成詳細",
        "learning_type": "深掘り",
        "depth_level": 4,
        "tags": ["Transformer", "音楽生成", "深層学習"]
    }
    
    # セッション関係性作成テスト
    print("\n🔗 セッション関係性作成テスト:")
    success1 = manager.create_session_relationship("test_session_001", test_session_data_1)
    print(f"セッション1作成: {'✅' if success1 else '❌'}")
    
    success2 = manager.create_session_relationship("test_session_002", test_session_data_2, "test_session_001")
    print(f"セッション2作成: {'✅' if success2 else '❌'}")
    
    # セッションコンテキスト取得テスト
    print("\n📋 セッションコンテキスト取得テスト:")
    context = manager.get_session_context("test_session_002")
    if "error" not in context:
        print(f"✅ コンテキスト取得成功")
        print(f"  関係タイプ: {context['relationship_info']['relationship_type']}")
        print(f"  継承知識: {len(context['relationship_info']['inherited_knowledge'])}件")
        print(f"  フォーカス領域: {context['relationship_info']['focus_areas']}")
    else:
        print(f"❌ コンテキスト取得失敗: {context['error']}")
    
    # 次回セッション推奨テスト
    print("\n💡 次回セッション推奨テスト:")
    recommendations = manager.recommend_next_sessions("test_session_001")
    print(f"推奨セッション数: {len(recommendations)}件")
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec['theme']} ({rec['type']}) - 価値: {rec['estimated_value']:.1f}")
    
    # 系譜可視化データテスト
    print("\n🌳 系譜可視化データテスト:")
    viz_data = manager.get_session_lineage_visualization("test_session_001")
    if "error" not in viz_data:
        print(f"✅ 可視化データ生成成功")
        print(f"  ノード数: {len(viz_data['nodes'])}個")
        print(f"  エッジ数: {len(viz_data['edges'])}個")
        print(f"  系譜深度: {viz_data['lineage_depth']}")
    else:
        print(f"❌ 可視化データ生成失敗: {viz_data['error']}")
    
    # 統計情報テスト
    print("\n📊 関係性統計テスト:")
    stats = manager.get_relationship_statistics()
    if "error" not in stats:
        print(f"✅ 統計情報生成成功")
        print(f"  総セッション数: {stats['total_sessions']}")
        print(f"  系譜数: {stats['lineage_statistics']['total_lineages']}")
        print(f"  関係性分布: {stats['relationship_type_distribution']}")
    else:
        print(f"❌ 統計情報生成失敗: {stats['error']}")
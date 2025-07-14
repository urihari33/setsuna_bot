#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知識グラフシステム - Phase 2B実装
動画・会話・コンセプト間の関連性をマッピングする知識グラフ構築システム
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
from datetime import datetime
import hashlib
import math
import networkx as nx
from difflib import SequenceMatcher

# プロジェクトルートをパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Windowsパス設定
if os.name == 'nt':
    DATA_DIR = Path("D:/setsuna_bot/youtube_knowledge_system/data")
    GRAPH_DIR = Path("D:/setsuna_bot/knowledge_graph")
    CONVERSATION_DIR = Path("D:/setsuna_bot/data")
else:
    DATA_DIR = Path("/mnt/d/setsuna_bot/youtube_knowledge_system/data")
    GRAPH_DIR = Path("/mnt/d/setsuna_bot/knowledge_graph")
    CONVERSATION_DIR = Path("/mnt/d/setsuna_bot/data")

GRAPH_DIR.mkdir(parents=True, exist_ok=True)

@dataclass
class KnowledgeNode:
    """知識ノードデータクラス"""
    node_id: str
    node_type: str  # "video", "artist", "genre", "concept", "conversation"
    title: str
    attributes: Dict[str, Any]
    relevance_score: float
    created_at: str
    updated_at: str

@dataclass
class KnowledgeEdge:
    """知識エッジデータクラス"""
    edge_id: str
    source_id: str
    target_id: str
    relationship_type: str  # "similarity", "association", "sequence", "genre", "collaboration"
    strength: float
    evidence: List[str]  # 関連性の根拠
    created_at: str

@dataclass
class GraphCluster:
    """グラフクラスターデータクラス"""
    cluster_id: str
    cluster_type: str
    node_ids: List[str]
    central_concepts: List[str]
    cohesion_score: float
    description: str

class KnowledgeGraphSystem:
    """知識グラフシステムクラス"""
    
    def __init__(self):
        """初期化"""
        self.knowledge_db_path = DATA_DIR / "unified_knowledge_db.json"
        self.graph_data_path = GRAPH_DIR / "knowledge_graph.json"
        self.clusters_path = GRAPH_DIR / "graph_clusters.json"
        self.conversation_history_path = CONVERSATION_DIR / "video_conversation_history.json"
        
        # ネットワークグラフ
        self.graph = nx.Graph()
        self.knowledge_nodes = {}
        self.knowledge_edges = {}
        self.clusters = {}
        
        # データベース
        self.knowledge_db = {}
        self.conversation_history = {}
        
        # 関連性計算用の重み設定
        self.relationship_weights = {
            "same_artist": 0.9,
            "same_genre": 0.7,
            "same_theme": 0.6,
            "similar_mood": 0.5,
            "collaboration": 0.8,
            "sequence": 0.4,
            "user_preference": 0.6,
            "conversation_context": 0.5
        }
        
        # 統計情報
        self.graph_statistics = {
            "total_nodes": 0,
            "total_edges": 0,
            "clusters_count": 0,
            "last_rebuild": None,
            "coverage_rate": 0.0
        }
        
        self._load_data()
        self._initialize_graph()
        
        print("[知識グラフ] ✅ 知識グラフシステム初期化完了")
    
    def _load_data(self):
        """データロード"""
        # YouTube知識データベース
        try:
            if self.knowledge_db_path.exists():
                with open(self.knowledge_db_path, 'r', encoding='utf-8') as f:
                    self.knowledge_db = json.load(f)
                video_count = len(self.knowledge_db.get("videos", {}))
                print(f"[知識グラフ] 📊 {video_count}件の動画データをロード")
        except Exception as e:
            print(f"[知識グラフ] ❌ 動画データロードエラー: {e}")
        
        # 会話履歴
        try:
            if self.conversation_history_path.exists():
                with open(self.conversation_history_path, 'r', encoding='utf-8') as f:
                    self.conversation_history = json.load(f)
                conv_count = len(self.conversation_history.get("conversations", {}))
                print(f"[知識グラフ] 💬 {conv_count}件の会話履歴をロード")
        except Exception as e:
            print(f"[知識グラフ] ⚠️ 会話履歴ロードエラー: {e}")
        
        # 既存グラフデータ
        try:
            if self.graph_data_path.exists():
                with open(self.graph_data_path, 'r', encoding='utf-8') as f:
                    graph_data = json.load(f)
                    self.knowledge_nodes = {nid: KnowledgeNode(**node) for nid, node in graph_data.get("nodes", {}).items()}
                    self.knowledge_edges = {eid: KnowledgeEdge(**edge) for eid, edge in graph_data.get("edges", {}).items()}
                print(f"[知識グラフ] 🔗 既存グラフデータをロード")
        except Exception as e:
            print(f"[知識グラフ] ⚠️ グラフデータロードエラー: {e}")
    
    def _initialize_graph(self):
        """グラフ初期化"""
        # ノード追加
        for node_id, node in self.knowledge_nodes.items():
            self.graph.add_node(node_id, **asdict(node))
        
        # エッジ追加
        for edge in self.knowledge_edges.values():
            if edge.source_id in self.graph.nodes and edge.target_id in self.graph.nodes:
                self.graph.add_edge(
                    edge.source_id, 
                    edge.target_id, 
                    weight=edge.strength,
                    relationship_type=edge.relationship_type,
                    edge_data=edge
                )
        
        # 統計更新
        self._update_statistics()
    
    def build_knowledge_graph(self, force_rebuild: bool = False):
        """知識グラフ構築"""
        if not force_rebuild and self.knowledge_nodes:
            print("[知識グラフ] 既存グラフを使用します（force_rebuild=Trueで再構築）")
            return
        
        print("[知識グラフ] 📊 知識グラフを構築中...")
        
        # グラフクリア
        self.graph.clear()
        self.knowledge_nodes.clear()
        self.knowledge_edges.clear()
        
        # Phase 1: 動画ノード作成
        self._create_video_nodes()
        
        # Phase 2: アーティスト/概念ノード作成  
        self._create_concept_nodes()
        
        # Phase 3: 会話ノード作成
        self._create_conversation_nodes()
        
        # Phase 4: 関連性エッジ構築
        self._build_relationships()
        
        # Phase 5: クラスタリング
        self._perform_clustering()
        
        # データ保存
        self._save_graph_data()
        
        # 統計更新
        self._update_statistics()
        
        print(f"[知識グラフ] ✅ グラフ構築完了: {len(self.knowledge_nodes)}ノード, {len(self.knowledge_edges)}エッジ")
    
    def _create_video_nodes(self):
        """動画ノード作成"""
        videos = self.knowledge_db.get("videos", {})
        
        for video_id, video_data in videos.items():
            metadata = video_data.get("metadata", {})
            custom_info = video_data.get("custom_info", {})
            creative_insight = video_data.get("creative_insight", {})
            
            # ノード属性
            attributes = {
                "title": custom_info.get("manual_title") or metadata.get("title", ""),
                "artist": custom_info.get("manual_artist") or metadata.get("channel_title", ""),
                "duration": metadata.get("duration", ""),
                "view_count": metadata.get("view_count", 0),
                "published_at": metadata.get("published_at", ""),
                "themes": creative_insight.get("themes", []),
                "genres": custom_info.get("manual_genre", "").split(",") if custom_info.get("manual_genre") else [],
                "mood": custom_info.get("manual_mood", ""),
                "tags": metadata.get("tags", []),
                "creators": creative_insight.get("creators", [])
            }
            
            # 関連度スコア（再生数、いいね数等から算出）
            relevance_score = self._calculate_video_relevance(metadata)
            
            node = KnowledgeNode(
                node_id=f"video_{video_id}",
                node_type="video",
                title=attributes["title"],
                attributes=attributes,
                relevance_score=relevance_score,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
            
            self.knowledge_nodes[node.node_id] = node
            self.graph.add_node(node.node_id, **asdict(node))
    
    def _create_concept_nodes(self):
        """概念ノード作成（アーティスト、ジャンル等）"""
        # アーティスト収集
        artists = defaultdict(list)
        genres = defaultdict(list)
        themes = defaultdict(list)
        
        for node_id, node in self.knowledge_nodes.items():
            if node.node_type == "video":
                attrs = node.attributes
                
                # アーティスト
                artist = attrs.get("artist", "")
                if artist:
                    artists[artist].append(node_id)
                
                # ジャンル
                for genre in attrs.get("genres", []):
                    if genre.strip():
                        genres[genre.strip()].append(node_id)
                
                # テーマ
                for theme in attrs.get("themes", []):
                    if theme.strip():
                        themes[theme.strip()].append(node_id)
        
        # アーティストノード作成
        for artist, video_nodes in artists.items():
            if len(video_nodes) >= 1:  # 最低1つの動画を持つアーティスト
                node = KnowledgeNode(
                    node_id=f"artist_{hashlib.md5(artist.encode()).hexdigest()[:8]}",
                    node_type="artist",
                    title=artist,
                    attributes={
                        "video_count": len(video_nodes),
                        "associated_videos": video_nodes
                    },
                    relevance_score=min(1.0, len(video_nodes) * 0.2),
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat()
                )
                self.knowledge_nodes[node.node_id] = node
                self.graph.add_node(node.node_id, **asdict(node))
        
        # ジャンルノード作成
        for genre, video_nodes in genres.items():
            if len(video_nodes) >= 2:  # 最低2つの動画を持つジャンル
                node = KnowledgeNode(
                    node_id=f"genre_{hashlib.md5(genre.encode()).hexdigest()[:8]}",
                    node_type="genre",
                    title=genre,
                    attributes={
                        "video_count": len(video_nodes),
                        "associated_videos": video_nodes
                    },
                    relevance_score=min(1.0, len(video_nodes) * 0.15),
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat()
                )
                self.knowledge_nodes[node.node_id] = node
                self.graph.add_node(node.node_id, **asdict(node))
        
        # テーマノード作成
        for theme, video_nodes in themes.items():
            if len(video_nodes) >= 2:  # 最低2つの動画を持つテーマ
                node = KnowledgeNode(
                    node_id=f"theme_{hashlib.md5(theme.encode()).hexdigest()[:8]}",
                    node_type="theme",
                    title=theme,
                    attributes={
                        "video_count": len(video_nodes),
                        "associated_videos": video_nodes
                    },
                    relevance_score=min(1.0, len(video_nodes) * 0.1),
                    created_at=datetime.now().isoformat(),
                    updated_at=datetime.now().isoformat()
                )
                self.knowledge_nodes[node.node_id] = node
                self.graph.add_node(node.node_id, **asdict(node))
    
    def _create_conversation_nodes(self):
        """会話ノード作成"""
        conversations = self.conversation_history.get("conversations", {})
        
        for conv_id, conv_data in conversations.items():
            if not conv_data.get("video_ids"):
                continue
            
            node = KnowledgeNode(
                node_id=f"conversation_{conv_id}",
                node_type="conversation",
                title=f"会話_{conv_id}",
                attributes={
                    "video_ids": conv_data.get("video_ids", []),
                    "context": conv_data.get("context", ""),
                    "user_preferences": conv_data.get("user_preferences", {}),
                    "timestamp": conv_data.get("timestamp", "")
                },
                relevance_score=0.3,  # 会話の基本重要度
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
            
            self.knowledge_nodes[node.node_id] = node
            self.graph.add_node(node.node_id, **asdict(node))
    
    def _build_relationships(self):
        """関連性エッジ構築"""
        print("[知識グラフ] 🔗 関連性エッジを構築中...")
        
        # 動画間の関連性
        self._build_video_relationships()
        
        # 動画-概念間の関連性
        self._build_video_concept_relationships()
        
        # 会話-動画間の関連性
        self._build_conversation_relationships()
        
        # 概念間の関連性
        self._build_concept_relationships()
    
    def _build_video_relationships(self):
        """動画間関連性構築"""
        video_nodes = [n for n in self.knowledge_nodes.values() if n.node_type == "video"]
        
        for i, video1 in enumerate(video_nodes):
            for video2 in video_nodes[i+1:]:
                similarity = self._calculate_video_similarity(video1, video2)
                
                if similarity > 0.3:  # 閾値
                    relationship_type = self._determine_video_relationship_type(video1, video2)
                    evidence = self._get_similarity_evidence(video1, video2)
                    
                    edge = KnowledgeEdge(
                        edge_id=f"edge_{video1.node_id}_{video2.node_id}",
                        source_id=video1.node_id,
                        target_id=video2.node_id,
                        relationship_type=relationship_type,
                        strength=similarity,
                        evidence=evidence,
                        created_at=datetime.now().isoformat()
                    )
                    
                    self.knowledge_edges[edge.edge_id] = edge
                    self.graph.add_edge(
                        edge.source_id, 
                        edge.target_id, 
                        weight=edge.strength,
                        relationship_type=edge.relationship_type,
                        edge_data=edge
                    )
    
    def _build_video_concept_relationships(self):
        """動画-概念間関連性構築"""
        video_nodes = [n for n in self.knowledge_nodes.values() if n.node_type == "video"]
        concept_nodes = [n for n in self.knowledge_nodes.values() if n.node_type in ["artist", "genre", "theme"]]
        
        for video in video_nodes:
            for concept in concept_nodes:
                strength = self._calculate_video_concept_strength(video, concept)
                
                if strength > 0.5:  # 閾値
                    relationship_type = f"belongs_to_{concept.node_type}"
                    
                    edge = KnowledgeEdge(
                        edge_id=f"edge_{video.node_id}_{concept.node_id}",
                        source_id=video.node_id,
                        target_id=concept.node_id,
                        relationship_type=relationship_type,
                        strength=strength,
                        evidence=[f"動画が{concept.node_type}: {concept.title}に属する"],
                        created_at=datetime.now().isoformat()
                    )
                    
                    self.knowledge_edges[edge.edge_id] = edge
                    self.graph.add_edge(
                        edge.source_id, 
                        edge.target_id, 
                        weight=edge.strength,
                        relationship_type=edge.relationship_type,
                        edge_data=edge
                    )
    
    def _build_conversation_relationships(self):
        """会話-動画間関連性構築"""
        conversation_nodes = [n for n in self.knowledge_nodes.values() if n.node_type == "conversation"]
        
        for conv in conversation_nodes:
            video_ids = conv.attributes.get("video_ids", [])
            
            for video_id in video_ids:
                video_node_id = f"video_{video_id}"
                if video_node_id in self.knowledge_nodes:
                    edge = KnowledgeEdge(
                        edge_id=f"edge_{conv.node_id}_{video_node_id}",
                        source_id=conv.node_id,
                        target_id=video_node_id,
                        relationship_type="discussed_in_conversation",
                        strength=0.8,
                        evidence=["会話で言及された動画"],
                        created_at=datetime.now().isoformat()
                    )
                    
                    self.knowledge_edges[edge.edge_id] = edge
                    self.graph.add_edge(
                        edge.source_id, 
                        edge.target_id, 
                        weight=edge.strength,
                        relationship_type=edge.relationship_type,
                        edge_data=edge
                    )
    
    def _build_concept_relationships(self):
        """概念間関連性構築"""
        concept_nodes = [n for n in self.knowledge_nodes.values() if n.node_type in ["artist", "genre", "theme"]]
        
        for i, concept1 in enumerate(concept_nodes):
            for concept2 in concept_nodes[i+1:]:
                strength = self._calculate_concept_similarity(concept1, concept2)
                
                if strength > 0.4:  # 閾値
                    relationship_type = "conceptual_similarity"
                    
                    edge = KnowledgeEdge(
                        edge_id=f"edge_{concept1.node_id}_{concept2.node_id}",
                        source_id=concept1.node_id,
                        target_id=concept2.node_id,
                        relationship_type=relationship_type,
                        strength=strength,
                        evidence=[f"{concept1.node_type}と{concept2.node_type}の概念的類似性"],
                        created_at=datetime.now().isoformat()
                    )
                    
                    self.knowledge_edges[edge.edge_id] = edge
                    self.graph.add_edge(
                        edge.source_id, 
                        edge.target_id, 
                        weight=edge.strength,
                        relationship_type=edge.relationship_type,
                        edge_data=edge
                    )
    
    def _calculate_video_relevance(self, metadata: Dict) -> float:
        """動画関連度計算"""
        view_count = metadata.get("view_count", 0)
        like_count = metadata.get("like_count", 0)
        
        # 正規化スコア
        view_score = min(1.0, view_count / 100000)  # 10万再生で1.0
        like_score = min(1.0, like_count / 1000)    # 1000いいねで1.0
        
        return (view_score * 0.7 + like_score * 0.3)
    
    def _calculate_video_similarity(self, video1: KnowledgeNode, video2: KnowledgeNode) -> float:
        """動画間類似度計算"""
        attrs1 = video1.attributes
        attrs2 = video2.attributes
        
        total_score = 0.0
        weights_sum = 0.0
        
        # アーティスト一致
        if attrs1.get("artist") == attrs2.get("artist") and attrs1.get("artist"):
            total_score += self.relationship_weights["same_artist"]
            weights_sum += self.relationship_weights["same_artist"]
        
        # ジャンル一致
        genres1 = set(attrs1.get("genres", []))
        genres2 = set(attrs2.get("genres", []))
        if genres1 and genres2:
            genre_overlap = len(genres1.intersection(genres2)) / len(genres1.union(genres2))
            total_score += genre_overlap * self.relationship_weights["same_genre"]
            weights_sum += self.relationship_weights["same_genre"]
        
        # テーマ一致
        themes1 = set(attrs1.get("themes", []))
        themes2 = set(attrs2.get("themes", []))
        if themes1 and themes2:
            theme_overlap = len(themes1.intersection(themes2)) / len(themes1.union(themes2))
            total_score += theme_overlap * self.relationship_weights["same_theme"]
            weights_sum += self.relationship_weights["same_theme"]
        
        # ムード類似性
        mood1 = attrs1.get("mood", "")
        mood2 = attrs2.get("mood", "")
        if mood1 and mood2:
            mood_similarity = 1.0 if mood1 == mood2 else 0.3
            total_score += mood_similarity * self.relationship_weights["similar_mood"]
            weights_sum += self.relationship_weights["similar_mood"]
        
        return total_score / weights_sum if weights_sum > 0 else 0.0
    
    def _determine_video_relationship_type(self, video1: KnowledgeNode, video2: KnowledgeNode) -> str:
        """動画関係タイプ判定"""
        attrs1 = video1.attributes
        attrs2 = video2.attributes
        
        if attrs1.get("artist") == attrs2.get("artist"):
            return "same_artist"
        
        genres1 = set(attrs1.get("genres", []))
        genres2 = set(attrs2.get("genres", []))
        if genres1.intersection(genres2):
            return "same_genre"
        
        themes1 = set(attrs1.get("themes", []))
        themes2 = set(attrs2.get("themes", []))
        if themes1.intersection(themes2):
            return "same_theme"
        
        return "similarity"
    
    def _get_similarity_evidence(self, video1: KnowledgeNode, video2: KnowledgeNode) -> List[str]:
        """類似性根拠取得"""
        evidence = []
        attrs1 = video1.attributes
        attrs2 = video2.attributes
        
        if attrs1.get("artist") == attrs2.get("artist"):
            evidence.append(f"同じアーティスト: {attrs1.get('artist')}")
        
        common_genres = set(attrs1.get("genres", [])).intersection(set(attrs2.get("genres", [])))
        if common_genres:
            evidence.append(f"共通ジャンル: {', '.join(common_genres)}")
        
        common_themes = set(attrs1.get("themes", [])).intersection(set(attrs2.get("themes", [])))
        if common_themes:
            evidence.append(f"共通テーマ: {', '.join(common_themes)}")
        
        return evidence
    
    def _calculate_video_concept_strength(self, video: KnowledgeNode, concept: KnowledgeNode) -> float:
        """動画-概念間強度計算"""
        video_attrs = video.attributes
        
        if concept.node_type == "artist":
            return 1.0 if video_attrs.get("artist") == concept.title else 0.0
        elif concept.node_type == "genre":
            return 1.0 if concept.title in video_attrs.get("genres", []) else 0.0
        elif concept.node_type == "theme":
            return 1.0 if concept.title in video_attrs.get("themes", []) else 0.0
        
        return 0.0
    
    def _calculate_concept_similarity(self, concept1: KnowledgeNode, concept2: KnowledgeNode) -> float:
        """概念間類似度計算"""
        # 関連動画の重複度
        videos1 = set(concept1.attributes.get("associated_videos", []))
        videos2 = set(concept2.attributes.get("associated_videos", []))
        
        if videos1 and videos2:
            overlap = len(videos1.intersection(videos2))
            union = len(videos1.union(videos2))
            return overlap / union
        
        return 0.0
    
    def _perform_clustering(self):
        """クラスタリング実行"""
        print("[知識グラフ] 🎯 クラスタリング実行中...")
        
        if len(self.graph.nodes) < 3:
            return
        
        try:
            # コミュニティ検出
            communities = nx.algorithms.community.greedy_modularity_communities(self.graph)
            
            for i, community in enumerate(communities):
                if len(community) >= 3:  # 最小クラスターサイズ
                    cluster_id = f"cluster_{i}"
                    
                    # 中心概念抽出
                    central_concepts = self._extract_central_concepts(community)
                    
                    # 結束度計算
                    cohesion_score = self._calculate_cluster_cohesion(community)
                    
                    # クラスタータイプ判定
                    cluster_type = self._determine_cluster_type(community)
                    
                    cluster = GraphCluster(
                        cluster_id=cluster_id,
                        cluster_type=cluster_type,
                        node_ids=list(community),
                        central_concepts=central_concepts,
                        cohesion_score=cohesion_score,
                        description=f"{cluster_type}クラスター（{len(community)}ノード）"
                    )
                    
                    self.clusters[cluster_id] = cluster
            
            print(f"[知識グラフ] 🎯 {len(self.clusters)}個のクラスターを生成")
            
        except Exception as e:
            print(f"[知識グラフ] ⚠️ クラスタリングエラー: {e}")
    
    def _extract_central_concepts(self, community: Set[str]) -> List[str]:
        """中心概念抽出"""
        concepts = []
        
        for node_id in community:
            if node_id in self.knowledge_nodes:
                node = self.knowledge_nodes[node_id]
                if node.node_type in ["artist", "genre", "theme"]:
                    concepts.append(node.title)
        
        return concepts[:3]  # 上位3つ
    
    def _calculate_cluster_cohesion(self, community: Set[str]) -> float:
        """クラスター結束度計算"""
        if len(community) < 2:
            return 0.0
        
        # クラスター内エッジ数
        internal_edges = 0
        total_possible_edges = len(community) * (len(community) - 1) / 2
        
        for node1 in community:
            for node2 in community:
                if node1 != node2 and self.graph.has_edge(node1, node2):
                    internal_edges += 1
        
        return internal_edges / total_possible_edges if total_possible_edges > 0 else 0.0
    
    def _determine_cluster_type(self, community: Set[str]) -> str:
        """クラスタータイプ判定"""
        node_types = []
        
        for node_id in community:
            if node_id in self.knowledge_nodes:
                node_types.append(self.knowledge_nodes[node_id].node_type)
        
        type_counts = Counter(node_types)
        most_common = type_counts.most_common(1)
        
        if most_common:
            dominant_type = most_common[0][0]
            if dominant_type == "video":
                return "video_cluster"
            elif dominant_type == "artist":
                return "artist_cluster"
            elif dominant_type == "genre":
                return "genre_cluster"
            elif dominant_type == "theme":
                return "theme_cluster"
        
        return "mixed_cluster"
    
    def _save_graph_data(self):
        """グラフデータ保存"""
        try:
            graph_data = {
                "nodes": {nid: asdict(node) for nid, node in self.knowledge_nodes.items()},
                "edges": {eid: asdict(edge) for eid, edge in self.knowledge_edges.items()},
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "node_count": len(self.knowledge_nodes),
                    "edge_count": len(self.knowledge_edges)
                }
            }
            
            with open(self.graph_data_path, 'w', encoding='utf-8') as f:
                json.dump(graph_data, f, ensure_ascii=False, indent=2)
            
            # クラスターデータ保存
            cluster_data = {
                "clusters": {cid: asdict(cluster) for cid, cluster in self.clusters.items()},
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "cluster_count": len(self.clusters)
                }
            }
            
            with open(self.clusters_path, 'w', encoding='utf-8') as f:
                json.dump(cluster_data, f, ensure_ascii=False, indent=2)
            
            print("[知識グラフ] 💾 グラフデータを保存しました")
            
        except Exception as e:
            print(f"[知識グラフ] ❌ データ保存エラー: {e}")
    
    def _update_statistics(self):
        """統計情報更新"""
        self.graph_statistics.update({
            "total_nodes": len(self.knowledge_nodes),
            "total_edges": len(self.knowledge_edges),
            "clusters_count": len(self.clusters),
            "last_rebuild": datetime.now().isoformat(),
            "coverage_rate": self._calculate_coverage_rate()
        })
    
    def _calculate_coverage_rate(self) -> float:
        """カバレッジ率計算"""
        total_videos = len(self.knowledge_db.get("videos", {}))
        video_nodes = len([n for n in self.knowledge_nodes.values() if n.node_type == "video"])
        
        return video_nodes / total_videos if total_videos > 0 else 0.0
    
    def find_related_content(self, video_id: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """関連コンテンツ検索"""
        node_id = f"video_{video_id}"
        
        if node_id not in self.graph.nodes:
            return []
        
        # 直接接続されたノード
        neighbors = list(self.graph.neighbors(node_id))
        
        # 関連度でソート
        related_items = []
        
        for neighbor_id in neighbors:
            if neighbor_id in self.knowledge_nodes:
                neighbor = self.knowledge_nodes[neighbor_id]
                edge_data = self.graph.get_edge_data(node_id, neighbor_id)
                
                related_items.append({
                    "node_id": neighbor_id,
                    "title": neighbor.title,
                    "type": neighbor.node_type,
                    "relevance": edge_data.get("weight", 0.0),
                    "relationship": edge_data.get("relationship_type", ""),
                    "evidence": edge_data.get("edge_data", {}).get("evidence", [])
                })
        
        # 関連度でソート
        related_items.sort(key=lambda x: x["relevance"], reverse=True)
        
        return related_items[:max_results]
    
    def get_cluster_recommendations(self, video_id: str) -> List[Dict[str, Any]]:
        """クラスター基準推薦"""
        node_id = f"video_{video_id}"
        recommendations = []
        
        # ノードが属するクラスターを見つける
        for cluster in self.clusters.values():
            if node_id in cluster.node_ids:
                # 同じクラスター内の他の動画を推薦
                for other_node_id in cluster.node_ids:
                    if other_node_id != node_id and other_node_id in self.knowledge_nodes:
                        other_node = self.knowledge_nodes[other_node_id]
                        if other_node.node_type == "video":
                            recommendations.append({
                                "node_id": other_node_id,
                                "title": other_node.title,
                                "cluster_type": cluster.cluster_type,
                                "cohesion_score": cluster.cohesion_score,
                                "central_concepts": cluster.central_concepts
                            })
                break
        
        return recommendations
    
    def get_graph_statistics(self) -> Dict[str, Any]:
        """グラフ統計情報取得"""
        return dict(self.graph_statistics)
    
    def analyze_knowledge_patterns(self) -> Dict[str, Any]:
        """知識パターン分析"""
        patterns = {
            "popular_artists": [],
            "dominant_genres": [],
            "common_themes": [],
            "cluster_analysis": {},
            "connectivity_analysis": {}
        }
        
        # 人気アーティスト
        artist_nodes = [n for n in self.knowledge_nodes.values() if n.node_type == "artist"]
        artist_nodes.sort(key=lambda x: x.attributes.get("video_count", 0), reverse=True)
        patterns["popular_artists"] = [
            {"name": n.title, "video_count": n.attributes.get("video_count", 0)}
            for n in artist_nodes[:10]
        ]
        
        # 支配的ジャンル
        genre_nodes = [n for n in self.knowledge_nodes.values() if n.node_type == "genre"]
        genre_nodes.sort(key=lambda x: x.attributes.get("video_count", 0), reverse=True)
        patterns["dominant_genres"] = [
            {"name": n.title, "video_count": n.attributes.get("video_count", 0)}
            for n in genre_nodes[:10]
        ]
        
        # 一般的テーマ
        theme_nodes = [n for n in self.knowledge_nodes.values() if n.node_type == "theme"]
        theme_nodes.sort(key=lambda x: x.attributes.get("video_count", 0), reverse=True)
        patterns["common_themes"] = [
            {"name": n.title, "video_count": n.attributes.get("video_count", 0)}
            for n in theme_nodes[:10]
        ]
        
        # クラスター分析
        patterns["cluster_analysis"] = {
            "total_clusters": len(self.clusters),
            "cluster_types": Counter([c.cluster_type for c in self.clusters.values()]),
            "average_cohesion": sum(c.cohesion_score for c in self.clusters.values()) / len(self.clusters) if self.clusters else 0
        }
        
        # 接続性分析
        if self.graph.number_of_nodes() > 0:
            patterns["connectivity_analysis"] = {
                "density": nx.density(self.graph),
                "average_clustering": nx.average_clustering(self.graph),
                "number_of_components": nx.number_connected_components(self.graph)
            }
        
        return patterns
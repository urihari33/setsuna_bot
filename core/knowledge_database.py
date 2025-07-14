#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KnowledgeDatabase - Phase 2A-2
階層的知識蓄積・管理システム
"""

import json
import os
import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import uuid
from collections import defaultdict
import re

# Windows環境のパス設定
if os.name == 'nt':
    DATA_DIR = Path("D:/setsuna_bot/data/activity_knowledge")
else:
    DATA_DIR = Path("/mnt/d/setsuna_bot/data/activity_knowledge")

@dataclass
class KnowledgeItem:
    """知識アイテムデータクラス"""
    item_id: str
    session_id: str
    layer: str  # "raw", "structured", "integrated"
    content: str
    source_url: Optional[str] = None
    reliability_score: float = 0.7
    importance_score: float = 0.5
    categories: List[str] = None
    keywords: List[str] = None
    entities: List[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    references: List[str] = None
    
    def __post_init__(self):
        if self.categories is None:
            self.categories = []
        if self.keywords is None:
            self.keywords = []
        if self.entities is None:
            self.entities = []
        if self.references is None:
            self.references = []
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

@dataclass
class KnowledgeEntity:
    """知識エンティティ"""
    entity_id: str
    name: str
    type: str  # "技術", "企業", "製品", "人物", "概念"
    description: str
    aliases: List[str] = None
    first_discovered: Optional[str] = None  # セッションID
    last_updated: Optional[str] = None
    frequency: int = 0
    importance_score: float = 0.5
    categories: List[str] = None
    related_sessions: List[str] = None
    activity_relevance: Dict[str, float] = None
    
    def __post_init__(self):
        if self.aliases is None:
            self.aliases = []
        if self.categories is None:
            self.categories = []
        if self.related_sessions is None:
            self.related_sessions = []
        if self.activity_relevance is None:
            self.activity_relevance = {}

class KnowledgeDatabase:
    """知識データベースメインクラス"""
    
    def __init__(self):
        """初期化"""
        self.knowledge_dir = DATA_DIR / "knowledge_graph"
        self.knowledge_dir.mkdir(parents=True, exist_ok=True)
        
        # データファイル
        self.entities_file = self.knowledge_dir / "entities.json"
        self.relationships_file = self.knowledge_dir / "relationships.json"
        self.categories_file = self.knowledge_dir / "categories.json"
        
        # SQLiteインデックス
        self.db_file = self.knowledge_dir / "knowledge_index.db"
        
        # メモリ内データ
        self.knowledge_items: Dict[str, KnowledgeItem] = {}
        self.entities: Dict[str, KnowledgeEntity] = {}
        self.relationships: List[Dict] = []
        self.categories: Dict[str, List[str]] = defaultdict(list)
        
        # 設定
        self.config = {
            "max_knowledge_items": 10000,
            "min_reliability_score": 0.3,
            "entity_extraction_threshold": 0.6,
            "auto_backup_interval": 24,  # 時間
            "cleanup_old_items_days": 180
        }
        
        self._initialize_database()
        self._load_existing_data()
        
        print("[知識DB] ✅ KnowledgeDatabase初期化完了")
    
    def _initialize_database(self):
        """SQLiteデータベース初期化"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # 知識アイテムテーブル
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS knowledge_items (
                    item_id TEXT PRIMARY KEY,
                    session_id TEXT,
                    layer TEXT,
                    content TEXT,
                    categories TEXT,
                    keywords TEXT,
                    entities TEXT,
                    reliability_score REAL,
                    importance_score REAL,
                    created_at TEXT,
                    updated_at TEXT
                )
            """)
            
            # エンティティテーブル
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS entities (
                    entity_id TEXT PRIMARY KEY,
                    name TEXT,
                    type TEXT,
                    description TEXT,
                    frequency INTEGER,
                    importance_score REAL,
                    categories TEXT,
                    created_at TEXT
                )
            """)
            
            # 関係性テーブル
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS relationships (
                    relationship_id TEXT PRIMARY KEY,
                    source_entity TEXT,
                    target_entity TEXT,
                    relationship_type TEXT,
                    strength REAL,
                    discovered_in TEXT,
                    confidence REAL
                )
            """)
            
            # インデックス作成
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_knowledge_session ON knowledge_items(session_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_knowledge_layer ON knowledge_items(layer)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_knowledge_categories ON knowledge_items(categories)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_entity_name ON entities(name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_entity_type ON entities(type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_relationship_source ON relationships(source_entity)")
            
            conn.commit()
            conn.close()
            
            print("[知識DB] ✅ SQLiteデータベース初期化完了")
            
        except Exception as e:
            print(f"[知識DB] ❌ データベース初期化失敗: {e}")
    
    def _load_existing_data(self):
        """既存データの読み込み"""
        try:
            # エンティティデータ読み込み
            if self.entities_file.exists():
                with open(self.entities_file, 'r', encoding='utf-8') as f:
                    entities_data = json.load(f)
                    for entity_data in entities_data.get("entities", []):
                        entity = KnowledgeEntity(**entity_data)
                        self.entities[entity.entity_id] = entity
                
                print(f"[知識DB] 📚 エンティティ読み込み: {len(self.entities)}件")
            
            # 関係性データ読み込み
            if self.relationships_file.exists():
                with open(self.relationships_file, 'r', encoding='utf-8') as f:
                    relationships_data = json.load(f)
                    self.relationships = relationships_data.get("relationships", [])
                
                print(f"[知識DB] 🔗 関係性読み込み: {len(self.relationships)}件")
            
            # カテゴリデータ読み込み
            if self.categories_file.exists():
                with open(self.categories_file, 'r', encoding='utf-8') as f:
                    categories_data = json.load(f)
                    self.categories = defaultdict(list, categories_data.get("categories", {}))
                
                print(f"[知識DB] 📂 カテゴリ読み込み: {len(self.categories)}件")
            
        except Exception as e:
            print(f"[知識DB] ⚠️ 既存データ読み込み失敗: {e}")
    
    def store_knowledge_item(self, 
                           session_id: str,
                           layer: str,
                           content: str,
                           source_url: Optional[str] = None,
                           reliability_score: float = 0.7,
                           importance_score: float = 0.5,
                           categories: List[str] = None,
                           keywords: List[str] = None,
                           entities: List[str] = None) -> str:
        """
        知識アイテムを保存
        
        Args:
            session_id: セッションID
            layer: データ層 ("raw", "structured", "integrated")
            content: 知識内容
            source_url: ソースURL
            reliability_score: 信頼性スコア
            importance_score: 重要度スコア
            categories: カテゴリリスト
            keywords: キーワードリスト
            entities: エンティティリスト
            
        Returns:
            知識アイテムID
        """
        try:
            # 重複チェック
            content_hash = hashlib.sha256(content.encode()).hexdigest()[:16]
            item_id = f"know_{layer}_{content_hash}"
            
            if item_id in self.knowledge_items:
                print(f"[知識DB] ⚠️ 重複知識アイテム: {item_id}")
                return item_id
            
            # 知識アイテム作成
            knowledge_item = KnowledgeItem(
                item_id=item_id,
                session_id=session_id,
                layer=layer,
                content=content,
                source_url=source_url,
                reliability_score=reliability_score,
                importance_score=importance_score,
                categories=categories or [],
                keywords=keywords or [],
                entities=entities or []
            )
            
            # メモリ内保存
            self.knowledge_items[item_id] = knowledge_item
            
            # SQLite保存
            self._save_knowledge_item_to_db(knowledge_item)
            
            # カテゴリ更新
            for category in knowledge_item.categories:
                if item_id not in self.categories[category]:
                    self.categories[category].append(item_id)
            
            print(f"[知識DB] 💾 知識アイテム保存: {item_id} ({layer}層)")
            return item_id
            
        except Exception as e:
            print(f"[知識DB] ❌ 知識アイテム保存失敗: {e}")
            return ""
    
    def _save_knowledge_item_to_db(self, item: KnowledgeItem):
        """知識アイテムをSQLiteに保存"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO knowledge_items 
                (item_id, session_id, layer, content, categories, keywords, entities,
                 reliability_score, importance_score, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                item.item_id,
                item.session_id,
                item.layer,
                item.content,
                json.dumps(item.categories, ensure_ascii=False),
                json.dumps(item.keywords, ensure_ascii=False),
                json.dumps(item.entities, ensure_ascii=False),
                item.reliability_score,
                item.importance_score,
                item.created_at.isoformat(),
                item.updated_at.isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"[知識DB] ❌ SQLite保存失敗: {e}")
    
    def store_entity(self,
                    name: str,
                    entity_type: str,
                    description: str,
                    session_id: str,
                    aliases: List[str] = None,
                    categories: List[str] = None,
                    importance_score: float = 0.5) -> str:
        """
        エンティティを保存・更新
        
        Args:
            name: エンティティ名
            entity_type: エンティティタイプ
            description: 説明
            session_id: 発見セッションID
            aliases: 別名リスト
            categories: カテゴリリスト
            importance_score: 重要度スコア
            
        Returns:
            エンティティID
        """
        try:
            # 既存エンティティチェック
            entity_id = None
            for eid, entity in self.entities.items():
                if entity.name.lower() == name.lower() or name.lower() in [alias.lower() for alias in entity.aliases]:
                    entity_id = eid
                    break
            
            if entity_id:
                # 既存エンティティ更新
                entity = self.entities[entity_id]
                entity.frequency += 1
                entity.last_updated = session_id
                entity.description = description  # より詳細な説明で上書き
                if session_id not in entity.related_sessions:
                    entity.related_sessions.append(session_id)
                
                print(f"[知識DB] 🔄 エンティティ更新: {name} (頻度: {entity.frequency})")
            else:
                # 新規エンティティ作成
                entity_id = f"ent_{hashlib.sha256(name.encode()).hexdigest()[:12]}"
                
                entity = KnowledgeEntity(
                    entity_id=entity_id,
                    name=name,
                    type=entity_type,
                    description=description,
                    aliases=aliases or [],
                    first_discovered=session_id,
                    last_updated=session_id,
                    frequency=1,
                    importance_score=importance_score,
                    categories=categories or [],
                    related_sessions=[session_id]
                )
                
                self.entities[entity_id] = entity
                print(f"[知識DB] ✨ 新規エンティティ: {name}")
            
            # SQLite保存
            self._save_entity_to_db(entity)
            
            return entity_id
            
        except Exception as e:
            print(f"[知識DB] ❌ エンティティ保存失敗: {e}")
            return ""
    
    def _save_entity_to_db(self, entity: KnowledgeEntity):
        """エンティティをSQLiteに保存"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO entities
                (entity_id, name, type, description, frequency, importance_score, categories, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                entity.entity_id,
                entity.name,
                entity.type,
                entity.description,
                entity.frequency,
                entity.importance_score,
                json.dumps(entity.categories, ensure_ascii=False),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"[知識DB] ❌ エンティティSQLite保存失敗: {e}")
    
    def store_relationship(self,
                          source_entity: str,
                          target_entity: str,
                          relationship_type: str,
                          strength: float,
                          session_id: str,
                          supporting_evidence: List[str] = None,
                          confidence: float = 0.8) -> str:
        """
        関係性を保存
        
        Args:
            source_entity: ソースエンティティID
            target_entity: ターゲットエンティティID
            relationship_type: 関係性タイプ
            strength: 関係性の強さ
            session_id: 発見セッションID
            supporting_evidence: 支持証拠
            confidence: 信頼度
            
        Returns:
            関係性ID
        """
        try:
            relationship_id = f"rel_{source_entity}_{target_entity}_{relationship_type}"
            
            # 既存関係性チェック
            existing_rel = None
            for rel in self.relationships:
                if (rel["source_entity"] == source_entity and 
                    rel["target_entity"] == target_entity and
                    rel["relationship_type"] == relationship_type):
                    existing_rel = rel
                    break
            
            if existing_rel:
                # 既存関係性強化
                existing_rel["strength"] = min(1.0, existing_rel["strength"] + (strength * 0.1))
                existing_rel["confidence"] = max(existing_rel["confidence"], confidence)
                existing_rel["reinforced_in"].append(session_id)
                print(f"[知識DB] 🔗 関係性強化: {relationship_type}")
            else:
                # 新規関係性作成
                relationship = {
                    "relationship_id": relationship_id,
                    "source_entity": source_entity,
                    "target_entity": target_entity,
                    "relationship_type": relationship_type,
                    "strength": strength,
                    "direction": "directional",
                    "discovered_in": session_id,
                    "reinforced_in": [session_id],
                    "supporting_evidence": supporting_evidence or [],
                    "confidence": confidence
                }
                
                self.relationships.append(relationship)
                print(f"[知識DB] ✨ 新規関係性: {source_entity} -{relationship_type}-> {target_entity}")
            
            # SQLite保存
            self._save_relationship_to_db(relationship_id, source_entity, target_entity, 
                                        relationship_type, strength, session_id, confidence)
            
            return relationship_id
            
        except Exception as e:
            print(f"[知識DB] ❌ 関係性保存失敗: {e}")
            return ""
    
    def _save_relationship_to_db(self, rel_id: str, source: str, target: str, 
                               rel_type: str, strength: float, session_id: str, confidence: float):
        """関係性をSQLiteに保存"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO relationships
                (relationship_id, source_entity, target_entity, relationship_type, 
                 strength, discovered_in, confidence)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (rel_id, source, target, rel_type, strength, session_id, confidence))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"[知識DB] ❌ 関係性SQLite保存失敗: {e}")
    
    def search_knowledge(self,
                        query: str,
                        layer: Optional[str] = None,
                        categories: List[str] = None,
                        min_importance: float = 0.0,
                        limit: int = 10) -> List[Dict]:
        """
        知識検索
        
        Args:
            query: 検索クエリ
            layer: データ層フィルタ
            categories: カテゴリフィルタ
            min_importance: 最小重要度
            limit: 結果制限数
            
        Returns:
            検索結果リスト
        """
        try:
            results = []
            query_lower = query.lower()
            
            for item_id, item in self.knowledge_items.items():
                # 層フィルタ
                if layer and item.layer != layer:
                    continue
                
                # 重要度フィルタ
                if item.importance_score < min_importance:
                    continue
                
                # カテゴリフィルタ
                if categories and not any(cat in item.categories for cat in categories):
                    continue
                
                # テキスト検索
                relevance_score = 0.0
                
                # コンテンツ内検索
                if query_lower in item.content.lower():
                    relevance_score += 0.8
                
                # キーワード検索
                for keyword in item.keywords:
                    if query_lower in keyword.lower():
                        relevance_score += 0.6
                
                # エンティティ検索
                for entity in item.entities:
                    if query_lower in entity.lower():
                        relevance_score += 0.7
                
                if relevance_score > 0:
                    results.append({
                        "item": asdict(item),
                        "relevance_score": relevance_score,
                        "combined_score": relevance_score * item.importance_score
                    })
            
            # スコア順でソート
            results.sort(key=lambda x: x["combined_score"], reverse=True)
            
            print(f"[知識DB] 🔍 検索結果: {len(results[:limit])}件 (クエリ: {query})")
            return results[:limit]
            
        except Exception as e:
            print(f"[知識DB] ❌ 知識検索失敗: {e}")
            return []
    
    def get_entity_knowledge_graph(self, entity_name: str, depth: int = 2) -> Dict:
        """
        エンティティ中心の知識グラフ取得
        
        Args:
            entity_name: エンティティ名
            depth: 関係性の深度
            
        Returns:
            知識グラフデータ
        """
        try:
            # エンティティ検索
            target_entity = None
            for entity in self.entities.values():
                if (entity.name.lower() == entity_name.lower() or 
                    entity_name.lower() in [alias.lower() for alias in entity.aliases]):
                    target_entity = entity
                    break
            
            if not target_entity:
                return {"error": f"エンティティ未発見: {entity_name}"}
            
            # 関係性抽出
            connected_entities = set()
            relationships = []
            
            for rel in self.relationships:
                if (rel["source_entity"] == target_entity.entity_id or 
                    rel["target_entity"] == target_entity.entity_id):
                    relationships.append(rel)
                    connected_entities.add(rel["source_entity"])
                    connected_entities.add(rel["target_entity"])
            
            # 関連エンティティ情報
            entities_info = {}
            for entity_id in connected_entities:
                if entity_id in self.entities:
                    entities_info[entity_id] = asdict(self.entities[entity_id])
            
            knowledge_graph = {
                "center_entity": asdict(target_entity),
                "connected_entities": entities_info,
                "relationships": relationships,
                "total_connections": len(relationships),
                "entity_count": len(connected_entities)
            }
            
            print(f"[知識DB] 🕸️ 知識グラフ生成: {entity_name} ({len(relationships)}関係)")
            return knowledge_graph
            
        except Exception as e:
            print(f"[知識DB] ❌ 知識グラフ生成失敗: {e}")
            return {"error": str(e)}
    
    def get_session_knowledge_summary(self, session_id: str) -> Dict:
        """
        セッション別知識サマリー
        
        Args:
            session_id: セッションID
            
        Returns:
            知識サマリー
        """
        try:
            session_items = [item for item in self.knowledge_items.values() 
                           if item.session_id == session_id]
            
            session_entities = [entity for entity in self.entities.values()
                              if session_id in entity.related_sessions]
            
            session_relationships = [rel for rel in self.relationships
                                   if rel["discovered_in"] == session_id]
            
            # 層別統計
            layer_stats = defaultdict(int)
            for item in session_items:
                layer_stats[item.layer] += 1
            
            # カテゴリ別統計
            category_stats = defaultdict(int)
            for item in session_items:
                for category in item.categories:
                    category_stats[category] += 1
            
            summary = {
                "session_id": session_id,
                "total_knowledge_items": len(session_items),
                "total_entities": len(session_entities),
                "total_relationships": len(session_relationships),
                "layer_distribution": dict(layer_stats),
                "category_distribution": dict(category_stats),
                "top_entities": [
                    {"name": e.name, "type": e.type, "frequency": e.frequency}
                    for e in sorted(session_entities, key=lambda x: x.frequency, reverse=True)[:5]
                ],
                "average_importance": sum(item.importance_score for item in session_items) / len(session_items) if session_items else 0,
                "average_reliability": sum(item.reliability_score for item in session_items) / len(session_items) if session_items else 0
            }
            
            print(f"[知識DB] 📊 セッションサマリー: {session_id}")
            return summary
            
        except Exception as e:
            print(f"[知識DB] ❌ セッションサマリー生成失敗: {e}")
            return {"error": str(e)}
    
    def backup_knowledge_data(self) -> bool:
        """知識データのバックアップ"""
        try:
            backup_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = self.knowledge_dir / "backups" / backup_timestamp
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # エンティティデータ保存
            entities_data = {
                "entities": [asdict(entity) for entity in self.entities.values()],
                "entity_statistics": {
                    "total_entities": len(self.entities),
                    "by_type": self._get_entity_type_stats(),
                    "by_importance": self._get_entity_importance_stats()
                },
                "backup_timestamp": datetime.now().isoformat()
            }
            
            with open(backup_dir / "entities.json", 'w', encoding='utf-8') as f:
                json.dump(entities_data, f, ensure_ascii=False, indent=2, default=str)
            
            # 関係性データ保存
            relationships_data = {
                "relationships": self.relationships,
                "relationship_types": self._get_relationship_types(),
                "backup_timestamp": datetime.now().isoformat()
            }
            
            with open(backup_dir / "relationships.json", 'w', encoding='utf-8') as f:
                json.dump(relationships_data, f, ensure_ascii=False, indent=2, default=str)
            
            # カテゴリデータ保存
            categories_data = {
                "categories": dict(self.categories),
                "backup_timestamp": datetime.now().isoformat()
            }
            
            with open(backup_dir / "categories.json", 'w', encoding='utf-8') as f:
                json.dump(categories_data, f, ensure_ascii=False, indent=2, default=str)
            
            print(f"[知識DB] 💾 バックアップ完了: {backup_timestamp}")
            return True
            
        except Exception as e:
            print(f"[知識DB] ❌ バックアップ失敗: {e}")
            return False
    
    def _get_entity_type_stats(self) -> Dict[str, int]:
        """エンティティタイプ別統計"""
        type_stats = defaultdict(int)
        for entity in self.entities.values():
            type_stats[entity.type] += 1
        return dict(type_stats)
    
    def _get_entity_importance_stats(self) -> Dict[str, int]:
        """エンティティ重要度別統計"""
        importance_stats = {"high": 0, "medium": 0, "low": 0}
        for entity in self.entities.values():
            if entity.importance_score >= 0.8:
                importance_stats["high"] += 1
            elif entity.importance_score >= 0.5:
                importance_stats["medium"] += 1
            else:
                importance_stats["low"] += 1
        return importance_stats
    
    def _get_relationship_types(self) -> Dict[str, str]:
        """関係性タイプ一覧"""
        return {
            "enables": "技術的実現関係",
            "competes_with": "競合関係",
            "depends_on": "依存関係",
            "part_of": "包含関係",
            "similar_to": "類似関係",
            "developed_by": "開発関係",
            "used_in": "使用関係"
        }
    
    def cleanup_old_data(self, days: int = 180) -> int:
        """古いデータのクリーンアップ"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            removed_count = 0
            
            # 古い知識アイテム削除
            items_to_remove = []
            for item_id, item in self.knowledge_items.items():
                if item.created_at < cutoff_date and item.importance_score < 0.3:
                    items_to_remove.append(item_id)
            
            for item_id in items_to_remove:
                del self.knowledge_items[item_id]
                removed_count += 1
            
            print(f"[知識DB] 🗑️ クリーンアップ完了: {removed_count}件削除")
            return removed_count
            
        except Exception as e:
            print(f"[知識DB] ❌ クリーンアップ失敗: {e}")
            return 0
    
    def get_database_statistics(self) -> Dict:
        """データベース統計情報"""
        return {
            "knowledge_items": len(self.knowledge_items),
            "entities": len(self.entities),
            "relationships": len(self.relationships),
            "categories": len(self.categories),
            "total_storage_mb": self._calculate_storage_size(),
            "last_backup": self._get_last_backup_time(),
            "entity_type_distribution": self._get_entity_type_stats(),
            "layer_distribution": self._get_layer_stats()
        }
    
    def _calculate_storage_size(self) -> float:
        """ストレージサイズ計算"""
        try:
            total_size = 0
            for file_path in self.knowledge_dir.rglob("*.json"):
                total_size += file_path.stat().st_size
            return total_size / (1024 * 1024)  # MB
        except:
            return 0.0
    
    def _get_last_backup_time(self) -> Optional[str]:
        """最後のバックアップ時間"""
        try:
            backup_dir = self.knowledge_dir / "backups"
            if backup_dir.exists():
                backup_dirs = [d for d in backup_dir.iterdir() if d.is_dir()]
                if backup_dirs:
                    latest_backup = max(backup_dirs, key=lambda x: x.name)
                    return latest_backup.name
        except:
            pass
        return None
    
    def _get_layer_stats(self) -> Dict[str, int]:
        """層別統計"""
        layer_stats = defaultdict(int)
        for item in self.knowledge_items.values():
            layer_stats[item.layer] += 1
        return dict(layer_stats)


# テスト用コード
if __name__ == "__main__":
    print("=== KnowledgeDatabase テスト ===")
    
    db = KnowledgeDatabase()
    
    # テスト知識アイテム追加
    print("\n📝 知識アイテム追加テスト:")
    item_id = db.store_knowledge_item(
        session_id="test_session_001",
        layer="structured",
        content="AIによる音楽生成技術は2024年に大きく進歩している",
        categories=["AI技術", "音楽"],
        keywords=["AI", "音楽生成", "2024"],
        entities=["AI技術", "音楽生成"],
        importance_score=0.8,
        reliability_score=0.9
    )
    print(f"✅ 保存完了: {item_id}")
    
    # テストエンティティ追加
    print("\n🏷️ エンティティ追加テスト:")
    entity_id = db.store_entity(
        name="Transformer",
        entity_type="技術",
        description="注意機構を使った深層学習アーキテクチャ",
        session_id="test_session_001",
        aliases=["トランスフォーマー", "Attention機構"],
        categories=["AI技術", "深層学習"],
        importance_score=0.9
    )
    print(f"✅ エンティティ保存: {entity_id}")
    
    # 検索テスト
    print("\n🔍 知識検索テスト:")
    results = db.search_knowledge("音楽生成", limit=5)
    print(f"✅ 検索結果: {len(results)}件")
    for result in results:
        print(f"  - {result['item']['content'][:50]}... (関連度: {result['relevance_score']:.2f})")
    
    # 統計情報表示
    print("\n📊 データベース統計:")
    stats = db.get_database_statistics()
    print(f"  知識アイテム: {stats['knowledge_items']}件")
    print(f"  エンティティ: {stats['entities']}件")
    print(f"  関係性: {stats['relationships']}件")
    print(f"  ストレージ: {stats['total_storage_mb']:.2f}MB")
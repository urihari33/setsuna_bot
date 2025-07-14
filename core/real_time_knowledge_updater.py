#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
リアルタイム知識更新システム - Phase 2E実装
会話中の新情報自動検出・抽出・動的知識ベース更新
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from datetime import datetime, timedelta
import re
import hashlib
import difflib

# プロジェクトルートをパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 関連システム
try:
    from core.knowledge_graph_system import KnowledgeGraphSystem
    from core.semantic_search_engine import SemanticSearchEngine
    DEPENDENCIES_AVAILABLE = True
except ImportError:
    DEPENDENCIES_AVAILABLE = False

# Windowsパス設定
if os.name == 'nt':
    DATA_DIR = Path("D:/setsuna_bot/youtube_knowledge_system/data")
    UPDATE_CACHE_DIR = Path("D:/setsuna_bot/realtime_update_cache")
else:
    DATA_DIR = Path("/mnt/d/setsuna_bot/youtube_knowledge_system/data")
    UPDATE_CACHE_DIR = Path("/mnt/d/setsuna_bot/realtime_update_cache")

UPDATE_CACHE_DIR.mkdir(parents=True, exist_ok=True)

@dataclass
class NewInformation:
    """新情報データクラス"""
    info_id: str
    content: str
    info_type: str              # "artist", "song", "genre", "fact", "opinion", "relationship"
    confidence: float
    source_context: str
    extraction_method: str
    related_entities: List[str]
    validation_status: str      # "pending", "validated", "rejected"
    detected_at: str

@dataclass
class KnowledgeUpdate:
    """知識更新データクラス"""
    update_id: str
    target_entity: str
    update_type: str            # "add", "modify", "enhance", "correct"
    old_value: Optional[Any]
    new_value: Any
    confidence: float
    supporting_evidence: List[str]
    impact_score: float         # 更新の重要度
    applied_at: Optional[str]

@dataclass
class ConflictResolution:
    """矛盾解決データクラス"""
    conflict_id: str
    conflicting_info: List[str]
    resolution_strategy: str    # "merge", "replace", "flag", "ignore"
    resolution_reasoning: str
    confidence: float
    resolved_at: str

class RealTimeKnowledgeUpdater:
    """リアルタイム知識更新システムクラス"""
    
    def __init__(self):
        """初期化"""
        # データパス
        self.knowledge_db_path = DATA_DIR / "unified_knowledge_db.json"
        self.new_information_path = UPDATE_CACHE_DIR / "new_information.json"
        self.knowledge_updates_path = UPDATE_CACHE_DIR / "knowledge_updates.json"
        self.conflict_resolutions_path = UPDATE_CACHE_DIR / "conflict_resolutions.json"
        self.update_log_path = UPDATE_CACHE_DIR / "update_log.json"
        
        # 依存システム
        if DEPENDENCIES_AVAILABLE:
            self.knowledge_graph = KnowledgeGraphSystem()
            self.semantic_search = SemanticSearchEngine()
        else:
            self.knowledge_graph = None
            self.semantic_search = None
            print("[リアルタイム更新] ⚠️ 依存システムが利用できません")
        
        # データ
        self.knowledge_db = {}
        self.new_information = deque(maxlen=1000)
        self.pending_updates = {}
        self.conflict_resolutions = {}
        self.update_log = []
        
        # リアルタイム処理用
        self.current_session_info = []
        self.information_buffer = deque(maxlen=50)
        self.last_update_time = datetime.now()
        
        # 更新パラメータ
        self.confidence_threshold = 0.7    # 自動更新信頼度閾値
        self.validation_threshold = 0.9    # 検証要求閾値
        self.conflict_threshold = 0.5      # 矛盾検出閾値
        self.update_batch_size = 10        # バッチ更新サイズ
        
        # 情報抽出パターン
        self.extraction_patterns = self._build_extraction_patterns()
        self.entity_patterns = self._build_entity_patterns()
        self.relationship_patterns = self._build_relationship_patterns()
        
        # 統計情報
        self.update_statistics = {
            "total_info_detected": 0,
            "total_updates_applied": 0,
            "conflicts_resolved": 0,
            "validation_requests": 0,
            "last_update_batch": None
        }
        
        self._load_existing_data()
        print("[リアルタイム更新] ✅ リアルタイム知識更新システム初期化完了")
    
    def _build_extraction_patterns(self) -> Dict[str, List[str]]:
        """情報抽出パターン構築"""
        return {
            "artist_info": [
                r"(.+)(は|が)(アーティスト|歌手|ミュージシャン|バンド)",
                r"(.+)(の)(新曲|アルバム|シングル)",
                r"(.+)(が)(歌って|作って|制作した)"
            ],
            "song_info": [
                r"(.+)(という|っていう)(曲|歌|楽曲)",
                r"(.+)(の)(テーマ|歌詞|メロディ)",
                r"(.+)(は|が)(人気|有名|話題)"
            ],
            "genre_info": [
                r"(.+)(は|が)(.+)(系|風|っぽい)",
                r"(.+)(ジャンル|スタイル|カテゴリ)",
                r"(.+)(ロック|ポップ|クラシック|ボカロ)"
            ],
            "factual_info": [
                r"(.+)(は|が)(発売|リリース|公開)された",
                r"(.+)(年|月|日)に(.+)",
                r"(.+)(回|万|億)(再生|視聴|ダウンロード)"
            ],
            "opinion_info": [
                r"(.+)(と思う|感じる|考える)",
                r"(.+)(好き|嫌い|気に入った)",
                r"(.+)(おすすめ|推薦|提案)"
            ]
        }
    
    def _build_entity_patterns(self) -> Dict[str, List[str]]:
        """エンティティパターン構築"""
        return {
            "artist_names": [
                r"[ァ-ヶー]{2,}",           # カタカナ2文字以上
                r"[A-Za-z]{2,}",            # 英字2文字以上
                r"[一-龯]{2,}"              # 漢字2文字以上
            ],
            "song_titles": [
                r"「(.+?)」",               # 鍵括弧
                r"『(.+?)』",               # 二重鍵括弧  
                r"\"(.+?)\"",               # ダブルクォート
                r"'(.+?)'"                  # シングルクォート
            ],
            "temporal_expressions": [
                r"\d{4}年",                 # 年
                r"\d{1,2}月",               # 月
                r"\d{1,2}日",               # 日
                r"最近|今年|去年|昔"         # 相対時間
            ]
        }
    
    def _build_relationship_patterns(self) -> Dict[str, List[str]]:
        """関係性パターン構築"""
        return {
            "artist_song": [
                r"(.+)(の|が歌う|が作った)(.+)",
                r"(.+)(による|featuring)(.+)",
                r"(.+)(×|x|feat\.?)(.+)"
            ],
            "genre_classification": [
                r"(.+)(は|が)(.+)(系|風|ジャンル)",
                r"(.+)(ロック|ポップ|ジャズ|クラシック)"
            ],
            "temporal_relation": [
                r"(.+)(の後に|の前に|と同時期に)(.+)",
                r"(.+)(年の|月の)(.+)"
            ],
            "similarity_relation": [
                r"(.+)(に似てる|みたいな|っぽい)(.+)",
                r"(.+)(と|より)(.+)(が似てる|が近い)"
            ]
        }
    
    def _load_existing_data(self):
        """既存データロード"""
        # 知識データベース
        try:
            if self.knowledge_db_path.exists():
                with open(self.knowledge_db_path, 'r', encoding='utf-8') as f:
                    self.knowledge_db = json.load(f)
                print(f"[リアルタイム更新] 📊 知識データベースをロード")
        except Exception as e:
            print(f"[リアルタイム更新] ⚠️ 知識データベースロードエラー: {e}")
        
        # 新情報
        try:
            if self.new_information_path.exists():
                with open(self.new_information_path, 'r', encoding='utf-8') as f:
                    info_data = json.load(f)
                    info_list = info_data.get("information", [])
                    self.new_information = deque(
                        [NewInformation(**info) for info in info_list],
                        maxlen=1000
                    )
                print(f"[リアルタイム更新] 📊 {len(self.new_information)}件の新情報をロード")
        except Exception as e:
            print(f"[リアルタイム更新] ⚠️ 新情報ロードエラー: {e}")
        
        # 保留中更新
        try:
            if self.knowledge_updates_path.exists():
                with open(self.knowledge_updates_path, 'r', encoding='utf-8') as f:
                    updates_data = json.load(f)
                    self.pending_updates = {
                        uid: KnowledgeUpdate(**update) 
                        for uid, update in updates_data.get("updates", {}).items()
                    }
                print(f"[リアルタイム更新] 📊 {len(self.pending_updates)}件の保留更新をロード")
        except Exception as e:
            print(f"[リアルタイム更新] ⚠️ 保留更新ロードエラー: {e}")
    
    def process_user_input(self, user_input: str, context: Optional[str] = None) -> List[NewInformation]:
        """ユーザー入力処理"""
        # 情報バッファに追加
        input_data = {
            "timestamp": datetime.now().isoformat(),
            "content": user_input,
            "context": context or "",
            "processed": False
        }
        self.information_buffer.append(input_data)
        
        # 新情報検出
        detected_info = self._detect_new_information(user_input, context)
        
        # セッション情報に追加
        self.current_session_info.extend(detected_info)
        
        # 新情報キューに追加
        for info in detected_info:
            self.new_information.append(info)
        
        # 処理済みマーク
        input_data["processed"] = True
        
        # 統計更新
        self.update_statistics["total_info_detected"] += len(detected_info)
        
        return detected_info
    
    def _detect_new_information(self, text: str, context: Optional[str]) -> List[NewInformation]:
        """新情報検出"""
        detected_info = []
        
        # パターン別情報抽出
        for info_type, patterns in self.extraction_patterns.items():
            info_list = self._extract_by_patterns(text, patterns, info_type, context)
            detected_info.extend(info_list)
        
        # エンティティ抽出
        entities = self._extract_entities(text)
        for entity in entities:
            info = self._create_entity_information(entity, text, context)
            if info:
                detected_info.append(info)
        
        # 関係性抽出
        relationships = self._extract_relationships(text)
        for relationship in relationships:
            info = self._create_relationship_information(relationship, text, context)
            if info:
                detected_info.append(info)
        
        return detected_info
    
    def _extract_by_patterns(self, text: str, patterns: List[str], info_type: str, context: Optional[str]) -> List[NewInformation]:
        """パターンによる抽出"""
        extracted = []
        
        for pattern in patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                content = match.group(0)
                confidence = self._calculate_extraction_confidence(content, pattern, text)
                
                if confidence > 0.3:  # 最小信頼度
                    info_id = f"info_{info_type}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
                    
                    info = NewInformation(
                        info_id=info_id,
                        content=content,
                        info_type=info_type,
                        confidence=confidence,
                        source_context=text[:200],
                        extraction_method=f"pattern_{pattern[:20]}",
                        related_entities=self._extract_entities_from_match(match),
                        validation_status="pending",
                        detected_at=datetime.now().isoformat()
                    )
                    extracted.append(info)
        
        return extracted
    
    def _calculate_extraction_confidence(self, content: str, pattern: str, full_text: str) -> float:
        """抽出信頼度計算"""
        confidence = 0.5  # ベース信頼度
        
        # 長さによる調整
        if len(content) > 10:
            confidence += 0.1
        if len(content) > 20:
            confidence += 0.1
        
        # 既知エンティティとの照合
        if self._contains_known_entities(content):
            confidence += 0.2
        
        # コンテキスト一貫性
        if self._is_contextually_consistent(content, full_text):
            confidence += 0.2
        
        # パターン特異性
        if len(pattern) > 30:  # 複雑なパターン
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def _contains_known_entities(self, text: str) -> bool:
        """既知エンティティ含有確認"""
        # 知識ベースの動画タイトル・アーティストと照合
        videos = self.knowledge_db.get("videos", {})
        
        for video_data in videos.values():
            metadata = video_data.get("metadata", {})
            title = metadata.get("title", "")
            channel = metadata.get("channel_title", "")
            
            if title.lower() in text.lower() or channel.lower() in text.lower():
                return True
        
        return False
    
    def _is_contextually_consistent(self, content: str, full_text: str) -> bool:
        """コンテキスト一貫性確認"""
        # 音楽関連キーワードの存在確認
        music_keywords = ["音楽", "曲", "歌", "アーティスト", "バンド", "アルバム", "シングル"]
        
        content_has_music = any(keyword in content for keyword in music_keywords)
        context_has_music = any(keyword in full_text for keyword in music_keywords)
        
        return content_has_music or context_has_music
    
    def _extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """エンティティ抽出"""
        entities = []
        
        for entity_type, patterns in self.entity_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text)
                for match in matches:
                    entity = {
                        "type": entity_type,
                        "text": match.group(1) if match.groups() else match.group(0),
                        "position": match.span(),
                        "confidence": 0.7
                    }
                    entities.append(entity)
        
        return entities
    
    def _extract_entities_from_match(self, match) -> List[str]:
        """マッチからエンティティ抽出"""
        entities = []
        
        for group in match.groups():
            if group and len(group.strip()) > 1:
                entities.append(group.strip())
        
        return entities
    
    def _create_entity_information(self, entity: Dict[str, Any], source_text: str, context: Optional[str]) -> Optional[NewInformation]:
        """エンティティ情報作成"""
        entity_text = entity["text"]
        entity_type = entity["type"]
        
        # 重複チェック
        if self._is_duplicate_entity(entity_text, entity_type):
            return None
        
        info_id = f"entity_{entity_type}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        return NewInformation(
            info_id=info_id,
            content=f"{entity_type}: {entity_text}",
            info_type="entity",
            confidence=entity["confidence"],
            source_context=source_text[:200],
            extraction_method="entity_extraction",
            related_entities=[entity_text],
            validation_status="pending",
            detected_at=datetime.now().isoformat()
        )
    
    def _is_duplicate_entity(self, entity_text: str, entity_type: str) -> bool:
        """重複エンティティ確認"""
        # 既存の新情報との重複チェック
        for info in self.new_information:
            if (info.info_type == "entity" and 
                entity_text.lower() in info.content.lower()):
                return True
        
        return False
    
    def _extract_relationships(self, text: str) -> List[Dict[str, Any]]:
        """関係性抽出"""
        relationships = []
        
        for rel_type, patterns in self.relationship_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text)
                for match in matches:
                    if len(match.groups()) >= 2:
                        relationship = {
                            "type": rel_type,
                            "entity1": match.group(1).strip(),
                            "entity2": match.group(3).strip() if len(match.groups()) >= 3 else match.group(2).strip(),
                            "relation": match.group(2).strip() if len(match.groups()) >= 3 else "related_to",
                            "confidence": 0.6
                        }
                        relationships.append(relationship)
        
        return relationships
    
    def _create_relationship_information(self, relationship: Dict[str, Any], source_text: str, context: Optional[str]) -> Optional[NewInformation]:
        """関係性情報作成"""
        rel_type = relationship["type"]
        entity1 = relationship["entity1"]
        entity2 = relationship["entity2"]
        relation = relationship["relation"]
        
        # 関係性の有意性チェック
        if len(entity1) < 2 or len(entity2) < 2:
            return None
        
        info_id = f"relationship_{rel_type}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        content = f"{entity1} {relation} {entity2}"
        
        return NewInformation(
            info_id=info_id,
            content=content,
            info_type="relationship",
            confidence=relationship["confidence"],
            source_context=source_text[:200],
            extraction_method="relationship_extraction",
            related_entities=[entity1, entity2],
            validation_status="pending",
            detected_at=datetime.now().isoformat()
        )
    
    def generate_knowledge_updates(self) -> List[KnowledgeUpdate]:
        """知識更新生成"""
        print("[リアルタイム更新] 🔄 知識更新を生成中...")
        
        updates = []
        
        # 検証済み新情報から更新を生成
        validated_info = [
            info for info in self.new_information 
            if info.validation_status == "validated" or info.confidence > self.confidence_threshold
        ]
        
        for info in validated_info:
            update = self._create_knowledge_update(info)
            if update:
                updates.append(update)
        
        # 保留更新に追加
        for update in updates:
            self.pending_updates[update.update_id] = update
        
        print(f"[リアルタイム更新] ✅ {len(updates)}件の知識更新を生成")
        return updates
    
    def _create_knowledge_update(self, info: NewInformation) -> Optional[KnowledgeUpdate]:
        """知識更新作成"""
        # 情報タイプ別の更新戦略
        if info.info_type == "artist_info":
            return self._create_artist_update(info)
        elif info.info_type == "song_info":
            return self._create_song_update(info)
        elif info.info_type == "entity":
            return self._create_entity_update(info)
        elif info.info_type == "relationship":
            return self._create_relationship_update(info)
        else:
            return self._create_generic_update(info)
    
    def _create_artist_update(self, info: NewInformation) -> Optional[KnowledgeUpdate]:
        """アーティスト更新作成"""
        entities = info.related_entities
        if not entities:
            return None
        
        artist_name = entities[0]
        
        # 既存アーティスト検索
        target_video = self._find_video_by_artist(artist_name)
        
        if target_video:
            update_id = f"update_artist_{artist_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            return KnowledgeUpdate(
                update_id=update_id,
                target_entity=target_video,
                update_type="enhance",
                old_value=None,
                new_value={"artist_info": info.content},
                confidence=info.confidence,
                supporting_evidence=[info.source_context],
                impact_score=0.6,
                applied_at=None
            )
        
        return None
    
    def _create_song_update(self, info: NewInformation) -> Optional[KnowledgeUpdate]:
        """楽曲更新作成"""
        # 楽曲タイトル抽出
        song_titles = self._extract_song_titles_from_content(info.content)
        
        for title in song_titles:
            target_video = self._find_video_by_title(title)
            
            if target_video:
                update_id = f"update_song_{title}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
                return KnowledgeUpdate(
                    update_id=update_id,
                    target_entity=target_video,
                    update_type="enhance",
                    old_value=None,
                    new_value={"song_info": info.content},
                    confidence=info.confidence,
                    supporting_evidence=[info.source_context],
                    impact_score=0.7,
                    applied_at=None
                )
        
        return None
    
    def _create_entity_update(self, info: NewInformation) -> KnowledgeUpdate:
        """エンティティ更新作成"""
        update_id = f"update_entity_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return KnowledgeUpdate(
            update_id=update_id,
            target_entity="new_entity",
            update_type="add",
            old_value=None,
            new_value={"entity": info.content, "entities": info.related_entities},
            confidence=info.confidence,
            supporting_evidence=[info.source_context],
            impact_score=0.4,
            applied_at=None
        )
    
    def _create_relationship_update(self, info: NewInformation) -> KnowledgeUpdate:
        """関係性更新作成"""
        update_id = f"update_relationship_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return KnowledgeUpdate(
            update_id=update_id,
            target_entity="knowledge_graph",
            update_type="add",
            old_value=None,
            new_value={"relationship": info.content, "entities": info.related_entities},
            confidence=info.confidence,
            supporting_evidence=[info.source_context],
            impact_score=0.5,
            applied_at=None
        )
    
    def _create_generic_update(self, info: NewInformation) -> KnowledgeUpdate:
        """汎用更新作成"""
        update_id = f"update_generic_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        return KnowledgeUpdate(
            update_id=update_id,
            target_entity="general_knowledge",
            update_type="add",
            old_value=None,
            new_value={"info": info.content},
            confidence=info.confidence,
            supporting_evidence=[info.source_context],
            impact_score=0.3,
            applied_at=None
        )
    
    def _find_video_by_artist(self, artist_name: str) -> Optional[str]:
        """アーティスト名で動画検索"""
        videos = self.knowledge_db.get("videos", {})
        
        for video_id, video_data in videos.items():
            metadata = video_data.get("metadata", {})
            channel_title = metadata.get("channel_title", "")
            custom_info = video_data.get("custom_info", {})
            manual_artist = custom_info.get("manual_artist", "")
            
            if (artist_name.lower() in channel_title.lower() or 
                artist_name.lower() in manual_artist.lower()):
                return video_id
        
        return None
    
    def _find_video_by_title(self, title: str) -> Optional[str]:
        """タイトルで動画検索"""
        videos = self.knowledge_db.get("videos", {})
        
        for video_id, video_data in videos.items():
            metadata = video_data.get("metadata", {})
            video_title = metadata.get("title", "")
            custom_info = video_data.get("custom_info", {})
            manual_title = custom_info.get("manual_title", "")
            
            # 類似度チェック
            similarity1 = difflib.SequenceMatcher(None, title.lower(), video_title.lower()).ratio()
            similarity2 = difflib.SequenceMatcher(None, title.lower(), manual_title.lower()).ratio()
            
            if similarity1 > 0.8 or similarity2 > 0.8:
                return video_id
        
        return None
    
    def _extract_song_titles_from_content(self, content: str) -> List[str]:
        """コンテンツから楽曲タイトル抽出"""
        titles = []
        
        # 引用符で囲まれたテキスト
        quote_patterns = [r"「(.+?)」", r"『(.+?)』", r"\"(.+?)\"", r"'(.+?)'"]
        
        for pattern in quote_patterns:
            matches = re.findall(pattern, content)
            titles.extend(matches)
        
        return titles
    
    def apply_knowledge_updates(self, batch_size: Optional[int] = None) -> int:
        """知識更新適用"""
        if batch_size is None:
            batch_size = self.update_batch_size
        
        print(f"[リアルタイム更新] 🔄 知識更新を適用中... (バッチサイズ: {batch_size})")
        
        applied_count = 0
        
        # 高信頼度の更新から適用
        sorted_updates = sorted(
            self.pending_updates.values(),
            key=lambda x: x.confidence,
            reverse=True
        )
        
        for update in sorted_updates[:batch_size]:
            if self._apply_single_update(update):
                applied_count += 1
        
        # 適用済み更新を削除
        applied_updates = [u for u in sorted_updates[:batch_size] if u.applied_at]
        for update in applied_updates:
            if update.update_id in self.pending_updates:
                del self.pending_updates[update.update_id]
        
        # 統計更新
        self.update_statistics["total_updates_applied"] += applied_count
        self.update_statistics["last_update_batch"] = datetime.now().isoformat()
        
        print(f"[リアルタイム更新] ✅ {applied_count}件の更新を適用完了")
        return applied_count
    
    def _apply_single_update(self, update: KnowledgeUpdate) -> bool:
        """単一更新適用"""
        try:
            if update.target_entity == "knowledge_graph":
                return self._apply_graph_update(update)
            elif update.target_entity == "new_entity":
                return self._apply_entity_update(update)
            elif update.target_entity in self.knowledge_db.get("videos", {}):
                return self._apply_video_update(update)
            else:
                return self._apply_general_update(update)
        except Exception as e:
            print(f"[リアルタイム更新] ⚠️ 更新適用エラー: {e}")
            return False
    
    def _apply_graph_update(self, update: KnowledgeUpdate) -> bool:
        """グラフ更新適用"""
        if self.knowledge_graph:
            # 関係性情報を知識グラフに追加
            new_value = update.new_value
            relationship = new_value.get("relationship", "")
            entities = new_value.get("entities", [])
            
            # 簡易実装：ログ記録のみ
            self.update_log.append({
                "type": "graph_update",
                "relationship": relationship,
                "entities": entities,
                "timestamp": datetime.now().isoformat()
            })
            
            update.applied_at = datetime.now().isoformat()
            return True
        
        return False
    
    def _apply_entity_update(self, update: KnowledgeUpdate) -> bool:
        """エンティティ更新適用"""
        # 新エンティティを一時的なストレージに保存
        if "entities" not in self.knowledge_db:
            self.knowledge_db["entities"] = {}
        
        new_value = update.new_value
        entity_content = new_value.get("entity", "")
        entities = new_value.get("entities", [])
        
        for entity in entities:
            entity_id = hashlib.md5(entity.encode()).hexdigest()[:8]
            self.knowledge_db["entities"][entity_id] = {
                "name": entity,
                "content": entity_content,
                "confidence": update.confidence,
                "added_at": datetime.now().isoformat()
            }
        
        update.applied_at = datetime.now().isoformat()
        return True
    
    def _apply_video_update(self, update: KnowledgeUpdate) -> bool:
        """動画更新適用"""
        video_id = update.target_entity
        videos = self.knowledge_db.get("videos", {})
        
        if video_id in videos:
            video_data = videos[video_id]
            new_value = update.new_value
            
            # カスタム情報に追加
            if "custom_info" not in video_data:
                video_data["custom_info"] = {}
            
            if "realtime_updates" not in video_data["custom_info"]:
                video_data["custom_info"]["realtime_updates"] = []
            
            video_data["custom_info"]["realtime_updates"].append({
                "content": new_value,
                "confidence": update.confidence,
                "added_at": datetime.now().isoformat()
            })
            
            update.applied_at = datetime.now().isoformat()
            return True
        
        return False
    
    def _apply_general_update(self, update: KnowledgeUpdate) -> bool:
        """汎用更新適用"""
        # 汎用更新ログに記録
        self.update_log.append({
            "type": "general_update",
            "update_id": update.update_id,
            "content": update.new_value,
            "confidence": update.confidence,
            "timestamp": datetime.now().isoformat()
        })
        
        update.applied_at = datetime.now().isoformat()
        return True
    
    def detect_conflicts(self) -> List[ConflictResolution]:
        """矛盾検出"""
        print("[リアルタイム更新] ⚙️ 矛盾を検出中...")
        
        conflicts = []
        
        # 新情報間の矛盾
        info_conflicts = self._detect_information_conflicts()
        conflicts.extend(info_conflicts)
        
        # 既存知識との矛盾
        knowledge_conflicts = self._detect_knowledge_conflicts()
        conflicts.extend(knowledge_conflicts)
        
        # 矛盾解決策を生成
        for conflict in conflicts:
            resolution = self._generate_conflict_resolution(conflict)
            if resolution:
                self.conflict_resolutions[resolution.conflict_id] = resolution
        
        print(f"[リアルタイム更新] ✅ {len(conflicts)}件の矛盾を検出")
        return conflicts
    
    def _detect_information_conflicts(self) -> List[Dict[str, Any]]:
        """情報間矛盾検出"""
        conflicts = []
        
        # 同一エンティティに関する矛盾する情報
        entity_info = defaultdict(list)
        
        for info in self.new_information:
            for entity in info.related_entities:
                entity_info[entity].append(info)
        
        for entity, info_list in entity_info.items():
            if len(info_list) > 1:
                # 矛盾チェック
                for i in range(len(info_list)):
                    for j in range(i + 1, len(info_list)):
                        if self._are_conflicting(info_list[i], info_list[j]):
                            conflicts.append({
                                "type": "information_conflict",
                                "entity": entity,
                                "info1": info_list[i],
                                "info2": info_list[j]
                            })
        
        return conflicts
    
    def _detect_knowledge_conflicts(self) -> List[Dict[str, Any]]:
        """既存知識矛盾検出"""
        conflicts = []
        
        # 新情報と既存データベースの矛盾
        for info in self.new_information:
            for entity in info.related_entities:
                existing_info = self._find_existing_entity_info(entity)
                if existing_info and self._conflicts_with_existing(info, existing_info):
                    conflicts.append({
                        "type": "knowledge_conflict",
                        "entity": entity,
                        "new_info": info,
                        "existing_info": existing_info
                    })
        
        return conflicts
    
    def _are_conflicting(self, info1: NewInformation, info2: NewInformation) -> bool:
        """情報矛盾判定"""
        # 同じエンティティに対する矛盾する記述をチェック
        content1 = info1.content.lower()
        content2 = info2.content.lower()
        
        # 対立する表現
        contradictions = [
            ("好き", "嫌い"),
            ("良い", "悪い"),
            ("人気", "不人気"),
            ("新しい", "古い"),
            ("有名", "無名")
        ]
        
        for pos, neg in contradictions:
            if pos in content1 and neg in content2:
                return True
            if neg in content1 and pos in content2:
                return True
        
        return False
    
    def _find_existing_entity_info(self, entity: str) -> Optional[Dict[str, Any]]:
        """既存エンティティ情報検索"""
        videos = self.knowledge_db.get("videos", {})
        
        for video_data in videos.values():
            metadata = video_data.get("metadata", {})
            if entity.lower() in metadata.get("title", "").lower():
                return metadata
            if entity.lower() in metadata.get("channel_title", "").lower():
                return metadata
        
        return None
    
    def _conflicts_with_existing(self, new_info: NewInformation, existing_info: Dict[str, Any]) -> bool:
        """既存情報との矛盾判定"""
        # 簡易実装：基本的な矛盾チェック
        new_content = new_info.content.lower()
        existing_title = existing_info.get("title", "").lower()
        
        # タイトルの大幅な相違
        if new_info.info_type == "song_info":
            similarity = difflib.SequenceMatcher(None, new_content, existing_title).ratio()
            return similarity < 0.3
        
        return False
    
    def _generate_conflict_resolution(self, conflict: Dict[str, Any]) -> Optional[ConflictResolution]:
        """矛盾解決策生成"""
        conflict_id = f"conflict_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        conflict_type = conflict["type"]
        
        if conflict_type == "information_conflict":
            return self._resolve_information_conflict(conflict_id, conflict)
        elif conflict_type == "knowledge_conflict":
            return self._resolve_knowledge_conflict(conflict_id, conflict)
        
        return None
    
    def _resolve_information_conflict(self, conflict_id: str, conflict: Dict[str, Any]) -> ConflictResolution:
        """情報矛盾解決"""
        info1 = conflict["info1"]
        info2 = conflict["info2"]
        
        # 信頼度比較
        if info1.confidence > info2.confidence + 0.2:
            strategy = "replace"
            reasoning = f"高信頼度情報({info1.confidence:.2f})を採用"
        elif info2.confidence > info1.confidence + 0.2:
            strategy = "replace"
            reasoning = f"高信頼度情報({info2.confidence:.2f})を採用"
        else:
            strategy = "merge"
            reasoning = "両情報をマージして保持"
        
        return ConflictResolution(
            conflict_id=conflict_id,
            conflicting_info=[info1.info_id, info2.info_id],
            resolution_strategy=strategy,
            resolution_reasoning=reasoning,
            confidence=0.7,
            resolved_at=datetime.now().isoformat()
        )
    
    def _resolve_knowledge_conflict(self, conflict_id: str, conflict: Dict[str, Any]) -> ConflictResolution:
        """知識矛盾解決"""
        new_info = conflict["new_info"]
        
        # 既存知識の保護を優先
        strategy = "flag"
        reasoning = "既存知識を保護し、新情報に要検証フラグを設定"
        
        return ConflictResolution(
            conflict_id=conflict_id,
            conflicting_info=[new_info.info_id],
            resolution_strategy=strategy,
            resolution_reasoning=reasoning,
            confidence=0.8,
            resolved_at=datetime.now().isoformat()
        )
    
    def save_updated_knowledge(self):
        """更新済み知識保存"""
        try:
            # 知識データベース保存
            with open(self.knowledge_db_path, 'w', encoding='utf-8') as f:
                json.dump(self.knowledge_db, f, ensure_ascii=False, indent=2)
            
            # 新情報保存
            self._save_new_information()
            
            # 保留更新保存
            self._save_pending_updates()
            
            # 矛盾解決保存
            self._save_conflict_resolutions()
            
            print("[リアルタイム更新] 💾 更新済み知識を保存しました")
            
        except Exception as e:
            print(f"[リアルタイム更新] ❌ 知識保存エラー: {e}")
    
    def _save_new_information(self):
        """新情報保存"""
        try:
            info_data = {
                "information": [asdict(info) for info in self.new_information],
                "metadata": {
                    "total_info": len(self.new_information),
                    "last_updated": datetime.now().isoformat()
                }
            }
            
            with open(self.new_information_path, 'w', encoding='utf-8') as f:
                json.dump(info_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[リアルタイム更新] ⚠️ 新情報保存エラー: {e}")
    
    def _save_pending_updates(self):
        """保留更新保存"""
        try:
            updates_data = {
                "updates": {uid: asdict(update) for uid, update in self.pending_updates.items()},
                "metadata": {
                    "total_updates": len(self.pending_updates),
                    "last_updated": datetime.now().isoformat()
                }
            }
            
            with open(self.knowledge_updates_path, 'w', encoding='utf-8') as f:
                json.dump(updates_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[リアルタイム更新] ⚠️ 保留更新保存エラー: {e}")
    
    def _save_conflict_resolutions(self):
        """矛盾解決保存"""
        try:
            resolutions_data = {
                "resolutions": {cid: asdict(resolution) for cid, resolution in self.conflict_resolutions.items()},
                "metadata": {
                    "total_resolutions": len(self.conflict_resolutions),
                    "last_updated": datetime.now().isoformat()
                }
            }
            
            with open(self.conflict_resolutions_path, 'w', encoding='utf-8') as f:
                json.dump(resolutions_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[リアルタイム更新] ⚠️ 矛盾解決保存エラー: {e}")
    
    def get_update_summary(self) -> Dict[str, Any]:
        """更新サマリー取得"""
        return {
            "statistics": self.update_statistics,
            "new_information": len(self.new_information),
            "pending_updates": len(self.pending_updates),
            "conflicts": len(self.conflict_resolutions),
            "recent_activity": [
                {
                    "timestamp": info.detected_at,
                    "type": info.info_type,
                    "content": info.content[:50] + "..." if len(info.content) > 50 else info.content,
                    "confidence": info.confidence
                }
                for info in list(self.new_information)[-5:]
            ]
        }
    
    def perform_comprehensive_update(self) -> Dict[str, Any]:
        """包括的更新実行"""
        print("[リアルタイム更新] 🔄 包括的更新を実行中...")
        
        # 知識更新生成
        updates = self.generate_knowledge_updates()
        
        # 矛盾検出
        conflicts = self.detect_conflicts()
        
        # 更新適用
        applied = self.apply_knowledge_updates()
        
        # データ保存
        self.save_updated_knowledge()
        
        result = {
            "updates_generated": len(updates),
            "conflicts_detected": len(conflicts),
            "updates_applied": applied,
            "statistics": self.update_statistics
        }
        
        print("[リアルタイム更新] ✅ 包括的更新完了")
        return result
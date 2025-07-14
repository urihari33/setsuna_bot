#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
KnowledgeIntegrationSystem - Phase 2B-2
複数セッションからの知識統合・深い洞察生成システム
"""

import json
import os
import openai
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import uuid
import hashlib
from collections import defaultdict
import networkx as nx
import numpy as np
from difflib import SequenceMatcher
from .config_manager import get_config_manager

# Windows環境のパス設定
if os.name == 'nt':
    DATA_DIR = Path("D:/setsuna_bot/data/activity_knowledge")
else:
    DATA_DIR = Path("/mnt/d/setsuna_bot/data/activity_knowledge")

@dataclass
class IntegratedKnowledge:
    """統合知識データクラス"""
    knowledge_id: str
    integration_type: str  # "cross_session", "temporal_evolution", "concept_synthesis"
    source_sessions: List[str]
    source_knowledge_items: List[str]
    
    # 統合結果
    synthesized_content: str
    key_insights: List[str]
    confidence_score: float  # 0.0-1.0
    novelty_score: float    # 新規性スコア
    
    # 関連性・関係性
    related_concepts: List[str]
    contradiction_analysis: Dict[str, Any]
    evolution_trends: List[Dict[str, Any]]
    
    # メタデータ
    created_at: datetime
    integration_method: str  # "gpt_synthesis", "pattern_analysis", "network_analysis"
    quality_metrics: Dict[str, float]
    
    # 活用可能性
    application_domains: List[str]
    actionable_insights: List[str]
    future_research_directions: List[str]

@dataclass
class KnowledgePattern:
    """知識パターンデータクラス"""
    pattern_id: str
    pattern_type: str  # "recurring_theme", "causal_relationship", "temporal_trend"
    description: str
    supporting_evidence: List[str]
    confidence: float
    occurrences: List[Dict[str, Any]]  # 出現箇所・文脈
    
@dataclass
class ConceptEvolution:
    """概念進化データクラス"""
    concept_name: str
    evolution_timeline: List[Dict[str, Any]]  # 時系列変化
    trend_direction: str  # "increasing", "decreasing", "stable", "cyclical"
    key_turning_points: List[Dict[str, Any]]
    prediction_confidence: float

class KnowledgeIntegrationSystem:
    """知識統合システムメインクラス"""
    
    def __init__(self):
        """初期化"""
        self.integration_dir = DATA_DIR / "integrated_knowledge"
        self.integration_dir.mkdir(parents=True, exist_ok=True)
        
        # OpenAI設定
        self.openai_client = None
        self._initialize_openai()
        
        # GPT設定
        self.gpt_config = {
            "model": "gpt-4-turbo-preview",
            "temperature": 0.3,  # 分析的思考重視
            "max_tokens": 2000
        }
        
        # 統合設定
        self.integration_config = {
            "min_sessions_for_integration": 2,
            "similarity_threshold": 0.6,
            "confidence_threshold": 0.7,
            "max_integration_scope": 10,  # 最大統合セッション数
            "enable_temporal_analysis": True,
            "enable_contradiction_detection": True,
            "enable_trend_prediction": True
        }
        
        # 知識グラフ
        self.knowledge_graph = nx.MultiDiGraph()
        
        # 統合済み知識
        self.integrated_knowledge: Dict[str, IntegratedKnowledge] = {}
        self.knowledge_patterns: Dict[str, KnowledgePattern] = {}
        self.concept_evolutions: Dict[str, ConceptEvolution] = {}
        
        # キャッシュ
        self.similarity_cache: Dict[str, float] = {}
        self.integration_cache: Dict[str, Dict] = {}
        
        self._load_existing_integrations()
        
        print("[知識統合] ✅ KnowledgeIntegrationSystem初期化完了")
    
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
                        print("[知識統合] ✅ OpenAI API設定・接続確認完了")
                        return True
                except Exception as api_error:
                    print(f"[知識統合] ❌ OpenAI API接続失敗: {api_error}")
                    self.openai_client = None
                    return False
            else:
                print("[知識統合] ⚠️ OpenAI APIキーが設定されていません")
                print("  .envファイルまたは環境変数 OPENAI_API_KEY を設定してください")
                self.openai_client = None
                return False
                
        except Exception as e:
            print(f"[知識統合] ❌ OpenAI API初期化失敗: {e}")
            self.openai_client = None
            return False
    
    def _load_existing_integrations(self):
        """既存統合結果の読み込み"""
        try:
            # 統合知識読み込み
            integration_files = list(self.integration_dir.glob("integration_*.json"))
            for file_path in integration_files:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for item_data in data.get("integrated_knowledge", []):
                        item = IntegratedKnowledge(
                            knowledge_id=item_data["knowledge_id"],
                            integration_type=item_data["integration_type"],
                            source_sessions=item_data["source_sessions"],
                            source_knowledge_items=item_data["source_knowledge_items"],
                            synthesized_content=item_data["synthesized_content"],
                            key_insights=item_data["key_insights"],
                            confidence_score=item_data["confidence_score"],
                            novelty_score=item_data["novelty_score"],
                            related_concepts=item_data["related_concepts"],
                            contradiction_analysis=item_data["contradiction_analysis"],
                            evolution_trends=item_data["evolution_trends"],
                            created_at=datetime.fromisoformat(item_data["created_at"]),
                            integration_method=item_data["integration_method"],
                            quality_metrics=item_data["quality_metrics"],
                            application_domains=item_data["application_domains"],
                            actionable_insights=item_data["actionable_insights"],
                            future_research_directions=item_data["future_research_directions"]
                        )
                        self.integrated_knowledge[item.knowledge_id] = item
            
            print(f"[知識統合] 📚 既存統合知識読み込み: {len(self.integrated_knowledge)}件")
            
        except Exception as e:
            print(f"[知識統合] ⚠️ 既存データ読み込み失敗: {e}")
    
    def integrate_multi_session_knowledge(self, 
                                        session_ids: List[str],
                                        session_data: Dict[str, Dict],
                                        integration_scope: str = "comprehensive") -> List[IntegratedKnowledge]:
        """
        複数セッション知識統合
        
        Args:
            session_ids: 統合対象セッションIDリスト
            session_data: セッションデータ辞書
            integration_scope: 統合範囲 ("basic", "comprehensive", "deep")
            
        Returns:
            統合知識リスト
        """
        try:
            print(f"[知識統合] 🔗 複数セッション知識統合開始: {len(session_ids)}セッション")
            
            if len(session_ids) < self.integration_config["min_sessions_for_integration"]:
                print("[知識統合] ⚠️ 統合には最低2セッション必要")
                return []
            
            # 1. 知識グラフ構築
            self._build_knowledge_graph(session_ids, session_data)
            
            # 2. クロスセッション分析
            cross_session_results = self._perform_cross_session_analysis(session_ids, session_data)
            
            # 3. 時系列進化分析
            temporal_results = []
            if self.integration_config["enable_temporal_analysis"]:
                temporal_results = self._perform_temporal_evolution_analysis(session_ids, session_data)
            
            # 4. 概念合成分析
            concept_synthesis_results = self._perform_concept_synthesis(session_ids, session_data)
            
            # 5. 統合結果マージ
            all_integrations = cross_session_results + temporal_results + concept_synthesis_results
            
            # 6. 品質フィルタリング
            filtered_integrations = self._filter_integration_quality(all_integrations)
            
            # 7. 統合結果保存
            self._save_integrations(filtered_integrations)
            
            print(f"[知識統合] ✅ 統合完了: {len(filtered_integrations)}件の統合知識生成")
            
            return filtered_integrations
            
        except Exception as e:
            print(f"[知識統合] ❌ 知識統合失敗: {e}")
            return []
    
    def _build_knowledge_graph(self, session_ids: List[str], session_data: Dict[str, Dict]):
        """知識グラフ構築"""
        try:
            print("[知識統合] 🕸️ 知識グラフ構築開始")
            
            # グラフクリア（新規構築）
            self.knowledge_graph.clear()
            
            # セッション別に知識ノード・エッジ追加
            for session_id in session_ids:
                session = session_data.get(session_id, {})
                knowledge_items = session.get("knowledge_items", [])
                
                # 知識アイテムをノードとして追加
                for item in knowledge_items:
                    node_id = item.get("item_id", f"item_{uuid.uuid4().hex[:8]}")
                    
                    self.knowledge_graph.add_node(node_id, **{
                        "session_id": session_id,
                        "content": item.get("content", ""),
                        "categories": item.get("categories", []),
                        "keywords": item.get("keywords", []),
                        "entities": item.get("entities", []),
                        "importance_score": item.get("importance_score", 0.5),
                        "reliability_score": item.get("reliability_score", 0.7)
                    })
                
                # エンティティ間の関係性をエッジとして追加
                self._add_entity_relationships(session_id, knowledge_items)
            
            print(f"[知識統合] ✅ 知識グラフ構築完了: {self.knowledge_graph.number_of_nodes()}ノード, {self.knowledge_graph.number_of_edges()}エッジ")
            
        except Exception as e:
            print(f"[知識統合] ❌ 知識グラフ構築失敗: {e}")
    
    def _add_entity_relationships(self, session_id: str, knowledge_items: List[Dict]):
        """エンティティ関係性追加"""
        try:
            # 同一セッション内のエンティティ共起関係
            entity_cooccurrence = defaultdict(list)
            
            for item in knowledge_items:
                entities = item.get("entities", [])
                item_id = item.get("item_id", "")
                
                # エンティティペア生成
                for i, entity1 in enumerate(entities):
                    for entity2 in entities[i+1:]:
                        if entity1 != entity2:
                            # 共起関係記録
                            entity_cooccurrence[(entity1, entity2)].append(item_id)
            
            # 共起頻度に基づくエッジ追加
            for (entity1, entity2), item_ids in entity_cooccurrence.items():
                if len(item_ids) >= 1:  # 最低1回以上共起
                    self.knowledge_graph.add_edge(
                        entity1, entity2,
                        relationship_type="co_occurs_in",
                        session_id=session_id,
                        strength=len(item_ids),
                        supporting_items=item_ids
                    )
            
        except Exception as e:
            print(f"[知識統合] ⚠️ エンティティ関係性追加失敗: {e}")
    
    def _perform_cross_session_analysis(self, session_ids: List[str], session_data: Dict[str, Dict]) -> List[IntegratedKnowledge]:
        """クロスセッション分析"""
        try:
            print("[知識統合] 🔍 クロスセッション分析開始")
            
            cross_session_integrations = []
            
            # セッション間の概念重複・関連性分析
            concept_overlaps = self._find_concept_overlaps(session_ids, session_data)
            
            # 重複概念の統合
            for overlap in concept_overlaps:
                if overlap["similarity_score"] >= self.integration_config["similarity_threshold"]:
                    integration = self._create_cross_session_integration(overlap, session_data)
                    if integration:
                        cross_session_integrations.append(integration)
            
            # 補完的知識の統合
            complementary_knowledge = self._find_complementary_knowledge(session_ids, session_data)
            for complement in complementary_knowledge:
                integration = self._create_complementary_integration(complement, session_data)
                if integration:
                    cross_session_integrations.append(integration)
            
            print(f"[知識統合] ✅ クロスセッション分析完了: {len(cross_session_integrations)}件")
            
            return cross_session_integrations
            
        except Exception as e:
            print(f"[知識統合] ❌ クロスセッション分析失敗: {e}")
            return []
    
    def _find_concept_overlaps(self, session_ids: List[str], session_data: Dict[str, Dict]) -> List[Dict]:
        """概念重複検出"""
        overlaps = []
        
        try:
            # セッション間の知識アイテム比較
            for i, session_id1 in enumerate(session_ids):
                for session_id2 in session_ids[i+1:]:
                    session1_items = session_data.get(session_id1, {}).get("knowledge_items", [])
                    session2_items = session_data.get(session_id2, {}).get("knowledge_items", [])
                    
                    # アイテム間類似度計算
                    for item1 in session1_items:
                        for item2 in session2_items:
                            similarity = self._calculate_knowledge_similarity(item1, item2)
                            
                            if similarity >= self.integration_config["similarity_threshold"]:
                                overlaps.append({
                                    "session1": session_id1,
                                    "session2": session_id2,
                                    "item1": item1,
                                    "item2": item2,
                                    "similarity_score": similarity,
                                    "overlap_type": "concept_overlap"
                                })
            
        except Exception as e:
            print(f"[知識統合] ⚠️ 概念重複検出失敗: {e}")
        
        return overlaps
    
    def _calculate_knowledge_similarity(self, item1: Dict, item2: Dict) -> float:
        """知識類似度計算"""
        try:
            # キャッシュチェック
            cache_key = f"{item1.get('item_id', '')}_{item2.get('item_id', '')}"
            if cache_key in self.similarity_cache:
                return self.similarity_cache[cache_key]
            
            # 複数要素での類似度計算
            similarities = []
            
            # コンテンツ類似度
            content1 = item1.get("content", "")
            content2 = item2.get("content", "")
            if content1 and content2:
                content_sim = SequenceMatcher(None, content1.lower(), content2.lower()).ratio()
                similarities.append(("content", content_sim, 0.4))
            
            # キーワード類似度
            keywords1 = set(item1.get("keywords", []))
            keywords2 = set(item2.get("keywords", []))
            if keywords1 and keywords2:
                keyword_sim = len(keywords1 & keywords2) / len(keywords1 | keywords2)
                similarities.append(("keywords", keyword_sim, 0.3))
            
            # エンティティ類似度
            entities1 = set(item1.get("entities", []))
            entities2 = set(item2.get("entities", []))
            if entities1 and entities2:
                entity_sim = len(entities1 & entities2) / len(entities1 | entities2)
                similarities.append(("entities", entity_sim, 0.2))
            
            # カテゴリ類似度
            categories1 = set(item1.get("categories", []))
            categories2 = set(item2.get("categories", []))
            if categories1 and categories2:
                category_sim = len(categories1 & categories2) / len(categories1 | categories2)
                similarities.append(("categories", category_sim, 0.1))
            
            # 重み付き平均
            if similarities:
                weighted_sum = sum(sim * weight for _, sim, weight in similarities)
                total_weight = sum(weight for _, _, weight in similarities)
                final_similarity = weighted_sum / total_weight
            else:
                final_similarity = 0.0
            
            # キャッシュ保存
            self.similarity_cache[cache_key] = final_similarity
            
            return final_similarity
            
        except Exception as e:
            print(f"[知識統合] ⚠️ 類似度計算失敗: {e}")
            return 0.0
    
    def _find_complementary_knowledge(self, session_ids: List[str], session_data: Dict[str, Dict]) -> List[Dict]:
        """補完的知識検出"""
        complementary_sets = []
        
        try:
            # セッション間のカテゴリ・ドメイン分析
            session_domains = {}
            for session_id in session_ids:
                knowledge_items = session_data.get(session_id, {}).get("knowledge_items", [])
                
                domains = set()
                for item in knowledge_items:
                    domains.update(item.get("categories", []))
                
                session_domains[session_id] = domains
            
            # 補完関係検出
            for session_id1 in session_ids:
                for session_id2 in session_ids:
                    if session_id1 != session_id2:
                        domains1 = session_domains[session_id1]
                        domains2 = session_domains[session_id2]
                        
                        # 補完性評価（重複が少なく、組み合わせで包括的）
                        overlap = len(domains1 & domains2)
                        union = len(domains1 | domains2)
                        
                        if overlap < len(domains1) * 0.5 and union > len(domains1) * 1.2:
                            complementary_sets.append({
                                "session1": session_id1,
                                "session2": session_id2,
                                "complementary_type": "domain_complement",
                                "overlap_ratio": overlap / len(domains1) if domains1 else 0,
                                "expansion_ratio": union / len(domains1) if domains1 else 0
                            })
            
        except Exception as e:
            print(f"[知識統合] ⚠️ 補完的知識検出失敗: {e}")
        
        return complementary_sets
    
    def _create_cross_session_integration(self, overlap: Dict, session_data: Dict[str, Dict]) -> Optional[IntegratedKnowledge]:
        """クロスセッション統合作成"""
        try:
            # GPT-4による統合分析
            if self.openai_client:
                integration_content = self._synthesize_with_gpt(overlap, session_data)
            else:
                integration_content = self._synthesize_without_gpt(overlap, session_data)
            
            if not integration_content:
                return None
            
            knowledge_id = f"cross_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            
            integration = IntegratedKnowledge(
                knowledge_id=knowledge_id,
                integration_type="cross_session",
                source_sessions=[overlap["session1"], overlap["session2"]],
                source_knowledge_items=[
                    overlap["item1"].get("item_id", ""),
                    overlap["item2"].get("item_id", "")
                ],
                synthesized_content=integration_content["synthesized_content"],
                key_insights=integration_content["key_insights"],
                confidence_score=overlap["similarity_score"],
                novelty_score=integration_content.get("novelty_score", 0.5),
                related_concepts=integration_content.get("related_concepts", []),
                contradiction_analysis=integration_content.get("contradiction_analysis", {}),
                evolution_trends=integration_content.get("evolution_trends", []),
                created_at=datetime.now(),
                integration_method="gpt_synthesis" if self.openai_client else "pattern_analysis",
                quality_metrics=integration_content.get("quality_metrics", {}),
                application_domains=integration_content.get("application_domains", []),
                actionable_insights=integration_content.get("actionable_insights", []),
                future_research_directions=integration_content.get("future_research_directions", [])
            )
            
            return integration
            
        except Exception as e:
            print(f"[知識統合] ❌ クロスセッション統合作成失敗: {e}")
            return None
    
    def _synthesize_with_gpt(self, overlap: Dict, session_data: Dict[str, Dict]) -> Optional[Dict]:
        """GPT-4による統合合成"""
        try:
            item1 = overlap["item1"]
            item2 = overlap["item2"]
            
            prompt = f"""
以下の2つの関連する知識を統合し、より深い洞察を生成してください。

【知識1】
内容: {item1.get('content', '')}
カテゴリ: {', '.join(item1.get('categories', []))}
キーワード: {', '.join(item1.get('keywords', []))}

【知識2】  
内容: {item2.get('content', '')}
カテゴリ: {', '.join(item2.get('categories', []))}
キーワード: {', '.join(item2.get('keywords', []))}

以下の形式で統合結果を出力してください：

{{
  "synthesized_content": "統合された知識の説明",
  "key_insights": ["洞察1", "洞察2", "洞察3"],
  "novelty_score": 0.8,
  "related_concepts": ["関連概念1", "関連概念2"],
  "contradiction_analysis": {{"conflicts": [], "resolutions": []}},
  "evolution_trends": [{{"trend": "傾向", "evidence": "根拠"}}],
  "quality_metrics": {{"coherence": 0.9, "completeness": 0.8}},
  "application_domains": ["応用分野1", "応用分野2"],
  "actionable_insights": ["実行可能な洞察1", "実行可能な洞察2"],
  "future_research_directions": ["今後の研究方向1", "今後の研究方向2"]
}}
"""
            
            response = self.openai_client.chat.completions.create(
                model=self.gpt_config["model"],
                messages=[{"role": "user", "content": prompt}],
                temperature=self.gpt_config["temperature"],
                max_tokens=self.gpt_config["max_tokens"]
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # JSON抽出
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            elif "{" in response_text and "}" in response_text:
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
                json_text = response_text[json_start:json_end]
            else:
                return None
            
            return json.loads(json_text)
            
        except Exception as e:
            print(f"[知識統合] ❌ GPT統合合成失敗: {e}")
            return None
    
    def _synthesize_without_gpt(self, overlap: Dict, session_data: Dict[str, Dict]) -> Dict:
        """GPT無しでの統合合成（フォールバック）"""
        item1 = overlap["item1"]
        item2 = overlap["item2"]
        
        # 基本的な統合
        combined_content = f"{item1.get('content', '')} {item2.get('content', '')}"
        combined_keywords = list(set(item1.get('keywords', []) + item2.get('keywords', [])))
        combined_categories = list(set(item1.get('categories', []) + item2.get('categories', [])))
        
        return {
            "synthesized_content": f"2つのセッションから得られた関連知識の統合: {combined_content[:200]}...",
            "key_insights": [
                f"共通キーワード: {', '.join(combined_keywords[:3])}",
                f"関連カテゴリ: {', '.join(combined_categories[:3])}"
            ],
            "novelty_score": 0.6,
            "related_concepts": combined_keywords[:5],
            "contradiction_analysis": {"conflicts": [], "resolutions": []},
            "evolution_trends": [],
            "quality_metrics": {"coherence": 0.7, "completeness": 0.6},
            "application_domains": combined_categories,
            "actionable_insights": ["統合知識の詳細分析が推奨"],
            "future_research_directions": ["関連分野の追加調査"]
        }
    
    def _create_complementary_integration(self, complement: Dict, session_data: Dict[str, Dict]) -> Optional[IntegratedKnowledge]:
        """補完的統合作成"""
        try:
            session1_data = session_data.get(complement["session1"], {})
            session2_data = session_data.get(complement["session2"], {})
            
            # 補完的知識の統合
            knowledge_id = f"comp_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            
            integration = IntegratedKnowledge(
                knowledge_id=knowledge_id,
                integration_type="cross_session",
                source_sessions=[complement["session1"], complement["session2"]],
                source_knowledge_items=[],
                synthesized_content=f"補完的セッション統合: {complement['complementary_type']}",
                key_insights=[
                    f"セッション間の補完性: {complement['expansion_ratio']:.2f}",
                    "異なる観点からの包括的理解"
                ],
                confidence_score=0.7,
                novelty_score=0.6,
                related_concepts=[],
                contradiction_analysis={},
                evolution_trends=[],
                created_at=datetime.now(),
                integration_method="pattern_analysis",
                quality_metrics={"coherence": 0.7, "completeness": 0.8},
                application_domains=[],
                actionable_insights=["統合された包括的な理解の活用"],
                future_research_directions=["補完分野の更なる探求"]
            )
            
            return integration
            
        except Exception as e:
            print(f"[知識統合] ❌ 補完的統合作成失敗: {e}")
            return None
    
    def _perform_temporal_evolution_analysis(self, session_ids: List[str], session_data: Dict[str, Dict]) -> List[IntegratedKnowledge]:
        """時系列進化分析"""
        try:
            print("[知識統合] ⏰ 時系列進化分析開始")
            
            temporal_integrations = []
            
            # セッションの時系列ソート
            sessions_with_time = []
            for session_id in session_ids:
                session_info = session_data.get(session_id, {})
                session_metadata = session_info.get("session_metadata", {})
                created_at = session_metadata.get("created_at")
                if created_at:
                    sessions_with_time.append((session_id, datetime.fromisoformat(created_at)))
            
            sessions_with_time.sort(key=lambda x: x[1])
            
            # 概念の時系列変化分析
            concept_evolution = self._analyze_concept_evolution(sessions_with_time, session_data)
            
            for evolution in concept_evolution:
                integration = self._create_temporal_integration(evolution, session_data)
                if integration:
                    temporal_integrations.append(integration)
            
            print(f"[知識統合] ✅ 時系列進化分析完了: {len(temporal_integrations)}件")
            
            return temporal_integrations
            
        except Exception as e:
            print(f"[知識統合] ❌ 時系列進化分析失敗: {e}")
            return []
    
    def _analyze_concept_evolution(self, sessions_with_time: List[Tuple], session_data: Dict[str, Dict]) -> List[ConceptEvolution]:
        """概念進化分析"""
        evolutions = []
        
        try:
            # 概念の出現・変化を追跡
            concept_timeline = defaultdict(list)
            
            for session_id, timestamp in sessions_with_time:
                knowledge_items = session_data.get(session_id, {}).get("knowledge_items", [])
                
                for item in knowledge_items:
                    entities = item.get("entities", [])
                    keywords = item.get("keywords", [])
                    
                    for concept in entities + keywords:
                        concept_timeline[concept].append({
                            "session_id": session_id,
                            "timestamp": timestamp,
                            "context": item.get("content", "")[:100],
                            "importance": item.get("importance_score", 0.5)
                        })
            
            # 進化パターン分析
            for concept, timeline in concept_timeline.items():
                if len(timeline) >= 2:  # 最低2回出現
                    evolution = ConceptEvolution(
                        concept_name=concept,
                        evolution_timeline=timeline,
                        trend_direction=self._determine_trend_direction(timeline),
                        key_turning_points=self._find_turning_points(timeline),
                        prediction_confidence=0.7
                    )
                    evolutions.append(evolution)
            
        except Exception as e:
            print(f"[知識統合] ⚠️ 概念進化分析失敗: {e}")
        
        return evolutions
    
    def _determine_trend_direction(self, timeline: List[Dict]) -> str:
        """トレンド方向判定"""
        if len(timeline) < 2:
            return "stable"
        
        # 重要度の変化を分析
        importance_values = [entry["importance"] for entry in timeline]
        
        if len(importance_values) >= 3:
            # 線形回帰による傾向分析（簡易版）
            x = list(range(len(importance_values)))
            slope = np.polyfit(x, importance_values, 1)[0]
            
            if slope > 0.1:
                return "increasing"
            elif slope < -0.1:
                return "decreasing"
            else:
                return "stable"
        else:
            # 単純比較
            if importance_values[-1] > importance_values[0]:
                return "increasing"
            elif importance_values[-1] < importance_values[0]:
                return "decreasing"
            else:
                return "stable"
    
    def _find_turning_points(self, timeline: List[Dict]) -> List[Dict]:
        """転換点検出"""
        turning_points = []
        
        if len(timeline) >= 3:
            importance_values = [entry["importance"] for entry in timeline]
            
            # 極値検出
            for i in range(1, len(importance_values) - 1):
                prev_val = importance_values[i-1]
                curr_val = importance_values[i]
                next_val = importance_values[i+1]
                
                # 極大値
                if curr_val > prev_val and curr_val > next_val:
                    turning_points.append({
                        "type": "peak",
                        "session_id": timeline[i]["session_id"],
                        "timestamp": timeline[i]["timestamp"].isoformat(),
                        "importance": curr_val
                    })
                
                # 極小値
                elif curr_val < prev_val and curr_val < next_val:
                    turning_points.append({
                        "type": "valley",
                        "session_id": timeline[i]["session_id"],
                        "timestamp": timeline[i]["timestamp"].isoformat(),
                        "importance": curr_val
                    })
        
        return turning_points
    
    def _create_temporal_integration(self, evolution: ConceptEvolution, session_data: Dict[str, Dict]) -> Optional[IntegratedKnowledge]:
        """時系列統合作成"""
        try:
            knowledge_id = f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            
            source_sessions = [entry["session_id"] for entry in evolution.evolution_timeline]
            
            integration = IntegratedKnowledge(
                knowledge_id=knowledge_id,
                integration_type="temporal_evolution",
                source_sessions=source_sessions,
                source_knowledge_items=[],
                synthesized_content=f"概念「{evolution.concept_name}」の時系列進化分析",
                key_insights=[
                    f"トレンド方向: {evolution.trend_direction}",
                    f"転換点数: {len(evolution.key_turning_points)}",
                    f"出現セッション数: {len(evolution.evolution_timeline)}"
                ],
                confidence_score=evolution.prediction_confidence,
                novelty_score=0.7,
                related_concepts=[evolution.concept_name],
                contradiction_analysis={},
                evolution_trends=[{
                    "concept": evolution.concept_name,
                    "trend": evolution.trend_direction,
                    "timeline": [asdict(entry) for entry in evolution.evolution_timeline]
                }],
                created_at=datetime.now(),
                integration_method="temporal_analysis",
                quality_metrics={"coherence": 0.8, "completeness": 0.7},
                application_domains=["トレンド分析", "予測"],
                actionable_insights=[f"概念「{evolution.concept_name}」の{evolution.trend_direction}傾向を活用"],
                future_research_directions=[f"「{evolution.concept_name}」の将来動向予測"]
            )
            
            return integration
            
        except Exception as e:
            print(f"[知識統合] ❌ 時系列統合作成失敗: {e}")
            return None
    
    def _perform_concept_synthesis(self, session_ids: List[str], session_data: Dict[str, Dict]) -> List[IntegratedKnowledge]:
        """概念合成分析"""
        try:
            print("[知識統合] 🧠 概念合成分析開始")
            
            synthesis_integrations = []
            
            # 概念間の関係性分析
            concept_relationships = self._analyze_concept_relationships(session_ids, session_data)
            
            # 新しい洞察の合成
            for relationship in concept_relationships:
                if relationship["strength"] >= 0.6:
                    integration = self._create_synthesis_integration(relationship, session_data)
                    if integration:
                        synthesis_integrations.append(integration)
            
            print(f"[知識統合] ✅ 概念合成分析完了: {len(synthesis_integrations)}件")
            
            return synthesis_integrations
            
        except Exception as e:
            print(f"[知識統合] ❌ 概念合成分析失敗: {e}")
            return []
    
    def _analyze_concept_relationships(self, session_ids: List[str], session_data: Dict[str, Dict]) -> List[Dict]:
        """概念関係性分析"""
        relationships = []
        
        try:
            # 全概念抽出
            all_concepts = set()
            concept_contexts = defaultdict(list)
            
            for session_id in session_ids:
                knowledge_items = session_data.get(session_id, {}).get("knowledge_items", [])
                
                for item in knowledge_items:
                    entities = item.get("entities", [])
                    keywords = item.get("keywords", [])
                    
                    for concept in entities + keywords:
                        all_concepts.add(concept)
                        concept_contexts[concept].append({
                            "session_id": session_id,
                            "content": item.get("content", ""),
                            "categories": item.get("categories", [])
                        })
            
            # 概念ペアの関係性分析
            concept_list = list(all_concepts)
            for i, concept1 in enumerate(concept_list):
                for concept2 in concept_list[i+1:]:
                    relationship_strength = self._calculate_concept_relationship_strength(
                        concept1, concept2, concept_contexts
                    )
                    
                    if relationship_strength > 0.3:
                        relationships.append({
                            "concept1": concept1,
                            "concept2": concept2,
                            "strength": relationship_strength,
                            "relationship_type": "semantic_association"
                        })
            
        except Exception as e:
            print(f"[知識統合] ⚠️ 概念関係性分析失敗: {e}")
        
        return relationships
    
    def _calculate_concept_relationship_strength(self, concept1: str, concept2: str, concept_contexts: Dict) -> float:
        """概念関係性強度計算"""
        try:
            contexts1 = concept_contexts.get(concept1, [])
            contexts2 = concept_contexts.get(concept2, [])
            
            if not contexts1 or not contexts2:
                return 0.0
            
            # 共起分析
            cooccurrence_count = 0
            total_contexts = len(contexts1) + len(contexts2)
            
            for ctx1 in contexts1:
                for ctx2 in contexts2:
                    # 同一セッション内での共起
                    if ctx1["session_id"] == ctx2["session_id"]:
                        cooccurrence_count += 1
                    
                    # カテゴリ共通性
                    common_categories = set(ctx1["categories"]) & set(ctx2["categories"])
                    if common_categories:
                        cooccurrence_count += 0.5
            
            return min(1.0, cooccurrence_count / total_contexts) if total_contexts > 0 else 0.0
            
        except Exception as e:
            print(f"[知識統合] ⚠️ 概念関係性強度計算失敗: {e}")
            return 0.0
    
    def _create_synthesis_integration(self, relationship: Dict, session_data: Dict[str, Dict]) -> Optional[IntegratedKnowledge]:
        """合成統合作成"""
        try:
            knowledge_id = f"synth_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            
            integration = IntegratedKnowledge(
                knowledge_id=knowledge_id,
                integration_type="concept_synthesis",
                source_sessions=[],  # 関係性分析のため特定セッションなし
                source_knowledge_items=[],
                synthesized_content=f"概念「{relationship['concept1']}」と「{relationship['concept2']}」の関係性分析",
                key_insights=[
                    f"概念間関係性強度: {relationship['strength']:.2f}",
                    f"関係性タイプ: {relationship['relationship_type']}"
                ],
                confidence_score=relationship["strength"],
                novelty_score=0.6,
                related_concepts=[relationship["concept1"], relationship["concept2"]],
                contradiction_analysis={},
                evolution_trends=[],
                created_at=datetime.now(),
                integration_method="network_analysis",
                quality_metrics={"coherence": 0.7, "completeness": 0.6},
                application_domains=["概念マップ", "関係性分析"],
                actionable_insights=[f"概念関係性の活用による深い理解"],
                future_research_directions=[f"関連概念群の体系的分析"]
            )
            
            return integration
            
        except Exception as e:
            print(f"[知識統合] ❌ 合成統合作成失敗: {e}")
            return None
    
    def _filter_integration_quality(self, integrations: List[IntegratedKnowledge]) -> List[IntegratedKnowledge]:
        """統合品質フィルタリング"""
        filtered = []
        
        for integration in integrations:
            # 品質閾値チェック
            if (integration.confidence_score >= self.integration_config["confidence_threshold"] and
                len(integration.key_insights) >= 1 and
                integration.synthesized_content):
                filtered.append(integration)
        
        # 重複排除・優先度ソート
        filtered.sort(key=lambda x: x.confidence_score * x.novelty_score, reverse=True)
        
        return filtered[:self.integration_config["max_integration_scope"]]
    
    def _save_integrations(self, integrations: List[IntegratedKnowledge]):
        """統合結果保存"""
        try:
            if not integrations:
                return
            
            current_month = datetime.now().strftime("%Y%m")
            integration_file = self.integration_dir / f"integration_{current_month}.json"
            
            # 既存データ読み込み
            if integration_file.exists():
                with open(integration_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = {
                    "month": current_month,
                    "integrated_knowledge": [],
                    "integration_statistics": {}
                }
            
            # 新しい統合結果追加
            for integration in integrations:
                integration_dict = asdict(integration)
                data["integrated_knowledge"].append(integration_dict)
                
                # メモリ内にも保存
                self.integrated_knowledge[integration.knowledge_id] = integration
            
            # 統計更新
            data["integration_statistics"] = {
                "total_integrations": len(data["integrated_knowledge"]),
                "by_type": self._get_integration_type_stats(data["integrated_knowledge"]),
                "average_confidence": self._get_average_confidence(data["integrated_knowledge"]),
                "last_updated": datetime.now().isoformat()
            }
            
            # 保存
            with open(integration_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            
        except Exception as e:
            print(f"[知識統合] ❌ 統合結果保存失敗: {e}")
    
    def _get_integration_type_stats(self, integrations: List[Dict]) -> Dict[str, int]:
        """統合タイプ別統計"""
        type_stats = defaultdict(int)
        for integration in integrations:
            integration_type = integration.get("integration_type", "unknown")
            type_stats[integration_type] += 1
        return dict(type_stats)
    
    def _get_average_confidence(self, integrations: List[Dict]) -> float:
        """平均信頼度計算"""
        if not integrations:
            return 0.0
        
        total_confidence = sum(integration.get("confidence_score", 0.0) for integration in integrations)
        return total_confidence / len(integrations)
    
    def get_integration_summary(self, session_ids: List[str] = None) -> Dict[str, Any]:
        """統合サマリー取得"""
        if session_ids:
            # 特定セッションの統合結果
            relevant_integrations = [
                integration for integration in self.integrated_knowledge.values()
                if any(sid in integration.source_sessions for sid in session_ids)
            ]
        else:
            # 全統合結果
            relevant_integrations = list(self.integrated_knowledge.values())
        
        return {
            "total_integrations": len(relevant_integrations),
            "by_type": self._get_integration_type_stats([asdict(i) for i in relevant_integrations]),
            "average_confidence": np.mean([i.confidence_score for i in relevant_integrations]) if relevant_integrations else 0.0,
            "average_novelty": np.mean([i.novelty_score for i in relevant_integrations]) if relevant_integrations else 0.0,
            "top_insights": [
                {
                    "knowledge_id": integration.knowledge_id,
                    "type": integration.integration_type,
                    "insights": integration.key_insights[:2],
                    "confidence": integration.confidence_score
                }
                for integration in sorted(relevant_integrations, 
                                        key=lambda x: x.confidence_score * x.novelty_score, 
                                        reverse=True)[:5]
            ]
        }


# テスト用コード
if __name__ == "__main__":
    print("=== KnowledgeIntegrationSystem テスト ===")
    
    system = KnowledgeIntegrationSystem()
    
    # テスト用セッションデータ
    test_session_data = {
        "session_001": {
            "session_metadata": {"created_at": "2025-01-05T10:00:00"},
            "knowledge_items": [
                {
                    "item_id": "item_001",
                    "content": "AI音楽生成技術はTransformerアーキテクチャを基盤としている",
                    "categories": ["AI技術", "音楽生成"],
                    "keywords": ["Transformer", "AI", "音楽生成"],
                    "entities": ["Transformer", "AI技術"],
                    "importance_score": 0.8
                }
            ]
        },
        "session_002": {
            "session_metadata": {"created_at": "2025-01-06T15:00:00"},
            "knowledge_items": [
                {
                    "item_id": "item_002",
                    "content": "Transformerによる音楽生成は高品質な結果を生成する",
                    "categories": ["AI技術", "品質評価"],
                    "keywords": ["Transformer", "高品質", "音楽生成"],
                    "entities": ["Transformer", "品質評価"],
                    "importance_score": 0.7
                }
            ]
        }
    }
    
    # 知識統合テスト
    print("\n🔗 知識統合テスト:")
    integrations = system.integrate_multi_session_knowledge(
        session_ids=["session_001", "session_002"],
        session_data=test_session_data
    )
    
    print(f"\n📊 統合結果: {len(integrations)}件")
    for integration in integrations:
        print(f"\n統合ID: {integration.knowledge_id}")
        print(f"タイプ: {integration.integration_type}")
        print(f"内容: {integration.synthesized_content}")
        print(f"洞察: {integration.key_insights}")
        print(f"信頼度: {integration.confidence_score:.2f}")
    
    # 統合サマリー
    print(f"\n📈 統合サマリー:")
    summary = system.get_integration_summary(["session_001", "session_002"])
    print(f"  総統合数: {summary['total_integrations']}")
    print(f"  タイプ別: {summary['by_type']}")
    print(f"  平均信頼度: {summary['average_confidence']:.2f}")
    print(f"  平均新規性: {summary['average_novelty']:.2f}")
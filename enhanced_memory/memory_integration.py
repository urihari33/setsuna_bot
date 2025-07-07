#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
せつな記憶統合システム
PersonalityMemoryとCollaborationMemoryの横断的統合・関連付け管理
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import hashlib
import re

class MemoryIntegrationSystem:
    """せつなの記憶統合管理システム"""
    
    def __init__(self, personality_memory=None, collaboration_memory=None, memory_mode="normal"):
        """
        記憶統合システム初期化
        
        Args:
            personality_memory: PersonalityMemoryインスタンス
            collaboration_memory: CollaborationMemoryインスタンス
            memory_mode: "normal" または "test"
        """
        self.personality_memory = personality_memory
        self.collaboration_memory = collaboration_memory
        self.memory_mode = memory_mode
        
        # 環境に応じてパスを決定
        if os.path.exists("/mnt/d/setsuna_bot"):
            base_path = Path("/mnt/d/setsuna_bot")
        else:
            base_path = Path("D:/setsuna_bot")
        
        if memory_mode == "test":
            # テストモード: 一時ファイル
            import tempfile
            self.integration_file = base_path / "temp" / f"test_memory_integration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            os.makedirs(self.integration_file.parent, exist_ok=True)
        else:
            # 通常モード: 永続ファイル
            self.integration_file = base_path / "enhanced_memory" / "memory_integration.json"
            os.makedirs(self.integration_file.parent, exist_ok=True)
        
        # 統合記憶データ構造
        self.integration_data = {
            "memory_relationships": [],    # 記憶間関係性
            "memory_clusters": {},         # 記憶クラスター
            "relationship_types": {        # 関係性タイプ定義
                "causal": "因果関係",
                "temporal": "時系列関係", 
                "thematic": "テーマ関係",
                "reinforcing": "相互強化",
                "contradictory": "矛盾関係"
            },
            "integration_patterns": [],    # 統合パターン
            "adaptive_insights": {},       # 適応的洞察
            "cross_references": {},        # クロスリファレンス
            "created_at": datetime.now().isoformat(),
            "version": "1.0"
        }
        
        # 関連付けアルゴリズム設定
        self.relationship_config = {
            "temporal_threshold_hours": 24,     # 時系列関連の閾値（時間）
            "theme_similarity_threshold": 0.3,  # テーマ類似度閾値
            "causal_confidence_threshold": 0.6, # 因果関係信頼度閾値
            "keyword_weight": 0.4,              # キーワード重み
            "emotion_weight": 0.3,              # 感情重み
            "temporal_weight": 0.3              # 時系列重み
        }
        
        # データ読み込み
        self._load_integration_data()
        
        print(f"🔗 記憶統合システム初期化完了 ({memory_mode}モード)")
    
    def _load_integration_data(self):
        """統合記憶データを読み込み"""
        if self.integration_file.exists() and self.memory_mode == "normal":
            try:
                with open(self.integration_file, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                    self.integration_data.update(loaded_data)
                
                relationships_count = len(self.integration_data.get("memory_relationships", []))
                clusters_count = len(self.integration_data.get("memory_clusters", {}))
                print(f"✅ 記憶統合データ読み込み: 関係性{relationships_count}件, クラスター{clusters_count}件")
                
            except Exception as e:
                print(f"⚠️ 記憶統合データ読み込みエラー: {e}")
        else:
            print("🆕 新規記憶統合データベース作成")
    
    def save_integration_data(self):
        """統合記憶データを保存"""
        if self.memory_mode == "test":
            # テストモードでは保存しない
            return
        
        try:
            with open(self.integration_file, 'w', encoding='utf-8') as f:
                json.dump(self.integration_data, f, ensure_ascii=False, indent=2)
            print(f"💾 記憶統合データ保存完了")
        except Exception as e:
            print(f"❌ 記憶統合データ保存エラー: {e}")
    
    def analyze_memory_relationships(self) -> Dict[str, int]:
        """
        記憶間の関係性を分析・更新
        
        Returns:
            Dict[str, int]: 分析結果統計
        """
        try:
            print("🔍 記憶関係性分析開始...")
            
            # 既存の関係性をクリア（再分析）
            old_count = len(self.integration_data["memory_relationships"])
            self.integration_data["memory_relationships"] = []
            
            analysis_stats = {
                "temporal_relationships": 0,
                "thematic_relationships": 0,
                "causal_relationships": 0,
                "total_relationships": 0
            }
            
            if not self.personality_memory or not self.collaboration_memory:
                print("⚠️ 記憶システムが初期化されていません")
                return analysis_stats
            
            # 個人記憶と協働記憶の取得
            personality_experiences = self.personality_memory.personality_data.get("personal_experiences", [])
            collaboration_successes = self.collaboration_memory.collaboration_data.get("success_patterns", [])
            collaboration_patterns = self.collaboration_memory.collaboration_data.get("work_patterns", [])
            
            # 1. 時系列関係分析
            analysis_stats["temporal_relationships"] = self._analyze_temporal_relationships(
                personality_experiences, collaboration_successes, collaboration_patterns
            )
            
            # 2. テーマ関係分析  
            analysis_stats["thematic_relationships"] = self._analyze_thematic_relationships(
                personality_experiences, collaboration_successes
            )
            
            # 3. 因果関係分析
            analysis_stats["causal_relationships"] = self._analyze_causal_relationships(
                personality_experiences, collaboration_successes
            )
            
            analysis_stats["total_relationships"] = len(self.integration_data["memory_relationships"])
            
            # メモリクラスター更新
            self._update_memory_clusters()
            
            print(f"✅ 記憶関係性分析完了: {old_count}件 -> {analysis_stats['total_relationships']}件")
            print(f"   - 時系列関係: {analysis_stats['temporal_relationships']}件")
            print(f"   - テーマ関係: {analysis_stats['thematic_relationships']}件")
            print(f"   - 因果関係: {analysis_stats['causal_relationships']}件")
            
            return analysis_stats
            
        except Exception as e:
            print(f"❌ 記憶関係性分析エラー: {e}")
            return {"error": str(e)}
    
    def _analyze_temporal_relationships(self, experiences: List[Dict], 
                                      successes: List[Dict], patterns: List[Dict]) -> int:
        """時系列関係を分析"""
        temporal_count = 0
        threshold_hours = self.relationship_config["temporal_threshold_hours"]
        
        # 個人体験と協働成功の時系列関係
        for exp in experiences:
            exp_time = datetime.fromisoformat(exp["date"])
            
            for success in successes:
                success_time = datetime.fromisoformat(success["date"])
                time_diff = abs((exp_time - success_time).total_seconds() / 3600)
                
                if time_diff <= threshold_hours:
                    relationship = self._create_relationship(
                        source={"type": "personality", "id": exp["id"]},
                        target={"type": "collaboration_success", "id": success["id"]},
                        relationship_type="temporal",
                        strength=max(0.1, 1.0 - (time_diff / threshold_hours)),
                        context=f"{time_diff:.1f}時間以内の近接体験",
                        metadata={
                            "time_diff_hours": time_diff,
                            "exp_emotion": exp.get("emotion", "unknown"),
                            "success_type": success.get("success_type", "unknown")
                        }
                    )
                    self.integration_data["memory_relationships"].append(relationship)
                    temporal_count += 1
        
        return temporal_count
    
    def _analyze_thematic_relationships(self, experiences: List[Dict], successes: List[Dict]) -> int:
        """テーマ関係を分析"""
        thematic_count = 0
        threshold = self.relationship_config["theme_similarity_threshold"]
        
        for exp in experiences:
            for success in successes:
                similarity_score = self._calculate_thematic_similarity(exp, success)
                
                if similarity_score >= threshold:
                    relationship = self._create_relationship(
                        source={"type": "personality", "id": exp["id"]},
                        target={"type": "collaboration_success", "id": success["id"]},
                        relationship_type="thematic",
                        strength=similarity_score,
                        context=f"テーマ類似度: {similarity_score:.2f}",
                        metadata={
                            "common_themes": self._extract_common_themes(exp, success),
                            "exp_type": exp.get("type", "unknown"),
                            "success_type": success.get("success_type", "unknown")
                        }
                    )
                    self.integration_data["memory_relationships"].append(relationship)
                    thematic_count += 1
        
        return thematic_count
    
    def _analyze_causal_relationships(self, experiences: List[Dict], successes: List[Dict]) -> int:
        """因果関係を分析"""
        causal_count = 0
        threshold = self.relationship_config["causal_confidence_threshold"]
        
        for exp in experiences:
            for success in successes:
                causal_confidence = self._estimate_causal_relationship(exp, success)
                
                if causal_confidence >= threshold:
                    relationship = self._create_relationship(
                        source={"type": "personality", "id": exp["id"]},
                        target={"type": "collaboration_success", "id": success["id"]},
                        relationship_type="causal",
                        strength=causal_confidence,
                        context=f"因果関係推定信頼度: {causal_confidence:.2f}",
                        metadata={
                            "causal_factors": self._identify_causal_factors(exp, success),
                            "learning_connection": exp.get("learning", ""),
                            "success_factors": success.get("key_factors", [])
                        }
                    )
                    self.integration_data["memory_relationships"].append(relationship)
                    causal_count += 1
        
        return causal_count
    
    def _calculate_thematic_similarity(self, exp: Dict, success: Dict) -> float:
        """テーマ類似度を計算"""
        # キーワード抽出・比較
        exp_text = f"{exp.get('description', '')} {exp.get('learning', '')}"
        success_text = f"{success.get('context', '')} {success.get('outcome', '')}"
        
        exp_keywords = self._extract_keywords(exp_text)
        success_keywords = self._extract_keywords(success_text)
        
        if not exp_keywords or not success_keywords:
            return 0.0
        
        # 共通キーワード率
        common_keywords = set(exp_keywords) & set(success_keywords)
        keyword_similarity = len(common_keywords) / max(len(exp_keywords), len(success_keywords))
        
        # 感情一致度
        emotion_similarity = 0.0
        if exp.get("emotion") and success.get("success_type"):
            emotion_map = {
                "excited": ["creative_breakthrough", "project_completion"],
                "proud": ["creative_breakthrough", "problem_solving"],
                "curious": ["learning", "efficient_workflow"],
                "determined": ["problem_solving", "project_completion"]
            }
            exp_emotion = exp.get("emotion")
            if exp_emotion in emotion_map and success.get("success_type") in emotion_map[exp_emotion]:
                emotion_similarity = 1.0
        
        # 重み付き総合類似度
        total_similarity = (
            keyword_similarity * self.relationship_config["keyword_weight"] +
            emotion_similarity * self.relationship_config["emotion_weight"]
        )
        
        return min(1.0, total_similarity)
    
    def _estimate_causal_relationship(self, exp: Dict, success: Dict) -> float:
        """因果関係の信頼度を推定"""
        confidence_factors = []
        
        # 時系列順序（体験が成功より前）
        try:
            exp_time = datetime.fromisoformat(exp["date"])
            success_time = datetime.fromisoformat(success["date"])
            
            if exp_time < success_time:
                time_diff_days = (success_time - exp_time).days
                if time_diff_days <= 30:  # 30日以内
                    temporal_factor = max(0.1, 1.0 - (time_diff_days / 30))
                    confidence_factors.append(temporal_factor)
        except:
            pass
        
        # 学習内容と成功要因の関連性
        exp_learning = exp.get("learning", "").lower()
        success_factors = [f.lower() for f in success.get("key_factors", [])]
        
        learning_factor = 0.0
        for factor in success_factors:
            if any(word in factor for word in exp_learning.split()):
                learning_factor = 0.8
                break
        
        if learning_factor > 0:
            confidence_factors.append(learning_factor)
        
        # タイプ関連性
        type_factor = 0.0
        exp_type = exp.get("type", "")
        success_type = success.get("success_type", "")
        
        type_correlations = {
            "learning": ["problem_solving", "efficient_workflow"],
            "creation": ["creative_breakthrough", "project_completion"],
            "challenge": ["problem_solving", "project_completion"]
        }
        
        if exp_type in type_correlations and success_type in type_correlations[exp_type]:
            type_factor = 0.7
            confidence_factors.append(type_factor)
        
        # 総合信頼度
        if not confidence_factors:
            return 0.0
        
        return min(1.0, sum(confidence_factors) / len(confidence_factors))
    
    def _extract_keywords(self, text: str) -> List[str]:
        """テキストからキーワードを抽出"""
        if not text:
            return []
        
        # 基本的な形態素解析の代替（シンプル版）
        keywords = []
        
        # 日本語の重要キーワードリスト
        important_words = [
            "音楽", "創作", "歌", "動画", "プロジェクト", "学習", "技術", "プログラミング",
            "アイデア", "制作", "作業", "効率", "改善", "成功", "完成", "挑戦", "経験",
            "集中", "理解", "習得", "開発", "設計", "企画", "計画", "実装", "テスト"
        ]
        
        for word in important_words:
            if word in text:
                keywords.append(word)
        
        # 英単語の抽出
        english_words = re.findall(r'[a-zA-Z]+', text)
        keywords.extend([w.lower() for w in english_words if len(w) >= 3])
        
        return list(set(keywords))
    
    def _extract_common_themes(self, exp: Dict, success: Dict) -> List[str]:
        """共通テーマを抽出"""
        exp_text = f"{exp.get('description', '')} {exp.get('learning', '')}"
        success_text = f"{success.get('context', '')} {success.get('outcome', '')}"
        
        exp_keywords = set(self._extract_keywords(exp_text))
        success_keywords = set(self._extract_keywords(success_text))
        
        return list(exp_keywords & success_keywords)
    
    def _identify_causal_factors(self, exp: Dict, success: Dict) -> List[str]:
        """因果要因を特定"""
        factors = []
        
        # 学習内容の影響
        if exp.get("learning"):
            factors.append(f"学習: {exp['learning'][:30]}...")
        
        # 感情状態の影響
        if exp.get("emotion"):
            factors.append(f"感情: {exp['emotion']}")
        
        # 体験タイプの影響
        if exp.get("type"):
            factors.append(f"体験タイプ: {exp['type']}")
        
        return factors
    
    def _create_relationship(self, source: Dict, target: Dict, relationship_type: str,
                           strength: float, context: str, metadata: Dict = None) -> Dict:
        """関係性レコードを作成"""
        relationship_id = self._generate_relationship_id(source, target, relationship_type)
        
        return {
            "relationship_id": relationship_id,
            "source_memory": source,
            "target_memory": target,
            "relationship_type": relationship_type,
            "strength": round(strength, 3),
            "context": context,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat(),
            "last_referenced": None,
            "reference_count": 0
        }
    
    def _generate_relationship_id(self, source: Dict, target: Dict, rel_type: str) -> str:
        """関係性IDを生成"""
        content = f"{source['type']}_{source['id']}_{target['type']}_{target['id']}_{rel_type}"
        hash_value = hashlib.md5(content.encode()).hexdigest()[:8]
        return f"rel_{hash_value}"
    
    def _update_memory_clusters(self):
        """記憶クラスターを更新"""
        clusters = {}
        
        # 関係性データからクラスターを生成
        for rel in self.integration_data["memory_relationships"]:
            # 強い関係性（0.6以上）のみクラスター化
            if rel["strength"] >= 0.6:
                cluster_theme = self._determine_cluster_theme(rel)
                
                if cluster_theme not in clusters:
                    clusters[cluster_theme] = {
                        "personality_memories": [],
                        "collaboration_memories": [],
                        "theme": cluster_theme,
                        "total_relationships": 0,
                        "average_strength": 0.0
                    }
                
                # メモリをクラスターに追加
                if rel["source_memory"]["type"] == "personality":
                    if rel["source_memory"]["id"] not in clusters[cluster_theme]["personality_memories"]:
                        clusters[cluster_theme]["personality_memories"].append(rel["source_memory"]["id"])
                
                if rel["target_memory"]["type"].startswith("collaboration"):
                    if rel["target_memory"]["id"] not in clusters[cluster_theme]["collaboration_memories"]:
                        clusters[cluster_theme]["collaboration_memories"].append(rel["target_memory"]["id"])
                
                clusters[cluster_theme]["total_relationships"] += 1
        
        # 平均強度を計算
        for cluster_name, cluster_data in clusters.items():
            related_rels = [rel for rel in self.integration_data["memory_relationships"] 
                          if self._determine_cluster_theme(rel) == cluster_name]
            if related_rels:
                cluster_data["average_strength"] = sum(rel["strength"] for rel in related_rels) / len(related_rels)
        
        self.integration_data["memory_clusters"] = clusters
        print(f"🔗 記憶クラスター更新: {len(clusters)}個のクラスター生成")
    
    def _determine_cluster_theme(self, relationship: Dict) -> str:
        """関係性からクラスターテーマを決定"""
        metadata = relationship.get("metadata", {})
        
        # メタデータから共通テーマを抽出
        if "common_themes" in metadata and metadata["common_themes"]:
            primary_theme = metadata["common_themes"][0]
            return f"{primary_theme}_cluster"
        
        # 体験タイプと成功タイプから推定
        exp_type = metadata.get("exp_type", "")
        success_type = metadata.get("success_type", "")
        
        if exp_type == "creation" or "creative" in success_type:
            return "creative_growth"
        elif exp_type == "learning" or "problem" in success_type:
            return "learning_development"
        elif exp_type == "challenge":
            return "challenge_mastery"
        else:
            return "general_development"
    
    def find_related_memories(self, memory_id: str, memory_type: str, 
                            max_results: int = 5) -> List[Dict]:
        """
        指定記憶に関連する記憶を検索
        
        Args:
            memory_id: 検索基準となる記憶ID
            memory_type: 記憶タイプ ("personality" or "collaboration")
            max_results: 最大結果数
            
        Returns:
            List[Dict]: 関連記憶リスト（関連度順）
        """
        related_memories = []
        
        for rel in self.integration_data["memory_relationships"]:
            source = rel["source_memory"]
            target = rel["target_memory"]
            
            # 指定記憶が関係性に含まれているかチェック
            if (source["type"] == memory_type and source["id"] == memory_id):
                related_memories.append({
                    "memory": target,
                    "relationship": rel,
                    "relevance_score": rel["strength"]
                })
            elif (target["type"] == memory_type and target["id"] == memory_id):
                related_memories.append({
                    "memory": source,
                    "relationship": rel,
                    "relevance_score": rel["strength"]
                })
        
        # 関連度順でソート
        related_memories.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return related_memories[:max_results]
    
    def generate_integrated_context(self, user_input: str = "", context_type: str = "full") -> str:
        """
        統合記憶コンテキストを生成
        
        Args:
            user_input: ユーザー入力（関連記憶検索用）
            context_type: コンテキストタイプ ("full", "recent", "relevant")
            
        Returns:
            str: 統合プロンプトコンテキスト
        """
        try:
            context_parts = []
            
            if context_type == "full":
                # 完全な統合コンテキスト
                context_parts.extend(self._generate_relationship_summary())
                context_parts.extend(self._generate_cluster_insights())
                context_parts.extend(self._generate_adaptive_insights())
                
            elif context_type == "recent":
                # 最近の統合記憶のみ
                context_parts.extend(self._generate_recent_relationships())
                
            elif context_type == "relevant":
                # ユーザー入力に関連する記憶のみ
                context_parts.extend(self._generate_relevant_context(user_input))
            
            return "\n".join(context_parts) if context_parts else ""
            
        except Exception as e:
            print(f"❌ 統合コンテキスト生成エラー: {e}")
            return ""
    
    def _generate_relationship_summary(self) -> List[str]:
        """関係性サマリーを生成"""
        summary_parts = []
        relationships = self.integration_data["memory_relationships"]
        
        if not relationships:
            return summary_parts
        
        # 強い関係性のみ表示
        strong_rels = [r for r in relationships if r["strength"] >= 0.7]
        
        if strong_rels:
            summary_parts.append("【記憶間の重要な関連性】")
            
            for rel in strong_rels[:3]:  # 上位3件
                rel_type_name = self.integration_data["relationship_types"].get(
                    rel["relationship_type"], rel["relationship_type"]
                )
                summary_parts.append(
                    f"- {rel_type_name}: {rel['context']} (関連度: {rel['strength']:.2f})"
                )
        
        return summary_parts
    
    def _generate_cluster_insights(self) -> List[str]:
        """クラスター洞察を生成"""
        insights = []
        clusters = self.integration_data["memory_clusters"]
        
        if not clusters:
            return insights
        
        insights.append("\n【統合記憶パターン】")
        
        # 最も活発なクラスター（記憶数が多い）を表示
        sorted_clusters = sorted(
            clusters.items(), 
            key=lambda x: len(x[1]["personality_memories"]) + len(x[1]["collaboration_memories"]),
            reverse=True
        )
        
        for cluster_name, cluster_data in sorted_clusters[:2]:  # 上位2クラスター
            total_memories = len(cluster_data["personality_memories"]) + len(cluster_data["collaboration_memories"])
            avg_strength = cluster_data.get("average_strength", 0)
            
            insights.append(
                f"- {cluster_data['theme']}: {total_memories}件の関連記憶 (関連度: {avg_strength:.2f})"
            )
        
        return insights
    
    def _generate_adaptive_insights(self) -> List[str]:
        """適応的洞察を生成"""
        insights = []
        
        # パフォーマンスベースの洞察
        performance_insight = self._analyze_performance_patterns()
        if performance_insight:
            insights.append("\n【学習・成長パターン】")
            insights.append(f"- {performance_insight}")
        
        # 協働効果の洞察
        collaboration_insight = self._analyze_collaboration_effectiveness()
        if collaboration_insight:
            if not insights:
                insights.append("\n【協働効果分析】")
            else:
                insights.append("- " + collaboration_insight)
        
        return insights
    
    def _generate_recent_relationships(self) -> List[str]:
        """最近の関係性を生成"""
        recent_parts = []
        relationships = self.integration_data["memory_relationships"]
        
        # 過去7日以内の関係性
        cutoff_date = datetime.now() - timedelta(days=7)
        recent_rels = [
            rel for rel in relationships 
            if datetime.fromisoformat(rel["created_at"]) >= cutoff_date
        ]
        
        if recent_rels:
            recent_parts.append("【最近発見された記憶関連性】")
            
            for rel in recent_rels[-3:]:  # 最新3件
                recent_parts.append(f"- {rel['context']}")
        
        return recent_parts
    
    def _generate_relevant_context(self, user_input: str) -> List[str]:
        """ユーザー入力に関連するコンテキストを生成"""
        relevant_parts = []
        
        if not user_input:
            return relevant_parts
        
        # キーワード抽出
        input_keywords = self._extract_keywords(user_input)
        
        if not input_keywords:
            return relevant_parts
        
        # 関連する関係性を検索
        relevant_relationships = []
        
        for rel in self.integration_data["memory_relationships"]:
            # メタデータから関連性をチェック
            metadata = rel.get("metadata", {})
            
            # 共通テーマとの一致
            common_themes = metadata.get("common_themes", [])
            if any(theme in input_keywords for theme in common_themes):
                relevant_relationships.append(rel)
                continue
            
            # 関係性コンテキストとの一致
            context_keywords = self._extract_keywords(rel.get("context", ""))
            if set(input_keywords) & set(context_keywords):
                relevant_relationships.append(rel)
        
        if relevant_relationships:
            relevant_parts.append("【関連する過去の体験・成功パターン】")
            
            # 関連度でソート
            relevant_relationships.sort(key=lambda x: x["strength"], reverse=True)
            
            for rel in relevant_relationships[:3]:  # 上位3件
                relevant_parts.append(f"- {rel['context']} (関連度: {rel['strength']:.2f})")
        
        return relevant_parts
    
    def _analyze_performance_patterns(self) -> str:
        """パフォーマンスパターンを分析"""
        if not self.personality_memory or not self.collaboration_memory:
            return ""
        
        # キャラクター進化と協働成功の関連性を分析
        evolution = self.personality_memory.personality_data.get("character_evolution", {})
        partnership = self.collaboration_memory.collaboration_data.get("partnership_evolution", {})
        
        confidence = evolution.get("confidence_level", 0.5)
        creative_exp = evolution.get("creative_experience", 0.7)
        creative_compat = partnership.get("creative_compatibility", 0.6)
        
        if confidence >= 0.7 and creative_compat >= 0.7:
            return "自信と創作適合性の向上が相互に強化している"
        elif creative_exp >= 0.8 and creative_compat >= 0.6:
            return "創作経験の蓄積が協働品質向上に寄与している"
        elif confidence < 0.4 and creative_compat < 0.5:
            return "自信向上が協働効率改善の鍵となる可能性"
        
        return ""
    
    def _analyze_collaboration_effectiveness(self) -> str:
        """協働効果を分析"""
        if not self.collaboration_memory:
            return ""
        
        # 作業パターンと成功パターンの関連性
        work_patterns = self.collaboration_memory.collaboration_data.get("work_patterns", [])
        success_patterns = self.collaboration_memory.collaboration_data.get("success_patterns", [])
        
        if not work_patterns or not success_patterns:
            return ""
        
        # 高効率作業と成功の相関
        high_efficiency_works = [w for w in work_patterns if w.get("efficiency_score", 0) >= 0.7]
        high_impact_successes = [s for s in success_patterns if s.get("impact_rating", 0) >= 0.7]
        
        if len(high_efficiency_works) >= 2 and len(high_impact_successes) >= 1:
            return "高効率作業パターンが成功につながる傾向"
        
        return ""
    
    def suggest_adaptive_responses(self, user_input: str, current_context: Dict = None) -> List[str]:
        """
        適応的応答を提案
        
        Args:
            user_input: ユーザー入力
            current_context: 現在のコンテキスト情報
            
        Returns:
            List[str]: 応答提案リスト
        """
        suggestions = []
        
        try:
            # 関連する過去の成功パターンから提案
            related_memories = self._find_memories_by_keywords(user_input)
            
            for memory in related_memories[:2]:  # 上位2件
                if memory["memory"]["type"] == "collaboration_success":
                    success_data = self._get_success_data_by_id(memory["memory"]["id"])
                    if success_data:
                        suggestions.append(
                            f"過去の{success_data.get('success_type', '成功')}体験を活かして: {success_data.get('outcome', '')[:40]}..."
                        )
            
            # クラスター情報から提案
            cluster_suggestions = self._get_cluster_based_suggestions(user_input)
            suggestions.extend(cluster_suggestions)
            
            return suggestions[:3]  # 最大3つの提案
            
        except Exception as e:
            print(f"❌ 適応的応答提案エラー: {e}")
            return []
    
    def _find_memories_by_keywords(self, user_input: str) -> List[Dict]:
        """キーワードベースで記憶を検索"""
        input_keywords = self._extract_keywords(user_input)
        
        if not input_keywords:
            return []
        
        matching_memories = []
        
        for rel in self.integration_data["memory_relationships"]:
            metadata = rel.get("metadata", {})
            common_themes = metadata.get("common_themes", [])
            
            # キーワード一致度計算
            match_score = len(set(input_keywords) & set(common_themes)) / max(len(input_keywords), 1)
            
            if match_score > 0:
                matching_memories.append({
                    "memory": rel["target_memory"],
                    "relevance_score": match_score * rel["strength"],
                    "relationship": rel
                })
        
        # 関連度順でソート
        matching_memories.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return matching_memories
    
    def _get_success_data_by_id(self, success_id: str) -> Optional[Dict]:
        """成功データをIDで取得"""
        if not self.collaboration_memory:
            return None
        
        successes = self.collaboration_memory.collaboration_data.get("success_patterns", [])
        
        for success in successes:
            if success.get("id") == success_id:
                return success
        
        return None
    
    def _get_cluster_based_suggestions(self, user_input: str) -> List[str]:
        """クラスターベースの提案を生成"""
        suggestions = []
        input_keywords = self._extract_keywords(user_input)
        
        for cluster_name, cluster_data in self.integration_data["memory_clusters"].items():
            # クラスターテーマとの関連性チェック
            theme = cluster_data.get("theme", "")
            
            if any(keyword in theme for keyword in input_keywords):
                suggestion = f"{theme}の経験を活かしたアプローチがおすすめ"
                suggestions.append(suggestion)
        
        return suggestions
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """記憶統合統計情報を取得"""
        relationships = self.integration_data["memory_relationships"]
        clusters = self.integration_data["memory_clusters"]
        
        # 関係性タイプ別統計
        type_stats = {}
        for rel_type in self.integration_data["relationship_types"].keys():
            type_stats[rel_type] = len([r for r in relationships if r["relationship_type"] == rel_type])
        
        # 強度別統計
        strong_relationships = len([r for r in relationships if r["strength"] >= 0.7])
        moderate_relationships = len([r for r in relationships if 0.4 <= r["strength"] < 0.7])
        weak_relationships = len([r for r in relationships if r["strength"] < 0.4])
        
        return {
            "total_relationships": len(relationships),
            "total_clusters": len(clusters),
            "relationship_types": type_stats,
            "strength_distribution": {
                "strong": strong_relationships,
                "moderate": moderate_relationships,
                "weak": weak_relationships
            },
            "memory_mode": self.memory_mode,
            "last_analysis": datetime.now().isoformat()
        }

if __name__ == "__main__":
    # テスト実行
    print("=== MemoryIntegrationSystem テスト ===")
    
    # 基本初期化テスト
    print("\n--- 基本初期化 ---")
    integration = MemoryIntegrationSystem(memory_mode="test")
    
    # 統計情報テスト
    stats = integration.get_memory_stats()
    print(f"初期統計: {stats}")
    
    print("\n✅ MemoryIntegrationSystem 基盤テスト完了")
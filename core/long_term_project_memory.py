#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
長期プロジェクト記憶統合システム
既存のProjectSystem、MemoryIntegrationSystem、CollaborationMemoryを統合し、
長期プロジェクトの文脈維持と記憶関連付けを管理する
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import hashlib

# 既存システムのインポート
from project_system import ProjectSystem
from enhanced_memory.memory_integration import MemoryIntegrationSystem
from enhanced_memory.collaboration_memory import CollaborationMemory
from enhanced_memory.personality_memory import PersonalityMemory


class LongTermProjectMemory:
    """長期プロジェクト記憶統合システム"""
    
    def __init__(self, project_system=None, memory_integration=None, 
                 collaboration_memory=None, personality_memory=None, memory_mode="normal"):
        """
        長期プロジェクト記憶システム初期化
        
        Args:
            project_system: ProjectSystemインスタンス
            memory_integration: MemoryIntegrationSystemインスタンス
            collaboration_memory: CollaborationMemoryインスタンス
            personality_memory: PersonalityMemoryインスタンス
            memory_mode: "normal" または "test"
        """
        # 既存システムとの統合
        self.project_system = project_system or ProjectSystem()
        self.memory_integration = memory_integration
        self.collaboration_memory = collaboration_memory
        self.personality_memory = personality_memory
        self.memory_mode = memory_mode
        
        # 環境に応じてパスを決定
        if os.path.exists("/mnt/d/setsuna_bot"):
            base_path = Path("/mnt/d/setsuna_bot")
        else:
            base_path = Path("D:/setsuna_bot")
        
        # データファイルパス設定
        if memory_mode == "test":
            self.project_memory_file = base_path / "temp" / f"test_project_memory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            os.makedirs(self.project_memory_file.parent, exist_ok=True)
        else:
            self.project_memory_file = base_path / "enhanced_memory" / "long_term_project_memory.json"
            os.makedirs(self.project_memory_file.parent, exist_ok=True)
        
        # 長期プロジェクト記憶データ構造
        self.project_memory_data = {
            "project_contexts": {},           # プロジェクト別統合文脈
            "memory_links": {},              # プロジェクト-記憶リンク
            "decision_chains": {},           # 意思決定チェーン
            "context_snapshots": {},         # 文脈スナップショット
            "project_relationships": [],     # プロジェクト間関係性
            "long_term_patterns": {},        # 長期パターン分析
            "created_at": datetime.now().isoformat(),
            "version": "1.0"
        }
        
        # 設定パラメータ
        self.config = {
            "max_context_memory_days": 180,      # 文脈記憶保持期間（日）
            "memory_link_threshold": 0.3,        # 記憶リンク閾値
            "decision_importance_threshold": 0.5, # 意思決定重要度閾値
            "snapshot_interval_hours": 24,       # スナップショット間隔（時間）
            "auto_link_enabled": True            # 自動リンク機能
        }
        
        # データ読み込み
        self._load_project_memory_data()
        
        print(f"🔗 長期プロジェクト記憶システム初期化完了 ({memory_mode}モード)")
    
    def _load_project_memory_data(self):
        """長期プロジェクト記憶データを読み込み"""
        if self.project_memory_file.exists() and self.memory_mode == "normal":
            try:
                with open(self.project_memory_file, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                    self.project_memory_data.update(loaded_data)
                
                contexts_count = len(self.project_memory_data.get("project_contexts", {}))
                links_count = len(self.project_memory_data.get("memory_links", {}))
                print(f"✅ 長期プロジェクト記憶読み込み: 文脈{contexts_count}件, リンク{links_count}件")
                
            except Exception as e:
                print(f"⚠️ 長期プロジェクト記憶読み込みエラー: {e}")
        else:
            print("🆕 新規長期プロジェクト記憶データベース作成")
    
    def save_project_memory_data(self):
        """長期プロジェクト記憶データを保存"""
        if self.memory_mode == "test":
            return
        
        try:
            # 古いデータのクリーンアップ
            self._cleanup_old_data()
            
            with open(self.project_memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.project_memory_data, f, ensure_ascii=False, indent=2)
            print(f"💾 長期プロジェクト記憶データ保存完了")
        except Exception as e:
            print(f"❌ 長期プロジェクト記憶データ保存エラー: {e}")
    
    def link_project_to_memories(self, project_id: str, force_relink: bool = False) -> Dict[str, int]:
        """
        プロジェクトと関連記憶を自動関連付け
        
        Args:
            project_id: プロジェクトID
            force_relink: 強制再リンクフラグ
            
        Returns:
            Dict[str, int]: リンク結果統計
        """
        try:
            print(f"🔍 プロジェクト記憶リンク開始: {project_id}")
            
            # プロジェクト情報取得
            project = self._get_project_by_id(project_id)
            if not project:
                print(f"⚠️ プロジェクトが見つかりません: {project_id}")
                return {}
            
            # 既存リンクをクリア（再リンク時）
            if force_relink and project_id in self.project_memory_data["memory_links"]:
                del self.project_memory_data["memory_links"][project_id]
            
            # プロジェクト-記憶リンク初期化
            if project_id not in self.project_memory_data["memory_links"]:
                self.project_memory_data["memory_links"][project_id] = {
                    "collaboration_memories": [],
                    "personality_memories": [],
                    "integration_patterns": [],
                    "last_updated": datetime.now().isoformat()
                }
            
            link_stats = {
                "collaboration_links": 0,
                "personality_links": 0,
                "integration_links": 0,
                "total_links": 0
            }
            
            # 協働記憶とのリンク
            if self.collaboration_memory:
                collab_links = self._link_collaboration_memories(project, project_id)
                link_stats["collaboration_links"] = len(collab_links)
                self.project_memory_data["memory_links"][project_id]["collaboration_memories"].extend(collab_links)
            
            # 個人記憶とのリンク
            if self.personality_memory:
                person_links = self._link_personality_memories(project, project_id)
                link_stats["personality_links"] = len(person_links)
                self.project_memory_data["memory_links"][project_id]["personality_memories"].extend(person_links)
            
            # 統合記憶パターンとのリンク
            if self.memory_integration:
                integration_links = self._link_integration_patterns(project, project_id)
                link_stats["integration_links"] = len(integration_links)
                self.project_memory_data["memory_links"][project_id]["integration_patterns"].extend(integration_links)
            
            link_stats["total_links"] = (
                link_stats["collaboration_links"] + 
                link_stats["personality_links"] + 
                link_stats["integration_links"]
            )
            
            # リンク更新時刻を記録
            self.project_memory_data["memory_links"][project_id]["last_updated"] = datetime.now().isoformat()
            
            print(f"✅ プロジェクト記憶リンク完了: {link_stats['total_links']}件")
            return link_stats
            
        except Exception as e:
            print(f"❌ プロジェクト記憶リンクエラー: {e}")
            return {}
    
    def get_project_context_history(self, project_id: str, days_back: int = 30) -> Dict[str, Any]:
        """
        プロジェクト関連の全記憶を時系列で取得
        
        Args:
            project_id: プロジェクトID
            days_back: 遡る日数
            
        Returns:
            Dict[str, Any]: 統合プロジェクト文脈
        """
        try:
            print(f"📋 プロジェクト文脈履歴取得: {project_id}")
            
            # プロジェクト基本情報
            project = self._get_project_by_id(project_id)
            if not project:
                return {}
            
            # 対象期間設定
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days_back)
            
            # 統合文脈構築
            context_history = {
                "project_info": project,
                "timeline": [],
                "memory_summary": {
                    "collaboration_memories": [],
                    "personality_memories": [],
                    "decision_points": [],
                    "key_insights": []
                },
                "context_evolution": [],
                "generated_at": datetime.now().isoformat()
            }
            
            # リンクされた記憶を取得
            linked_memories = self.project_memory_data.get("memory_links", {}).get(project_id, {})
            
            # 協働記憶の統合
            if self.collaboration_memory and linked_memories.get("collaboration_memories"):
                collab_context = self._build_collaboration_context(linked_memories["collaboration_memories"], start_date, end_date)
                context_history["memory_summary"]["collaboration_memories"] = collab_context
            
            # 個人記憶の統合
            if self.personality_memory and linked_memories.get("personality_memories"):
                person_context = self._build_personality_context(linked_memories["personality_memories"], start_date, end_date)
                context_history["memory_summary"]["personality_memories"] = person_context
            
            # 意思決定履歴の統合
            decision_history = self.project_memory_data.get("decision_chains", {}).get(project_id, [])
            context_history["memory_summary"]["decision_points"] = self._filter_decisions_by_date(decision_history, start_date, end_date)
            
            # タイムライン構築
            context_history["timeline"] = self._build_project_timeline(project_id, start_date, end_date)
            
            print(f"✅ プロジェクト文脈履歴構築完了")
            return context_history
            
        except Exception as e:
            print(f"❌ プロジェクト文脈履歴取得エラー: {e}")
            return {}
    
    def analyze_project_decision_patterns(self, project_id: str) -> Dict[str, Any]:
        """
        過去の意思決定パターンを分析
        
        Args:
            project_id: プロジェクトID
            
        Returns:
            Dict[str, Any]: 意思決定パターン分析結果
        """
        try:
            print(f"🧠 プロジェクト意思決定パターン分析: {project_id}")
            
            # 意思決定履歴取得
            decision_chain = self.project_memory_data.get("decision_chains", {}).get(project_id, [])
            
            if not decision_chain:
                print(f"📋 意思決定履歴なし: {project_id}")
                return {
                    "pattern_summary": "意思決定履歴が不足しています",
                    "recommendations": [],
                    "confidence": 0.0
                }
            
            # パターン分析
            analysis_result = {
                "total_decisions": len(decision_chain),
                "decision_types": {},
                "success_patterns": [],
                "risk_patterns": [],
                "timing_patterns": {},
                "confidence_trends": [],
                "recommendations": [],
                "pattern_summary": "",
                "analyzed_at": datetime.now().isoformat()
            }
            
            # 意思決定タイプ分析
            for decision in decision_chain:
                decision_type = decision.get("type", "unknown")
                if decision_type not in analysis_result["decision_types"]:
                    analysis_result["decision_types"][decision_type] = 0
                analysis_result["decision_types"][decision_type] += 1
            
            # 成功パターン抽出
            successful_decisions = [d for d in decision_chain if d.get("outcome_success", False)]
            analysis_result["success_patterns"] = self._extract_decision_patterns(successful_decisions, "success")
            
            # リスクパターン抽出
            risky_decisions = [d for d in decision_chain if d.get("risk_level", 0) > 0.7]
            analysis_result["risk_patterns"] = self._extract_decision_patterns(risky_decisions, "risk")
            
            # タイミング分析
            analysis_result["timing_patterns"] = self._analyze_decision_timing(decision_chain)
            
            # 推薦事項生成
            analysis_result["recommendations"] = self._generate_decision_recommendations(analysis_result)
            
            # パターンサマリー生成
            analysis_result["pattern_summary"] = self._generate_pattern_summary(analysis_result)
            
            print(f"✅ 意思決定パターン分析完了: {len(successful_decisions)}件の成功パターン")
            return analysis_result
            
        except Exception as e:
            print(f"❌ 意思決定パターン分析エラー: {e}")
            return {}
    
    def record_project_decision(self, project_id: str, decision_data: Dict[str, Any]) -> bool:
        """
        プロジェクトの意思決定を記録
        
        Args:
            project_id: プロジェクトID
            decision_data: 意思決定データ
            
        Returns:
            bool: 記録成功フラグ
        """
        try:
            # 意思決定チェーン初期化
            if project_id not in self.project_memory_data["decision_chains"]:
                self.project_memory_data["decision_chains"][project_id] = []
            
            # 意思決定記録構造
            decision_record = {
                "id": f"decision_{len(self.project_memory_data['decision_chains'][project_id]) + 1:03d}",
                "timestamp": datetime.now().isoformat(),
                "type": decision_data.get("type", "general"),
                "description": decision_data.get("description", ""),
                "options_considered": decision_data.get("options", []),
                "chosen_option": decision_data.get("chosen", ""),
                "reasoning": decision_data.get("reasoning", ""),
                "confidence_level": decision_data.get("confidence", 0.5),
                "risk_level": decision_data.get("risk", 0.3),
                "expected_outcome": decision_data.get("expected", ""),
                "context_snapshot": self._capture_current_context(project_id),
                "outcome_success": None,  # 後で評価
                "actual_outcome": None,   # 後で記録
                "lessons_learned": None   # 後で記録
            }
            
            # 意思決定チェーンに追加
            self.project_memory_data["decision_chains"][project_id].append(decision_record)
            
            print(f"📝 意思決定記録: {decision_record['id']} - {decision_data.get('type', 'general')}")
            return True
            
        except Exception as e:
            print(f"❌ 意思決定記録エラー: {e}")
            return False
    
    def capture_context_snapshot(self, project_id: str, snapshot_type: str = "auto") -> bool:
        """
        現在の文脈スナップショットを保存
        
        Args:
            project_id: プロジェクトID
            snapshot_type: スナップショットタイプ（auto/manual/milestone）
            
        Returns:
            bool: 保存成功フラグ
        """
        try:
            # スナップショット記録初期化
            if project_id not in self.project_memory_data["context_snapshots"]:
                self.project_memory_data["context_snapshots"][project_id] = []
            
            # 現在の文脈キャプチャ
            snapshot = {
                "id": f"snapshot_{len(self.project_memory_data['context_snapshots'][project_id]) + 1:03d}",
                "timestamp": datetime.now().isoformat(),
                "type": snapshot_type,
                "project_state": self._capture_current_context(project_id),
                "memory_state": self._capture_memory_state(project_id),
                "conversation_context": self._capture_conversation_context(),
                "system_metrics": self._capture_system_metrics()
            }
            
            # スナップショット追加
            self.project_memory_data["context_snapshots"][project_id].append(snapshot)
            
            # 古いスナップショットのクリーンアップ（最新30件まで保持）
            if len(self.project_memory_data["context_snapshots"][project_id]) > 30:
                self.project_memory_data["context_snapshots"][project_id] = (
                    self.project_memory_data["context_snapshots"][project_id][-30:]
                )
            
            print(f"📸 文脈スナップショット保存: {snapshot['id']} ({snapshot_type})")
            return True
            
        except Exception as e:
            print(f"❌ 文脈スナップショット保存エラー: {e}")
            return False
    
    # ========== 内部ヘルパーメソッド ==========
    
    def _get_project_by_id(self, project_id: str) -> Optional[Dict[str, Any]]:
        """プロジェクトIDからプロジェクト情報を取得"""
        if not self.project_system:
            return None
        
        # アクティブプロジェクトから検索
        for project in self.project_system.get_active_projects():
            if project.get("id") == project_id:
                return project
        
        # 完了プロジェクトから検索
        for project in self.project_system.get_completed_projects():
            if project.get("id") == project_id:
                return project
        
        return None
    
    def _link_collaboration_memories(self, project: Dict[str, Any], project_id: str) -> List[Dict[str, Any]]:
        """協働記憶とのリンク生成"""
        links = []
        
        if not self.collaboration_memory:
            return links
        
        try:
            # プロジェクトキーワード抽出
            project_keywords = self._extract_project_keywords(project)
            
            # 協働記憶データ取得
            collab_data = self.collaboration_memory.collaboration_data
            
            # 成功パターンとのマッチング
            for success_pattern in collab_data.get("success_patterns", []):
                relevance = self._calculate_relevance(project_keywords, success_pattern)
                if relevance > self.config["memory_link_threshold"]:
                    links.append({
                        "memory_type": "success_pattern",
                        "memory_id": success_pattern.get("id"),
                        "relevance": relevance,
                        "linked_at": datetime.now().isoformat()
                    })
            
            # 作業パターンとのマッチング
            for work_pattern in collab_data.get("work_patterns", []):
                relevance = self._calculate_relevance(project_keywords, work_pattern)
                if relevance > self.config["memory_link_threshold"]:
                    links.append({
                        "memory_type": "work_pattern",
                        "memory_id": work_pattern.get("id"),
                        "relevance": relevance,
                        "linked_at": datetime.now().isoformat()
                    })
            
        except Exception as e:
            print(f"⚠️ 協働記憶リンクエラー: {e}")
        
        return links
    
    def _link_personality_memories(self, project: Dict[str, Any], project_id: str) -> List[Dict[str, Any]]:
        """個人記憶とのリンク生成"""
        links = []
        
        if not self.personality_memory:
            return links
        
        try:
            project_keywords = self._extract_project_keywords(project)
            person_data = self.personality_memory.personality_data
            
            # 個人体験とのマッチング
            for experience in person_data.get("personal_experiences", []):
                relevance = self._calculate_relevance(project_keywords, experience)
                if relevance > self.config["memory_link_threshold"]:
                    links.append({
                        "memory_type": "personal_experience",
                        "memory_id": experience.get("id"),
                        "relevance": relevance,
                        "linked_at": datetime.now().isoformat()
                    })
            
            # 学習体験とのマッチング
            for learning in person_data.get("learning_experiences", []):
                relevance = self._calculate_relevance(project_keywords, learning)
                if relevance > self.config["memory_link_threshold"]:
                    links.append({
                        "memory_type": "learning_experience",
                        "memory_id": learning.get("id"),
                        "relevance": relevance,
                        "linked_at": datetime.now().isoformat()
                    })
            
        except Exception as e:
            print(f"⚠️ 個人記憶リンクエラー: {e}")
        
        return links
    
    def _link_integration_patterns(self, project: Dict[str, Any], project_id: str) -> List[Dict[str, Any]]:
        """統合記憶パターンとのリンク生成"""
        links = []
        
        if not self.memory_integration:
            return links
        
        try:
            project_keywords = self._extract_project_keywords(project)
            integration_data = self.memory_integration.integration_data
            
            # 統合パターンとのマッチング
            for pattern in integration_data.get("integration_patterns", []):
                relevance = self._calculate_relevance(project_keywords, pattern)
                if relevance > self.config["memory_link_threshold"]:
                    links.append({
                        "memory_type": "integration_pattern",
                        "memory_id": pattern.get("id"),
                        "relevance": relevance,
                        "linked_at": datetime.now().isoformat()
                    })
            
        except Exception as e:
            print(f"⚠️ 統合記憶リンクエラー: {e}")
        
        return links
    
    def _extract_project_keywords(self, project: Dict[str, Any]) -> List[str]:
        """プロジェクトからキーワードを抽出"""
        keywords = []
        
        # タイトルから
        title = project.get("title", "")
        keywords.extend(title.split())
        
        # 説明から
        description = project.get("description", "")
        keywords.extend(description.split())
        
        # タイプから
        project_type = project.get("type", "")
        keywords.append(project_type)
        
        # ノートから
        notes = project.get("notes", [])
        for note in notes:
            if isinstance(note, str):
                keywords.extend(note.split())
        
        # 重複除去と小文字化
        keywords = list(set([k.lower() for k in keywords if k]))
        
        return keywords
    
    def _calculate_relevance(self, project_keywords: List[str], memory_item: Dict[str, Any]) -> float:
        """プロジェクトと記憶アイテムの関連度を計算"""
        if not project_keywords:
            return 0.0
        
        # 記憶アイテムからキーワード抽出
        memory_text = ""
        for key in ["content", "description", "context", "notes", "title"]:
            if key in memory_item:
                memory_text += str(memory_item[key]) + " "
        
        memory_keywords = memory_text.lower().split()
        
        if not memory_keywords:
            return 0.0
        
        # 共通キーワード数による関連度計算
        common_keywords = set(project_keywords) & set(memory_keywords)
        relevance = len(common_keywords) / max(len(project_keywords), len(memory_keywords))
        
        return min(relevance, 1.0)
    
    def _capture_current_context(self, project_id: str) -> Dict[str, Any]:
        """現在のプロジェクト文脈をキャプチャ"""
        project = self._get_project_by_id(project_id)
        
        context = {
            "project_snapshot": project,
            "timestamp": datetime.now().isoformat(),
            "active_memories": self._get_active_memory_count(),
            "system_state": "normal"
        }
        
        return context
    
    def _capture_memory_state(self, project_id: str) -> Dict[str, Any]:
        """記憶システムの状態をキャプチャ"""
        memory_state = {
            "linked_memories_count": 0,
            "last_memory_update": None,
            "memory_types": []
        }
        
        # リンクされた記憶の統計
        if project_id in self.project_memory_data["memory_links"]:
            links = self.project_memory_data["memory_links"][project_id]
            memory_state["linked_memories_count"] = (
                len(links.get("collaboration_memories", [])) +
                len(links.get("personality_memories", [])) +
                len(links.get("integration_patterns", []))
            )
            memory_state["last_memory_update"] = links.get("last_updated")
        
        return memory_state
    
    def _capture_conversation_context(self) -> Dict[str, Any]:
        """会話コンテキストをキャプチャ"""
        # 基本的な会話状態情報
        return {
            "timestamp": datetime.now().isoformat(),
            "context_type": "project_focused"
        }
    
    def _capture_system_metrics(self) -> Dict[str, Any]:
        """システムメトリクスをキャプチャ"""
        return {
            "memory_systems_active": self._count_active_memory_systems(),
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_active_memory_count(self) -> int:
        """アクティブな記憶数を取得"""
        count = 0
        
        if self.collaboration_memory:
            collab_data = self.collaboration_memory.collaboration_data
            count += len(collab_data.get("success_patterns", []))
            count += len(collab_data.get("work_patterns", []))
        
        if self.personality_memory:
            person_data = self.personality_memory.personality_data
            count += len(person_data.get("personal_experiences", []))
            count += len(person_data.get("learning_experiences", []))
        
        return count
    
    def _count_active_memory_systems(self) -> int:
        """アクティブな記憶システム数をカウント"""
        count = 0
        if self.collaboration_memory:
            count += 1
        if self.personality_memory:
            count += 1
        if self.memory_integration:
            count += 1
        if self.project_system:
            count += 1
        return count
    
    def _cleanup_old_data(self):
        """古いデータのクリーンアップ"""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.config["max_context_memory_days"])
            cutoff_str = cutoff_date.isoformat()
            
            # 古い文脈スナップショットを削除
            for project_id in list(self.project_memory_data["context_snapshots"].keys()):
                snapshots = self.project_memory_data["context_snapshots"][project_id]
                self.project_memory_data["context_snapshots"][project_id] = [
                    s for s in snapshots if s.get("timestamp", "") > cutoff_str
                ]
                
                # 空になったプロジェクトエントリを削除
                if not self.project_memory_data["context_snapshots"][project_id]:
                    del self.project_memory_data["context_snapshots"][project_id]
            
        except Exception as e:
            print(f"⚠️ データクリーンアップエラー: {e}")
    
    # 追加のヘルパーメソッド（後で実装予定）
    def _build_collaboration_context(self, memory_links: List[Dict], start_date: datetime, end_date: datetime) -> List[Dict]:
        """協働記憶コンテキスト構築"""
        return []  # 簡易実装
    
    def _build_personality_context(self, memory_links: List[Dict], start_date: datetime, end_date: datetime) -> List[Dict]:
        """個人記憶コンテキスト構築"""
        return []  # 簡易実装
    
    def _filter_decisions_by_date(self, decisions: List[Dict], start_date: datetime, end_date: datetime) -> List[Dict]:
        """日付範囲で意思決定をフィルタ"""
        return []  # 簡易実装
    
    def _build_project_timeline(self, project_id: str, start_date: datetime, end_date: datetime) -> List[Dict]:
        """プロジェクトタイムライン構築"""
        return []  # 簡易実装
    
    def _extract_decision_patterns(self, decisions: List[Dict], pattern_type: str) -> List[Dict]:
        """意思決定パターン抽出"""
        return []  # 簡易実装
    
    def _analyze_decision_timing(self, decisions: List[Dict]) -> Dict[str, Any]:
        """意思決定タイミング分析"""
        return {}  # 簡易実装
    
    def _generate_decision_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """意思決定推薦生成"""
        return []  # 簡易実装
    
    def _generate_pattern_summary(self, analysis: Dict[str, Any]) -> str:
        """パターンサマリー生成"""
        return "パターン分析結果要約"  # 簡易実装


# 使用例・テスト用
if __name__ == "__main__":
    print("=" * 50)
    print("🔗 長期プロジェクト記憶システムテスト")
    print("=" * 50)
    
    try:
        # テストモードで初期化
        ltpm = LongTermProjectMemory(memory_mode="test")
        
        # 基本機能テスト
        print("✅ 長期プロジェクト記憶システム初期化完了")
        
        # テスト用意思決定記録
        test_decision = {
            "type": "feature_decision",
            "description": "新機能の実装方針決定",
            "options": ["方法A", "方法B", "方法C"],
            "chosen": "方法B",
            "reasoning": "実装コストと効果のバランスが最適",
            "confidence": 0.8,
            "risk": 0.3
        }
        
        # 意思決定記録テスト
        result = ltpm.record_project_decision("test_proj_001", test_decision)
        print(f"📝 意思決定記録テスト: {'✅' if result else '❌'}")
        
        # 文脈スナップショットテスト
        result = ltpm.capture_context_snapshot("test_proj_001", "manual")
        print(f"📸 文脈スナップショットテスト: {'✅' if result else '❌'}")
        
        print("\n🎉 長期プロジェクト記憶システムテスト完了")
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
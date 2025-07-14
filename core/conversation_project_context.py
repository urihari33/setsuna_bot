#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
会話プロジェクト文脈システム
長期プロジェクト記憶と現在の会話を統合し、
プロジェクト中心の会話コンテキストを提供する
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

class ConversationProjectContext:
    """会話プロジェクト文脈管理システム"""
    
    def __init__(self, long_term_memory=None, memory_integration=None, memory_mode="normal"):
        """
        会話プロジェクト文脈システム初期化
        
        Args:
            long_term_memory: LongTermProjectMemoryインスタンス
            memory_integration: MemoryIntegrationSystemインスタンス  
            memory_mode: "normal" または "test"
        """
        self.long_term_memory = long_term_memory
        self.memory_integration = memory_integration
        self.memory_mode = memory_mode
        
        # 環境に応じてパスを決定
        if os.path.exists("/mnt/d/setsuna_bot"):
            base_path = Path("/mnt/d/setsuna_bot")
        else:
            base_path = Path("D:/setsuna_bot")
        
        # データファイルパス設定
        if memory_mode == "test":
            self.context_file = base_path / "temp" / f"test_conversation_context_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            os.makedirs(self.context_file.parent, exist_ok=True)
        else:
            self.context_file = base_path / "data" / "conversation_project_context.json"
            os.makedirs(self.context_file.parent, exist_ok=True)
        
        # 会話プロジェクト文脈データ構造
        self.context_data = {
            "current_project_context": None,      # 現在のプロジェクト文脈
            "active_project_threads": {},         # アクティブプロジェクトスレッド
            "conversation_project_links": [],     # 会話-プロジェクトリンク
            "context_evolution": [],              # 文脈進化履歴
            "project_discussion_patterns": {},    # プロジェクト議論パターン
            "memory_activation_history": [],      # 記憶活性化履歴
            "created_at": datetime.now().isoformat(),
            "version": "1.0"
        }
        
        # 設定パラメータ
        self.config = {
            "context_retention_hours": 48,         # 文脈保持時間（時間）
            "max_active_threads": 5,               # 最大アクティブスレッド数
            "memory_activation_threshold": 0.3,    # 記憶活性化閾値
            "project_relevance_threshold": 0.4,    # プロジェクト関連性閾値
            "auto_context_update": True             # 自動文脈更新
        }
        
        # データ読み込み
        self._load_context_data()
        
        print(f"💬 会話プロジェクト文脈システム初期化完了 ({memory_mode}モード)")
    
    def _load_context_data(self):
        """会話プロジェクト文脈データを読み込み"""
        if self.context_file.exists() and self.memory_mode == "normal":
            try:
                with open(self.context_file, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                    self.context_data.update(loaded_data)
                
                threads_count = len(self.context_data.get("active_project_threads", {}))
                links_count = len(self.context_data.get("conversation_project_links", []))
                print(f"✅ 会話プロジェクト文脈読み込み: スレッド{threads_count}件, リンク{links_count}件")
                
            except Exception as e:
                print(f"⚠️ 会話プロジェクト文脈読み込みエラー: {e}")
        else:
            print("🆕 新規会話プロジェクト文脈データベース作成")
    
    def save_context_data(self):
        """会話プロジェクト文脈データを保存"""
        if self.memory_mode == "test":
            return
        
        try:
            # 古いデータのクリーンアップ
            self._cleanup_old_context()
            
            with open(self.context_file, 'w', encoding='utf-8') as f:
                json.dump(self.context_data, f, ensure_ascii=False, indent=2)
            print("💾 会話プロジェクト文脈データ保存完了")
        except Exception as e:
            print(f"❌ 会話プロジェクト文脈データ保存エラー: {e}")
    
    def analyze_project_relevance(self, user_input: str, setsuna_response: str = "") -> Dict[str, Any]:
        """
        会話内容のプロジェクト関連性を分析
        
        Args:
            user_input: ユーザー入力
            setsuna_response: せつなの応答
            
        Returns:
            Dict[str, Any]: プロジェクト関連性分析結果
        """
        try:
            print("🔍 プロジェクト関連性分析開始...")
            
            # プロジェクトキーワード検出
            project_keywords = self._extract_project_keywords_from_text(user_input + " " + setsuna_response)
            
            # アクティブプロジェクトとの関連性チェック
            active_project_matches = self._match_active_projects(project_keywords, user_input)
            
            # 記憶との関連性チェック
            memory_activations = self._analyze_memory_activations(project_keywords, user_input)
            
            # 新しいプロジェクト示唆の検出
            new_project_signals = self._detect_new_project_signals(user_input, setsuna_response)
            
            analysis_result = {
                "project_keywords": project_keywords,
                "active_project_matches": active_project_matches,
                "memory_activations": memory_activations,
                "new_project_signals": new_project_signals,
                "overall_relevance": self._calculate_overall_relevance(
                    active_project_matches, memory_activations, new_project_signals
                ),
                "recommended_actions": self._generate_context_recommendations(
                    active_project_matches, memory_activations, new_project_signals
                ),
                "analyzed_at": datetime.now().isoformat()
            }
            
            print(f"✅ プロジェクト関連性分析完了: 関連度 {analysis_result['overall_relevance']:.2f}")
            return analysis_result
            
        except Exception as e:
            print(f"❌ プロジェクト関連性分析エラー: {e}")
            return {}
    
    def update_conversation_context(self, user_input: str, setsuna_response: str, 
                                  project_analysis: Dict[str, Any] = None) -> bool:
        """
        会話文脈を更新
        
        Args:
            user_input: ユーザー入力
            setsuna_response: せつなの応答
            project_analysis: プロジェクト関連性分析結果
            
        Returns:
            bool: 更新成功フラグ
        """
        try:
            # プロジェクト分析が未実施の場合は実行
            if not project_analysis:
                project_analysis = self.analyze_project_relevance(user_input, setsuna_response)
            
            # 会話-プロジェクトリンクを記録
            conversation_link = {
                "id": f"conv_link_{len(self.context_data['conversation_project_links']) + 1:03d}",
                "timestamp": datetime.now().isoformat(),
                "user_input": user_input[:200],  # 最初の200文字
                "setsuna_response": setsuna_response[:200],
                "project_relevance": project_analysis.get("overall_relevance", 0.0),
                "activated_memories": project_analysis.get("memory_activations", []),
                "related_projects": [match["project_id"] for match in project_analysis.get("active_project_matches", [])],
                "new_project_signals": project_analysis.get("new_project_signals", {})
            }
            
            self.context_data["conversation_project_links"].append(conversation_link)
            
            # アクティブプロジェクトスレッドを更新
            self._update_active_threads(project_analysis)
            
            # 現在のプロジェクト文脈を更新
            self._update_current_project_context(project_analysis)
            
            # 記憶活性化履歴を記録
            self._record_memory_activations(project_analysis.get("memory_activations", []))
            
            print(f"📝 会話文脈更新完了: プロジェクト関連度 {conversation_link['project_relevance']:.2f}")
            return True
            
        except Exception as e:
            print(f"❌ 会話文脈更新エラー: {e}")
            return False
    
    def get_current_project_context(self, include_history: bool = True) -> str:
        """
        現在のプロジェクト文脈を取得
        
        Args:
            include_history: 履歴を含むかどうか
            
        Returns:
            str: プロジェクト文脈文字列
        """
        try:
            context_parts = []
            
            # 現在のプロジェクト文脈
            current_context = self.context_data.get("current_project_context")
            if current_context:
                context_parts.append("【現在のプロジェクト文脈】")
                context_parts.append(f"- 主要プロジェクト: {current_context.get('primary_project', '未設定')}")
                context_parts.append(f"- 文脈の強度: {current_context.get('context_strength', 0):.2f}")
                context_parts.append(f"- 関連記憶数: {len(current_context.get('active_memories', []))}")
            
            # アクティブプロジェクトスレッド
            active_threads = self.context_data.get("active_project_threads", {})
            if active_threads:
                context_parts.append("\n【アクティブプロジェクト】")
                for project_id, thread_info in list(active_threads.items())[:3]:  # 上位3件
                    context_parts.append(f"- {thread_info.get('project_title', 'Unknown')}: {thread_info.get('thread_strength', 0):.2f}")
            
            # 最近活性化された記憶
            if include_history:
                recent_activations = self._get_recent_memory_activations(hours_back=6)
                if recent_activations:
                    context_parts.append("\n【最近活性化された記憶】")
                    for activation in recent_activations[:3]:
                        context_parts.append(f"- {activation.get('description', 'Unknown')}")
            
            return "\n".join(context_parts) if context_parts else ""
            
        except Exception as e:
            print(f"❌ プロジェクト文脈取得エラー: {e}")
            return ""
    
    def suggest_project_actions(self, current_input: str = "") -> List[Dict[str, str]]:
        """
        プロジェクト関連のアクション提案
        
        Args:
            current_input: 現在のユーザー入力
            
        Returns:
            List[Dict[str, str]]: アクション提案リスト
        """
        suggestions = []
        
        try:
            # アクティブプロジェクトからの提案
            active_threads = self.context_data.get("active_project_threads", {})
            
            for project_id, thread_info in active_threads.items():
                if thread_info.get("thread_strength", 0) > 0.6:
                    suggestions.append({
                        "type": "project_progress",
                        "action": f"{thread_info.get('project_title', 'プロジェクト')}の進捗確認",
                        "description": f"現在の{thread_info.get('project_title', 'プロジェクト')}について話し合う",
                        "priority": "high"
                    })
            
            # 新しいプロジェクト開始の提案
            new_signals = self._analyze_new_project_potential(current_input)
            if new_signals.get("potential_score", 0) > 0.5:
                suggestions.append({
                    "type": "new_project",
                    "action": "新しいプロジェクト開始",
                    "description": new_signals.get("suggestion", "新しいプロジェクトを開始してみましょう"),
                    "priority": "medium"
                })
            
            # 記憶活用の提案
            memory_suggestions = self._suggest_memory_utilization()
            suggestions.extend(memory_suggestions)
            
            return suggestions[:5]  # 最大5件
            
        except Exception as e:
            print(f"❌ プロジェクトアクション提案エラー: {e}")
            return []
    
    # ========== 内部ヘルパーメソッド ==========
    
    def _extract_project_keywords_from_text(self, text: str) -> List[str]:
        """テキストからプロジェクトキーワードを抽出"""
        project_keywords = [
            "プロジェクト", "企画", "作業", "制作", "開発", "計画", "目標", "課題",
            "動画", "音楽", "歌", "楽曲", "創作", "アイデア", "ネタ", "企画書",
            "進捗", "完成", "公開", "投稿", "アップロード", "編集", "録音", "撮影"
        ]
        
        detected_keywords = []
        text_lower = text.lower()
        
        for keyword in project_keywords:
            if keyword in text:
                detected_keywords.append(keyword)
        
        # 英単語のプロジェクト関連キーワード
        english_keywords = [
            "project", "plan", "goal", "task", "create", "make", "build", "develop"
        ]
        
        for keyword in english_keywords:
            if keyword in text_lower:
                detected_keywords.append(keyword)
        
        return list(set(detected_keywords))
    
    def _match_active_projects(self, keywords: List[str], user_input: str) -> List[Dict[str, Any]]:
        """アクティブプロジェクトとのマッチングを実行"""
        matches = []
        
        if not self.long_term_memory:
            return matches
        
        # アクティブプロジェクトを取得
        try:
            active_projects = self.long_term_memory.project_system.get_active_projects()
            
            for project in active_projects:
                # プロジェクトとの関連度計算
                relevance_score = self._calculate_project_relevance(project, keywords, user_input)
                
                if relevance_score >= self.config["project_relevance_threshold"]:
                    matches.append({
                        "project_id": project.get("id"),
                        "project_title": project.get("title"),
                        "relevance_score": relevance_score,
                        "matching_keywords": self._find_matching_keywords(project, keywords)
                    })
            
            # 関連度順でソート
            matches.sort(key=lambda x: x["relevance_score"], reverse=True)
            
        except Exception as e:
            print(f"⚠️ アクティブプロジェクトマッチングエラー: {e}")
        
        return matches
    
    def _analyze_memory_activations(self, keywords: List[str], user_input: str) -> List[Dict[str, Any]]:
        """記憶活性化を分析"""
        activations = []
        
        if not self.memory_integration:
            return activations
        
        try:
            # 統合記憶から関連記憶を検索
            relevant_context = self.memory_integration._generate_relevant_context(user_input)
            
            if relevant_context:
                activations.append({
                    "type": "integration_memory",
                    "description": "統合記憶から関連パターンが活性化",
                    "strength": 0.7,
                    "details": relevant_context[:100]  # 最初の100文字
                })
            
        except Exception as e:
            print(f"⚠️ 記憶活性化分析エラー: {e}")
        
        return activations
    
    def _detect_new_project_signals(self, user_input: str, setsuna_response: str) -> Dict[str, Any]:
        """新しいプロジェクトの兆候を検出"""
        signals = {
            "has_signal": False,
            "signal_strength": 0.0,
            "signal_types": [],
            "suggested_project_type": ""
        }
        
        # 新プロジェクト示唆キーワード
        new_project_indicators = [
            "作りたい", "やってみたい", "始めよう", "企画", "新しい", "アイデア",
            "思いついた", "提案", "計画", "目標"
        ]
        
        combined_text = user_input + " " + setsuna_response
        
        for indicator in new_project_indicators:
            if indicator in combined_text:
                signals["has_signal"] = True
                signals["signal_strength"] += 0.2
                signals["signal_types"].append(indicator)
        
        # プロジェクトタイプの推定
        if "動画" in combined_text or "映像" in combined_text:
            signals["suggested_project_type"] = "動画"
        elif "音楽" in combined_text or "歌" in combined_text or "楽曲" in combined_text:
            signals["suggested_project_type"] = "音楽"
        elif "プログラム" in combined_text or "開発" in combined_text:
            signals["suggested_project_type"] = "開発"
        else:
            signals["suggested_project_type"] = "その他"
        
        signals["signal_strength"] = min(signals["signal_strength"], 1.0)
        
        return signals
    
    def _calculate_project_relevance(self, project: Dict[str, Any], keywords: List[str], user_input: str) -> float:
        """プロジェクトとの関連度を計算"""
        relevance_score = 0.0
        
        # プロジェクト情報からテキストを抽出
        project_text = f"{project.get('title', '')} {project.get('description', '')} {project.get('type', '')}"
        
        # キーワードマッチング
        matching_keywords = self._find_matching_keywords(project, keywords)
        if keywords:
            keyword_score = len(matching_keywords) / len(keywords)
            relevance_score += keyword_score * 0.6
        
        # テキスト類似度（簡易版）
        common_words = set(user_input.split()) & set(project_text.split())
        if user_input.split():
            text_score = len(common_words) / len(user_input.split())
            relevance_score += text_score * 0.4
        
        return min(relevance_score, 1.0)
    
    def _find_matching_keywords(self, project: Dict[str, Any], keywords: List[str]) -> List[str]:
        """プロジェクトと一致するキーワードを検索"""
        project_text = f"{project.get('title', '')} {project.get('description', '')} {project.get('type', '')}"
        
        matching = []
        for keyword in keywords:
            if keyword in project_text:
                matching.append(keyword)
        
        return matching
    
    def _calculate_overall_relevance(self, project_matches: List[Dict], 
                                   memory_activations: List[Dict], 
                                   new_signals: Dict) -> float:
        """総合関連度を計算"""
        relevance_score = 0.0
        
        # アクティブプロジェクトマッチの寄与
        if project_matches:
            max_project_relevance = max(match["relevance_score"] for match in project_matches)
            relevance_score += max_project_relevance * 0.5
        
        # 記憶活性化の寄与
        if memory_activations:
            avg_memory_strength = sum(act["strength"] for act in memory_activations) / len(memory_activations)
            relevance_score += avg_memory_strength * 0.3
        
        # 新プロジェクト兆候の寄与
        relevance_score += new_signals.get("signal_strength", 0) * 0.2
        
        return min(relevance_score, 1.0)
    
    def _generate_context_recommendations(self, project_matches: List[Dict], 
                                        memory_activations: List[Dict], 
                                        new_signals: Dict) -> List[str]:
        """文脈推薦を生成"""
        recommendations = []
        
        # アクティブプロジェクトに関する推薦
        if project_matches:
            top_match = project_matches[0]
            recommendations.append(
                f"{top_match['project_title']}プロジェクトとの関連性が高いです"
            )
        
        # 記憶活用の推薦
        if memory_activations:
            recommendations.append("過去の経験が参考になりそうです")
        
        # 新プロジェクトの推薦
        if new_signals.get("has_signal") and new_signals.get("signal_strength", 0) > 0.5:
            recommendations.append(
                f"新しい{new_signals.get('suggested_project_type', 'プロジェクト')}の開始を検討してみましょう"
            )
        
        return recommendations
    
    def _update_active_threads(self, project_analysis: Dict[str, Any]):
        """アクティブプロジェクトスレッドを更新"""
        for match in project_analysis.get("active_project_matches", []):
            project_id = match["project_id"]
            
            if project_id not in self.context_data["active_project_threads"]:
                self.context_data["active_project_threads"][project_id] = {
                    "project_title": match["project_title"],
                    "thread_strength": 0.0,
                    "last_mention": datetime.now().isoformat(),
                    "mention_count": 0,
                    "keywords": []
                }
            
            # スレッド強度を更新
            thread = self.context_data["active_project_threads"][project_id]
            thread["thread_strength"] = max(thread["thread_strength"], match["relevance_score"])
            thread["last_mention"] = datetime.now().isoformat()
            thread["mention_count"] += 1
            thread["keywords"].extend(match.get("matching_keywords", []))
            thread["keywords"] = list(set(thread["keywords"]))  # 重複除去
        
        # 古いスレッドの強度を減衰
        self._decay_thread_strengths()
    
    def _update_current_project_context(self, project_analysis: Dict[str, Any]):
        """現在のプロジェクト文脈を更新"""
        overall_relevance = project_analysis.get("overall_relevance", 0)
        
        if overall_relevance > 0.5:
            # 強い関連性がある場合、文脈を更新
            project_matches = project_analysis.get("active_project_matches", [])
            
            if project_matches:
                primary_project = project_matches[0]
                
                self.context_data["current_project_context"] = {
                    "primary_project": primary_project["project_title"],
                    "primary_project_id": primary_project["project_id"],
                    "context_strength": overall_relevance,
                    "active_memories": [act["type"] for act in project_analysis.get("memory_activations", [])],
                    "last_updated": datetime.now().isoformat()
                }
    
    def _record_memory_activations(self, activations: List[Dict[str, Any]]):
        """記憶活性化履歴を記録"""
        for activation in activations:
            activation_record = {
                "timestamp": datetime.now().isoformat(),
                "type": activation.get("type"),
                "description": activation.get("description"),
                "strength": activation.get("strength")
            }
            
            self.context_data["memory_activation_history"].append(activation_record)
        
        # 古い履歴のクリーンアップ（最新50件まで保持）
        if len(self.context_data["memory_activation_history"]) > 50:
            self.context_data["memory_activation_history"] = self.context_data["memory_activation_history"][-50:]
    
    def _decay_thread_strengths(self):
        """スレッド強度の時間減衰"""
        current_time = datetime.now()
        
        for project_id, thread in list(self.context_data["active_project_threads"].items()):
            last_mention = datetime.fromisoformat(thread["last_mention"])
            hours_since_mention = (current_time - last_mention).total_seconds() / 3600
            
            # 1時間ごとに10%減衰
            decay_factor = max(0.1, 1.0 - (hours_since_mention * 0.1))
            thread["thread_strength"] *= decay_factor
            
            # 強度が低すぎる場合は削除
            if thread["thread_strength"] < 0.1:
                del self.context_data["active_project_threads"][project_id]
    
    def _get_recent_memory_activations(self, hours_back: int = 6) -> List[Dict[str, Any]]:
        """最近の記憶活性化を取得"""
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        recent_activations = []
        for activation in self.context_data["memory_activation_history"]:
            activation_time = datetime.fromisoformat(activation["timestamp"])
            if activation_time >= cutoff_time:
                recent_activations.append(activation)
        
        return sorted(recent_activations, key=lambda x: x["timestamp"], reverse=True)
    
    def _analyze_new_project_potential(self, current_input: str) -> Dict[str, Any]:
        """新プロジェクト開始の可能性を分析"""
        potential_signals = {
            "potential_score": 0.0,
            "suggestion": "",
            "confidence": 0.0
        }
        
        # 新プロジェクト開始の兆候を検索
        creation_keywords = ["作りたい", "始めたい", "やってみたい", "企画したい"]
        
        for keyword in creation_keywords:
            if keyword in current_input:
                potential_signals["potential_score"] += 0.3
        
        if potential_signals["potential_score"] > 0:
            potential_signals["suggestion"] = "新しいプロジェクトを始めてみませんか？"
            potential_signals["confidence"] = min(potential_signals["potential_score"], 1.0)
        
        return potential_signals
    
    def _suggest_memory_utilization(self) -> List[Dict[str, str]]:
        """記憶活用の提案"""
        suggestions = []
        
        # 最近活性化されていない強い記憶を探す
        if self.memory_integration:
            try:
                strong_relationships = [
                    rel for rel in self.memory_integration.integration_data["memory_relationships"]
                    if rel["strength"] >= 0.7 and not rel.get("last_referenced")
                ]
                
                if strong_relationships:
                    suggestions.append({
                        "type": "memory_utilization",
                        "action": "過去の成功パターン活用",
                        "description": "活用されていない過去の成功体験があります",
                        "priority": "medium"
                    })
                    
            except Exception as e:
                print(f"⚠️ 記憶活用提案エラー: {e}")
        
        return suggestions
    
    def _cleanup_old_context(self):
        """古い文脈データのクリーンアップ"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=self.config["context_retention_hours"])
            cutoff_str = cutoff_time.isoformat()
            
            # 古い会話リンクを削除
            old_links = self.context_data["conversation_project_links"]
            self.context_data["conversation_project_links"] = [
                link for link in old_links 
                if link.get("timestamp", "") > cutoff_str
            ]
            
            # 古い記憶活性化履歴を削除
            old_activations = self.context_data["memory_activation_history"]
            self.context_data["memory_activation_history"] = [
                act for act in old_activations 
                if act.get("timestamp", "") > cutoff_str
            ]
            
        except Exception as e:
            print(f"⚠️ 文脈データクリーンアップエラー: {e}")


# 使用例・テスト用
if __name__ == "__main__":
    print("=" * 50)
    print("💬 会話プロジェクト文脈システムテスト")
    print("=" * 50)
    
    try:
        # テストモードで初期化
        cpc = ConversationProjectContext(memory_mode="test")
        
        # プロジェクト関連性分析テスト
        test_input = "動画の企画について相談したいんだけど"
        test_response = "どんな動画を作りたいか教えてください"
        
        analysis = cpc.analyze_project_relevance(test_input, test_response)
        print(f"📊 関連性分析: {analysis.get('overall_relevance', 0):.2f}")
        
        # 会話文脈更新テスト
        update_result = cpc.update_conversation_context(test_input, test_response, analysis)
        print(f"📝 文脈更新: {'✅' if update_result else '❌'}")
        
        # 現在の文脈取得テスト
        current_context = cpc.get_current_project_context()
        print(f"📋 現在の文脈: {len(current_context)}文字")
        
        # アクション提案テスト
        suggestions = cpc.suggest_project_actions(test_input)
        print(f"💡 アクション提案: {len(suggestions)}件")
        
        print("\n🎉 会話プロジェクト文脈システムテスト完了")
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
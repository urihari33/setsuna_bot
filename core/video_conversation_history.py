#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
動画会話履歴管理システム - Phase 2-B-1
ユーザーとの動画関連会話を記録・学習する
"""

import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import re

class VideoConversationHistory:
    """動画関連会話履歴の管理クラス"""
    
    def __init__(self):
        """初期化"""
        # Windows環境とWSL2環境両方に対応
        if os.name == 'nt':  # Windows
            self.history_file = Path("D:/setsuna_bot/data/video_conversation_history.json")
        else:  # Linux/WSL2
            self.history_file = Path("/mnt/d/setsuna_bot/data/video_conversation_history.json")
        
        self.video_conversations = {}  # video_id: conversation_data
        self.session_videos = []  # 今回のセッションで話した動画
        
        # データ構造
        self.conversation_structure = {
            # "video_id": {
            #     "video_title": "楽曲名",
            #     "conversation_count": 回数,
            #     "first_talked": "初回日時",
            #     "last_talked": "最終日時", 
            #     "user_reactions": ["positive", "neutral", "negative"],
            #     "conversation_contexts": [{"date": "", "input": "", "reaction": ""}],
            #     "familiarity_score": 0.0-1.0
            # }
        }
        
        self._ensure_data_dir()
        self._load_history()
        
        print("[動画履歴] ✅ 動画会話履歴システム初期化完了")
    
    def _ensure_data_dir(self):
        """データディレクトリの確保"""
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
    
    def _load_history(self):
        """履歴ファイルから読み込み"""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.video_conversations = data.get('video_conversations', {})
                
                video_count = len(self.video_conversations)
                print(f"[動画履歴] 📊 過去の動画会話履歴: {video_count}件をロード")
            else:
                self.video_conversations = {}
                print("[動画履歴] 📝 新規履歴ファイルを作成")
                
        except Exception as e:
            print(f"[動画履歴] ⚠️ 履歴読み込み失敗: {e}")
            self.video_conversations = {}
    
    def _save_history(self):
        """履歴ファイルに保存"""
        try:
            data = {
                'video_conversations': self.video_conversations,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"[動画履歴] ❌ 履歴保存失敗: {e}")
    
    def _analyze_user_reaction(self, user_input: str) -> str:
        """ユーザー入力から反応を分析"""
        user_lower = user_input.lower()
        
        # ポジティブ反応パターン
        positive_patterns = [
            r'(いい|良い|好き|気に入|素晴らしい|最高|すごい)',
            r'(もう一度|また|繰り返|リピート)',
            r'(ありがとう|サンキュー)',
            r'(感動|泣け|心に響|素敵)'
        ]
        
        # ネガティブ反応パターン
        negative_patterns = [
            r'(嫌い|ダメ|良くない|微妙|イマイチ)',
            r'(飽きた|もういい|違う)',
            r'(つまらない|面白くない)'
        ]
        
        # 質問・継続パターン
        neutral_patterns = [
            r'(どう|どんな|教えて|知りたい)',
            r'(について|って|は|の)',
            r'(\?|？|かな|かしら)'
        ]
        
        for pattern in positive_patterns:
            if re.search(pattern, user_input):
                return "positive"
        
        for pattern in negative_patterns:
            if re.search(pattern, user_input):
                return "negative"
        
        for pattern in neutral_patterns:
            if re.search(pattern, user_input):
                return "neutral"
        
        return "neutral"  # デフォルト
    
    def record_conversation(self, video_id: str, video_title: str, user_input: str, user_reaction: Optional[str] = None) -> bool:
        """
        動画関連会話を記録
        
        Args:
            video_id: YouTube動画ID
            video_title: 動画タイトル（簡略化済み）
            user_input: ユーザーの入力
            user_reaction: ユーザー反応（auto分析 or 手動指定）
            
        Returns:
            記録成功したかどうか
        """
        try:
            current_time = datetime.now().isoformat()
            
            # 反応分析
            if user_reaction is None:
                user_reaction = self._analyze_user_reaction(user_input)
            
            # 新規動画の場合
            if video_id not in self.video_conversations:
                self.video_conversations[video_id] = {
                    "video_title": video_title,
                    "conversation_count": 0,
                    "first_talked": current_time,
                    "last_talked": current_time,
                    "user_reactions": [],
                    "conversation_contexts": [],
                    "familiarity_score": 0.0
                }
            
            # 会話記録の更新
            video_data = self.video_conversations[video_id]
            video_data["conversation_count"] += 1
            video_data["last_talked"] = current_time
            video_data["user_reactions"].append(user_reaction)
            
            # 会話コンテキストの追加（最新10件まで保持）
            context_entry = {
                "date": current_time,
                "input": user_input[:100],  # 長すぎる場合は切り詰め
                "reaction": user_reaction
            }
            video_data["conversation_contexts"].append(context_entry)
            
            # 古いコンテキストの削除（10件超過時）
            if len(video_data["conversation_contexts"]) > 10:
                video_data["conversation_contexts"] = video_data["conversation_contexts"][-10:]
            
            # 最新5件の反応も保持
            if len(video_data["user_reactions"]) > 5:
                video_data["user_reactions"] = video_data["user_reactions"][-5:]
            
            # 親しみやすさスコアの計算
            video_data["familiarity_score"] = self._calculate_familiarity_score(video_data)
            
            # セッション記録
            if video_id not in self.session_videos:
                self.session_videos.append(video_id)
            
            # 自動保存
            self._save_history()
            
            print(f"[動画履歴] 📝 会話記録: {video_title} (反応: {user_reaction}, 累計: {video_data['conversation_count']}回)")
            return True
            
        except Exception as e:
            print(f"[動画履歴] ❌ 会話記録失敗: {e}")
            return False
    
    def _calculate_familiarity_score(self, video_data: Dict[str, Any]) -> float:
        """
        親しみやすさスコアを計算
        
        Args:
            video_data: 動画データ
            
        Returns:
            0.0-1.0のスコア
        """
        try:
            # 基本スコア（会話回数ベース）
            conversation_count = video_data.get("conversation_count", 0)
            base_score = min(conversation_count / 10.0, 0.6)  # 最大0.6
            
            # 反応ボーナス
            reactions = video_data.get("user_reactions", [])
            if reactions:
                positive_count = reactions.count("positive")
                negative_count = reactions.count("negative")
                
                if len(reactions) > 0:
                    reaction_ratio = positive_count / len(reactions)
                    reaction_bonus = reaction_ratio * 0.3  # 最大0.3
                    negative_penalty = (negative_count / len(reactions)) * 0.2  # 最大-0.2
                else:
                    reaction_bonus = 0.0
                    negative_penalty = 0.0
            else:
                reaction_bonus = 0.0
                negative_penalty = 0.0
            
            # 最近の会話ボーナス
            last_talked = video_data.get("last_talked")
            if last_talked:
                last_date = datetime.fromisoformat(last_talked)
                days_ago = (datetime.now() - last_date).days
                
                if days_ago <= 7:  # 1週間以内
                    recency_bonus = 0.1
                elif days_ago <= 30:  # 1ヶ月以内
                    recency_bonus = 0.05
                else:
                    recency_bonus = 0.0
            else:
                recency_bonus = 0.0
            
            # 総合スコア計算
            total_score = base_score + reaction_bonus - negative_penalty + recency_bonus
            return max(0.0, min(1.0, total_score))  # 0.0-1.0の範囲に制限
            
        except Exception as e:
            print(f"[動画履歴] ⚠️ スコア計算エラー: {e}")
            return 0.0
    
    def get_conversation_context(self, video_id: str) -> Optional[Dict[str, Any]]:
        """
        特定動画の会話コンテキストを取得
        
        Args:
            video_id: YouTube動画ID
            
        Returns:
            会話コンテキスト情報
        """
        if video_id not in self.video_conversations:
            return None
        
        video_data = self.video_conversations[video_id]
        
        # 過去の会話から自然な表現を生成
        conversation_count = video_data.get("conversation_count", 0)
        familiarity_score = video_data.get("familiarity_score", 0.0)
        last_talked = video_data.get("last_talked")
        recent_reactions = video_data.get("user_reactions", [])[-3:]  # 最新3件
        
        # 親しみやすさレベルの判定
        if familiarity_score >= 0.7:
            familiarity_level = "very_familiar"  # とても親しみ
        elif familiarity_score >= 0.4:
            familiarity_level = "familiar"  # 親しみ
        elif familiarity_score >= 0.2:
            familiarity_level = "somewhat_familiar"  # やや親しみ
        else:
            familiarity_level = "new"  # 新規
        
        # 最後に話した時期の計算
        if last_talked:
            last_date = datetime.fromisoformat(last_talked)
            days_ago = (datetime.now() - last_date).days
            
            if days_ago == 0:
                recency = "today"
            elif days_ago <= 3:
                recency = "recent"
            elif days_ago <= 14:
                recency = "somewhat_recent"
            else:
                recency = "long_ago"
        else:
            recency = "never"
        
        return {
            "video_id": video_id,
            "video_title": video_data.get("video_title", ""),
            "conversation_count": conversation_count,
            "familiarity_level": familiarity_level,
            "familiarity_score": familiarity_score,
            "recency": recency,
            "days_ago": (datetime.now() - datetime.fromisoformat(last_talked)).days if last_talked else None,
            "recent_reactions": recent_reactions,
            "is_session_topic": video_id in self.session_videos
        }
    
    def generate_conversation_hints(self, video_id: str) -> List[str]:
        """
        会話のヒント文を生成
        
        Args:
            video_id: YouTube動画ID
            
        Returns:
            会話ヒントのリスト
        """
        context = self.get_conversation_context(video_id)
        if not context:
            return []
        
        hints = []
        familiarity_level = context["familiarity_level"]
        recency = context["recency"]
        conversation_count = context["conversation_count"]
        recent_reactions = context["recent_reactions"]
        
        # 親しみやすさベースのヒント
        if familiarity_level == "very_familiar":
            hints.append("おなじみの楽曲として親しみを込めて話す")
            hints.append("「いつもの」「例の」等の表現を使用")
        elif familiarity_level == "familiar":
            hints.append("前にも話した楽曲として言及")
            hints.append("「また」「やっぱり」等の継続表現を使用")
        elif familiarity_level == "somewhat_familiar":
            hints.append("聞いたことがある楽曲として話す")
        
        # 時期ベースのヒント
        if recency == "today":
            hints.append("今日も話題に上った楽曲として言及")
        elif recency == "recent":
            hints.append("最近話した楽曲として言及")
        elif recency == "somewhat_recent":
            hints.append("少し前に話した楽曲として言及")
        
        # 反応ベースのヒント
        if recent_reactions:
            positive_count = recent_reactions.count("positive")
            if positive_count >= 2:
                hints.append("ユーザーがお気に入りの楽曲として扱う")
            elif "negative" in recent_reactions:
                hints.append("ユーザーがあまり好まない可能性を考慮")
        
        # 会話回数ベースのヒント
        if conversation_count >= 5:
            hints.append("よく話題になる楽曲として特別感を出す")
        
        return hints
    
    def get_session_summary(self) -> Dict[str, Any]:
        """今回セッションの動画会話サマリーを取得"""
        if not self.session_videos:
            return {"session_video_count": 0, "videos": []}
        
        session_data = []
        for video_id in self.session_videos:
            context = self.get_conversation_context(video_id)
            if context:
                session_data.append(context)
        
        return {
            "session_video_count": len(self.session_videos),
            "videos": session_data
        }
    
    def clear_session(self):
        """セッション記録をクリア"""
        self.session_videos = []
        print("[動画履歴] 🔄 セッション記録をクリア")
    
    def get_familiar_videos(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        親しみやすさスコア順で動画を取得
        
        Args:
            limit: 取得件数
            
        Returns:
            親しみやすさ順の動画リスト
        """
        if not self.video_conversations:
            return []
        
        # スコア順でソート
        sorted_videos = sorted(
            self.video_conversations.items(),
            key=lambda x: x[1].get("familiarity_score", 0.0),
            reverse=True
        )
        
        result = []
        for video_id, video_data in sorted_videos[:limit]:
            context = self.get_conversation_context(video_id)
            if context:
                result.append(context)
        
        return result
    
    def delete_video_history(self, video_id: str) -> bool:
        """特定動画の履歴を削除"""
        if video_id in self.video_conversations:
            del self.video_conversations[video_id]
            self._save_history()
            print(f"[動画履歴] 🗑️ 動画履歴削除: {video_id}")
            return True
        return False
    
    def clear_all_history(self):
        """全履歴をクリア"""
        self.video_conversations = {}
        self.session_videos = []
        self._save_history()
        print("[動画履歴] 🗑️ 全動画履歴をクリア")

# 使用例・テスト
if __name__ == "__main__":
    print("=== 動画会話履歴システムテスト ===")
    
    history = VideoConversationHistory()
    
    # テスト会話の記録
    test_conversations = [
        ("Av3xaZkVpJs", "アドベンチャー", "アドベンチャーはどんな曲？"),
        ("Av3xaZkVpJs", "アドベンチャー", "この曲いいね！"),
        ("VIDEO_ID_2", "XOXO", "XOXOって曲知ってる？"),
        ("Av3xaZkVpJs", "アドベンチャー", "またアドベンチャー聞きたい"),
    ]
    
    for video_id, title, user_input in test_conversations:
        history.record_conversation(video_id, title, user_input)
    
    # コンテキスト取得テスト
    context = history.get_conversation_context("Av3xaZkVpJs")
    if context:
        print(f"\n📊 アドベンチャーの会話コンテキスト:")
        print(f"  会話回数: {context['conversation_count']}")
        print(f"  親しみやすさ: {context['familiarity_level']} (スコア: {context['familiarity_score']:.2f})")
        print(f"  最近の反応: {context['recent_reactions']}")
        
        hints = history.generate_conversation_hints("Av3xaZkVpJs")
        print(f"  会話ヒント: {hints}")
    
    # セッションサマリー
    session = history.get_session_summary()
    print(f"\n📝 セッションサマリー: {session['session_video_count']}件の動画")
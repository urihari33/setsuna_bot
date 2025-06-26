#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文脈理解向上システム - Phase 2-B-3
会話の文脈をより深く理解し、暗黙的な言及や継続性を認識する
"""

import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from collections import deque
import os

class ContextUnderstandingSystem:
    """文脈理解と参照解決を行うクラス"""
    
    def __init__(self):
        """初期化"""
        # Windows環境とWSL2環境両方に対応
        if os.name == 'nt':  # Windows
            self.context_file = Path("D:/setsuna_bot/data/conversation_context.json")
        else:  # Linux/WSL2
            self.context_file = Path("/mnt/d/setsuna_bot/data/conversation_context.json")
        
        # 会話コンテキスト管理
        self.conversation_memory = deque(maxlen=10)  # 最近10回の会話を記憶
        self.active_topics = {}  # アクティブな話題（動画ID -> 情報）
        self.emotional_context = {}  # 感情文脈
        self.reference_cache = {}  # 代名詞参照キャッシュ
        
        # 設定
        self.config = {
            "max_conversation_memory": 10,
            "context_timeout_minutes": 30,  # 文脈の有効時間
            "reference_confidence_threshold": 0.7,
            "enable_emotional_analysis": True,
            "enable_pronoun_resolution": True,
            "enable_topic_tracking": True
        }
        
        self._ensure_data_dir()
        self._load_context()
        
        print("[文脈理解] ✅ 文脈理解向上システム初期化完了")
    
    def _ensure_data_dir(self):
        """データディレクトリの確保"""
        self.context_file.parent.mkdir(parents=True, exist_ok=True)
    
    def _load_context(self):
        """文脈データの読み込み"""
        try:
            if self.context_file.exists():
                with open(self.context_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # 会話記憶の復元（最近のもののみ）
                    saved_memory = data.get('conversation_memory', [])
                    recent_memory = [
                        mem for mem in saved_memory 
                        if self._is_recent_conversation(mem.get('timestamp'))
                    ]
                    self.conversation_memory.extend(recent_memory)
                    
                    # アクティブ話題の復元
                    saved_topics = data.get('active_topics', {})
                    self.active_topics = {
                        topic_id: topic_data for topic_id, topic_data in saved_topics.items()
                        if self._is_recent_conversation(topic_data.get('last_mentioned'))
                    }
                    
                    # 感情文脈の復元
                    self.emotional_context = data.get('emotional_context', {})
                    
                    print(f"[文脈理解] 📊 文脈データ復元: 会話{len(self.conversation_memory)}件, 話題{len(self.active_topics)}件")
            else:
                print("[文脈理解] 📝 新規文脈データファイルを作成")
                
        except Exception as e:
            print(f"[文脈理解] ⚠️ 文脈データ読み込み失敗: {e}")
            self._initialize_empty_context()
    
    def _initialize_empty_context(self):
        """空の文脈で初期化"""
        self.conversation_memory.clear()
        self.active_topics = {}
        self.emotional_context = {}
        self.reference_cache = {}
    
    def _save_context(self):
        """文脈データの保存"""
        try:
            data = {
                'conversation_memory': list(self.conversation_memory),
                'active_topics': self.active_topics,
                'emotional_context': self.emotional_context,
                'config': self.config,
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.context_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            print(f"[文脈理解] ❌ 文脈データ保存失敗: {e}")
    
    def _is_recent_conversation(self, timestamp_str: str) -> bool:
        """会話が最近のものかチェック"""
        if not timestamp_str:
            return False
        
        try:
            timestamp = datetime.fromisoformat(timestamp_str)
            now = datetime.now()
            return now - timestamp < timedelta(minutes=self.config["context_timeout_minutes"])
        except:
            return False
    
    def analyze_input_context(self, user_input: str) -> Dict[str, Any]:
        """
        ユーザー入力の文脈を分析
        
        Args:
            user_input: ユーザーの入力
            
        Returns:
            文脈分析結果
        """
        analysis = {
            "input": user_input,
            "timestamp": datetime.now().isoformat(),
            "pronoun_references": [],
            "continuity_indicators": [],
            "emotional_signals": {},
            "topic_relevance": {},
            "requires_resolution": False
        }
        
        # 代名詞・指示語検出
        if self.config["enable_pronoun_resolution"]:
            analysis["pronoun_references"] = self._detect_pronoun_references(user_input)
            analysis["requires_resolution"] = len(analysis["pronoun_references"]) > 0
        
        # 継続性指標の検出
        analysis["continuity_indicators"] = self._detect_continuity_indicators(user_input)
        
        # 感情シグナルの分析
        if self.config["enable_emotional_analysis"]:
            analysis["emotional_signals"] = self._analyze_emotional_signals(user_input)
        
        # 話題関連性の分析
        if self.config["enable_topic_tracking"]:
            analysis["topic_relevance"] = self._analyze_topic_relevance(user_input)
        
        return analysis
    
    def _detect_pronoun_references(self, user_input: str) -> List[Dict[str, Any]]:
        """代名詞・指示語の検出"""
        pronouns = []
        
        # 代名詞パターン
        pronoun_patterns = {
            "demonstrative": {  # 指示語
                "patterns": [r"(あの|その|この)(曲|動画|楽曲|歌|音楽)", r"(それ|あれ|これ)", r"(この|その|あの)"],
                "confidence": 0.9
            },
            "temporal": {  # 時間的指示
                "patterns": [r"(さっき|先ほど|前|今|最近)(の|に|聞いた|見た|話した)", r"(さっき|先ほど|前)", r"(さっきの|前の)"],
                "confidence": 0.8
            },
            "relative": {  # 相対的指示
                "patterns": [r"(同じ|似た|別の|違う)(やつ|もの|曲|動画)", r"(もう一度|また|繰り返し)", r"(似たような|同じような)"],
                "confidence": 0.7
            },
            "implicit": {  # 暗黙的指示
                "patterns": [r"(詳しく|もっと|他に|続き)", r"(どう|なぜ|いつ|どこ)", r"(もっと|さらに)"],
                "confidence": 0.6
            }
        }
        
        for category, info in pronoun_patterns.items():
            for pattern in info["patterns"]:
                matches = re.finditer(pattern, user_input, re.IGNORECASE)
                for match in matches:
                    pronouns.append({
                        "type": category,
                        "text": match.group(),
                        "position": match.span(),
                        "confidence": info["confidence"]
                    })
        
        return pronouns
    
    def _detect_continuity_indicators(self, user_input: str) -> List[Dict[str, Any]]:
        """会話の継続性指標を検出"""
        indicators = []
        
        # 継続性パターン
        continuity_patterns = {
            "agreement": {  # 同意・肯定
                "patterns": [r"(そうだね|そう|うん|はい|いいね|好き|気に入)", r"(ありがとう|サンキュー)"],
                "strength": "strong"
            },
            "disagreement": {  # 否定・反対
                "patterns": [r"(違う|ちがう|そうじゃない|嫌|微妙|イマイチ)", r"(でも|けど|しかし)"],
                "strength": "strong"
            },
            "continuation": {  # 継続
                "patterns": [r"(それで|そして|また|次に|今度)", r"(もっと|さらに|他に|別の)"],
                "strength": "medium"
            },
            "clarification": {  # 明確化
                "patterns": [r"(つまり|要するに|ということは)", r"(どういう|どんな|なぜ|なに)"],
                "strength": "medium"
            },
            "transition": {  # 話題転換
                "patterns": [r"(ところで|そういえば|話は変わって)", r"(別の話|新しい|今度は)"],
                "strength": "weak"
            }
        }
        
        for category, info in continuity_patterns.items():
            for pattern in info["patterns"]:
                matches = re.finditer(pattern, user_input, re.IGNORECASE)
                for match in matches:
                    indicators.append({
                        "type": category,
                        "text": match.group(),
                        "position": match.span(),
                        "strength": info["strength"]
                    })
        
        return indicators
    
    def _analyze_emotional_signals(self, user_input: str) -> Dict[str, Any]:
        """感情シグナルの分析"""
        emotional_signals = {
            "positive": 0.0,
            "negative": 0.0,
            "excitement": 0.0,
            "curiosity": 0.0,
            "satisfaction": 0.0,
            "detected_emotions": []
        }
        
        # 感情パターン
        emotion_patterns = {
            "positive": {
                "patterns": [r"(いい|良い|好き|素晴らしい|最高|すごい|きれい|美しい)", r"(ありがとう|感謝|嬉しい|楽しい)"],
                "weight": 1.0
            },
            "negative": {
                "patterns": [r"(嫌|ダメ|悪い|微妙|イマイチ|つまらない)", r"(残念|がっかり|悲しい|困った)"],
                "weight": 1.0
            },
            "excitement": {
                "patterns": [r"(！|!!|わー|やった|すげー)", r"(興奮|テンション|盛り上がる)"],
                "weight": 0.8
            },
            "curiosity": {
                "patterns": [r"(？|\?|なぜ|どうして|どんな|気になる)", r"(知りたい|教えて|聞きたい)"],
                "weight": 0.7
            },
            "satisfaction": {
                "patterns": [r"(満足|納得|理解|わかった|そうか)", r"(完璧|十分|丁度いい)"],
                "weight": 0.6
            }
        }
        
        for emotion, info in emotion_patterns.items():
            score = 0
            for pattern in info["patterns"]:
                matches = re.findall(pattern, user_input, re.IGNORECASE)
                score += len(matches) * info["weight"]
            
            if score > 0:
                emotional_signals[emotion] = min(1.0, score)
                emotional_signals["detected_emotions"].append({
                    "emotion": emotion,
                    "strength": score
                })
        
        return emotional_signals
    
    def _analyze_topic_relevance(self, user_input: str) -> Dict[str, Any]:
        """話題関連性の分析"""
        topic_relevance = {}
        
        # 現在アクティブな話題との関連性をチェック
        for topic_id, topic_data in self.active_topics.items():
            relevance_score = self._calculate_topic_relevance_score(user_input, topic_data)
            if relevance_score > 0.3:  # 閾値以上の関連性
                topic_relevance[topic_id] = {
                    "relevance_score": relevance_score,
                    "topic_data": topic_data,
                    "related_keywords": self._extract_related_keywords(user_input, topic_data)
                }
        
        return topic_relevance
    
    def _calculate_topic_relevance_score(self, user_input: str, topic_data: Dict[str, Any]) -> float:
        """話題との関連性スコアを計算"""
        score = 0.0
        user_lower = user_input.lower()
        
        # 代名詞・指示語がある場合は基本スコアを与える
        pronoun_keywords = ["この", "その", "あの", "さっき", "前", "似た", "同じ"]
        has_pronoun = any(keyword in user_lower for keyword in pronoun_keywords)
        
        if has_pronoun:
            score += 0.5  # 基本的な代名詞関連性
        
        # タイトル関連性
        title = topic_data.get("title", "").lower()
        if title:
            # 完全一致
            if title in user_lower:
                score += 1.0
            else:
                # 部分一致
                title_words = title.split()
                for word in title_words:
                    if len(word) >= 2 and word in user_lower:
                        score += 0.3
        
        # チャンネル関連性
        channel = topic_data.get("channel", "").lower()
        if channel and channel in user_lower:
            score += 0.5
        
        # ジャンル関連性
        genre = topic_data.get("genre", "").lower()
        if genre and genre in user_lower:
            score += 0.4
        
        # キーワード関連性
        keywords = topic_data.get("keywords", [])
        for keyword in keywords:
            if keyword.lower() in user_lower:
                score += 0.2
        
        # 曲・動画関連の一般的なキーワード
        music_keywords = ["曲", "歌", "動画", "楽曲", "音楽"]
        if any(keyword in user_lower for keyword in music_keywords):
            score += 0.3
        
        return min(1.0, score)
    
    def _extract_related_keywords(self, user_input: str, topic_data: Dict[str, Any]) -> List[str]:
        """関連キーワードを抽出"""
        related_keywords = []
        user_lower = user_input.lower()
        
        # 各種データからキーワード抽出
        for key in ["title", "channel", "genre"]:
            value = topic_data.get(key, "")
            if value and value.lower() in user_lower:
                related_keywords.append(value)
        
        # 存在するキーワード
        for keyword in topic_data.get("keywords", []):
            if keyword.lower() in user_lower:
                related_keywords.append(keyword)
        
        return related_keywords
    
    def resolve_references(self, context_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        代名詞・指示語の参照解決
        
        Args:
            context_analysis: 文脈分析結果
            
        Returns:
            参照解決結果
        """
        resolution_result = {
            "resolved_references": [],
            "suggested_topics": [],
            "context_suggestions": [],
            "confidence": 0.0
        }
        
        if not context_analysis.get("requires_resolution"):
            return resolution_result
        
        # 代名詞ごとに解決を試行
        for pronoun in context_analysis.get("pronoun_references", []):
            resolved = self._resolve_single_pronoun(pronoun, context_analysis)
            if resolved:
                resolution_result["resolved_references"].append(resolved)
        
        # 話題関連性に基づく提案
        for topic_id, relevance_data in context_analysis.get("topic_relevance", {}).items():
            if relevance_data["relevance_score"] > self.config["reference_confidence_threshold"]:
                resolution_result["suggested_topics"].append({
                    "topic_id": topic_id,
                    "topic_data": relevance_data["topic_data"],
                    "confidence": relevance_data["relevance_score"]
                })
        
        # 全体の信頼度計算
        if resolution_result["resolved_references"] or resolution_result["suggested_topics"]:
            total_confidence = 0.0
            count = 0
            
            for ref in resolution_result["resolved_references"]:
                total_confidence += ref.get("confidence", 0.0)
                count += 1
            
            for topic in resolution_result["suggested_topics"]:
                total_confidence += topic.get("confidence", 0.0)
                count += 1
            
            if count > 0:
                resolution_result["confidence"] = total_confidence / count
        
        return resolution_result
    
    def _resolve_single_pronoun(self, pronoun: Dict[str, Any], context_analysis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """単一の代名詞を解決"""
        pronoun_type = pronoun.get("type")
        pronoun_text = pronoun.get("text", "").lower()
        
        # 時間的指示語の解決
        if pronoun_type == "temporal":
            return self._resolve_temporal_reference(pronoun, context_analysis)
        
        # 指示語の解決
        elif pronoun_type == "demonstrative":
            return self._resolve_demonstrative_reference(pronoun, context_analysis)
        
        # 相対的指示の解決
        elif pronoun_type == "relative":
            return self._resolve_relative_reference(pronoun, context_analysis)
        
        return None
    
    def _resolve_temporal_reference(self, pronoun: Dict[str, Any], context_analysis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """時間的指示語の解決"""
        if len(self.conversation_memory) == 0:
            return None
        
        # 最近の会話から候補を抽出
        recent_conversations = list(self.conversation_memory)[-3:]  # 最近3件
        
        for conv in reversed(recent_conversations):  # 新しい順
            if conv.get("mentioned_videos"):
                for video_info in conv["mentioned_videos"]:
                    return {
                        "pronoun": pronoun,
                        "resolved_topic": video_info,
                        "confidence": 0.8,
                        "resolution_type": "temporal",
                        "source_conversation": conv["timestamp"]
                    }
        
        return None
    
    def _resolve_demonstrative_reference(self, pronoun: Dict[str, Any], context_analysis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """指示語の解決"""
        # 最もスコアの高い話題を返す
        topic_relevance = context_analysis.get("topic_relevance", {})
        
        if topic_relevance:
            best_topic_id = max(topic_relevance.keys(), 
                              key=lambda tid: topic_relevance[tid]["relevance_score"])
            best_topic = topic_relevance[best_topic_id]
            
            return {
                "pronoun": pronoun,
                "resolved_topic": best_topic["topic_data"],
                "confidence": best_topic["relevance_score"],
                "resolution_type": "demonstrative",
                "related_keywords": best_topic["related_keywords"]
            }
        
        return None
    
    def _resolve_relative_reference(self, pronoun: Dict[str, Any], context_analysis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """相対的指示の解決"""
        pronoun_text = pronoun.get("text", "").lower()
        
        # 「似た」「同じ」等は最近の話題から類似を検索
        if any(keyword in pronoun_text for keyword in ["似た", "同じ", "類似"]):
            if self.active_topics:
                # アクティブな話題の中から最新のものを選択
                latest_topic_id = max(self.active_topics.keys(), 
                                    key=lambda tid: self.active_topics[tid].get("last_mentioned", ""))
                
                return {
                    "pronoun": pronoun,
                    "resolved_topic": self.active_topics[latest_topic_id],
                    "confidence": 0.7,
                    "resolution_type": "relative_similarity",
                    "similarity_request": True
                }
        
        return None
    
    def update_conversation_memory(self, user_input: str, context_analysis: Dict[str, Any], 
                                 mentioned_videos: List[Dict[str, Any]] = None):
        """
        会話記憶を更新
        
        Args:
            user_input: ユーザーの入力
            context_analysis: 文脈分析結果
            mentioned_videos: 言及された動画のリスト
        """
        conversation_entry = {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "context_analysis": context_analysis,
            "mentioned_videos": mentioned_videos or [],
            "emotional_state": context_analysis.get("emotional_signals", {}),
            "continuity_indicators": context_analysis.get("continuity_indicators", [])
        }
        
        self.conversation_memory.append(conversation_entry)
        
        # アクティブ話題の更新
        if mentioned_videos:
            for video_info in mentioned_videos:
                video_id = video_info.get("video_id")
                if video_id:
                    self.active_topics[video_id] = {
                        "video_id": video_id,
                        "title": video_info.get("title", ""),
                        "channel": video_info.get("channel", ""),
                        "genre": video_info.get("genre", ""),
                        "keywords": self._extract_keywords_from_video(video_info),
                        "last_mentioned": datetime.now().isoformat(),
                        "mention_count": self.active_topics.get(video_id, {}).get("mention_count", 0) + 1
                    }
        
        # 古い話題の削除
        self._cleanup_old_topics()
        
        # 自動保存
        self._save_context()
        
        print(f"[文脈理解] 📝 会話記憶更新: {len(self.conversation_memory)}件, アクティブ話題: {len(self.active_topics)}件")
    
    def _extract_keywords_from_video(self, video_info: Dict[str, Any]) -> List[str]:
        """動画情報からキーワードを抽出"""
        keywords = []
        
        # タイトルから重要語句を抽出
        title = video_info.get("title", "")
        if title:
            # 簡単なキーワード抽出（カタカナ、漢字ひらがな3文字以上）
            title_keywords = re.findall(r'[ァ-ヶー]{3,}|[ぁ-ゖ一-龯]{3,}', title)
            keywords.extend(title_keywords)
        
        # チャンネル名
        channel = video_info.get("channel", "")
        if channel:
            keywords.append(channel)
        
        # ジャンル
        genre = video_info.get("genre", "")
        if genre:
            keywords.append(genre)
        
        return list(set(keywords))  # 重複除去
    
    def _cleanup_old_topics(self):
        """古い話題の削除"""
        current_time = datetime.now()
        timeout_delta = timedelta(minutes=self.config["context_timeout_minutes"])
        
        topics_to_remove = []
        for topic_id, topic_data in self.active_topics.items():
            last_mentioned_str = topic_data.get("last_mentioned")
            if last_mentioned_str:
                try:
                    last_mentioned = datetime.fromisoformat(last_mentioned_str)
                    if current_time - last_mentioned > timeout_delta:
                        topics_to_remove.append(topic_id)
                except:
                    topics_to_remove.append(topic_id)
        
        for topic_id in topics_to_remove:
            del self.active_topics[topic_id]
    
    def get_context_summary(self) -> Dict[str, Any]:
        """現在の文脈状況のサマリーを取得"""
        return {
            "conversation_count": len(self.conversation_memory),
            "active_topics_count": len(self.active_topics),
            "active_topics": list(self.active_topics.keys()),
            "recent_emotions": self._get_recent_emotional_trends(),
            "context_quality": self._assess_context_quality()
        }
    
    def _get_recent_emotional_trends(self) -> Dict[str, float]:
        """最近の感情傾向を取得"""
        if not self.conversation_memory:
            return {}
        
        # 最近3件の会話の感情を集計
        recent_conversations = list(self.conversation_memory)[-3:]
        emotion_totals = {}
        
        for conv in recent_conversations:
            emotional_signals = conv.get("emotional_state", {})
            for emotion, value in emotional_signals.items():
                if emotion != "detected_emotions" and isinstance(value, (int, float)):
                    emotion_totals[emotion] = emotion_totals.get(emotion, 0) + value
        
        # 平均化
        for emotion in emotion_totals:
            emotion_totals[emotion] /= len(recent_conversations)
        
        return emotion_totals
    
    def _assess_context_quality(self) -> Dict[str, Any]:
        """文脈品質の評価"""
        quality_metrics = {
            "completeness": 0.0,  # 文脈の完全性
            "continuity": 0.0,    # 継続性
            "relevance": 0.0,     # 関連性
            "overall": 0.0
        }
        
        # 完全性: 会話記憶の充実度
        if len(self.conversation_memory) >= 3:
            quality_metrics["completeness"] = min(1.0, len(self.conversation_memory) / 5)
        
        # 継続性: 継続性指標の存在
        if self.conversation_memory:
            recent_conv = list(self.conversation_memory)[-1]
            continuity_indicators = recent_conv.get("continuity_indicators", [])
            quality_metrics["continuity"] = min(1.0, len(continuity_indicators) * 0.3)
        
        # 関連性: アクティブ話題の存在
        quality_metrics["relevance"] = min(1.0, len(self.active_topics) * 0.5)
        
        # 総合評価
        quality_metrics["overall"] = (
            quality_metrics["completeness"] * 0.4 +
            quality_metrics["continuity"] * 0.3 +
            quality_metrics["relevance"] * 0.3
        )
        
        return quality_metrics


# 使用例・テスト
if __name__ == "__main__":
    print("=== 文脈理解向上システムテスト ===")
    
    context_system = ContextUnderstandingSystem()
    
    # テストシナリオ
    test_conversations = [
        "アドベンチャーについて教えて",
        "この曲いいね！",
        "もっと似たような曲ある？",
        "あの動画のクリエイターは誰？"
    ]
    
    print("\n📝 文脈理解テスト:")
    for i, conversation in enumerate(test_conversations):
        print(f"\n会話 {i+1}: '{conversation}'")
        
        # 文脈分析
        analysis = context_system.analyze_input_context(conversation)
        print(f"  代名詞検出: {len(analysis['pronoun_references'])}件")
        print(f"  継続性指標: {len(analysis['continuity_indicators'])}件")
        print(f"  感情シグナル: {analysis['emotional_signals']['detected_emotions']}")
        
        # 参照解決
        if analysis["requires_resolution"]:
            resolution = context_system.resolve_references(analysis)
            print(f"  参照解決: 信頼度 {resolution['confidence']:.2f}")
        
        # 会話記憶更新（テスト用のダミー動画情報）
        if i == 0:  # 最初の会話で動画を設定
            test_video = {
                "video_id": "test_adventure",
                "title": "アドベンチャー",
                "channel": "テストチャンネル",
                "genre": "ポップス"
            }
            context_system.update_conversation_memory(conversation, analysis, [test_video])
        else:
            context_system.update_conversation_memory(conversation, analysis)
    
    # 最終サマリー
    summary = context_system.get_context_summary()
    print(f"\n📊 文脈サマリー:")
    print(f"  会話数: {summary['conversation_count']}")
    print(f"  アクティブ話題: {summary['active_topics_count']}件")
    print(f"  文脈品質: {summary['context_quality']['overall']:.2f}")
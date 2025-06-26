#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
会話コンテキスト構築システム - せつなBot統合用
ユーザーの発言から動画関連のコンテキストを構築
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from .youtube_knowledge_manager import YouTubeKnowledgeManager
from .video_conversation_history import VideoConversationHistory
from .topic_learning_system import TopicLearningSystem
from .personalized_recommendation_engine import PersonalizedRecommendationEngine
from .context_understanding_system import ContextUnderstandingSystem
from .multi_turn_conversation_manager import MultiTurnConversationManager


class ConversationContextBuilder:
    """会話コンテキストを構築するクラス"""
    
    def __init__(self):
        """初期化"""
        self.knowledge_manager = YouTubeKnowledgeManager()
        self.conversation_history = VideoConversationHistory()
        
        # Phase 2-B-2: 学習・推薦システム追加
        try:
            self.topic_learning = TopicLearningSystem()
            self.personalized_engine = PersonalizedRecommendationEngine(
                self.topic_learning,
                self.conversation_history,
                self.knowledge_manager
            )
            print("[コンテキスト] ✅ 個人化推薦システム統合完了")
        except Exception as e:
            print(f"[コンテキスト] ⚠️ 個人化推薦システム初期化失敗: {e}")
            self.topic_learning = None
            self.personalized_engine = None
        
        # Phase 2-B-3: 文脈理解・マルチターン会話システム追加
        try:
            self.context_understanding = ContextUnderstandingSystem()
            self.multi_turn_manager = MultiTurnConversationManager()
            print("[コンテキスト] ✅ 文脈理解・マルチターン会話システム統合完了")
        except Exception as e:
            print(f"[コンテキスト] ⚠️ 文脈理解システム初期化失敗: {e}")
            self.context_understanding = None
            self.multi_turn_manager = None
        
        # 動画関連質問のパターン（改善版）
        self.video_query_patterns = [
            # 知識確認系
            r'(.+)(知って|見た|聞いた)?(る?|ことある?|こと?)?',
            r'(.+)(の|っていう)?(動画|曲|歌|MV|ミュージックビデオ)(.+)?',
            r'(.+)(って|という)(クリエイター|チャンネル|アーティスト)',
            
            # 推薦・質問系
            r'(何か|どんな|おすすめの?)(.+)?(動画|曲|歌)(.+)?',
            r'(最近|今|新しい)(.+)?(見た|聞いた)(.+)?(動画|曲)',
            
            # 具体的言及系
            r'(.+)について',
            r'(.+)って(どう|どんな)',
            r'(.+)の(印象|感想|分析)',
            
            # 継続会話・単純言及系（新規追加）
            r'(じゃあ|それじゃ|では)?(.+)(は|って)?$',  # 「じゃあ アドベンチャーは」等
            r'^(.+)(は|って)$',  # 「アドベンチャーは」等の単純言及
            r'(そっちの|その|あの)(.+)',  # 文脈参照
        ]
        
        print("[コンテキスト] ✅ 会話コンテキスト構築システム初期化完了")
    
    def _convert_katakana_to_english(self, katakana: str) -> List[str]:
        """
        カタカナを可能性のある英語に変換
        
        Args:
            katakana: カタカナ文字列
            
        Returns:
            変換候補のリスト
        """
        # よく使われる変換パターン
        common_conversions = {
            'トリニティ': ['TRINITY', 'trinity'],
            'エックスオーエックスオー': ['XOXO', 'xoxo'],
            'ボカロ': ['VOCALOID', 'vocaloid'],
            'ボイス': ['VOICE', 'voice'],
            'ミュージック': ['MUSIC', 'music'],
            'ビデオ': ['VIDEO', 'video'],
            'クリエイター': ['CREATOR', 'creator'],
            'チャンネル': ['CHANNEL', 'channel'],
            'コラボ': ['COLLABORATION', 'collaboration', 'collab'],
            'オリジナル': ['ORIGINAL', 'original'],
            'カバー': ['COVER', 'cover'],
        }
        
        candidates = []
        
        # 直接変換
        if katakana in common_conversions:
            candidates.extend(common_conversions[katakana])
        
        # 部分マッチング
        for jp, en_list in common_conversions.items():
            if jp in katakana or katakana in jp:
                candidates.extend(en_list)
        
        return candidates

    def _extract_keywords(self, text: str) -> List[str]:
        """
        テキストから検索用キーワードを抽出
        
        Args:
            text: 入力テキスト
            
        Returns:
            抽出されたキーワードのリスト
        """
        keywords = []
        text_clean = text.strip()
        
        # 固有名詞候補（カタカナ、英数字、特殊記号組み合わせ）
        proper_noun_patterns = [
            r'[ァ-ヶー]+',  # カタカナ
            r'[A-Za-z][A-Za-z0-9]*',  # 英数字
            r'▽▲[^▲▽]*▲▽',  # TRiNITY形式
            r'にじさんじ',  # 重要な固有名詞
            r'VOICEVOX|ボイスボックス',  # その他固有名詞
        ]
        
        for pattern in proper_noun_patterns:
            matches = re.findall(pattern, text_clean)
            for match in matches:
                if len(match) > 1:  # 1文字は除外
                    keywords.append(match)
                    
                    # カタカナの場合、英語変換候補も追加
                    if re.match(r'[ァ-ヶー]+', match):
                        english_candidates = self._convert_katakana_to_english(match)
                        keywords.extend(english_candidates)
        
        # 楽曲・動画関連キーワード
        content_keywords = [
            r'([^の\s]{2,})(の)?(動画|曲|歌|MV|ミュージックビデオ)',  # 「XXXの動画」
            r'([^っ\s]{2,})(って)(曲|歌)',  # 「XXXって曲」
            r'([^に\s]{2,})(について)',  # 「XXXについて」
        ]
        
        # 一般的な動画関連表現の場合は、形容詞も含める
        general_video_patterns = [
            r'(最近|新しい|面白い|良い|おすすめ)',  # 一般的な形容詞
            r'(動画|曲|歌|MV)',  # 動画関連キーワード
        ]
        
        # 動画キーワードがある場合の一般的な形容詞抽出
        if any(keyword in text_clean for keyword in ['動画', '曲', '歌', 'MV']):
            for pattern in general_video_patterns:
                matches = re.findall(pattern, text_clean)
                for match in matches:
                    if len(match) > 1:
                        keywords.append(match)
        
        for pattern in content_keywords:
            matches = re.findall(pattern, text_clean)
            for match in matches:
                if isinstance(match, tuple):
                    keyword = match[0].strip()
                    if keyword and len(keyword) > 1:
                        keywords.append(keyword)
                        
                        # この場合も英語変換を試行
                        if re.match(r'[ァ-ヶー]+', keyword):
                            english_candidates = self._convert_katakana_to_english(keyword)
                            keywords.extend(english_candidates)
        
        # 重複除去と長い順ソート（より具体的なキーワードを優先）
        unique_keywords = list(set(keywords))
        unique_keywords.sort(key=len, reverse=True)
        
        return unique_keywords[:8]  # 英語変換候補が増えるので最大8個まで

    def detect_video_queries(self, text: str) -> List[Dict[str, Any]]:
        """
        テキストから動画関連クエリを検出
        
        Args:
            text: ユーザーの入力テキスト
            
        Returns:
            検出されたクエリのリスト
        """
        queries = []
        text_clean = text.strip()
        
        # 直接的な動画関連キーワード検出
        video_keywords = ['動画', '曲', '歌', 'MV', 'ミュージックビデオ', 'クリエイター', 'チャンネル']
        has_video_keyword = any(keyword in text_clean for keyword in video_keywords)
        
        # キーワード抽出
        extracted_keywords = self._extract_keywords(text_clean)
        
        # 知識確認パターン検出
        knowledge_patterns = [
            r'(.+)知って(る|ます|いる|ますか)?',
            r'(.+)(見た|聞いた)ことある?',
            r'(.+)って(知って|聞いて)(る|いる|ますか)?',
            r'(.+)ある\?',
            r'(.+)について(.+)知って'
        ]
        
        for pattern in knowledge_patterns:
            matches = re.findall(pattern, text_clean)
            for match in matches:
                # マッチした部分からクエリを抽出
                if isinstance(match, tuple):
                    query_text = match[0].strip()
                else:
                    query_text = match.strip()
                
                if query_text and len(query_text) > 1:
                    # キーワード抽出を優先、フォールバックで元のクエリ
                    search_terms = extracted_keywords if extracted_keywords else [query_text]
                    
                    for term in search_terms:
                        queries.append({
                            'type': 'knowledge_check',
                            'query': term,
                            'original_text': text_clean,
                            'confidence': 0.9 if term in extracted_keywords else 0.6
                        })
        
        # 推薦・質問パターン検出
        recommendation_patterns = [
            r'(何か|どんな|おすすめ)(.+)?(動画|曲|歌)',
            r'(面白い|良い|新しい)(.+)?(動画|曲|歌)',
            r'(最近|今)(.+)?(見た|聞いた)'
        ]
        
        for pattern in recommendation_patterns:
            if re.search(pattern, text_clean):
                # 推薦系もキーワード抽出を使用
                search_terms = extracted_keywords if extracted_keywords else [text_clean]
                
                for term in search_terms:
                    queries.append({
                        'type': 'recommendation',
                        'query': term,
                        'original_text': text_clean,
                        'confidence': 0.8 if term in extracted_keywords else 0.5
                    })
        
        # 抽出されたキーワードがあり、動画関連キーワードがある場合
        if extracted_keywords and has_video_keyword and not queries:
            for keyword in extracted_keywords:
                queries.append({
                    'type': 'general_search',
                    'query': keyword,
                    'original_text': text_clean,
                    'confidence': 0.7
                })
        
        # 新規追加: キーワードがあるが動画関連キーワードがない場合でも、
        # 具体的なキーワードがあれば検索対象として扱う
        if extracted_keywords and not queries:
            for keyword in extracted_keywords:
                if self._is_specific_query(keyword):
                    queries.append({
                        'type': 'contextual_search',
                        'query': keyword,
                        'original_text': text_clean,
                        'confidence': 0.6
                    })
        
        return queries
    
    def _is_specific_query(self, query: str) -> bool:
        """
        クエリが具体的な固有名詞を含むかチェック（改善版）
        
        Args:
            query: 検索クエリ
            
        Returns:
            具体的なクエリかどうか
        """
        # 一般的すぎるキーワード（これらのみの場合は検索しない）
        generic_keywords = {
            '動画', '曲', '歌', 'MV', 'ミュージックビデオ',
            '最近', '新しい', '面白い', '良い', 'おすすめ', 
            'いい', 'すごい', '人気', '有名', '最近見た',
            '何か', 'どんな', 'ある', 'ない', 'やつ', 'もの',
            'とか', 'とき', 'ここ', 'そこ', 'あそこ'
        }
        
        print(f"[コンテキスト] 具体性チェック: '{query}'")
        
        # 高信頼度固有名詞パターン
        high_confidence_patterns = [
            r'にじさんじ',      # 重要な固有名詞
            r'▽▲.*▲▽',       # TRiNITY形式
            r'[A-Z][A-Z]+',    # 大文字の略語（例：XOXO）
            r'[A-Za-z]{4,}',   # 4文字以上の英語（一般的な英語除外）
        ]
        
        # 中信頼度固有名詞パターン
        medium_confidence_patterns = [
            r'[ァ-ヶー]{3,}',  # 3文字以上のカタカナ
            r'[A-Za-z]{3}',    # 3文字の英語
        ]
        
        # 低信頼度固有名詞パターン（追加検証要）
        low_confidence_patterns = [
            r'[ァ-ヶー]{2}',   # 2文字のカタカナ
            r'[A-Za-z]{2}',    # 2文字の英語
        ]
        
        # 一般的な英語を除外
        common_english_words = {
            'music', 'video', 'cover', 'song', 'new', 'old', 
            'good', 'bad', 'nice', 'cool', 'hot', 'big', 'small',
            'up', 'down', 'in', 'out', 'on', 'off', 'all', 'any'
        }
        
        confidence_score = 0
        found_patterns = []
        
        # 高信頼度パターンチェック
        for pattern in high_confidence_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            for match in matches:
                if match.lower() not in common_english_words:
                    confidence_score += 10
                    found_patterns.append(f"高信頼度: {match}")
        
        # 中信頼度パターンチェック
        for pattern in medium_confidence_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            for match in matches:
                if match.lower() not in common_english_words:
                    confidence_score += 5
                    found_patterns.append(f"中信頼度: {match}")
        
        # 低信頼度パターンチェック
        for pattern in low_confidence_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            for match in matches:
                if match.lower() not in common_english_words:
                    confidence_score += 2
                    found_patterns.append(f"低信頼度: {match}")
        
        # 日本語固有名詞候補（3文字以上のひらがな・漢字）
        japanese_name_pattern = r'[ぁ-ゖ一-龯]{3,}'
        japanese_matches = re.findall(japanese_name_pattern, query)
        for match in japanese_matches:
            if match not in generic_keywords and match not in ['ありがとう', 'おはよう', 'こんにちは', 'こんばんは']:
                confidence_score += 8
                found_patterns.append(f"日本語固有名詞: {match}")
        
        # デバッグ出力
        if found_patterns:
            print(f"  → 発見パターン: {', '.join(found_patterns)}")
            print(f"  → 信頼度スコア: {confidence_score}")
        
        # 判定基準: スコア5以上で具体的とみなす
        is_specific = confidence_score >= 5
        
        if is_specific:
            print(f"  → 具体的クエリ（スコア: {confidence_score}）")
        else:
            print(f"  → 一般的クエリ（スコア: {confidence_score}）")
        
        return is_specific
    
    def _analyze_user_reaction_from_input(self, user_input: str) -> str:
        """
        ユーザー入力から反応を分析（簡易版）
        
        Args:
            user_input: ユーザーの入力
            
        Returns:
            反応タイプ (positive/neutral/negative)
        """
        user_lower = user_input.lower()
        
        # ポジティブ反応パターン
        positive_patterns = [
            r'(いい|良い|好き|気に入|素晴らしい|最高|すごい)',
            r'(もう一度|また|繰り返|リピート)',
            r'(ありがとう|サンキュー)',
            r'(感動|泣け|心に響|素敵|きれい|美しい)'
        ]
        
        # ネガティブ反応パターン
        negative_patterns = [
            r'(嫌い|ダメ|良くない|微妙|イマイチ)',
            r'(飽きた|もういい|違う)',
            r'(つまらない|面白くない|退屈)'
        ]
        
        for pattern in positive_patterns:
            if re.search(pattern, user_input):
                return "positive"
        
        for pattern in negative_patterns:
            if re.search(pattern, user_input):
                return "negative"
        
        return "neutral"  # デフォルト

    def build_video_context(self, queries: List[Dict[str, Any]], max_videos: int = 3) -> Optional[Dict[str, Any]]:
        """
        検出されたクエリから動画コンテキストを構築
        
        Args:
            queries: 検出されたクエリのリスト
            max_videos: 最大動画数
            
        Returns:
            構築されたコンテキスト
        """
        if not queries:
            return None
        
        # 重複除去
        unique_queries = []
        seen_queries = set()
        for query_info in queries:
            query = query_info['query']
            if query not in seen_queries:
                unique_queries.append(query_info)
                seen_queries.add(query)
        
        # 具体的なクエリのみをフィルタリング
        specific_queries = [q for q in unique_queries if self._is_specific_query(q['query'])]
        
        if not specific_queries:
            print("[コンテキスト] ⚠️ 具体的な固有名詞なし - 個人化推薦を試行")
            
            # 元の入力からコンテキストヒントを抽出
            context_hint = ""
            for query_info in unique_queries:
                context_hint += " " + query_info['query']
            
            # Phase 2-B-2: 個人化推薦を試行
            if self.personalized_engine:
                try:
                    personalized_result = self.personalized_engine.get_personalized_recommendations(
                        context_hint.strip(), limit=2
                    )
                    
                    if personalized_result["recommendations"]:
                        print(f"[コンテキスト] 🧠 個人化推薦成功: {len(personalized_result['recommendations'])}件")
                        
                        recommended_videos = []
                        for rec in personalized_result["recommendations"]:
                            video_data = rec['video_data']
                            metadata = video_data.get('metadata', {})
                            
                            video_info = {
                                'video_id': rec['video_id'],
                                'title': metadata.get('title', ''),
                                'channel': metadata.get('channel_title', ''),
                                'analysis_status': video_data.get('analysis_status', 'unknown'),
                                'search_score': rec.get('preference_score', 0.5) * 100,  # 嗜好スコアを検索スコア形式に変換
                                'query_type': 'personalized_recommendation',
                                'matched_query': '個人化推薦',
                                'recommendation_reason': rec.get('recommendation_reason', '')
                            }
                            
                            # 分析結果を追加
                            if 'creative_insight' in video_data:
                                insight = video_data['creative_insight']
                                video_info['creators'] = insight.get('creators', [])
                                video_info['music_analysis'] = insight.get('music_analysis', {})
                                video_info['lyrics'] = insight.get('lyrics', {})
                            
                            recommended_videos.append(video_info)
                        
                        for video in recommended_videos:
                            print(f"  - {video['title'][:50]}... (嗜好スコア: {video['search_score']:.1f})")
                        
                        return {
                            'search_terms': [context_hint.strip()],
                            'videos': recommended_videos,
                            'total_found': len(recommended_videos),
                            'recommendation_type': personalized_result["recommendation_type"],
                            'user_analysis': personalized_result["user_analysis"]
                        }
                        
                except Exception as e:
                    print(f"[コンテキスト] ⚠️ 個人化推薦失敗: {e}")
            
            # フォールバック: 従来のランダム推薦
            print("[コンテキスト] 🎲 フォールバック: ランダム推薦を実行")
            random_recommendations = self.knowledge_manager.get_random_recommendation(
                context_hint=context_hint.strip(), 
                limit=2
            )
            
            if not random_recommendations:
                print("[コンテキスト] ❌ ランダム推薦も失敗")
                return None
            
            # 推薦動画をコンテキスト形式に変換
            recommended_videos = []
            for rec in random_recommendations:
                video_data = rec['data']
                metadata = video_data.get('metadata', {})
                
                video_info = {
                    'video_id': rec['video_id'],
                    'title': metadata.get('title', ''),
                    'channel': metadata.get('channel_title', ''),
                    'analysis_status': video_data.get('analysis_status', 'unknown'),
                    'search_score': rec['score'],
                    'query_type': 'random_recommendation',
                    'matched_query': 'ランダム推薦'
                }
                
                # 分析結果を追加
                if 'creative_insight' in video_data:
                    insight = video_data['creative_insight']
                    video_info['creators'] = insight.get('creators', [])
                    video_info['music_analysis'] = insight.get('music_analysis', {})
                    video_info['lyrics'] = insight.get('lyrics', {})
                
                recommended_videos.append(video_info)
            
            print(f"[コンテキスト] 🎲 ランダム推薦成功: {len(recommended_videos)}件")
            for video in recommended_videos:
                print(f"  - {video['title'][:50]}... (重み付きスコア: {video['search_score']})")
            
            return {
                'search_terms': [context_hint.strip()],
                'videos': recommended_videos,
                'total_found': len(recommended_videos),
                'recommendation_type': 'random'
            }
        
        all_videos = []
        search_terms = []
        
        # 各クエリに対して動画検索
        for query_info in specific_queries:
            query = query_info['query']
            search_terms.append(query)
            
            # 動画検索実行
            search_results = self.knowledge_manager.search_videos(query, limit=max_videos)
            
            for result in search_results:
                # 低スコア結果を除外（スコア10未満）
                if result['score'] < 10:
                    continue
                    
                video_data = result['data']
                metadata = video_data.get('metadata', {})
                
                video_info = {
                    'video_id': result['video_id'],
                    'title': metadata.get('title', ''),
                    'channel': metadata.get('channel_title', ''),
                    'analysis_status': video_data.get('analysis_status', 'unknown'),
                    'search_score': result['score'],
                    'query_type': query_info['type'],
                    'matched_query': query
                }
                
                # 分析結果を追加
                if 'creative_insight' in video_data:
                    insight = video_data['creative_insight']
                    video_info['creators'] = insight.get('creators', [])
                    video_info['music_analysis'] = insight.get('music_analysis', {})
                    video_info['lyrics'] = insight.get('lyrics', {})
                
                all_videos.append(video_info)
        
        if not all_videos:
            return None
        
        # 重複除去とスコア順ソート
        unique_videos = {}
        for video in all_videos:
            video_id = video['video_id']
            if video_id not in unique_videos or video['search_score'] > unique_videos[video_id]['search_score']:
                unique_videos[video_id] = video
        
        sorted_videos = sorted(
            unique_videos.values(),
            key=lambda x: x['search_score'],
            reverse=True
        )[:max_videos]
        
        return {
            'search_terms': search_terms,
            'videos': sorted_videos,
            'total_found': len(unique_videos)
        }
    
    def format_for_setsuna(self, context: Dict[str, Any]) -> str:
        """
        コンテキストをせつな用のフォーマットに変換（感情表現強化版）
        
        Args:
            context: 動画コンテキスト
            
        Returns:
            せつな用フォーマットのテキスト
        """
        if not context or not context.get('videos'):
            return ""
        
        formatted_parts = []
        
        # 動画情報をフォーマット（会話履歴統合版）
        for video in context['videos']:
            video_info = []
            
            # 基本情報
            video_id = video.get('video_id', '')
            full_title = video.get('title', '')
            channel = video.get('channel', '')
            analysis_status = video.get('analysis_status', 'unknown')
            
            # タイトル簡略化
            main_title = self.knowledge_manager._extract_main_title(full_title)
            
            # 会話履歴の取得
            conversation_context = self.conversation_history.get_conversation_context(video_id)
            conversation_hints = []
            if conversation_context:
                conversation_hints = self.conversation_history.generate_conversation_hints(video_id)
            
            # 簡略化されたタイトルを使用（ただし、元のタイトルも保持）
            video_info.append(f"楽曲名: {main_title}")
            if main_title != full_title and len(full_title) <= 80:
                video_info.append(f"フルタイトル: {full_title}")
            
            if channel:
                video_info.append(f"チャンネル: {channel}")
            
            # 会話履歴情報の追加
            if conversation_context:
                familiarity_level = conversation_context['familiarity_level']
                conversation_count = conversation_context['conversation_count']
                recency = conversation_context['recency']
                
                if familiarity_level != 'new':
                    if familiarity_level == 'very_familiar':
                        video_info.append(f"おなじみの楽曲（{conversation_count}回会話）")
                    elif familiarity_level == 'familiar':
                        video_info.append(f"前にも話した楽曲（{conversation_count}回会話）")
                    else:
                        video_info.append(f"話したことがある楽曲（{conversation_count}回会話）")
                    
                    if recency == 'today':
                        video_info.append("今日も話題に上った")
                    elif recency == 'recent':
                        video_info.append("最近話した")
            
            # 分析結果がある場合
            if analysis_status == 'completed':
                # クリエイター情報
                creators = video.get('creators', [])
                if creators:
                    creator_names = [c.get('name', '') for c in creators if c.get('name')]
                    if creator_names:
                        video_info.append(f"クリエイター: {', '.join(creator_names)}")
                
                # 楽曲分析
                music_analysis = video.get('music_analysis', {})
                emotion_hints = []
                if music_analysis:
                    if music_analysis.get('genre'):
                        video_info.append(f"ジャンル: {music_analysis['genre']}")
                    if music_analysis.get('mood'):
                        mood = music_analysis['mood']
                        video_info.append(f"ムード: {mood}")
                        emotion_hints.append(f"mood_{mood}")
                
                # 歌詞情報
                lyrics = video.get('lyrics', {})
                if lyrics:
                    if lyrics.get('theme'):
                        theme = lyrics['theme']
                        video_info.append(f"テーマ: {theme}")
                        emotion_hints.append(f"theme_{theme}")
                    if lyrics.get('main_message'):
                        video_info.append(f"メッセージ: {lyrics['main_message']}")
                
                # 感情表現ヒントを追加
                if emotion_hints:
                    video_info.append(f"感情ヒント: {', '.join(emotion_hints)}")
                
                video_info.append("（分析済み）")
            else:
                video_info.append("（聞いたことはある）")
            
            # 会話ヒントの追加
            if conversation_hints:
                video_info.append(f"会話ヒント: {', '.join(conversation_hints[:2])}")  # 最大2つまで
            
            formatted_parts.append(" / ".join(video_info))
        
        # 推薦タイプに応じた表現指示を追加（個人化推薦対応）
        recommendation_type = context.get('recommendation_type', 'search')
        user_analysis = context.get('user_analysis', {})
        
        if recommendation_type == 'familiar':
            formatted_parts.append("【表現指示】馴染み推薦: 「いつものXXXだけど」「お気に入りのXXX」など親しみのある推薦表現を使用")
        elif recommendation_type == 'novel':
            formatted_parts.append("【表現指示】新規推薦: 「初めてだけど好みに合いそうなXXX」「新しく見つけたXXX」など発見の推薦表現を使用")
        elif recommendation_type == 'specific':
            formatted_parts.append("【表現指示】嗜好マッチ推薦: 「ご希望の〜系ならXXX」「〜がお好みならXXX」など的確な推薦表現を使用")
        elif recommendation_type == 'mixed':
            formatted_parts.append("【表現指示】個人化推薦: 学習した嗜好を活かして「あなたならXXXが気に入りそう」など個人的推薦表現を使用")
        elif recommendation_type == 'random':
            formatted_parts.append("【表現指示】ランダム推薦: 「最近見た中では〜かな」「個人的には〜が気に入ってる」など自然な推薦表現を使用")
        else:
            formatted_parts.append("【表現指示】検索結果: 「〜について知ってるよ」「〜なら聞いたことがある」など知識ベースの表現を使用")
        
        # ユーザー分析結果に基づく追加指示
        if user_analysis.get('familiarity_preference') == 'familiar':
            formatted_parts.append("【追加指示】ユーザーは馴染みのあるものを求めているため、親しみやすい表現を重視")
        elif user_analysis.get('familiarity_preference') == 'new':
            formatted_parts.append("【追加指示】ユーザーは新しいものを求めているため、発見・新鮮さを強調した表現を使用")
        
        # 最終フォーマット
        result = "\n".join([f"• {info}" for info in formatted_parts])
        
        return result
    
    def process_user_input(self, user_input: str) -> Optional[str]:
        """
        ユーザー入力を処理して動画コンテキストを生成（文脈理解強化版）
        
        Args:
            user_input: ユーザーの入力
            
        Returns:
            せつな用のコンテキスト文字列（None if 動画関連でない）
        """
        print(f"[コンテキスト] 🔍 入力分析: '{user_input}'")
        
        # Phase 2-B-3: 文脈理解分析
        context_analysis = None
        if self.context_understanding:
            try:
                context_analysis = self.context_understanding.analyze_input_context(user_input)
                print(f"[コンテキスト] 🧠 文脈分析完了: 代名詞{len(context_analysis.get('pronoun_references', []))}件, 継続性{len(context_analysis.get('continuity_indicators', []))}件")
                
                # 参照解決の実行
                if context_analysis.get("requires_resolution"):
                    resolution_result = self.context_understanding.resolve_references(context_analysis)
                    print(f"[コンテキスト] 🔗 参照解決: 信頼度{resolution_result.get('confidence', 0):.2f}")
                    
                    # 解決された参照があれば、それを基にクエリを補強
                    if resolution_result.get("suggested_topics"):
                        print("[コンテキスト] 💡 文脈から話題を特定")
                        for suggestion in resolution_result["suggested_topics"]:
                            topic_data = suggestion["topic_data"]
                            print(f"  - {topic_data.get('title', 'unknown')} (信頼度: {suggestion['confidence']:.2f})")
                        
                        # 特定された話題を直接使用
                        return self._process_contextual_reference(user_input, resolution_result, context_analysis)
            except Exception as e:
                print(f"[コンテキスト] ⚠️ 文脈理解エラー: {e}")
        
        # 従来のクエリ検出
        queries = self.detect_video_queries(user_input)
        print(f"[コンテキスト] 📝 検出クエリ: {len(queries)}件")
        for i, query in enumerate(queries):
            print(f"  {i+1}. {query['type']}: '{query['query']}' (信頼度: {query['confidence']})")
        
        if not queries:
            print("[コンテキスト] ❌ 動画関連クエリなし")
            
            # Phase 2-B-3: 文脈理解で会話記憶更新（動画なしでも記録）
            if self.context_understanding:
                self.context_understanding.update_conversation_memory(user_input, context_analysis or {})
            
            return None
        
        # コンテキスト構築
        context = self.build_video_context(queries)
        if not context:
            print("[コンテキスト] ❌ マッチする動画なし")
            return None
        
        print(f"[コンテキスト] ✅ 動画発見: {len(context['videos'])}件")
        for video in context['videos']:
            print(f"  - {video['title'][:50]}... (スコア: {video['search_score']})")
        
        # 検出された動画情報を準備
        mentioned_videos = []
        for video in context['videos']:
            video_id = video['video_id']
            video_title = self.knowledge_manager._extract_main_title(video.get('title', ''))
            
            mentioned_videos.append({
                "video_id": video_id,
                "title": video_title,
                "channel": video.get('channel', ''),
                "genre": video.get('genre', ''),
                "search_score": video.get('search_score', 0)
            })
            
            # 従来のキャッシュ
            self.knowledge_manager.add_to_cache(video_id, user_input)
            
            # Phase 2-B-1: 会話履歴記録
            self.conversation_history.record_conversation(video_id, video_title, user_input)
            
            # Phase 2-B-2: 嗜好学習
            if self.topic_learning:
                try:
                    # 動画データを取得
                    full_video_data = self.knowledge_manager.get_video_context(video_id)
                    if full_video_data:
                        # ユーザー反応を自動分析（より詳細な分析は後で人手追加可能）
                        reaction = self._analyze_user_reaction_from_input(user_input)
                        self.topic_learning.learn_from_interaction(
                            full_video_data, reaction, user_input, video_title
                        )
                except Exception as e:
                    print(f"[コンテキスト] ⚠️ 嗜好学習エラー: {e}")
        
        # Phase 2-B-3: 文脈理解・マルチターン会話管理
        if self.context_understanding:
            self.context_understanding.update_conversation_memory(user_input, context_analysis or {}, mentioned_videos)
        
        if self.multi_turn_manager:
            try:
                turn_result = self.multi_turn_manager.add_turn(
                    user_input, context_analysis or {}, "", mentioned_videos
                )
                print(f"[コンテキスト] 🎭 対話状態: {turn_result.get('previous_state')} → {turn_result.get('new_state')}")
                
                # マルチターン会話コンテキストをフォーマットに反映
                conversation_context = self.multi_turn_manager.get_conversation_context_for_response()
                context['conversation_context'] = conversation_context
                
            except Exception as e:
                print(f"[コンテキスト] ⚠️ マルチターン管理エラー: {e}")
        
        # せつな用フォーマット
        formatted_context = self.format_for_setsuna(context)
        print(f"[コンテキスト] 📄 フォーマット済みコンテキスト:")
        print(formatted_context[:200] + "..." if len(formatted_context) > 200 else formatted_context)
        
        return formatted_context
    
    def _process_contextual_reference(self, user_input: str, resolution_result: Dict[str, Any], 
                                    context_analysis: Dict[str, Any]) -> Optional[str]:
        """
        文脈参照に基づく処理
        
        Args:
            user_input: ユーザーの入力
            resolution_result: 参照解決結果
            context_analysis: 文脈分析結果
            
        Returns:
            コンテキスト文字列
        """
        print("[コンテキスト] 🔗 文脈参照処理開始")
        
        # 解決された話題から動画情報を構築
        videos = []
        for suggestion in resolution_result.get("suggested_topics", []):
            topic_data = suggestion["topic_data"]
            
            video_info = {
                "video_id": topic_data.get("video_id", ""),
                "title": topic_data.get("title", ""),
                "channel": topic_data.get("channel", ""),
                "genre": topic_data.get("genre", ""),
                "search_score": suggestion["confidence"] * 100,  # 信頼度をスコアに変換
                "query_type": "contextual_reference",
                "matched_query": "文脈参照",
                "reference_type": suggestion.get("confidence", 0.5)
            }
            
            videos.append(video_info)
        
        if not videos:
            return None
        
        # 文脈ベースのコンテキストを構築
        context = {
            "search_terms": ["文脈参照"],
            "videos": videos,
            "total_found": len(videos),
            "context_type": "reference_resolution",
            "resolution_confidence": resolution_result.get("confidence", 0.0),
            "conversation_context": None
        }
        
        # 同様の記録・学習処理
        mentioned_videos = []
        for video in videos:
            video_id = video["video_id"]
            video_title = video["title"]
            
            if video_id:  # 有効な動画IDがある場合のみ
                mentioned_videos.append({
                    "video_id": video_id,
                    "title": video_title,
                    "channel": video.get("channel", ""),
                    "genre": video.get("genre", ""),
                    "search_score": video.get("search_score", 0)
                })
                
                # キャッシュ追加
                self.knowledge_manager.add_to_cache(video_id, user_input)
                
                # 会話履歴記録
                self.conversation_history.record_conversation(video_id, video_title, user_input)
                
                # 嗜好学習
                if self.topic_learning:
                    try:
                        full_video_data = self.knowledge_manager.get_video_context(video_id)
                        if full_video_data:
                            reaction = self._analyze_user_reaction_from_input(user_input)
                            self.topic_learning.learn_from_interaction(
                                full_video_data, reaction, user_input, video_title
                            )
                    except Exception as e:
                        print(f"[コンテキスト] ⚠️ 文脈参照での嗜好学習エラー: {e}")
        
        # 文脈理解・マルチターン管理
        if self.context_understanding:
            self.context_understanding.update_conversation_memory(user_input, context_analysis, mentioned_videos)
        
        if self.multi_turn_manager:
            try:
                turn_result = self.multi_turn_manager.add_turn(
                    user_input, context_analysis, "", mentioned_videos
                )
                print(f"[コンテキスト] 🎭 文脈参照での対話状態: {turn_result.get('previous_state')} → {turn_result.get('new_state')}")
                
                conversation_context = self.multi_turn_manager.get_conversation_context_for_response()
                context['conversation_context'] = conversation_context
                
            except Exception as e:
                print(f"[コンテキスト] ⚠️ 文脈参照でのマルチターン管理エラー: {e}")
        
        # フォーマット（特別な文脈参照指示を追加）
        formatted_context = self.format_for_setsuna(context)
        
        # 文脈参照の場合の追加指示
        contextual_instructions = [
            "【文脈参照】この応答は前の会話からの文脈参照に基づいています",
            f"【参照信頼度】{resolution_result.get('confidence', 0.0):.2f}",
            "【表現指示】「さっきの〜」「その〜について」など文脈を明示した自然な応答を使用"
        ]
        
        # 検出された代名詞情報を追加
        pronouns = context_analysis.get("pronoun_references", [])
        if pronouns:
            pronoun_texts = [p.get("text", "") for p in pronouns]
            contextual_instructions.append(f"【検出代名詞】{', '.join(pronoun_texts)}")
        
        # 継続性情報を追加
        continuity = context_analysis.get("continuity_indicators", [])
        if continuity:
            continuity_types = [c.get("type", "") for c in continuity]
            contextual_instructions.append(f"【継続性】{', '.join(set(continuity_types))}")
        
        final_context = formatted_context + "\n" + "\n".join([f"• {inst}" for inst in contextual_instructions])
        
        print("[コンテキスト] ✅ 文脈参照処理完了")
        return final_context


if __name__ == "__main__":
    # テスト実行
    builder = ConversationContextBuilder()
    
    test_inputs = [
        "TRiNITYの動画知ってる？",
        "にじさんじの歌ってみた動画ある？",
        "最近面白い動画見た？",
        "XOXOって曲について教えて"
    ]
    
    for test_input in test_inputs:
        print(f"\n🔍 入力: '{test_input}'")
        
        # クエリ検出テスト
        queries = builder.detect_video_queries(test_input)
        print(f"検出クエリ: {len(queries)}件")
        for query in queries:
            print(f"  - {query['type']}: '{query['query']}' (信頼度: {query['confidence']})")
        
        # コンテキスト生成テスト
        context_text = builder.process_user_input(test_input)
        if context_text:
            print(f"コンテキスト:\n{context_text}")
        else:
            print("コンテキスト: なし")
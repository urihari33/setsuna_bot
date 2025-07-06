#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
動画-画像統合コンテキストビルダー
動画情報と画像分析結果を統合して、会話用の文脈を構築
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from collections import defaultdict, Counter


class VideoImageContextBuilder:
    """動画と画像の統合コンテキスト構築エンジン"""
    
    def __init__(self, youtube_manager=None):
        """
        初期化
        
        Args:
            youtube_manager: YouTubeKnowledgeManagerインスタンス
        """
        self.youtube_manager = youtube_manager
        
        # 会話テンプレート読み込み
        self.conversation_templates = self._load_conversation_templates()
        
        # シーン分類設定
        self.scene_classifications = self._load_scene_classifications()
        
        # 視覚要素カテゴリ
        self.visual_element_categories = self._load_visual_categories()
        
        print("[コンテキスト] ✅ VideoImageContextBuilder初期化完了")
    
    def _load_conversation_templates(self) -> Dict[str, str]:
        """会話テンプレートを読み込み"""
        return {
            "general_video_discussion": """
{artist}の「{title}」について話しましょう。

【動画の印象】
{video_description}

【画像から分かること】
{image_summaries}

【話したいトピック】
{discussion_topics}

この動画の魅力について、どんなことが気になりますか？
""",

            "specific_image_focus": """
この画像について詳しく見てみましょう。

【画像の内容】
{image_description}

【動画全体での位置づけ】
{image_context_in_video}

【注目ポイント】
{key_visual_elements}

どんなところが印象的でしたか？
""",

            "visual_analysis": """
「{title}」の映像表現について分析してみました。

【視覚的な特徴】
{visual_characteristics}

【ストーリーの流れ】
{narrative_flow}

【アーティスティックな要素】
{artistic_elements}

映像の演出についてどう思いますか？
""",

            "music_video_comprehensive": """
{artist}の「{title}」の魅力を画像から分析してみました！

【楽曲の雰囲気】
{video_mood}

【映像の見どころ】
{visual_highlights}

【演出のポイント】
{production_points}

【話し合いたいこと】
{conversation_topics}

どのシーンが一番印象に残りましたか？
""",

            "simple_image_chat": """
{image_description}

{context_summary}

この画像について、何か聞きたいことはありますか？
"""
        }
    
    def _load_scene_classifications(self) -> Dict[str, List[str]]:
        """シーン分類カテゴリを読み込み"""
        return {
            "performance_scenes": [
                "ライブ演奏", "スタジオ録音", "ソロパフォーマンス", 
                "楽器演奏", "歌唱シーン", "ダンス"
            ],
            "narrative_scenes": [
                "ストーリー展開", "ドラマティックシーン", "回想シーン",
                "日常風景", "感情表現", "対話シーン"
            ],
            "artistic_scenes": [
                "抽象的映像", "シンボリック表現", "色彩効果",
                "ライティング効果", "特殊効果", "アニメーション"
            ],
            "environmental_scenes": [
                "自然風景", "都市風景", "室内空間", "スタジオ",
                "ライブ会場", "特別な場所"
            ]
        }
    
    def _load_visual_categories(self) -> Dict[str, List[str]]:
        """視覚要素カテゴリを読み込み"""
        return {
            "musical_elements": [
                "楽器", "マイク", "アンプ", "ヘッドホン", "楽譜",
                "レコーディング機器", "ピアノ", "ギター", "ドラム"
            ],
            "human_elements": [
                "アーティスト", "バンドメンバー", "観客", "スタッフ",
                "ダンサー", "コーラス", "子供", "大人"
            ],
            "technical_elements": [
                "照明", "カメラワーク", "エフェクト", "編集技法",
                "色調整", "構図", "フレーミング", "動き"
            ],
            "emotional_elements": [
                "表情", "ジェスチャー", "雰囲気", "感情表現",
                "エネルギー", "親密感", "力強さ", "優しさ"
            ],
            "environmental_elements": [
                "背景", "セット", "小道具", "衣装", "メイク",
                "装飾", "建築", "自然", "天候"
            ]
        }
    
    def build_comprehensive_context(self, video_id: str) -> Dict[str, Any]:
        """
        動画+全画像の包括的コンテキスト生成
        
        Args:
            video_id: YouTube動画ID
            
        Returns:
            包括的コンテキスト辞書
        """
        try:
            if not self.youtube_manager:
                return {"error": "YouTubeKnowledgeManagerが設定されていません"}
            
            print(f"[コンテキスト] 🔍 包括的コンテキスト構築開始: {video_id}")
            
            # Step 1: 基本データ収集
            video_data = self._collect_video_data(video_id)
            if not video_data:
                return {"error": "動画データが見つかりません"}
            
            # Step 2: 画像分析データ統合
            images_analysis = self._integrate_image_analyses(video_data['images_data'])
            
            # Step 3: 視覚的ストーリー構築
            visual_narrative = self._build_visual_narrative(images_analysis)
            
            # Step 4: 会話トピック生成
            conversation_topics = self._generate_discussion_topics(video_data, images_analysis)
            
            # Step 5: 総合コンテキスト構築
            comprehensive_context = {
                "video_id": video_id,
                "video_info": video_data['video_metadata'],
                "images_analysis": images_analysis,
                "visual_narrative": visual_narrative,
                "conversation_topics": conversation_topics,
                "context_summary": self._generate_context_summary(
                    video_data['video_metadata'], 
                    images_analysis, 
                    visual_narrative
                ),
                "generation_timestamp": datetime.now().isoformat()
            }
            
            print(f"[コンテキスト] ✅ 包括的コンテキスト構築完了")
            return comprehensive_context
            
        except Exception as e:
            print(f"[コンテキスト] ❌ 包括的コンテキスト構築エラー: {e}")
            return {"error": str(e)}
    
    def build_image_specific_context(self, video_id: str, image_id: str) -> Dict[str, Any]:
        """
        特定画像フォーカスのコンテキスト生成
        
        Args:
            video_id: YouTube動画ID
            image_id: 対象画像ID
            
        Returns:
            画像特化コンテキスト
        """
        try:
            if not self.youtube_manager:
                return {"error": "YouTubeKnowledgeManagerが設定されていません"}
            
            print(f"[コンテキスト] 🎯 画像特化コンテキスト構築: {image_id}")
            
            # 動画情報取得
            video_data = self._collect_video_data(video_id)
            if not video_data:
                return {"error": "動画データが見つかりません"}
            
            # 対象画像の分析結果取得
            target_image = None
            for img_data in video_data['images_data']:
                if img_data.get('image_id') == image_id:
                    target_image = img_data
                    break
            
            if not target_image:
                return {"error": f"画像が見つかりません: {image_id}"}
            
            # 画像分析結果取得
            analysis_result = self.youtube_manager.get_image_analysis_result(video_id, image_id)
            if not analysis_result:
                return {"error": "画像分析結果が見つかりません"}
            
            # 他の画像との関係性分析
            other_images = [img for img in video_data['images_data'] if img.get('image_id') != image_id]
            relationships = self._analyze_single_image_relationships(target_image, other_images)
            
            # 画像特化コンテキスト構築
            image_context = {
                "video_id": video_id,
                "image_id": image_id,
                "video_info": video_data['video_metadata'],
                "image_analysis": analysis_result,
                "image_metadata": target_image,
                "relationships": relationships,
                "context_in_video": self._determine_image_context_in_video(
                    target_image, video_data['video_metadata']
                ),
                "key_discussion_points": self._extract_image_discussion_points(analysis_result),
                "generation_timestamp": datetime.now().isoformat()
            }
            
            print(f"[コンテキスト] ✅ 画像特化コンテキスト構築完了")
            return image_context
            
        except Exception as e:
            print(f"[コンテキスト] ❌ 画像特化コンテキスト構築エラー: {e}")
            return {"error": str(e)}
    
    def create_conversation_context(self, video_id: str, query: str = None, template_type: str = "general_video_discussion") -> str:
        """
        会話用の最適化されたコンテキスト生成
        
        Args:
            video_id: YouTube動画ID
            query: ユーザーのクエリ（オプション）
            template_type: 使用するテンプレートタイプ
            
        Returns:
            会話用コンテキスト文字列
        """
        try:
            print(f"[コンテキスト] 💬 会話コンテキスト生成: {template_type}")
            
            # 包括的コンテキスト取得
            comprehensive_context = self.build_comprehensive_context(video_id)
            if "error" in comprehensive_context:
                return f"申し訳ありません。動画の情報が取得できませんでした。({comprehensive_context['error']})"
            
            # クエリ意図解析
            query_intent = self._analyze_query_intent(query) if query else "general"
            
            # テンプレート選択
            if query_intent != "general":
                template_type = self._select_template_by_intent(query_intent)
            
            # テンプレート適用
            conversation_text = self._apply_conversation_template(
                comprehensive_context, 
                template_type,
                query
            )
            
            print(f"[コンテキスト] ✅ 会話コンテキスト生成完了")
            return conversation_text
            
        except Exception as e:
            print(f"[コンテキスト] ❌ 会話コンテキスト生成エラー: {e}")
            return f"申し訳ありません。コンテキストの生成中にエラーが発生しました。({str(e)})"
    
    def _analyze_query_intent(self, query: str) -> str:
        """ユーザークエリの意図を分析"""
        try:
            if not query:
                return "general"
            
            query_lower = query.lower()
            
            # 意図パターンのマッピング
            intent_patterns = {
                "image_focus": [
                    "この画像", "画像について", "写真について", "スクリーンショット",
                    "シーンについて", "映像について", "見える", "写っている"
                ],
                "visual_analysis": [
                    "映像表現", "演出", "撮影", "カメラワーク", "構図", "色彩",
                    "ライティング", "エフェクト", "視覚的", "アート"
                ],
                "music_video_comprehensive": [
                    "楽曲", "音楽", "歌詞", "アーティスト", "パフォーマンス",
                    "歌って", "演奏", "ミュージック", "ビデオ"
                ],
                "mood_atmosphere": [
                    "雰囲気", "ムード", "感じ", "印象", "気持ち", "感情",
                    "暖かい", "冷たい", "明るい", "暗い", "優しい"
                ]
            }
            
            # パターンマッチング
            for intent, patterns in intent_patterns.items():
                if any(pattern in query_lower for pattern in patterns):
                    return intent
            
            return "general"
            
        except Exception as e:
            print(f"[コンテキスト] ❌ クエリ意図分析エラー: {e}")
            return "general"
    
    def _select_template_by_intent(self, intent: str) -> str:
        """意図に基づいてテンプレートを選択"""
        try:
            # 意図とテンプレートのマッピング
            intent_template_mapping = {
                "image_focus": "specific_image_focus",
                "visual_analysis": "visual_analysis",
                "music_video_comprehensive": "music_video_comprehensive",
                "mood_atmosphere": "visual_analysis",
                "general": "general_video_discussion"
            }
            
            return intent_template_mapping.get(intent, "general_video_discussion")
            
        except Exception as e:
            print(f"[コンテキスト] ❌ テンプレート選択エラー: {e}")
            return "general_video_discussion"
    
    def _apply_conversation_template(self, comprehensive_context: Dict, template_type: str, query: str = None) -> str:
        """会話テンプレートを適用してコンテキストを生成"""
        try:
            # テンプレート取得
            template = self.conversation_templates.get(template_type, self.conversation_templates["general_video_discussion"])
            
            # データ準備
            video_info = comprehensive_context.get('video_info', {})
            images_analysis = comprehensive_context.get('images_analysis', {})
            visual_narrative = comprehensive_context.get('visual_narrative', {})
            conversation_topics = comprehensive_context.get('conversation_topics', [])
            
            # テンプレート変数の構築
            template_vars = {
                # 基本情報
                'title': video_info.get('title', '楽曲'),
                'artist': video_info.get('channel_title', 'アーティスト'),
                'video_description': video_info.get('description', '魅力的な映像作品')[:100],
                
                # 画像分析結果
                'image_summaries': self._format_image_summaries(images_analysis),
                'visual_characteristics': self._format_visual_characteristics(images_analysis),
                'discussion_topics': self._format_discussion_topics(conversation_topics),
                
                # 視覚的ストーリー
                'narrative_flow': visual_narrative.get('story_flow', '映像展開'),
                'artistic_elements': self._format_artistic_elements(images_analysis),
                
                # 総合情報
                'context_summary': comprehensive_context.get('context_summary', ''),
                'video_mood': self._extract_overall_mood(images_analysis),
                'visual_highlights': self._format_visual_highlights(images_analysis),
                'production_points': self._format_production_points(images_analysis),
                'conversation_topics': self._format_conversation_topics_detailed(conversation_topics)
            }
            
            # 特定テンプレート用の追加変数
            if template_type == "specific_image_focus":
                template_vars.update({
                    'image_description': self._get_first_image_description(images_analysis),
                    'image_context_in_video': self._get_image_context_in_video(images_analysis, video_info),
                    'key_visual_elements': self._get_key_visual_elements(images_analysis)
                })
            
            # テンプレート適用
            conversation_text = template.format(**template_vars)
            
            # クエリ関連の補足情報追加
            if query and template_type != "simple_image_chat":
                conversation_text += f"\n\n【ユーザーの質問】\n{query}\n\nこの点について、どのように感じられましたか？"
            
            return conversation_text
            
        except Exception as e:
            print(f"[コンテキスト] ❌ テンプレート適用エラー: {e}")
            return f"「{video_info.get('title', '楽曲')}」について話しましょう。どんなことが気になりますか？"
    
    def _format_image_summaries(self, images_analysis: Dict) -> str:
        """画像サマリーのフォーマット"""
        try:
            summaries = images_analysis.get('image_summaries', [])
            if not summaries:
                return "画像の詳細情報はありませんが、映像の魅力について話しましょう。"
            
            formatted_summaries = []
            for i, summary in enumerate(summaries[:3], 1):  # 最大3つまで
                desc = summary.get('description', '画像の内容')
                formatted_summaries.append(f"• {desc}")
            
            return "\n".join(formatted_summaries)
            
        except Exception:
            return "映像から読み取れる印象的な要素について話しましょう。"
    
    def _format_visual_characteristics(self, images_analysis: Dict) -> str:
        """視覚的特徴のフォーマット"""
        try:
            themes = images_analysis.get('visual_themes', [])
            common_elements = images_analysis.get('common_elements', {})
            
            characteristics = []
            
            # 主要テーマ
            if themes:
                themes_text = "、".join(themes[:3])
                characteristics.append(f"主要テーマ: {themes_text}")
            
            # 共通要素
            if common_elements:
                top_elements = list(common_elements.keys())[:3]
                if top_elements:
                    elements_text = "、".join(top_elements)
                    characteristics.append(f"特徴的な要素: {elements_text}")
            
            # ムード進行
            mood_progression = images_analysis.get('mood_progression', [])
            if mood_progression:
                unique_moods = list(set(mood_progression))
                if len(unique_moods) == 1:
                    characteristics.append(f"一貫した{unique_moods[0]}な雰囲気")
                else:
                    characteristics.append(f"多様な雰囲気の変化({len(unique_moods)}パターン)")
            
            return "\n• ".join(characteristics) if characteristics else "多彩な視覚表現"
            
        except Exception:
            return "印象的な視覚的特徴"
    
    def _format_discussion_topics(self, topics: List[str]) -> str:
        """議論トピックのフォーマット"""
        try:
            if not topics:
                return "• 映像の印象について\n• 好きなシーンについて\n• 音楽と映像の関係について"
            
            formatted_topics = []
            for topic in topics[:4]:  # 最大4つまで
                formatted_topics.append(f"• {topic}")
            
            return "\n".join(formatted_topics)
            
        except Exception:
            return "• 映像について\n• 楽曲について"
    
    def _format_artistic_elements(self, images_analysis: Dict) -> str:
        """アーティスティック要素のフォーマット"""
        try:
            scene_types = images_analysis.get('scene_types', [])
            if not scene_types:
                return "創造的な映像表現"
            
            unique_scenes = list(set(scene_types))
            if len(unique_scenes) == 1:
                return f"{unique_scenes[0]}を中心とした演出"
            else:
                return f"多様な演出技法({len(unique_scenes)}種類のシーン構成)"
                
        except Exception:
            return "多彩な演出技法"
    
    def _extract_overall_mood(self, images_analysis: Dict) -> str:
        """全体的なムードの抽出"""
        try:
            mood_progression = images_analysis.get('mood_progression', [])
            if not mood_progression:
                return "魅力的な雰囲気"
            
            # 最も頻出するムードを特定
            from collections import Counter
            mood_counter = Counter(mood_progression)
            if mood_counter:
                dominant_mood = mood_counter.most_common(1)[0][0]
                return f"{dominant_mood}で印象的な雰囲気"
            
            return "多彩な雰囲気"
            
        except Exception:
            return "印象的な雰囲気"
    
    def _format_visual_highlights(self, images_analysis: Dict) -> str:
        """視覚的ハイライトのフォーマット"""
        try:
            common_elements = images_analysis.get('common_elements', {})
            if not common_elements:
                return "印象的な映像表現"
            
            highlights = []
            for element, count in list(common_elements.items())[:3]:
                if count > 1:
                    highlights.append(f"{element}の効果的な使用")
                else:
                    highlights.append(element)
            
            return "\n• ".join(highlights) if highlights else "多彩な視覚表現"
            
        except Exception:
            return "印象的な映像表現"
    
    def _format_production_points(self, images_analysis: Dict) -> str:
        """制作ポイントのフォーマット"""
        try:
            scene_types = images_analysis.get('scene_types', [])
            visual_themes = images_analysis.get('visual_themes', [])
            
            points = []
            
            # シーン構成
            if scene_types:
                unique_scenes = list(set(scene_types))
                if len(unique_scenes) > 1:
                    points.append(f"多様なシーン構成({len(unique_scenes)}種類)")
                else:
                    points.append(f"{unique_scenes[0]}中心の構成")
            
            # 視覚テーマ
            if visual_themes:
                themes_text = "、".join(visual_themes[:2])
                points.append(f"{themes_text}を活かした演出")
            
            # 総合的な制作アプローチ
            total_images = images_analysis.get('total_images', 0)
            if total_images > 0:
                points.append(f"詳細な映像構成({total_images}枚の画像解析)")
            
            return "\n• ".join(points) if points else "丁寧な映像制作"
            
        except Exception:
            return "印象的な制作技法"
    
    def _format_conversation_topics_detailed(self, topics: List[str]) -> str:
        """詳細な会話トピックのフォーマット"""
        try:
            if not topics:
                return "• 映像の印象について\n• 好きなシーンについて\n• 音楽と映像の関係について"
            
            formatted_topics = []
            for i, topic in enumerate(topics[:5], 1):
                formatted_topics.append(f"{i}. {topic}")
            
            return "\n".join(formatted_topics)
            
        except Exception:
            return "• 映像について\n• 楽曲について"
    
    def _get_first_image_description(self, images_analysis: Dict) -> str:
        """最初の画像の説明を取得"""
        try:
            summaries = images_analysis.get('image_summaries', [])
            if summaries:
                return summaries[0].get('description', '画像の内容')
            return "画像の内容"
            
        except Exception:
            return "画像の内容"
    
    def _get_image_context_in_video(self, images_analysis: Dict, video_info: Dict) -> str:
        """動画内での画像の文脈を取得"""
        try:
            title = video_info.get('title', '楽曲')
            total_images = images_analysis.get('total_images', 0)
            
            if total_images > 1:
                return f"「{title}」の映像の中で、特に印象的なシーンの一つ"
            else:
                return f"「{title}」の代表的なシーン"
                
        except Exception:
            return "動画の印象的な一場面"
    
    def _get_key_visual_elements(self, images_analysis: Dict) -> str:
        """キーとなる視覚要素を取得"""
        try:
            common_elements = images_analysis.get('common_elements', {})
            if common_elements:
                top_elements = list(common_elements.keys())[:3]
                return "\n• ".join(top_elements)
            
            return "印象的な視覚表現"
            
        except Exception:
            return "魅力的な視覚要素"
    
    def _collect_video_data(self, video_id: str) -> Optional[Dict[str, Any]]:
        """動画の基本情報収集"""
        try:
            # 動画メタデータ取得
            video_metadata = self.youtube_manager.get_video_context(video_id)
            if not video_metadata:
                return None
            
            # 画像データ取得
            images_data = self.youtube_manager.get_video_images(video_id)
            
            return {
                'video_metadata': video_metadata,
                'images_data': images_data
            }
            
        except Exception as e:
            print(f"[コンテキスト] ❌ 動画データ収集エラー: {e}")
            return None
    
    def _integrate_image_analyses(self, images_data: List[Dict]) -> Dict[str, Any]:
        """複数画像の分析結果を統合"""
        try:
            if not images_data:
                return {
                    "total_images": 0,
                    "analyzed_images": 0,
                    "image_summaries": [],
                    "common_elements": {},
                    "mood_progression": [],
                    "visual_themes": []
                }
            
            integrated = {
                "total_images": len(images_data),
                "analyzed_images": 0,
                "image_summaries": [],
                "common_elements": defaultdict(int),
                "mood_progression": [],
                "visual_themes": [],
                "scene_types": []
            }
            
            for image_data in images_data:
                # 分析結果確認
                if image_data.get('analysis_status') != 'completed':
                    continue
                
                analysis_result = self.youtube_manager.get_image_analysis_result(
                    image_data.get('video_id', ''), 
                    image_data.get('image_id', '')
                )
                
                if not analysis_result:
                    continue
                
                integrated["analyzed_images"] += 1
                
                # 画像サマリー作成
                summary = self._create_image_summary(image_data, analysis_result)
                integrated["image_summaries"].append(summary)
                
                # 共通要素抽出
                elements = self._extract_visual_elements_from_analysis(analysis_result)
                for element in elements:
                    integrated["common_elements"][element] += 1
                
                # ムード進行
                mood = self._extract_mood_from_analysis(analysis_result)
                if mood:
                    integrated["mood_progression"].append(mood)
                
                # シーンタイプ
                scene_type = self._classify_scene_type_from_analysis(analysis_result)
                if scene_type:
                    integrated["scene_types"].append(scene_type)
            
            # 共通要素を頻度順にソート
            integrated["common_elements"] = dict(
                sorted(integrated["common_elements"].items(), 
                       key=lambda x: x[1], reverse=True)
            )
            
            # 視覚テーマ抽出
            integrated["visual_themes"] = self._extract_visual_themes(integrated)
            
            return integrated
            
        except Exception as e:
            print(f"[コンテキスト] ❌ 画像分析統合エラー: {e}")
            return {"error": str(e)}
    
    def _create_image_summary(self, image_data: Dict, analysis_result: Dict) -> Dict[str, Any]:
        """個別画像のサマリー作成"""
        try:
            description = analysis_result.get('description', '')
            
            return {
                "image_id": image_data.get('image_id'),
                "description": description[:200] + "..." if len(description) > 200 else description,
                "upload_timestamp": image_data.get('upload_timestamp'),
                "user_description": image_data.get('user_description', ''),
                "analysis_confidence": "high"  # 今後改善予定
            }
            
        except Exception as e:
            print(f"[コンテキスト] ❌ 画像サマリー作成エラー: {e}")
            return {"image_id": image_data.get('image_id'), "error": str(e)}
    
    def _extract_visual_elements_from_analysis(self, analysis_result: Dict) -> List[str]:
        """分析結果から視覚要素を抽出"""
        elements = []
        description = analysis_result.get('description', '').lower()
        
        # 各カテゴリから要素を検索
        for category, keywords in self.visual_element_categories.items():
            for keyword in keywords:
                if keyword.lower() in description:
                    elements.append(keyword)
        
        return list(set(elements))  # 重複除去
    
    def _extract_mood_from_analysis(self, analysis_result: Dict) -> Optional[str]:
        """分析結果からムードを抽出"""
        description = analysis_result.get('description', '').lower()
        
        # ムードキーワードのマッピング
        mood_keywords = {
            "明るい": ["明るい", "楽しい", "元気", "ポジティブ", "華やか"],
            "落ち着いた": ["落ち着いた", "静か", "穏やか", "リラックス", "安らか"],
            "情熱的": ["情熱的", "熱い", "激しい", "エネルギッシュ", "力強い"],
            "ロマンチック": ["ロマンチック", "甘い", "優しい", "温かい", "愛らしい"],
            "ドラマチック": ["ドラマチック", "劇的", "感動的", "印象的", "強烈"]
        }
        
        for mood, keywords in mood_keywords.items():
            if any(keyword in description for keyword in keywords):
                return mood
        
        return None
    
    def _classify_scene_type_from_analysis(self, analysis_result: Dict) -> Optional[str]:
        """分析結果からシーンタイプを分類"""
        description = analysis_result.get('description', '').lower()
        
        for scene_category, scene_types in self.scene_classifications.items():
            for scene_type in scene_types:
                if scene_type.lower() in description:
                    return scene_type
        
        return None
    
    def _extract_visual_themes(self, integrated_data: Dict) -> List[str]:
        """統合データから視覚テーマを抽出"""
        themes = []
        
        # 共通要素から主要テーマを特定
        common_elements = integrated_data.get('common_elements', {})
        if len(common_elements) > 0:
            # 最も頻出する要素をテーマとして採用
            top_elements = list(common_elements.keys())[:3]
            themes.extend(top_elements)
        
        # ムード進行からテーマを抽出
        mood_progression = integrated_data.get('mood_progression', [])
        if mood_progression:
            mood_counter = Counter(mood_progression)
            dominant_mood = mood_counter.most_common(1)[0][0] if mood_counter else None
            if dominant_mood:
                themes.append(f"{dominant_mood}な雰囲気")
        
        # シーンタイプからテーマを抽出
        scene_types = integrated_data.get('scene_types', [])
        if scene_types:
            scene_counter = Counter(scene_types)
            dominant_scene = scene_counter.most_common(1)[0][0] if scene_counter else None
            if dominant_scene:
                themes.append(f"{dominant_scene}中心")
        
        return list(set(themes))  # 重複除去
    
    def _build_visual_narrative(self, images_analysis: Dict) -> Dict[str, Any]:
        """画像から視覚的ストーリーを構築"""
        try:
            image_summaries = images_analysis.get('image_summaries', [])
            if not image_summaries:
                return {"story_flow": "画像が不足しており、ストーリーを構築できません"}
            
            # ストーリーフロー推定
            story_flow = self._estimate_story_flow(image_summaries)
            
            # 繰り返しテーマ
            recurring_themes = images_analysis.get('visual_themes', [])
            
            # 視覚的進行
            visual_progression = self._analyze_visual_progression(images_analysis)
            
            # 物語アーク
            narrative_arc = self._generate_narrative_arc(story_flow, recurring_themes)
            
            return {
                "story_flow": story_flow,
                "recurring_themes": recurring_themes,
                "visual_progression": visual_progression,
                "narrative_arc": narrative_arc
            }
            
        except Exception as e:
            print(f"[コンテキスト] ❌ 視覚的ストーリー構築エラー: {e}")
            return {"error": str(e)}
    
    def _estimate_story_flow(self, image_summaries: List[Dict]) -> str:
        """画像から物語の流れを推定"""
        try:
            if len(image_summaries) == 1:
                return "単一シーンフォーカス"
            elif len(image_summaries) == 2:
                return "二部構成（導入→展開）"
            elif len(image_summaries) >= 3:
                return "三幕構成（導入→展開→クライマックス）"
            else:
                return "ストーリー構造不明"
                
        except Exception:
            return "ストーリーフロー分析エラー"
    
    def _analyze_visual_progression(self, images_analysis: Dict) -> str:
        """視覚的進行の分析"""
        try:
            mood_progression = images_analysis.get('mood_progression', [])
            
            if not mood_progression:
                return "進行パターン不明"
            
            if len(mood_progression) == 1:
                return f"一貫した{mood_progression[0]}な雰囲気"
            
            # ムードの変化パターンを分析
            if mood_progression[0] != mood_progression[-1]:
                return f"{mood_progression[0]}から{mood_progression[-1]}への変化"
            else:
                return f"全体的に{mood_progression[0]}な雰囲気を維持"
                
        except Exception:
            return "視覚的進行分析エラー"
    
    def _generate_narrative_arc(self, story_flow: str, themes: List[str]) -> str:
        """物語アークの生成"""
        try:
            if not themes:
                return f"{story_flow}の構造で展開"
            
            themes_text = "、".join(themes[:2])  # 上位2つのテーマを使用
            return f"{story_flow}の構造で、{themes_text}を中心とした物語展開"
            
        except Exception:
            return "物語アーク生成エラー"
    
    def _generate_discussion_topics(self, video_data: Dict, images_analysis: Dict) -> List[str]:
        """画像内容から会話トピックを自動生成"""
        try:
            topics = []
            
            # 動画情報から基本トピック
            video_metadata = video_data.get('video_metadata', {})
            if video_metadata:
                topics.append(f"「{video_metadata.get('title', '楽曲')}」の魅力について")
            
            # 共通要素からトピック生成
            common_elements = images_analysis.get('common_elements', {})
            for element, count in list(common_elements.items())[:3]:
                if count > 1:  # 複数の画像に登場する要素
                    topics.append(f"{element}の使い方や効果について")
            
            # ムードからトピック生成
            mood_progression = images_analysis.get('mood_progression', [])
            if mood_progression:
                unique_moods = list(set(mood_progression))
                if len(unique_moods) > 1:
                    topics.append("映像の雰囲気の変化について")
                else:
                    topics.append(f"{unique_moods[0]}な雰囲気の演出について")
            
            # シーンタイプからトピック生成
            scene_types = images_analysis.get('scene_types', [])
            if scene_types:
                unique_scenes = list(set(scene_types))
                for scene in unique_scenes[:2]:  # 上位2つ
                    topics.append(f"{scene}の表現技法について")
            
            # 最小限のトピック保証
            if not topics:
                topics = [
                    "映像の印象について",
                    "好きなシーンについて",
                    "音楽と映像の関係について"
                ]
            
            return topics[:5]  # 最大5つまで
            
        except Exception as e:
            print(f"[コンテキスト] ❌ 議論トピック生成エラー: {e}")
            return ["映像について", "楽曲について"]
    
    def _generate_context_summary(self, video_metadata: Dict, images_analysis: Dict, visual_narrative: Dict) -> str:
        """総合コンテキストサマリー生成"""
        try:
            title = video_metadata.get('title', '楽曲')
            artist = video_metadata.get('channel_title', 'アーティスト')
            
            # 画像数と分析状況
            total_images = images_analysis.get('total_images', 0)
            analyzed_images = images_analysis.get('analyzed_images', 0)
            
            # 主要テーマ
            themes = images_analysis.get('visual_themes', [])
            themes_text = "、".join(themes[:2]) if themes else "多様な表現"
            
            # ストーリー構造
            story_flow = visual_narrative.get('story_flow', '映像展開')
            
            # サマリー構築
            summary = f"{artist}の「{title}」は、{analyzed_images}枚の画像から分析すると、{themes_text}を特徴とした映像作品です。"
            
            if story_flow:
                summary += f" {story_flow}で構成されており、"
            
            # 視覚的進行
            visual_progression = visual_narrative.get('visual_progression', '')
            if visual_progression:
                summary += f"{visual_progression}が印象的です。"
            else:
                summary += "魅力的な映像表現が展開されています。"
            
            return summary
            
        except Exception as e:
            print(f"[コンテキスト] ❌ コンテキストサマリー生成エラー: {e}")
            return "この動画の映像について分析した内容をもとに会話しましょう。"
    
    def _analyze_single_image_relationships(self, target_image: Dict, other_images: List[Dict]) -> Dict[str, Any]:
        """単一画像と他画像との関係性分析"""
        try:
            if not other_images:
                return {"relationship_type": "single_image", "connections": []}
            
            relationships = {
                "total_other_images": len(other_images),
                "temporal_position": self._estimate_temporal_position(target_image, other_images),
                "thematic_connections": [],
                "visual_similarities": []
            }
            
            # 時間的位置の推定（アップロード時刻基準）
            target_time = target_image.get('upload_timestamp', '')
            if target_time:
                earlier_count = 0
                later_count = 0
                
                for other_img in other_images:
                    other_time = other_img.get('upload_timestamp', '')
                    if other_time:
                        if other_time < target_time:
                            earlier_count += 1
                        else:
                            later_count += 1
                
                if earlier_count == 0:
                    relationships["sequence_position"] = "最初"
                elif later_count == 0:
                    relationships["sequence_position"] = "最後"
                else:
                    relationships["sequence_position"] = "中間"
            
            return relationships
            
        except Exception as e:
            print(f"[コンテキスト] ❌ 画像関係性分析エラー: {e}")
            return {"error": str(e)}
    
    def _estimate_temporal_position(self, target_image: Dict, other_images: List[Dict]) -> str:
        """画像の時間的位置を推定"""
        # 簡易実装：アップロード順序から推定
        try:
            target_desc = target_image.get('user_description', '').lower()
            
            # キーワードベースの推定
            if any(keyword in target_desc for keyword in ['最初', '冒頭', 'イントロ', '始まり']):
                return "opening"
            elif any(keyword in target_desc for keyword in ['最後', '終わり', 'エンディング', '締め']):
                return "closing" 
            elif any(keyword in target_desc for keyword in ['サビ', 'クライマックス', '盛り上がり']):
                return "climax"
            else:
                return "middle"
                
        except Exception:
            return "unknown"
    
    def _determine_image_context_in_video(self, target_image: Dict, video_metadata: Dict) -> str:
        """動画全体における画像の文脈を決定"""
        try:
            title = video_metadata.get('title', '楽曲')
            user_desc = target_image.get('user_description', '')
            
            if user_desc:
                return f"「{title}」の{user_desc}として位置づけられるシーン"
            else:
                return f"「{title}」の一場面"
                
        except Exception:
            return "動画の一部として含まれるシーン"
    
    def _extract_image_discussion_points(self, analysis_result: Dict) -> List[str]:
        """画像分析結果から議論ポイントを抽出"""
        try:
            points = []
            description = analysis_result.get('description', '')
            
            # 長い説明から重要なポイントを抽出
            if len(description) > 100:
                # 文を分割して重要そうな文を抽出
                sentences = description.split('。')
                for sentence in sentences[:3]:  # 最初の3文
                    if len(sentence.strip()) > 10:
                        points.append(sentence.strip() + "。")
            else:
                points.append(description)
            
            # 最小限のポイント保証
            if not points:
                points = ["この画像の内容について", "印象的な要素について"]
            
            return points[:3]  # 最大3つまで
            
        except Exception as e:
            print(f"[コンテキスト] ❌ 議論ポイント抽出エラー: {e}")
            return ["この画像について"]
    
    def analyze_advanced_image_relationships(self, video_id: str) -> Dict[str, Any]:
        """
        高度な画像関連性分析
        画像間の時間的・空間的・テーマ的関係性を詳細分析
        
        Args:
            video_id: YouTube動画ID
            
        Returns:
            高度な関連性分析結果
        """
        try:
            print(f"[コンテキスト] 🔍 高度な関連性分析開始: {video_id}")
            
            # 基本データ収集
            video_data = self._collect_video_data(video_id)
            if not video_data:
                return {"error": "動画データが見つかりません"}
            
            images_data = video_data['images_data']
            if len(images_data) < 2:
                return {
                    "relationship_type": "single_image",
                    "message": "関連性分析には複数の画像が必要です"
                }
            
            # Step 1: 時間的関係性分析
            temporal_analysis = self._analyze_temporal_relationships(images_data)
            
            # Step 2: 視覚的類似性分析
            visual_similarity = self._analyze_visual_similarities(images_data, video_id)
            
            # Step 3: テーマ的関連性分析
            thematic_relationships = self._analyze_thematic_relationships(images_data, video_id)
            
            # Step 4: 空間的・構図関連性分析
            spatial_analysis = self._analyze_spatial_relationships(images_data, video_id)
            
            # Step 5: 楽曲構造との対応分析
            musical_correspondence = self._analyze_musical_correspondence(images_data, video_data['video_metadata'])
            
            # Step 6: 感情・ムード遷移分析
            emotional_flow = self._analyze_emotional_flow(images_data, video_id)
            
            # Step 7: 統合関連性マトリクス生成
            relationship_matrix = self._generate_relationship_matrix(images_data, {
                'temporal': temporal_analysis,
                'visual': visual_similarity,
                'thematic': thematic_relationships,
                'spatial': spatial_analysis,
                'musical': musical_correspondence,
                'emotional': emotional_flow
            })
            
            # 結果統合
            advanced_analysis = {
                "video_id": video_id,
                "total_images": len(images_data),
                "analysis_timestamp": datetime.now().isoformat(),
                "temporal_analysis": temporal_analysis,
                "visual_similarity": visual_similarity,
                "thematic_relationships": thematic_relationships,
                "spatial_analysis": spatial_analysis,
                "musical_correspondence": musical_correspondence,
                "emotional_flow": emotional_flow,
                "relationship_matrix": relationship_matrix,
                "overall_coherence_score": self._calculate_overall_coherence(relationship_matrix),
                "narrative_structure": self._identify_narrative_structure(relationship_matrix),
                "key_transitions": self._identify_key_transitions(relationship_matrix)
            }
            
            print(f"[コンテキスト] ✅ 高度な関連性分析完了")
            return advanced_analysis
            
        except Exception as e:
            print(f"[コンテキスト] ❌ 高度な関連性分析エラー: {e}")
            return {"error": str(e)}
    
    def _analyze_temporal_relationships(self, images_data: List[Dict]) -> Dict[str, Any]:
        """時間的関係性の詳細分析"""
        try:
            sorted_images = sorted(images_data, key=lambda x: x.get('upload_timestamp', ''))
            
            temporal_analysis = {
                "sequence_length": len(sorted_images),
                "time_spans": [],
                "sequence_patterns": [],
                "temporal_clusters": []
            }
            
            # 時間間隔分析
            for i in range(len(sorted_images) - 1):
                current_time = sorted_images[i].get('upload_timestamp', '')
                next_time = sorted_images[i + 1].get('upload_timestamp', '')
                
                if current_time and next_time:
                    # 簡易的な時間差計算（実際の実装では datetime パースが必要）
                    temporal_analysis["time_spans"].append({
                        "from_image": sorted_images[i].get('image_id'),
                        "to_image": sorted_images[i + 1].get('image_id'),
                        "interval_type": "sequential"
                    })
            
            # シーケンスパターン識別
            if len(sorted_images) >= 3:
                temporal_analysis["sequence_patterns"] = [
                    "beginning_middle_end",
                    "chronological_progression"
                ]
            elif len(sorted_images) == 2:
                temporal_analysis["sequence_patterns"] = ["before_after"]
            
            return temporal_analysis
            
        except Exception as e:
            print(f"[コンテキスト] ❌ 時間的関係性分析エラー: {e}")
            return {"error": str(e)}
    
    def _analyze_visual_similarities(self, images_data: List[Dict], video_id: str) -> Dict[str, Any]:
        """視覚的類似性の詳細分析"""
        try:
            similarity_analysis = {
                "similarity_pairs": [],
                "visual_clusters": [],
                "common_visual_themes": [],
                "style_consistency": "high"  # 簡易実装
            }
            
            # 画像ペアの類似性分析
            for i in range(len(images_data)):
                for j in range(i + 1, len(images_data)):
                    img1 = images_data[i]
                    img2 = images_data[j]
                    
                    # 分析結果取得
                    analysis1 = self.youtube_manager.get_image_analysis_result(video_id, img1.get('image_id', '')) if self.youtube_manager else None
                    analysis2 = self.youtube_manager.get_image_analysis_result(video_id, img2.get('image_id', '')) if self.youtube_manager else None
                    
                    if analysis1 and analysis2:
                        similarity_score = self._calculate_description_similarity(
                            analysis1.get('description', ''),
                            analysis2.get('description', '')
                        )
                        
                        similarity_analysis["similarity_pairs"].append({
                            "image1_id": img1.get('image_id'),
                            "image2_id": img2.get('image_id'),
                            "similarity_score": similarity_score,
                            "similarity_type": self._classify_similarity_type(analysis1, analysis2)
                        })
            
            # 視覚的クラスタリング
            high_similarity_pairs = [
                pair for pair in similarity_analysis["similarity_pairs"]
                if pair["similarity_score"] > 0.7
            ]
            
            if high_similarity_pairs:
                similarity_analysis["visual_clusters"] = self._form_visual_clusters(high_similarity_pairs)
            
            return similarity_analysis
            
        except Exception as e:
            print(f"[コンテキスト] ❌ 視覚的類似性分析エラー: {e}")
            return {"error": str(e)}
    
    def _analyze_thematic_relationships(self, images_data: List[Dict], video_id: str) -> Dict[str, Any]:
        """テーマ的関連性の詳細分析"""
        try:
            thematic_analysis = {
                "dominant_themes": [],
                "theme_evolution": [],
                "thematic_consistency": 0.0,
                "cross_image_themes": []
            }
            
            all_themes = []
            image_themes = {}
            
            # 各画像のテーマ抽出
            for img_data in images_data:
                image_id = img_data.get('image_id')
                analysis_result = self.youtube_manager.get_image_analysis_result(video_id, image_id) if self.youtube_manager else None
                
                if analysis_result:
                    themes = self._extract_themes_from_analysis(analysis_result)
                    image_themes[image_id] = themes
                    all_themes.extend(themes)
            
            # テーマ頻度分析
            theme_counter = Counter(all_themes)
            thematic_analysis["dominant_themes"] = [
                {"theme": theme, "frequency": count}
                for theme, count in theme_counter.most_common(5)
            ]
            
            # テーマ進化パターン
            if len(image_themes) >= 2:
                theme_sequence = []
                for img_data in sorted(images_data, key=lambda x: x.get('upload_timestamp', '')):
                    img_id = img_data.get('image_id')
                    if img_id in image_themes:
                        theme_sequence.append(image_themes[img_id])
                
                thematic_analysis["theme_evolution"] = self._analyze_theme_sequence(theme_sequence)
            
            # テーマ一貫性計算
            if theme_counter:
                total_themes = sum(theme_counter.values())
                max_frequency = max(theme_counter.values())
                thematic_analysis["thematic_consistency"] = max_frequency / total_themes
            
            # 画像間共通テーマ
            if len(image_themes) > 1:
                thematic_analysis["cross_image_themes"] = self._find_cross_image_themes(image_themes)
            
            return thematic_analysis
            
        except Exception as e:
            print(f"[コンテキスト] ❌ テーマ的関連性分析エラー: {e}")
            return {"error": str(e)}
    
    def _analyze_spatial_relationships(self, images_data: List[Dict], video_id: str) -> Dict[str, Any]:
        """空間的・構図関連性分析"""
        try:
            spatial_analysis = {
                "composition_patterns": [],
                "spatial_continuity": 0.0,
                "camera_movement_inference": [],
                "framing_analysis": []
            }
            
            # 各画像の空間的特徴抽出
            spatial_features = []
            for img_data in images_data:
                image_id = img_data.get('image_id')
                analysis_result = self.youtube_manager.get_image_analysis_result(video_id, image_id) if self.youtube_manager else None
                
                if analysis_result:
                    spatial_feature = self._extract_spatial_features(analysis_result)
                    spatial_features.append({
                        "image_id": image_id,
                        "features": spatial_feature
                    })
            
            # 構図パターン分析
            if spatial_features:
                composition_types = [f["features"].get("composition_type", "unknown") for f in spatial_features]
                spatial_analysis["composition_patterns"] = list(set(composition_types))
            
            # 空間的連続性計算
            if len(spatial_features) > 1:
                continuity_scores = []
                for i in range(len(spatial_features) - 1):
                    score = self._calculate_spatial_continuity(
                        spatial_features[i]["features"],
                        spatial_features[i + 1]["features"]
                    )
                    continuity_scores.append(score)
                
                spatial_analysis["spatial_continuity"] = sum(continuity_scores) / len(continuity_scores)
            
            # カメラワーク推論
            spatial_analysis["camera_movement_inference"] = self._infer_camera_movements(spatial_features)
            
            return spatial_analysis
            
        except Exception as e:
            print(f"[コンテキスト] ❌ 空間的関連性分析エラー: {e}")
            return {"error": str(e)}
    
    def _analyze_musical_correspondence(self, images_data: List[Dict], video_metadata: Dict) -> Dict[str, Any]:
        """楽曲構造との対応分析"""
        try:
            musical_analysis = {
                "song_structure_mapping": [],
                "tempo_visual_correlation": "moderate",
                "lyrical_visual_alignment": [],
                "musical_narrative_sync": 0.0
            }
            
            # 楽曲情報から構造推定
            title = video_metadata.get('title', '')
            description = video_metadata.get('description', '')
            
            # 楽曲構造パターンの推定
            estimated_structure = self._estimate_song_structure(title, description, len(images_data))
            musical_analysis["song_structure_mapping"] = estimated_structure
            
            # 画像と楽曲部分の対応
            if len(images_data) >= 2:
                for i, img_data in enumerate(images_data):
                    structure_part = self._map_image_to_song_part(i, len(images_data), estimated_structure)
                    musical_analysis["lyrical_visual_alignment"].append({
                        "image_id": img_data.get('image_id'),
                        "song_part": structure_part,
                        "position_ratio": i / (len(images_data) - 1) if len(images_data) > 1 else 0
                    })
            
            # 音楽ナラティブ同期度計算
            if musical_analysis["lyrical_visual_alignment"]:
                musical_analysis["musical_narrative_sync"] = self._calculate_narrative_sync(
                    musical_analysis["lyrical_visual_alignment"]
                )
            
            return musical_analysis
            
        except Exception as e:
            print(f"[コンテキスト] ❌ 楽曲対応分析エラー: {e}")
            return {"error": str(e)}
    
    def _analyze_emotional_flow(self, images_data: List[Dict], video_id: str) -> Dict[str, Any]:
        """感情・ムード遷移分析"""
        try:
            emotional_analysis = {
                "emotion_sequence": [],
                "mood_transitions": [],
                "emotional_arc": "",
                "emotional_intensity_curve": []
            }
            
            # 各画像の感情分析
            emotions = []
            for img_data in sorted(images_data, key=lambda x: x.get('upload_timestamp', '')):
                image_id = img_data.get('image_id')
                analysis_result = self.youtube_manager.get_image_analysis_result(video_id, image_id) if self.youtube_manager else None
                
                if analysis_result:
                    emotion = self._extract_emotion_from_analysis(analysis_result)
                    intensity = self._calculate_emotional_intensity(analysis_result)
                    
                    emotions.append({
                        "image_id": image_id,
                        "emotion": emotion,
                        "intensity": intensity
                    })
            
            emotional_analysis["emotion_sequence"] = emotions
            
            # ムード遷移分析
            if len(emotions) > 1:
                for i in range(len(emotions) - 1):
                    transition = {
                        "from_emotion": emotions[i]["emotion"],
                        "to_emotion": emotions[i + 1]["emotion"],
                        "transition_type": self._classify_mood_transition(
                            emotions[i]["emotion"],
                            emotions[i + 1]["emotion"]
                        )
                    }
                    emotional_analysis["mood_transitions"].append(transition)
            
            # 感情アーク特定
            emotional_analysis["emotional_arc"] = self._identify_emotional_arc(emotions)
            
            # 感情強度カーブ
            emotional_analysis["emotional_intensity_curve"] = [
                e["intensity"] for e in emotions
            ]
            
            return emotional_analysis
            
        except Exception as e:
            print(f"[コンテキスト] ❌ 感情フロー分析エラー: {e}")
            return {"error": str(e)}
    
    def _generate_relationship_matrix(self, images_data: List[Dict], analysis_results: Dict) -> Dict[str, Any]:
        """関連性マトリクス生成"""
        try:
            num_images = len(images_data)
            matrix = {
                "size": num_images,
                "image_ids": [img.get('image_id') for img in images_data],
                "relationships": []
            }
            
            # 全ペア組み合わせの関連性スコア計算
            for i in range(num_images):
                for j in range(i + 1, num_images):
                    img1_id = images_data[i].get('image_id')
                    img2_id = images_data[j].get('image_id')
                    
                    # 各次元での関連性スコア計算
                    temporal_score = self._get_temporal_score(i, j, analysis_results.get('temporal', {}))
                    visual_score = self._get_visual_score(img1_id, img2_id, analysis_results.get('visual', {}))
                    thematic_score = self._get_thematic_score(img1_id, img2_id, analysis_results.get('thematic', {}))
                    spatial_score = self._get_spatial_score(i, j, analysis_results.get('spatial', {}))
                    emotional_score = self._get_emotional_score(i, j, analysis_results.get('emotional', {}))
                    
                    # 総合関連性スコア
                    overall_score = (temporal_score + visual_score + thematic_score + spatial_score + emotional_score) / 5
                    
                    matrix["relationships"].append({
                        "image1_id": img1_id,
                        "image2_id": img2_id,
                        "temporal_score": temporal_score,
                        "visual_score": visual_score,
                        "thematic_score": thematic_score,
                        "spatial_score": spatial_score,
                        "emotional_score": emotional_score,
                        "overall_score": overall_score,
                        "relationship_strength": "strong" if overall_score > 0.7 else "moderate" if overall_score > 0.4 else "weak"
                    })
            
            return matrix
            
        except Exception as e:
            print(f"[コンテキスト] ❌ 関連性マトリクス生成エラー: {e}")
            return {"error": str(e)}
    
    # ヘルパーメソッド群
    def _calculate_description_similarity(self, desc1: str, desc2: str) -> float:
        """説明文の類似度計算（簡易実装）"""
        try:
            words1 = set(desc1.lower().split())
            words2 = set(desc2.lower().split())
            
            if not words1 or not words2:
                return 0.0
            
            intersection = len(words1.intersection(words2))
            union = len(words1.union(words2))
            
            return intersection / union if union > 0 else 0.0
        except Exception:
            return 0.0
    
    def _classify_similarity_type(self, analysis1: Dict, analysis2: Dict) -> str:
        """類似性タイプの分類"""
        try:
            desc1 = analysis1.get('description', '').lower()
            desc2 = analysis2.get('description', '').lower()
            
            # キーワードベースの類似性分類
            if any(word in desc1 and word in desc2 for word in ['人物', 'アーティスト', '歌', '演奏']):
                return "人物・パフォーマンス類似"
            elif any(word in desc1 and word in desc2 for word in ['背景', '環境', '場所', 'セット']):
                return "環境・背景類似"
            elif any(word in desc1 and word in desc2 for word in ['色', '照明', '雰囲気', 'ライト']):
                return "視覚効果類似"
            else:
                return "一般的類似"
        except Exception:
            return "不明"
    
    def _extract_themes_from_analysis(self, analysis_result: Dict) -> List[str]:
        """分析結果からテーマを抽出"""
        try:
            description = analysis_result.get('description', '').lower()
            themes = []
            
            # テーマキーワードマッピング
            theme_keywords = {
                '音楽': ['音楽', '楽器', '演奏', '歌', 'マイク', 'ギター', 'ピアノ', 'ドラム'],
                'パフォーマンス': ['パフォーマンス', 'ライブ', 'ステージ', '観客', 'コンサート'],
                '照明・映像': ['照明', 'ライト', 'エフェクト', '映像', 'カメラ'],
                '人物・表情': ['人物', 'アーティスト', '表情', '感情', '笑顔'],
                '環境・背景': ['背景', '環境', '場所', 'セット', 'スタジオ']
            }
            
            for theme, keywords in theme_keywords.items():
                if any(keyword in description for keyword in keywords):
                    themes.append(theme)
            
            return themes if themes else ['一般']
        except Exception:
            return ['一般']
    
    def _extract_emotion_from_analysis(self, analysis_result: Dict) -> str:
        """分析結果から感情を抽出"""
        try:
            description = analysis_result.get('description', '').lower()
            
            # 感情キーワードマッピング
            emotion_keywords = {
                '喜び': ['明るい', '楽しい', '嬉しい', '笑顔', 'ポジティブ', 'エネルギッシュ'],
                '情熱': ['情熱的', '熱い', '激しい', '力強い', 'パワフル'],
                '落ち着き': ['落ち着いた', '静か', '穏やか', 'リラックス', '安らか'],
                '感動': ['感動的', '美しい', '印象的', '心に響く', '素晴らしい'],
                '神秘': ['神秘的', '幻想的', '不思議', 'ミステリアス']
            }
            
            for emotion, keywords in emotion_keywords.items():
                if any(keyword in description for keyword in keywords):
                    return emotion
            
            return '中性'
        except Exception:
            return '中性'
    
    def _calculate_emotional_intensity(self, analysis_result: Dict) -> float:
        """感情強度の計算"""
        try:
            description = analysis_result.get('description', '').lower()
            
            # 強度キーワード
            high_intensity = ['非常に', '極めて', '強烈', '圧倒的', '激しく']
            medium_intensity = ['やや', 'そこそこ', '適度に', 'ほどよく']
            
            if any(word in description for word in high_intensity):
                return 0.9
            elif any(word in description for word in medium_intensity):
                return 0.6
            else:
                return 0.5  # デフォルト中程度
        except Exception:
            return 0.5
    
    def _calculate_overall_coherence(self, relationship_matrix: Dict) -> float:
        """全体的一貫性スコア計算"""
        try:
            relationships = relationship_matrix.get('relationships', [])
            if not relationships:
                return 0.0
            
            overall_scores = [r['overall_score'] for r in relationships]
            return sum(overall_scores) / len(overall_scores)
        except Exception:
            return 0.0
    
    def _identify_narrative_structure(self, relationship_matrix: Dict) -> str:
        """物語構造の特定"""
        try:
            coherence = self._calculate_overall_coherence(relationship_matrix)
            size = relationship_matrix.get('size', 0)
            
            if coherence > 0.8:
                return "高い一貫性を持つ統合的ナラティブ"
            elif coherence > 0.6:
                if size >= 3:
                    return "明確な三幕構成"
                else:
                    return "二部構成の展開"
            elif coherence > 0.4:
                return "緩やかな関連性を持つエピソード構成"
            else:
                return "独立したシーン集合"
        except Exception:
            return "構造分析不可"
    
    def _identify_key_transitions(self, relationship_matrix: Dict) -> List[Dict]:
        """重要な転換点の特定"""
        try:
            relationships = relationship_matrix.get('relationships', [])
            if len(relationships) < 2:
                return []
            
            # 関連性スコアの変化が大きい箇所を転換点とする
            transitions = []
            for i, rel in enumerate(relationships[:-1]):
                current_score = rel['overall_score']
                next_score = relationships[i + 1]['overall_score']
                
                score_change = abs(next_score - current_score)
                if score_change > 0.3:  # 閾値
                    transitions.append({
                        "transition_point": i + 1,
                        "from_image": rel['image1_id'],
                        "to_image": rel['image2_id'],
                        "change_magnitude": score_change,
                        "transition_type": "dramatic_shift" if score_change > 0.5 else "moderate_shift"
                    })
            
            return transitions[:3]  # 最大3つまで
        except Exception:
            return []
    
    # 簡易ヘルパーメソッド群（実装を簡略化）
    def _form_visual_clusters(self, pairs): return []
    def _analyze_theme_sequence(self, sequence): return []
    def _find_cross_image_themes(self, themes): return []
    def _extract_spatial_features(self, analysis): return {"composition_type": "center"}
    def _calculate_spatial_continuity(self, f1, f2): return 0.5
    def _infer_camera_movements(self, features): return []
    def _estimate_song_structure(self, title, desc, num_images): return ["intro", "verse", "chorus"]
    def _map_image_to_song_part(self, index, total, structure): return structure[min(index, len(structure)-1)]
    def _calculate_narrative_sync(self, alignment): return 0.7
    def _classify_mood_transition(self, e1, e2): return "gradual" if e1 == e2 else "contrast"
    def _identify_emotional_arc(self, emotions): return "上昇型" if len(emotions) > 1 else "安定型"
    def _get_temporal_score(self, i, j, temporal): return abs(i - j) / 10
    def _get_visual_score(self, id1, id2, visual): return 0.6
    def _get_thematic_score(self, id1, id2, thematic): return 0.7
    def _get_spatial_score(self, i, j, spatial): return 0.5
    def _get_emotional_score(self, i, j, emotional): return 0.6


def test_video_image_context_builder():
    """VideoImageContextBuilderの基本動作テスト"""
    print("=== VideoImageContextBuilder テスト開始 ===")
    
    try:
        # 初期化
        context_builder = VideoImageContextBuilder()
        print("✅ VideoImageContextBuilder初期化成功")
        
        # テンプレート確認
        templates = context_builder.conversation_templates
        print(f"✅ 会話テンプレート数: {len(templates)}")
        
        # カテゴリ確認
        scene_categories = context_builder.scene_classifications
        visual_categories = context_builder.visual_element_categories
        print(f"✅ シーンカテゴリ数: {len(scene_categories)}")
        print(f"✅ 視覚要素カテゴリ数: {len(visual_categories)}")
        
        print("✅ VideoImageContextBuilder基本機能正常")
        return True
        
    except Exception as e:
        print(f"❌ VideoImageContextBuilderテスト失敗: {e}")
        return False


if __name__ == "__main__":
    test_video_image_context_builder()
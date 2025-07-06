#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
画像分析エンジン - OpenAI Vision API統合
動画関連画像の自動分析・理解システム
"""

import base64
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
import requests
from PIL import Image
import openai
from openai import OpenAI
from dotenv import load_dotenv

# 環境変数読み込み
load_dotenv()


class ImageAnalyzer:
    """OpenAI Vision APIを使用した画像分析エンジン"""
    
    def __init__(self, model="gpt-4o"):
        """
        初期化
        
        Args:
            model: 使用するOpenAIモデル（Vision対応）
        """
        # OpenAI API設定
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY が設定されていません。.envファイルを確認してください。")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        
        # 設定パラメータ
        self.max_image_size = (1024, 1024)  # コスト最適化用
        self.default_max_tokens = 500
        self.default_temperature = 0.7
        
        # 分析プロンプトテンプレート
        self.analysis_prompts = self._load_analysis_prompts()
        
        # 統計情報
        self.analysis_stats = {
            'total_analyses': 0,
            'total_cost': 0.0,
            'total_tokens': 0,
            'last_analysis': None
        }
        
        print("[画像分析] ✅ ImageAnalyzer初期化完了")
    
    def _load_analysis_prompts(self) -> Dict[str, str]:
        """分析用プロンプトテンプレートを読み込み"""
        return {
            "general_description": """この画像について、以下の観点から詳しく分析してください：

【分析項目】
1. 全体的な内容・シーン
2. 主要な要素（人物、オブジェクト、テキストなど）
3. 色彩・雰囲気・スタイル
4. 注目すべき詳細・特徴

【出力形式】
自然で分かりやすい日本語で、詳細かつ簡潔に説明してください。""",

            "general_with_context": """この画像について、以下の観点から詳しく分析してください：

【分析項目】
1. 全体的な内容・シーン
2. 主要な要素（人物、オブジェクト、テキストなど）
3. 色彩・雰囲気・スタイル
4. 注目すべき詳細・特徴

【動画コンテキスト】
{video_context}

【出力形式】
自然で分かりやすい日本語で、詳細かつ簡潔に説明してください。""",

            "music_video_analysis": """この音楽動画のスクリーンショットを分析してください：

【分析項目】
1. 映像のスタイル・演出技法
2. 出演者・パフォーマンス内容
3. セット・背景・衣装デザイン
4. 画面に表示されている歌詞やテキスト
5. 楽曲の雰囲気との関連性

【楽曲情報】
タイトル: {title}
アーティスト: {artist}
概要: {description}

【出力形式】
音楽動画として魅力的な点を中心に、日本語で詳しく説明してください。""",

            "scene_elements": """画像内の要素を以下の形式で構造化して抽出してください：

【抽出項目】
- 人物: [人数、性別、年齢層、表情、動作、服装]
- オブジェクト: [楽器、小道具、装飾、家具など]
- 環境: [場所、時間帯、天候、照明、雰囲気]
- テキスト: [歌詞、字幕、看板、ロゴなど]
- 技術的要素: [カメラアングル、構図、エフェクト]

各項目について、見えるものを具体的にリストアップしてください。""",

            "text_extraction": """この画像に含まれているテキスト内容をすべて抽出してください：

【抽出対象】
- 歌詞・字幕
- タイトル・クレジット
- 看板・ロゴ
- その他すべての文字情報

【出力形式】
抽出したテキストを元の位置・文脈と共に整理して報告してください。""",

            "mood_atmosphere": """この画像の雰囲気・ムードを分析してください：

【分析項目】
1. 色彩の印象（暖色・寒色、明度、彩度）
2. 構図・空間の使い方
3. 光の使い方・影の効果
4. 全体的な感情・雰囲気
5. 視聴者に与える印象

【出力形式】
感性的な要素も含めて、詳しく説明してください。"""
        }
    
    def _resize_image_for_api(self, image_path: str) -> str:
        """
        API送信用に画像サイズを最適化
        
        Args:
            image_path: 元画像のパス
            
        Returns:
            最適化された画像のパス
        """
        try:
            with Image.open(image_path) as img:
                # すでに適切なサイズの場合はそのまま返す
                if img.size[0] <= self.max_image_size[0] and img.size[1] <= self.max_image_size[1]:
                    return image_path
                
                # リサイズが必要な場合
                import tempfile
                import uuid
                
                # 一時ファイル作成
                temp_dir = Path(tempfile.gettempdir()) / "setsuna_bot_analysis"
                temp_dir.mkdir(exist_ok=True)
                
                unique_id = str(uuid.uuid4())[:8]
                temp_filename = f"resized_{unique_id}.jpg"
                temp_path = temp_dir / temp_filename
                
                # アスペクト比を保持してリサイズ
                img_copy = img.copy()
                img_copy.thumbnail(self.max_image_size, Image.LANCZOS)
                
                # RGB形式に変換（JPEG保存のため）
                if img_copy.mode in ('RGBA', 'LA', 'P'):
                    background = Image.new('RGB', img_copy.size, (255, 255, 255))
                    if img_copy.mode == 'P':
                        img_copy = img_copy.convert('RGBA')
                    background.paste(img_copy, mask=img_copy.split()[-1] if 'A' in img_copy.mode else None)
                    img_copy = background
                
                # JPEG形式で保存
                img_copy.save(temp_path, 'JPEG', quality=85)
                
                print(f"[画像分析] 📏 画像リサイズ: {img.size} → {img_copy.size}")
                return str(temp_path)
                
        except Exception as e:
            print(f"[画像分析] ❌ 画像リサイズエラー: {e}")
            return image_path  # エラー時は元画像を返す
    
    def _encode_image_to_base64(self, image_path: str) -> str:
        """
        画像をBase64エンコード
        
        Args:
            image_path: 画像ファイルのパス
            
        Returns:
            Base64エンコードされた画像データ
        """
        try:
            with open(image_path, 'rb') as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
                return encoded_image
        except Exception as e:
            print(f"[画像分析] ❌ Base64エンコードエラー: {e}")
            raise
    
    def _call_vision_api(self, prompt: str, image_path: str, max_tokens: int = None, temperature: float = None) -> Dict[str, Any]:
        """
        OpenAI Vision APIを呼び出し
        
        Args:
            prompt: 分析用プロンプト
            image_path: 画像ファイルのパス
            max_tokens: 最大トークン数
            temperature: 温度パラメータ
            
        Returns:
            API応答と統計情報
        """
        try:
            # パラメータのデフォルト値設定
            max_tokens = max_tokens or self.default_max_tokens
            temperature = temperature or self.default_temperature
            
            # 画像の最適化
            optimized_image_path = self._resize_image_for_api(image_path)
            
            # 画像をBase64エンコード
            base64_image = self._encode_image_to_base64(optimized_image_path)
            
            # API呼び出し
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                    "detail": "high"  # 高品質分析
                                }
                            }
                        ]
                    }
                ],
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            end_time = time.time()
            
            # レスポンス解析
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            
            # コスト概算計算（GPT-4o Vision概算）
            estimated_cost = self._estimate_cost(tokens_used, has_image=True)
            
            # 統計更新
            self.analysis_stats['total_analyses'] += 1
            self.analysis_stats['total_cost'] += estimated_cost
            self.analysis_stats['total_tokens'] += tokens_used
            self.analysis_stats['last_analysis'] = datetime.now().isoformat()
            
            print(f"[画像分析] ✅ API呼び出し成功: {tokens_used}トークン, ${estimated_cost:.4f}")
            
            # 一時ファイル削除
            if optimized_image_path != image_path:
                try:
                    os.unlink(optimized_image_path)
                except:
                    pass
            
            return {
                'content': content,
                'tokens_used': tokens_used,
                'estimated_cost': estimated_cost,
                'processing_time': end_time - start_time,
                'model': self.model,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"[画像分析] ❌ Vision API呼び出しエラー: {e}")
            raise
    
    def _estimate_cost(self, tokens: int, has_image: bool = False) -> float:
        """
        API使用コストを概算
        
        Args:
            tokens: 使用トークン数
            has_image: 画像が含まれているか
            
        Returns:
            推定コスト（USD）
        """
        # GPT-4o料金（2024年時点の概算）
        text_cost_per_1k_tokens = 0.005  # $0.005 per 1K tokens
        image_base_cost = 0.01  # 画像1枚あたりの基本コスト
        
        text_cost = (tokens / 1000) * text_cost_per_1k_tokens
        image_cost = image_base_cost if has_image else 0
        
        return text_cost + image_cost
    
    def _safe_format_prompt(self, prompt_template: str, context: Dict[str, Any]) -> str:
        """
        プロンプトテンプレートを安全にフォーマット
        不足しているキーを自動的にデフォルト値で補完
        
        Args:
            prompt_template: フォーマット対象のプロンプトテンプレート
            context: コンテキスト辞書
            
        Returns:
            フォーマット済みプロンプト
        """
        try:
            import string
            import re
            
            # プロンプトテンプレート内の全てのプレースホルダーを抽出
            formatter = string.Formatter()
            placeholders = set()
            
            try:
                for literal_text, field_name, format_spec, conversion in formatter.parse(prompt_template):
                    if field_name:
                        placeholders.add(field_name)
            except Exception as e:
                print(f"[画像分析] ⚠️ プロンプト解析エラー: {e}")
                # フォールバック: 正規表現で{key}形式のプレースホルダーを抽出
                placeholders = set(re.findall(r'\{([^}]+)\}', prompt_template))
            
            # デフォルト値を設定
            default_values = {
                'video_context': '情報なし',
                'title': '不明',
                'artist': '不明',
                'description': '情報なし',
                'channel_title': '不明',
                'published_at': '不明',
                'view_count': '不明'
            }
            
            # 不足しているキーをデフォルト値で補完
            safe_context = context.copy()
            for placeholder in placeholders:
                if placeholder not in safe_context:
                    safe_context[placeholder] = default_values.get(placeholder, f'[{placeholder}]')
                    print(f"[画像分析] 🔧 不足キーを補完: {placeholder} = {safe_context[placeholder]}")
            
            # 安全にフォーマット
            formatted_prompt = prompt_template.format(**safe_context)
            return formatted_prompt
            
        except Exception as e:
            print(f"[画像分析] ❌ プロンプトフォーマットエラー: {e}")
            # エラー時はコンテキストなしの基本プロンプトを返す
            return f"この画像について詳しく分析してください。\n\n提供されたコンテキスト: {context}"
    
    def _select_analysis_type(self, requested_type: str, context: Dict[str, Any]) -> str:
        """
        コンテキストに応じて適切な分析タイプを選択
        
        Args:
            requested_type: 要求された分析タイプ
            context: コンテキスト情報
            
        Returns:
            効果的な分析タイプ
        """
        # 利用可能な分析タイプのリスト
        available_types = list(self.analysis_prompts.keys())
        
        # 要求されたタイプが利用可能な場合
        if requested_type in available_types:
            # コンテキストの有無でタイプを調整
            if requested_type == "general_description" and context:
                # コンテキストがある場合は、コンテキスト付きの分析を優先
                video_context = context.get('video_context')
                if video_context and "general_with_context" in available_types:
                    return "general_with_context"
            return requested_type
        
        # デフォルト選択ロジック
        if context:
            # コンテキストがある場合の選択
            if any(key in context for key in ['title', 'artist', 'description']):
                return "music_video_analysis"
            elif 'video_context' in context:
                return "general_with_context"
        
        # デフォルト
        return "general_description"
    
    def analyze_image(self, image_path: str, analysis_type: str = "general_description", context: Dict = None) -> Dict[str, Any]:
        """
        画像の包括的分析
        
        Args:
            image_path: 分析する画像のパス
            analysis_type: 分析タイプ
            context: 追加コンテキスト情報
            
        Returns:
            分析結果辞書
        """
        try:
            # コンテキスト準備
            context = context or {}
            
            # 分析タイプの適切な選択
            effective_analysis_type = self._select_analysis_type(analysis_type, context)
            
            # プロンプト生成（安全なフォーマット処理）
            prompt_template = self.analysis_prompts.get(effective_analysis_type, self.analysis_prompts["general_description"])
            prompt = self._safe_format_prompt(prompt_template, context)
            
            print(f"[画像分析] 🔍 分析開始: {effective_analysis_type}")
            
            # Vision API呼び出し
            api_result = self._call_vision_api(prompt, image_path)
            
            # 結果構造化
            analysis_result = {
                'analysis_type': effective_analysis_type,
                'image_path': image_path,
                'description': api_result['content'],
                'metadata': {
                    'tokens_used': api_result['tokens_used'],
                    'estimated_cost': api_result['estimated_cost'],
                    'processing_time': api_result['processing_time'],
                    'model': api_result['model'],
                    'timestamp': api_result['timestamp']
                },
                'context': context
            }
            
            return analysis_result
            
        except Exception as e:
            print(f"[画像分析] ❌ 画像分析エラー: {e}")
            return {
                'analysis_type': analysis_type,
                'image_path': image_path,
                'description': f"分析中にエラーが発生しました: {str(e)}",
                'error': str(e),
                'metadata': {
                    'timestamp': datetime.now().isoformat()
                }
            }
    
    def analyze_with_video_context(self, image_path: str, video_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        動画情報と組み合わせた文脈分析
        
        Args:
            image_path: 分析する画像のパス
            video_info: 動画メタデータ
            
        Returns:
            文脈分析結果
        """
        try:
            # 動画情報からコンテキスト構築
            video_context = f"""
タイトル: {video_info.get('title', '不明')}
チャンネル: {video_info.get('channel_title', '不明')}
概要: {video_info.get('description', '情報なし')[:200]}...
公開日: {video_info.get('published_at', '不明')}
再生回数: {video_info.get('view_count', '不明')}
"""
            
            # 音楽動画として分析
            context = {
                'video_context': video_context,
                'title': video_info.get('title', '不明'),
                'artist': video_info.get('channel_title', '不明'),
                'description': video_info.get('description', '情報なし')[:300]
            }
            
            return self.analyze_image(image_path, "music_video_analysis", context)
            
        except Exception as e:
            print(f"[画像分析] ❌ 動画コンテキスト分析エラー: {e}")
            return self.analyze_image(image_path, "general_description")
    
    def get_analysis_stats(self) -> Dict[str, Any]:
        """分析統計情報を取得"""
        return self.analysis_stats.copy()
    
    def reset_stats(self):
        """統計情報をリセット"""
        self.analysis_stats = {
            'total_analyses': 0,
            'total_cost': 0.0,
            'total_tokens': 0,
            'last_analysis': None
        }
        print("[画像分析] 📊 統計情報をリセットしました")


def test_image_analyzer():
    """ImageAnalyzerの基本動作テスト"""
    print("=== ImageAnalyzer テスト開始 ===")
    
    try:
        # 初期化
        analyzer = ImageAnalyzer()
        
        # 統計情報確認
        stats = analyzer.get_analysis_stats()
        print(f"✅ 初期統計: {stats}")
        
        # プロンプト確認
        prompts = analyzer.analysis_prompts
        print(f"✅ 分析プロンプト数: {len(prompts)}")
        
        print("✅ ImageAnalyzer基本機能正常")
        
    except Exception as e:
        print(f"❌ ImageAnalyzerテスト失敗: {e}")
    
    print("=== ImageAnalyzer テスト完了 ===")


if __name__ == "__main__":
    test_image_analyzer()
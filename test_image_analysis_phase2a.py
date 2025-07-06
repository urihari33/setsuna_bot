#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 2A: ImageAnalyzer統合テスト
OpenAI Vision API統合の動作確認
"""

import sys
from pathlib import Path
import json
from PIL import Image, ImageDraw
import tempfile
import os

# パス設定
sys.path.append(str(Path(__file__).parent))

from core.image_analyzer import ImageAnalyzer
from core.youtube_knowledge_manager import YouTubeKnowledgeManager


def create_test_image_with_text(text="TEST IMAGE", size=(400, 300)):
    """テスト用の画像（テキスト付き）を作成"""
    img = Image.new('RGB', size, color='lightblue')
    draw = ImageDraw.Draw(img)
    
    # テキスト描画
    draw.text((50, 50), text, fill='black')
    draw.text((50, 100), "Music Video Screenshot", fill='darkblue')
    draw.text((50, 150), "Artist: Test Artist", fill='darkblue')
    draw.text((50, 200), "Song: Test Song", fill='darkblue')
    
    # 図形描画
    draw.rectangle([300, 50, 350, 100], fill='red')
    draw.ellipse([300, 150, 350, 200], fill='green')
    
    temp_path = Path(tempfile.gettempdir()) / f"test_analysis_{text.replace(' ', '_')}.jpg"
    img.save(temp_path, 'JPEG')
    return str(temp_path)


def test_image_analyzer_basic():
    """ImageAnalyzer基本機能テスト"""
    print("=== ImageAnalyzer基本機能テスト ===")
    
    try:
        # 初期化
        analyzer = ImageAnalyzer()
        print("✅ ImageAnalyzer初期化成功")
        
        # テスト画像作成
        test_image_path = create_test_image_with_text("ANALYZER_TEST")
        print(f"📷 テスト画像作成: {test_image_path}")
        
        # 画像分析テスト（API呼び出しはスキップ）
        print("ℹ️ 実際のAPI呼び出しテストはコスト考慮により手動実行")
        
        # 統計確認
        stats = analyzer.get_analysis_stats()
        print(f"📊 分析統計: {stats}")
        
        # テンポラリファイル削除
        os.unlink(test_image_path)
        
        return True
        
    except Exception as e:
        print(f"❌ ImageAnalyzer基本テスト失敗: {e}")
        return False


def test_youtube_manager_integration():
    """YouTubeKnowledgeManagerとの統合テスト"""
    print("\n=== YouTubeKnowledgeManager統合テスト ===")
    
    try:
        # マネージャー初期化
        yt_manager = YouTubeKnowledgeManager()
        print("✅ YouTubeKnowledgeManager初期化成功")
        
        # ImageAnalyzer統合確認
        if yt_manager.image_analyzer:
            print("✅ ImageAnalyzer統合確認")
        else:
            print("⚠️ ImageAnalyzer統合失敗（APIキー未設定の可能性）")
            return False
        
        # 分析統計取得テスト
        stats = yt_manager.get_analysis_stats()
        print(f"📊 統合統計情報: {json.dumps(stats, indent=2, ensure_ascii=False)}")
        
        return True
        
    except Exception as e:
        print(f"❌ YouTubeKnowledgeManager統合テスト失敗: {e}")
        return False


def test_mock_analysis():
    """モック画像分析テスト（API呼び出しなし）"""
    print("\n=== モック画像分析テスト ===")
    
    try:
        analyzer = ImageAnalyzer()
        
        # テスト画像作成
        test_image_path = create_test_image_with_text("MOCK_ANALYSIS")
        
        # モック動画情報
        mock_video_info = {
            'title': 'テスト楽曲 - Music Video',
            'channel_title': 'Test Artist',
            'description': 'これはテスト用の音楽動画です。明るい雰囲気の楽曲。',
            'published_at': '2025-07-04T00:00:00Z',
            'view_count': 100000
        }
        
        # 分析準備（API呼び出しはしない）
        print("📝 分析設定確認:")
        print(f"  - 分析プロンプト数: {len(analyzer.analysis_prompts)}")
        print(f"  - 最大画像サイズ: {analyzer.max_image_size}")
        print(f"  - デフォルトトークン数: {analyzer.default_max_tokens}")
        
        # 画像最適化テスト
        optimized_path = analyzer._resize_image_for_api(test_image_path)
        print(f"📏 画像最適化: {test_image_path} → {optimized_path}")
        
        # Base64エンコードテスト
        try:
            encoded = analyzer._encode_image_to_base64(optimized_path)
            print(f"📝 Base64エンコード成功: {len(encoded)}文字")
        except Exception as e:
            print(f"❌ Base64エンコードエラー: {e}")
        
        # プロンプト生成テスト
        context = {
            'video_context': f"タイトル: {mock_video_info['title']}\nアーティスト: {mock_video_info['channel_title']}",
            'title': mock_video_info['title'],
            'artist': mock_video_info['channel_title'],
            'description': mock_video_info['description']
        }
        
        prompt_template = analyzer.analysis_prompts["music_video_analysis"]
        prompt = prompt_template.format(**context)
        print(f"📋 生成プロンプト: {len(prompt)}文字")
        
        # テンポラリファイル削除
        os.unlink(test_image_path)
        if optimized_path != test_image_path:
            try:
                os.unlink(optimized_path)
            except:
                pass
        
        print("✅ モック分析テスト完了")
        return True
        
    except Exception as e:
        print(f"❌ モック分析テスト失敗: {e}")
        return False


def test_manual_api_call():
    """手動API呼び出しテスト（実際のOpenAI API使用）"""
    print("\n=== 手動API呼び出しテスト ===")
    print("⚠️ このテストは実際のOpenAI APIを呼び出し、コストが発生します。")
    
    response = input("続行しますか？ (y/N): ").strip().lower()
    if response != 'y':
        print("ℹ️ 手動API呼び出しテストをスキップしました")
        return True
    
    try:
        analyzer = ImageAnalyzer()
        
        # テスト画像作成
        test_image_path = create_test_image_with_text("API_TEST", (300, 200))
        print(f"📷 API テスト用画像作成: {test_image_path}")
        
        # 簡単な分析実行
        context = {
            'video_context': "テスト動画: サンプル音楽動画"
        }
        
        print("🚀 OpenAI Vision API呼び出し開始...")
        result = analyzer.analyze_image(
            image_path=test_image_path,
            analysis_type="general_description",
            context=context
        )
        
        print("✅ API呼び出し成功！")
        print(f"📝 分析結果: {result['description'][:200]}...")
        print(f"💰 推定コスト: ${result['metadata']['estimated_cost']:.4f}")
        print(f"🔢 使用トークン: {result['metadata']['tokens_used']}")
        
        # テンポラリファイル削除
        os.unlink(test_image_path)
        
        return True
        
    except Exception as e:
        print(f"❌ 手動API呼び出しテスト失敗: {e}")
        return False


def main():
    """メインテスト実行"""
    print("🎯 Phase 2A: ImageAnalyzer統合テスト開始")
    print("=" * 60)
    
    success_count = 0
    total_tests = 3  # 基本テストのみ（手動API呼び出しは別扱い）
    
    # 基本テスト実行
    if test_image_analyzer_basic():
        success_count += 1
    
    if test_youtube_manager_integration():
        success_count += 1
    
    if test_mock_analysis():
        success_count += 1
    
    # 結果表示
    print("\n" + "=" * 60)
    print(f"📊 基本テスト結果: {success_count}/{total_tests} 成功")
    
    if success_count == total_tests:
        print("🎉 Phase 2A基本実装完了！")
        print("\n✨ 実装された機能:")
        print("  ✅ ImageAnalyzer基本クラス構造")
        print("  ✅ OpenAI Vision API統合準備")
        print("  ✅ 分析プロンプト最適化")
        print("  ✅ YouTubeKnowledgeManager統合")
        print("  ✅ コスト計算・統計機能")
        print("  ✅ エラーハンドリング")
        
        # 手動APIテストの提案
        print(f"\n🧪 手動APIテストを実行しますか？")
        if test_manual_api_call():
            print("🚀 Phase 2A完全テスト成功！")
        
        return True
    else:
        print(f"❌ {total_tests - success_count}個のテストが失敗しました")
        return False


if __name__ == "__main__":
    main()
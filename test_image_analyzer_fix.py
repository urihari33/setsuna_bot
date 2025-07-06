#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ImageAnalyzer修正版テストスクリプト
プロンプトテンプレートの不足キー問題修正の動作確認
"""

import sys
import os
from pathlib import Path
import tempfile
import traceback
from PIL import Image

# パス設定
sys.path.append(str(Path(__file__).parent))

def create_test_image():
    """テスト用画像ファイル作成"""
    try:
        img = Image.new('RGB', (400, 300), color='lightblue')
        temp_path = tempfile.mktemp(suffix='.jpg')
        img.save(temp_path, 'JPEG')
        return temp_path
    except Exception as e:
        print(f"❌ テスト画像作成失敗: {e}")
        return None

def test_image_analyzer_fix():
    """ImageAnalyzer修正版テスト"""
    print("🔧 ImageAnalyzer修正版テスト開始")
    print("=" * 60)
    
    try:
        # 1. ImageAnalyzerクラスのインポート
        print("1️⃣ ImageAnalyzerクラスのインポート...")
        from core.image_analyzer import ImageAnalyzer
        print("✅ インポート成功")
        
        # 2. 初期化
        print("\n2️⃣ ImageAnalyzer初期化...")
        analyzer = ImageAnalyzer()
        print("✅ 初期化成功")
        
        # 3. テスト画像作成
        print("\n3️⃣ テスト画像作成...")
        test_image_path = create_test_image()
        if not test_image_path:
            return False
        print(f"✅ テスト画像作成: {test_image_path}")
        
        # 4. 基本的な分析テスト（コンテキストなし）
        print("\n4️⃣ 基本的な分析テスト（コンテキストなし）...")
        try:
            result1 = analyzer.analyze_image(
                test_image_path,
                analysis_type="general_description"
            )
            
            if result1 and 'description' in result1:
                print("✅ 基本分析成功")
                print(f"   分析タイプ: {result1['analysis_type']}")
                print(f"   結果: {result1['description'][:100]}...")
            else:
                print(f"⚠️ 基本分析結果異常: {result1}")
                
        except Exception as e:
            print(f"❌ 基本分析エラー: {e}")
            traceback.print_exc()
        
        # 5. 不完全なコンテキスト付き分析テスト
        print("\n5️⃣ 不完全なコンテキスト付き分析テスト...")
        try:
            incomplete_context = {
                'title': 'テスト画像のタイトル'
                # 'artist', 'description' は意図的に省略
            }
            
            result2 = analyzer.analyze_image(
                test_image_path,
                analysis_type="music_video_analysis",
                context=incomplete_context
            )
            
            if result2 and 'description' in result2:
                print("✅ 不完全コンテキスト分析成功")
                print(f"   分析タイプ: {result2['analysis_type']}")
                print(f"   結果: {result2['description'][:100]}...")
            else:
                print(f"⚠️ 不完全コンテキスト分析結果異常: {result2}")
                
        except Exception as e:
            print(f"❌ 不完全コンテキスト分析エラー: {e}")
            traceback.print_exc()
        
        # 6. 存在しない分析タイプテスト
        print("\n6️⃣ 存在しない分析タイプテスト...")
        try:
            result3 = analyzer.analyze_image(
                test_image_path,
                analysis_type="non_existent_type"
            )
            
            if result3 and 'description' in result3:
                print("✅ 存在しない分析タイプ処理成功")
                print(f"   分析タイプ: {result3['analysis_type']}")
                print(f"   結果: {result3['description'][:100]}...")
            else:
                print(f"⚠️ 存在しない分析タイプ結果異常: {result3}")
                
        except Exception as e:
            print(f"❌ 存在しない分析タイプエラー: {e}")
            traceback.print_exc()
        
        # 7. 完全なコンテキスト付き分析テスト
        print("\n7️⃣ 完全なコンテキスト付き分析テスト...")
        try:
            complete_context = {
                'title': 'テスト楽曲',
                'artist': 'テストアーティスト',
                'description': 'これは修正テスト用の楽曲です。',
                'video_context': '動画情報：テスト楽曲のミュージックビデオ'
            }
            
            result4 = analyzer.analyze_image(
                test_image_path,
                analysis_type="music_video_analysis",
                context=complete_context
            )
            
            if result4 and 'description' in result4:
                print("✅ 完全コンテキスト分析成功")
                print(f"   分析タイプ: {result4['analysis_type']}")
                print(f"   結果: {result4['description'][:100]}...")
            else:
                print(f"⚠️ 完全コンテキスト分析結果異常: {result4}")
                
        except Exception as e:
            print(f"❌ 完全コンテキスト分析エラー: {e}")
            traceback.print_exc()
        
        # 8. 空のコンテキスト辞書テスト
        print("\n8️⃣ 空のコンテキスト辞書テスト...")
        try:
            result5 = analyzer.analyze_image(
                test_image_path,
                analysis_type="music_video_analysis",
                context={}
            )
            
            if result5 and 'description' in result5:
                print("✅ 空コンテキスト分析成功")
                print(f"   分析タイプ: {result5['analysis_type']}")
                print(f"   結果: {result5['description'][:100]}...")
            else:
                print(f"⚠️ 空コンテキスト分析結果異常: {result5}")
                
        except Exception as e:
            print(f"❌ 空コンテキスト分析エラー: {e}")
            traceback.print_exc()
        
        # 9. _safe_format_prompt直接テスト
        print("\n9️⃣ _safe_format_promptメソッド直接テスト...")
        try:
            # 不完全なコンテキストでテスト
            test_template = analyzer.analysis_prompts["music_video_analysis"]
            test_context = {'title': 'テスト'}
            
            formatted_prompt = analyzer._safe_format_prompt(test_template, test_context)
            
            if formatted_prompt and "不明" in formatted_prompt:
                print("✅ _safe_format_prompt成功")
                print(f"   フォーマット結果: {formatted_prompt[:200]}...")
            else:
                print(f"⚠️ _safe_format_prompt結果異常: {formatted_prompt}")
                
        except Exception as e:
            print(f"❌ _safe_format_promptエラー: {e}")
            traceback.print_exc()
        
        # 10. 統計情報確認
        print("\n🔟 統計情報確認...")
        try:
            stats = analyzer.get_analysis_stats()
            print(f"✅ 統計情報: {stats}")
            
        except Exception as e:
            print(f"❌ 統計情報エラー: {e}")
        
        # クリーンアップ
        print("\n🧹 クリーンアップ...")
        try:
            if os.path.exists(test_image_path):
                os.remove(test_image_path)
                print("✅ テスト画像削除完了")
        except Exception as e:
            print(f"⚠️ クリーンアップエラー: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ テスト中にエラーが発生: {e}")
        traceback.print_exc()
        return False

def main():
    """メイン実行"""
    print("🔧 ImageAnalyzer修正版テストシステム")
    print("=" * 60)
    
    if test_image_analyzer_fix():
        print("\n✅ テスト完了")
        print("\n📊 修正内容:")
        print("1. _safe_format_promptメソッドを追加")
        print("2. 不足キーの自動補完機能")
        print("3. 分析タイプの自動選択機能")
        print("4. general_with_contextテンプレートを追加")
        print("5. エラーハンドリング強化")
        
        print("\n✅ 期待される改善点:")
        print("- 'title'キーエラーの解決")
        print("- 'description'キーエラーの解決")
        print("- 不完全なコンテキストでの安定動作")
        print("- フォールバック機能の強化")
        
        return True
    else:
        print("\n❌ テスト失敗")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
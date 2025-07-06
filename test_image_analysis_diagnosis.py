#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
画像分析エラー診断スクリプト
画像分析システムの詳細なエラー原因を特定
"""

import sys
from pathlib import Path
import tempfile
import os
from PIL import Image
import traceback

# パス設定
sys.path.append(str(Path(__file__).parent))

def create_test_image():
    """テスト用画像ファイル作成"""
    try:
        img = Image.new('RGB', (300, 200), color='green')
        temp_path = tempfile.mktemp(suffix='.jpg')
        img.save(temp_path, 'JPEG')
        return temp_path
    except Exception as e:
        print(f"❌ テスト画像作成失敗: {e}")
        return None

def diagnose_image_analysis():
    """画像分析エラー診断"""
    print("🔍 画像分析エラー診断開始")
    print("=" * 60)
    
    try:
        # 1. システム初期化確認
        print("1️⃣ システム初期化確認...")
        from voice_chat_gui import SetsunaGUI
        gui = SetsunaGUI()
        print("✅ GUI初期化成功")
        
        # 2. YouTube管理システム確認
        print("\n2️⃣ YouTube管理システム確認...")
        if not gui.youtube_manager:
            print("❌ YouTube管理システムが初期化されていません")
            return False
        print("✅ YouTube管理システム確認完了")
        
        # 3. 画像分析システム確認
        print("\n3️⃣ 画像分析システム確認...")
        if not hasattr(gui.youtube_manager, 'image_analyzer'):
            print("❌ 画像分析システムが統合されていません")
            return False
        
        image_analyzer = gui.youtube_manager.image_analyzer
        print("✅ 画像分析システム確認完了")
        print(f"   - 分析システムタイプ: {type(image_analyzer)}")
        
        # 4. プロンプトテンプレート確認
        print("\n4️⃣ プロンプトテンプレート確認...")
        if hasattr(image_analyzer, 'prompt_templates'):
            templates = image_analyzer.prompt_templates
            print(f"✅ プロンプトテンプレート数: {len(templates)}")
            
            for template_name in templates.keys():
                print(f"   - {template_name}")
        else:
            print("⚠️ プロンプトテンプレートが見つかりません")
        
        # 5. テスト画像作成
        print("\n5️⃣ テスト画像作成...")
        test_image_path = create_test_image()
        if not test_image_path:
            return False
        print(f"✅ テスト画像作成: {test_image_path}")
        
        # 6. 画像分析テスト（一般的な分析）
        print("\n6️⃣ 一般的な画像分析テスト...")
        try:
            result1 = image_analyzer.analyze_image(
                test_image_path,
                analysis_type="general_description"
            )
            
            if result1:
                print("✅ 一般的な分析成功")
                print(f"   結果タイプ: {type(result1)}")
                print(f"   結果内容: {result1}")
            else:
                print("⚠️ 一般的な分析結果が空です")
                
        except Exception as e:
            print(f"❌ 一般的な分析エラー: {e}")
            print("詳細エラー:")
            traceback.print_exc()
        
        # 7. 画像分析テスト（音楽動画分析・コンテキスト付き）
        print("\n7️⃣ 音楽動画分析テスト（コンテキスト付き）...")
        try:
            context = {
                'title': 'テスト画像',
                'artist': 'テストアーティスト',
                'description': 'テスト用の画像です'
            }
            
            result2 = image_analyzer.analyze_image(
                test_image_path,
                analysis_type="music_video_analysis",
                context=context
            )
            
            if result2:
                print("✅ 音楽動画分析成功")
                print(f"   結果タイプ: {type(result2)}")
                print(f"   結果内容: {result2}")
            else:
                print("⚠️ 音楽動画分析結果が空です")
                
        except Exception as e:
            print(f"❌ 音楽動画分析エラー: {e}")
            print("詳細エラー:")
            traceback.print_exc()
        
        # 8. 画像分析テスト（音楽動画分析・コンテキストなし）
        print("\n8️⃣ 音楽動画分析テスト（コンテキストなし）...")
        try:
            result3 = image_analyzer.analyze_image(
                test_image_path,
                analysis_type="music_video_analysis"
            )
            
            if result3:
                print("✅ 音楽動画分析（コンテキストなし）成功")
                print(f"   結果内容: {result3}")
            else:
                print("⚠️ 音楽動画分析（コンテキストなし）結果が空です")
                
        except Exception as e:
            print(f"❌ 音楽動画分析（コンテキストなし）エラー: {e}")
            print(f"エラー詳細: {traceback.format_exc()}")
        
        # 9. 統合メッセージ処理テスト
        print("\n9️⃣ 統合メッセージ処理テスト...")
        
        test_file_info = {
            'type': 'image',
            'path': test_image_path,
            'name': 'test_diagnosis.jpg',
            'size': os.path.getsize(test_image_path)
        }
        
        integrated_message = {
            'text': 'この画像について教えて',
            'images': [test_file_info],
            'url': None,
            'timestamp': '2025-07-06T12:00:00'
        }
        
        try:
            # 統合メッセージ処理をモック実行
            print("🔍 統合メッセージ処理開始...")
            
            # 画像分析部分のみテスト
            images = integrated_message.get('images', [])
            if images:
                for image_info in images:
                    image_path = image_info.get('path')
                    if image_path and os.path.exists(image_path):
                        print(f"📸 画像分析実行: {image_info['name']}")
                        
                        # Phase 2C-1のロジックと同じ処理
                        try:
                            context = {
                                'title': integrated_message.get('text', '添付画像'),
                                'artist': '不明',
                                'description': f"ユーザーから添付された画像: {image_info['name']}"
                            }
                            
                            # 一般的な分析を試行
                            analysis_result = image_analyzer.analyze_image(
                                image_path, 
                                analysis_type="general_description"
                            )
                            
                            # 成功しなかった場合はcontextを付けて再試行
                            if not analysis_result or 'description' not in analysis_result:
                                analysis_result = image_analyzer.analyze_image(
                                    image_path, 
                                    analysis_type="music_video_analysis",
                                    context=context
                                )
                            
                            if analysis_result and 'description' in analysis_result:
                                print(f"✅ 統合処理画像分析成功: {analysis_result['description'][:100]}...")
                            else:
                                print(f"⚠️ 統合処理画像分析結果不正: {analysis_result}")
                                
                        except Exception as analysis_error:
                            print(f"❌ 統合処理画像分析エラー: {analysis_error}")
                            print(f"詳細: {traceback.format_exc()}")
            
        except Exception as e:
            print(f"❌ 統合メッセージ処理エラー: {e}")
            traceback.print_exc()
        
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
        print(f"❌ 診断エラー: {e}")
        traceback.print_exc()
        return False

def main():
    """メイン診断実行"""
    print("🩺 画像分析エラー診断システム")
    print("=" * 60)
    
    if diagnose_image_analysis():
        print("\n📊 診断完了")
        print("\n🔍 エラー原因特定のために確認してください:")
        print("1. 上記の各テストでどの段階でエラーが発生しているか")
        print("2. エラーメッセージの詳細内容")
        print("3. プロンプトテンプレートが正しく読み込まれているか")
        print("4. OpenAI APIキーが正しく設定されているか")
        
        print("\n💡 推奨対処法:")
        print("- 'title'エラーの場合: プロンプトテンプレートの問題")
        print("- 'description'エラーの場合: 戻り値の形式問題") 
        print("- API関連エラー: OpenAI接続問題")
        print("- ファイル関連エラー: 画像ファイルアクセス問題")
        
        return True
    else:
        print("\n❌ 診断中にエラーが発生しました")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
#!/usr/bin/env python3
"""緊急テスト - docsに接続できる場合の簡単テスト"""

import requests
import json

def quick_test():
    """docsに接続できている場合の緊急テスト"""
    print("🔧 緊急テスト実行中...")
    
    try:
        # 1. バージョン確認
        print("1. バージョン確認...")
        version_response = requests.get("http://127.0.0.1:50021/version", timeout=5)
        if version_response.status_code == 200:
            print(f"✅ バージョン: {version_response.json()}")
        else:
            print(f"❌ バージョン取得失敗: {version_response.status_code}")
            return
        
        # 2. スピーカー確認
        print("2. スピーカー確認...")
        speakers_response = requests.get("http://127.0.0.1:50021/speakers", timeout=5)
        if speakers_response.status_code == 200:
            speakers = speakers_response.json()
            print(f"✅ スピーカー数: {len(speakers)}")
            # 最初のスピーカーを使用
            first_speaker = speakers[0]
            speaker_id = first_speaker['styles'][0]['id']
            speaker_name = first_speaker['name']
            print(f"使用スピーカー: {speaker_name} (ID: {speaker_id})")
        else:
            print(f"❌ スピーカー取得失敗: {speakers_response.status_code}")
            return
        
        # 3. 音声合成テスト
        print("3. 音声合成テスト...")
        text = "音声システムのテストです。正常に動作しています。"
        
        # Step 1: audio_query
        print("  Step 1: audio_query...")
        params = {"text": text, "speaker": speaker_id}
        query_response = requests.post(
            "http://127.0.0.1:50021/audio_query",
            params=params,
            timeout=10
        )
        
        if query_response.status_code != 200:
            print(f"❌ audio_query失敗: {query_response.status_code}")
            print(f"エラー内容: {query_response.text}")
            return
        
        print("  ✅ audio_query成功")
        
        # Step 2: synthesis
        print("  Step 2: synthesis...")
        synthesis_response = requests.post(
            "http://127.0.0.1:50021/synthesis",
            params={"speaker": speaker_id},
            data=json.dumps(query_response.json()),
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if synthesis_response.status_code != 200:
            print(f"❌ synthesis失敗: {synthesis_response.status_code}")
            print(f"エラー内容: {synthesis_response.text}")
            return
        
        print("  ✅ synthesis成功")
        
        # ファイル保存
        with open("emergency_test.wav", "wb") as f:
            f.write(synthesis_response.content)
        
        print(f"🎉 テスト完了！")
        print(f"📁 emergency_test.wav として保存しました ({len(synthesis_response.content)} bytes)")
        print("🔊 ファイルを再生して音声を確認してください")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ 接続エラー: VOICEVOXに接続できません")
        print("→ VOICEVOXが正常に起動しているか確認してください")
    except requests.exceptions.Timeout:
        print("❌ タイムアウト: 処理に時間がかかりすぎています")
        print("→ PCのスペックまたはVOICEVOXの設定を確認してください")
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
    
    return False

def check_voicevox_speaker_module():
    """voicevox_speakerモジュールの確認"""
    print("\n🔍 voicevox_speakerモジュールの確認...")
    try:
        from voicevox_speaker import speak_with_voicevox
        print("✅ voicevox_speakerモジュールは正常にインポートできます")
        
        # モジュールの詳細確認
        import inspect
        signature = inspect.signature(speak_with_voicevox)
        print(f"関数シグネチャ: {signature}")
        
        return True
    except ImportError as e:
        print(f"❌ voicevox_speakerモジュールが見つかりません: {e}")
        print("→ モジュールが正しくインストールされているか確認してください")
        return False
    except Exception as e:
        print(f"❌ voicevox_speakerモジュールエラー: {e}")
        return False

if __name__ == "__main__":
    print("🚨 VOICEVOX 緊急テスト")
    print("=" * 50)
    
    # まずは直接APIテスト
    if quick_test():
        print("\n" + "=" * 50)
        print("✅ 直接API呼び出しは成功しました！")
        print("問題は voicevox_speaker モジュールにあると思われます。")
        
        # voicevox_speakerモジュールの確認
        check_voicevox_speaker_module()
        
        print("\n💡 解決策:")
        print("1. voicevox_speakerモジュールを使わず、上記のコードを使用する")
        print("2. voicevox_speakerモジュールを最新版に更新する")
        print("3. 独自の音声合成関数を作成する")
        
    else:
        print("\n" + "=" * 50)
        print("❌ 基本的なAPI接続に問題があります")
        print("診断ツールを実行して詳細を確認してください")
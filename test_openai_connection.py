"""
OpenAI API接続テスト
"""
import os
from openai import OpenAI
from dotenv import load_dotenv

# 環境変数読み込み
load_dotenv()

def test_openai_connection():
    """OpenAI API接続をテスト"""
    print("=== OpenAI API接続テスト ===")
    
    # APIキー確認
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY が設定されていません")
        print("  .envファイルを確認してください")
        return False
    
    print(f"✅ OPENAI_API_KEY が設定されています (末尾: ...{api_key[-4:]})")
    
    # OpenAIクライアント初期化
    client = OpenAI(api_key=api_key)
    
    # 簡単なテスト呼び出し
    try:
        print("📡 OpenAI APIをテスト中...")
        
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "あなたは親切なアシスタントです。"},
                {"role": "user", "content": "こんにちは。簡単なテストメッセージです。「テスト成功」と答えてください。"}
            ],
            max_tokens=50,
            temperature=0.3
        )
        
        response_text = response.choices[0].message.content.strip()
        print(f"✅ API呼び出し成功")
        print(f"📝 レスポンス: {response_text}")
        
        return True
        
    except Exception as e:
        error_message = str(e)
        print(f"❌ エラーが発生しました: {error_message}")
        
        if "authentication" in error_message.lower():
            print("  → 認証エラー: APIキーが無効です")
        elif "rate_limit" in error_message.lower():
            print("  → レート制限エラー: APIの使用量制限に達しています")
        elif "insufficient_quota" in error_message.lower():
            print("  → クォータ不足: APIの利用枠を使い切っています")
        else:
            print(f"  → 詳細: {e}")
        
        return False

def test_description_analysis():
    """概要欄分析のテスト"""
    print("\n=== 概要欄分析テスト ===")
    
    # APIキー確認
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY が設定されていません")
        return False
    
    # OpenAIクライアント初期化
    client = OpenAI(api_key=api_key)
    
    # テスト用の概要欄データ
    test_description = """
Music&Lyric：MATZ、Nanako Ashida
Arrangement：MATZ
Vocal: ▽▲TRiNITY▲▽
Illust：猫山桜梨
Movie：木葉はづく

歌詞：
Yeah…
I'm a girl cuter than a Barbie doll ya
誰も知らない I'm a royal
君もハマるわ Count on 1 2 3
"""
    
    try:
        print("📡 概要欄分析をテスト中...")
        
        prompt = """
以下の概要欄テキストから情報を抽出してください。
JSON形式で返してください：

{
  "creators": {
    "vocal": "歌い手名",
    "movie": "映像制作者",
    "music": "作曲者"
  },
  "lyrics": "歌詞の一部"
}

概要欄テキスト:
""" + test_description
        
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "あなたは音楽・映像制作の専門家です。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.3
        )
        
        response_text = response.choices[0].message.content.strip()
        print(f"✅ 概要欄分析テスト成功")
        print(f"📝 分析結果:")
        print(response_text)
        
        return True
        
    except Exception as e:
        print(f"❌ 概要欄分析テストエラー: {e}")
        return False

if __name__ == "__main__":
    # OpenAI API接続テスト
    if test_openai_connection():
        # 概要欄分析テスト
        test_description_analysis()
    
    print("\n=== テスト完了 ===")
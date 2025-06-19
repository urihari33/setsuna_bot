"""
手動分析用ヘルパー：概要欄テキストを抽出してClaude用に整形
"""
import json
from pathlib import Path

def extract_descriptions_for_manual_analysis():
    """概要欄を抽出してClaudeでの手動分析用に整形"""
    
    playlist_file = Path("D:/setsuna_bot/youtube_knowledge_system/data/playlists/playlist_PL4R2l8ETuvxueMZJo63H8ykV_OY0LuzfX.json")
    
    with open(playlist_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    videos = data.get('videos', [])
    
    print("=== Claude手動分析用データ ===\n")
    
    for i, video in enumerate(videos[:5]):  # 最初の5件をサンプル
        print(f"## 動画 {i+1}: {video['title']}")
        print(f"概要欄:")
        print(video['description'][:500] + "..." if len(video['description']) > 500 else video['description'])
        print("\n" + "="*80 + "\n")
    
    print(f"全{len(videos)}件のうち、最初の5件を表示しました。")
    print("\nClaude用プロンプト例:")
    print("""
以下のYouTube動画概要欄から、JSON形式で情報を抽出してください：
{
  "creators": {"vocal": "名前", "movie": "名前", "composer": "名前"},
  "lyrics": "歌詞（あれば）",
  "tools": {"software": ["ツール"], "instruments": ["楽器"]}
}
    """)

if __name__ == "__main__":
    extract_descriptions_for_manual_analysis()
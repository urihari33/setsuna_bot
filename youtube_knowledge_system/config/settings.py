"""
YouTube Knowledge System Configuration
"""
import os
from pathlib import Path

# プロジェクトルートディレクトリ
PROJECT_ROOT = Path(__file__).parent.parent.parent

# 認証情報
YOUTUBE_CREDENTIALS_PATH = PROJECT_ROOT / "config" / "youtube_credentials.json"
YOUTUBE_TOKEN_PATH = PROJECT_ROOT / "config" / "youtube_token.json"

# API設定
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"
YOUTUBE_SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]

# データ保存設定
# Windows環境でのパス設定（WSL2のマウントパスではなく、実際のWindowsパス）
DATA_DIR = Path("D:/setsuna_bot/youtube_knowledge_system/data")
HISTORY_DATA_FILE = DATA_DIR / "watch_history.json"
PLAYLIST_DATA_FILE = DATA_DIR / "playlists.json"

# 取得制限設定
MAX_RESULTS_PER_REQUEST = 50  # YouTube API の制限
MAX_TOTAL_VIDEOS = 1000  # 一度に取得する最大動画数
QUOTA_LIMIT_PER_DAY = 10000  # YouTube API の日次制限

# フィルタリング設定
CREATIVE_KEYWORDS = [
    "映像制作", "動画編集", "撮影", "ストーリーテリング", "映画制作",
    "video editing", "filmmaking", "cinematography", "storytelling",
    "Adobe Premiere", "Final Cut", "DaVinci Resolve", "After Effects",
    "カメラワーク", "照明", "音響", "脚本", "演出", "プロダクション"
]

EXCLUDE_KEYWORDS = [
    "ゲーム実況", "料理", "スポーツ", "ニュース", "政治"
]

# ログ設定
LOG_LEVEL = "INFO"
LOG_FILE = PROJECT_ROOT / "logs" / "youtube_knowledge.log"
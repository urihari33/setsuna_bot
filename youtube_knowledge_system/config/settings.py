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
# WSL2とWindows環境両対応のパス設定
def get_data_dir():
    """環境に応じたデータディレクトリを取得"""
    import platform
    import shutil
    
    # Windows環境かWSL2かを判定
    system = platform.system().lower()
    
    if system == "windows":
        # 純粋なWindows環境
        windows_path = Path("D:/setsuna_bot/youtube_knowledge_system/data")
        wsl_path = Path("/mnt/d/setsuna_bot/youtube_knowledge_system/data")
        
        # Windowsディレクトリを作成
        if not windows_path.exists():
            windows_path.mkdir(parents=True, exist_ok=True)
            print(f"Windows データディレクトリを作成しました: {windows_path}")
        
        # WSL2にデータが存在する場合はコピー
        if wsl_path.exists():
            wsl_db_file = wsl_path / "unified_knowledge_db.json"
            windows_db_file = windows_path / "unified_knowledge_db.json"
            
            if wsl_db_file.exists() and not windows_db_file.exists():
                try:
                    shutil.copy2(str(wsl_db_file), str(windows_db_file))
                    print(f"データベースをWSL2からWindowsにコピーしました: {windows_db_file}")
                except Exception as e:
                    print(f"データベースコピーエラー: {e}")
            
            # プレイリスト設定もコピー
            wsl_config_file = wsl_path / "playlist_configs.json"
            windows_config_file = windows_path / "playlist_configs.json"
            
            if wsl_config_file.exists() and not windows_config_file.exists():
                try:
                    shutil.copy2(str(wsl_config_file), str(windows_config_file))
                    print(f"プレイリスト設定をコピーしました: {windows_config_file}")
                except Exception as e:
                    print(f"設定ファイルコピーエラー: {e}")
        
        return windows_path
    else:
        # Linux/WSL2環境
        wsl_path = Path("/mnt/d/setsuna_bot/youtube_knowledge_system/data")
        windows_path = Path("D:/setsuna_bot/youtube_knowledge_system/data")
        
        if wsl_path.exists():
            return wsl_path
        elif windows_path.exists():
            return windows_path
        else:
            # フォールバック：WSL2パスを作成
            wsl_path.mkdir(parents=True, exist_ok=True)
            return wsl_path

DATA_DIR = get_data_dir()
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
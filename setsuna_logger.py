import logging
import os
from datetime import datetime

# ログディレクトリの作成
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# 実行開始時刻でログファイル名を生成
START_TIME = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_FILENAME = f"setsuna_{START_TIME}.log"
LOG_FILEPATH = os.path.join(LOG_DIR, LOG_FILENAME)

def setup_unified_logger():
    """統合ログシステムのセットアップ"""
    formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # ファイルハンドラー
    file_handler = logging.FileHandler(LOG_FILEPATH, encoding='utf-8')
    file_handler.setFormatter(formatter)
    
    # コンソールハンドラー（エラーレベルのみ）
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.ERROR)
    
    # ルートロガーの設定
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    return root_logger

# 統合ロガーを初期化
logger = setup_unified_logger()

def log_startup():
    """起動ログを記録"""
    logger.info("=" * 50)
    logger.info(f"SETSUNA BOT STARTED - Session: {START_TIME}")
    logger.info("=" * 50)

def log_conversation(user_input, bot_response, response_time):
    """対話ログを記録"""
    conversation_logger = logging.getLogger('CONVERSATION')
    conversation_logger.info(f"USER: {user_input}")
    conversation_logger.info(f"BOT: {bot_response}")
    conversation_logger.info(f"RESPONSE_TIME: {response_time:.2f}s")
    conversation_logger.info("---")

def log_memory_operation(operation, details):
    """記憶操作ログを記録"""
    memory_logger = logging.getLogger('MEMORY')
    memory_logger.info(f"{operation}: {details}")

def log_voice_operation(operation, details):
    """音声操作ログを記録"""
    voice_logger = logging.getLogger('VOICE')
    voice_logger.info(f"{operation}: {details}")

def log_error(component, error_msg, exception=None):
    """エラーログを記録"""
    error_logger = logging.getLogger('ERROR')
    error_logger.error(f"{component}: {error_msg}")
    if exception:
        error_logger.error(f"Exception: {str(exception)}", exc_info=True)

def log_system(message):
    """システムログを記録"""
    system_logger = logging.getLogger('SYSTEM')
    system_logger.info(message)

def log_shutdown():
    """終了ログを記録"""
    logger.info("=" * 50)
    logger.info(f"SETSUNA BOT STOPPED - Session: {START_TIME}")
    logger.info("=" * 50)

# 起動時にスタートアップログを記録
log_startup()
log_system(f"Log file: {LOG_FILEPATH}")
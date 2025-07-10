#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ConfigManager - 共通設定管理モジュール
環境変数・設定ファイルの統一管理システム
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
import json
from dataclasses import dataclass

# python-dotenvの安全なインポート
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    print("[設定管理] ⚠️ python-dotenvが見つかりません。pip install python-dotenvを実行してください。")

@dataclass
class ConfigValidationResult:
    """設定検証結果"""
    is_valid: bool
    missing_keys: list
    warnings: list
    errors: list

class ConfigManager:
    """共通設定管理クラス"""
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        初期化
        
        Args:
            config_path: 設定ファイルパス（オプション）
        """
        self.config_path = config_path or Path(__file__).parent.parent / ".env"
        self.config_data = {}
        self.validation_result = None
        
        # 環境変数読み込み
        self._load_environment_variables()
        
        # 設定検証
        self.validation_result = self._validate_config()
        
        # 初期化完了ログ
        self._print_initialization_status()
    
    def _load_environment_variables(self):
        """環境変数読み込み"""
        try:
            if DOTENV_AVAILABLE and self.config_path.exists():
                # .envファイルから読み込み
                load_dotenv(self.config_path)
                print(f"[設定管理] 📋 .envファイル読み込み完了: {self.config_path}")
            else:
                if not self.config_path.exists():
                    print(f"[設定管理] ⚠️ .envファイルが見つかりません: {self.config_path}")
                print("[設定管理] 📋 システム環境変数を使用")
            
            # 設定データキャッシュ
            self._cache_config_data()
            
        except Exception as e:
            print(f"[設定管理] ❌ 環境変数読み込み失敗: {e}")
    
    def _cache_config_data(self):
        """設定データキャッシュ"""
        # OpenAI設定
        self.config_data["openai"] = {
            "api_key": os.getenv("OPENAI_API_KEY") or os.getenv("OPENAI_KEY"),
            "organization": os.getenv("OPENAI_ORGANIZATION"),
            "base_url": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        }
        
        # VOICEVOX設定
        self.config_data["voicevox"] = {
            "url": os.getenv("VOICEVOX_URL", "http://localhost:50021"),
            "speaker_id": int(os.getenv("VOICEVOX_SPEAKER_ID", "20"))
        }
        
        # Discord設定
        self.config_data["discord"] = {
            "bot_token": os.getenv("DISCORD_BOT_TOKEN"),
            "guild_id": os.getenv("DISCORD_GUILD_ID")
        }
        
        # データベース設定
        self.config_data["database"] = {
            "url": os.getenv("DATABASE_URL", "sqlite:///setsuna_bot.db"),
            "max_connections": int(os.getenv("DATABASE_MAX_CONNECTIONS", "10"))
        }
        
        # ログ設定
        self.config_data["logging"] = {
            "level": os.getenv("LOG_LEVEL", "INFO"),
            "file_path": os.getenv("LOG_FILE_PATH", "logs/setsuna_bot.log")
        }
        
        # Google Search API設定
        self.config_data["google_search"] = {
            "api_key": os.getenv("GOOGLE_API_KEY"),
            "search_engine_id": os.getenv("GOOGLE_SEARCH_ENGINE_ID"),
            "daily_quota": int(os.getenv("GOOGLE_DAILY_QUOTA", "100"))
        }
    
    def _validate_config(self) -> ConfigValidationResult:
        """設定検証"""
        missing_keys = []
        warnings = []
        errors = []
        
        # 必須設定チェック
        required_configs = [
            ("openai.api_key", "OpenAI API Key"),
            ("google_search.api_key", "Google Search API Key"),
            ("google_search.search_engine_id", "Google Search Engine ID"),
        ]
        
        for config_key, description in required_configs:
            if not self._get_nested_config(config_key):
                missing_keys.append(f"{description} ({config_key})")
        
        # 推奨設定チェック
        recommended_configs = [
            ("voicevox.url", "VOICEVOX URL"),
        ]
        
        for config_key, description in recommended_configs:
            if not self._get_nested_config(config_key):
                warnings.append(f"{description} ({config_key}) が設定されていません")
        
        # 設定値検証
        if self.config_data["openai"]["api_key"]:
            if not self.config_data["openai"]["api_key"].startswith("sk-"):
                errors.append("OpenAI API Keyの形式が正しくありません")
        
        is_valid = len(missing_keys) == 0 and len(errors) == 0
        
        return ConfigValidationResult(
            is_valid=is_valid,
            missing_keys=missing_keys,
            warnings=warnings,
            errors=errors
        )
    
    def _get_nested_config(self, key: str) -> Any:
        """ネストした設定値取得"""
        keys = key.split(".")
        value = self.config_data
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return None
        
        return value
    
    def _print_initialization_status(self):
        """初期化状態表示"""
        print("[設定管理] 🚀 ConfigManager初期化完了")
        
        if self.validation_result.is_valid:
            print("[設定管理] ✅ 設定検証成功")
        else:
            print("[設定管理] ❌ 設定検証失敗")
            
            if self.validation_result.missing_keys:
                print("  必須設定不足:")
                for key in self.validation_result.missing_keys:
                    print(f"    - {key}")
            
            if self.validation_result.errors:
                print("  設定エラー:")
                for error in self.validation_result.errors:
                    print(f"    - {error}")
        
        if self.validation_result.warnings:
            print("  警告:")
            for warning in self.validation_result.warnings:
                print(f"    - {warning}")
    
    # OpenAI設定取得メソッド
    def get_openai_key(self) -> Optional[str]:
        """OpenAI API Key取得"""
        return self.config_data["openai"]["api_key"]
    
    def get_openai_organization(self) -> Optional[str]:
        """OpenAI Organization取得"""
        return self.config_data["openai"]["organization"]
    
    def get_openai_base_url(self) -> str:
        """OpenAI Base URL取得"""
        return self.config_data["openai"]["base_url"]
    
    def is_openai_configured(self) -> bool:
        """OpenAI設定確認"""
        return bool(self.get_openai_key())
    
    # VOICEVOX設定取得メソッド
    def get_voicevox_url(self) -> str:
        """VOICEVOX URL取得"""
        return self.config_data["voicevox"]["url"]
    
    def get_voicevox_speaker_id(self) -> int:
        """VOICEVOX Speaker ID取得"""
        return self.config_data["voicevox"]["speaker_id"]
    
    # Discord設定取得メソッド
    def get_discord_bot_token(self) -> Optional[str]:
        """Discord Bot Token取得"""
        return self.config_data["discord"]["bot_token"]
    
    def get_discord_guild_id(self) -> Optional[str]:
        """Discord Guild ID取得"""
        return self.config_data["discord"]["guild_id"]
    
    # データベース設定取得メソッド
    def get_database_url(self) -> str:
        """データベースURL取得"""
        return self.config_data["database"]["url"]
    
    def get_database_max_connections(self) -> int:
        """データベース最大接続数取得"""
        return self.config_data["database"]["max_connections"]
    
    # ログ設定取得メソッド
    def get_log_level(self) -> str:
        """ログレベル取得"""
        return self.config_data["logging"]["level"]
    
    def get_log_file_path(self) -> str:
        """ログファイルパス取得"""
        return self.config_data["logging"]["file_path"]
    
    # Google Search API設定取得メソッド
    def get_google_api_key(self) -> Optional[str]:
        """Google API Key取得"""
        return self.config_data["google_search"]["api_key"]
    
    def get_google_search_engine_id(self) -> Optional[str]:
        """Google Search Engine ID取得"""
        return self.config_data["google_search"]["search_engine_id"]
    
    def get_google_daily_quota(self) -> int:
        """Google検索日次クォータ取得"""
        return self.config_data["google_search"]["daily_quota"]
    
    def is_google_search_configured(self) -> bool:
        """Google検索設定確認"""
        return bool(self.get_google_api_key())
    
    # 設定確認メソッド
    def get_validation_result(self) -> ConfigValidationResult:
        """設定検証結果取得"""
        return self.validation_result
    
    def is_valid_config(self) -> bool:
        """設定有効性確認"""
        return self.validation_result.is_valid
    
    def get_config_summary(self) -> Dict[str, Any]:
        """設定サマリー取得"""
        return {
            "openai_configured": self.is_openai_configured(),
            "voicevox_url": self.get_voicevox_url(),
            "discord_configured": bool(self.get_discord_bot_token()),
            "google_search_configured": self.is_google_search_configured(),
            "database_url": self.get_database_url(),
            "log_level": self.get_log_level(),
            "validation_result": {
                "is_valid": self.validation_result.is_valid,
                "missing_keys": self.validation_result.missing_keys,
                "warnings": self.validation_result.warnings,
                "errors": self.validation_result.errors
            }
        }
    
    def reload_config(self):
        """設定再読み込み"""
        print("[設定管理] 🔄 設定再読み込み開始")
        self._load_environment_variables()
        self.validation_result = self._validate_config()
        self._print_initialization_status()


# グローバルインスタンス（シングルトンパターン）
_config_manager_instance = None

def get_config_manager() -> ConfigManager:
    """ConfigManager グローバルインスタンス取得"""
    global _config_manager_instance
    if _config_manager_instance is None:
        _config_manager_instance = ConfigManager()
    return _config_manager_instance

def reload_global_config():
    """グローバル設定再読み込み"""
    global _config_manager_instance
    if _config_manager_instance:
        _config_manager_instance.reload_config()
    else:
        _config_manager_instance = ConfigManager()


# テスト用コード
if __name__ == "__main__":
    print("=== ConfigManager テスト ===")
    
    # ConfigManager初期化
    config = ConfigManager()
    
    # 設定確認
    print(f"\n📋 設定サマリー:")
    summary = config.get_config_summary()
    
    for key, value in summary.items():
        if key != "validation_result":
            print(f"  {key}: {value}")
    
    # 検証結果
    print(f"\n🔍 検証結果:")
    validation = summary["validation_result"]
    print(f"  有効: {validation['is_valid']}")
    
    if validation["missing_keys"]:
        print(f"  不足キー: {validation['missing_keys']}")
    
    if validation["warnings"]:
        print(f"  警告: {validation['warnings']}")
    
    if validation["errors"]:
        print(f"  エラー: {validation['errors']}")
    
    # OpenAI設定テスト
    print(f"\n🤖 OpenAI設定:")
    print(f"  API Key: {'設定済み' if config.is_openai_configured() else '未設定'}")
    print(f"  Base URL: {config.get_openai_base_url()}")
    
    # VOICEVOX設定テスト
    print(f"\n🎵 VOICEVOX設定:")
    print(f"  URL: {config.get_voicevox_url()}")
    print(f"  Speaker ID: {config.get_voicevox_speaker_id()}")
    
    # Google Search設定テスト
    print(f"\n🔍 Google Search設定:")
    print(f"  API Key: {'設定済み' if config.is_google_search_configured() else '未設定'}")
    print(f"  Search Engine ID: {'設定済み' if config.get_google_search_engine_id() else '未設定'}")
    print(f"  Daily Quota: {config.get_google_daily_quota()}")
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自動バックアップシステム - せつなBot D案 Phase 2
重要データの自動バックアップ・復旧機能
"""

import os
import shutil
import json
import hashlib
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import zipfile
import tempfile

from logging_system import get_logger, get_monitor


class BackupManager:
    """バックアップ管理システム"""
    
    def __init__(self, base_dir: str = "/mnt/d/setsuna_bot", 
                 backup_dir: str = "/mnt/d/setsuna_bot/backups"):
        """
        初期化
        
        Args:
            base_dir: プロジェクトのベースディレクトリ
            backup_dir: バックアップ保存ディレクトリ
        """
        self.logger = get_logger()
        self.monitor = get_monitor()
        
        self.base_dir = Path(base_dir)
        self.backup_dir = Path(backup_dir)
        
        # バックアップディレクトリ作成
        self.backup_dir.mkdir(exist_ok=True)
        (self.backup_dir / "daily").mkdir(exist_ok=True)
        (self.backup_dir / "weekly").mkdir(exist_ok=True)
        (self.backup_dir / "monthly").mkdir(exist_ok=True)
        (self.backup_dir / "emergency").mkdir(exist_ok=True)
        
        # バックアップ対象ファイル定義
        self.backup_targets = {
            "youtube_knowledge": "youtube_knowledge_system/data/unified_knowledge_db.json",
            "user_preferences": "data/user_preferences.json",
            "conversation_context": "data/conversation_context.json",
            "multi_turn_conversations": "data/multi_turn_conversations.json",
            "video_conversation_history": "data/video_conversation_history.json",
            "setsuna_memory": "character/setsuna_memory_data.json",
            "setsuna_responses": "character/setsuna_responses.json",
            "setsuna_projects": "character/setsuna_projects.json",
            "response_cache": "response_cache/response_cache.json",
            "cache_stats": "response_cache/cache_stats.json"
        }
        
        # スケジューラー設定
        self.scheduler_running = False
        self.scheduler_thread = None
        
        self.logger.info("backup_system", "__init__", "バックアップシステム初期化完了", {
            "base_dir": str(self.base_dir),
            "backup_dir": str(self.backup_dir),
            "targets_count": len(self.backup_targets)
        })
    
    @get_monitor().monitor_function("create_backup")
    def create_backup(self, backup_type: str = "manual", 
                     compress: bool = True, 
                     verify: bool = True) -> Optional[Path]:
        """
        バックアップを作成
        
        Args:
            backup_type: バックアップタイプ (manual/daily/weekly/monthly/emergency)
            compress: ZIP圧縮するか
            verify: バックアップ後に検証するか
            
        Returns:
            Path: 作成されたバックアップのパス
        """
        self.logger.info("backup_system", "create_backup", f"バックアップ作成開始: {backup_type}")
        
        try:
            # バックアップディレクトリ決定
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if backup_type in ["daily", "weekly", "monthly"]:
                backup_path = self.backup_dir / backup_type / timestamp
            else:
                backup_path = self.backup_dir / "emergency" / f"{backup_type}_{timestamp}"
            
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # バックアップマニフェスト作成
            manifest = {
                "timestamp": timestamp,
                "backup_type": backup_type,
                "created_at": datetime.now().isoformat(),
                "files": {},
                "total_size": 0,
                "compressed": compress,
                "verified": verify
            }
            
            copied_files = 0
            total_size = 0
            
            # 各ファイルをバックアップ
            for name, relative_path in self.backup_targets.items():
                source_path = self.base_dir / relative_path
                
                if not source_path.exists():
                    self.logger.warning("backup_system", "create_backup", 
                                      f"バックアップ対象ファイルが存在しません: {relative_path}")
                    continue
                
                # ファイルコピー
                dest_path = backup_path / relative_path
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                
                shutil.copy2(source_path, dest_path)
                
                # ファイル情報記録
                file_size = source_path.stat().st_size
                file_hash = self._calculate_file_hash(source_path)
                
                manifest["files"][name] = {
                    "path": relative_path,
                    "size": file_size,
                    "hash": file_hash,
                    "modified": datetime.fromtimestamp(source_path.stat().st_mtime).isoformat()
                }
                
                copied_files += 1
                total_size += file_size
                
                self.logger.debug("backup_system", "create_backup", 
                                f"ファイルコピー完了: {name}", {
                                    "source": str(source_path),
                                    "dest": str(dest_path),
                                    "size": file_size
                                })
            
            manifest["total_size"] = total_size
            manifest["files_count"] = copied_files
            
            # マニフェストファイル保存
            manifest_path = backup_path / "backup_manifest.json"
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, ensure_ascii=False, indent=2)
            
            self.logger.info("backup_system", "create_backup", 
                           f"バックアップファイル作成完了: {copied_files}件", {
                               "total_size_mb": total_size / 1024 / 1024,
                               "backup_path": str(backup_path)
                           })
            
            # ZIP圧縮
            final_path = backup_path
            if compress:
                final_path = self._compress_backup(backup_path)
                if final_path:
                    # 元のディレクトリを削除
                    shutil.rmtree(backup_path)
            
            # バックアップ検証
            if verify and final_path:
                if self._verify_backup(final_path):
                    self.logger.info("backup_system", "create_backup", "バックアップ検証成功")
                else:
                    self.logger.error("backup_system", "create_backup", "バックアップ検証失敗")
            
            return final_path
            
        except Exception as e:
            self.logger.error("backup_system", "create_backup", f"バックアップ作成エラー: {e}")
            return None
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """ファイルのSHA256ハッシュを計算"""
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            self.logger.error("backup_system", "_calculate_file_hash", f"ハッシュ計算エラー: {e}")
            return ""
    
    def _compress_backup(self, backup_path: Path) -> Optional[Path]:
        """バックアップを ZIP 圧縮"""
        try:
            zip_path = backup_path.with_suffix('.zip')
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
                for file_path in backup_path.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(backup_path)
                        zipf.write(file_path, arcname)
            
            # 圧縮率計算
            original_size = sum(f.stat().st_size for f in backup_path.rglob('*') if f.is_file())
            compressed_size = zip_path.stat().st_size
            compression_ratio = (1 - compressed_size / original_size) * 100
            
            self.logger.info("backup_system", "_compress_backup", "バックアップ圧縮完了", {
                "original_size_mb": original_size / 1024 / 1024,
                "compressed_size_mb": compressed_size / 1024 / 1024,
                "compression_ratio": compression_ratio
            })
            
            return zip_path
            
        except Exception as e:
            self.logger.error("backup_system", "_compress_backup", f"圧縮エラー: {e}")
            return None
    
    def _verify_backup(self, backup_path: Path) -> bool:
        """バックアップの整合性を検証"""
        try:
            if backup_path.suffix == '.zip':
                return self._verify_compressed_backup(backup_path)
            else:
                return self._verify_uncompressed_backup(backup_path)
        except Exception as e:
            self.logger.error("backup_system", "_verify_backup", f"検証エラー: {e}")
            return False
    
    def _verify_compressed_backup(self, zip_path: Path) -> bool:
        """圧縮バックアップの検証"""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                # ZIPファイルの整合性チェック
                bad_file = zipf.testzip()
                if bad_file:
                    self.logger.error("backup_system", "_verify_compressed_backup", 
                                    f"破損ファイル検出: {bad_file}")
                    return False
                
                # マニフェストファイル確認
                try:
                    manifest_data = zipf.read('backup_manifest.json')
                    manifest = json.loads(manifest_data.decode('utf-8'))
                    
                    # ファイル数確認
                    expected_files = len(manifest.get("files", {})) + 1  # +1 for manifest
                    actual_files = len(zipf.namelist())
                    
                    if expected_files != actual_files:
                        self.logger.error("backup_system", "_verify_compressed_backup", 
                                        f"ファイル数不一致: 期待{expected_files}, 実際{actual_files}")
                        return False
                    
                    self.logger.debug("backup_system", "_verify_compressed_backup", 
                                    f"ZIP検証成功: {actual_files}ファイル")
                    return True
                    
                except KeyError:
                    self.logger.error("backup_system", "_verify_compressed_backup", 
                                    "マニフェストファイルが見つかりません")
                    return False
                    
        except Exception as e:
            self.logger.error("backup_system", "_verify_compressed_backup", f"ZIP検証エラー: {e}")
            return False
    
    def _verify_uncompressed_backup(self, backup_path: Path) -> bool:
        """非圧縮バックアップの検証"""
        try:
            manifest_path = backup_path / "backup_manifest.json"
            if not manifest_path.exists():
                self.logger.error("backup_system", "_verify_uncompressed_backup", 
                                "マニフェストファイルが存在しません")
                return False
            
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
            
            # 各ファイルの検証
            for name, file_info in manifest.get("files", {}).items():
                file_path = backup_path / file_info["path"]
                
                if not file_path.exists():
                    self.logger.error("backup_system", "_verify_uncompressed_backup", 
                                    f"ファイルが存在しません: {file_info['path']}")
                    return False
                
                # ファイルサイズ確認
                actual_size = file_path.stat().st_size
                expected_size = file_info["size"]
                
                if actual_size != expected_size:
                    self.logger.error("backup_system", "_verify_uncompressed_backup", 
                                    f"ファイルサイズ不一致: {file_info['path']}")
                    return False
                
                # ハッシュ確認
                actual_hash = self._calculate_file_hash(file_path)
                expected_hash = file_info["hash"]
                
                if actual_hash != expected_hash:
                    self.logger.error("backup_system", "_verify_uncompressed_backup", 
                                    f"ハッシュ不一致: {file_info['path']}")
                    return False
            
            self.logger.debug("backup_system", "_verify_uncompressed_backup", 
                            f"検証成功: {len(manifest.get('files', {}))}ファイル")
            return True
            
        except Exception as e:
            self.logger.error("backup_system", "_verify_uncompressed_backup", f"検証エラー: {e}")
            return False
    
    def list_backups(self, backup_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """バックアップ一覧を取得"""
        try:
            backups = []
            
            search_dirs = [self.backup_dir / "emergency"]
            if backup_type:
                if backup_type in ["daily", "weekly", "monthly"]:
                    search_dirs = [self.backup_dir / backup_type]
            else:
                search_dirs.extend([
                    self.backup_dir / "daily",
                    self.backup_dir / "weekly", 
                    self.backup_dir / "monthly"
                ])
            
            for search_dir in search_dirs:
                if not search_dir.exists():
                    continue
                
                for item in search_dir.iterdir():
                    if item.is_dir():
                        manifest_path = item / "backup_manifest.json"
                    elif item.suffix == '.zip':
                        # ZIP内のマニフェスト確認
                        try:
                            with zipfile.ZipFile(item, 'r') as zipf:
                                manifest_data = zipf.read('backup_manifest.json')
                                manifest = json.loads(manifest_data.decode('utf-8'))
                        except:
                            continue
                    else:
                        continue
                    
                    if item.is_dir() and manifest_path.exists():
                        with open(manifest_path, 'r', encoding='utf-8') as f:
                            manifest = json.load(f)
                    
                    backup_info = {
                        "path": str(item),
                        "name": item.name,
                        "type": manifest.get("backup_type", "unknown"),
                        "created_at": manifest.get("created_at", ""),
                        "files_count": manifest.get("files_count", 0),
                        "total_size": manifest.get("total_size", 0),
                        "compressed": manifest.get("compressed", False),
                        "verified": manifest.get("verified", False)
                    }
                    backups.append(backup_info)
            
            # 作成日時で降順ソート
            backups.sort(key=lambda x: x["created_at"], reverse=True)
            
            return backups
            
        except Exception as e:
            self.logger.error("backup_system", "list_backups", f"バックアップ一覧取得エラー: {e}")
            return []
    
    def cleanup_old_backups(self, retention_days: int = 30):
        """古いバックアップを削除"""
        try:
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            deleted_count = 0
            deleted_size = 0
            
            for backup_type in ["daily", "weekly", "monthly", "emergency"]:
                backup_type_dir = self.backup_dir / backup_type
                if not backup_type_dir.exists():
                    continue
                
                for item in backup_type_dir.iterdir():
                    # ファイル/ディレクトリの作成日時確認
                    item_time = datetime.fromtimestamp(item.stat().st_mtime)
                    
                    if item_time < cutoff_date:
                        item_size = self._get_size(item)
                        
                        if item.is_dir():
                            shutil.rmtree(item)
                        else:
                            item.unlink()
                        
                        deleted_count += 1
                        deleted_size += item_size
                        
                        self.logger.info("backup_system", "cleanup_old_backups", 
                                       f"古いバックアップ削除: {item.name}")
            
            self.logger.info("backup_system", "cleanup_old_backups", 
                           f"クリーンアップ完了: {deleted_count}件削除", {
                               "deleted_size_mb": deleted_size / 1024 / 1024,
                               "retention_days": retention_days
                           })
            
        except Exception as e:
            self.logger.error("backup_system", "cleanup_old_backups", f"クリーンアップエラー: {e}")
    
    def _get_size(self, path: Path) -> int:
        """パス（ファイル/ディレクトリ）のサイズを取得"""
        if path.is_file():
            return path.stat().st_size
        elif path.is_dir():
            return sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
        return 0


# テスト用関数
if __name__ == "__main__":
    print("🧪 バックアップシステムテスト開始")
    
    backup_manager = BackupManager()
    
    # バックアップ作成テスト
    print("📦 テストバックアップ作成中...")
    backup_path = backup_manager.create_backup("test", compress=True, verify=True)
    
    if backup_path:
        print(f"✅ バックアップ作成成功: {backup_path}")
        
        # バックアップ一覧表示
        backups = backup_manager.list_backups()
        print(f"📋 バックアップ一覧: {len(backups)}件")
        for backup in backups[:3]:  # 最新3件表示
            print(f"   - {backup['name']}: {backup['files_count']}ファイル, {backup['total_size']/1024:.1f}KB")
    else:
        print("❌ バックアップ作成失敗")
    
    print("✅ バックアップシステムテスト完了")
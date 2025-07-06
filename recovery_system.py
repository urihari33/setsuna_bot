#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
復旧システム - せつなBot D案 Phase 2
バックアップからのデータ復旧機能
"""

import os
import shutil
import json
import zipfile
import tempfile
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from backup_system import BackupManager
from logging_system import get_logger, get_monitor


class RecoveryManager:
    """復旧管理システム"""
    
    def __init__(self, backup_manager: BackupManager):
        """
        初期化
        
        Args:
            backup_manager: BackupManagerインスタンス
        """
        self.logger = get_logger()
        self.monitor = get_monitor()
        self.backup_manager = backup_manager
        
        self.logger.info("recovery_system", "__init__", "復旧システム初期化完了")
    
    @get_monitor().monitor_function("restore_from_backup")
    def restore_from_backup(self, backup_path: str, 
                           target_files: Optional[List[str]] = None,
                           create_backup_before_restore: bool = True,
                           dry_run: bool = False) -> bool:
        """
        バックアップからデータを復旧
        
        Args:
            backup_path: 復旧元バックアップパス
            target_files: 復旧対象ファイル（Noneの場合は全ファイル）
            create_backup_before_restore: 復旧前に現在の状態をバックアップするか
            dry_run: 実際に復旧せずにテストするか
            
        Returns:
            bool: 復旧成功かどうか
        """
        backup_path = Path(backup_path)
        
        self.logger.info("recovery_system", "restore_from_backup", 
                        f"復旧処理開始: {backup_path.name}", {
                            "backup_path": str(backup_path),
                            "target_files": target_files,
                            "dry_run": dry_run
                        })
        
        if not backup_path.exists():
            self.logger.error("recovery_system", "restore_from_backup", 
                            f"バックアップファイルが存在しません: {backup_path}")
            return False
        
        try:
            # 復旧前バックアップの作成
            pre_restore_backup = None
            if create_backup_before_restore and not dry_run:
                pre_restore_backup = self._create_pre_restore_backup()
                if not pre_restore_backup:
                    self.logger.warning("recovery_system", "restore_from_backup", 
                                      "復旧前バックアップの作成に失敗しました")
            
            # バックアップの解析
            manifest = self._load_backup_manifest(backup_path)
            if not manifest:
                self.logger.error("recovery_system", "restore_from_backup", 
                                "バックアップマニフェストの読み込みに失敗")
                return False
            
            # 復旧対象ファイルの決定
            files_to_restore = self._determine_restore_targets(manifest, target_files)
            
            if not files_to_restore:
                self.logger.warning("recovery_system", "restore_from_backup", 
                                  "復旧対象ファイルがありません")
                return True
            
            # 復旧実行
            success = self._execute_restore(backup_path, files_to_restore, dry_run)
            
            if success:
                self.logger.info("recovery_system", "restore_from_backup", 
                               f"復旧完了: {len(files_to_restore)}ファイル", {
                                   "restored_files": [f["name"] for f in files_to_restore],
                                   "pre_restore_backup": str(pre_restore_backup) if pre_restore_backup else None
                               })
            else:
                self.logger.error("recovery_system", "restore_from_backup", "復旧処理中にエラーが発生")
            
            return success
            
        except Exception as e:
            self.logger.error("recovery_system", "restore_from_backup", f"復旧エラー: {e}")
            return False
    
    def _create_pre_restore_backup(self) -> Optional[Path]:
        """復旧前の現在状態をバックアップ"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = self.backup_manager.create_backup(
                backup_type=f"pre_restore_{timestamp}",
                compress=True,
                verify=False  # 高速化のため検証スキップ
            )
            
            if backup_path:
                self.logger.info("recovery_system", "_create_pre_restore_backup", 
                               f"復旧前バックアップ作成: {backup_path.name}")
            
            return backup_path
            
        except Exception as e:
            self.logger.error("recovery_system", "_create_pre_restore_backup", 
                            f"復旧前バックアップエラー: {e}")
            return None
    
    def _load_backup_manifest(self, backup_path: Path) -> Optional[Dict[str, Any]]:
        """バックアップマニフェストを読み込み"""
        try:
            if backup_path.suffix == '.zip':
                # ZIP形式の場合
                with zipfile.ZipFile(backup_path, 'r') as zipf:
                    manifest_data = zipf.read('backup_manifest.json')
                    return json.loads(manifest_data.decode('utf-8'))
            else:
                # ディレクトリ形式の場合
                manifest_path = backup_path / 'backup_manifest.json'
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
                    
        except Exception as e:
            self.logger.error("recovery_system", "_load_backup_manifest", 
                            f"マニフェスト読み込みエラー: {e}")
            return None
    
    def _determine_restore_targets(self, manifest: Dict[str, Any], 
                                 target_files: Optional[List[str]]) -> List[Dict[str, Any]]:
        """復旧対象ファイルを決定"""
        all_files = manifest.get("files", {})
        
        if target_files is None:
            # 全ファイルを対象
            return [{"name": name, "info": info} for name, info in all_files.items()]
        else:
            # 指定されたファイルのみ
            selected_files = []
            for target in target_files:
                if target in all_files:
                    selected_files.append({"name": target, "info": all_files[target]})
                else:
                    self.logger.warning("recovery_system", "_determine_restore_targets", 
                                      f"指定されたファイルがバックアップに存在しません: {target}")
            
            return selected_files
    
    def _execute_restore(self, backup_path: Path, files_to_restore: List[Dict[str, Any]], 
                        dry_run: bool) -> bool:
        """復旧を実行"""
        try:
            if backup_path.suffix == '.zip':
                return self._restore_from_zip(backup_path, files_to_restore, dry_run)
            else:
                return self._restore_from_directory(backup_path, files_to_restore, dry_run)
                
        except Exception as e:
            self.logger.error("recovery_system", "_execute_restore", f"復旧実行エラー: {e}")
            return False
    
    def _restore_from_zip(self, zip_path: Path, files_to_restore: List[Dict[str, Any]], 
                         dry_run: bool) -> bool:
        """ZIP形式バックアップからの復旧"""
        try:
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                for file_info in files_to_restore:
                    file_name = file_info["name"]
                    file_data = file_info["info"]
                    source_path = file_data["path"]
                    target_path = self.backup_manager.base_dir / source_path
                    
                    if dry_run:
                        self.logger.info("recovery_system", "_restore_from_zip", 
                                       f"[DRY RUN] 復旧対象: {source_path} → {target_path}")
                        continue
                    
                    # ディレクトリ作成
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # ファイル復旧
                    with zipf.open(source_path) as source_file:
                        with open(target_path, 'wb') as target_file:
                            shutil.copyfileobj(source_file, target_file)
                    
                    self.logger.debug("recovery_system", "_restore_from_zip", 
                                    f"ファイル復旧完了: {source_path}")
            
            return True
            
        except Exception as e:
            self.logger.error("recovery_system", "_restore_from_zip", f"ZIP復旧エラー: {e}")
            return False
    
    def _restore_from_directory(self, backup_dir: Path, files_to_restore: List[Dict[str, Any]], 
                               dry_run: bool) -> bool:
        """ディレクトリ形式バックアップからの復旧"""
        try:
            for file_info in files_to_restore:
                file_name = file_info["name"]
                file_data = file_info["info"]
                source_path = backup_dir / file_data["path"]
                target_path = self.backup_manager.base_dir / file_data["path"]
                
                if not source_path.exists():
                    self.logger.warning("recovery_system", "_restore_from_directory", 
                                      f"復旧元ファイルが存在しません: {source_path}")
                    continue
                
                if dry_run:
                    self.logger.info("recovery_system", "_restore_from_directory", 
                                   f"[DRY RUN] 復旧対象: {source_path} → {target_path}")
                    continue
                
                # ディレクトリ作成
                target_path.parent.mkdir(parents=True, exist_ok=True)
                
                # ファイル復旧
                shutil.copy2(source_path, target_path)
                
                self.logger.debug("recovery_system", "_restore_from_directory", 
                                f"ファイル復旧完了: {file_data['path']}")
            
            return True
            
        except Exception as e:
            self.logger.error("recovery_system", "_restore_from_directory", 
                            f"ディレクトリ復旧エラー: {e}")
            return False
    
    def list_restorable_backups(self) -> List[Dict[str, Any]]:
        """復旧可能なバックアップ一覧を取得"""
        return self.backup_manager.list_backups()
    
    def verify_backup_integrity(self, backup_path: str) -> Tuple[bool, Dict[str, Any]]:
        """バックアップの整合性を詳細確認"""
        backup_path = Path(backup_path)
        
        self.logger.info("recovery_system", "verify_backup_integrity", 
                        f"整合性確認開始: {backup_path.name}")
        
        try:
            # 基本的な整合性確認
            basic_check = self.backup_manager._verify_backup(backup_path)
            
            # 詳細な整合性確認
            manifest = self._load_backup_manifest(backup_path)
            if not manifest:
                return False, {"error": "マニフェスト読み込み失敗"}
            
            verification_result = {
                "basic_integrity": basic_check,
                "files_count": len(manifest.get("files", {})),
                "total_size": manifest.get("total_size", 0),
                "created_at": manifest.get("created_at", ""),
                "backup_type": manifest.get("backup_type", "unknown"),
                "file_details": []
            }
            
            # 各ファイルの詳細確認
            for file_name, file_info in manifest.get("files", {}).items():
                file_detail = {
                    "name": file_name,
                    "path": file_info["path"],
                    "size": file_info["size"],
                    "hash": file_info["hash"],
                    "exists_in_current": False,
                    "size_match": False,
                    "hash_match": False
                }
                
                # 現在のファイルと比較
                current_file = self.backup_manager.base_dir / file_info["path"]
                if current_file.exists():
                    file_detail["exists_in_current"] = True
                    
                    current_size = current_file.stat().st_size
                    file_detail["size_match"] = (current_size == file_info["size"])
                    
                    current_hash = self.backup_manager._calculate_file_hash(current_file)
                    file_detail["hash_match"] = (current_hash == file_info["hash"])
                
                verification_result["file_details"].append(file_detail)
            
            overall_success = basic_check
            
            self.logger.info("recovery_system", "verify_backup_integrity", 
                           f"整合性確認完了: {backup_path.name}", {
                               "success": overall_success,
                               "files_count": verification_result["files_count"]
                           })
            
            return overall_success, verification_result
            
        except Exception as e:
            self.logger.error("recovery_system", "verify_backup_integrity", 
                            f"整合性確認エラー: {e}")
            return False, {"error": str(e)}
    
    def get_recovery_recommendations(self) -> List[Dict[str, Any]]:
        """復旧推奨事項を取得"""
        try:
            recommendations = []
            
            # 利用可能なバックアップ一覧取得
            backups = self.list_restorable_backups()
            
            if not backups:
                recommendations.append({
                    "type": "warning",
                    "message": "利用可能なバックアップがありません",
                    "action": "まずバックアップを作成してください"
                })
                return recommendations
            
            # 最新バックアップの確認
            latest_backup = backups[0]  # 既に日付順でソート済み
            backup_age = datetime.now() - datetime.fromisoformat(latest_backup["created_at"])
            
            if backup_age.days > 7:
                recommendations.append({
                    "type": "warning",
                    "message": f"最新バックアップが{backup_age.days}日前です",
                    "action": "新しいバックアップの作成を推奨します",
                    "backup_info": latest_backup
                })
            
            # 各ファイルの状態確認
            for backup in backups[:3]:  # 最新3件をチェック
                integrity_check, details = self.verify_backup_integrity(backup["path"])
                
                if not integrity_check:
                    recommendations.append({
                        "type": "error",
                        "message": f"バックアップ '{backup['name']}' に整合性の問題があります",
                        "action": "このバックアップからの復旧は推奨されません",
                        "backup_info": backup
                    })
                else:
                    # 現在のファイルとの差分確認
                    changed_files = []
                    for file_detail in details.get("file_details", []):
                        if (file_detail["exists_in_current"] and 
                            not file_detail["hash_match"]):
                            changed_files.append(file_detail["name"])
                    
                    if changed_files:
                        recommendations.append({
                            "type": "info",
                            "message": f"バックアップ '{backup['name']}' から {len(changed_files)}ファイルの復旧が可能",
                            "action": "変更されたファイルの復旧を検討してください",
                            "backup_info": backup,
                            "changed_files": changed_files
                        })
            
            return recommendations
            
        except Exception as e:
            self.logger.error("recovery_system", "get_recovery_recommendations", 
                            f"推奨事項取得エラー: {e}")
            return [{"type": "error", "message": f"推奨事項の取得に失敗: {e}"}]


# テスト用関数
if __name__ == "__main__":
    print("🧪 復旧システムテスト開始")
    
    # バックアップマネージャー初期化
    backup_manager = BackupManager()
    
    # 復旧マネージャー初期化
    recovery_manager = RecoveryManager(backup_manager)
    
    try:
        # 利用可能なバックアップ一覧
        backups = recovery_manager.list_restorable_backups()
        print(f"📋 利用可能なバックアップ: {len(backups)}件")
        
        if backups:
            latest_backup = backups[0]
            print(f"📦 最新バックアップ: {latest_backup['name']}")
            
            # 整合性確認テスト
            print("🔍 整合性確認テスト実行中...")
            integrity_ok, details = recovery_manager.verify_backup_integrity(latest_backup["path"])
            
            if integrity_ok:
                print("✅ 整合性確認成功")
                print(f"   - ファイル数: {details['files_count']}")
                print(f"   - 総サイズ: {details['total_size']/1024:.1f}KB")
            else:
                print("❌ 整合性確認失敗")
            
            # ドライランテスト
            print("\n🔧 復旧ドライランテスト実行中...")
            dry_run_success = recovery_manager.restore_from_backup(
                latest_backup["path"],
                target_files=None,
                dry_run=True
            )
            
            if dry_run_success:
                print("✅ ドライラン成功")
            else:
                print("❌ ドライラン失敗")
        
        # 復旧推奨事項
        print("\n💡 復旧推奨事項:")
        recommendations = recovery_manager.get_recovery_recommendations()
        for i, rec in enumerate(recommendations, 1):
            rec_type = rec["type"]
            message = rec["message"]
            action = rec.get("action", "")
            
            emoji = {"info": "ℹ️", "warning": "⚠️", "error": "❌"}.get(rec_type, "📝")
            print(f"{i}. {emoji} {message}")
            if action:
                print(f"   推奨アクション: {action}")
        
        print("\n✅ 復旧システムテスト完了")
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
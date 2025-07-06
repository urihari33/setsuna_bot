#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ログローテーション機能 - せつなBot D案 Phase 1
日別・サイズ別のログファイル管理システム
"""

import os
import gzip
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional
import threading
import time


class LogRotationManager:
    """ログローテーション管理クラス"""
    
    def __init__(self, log_dir: str = "/mnt/d/setsuna_bot/logs", 
                 max_file_size_mb: int = 50,
                 max_files_per_day: int = 10,
                 retention_days: int = 30,
                 compress_old_logs: bool = True):
        """
        初期化
        
        Args:
            log_dir: ログディレクトリ
            max_file_size_mb: ログファイルの最大サイズ（MB）
            max_files_per_day: 1日の最大ファイル数
            retention_days: ログ保持日数
            compress_old_logs: 古いログを圧縮するか
        """
        self.log_dir = Path(log_dir)
        self.max_file_size = max_file_size_mb * 1024 * 1024  # バイト単位
        self.max_files_per_day = max_files_per_day
        self.retention_days = retention_days
        self.compress_old_logs = compress_old_logs
        
        # バックグラウンドローテーション用
        self.rotation_thread = None
        self.rotation_running = False
        
        print(f"🔄 [LogRotation] ログローテーション管理初期化完了")
        print(f"   - ディレクトリ: {self.log_dir}")
        print(f"   - 最大ファイルサイズ: {max_file_size_mb}MB")
        print(f"   - 保持日数: {retention_days}日")
    
    def should_rotate_file(self, log_file_path: Path) -> bool:
        """
        ファイルがローテーション対象かチェック
        
        Args:
            log_file_path: ログファイルパス
            
        Returns:
            bool: ローテーションが必要かどうか
        """
        if not log_file_path.exists():
            return False
        
        # ファイルサイズチェック
        file_size = log_file_path.stat().st_size
        if file_size >= self.max_file_size:
            print(f"🔄 [LogRotation] サイズ超過によるローテーション対象: {log_file_path.name} ({file_size/1024/1024:.1f}MB)")
            return True
        
        return False
    
    def rotate_log_file(self, log_file_path: Path) -> Optional[Path]:
        """
        ログファイルをローテーション
        
        Args:
            log_file_path: ローテーション対象ファイル
            
        Returns:
            Path: 新しいローテーション後ファイルパス
        """
        if not log_file_path.exists():
            return None
        
        try:
            # ファイル名から日付を抽出
            file_stem = log_file_path.stem  # 拡張子なしのファイル名
            file_suffix = log_file_path.suffix  # 拡張子
            
            # 今日の日付でローテーション番号を決定
            today = datetime.now().strftime("%Y-%m-%d")
            
            # 既存のローテーションファイル数をカウント
            rotation_files = list(self.log_dir.glob(f"{file_stem}_*{file_suffix}"))
            rotation_number = len(rotation_files) + 1
            
            # 最大ファイル数チェック
            if rotation_number > self.max_files_per_day:
                print(f"⚠️ [LogRotation] 1日の最大ファイル数超過: {rotation_number}/{self.max_files_per_day}")
                # 最も古いファイルを削除
                oldest_file = min(rotation_files, key=lambda f: f.stat().st_mtime)
                oldest_file.unlink()
                print(f"🗑️ [LogRotation] 古いファイル削除: {oldest_file.name}")
                rotation_number = self.max_files_per_day
            
            # ローテーション後のファイル名
            rotated_file_name = f"{file_stem}_{today}_{rotation_number:02d}{file_suffix}"
            rotated_file_path = self.log_dir / rotated_file_name
            
            # ファイル移動
            shutil.move(str(log_file_path), str(rotated_file_path))
            print(f"🔄 [LogRotation] ファイルローテーション完了: {log_file_path.name} → {rotated_file_path.name}")
            
            # 圧縮処理
            if self.compress_old_logs:
                compressed_path = self._compress_log_file(rotated_file_path)
                if compressed_path:
                    rotated_file_path.unlink()  # 元ファイル削除
                    return compressed_path
            
            return rotated_file_path
            
        except Exception as e:
            print(f"❌ [LogRotation] ローテーションエラー: {e}")
            return None
    
    def _compress_log_file(self, log_file_path: Path) -> Optional[Path]:
        """
        ログファイルを圧縮
        
        Args:
            log_file_path: 圧縮対象ファイル
            
        Returns:
            Path: 圧縮後ファイルパス
        """
        try:
            compressed_path = log_file_path.with_suffix(log_file_path.suffix + '.gz')
            
            with open(log_file_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            original_size = log_file_path.stat().st_size
            compressed_size = compressed_path.stat().st_size
            compression_ratio = (1 - compressed_size / original_size) * 100
            
            print(f"📦 [LogRotation] ファイル圧縮完了: {log_file_path.name}")
            print(f"   - 元サイズ: {original_size/1024:.1f}KB → 圧縮後: {compressed_size/1024:.1f}KB")
            print(f"   - 圧縮率: {compression_ratio:.1f}%")
            
            return compressed_path
            
        except Exception as e:
            print(f"❌ [LogRotation] 圧縮エラー: {e}")
            return None
    
    def cleanup_old_logs(self):
        """古いログファイルを削除"""
        try:
            cutoff_date = datetime.now() - timedelta(days=self.retention_days)
            cutoff_timestamp = cutoff_date.timestamp()
            
            deleted_count = 0
            total_size_deleted = 0
            
            # すべてのログファイルをチェック
            for log_file in self.log_dir.glob("*.log*"):
                if log_file.stat().st_mtime < cutoff_timestamp:
                    file_size = log_file.stat().st_size
                    log_file.unlink()
                    deleted_count += 1
                    total_size_deleted += file_size
                    print(f"🗑️ [LogRotation] 古いファイル削除: {log_file.name}")
            
            if deleted_count > 0:
                print(f"✅ [LogRotation] クリーンアップ完了: {deleted_count}件, {total_size_deleted/1024/1024:.1f}MB削除")
            else:
                print("ℹ️ [LogRotation] 削除対象の古いファイルなし")
                
        except Exception as e:
            print(f"❌ [LogRotation] クリーンアップエラー: {e}")
    
    def get_log_statistics(self) -> dict:
        """ログファイルの統計情報を取得"""
        try:
            log_files = list(self.log_dir.glob("*.log*"))
            
            if not log_files:
                return {
                    "total_files": 0,
                    "total_size_mb": 0,
                    "oldest_file": None,
                    "newest_file": None
                }
            
            total_size = sum(f.stat().st_size for f in log_files)
            oldest_file = min(log_files, key=lambda f: f.stat().st_mtime)
            newest_file = max(log_files, key=lambda f: f.stat().st_mtime)
            
            return {
                "total_files": len(log_files),
                "total_size_mb": total_size / 1024 / 1024,
                "oldest_file": {
                    "name": oldest_file.name,
                    "date": datetime.fromtimestamp(oldest_file.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                },
                "newest_file": {
                    "name": newest_file.name,
                    "date": datetime.fromtimestamp(newest_file.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                }
            }
            
        except Exception as e:
            print(f"❌ [LogRotation] 統計情報取得エラー: {e}")
            return {}
    
    def start_background_rotation(self, check_interval_minutes: int = 60):
        """
        バックグラウンドでのローテーションチェック開始
        
        Args:
            check_interval_minutes: チェック間隔（分）
        """
        if self.rotation_running:
            print("⚠️ [LogRotation] バックグラウンドローテーションは既に実行中")
            return
        
        self.rotation_running = True
        self.rotation_thread = threading.Thread(
            target=self._background_rotation_worker,
            args=(check_interval_minutes,),
            daemon=True
        )
        self.rotation_thread.start()
        print(f"🔄 [LogRotation] バックグラウンドローテーション開始 (間隔: {check_interval_minutes}分)")
    
    def _background_rotation_worker(self, check_interval_minutes: int):
        """バックグラウンドローテーションワーカー"""
        while self.rotation_running:
            try:
                # ローテーションチェック
                log_files = list(self.log_dir.glob("*.log"))
                for log_file in log_files:
                    if self.should_rotate_file(log_file):
                        self.rotate_log_file(log_file)
                
                # 古いファイルクリーンアップ（1日1回）
                current_hour = datetime.now().hour
                if current_hour == 2:  # 深夜2時にクリーンアップ
                    self.cleanup_old_logs()
                
                # 指定間隔で待機
                time.sleep(check_interval_minutes * 60)
                
            except Exception as e:
                print(f"❌ [LogRotation] バックグラウンドワーカーエラー: {e}")
                time.sleep(60)  # エラー時は1分待機
    
    def stop_background_rotation(self):
        """バックグラウンドローテーション停止"""
        if self.rotation_running:
            self.rotation_running = False
            if self.rotation_thread and self.rotation_thread.is_alive():
                self.rotation_thread.join(timeout=5.0)
            print("✅ [LogRotation] バックグラウンドローテーション停止")


# テスト用関数
if __name__ == "__main__":
    print("🧪 ログローテーションシステムテスト開始")
    
    # ローテーションマネージャー初期化
    rotation_manager = LogRotationManager(
        max_file_size_mb=1,  # テスト用に小さく設定
        retention_days=7
    )
    
    # 統計情報取得テスト
    stats = rotation_manager.get_log_statistics()
    print(f"📊 [統計] ログファイル統計:")
    for key, value in stats.items():
        print(f"   - {key}: {value}")
    
    # クリーンアップテスト
    rotation_manager.cleanup_old_logs()
    
    print("✅ ログローテーションテスト完了")
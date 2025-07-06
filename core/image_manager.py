#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
動画関連画像管理システム - せつなBot
動画に関連する画像のアップロード・保存・管理機能
"""

import os
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import shutil
from PIL import Image, ImageTk
import tkinter as tk


class VideoImageManager:
    """動画関連画像を管理するクラス"""
    
    def __init__(self):
        """初期化"""
        # Windows環境とWSL2環境両方に対応
        if os.name == 'nt':  # Windows
            self.base_image_dir = Path("D:/setsuna_bot/video_images")
        else:  # Linux/WSL2
            self.base_image_dir = Path("/mnt/d/setsuna_bot/video_images")
        
        # サポートされる画像形式
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
        
        # 設定
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.thumbnail_size = (150, 150)
        
        # ディレクトリ作成
        self._ensure_directories()
        
        print(f"[画像管理] ✅ VideoImageManager初期化完了 (保存先: {self.base_image_dir})")
    
    def _ensure_directories(self):
        """必要なディレクトリを作成"""
        try:
            self.base_image_dir.mkdir(parents=True, exist_ok=True)
            print(f"[画像管理] 📁 ベースディレクトリ確認完了: {self.base_image_dir}")
        except Exception as e:
            print(f"[画像管理] ❌ ディレクトリ作成エラー: {e}")
            raise
    
    def _get_video_image_dir(self, video_id: str) -> Path:
        """動画IDに対応する画像ディレクトリを取得"""
        video_dir = self.base_image_dir / video_id
        video_dir.mkdir(parents=True, exist_ok=True)
        
        # サムネイルディレクトリも作成
        thumbnail_dir = video_dir / "thumbnails"
        thumbnail_dir.mkdir(parents=True, exist_ok=True)
        
        return video_dir
    
    def validate_image_file(self, file_path: str) -> Tuple[bool, str]:
        """
        画像ファイルのバリデーション
        
        Args:
            file_path: 検証する画像ファイルのパス
            
        Returns:
            (is_valid, error_message)
        """
        try:
            file_path = Path(file_path)
            
            # ファイル存在チェック
            if not file_path.exists():
                return False, "ファイルが存在しません"
            
            # 拡張子チェック
            if file_path.suffix.lower() not in self.supported_formats:
                return False, f"サポートされていない形式です。対応形式: {', '.join(self.supported_formats)}"
            
            # ファイルサイズチェック
            file_size = file_path.stat().st_size
            if file_size > self.max_file_size:
                return False, f"ファイルサイズが大きすぎます（最大: {self.max_file_size // (1024*1024)}MB）"
            
            # PIL で画像として読み込み可能かチェック
            with Image.open(file_path) as img:
                img.verify()  # 画像の整合性チェック
            
            return True, ""
            
        except Exception as e:
            return False, f"画像検証エラー: {str(e)}"
    
    def _generate_image_id(self, file_path: str) -> str:
        """ファイル内容から一意のIDを生成"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # ファイル内容のハッシュ値生成
            with open(file_path, 'rb') as f:
                file_hash = hashlib.md5(f.read()).hexdigest()[:8]
            
            return f"img_{timestamp}_{file_hash}"
            
        except Exception as e:
            print(f"[画像管理] ❌ ID生成エラー: {e}")
            # フォールバック: タイムスタンプのみ
            return f"img_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def create_thumbnail(self, image_path: str, thumbnail_path: str) -> bool:
        """
        サムネイル画像を作成
        
        Args:
            image_path: 元画像のパス
            thumbnail_path: サムネイル保存パス
            
        Returns:
            作成成功フラグ
        """
        try:
            with Image.open(image_path) as img:
                # RGBA モードの場合は RGB に変換（JPEG保存のため）
                if img.mode in ('RGBA', 'LA', 'P'):
                    # 透明背景を白に変換
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if 'A' in img.mode else None)
                    img = background
                
                # サムネイル作成（アスペクト比維持）
                # PIL バージョン互換性対応
                try:
                    img.thumbnail(self.thumbnail_size, Image.Resampling.LANCZOS)
                except AttributeError:
                    # 古いPILバージョン対応
                    img.thumbnail(self.thumbnail_size, Image.LANCZOS)
                
                # サムネイル保存
                img.save(thumbnail_path, 'JPEG', quality=85)
                
            print(f"[画像管理] ✅ サムネイル作成完了: {thumbnail_path}")
            return True
            
        except Exception as e:
            print(f"[画像管理] ❌ サムネイル作成エラー: {e}")
            return False
    
    def save_image(self, video_id: str, source_file_path: str, user_description: str = "") -> Optional[Dict[str, Any]]:
        """
        画像を保存して、メタデータを返す
        
        Args:
            video_id: 関連する動画のID
            source_file_path: 保存する画像ファイルのパス
            user_description: ユーザーが入力した画像の説明
            
        Returns:
            画像メタデータ辞書、エラー時は None
        """
        try:
            # バリデーション
            is_valid, error_msg = self.validate_image_file(source_file_path)
            if not is_valid:
                print(f"[画像管理] ❌ バリデーションエラー: {error_msg}")
                return None
            
            # 動画用ディレクトリ取得
            video_dir = self._get_video_image_dir(video_id)
            
            # 画像ID生成
            image_id = self._generate_image_id(source_file_path)
            
            # ファイル拡張子取得
            source_path = Path(source_file_path)
            file_extension = source_path.suffix.lower()
            
            # 保存パス決定
            image_filename = f"{image_id}{file_extension}"
            image_path = video_dir / image_filename
            thumbnail_path = video_dir / "thumbnails" / f"{image_id}_thumb.jpg"
            
            # 画像ファイルをコピー
            shutil.copy2(source_file_path, image_path)
            print(f"[画像管理] 📁 画像コピー完了: {image_path}")
            
            # サムネイル作成
            thumbnail_created = self.create_thumbnail(str(image_path), str(thumbnail_path))
            
            # 画像メタデータ取得
            with Image.open(image_path) as img:
                width, height = img.size
                image_format = img.format
            
            file_size = image_path.stat().st_size
            
            # メタデータ構築
            image_metadata = {
                "image_id": image_id,
                "file_path": str(image_path),
                "thumbnail_path": str(thumbnail_path) if thumbnail_created else None,
                "upload_timestamp": datetime.now().isoformat(),
                "file_size": file_size,
                "dimensions": {
                    "width": width,
                    "height": height
                },
                "format": image_format,
                "user_description": user_description,
                "analysis_status": "pending"  # Phase 2で利用
            }
            
            print(f"[画像管理] ✅ 画像保存完了: {image_id}")
            return image_metadata
            
        except Exception as e:
            print(f"[画像管理] ❌ 画像保存エラー: {e}")
            return None
    
    def get_video_images(self, video_id: str) -> List[Dict[str, Any]]:
        """
        指定動画の画像一覧を取得
        
        Args:
            video_id: 動画ID
            
        Returns:
            画像メタデータのリスト
        """
        try:
            video_dir = self.base_image_dir / video_id
            
            if not video_dir.exists():
                return []
            
            images = []
            # 画像ファイルを検索
            for file_path in video_dir.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in self.supported_formats:
                    # 基本的なメタデータを生成
                    try:
                        with Image.open(file_path) as img:
                            width, height = img.size
                            image_format = img.format
                        
                        file_size = file_path.stat().st_size
                        
                        image_data = {
                            "image_id": file_path.stem,
                            "file_path": str(file_path),
                            "file_size": file_size,
                            "dimensions": {"width": width, "height": height},
                            "format": image_format
                        }
                        images.append(image_data)
                        
                    except Exception as e:
                        print(f"[画像管理] ⚠️ 画像読み込みエラー: {file_path} - {e}")
                        continue
            
            return images
            
        except Exception as e:
            print(f"[画像管理] ❌ 画像一覧取得エラー: {e}")
            return []
    
    def delete_image(self, video_id: str, image_id: str) -> bool:
        """
        画像を削除
        
        Args:
            video_id: 動画ID
            image_id: 画像ID
            
        Returns:
            削除成功フラグ
        """
        try:
            video_dir = self._get_video_image_dir(video_id)
            
            # 画像ファイルとサムネイルを削除
            deleted_count = 0
            
            # メイン画像ファイル削除
            for file_path in video_dir.iterdir():
                if file_path.is_file() and file_path.stem == image_id:
                    file_path.unlink()
                    print(f"[画像管理] 🗑️ 画像削除: {file_path}")
                    deleted_count += 1
                    break
            
            # サムネイル削除
            thumbnail_dir = video_dir / "thumbnails"
            for thumb_path in thumbnail_dir.iterdir():
                if thumb_path.is_file() and thumb_path.stem.startswith(f"{image_id}_thumb"):
                    thumb_path.unlink()
                    print(f"[画像管理] 🗑️ サムネイル削除: {thumb_path}")
                    deleted_count += 1
                    break
            
            if deleted_count > 0:
                print(f"[画像管理] ✅ 画像削除完了: {image_id}")
                return True
            else:
                print(f"[画像管理] ⚠️ 削除対象が見つかりません: {image_id}")
                return False
                
        except Exception as e:
            print(f"[画像管理] ❌ 画像削除エラー: {e}")
            return False
    
    def get_image_info(self, video_id: str, image_id: str) -> Optional[Dict[str, Any]]:
        """
        特定画像の詳細情報を取得
        
        Args:
            video_id: 動画ID
            image_id: 画像ID
            
        Returns:
            画像情報辞書、見つからない場合は None
        """
        try:
            video_dir = self._get_video_image_dir(video_id)
            
            # 画像ファイルを検索
            for file_path in video_dir.iterdir():
                if file_path.is_file() and file_path.stem == image_id:
                    # 画像情報を構築
                    with Image.open(file_path) as img:
                        width, height = img.size
                        image_format = img.format
                    
                    file_size = file_path.stat().st_size
                    modified_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    
                    # サムネイルパス確認
                    thumbnail_dir = video_dir / "thumbnails"
                    thumbnail_path = None
                    for thumb_path in thumbnail_dir.iterdir():
                        if thumb_path.stem.startswith(f"{image_id}_thumb"):
                            thumbnail_path = str(thumb_path)
                            break
                    
                    return {
                        "image_id": image_id,
                        "file_path": str(file_path),
                        "thumbnail_path": thumbnail_path,
                        "file_size": file_size,
                        "dimensions": {"width": width, "height": height},
                        "format": image_format,
                        "modified_timestamp": modified_time.isoformat()
                    }
            
            return None
            
        except Exception as e:
            print(f"[画像管理] ❌ 画像情報取得エラー: {e}")
            return None


# テスト用の関数
def test_image_manager():
    """VideoImageManagerの基本動作テスト"""
    print("=== VideoImageManager テスト開始 ===")
    
    manager = VideoImageManager()
    
    # ディレクトリ作成テスト
    test_video_id = "test_video_123"
    video_dir = manager._get_video_image_dir(test_video_id)
    print(f"✅ ディレクトリ作成テスト完了: {video_dir}")
    
    # バリデーションテスト（存在しないファイル）
    is_valid, error = manager.validate_image_file("nonexistent.jpg")
    print(f"✅ バリデーションテスト（存在しないファイル）: {is_valid}, {error}")
    
    print("=== VideoImageManager テスト完了 ===")


if __name__ == "__main__":
    test_image_manager()
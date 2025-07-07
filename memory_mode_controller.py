#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
メモリモード制御システム
テストモードと通常モードを管理
"""

import os
import json
import atexit
from datetime import datetime
from typing import Dict, Any, Optional

class MemoryModeController:
    """メモリモード制御クラス"""
    
    def __init__(self):
        self.current_mode = "normal"  # "normal" | "test"
        self.test_data_files = []  # テスト時に作成されたファイル一覧
        self.session_start_time = datetime.now()
        
        # プロセス終了時の自動クリーンアップ登録
        atexit.register(self.cleanup_test_data)
        
        print("[メモリ制御] ✅ メモリモード制御システム初期化完了")
    
    def switch_to_test_mode(self):
        """テストモードに切り替え"""
        if self.current_mode == "test":
            print("🧪 [TEST MODE] 既にテストモードです")
            return
        
        self.current_mode = "test"
        print("🧪 [TEST MODE] テストモードに切り替えました")
        print("⚠️  この会話は保存されません（セッション終了時に自動削除）")
        print("📝 通常モードに戻るには Alt+N を押してください")
    
    def switch_to_normal_mode(self):
        """通常モードに切り替え"""
        if self.current_mode == "normal":
            print("📝 [NORMAL MODE] 既に通常モードです")
            return
        
        # テストモード終了時にデータをクリーンアップ
        self.cleanup_test_data()
        
        self.current_mode = "normal"
        print("📝 [NORMAL MODE] 通常モードに戻りました")
        print("💾 会話は永続保存されます")
    
    def get_current_mode(self) -> str:
        """現在のモードを取得"""
        return self.current_mode
    
    def is_test_mode(self) -> bool:
        """テストモードかどうか判定"""
        return self.current_mode == "test"
    
    def is_normal_mode(self) -> bool:
        """通常モードかどうか判定"""
        return self.current_mode == "normal"
    
    def register_test_file(self, file_path: str):
        """テスト用ファイルを登録（自動削除対象）"""
        if self.is_test_mode() and file_path not in self.test_data_files:
            self.test_data_files.append(file_path)
            print(f"[メモリ制御] 🗑️ テスト用ファイル登録: {file_path}")
    
    def cleanup_test_data(self):
        """テスト用データをクリーンアップ"""
        if not self.test_data_files:
            return
        
        cleaned_count = 0
        for file_path in self.test_data_files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    cleaned_count += 1
                    print(f"[メモリ制御] 🗑️ 削除完了: {file_path}")
            except Exception as e:
                print(f"[メモリ制御] ❌ 削除失敗 {file_path}: {e}")
        
        if cleaned_count > 0:
            print(f"[メモリ制御] ✅ テストデータクリーンアップ完了: {cleaned_count}件")
        
        self.test_data_files.clear()
    
    def get_status_display(self) -> str:
        """ステータス表示用の文字列を取得"""
        if self.is_test_mode():
            return "🧪 [TEST]"
        else:
            return "📝 [NORMAL]"
    
    def get_memory_file_path(self, base_filename: str) -> str:
        """
        モードに応じた記憶ファイルパスを生成
        
        Args:
            base_filename: ベースとなるファイル名
            
        Returns:
            str: モード別のファイルパス
        """
        if self.is_test_mode():
            # テストモード用の一時ファイル
            timestamp = self.session_start_time.strftime("%Y%m%d_%H%M%S")
            test_filename = f"test_{timestamp}_{base_filename}"
            test_path = os.path.join("temp", test_filename)
            
            # tempディレクトリ作成
            os.makedirs("temp", exist_ok=True)
            
            # テスト用ファイルとして登録
            self.register_test_file(test_path)
            
            return test_path
        else:
            # 通常モード用のファイル
            return base_filename
    
    def create_memory_config(self) -> Dict[str, Any]:
        """メモリシステム用の設定を作成"""
        return {
            "mode": self.current_mode,
            "persistent_save": self.is_normal_mode(),
            "auto_cleanup": self.is_test_mode(),
            "session_id": self.session_start_time.isoformat(),
            "status_display": self.get_status_display()
        }

# グローバルなメモリモード制御インスタンス
_memory_controller = None

def get_memory_controller() -> MemoryModeController:
    """グローバルなメモリモード制御インスタンスを取得"""
    global _memory_controller
    if _memory_controller is None:
        _memory_controller = MemoryModeController()
    return _memory_controller

def switch_to_test_mode():
    """テストモードに切り替え（便利関数）"""
    get_memory_controller().switch_to_test_mode()

def switch_to_normal_mode():
    """通常モードに切り替え（便利関数）"""
    get_memory_controller().switch_to_normal_mode()

def is_test_mode() -> bool:
    """テストモードかどうか判定（便利関数）"""
    return get_memory_controller().is_test_mode()

def get_current_mode() -> str:
    """現在のモードを取得（便利関数）"""
    return get_memory_controller().get_current_mode()

def get_status_display() -> str:
    """ステータス表示を取得（便利関数）"""
    return get_memory_controller().get_status_display()

if __name__ == "__main__":
    # テスト実行
    controller = MemoryModeController()
    
    print("\n=== テストモード切り替えテスト ===")
    print(f"初期モード: {controller.get_current_mode()}")
    print(f"ステータス: {controller.get_status_display()}")
    
    # テストモードに切り替え
    controller.switch_to_test_mode()
    print(f"切り替え後: {controller.get_current_mode()}")
    print(f"テストファイルパス例: {controller.get_memory_file_path('memory.json')}")
    
    # 通常モードに戻す
    controller.switch_to_normal_mode()
    print(f"復帰後: {controller.get_current_mode()}")
    print(f"通常ファイルパス例: {controller.get_memory_file_path('memory.json')}")
    
    print("\n✅ テスト完了")
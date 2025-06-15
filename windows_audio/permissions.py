#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows音声権限管理
マイク権限・プライバシー設定・デバイスアクセス確認
"""

import os
import subprocess
import winreg
import json
from typing import Dict, List, Optional, Tuple


class WindowsPermissionManager:
    """Windows音声権限管理クラス"""
    
    def __init__(self):
        self.permission_status = {}
        self.privacy_settings = {}
        
    def check_microphone_permissions(self) -> Dict[str, bool]:
        """マイク権限包括チェック"""
        permissions = {
            'microphone_access': False,
            'app_microphone_access': False,
            'desktop_apps_microphone': False,
            'microphone_device_available': False
        }
        
        try:
            # Windows 10/11プライバシー設定確認
            permissions['microphone_access'] = self._check_system_microphone_access()
            permissions['app_microphone_access'] = self._check_app_microphone_access()
            permissions['desktop_apps_microphone'] = self._check_desktop_apps_microphone()
            
            # ハードウェアデバイス確認
            permissions['microphone_device_available'] = self._check_microphone_hardware()
            
            self.permission_status = permissions
            return permissions
            
        except Exception as e:
            print(f"❌ 権限チェックエラー: {e}")
            return permissions
    
    def _check_system_microphone_access(self) -> bool:
        """システムレベルマイクアクセス確認"""
        try:
            # レジストリからプライバシー設定取得
            reg_path = r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\CapabilityAccessManager\\ConsentStore\\microphone"
            
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
                value, _ = winreg.QueryValueEx(key, "Value")
                # "Allow" = マイクアクセス許可
                return value == "Allow"
                
        except (FileNotFoundError, OSError):
            print("⚠️  マイクプライバシー設定が見つかりません")
            return False
        except Exception as e:
            print(f"⚠️  システムマイクアクセス確認エラー: {e}")
            return False
    
    def _check_app_microphone_access(self) -> bool:
        """アプリケーションレベルマイクアクセス確認"""
        try:
            # Microsoft Store アプリのマイクアクセス設定
            reg_path = r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\CapabilityAccessManager\\ConsentStore\\microphone"
            
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
                # 個別アプリ設定を確認
                app_value, _ = winreg.QueryValueEx(key, "Value")
                return app_value == "Allow"
                
        except Exception:
            # デスクトップアプリの場合は通常制限なし
            return True
    
    def _check_desktop_apps_microphone(self) -> bool:
        """デスクトップアプリマイクアクセス確認"""
        try:
            reg_path = r"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\CapabilityAccessManager\\ConsentStore\\microphone"
            
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path) as key:
                # デスクトップアプリアクセス設定
                desktop_value, _ = winreg.QueryValueEx(key, "Value")
                return desktop_value == "Allow"
                
        except Exception:
            # デフォルトで許可されていることが多い
            return True
    
    def _check_microphone_hardware(self) -> bool:
        """マイクハードウェア存在確認"""
        try:
            # PowerShellでマイクデバイス確認
            cmd = [
                "powershell", "-Command",
                "Get-AudioDevice -RecordingVolume | Where-Object {$_.Type -eq 'Recording'} | Measure-Object | Select-Object -ExpandProperty Count"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            
            if result.returncode == 0:
                device_count = int(result.stdout.strip())
                return device_count > 0
            else:
                # フォールバック: WMIでチェック
                return self._check_microphone_wmi()
                
        except Exception as e:
            print(f"⚠️  マイクハードウェア確認エラー: {e}")
            return self._check_microphone_wmi()
    
    def _check_microphone_wmi(self) -> bool:
        """WMI経由でマイクデバイス確認"""
        try:
            cmd = [
                "wmic", "sounddev", "where", 
                "\"DeviceID like '%MICROPHONE%' or DeviceID like '%MIC%'\"", 
                "get", "Name"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            return len(result.stdout.strip().split('\n')) > 2  # ヘッダー除く
            
        except Exception:
            return False
    
    def get_permission_status_report(self) -> str:
        """権限状態レポート生成"""
        permissions = self.check_microphone_permissions()
        
        report = "🔍 === Windows音声権限状態 ===\\n"
        
        # 各権限の状態表示
        status_map = {
            'microphone_access': 'システムマイクアクセス',
            'app_microphone_access': 'アプリマイクアクセス', 
            'desktop_apps_microphone': 'デスクトップアプリマイクアクセス',
            'microphone_device_available': 'マイクデバイス存在'
        }
        
        for key, label in status_map.items():
            status = "✅ 有効" if permissions.get(key, False) else "❌ 無効"
            report += f"{label}: {status}\\n"
        
        # 総合判定
        all_permissions_ok = all(permissions.values())
        overall_status = "✅ 音声入力可能" if all_permissions_ok else "⚠️  設定要確認"
        report += f"\\n総合状態: {overall_status}"
        
        return report
    
    def open_microphone_privacy_settings(self):
        """マイクプライバシー設定を開く"""
        try:
            # Windows 10/11 設定アプリのマイクページを開く
            subprocess.run([
                "start", 
                "ms-settings:privacy-microphone"
            ], shell=True, check=True)
            
            print("🔧 マイクプライバシー設定を開きました")
            return True
            
        except subprocess.CalledProcessError:
            print("❌ プライバシー設定を開けませんでした")
            return False
        except Exception as e:
            print(f"❌ 設定画面起動エラー: {e}")
            return False
    
    def open_sound_control_panel(self):
        """Windowsサウンドコントロールパネルを開く"""
        try:
            subprocess.run(["mmsys.cpl"], shell=True, check=True)
            print("🔊 サウンドコントロールパネルを開きました")
            return True
        except Exception as e:
            print(f"❌ サウンド設定起動エラー: {e}")
            return False
    
    def request_permissions_interactive(self) -> bool:
        """対話的権限要求"""
        permissions = self.check_microphone_permissions()
        
        if all(permissions.values()):
            print("✅ 全ての音声権限が有効です")
            return True
        
        print("⚠️  音声権限に問題があります")
        print(self.get_permission_status_report())
        
        # ユーザーに設定画面を開くか確認
        response = input("\\n🔧 プライバシー設定を開きますか？ (y/n): ").lower().strip()
        
        if response in ['y', 'yes', 'はい']:
            self.open_microphone_privacy_settings()
            
            input("\\n💡 設定完了後、Enterキーを押してください...")
            
            # 再チェック
            updated_permissions = self.check_microphone_permissions()
            
            if all(updated_permissions.values()):
                print("✅ 権限設定が正常に更新されました")
                return True
            else:
                print("⚠️  一部権限が未解決です")
                return False
        
        return False
    
    def get_troubleshooting_guide(self) -> str:
        """トラブルシューティングガイド"""
        permissions = self.check_microphone_permissions()
        
        guide = "🛠️  === 音声権限トラブルシューティング ===\\n\\n"
        
        if not permissions.get('microphone_device_available', False):
            guide += "🎤 マイクデバイス問題:\\n"
            guide += "  • マイクが物理的に接続されているか確認\\n"
            guide += "  • デバイスマネージャーでマイクドライバー確認\\n"
            guide += "  • USB マイクの場合は別ポートで試行\\n\\n"
        
        if not permissions.get('microphone_access', False):
            guide += "🔒 システムマイクアクセス問題:\\n"
            guide += "  • Windows設定 > プライバシー > マイク\\n"
            guide += "  • 'このデバイスでのマイクアクセスを許可する'をオン\\n"
            guide += "  • 'アプリがマイクにアクセスすることを許可する'をオン\\n\\n"
        
        if not permissions.get('desktop_apps_microphone', False):
            guide += "🖥️  デスクトップアプリアクセス問題:\\n"
            guide += "  • 'デスクトップアプリがマイクにアクセスすることを許可する'をオン\\n"
            guide += "  • Windows Defenderファイアウォール確認\\n\\n"
        
        guide += "💡 追加の対処法:\\n"
        guide += "  • Windowsを再起動\\n"
        guide += "  • Pythonを管理者権限で実行\\n"
        guide += "  • ウイルス対策ソフトの許可設定確認"
        
        return guide
    
    def export_permission_report(self, file_path: Optional[str] = None) -> str:
        """権限レポートをファイル出力"""
        if file_path is None:
            config_dir = os.path.expandvars('%APPDATA%\\SetsunaBot')
            if not os.path.exists(config_dir):
                os.makedirs(config_dir)
            file_path = os.path.join(config_dir, 'permission_report.json')
        
        try:
            permissions = self.check_microphone_permissions()
            
            report_data = {
                'timestamp': str(pd.Timestamp.now()) if 'pd' in globals() else None,
                'permissions': permissions,
                'troubleshooting_guide': self.get_troubleshooting_guide(),
                'system_info': {
                    'os': os.name,
                    'platform': os.getenv('OS', 'Unknown')
                }
            }
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            
            print(f"📄 権限レポート出力: {file_path}")
            return file_path
            
        except Exception as e:
            print(f"❌ レポート出力エラー: {e}")
            return ""


# テスト用関数
def main():
    """権限管理テスト"""
    print("🔐 Windows音声権限管理テスト")
    
    permission_manager = WindowsPermissionManager()
    
    # 権限チェック
    print(permission_manager.get_permission_status_report())
    
    # トラブルシューティングガイド表示
    print("\\n" + permission_manager.get_troubleshooting_guide())
    
    # レポート出力
    permission_manager.export_permission_report()


if __name__ == "__main__":
    main()
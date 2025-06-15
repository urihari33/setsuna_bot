# 🪟 せつなBot Windows完全移行計画

## 🎯 移行目標

WSL2環境の制約を排除し、Windows ネイティブ環境での最適な音声対話システムを構築する。

---

## 📊 現状とWindows移行の利点

### **WSL2制約の排除**
- ❌ WSL2: 音声デバイスアクセス制限
- ✅ Windows: 直接音声API使用可能
- ❌ WSL2: GUI・マイク権限問題  
- ✅ Windows: ネイティブ権限管理
- ❌ WSL2: arecord フォールバック必要
- ✅ Windows: PyAudio・WASAPI直接利用

### **パフォーマンス向上**
- 音声レイテンシ削減
- リアルタイム処理能力向上
- ハードウェア直接アクセス

---

## 🔧 段階的移行戦略

### **Phase 1: 音声システムWindows最適化**

#### 1.1 音声入力システム刷新
```python
# Windows専用音声入力クラス
class WindowsVoiceInput:
    def __init__(self):
        self.audio_engine = self._initialize_windows_audio()
        self.device_manager = WindowsAudioDeviceManager()
    
    def _initialize_windows_audio(self):
        """Windows音声APIの最適化初期化"""
        if self._check_wasapi_available():
            return WASAPIAudioEngine()
        elif self._check_pyaudio_available():
            return PyAudioEngine()
        else:
            raise AudioEngineNotFoundError()
```

#### 1.2 マイクロソフト Speech API統合
```python
# Windows Speech API + Google API フォールバック
class WindowsSpeechRecognizer:
    def __init__(self):
        self.primary_engine = WindowsSpeechAPI()
        self.fallback_engine = GoogleSpeechAPI()
    
    async def recognize(self, audio_data):
        try:
            return await self.primary_engine.recognize(audio_data, language='ja-JP')
        except Exception:
            return await self.fallback_engine.recognize(audio_data, language='ja-JP')
```

### **Phase 2: システム統合・権限管理**

#### 2.1 Windows権限管理
```python
# 権限チェック・要求システム
class WindowsPermissionManager:
    def check_microphone_permissions(self):
        """マイク権限確認・要求"""
        
    def check_audio_devices(self):
        """利用可能音声デバイス検出"""
        
    def request_permissions_if_needed(self):
        """必要に応じて権限要求ダイアログ表示"""
```

#### 2.2 Windowsファイルシステム統合
```python
# Windows専用パス・設定管理
class WindowsPathManager:
    def __init__(self):
        self.app_data = os.path.expandvars('%APPDATA%\\SetsunaBot')
        self.voice_cache = os.path.join(self.app_data, 'voice_cache')
        self.config_file = os.path.join(self.app_data, 'config.json')
```

### **Phase 3: ユーザビリティ向上**

#### 3.1 Windows通知システム
```python
# Windows Toast通知
from plyer import notification

class WindowsNotificationManager:
    def notify_voice_ready(self):
        notification.notify(
            title='せつなBot',
            message='音声対話準備完了！Ctrl+Shift+Altで話しかけてください',
            app_name='SetsunaBot',
            timeout=3
        )
```

#### 3.2 タスクトレイ・システム統合
```python
# システムトレイアプリケーション
import pystray
from PIL import Image

class WindowsSystemTrayApp:
    def create_tray_icon(self):
        """タスクトレイアイコン作成"""
        
    def show_status_menu(self):
        """右クリックメニュー表示"""
```

---

## 🛠️ 実装ロードマップ

### **Week 1: 基盤音声システム**
- [ ] PyAudio完全動作確認
- [ ] Windows音声デバイス検出・選択
- [ ] リアルタイム音声録音テスト
- [ ] 音声品質最適化

### **Week 2: Discord統合改良**
- [ ] Windows環境でのDiscord音声受信最適化
- [ ] PCM→WAV変換処理改良
- [ ] 音声認識精度向上
- [ ] エラーハンドリング強化

### **Week 3: ホットキー・UI完成**
- [ ] Ctrl+Shift+Altホットキー完全実装
- [ ] Windows通知システム統合
- [ ] 設定UI（オプション）
- [ ] システムトレイ統合（オプション）

---

## 📦 Windows専用ライブラリ追加

### **必須ライブラリ**
```bash
# 音声関連
pip install pyaudio sounddevice

# Windows API
pip install pywin32 winsound

# システム統合
pip install plyer pystray pillow

# ホットキー（Windows最適化版）
pip install keyboard pynput
```

### **オプションライブラリ**
```bash
# Microsoft Speech API
pip install speech-recognition[whisper]

# Windows性能監視
pip install psutil

# 設定GUI（オプション）
pip install tkinter-modern
```

---

## 🔧 移行手順

### **Step 1: 開発環境確認**
```powershell
# Windows環境での完全動作確認
cd D:\setsuna_bot
.\setsuna_win_env\Scripts\Activate.ps1

# Windows音声機能テスト
python -c "
import pyaudio
import sounddevice as sd
print('✅ PyAudio:', pyaudio.get_portaudio_version())
print('✅ SoundDevice:', sd.query_devices())
"
```

### **Step 2: Windows専用モジュール作成**
```
D:\setsuna_bot\
├── windows_audio\
│   ├── __init__.py
│   ├── voice_input.py      # Windows音声入力
│   ├── device_manager.py   # デバイス管理
│   ├── permissions.py      # 権限管理
│   └── notifications.py    # 通知システム
├── windows_gui\            # オプション
│   ├── tray_app.py        # システムトレイ
│   └── settings_ui.py     # 設定GUI
```

### **Step 3: 段階的置き換え**
1. 音声入力システムをWindows専用に置き換え
2. ホットキーシステムの最適化
3. Discord統合の改良
4. 最終統合テスト

---

## 🎯 期待される改善効果

### **音声品質・レスポンス**
- 音声レイテンシ: 500ms → 100ms以下
- 認識精度: 70% → 90%以上
- 安定性: エラー頻発 → 安定動作

### **ユーザー体験**
- ワンクリック起動
- バックグラウンド動作
- Windows通知連携
- 設定の永続化

### **開発・メンテナンス**
- WSL2/Linux互換性考慮不要
- Windows API直接利用
- パフォーマンス最適化容易
- トラブルシューティング簡素化

---

## 🚀 今すぐ開始する実装

1. **Windows音声デバイス検出機能**
2. **PyAudio最適化設定**
3. **権限チェック・管理システム**
4. **Windows専用Discord Bot起動スクリプト**

これらから始めて、WSL2制約を完全に排除した高性能な音声対話システムを構築します。
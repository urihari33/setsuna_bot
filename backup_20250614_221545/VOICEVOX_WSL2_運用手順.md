# 🎯 Setsuna Bot WSL2 + VOICEVOX 運用手順

## ✅ セットアップ完了確認

以下が正常に動作することを確認済み：
- ✅ Windows ホストIP自動検出: `172.20.144.1`
- ✅ VOICEVOX接続成功: `version 0.23.1` 
- ✅ 音声合成テスト成功
- ✅ ファイアウォール設定完了

---

## 🚀 日常運用手順

### 1️⃣ VOICEVOX起動（Windows側）

**推奨方法: 手動起動**
```batch
cd "%LOCALAPPDATA%\Programs\VOICEVOX\vv-engine"
run.exe --host 0.0.0.0 --port 50021
```

**代替方法: バッチファイル使用**
```batch
D:
cd D:\setsuna_bot
.\start_voicevox_simple.bat
```

**確認ポイント:**
- "サーバーを開始しました" のメッセージを確認
- 15-30秒の起動時間を待つ

### 2️⃣ Setsuna GUI起動（WSL2側）

```bash
cd /mnt/d/setsuna_bot
python setsuna_gui.py
```

**または、ホットキーモードのみ:**
```bash
python setsuna_hotkey_mode.py
```

### 3️⃣ 動作確認

1. **接続テスト実行:**
   ```bash
   python test_voicevox_connection.py
   ```

2. **音声パラメータ調整:**
   - GUIのスライダーで速度・音程・抑揚を調整
   - リアルタイムで設定が反映される

3. **ホットキー動作:**
   - `Ctrl+Shift+Alt` で音声入力開始
   - 音声認識 → GPT応答 → VOICEVOX音声出力

---

## 🔧 トラブルシューティング

### 🚨 "接続エラー" が出た場合

1. **VOICEVOX再起動:**
   ```batch
   # Windows側で
   cd "%LOCALAPPDATA%\Programs\VOICEVOX\vv-engine"
   run.exe --host 0.0.0.0 --port 50021
   ```

2. **ファイアウォール確認:**
   ```powershell
   Get-NetFirewallRule -DisplayName "VOICEVOX-WSL2"
   ```

3. **ポート確認:**
   ```batch
   # Windows側で
   netstat -an | findstr 50021
   ```

### 🚨 音声が出ない場合

1. **WSL2の音声設定確認:**
   ```bash
   # PulseAudio設定（必要に応じて）
   pulseaudio --start
   ```

2. **Pygame音声バックエンド確認:**
   - エラーメッセージで `[AUDIO] Using pygame mixer` を確認

### 🚨 IPアドレスが変わった場合

WSL2のIPアドレスは再起動時に変更される可能性があります：

```bash
# 自動検出なので通常は問題なし
python test_voicevox_connection.py
```

---

## ⚙️ 設定ファイル

### 音声パラメータ（voicevox_speaker.py）
```python
voice_settings = {
    "speedScale": 1.3,    # 話速（0.5-2.0）
    "pitchScale": 0.0,    # 音程（-0.15-0.15）
    "intonationScale": 1.0 # 抑揚（0.0-2.0）
}
```

### VOICEVOX接続設定
- 自動でWindows ホストIPを検出
- フォールバック機能付き
- エラーハンドリング完備

---

## 🎵 使用例

1. **GUI起動後:**
   - スライダーで音声調整
   - テキスト入力で応答確認

2. **ホットキーモード:**
   - `Ctrl+Shift+Alt` 長押し
   - 音声入力開始
   - 離すと処理開始
   - 自動音声出力

3. **手動テスト:**
   ```bash
   python -c "from voicevox_speaker import speak_with_voicevox; speak_with_voicevox('こんにちは、せつなです。')"
   ```

---

## 📝 定期メンテナンス

- **週1回:** 音声キャッシュのクリーンアップ（自動実行）
- **月1回:** ログファイルの整理
- **必要時:** VOICEVOX/WSL2のアップデート確認
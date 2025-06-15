# 🤖 せつなBot Windows環境実行手順

## 📋 概要

せつなBot をWindows環境で実行するための完全手順書です。  
仮想環境の正しい使い方からBot起動まで、ステップバイステップで説明します。

---

## 🚀 基本実行手順

### 1. **PowerShell起動**
```
Windows + X → "Windows PowerShell"
または
Windows + R → "powershell" → Enter
```

### 2. **プロジェクトディレクトリに移動**
```powershell
cd D:\setsuna_bot
```

### 3. **正しい仮想環境の確認**
```powershell
# 仮想環境フォルダが存在するか確認
ls setsuna_win_env
```
✅ **期待される結果:** フォルダ内容が表示される  
❌ **エラーの場合:** 「項目が見つかりません」→ 初回セットアップが必要

### 4. **仮想環境アクティベート**
```powershell
.\setsuna_win_env\Scripts\Activate.ps1
```
✅ **成功時の表示:** `(setsuna_win_env) PS D:\setsuna_bot>`  
❌ **エラーの場合:** スクリプト実行ポリシーエラー → 下記対処法参照

### 5. **環境変数設定**
```powershell
$env:PYTHONIOENCODING="utf-8"
```

### 6. **Bot起動**
```powershell
# テスト版（推奨）
python test_bot_simple.py

# または完全版
python setsuna_discord_bot.py
```

---

## 🔧 初回セットアップ（仮想環境がない場合）

### 1. **仮想環境作成**
```powershell
cd D:\setsuna_bot
python -m venv setsuna_win_env
```

### 2. **仮想環境アクティベート**
```powershell
.\setsuna_win_env\Scripts\Activate.ps1
```

### 3. **必須ライブラリインストール**
```powershell
python -m pip install --upgrade pip
python -m pip install discord.py openai requests python-dotenv
python -m pip install SpeechRecognition pydub pynput pygame
```

### 4. **PyAudio追加インストール（音声機能用）**
```powershell
python -m pip install pyaudio
```

### 5. **インストール確認**
```powershell
python -m pip list | findstr -i "discord openai"
```

---

## ⚠️ よくある問題と対処法

### 🔒 **PowerShell実行ポリシーエラー**
```
このシステムではスクリプトの実行が無効になっています
```

**対処法:**
```powershell
# 管理者権限でPowerShell起動して実行
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 🔄 **間違った仮想環境がアクティブな場合**
```powershell
# 現在の仮想環境を無効化
deactivate

# 正しい仮想環境をアクティベート
.\setsuna_win_env\Scripts\Activate.ps1
```

### 📦 **ライブラリがインストールされていない**
```
ModuleNotFoundError: No module named 'discord'
```

**対処法:**
```powershell
# 仮想環境がアクティブか確認
python -m pip install discord.py
```

### 🌐 **文字化け問題**
```powershell
# UTF-8エンコーディング設定
$env:PYTHONIOENCODING="utf-8"
chcp 65001
```

---

## 📋 コマンド一覧（チートシート）

### **基本操作**
```powershell
cd D:\setsuna_bot                               # ディレクトリ移動
.\setsuna_win_env\Scripts\Activate.ps1          # 仮想環境アクティベート
deactivate                                      # 仮想環境無効化
```

### **ライブラリ管理**
```powershell
python -m pip list                              # インストール済み一覧
python -m pip install パッケージ名                # パッケージインストール
python -m pip install --upgrade パッケージ名      # パッケージ更新
```

### **Bot起動**
```powershell
python test_bot_simple.py                       # テスト版起動
python setsuna_discord_bot.py                   # 完全版起動
```

---

## 🎯 Discord での動作確認

Bot起動後、Discordで以下をテスト：

### **テスト版コマンド**
- `!test` - 基本動作確認
- `!ping` - 応答時間確認

### **完全版コマンド**
- `!guide` - 全コマンド表示
- `!join` - ボイスチャンネル参加
- `!voice_start` - 音声対話開始
- `!hotkey_start` - Ctrl+Shift+Alt音声入力開始

---

## 🔍 トラブルシューティング

### **Botが起動しない場合**
1. `.env` ファイルのトークン設定確認
2. VOICEVOX起動確認（完全版の場合）
3. インターネット接続確認

### **音声機能が動作しない場合**
1. PyAudioインストール確認: `python -c "import pyaudio; print('OK')"`
2. Windowsマイク権限確認
3. VOICEVOX接続確認: http://localhost:50021

### **仮想環境リセット**
```powershell
deactivate
Remove-Item -Recurse -Force setsuna_win_env
python -m venv setsuna_win_env
.\setsuna_win_env\Scripts\Activate.ps1
# 再度ライブラリインストール
```

---

## 💡 ベストプラクティス

### **日常の起動手順**
1. PowerShell起動
2. `cd D:\setsuna_bot`
3. `.\setsuna_win_env\Scripts\Activate.ps1`
4. `python test_bot_simple.py`

### **開発時の推奨事項**
- まずテスト版で動作確認
- 仮想環境が正しくアクティブか常に確認
- エラーが出たら仮想環境から確認

### **定期メンテナンス**
```powershell
# 月1回程度、ライブラリ更新
python -m pip install --upgrade discord.py openai
```

---

## 📞 サポート情報

問題が解決しない場合は、以下の情報を確認してください：

- Python バージョン: `python --version`
- 仮想環境状態: プロンプトに `(setsuna_win_env)` 表示があるか
- インストール済みライブラリ: `python -m pip list`
- エラーメッセージの全文

---

**🎉 この手順に従えば、せつなBot が正常に起動できます！**
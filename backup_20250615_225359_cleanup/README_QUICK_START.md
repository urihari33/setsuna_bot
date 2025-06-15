# 🤖 せつなBot クイックスタートガイド

## 🚀 最速セットアップ (3ステップ)

### 1. **ランチャー起動**
```
📁 D:\setsuna_bot フォルダで
🖱️ setsuna_launcher.bat をダブルクリック
```

### 2. **初回セットアップ**
```
ランチャーで「2」を選択 → 初回環境セットアップ
↓
.env ファイルに以下を設定:
- DISCORD_BOT_TOKEN=あなたのDiscord Bot Token
- OPENAI_API_KEY=あなたのOpenAI API Key
```

### 3. **VOICEVOX起動 + Bot起動**
```
ランチャーで「6」→ VOICEVOX起動
ランチャーで「1」→ せつなBot起動
```

## 🎯 動作確認

### Discordで以下をテスト:
```
!join          # ボイスチャンネル参加
!voice_start   # 音声対話モード開始
!hotkey_start  # Ctrl+Shift+Alt音声入力開始
```

### **🎤 実際にCtrl+Shift+Altを押しながら話してください！**

## 📁 作成されるファイル

```
D:\setsuna_bot\
├── 🚀 setsuna_launcher.bat      ← メインランチャー
├── 🔧 setup_environment.bat     ← 初回セットアップ
├── 🤖 start_setsuna.bat         ← Bot起動
├── 🔄 update_libraries.bat      ← アップデート
├── 🔍 troubleshoot.bat          ← トラブルシューティング
├── 📝 .env                      ← 設定ファイル
├── 📦 setsuna_win_env\          ← Python仮想環境
└── 🗃️ install.log               ← インストールログ
```

## ⚡ 日常の使い方

### **通常起動**
```
🖱️ setsuna_launcher.bat をダブルクリック
→ 「1. せつなBot を起動」
```

### **メンテナンス**
```
🖱️ setsuna_launcher.bat をダブルクリック
→ 「3. ライブラリアップデート」（月1回推奨）
```

### **問題が発生した場合**
```
🖱️ setsuna_launcher.bat をダブルクリック
→ 「4. トラブルシューティング」
```

## 🎮 Discord コマンド一覧

### **基本コマンド**
```
!join          - ボイスチャンネル参加
!leave         - ボイスチャンネル退出
!status        - Bot状態確認
!guide         - ヘルプ表示
```

### **音声対話**
```
!voice_start   - 音声対話モード開始
!voice_stop    - 音声対話モード停止
!voice_settings - 音声設定変更
```

### **音声入力 (Windows版の特徴)**
```
!hotkey_start  - Ctrl+Shift+Alt音声入力開始
!hotkey_stop   - ホットキー音声入力停止
!record 5      - 5秒間音声録音
!voice_test    - 音声入力テスト
```

### **テキストチャット**
```
@せつな こんにちは    - メンション形式
!say こんにちは       - 音声対話シミュレート
```

## 🔧 設定ファイル (.env)

```env
# Discord Bot設定
DISCORD_BOT_TOKEN=あなたのBot Token

# OpenAI API設定  
OPENAI_API_KEY=あなたのAPI Key

# VOICEVOX設定
VOICEVOX_URL=http://localhost:50021
```

## 💡 トラブルシューティング

### **よくある問題**

#### ❌ PyAudioエラー
```
→ ランチャーの「ライブラリアップデート」実行
```

#### ❌ VOICEVOX接続エラー
```
→ VOICEVOX.exe が起動しているか確認
→ http://localhost:50021 にアクセス可能か確認
```

#### ❌ Discord Bot Token エラー
```
→ .env ファイルのTOKENが正しいか確認
→ Discord Developer Portal で権限確認
```

#### ❌ 音声認識しない
```
→ Windowsのマイク設定確認
→ 「設定」→「プライバシー」→「マイク」
```

### **詳細診断**
```
🔍 troubleshoot.bat 実行
→ 生成されるログファイルを確認
```

## 🔗 必要なリンク

- **Discord Developer Portal**: https://discord.com/developers/applications
- **OpenAI API Keys**: https://platform.openai.com/api-keys  
- **VOICEVOX**: https://voicevox.hiroshiba.jp/

## 🎉 完了！

これで真の音声対話が可能になりました！

**Ctrl+Shift+Altを押しながら「こんにちは、せつな」と話してみてください** 🎤
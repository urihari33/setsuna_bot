# Windows環境での真の音声入力実現方法

## 必要な手順

### 1. Windowsに環境構築
```cmd
# Python環境セットアップ
cd /d D:\setsuna_bot
python -m venv setsuna_win_env
setsuna_win_env\Scripts\activate

# 必要なライブラリインストール（Windowsでは成功する）
pip install discord.py
pip install openai
pip install requests
pip install pygame
pip install python-dotenv
pip install SpeechRecognition
pip install pyaudio  # ← Windowsでは正常にインストール可能
pip install pynput
pip install pydub
```

### 2. VOICEVOX起動
```cmd
# VOICEVOXをWindows上で起動
VOICEVOX.exe
# → http://localhost:50021 で利用可能
```

### 3. Discord Bot起動
```cmd
python setsuna_discord_bot.py
# → 真の音声録音・ホットキー機能が動作
```

## 期待される動作
✅ Ctrl+Shift+Alt でリアルタイム音声録音
✅ Google Speech Recognition APIで音声認識
✅ VOICEVOX音声合成 → Discord再生
✅ 完全な音声対話ループ
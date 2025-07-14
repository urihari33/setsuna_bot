# Python仮想環境セットアップガイド

## 概要
このガイドは、せつなBotプロジェクトでPython仮想環境を作成・管理するための手順を説明します。

## 前提条件
- Python 3.9以上がインストールされている
- `D:\setsuna_bot`ディレクトリでの作業
- `requirements.txt`が存在している

## 🐍 仮想環境の作成手順

### 1. プロジェクトディレクトリに移動
```bash
cd "D:\setsuna_bot"
```

### 2. 仮想環境を作成
```bash
python -m venv venv
```

### 3. 仮想環境をアクティベート
環境に応じて以下のコマンドを使用：

#### Windows コマンドプロンプト
```bash
venv\Scripts\activate
```

#### Windows PowerShell
```bash
venv\Scripts\Activate.ps1
```

#### Git Bash / WSL
```bash
source venv/Scripts/activate
```

### 4. pipをアップグレード
```bash
pip install --upgrade pip
```

### 5. 必要なパッケージをインストール
```bash
pip install -r requirements.txt
```

### 6. 仮想環境の確認
```bash
python --version
pip list
```

## 🔧 日常的な使用方法

### 仮想環境をアクティベート
```bash
# プロジェクトディレクトリで
venv\Scripts\activate  # Windows
source venv/Scripts/activate  # Git Bash/WSL
```

### Pythonスクリプトを実行
```bash
# 仮想環境がアクティブな状態で
python voice_chat_gpt4.py
python core/setsuna_chat.py
```

### 仮想環境を非アクティベート
```bash
deactivate
```

## 📦 パッケージ管理

### 新しいパッケージのインストール
```bash
pip install package_name
```

### requirements.txtの更新
```bash
pip freeze > requirements.txt
```

### 特定のパッケージのアンインストール
```bash
pip uninstall package_name
```

## 🛠️ トラブルシューティング

### 仮想環境が作成されない場合
```bash
# Python venvモジュールの確認
python -m venv --help

# Pythonバージョンの確認
python --version
```

### PowerShellでActivate.ps1が実行できない場合
```powershell
# 実行ポリシーの確認
Get-ExecutionPolicy

# 実行ポリシーの変更（管理者権限が必要）
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### パッケージインストールでエラーが発生する場合
```bash
# pipのアップグレード
pip install --upgrade pip

# キャッシュクリア
pip cache purge

# 管理者権限で実行
# または --user フラグを使用
pip install --user package_name
```

## 📁 ディレクトリ構造

仮想環境作成後のディレクトリ構造：
```
D:\setsuna_bot\
├── venv\                 # 仮想環境ディレクトリ
│   ├── Scripts\          # 実行ファイル
│   │   ├── activate      # アクティベーションスクリプト
│   │   ├── python.exe    # Python実行ファイル
│   │   └── pip.exe       # pip実行ファイル
│   └── Lib\              # パッケージライブラリ
├── requirements.txt      # 必要パッケージ一覧
├── voice_chat_gpt4.py    # メインアプリケーション
└── ...
```

## ⚠️ 注意事項

### 1. 仮想環境のアクティベート確認
コマンドプロンプトの先頭に`(venv)`が表示されていることを確認：
```bash
(venv) D:\setsuna_bot>
```

### 2. .gitignoreの設定
仮想環境ディレクトリをGitで管理しないよう`.gitignore`に追加：
```gitignore
venv/
__pycache__/
*.pyc
```

### 3. 環境の再作成
問題が発生した場合は仮想環境を削除して再作成：
```bash
# 仮想環境を非アクティベート
deactivate

# 仮想環境ディレクトリを削除
rmdir /s venv  # Windows
rm -rf venv    # Git Bash/WSL

# 仮想環境を再作成
python -m venv venv
```

## 🎯 せつなBot特有の設定

### 必要な環境変数
仮想環境アクティベート後、以下の環境変数を設定：
```bash
# .envファイルの作成または確認
# OPENAI_API_KEY=your_api_key_here
# GOOGLE_API_KEY=your_google_api_key
# GOOGLE_CSE_ID=your_cse_id
```

### 主要な依存パッケージ
- `openai` - OpenAI API
- `speech_recognition` - 音声認識
- `pynput` - キーボード制御
- `requests` - HTTP通信
- `pyaudio` - 音声処理
- `google-api-python-client` - Google API
- `PyQt5` - GUI
- `pyyaml` - YAML処理

### 動作確認
```bash
# 仮想環境アクティベート後
python -c "import openai; print('OpenAI OK')"
python -c "import speech_recognition; print('SpeechRecognition OK')"
python -c "import pynput; print('Pynput OK')"
```

---

**作成日**: 2025年7月14日  
**対象プロジェクト**: せつなBot  
**Python版本**: 3.9.12  
**更新履歴**: 初版作成
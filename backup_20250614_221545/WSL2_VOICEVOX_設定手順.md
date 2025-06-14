# WSL2環境でのVOICEVOX接続設定手順

## 🚀 簡単設定（推奨）

### ステップ1: ファイアウォール設定
```powershell
# PowerShellを管理者権限で開いて実行
.\setup_firewall.ps1
```

### ステップ2: VOICEVOX起動
```batch
# start_voicevox_wsl.bat をダブルクリック、または
.\start_voicevox_wsl.bat
```

### ステップ3: 接続テスト
```bash
# WSL2側で実行
python test_voicevox_connection.py
```

---

## 🔧 手動設定（詳細）

### 1. VOICEVOXを外部接続対応で起動

**方法A: エンジンのみ起動（軽量）**
```batch
cd "%LOCALAPPDATA%\Programs\VOICEVOX\vv-engine"
.\run.exe --host 0.0.0.0 --port 50021
```

**方法B: VOICEVOX全体起動**
```batch
cd "%LOCALAPPDATA%\Programs\VOICEVOX"
.\VOICEVOX.exe --host 0.0.0.0 --port 50021
```

### 2. Windowsファイアウォール設定

**PowerShell（管理者権限）で実行:**
```powershell
New-NetFirewallRule -DisplayName "VOICEVOX WSL2" -Direction Inbound -Protocol TCP -LocalPort 50021 -Action Allow
```

**または、GUIで設定:**
1. Windows セキュリティ → ファイアウォールとネットワーク保護
2. 詳細設定 → 受信の規則 → 新しい規則
3. ポート → TCP → 特定のローカルポート: 50021
4. 接続を許可する → すべてのプロファイル → 名前: "VOICEVOX WSL2"

### 3. 接続確認

**Windows側:**
```batch
curl http://localhost:50021/version
```

**WSL2側:**
```bash
python test_voicevox_connection.py
```

---

## ❓ トラブルシューティング

### 問題: "接続エラー"が出る
- VOICEVOXが `--host 0.0.0.0` で起動されているか確認
- ファイアウォールでポート50021が許可されているか確認
- Windows側で `netstat -an | findstr 50021` でポートがリッスンされているか確認

### 問題: "タイムアウト"が出る
- VOICEVOXエンジンの起動完了まで15-30秒かかる場合があります
- 少し待ってから再度テストしてください

### 問題: IPアドレスが間違っている
- WSL2環境では Windows のIPアドレスが動的に変わる場合があります
- スクリプトが自動検出するIPが正しいか確認してください
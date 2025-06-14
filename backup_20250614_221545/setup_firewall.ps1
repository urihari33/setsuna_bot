# VOICEVOX WSL2対応 ファイアウォール設定スクリプト
# 管理者権限で実行してください

Write-Host "VOICEVOX WSL2対応 ファイアウォール設定" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green

# 既存のルールを削除（エラーは無視）
Write-Host "既存のVOICEVOXルールを削除中..." -ForegroundColor Yellow
Remove-NetFirewallRule -DisplayName "VOICEVOX WSL2" -ErrorAction SilentlyContinue

# 新しいルールを追加
Write-Host "新しいファイアウォールルールを追加中..." -ForegroundColor Yellow

# TCP 50021ポートのインバウンド接続を許可
New-NetFirewallRule -DisplayName "VOICEVOX WSL2" -Direction Inbound -Protocol TCP -LocalPort 50021 -Action Allow -Profile Any

Write-Host "✅ ファイアウォール設定完了" -ForegroundColor Green
Write-Host "ポート50021でWSL2からの接続が許可されました" -ForegroundColor Green

# 設定確認
Write-Host "`n設定確認:" -ForegroundColor Cyan
Get-NetFirewallRule -DisplayName "VOICEVOX WSL2" | Format-Table DisplayName, Direction, Action, Enabled

Write-Host "`n次のステップ:" -ForegroundColor Cyan
Write-Host "1. start_voicevox_wsl.bat を実行してVOICEVOXを起動"
Write-Host "2. WSL2側でpython test_voicevox_connection.py を実行"
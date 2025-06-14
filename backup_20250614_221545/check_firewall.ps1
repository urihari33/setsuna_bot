# ファイアウォール設定確認スクリプト

Write-Host "=== VOICEVOX ファイアウォール設定確認 ===" -ForegroundColor Green

# 既存のVOICEVOX関連ルールを確認
Write-Host "既存のVOICEVOX関連ルールを検索中..." -ForegroundColor Yellow
$rules = Get-NetFirewallRule | Where-Object { $_.DisplayName -like "*VOICEVOX*" -or $_.DisplayName -like "*WSL*" }

if ($rules) {
    Write-Host "発見されたルール:" -ForegroundColor Green
    $rules | Format-Table DisplayName, Direction, Action, Enabled -AutoSize
} else {
    Write-Host "VOICEVOX関連のルールが見つかりません" -ForegroundColor Red
}

# ポート50021の設定を確認
Write-Host "`nポート50021の設定を確認中..." -ForegroundColor Yellow
$portRules = Get-NetFirewallRule | Get-NetFirewallPortFilter | Where-Object { $_.LocalPort -eq "50021" }

if ($portRules) {
    Write-Host "ポート50021のルールが見つかりました:" -ForegroundColor Green
    foreach ($rule in $portRules) {
        $mainRule = Get-NetFirewallRule -AssociatedNetFirewallPortFilter $rule
        Write-Host "  - $($mainRule.DisplayName): $($mainRule.Action)" -ForegroundColor Cyan
    }
} else {
    Write-Host "ポート50021のルールが見つかりません" -ForegroundColor Red
}

Write-Host "`n=== 手動でファイアウォールルールを追加 ===" -ForegroundColor Yellow
Write-Host "以下のコマンドを実行してルールを追加してください:" -ForegroundColor White
Write-Host 'New-NetFirewallRule -DisplayName "VOICEVOX-WSL2" -Direction Inbound -Protocol TCP -LocalPort 50021 -Action Allow -Profile Any' -ForegroundColor Cyan
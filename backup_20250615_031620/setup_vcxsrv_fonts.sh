#!/bin/bash
# VcXsrv日本語フォント設定自動化スクリプト

echo "=== VcXsrv日本語フォント設定スクリプト ==="

# 1. フォントディレクトリ準備
echo "1. フォントディレクトリ設定..."
mkdir -p ~/.fonts

# Windowsフォントを直接コピー（シンボリックリンクではなく）
echo "2. Windowsフォントをコピー..."
if [ -f "/mnt/c/Windows/Fonts/meiryo.ttc" ]; then
    cp /mnt/c/Windows/Fonts/meiryo.ttc ~/.fonts/
    echo "✅ メイリオをコピー"
fi

if [ -f "/mnt/c/Windows/Fonts/YuGothR.ttc" ]; then
    cp /mnt/c/Windows/Fonts/YuGothR.ttc ~/.fonts/
    echo "✅ Yu Gothic Regularをコピー"
fi

if [ -f "/mnt/c/Windows/Fonts/YuGothM.ttc" ]; then
    cp /mnt/c/Windows/Fonts/YuGothM.ttc ~/.fonts/
    echo "✅ Yu Gothic Mediumをコピー"
fi

# 3. フォントキャッシュ更新
echo "3. フォントキャッシュ更新..."
fc-cache -fv ~/.fonts
fc-cache -fv ~/.local/share/fonts

# 4. 環境変数設定
echo "4. 環境変数設定..."
export FONTCONFIG_PATH=/etc/fonts:$HOME/.fonts:$HOME/.local/share/fonts
echo "export FONTCONFIG_PATH=/etc/fonts:\$HOME/.fonts:\$HOME/.local/share/fonts" >> ~/.bashrc

# 5. X11フォント設定（xsetが利用可能な場合）
echo "5. X11フォント設定..."
if command -v xset >/dev/null 2>&1; then
    echo "xsetコマンドでフォントパス追加を試行..."
    xset +fp ~/.fonts 2>/dev/null && echo "✅ ~/.fontsを追加" || echo "❌ ~/.fonts追加失敗"
    xset +fp ~/.local/share/fonts 2>/dev/null && echo "✅ ~/.local/share/fontsを追加" || echo "❌ ~/.local/share/fonts追加失敗"
    xset fp rehash 2>/dev/null && echo "✅ フォントキャッシュ更新" || echo "❌ フォントキャッシュ更新失敗"
else
    echo "xsetコマンドが利用できません"
fi

# 6. フォント確認
echo "6. 設定結果確認..."
echo "コピーしたフォント:"
ls -la ~/.fonts/

echo -e "\nfc-listでの認識確認:"
fc-list | grep -i -E "(meiryo|yugoth)" | head -3

echo -e "\n=== 設定完了 ==="
echo "次のステップ:"
echo "1. VcXsrvを再起動してください"
echo "2. 新しいターミナルでGUIアプリを起動してください"
echo "3. python test_japanese_gui_final.py でテストしてください"
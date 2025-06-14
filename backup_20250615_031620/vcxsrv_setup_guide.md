# VcXsrv設定変更ガイド - 日本語フォント対応

## 現在の問題
- VcXsrvが基本的なビットマップフォント（fixed）のみ認識
- TrueTypeフォント（TTF/TTC）が無効
- X11フォントパスが限定的

## VcXsrv設定変更手順

### 1. VcXsrvの再起動（重要）

#### A. 現在のVcXsrvを終了
1. Windowsのタスクトレイから VcXsrv アイコンを右クリック
2. "Exit" を選択

#### B. 新しい設定でVcXsrvを起動
1. XLaunch を起動
2. 設定画面で以下を選択：

**Display settings:**
- ✅ Multiple windows
- Display number: 0

**Client startup:**
- ✅ Start no client

**Extra settings:**
- ✅ Clipboard
- ✅ Primary Selection  
- ✅ Native opengl
- ✅ **Disable access control** ←重要
- ✅ **Additional parameters for VcXsrv:** ←重要
  ```
  -multiwindow -clipboard -wgl -ac -dpi 96 +extension GLX
  ```

### 2. フォントサーバー設定（WSL2側）

```bash
# フォントディレクトリをX11に追加
mkdir -p ~/.fonts
cp ~/.local/share/fonts/* ~/.fonts/ 2>/dev/null || true

# フォントキャッシュ強制更新
fc-cache -fv ~/.fonts
fc-cache -fv ~/.local/share/fonts

# X11フォントパス追加（VcXsrv再起動後）
export FONTCONFIG_PATH=/etc/fonts:/home/urihari/.local/share/fonts
```

### 3. 設定ファイル保存
設定完了後、XLaunchで "Save configuration" を選択し、
`vcxsrv_japanese.xlaunch` として保存

## 自動化スクリプト
以下のコマンドでVcXsrv設定を自動適用：
```bash
./setup_vcxsrv_fonts.sh
```
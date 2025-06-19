# 次回セッション クイックスタートガイド

**作成日時**: 2025年6月20日 17:30  
**プロジェクト**: YouTube知識システム  
**現在のフェーズ**: Phase 3 - プレイリスト別分析システム実装

## 🎯 次回の最優先タスク

### 1. 既存プレイリストJSONファイル生成
```bash
cd D:\setsuna_bot\youtube_knowledge_system
python generate_existing_playlist_jsons.py
```

**目的**: 既存の"第一回プレイリスト"のJSONファイルを生成  
**重要性**: プレイリスト別分析の前提条件  
**予想所要時間**: 10-15分

## 📋 今日完了した作業

### ✅ 完了項目
1. **プレイリスト動画収集問題の解決**
   - 57動画中7動画のみ収集される問題を調査・解決
   - 原因: 初回収集時の処理中断（重複チェック問題ではない）
   - 結果: 57動画完全収集成功確認

2. **認証システムの堅牢化**
   - JSONトークンファイルの読み込みエラー修復
   - JSON/pickle両対応 + 自動再認証機能実装
   - multi_playlist_collector.pyの認証処理修正

3. **デバッグツールの整備**
   - `debug_playlist_collection.py`: 詳細収集プロセス調査
   - `test_normal_collection.py`: 通常収集プロセステスト
   - API応答の詳細確認機能

## 🔄 現在のシステム状態

### データベース状況
- **統合データベース**: 111動画、2プレイリスト管理中
- **プレイリスト1**: "第一回プレイリスト"（54動画）
- **プレイリスト2**: "お手伝いした動画リスト"（57動画）

### 認証状況
- **YouTube Data API**: ✅ 正常動作
- **OpenAI API**: ✅ 正常動作
- **トークンファイル**: ✅ JSON形式で安定動作

## 🎯 次回の作業フロー

### Step 1: システム確認（5分）
```bash
cd D:\setsuna_bot\youtube_knowledge_system
python test_normal_collection.py
```

### Step 2: 既存プレイリストJSON生成（15分）
```bash
python generate_existing_playlist_jsons.py
```

### Step 3: プレイリスト別分析機能実装（60-90分）
- プレイリスト単位での分析実行機能
- 分析進捗の個別管理システム
- GUI分析機能のプレイリスト対応

## 📂 重要なファイル場所

### 実装済みファイル
- `collectors/multi_playlist_collector.py` - マルチプレイリスト収集（✅完成）
- `storage/unified_storage.py` - 統合データベース（✅完成）
- `managers/playlist_config_manager.py` - プレイリスト設定管理（✅完成）
- `gui/main_window.py` - GUIシステム（✅完成）

### 作業対象ファイル
- `generate_existing_playlist_jsons.py` - 既存プレイリストJSON生成（🎯次回実行）
- `analyzers/description_analyzer.py` - 分析システム（🔄プレイリスト対応予定）

### データファイル
- `data/unified_knowledge_db.json` - 統合データベース
- `data/playlist_configs.json` - プレイリスト設定
- `data/playlists/` - プレイリスト別JSONディレクトリ

## ⚠️ 重要な注意事項

### ファイルパス設定
- **必須**: すべてのパスは`D:/setsuna_bot/`で開始
- **禁止**: `/mnt/d/`パスは使用しない（WSL2マウントパス）

### 認証について
- JSONトークンファイル形式で安定動作
- エラー時は自動再認証が実行される
- `test_normal_collection.py`で認証状態確認可能

### API制限
- YouTube Data API: 中程度使用（今日のテストで消費）
- OpenAI API: 低使用量

## 🔍 トラブルシューティング

### よくある問題と解決策

#### 認証エラー
```bash
# 認証状態確認
python test_normal_collection.py
```

#### ファイルパスエラー
- `D:/`で始まるパスを使用
- CLAUDE.mdの「ファイルパス設定の重要な注意事項」を参照

#### JSON生成エラー
- 統合データベースの存在確認
- プレイリスト設定の確認

## 📈 次回セッション後の予定

### Phase 3 完了後の目標
1. **プレイリスト別分析システム**完成
2. **GUI分析機能のプレイリスト対応**
3. **せつなさん統合システム**の要件定義

### 予想される次のフェーズ
- **Phase 4**: せつなBot統合システム実装
- 分析結果の対話システム向け形式変換
- 記憶システムとの連携実装

---

**このファイルを次回セッション開始時に確認してください**  
**推奨作業時間**: 1-2時間  
**難易度**: 中程度（基盤システム完成済み）
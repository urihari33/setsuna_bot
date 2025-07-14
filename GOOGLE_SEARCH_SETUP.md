# Google Custom Search API設定手順（必須）

## 🚨 重要：MockSearchServiceは削除されました

この学習システムは現在、**Google Custom Search API専用**で動作します。  
以下の設定は**必須**です。

## 🔧 必須設定

### 1. 既に設定済み
- ✅ `GOOGLE_API_KEY` - Google API Key（.envに設定済み）
- ✅ `GOOGLE_SEARCH_ENGINE_ID` - Google Search Engine ID（.envに設定済み）

### 2. 設定が正しいか確認

現在の.env設定：
```bash
GOOGLE_API_KEY=AIzaSyBrCcmiVtGVYkg3AuQ4PMRbp7ARFlXsYXmA
GOOGLE_SEARCH_ENGINE_ID=52328810b877e402b
```

### 3. Google Custom Search Engine IDの取得方法

1. [Google Custom Search Engine](https://cse.google.com/cse/) にアクセス
2. 「Add」または「新しい検索エンジンを作成」をクリック
3. 検索対象サイトを「*」（全Web）に設定
4. 検索エンジンを作成
5. 「検索エンジンID」をコピーして.envに設定

### 4. 料金情報

- **無料枠**: 100検索/日
- **有料**: $5/1000検索（無料枠超過後）
- **制限**: 1日あたり最大10,000検索

### 5. 設定確認

設定が完了したら、以下で確認できます：

```bash
python -c "from core.config_manager import get_config_manager; config = get_config_manager(); print(f'Google API設定: {config.is_google_search_configured()}'); print(f'Search Engine ID: {config.get_google_search_engine_id()}')"
```

### 6. システム動作（重要な変更）

- **Google Search成功時**: 実際のWeb検索結果を使用
- **Google Search失敗時**: 学習セッション停止（Mockフォールバックなし）
- **設定不備時**: システム起動時にエラー表示
- **クォータ超過時**: 明確なエラーメッセージと推奨対応策を表示

### 7. 実装詳細

- **メインサービス**: `core/google_search_service.py`
- **検索管理**: `core/google_search_manager.py` (Google専用)
- **設定管理**: `core/config_manager.py` (Google設定必須化)
- **統合ファイル**: `core/mock_search_service.py` (後方互換性のみ)
- **使用箇所**: `core/activity_learning_engine.py`

### 8. 重要な変更点

- **MockSearchService削除**: モック検索は完全に削除されました
- **Google専用化**: Google Custom Search APIのみで動作
- **必須設定化**: Google API設定が必須になりました
- **エラー処理強化**: クォータ超過時の明確な対応指示

## 🚀 システム準備完了

現在の設定でGoogle Custom Search APIが利用可能です。学習セッションは実際のWeb検索データを取得します。

## ⚠️ 注意事項

1. **日次制限**: 100検索/日の無料枠があります
2. **クォータ管理**: 制限到達時は翌日まで待機が必要
3. **代替API**: 必要に応じてBing Search API等の追加を検討
4. **Mock削除**: フォールバック機能はありません
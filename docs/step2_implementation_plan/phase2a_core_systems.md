# Phase 2A: コアシステム実装詳細

## 🎯 Phase 2A 概要

### 実装期間
3週間（週1-3）

### 主要コンポーネント
1. **ActivityLearningEngine**: 学習セッション管理・実行
2. **KnowledgeDatabase**: 階層的知識蓄積・管理
3. **BudgetSafetyManager**: 予算制限・コスト管理
4. **SessionRelationshipManager**: セッション間関連性管理

## 🔧 週別実装計画

### 週1: ActivityLearningEngine + KnowledgeDatabase基盤

#### ActivityLearningEngine
**主要機能**
- 学習セッション作成・開始・停止
- 情報収集プロセス管理
- GPT-4-turbo統合・分析処理
- リアルタイム進捗追跡

**実装項目**
- セッション設定解析（テーマ、深度、時間制限）
- Web検索API統合（Google Custom Search、DuckDuckGo）
- 収集コンテンツ前処理・フィルタリング
- GPT-4-turbo分析パイプライン
- 進捗状況リアルタイム更新

**データ構造**
```python
learning_session = {
    "session_id": "unique_session_id",
    "theme": "学習テーマ",
    "type": "概要/深掘り/実用",
    "depth_level": 1-5,
    "time_limit": 1800,  # 秒
    "budget_limit": 5.0,  # ドル
    "status": "running/paused/completed/error",
    "progress": {
        "phase": "collection/analysis/integration",
        "collected_items": 0,
        "processed_items": 0,
        "important_findings": [],
        "current_cost": 0.0
    },
    "start_time": "ISO8601",
    "end_time": "ISO8601"
}
```

#### KnowledgeDatabase
**主要機能**
- 階層的知識構造管理（生情報→構造化→統合）
- 知識の保存・検索・更新
- 信頼性スコア管理
- 知識の時系列管理

**実装項目**
- JSON形式知識データベース設計
- 知識エンティティ・関係性管理
- 検索・フィルタリング機能
- バックアップ・復旧機能

**データ構造**
```python
knowledge_item = {
    "item_id": "unique_item_id",
    "session_id": "source_session_id",
    "layer": "raw/structured/integrated",
    "content": "知識内容",
    "source_url": "元URL",
    "reliability_score": 0.8,
    "importance_score": 0.7,
    "categories": ["技術", "市場"],
    "keywords": ["AI", "音楽生成"],
    "entities": ["OpenAI", "Transformer"],
    "created_at": "ISO8601",
    "updated_at": "ISO8601",
    "references": ["related_item_ids"]
}
```

### 週2: BudgetSafetyManager + SessionRelationshipManager

#### BudgetSafetyManager
**主要機能**
- 多段階予算制限（セッション/日次/月次）
- リアルタイムコスト追跡
- 自動停止・アラート機能
- コスト最適化提案

**実装項目**
- APIコスト計算ロジック
- 予算超過検知・停止機能
- 使用量履歴管理
- コスト予測・最適化

**予算管理構造**
```python
budget_config = {
    "limits": {
        "session_max": 10.0,    # セッションあたり上限
        "daily_max": 25.0,      # 日次上限
        "monthly_max": 200.0    # 月次上限
    },
    "alerts": {
        "session_50percent": True,
        "session_80percent": True,
        "daily_80percent": True
    },
    "auto_stop": {
        "session_limit": True,
        "daily_limit": True,
        "monthly_limit": True
    }
}
```

#### SessionRelationshipManager
**主要機能**
- セッション間の親子関係管理
- 関連性スコア計算
- 継承すべき知識の特定
- セッション系譜追跡

**実装項目**
- セッション関係性データ構造
- 親子・兄弟関係解析
- 知識継承ロジック
- 関連セッション推薦

**関係性構造**
```python
session_relationship = {
    "session_id": "current_session_id",
    "parent_session": "parent_session_id",
    "child_sessions": ["child_session_ids"],
    "related_sessions": ["related_session_ids"],
    "inherited_knowledge": ["knowledge_item_ids"],
    "relationship_type": "deep_dive/related/continuation",
    "relevance_score": 0.9
}
```

### 週3: コアシステム統合・テスト

#### 統合テスト項目
1. **エンドツーエンドテスト**
   - 学習セッション完全実行
   - 知識蓄積・検索動作確認
   - 予算管理・自動停止確認

2. **パフォーマンステスト**
   - 大量データ処理性能
   - API応答時間測定
   - メモリ使用量最適化

3. **安全性テスト**
   - 予算超過時の自動停止
   - エラー処理・復旧機能
   - データ整合性確認

#### 品質保証
- 単体テストカバレッジ80%以上
- 統合テスト全項目クリア
- エラーハンドリング完全実装

## 🔍 技術仕様詳細

### GPT-4-turbo統合
**使用モデル**: gpt-4-turbo-preview
**最大トークン**: セッションあたり50,000トークン
**温度設定**: 0.3（一貫性重視）

### API使用最適化
1. **バッチ処理**: 複数コンテンツの一括分析
2. **段階的処理**: 重要度による処理深度調整
3. **キャッシュ活用**: 類似分析結果の再利用

### データ保存形式
- **メインDB**: JSON形式ファイル
- **インデックス**: SQLite（高速検索用）
- **バックアップ**: 日次自動バックアップ

## 📊 パフォーマンス目標

### 処理性能
- セッション開始時間: 5秒以内
- コンテンツ処理速度: 10記事/分
- 知識検索応答時間: 1秒以内

### リソース使用量
- メモリ使用量: 1GB以内
- ディスク使用量: セッションあたり10MB以内
- CPU使用率: 平均50%以下

## 🔒 セキュリティ考慮

### APIキー管理
- 環境変数での安全な管理
- キー露出防止機能
- 使用量監視・異常検知

### データ保護
- 知識データの暗号化保存
- アクセス制御機能
- データ整合性チェック

## 🧪 テスト戦略

### 単体テスト
- 各コンポーネントの独立テスト
- モック・スタブを使用したAPI分離テスト
- エラーケース網羅テスト

### 統合テスト
- コンポーネント間連携テスト
- エンドツーエンドシナリオテスト
- パフォーマンス・負荷テスト

### 受け入れテスト
- 実際の学習シナリオでの動作確認
- ユーザビリティ検証
- システム安定性確認
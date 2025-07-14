# 学習セッション結果表示ガイド

## 🎯 概要

学習セッションで収集・分析された内容を確認するためのツール群です。Google検索で取得した実際のデータや、GPT-4による分析結果を詳しく見ることができます。

## 🔧 利用可能なツール

### 1. セッション結果ビューワー (`session_result_viewer.py`)

#### 基本的な使用方法

```bash
# セッション一覧表示
python session_result_viewer.py

# 特定セッションの詳細表示
python session_result_viewer.py <session_id>
```

#### 表示内容
- ✅ セッション基本情報（テーマ、タイプ、深度レベル）
- ✅ 実行情報（開始・終了時刻、ステータス、コスト）
- ✅ 収集結果（Google検索で取得したURL、タイトル、内容）
- ✅ 分析結果（GPT-4による重要発見、エンティティ抽出）
- ✅ 知識統合結果（サマリー、主要ポイント、推奨アクション）

### 2. HTMLレポート生成 (`session_html_report.py`)

#### 使用方法

```bash
# HTMLレポート生成
python session_html_report.py <session_id>
```

#### 特徴
- 🌐 ブラウザで見やすい形式
- 🎨 プロフェッショナルなデザイン
- 🔗 URLリンクのクリック可能
- 📊 カラーコード化された情報

## 📋 実際の使用例

### 最新セッションの確認

```bash
# 1. セッション一覧を表示
python session_result_viewer.py

# 2. 最新セッションID（session_20250710_xxxxxx）をコピー
# 3. 詳細表示
python session_result_viewer.py session_20250710_xxxxxx

# 4. HTMLレポート生成（ブラウザで見やすく）
python session_html_report.py session_20250710_xxxxxx
```

### Google検索結果の確認

学習セッションで実際に収集されたデータ：

- **収集ソース**: Google Custom Search APIから取得した実際のWebページ
- **URL**: クリック可能なリンク
- **内容**: 各ページの要約や抜粋
- **信頼性スコア**: ソースの信頼度評価
- **関連性スコア**: テーマとの関連度

### GPT-4分析結果の確認

- **重要な発見**: GPT-4が特定した重要なポイント
- **エンティティ抽出**: 人名、組織名、技術名等の抽出
- **関係性分析**: 概念間の関係性の分析
- **統合サマリー**: 全体を通した洞察とまとめ

## 🚀 活用シーン

### 1. 研究・調査結果の確認
```bash
# AI技術の市場調査セッション後
python session_result_viewer.py session_ai_market_research
python session_html_report.py session_ai_market_research
```

### 2. 競合分析の詳細確認
```bash
# 競合他社の動向調査後
python session_result_viewer.py session_competitor_analysis
```

### 3. プレゼン資料への活用
```bash
# HTMLレポートを生成してプレゼンに使用
python session_html_report.py session_presentation_research
# → 生成されたHTMLをブラウザで開いてコピー&ペースト
```

## 📁 ファイル構成

```
/mnt/d/setsuna_bot/
├── session_result_viewer.py      # メインビューワー
├── session_html_report.py        # HTMLレポート生成
├── data/activity_knowledge/
│   └── sessions/                  # セッションデータ保存先
│       ├── session_20250710_xxxxx.json
│       └── session_20250710_yyyyy.json
└── session_report_xxxxx.html     # 生成されたHTMLレポート
```

## 💡 Tips

### 最新セッションの簡単確認
```bash
# 最新セッションのHTMLレポートを即座に生成
python session_result_viewer.py | head -20  # 最新セッションIDを確認
python session_html_report.py <最新session_id>
```

### 複数セッションの比較
```bash
# 複数のセッション結果を比較
python session_result_viewer.py session_A
python session_result_viewer.py session_B
```

## 🔍 実際のデータ例

Google Custom Search APIが有効になった後の学習セッションでは：

1. **実際のWebサイト情報**
   - 企業の公式サイト
   - 技術ブログ記事
   - ニュース記事
   - 研究論文

2. **高品質な分析結果**
   - GPT-4による洞察
   - 実用的な推奨事項
   - 具体的なアクションプラン

3. **コスト効率**
   - Google: 100検索/日無料
   - OpenAI: GPT-4分析によるコスト

これらのツールにより、学習セッションの価値を最大限に活用できます。
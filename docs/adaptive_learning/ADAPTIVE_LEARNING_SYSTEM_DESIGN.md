# 人間評価型Simulated Annealing学習システム - システム設計書

## 📋 概要

**作成日**: 2025年7月11日  
**対象システム**: せつなBot 大規模適応学習システム  
**設計目標**: 1000セッション規模・人間評価・SA最適化

---

## 🎯 システム目標

### 主要目標
1. **大規模知識ベース構築**: 1000セッション規模のデータ蓄積
2. **効率的コスト管理**: セッション単価 < $1の実現
3. **人間評価型探索**: Simulated Annealing + ユーザーフィードバック
4. **適応的学習制御**: 温度パラメータによる探索戦略調整

### 成果指標
- **データ規模**: 1000セッション (現在15 → 目標1000)
- **コスト効率**: 総予算 $800-1000、平均 $0.8/セッション
- **品質向上**: 温度降下に伴う段階的品質向上
- **ユーザー満足度**: 対話的調整による方向性適合

---

## 🏗️ システムアーキテクチャ

### 全体構成図
```
┌─────────────────────────────────────────────────────────────────┐
│                人間評価型SA学習システム                              │
├─────────────────────────────────────────────────────────────────┤
│ ExplorationOrchestrator (探索統制エンジン)                        │
│  ├─ TemperatureController (温度制御)                            │
│  ├─ AdaptiveQueryGenerator (適応クエリ生成)                      │
│  ├─ BatchSessionManager (バッチセッション管理)                   │
│  ├─ ResultsAnalyzer (結果分析)                                 │
│  └─ UserFeedbackInterface (ユーザー対話)                        │
├─────────────────────────────────────────────────────────────────┤
│ 支援システム                                                      │
│  ├─ CostOptimizer (コスト最適化)                                │
│  ├─ QualityController (品質制御)                               │
│  ├─ PreferenceModel (嗜好学習)                                 │
│  └─ ExplorationGUI (探索GUI)                                   │
├─────────────────────────────────────────────────────────────────┤
│ 既存システム統合                                                   │
│  ├─ ActivityLearningEngine (学習エンジン)                        │
│  ├─ MultiSearchManager (検索統合)                               │
│  ├─ PreProcessingEngine (前処理)                               │
│  └─ SessionResultViewer (結果表示)                             │
└─────────────────────────────────────────────────────────────────┘
```

### データフロー
```
1. ユーザー: 初期テーマ・目標設定
2. ExplorationOrchestrator: 探索戦略決定
3. TemperatureController: 現在温度に応じた設定適用
4. AdaptiveQueryGenerator: 温度対応クエリ生成
5. BatchSessionManager: セッション群実行
6. ResultsAnalyzer: 結果分析・要約作成
7. UserFeedbackInterface: 結果提示・評価取得
8. フィードバック → 温度調整 → 次回探索 (ループ)
```

---

## 🌡️ Simulated Annealing設計

### 温度パラメータ定義
```python
TEMPERATURE_CONFIGS = {
    "high": {
        "exploration_scope": "maximum_breadth",    # 最大範囲探索
        "query_diversity": 0.9,                   # 多様性重視
        "quality_threshold": 0.3,                 # 低品質許容
        "sessions_per_round": 25,                 # 大量セッション
        "analysis_depth": "shallow",              # 浅い分析
        "cost_per_session": 0.5,                  # 低コスト
        "preprocessing_mode": "lightweight"       # 軽量前処理
    },
    "medium": {
        "exploration_scope": "focused_breadth",   # 焦点型広域
        "query_diversity": 0.6,                   # バランス重視
        "quality_threshold": 0.5,                 # 中品質要求
        "sessions_per_round": 15,                 # 中量セッション
        "analysis_depth": "medium",               # 中程度分析
        "cost_per_session": 1.0,                  # 中コスト
        "preprocessing_mode": "standard"          # 標準前処理
    },
    "low": {
        "exploration_scope": "deep_focus",        # 深度重視
        "query_diversity": 0.3,                   # 特化探索
        "quality_threshold": 0.8,                 # 高品質要求
        "sessions_per_round": 8,                  # 少数精鋭
        "analysis_depth": "deep",                 # 深い分析
        "cost_per_session": 2.5,                  # 高コスト
        "preprocessing_mode": "comprehensive"     # 包括前処理
    }
}
```

### 温度遷移アルゴリズム
```python
def calculate_next_temperature(current_temp, user_feedback, session_quality):
    """
    ユーザーフィードバックと品質に基づく温度調整
    
    Args:
        current_temp: 現在の温度 ("high", "medium", "low")
        user_feedback: ユーザー評価 ("deeper", "broader", "pivot", "focus")
        session_quality: セッション品質平均 (0.0-1.0)
    
    Returns:
        次回温度設定
    """
    # 品質が高く、深掘り要求 → 温度下げる
    if user_feedback == "deeper" and session_quality > 0.7:
        return cool_down(current_temp)
    
    # 品質が低く、横展開要求 → 温度上げる  
    elif user_feedback == "broader" or session_quality < 0.4:
        return heat_up(current_temp)
    
    # 方向転換要求 → 温度リセット
    elif user_feedback == "pivot":
        return "high"
    
    # その他 → 現状維持
    else:
        return current_temp
```

---

## 👤 人間評価システム

### 評価フィードバック設計
```python
class UserFeedbackTypes:
    DIRECTION_CHOICES = {
        "deeper": {
            "description": "このテーマをさらに深く探索",
            "temperature_effect": "cool_down",
            "scope_change": "narrow_focus"
        },
        "broader": {
            "description": "関連領域をもっと広く探索", 
            "temperature_effect": "heat_up",
            "scope_change": "expand_scope"
        },
        "pivot": {
            "description": "別の角度・視点から探索",
            "temperature_effect": "reset_high",
            "scope_change": "shift_direction"
        },
        "focus": {
            "description": "特定の側面に集中",
            "temperature_effect": "cool_down",
            "scope_change": "aspect_focus"
        },
        "merge": {
            "description": "複数テーマを統合",
            "temperature_effect": "maintain",
            "scope_change": "theme_integration"
        }
    }
    
    QUALITY_RATINGS = {
        "excellent": 0.9,    # 非常に価値のある情報
        "good": 0.7,         # 有用な情報
        "fair": 0.5,         # 普通の情報
        "poor": 0.3,         # 価値の低い情報
        "irrelevant": 0.1    # 無関係な情報
    }
```

### 結果提示フォーマット
```python
class ExplorationResultsPresentation:
    def create_summary(self, sessions: List[Session]) -> Dict:
        return {
            "exploration_overview": {
                "total_sessions": len(sessions),
                "themes_discovered": self.extract_themes(sessions),
                "quality_distribution": self.analyze_quality(sessions),
                "cost_summary": self.calculate_costs(sessions)
            },
            "key_discoveries": {
                "major_themes": self.rank_themes_by_importance(sessions),
                "unexpected_connections": self.find_surprising_links(sessions),
                "knowledge_gaps": self.identify_gaps(sessions),
                "high_value_insights": self.extract_insights(sessions)
            },
            "next_direction_suggestions": {
                "deeper_options": self.suggest_deep_dive_topics(sessions),
                "broader_options": self.suggest_expansion_areas(sessions),
                "pivot_options": self.suggest_alternative_angles(sessions),
                "focus_options": self.suggest_specific_aspects(sessions)
            },
            "progress_metrics": {
                "knowledge_coverage": self.calculate_coverage(sessions),
                "exploration_efficiency": self.calculate_efficiency(sessions),
                "budget_utilization": self.calculate_budget_usage(sessions)
            }
        }
```

---

## 💰 コスト最適化戦略

### セッション単価目標
```python
COST_OPTIMIZATION_STRATEGY = {
    "target_distribution": {
        "high_temp_sessions": {
            "count": 600,
            "target_cost": 0.6,
            "total_budget": 360
        },
        "medium_temp_sessions": {
            "count": 300, 
            "target_cost": 1.2,
            "total_budget": 360
        },
        "low_temp_sessions": {
            "count": 100,
            "target_cost": 2.8,
            "total_budget": 280
        }
    },
    "total_budget": 1000,
    "safety_margin": 0.15
}
```

### 効率化手法
1. **バッチ処理最適化**: 同時実行・API効率化
2. **前処理調整**: 温度に応じた処理レベル選択
3. **品質フィルタリング**: 早期品質判定・無駄排除
4. **キャッシュ活用**: 類似クエリ結果再利用
5. **API制限対応**: Rate Limiting最適化

---

## 📊 品質制御システム

### 品質メトリクス
```python
class QualityMetrics:
    def calculate_session_quality(self, session: Session) -> float:
        """セッション品質の総合評価"""
        return weighted_average([
            (session.relevance_score, 0.4),      # 関連性
            (session.information_value, 0.3),    # 情報価値
            (session.uniqueness_score, 0.2),     # 独自性
            (session.actionability, 0.1)         # 実用性
        ])
    
    def assess_exploration_progress(self, sessions: List[Session]) -> Dict:
        """探索進捗の品質評価"""
        return {
            "coverage_completeness": self.calculate_coverage(sessions),
            "depth_adequacy": self.assess_depth(sessions), 
            "diversity_balance": self.measure_diversity(sessions),
            "knowledge_coherence": self.evaluate_coherence(sessions)
        }
```

---

## 🔧 実装仕様

### コアクラス設計
```python
class ExplorationOrchestrator:
    """探索統制メインエンジン"""
    def __init__(self):
        self.temperature_controller = TemperatureController()
        self.query_generator = AdaptiveQueryGenerator()
        self.session_manager = BatchSessionManager()
        self.results_analyzer = ResultsAnalyzer()
        self.feedback_interface = UserFeedbackInterface()
    
    def start_adaptive_exploration(self, initial_theme: str, budget: float):
        """適応的探索開始"""
        pass
    
    def run_exploration_round(self) -> ExplorationResults:
        """探索ラウンド実行"""
        pass
    
    def process_user_feedback(self, feedback: UserFeedback):
        """ユーザーフィードバック処理"""
        pass

class TemperatureController:
    """温度制御システム"""
    def get_current_config(self) -> TemperatureConfig:
        """現在の温度設定取得"""
        pass
    
    def adjust_temperature(self, feedback: UserFeedback, quality: float):
        """温度調整"""
        pass

class AdaptiveQueryGenerator:
    """適応的クエリ生成"""
    def generate_temperature_adapted_queries(self, theme: str, temp_config: TemperatureConfig) -> List[str]:
        """温度対応クエリ生成"""
        pass
```

### データモデル
```python
@dataclass
class ExplorationRound:
    round_id: str
    theme: str
    temperature: str
    start_time: datetime
    sessions: List[Session]
    user_feedback: Optional[UserFeedback]
    cost_summary: CostSummary
    quality_metrics: QualityMetrics

@dataclass
class UserFeedback:
    direction_choice: str
    quality_rating: float
    specific_interests: List[str]
    continuation_preference: str
    timestamp: datetime

@dataclass
class TemperatureConfig:
    temperature_level: str
    exploration_scope: str
    query_diversity: float
    quality_threshold: float
    sessions_per_round: int
    analysis_depth: str
    cost_per_session: float
```

---

## 🗂️ ファイル構造

### 実装ディレクトリ
```
/core/adaptive_learning/
├── orchestrator.py              # ExplorationOrchestrator
├── temperature_controller.py    # TemperatureController  
├── adaptive_query_generator.py  # AdaptiveQueryGenerator
├── batch_session_manager.py     # BatchSessionManager
├── results_analyzer.py          # ResultsAnalyzer
├── user_feedback_interface.py   # UserFeedbackInterface
├── cost_optimizer.py            # CostOptimizer
├── quality_controller.py        # QualityController
├── preference_model.py           # PreferenceModel
└── models/
    ├── exploration_models.py     # データモデル
    ├── temperature_models.py     # 温度関連モデル
    └── feedback_models.py        # フィードバックモデル

/data/adaptive_learning/
├── exploration_sessions/        # 探索セッションデータ
├── temperature_history/         # 温度変化履歴
├── user_feedback_logs/          # ユーザー評価ログ
├── preference_models/           # 嗜好モデルデータ
└── cost_tracking/              # コスト追跡データ
```

---

## 🧪 テスト戦略

### テストカテゴリ
1. **単体テスト**: 各コンポーネントの機能検証
2. **統合テスト**: コンポーネント間連携確認
3. **システムテスト**: 全体フロー検証
4. **ユーザーテスト**: 実際の探索シナリオ

### 検証項目
- **温度制御精度**: SA温度パラメータの正確な制御
- **フィードバック反映**: ユーザー評価の適切な反映
- **コスト効率**: 予算制約内での最適化
- **品質向上**: 温度降下に伴う品質改善
- **スケーラビリティ**: 1000セッション規模対応

---

*設計書作成日: 2025年7月11日*  
*作成者: Claude Code (Sonnet 4)*  
*対象プロジェクト: せつなBot 人間評価型SA学習システム*
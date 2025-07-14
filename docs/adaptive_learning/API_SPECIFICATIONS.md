# API仕様書 - 人間評価型SA学習システム

## 📋 概要

**API設計原則**: RESTful・型安全・拡張可能  
**データ形式**: JSON・強型付きDataclass  
**エラーハンドリング**: 統一的例外処理

---

## 🏗️ コアAPIクラス

### ExplorationOrchestrator API

#### クラス定義
```python
class ExplorationOrchestrator:
    """探索統制メインエンジンAPI"""
    
    def __init__(self, config: OrchestratorConfig = None):
        """
        初期化
        
        Args:
            config: オーケストレーター設定
        """
        pass
    
    def start_exploration(self, 
                         theme: str, 
                         budget: float,
                         initial_temperature: str = "high",
                         session_limit: int = None) -> ExplorationSession:
        """
        新規探索セッション開始
        
        Args:
            theme: 探索テーマ
            budget: 予算制限 (USD)
            initial_temperature: 初期温度 ("high", "medium", "low")
            session_limit: セッション数制限
            
        Returns:
            ExplorationSession: 開始された探索セッション
            
        Raises:
            InvalidThemeError: テーマが無効
            BudgetError: 予算が不足
            ConfigurationError: 設定エラー
        """
        pass
    
    def run_exploration_round(self, 
                            session_id: str) -> ExplorationRoundResult:
        """
        探索ラウンド実行
        
        Args:
            session_id: 探索セッションID
            
        Returns:
            ExplorationRoundResult: ラウンド実行結果
            
        Raises:
            SessionNotFoundError: セッションが見つからない
            ResourceLimitError: リソース制限超過
        """
        pass
    
    def process_user_feedback(self, 
                            session_id: str,
                            feedback: UserFeedback) -> FeedbackProcessResult:
        """
        ユーザーフィードバック処理
        
        Args:
            session_id: 探索セッションID
            feedback: ユーザーフィードバック
            
        Returns:
            FeedbackProcessResult: フィードバック処理結果
        """
        pass
    
    def get_exploration_status(self, 
                             session_id: str) -> ExplorationStatus:
        """
        探索状態取得
        
        Args:
            session_id: 探索セッションID
            
        Returns:
            ExplorationStatus: 現在の探索状態
        """
        pass
    
    def finalize_exploration(self, 
                           session_id: str) -> ExplorationSummary:
        """
        探索終了・要約生成
        
        Args:
            session_id: 探索セッションID
            
        Returns:
            ExplorationSummary: 探索要約
        """
        pass
```

### TemperatureController API

#### クラス定義
```python
class TemperatureController:
    """SA温度制御システムAPI"""
    
    def get_current_temperature(self, session_id: str) -> TemperatureState:
        """
        現在温度状態取得
        
        Args:
            session_id: セッションID
            
        Returns:
            TemperatureState: 現在の温度状態
        """
        pass
    
    def get_temperature_config(self, 
                             temperature: str) -> TemperatureConfig:
        """
        温度設定取得
        
        Args:
            temperature: 温度レベル ("high", "medium", "low")
            
        Returns:
            TemperatureConfig: 温度設定
        """
        pass
    
    def adjust_temperature(self, 
                         session_id: str,
                         feedback: UserFeedback,
                         quality_metrics: QualityMetrics) -> TemperatureAdjustment:
        """
        温度調整
        
        Args:
            session_id: セッションID
            feedback: ユーザーフィードバック
            quality_metrics: 品質メトリクス
            
        Returns:
            TemperatureAdjustment: 温度調整結果
        """
        pass
    
    def calculate_next_temperature(self,
                                 current_temp: str,
                                 feedback: UserFeedback,
                                 session_quality: float) -> str:
        """
        次回温度計算
        
        Args:
            current_temp: 現在温度
            feedback: ユーザーフィードバック
            session_quality: セッション品質 (0.0-1.0)
            
        Returns:
            str: 次回温度レベル
        """
        pass
```

### AdaptiveQueryGenerator API

#### クラス定義
```python
class AdaptiveQueryGenerator:
    """適応的クエリ生成API"""
    
    def generate_temperature_adapted_queries(self,
                                           theme: str,
                                           temperature_config: TemperatureConfig,
                                           existing_knowledge: List[Session] = None) -> List[AdaptiveQuery]:
        """
        温度対応クエリ生成
        
        Args:
            theme: 探索テーマ
            temperature_config: 温度設定
            existing_knowledge: 既存知識セッション
            
        Returns:
            List[AdaptiveQuery]: 生成されたクエリリスト
        """
        pass
    
    def expand_query_diversity(self,
                             base_queries: List[str],
                             diversity_level: float) -> List[str]:
        """
        クエリ多様性拡張
        
        Args:
            base_queries: ベースクエリ
            diversity_level: 多様性レベル (0.0-1.0)
            
        Returns:
            List[str]: 拡張されたクエリ
        """
        pass
    
    def optimize_query_selection(self,
                                candidate_queries: List[AdaptiveQuery],
                                selection_criteria: SelectionCriteria) -> List[AdaptiveQuery]:
        """
        クエリ選択最適化
        
        Args:
            candidate_queries: 候補クエリ
            selection_criteria: 選択基準
            
        Returns:
            List[AdaptiveQuery]: 最適化されたクエリ
        """
        pass
```

### BatchSessionManager API

#### クラス定義
```python
class BatchSessionManager:
    """バッチセッション管理API"""
    
    def execute_session_batch(self,
                             queries: List[AdaptiveQuery],
                             temperature_config: TemperatureConfig,
                             cost_limit: float = None) -> BatchExecutionResult:
        """
        セッションバッチ実行
        
        Args:
            queries: 実行クエリ
            temperature_config: 温度設定
            cost_limit: コスト制限
            
        Returns:
            BatchExecutionResult: バッチ実行結果
        """
        pass
    
    def manage_parallel_execution(self,
                                session_requests: List[SessionRequest],
                                max_concurrent: int = 5) -> List[SessionResult]:
        """
        並列実行管理
        
        Args:
            session_requests: セッション要求
            max_concurrent: 最大同時実行数
            
        Returns:
            List[SessionResult]: セッション結果
        """
        pass
    
    def track_execution_costs(self,
                            sessions: List[Session]) -> CostSummary:
        """
        実行コスト追跡
        
        Args:
            sessions: セッション群
            
        Returns:
            CostSummary: コスト要約
        """
        pass
```

### ResultsAnalyzer API

#### クラス定義
```python
class ResultsAnalyzer:
    """結果分析API"""
    
    def analyze_exploration_results(self,
                                  sessions: List[Session],
                                  analysis_depth: str = "medium") -> ExplorationAnalysis:
        """
        探索結果分析
        
        Args:
            sessions: セッション群
            analysis_depth: 分析深度 ("shallow", "medium", "deep")
            
        Returns:
            ExplorationAnalysis: 分析結果
        """
        pass
    
    def extract_major_themes(self,
                           sessions: List[Session],
                           min_relevance: float = 0.5) -> List[ThemeCluster]:
        """
        主要テーマ抽出
        
        Args:
            sessions: セッション群
            min_relevance: 最小関連性
            
        Returns:
            List[ThemeCluster]: テーマクラスター
        """
        pass
    
    def identify_knowledge_gaps(self,
                              sessions: List[Session],
                              target_coverage: float = 0.8) -> List[KnowledgeGap]:
        """
        知識ギャップ特定
        
        Args:
            sessions: セッション群
            target_coverage: 目標カバレッジ
            
        Returns:
            List[KnowledgeGap]: 知識ギャップ
        """
        pass
    
    def calculate_quality_metrics(self,
                                sessions: List[Session]) -> QualityMetrics:
        """
        品質メトリクス計算
        
        Args:
            sessions: セッション群
            
        Returns:
            QualityMetrics: 品質メトリクス
        """
        pass
```

### UserFeedbackInterface API

#### クラス定義
```python
class UserFeedbackInterface:
    """ユーザーフィードバックインターフェースAPI"""
    
    def present_exploration_results(self,
                                  analysis: ExplorationAnalysis,
                                  presentation_mode: str = "interactive") -> ResultsPresentation:
        """
        探索結果提示
        
        Args:
            analysis: 探索分析結果
            presentation_mode: 提示モード ("interactive", "summary", "detailed")
            
        Returns:
            ResultsPresentation: 結果提示
        """
        pass
    
    def collect_direction_feedback(self,
                                 available_directions: List[DirectionOption]) -> DirectionChoice:
        """
        方向性フィードバック収集
        
        Args:
            available_directions: 利用可能な方向性選択肢
            
        Returns:
            DirectionChoice: 選択された方向性
        """
        pass
    
    def gather_quality_ratings(self,
                             sessions: List[Session],
                             rating_criteria: List[str]) -> List[QualityRating]:
        """
        品質評価収集
        
        Args:
            sessions: 評価対象セッション
            rating_criteria: 評価基準
            
        Returns:
            List[QualityRating]: 品質評価
        """
        pass
    
    def get_continuation_preference(self,
                                  current_status: ExplorationStatus) -> ContinuationChoice:
        """
        継続意向確認
        
        Args:
            current_status: 現在の探索状態
            
        Returns:
            ContinuationChoice: 継続選択
        """
        pass
```

---

## 📊 データモデル仕様

### 基本データ型

#### ExplorationSession
```python
@dataclass
class ExplorationSession:
    session_id: str
    theme: str
    start_time: datetime
    initial_temperature: str
    budget_limit: float
    session_limit: Optional[int]
    status: str  # "active", "paused", "completed", "error"
    
    # 進捗情報
    current_temperature: str
    rounds_completed: int
    total_cost: float
    sessions_executed: int
    
    # メタデータ
    created_by: str
    tags: List[str]
    notes: str
```

#### TemperatureConfig
```python
@dataclass
class TemperatureConfig:
    temperature_level: str  # "high", "medium", "low"
    exploration_scope: str
    query_diversity: float  # 0.0-1.0
    quality_threshold: float  # 0.0-1.0
    sessions_per_round: int
    analysis_depth: str  # "shallow", "medium", "deep"
    cost_per_session: float
    preprocessing_mode: str  # "lightweight", "standard", "comprehensive"
    
    # SA パラメータ
    cooling_rate: float
    acceptance_probability: float
    min_temperature: float
```

#### UserFeedback
```python
@dataclass
class UserFeedback:
    feedback_id: str
    session_id: str
    timestamp: datetime
    
    # 方向性フィードバック
    direction_choice: str  # "deeper", "broader", "pivot", "focus", "merge"
    direction_confidence: float  # 0.0-1.0
    
    # 品質評価
    overall_quality: float  # 0.0-1.0
    session_ratings: List[QualityRating]
    
    # 継続意向
    continuation_preference: str  # "continue", "pause", "redirect", "stop"
    
    # 自由記述
    comments: str
    interests: List[str]
    concerns: List[str]
```

#### ExplorationRoundResult
```python
@dataclass
class ExplorationRoundResult:
    round_id: str
    session_id: str
    round_number: int
    execution_time: datetime
    
    # 実行情報
    temperature_used: str
    queries_generated: List[AdaptiveQuery]
    sessions_executed: List[Session]
    
    # 結果サマリー
    sessions_completed: int
    total_cost: float
    average_quality: float
    themes_discovered: List[str]
    
    # エラー情報
    errors: List[ExecutionError]
    warnings: List[str]
    
    # 次回推奨
    recommended_next_temperature: str
    suggested_directions: List[DirectionOption]
```

#### ExplorationAnalysis
```python
@dataclass
class ExplorationAnalysis:
    analysis_id: str
    session_id: str
    analysis_timestamp: datetime
    analysis_depth: str
    
    # テーマ分析
    major_themes: List[ThemeCluster]
    theme_relationships: List[ThemeRelation]
    unexpected_connections: List[Connection]
    
    # 品質分析
    quality_distribution: QualityDistribution
    high_value_sessions: List[Session]
    improvement_opportunities: List[str]
    
    # カバレッジ分析
    knowledge_coverage: CoverageMetrics
    identified_gaps: List[KnowledgeGap]
    redundant_areas: List[str]
    
    # 進捗分析
    exploration_efficiency: float
    goal_achievement: float
    resource_utilization: ResourceUtilization
```

#### AdaptiveQuery
```python
@dataclass
class AdaptiveQuery:
    query_id: str
    query_text: str
    query_type: str  # "exploratory", "focused", "deep_dive", "related"
    
    # 生成情報
    source_theme: str
    generation_strategy: str
    temperature_context: str
    
    # 品質予測
    predicted_relevance: float
    predicted_uniqueness: float
    estimated_cost: float
    
    # メタデータ
    keywords: List[str]
    target_categories: List[str]
    priority_score: float
```

---

## 🔧 エラーハンドリング

### 例外クラス階層
```python
class AdaptiveLearningError(Exception):
    """基底例外クラス"""
    pass

class ConfigurationError(AdaptiveLearningError):
    """設定エラー"""
    pass

class SessionError(AdaptiveLearningError):
    """セッション関連エラー"""
    pass

class SessionNotFoundError(SessionError):
    """セッション未発見"""
    pass

class ResourceLimitError(AdaptiveLearningError):
    """リソース制限エラー"""
    pass

class BudgetExceededError(ResourceLimitError):
    """予算超過エラー"""
    pass

class TemperatureError(AdaptiveLearningError):
    """温度制御エラー"""
    pass

class QueryGenerationError(AdaptiveLearningError):
    """クエリ生成エラー"""
    pass

class AnalysisError(AdaptiveLearningError):
    """分析エラー"""
    pass
```

### エラーレスポンス形式
```python
@dataclass
class ErrorResponse:
    error_type: str
    error_code: str
    message: str
    details: Dict[str, Any]
    timestamp: datetime
    session_id: Optional[str]
    
    # デバッグ情報
    trace_id: str
    component: str
    recovery_suggestions: List[str]
```

---

## 🎛️ 設定仕様

### システム設定
```python
@dataclass
class SystemConfig:
    # API設定
    openai_api_key: str
    google_search_api_key: str
    max_concurrent_sessions: int = 5
    
    # デフォルト制限
    default_budget_limit: float = 100.0
    default_session_limit: int = 1000
    max_rounds_per_session: int = 20
    
    # 温度制御設定
    temperature_configs: Dict[str, TemperatureConfig]
    cooling_schedule: List[float]
    
    # 品質制御
    min_quality_threshold: float = 0.1
    max_quality_threshold: float = 0.9
    quality_improvement_target: float = 0.05
    
    # コスト制御
    cost_monitoring_enabled: bool = True
    cost_alert_threshold: float = 0.8
    auto_pause_on_budget_limit: bool = True
    
    # データ管理
    data_retention_days: int = 365
    auto_cleanup_enabled: bool = True
    backup_frequency_hours: int = 24
```

---

## 📡 通信プロトコル

### リクエスト/レスポンス形式

#### 標準リクエスト
```json
{
    "method": "start_exploration",
    "session_id": "optional_session_id",
    "parameters": {
        "theme": "AI音楽生成技術",
        "budget": 50.0,
        "initial_temperature": "high"
    },
    "metadata": {
        "user_id": "user_123",
        "client_version": "1.0.0",
        "timestamp": "2025-07-11T23:30:00Z"
    }
}
```

#### 標準レスポンス
```json
{
    "success": true,
    "result": {
        "session_id": "session_20250711_233000_abc123",
        "status": "started",
        "initial_state": { /* ExplorationSession object */ }
    },
    "metadata": {
        "execution_time": 1.23,
        "api_version": "1.0.0",
        "timestamp": "2025-07-11T23:30:01Z"
    }
}
```

#### エラーレスポンス
```json
{
    "success": false,
    "error": {
        "error_type": "BudgetExceededError",
        "error_code": "BUDGET_001",
        "message": "指定された予算が制限を超えています",
        "details": {
            "requested_budget": 1000.0,
            "max_allowed_budget": 500.0
        }
    },
    "metadata": {
        "execution_time": 0.05,
        "api_version": "1.0.0",
        "timestamp": "2025-07-11T23:30:00Z"
    }
}
```

---

*API仕様書作成日: 2025年7月11日*  
*作成者: Claude Code (Sonnet 4)*  
*バージョン: 1.0.0*
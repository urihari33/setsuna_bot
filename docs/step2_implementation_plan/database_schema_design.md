# データベース設計仕様書

## 🗄️ データベース構成概要

### 設計方針
- **JSON形式**: 柔軟性・可読性重視
- **階層構造**: 生情報→構造化→統合知識の3層管理
- **関係性管理**: セッション間・知識間の関連性追跡
- **インデックス**: SQLiteでの高速検索支援

### ファイル構成
```
data/
├── activity_knowledge/
│   ├── sessions/                    # セッション別データ
│   │   ├── session_YYYYMMDD_HHMMSS.json
│   │   └── index.json              # セッション一覧
│   ├── knowledge_graph/             # 知識グラフ構造
│   │   ├── entities.json           # エンティティ一覧
│   │   ├── relationships.json      # 関係性データ
│   │   └── categories.json         # カテゴリ分類
│   └── relationships/               # セッション関連性
│       ├── session_tree.json       # セッション系譜
│       └── knowledge_links.json    # 知識リンク
├── learning_budget/                 # 予算・コスト管理
│   ├── daily_usage.json           # 日次使用量
│   ├── monthly_budget.json        # 月次予算管理
│   └── cost_history.json          # コスト履歴
└── activity_proposals/              # 生成された活動提案
    ├── proposals_YYYYMM.json      # 月別提案データ
    └── accepted_proposals.json     # 採用された提案
```

## 📋 データスキーマ詳細

### 1. 学習セッションデータ

**sessions/session_YYYYMMDD_HHMMSS.json**
```json
{
  "session_metadata": {
    "session_id": "session_20250108_143022",
    "theme": "AI音楽生成技術調査",
    "learning_type": "概要調査",
    "depth_level": 3,
    "time_limit": 3600,
    "budget_limit": 5.0,
    "status": "completed",
    "created_at": "2025-01-08T14:30:22Z",
    "completed_at": "2025-01-08T15:15:33Z",
    "parent_session": "session_20250105_120000",
    "tags": ["AI", "音楽", "技術調査"]
  },
  
  "session_progress": {
    "phases": [
      {
        "phase": "information_collection",
        "start_time": "2025-01-08T14:30:22Z",
        "end_time": "2025-01-08T14:50:15Z",
        "status": "completed",
        "collected_items": 25,
        "cost": 0.15
      },
      {
        "phase": "content_analysis",
        "start_time": "2025-01-08T14:50:15Z", 
        "end_time": "2025-01-08T15:10:30Z",
        "status": "completed",
        "processed_items": 25,
        "cost": 1.20
      },
      {
        "phase": "knowledge_integration",
        "start_time": "2025-01-08T15:10:30Z",
        "end_time": "2025-01-08T15:15:33Z", 
        "status": "completed",
        "generated_knowledge": 15,
        "cost": 0.35
      }
    ],
    "total_cost": 1.70,
    "total_items_processed": 25
  },

  "collection_results": {
    "information_sources": [
      {
        "source_id": "web_001",
        "source_type": "web_search",
        "query": "AI音楽生成 Transformer 2024",
        "url": "https://example.com/ai-music-generation",
        "title": "最新AI音楽生成技術の動向",
        "content": "記事の全文内容...",
        "collected_at": "2025-01-08T14:35:10Z",
        "reliability_score": 0.8,
        "relevance_score": 0.9
      }
    ],
    "raw_content_count": 25,
    "filtered_content_count": 18,
    "analysis_ready_count": 15
  },

  "analysis_results": {
    "key_findings": [
      {
        "finding_id": "finding_001",
        "importance": 0.9,
        "category": "技術トレンド",
        "content": "Transformer技術がAI音楽生成の主流になっている",
        "supporting_sources": ["web_001", "web_003", "web_007"],
        "related_entities": ["Transformer", "音楽生成", "OpenAI"],
        "confidence": 0.85
      }
    ],
    "extracted_entities": [
      {
        "entity_id": "ent_transformer",
        "name": "Transformer",
        "type": "技術",
        "description": "注意機構を使った深層学習アーキテクチャ",
        "frequency": 15,
        "importance": 0.9
      }
    ],
    "identified_relationships": [
      {
        "relationship_id": "rel_001",
        "source_entity": "Transformer",
        "target_entity": "音楽生成",
        "relationship_type": "enables",
        "strength": 0.8
      }
    ]
  },

  "generated_knowledge": {
    "structured_knowledge": [
      {
        "knowledge_id": "know_001",
        "layer": "structured",
        "category": "技術概要",
        "title": "AI音楽生成におけるTransformer技術",
        "content": "構造化された知識内容...",
        "source_findings": ["finding_001", "finding_003"],
        "reliability": 0.8,
        "last_updated": "2025-01-08T15:15:33Z"
      }
    ],
    "integration_knowledge": [
      {
        "knowledge_id": "int_know_001", 
        "layer": "integrated",
        "title": "AI音楽生成技術の現状と展望",
        "summary": "統合的な理解内容...",
        "key_technologies": ["Transformer", "GAN", "Diffusion Models"],
        "market_status": "急速成長中",
        "future_outlook": "商用化が進む見込み",
        "activity_implications": ["技術検証動画制作", "ツール比較企画"]
      }
    ]
  },

  "session_statistics": {
    "information_collection": {
      "web_searches": 12,
      "news_articles": 8,
      "social_posts": 5,
      "total_sources": 25
    },
    "analysis_processing": {
      "gpt4_calls": 15,
      "total_input_tokens": 25000,
      "total_output_tokens": 8000,
      "processing_time": 1200
    },
    "cost_breakdown": {
      "openai_api": 1.45,
      "search_api": 0.20,
      "news_api": 0.05,
      "total": 1.70
    }
  }
}
```

### 2. セッション関連性データ

**relationships/session_tree.json**
```json
{
  "session_relationships": [
    {
      "session_id": "session_20250108_143022",
      "parent_session": "session_20250105_120000",
      "relationship_type": "deep_dive",
      "inheritance_data": {
        "inherited_knowledge": ["know_base_001", "know_base_003"],
        "focus_areas": ["Transformer技術", "商用ツール"],
        "avoided_duplicates": ["基本概念", "歴史的経緯"]
      },
      "child_sessions": [],
      "related_sessions": [
        {
          "session_id": "session_20250106_160000",
          "relationship": "parallel_research",
          "relevance_score": 0.7
        }
      ],
      "knowledge_evolution": {
        "new_concepts": ["リアルタイム生成", "個人化技術"],
        "updated_concepts": ["商用化状況", "技術精度"],
        "deprecated_concepts": []
      }
    }
  ],
  
  "session_lineage": {
    "root_sessions": ["session_20250105_120000"],
    "lineage_trees": [
      {
        "root": "session_20250105_120000",
        "branches": [
          {
            "session": "session_20250108_143022",
            "depth": 1,
            "children": []
          }
        ]
      }
    ]
  }
}
```

### 3. 知識グラフデータ

**knowledge_graph/entities.json**
```json
{
  "entities": [
    {
      "entity_id": "ent_transformer",
      "name": "Transformer",
      "type": "技術",
      "description": "注意機構を使った深層学習アーキテクチャ",
      "aliases": ["トランスフォーマー", "Attention機構"],
      "first_discovered": "session_20250105_120000",
      "last_updated": "session_20250108_143022",
      "frequency": 25,
      "importance_score": 0.9,
      "categories": ["AI技術", "深層学習", "音楽生成"],
      "related_sessions": ["session_20250105_120000", "session_20250108_143022"],
      "activity_relevance": {
        "content_creation": 0.8,
        "technical_explanation": 0.9,
        "market_analysis": 0.6
      }
    }
  ],
  
  "entity_statistics": {
    "total_entities": 156,
    "by_type": {
      "技術": 45,
      "企業": 23,
      "製品": 31,
      "人物": 12,
      "概念": 45
    },
    "by_importance": {
      "high": 25,
      "medium": 67,
      "low": 64
    }
  }
}
```

**knowledge_graph/relationships.json**
```json
{
  "relationships": [
    {
      "relationship_id": "rel_transformer_music",
      "source_entity": "ent_transformer",
      "target_entity": "ent_music_generation",
      "relationship_type": "enables",
      "strength": 0.9,
      "direction": "directional",
      "discovered_in": "session_20250105_120000",
      "reinforced_in": ["session_20250108_143022"],
      "supporting_evidence": [
        "複数の論文でTransformerベース音楽生成モデルが報告",
        "主要な商用ツールがTransformerを採用"
      ],
      "confidence": 0.85
    }
  ],
  
  "relationship_types": {
    "enables": "技術的実現関係",
    "competes_with": "競合関係", 
    "depends_on": "依存関係",
    "part_of": "包含関係",
    "similar_to": "類似関係"
  }
}
```

### 4. 予算管理データ

**learning_budget/monthly_budget.json**
```json
{
  "budget_period": "2025-01",
  "budget_config": {
    "monthly_limit": 200.0,
    "daily_limit": 25.0,
    "session_limits": {
      "light": 2.0,
      "standard": 5.0,
      "thorough": 10.0,
      "unlimited": 25.0
    },
    "alert_thresholds": {
      "session_50percent": true,
      "session_80percent": true,
      "daily_80percent": true,
      "monthly_80percent": true
    }
  },
  
  "usage_tracking": {
    "current_month_total": 45.30,
    "daily_usage": {
      "2025-01-08": 12.50,
      "2025-01-07": 8.30,
      "2025-01-06": 15.20
    },
    "session_usage": [
      {
        "session_id": "session_20250108_143022",
        "planned_budget": 5.0,
        "actual_cost": 1.70,
        "efficiency": 0.34
      }
    ]
  },
  
  "cost_optimization": {
    "total_savings": 23.40,
    "optimization_methods": {
      "batch_processing": 8.20,
      "cache_utilization": 7.10,
      "api_efficiency": 8.10
    },
    "efficiency_trends": {
      "average_session_efficiency": 0.42,
      "improving_trend": true
    }
  }
}
```

### 5. 活動提案データ

**activity_proposals/proposals_202501.json**
```json
{
  "month": "2025-01",
  "generated_proposals": [
    {
      "proposal_id": "prop_20250108_001",
      "generated_from": "session_20250108_143022",
      "proposal_type": "content_creation",
      "title": "AI音楽生成ツール比較動画企画",
      "description": "主要なAI音楽生成ツールを実際に使って比較検証する動画企画",
      "generated_at": "2025-01-08T15:20:00Z",
      
      "knowledge_basis": {
        "source_sessions": ["session_20250105_120000", "session_20250108_143022"],
        "key_knowledge": ["商用ツール比較", "技術的差異", "ユーザビリティ"],
        "market_opportunity": "技術比較コンテンツの需要",
        "technical_feasibility": 0.8
      },
      
      "proposal_details": {
        "target_audience": "技術系クリエイター、音楽制作者",
        "difficulty_level": "medium",
        "required_resources": ["AI音楽ツールアカウント", "録画環境", "音楽知識"],
        "estimated_duration": "1週間",
        "expected_impact": {
          "audience_growth": 0.7,
          "expertise_demonstration": 0.9,
          "community_value": 0.8
        }
      },
      
      "implementation_plan": {
        "phase1": "ツール選定・アカウント取得（1日）",
        "phase2": "各ツールでの楽曲生成実験（3日）",
        "phase3": "比較分析・スクリプト作成（2日）",
        "phase4": "動画撮影・編集・公開（1日）"
      },
      
      "status": "pending",
      "user_feedback": null,
      "acceptance_date": null
    }
  ],
  
  "proposal_statistics": {
    "total_generated": 8,
    "by_type": {
      "content_creation": 3,
      "tool_development": 2,
      "collaboration": 2,
      "market_research": 1
    },
    "acceptance_rate": 0.375,
    "implementation_success_rate": 0.667
  }
}
```

## 🔍 インデックス・検索最適化

### SQLiteインデックス設計
```sql
-- セッション検索用インデックス
CREATE INDEX idx_session_theme ON sessions(theme);
CREATE INDEX idx_session_date ON sessions(created_at);
CREATE INDEX idx_session_type ON sessions(learning_type);

-- 知識検索用インデックス  
CREATE INDEX idx_knowledge_category ON knowledge(category);
CREATE INDEX idx_knowledge_keywords ON knowledge_keywords(keyword);
CREATE INDEX idx_entity_name ON entities(name);

-- 関係性検索用インデックス
CREATE INDEX idx_relationship_source ON relationships(source_entity);
CREATE INDEX idx_relationship_type ON relationships(relationship_type);
```

### 検索クエリ最適化
- **フルテキスト検索**: FTS5拡張使用
- **類似度検索**: ベクトル類似度計算
- **階層検索**: セッション系譜での検索

この設計により、効率的で拡張性の高い知識管理システムを実現できます。
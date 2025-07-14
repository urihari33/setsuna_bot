# せつなBot ファイル構造

## コアシステム

### メインアプリケーション
- `voice_chat_gpt4.py` - メインアプリケーション（音声チャット統合）
- `voice_synthesizer.py` - VOICEVOX音声合成システム
- `speech_text_converter.py` - 音声テキスト変換
- `project_system.py` - プロジェクト管理システム

### 設定・環境管理
- `CLAUDE.md` - Claude Code向け開発ガイド
- `requirements.txt` - Python依存関係
- `debug_settings.json` - デバッグ設定

## coreディレクトリ（主要機能）

### 会話システム
- `core/setsuna_chat.py` - せつなキャラクターチャット
- `core/multi_turn_conversation_manager.py` - 会話管理
- `core/conversation_context_builder.py` - 会話コンテキスト構築
- `core/conversation_knowledge_provider.py` - 会話知識提供
- `core/conversation_project_context.py` - プロジェクト会話コンテキスト

### 検索・知識システム
- `core/google_search_service.py` - Google検索サービス
- `core/duckduckgo_search_service.py` - DuckDuckGo検索サービス
- `core/multi_search_manager.py` - 複数検索管理
- `core/knowledge_database.py` - 知識データベース
- `core/knowledge_integration_system.py` - 知識統合システム
- `core/dynamic_query_generator.py` - 動的クエリ生成

### 分析・学習システム
- `core/activity_learning_engine.py` - 活動学習エンジン
- `core/activity_proposal_engine.py` - 活動提案エンジン
- `core/preprocessing_engine.py` - 前処理エンジン
- `core/topic_learning_system.py` - トピック学習システム

### 画像・動画処理
- `core/image_analyzer.py` - 画像分析
- `core/image_manager.py` - 画像管理
- `core/video_conversation_history.py` - 動画会話履歴
- `core/video_image_context.py` - 動画画像コンテキスト

### メモリ・セッション管理
- `core/long_term_project_memory.py` - 長期プロジェクトメモリ
- `core/session_relationship_manager.py` - セッション関係管理

### 品質管理
- `core/quality_monitoring/quality_history_manager.py` - 品質履歴管理
- `core/knowledge_analysis/knowledge_analysis_engine.py` - 知識分析エンジン
- `core/knowledge_analysis/report_quality_validator.py` - レポート品質検証

### 表示・UI
- `core/rich_message_renderer.py` - メッセージ表示
- `core/progress_manager.py` - 進捗管理
- `core/progress_widget.py` - 進捗ウィジェット

### 適応学習システム
- `core/adaptive_learning/accurate_cost_calculator.py` - コスト計算
- `core/adaptive_learning/duckduckgo_search_service.py` - DuckDuckGo検索
- `core/adaptive_learning/gpt35_analysis_service.py` - GPT-3.5分析サービス

## characterディレクトリ（キャラクター設定）

### 基本設定
- `character/setsuna_memory_data.json` - せつなメモリデータ
- `character/setsuna_projects.json` - せつなプロジェクトデータ
- `character/setsuna_responses.json` - せつな応答データ
- `character/setsuna_memories.txt` - せつなメモリ
- `character/setsuna_personality.md` - せつな性格設定

### プロンプト管理
- `character/prompts/base_personality.yaml` - 基本性格
- `character/prompts/emotional_responses.yaml` - 感情応答
- `character/prompts/mode_adjustments.yaml` - モード調整
- `character/prompts/speech_patterns.yaml` - 会話パターン

### 管理システム
- `character/managers/character_consistency.py` - キャラクター一貫性
- `character/managers/prompt_manager.py` - プロンプト管理

### 設定
- `character/settings/character_config.yaml` - キャラクター設定

## dataディレクトリ（データ保存）

### 基本データ
- `data/conversation_context.json` - 会話コンテキスト
- `data/multi_turn_conversations.json` - 複数ターン会話
- `data/user_preferences.json` - ユーザー設定
- `data/video_conversation_history.json` - 動画会話履歴

### 活動知識データ
- `data/activity_knowledge/` - 活動知識データ
- `data/adaptive_learning/` - 適応学習データ

## youtube_knowledge_systemディレクトリ（YouTube知識システム）

### システム構成
- `youtube_knowledge_system/core/data_models.py` - データモデル
- `youtube_knowledge_system/core/adaptive_learning_system.py` - 適応学習システム
- `youtube_knowledge_system/config/settings.py` - 設定
- `youtube_knowledge_system/storage/unified_storage.py` - 統合ストレージ

### GUI
- `youtube_knowledge_system/gui/video_main_window.py` - メインウィンドウ

### データ
- `youtube_knowledge_system/data/unified_knowledge_db.json` - 統合知識データベース

## enhanced_memoryディレクトリ（拡張メモリ）

- `enhanced_memory/memory_integration.py` - メモリ統合
- `enhanced_memory/collaboration_memory.py` - コラボレーションメモリ
- `enhanced_memory/personality_memory.py` - 性格メモリ

## guiディレクトリ（GUI）

- `gui/learning_session_gui.py` - 学習セッションGUI

## configディレクトリ（設定）

- `config/api_secrets.yaml` - API秘密鍵
- `config/production_config.yaml` - 本番設定
- `config/youtube_credentials.json` - YouTube認証情報

## キャッシュ・一時データ

- `voice_cache/` - 音声キャッシュ
- `response_cache/` - レスポンスキャッシュ
- `video_images/` - 動画画像

## バックアップ・ログ

- `backups/` - バックアップデータ
- `logs/` - ログファイル

## テストディレクトリ

- `test/` - テストファイル置き場（今後のテストファイル用）

## 文書・ドキュメント

- `docs/` - システム文書
- `*.md` - プロジェクト文書（レポート等）
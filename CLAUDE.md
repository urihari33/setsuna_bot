# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Language Requirements

**All communication with users should be in Japanese.** This project is designed for Japanese users, and the AI character せつな responds exclusively in Japanese. When working on this codebase, provide explanations, error messages, and documentation in Japanese to maintain consistency with the project's target audience.

## Project Overview

This is せつなBot (Setsuna Bot), a Japanese conversational AI system with voice synthesis capabilities. The project provides a web-based interface for real-time chat with an AI character named "片無せつな" (Katanashi Setsuna) using OpenAI GPT for conversation and VOICEVOX for Japanese text-to-speech synthesis.

## Architecture

The system follows a modular architecture with three main layers:

### Core Components (`core/` directory)
- **setsuna_chat.py**: OpenAI GPT integration with character-specific prompts and conversation history management
- **voice_output.py**: VOICEVOX API integration with caching, WSL2 network detection, and audio playback via pygame
- **voice_input.py**: Audio input handling (various implementations available)
- **hotkey_listener.py**: Keyboard shortcut handling

### Web Application Layer
- **setsuna_web_app.py**: Flask/SocketIO web server that integrates all core components
- **templates/setsuna_web.html**: Single-page web interface with real-time chat and voice controls

### Data Flow
1. User input → Web UI → Flask SocketIO → SetsunaChat (GPT) → response generation
2. Response text → VoiceOutput → VOICEVOX API → audio synthesis → browser playback
3. Voice settings updates flow through Flask API → VoiceOutput parameter updates

## Running the Application

### Prerequisites
- Python 3.9+ with required packages: flask, flask-socketio, openai, requests, pygame, python-dotenv
- VOICEVOX running on Windows host (automatically detected via WSL2 gateway IP)
- OpenAI API key in `.env` file: `OPENAI_API_KEY=your_key_here`

### Start the Web Application
```bash
python setsuna_web_app.py
```
Access via browser at `http://localhost:5000`

### Testing Voice Functionality
```bash
python core/voice_output.py  # Test VOICEVOX connection and synthesis
```

## Development Notes

### Voice System Architecture
The voice system automatically detects the Windows host IP in WSL2 environments and connects to VOICEVOX running on Windows. Voice synthesis uses caching (SHA1 hashes) to avoid re-synthesizing identical text.

### Character Implementation
The AI character "せつな" has a defined personality implemented through system prompts in `setsuna_chat.py`. The character is designed to be thoughtful, gentle, and uses specific Japanese speech patterns.

### Error Handling
Both chat and voice systems include fallback mechanisms. Chat falls back to simple pattern matching if OpenAI is unavailable. Voice synthesis degrades gracefully if VOICEVOX is not accessible.

### State Management
The web application uses a global `bot_state` dictionary for tracking conversation count, voice settings, system status, and chat history. This state is synchronized with clients via SocketIO events.

### Configuration
- VOICEVOX speaker ID is set to 20 (Setsuna voice) in `voice_output.py`
- Voice parameters (speed, pitch, intonation) are adjustable via web UI
- OpenAI model is set to "gpt-4" with max 150 tokens for voice-appropriate responses

## Development Methodology

**実装時の基本方針**: すべての新機能実装において、以下の段階的アプローチを採用する：

### 1. 段階的実装プロセス
- **Phase 1**: 個別機能の単体テスト作成・実行
- **Phase 2**: 統合テスト実施・問題特定
- **Phase 3**: 実装修正・再テスト
- **Phase 4**: 最終統合・動作確認

### 2. テスト駆動の確認手順
- 各実装段階で専用テストファイルを作成
- Windows環境とWSL2環境の違いを考慮
- 依存関係の段階的確認（ライブラリ→基本機能→統合機能）
- 成功・失敗の明確な判定基準設定

### 3. ユーザーとのコミュニケーション
- 各テスト結果の詳細説明
- 問題発生時の原因分析・代替案提示
- 次のステップの明確な提示
- 実装方針の事前確認

### 4. 実装品質基準
- フォールバック機能の必須実装
- エラーハンドリングの完全性
- ログ出力の詳細性
- 段階的な機能有効化

この方針により、複雑な機能でも確実に動作する実装を実現する。

## バッチファイル作成方針

**バッチファイル(.bat)作成の制限**: ユーザーから明示的に要求されない限り、Windows バッチファイルを自動的に作成・提示してはならない。過去にバッチファイルの実行で問題が発生した経験があるため、ユーザーが特別に依頼した場合のみ作成する。

代替として以下を推奨：
- Python スクリプトでの直接実行方法の説明
- コマンドライン実行手順の詳細提示
- 仮想環境のアクティベーション方法の説明
# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Language Requirements

**All communication with users should be in Japanese.** This project is designed for Japanese users, and the AI character せつな responds exclusively in Japanese. When working on this codebase, provide explanations, error messages, and documentation in Japanese to maintain consistency with the project's target audience.

## Project Overview

This is せつなBot (Setsuna Bot), a Japanese conversational AI system with voice synthesis capabilities. The project provides a hotkey-based voice conversation interface with an AI character named "片無せつな" (Katanashi Setsuna) using OpenAI GPT-4-Turbo for conversation and VOICEVOX for Japanese text-to-speech synthesis.

## Architecture

The system follows a simplified modular architecture with integrated voice conversation:

### Core Components
- **voice_chat_gpt4.py**: Main application integrating voice recognition, GPT-4-Turbo conversation, and voice synthesis with hotkey controls
- **core/setsuna_chat.py**: OpenAI GPT-4-Turbo integration with character-specific prompts and conversation history management  
- **voice_synthesizer.py**: VOICEVOX API integration with caching, WSL2 network detection, and audio playback

### Data Flow
1. Hotkey press (Ctrl+Shift+Alt) → Voice recording (15 seconds) → Google Speech Recognition
2. Recognized text → SetsunaChat (GPT-4-Turbo) → Character response generation
3. Response text → VoiceVoxSynthesizer → VOICEVOX API → Audio synthesis → Playback

## Running the Application

### Prerequisites
- Python 3.9+ with required packages: speech_recognition, pynput, openai, requests, pyaudio
- VOICEVOX running on Windows localhost
- OpenAI API key in `.env` file: `OPENAI_API_KEY=your_key_here`
- Microphone and speakers/headphones
- Windows環境（WSL2は非対応）

### Start the Voice Chat System
```bash
python voice_chat_gpt4.py
```
Use Ctrl+Shift+Alt hotkey combination to start voice input, Ctrl+C to exit

### Testing Individual Components
```bash
python core/setsuna_chat.py      # Test GPT-4-Turbo chat integration
python voice_synthesizer.py     # Test VOICEVOX connection and synthesis
```

## Development Notes

### Voice System Architecture
The voice system automatically detects the Windows host IP in WSL2 environments and connects to VOICEVOX running on Windows. Voice synthesis uses caching (SHA1 hashes) to avoid re-synthesizing identical text.

### Character Implementation
The AI character "せつな" has a defined personality implemented through system prompts in `setsuna_chat.py`. The character is designed to be thoughtful, gentle, and uses specific Japanese speech patterns.

### Error Handling
Both chat and voice systems include fallback mechanisms. Chat falls back to simple pattern matching if OpenAI is unavailable. Voice synthesis degrades gracefully if VOICEVOX is not accessible.

### State Management
The voice chat application maintains conversation history through the SetsunaChat class, with global state management for hotkey detection and voice processing status. Voice cache is maintained automatically to improve response times for repeated phrases.

### Configuration
- VOICEVOX speaker ID is set to 20 (Setsuna voice) in `voice_synthesizer.py`
- OpenAI model is set to "gpt-4-turbo" with max 150 tokens for voice-appropriate responses
- Voice recording timeout set to 15 seconds for longer conversations
- Audio preprocessing optimized for fast response times

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

## ファイルパス設定の重要な注意事項

**Windows環境でのパス設定**: この環境はWSL2上で動作しているが、実際のファイル保存・読み込みはWindows側で行う必要がある。そのため、Pythonファイル内でのパス指定では以下の規則を厳守すること：

### 正しいパス設定
```python
# 正しい：Windows環境での実際のパス
DATA_DIR = Path("D:/setsuna_bot/youtube_knowledge_system/data")
output_path = Path("D:/setsuna_bot/output/result.json")
```

### 間違ったパス設定
```python
# 間違い：WSL2のマウントパス（ファイル保存に失敗する）
DATA_DIR = Path("/mnt/d/setsuna_bot/youtube_knowledge_system/data")
output_path = Path("/mnt/d/setsuna_bot/output/result.json")
```

### 適用対象
- すべてのデータ保存処理
- 設定ファイルの読み込み
- ログファイルの出力
- 一時ファイルの作成

この規則に従わない場合、ファイルの保存・読み込みが失敗し、機能が正常に動作しない。

## 重要な実行環境に関する注意事項

### 実行環境
**すべてのPythonスクリプトはWindows環境で直接実行すること**。WSL2環境は非対応です。

### Windows環境での要件
- VOICEVOXはWindows上で直接起動する必要があります
- 音声入出力デバイスへの直接アクセスが必要です
- Windows標準の音声再生機能（winsound）を使用します

### 外部サービステスト
VOICEVOXとの連携テストは通常のWindows環境で実行してください：
- VOICEVOX APIへの接続テスト（localhost:50021）
- 音声入出力デバイスへのアクセス
- Windows音声再生システム
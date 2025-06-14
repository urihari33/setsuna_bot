# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Japanese virtual character AI chatbot called "片無せつな (Katanashi Setsuna)" - a voice-interactive AI companion that responds with synthesized speech. The system integrates OpenAI GPT-4, Google Speech Recognition, and VOICEVOX text-to-speech synthesis.

## Core Architecture

### Main Components

- **setsuna_bot.py**: Core chat logic with GPT-4 integration and character prompt
- **setsuna_hotkey_mode.py**: Hotkey-triggered voice interaction mode (Ctrl+Shift+Alt)
- **setsuna_ui.py**: Tkinter UI for voice parameter adjustment with real-time hotkey functionality
- **voicevox_speaker.py**: VOICEVOX TTS integration with voice caching and parameter control
- **speech_input.py**: Google Speech Recognition wrapper for voice input
- **setsuna_memory_manager.py**: SQLite-based project memory system for conversation context
- **setsuna_prompt_memory_helper.py**: Memory injection system for GPT prompts

### Data Flow

1. Voice input via hotkey → Speech recognition → GPT-4 processing → VOICEVOX synthesis → Audio playback
2. Memory system tracks project context and injects it into GPT prompts
3. Voice parameters (speed, pitch, intonation) are adjustable via UI during runtime

## Development Setup

### Environment Activation
```bash
# Windows
D:
cd D:\setsuna_bot
call setsuna_env\Scripts\activate
```

### Dependencies
- OpenAI API key required in `.env` file
- VOICEVOX engine must be running on localhost:50021
- Python packages: openai, speech_recognition, pynput, tkinter, requests, simpleaudio

### Running the Application
```bash
# Main UI with hotkey mode
python setsuna_ui.py

# Hotkey mode only
python setsuna_hotkey_mode.py

# Windows batch launcher (auto-starts VOICEVOX)
run_hotkey_mode.bat
```

## Key Configuration

- **Character Prompt**: Detailed Japanese character personality in setsuna_bot.py:14-80
- **VOICEVOX Speaker ID**: Set to 20 in voicevox_speaker.py:9
- **Hotkey Combination**: Ctrl+Shift+Alt (left keys) in setsuna_hotkey_mode.py:9
- **Database**: SQLite file setsuna_memory.db for project tracking

## Architecture Notes

- Threading is used extensively for non-blocking audio processing
- Voice cache system prevents redundant TTS synthesis
- Memory system provides conversation continuity across sessions
- UI sliders update voice parameters in real-time without restart
- Error handling includes fallback messages for API failures
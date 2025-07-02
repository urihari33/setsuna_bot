# 音声認識ホットキー動作 - 修正履歴と対策メモ

## 問題の概要
修正のたびに「キーを押している間録音、離したら終了」の動作が壊れる問題が発生している。

## 根本原因
`voice_chat_gui.py`の`_voice_recognition()`メソッドで固定時間（15秒）の録音を使用していたため、キーリリース制御が効かなかった。

```python
# 問題のあった実装
audio = self.voice_recognizer.listen(source, timeout=15, phrase_time_limit=15)
```

## 修正履歴

### 修正1 (2025-07-03 - 失敗)
- `self.listening`フラグをチェックしながらチャンク録音
- **問題**: 音声が途切れる不具合が発生

### 修正2 (2025-07-03 - 最終版)
- **pyaudio直接使用**: speech_recognitionの制約を回避
- **リアルタイム録音**: キー押下中は連続録音、リリース時に即座停止
- **一時ファイル保存**: WAVファイルとして保存後にspeech_recognitionで認識

```python
# 最終実装（重要部分）
def record_audio():
    while self.listening and recording_active:
        data = stream.read(chunk, exception_on_overflow=False)
        frames.append(data)
```

## キーマッピング
- **通常モード**: `Ctrl+Shift+Alt` 同時押し
- **高速モード**: `Shift+Ctrl` 同時押し（Altなし）

## 重要なファイル・関数

### voice_chat_gui.py
- `_on_key_press()`: キー押下検出、録音開始
- `_on_key_release()`: キー離上検出、`self.listening = False`設定
- `_voice_recognition()`: 実際の録音処理（**このメソッドが重要**）
- `_handle_voice_input()`: 音声入力の全体制御

### 重要なフラグ
- `self.listening`: 録音状態フラグ
- `self.current_keys`: 現在押されているキーのセット

## 今後の修正時の注意点

### ⚠️ 絶対に避けるべき変更
1. **speech_recognitionのlisten()に依存しない**
   ```python
   # ❌ これをやると制御不能になる
   audio = recognizer.listen(source, timeout=固定値)
   ```

2. **`self.listening`フラグを無視しない**
   - 録音ループ内で必ず`self.listening`状態をチェック

3. **キーリリースハンドラを削除・変更しない**
   - `_on_key_release()`の`self.listening = False`は必須

4. **pyaudioリソース管理を怠らない**
   - ストリーム・pyaudioインスタンスの適切なクリーンアップが必要

### ✅ 修正時に確認すべきポイント（最終版）
1. `_voice_recognition()`がpyaudio直接使用している
2. `while self.listening and recording_active:`の二重チェック
3. バックグラウンドスレッドで録音実行
4. 一時ファイル作成→speech_recognitionで認識の流れ
5. pyaudioリソースの適切な解放

### 🔧 テスト手順
1. キーを押すと即座に録音開始
2. キーを離すと即座に録音停止
3. 短時間押下でも録音される
4. 長時間押下でも正常動作
5. 音声途切れが発生しない

### 📋 実装の核心部分
```python
# 重要: この部分を変更してはいけない
while self.listening and recording_active:
    data = stream.read(chunk, exception_on_overflow=False)
    frames.append(data)
```

## 関連する他の音声機能
- 音声合成（VoiceVox）: 独立システム、影響なし
- 音声テキスト変換: 独立システム、影響なし

## バックアップ用コード（修正版）

```python
def _voice_recognition(self):
    """音声認識実行（キー押下制御対応）"""
    # ... エラーチェック ...
    
    with self.microphone as source:
        audio_frames = []
        chunk_duration = 0.5
        
        while self.listening:  # 重要: この条件チェック
            try:
                chunk_audio = self.voice_recognizer.listen(
                    source, 
                    timeout=chunk_duration,  # 短時間
                    phrase_time_limit=chunk_duration
                )
                audio_frames.append(chunk_audio.frame_data)
            except sr.WaitTimeoutError:
                if not self.listening:
                    break
                continue
        
        # チャンク結合処理...
```

このメモを参考に、今後の修正で同じ問題を再発させないようにしてください。
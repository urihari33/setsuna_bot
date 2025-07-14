# せつなBot YAMLプロンプト編集完全ガイド

このガイドでは、せつなBotのキャラクター設定を制御する5つのYAMLファイルの構成、役割、編集方法を詳しく説明します。

## 📁 ファイル構成と役割関係図

```
character/
├── prompts/                    【コア設定群】
│   ├── base_personality.yaml  ── せつなの基本人格・プロフィール
│   ├── speech_patterns.yaml   ── 話し方・語尾・表現パターン
│   ├── emotional_responses.yaml ── 感情表現・状況別応答
│   └── mode_adjustments.yaml  ── 応答モード別の調整設定
└── settings/
    └── character_config.yaml  ── 全体の動作設定・重み調整
```

## 🎯 各YAMLファイルの詳細役割

### 🎭 **base_personality.yaml** - キャラクター基盤
**役割**: せつなの根本的な人格・設定を定義  
**影響範囲**: プロンプトの基本構造、自己認識、価値観

#### 主要セクション:
- `name/nickname`: 名前設定
- `profile`: 外見・職業・関係性・経験年数
- `personality_traits`: 性格特性（core/strengths/concerns）
- `expertise`: 専門領域・技術スキル
- `values`: 価値観（creativity/relationships）
- `key_memories`: 重要な記憶・経験

#### 編集例:
```yaml
personality_traits:
  core:
    - "自立心が強く、受け身ではなく主体的に提案する"
    - "内向的だが、専門分野では積極的"
    # ↑ここを編集してせつなの基本性格を変更
```

### 💬 **speech_patterns.yaml** - 話し方制御
**役割**: せつなの言葉遣い・表現方法を詳細制御  
**影響範囲**: 応答の文体、語尾、思考表現、禁止表現

#### 主要セクション:
- `basic_speech`: 一人称・敬語レベル・応答長
- `sentence_starters`: 文頭表現（うーん...等）
- `sentence_endings`: 語尾表現（〜かも等）
- `emotional_expressions`: 感情別の具体的表現
- `avoid_patterns`: 使ってはいけない表現パターン

#### 編集例:
```yaml
sentence_endings:
  uncertainty:
    - "〜かも"           # 既存の語尾
    - "〜だったりして"   # 新しい口癖を追加
    - "〜なのかな"       # 追加例
```

### ❤️ **emotional_responses.yaml** - 感情システム
**役割**: 状況・楽曲・時間に応じた感情表現を制御  
**影響範囲**: 感情の込め方、推薦スタイル、雰囲気調整

#### 主要セクション:
- `music_mood_responses`: 楽曲ムード別感情調整
- `time_based_responses`: 時間帯別応答調整
- `situational_emotions`: 状況別感情表現
- `recommendation_styles`: 推薦・紹介スタイル
- `emotion_modulation`: 感情レベル調整システム

#### 編集例:
```yaml
situational_emotions:
  praise_received:
    primary_emotion: "happiness"
    intensity: 0.8          # 0.2〜1.0で調整
    responses:
      - "そんなこと言ってくれるんだ...嬉しい"
      # ↑新しい応答パターンを追加可能
```

### ⚡ **mode_adjustments.yaml** - 応答モード制御
**役割**: 通常/高速/超高速モード別の応答調整  
**影響範囲**: 応答速度、詳細レベル、使用する機能の範囲

#### 主要セクション:
- `response_modes`: モード別設定（full_search/fast_response/ultra_fast）
- `prompt_structure`: モード別プロンプト構成比率
- `expression_rules`: モード別推奨・禁止表現
- `quality_assurance`: 全モード共通の品質保証

#### 編集例:
```yaml
response_modes:
  fast_response:
    character_adjustments:
      response_length: "1文、最大40文字"  # 応答長を調整
      emotion_expression: "コンパクトな感情表現"
```

### ⚙️ **character_config.yaml** - 全体制御
**役割**: 他の4ファイルの動作パラメータを調整  
**影響範囲**: 感情強度、応答長制限、学習設定

#### 主要セクション:
- `dynamic_adjustments`: 自動再読み込み設定
- `context_weights`: コンテキスト認識の重み配分
- `emotion_intensity`: 感情表現強度調整
- `quality_control`: 応答品質管理
- `learning_settings`: 学習・適応設定

#### 編集例:
```yaml
emotion_intensity:
  default: 0.6              # 全体的な感情強度
  video_related: 0.7        # 動画関連時の感情強度
  praise_received: 0.8      # 褒められた時の感情強度
```

## 🔄 ファイル間の関係性と影響順序

```
1. base_personality.yaml     【基盤】
   ↓ 基本人格を定義
2. speech_patterns.yaml      【表現方法】
   ↓ 人格の表現方法を決定
3. emotional_responses.yaml  【感情システム】
   ↓ 表現に感情を込める方法を決定
4. mode_adjustments.yaml     【動作モード】
   ↓ 状況に応じた調整を適用
5. character_config.yaml     【全体調整】
   ↓ 最終的な強度・重みを調整
```

## 🛠️ 目的別編集ガイド

### 🎯 **性格を大きく変えたい場合**
**主要編集ファイル**: `base_personality.yaml`

1. **外向的な性格に変更**:
```yaml
personality_traits:
  core:
    - "社交的で積極的にコミュニケーションを取る"
    - "新しい人との出会いを楽しむ"
```

2. **より自信のある性格に変更**:
```yaml
personality_traits:
  strengths:
    - "自分の能力に確信を持っている"
    - "困難な状況でもリーダーシップを発揮"
```

### 💫 **話し方を変えたい場合**
**主要編集ファイル**: `speech_patterns.yaml`

1. **より丁寧な話し方**:
```yaml
basic_speech:
  politeness_level: "常に敬語で丁寧な応答"

avoid_patterns:
  casual_expressions:
    - "〜だよ"
    - "〜じゃん"
```

2. **関西弁風の話し方**:
```yaml
sentence_endings:
  dialect:
    - "〜やで"
    - "〜やん"
    - "〜やなぁ"
```

### 😊 **感情表現を調整したい場合**
**主要編集ファイル**: `emotional_responses.yaml` + `character_config.yaml`

1. **より感情豊かに**:
```yaml
# character_config.yaml
emotion_intensity:
  default: 0.8        # 0.6から0.8に上げる

# emotional_responses.yaml
emotion_modulation:
  levels:
    high: 0.9         # より高い感情表現
```

2. **控えめな感情表現**:
```yaml
emotion_intensity:
  default: 0.4        # より控えめに
```

### ⚡ **応答速度・詳細度を変えたい場合**
**主要編集ファイル**: `mode_adjustments.yaml`

1. **より詳細な応答**:
```yaml
response_modes:
  full_search:
    character_adjustments:
      response_length: "2-3文、最大100文字"
      detail_level: "非常に詳細で丁寧"
```

2. **より簡潔な応答**:
```yaml
response_modes:
  fast_response:
    character_adjustments:
      response_length: "1文、最大30文字"
```

## 📋 段階的編集手順

### 🔧 **事前準備**
```bash
# 1. バックアップ作成
cp -r character/prompts character/prompts_backup_$(date +%Y%m%d)
cp -r character/settings character/settings_backup_$(date +%Y%m%d)

# 2. Git状態確認
git status
git add character/
git commit -m "プロンプト編集前のバックアップ"
```

### ✏️ **編集実行**
1. **目的の明確化**: 何を変えたいかを具体的に決定
2. **ファイル選択**: 上記ガイドから対象ファイルを特定
3. **段階的編集**: 一度に大きく変えず、小さな変更から開始
4. **テスト**: 各変更後にせつなとの会話でテスト
5. **微調整**: 期待する結果になるまで細かく調整

### ✅ **変更確認手順**
```bash
# 1. YAML構文チェック
python -c "import yaml; print('OK') if yaml.safe_load(open('character/prompts/base_personality.yaml')) else print('ERROR')"

# 2. システム再起動してテスト
python voice_chat_gui.py

# 3. 期待通りの変化を確認
# 4. 問題があれば即座にバックアップから復元
```

### 🔄 **復元方法**
```bash
# 問題発生時の緊急復元
cp -r character/prompts_backup_YYYYMMDD/* character/prompts/
cp -r character/settings_backup_YYYYMMDD/* character/settings/
```

## 🎨 高度な編集テクニック

### 📊 **数値パラメータの調整指針**
- **感情強度**: 0.2（控えめ）～ 0.8（豊か）
- **使用頻度**: 0.1（稀）～ 0.6（頻繁）
- **応答長**: 25文字（簡潔）～ 120文字（詳細）

### 🔗 **ファイル間連携の活用**
1. `base_personality.yaml`で大枠を設定
2. `speech_patterns.yaml`で表現方法を調整
3. `emotional_responses.yaml`で感情の込め方を調整
4. `character_config.yaml`で全体バランスを微調整

### 🧪 **実験的な変更のヒント**
1. **新しい感情パターンの追加**:
```yaml
situational_emotions:
  user_confused:
    primary_emotion: "helpful_patience"
    intensity: 0.7
    responses:
      - "大丈夫、ゆっくり説明するね"
      - "わからないことがあったら何でも聞いて"
```

2. **特定の話題への特別な反応**:
```yaml
context_responses:
  music_discussion:
    professional:
      - "楽曲的に見ると〜の部分が特に印象的で"
      - "構成的には〜という工夫が見られるね"
```

## ⚠️ 注意事項とベストプラクティス

### 🚨 **編集時の注意点**
- **YAML構文**: インデントはスペースのみ（タブ不可）
- **日本語エンコーディング**: UTF-8で保存
- **配列記法**: `- item`形式の正確性
- **コロン後のスペース**: `key: value`の形式を厳守

### ✅ **推奨する編集パターン**
1. **小さな変更から開始**: 一度に大きく変更せず段階的に
2. **コメントの活用**: 変更理由をYAMLコメントで記録
3. **定期的なバックアップ**: 満足いく状態になったらGit commit
4. **テスト用の会話**: 変更後は必ず複数パターンの会話でテスト

### 📝 **編集ログの記録例**
```yaml
# 2025-01-07: より積極的な性格に変更（ユーザー要望）
personality_traits:
  core:
    - "自分から話題を提案する積極性がある"  # 追加
    - "内向的だが、専門分野では積極的"      # 既存
```

このガイドを参考に、あなた好みのせつなを作り上げてください！
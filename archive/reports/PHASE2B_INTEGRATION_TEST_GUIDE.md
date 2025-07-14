# 🧪 Phase 2B 統合テストガイド
**動画-画像コンテキスト統合機能の完全動作確認**

## 📋 テスト対象機能

### ✅ Phase 2B 実装済み機能
- **VideoImageContextBuilder**: 動画+画像の統合コンテキスト構築
- **6次元関連性分析**: 時間的・視覚的・テーマ的・空間的・音楽的・感情的
- **会話テンプレートシステム**: 5種類のインテリジェント会話生成
- **クエリ意図分析**: ユーザー質問の自動意図判定
- **物語構造分析**: 画像から映像ストーリー構築

## 🎯 統合テストシナリオ

### **前提条件**
```bash
# Windows環境で実行
cd D:\setsuna_bot
python -c "import sys; print('Python:', sys.version)"
python -c "from core.video_image_context import VideoImageContextBuilder; print('✅ Phase 2B ready')"
```

---

## **テスト1: 基本統合動作確認**

### **1.1 YouTubeKnowledgeManager統合テスト**
```bash
python -c "
from core.youtube_knowledge_manager import YouTubeKnowledgeManager
from core.video_image_context import VideoImageContextBuilder

# マネージャー初期化
yt_manager = YouTubeKnowledgeManager()
context_builder = VideoImageContextBuilder(yt_manager)

print('✅ 統合初期化成功')
print(f'ImageAnalyzer統合: {yt_manager.image_analyzer is not None}')
print(f'テンプレート数: {len(context_builder.conversation_templates)}')
"
```

**期待結果:**
```
✅ 統合初期化成功
ImageAnalyzer統合: True
テンプレート数: 5
```

### **1.2 データベース連携テスト**
```bash
python -c "
from core.youtube_knowledge_manager import YouTubeKnowledgeManager
import json

yt_manager = YouTubeKnowledgeManager()
db_path = yt_manager.knowledge_db_path
print(f'データベースパス: {db_path}')
print(f'データベース存在: {db_path.exists()}')

if db_path.exists():
    with open(db_path, 'r', encoding='utf-8') as f:
        db = json.load(f)
    video_count = len(db.get('videos', {}))
    print(f'登録動画数: {video_count}')
else:
    print('⚠️ データベースファイルが見つかりません')
"
```

---

## **テスト2: 実際の動画データでのコンテキスト生成**

### **2.1 登録済み動画の確認**
```bash
python -c "
from core.youtube_knowledge_manager import YouTubeKnowledgeManager
import json

yt_manager = YouTubeKnowledgeManager()
if yt_manager.knowledge_db_path.exists():
    with open(yt_manager.knowledge_db_path, 'r', encoding='utf-8') as f:
        db = json.load(f)
    
    videos = db.get('videos', {})
    print('登録済み動画一覧:')
    for video_id, video_data in list(videos.items())[:3]:  # 最初の3つ
        title = video_data.get('title', '不明')
        images = video_data.get('images', [])
        print(f'  - {video_id}: {title} (画像: {len(images)}枚)')
        
        if len(images) >= 2:  # 2枚以上画像がある動画があればテスト対象として表示
            print(f'    → テスト対象候補: {video_id}')
            break
else:
    print('データベースが見つかりません')
"
```

### **2.2 コンテキスト生成テスト（実データ）**
**上記で見つかったvideo_idを使用してテスト:**

```bash
python -c "
from core.youtube_knowledge_manager import YouTubeKnowledgeManager
from core.video_image_context import VideoImageContextBuilder

# video_idを実際の値に置き換えてください
TEST_VIDEO_ID = 'YOUR_VIDEO_ID_HERE'  # ← ここを変更

yt_manager = YouTubeKnowledgeManager()
context_builder = VideoImageContextBuilder(yt_manager)

print(f'テスト対象動画: {TEST_VIDEO_ID}')

# 包括的コンテキスト構築
result = context_builder.build_comprehensive_context(TEST_VIDEO_ID)

if 'error' not in result:
    print('✅ 包括的コンテキスト構築成功')
    print(f'  動画タイトル: {result[\"video_info\"][\"title\"]}')
    print(f'  分析画像数: {result[\"images_analysis\"][\"analyzed_images\"]}')
    print(f'  視覚テーマ数: {len(result[\"images_analysis\"][\"visual_themes\"])}')
    print(f'  会話トピック数: {len(result[\"conversation_topics\"])}')
    
    # ストーリー構築確認
    narrative = result.get('visual_narrative', {})
    print(f'  ストーリーフロー: {narrative.get(\"story_flow\", \"不明\")}')
    print(f'  視覚的進行: {narrative.get(\"visual_progression\", \"不明\")}')
else:
    print(f'❌ エラー: {result[\"error\"]}')
"
```

---

## **テスト3: 高度な関連性分析**

### **3.1 6次元関連性分析テスト**
```bash
python -c "
from core.youtube_knowledge_manager import YouTubeKnowledgeManager
from core.video_image_context import VideoImageContextBuilder

TEST_VIDEO_ID = 'YOUR_VIDEO_ID_HERE'  # ← 実際のvideo_idに変更

yt_manager = YouTubeKnowledgeManager()
context_builder = VideoImageContextBuilder(yt_manager)

print(f'高度な関連性分析テスト: {TEST_VIDEO_ID}')

# 高度な関連性分析実行
analysis = context_builder.analyze_advanced_image_relationships(TEST_VIDEO_ID)

if 'error' not in analysis:
    print('✅ 高度な関連性分析成功')
    print(f'  総画像数: {analysis[\"total_images\"]}')
    print(f'  全体一貫性スコア: {analysis[\"overall_coherence_score\"]:.3f}')
    print(f'  物語構造: {analysis[\"narrative_structure\"]}')
    
    # 感情フロー
    emotional_flow = analysis.get('emotional_flow', {})
    emotions = emotional_flow.get('emotion_sequence', [])
    if emotions:
        print(f'  感情の流れ: {\" → \".join([e[\"emotion\"] for e in emotions])}')
    
    # 関連性マトリックス
    matrix = analysis.get('relationship_matrix', {})
    if matrix:
        relationships = matrix.get('relationships', [])
        strong_rels = [r for r in relationships if r['relationship_strength'] == 'strong']
        moderate_rels = [r for r in relationships if r['relationship_strength'] == 'moderate']
        print(f'  強い関連性: {len(strong_rels)}ペア')
        print(f'  中程度関連性: {len(moderate_rels)}ペア')
        
        # 詳細表示（最初の関連性）
        if relationships:
            rel = relationships[0]
            print(f'  関連性例: {rel[\"overall_score\"]:.2f} ({rel[\"relationship_strength\"]})')
    
    # 重要転換点
    transitions = analysis.get('key_transitions', [])
    print(f'  重要転換点: {len(transitions)}箇所')
    
else:
    print(f'❌ エラー: {analysis[\"error\"]}')
"
```

---

## **テスト4: 会話コンテキスト生成**

### **4.1 各テンプレートでの生成テスト**
```bash
python -c "
from core.youtube_knowledge_manager import YouTubeKnowledgeManager
from core.video_image_context import VideoImageContextBuilder

TEST_VIDEO_ID = 'YOUR_VIDEO_ID_HERE'  # ← 実際のvideo_idに変更

yt_manager = YouTubeKnowledgeManager()
context_builder = VideoImageContextBuilder(yt_manager)

# テストケース
test_cases = [
    ('一般議論', None, 'general_video_discussion'),
    ('画像フォーカス', 'この画像について詳しく教えて', 'specific_image_focus'),
    ('映像分析', '演出の技法について', 'visual_analysis'),
    ('音楽動画包括', '楽曲の魅力について', 'music_video_comprehensive')
]

print(f'会話コンテキスト生成テスト: {TEST_VIDEO_ID}')
print('=' * 50)

for name, query, template_type in test_cases:
    print(f'\\n🧪 {name}テスト')
    
    context = context_builder.create_conversation_context(
        video_id=TEST_VIDEO_ID,
        query=query,
        template_type=template_type
    )
    
    if '申し訳ありません' not in context:
        print(f'✅ 生成成功 ({len(context)}文字)')
        print(f'📄 内容: {context[:150]}...')
    else:
        print(f'❌ 生成失敗: {context[:100]}...')
"
```

### **4.2 クエリ意図分析テスト**
```bash
python -c "
from core.video_image_context import VideoImageContextBuilder

context_builder = VideoImageContextBuilder()

test_queries = [
    'この画像はどんな内容ですか？',
    '映像の演出が素晴らしいですね',
    'アーティストの表現力について',
    '雰囲気がとても良い動画ですね',
    '楽曲の魅力を教えてください'
]

print('クエリ意図分析テスト:')
for query in test_queries:
    intent = context_builder._analyze_query_intent(query)
    template_type = context_builder._select_template_by_intent(intent)
    print(f'  \"{query}\" → {intent} → {template_type}')
"
```

---

## **テスト5: エラーハンドリング**

### **5.1 存在しない動画IDテスト**
```bash
python -c "
from core.youtube_knowledge_manager import YouTubeKnowledgeManager
from core.video_image_context import VideoImageContextBuilder

yt_manager = YouTubeKnowledgeManager()
context_builder = VideoImageContextBuilder(yt_manager)

# 存在しない動画ID
result = context_builder.build_comprehensive_context('nonexistent_video_123')
print('存在しない動画IDテスト:')
if 'error' in result:
    print(f'✅ 適切なエラーハンドリング: {result[\"error\"]}')
else:
    print('❌ エラーハンドリング不備')
"
```

### **5.2 画像なし動画テスト**
```bash
python -c "
from core.youtube_knowledge_manager import YouTubeKnowledgeManager
from core.video_image_context import VideoImageContextBuilder
import json

yt_manager = YouTubeKnowledgeManager()
context_builder = VideoImageContextBuilder(yt_manager)

# 画像数が少ない動画を探す
if yt_manager.knowledge_db_path.exists():
    with open(yt_manager.knowledge_db_path, 'r', encoding='utf-8') as f:
        db = json.load(f)
    
    videos = db.get('videos', {})
    for video_id, video_data in videos.items():
        images = video_data.get('images', [])
        if len(images) == 0:
            print(f'画像なし動画テスト: {video_id}')
            result = context_builder.build_comprehensive_context(video_id)
            
            if 'images_analysis' in result:
                analyzed = result['images_analysis']['analyzed_images']
                print(f'  分析画像数: {analyzed} (期待: 0)')
                if analyzed == 0:
                    print('✅ 画像なしケース適切処理')
                else:
                    print('❌ 画像なしケース処理不備')
            break
    else:
        print('画像なし動画が見つかりませんでした')
"
```

---

## **テスト6: パフォーマンス確認**

### **6.1 処理時間測定**
```bash
python -c "
import time
from core.youtube_knowledge_manager import YouTubeKnowledgeManager
from core.video_image_context import VideoImageContextBuilder

TEST_VIDEO_ID = 'YOUR_VIDEO_ID_HERE'  # ← 実際のvideo_idに変更

yt_manager = YouTubeKnowledgeManager()
context_builder = VideoImageContextBuilder(yt_manager)

print('パフォーマンステスト:')

# 包括的コンテキスト構築
start_time = time.time()
result = context_builder.build_comprehensive_context(TEST_VIDEO_ID)
context_time = time.time() - start_time

# 高度な関連性分析
start_time = time.time()
analysis = context_builder.analyze_advanced_image_relationships(TEST_VIDEO_ID)
analysis_time = time.time() - start_time

# 会話コンテキスト生成
start_time = time.time()
conversation = context_builder.create_conversation_context(TEST_VIDEO_ID, '楽曲について教えて')
conversation_time = time.time() - start_time

print(f'  包括的コンテキスト構築: {context_time:.2f}秒')
print(f'  高度な関連性分析: {analysis_time:.2f}秒')
print(f'  会話コンテキスト生成: {conversation_time:.2f}秒')
print(f'  総合計時間: {context_time + analysis_time + conversation_time:.2f}秒')

# パフォーマンス評価
total_time = context_time + analysis_time + conversation_time
if total_time < 5.0:
    print('✅ パフォーマンス良好 (<5秒)')
elif total_time < 10.0:
    print('⚠️ パフォーマンス普通 (5-10秒)')
else:
    print('❌ パフォーマンス要改善 (>10秒)')
"
```

---

## 📊 **テスト結果チェックリスト**

### **基本機能**
- [ ] VideoImageContextBuilder初期化成功
- [ ] YouTubeKnowledgeManager統合成功
- [ ] データベース連携正常
- [ ] テンプレート読み込み完了（5種類）

### **コア機能**
- [ ] 包括的コンテキスト構築成功
- [ ] 6次元関連性分析成功
- [ ] 会話コンテキスト生成成功（4パターン）
- [ ] クエリ意図分析精度確認

### **高度な機能**
- [ ] 物語構造分析動作
- [ ] 感情フロー分析動作
- [ ] 関連性マトリックス生成
- [ ] 重要転換点検出動作

### **エラーハンドリング**
- [ ] 存在しない動画ID適切処理
- [ ] 画像なし動画適切処理
- [ ] 分析失敗時のフォールバック動作

### **パフォーマンス**
- [ ] 処理時間許容範囲内（<10秒）
- [ ] メモリ使用量適正
- [ ] エラーなく連続実行可能

---

## 🚨 **トラブルシューティング**

### **想定されるエラーと対処法**

#### **1. ImportError**
```
ImportError: No module named 'core.video_image_context'
```
**対処**: `sys.path.append()` でパス追加、または正しいディレクトリから実行

#### **2. データベースアクセスエラー**
```
FileNotFoundError: unified_knowledge_db.json
```
**対処**: データベースファイルの存在確認、パス設定確認

#### **3. 分析結果なしエラー**
```
分析画像数: 0
```
**対処**: 対象動画に画像が追加されているか確認、ImageAnalyzer動作確認

#### **4. メモリ不足**
```
MemoryError during relationship analysis
```
**対処**: 大量画像がある動画は避ける、PC再起動

---

## 💬 **フィードバック項目**

テスト完了後、以下について報告してください：

### **1. 成功した機能**
- どの機能が期待通りに動作したか
- 特に印象的だった分析結果

### **2. 問題が発生した機能**
- エラー内容とその状況
- 再現手順

### **3. パフォーマンス評価**
- 処理速度の体感
- 分析精度の印象

### **4. 実用性評価**
- 生成される会話コンテキストの自然さ
- 関連性分析の有用性

### **5. 改善提案**
- あったら便利な機能
- UI/UX改善案

---

## 🎯 **最終確認ポイント**

✅ **Phase 2B完全統合テスト成功基準:**
1. 全テストケースでエラーなし実行
2. 実際の動画データで関連性分析成功
3. 自然な会話コンテキスト生成
4. 処理時間10秒以内
5. 意図分析精度80%以上

**統合テスト完了後、Phase 2B完全実装完了となります！**

---

**テスト用の実際のvideo_idは、データベース確認テスト（テスト2.1）で見つかったものを使用してください。** 🚀
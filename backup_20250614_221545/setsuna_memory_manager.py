import sqlite3
from datetime import datetime, timedelta
import json
import re
from setsuna_logger import log_memory_operation, log_error

DB_PATH = "setsuna_memory.db"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            status TEXT NOT NULL CHECK (status IN ('進行中', '完了', '中止')),
            last_updated TEXT NOT NULL,
            notes TEXT
        )
        """)
        
        # 会話テーマ記憶テーブル
        c.execute("""
        CREATE TABLE IF NOT EXISTS conversation_topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            context TEXT,
            importance INTEGER DEFAULT 1,
            last_mentioned TEXT NOT NULL,
            mention_count INTEGER DEFAULT 1,
            UNIQUE(topic)
        )
        """)
        
        conn.commit()

def add_project(title, notes=""):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        now = datetime.now().isoformat()
        c.execute("INSERT INTO projects (title, status, last_updated, notes) VALUES (?, '進行中', ?, ?)",
                  (title, now, notes))
        conn.commit()

def update_project_status(title, new_status):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        now = datetime.now().isoformat()
        c.execute("UPDATE projects SET status = ?, last_updated = ? WHERE title = ?",
                  (new_status, now, title))
        conn.commit()

def get_project_summary():
    init_db()  # ← これを追加（重要）
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute("SELECT title, status, notes FROM projects ORDER BY last_updated DESC")
        projects = c.fetchall()
        lines = []
        for title, status, notes in projects:
            note_part = f"（{notes}）" if notes else ""
            lines.append(f"- 『{title}』：{status}{note_part}")
        return "\n".join(lines)

def add_conversation_topic(topic, context="", importance=1):
    """会話のトピックと文脈を記憶"""
    init_db()
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            now = datetime.now().isoformat()
            
            # 既存トピックがあるかチェック
            c.execute("SELECT mention_count FROM conversation_topics WHERE topic = ?", (topic,))
            existing = c.fetchone()
            
            if existing:
                # 既存トピックの更新
                new_count = existing[0] + 1
                c.execute("""
                UPDATE conversation_topics 
                SET context = ?, importance = ?, last_mentioned = ?, mention_count = ?
                WHERE topic = ?
                """, (context, importance, now, new_count, topic))
                log_memory_operation("UPDATE_TOPIC", f"'{topic}' updated (count: {new_count})")
            else:
                # 新規トピック追加
                c.execute("""
                INSERT INTO conversation_topics (topic, context, importance, last_mentioned, mention_count)
                VALUES (?, ?, ?, ?, 1)
                """, (topic, context, importance, now))
                log_memory_operation("ADD_TOPIC", f"New topic added: '{topic}' (importance: {importance})")
            
            conn.commit()
    except Exception as e:
        log_error("memory_manager", f"Failed to add topic '{topic}'", e)

def get_weighted_context(days=7, limit=5):
    """重要度加重による動的文脈選択"""
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        
        # 重要度スコアリング
        c.execute("""
        SELECT topic, context, last_mentioned, mention_count, importance,
               julianday('now') - julianday(last_mentioned) as days_ago
        FROM conversation_topics 
        WHERE last_mentioned > ?
        """, (cutoff,))
        
        topics = c.fetchall()
        if not topics:
            return ""
        
        # スコア計算（重み付け）
        scored_topics = []
        for topic, context, date, count, importance, days_ago in topics:
            recent_weight = 0.4  # 最近性の重み
            frequency_weight = 0.3  # 頻度の重み
            importance_weight = 0.3  # 重要度の重み
            
            # 正規化スコア計算
            recency_score = max(0, 1 - (days_ago / 7))  # 7日で線形減衰
            frequency_score = min(1, count / 5)  # 5回で最大
            importance_score = importance / 5  # 1-5の重要度
            
            total_score = (
                recent_weight * recency_score +
                frequency_weight * frequency_score +
                importance_weight * importance_score
            )
            
            scored_topics.append((topic, context, count, total_score))
        
        # スコア順にソートして上位を選択
        scored_topics.sort(key=lambda x: x[3], reverse=True)
        selected_topics = scored_topics[:limit]
        
        # フォーマット
        topic_lines = []
        for topic, context, count, score in selected_topics:
            context_part = f"（{context}）" if context else ""
            count_part = f"[{count}回]" if count > 1 else ""
            topic_lines.append(f"- 『{topic}』{context_part}{count_part}")
        
        return "\n".join(topic_lines)

def get_recent_conversation_topics(days=7, limit=5):
    """旧関数（互換性維持）"""
    return get_weighted_context(days, limit)

def extract_topics_from_text(text):
    """テキストから話題を抽出（改良版）"""
    # 基本キーワード
    keywords = [
        "プログラミング", "音声", "調整", "作業", "配信", "歌", "映像", "制作",
        "開発", "環境", "トラブル", "新しい", "プロジェクト", "締切"
    ]
    
    found_topics = []
    
    # 基本キーワードの抽出
    for keyword in keywords:
        if keyword in text:
            found_topics.append(keyword)
    
    # 固有名詞の抽出（カタカナ、英数字の組み合わせ）
    proper_nouns = re.findall(r'[ァ-ヴー]{3,}|[A-Za-z][A-Za-z0-9]{2,}', text)
    for noun in proper_nouns:
        # 長すぎるものや短すぎるものは除外
        if 3 <= len(noun) <= 20:
            found_topics.append(noun)
    
    # 「〜の話」「〜について」などの表現から名詞を抽出
    topic_patterns = [
        r'([ァ-ヴーa-zA-Z0-9]{2,})の話',
        r'([ァ-ヴーa-zA-Z0-9]{2,})について',
        r'([ァ-ヴーa-zA-Z0-9]{2,})って知ってる',
        r'([ァ-ヴーa-zA-Z0-9]{2,})を見た',
        r'([ァ-ヴーa-zA-Z0-9]{2,})が好き'
    ]
    
    for pattern in topic_patterns:
        matches = re.findall(pattern, text)
        found_topics.extend(matches)
    
    # 重複除去
    return list(set(found_topics))

def auto_add_topics_from_conversation():
    """会話履歴から自動でトピックを抽出して追加"""
    try:
        with open("chat_history.json", "r", encoding="utf-8") as f:
            messages = json.load(f)
        
        # 最新の数件のユーザーメッセージを分析
        recent_user_messages = [
            msg["content"] for msg in messages[-10:] 
            if msg["role"] == "user"
        ]
        
        total_topics = 0
        for message in recent_user_messages:
            topics = extract_topics_from_text(message)
            for topic in topics:
                add_conversation_topic(topic, f"最近の会話より: {message[:50]}...")
                total_topics += 1
        
        if total_topics > 0:
            log_memory_operation("AUTO_EXTRACT", f"Extracted {total_topics} topics from recent messages")
                
    except FileNotFoundError:
        log_memory_operation("AUTO_EXTRACT", "chat_history.json not found, skipping auto extraction")
    except Exception as e:
        log_error("memory_manager", "Failed to auto-extract topics", e)

def compress_conversation_history(messages, max_length=20):
    """会話履歴を要約・圧縮"""
    if len(messages) <= max_length:
        return messages
    
    # システムプロンプトは保持
    system_messages = [msg for msg in messages if msg["role"] == "system"]
    conversation_messages = [msg for msg in messages if msg["role"] != "system"]
    
    if len(conversation_messages) <= max_length:
        return messages
    
    # 最新の会話は保持
    recent_messages = conversation_messages[-10:]
    old_messages = conversation_messages[:-10]
    
    # 古い会話を要約
    if old_messages:
        # ユーザーとアシスタントのメッセージを組み合わせて要約
        conversation_pairs = []
        for i in range(0, len(old_messages), 2):
            if i + 1 < len(old_messages):
                user_msg = old_messages[i].get("content", "")
                assistant_msg = old_messages[i + 1].get("content", "")
                conversation_pairs.append(f"ユーザー: {user_msg[:50]}... / せつな: {assistant_msg[:50]}...")
        
        # 要約を作成
        summary_content = "【過去の会話要約】\n" + "\n".join(conversation_pairs[-5:])  # 最新5組のみ
        summary_message = {"role": "system", "content": summary_content}
        
        # 圧縮された履歴を構築
        compressed = system_messages + [summary_message] + recent_messages
        
        log_memory_operation("COMPRESS_HISTORY", f"Compressed {len(old_messages)} old messages into summary")
        return compressed
    
    return messages

def optimize_memory_usage():
    """メモリ使用量の最適化"""
    try:
        # 古いトピックをクリーンアップ（30日以上前）
        cutoff = (datetime.now() - timedelta(days=30)).isoformat()
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute("DELETE FROM conversation_topics WHERE last_mentioned < ? AND mention_count < 2", (cutoff,))
            deleted_count = c.rowcount
            conn.commit()
        
        if deleted_count > 0:
            log_memory_operation("CLEANUP", f"Removed {deleted_count} old topics")
        
        # 会話履歴も最適化
        try:
            with open("chat_history.json", "r", encoding="utf-8") as f:
                messages = json.load(f)
            
            if len(messages) > 30:
                compressed_messages = compress_conversation_history(messages, 25)
                with open("chat_history.json", "w", encoding="utf-8") as f:
                    json.dump(compressed_messages, f, ensure_ascii=False, indent=2)
                log_memory_operation("OPTIMIZE", f"Compressed chat history from {len(messages)} to {len(compressed_messages)} messages")
        
        except FileNotFoundError:
            pass
            
    except Exception as e:
        log_error("memory_manager", "Failed to optimize memory", e)

# 起動時にDBを初期化
if __name__ == "__main__":
    init_db()
    print("初期化完了。以下はプロジェクト概要：")
    print(get_project_summary())
    print("\n最近の会話トピック：")
    print(get_recent_conversation_topics())
    print("\nメモリ最適化実行中...")
    optimize_memory_usage()
    print("最適化完了。")

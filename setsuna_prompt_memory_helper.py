from setsuna_memory_manager import get_project_summary, get_weighted_context, auto_add_topics_from_conversation, optimize_memory_usage

def inject_memory_prompt(base_prompt):
    """
    setsuna_memory_manager.py から取得した記憶情報を
    GPTプロンプトの先頭に追加する。
    """
    # 定期的なメモリ最適化（10回に1回実行）
    import random
    if random.randint(1, 10) == 1:
        optimize_memory_usage()
    
    # 会話履歴から自動でトピック抽出
    auto_add_topics_from_conversation()
    
    # プロジェクト記憶
    project_memory = get_project_summary()
    
    # 重要度加重による最適化された文脈取得
    recent_topics = get_weighted_context(days=7, limit=5)
    
    memory_section = f"【プロジェクト共有履歴】\n{project_memory}\n\n"
    
    if recent_topics:
        memory_section += f"【最近話したトピック】\n{recent_topics}\n\n"
    
    return memory_section + base_prompt

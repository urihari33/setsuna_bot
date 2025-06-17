#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
創作プロジェクト管理システム
せつなとの共同創作をサポート
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class ProjectSystem:
    """創作プロジェクト管理システム"""
    
    def __init__(self):
        self.projects_file = "character/setsuna_projects.json"
        
        # プロジェクトデータ構造
        self.project_data = {
            "active_projects": [],     # 進行中プロジェクト
            "idea_stock": [],          # アイデアストック
            "completed_projects": [],  # 完了プロジェクト
            "project_counter": 0       # プロジェクトID用カウンター
        }
        
        self._load_project_data()
        print("📽️ 創作プロジェクト管理システム初期化完了")
    
    def _load_project_data(self):
        """プロジェクトデータを読み込み"""
        os.makedirs("character", exist_ok=True)
        
        if os.path.exists(self.projects_file):
            try:
                with open(self.projects_file, 'r', encoding='utf-8') as f:
                    self.project_data.update(json.load(f))
                print(f"✅ プロジェクトデータ読み込み: 進行中{len(self.project_data['active_projects'])}件")
            except Exception as e:
                print(f"⚠️ プロジェクトデータ読み込みエラー: {e}")
    
    def create_project(self, title: str, description: str, deadline: str = None, 
                      project_type: str = "動画") -> Dict:
        """新しいプロジェクトを作成"""
        try:
            self.project_data["project_counter"] += 1
            project_id = f"proj_{self.project_data['project_counter']:03d}"
            
            project = {
                "id": project_id,
                "title": title,
                "description": description,
                "type": project_type,
                "status": "計画中",
                "progress": 0,
                "created_date": datetime.now().isoformat(),
                "deadline": deadline,
                "last_updated": datetime.now().isoformat(),
                "next_steps": [],
                "notes": [],
                "milestones": []
            }
            
            self.project_data["active_projects"].append(project)
            self.save_project_data()
            
            print(f"🆕 新プロジェクト作成: {title}")
            return project
            
        except Exception as e:
            print(f"❌ プロジェクト作成エラー: {e}")
            return {}
    
    def add_idea(self, content: str, category: str = "動画", source: str = "雑談") -> bool:
        """アイデアをストックに追加"""
        try:
            idea = {
                "id": f"idea_{len(self.project_data['idea_stock']) + 1:03d}",
                "content": content,
                "category": category,
                "source": source,
                "created_date": datetime.now().isoformat(),
                "priority": "普通",
                "used": False
            }
            
            self.project_data["idea_stock"].append(idea)
            self.save_project_data()
            
            print(f"💡 アイデア追加: {content[:30]}...")
            return True
            
        except Exception as e:
            print(f"❌ アイデア追加エラー: {e}")
            return False
    
    def update_project_progress(self, project_id: str, progress: int, 
                              status: str = None, next_step: str = None) -> bool:
        """プロジェクト進捗を更新"""
        try:
            for project in self.project_data["active_projects"]:
                if project["id"] == project_id:
                    project["progress"] = progress
                    project["last_updated"] = datetime.now().isoformat()
                    
                    if status:
                        project["status"] = status
                    
                    if next_step:
                        project["next_steps"] = [next_step]
                    
                    self.save_project_data()
                    print(f"📈 進捗更新: {project['title']} -> {progress}%")
                    return True
            
            print(f"⚠️ プロジェクトが見つかりません: {project_id}")
            return False
            
        except Exception as e:
            print(f"❌ 進捗更新エラー: {e}")
            return False
    
    def complete_project(self, project_id: str, outcome: str = "", lessons: str = "") -> bool:
        """プロジェクトを完了"""
        try:
            for i, project in enumerate(self.project_data["active_projects"]):
                if project["id"] == project_id:
                    # 完了情報を追加
                    project["status"] = "完了"
                    project["progress"] = 100
                    project["completed_date"] = datetime.now().isoformat()
                    project["outcome"] = outcome
                    project["lessons"] = lessons
                    
                    # 進行中から完了済みに移動
                    completed_project = self.project_data["active_projects"].pop(i)
                    self.project_data["completed_projects"].append(completed_project)
                    
                    self.save_project_data()
                    print(f"✅ プロジェクト完了: {project['title']}")
                    return True
            
            print(f"⚠️ プロジェクトが見つかりません: {project_id}")
            return False
            
        except Exception as e:
            print(f"❌ プロジェクト完了エラー: {e}")
            return False
    
    def get_active_projects(self) -> List[Dict]:
        """進行中プロジェクト一覧を取得"""
        return self.project_data.get("active_projects", [])
    
    def get_idea_stock(self) -> List[Dict]:
        """アイデアストック一覧を取得"""
        return self.project_data.get("idea_stock", [])
    
    def get_completed_projects(self) -> List[Dict]:
        """完了プロジェクト一覧を取得"""
        return self.project_data.get("completed_projects", [])
    
    def get_project_by_id(self, project_id: str) -> Optional[Dict]:
        """IDでプロジェクトを取得"""
        for project in self.project_data["active_projects"]:
            if project["id"] == project_id:
                return project
        return None
    
    def delete_project(self, project_id: str) -> bool:
        """プロジェクトを削除"""
        try:
            for i, project in enumerate(self.project_data["active_projects"]):
                if project["id"] == project_id:
                    deleted_project = self.project_data["active_projects"].pop(i)
                    self.save_project_data()
                    print(f"🗑️ プロジェクト削除: {deleted_project['title']}")
                    return True
            
            print(f"⚠️ プロジェクトが見つかりません: {project_id}")
            return False
            
        except Exception as e:
            print(f"❌ プロジェクト削除エラー: {e}")
            return False
    
    def delete_idea(self, idea_id: str) -> bool:
        """アイデアを削除"""
        try:
            for i, idea in enumerate(self.project_data["idea_stock"]):
                if idea["id"] == idea_id:
                    deleted_idea = self.project_data["idea_stock"].pop(i)
                    self.save_project_data()
                    print(f"🗑️ アイデア削除: {deleted_idea['content'][:30]}...")
                    return True
            
            print(f"⚠️ アイデアが見つかりません: {idea_id}")
            return False
            
        except Exception as e:
            print(f"❌ アイデア削除エラー: {e}")
            return False
    
    def get_project_context(self) -> str:
        """プロジェクト情報をプロンプト用コンテキストとして生成"""
        context_parts = []
        
        # 進行中プロジェクト
        active_projects = self.get_active_projects()
        if active_projects:
            context_parts.append("【進行中のプロジェクト】")
            for project in active_projects[-3:]:  # 最新3件
                next_step = project.get('next_steps', ['未設定'])[0] if project.get('next_steps') else '未設定'
                context_parts.append(
                    f"・{project['title']} ({project['type']}) - 進捗{project['progress']}% - 次:{next_step}"
                )
        
        # 最近のアイデア
        recent_ideas = self.get_idea_stock()
        if recent_ideas:
            context_parts.append("\n【最近のアイデア】")
            for idea in recent_ideas[-3:]:  # 最新3件
                context_parts.append(f"・{idea['content'][:50]}... ({idea['category']})")
        
        # 最近の完了プロジェクト
        completed = self.get_completed_projects()
        if completed:
            context_parts.append("\n【最近完了したプロジェクト】")
            for project in completed[-2:]:  # 最新2件
                context_parts.append(f"・{project['title']} - {project.get('outcome', '成果記録なし')}")
        
        return "\n".join(context_parts)
    
    def analyze_conversation_for_projects(self, user_input: str, setsuna_response: str):
        """会話内容を分析してプロジェクト関連情報を抽出"""
        try:
            user_lower = user_input.lower()
            
            # アイデア検出キーワード
            idea_keywords = ["動画", "歌", "楽曲", "撮影", "企画", "作ろう", "作りたい", "面白い", "ネタ"]
            
            # プロジェクト進捗キーワード
            progress_keywords = ["進捗", "どう", "進んで", "完成", "できた", "終わった"]
            
            # アイデア候補検出
            for keyword in idea_keywords:
                if keyword in user_input:
                    # 簡単なアイデア候補として記録（手動で正式登録）
                    print(f"💡 アイデア候補検出: {user_input[:50]}...")
                    break
            
            # 進捗関連の発言検出
            for keyword in progress_keywords:
                if keyword in user_input:
                    print(f"📈 プロジェクト進捗関連の会話を検出")
                    break
                    
        except Exception as e:
            print(f"❌ 会話分析エラー: {e}")
    
    def save_project_data(self):
        """プロジェクトデータをファイルに保存"""
        try:
            with open(self.projects_file, 'w', encoding='utf-8') as f:
                json.dump(self.project_data, f, ensure_ascii=False, indent=2)
            print("💾 プロジェクトデータ保存完了")
        except Exception as e:
            print(f"❌ プロジェクトデータ保存エラー: {e}")
    
    def get_project_stats(self) -> Dict:
        """プロジェクト統計情報を取得"""
        return {
            "active_projects": len(self.project_data["active_projects"]),
            "idea_stock": len(self.project_data["idea_stock"]),
            "completed_projects": len(self.project_data["completed_projects"]),
            "total_projects": self.project_data["project_counter"]
        }

# テスト用
if __name__ == "__main__":
    print("=" * 50)
    print("🧪 創作プロジェクト管理システムテスト")
    print("=" * 50)
    
    project_sys = ProjectSystem()
    
    # テストプロジェクト作成
    print("\n📽️ プロジェクト作成テスト:")
    project1 = project_sys.create_project(
        "春の歌動画制作",
        "桜をテーマにした楽曲とMVの制作",
        "2025-02-15",
        "動画"
    )
    
    project2 = project_sys.create_project(
        "キャラクターデザイン企画",
        "オリジナルキャラクターの設定とデザイン",
        "2025-01-30",
        "イラスト"
    )
    
    # アイデア追加テスト
    print("\n💡 アイデア追加テスト:")
    project_sys.add_idea("猫カフェでの日常風景動画", "動画", "雑談")
    project_sys.add_idea("レトロゲーム風BGM制作", "音楽", "ブレスト")
    
    # 進捗更新テスト
    print("\n📈 進捗更新テスト:")
    if project1:
        project_sys.update_project_progress(
            project1["id"], 
            30, 
            "制作中", 
            "メロディライン決定"
        )
    
    # プロジェクトコンテキスト表示
    print("\n🎯 プロジェクトコンテキスト:")
    context = project_sys.get_project_context()
    print(context)
    
    # 統計表示
    print("\n📊 プロジェクト統計:")
    stats = project_sys.get_project_stats()
    for key, value in stats.items():
        print(f"   - {key}: {value}")
    
    print("\n✅ テスト完了")
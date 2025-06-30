"""
統一データストレージシステム

拡張性とパフォーマンスを両立した統合データ管理
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from core.data_models import (
    KnowledgeDatabase, Video, Playlist, 
    create_empty_database, migrate_legacy_data
)
from config.settings import DATA_DIR


class UnifiedStorage:
    """統一データストレージ管理クラス"""
    
    def __init__(self, data_dir: Path = None):
        self.data_dir = data_dir or DATA_DIR
        self.db_file = self.data_dir / "unified_knowledge_db.json"
        self.backup_dir = self.data_dir / "backups"
        self.legacy_dir = self.data_dir / "legacy"
        
        # ディレクトリ作成
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.legacy_dir.mkdir(parents=True, exist_ok=True)
        
        self._database: Optional[KnowledgeDatabase] = None
    
    def load_database(self) -> KnowledgeDatabase:
        """データベースを読み込み"""
        if self._database is None:
            if self.db_file.exists():
                try:
                    with open(self.db_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    self._database = KnowledgeDatabase.from_dict(data)
                    print(f"統合データベースを読み込みました: {self._database.total_videos}動画, {self._database.total_playlists}プレイリスト")
                except Exception as e:
                    print(f"データベース読み込みエラー: {e}")
                    print("新しいデータベースを作成します")
                    self._database = create_empty_database()
            else:
                # 既存データがあるか確認
                legacy_files = self._find_legacy_files()
                if legacy_files:
                    print("既存データを新しい形式に移行します...")
                    self._database = self._migrate_legacy_data(legacy_files)
                    self.save_database()
                else:
                    self._database = create_empty_database()
        
        return self._database
    
    def save_database(self, create_backup: bool = True) -> None:
        """データベースを保存"""
        if self._database is None:
            return
        
        # バックアップ作成
        if create_backup and self.db_file.exists():
            backup_file = self.backup_dir / f"unified_knowledge_db_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            shutil.copy2(self.db_file, backup_file)
            print(f"バックアップを作成しました: {backup_file}")
        
        # データベース保存
        try:
            self._database.last_updated = datetime.now()
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(self._database.to_dict(), f, ensure_ascii=False, indent=2)
            print(f"統合データベースを保存しました: {self.db_file}")
        except Exception as e:
            print(f"データベース保存エラー: {e}")
            raise
    
    def add_video(self, video: Video) -> None:
        """動画を追加"""
        db = self.load_database()
        db.add_video(video)
        self._database = db
    
    def add_playlist(self, playlist: Playlist) -> None:
        """プレイリストを追加"""
        db = self.load_database()
        db.add_playlist(playlist)
        self._database = db
    
    def remove_video_completely(self, video_id: str) -> tuple[bool, str]:
        """動画を完全削除（すべてのプレイリストからも除外）
        
        Args:
            video_id: 削除する動画のID
            
        Returns:
            (成功フラグ, メッセージ)
        """
        try:
            print(f"\n🗑️ 動画完全削除開始: {video_id}")
            
            db = self.load_database()
            
            # 動画の存在確認
            if video_id not in db.videos:
                error_msg = f"動画が見つかりません: {video_id}"
                print(f"   ❌ {error_msg}")
                return False, error_msg
            
            video = db.videos[video_id]
            video_title = video.metadata.title
            
            print(f"   📺 削除対象: {video_title}")
            
            # 動画が属するプレイリストから除外
            removed_from_playlists = []
            for playlist_id in video.playlists:
                if playlist_id in db.playlists:
                    playlist = db.playlists[playlist_id]
                    if video_id in playlist.video_ids:
                        playlist.video_ids.remove(video_id)
                        playlist.total_videos = len(playlist.video_ids)
                        playlist.updated_at = datetime.now()
                        removed_from_playlists.append(playlist_id)
                        print(f"   📋 プレイリストから除外: {playlist.metadata.title}")
            
            # 動画をデータベースから削除
            del db.videos[video_id]
            
            # データベース統計更新
            db.total_videos = len(db.videos)
            db.updated_at = datetime.now()
            
            # データベース保存
            self._database = db
            
            print(f"   ✅ 動画削除完了: {video_title}")
            print(f"   📊 除外プレイリスト数: {len(removed_from_playlists)}")
            
            success_msg = f"動画を削除しました: {video_title}"
            return True, success_msg
            
        except Exception as e:
            error_msg = f"動画削除エラー: {e}"
            print(f"   ❌ {error_msg}")
            import traceback
            traceback.print_exc()
            return False, error_msg
    
    def get_video(self, video_id: str) -> Optional[Video]:
        """動画を取得"""
        db = self.load_database()
        return db.videos.get(video_id)
    
    def get_playlist(self, playlist_id: str) -> Optional[Playlist]:
        """プレイリストを取得"""
        db = self.load_database()
        return db.playlists.get(playlist_id)
    
    def get_videos_by_playlist(self, playlist_id: str) -> List[Video]:
        """プレイリストの動画を順序付きで取得"""
        db = self.load_database()
        playlist = db.playlists.get(playlist_id)
        if not playlist:
            return []
        
        videos = []
        for video_id in playlist.video_ids:
            if video_id in db.videos:
                videos.append(db.videos[video_id])
        
        return videos
    
    def search_videos_by_creator(self, creator_name: str) -> List[Video]:
        """クリエイター名で動画検索"""
        db = self.load_database()
        return db.get_videos_by_creator(creator_name)
    
    def search_videos_by_tag(self, tag: str) -> List[Video]:
        """タグで動画検索"""
        db = self.load_database()
        return db.get_videos_by_tag(tag)
    
    def search_videos_by_theme(self, theme: str) -> List[Video]:
        """テーマで動画検索"""
        db = self.load_database()
        return db.get_videos_by_theme(theme)
    
    def get_all_creators(self) -> List[str]:
        """全クリエイター名を取得"""
        db = self.load_database()
        return list(db.creator_index.keys())
    
    def get_all_tags(self) -> List[str]:
        """全タグを取得"""
        db = self.load_database()
        return list(db.tag_index.keys())
    
    def get_all_themes(self) -> List[str]:
        """全テーマを取得"""
        db = self.load_database()
        return list(db.theme_index.keys())
    
    def get_all_videos(self) -> Dict[str, Video]:
        """全動画を取得"""
        db = self.load_database()
        return db.videos
    
    def get_failed_videos_for_retry(self, max_retry_count: int = 3) -> List[Video]:
        """再試行可能な失敗動画を取得"""
        db = self.load_database()
        from core.data_models import AnalysisStatus
        
        failed_videos = []
        for video in db.videos.values():
            if (video.analysis_status == AnalysisStatus.FAILED and 
                video.retry_count < max_retry_count):
                failed_videos.append(video)
        
        print(f"🔄 再試行可能な失敗動画: {len(failed_videos)}件 (最大再試行回数: {max_retry_count})")
        return failed_videos
    
    def update_video_analysis(self, video_id: str, analysis_status: str, 
                            creative_insight: Optional[str] = None, 
                            analysis_error: Optional[str] = None) -> bool:
        """動画の分析状況を更新"""
        try:
            db = self.load_database()
            if video_id in db.videos:
                video = db.videos[video_id]
                
                # 分析状況を更新
                from core.data_models import AnalysisStatus
                new_status = AnalysisStatus(analysis_status)
                
                # 分析失敗時の再試行カウント更新
                if new_status == AnalysisStatus.FAILED and video.analysis_status != AnalysisStatus.FAILED:
                    video.retry_count += 1
                    video.last_analysis_error = analysis_error
                    print(f"   📊 動画 {video.metadata.title}: 再試行回数 {video.retry_count}")
                
                video.analysis_status = new_status
                
                # 分析結果を更新
                if creative_insight:
                    from core.data_models import CreativeInsight
                    video.creative_insight = CreativeInsight(
                        creators=[],
                        music_info=None,
                        tools_used=[],
                        themes=[],
                        visual_elements=[],
                        analysis_confidence=0.8,
                        analysis_timestamp=datetime.now(),
                        analysis_model="GPT-4",
                        insights=creative_insight
                    )
                
                if analysis_error:
                    video.analysis_error = analysis_error
                
                # 更新日時を設定
                video.updated_at = datetime.now()
                
                # データベースを保存
                self.save_database()
                return True
            return False
        except Exception as e:
            print(f"動画分析更新エラー: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """統計情報を取得"""
        db = self.load_database()
        
        analyzed_videos = sum(1 for v in db.videos.values() if v.creative_insight is not None)
        analysis_success_rate = analyzed_videos / len(db.videos) if db.videos else 0
        
        playlist_stats = {}
        for pid, playlist in db.playlists.items():
            playlist_videos = [db.videos[vid] for vid in playlist.video_ids if vid in db.videos]
            analyzed_in_playlist = sum(1 for v in playlist_videos if v.creative_insight is not None)
            
            playlist_stats[pid] = {
                'title': playlist.metadata.title,
                'total_videos': len(playlist_videos),
                'analyzed_videos': analyzed_in_playlist,
                'analysis_rate': analyzed_in_playlist / len(playlist_videos) if playlist_videos else 0,
                'last_sync': playlist.last_full_sync.isoformat()
            }
        
        return {
            'total_videos': db.total_videos,
            'total_playlists': db.total_playlists,
            'analyzed_videos': analyzed_videos,
            'analysis_success_rate': analysis_success_rate,
            'total_creators': len(db.creator_index),
            'total_tags': len(db.tag_index),
            'total_themes': len(db.theme_index),
            'last_updated': db.last_updated.isoformat(),
            'playlists': playlist_stats,
            'database_version': db.database_version
        }
    
    def cleanup_old_backups(self, keep_days: int = 30) -> None:
        """古いバックアップファイルを削除"""
        cutoff_time = datetime.now().timestamp() - (keep_days * 24 * 60 * 60)
        
        for backup_file in self.backup_dir.glob("unified_knowledge_db_*.json"):
            if backup_file.stat().st_mtime < cutoff_time:
                backup_file.unlink()
                print(f"古いバックアップを削除しました: {backup_file}")
    
    def export_for_setsuna(self, output_file: Path = None) -> Path:
        """せつなさん用のデータエクスポート"""
        if output_file is None:
            output_file = self.data_dir / "setsuna_export.json"
        
        db = self.load_database()
        
        # せつなさん向けに最適化したデータ構造
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'total_videos': db.total_videos,
            'creators': {
                name: {
                    'video_count': len(video_ids),
                    'roles': self._get_creator_roles(name, db),
                    'recent_videos': [
                        {
                            'title': db.videos[vid].metadata.title,
                            'published_at': db.videos[vid].metadata.published_at.isoformat()
                        }
                        for vid in video_ids[:5] if vid in db.videos
                    ]
                }
                for name, video_ids in db.creator_index.items()
            },
            'popular_themes': {
                theme: len(video_ids)
                for theme, video_ids in sorted(db.theme_index.items(), key=lambda x: len(x[1]), reverse=True)[:20]
            },
            'music_insights': self._extract_music_insights(db)
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        print(f"せつなさん用データをエクスポートしました: {output_file}")
        return output_file
    
    def _find_legacy_files(self) -> Dict[str, Path]:
        """既存データファイルを探索"""
        legacy_files = {}
        
        # プレイリストファイル
        playlist_files = list(self.data_dir.glob("playlists/playlist_*.json"))
        if playlist_files:
            legacy_files['playlists'] = playlist_files
        
        # 分析結果ファイル
        analysis_files = list(self.data_dir.glob("analyzed_*.json"))
        if analysis_files:
            legacy_files['analysis'] = analysis_files
        
        return legacy_files
    
    def _migrate_legacy_data(self, legacy_files: Dict[str, Any]) -> KnowledgeDatabase:
        """既存データを移行"""
        db = create_empty_database()
        
        # プレイリストファイルを処理
        if 'playlists' in legacy_files:
            for playlist_file in legacy_files['playlists']:
                try:
                    print(f"プレイリストファイルを移行中: {playlist_file}")
                    playlist_db = migrate_legacy_data(str(playlist_file), "")
                    
                    # データを統合
                    for video_id, video in playlist_db.videos.items():
                        db.add_video(video)
                    
                    for playlist_id, playlist in playlist_db.playlists.items():
                        db.add_playlist(playlist)
                    
                    # レガシーファイルを移動
                    legacy_target = self.legacy_dir / playlist_file.name
                    shutil.move(str(playlist_file), str(legacy_target))
                    print(f"レガシーファイルを移動しました: {legacy_target}")
                    
                except Exception as e:
                    print(f"プレイリストファイル移行エラー {playlist_file}: {e}")
        
        # 分析結果を統合
        if 'analysis' in legacy_files:
            for analysis_file in legacy_files['analysis']:
                try:
                    print(f"分析結果ファイルを統合中: {analysis_file}")
                    self._integrate_analysis_data(analysis_file, db)
                    
                    # レガシーファイルを移動
                    legacy_target = self.legacy_dir / analysis_file.name
                    shutil.move(str(analysis_file), str(legacy_target))
                    print(f"レガシー分析ファイルを移動しました: {legacy_target}")
                    
                except Exception as e:
                    print(f"分析結果統合エラー {analysis_file}: {e}")
        
        return db
    
    def _get_creator_roles(self, creator_name: str, db: KnowledgeDatabase) -> List[str]:
        """クリエイターの役割一覧を取得"""
        roles = set()
        
        for video_id in db.creator_index.get(creator_name, []):
            video = db.videos.get(video_id)
            if video and video.creative_insight:
                for creator in video.creative_insight.creators:
                    if creator.name == creator_name:
                        roles.add(creator.role)
        
        return list(roles)
    
    def _extract_music_insights(self, db: KnowledgeDatabase) -> Dict[str, Any]:
        """音楽関連の洞察を抽出"""
        total_with_lyrics = 0
        popular_genres = {}
        
        for video in db.videos.values():
            if video.creative_insight and video.creative_insight.music_info:
                music_info = video.creative_insight.music_info
                if music_info.lyrics:
                    total_with_lyrics += 1
                if music_info.genre:
                    popular_genres[music_info.genre] = popular_genres.get(music_info.genre, 0) + 1
        
        return {
            'videos_with_lyrics': total_with_lyrics,
            'popular_genres': dict(sorted(popular_genres.items(), key=lambda x: x[1], reverse=True)[:10])
        }
    
    def _integrate_analysis_data(self, analysis_file: Path, db: KnowledgeDatabase) -> None:
        """分析結果ファイルをデータベースに統合"""
        try:
            with open(analysis_file, 'r', encoding='utf-8') as f:
                analysis_data = json.load(f)
            
            print(f"   📊 分析データ統合開始: {len(analysis_data)}件")
            
            integrated_count = 0
            for video_id, analysis_result in analysis_data.items():
                if video_id in db.videos:
                    video = db.videos[video_id]
                    
                    # 既存の分析結果を更新・強化
                    if self._enhance_video_analysis(video, analysis_result):
                        integrated_count += 1
                else:
                    print(f"   ⚠️  動画が見つかりません: {video_id}")
            
            print(f"   ✅ 分析データ統合完了: {integrated_count}件")
            
        except Exception as e:
            print(f"   ❌ 分析データ統合エラー: {e}")
            raise
    
    def _enhance_video_analysis(self, video: Video, analysis_result: Dict[str, Any]) -> bool:
        """動画の分析結果を強化"""
        try:
            from core.data_models import CreativeInsight, CreatorInfo, MusicInfo
            
            # 既存の分析結果を取得
            current_insight = video.creative_insight
            
            # 新しい分析結果から情報を抽出
            enhanced_creators = self._extract_creators_from_analysis(analysis_result)
            enhanced_themes = self._extract_themes_from_analysis(analysis_result)
            enhanced_music = self._extract_music_from_analysis(analysis_result)
            
            # 既存データと統合
            if current_insight:
                # 既存のクリエイター情報と統合
                existing_creators = {c.name: c for c in current_insight.creators}
                for new_creator in enhanced_creators:
                    if new_creator.name not in existing_creators:
                        existing_creators[new_creator.name] = new_creator
                    else:
                        # 信頼度の高い方を採用
                        if new_creator.confidence > existing_creators[new_creator.name].confidence:
                            existing_creators[new_creator.name] = new_creator
                
                # テーマ情報を統合
                existing_themes = set(current_insight.themes)
                existing_themes.update(enhanced_themes)
                
                # 音楽情報を統合
                music_info = current_insight.music_info or enhanced_music
                
                # 統合結果で更新
                video.creative_insight = CreativeInsight(
                    creators=list(existing_creators.values()),
                    music_info=music_info,
                    tools_used=current_insight.tools_used,
                    themes=list(existing_themes),
                    visual_elements=current_insight.visual_elements,
                    analysis_confidence=max(current_insight.analysis_confidence, 0.8),
                    analysis_timestamp=datetime.now(),
                    analysis_model=current_insight.analysis_model,
                    insights=current_insight.insights
                )
            else:
                # 新規分析結果を作成
                video.creative_insight = CreativeInsight(
                    creators=enhanced_creators,
                    music_info=enhanced_music,
                    tools_used=[],
                    themes=enhanced_themes,
                    visual_elements=[],
                    analysis_confidence=0.8,
                    analysis_timestamp=datetime.now(),
                    analysis_model="GPT-4",
                    insights=analysis_result.get('insights', '')
                )
            
            # 分析ステータスを更新
            from core.data_models import AnalysisStatus
            video.analysis_status = AnalysisStatus.COMPLETED
            video.updated_at = datetime.now()
            
            return True
            
        except Exception as e:
            print(f"   ❌ 動画分析強化エラー {video.metadata.id}: {e}")
            return False
    
    def _extract_creators_from_analysis(self, analysis_result: Dict[str, Any]) -> List:
        """分析結果からクリエイター情報を抽出"""
        from core.data_models import CreatorInfo
        
        creators = []
        
        # 様々な形式の分析結果に対応
        if 'creators' in analysis_result:
            for creator_data in analysis_result['creators']:
                if isinstance(creator_data, dict):
                    creators.append(CreatorInfo(
                        name=creator_data.get('name', ''),
                        role=creator_data.get('role', 'unknown'),
                        confidence=creator_data.get('confidence', 0.7)
                    ))
                elif isinstance(creator_data, str):
                    creators.append(CreatorInfo(
                        name=creator_data,
                        role='unknown',
                        confidence=0.6
                    ))
        
        # 説明文からクリエイター情報を抽出
        if 'analysis_text' in analysis_result:
            extracted_creators = self._parse_creators_from_text(analysis_result['analysis_text'])
            creators.extend(extracted_creators)
        
        return creators
    
    def _extract_themes_from_analysis(self, analysis_result: Dict[str, Any]) -> List[str]:
        """分析結果からテーマ情報を抽出"""
        themes = []
        
        # 直接指定されたテーマ
        if 'themes' in analysis_result:
            themes.extend(analysis_result['themes'])
        
        # 分析テキストからテーマを抽出
        if 'analysis_text' in analysis_result:
            extracted_themes = self._parse_themes_from_text(analysis_result['analysis_text'])
            themes.extend(extracted_themes)
        
        # ジャンルからテーマを推定
        if 'genre' in analysis_result:
            themes.append(analysis_result['genre'])
        
        return list(set(themes))  # 重複除去
    
    def _extract_music_from_analysis(self, analysis_result: Dict[str, Any]) -> Optional:
        """分析結果から音楽情報を抽出"""
        from core.data_models import MusicInfo
        
        if 'music_info' in analysis_result:
            music_data = analysis_result['music_info']
            return MusicInfo(
                lyrics=music_data.get('lyrics', ''),
                genre=music_data.get('genre'),
                bpm=music_data.get('bpm'),
                key=music_data.get('key'),
                mood=music_data.get('mood')
            )
        
        # 基本的な音楽情報を抽出
        lyrics = analysis_result.get('lyrics', '')
        genre = analysis_result.get('genre')
        
        if lyrics or genre:
            return MusicInfo(
                lyrics=lyrics,
                genre=genre
            )
        
        return None
    
    def _parse_creators_from_text(self, text: str) -> List:
        """テキストからクリエイター情報を解析"""
        from core.data_models import CreatorInfo
        import re
        
        creators = []
        
        # 一般的なクリエイター表記パターン
        patterns = [
            r'作詞[：:](.*?)(?:\\n|$)',
            r'作曲[：:](.*?)(?:\\n|$)',
            r'編曲[：:](.*?)(?:\\n|$)',
            r'歌[：:](.*?)(?:\\n|$)',
            r'ボーカル[：:](.*?)(?:\\n|$)',
            r'イラスト[：:](.*?)(?:\\n|$)',
            r'動画[：:](.*?)(?:\\n|$)',
        ]
        
        role_mapping = {
            '作詞': 'lyricist',
            '作曲': 'composer', 
            '編曲': 'arranger',
            '歌': 'vocal',
            'ボーカル': 'vocal',
            'イラスト': 'illustrator',
            '動画': 'movie'
        }
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                names = [name.strip() for name in match.split(',') if name.strip()]
                role = None
                for jp_role, en_role in role_mapping.items():
                    if jp_role in pattern:
                        role = en_role
                        break
                
                for name in names:
                    if name and len(name) > 1:  # 短すぎる名前は除外
                        creators.append(CreatorInfo(
                            name=name,
                            role=role or 'unknown',
                            confidence=0.8
                        ))
        
        return creators
    
    def _parse_themes_from_text(self, text: str) -> List[str]:
        """テキストからテーマを解析"""
        themes = []
        
        # 音楽ジャンル関連キーワード
        genre_keywords = ['ポップ', 'ロック', 'バラード', 'エレクトロ', 'ダンス', 'フォーク', 'ジャズ', 'クラシック']
        
        # 感情・ムード関連キーワード
        mood_keywords = ['切ない', '元気', '楽しい', '悲しい', '希望', '恋愛', '青春', '成長']
        
        # テーマ関連キーワード
        theme_keywords = ['友情', '恋愛', '別れ', '出会い', '成長', '冒険', '日常', '夢']
        
        text_lower = text.lower()
        
        for keyword in genre_keywords + mood_keywords + theme_keywords:
            if keyword in text:
                themes.append(keyword)
        
        return themes
    
    def enhance_existing_analysis(self) -> Dict[str, int]:
        """既存の分析データを強化"""
        print("\\n🔧 既存分析データの強化を開始します...")
        
        db = self.load_database()
        
        enhanced_count = 0
        theme_added_count = 0
        creator_enhanced_count = 0
        
        for video_id, video in db.videos.items():
            if video.creative_insight:
                original_enhanced = enhanced_count
                
                # テーマ情報が不足している動画の強化
                if not video.creative_insight.themes:
                    enhanced_themes = self._analyze_video_for_themes(video)
                    if enhanced_themes:
                        video.creative_insight.themes = enhanced_themes
                        theme_added_count += 1
                        enhanced_count += 1
                
                # クリエイター情報の強化
                if len(video.creative_insight.creators) < 2:
                    additional_creators = self._analyze_video_for_creators(video)
                    if additional_creators:
                        existing_names = {c.name for c in video.creative_insight.creators}
                        new_creators = [c for c in additional_creators if c.name not in existing_names]
                        if new_creators:
                            video.creative_insight.creators.extend(new_creators)
                            creator_enhanced_count += 1
                            enhanced_count += 1
                
                # 更新日時を設定
                if enhanced_count > original_enhanced:
                    video.updated_at = datetime.now()
        
        # データベースを保存
        if enhanced_count > 0:
            self.save_database()
        
        results = {
            'total_enhanced': enhanced_count,
            'themes_added': theme_added_count,
            'creators_enhanced': creator_enhanced_count
        }
        
        print(f"✅ 分析データ強化完了:")
        print(f"   強化された動画: {enhanced_count}件")
        print(f"   テーマ追加: {theme_added_count}件")
        print(f"   クリエイター強化: {creator_enhanced_count}件")
        
        return results
    
    def _analyze_video_for_themes(self, video: Video) -> List[str]:
        """動画からテーマを分析"""
        themes = []
        
        # タイトルと説明文からテーマを抽出
        text_content = f"{video.metadata.title} {video.metadata.description}"
        
        themes.extend(self._parse_themes_from_text(text_content))
        
        # タグからテーマを推定
        tag_themes = self._infer_themes_from_tags(video.metadata.tags)
        themes.extend(tag_themes)
        
        return list(set(themes))[:5]  # 最大5つのテーマ
    
    def _analyze_video_for_creators(self, video: Video) -> List:
        """動画から追加のクリエイター情報を分析"""
        creators = []
        
        # 説明文からクリエイター情報を抽出
        creators.extend(self._parse_creators_from_text(video.metadata.description))
        
        # チャンネル名をクリエイターとして追加
        if video.metadata.channel_title and video.metadata.channel_title != 'urihari 33':
            from core.data_models import CreatorInfo
            creators.append(CreatorInfo(
                name=video.metadata.channel_title,
                role='channel',
                confidence=0.9
            ))
        
        return creators[:3]  # 最大3つの追加クリエイター
    
    def _infer_themes_from_tags(self, tags: List[str]) -> List[str]:
        """タグからテーマを推定"""
        theme_mapping = {
            'ボカロ': '音楽',
            'VOCALOID': '音楽',
            'ボーカロイド': '音楽',
            'MV': '音楽',
            'Music Video': '音楽',
            'アニメ': 'アニメ',
            'ゲーム': 'ゲーム',
            'ゲーム配信': 'ゲーム',
            'にじさんじ': 'VTuber',
            'VTuber': 'VTuber',
            'バーチャルYouTuber': 'VTuber'
        }
        
        themes = []
        for tag in tags:
            if tag in theme_mapping:
                themes.append(theme_mapping[tag])
        
        return list(set(themes))


# シングルトンインスタンス
_storage_instance = None

def get_storage() -> UnifiedStorage:
    """ストレージインスタンスを取得"""
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = UnifiedStorage()
    return _storage_instance
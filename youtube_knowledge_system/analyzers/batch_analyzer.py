"""
バッチ分析システム

大量の未分析動画を効率的にGPT-4で分析する
"""

import sys
import time
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from storage.unified_storage import UnifiedStorage
from core.data_models import Video, AnalysisStatus, CreativeInsight, CreatorInfo, MusicInfo
from analyzers.description_analyzer import DescriptionAnalyzer


class BatchAnalyzer:
    """バッチ分析メインクラス"""
    
    def __init__(self, batch_size: int = 5, delay_seconds: float = 2.0):
        """
        初期化
        
        Args:
            batch_size: 一度に処理する動画数
            delay_seconds: API呼び出し間の待機時間
        """
        self.storage = UnifiedStorage()
        self.analyzer = DescriptionAnalyzer()
        self.batch_size = batch_size
        self.delay_seconds = delay_seconds
        
        # 統計情報
        self.stats = {
            'total_videos': 0,
            'processed_videos': 0,
            'successful_analyses': 0,
            'failed_analyses': 0,
            'start_time': None,
            'current_batch': 0
        }
    
    def find_unanalyzed_videos(self) -> List[Video]:
        """未分析動画を取得"""
        print("=== 未分析動画の検索 ===")
        
        db = self.storage.load_database()
        
        unanalyzed_videos = []
        for video_id, video in db.videos.items():
            if video.analysis_status == AnalysisStatus.PENDING:
                unanalyzed_videos.append(video)
        
        print(f"未分析動画数: {len(unanalyzed_videos)}件")
        print(f"総動画数: {len(db.videos)}件")
        
        # 公開日順でソート（新しい順）
        unanalyzed_videos.sort(key=lambda v: v.metadata.published_at, reverse=True)
        
        return unanalyzed_videos
    
    def analyze_video_batch(self, videos: List[Video]) -> Dict[str, Any]:
        """動画バッチの分析"""
        batch_results = {
            'successful': [],
            'failed': [],
            'batch_start_time': datetime.now()
        }
        
        print(f"\\n--- バッチ {self.stats['current_batch']} 開始 ({len(videos)}件) ---")
        
        for i, video in enumerate(videos, 1):
            print(f"  [{i}/{len(videos)}] {video.metadata.id}: {video.metadata.title[:50]}...")
            
            try:
                # 分析実行
                analysis_result = self.analyzer.analyze_description(
                    description=video.metadata.description,
                    video_title=video.metadata.title
                )
                
                if analysis_result:
                    # 分析成功
                    creative_insight = self._convert_to_creative_insight(
                        analysis_result, video.metadata.id
                    )
                    
                    # 動画オブジェクトを更新
                    video.creative_insight = creative_insight
                    video.analysis_status = AnalysisStatus.COMPLETED
                    video.updated_at = datetime.now()
                    
                    # データベースに保存
                    self.storage.add_video(video)
                    
                    batch_results['successful'].append({
                        'video_id': video.metadata.id,
                        'title': video.metadata.title,
                        'creators_found': len(creative_insight.creators) if creative_insight else 0,
                        'has_lyrics': bool(creative_insight.music_info and creative_insight.music_info.lyrics) if creative_insight else False
                    })
                    
                    print(f"    ✅ 分析成功 (信頼度: {creative_insight.analysis_confidence:.2f})")
                    self.stats['successful_analyses'] += 1
                    
                else:
                    # 分析失敗
                    self._handle_analysis_failure(video, "分析結果が無効")
                    batch_results['failed'].append({
                        'video_id': video.metadata.id,
                        'title': video.metadata.title,
                        'error': '分析結果が無効'
                    })
                    print(f"    ❌ 分析失敗: 分析結果が無効")
                
            except Exception as e:
                # エラー処理
                error_msg = str(e)
                self._handle_analysis_failure(video, error_msg)
                batch_results['failed'].append({
                    'video_id': video.metadata.id,
                    'title': video.metadata.title,
                    'error': error_msg
                })
                print(f"    ❌ 分析エラー: {error_msg}")
            
            self.stats['processed_videos'] += 1
            
            # API制限を考慮した待機
            if i < len(videos):
                print(f"    ⏱️ {self.delay_seconds}秒待機...")
                time.sleep(self.delay_seconds)
        
        # バッチ完了
        batch_duration = (datetime.now() - batch_results['batch_start_time']).total_seconds()
        print(f"--- バッチ {self.stats['current_batch']} 完了 ({batch_duration:.1f}秒) ---")
        print(f"  成功: {len(batch_results['successful'])}件")
        print(f"  失敗: {len(batch_results['failed'])}件")
        
        return batch_results
    
    def _convert_to_creative_insight(self, analysis_result: Dict[str, Any], video_id: str) -> CreativeInsight:
        """分析結果をCreativeInsightに変換"""
        
        # クリエイター情報の変換
        creators = []
        creators_data = analysis_result.get('creators', {})
        
        if isinstance(creators_data, dict):
            for role, name in creators_data.items():
                if name and name != "null":
                    creators.append(CreatorInfo(
                        name=str(name),
                        role=role,
                        confidence=analysis_result.get('confidence_score', 0.8)
                    ))
        
        # 音楽情報の変換
        music_info = None
        if analysis_result.get('lyrics') or analysis_result.get('music_info'):
            music_info = MusicInfo(
                lyrics=analysis_result.get('lyrics', ''),
                genre=analysis_result.get('music_info', {}).get('genre'),
                bpm=None,  # 現在は未対応
                key=None,  # 現在は未対応
                mood=analysis_result.get('music_info', {}).get('mood')
            )
        
        # ツール情報の取得
        tools_used = []
        tools_data = analysis_result.get('tools', {})
        if isinstance(tools_data, dict):
            for tool_type, tool_list in tools_data.items():
                if isinstance(tool_list, list):
                    tools_used.extend(tool_list)
                elif tool_list:
                    tools_used.append(str(tool_list))
        
        # テーマ情報（音楽ジャンルやムードから推定）
        themes = []
        if music_info:
            if music_info.genre:
                themes.append(music_info.genre)
            if music_info.mood:
                themes.append(music_info.mood)
        
        return CreativeInsight(
            creators=creators,
            music_info=music_info,
            tools_used=tools_used,
            themes=themes,
            visual_elements=[],  # 将来拡張用
            analysis_confidence=analysis_result.get('confidence_score', 0.8),
            analysis_timestamp=datetime.now(),
            analysis_model="gpt-4o-mini"
        )
    
    def _handle_analysis_failure(self, video: Video, error_message: str):
        """分析失敗の処理"""
        video.analysis_status = AnalysisStatus.FAILED
        video.analysis_error = error_message
        video.updated_at = datetime.now()
        
        # データベースに保存
        self.storage.add_video(video)
        self.stats['failed_analyses'] += 1
    
    def run_batch_analysis(self, max_videos: Optional[int] = None, auto_save_interval: int = 5) -> Dict[str, Any]:
        """バッチ分析の実行"""
        print("🔄 バッチ分析開始")
        print(f"開始時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        self.stats['start_time'] = datetime.now()
        
        # 未分析動画を取得
        unanalyzed_videos = self.find_unanalyzed_videos()
        
        if not unanalyzed_videos:
            print("✅ 未分析動画がありません")
            return self.stats
        
        # 処理対象を制限
        if max_videos:
            unanalyzed_videos = unanalyzed_videos[:max_videos]
            print(f"処理制限: 最大{max_videos}件")
        
        self.stats['total_videos'] = len(unanalyzed_videos)
        
        print(f"処理対象: {len(unanalyzed_videos)}件")
        print(f"バッチサイズ: {self.batch_size}件")
        print(f"推定完了時間: {(len(unanalyzed_videos) / self.batch_size * (self.batch_size * self.delay_seconds + 10) / 60):.1f}分")
        
        # バッチ処理実行
        all_results = []
        
        for i in range(0, len(unanalyzed_videos), self.batch_size):
            self.stats['current_batch'] += 1
            batch_videos = unanalyzed_videos[i:i + self.batch_size]
            
            # バッチ分析実行
            batch_result = self.analyze_video_batch(batch_videos)
            all_results.append(batch_result)
            
            # 定期保存
            if self.stats['current_batch'] % auto_save_interval == 0:
                print(f"\\n💾 中間保存実行...")
                self.storage.save_database()
                print(f"   データベース保存完了")
            
            # 進捗表示
            progress = (self.stats['processed_videos'] / self.stats['total_videos']) * 100
            elapsed = (datetime.now() - self.stats['start_time']).total_seconds()
            estimated_total = elapsed / progress * 100 if progress > 0 else 0
            remaining = estimated_total - elapsed
            
            print(f"\\n📊 進捗: {progress:.1f}% ({self.stats['processed_videos']}/{self.stats['total_videos']})")
            print(f"   成功: {self.stats['successful_analyses']}件")
            print(f"   失敗: {self.stats['failed_analyses']}件")
            print(f"   残り時間: {remaining/60:.1f}分")
        
        # 最終保存
        print(f"\\n💾 最終保存実行...")
        self.storage.save_database()
        
        # 結果サマリー
        total_duration = (datetime.now() - self.stats['start_time']).total_seconds()
        self.stats['duration_minutes'] = total_duration / 60
        
        print("\\n" + "=" * 60)
        print("🎉 バッチ分析完了")
        print("=" * 60)
        print(f"処理時間: {total_duration/60:.1f}分")
        print(f"総処理数: {self.stats['processed_videos']}件")
        print(f"成功: {self.stats['successful_analyses']}件 ({self.stats['successful_analyses']/self.stats['processed_videos']*100:.1f}%)")
        print(f"失敗: {self.stats['failed_analyses']}件")
        
        return self.stats
    
    def get_analysis_progress(self) -> Dict[str, Any]:
        """分析進捗の取得"""
        db = self.storage.load_database()
        
        total_videos = len(db.videos)
        completed = sum(1 for v in db.videos.values() if v.analysis_status == AnalysisStatus.COMPLETED)
        failed = sum(1 for v in db.videos.values() if v.analysis_status == AnalysisStatus.FAILED)
        pending = sum(1 for v in db.videos.values() if v.analysis_status == AnalysisStatus.PENDING)
        
        return {
            'total_videos': total_videos,
            'completed': completed,
            'failed': failed,
            'pending': pending,
            'completion_rate': completed / total_videos if total_videos > 0 else 0,
            'success_rate': completed / (completed + failed) if (completed + failed) > 0 else 0
        }


def quick_batch_test(max_videos: int = 3):
    """クイックバッチテスト"""
    print(f"⚡ クイックバッチテスト ({max_videos}件)")
    
    analyzer = BatchAnalyzer(batch_size=2, delay_seconds=1.0)
    
    # 進捗確認
    progress = analyzer.get_analysis_progress()
    print(f"分析進捗: {progress['completed']}/{progress['total_videos']} ({progress['completion_rate']:.2%})")
    
    if progress['pending'] == 0:
        print("✅ 未分析動画がありません")
        return
    
    # テスト実行
    result = analyzer.run_batch_analysis(max_videos=max_videos)
    
    print(f"\\nテスト結果:")
    print(f"  処理: {result['processed_videos']}件")
    print(f"  成功: {result['successful_analyses']}件")
    print(f"  失敗: {result['failed_analyses']}件")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            quick_batch_test(3)
        elif sys.argv[1] == "full":
            analyzer = BatchAnalyzer()
            analyzer.run_batch_analysis()
        else:
            print("使用方法:")
            print("  python batch_analyzer.py test   # 3件テスト")
            print("  python batch_analyzer.py full   # 全件分析")
    else:
        # デフォルトはテスト
        quick_batch_test(3)
"""
統合ワークフローマネージャー

複数プレイリストの差分更新→分析→統計レポート生成の統合フロー
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

# パス設定
sys.path.append(str(Path(__file__).parent.parent))

from managers.playlist_config_manager import PlaylistConfigManager
from managers.multi_incremental_manager import MultiIncrementalManager
from analyzers.batch_analyzer import BatchAnalyzer
from storage.unified_storage import UnifiedStorage
from core.data_models import AnalysisStatus, UpdateFrequency


class IntegratedWorkflowManager:
    """統合ワークフローマネージャー"""
    
    def __init__(self):
        self.config_manager = PlaylistConfigManager()
        self.incremental_manager = MultiIncrementalManager()
        self.batch_analyzer = BatchAnalyzer()
        self.storage = UnifiedStorage()
        
        # ワークフロー統計
        self.workflow_stats = {
            'start_time': None,
            'end_time': None,
            'total_duration': 0,
            'phases': {
                'incremental_update': {'success': False, 'duration': 0, 'stats': {}},
                'batch_analysis': {'success': False, 'duration': 0, 'stats': {}},
                'report_generation': {'success': False, 'duration': 0, 'stats': {}}
            },
            'overall_success': False,
            'errors': []
        }
    
    def execute_full_workflow(
        self,
        force_update: bool = False,
        auto_analyze: bool = True,
        generate_report: bool = True,
        playlist_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """完全ワークフローの実行
        
        Args:
            force_update: 強制差分更新
            auto_analyze: 新規動画の自動分析
            generate_report: レポート生成
            playlist_ids: 対象プレイリスト（None=全て）
        """
        print("🚀 統合ワークフロー開始")
        print("=" * 60)
        
        self.workflow_stats['start_time'] = datetime.now()
        
        try:
            # Phase 1: 差分更新
            print(f"\n📥 Phase 1: 差分更新")
            phase1_start = datetime.now()
            
            update_result = self.incremental_manager.update_multiple_playlists(
                playlist_ids=playlist_ids,
                force_update=force_update,
                priority_order=True,
                enabled_only=True
            )
            
            phase1_duration = (datetime.now() - phase1_start).total_seconds()
            self.workflow_stats['phases']['incremental_update'] = {
                'success': update_result['success'],
                'duration': phase1_duration,
                'stats': update_result.get('stats', {})
            }
            
            if not update_result['success']:
                error_msg = f"差分更新失敗: {update_result.get('error')}"
                self.workflow_stats['errors'].append(error_msg)
                print(f"❌ {error_msg}")
                return self._finalize_workflow_stats()
            
            print(f"✅ Phase 1完了 ({phase1_duration:.1f}秒)")
            
            # Phase 2: バッチ分析（自動分析が有効な場合）
            if auto_analyze:
                print(f"\n🔍 Phase 2: バッチ分析")
                phase2_start = datetime.now()
                
                # 分析対象の動画を確認
                analysis_stats = self.batch_analyzer.get_analysis_progress()
                
                if analysis_stats['pending'] > 0:
                    print(f"未分析動画: {analysis_stats['pending']}件")
                    
                    # 新規動画のみを分析対象にする場合の制限
                    if self.workflow_stats['phases']['incremental_update']['stats'].get('total_new_videos', 0) > 0:
                        # 新規動画のみ分析
                        max_videos = min(analysis_stats['pending'], 10)  # 一度に最大10件
                        print(f"新規動画分析: 最大{max_videos}件")
                    else:
                        max_videos = None
                        print(f"全未分析動画処理")
                    
                    analysis_result = self.batch_analyzer.run_batch_analysis(max_videos=max_videos)
                    
                    phase2_duration = (datetime.now() - phase2_start).total_seconds()
                    self.workflow_stats['phases']['batch_analysis'] = {
                        'success': True,
                        'duration': phase2_duration,
                        'stats': analysis_result
                    }
                    
                    print(f"✅ Phase 2完了 ({phase2_duration:.1f}秒)")
                else:
                    print(f"⏭️ Phase 2スキップ: 未分析動画なし")
                    self.workflow_stats['phases']['batch_analysis'] = {
                        'success': True,
                        'duration': 0,
                        'stats': {'message': '未分析動画なし'}
                    }
            else:
                print(f"⏭️ Phase 2スキップ: 自動分析無効")
                self.workflow_stats['phases']['batch_analysis'] = {
                    'success': True,
                    'duration': 0,
                    'stats': {'message': '自動分析無効'}
                }
            
            # Phase 3: レポート生成
            if generate_report:
                print(f"\n📊 Phase 3: レポート生成")
                phase3_start = datetime.now()
                
                report_data = self.generate_comprehensive_report()
                
                phase3_duration = (datetime.now() - phase3_start).total_seconds()
                self.workflow_stats['phases']['report_generation'] = {
                    'success': True,
                    'duration': phase3_duration,
                    'stats': report_data
                }
                
                print(f"✅ Phase 3完了 ({phase3_duration:.1f}秒)")
            else:
                print(f"⏭️ Phase 3スキップ: レポート生成無効")
                self.workflow_stats['phases']['report_generation'] = {
                    'success': True,
                    'duration': 0,
                    'stats': {'message': 'レポート生成無効'}
                }
            
            self.workflow_stats['overall_success'] = True
            
        except Exception as e:
            error_msg = f"ワークフロー実行エラー: {e}"
            self.workflow_stats['errors'].append(error_msg)
            print(f"❌ {error_msg}")
        
        return self._finalize_workflow_stats()
    
    def _finalize_workflow_stats(self) -> Dict[str, Any]:
        """ワークフロー統計の最終化"""
        self.workflow_stats['end_time'] = datetime.now()
        self.workflow_stats['total_duration'] = (
            self.workflow_stats['end_time'] - self.workflow_stats['start_time']
        ).total_seconds()
        
        # サマリー表示
        print(f"\n🎉 統合ワークフロー完了")
        print("=" * 60)
        print(f"総実行時間: {self.workflow_stats['total_duration']/60:.1f}分")
        print(f"全体成功: {'✅' if self.workflow_stats['overall_success'] else '❌'}")
        
        for phase_name, phase_data in self.workflow_stats['phases'].items():
            status = "✅" if phase_data['success'] else "❌"
            print(f"{status} {phase_name}: {phase_data['duration']:.1f}秒")
        
        if self.workflow_stats['errors']:
            print(f"\nエラー:")
            for error in self.workflow_stats['errors']:
                print(f"  - {error}")
        
        return self.workflow_stats
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """包括的レポートの生成"""
        print("   📈 レポートデータ収集中...")
        
        # データベース統計
        db = self.storage.load_database()
        
        # プレイリスト統計
        playlist_stats = []
        configs = self.config_manager.list_configs()
        
        for config in configs:
            playlist = db.playlists.get(config.playlist_id)
            
            if playlist:
                # 分析状況の詳細計算
                pending_count = 0
                completed_count = 0
                failed_count = 0
                
                for video_id in playlist.video_ids:
                    video = db.videos.get(video_id)
                    if video:
                        if video.analysis_status == AnalysisStatus.PENDING:
                            pending_count += 1
                        elif video.analysis_status == AnalysisStatus.COMPLETED:
                            completed_count += 1
                        elif video.analysis_status == AnalysisStatus.FAILED:
                            failed_count += 1
                
                playlist_stat = {
                    'id': config.playlist_id,
                    'display_name': config.display_name,
                    'category': config.category.value,
                    'enabled': config.enabled,
                    'update_frequency': config.update_frequency.value,
                    'total_videos': playlist.total_videos,
                    'analysis_breakdown': {
                        'completed': completed_count,
                        'pending': pending_count,
                        'failed': failed_count
                    },
                    'analysis_rate': completed_count / playlist.total_videos if playlist.total_videos > 0 else 0,
                    'last_sync': playlist.last_incremental_sync.isoformat() if playlist.last_incremental_sync else None
                }
            else:
                playlist_stat = {
                    'id': config.playlist_id,
                    'display_name': config.display_name,
                    'category': config.category.value,
                    'enabled': config.enabled,
                    'update_frequency': config.update_frequency.value,
                    'total_videos': 0,
                    'analysis_breakdown': {'completed': 0, 'pending': 0, 'failed': 0},
                    'analysis_rate': 0,
                    'last_sync': None,
                    'note': 'データベースに未存在'
                }
            
            playlist_stats.append(playlist_stat)
        
        # 全体統計
        total_videos = len(db.videos)
        total_playlists = len(db.playlists)
        
        analysis_breakdown = {
            'completed': 0,
            'pending': 0,
            'failed': 0,
            'skipped': 0
        }
        
        for video in db.videos.values():
            status = video.analysis_status.value
            if status in analysis_breakdown:
                analysis_breakdown[status] += 1
        
        # クリエイター統計（上位10名）
        creator_stats = {}
        for video in db.videos.values():
            if video.creative_insight and video.creative_insight.creators:
                for creator in video.creative_insight.creators:
                    if creator.name not in creator_stats:
                        creator_stats[creator.name] = {'video_count': 0, 'roles': set()}
                    creator_stats[creator.name]['video_count'] += 1
                    creator_stats[creator.name]['roles'].add(creator.role)
        
        # リストに変換してソート
        top_creators = []
        for name, data in creator_stats.items():
            top_creators.append({
                'name': name,
                'video_count': data['video_count'],
                'roles': list(data['roles'])
            })
        
        top_creators.sort(key=lambda x: x['video_count'], reverse=True)
        top_creators = top_creators[:10]  # 上位10名
        
        # レポートデータ構成
        report_data = {
            'generation_time': datetime.now().isoformat(),
            'summary': {
                'total_playlists': total_playlists,
                'total_videos': total_videos,
                'analysis_breakdown': analysis_breakdown,
                'overall_analysis_rate': analysis_breakdown['completed'] / total_videos if total_videos > 0 else 0
            },
            'playlist_details': playlist_stats,
            'top_creators': top_creators,
            'recent_workflow_stats': self.workflow_stats
        }
        
        # レポートファイル保存
        report_file = self.storage.data_dir / f"workflow_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            import json
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)
            
            print(f"   💾 レポート保存: {report_file}")
            report_data['report_file'] = str(report_file)
            
        except Exception as e:
            print(f"   ⚠️ レポート保存失敗: {e}")
            report_data['report_save_error'] = str(e)
        
        return report_data
    
    def execute_scheduled_update(self) -> Dict[str, Any]:
        """スケジュール更新の実行（更新が必要なプレイリストのみ）"""
        print("⏰ スケジュール更新開始")
        
        # 更新が必要なプレイリストを特定
        schedule = self.incremental_manager.get_update_schedule()
        needs_update = [item for item in schedule if item['should_update']]
        
        if not needs_update:
            print("✅ スケジュール更新: 更新対象なし")
            return {'success': True, 'message': '更新対象なし', 'updated_playlists': 0}
        
        playlist_ids = [item['playlist_id'] for item in needs_update]
        
        print(f"📋 更新対象: {len(playlist_ids)}プレイリスト")
        for item in needs_update:
            print(f"  - {item['display_name']} (優先度: {item['priority']})")
        
        # 限定的なワークフロー実行
        return self.execute_full_workflow(
            force_update=False,
            auto_analyze=True,
            generate_report=False,  # スケジュール更新では簡易実行
            playlist_ids=playlist_ids
        )
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """ワークフロー状況の取得"""
        # 更新スケジュール
        schedule = self.incremental_manager.get_update_schedule()
        needs_update = [item for item in schedule if item['should_update']]
        
        # 分析進捗
        analysis_progress = self.batch_analyzer.get_analysis_progress()
        
        # プレイリスト設定統計
        config_stats = self.config_manager.get_statistics()
        
        return {
            'update_schedule': {
                'total_playlists': len(schedule),
                'needs_update': len(needs_update),
                'schedule_details': schedule
            },
            'analysis_progress': analysis_progress,
            'config_summary': config_stats,
            'recommended_actions': self._get_recommended_actions(needs_update, analysis_progress)
        }
    
    def _get_recommended_actions(self, needs_update: List[Dict], analysis_progress: Dict) -> List[str]:
        """推奨アクションの生成"""
        actions = []
        
        if len(needs_update) > 0:
            actions.append(f"🔄 {len(needs_update)}プレイリストの差分更新を実行")
        
        if analysis_progress['pending'] > 0:
            actions.append(f"🔍 {analysis_progress['pending']}動画の分析を実行")
        
        if analysis_progress['failed'] > 0:
            actions.append(f"🔧 {analysis_progress['failed']}件の分析失敗を確認")
        
        if not actions:
            actions.append("✅ 現在対応が必要なタスクはありません")
        
        return actions


# テスト・実行用関数
def test_integrated_workflow():
    """統合ワークフローのテスト"""
    print("=== 統合ワークフローテスト ===")
    
    manager = IntegratedWorkflowManager()
    
    # 現在の状況確認
    status = manager.get_workflow_status()
    
    print("現在の状況:")
    print(f"  更新対象プレイリスト: {status['update_schedule']['needs_update']}/{status['update_schedule']['total_playlists']}")
    print(f"  未分析動画: {status['analysis_progress']['pending']}")
    print(f"  分析失敗: {status['analysis_progress']['failed']}")
    
    print("\n推奨アクション:")
    for action in status['recommended_actions']:
        print(f"  {action}")
    
    print("\n=== テスト完了 ===")


def execute_workflow():
    """ワークフロー実行"""
    print("=== 統合ワークフロー実行 ===")
    
    manager = IntegratedWorkflowManager()
    
    # 完全ワークフロー実行
    result = manager.execute_full_workflow(
        force_update=False,
        auto_analyze=True,
        generate_report=True
    )
    
    print(f"\n実行結果: {'成功' if result['overall_success'] else '失敗'}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            test_integrated_workflow()
        elif sys.argv[1] == "run":
            execute_workflow()
        elif sys.argv[1] == "schedule":
            manager = IntegratedWorkflowManager()
            result = manager.execute_scheduled_update()
            print(f"スケジュール更新完了: {result.get('message', '')}")
        else:
            print("使用方法:")
            print("  python integrated_workflow_manager.py test      # テスト実行")
            print("  python integrated_workflow_manager.py run       # 完全ワークフロー")
            print("  python integrated_workflow_manager.py schedule  # スケジュール更新")
    else:
        test_integrated_workflow()
"""
プレイリスト管理コマンドラインインターフェース

複数プレイリストシステムの統合管理CLI
"""

import sys
import argparse
from pathlib import Path
from typing import List, Optional

# パス設定
sys.path.append(str(Path(__file__).parent.parent))

from managers.playlist_config_manager import PlaylistConfigManager
from managers.playlist_manager import PlaylistManager
from managers.multi_incremental_manager import MultiIncrementalManager
from managers.integrated_workflow_manager import IntegratedWorkflowManager
from core.data_models import PlaylistCategory, UpdateFrequency


class PlaylistCLI:
    """プレイリスト管理CLI"""
    
    def __init__(self):
        self.config_manager = PlaylistConfigManager()
        self.playlist_manager = PlaylistManager()
        self.incremental_manager = MultiIncrementalManager()
        self.workflow_manager = IntegratedWorkflowManager()
    
    def add_playlist(self, args):
        """プレイリスト追加"""
        print(f"🔄 プレイリスト追加: {args.url}")
        
        # カテゴリ変換
        category = PlaylistCategory.OTHER
        if args.category:
            try:
                category = PlaylistCategory(args.category.lower())
            except ValueError:
                print(f"⚠️ 無効なカテゴリ: {args.category}")
                print(f"利用可能: {[c.value for c in PlaylistCategory]}")
                return False
        
        # 更新頻度変換
        frequency = UpdateFrequency.MANUAL
        if args.frequency:
            try:
                frequency = UpdateFrequency(args.frequency.lower())
            except ValueError:
                print(f"⚠️ 無効な更新頻度: {args.frequency}")
                print(f"利用可能: {[f.value for f in UpdateFrequency]}")
                return False
        
        # プレイリスト追加実行
        success, message, result = self.playlist_manager.add_playlist_from_url(
            url_or_id=args.url,
            display_name=args.name or "",
            category=category,
            update_frequency=frequency,
            priority=args.priority,
            auto_analyze=not args.no_analyze,
            verify_access=not args.no_verify,
            collect_immediately=args.collect
        )
        
        if success:
            print(f"✅ {message}")
            
            if result.get('verification'):
                verification = result['verification']
                if verification['playlist_info']:
                    info = verification['playlist_info']
                    print(f"   タイトル: {info['title']}")
                    print(f"   動画数: {info['item_count']}")
                    print(f"   チャンネル: {info['channel_title']}")
            
            if result.get('collection'):
                collection = result['collection']
                if collection['success']:
                    coll_result = collection['result']
                    print(f"   収集結果: 新規 {coll_result['new_videos']}件")
        else:
            print(f"❌ {message}")
            return False
        
        return True
    
    def remove_playlist(self, args):
        """プレイリスト削除"""
        print(f"🗑️ プレイリスト削除: {args.playlist_id}")
        
        if not args.force:
            # 確認プロンプト
            config = self.config_manager.get_config(args.playlist_id)
            if config:
                print(f"削除対象: {config.display_name}")
                print(f"データも削除: {'はい' if args.data else 'いいえ'}")
                confirm = input("削除を実行しますか？ (y/N): ")
                if confirm.lower() not in ['y', 'yes']:
                    print("❌ 削除をキャンセルしました")
                    return False
        
        success, message = self.playlist_manager.remove_playlist(
            playlist_id=args.playlist_id,
            remove_data=args.data,
            backup_before_removal=not args.no_backup
        )
        
        if success:
            print(f"✅ {message}")
        else:
            print(f"❌ {message}")
            return False
        
        return True
    
    def list_playlists(self, args):
        """プレイリスト一覧"""
        status = self.playlist_manager.get_playlist_status()
        
        if 'error' in status:
            print(f"❌ {status['error']}")
            return False
        
        # ヘッダー情報
        db_stats = status['database_stats']
        config_stats = status['config_stats']
        
        print("📋 プレイリスト一覧")
        print("=" * 80)
        print(f"設定プレイリスト: {config_stats['total_playlists']}")
        print(f"データベース: {db_stats['total_playlists']}プレイリスト, {db_stats['total_videos']}動画")
        print(f"分析進捗: {db_stats['total_analyzed']}/{db_stats['total_videos']} ({db_stats['analysis_rate']:.1%})")
        
        # プレイリスト詳細
        details = status['playlist_details']
        
        if args.enabled_only:
            details = [d for d in details if d['enabled']]
        
        if args.category:
            details = [d for d in details if d['category'] == args.category.lower()]
        
        print(f"\n詳細情報 ({len(details)}件):")
        print("-" * 80)
        
        for detail in details:
            # ステータスアイコン
            enabled_icon = "✅" if detail['enabled'] else "❌"
            db_icon = "📁" if detail['in_database'] else "🆕"
            
            print(f"{enabled_icon}{db_icon} {detail['display_name']}")
            print(f"    ID: {detail['id']}")
            print(f"    カテゴリ: {detail['category']}")
            print(f"    更新頻度: {detail['update_frequency']}")
            print(f"    優先度: {detail['priority']}")
            print(f"    動画: {detail['total_videos']}件")
            print(f"    分析済み: {detail['analyzed_videos']}件 ({detail['analysis_rate']:.1%})")
            
            if detail['last_sync']:
                from datetime import datetime
                sync_time = datetime.fromisoformat(detail['last_sync'])
                print(f"    最終同期: {sync_time.strftime('%Y-%m-%d %H:%M')}")
            else:
                print(f"    最終同期: 未実行")
            
            print()
        
        return True
    
    def update_playlists(self, args):
        """プレイリスト更新"""
        if args.playlist_ids:
            print(f"🔄 指定プレイリスト更新: {len(args.playlist_ids)}件")
            playlist_ids = args.playlist_ids
        else:
            print(f"🔄 全プレイリスト更新")
            playlist_ids = None
        
        if args.force:
            print("🔥 強制更新モード")
        
        result = self.incremental_manager.update_multiple_playlists(
            playlist_ids=playlist_ids,
            force_update=args.force,
            priority_order=True,
            enabled_only=not args.include_disabled
        )
        
        if result['success']:
            stats = result['stats']
            print(f"✅ 更新完了")
            print(f"   処理: {stats['updated_playlists']}件")
            print(f"   スキップ: {stats['skipped_playlists']}件")
            print(f"   失敗: {stats['failed_playlists']}件")
            print(f"   新規動画: {stats['total_new_videos']}件")
            print(f"   重複統合: {stats['videos_unified']}件")
        else:
            print(f"❌ 更新失敗: {result.get('error')}")
            return False
        
        return True
    
    def analyze_videos(self, args):
        """動画分析"""
        from analyzers.batch_analyzer import BatchAnalyzer
        
        analyzer = BatchAnalyzer()
        
        # 分析対象数の決定
        if args.max_videos:
            max_videos = args.max_videos
            print(f"🔍 動画分析開始: 最大{max_videos}件")
        else:
            progress = analyzer.get_analysis_progress()
            max_videos = None
            print(f"🔍 動画分析開始: 未分析{progress['pending']}件")
        
        # 分析実行
        result = analyzer.run_batch_analysis(max_videos=max_videos)
        
        print(f"✅ 分析完了")
        print(f"   処理: {result['processed_videos']}件")
        print(f"   成功: {result['successful_analyses']}件")
        print(f"   失敗: {result['failed_analyses']}件")
        print(f"   成功率: {result['successful_analyses']/result['processed_videos']*100:.1f}%")
        
        return True
    
    def run_workflow(self, args):
        """統合ワークフロー実行"""
        print(f"🚀 統合ワークフロー実行")
        
        result = self.workflow_manager.execute_full_workflow(
            force_update=args.force_update,
            auto_analyze=args.auto_analyze,
            generate_report=args.generate_report
        )
        
        if result['overall_success']:
            print(f"✅ ワークフロー完了")
            
            # フェーズ別結果
            for phase_name, phase_data in result['phases'].items():
                status = "✅" if phase_data['success'] else "❌"
                print(f"   {status} {phase_name}: {phase_data['duration']:.1f}秒")
        else:
            print(f"❌ ワークフロー失敗")
            for error in result['errors']:
                print(f"   - {error}")
            return False
        
        return True
    
    def show_status(self, args):
        """システム状況表示"""
        status = self.workflow_manager.get_workflow_status()
        
        print("📊 システム状況")
        print("=" * 60)
        
        # 更新スケジュール
        update_info = status['update_schedule']
        print(f"更新スケジュール:")
        print(f"  更新対象: {update_info['needs_update']}/{update_info['total_playlists']}プレイリスト")
        
        # 分析進捗
        analysis_info = status['analysis_progress']
        print(f"\n分析進捗:")
        print(f"  完了: {analysis_info['completed']}")
        print(f"  未分析: {analysis_info['pending']}")
        print(f"  失敗: {analysis_info['failed']}")
        print(f"  成功率: {analysis_info['success_rate']:.1%}")
        
        # 推奨アクション
        print(f"\n推奨アクション:")
        for action in status['recommended_actions']:
            print(f"  {action}")
        
        return True


def create_parser():
    """コマンドラインパーサーの作成"""
    parser = argparse.ArgumentParser(
        description="YouTube知識システム プレイリスト管理CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='利用可能なコマンド')
    
    # add コマンド
    add_parser = subparsers.add_parser('add', help='プレイリスト追加')
    add_parser.add_argument('url', help='プレイリストURLまたはID')
    add_parser.add_argument('--name', help='表示名')
    add_parser.add_argument('--category', choices=[c.value for c in PlaylistCategory], help='カテゴリ')
    add_parser.add_argument('--frequency', choices=[f.value for f in UpdateFrequency], help='更新頻度')
    add_parser.add_argument('--priority', type=int, default=3, choices=range(1, 6), help='優先度 (1-5)')
    add_parser.add_argument('--no-analyze', action='store_true', help='自動分析を無効化')
    add_parser.add_argument('--no-verify', action='store_true', help='アクセス検証をスキップ')
    add_parser.add_argument('--collect', action='store_true', help='即座にデータ収集')
    
    # remove コマンド
    remove_parser = subparsers.add_parser('remove', help='プレイリスト削除')
    remove_parser.add_argument('playlist_id', help='プレイリストID')
    remove_parser.add_argument('--data', action='store_true', help='データベースからもデータ削除')
    remove_parser.add_argument('--force', action='store_true', help='確認なしで削除')
    remove_parser.add_argument('--no-backup', action='store_true', help='バックアップ作成をスキップ')
    
    # list コマンド
    list_parser = subparsers.add_parser('list', help='プレイリスト一覧')
    list_parser.add_argument('--enabled-only', action='store_true', help='有効なプレイリストのみ')
    list_parser.add_argument('--category', help='カテゴリでフィルタ')
    
    # update コマンド
    update_parser = subparsers.add_parser('update', help='プレイリスト更新')
    update_parser.add_argument('playlist_ids', nargs='*', help='更新対象プレイリストID')
    update_parser.add_argument('--force', action='store_true', help='強制更新')
    update_parser.add_argument('--include-disabled', action='store_true', help='無効なプレイリストも含める')
    
    # analyze コマンド
    analyze_parser = subparsers.add_parser('analyze', help='動画分析')
    analyze_parser.add_argument('--max-videos', type=int, help='最大分析動画数')
    
    # workflow コマンド
    workflow_parser = subparsers.add_parser('workflow', help='統合ワークフロー')
    workflow_parser.add_argument('--force-update', action='store_true', help='強制差分更新')
    workflow_parser.add_argument('--no-analyze', action='store_false', dest='auto_analyze', help='自動分析を無効化')
    workflow_parser.add_argument('--no-report', action='store_false', dest='generate_report', help='レポート生成を無効化')
    
    # status コマンド
    status_parser = subparsers.add_parser('status', help='システム状況表示')
    
    return parser


def main():
    """メイン関数"""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = PlaylistCLI()
    
    try:
        # コマンド実行
        if args.command == 'add':
            success = cli.add_playlist(args)
        elif args.command == 'remove':
            success = cli.remove_playlist(args)
        elif args.command == 'list':
            success = cli.list_playlists(args)
        elif args.command == 'update':
            success = cli.update_playlists(args)
        elif args.command == 'analyze':
            success = cli.analyze_videos(args)
        elif args.command == 'workflow':
            success = cli.run_workflow(args)
        elif args.command == 'status':
            success = cli.show_status(args)
        else:
            print(f"❌ 未知のコマンド: {args.command}")
            success = False
        
        # 終了コード
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print(f"\n⚠️ 処理が中断されました")
        sys.exit(1)
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
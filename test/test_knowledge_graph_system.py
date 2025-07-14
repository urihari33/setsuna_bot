#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知識グラフシステムテスト - Phase 2B動作確認
"""

import sys
import os
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.append(str(Path(__file__).parent.parent))

from core.knowledge_graph_system import KnowledgeGraphSystem
import json

class KnowledgeGraphTester:
    """知識グラフテスター"""
    
    def __init__(self):
        """初期化"""
        self.graph_system = KnowledgeGraphSystem()
        
    def run_comprehensive_test(self):
        """包括的テスト実行"""
        print("🔗 知識グラフシステム包括テスト")
        print("=" * 60)
        
        test_results = {}
        
        # テスト1: グラフ構築
        test_results["graph_building"] = self.test_graph_building()
        
        # テスト2: ノード作成
        test_results["node_creation"] = self.test_node_creation()
        
        # テスト3: エッジ構築
        test_results["edge_building"] = self.test_edge_building()
        
        # テスト4: クラスタリング
        test_results["clustering"] = self.test_clustering()
        
        # テスト5: 関連コンテンツ検索
        test_results["related_content"] = self.test_related_content_search()
        
        # テスト6: パターン分析
        test_results["pattern_analysis"] = self.test_pattern_analysis()
        
        # 総合結果
        self.display_comprehensive_results(test_results)
        
        return test_results
    
    def test_graph_building(self):
        """グラフ構築テスト"""
        print("\n🏗️ グラフ構築テスト")
        print("-" * 40)
        
        try:
            # 強制再構築
            print("📊 知識グラフを構築中...")
            self.graph_system.build_knowledge_graph(force_rebuild=True)
            
            # 統計取得
            stats = self.graph_system.get_graph_statistics()
            
            # 結果確認
            node_count = stats.get("total_nodes", 0)
            edge_count = stats.get("total_edges", 0)
            cluster_count = stats.get("clusters_count", 0)
            coverage_rate = stats.get("coverage_rate", 0.0)
            
            print(f"✅ ノード数: {node_count}")
            print(f"✅ エッジ数: {edge_count}")
            print(f"✅ クラスター数: {cluster_count}")
            print(f"✅ カバレッジ率: {coverage_rate:.1%}")
            
            # 成功判定
            success = (
                node_count > 0 and
                edge_count > 0 and
                coverage_rate > 0.5  # 50%以上のカバレッジ
            )
            
            return {
                "success": success,
                "node_count": node_count,
                "edge_count": edge_count,
                "cluster_count": cluster_count,
                "coverage_rate": coverage_rate
            }
            
        except Exception as e:
            print(f"❌ エラー: {e}")
            return {"success": False, "error": str(e)}
    
    def test_node_creation(self):
        """ノード作成テスト"""
        print("\n🎯 ノード作成テスト")
        print("-" * 40)
        
        try:
            # ノードタイプ別カウント
            node_types = {}
            for node in self.graph_system.knowledge_nodes.values():
                node_type = node.node_type
                node_types[node_type] = node_types.get(node_type, 0) + 1
            
            print("📊 ノードタイプ別統計:")
            for node_type, count in node_types.items():
                print(f"   {node_type}: {count}件")
            
            # 必要なタイプがあるかチェック
            required_types = ["video", "artist", "genre", "theme"]
            missing_types = [t for t in required_types if t not in node_types]
            
            if missing_types:
                print(f"⚠️ 不足しているノードタイプ: {missing_types}")
            else:
                print("✅ 全必要ノードタイプが作成されました")
            
            # サンプルノード詳細表示
            video_nodes = [n for n in self.graph_system.knowledge_nodes.values() if n.node_type == "video"]
            if video_nodes:
                sample = video_nodes[0]
                print(f"\n📄 サンプル動画ノード:")
                print(f"   ID: {sample.node_id}")
                print(f"   タイトル: {sample.title}")
                print(f"   関連度: {sample.relevance_score:.3f}")
                print(f"   属性数: {len(sample.attributes)}")
            
            return {
                "success": len(missing_types) == 0,
                "node_types": node_types,
                "missing_types": missing_types,
                "total_nodes": len(self.graph_system.knowledge_nodes)
            }
            
        except Exception as e:
            print(f"❌ エラー: {e}")
            return {"success": False, "error": str(e)}
    
    def test_edge_building(self):
        """エッジ構築テスト"""
        print("\n🔗 エッジ構築テスト")
        print("-" * 40)
        
        try:
            # エッジタイプ別カウント
            edge_types = {}
            total_strength = 0.0
            
            for edge in self.graph_system.knowledge_edges.values():
                edge_type = edge.relationship_type
                edge_types[edge_type] = edge_types.get(edge_type, 0) + 1
                total_strength += edge.strength
            
            print("📊 エッジタイプ別統計:")
            for edge_type, count in edge_types.items():
                print(f"   {edge_type}: {count}件")
            
            avg_strength = total_strength / len(self.graph_system.knowledge_edges) if self.graph_system.knowledge_edges else 0
            print(f"\n📊 平均エッジ強度: {avg_strength:.3f}")
            
            # 強い関連性のエッジを表示
            strong_edges = [e for e in self.graph_system.knowledge_edges.values() if e.strength > 0.7]
            print(f"💪 強い関連性エッジ（>0.7）: {len(strong_edges)}件")
            
            if strong_edges:
                sample_edge = strong_edges[0]
                print(f"   サンプル: {sample_edge.source_id} → {sample_edge.target_id}")
                print(f"   タイプ: {sample_edge.relationship_type}")
                print(f"   強度: {sample_edge.strength:.3f}")
                print(f"   根拠: {sample_edge.evidence}")
            
            return {
                "success": len(self.graph_system.knowledge_edges) > 0,
                "edge_types": edge_types,
                "total_edges": len(self.graph_system.knowledge_edges),
                "average_strength": avg_strength,
                "strong_edges_count": len(strong_edges)
            }
            
        except Exception as e:
            print(f"❌ エラー: {e}")
            return {"success": False, "error": str(e)}
    
    def test_clustering(self):
        """クラスタリングテスト"""
        print("\n🎯 クラスタリングテスト")
        print("-" * 40)
        
        try:
            clusters = self.graph_system.clusters
            
            if not clusters:
                print("⚠️ クラスターが作成されていません")
                return {"success": False, "cluster_count": 0}
            
            print(f"✅ {len(clusters)}個のクラスターが作成されました")
            
            # クラスタータイプ別統計
            cluster_types = {}
            total_cohesion = 0.0
            
            for cluster in clusters.values():
                cluster_type = cluster.cluster_type
                cluster_types[cluster_type] = cluster_types.get(cluster_type, 0) + 1
                total_cohesion += cluster.cohesion_score
            
            avg_cohesion = total_cohesion / len(clusters)
            
            print("\n📊 クラスタータイプ別統計:")
            for cluster_type, count in cluster_types.items():
                print(f"   {cluster_type}: {count}件")
            
            print(f"\n📊 平均結束度: {avg_cohesion:.3f}")
            
            # 最大クラスター詳細
            largest_cluster = max(clusters.values(), key=lambda c: len(c.node_ids))
            print(f"\n📊 最大クラスター:")
            print(f"   ID: {largest_cluster.cluster_id}")
            print(f"   タイプ: {largest_cluster.cluster_type}")
            print(f"   ノード数: {len(largest_cluster.node_ids)}")
            print(f"   結束度: {largest_cluster.cohesion_score:.3f}")
            print(f"   中心概念: {largest_cluster.central_concepts}")
            
            return {
                "success": True,
                "cluster_count": len(clusters),
                "cluster_types": cluster_types,
                "average_cohesion": avg_cohesion,
                "largest_cluster_size": len(largest_cluster.node_ids)
            }
            
        except Exception as e:
            print(f"❌ エラー: {e}")
            return {"success": False, "error": str(e)}
    
    def test_related_content_search(self):
        """関連コンテンツ検索テスト"""
        print("\n🔍 関連コンテンツ検索テスト")
        print("-" * 40)
        
        try:
            # テスト用動画IDを取得
            video_nodes = [n for n in self.graph_system.knowledge_nodes.values() if n.node_type == "video"]
            if not video_nodes:
                print("❌ 動画ノードが見つかりません")
                return {"success": False, "error": "No video nodes"}
            
            # 最初の動画で関連コンテンツ検索
            test_video = video_nodes[0]
            video_id = test_video.node_id.replace("video_", "")
            
            print(f"🎯 テスト対象動画: {test_video.title}")
            
            # 関連コンテンツ検索
            related_items = self.graph_system.find_related_content(video_id, max_results=5)
            
            print(f"✅ {len(related_items)}件の関連コンテンツが見つかりました")
            
            if related_items:
                print("\n📋 関連コンテンツ一覧:")
                for i, item in enumerate(related_items[:3], 1):
                    print(f"   {i}. {item['title']} ({item['type']})")
                    print(f"      関連度: {item['relevance']:.3f}")
                    print(f"      関係: {item['relationship']}")
                    if item['evidence']:
                        print(f"      根拠: {', '.join(item['evidence'])}")
            
            # クラスター推薦テスト
            cluster_recommendations = self.graph_system.get_cluster_recommendations(video_id)
            print(f"\n🎯 クラスター推薦: {len(cluster_recommendations)}件")
            
            return {
                "success": len(related_items) > 0,
                "related_count": len(related_items),
                "cluster_recommendations": len(cluster_recommendations),
                "test_video": test_video.title
            }
            
        except Exception as e:
            print(f"❌ エラー: {e}")
            return {"success": False, "error": str(e)}
    
    def test_pattern_analysis(self):
        """パターン分析テスト"""
        print("\n📊 パターン分析テスト")
        print("-" * 40)
        
        try:
            patterns = self.graph_system.analyze_knowledge_patterns()
            
            print("📊 知識パターン分析結果:")
            
            # 人気アーティスト
            popular_artists = patterns.get("popular_artists", [])
            print(f"\n🎤 人気アーティストTOP3:")
            for i, artist in enumerate(popular_artists[:3], 1):
                print(f"   {i}. {artist['name']} ({artist['video_count']}曲)")
            
            # 支配的ジャンル
            dominant_genres = patterns.get("dominant_genres", [])
            print(f"\n🎵 支配的ジャンルTOP3:")
            for i, genre in enumerate(dominant_genres[:3], 1):
                print(f"   {i}. {genre['name']} ({genre['video_count']}曲)")
            
            # 一般的テーマ
            common_themes = patterns.get("common_themes", [])
            print(f"\n💭 一般的テーマTOP3:")
            for i, theme in enumerate(common_themes[:3], 1):
                print(f"   {i}. {theme['name']} ({theme['video_count']}曲)")
            
            # クラスター分析
            cluster_analysis = patterns.get("cluster_analysis", {})
            print(f"\n🎯 クラスター分析:")
            print(f"   総クラスター数: {cluster_analysis.get('total_clusters', 0)}")
            print(f"   平均結束度: {cluster_analysis.get('average_cohesion', 0):.3f}")
            
            # 接続性分析
            connectivity = patterns.get("connectivity_analysis", {})
            if connectivity:
                print(f"\n🔗 接続性分析:")
                print(f"   密度: {connectivity.get('density', 0):.3f}")
                print(f"   平均クラスタリング係数: {connectivity.get('average_clustering', 0):.3f}")
                print(f"   連結成分数: {connectivity.get('number_of_components', 0)}")
            
            return {
                "success": True,
                "popular_artists_count": len(popular_artists),
                "dominant_genres_count": len(dominant_genres),
                "common_themes_count": len(common_themes),
                "cluster_analysis": cluster_analysis,
                "connectivity_analysis": connectivity
            }
            
        except Exception as e:
            print(f"❌ エラー: {e}")
            return {"success": False, "error": str(e)}
    
    def display_comprehensive_results(self, test_results):
        """総合結果表示"""
        print("\n" + "=" * 60)
        print("📊 総合テスト結果")
        print("=" * 60)
        
        total_tests = 0
        passed_tests = 0
        
        for test_name, result in test_results.items():
            total_tests += 1
            
            if result.get("success", False):
                passed_tests += 1
                status = "✅ 合格"
            else:
                status = "❌ 不合格"
            
            print(f"{status} {test_name}")
            
            # 主要メトリクス表示
            if test_name == "graph_building":
                if "node_count" in result:
                    print(f"    ノード: {result['node_count']}, エッジ: {result['edge_count']}")
            elif test_name == "clustering":
                if "cluster_count" in result:
                    print(f"    クラスター数: {result['cluster_count']}")
            elif test_name == "related_content":
                if "related_count" in result:
                    print(f"    関連コンテンツ: {result['related_count']}件")
        
        overall_success_rate = passed_tests / total_tests * 100
        print(f"\n🎯 総合成功率: {overall_success_rate:.1f}% ({passed_tests}/{total_tests})")
        
        if overall_success_rate >= 80:
            print("🎉 知識グラフシステムが正常に動作しています！")
        elif overall_success_rate >= 60:
            print("⚠️ 一部機能に改善が必要です。")
        else:
            print("🔧 大幅な修正が必要です。")

def main():
    """メイン実行"""
    tester = KnowledgeGraphTester()
    results = tester.run_comprehensive_test()
    
    print(f"\n✨ 知識グラフシステムテスト完了")
    
    return results

if __name__ == "__main__":
    main()
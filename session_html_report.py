#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
セッション結果HTMLレポート生成ツール
学習セッションの結果を見やすいHTMLレポートとして出力
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from session_result_viewer import SessionResultViewer

class SessionHTMLReportGenerator:
    """セッション結果HTMLレポート生成クラス"""
    
    def __init__(self):
        """初期化"""
        self.viewer = SessionResultViewer()
        
    def generate_html_report(self, session_id: str, output_path: Optional[Path] = None) -> str:
        """HTMLレポート生成"""
        session_data = self.viewer.load_session_details(session_id)
        if not session_data:
            return ""
        
        metadata = session_data.get("session_metadata", {})
        
        # 出力パス設定
        if output_path is None:
            output_path = Path(f"session_report_{session_id}.html")
        
        html_content = self._generate_html_content(session_id, session_data, metadata)
        
        # HTMLファイル書き込み
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(output_path)
    
    def _generate_html_content(self, session_id: str, session_data: Dict, metadata: Dict) -> str:
        """HTML内容生成"""
        html = f"""
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>学習セッション報告書: {session_id}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            border-bottom: 3px solid #007acc;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        .header h1 {{
            color: #007acc;
            margin: 0;
            font-size: 2.5em;
        }}
        .meta-info {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .meta-card {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #007acc;
        }}
        .meta-card h3 {{
            margin-top: 0;
            color: #007acc;
        }}
        .section {{
            margin-bottom: 40px;
        }}
        .section h2 {{
            color: #333;
            border-bottom: 2px solid #007acc;
            padding-bottom: 10px;
        }}
        .source-item {{
            background-color: #f8f9fa;
            margin-bottom: 15px;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #28a745;
        }}
        .source-item h4 {{
            margin-top: 0;
            color: #333;
        }}
        .source-meta {{
            display: flex;
            gap: 20px;
            margin-bottom: 10px;
            font-size: 0.9em;
        }}
        .score {{
            background-color: #007acc;
            color: white;
            padding: 2px 8px;
            border-radius: 4px;
        }}
        .url {{
            color: #007acc;
            text-decoration: none;
        }}
        .url:hover {{
            text-decoration: underline;
        }}
        .content {{
            background-color: white;
            padding: 15px;
            border-radius: 5px;
            margin-top: 10px;
        }}
        .analysis-item {{
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 0 8px 8px 0;
        }}
        .knowledge-item {{
            background-color: #d1ecf1;
            border-left: 4px solid #17a2b8;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 0 8px 8px 0;
        }}
        .status-completed {{ color: #28a745; }}
        .status-running {{ color: #ffc107; }}
        .status-error {{ color: #dc3545; }}
        .timestamp {{
            color: #6c757d;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 学習セッション報告書</h1>
            <p class="timestamp">生成日時: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        {self._generate_meta_info_html(metadata)}
        {self._generate_collection_html(session_data.get("collection_results", {}))}
        {self._generate_analysis_html(session_data.get("analysis_results", {}))}
        {self._generate_knowledge_html(session_data.get("generated_knowledge", {}))}
    </div>
</body>
</html>
"""
        return html
    
    def _generate_meta_info_html(self, metadata: Dict) -> str:
        """メタ情報HTML生成"""
        status_class = f"status-{metadata.get('status', 'unknown')}"
        
        return f"""
        <div class="meta-info">
            <div class="meta-card">
                <h3>📋 基本情報</h3>
                <p><strong>セッションID:</strong> {metadata.get('session_id', '不明')}</p>
                <p><strong>テーマ:</strong> {metadata.get('theme', '不明')}</p>
                <p><strong>学習タイプ:</strong> {metadata.get('learning_type', '不明')}</p>
                <p><strong>深度レベル:</strong> {metadata.get('depth_level', 0)}</p>
            </div>
            <div class="meta-card">
                <h3>⏱️ 実行情報</h3>
                <p><strong>開始時刻:</strong> {metadata.get('start_time', '不明')}</p>
                <p><strong>終了時刻:</strong> {metadata.get('end_time', '実行中')}</p>
                <p><strong>ステータス:</strong> <span class="{status_class}">{metadata.get('status', '不明')}</span></p>
                <p><strong>タグ:</strong> {', '.join(metadata.get('tags', []))}</p>
            </div>
            <div class="meta-card">
                <h3>📊 進捗情報</h3>
                <p><strong>収集アイテム:</strong> {metadata.get('collected_items', 0)}件</p>
                <p><strong>処理アイテム:</strong> {metadata.get('processed_items', 0)}件</p>
                <p><strong>重要発見:</strong> {len(metadata.get('important_findings', []))}件</p>
                <p><strong>現在のコスト:</strong> ${metadata.get('current_cost', 0.0)}</p>
            </div>
        </div>
        """
    
    def _generate_collection_html(self, collection_results: Dict) -> str:
        """収集結果HTML生成"""
        if not collection_results:
            return ""
        
        sources = collection_results.get("information_sources", [])
        if not sources:
            return ""
        
        sources_html = ""
        for i, source in enumerate(sources, 1):
            sources_html += f"""
            <div class="source-item">
                <h4>{i}. {source.get('title', '無題')}</h4>
                <div class="source-meta">
                    <span class="score">信頼性: {source.get('reliability_score', 0):.2f}</span>
                    <span class="score">関連性: {source.get('relevance_score', 0):.2f}</span>
                    <span>タイプ: {source.get('source_type', '不明')}</span>
                </div>
                <p><strong>URL:</strong> <a href="{source.get('url', '#')}" class="url" target="_blank">{source.get('url', 'なし')}</a></p>
                <div class="content">
                    {source.get('content', 'コンテンツなし')}
                </div>
            </div>
            """
        
        return f"""
        <div class="section">
            <h2>🔍 情報収集結果 ({len(sources)}件)</h2>
            {sources_html}
        </div>
        """
    
    def _generate_analysis_html(self, analysis_results: Dict) -> str:
        """分析結果HTML生成"""
        if not analysis_results:
            return ""
        
        html = '<div class="section"><h2>🧠 コンテンツ分析結果</h2>'
        
        # キーファインディング
        key_findings = analysis_results.get("key_findings", [])
        if key_findings:
            findings_html = ""
            for finding in key_findings:
                findings_html += f'<div class="analysis-item">{finding}</div>'
            html += f"<h3>🔑 重要な発見</h3>{findings_html}"
        
        # エンティティ
        entities = analysis_results.get("extracted_entities", [])
        if entities:
            entities_str = ", ".join(entities)
            html += f'<h3>🏷️ 抽出エンティティ</h3><div class="analysis-item">{entities_str}</div>'
        
        # 関係性
        relationships = analysis_results.get("identified_relationships", [])
        if relationships:
            relationships_html = ""
            for relationship in relationships:
                relationships_html += f'<div class="analysis-item">{relationship}</div>'
            html += f"<h3>🔗 関係性分析</h3>{relationships_html}"
        
        html += '</div>'
        return html
    
    def _generate_knowledge_html(self, knowledge_integration: Dict) -> str:
        """知識統合HTML生成"""
        if not knowledge_integration:
            return ""
        
        html = '<div class="section"><h2>🔗 知識統合結果</h2>'
        
        # サマリー
        summary = knowledge_integration.get("integration_summary", "")
        if summary:
            html += f'<h3>📋 統合サマリー</h3><div class="knowledge-item">{summary}</div>'
        
        # キーポイント
        key_points = knowledge_integration.get("key_points", [])
        if key_points:
            points_html = ""
            for point in key_points:
                points_html += f'<div class="knowledge-item">{point}</div>'
            html += f"<h3>🎯 主要ポイント</h3>{points_html}"
        
        # 推奨アクション
        recommendations = knowledge_integration.get("recommendations", [])
        if recommendations:
            rec_html = ""
            for rec in recommendations:
                rec_html += f'<div class="knowledge-item">{rec}</div>'
            html += f"<h3>💡 推奨アクション</h3>{rec_html}"
        
        html += '</div>'
        return html

def main():
    """メイン関数"""
    if len(sys.argv) != 2:
        print("使用方法: python session_html_report.py <session_id>")
        return
    
    session_id = sys.argv[1]
    generator = SessionHTMLReportGenerator()
    
    output_file = generator.generate_html_report(session_id)
    if output_file:
        print(f"✅ HTMLレポート生成完了: {output_file}")
        print(f"💡 ブラウザで開いて確認できます: file://{Path(output_file).absolute()}")
    else:
        print("❌ レポート生成に失敗しました")

if __name__ == "__main__":
    main()
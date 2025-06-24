"""
YouTube動画概要欄の分析
GPT APIを使用してクリエイター情報・歌詞・制作情報を抽出
"""
import json
import os
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# 環境変数読み込み
load_dotenv()


class DescriptionAnalyzer:
    """概要欄分析クラス"""
    
    def __init__(self, model="gpt-4o-mini"):
        # OpenAI API設定
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY が設定されていません。.envファイルを確認してください。")
        
        self.client = OpenAI(api_key=api_key)
        self.model = model
        
        # 分析プロンプト
        self.analysis_prompt = self._create_analysis_prompt()
    
    def _create_analysis_prompt(self) -> str:
        """分析用プロンプトを作成（コスト削減版）"""
        return """YouTube概要欄から制作情報をJSON抽出。不明な項目はnull。

重要: JSONレスポンスは正確な形式で出力してください。
- 文字列内の改行は \\n でエスケープ
- 引用符は \\" でエスケープ  
- 末尾カンマは禁止

抽出項目：
1. クリエイター（vocal,movie,illustration,composer,lyricist,arranger,mix等）
2. 歌詞（最初の500文字まで、改行は\\nでエスケープ）
3. ツール（software,instruments,equipment）
4. 音楽情報（bpm,key,genre,mood）

JSON形式（必ず```jsonと```で囲む）：
```json
{
  "creators": {"vocal": "名前", "movie": "名前", "composer": "名前"},
  "lyrics": "歌詞全文（改行は\\\\nでエスケープ）",
  "tools": {"software": ["ツール名"], "instruments": ["楽器名"]},
  "music_info": {"genre": "ジャンル", "mood": "雰囲気"},
  "confidence_score": 0.8
}
```

概要欄：
"""
    
    def analyze_description(self, description: str, video_title: str = "") -> Optional[Dict[str, Any]]:
        """概要欄を分析してクリエイター情報等を抽出"""
        if not description or len(description.strip()) < 10:
            return None
        
        try:
            # プロンプトに概要欄テキストを追加
            full_prompt = self.analysis_prompt + f"\n\n動画タイトル: {video_title}\n\n概要欄:\n{description}"
            
            # OpenAI API呼び出し（トークン数を調整）
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "あなたは音楽・映像制作の専門家です。正確なJSON形式で回答してください。"},
                    {"role": "user", "content": full_prompt}
                ],
                max_tokens=1200,  # トークン数を増加（JSON完了を確保）
                temperature=0.1
            )
            
            # レスポンスからJSONを抽出
            response_text = response.choices[0].message.content.strip()
            
            # JSON部分を抽出（```json と ``` の間）
            json_start = response_text.find('```json')
            if json_start != -1:
                json_start += 7  # '```json'の長さ
                json_end = response_text.find('```', json_start)
                if json_end != -1:
                    json_text = response_text[json_start:json_end].strip()
                else:
                    json_text = response_text[json_start:].strip()
            else:
                # JSON形式のマーカーがない場合、全体をJSONとして試行
                json_text = response_text
            
            # JSONパース（エラー処理強化）
            try:
                analysis_result = json.loads(json_text)
                analysis_result['analyzed_at'] = datetime.now().isoformat()
                analysis_result['analysis_model'] = "gpt-4-turbo"
                return analysis_result
            except json.JSONDecodeError as e:
                print(f"JSON解析エラー: {e}")
                print(f"レスポンステキスト: {response_text}")
                
                # JSON修復を試行
                try:
                    fixed_json = self._fix_json_response(json_text)
                    if fixed_json:
                        analysis_result = json.loads(fixed_json)
                        analysis_result['analyzed_at'] = datetime.now().isoformat()
                        analysis_result['analysis_model'] = "gpt-4-turbo"
                        print("✅ JSON修復成功")
                        return analysis_result
                except Exception as fix_error:
                    print(f"JSON修復失敗: {fix_error}")
                
                return None
            
        except Exception as e:
            print(f"概要欄分析エラー: {e}")
            return None
    
    def _fix_json_response(self, json_text: str) -> Optional[str]:
        """不正なJSONレスポンスを修復"""
        try:
            import re
            
            print(f"🔧 JSON修復開始...")
            print(f"元のJSON（最初の200文字）: {json_text[:200]}...")
            
            # Step 1: 基本的なクリーニング
            fixed_text = json_text.strip()
            
            # Step 2: 不完全なJSONを検出して修復
            # 最後の } がない場合や、文字列が途中で切れている場合を処理
            
            # 開いた引用符の数をチェック
            quote_count = fixed_text.count('"')
            if quote_count % 2 == 1:
                # 奇数の場合、最後に引用符を追加
                print("🔧 不完全な文字列を検出、引用符を追加")
                fixed_text = fixed_text + '"'
            
            # lyrics フィールドが不完全な場合の特別処理
            lyrics_match = re.search(r'"lyrics":\s*"([^"]*)', fixed_text)
            if lyrics_match and not re.search(r'"lyrics":\s*"[^"]*"', fixed_text):
                # lyrics が途中で切れている場合
                print("🔧 不完全なlyricsフィールドを検出")
                # 安全な終了処理
                lyrics_start = lyrics_match.start(1)
                before_lyrics = fixed_text[:lyrics_start]
                # lyrics内容を安全に終了
                safe_ending = '",\n  "tools": null,\n  "music_info": null,\n  "confidence_score": 0.6\n}'
                fixed_text = before_lyrics + safe_ending
            
            # Step 3: JSONの構造を補完
            # 基本的なJSONオブジェクトの構造をチェック
            if not fixed_text.strip().endswith('}'):
                # JSONオブジェクトが完了していない場合
                print("🔧 不完全なJSONオブジェクトを検出、終了ブレースを追加")
                
                # 最低限の構造を確保
                if '"creators":' in fixed_text and not '"confidence_score":' in fixed_text:
                    # 基本フィールドを追加
                    if fixed_text.strip().endswith(','):
                        fixed_text = fixed_text.rstrip(',')
                    if not fixed_text.strip().endswith('}'):
                        fixed_text += ',\n  "confidence_score": 0.5\n}'
                elif not fixed_text.strip().endswith('}'):
                    fixed_text += '\n}'
            
            # Step 4: 改行をエスケープ（lyrics内のみ）
            def escape_lyrics_content(match):
                lyrics_content = match.group(1)
                # 改行をエスケープ
                lyrics_content = lyrics_content.replace('\n', '\\n').replace('\r', '\\r')
                # 内部の引用符をエスケープ
                lyrics_content = lyrics_content.replace('"', '\\"')
                return f'"lyrics": "{lyrics_content}"'
            
            # lyrics フィールドのみエスケープ処理
            fixed_text = re.sub(r'"lyrics":\s*"([^"]*(?:\\"[^"]*)*)"', escape_lyrics_content, fixed_text, flags=re.DOTALL)
            
            # Step 5: 最終的なクリーニング
            # 末尾のカンマを削除
            fixed_text = re.sub(r',(\s*[}\]])', r'\1', fixed_text)
            
            print(f"🔧 修復後JSON（最初の200文字）: {fixed_text[:200]}...")
            
            # Step 6: JSON構文の妥当性確認
            json.loads(fixed_text)
            print("✅ JSON修復成功")
            return fixed_text
            
        except Exception as e:
            print(f"❌ JSON修復処理エラー: {e}")
            
            # 最後の手段：最小限のJSONを返す
            try:
                minimal_json = {
                    "creators": {},
                    "lyrics": "解析失敗",
                    "tools": None,
                    "music_info": None,
                    "confidence_score": 0.1
                }
                print("🔧 最小限のJSONで代替")
                return json.dumps(minimal_json, ensure_ascii=False)
            except:
                return None
    
    def batch_analyze_videos(self, videos: List[Dict[str, Any]], delay: float = 1.0) -> List[Dict[str, Any]]:
        """複数動画の概要欄を一括分析"""
        analyzed_videos = []
        
        for i, video in enumerate(videos):
            print(f"分析中: {i+1}/{len(videos)} - {video.get('title', 'Unknown')}")
            
            # 概要欄分析
            description = video.get('description', '')
            title = video.get('title', '')
            
            analysis = self.analyze_description(description, title)
            
            # 元の動画データに分析結果を追加
            enhanced_video = video.copy()
            enhanced_video['description_analysis'] = analysis
            
            analyzed_videos.append(enhanced_video)
            
            # API制限を考慮して待機
            if delay > 0:
                time.sleep(delay)
            
            # 進捗表示
            if (i + 1) % 5 == 0:
                print(f"  {i + 1} 件の分析が完了しました")
        
        print(f"全 {len(analyzed_videos)} 件の分析が完了しました")
        return analyzed_videos
    
    def extract_creative_insights(self, videos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析結果から創作に関する洞察を抽出"""
        insights = {
            "creators": {},
            "tools": {"software": set(), "instruments": set(), "equipment": set()},
            "music_trends": {"genres": {}, "moods": {}, "keys": {}},
            "collaboration_patterns": [],
            "lyrics_themes": [],
            "total_analyzed": 0,
            "successful_analyses": 0
        }
        
        print("洞察抽出を開始します...")
        
        for i, video in enumerate(videos):
            try:
                analysis = video.get('description_analysis')
                if not analysis:
                    print(f"  動画 {i+1}: 分析結果なし")
                    continue
                
                insights["total_analyzed"] += 1
                
                # 信頼度が低い場合はスキップ
                confidence = analysis.get('confidence_score', 0)
                if confidence < 0.3:
                    print(f"  動画 {i+1}: 信頼度が低い ({confidence:.2f})")
                    continue
                
                insights["successful_analyses"] += 1
                print(f"  動画 {i+1}: 洞察抽出中...")
                
                # クリエイター情報を集計
                creators = analysis.get('creators', {})
                for role, name in creators.items():
                    if name and name != "null":
                        if role not in insights["creators"]:
                            insights["creators"][role] = {}
                        if name not in insights["creators"][role]:
                            insights["creators"][role][name] = 0
                        insights["creators"][role][name] += 1
                
                # ツール情報を集計
                tools = analysis.get('tools', {})
                print(f"    ツール情報: {tools}")
                
                for tool_type, tool_list in tools.items():
                    if tool_list and isinstance(tool_list, list):
                        # リスト内のアイテムが文字列であることを確認
                        for item in tool_list:
                            if isinstance(item, str) and item.strip():
                                insights["tools"][tool_type].add(item.strip())
                            else:
                                print(f"      警告: 非文字列アイテム ({type(item)}): {item}")
                    else:
                        print(f"      {tool_type}: {type(tool_list)} - {tool_list}")
                
                # 音楽情報を集計
                music_info = analysis.get('music_info', {})
                for key, value in music_info.items():
                    if value and value != "null":
                        if key not in insights["music_trends"]:
                            insights["music_trends"][key] = {}
                        if value not in insights["music_trends"][key]:
                            insights["music_trends"][key][value] = 0
                        insights["music_trends"][key][value] += 1
                        
            except Exception as e:
                print(f"  動画 {i+1} の洞察抽出でエラー: {e}")
                continue
        
        # セットをリストに変換（JSON化のため）
        for tool_type in insights["tools"]:
            insights["tools"][tool_type] = list(insights["tools"][tool_type])
        
        return insights
    
    def save_analysis_results(self, videos_with_analysis: List[Dict[str, Any]], output_path: str):
        """分析結果を保存"""
        try:
            from pathlib import Path
            
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            print(f"保存処理開始: {output_file}")
            
            # 基本統計情報
            total_videos = len(videos_with_analysis)
            analyzed_count = sum(1 for v in videos_with_analysis if v.get('description_analysis'))
            
            print(f"統計: {analyzed_count}/{total_videos} 件分析済み")
            
            # 創作洞察を抽出（エラーが発生してもスキップ）
            try:
                insights = self.extract_creative_insights(videos_with_analysis)
                print("洞察抽出完了")
            except Exception as e:
                print(f"洞察抽出でエラー: {e}")
                insights = {"error": str(e)}
            
            # 保存データ
            save_data = {
                "analysis_info": {
                    "total_videos": total_videos,
                    "analyzed_videos": analyzed_count,
                    "analysis_success_rate": analyzed_count / total_videos if total_videos > 0 else 0,
                    "analysis_date": datetime.now().isoformat()
                },
                "creative_insights": insights,
                "videos": videos_with_analysis
            }
            
            # JSON保存
            print("JSONファイル書き込み中...")
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 分析結果を保存しました: {output_file}")
            print(f"分析成功率: {analyzed_count}/{total_videos} ({analyzed_count/total_videos*100:.1f}%)")
            
        except Exception as e:
            print(f"❌ 保存処理でエラー: {e}")
            raise


def analyze_playlist_from_file(playlist_file_path: str, max_videos: int = 3):
    """プレイリストファイルを指定して分析を実行"""
    analyzer = DescriptionAnalyzer()
    
    print(f"=== 概要欄分析テスト ===")
    print(f"プレイリストファイル: {playlist_file_path}")
    
    from pathlib import Path
    import json
    
    playlist_file = Path(playlist_file_path)
    
    if not playlist_file.exists():
        print(f"エラー: プレイリストファイルが見つかりません: {playlist_file}")
        print("利用可能なプレイリストファイル:")
        
        # 利用可能なファイルを表示
        playlist_dir = Path("/mnt/d/setsuna_bot/youtube_knowledge_system/data/playlists")
        if playlist_dir.exists():
            for file in playlist_dir.glob("*.json"):
                print(f"  {file}")
        return
    
    try:
        with open(playlist_file, 'r', encoding='utf-8') as f:
            playlist_data = json.load(f)
        
        videos = playlist_data.get('videos', [])
        playlist_info = playlist_data.get('playlist_info', {})
        
        print(f"プレイリスト名: {playlist_info.get('title', 'Unknown')}")
        print(f"動画総数: {len(videos)} 件")
        
        # テスト用に指定件数だけ分析
        test_videos = videos[:max_videos]
        
        print(f"分析対象: {len(test_videos)} 件の動画")
        
        # 分析実行
        analyzed_videos = analyzer.batch_analyze_videos(test_videos, delay=2.0)
        
        # 結果保存（プレイリストIDを含むファイル名）
        playlist_id = playlist_info.get('id', 'unknown')
        from pathlib import Path
        output_path = Path("D:/setsuna_bot/youtube_knowledge_system/data") / f"analyzed_{playlist_id}.json"
        print(f"保存先: {output_path}")
        analyzer.save_analysis_results(analyzed_videos, str(output_path))
        
        # サンプル結果表示
        print("\n=== 分析結果サンプル ===")
        for i, video in enumerate(analyzed_videos):
            analysis = video.get('description_analysis')
            if analysis:
                print(f"\n{i+1}. {video['title']}")
                
                # クリエイター情報
                creators = analysis.get('creators', {})
                if any(v for v in creators.values() if v and v != "null"):
                    print("  クリエイター:")
                    for role, name in creators.items():
                        if name and name != "null":
                            print(f"    {role}: {name}")
                
                # 音楽情報
                music_info = analysis.get('music_info', {})
                if any(v for v in music_info.values() if v and v != "null"):
                    print("  音楽情報:")
                    for key, value in music_info.items():
                        if value and value != "null":
                            print(f"    {key}: {value}")
                
                # 歌詞の一部
                lyrics = analysis.get('lyrics')
                if lyrics and lyrics != "null" and len(lyrics.strip()) > 0:
                    lyrics_preview = lyrics.replace('\n', ' ')[:100]
                    print(f"  歌詞: {lyrics_preview}...")
                
                # ツール情報
                tools = analysis.get('tools', {})
                for tool_type, tool_list in tools.items():
                    if tool_list and isinstance(tool_list, list) and any(tool_list):
                        print(f"  {tool_type}: {', '.join(tool_list)}")
                
                # 信頼度
                confidence = analysis.get('confidence_score', 0)
                print(f"  信頼度: {confidence:.2f}")
            else:
                print(f"\n{i+1}. {video['title']} - 分析失敗")
        
        print(f"\n分析結果は {output_path} に保存されました")
        
    except Exception as e:
        print(f"エラーが発生しました: {e}")
    
    print("\n=== テスト完了 ===")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # コマンドライン引数でファイルパスを指定
        playlist_file_path = sys.argv[1]
        max_videos = int(sys.argv[2]) if len(sys.argv) > 2 else 3
        analyze_playlist_from_file(playlist_file_path, max_videos)
    else:
        # デフォルトのプレイリストファイルで実行
        default_playlist = "/mnt/d/setsuna_bot/youtube_knowledge_system/data/playlists/playlist_PL4R2l8ETuvxueMZJo63H8ykV_OY0LuzfX.json"
        analyze_playlist_from_file(default_playlist, 3)
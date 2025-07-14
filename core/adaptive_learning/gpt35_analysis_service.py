#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GPT35AnalysisService - GPT-3.5-turboを使用した分析サービス
コスト最適化された検索方向分析と結果解析システム
"""

from openai import OpenAI
import json
import os
import sys
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from pathlib import Path

# プロジェクトルートを確実にパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from core.adaptive_learning.accurate_cost_calculator import AccurateCostCalculator
except ImportError:
    try:
        from .accurate_cost_calculator import AccurateCostCalculator
    except ImportError:
        from accurate_cost_calculator import AccurateCostCalculator

class GPT35AnalysisService:
    """GPT-3.5-turbo分析サービス"""
    
    def __init__(self):
        """初期化"""
        # .envファイル読み込み（python-dotenvライブラリを優先使用）
        try:
            from dotenv import load_dotenv
            env_path = Path(__file__).parent.parent.parent / ".env"
            load_dotenv(env_path)
        except ImportError:
            # python-dotenvが利用できない場合は手動読み込み
            env_path = Path(__file__).parent.parent.parent / ".env"
            if env_path.exists():
                try:
                    with open(env_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            if line.startswith('OPENAI_API_KEY='):
                                os.environ['OPENAI_API_KEY'] = line.split('=', 1)[1].strip()
                except UnicodeDecodeError:
                    # Windows環境でcp932エラーが発生した場合の対処
                    try:
                        with open(env_path, 'r', encoding='cp932') as f:
                            for line in f:
                                if line.startswith('OPENAI_API_KEY='):
                                    os.environ['OPENAI_API_KEY'] = line.split('=', 1)[1].strip()
                    except UnicodeDecodeError:
                        # 最後の手段: latin-1で読み込み
                        with open(env_path, 'r', encoding='latin-1') as f:
                            for line in f:
                                if line.startswith('OPENAI_API_KEY='):
                                    os.environ['OPENAI_API_KEY'] = line.split('=', 1)[1].strip()
                except Exception as e:
                    print(f"⚠️ .envファイル読み込みエラー: {e}")
                    print("環境変数OPENAI_API_KEYを直接設定してください")
        
        # OpenAI API設定
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY環境変数が設定されていません")
        
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-3.5-turbo"
        self.cost_calculator = AccurateCostCalculator()
        self.analysis_history = []
        
    def analyze_search_direction(self, user_prompt: str) -> Dict:
        """ユーザープロンプトから検索方向を分析"""
        
        system_prompt = """あなたは情報探索の専門アナリストです。
ユーザーのプロンプトを分析し、効果的な検索方向を提案してください。

以下の形式で回答してください:
1. 主要キーワード: [3-5個の重要キーワード]
2. 検索方向: [3つの具体的な検索方向]
3. 探索戦略: [効果的なアプローチ方法]

簡潔で実用的な提案をお願いします。"""

        user_message = f"""
プロンプト: {user_prompt}

このプロンプトに基づいて、DuckDuckGo検索で効果的な情報収集を行うための検索方向を分析してください。
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            analysis_result = response.choices[0].message.content.strip()
            
            # コスト計算
            cost = self.cost_calculator.calculate_gpt_cost(
                input_text=system_prompt + user_message,
                output_text=analysis_result
            )
            
            # 履歴記録
            analysis_record = {
                "timestamp": datetime.now().isoformat(),
                "type": "search_direction_analysis",
                "user_prompt": user_prompt,
                "analysis_result": analysis_result,
                "cost": cost,
                "tokens": {
                    "input": len(self.cost_calculator.tokenizer.encode(system_prompt + user_message)),
                    "output": len(self.cost_calculator.tokenizer.encode(analysis_result))
                }
            }
            self.analysis_history.append(analysis_record)
            
            return {
                "analysis": analysis_result,
                "cost": cost,
                "search_queries": self._extract_search_queries(analysis_result),
                "metadata": analysis_record
            }
            
        except Exception as e:
            print(f"❌ GPT-3.5分析エラー: {e}")
            return self._generate_fallback_analysis(user_prompt)
    
    def analyze_search_results(self, search_results: List[Dict], original_prompt: str) -> Dict:
        """検索結果を分析して要約・次の方向性を提示"""
        
        # 検索結果をテキスト形式に整理
        results_text = ""
        for i, result in enumerate(search_results, 1):
            results_text += f"{i}. {result['title']}\n   {result['snippet']}\n   出典: {result['source']}\n\n"
        
        system_prompt = """あなたは情報分析の専門家です。
検索結果を分析し、以下の形式で回答してください:

1. 主要な発見: [重要なポイント2-3個]
2. トレンド分析: [現在の動向]
3. 次の探索方向: [3つの具体的な提案]

実用的で具体的な分析をお願いします。"""

        user_message = f"""
元のプロンプト: {original_prompt}

検索結果:
{results_text}

これらの検索結果を分析し、主要な発見をまとめ、さらに深掘りすべき方向性を提案してください。
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=400,
                temperature=0.7
            )
            
            analysis_result = response.choices[0].message.content.strip()
            
            # コスト計算
            cost = self.cost_calculator.calculate_gpt_cost(
                input_text=system_prompt + user_message,
                output_text=analysis_result
            )
            
            # 履歴記録
            analysis_record = {
                "timestamp": datetime.now().isoformat(),
                "type": "search_results_analysis",
                "original_prompt": original_prompt,
                "results_count": len(search_results),
                "analysis_result": analysis_result,
                "cost": cost
            }
            self.analysis_history.append(analysis_record)
            
            return {
                "analysis": analysis_result,
                "cost": cost,
                "next_directions": self._extract_next_directions(analysis_result),
                "metadata": analysis_record
            }
            
        except Exception as e:
            print(f"❌ GPT-3.5結果分析エラー: {e}")
            return self._generate_fallback_results_analysis(search_results, original_prompt)
    
    def generate_next_exploration_options(self, current_analysis: str, user_feedback: str = "") -> Dict:
        """次の探索選択肢を生成"""
        
        system_prompt = """あなたは探索戦略の専門家です。
現在の分析結果を基に、次の探索ステップの選択肢を3つ提案してください。

各選択肢には以下を含めてください:
- 探索方向の説明
- 期待される発見
- 具体的な検索キーワード"""

        user_message = f"""
現在の分析結果:
{current_analysis}

ユーザーフィードバック: {user_feedback}

次の探索ステップとして、3つの異なる方向性を提案してください。
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=350,
                temperature=0.8
            )
            
            options_result = response.choices[0].message.content.strip()
            
            # コスト計算
            cost = self.cost_calculator.calculate_gpt_cost(
                input_text=system_prompt + user_message,
                output_text=options_result
            )
            
            # 履歴記録
            analysis_record = {
                "timestamp": datetime.now().isoformat(),
                "type": "next_exploration_options",
                "current_analysis": current_analysis,
                "user_feedback": user_feedback,
                "options_result": options_result,
                "cost": cost
            }
            self.analysis_history.append(analysis_record)
            
            return {
                "options": options_result,
                "cost": cost,
                "parsed_options": self._parse_exploration_options(options_result),
                "metadata": analysis_record
            }
            
        except Exception as e:
            print(f"❌ GPT-3.5選択肢生成エラー: {e}")
            return self._generate_fallback_options(current_analysis)
    
    def _extract_search_queries(self, analysis_text: str) -> List[str]:
        """分析結果から検索クエリを抽出"""
        queries = []
        lines = analysis_text.split('\n')
        
        for line in lines:
            if '検索方向' in line or 'キーワード' in line:
                # 簡単なパターンマッチングで検索語を抽出
                if ':' in line:
                    query_part = line.split(':', 1)[1].strip()
                    if query_part and len(query_part) > 3:
                        queries.append(query_part)
        
        # 基本的なフォールバック
        if not queries:
            queries = ["技術動向", "実装事例", "ベストプラクティス"]
        
        return queries[:3]
    
    def _extract_next_directions(self, analysis_text: str) -> List[str]:
        """分析結果から次の方向性を抽出"""
        directions = []
        lines = analysis_text.split('\n')
        
        for line in lines:
            if '次の' in line or '方向' in line or '提案' in line:
                if ':' in line:
                    direction = line.split(':', 1)[1].strip()
                    if direction and len(direction) > 5:
                        directions.append(direction)
        
        if not directions:
            directions = ["詳細調査", "関連分野展開", "実践応用"]
        
        return directions[:3]
    
    def _parse_exploration_options(self, options_text: str) -> List[Dict]:
        """探索選択肢をパース"""
        options = []
        current_option = {}
        
        lines = options_text.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith(('1.', '2.', '3.', '●', '・')):
                if current_option:
                    options.append(current_option)
                current_option = {"title": line, "description": "", "keywords": []}
            elif line and current_option:
                if '期待' in line or '発見' in line:
                    current_option["expected"] = line
                elif 'キーワード' in line:
                    current_option["keywords"] = line.split(':')[-1].strip().split(',')
                else:
                    current_option["description"] += line + " "
        
        if current_option:
            options.append(current_option)
        
        return options
    
    def _generate_fallback_analysis(self, user_prompt: str) -> Dict:
        """フォールバック分析（API失敗時）"""
        return {
            "analysis": f"{user_prompt}に関する基本的な検索方向を提案します。主要キーワード、実装事例、最新動向の3つの軸で情報収集を行うことをお勧めします。",
            "cost": 0.0,
            "search_queries": [f"{user_prompt} 基本", f"{user_prompt} 事例", f"{user_prompt} 動向"],
            "metadata": {"fallback": True, "timestamp": datetime.now().isoformat()}
        }
    
    def _generate_fallback_results_analysis(self, search_results: List[Dict], original_prompt: str) -> Dict:
        """フォールバック結果分析"""
        return {
            "analysis": f"{len(search_results)}件の検索結果から、{original_prompt}に関する情報を確認しました。詳細な技術情報、実装パターン、最新動向について追加調査をお勧めします。",
            "cost": 0.0,
            "next_directions": ["技術詳細", "実装方法", "応用事例"],
            "metadata": {"fallback": True, "timestamp": datetime.now().isoformat()}
        }
    
    def _generate_fallback_options(self, current_analysis: str) -> Dict:
        """フォールバック選択肢生成"""
        return {
            "options": "1. より深い技術詳細の調査\n2. 関連技術領域への展開\n3. 実践的な応用方法の探索",
            "cost": 0.0,
            "parsed_options": [
                {"title": "技術詳細調査", "description": "詳細な技術仕様と実装方法"},
                {"title": "関連技術展開", "description": "関連する技術分野への展開"},
                {"title": "実践応用", "description": "実際のプロジェクトでの応用方法"}
            ],
            "metadata": {"fallback": True, "timestamp": datetime.now().isoformat()}
        }
    
    def get_total_cost(self) -> float:
        """総コスト取得"""
        return sum(record["cost"] for record in self.analysis_history)
    
    def get_analysis_summary(self) -> Dict:
        """分析履歴の要約"""
        if not self.analysis_history:
            return {"total_analyses": 0, "total_cost": 0.0}
        
        total_cost = self.get_total_cost()
        total_analyses = len(self.analysis_history)
        avg_cost = total_cost / total_analyses if total_analyses > 0 else 0
        
        return {
            "total_analyses": total_analyses,
            "total_cost": total_cost,
            "average_cost_per_analysis": avg_cost,
            "recent_analyses": self.analysis_history[-3:] if len(self.analysis_history) >= 3 else self.analysis_history
        }
    
    def save_analysis_history(self, filepath: str):
        """分析履歴をファイルに保存"""
        history_data = {
            "analysis_history": self.analysis_history,
            "summary": self.get_analysis_summary(),
            "cost_calculator_summary": self.cost_calculator.get_cost_summary(),
            "saved_at": datetime.now().isoformat()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(history_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    try:
        service = GPT35AnalysisService()
        
        print("🤖 GPT-3.5分析サービス - テスト実行")
        
        # テストプロンプト
        test_prompt = "AI技術の最新動向について詳しく調べたい"
        
        print(f"\n📝 テストプロンプト: '{test_prompt}'")
        
        # 検索方向分析
        direction_analysis = service.analyze_search_direction(test_prompt)
        print(f"✅ 方向分析完了 (コスト: ${direction_analysis['cost']:.6f})")
        print(f"提案された検索クエリ: {direction_analysis['search_queries']}")
        
        # モック検索結果での結果分析テスト
        mock_results = [
            {"title": "AI技術最新動向", "snippet": "2025年のAI技術進展", "source": "Tech News"},
            {"title": "GPT-4活用事例", "snippet": "企業でのGPT-4導入例", "source": "Business AI"}
        ]
        
        results_analysis = service.analyze_search_results(mock_results, test_prompt)
        print(f"✅ 結果分析完了 (コスト: ${results_analysis['cost']:.6f})")
        
        # 次の選択肢生成
        options = service.generate_next_exploration_options(results_analysis['analysis'])
        print(f"✅ 選択肢生成完了 (コスト: ${options['cost']:.6f})")
        
        # 総コスト表示
        total_cost = service.get_total_cost()
        print(f"\n💰 総コスト: ${total_cost:.6f}")
        
        # 結果保存
        output_path = Path("D:/setsuna_bot/data/adaptive_learning/gpt35_analysis_test.json")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        service.save_analysis_history(str(output_path))
        print(f"💾 テスト結果保存: {output_path}")
        
    except Exception as e:
        print(f"❌ テスト実行エラー: {e}")
        print("注意: OpenAI API キーが正しく設定されていることを確認してください")
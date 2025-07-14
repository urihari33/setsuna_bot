#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AccurateCostCalculator - 正確なコスト評価システム
実際のGPT-3.5-turbo料金に基づく正確なコスト計算
"""

import json
import tiktoken
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from pathlib import Path

class AccurateCostCalculator:
    """正確なコスト計算システム"""
    
    # GPT-3.5-turbo実際の料金 (2025年1月時点)
    GPT_35_TURBO_INPUT_COST = 0.0015  # $0.0015 per 1K input tokens
    GPT_35_TURBO_OUTPUT_COST = 0.002  # $0.002 per 1K output tokens
    
    # DuckDuckGo検索は無料
    DUCKDUCKGO_COST = 0.0
    
    def __init__(self):
        """初期化"""
        self.tokenizer = tiktoken.encoding_for_model("gpt-3.5-turbo")
        self.cost_history = []
        
    def calculate_gpt_cost(self, input_text: str, output_text: str) -> float:
        """GPT-3.5-turboのコスト計算"""
        input_tokens = len(self.tokenizer.encode(input_text))
        output_tokens = len(self.tokenizer.encode(output_text))
        
        input_cost = (input_tokens / 1000) * self.GPT_35_TURBO_INPUT_COST
        output_cost = (output_tokens / 1000) * self.GPT_35_TURBO_OUTPUT_COST
        
        total_cost = input_cost + output_cost
        
        # ログ記録
        self.cost_history.append({
            "timestamp": datetime.now().isoformat(),
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "input_cost": input_cost,
            "output_cost": output_cost,
            "total_cost": total_cost
        })
        
        return total_cost
    
    def estimate_exploration_cycle_cost(self, prompt: str, estimated_search_results: int = 5) -> Dict:
        """探索サイクル1回のコスト見積もり"""
        
        # 1. 検索方向分析用プロンプト
        search_analysis_prompt = f"""
        ユーザーのプロンプト: {prompt}
        
        このプロンプトに基づいて効果的な検索方向を3-5個提案してください。
        各検索方向には具体的なキーワードと検索意図を含めてください。
        """
        search_analysis_response = "検索方向1: [具体的キーワード] - 検索意図説明\n検索方向2: [具体的キーワード] - 検索意図説明\n検索方向3: [具体的キーワード] - 検索意図説明"
        
        # 2. 検索結果分析用プロンプト（検索結果5件分を想定）
        sample_search_results = "検索結果1: タイトル + 要約\n検索結果2: タイトル + 要約\n検索結果3: タイトル + 要約\n検索結果4: タイトル + 要約\n検索結果5: タイトル + 要約"
        results_analysis_prompt = f"""
        検索結果:
        {sample_search_results}
        
        これらの検索結果を分析し、以下の観点でまとめてください:
        1. 主要な発見・トレンド
        2. 重要な情報の要約
        3. さらに深掘りすべき方向性
        4. 次の探索に向けた提案
        """
        results_analysis_response = "分析結果: 主要トレンド説明 + 重要情報要約 + 次の探索方向提案 (約300-500文字)"
        
        # 3. 次の探索方向提示用プロンプト
        next_direction_prompt = f"""
        現在の探索結果: {results_analysis_response}
        
        次の探索ステップとして以下の選択肢を提示してください:
        1. より深く掘り下げる方向性
        2. 関連分野への展開方向性
        3. 実践的応用への方向性
        """
        next_direction_response = "次の探索選択肢: 3つの具体的な方向性提案 (各100-150文字)"
        
        # コスト計算
        search_analysis_cost = self.calculate_gpt_cost(search_analysis_prompt, search_analysis_response)
        results_analysis_cost = self.calculate_gpt_cost(results_analysis_prompt, results_analysis_response)
        next_direction_cost = self.calculate_gpt_cost(next_direction_prompt, next_direction_response)
        
        total_cycle_cost = search_analysis_cost + results_analysis_cost + next_direction_cost
        
        return {
            "search_analysis_cost": search_analysis_cost,
            "results_analysis_cost": results_analysis_cost,
            "next_direction_cost": next_direction_cost,
            "duckduckgo_cost": self.DUCKDUCKGO_COST,
            "total_cycle_cost": total_cycle_cost,
            "estimated_tokens": {
                "total_input": len(self.tokenizer.encode(search_analysis_prompt + results_analysis_prompt + next_direction_prompt)),
                "total_output": len(self.tokenizer.encode(search_analysis_response + results_analysis_response + next_direction_response))
            }
        }
    
    def calculate_budget_cycles(self, budget: float, prompt: str) -> Dict:
        """予算内で実行可能なサイクル数計算"""
        cycle_cost = self.estimate_exploration_cycle_cost(prompt)
        cost_per_cycle = cycle_cost["total_cycle_cost"]
        
        max_cycles = int(budget / cost_per_cycle)
        estimated_total_cost = max_cycles * cost_per_cycle
        remaining_budget = budget - estimated_total_cost
        
        return {
            "budget": budget,
            "cost_per_cycle": cost_per_cycle,
            "max_cycles": max_cycles,
            "estimated_total_cost": estimated_total_cost,
            "remaining_budget": remaining_budget,
            "cost_breakdown": cycle_cost
        }
    
    def simulate_realistic_costs(self) -> Dict:
        """現実的なコスト例のシミュレーション"""
        
        # 典型的なプロンプト例
        sample_prompts = [
            "AI技術の最新動向について詳しく調べたい",
            "Web開発における新しいフレームワークの比較検討をしたい",
            "機械学習の実践的な応用事例を探したい"
        ]
        
        simulation_results = {}
        
        for i, prompt in enumerate(sample_prompts):
            prompt_key = f"sample_prompt_{i+1}"
            
            # $1予算での計算
            budget_1_dollar = self.calculate_budget_cycles(1.0, prompt)
            
            # $5予算での計算
            budget_5_dollar = self.calculate_budget_cycles(5.0, prompt)
            
            simulation_results[prompt_key] = {
                "prompt": prompt,
                "budget_1_dollar": budget_1_dollar,
                "budget_5_dollar": budget_5_dollar
            }
        
        return simulation_results
    
    def get_cost_summary(self) -> Dict:
        """コスト履歴の要約"""
        if not self.cost_history:
            return {"total_cost": 0, "total_calls": 0}
        
        total_cost = sum(entry["total_cost"] for entry in self.cost_history)
        total_calls = len(self.cost_history)
        avg_cost = total_cost / total_calls if total_calls > 0 else 0
        
        return {
            "total_cost": total_cost,
            "total_calls": total_calls,
            "average_cost_per_call": avg_cost,
            "latest_entries": self.cost_history[-5:] if len(self.cost_history) >= 5 else self.cost_history
        }
    
    def save_cost_analysis(self, filepath: str):
        """コスト分析結果をファイルに保存"""
        analysis_data = {
            "calculator_info": {
                "gpt_35_turbo_input_cost": self.GPT_35_TURBO_INPUT_COST,
                "gpt_35_turbo_output_cost": self.GPT_35_TURBO_OUTPUT_COST,
                "duckduckgo_cost": self.DUCKDUCKGO_COST
            },
            "simulation_results": self.simulate_realistic_costs(),
            "cost_history_summary": self.get_cost_summary(),
            "generated_at": datetime.now().isoformat()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    calculator = AccurateCostCalculator()
    
    print("🧮 正確なコスト評価システム - テスト実行")
    
    # シミュレーション実行
    simulation = calculator.simulate_realistic_costs()
    
    print("\n📊 コストシミュレーション結果:")
    for key, data in simulation.items():
        print(f"\n{key}:")
        print(f"  プロンプト: {data['prompt']}")
        print(f"  $1予算: {data['budget_1_dollar']['max_cycles']}サイクル (1サイクル ${data['budget_1_dollar']['cost_per_cycle']:.6f})")
        print(f"  $5予算: {data['budget_5_dollar']['max_cycles']}サイクル")
    
    # 結果保存
    output_path = Path("D:/setsuna_bot/data/adaptive_learning/cost_analysis_realistic.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    calculator.save_cost_analysis(str(output_path))
    
    print(f"\n💾 分析結果保存: {output_path}")
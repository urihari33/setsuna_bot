#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ActivityProposalEngine - Phase 2B-1
学習知識を活動提案に変換するエンジン
"""

import json
import os
import openai
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import uuid
import hashlib
from collections import defaultdict
from .config_manager import get_config_manager

# Windows環境のパス設定
if os.name == 'nt':
    DATA_DIR = Path("D:/setsuna_bot/data/activity_knowledge/activity_proposals")
else:
    DATA_DIR = Path("/mnt/d/setsuna_bot/data/activity_knowledge/activity_proposals")

@dataclass
class ActivityProposal:
    """活動提案データクラス"""
    proposal_id: str
    generated_from: str  # セッションID
    proposal_type: str   # "content_creation", "tool_development", "collaboration", "market_research"
    title: str
    description: str
    generated_at: datetime
    
    # 知識基盤
    source_sessions: List[str]
    key_knowledge: List[str]
    market_opportunity: str
    technical_feasibility: float  # 0.0-1.0
    
    # 提案詳細
    target_audience: str
    difficulty_level: str  # "easy", "medium", "hard"
    required_resources: List[str]
    estimated_duration: str
    expected_impact: Dict[str, float]  # audience_growth, expertise_demonstration, community_value
    
    # 実装計画
    implementation_plan: Dict[str, str]  # phase -> description
    
    # ステータス
    status: str = "pending"  # "pending", "accepted", "rejected", "in_progress", "completed"
    user_feedback: Optional[str] = None
    acceptance_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    
    # せつな特性適合度
    setsuna_alignment: Dict[str, float] = None  # personality_fit, skill_match, interest_level
    
    def __post_init__(self):
        if self.setsuna_alignment is None:
            self.setsuna_alignment = {
                "personality_fit": 0.7,
                "skill_match": 0.6,
                "interest_level": 0.8
            }

@dataclass
class ProposalTemplate:
    """提案テンプレートデータクラス"""
    template_id: str
    template_type: str
    title_pattern: str
    description_pattern: str
    required_knowledge_types: List[str]
    setsuna_characteristics: Dict[str, Any]
    success_criteria: List[str]

class ActivityProposalEngine:
    """活動提案エンジンメインクラス"""
    
    def __init__(self):
        """初期化"""
        self.proposals_dir = DATA_DIR
        self.proposals_dir.mkdir(parents=True, exist_ok=True)
        
        # OpenAI設定
        self.openai_client = None
        self._initialize_openai()
        
        # GPT設定
        self.gpt_config = {
            "model": "gpt-4-turbo-preview",
            "temperature": 0.7,  # 創造性重視
            "max_tokens": 1500
        }
        
        # せつなの特性・嗜好データ
        self.setsuna_profile = {
            "personality": {
                "thoughtful": 0.9,      # 思慮深い
                "gentle": 0.8,          # 優しい
                "creative": 0.7,        # 創造的
                "analytical": 0.8,      # 分析的
                "collaborative": 0.6,   # 協調的
                "perfectionist": 0.7    # 完璧主義
            },
            "skills": {
                "technology_explanation": 0.9,  # 技術解説
                "content_creation": 0.8,        # コンテンツ制作
                "research_analysis": 0.9,       # 調査分析
                "community_interaction": 0.6,   # コミュニティ交流
                "tool_development": 0.5,        # ツール開発
                "presentation": 0.7             # プレゼンテーション
            },
            "interests": {
                "ai_technology": 0.9,           # AI技術
                "music_generation": 0.8,        # 音楽生成
                "creative_tools": 0.8,          # 創作ツール
                "technical_trends": 0.9,        # 技術動向
                "educational_content": 0.8,     # 教育コンテンツ
                "innovation": 0.9               # イノベーション
            },
            "constraints": {
                "time_availability": "moderate",     # 時間的制約
                "technical_complexity": "high",      # 技術的複雑さへの対応
                "social_interaction": "selective",   # 社会的交流の選択性
                "risk_tolerance": "low"              # リスク許容度
            }
        }
        
        # 提案テンプレート
        self.proposal_templates = self._initialize_templates()
        
        # 既存提案
        self.proposals: Dict[str, ActivityProposal] = {}
        self._load_existing_proposals()
        
        # 統計
        self.stats = {
            "total_generated": 0,
            "by_type": defaultdict(int),
            "acceptance_rate": 0.0,
            "completion_rate": 0.0
        }
        
        print("[提案エンジン] ✅ ActivityProposalEngine初期化完了")
    
    def _initialize_openai(self):
        """OpenAI API初期化"""
        try:
            # ConfigManager経由でOpenAI設定取得
            config = get_config_manager()
            openai_key = config.get_openai_key()
            
            if openai_key:
                openai.api_key = openai_key
                self.openai_client = openai
                
                # 接続テスト実行
                try:
                    # 簡単な接続テスト
                    test_response = openai.models.list()
                    if test_response:
                        print("[提案エンジン] ✅ OpenAI API設定・接続確認完了")
                        return True
                except Exception as api_error:
                    print(f"[提案エンジン] ❌ OpenAI API接続失敗: {api_error}")
                    self.openai_client = None
                    return False
            else:
                print("[提案エンジン] ⚠️ OpenAI APIキーが設定されていません")
                print("  .envファイルまたは環境変数 OPENAI_API_KEY を設定してください")
                self.openai_client = None
                return False
                
        except Exception as e:
            print(f"[提案エンジン] ❌ OpenAI API初期化失敗: {e}")
            self.openai_client = None
            return False
    
    def _initialize_templates(self) -> List[ProposalTemplate]:
        """提案テンプレート初期化"""
        templates = [
            ProposalTemplate(
                template_id="content_tech_explanation",
                template_type="content_creation",
                title_pattern="{technology}技術解説コンテンツ制作",
                description_pattern="{technology}について詳しく解説する{format}を制作し、技術的な理解を深めてもらう",
                required_knowledge_types=["技術", "実用"],
                setsuna_characteristics={
                    "personality_fit": 0.9,  # 解説が得意
                    "skill_match": 0.9,      # 技術説明スキル
                    "interest_level": 0.8    # 技術への関心
                },
                success_criteria=["技術理解の向上", "視聴者の満足度", "専門性の認知"]
            ),
            ProposalTemplate(
                template_id="tool_comparison",
                template_type="content_creation", 
                title_pattern="{category}ツール比較・検証企画",
                description_pattern="複数の{category}ツールを実際に使用して比較検証し、特徴・使い分けを分析",
                required_knowledge_types=["市場", "実用"],
                setsuna_characteristics={
                    "personality_fit": 0.8,   # 分析的思考
                    "skill_match": 0.8,       # 比較分析
                    "interest_level": 0.7     # ツールへの関心
                },
                success_criteria=["客観的比較", "実用的価値", "決定支援"]
            ),
            ProposalTemplate(
                template_id="trend_analysis",
                template_type="market_research",
                title_pattern="{field}分野の技術動向分析",
                description_pattern="{field}分野の最新技術動向を調査・分析し、将来性を考察",
                required_knowledge_types=["技術", "市場", "トレンド"],
                setsuna_characteristics={
                    "personality_fit": 0.9,   # 分析好き
                    "skill_match": 0.9,       # 調査分析
                    "interest_level": 0.9     # 技術動向
                },
                success_criteria=["洞察の深さ", "予測精度", "価値ある情報提供"]
            ),
            ProposalTemplate(
                template_id="collaborative_project",
                template_type="collaboration",
                title_pattern="{topic}に関する共同研究・検証プロジェクト",
                description_pattern="専門家や他のクリエイターと協力して{topic}を深く探求するプロジェクト",
                required_knowledge_types=["技術", "実用"],
                setsuna_characteristics={
                    "personality_fit": 0.6,   # 協調性は中程度
                    "skill_match": 0.7,       # 専門知識
                    "interest_level": 0.8     # 深い探求
                },
                success_criteria=["知識の深化", "ネットワーク構築", "相互学習"]
            ),
            ProposalTemplate(
                template_id="educational_series",
                template_type="content_creation",
                title_pattern="{subject}学習シリーズ企画",
                description_pattern="{subject}を体系的に学べる段階的な学習コンテンツシリーズ",
                required_knowledge_types=["技術", "実用"],
                setsuna_characteristics={
                    "personality_fit": 0.8,   # 教育的思考
                    "skill_match": 0.8,       # 説明能力
                    "interest_level": 0.8     # 教育的価値
                },
                success_criteria=["学習効果", "継続視聴", "スキル向上支援"]
            )
        ]
        return templates
    
    def _load_existing_proposals(self):
        """既存提案の読み込み"""
        try:
            for proposals_file in self.proposals_dir.glob("proposals_*.json"):
                with open(proposals_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for proposal_data in data.get("generated_proposals", []):
                        proposal = ActivityProposal(
                            proposal_id=proposal_data["proposal_id"],
                            generated_from=proposal_data["generated_from"],
                            proposal_type=proposal_data["proposal_type"],
                            title=proposal_data["title"],
                            description=proposal_data["description"],
                            generated_at=datetime.fromisoformat(proposal_data["generated_at"]),
                            source_sessions=proposal_data.get("source_sessions", []),
                            key_knowledge=proposal_data.get("key_knowledge", []),
                            market_opportunity=proposal_data.get("market_opportunity", ""),
                            technical_feasibility=proposal_data.get("technical_feasibility", 0.7),
                            target_audience=proposal_data.get("target_audience", ""),
                            difficulty_level=proposal_data.get("difficulty_level", "medium"),
                            required_resources=proposal_data.get("required_resources", []),
                            estimated_duration=proposal_data.get("estimated_duration", ""),
                            expected_impact=proposal_data.get("expected_impact", {}),
                            implementation_plan=proposal_data.get("implementation_plan", {}),
                            status=proposal_data.get("status", "pending"),
                            user_feedback=proposal_data.get("user_feedback"),
                            acceptance_date=datetime.fromisoformat(proposal_data["acceptance_date"]) if proposal_data.get("acceptance_date") else None,
                            completion_date=datetime.fromisoformat(proposal_data["completion_date"]) if proposal_data.get("completion_date") else None,
                            setsuna_alignment=proposal_data.get("setsuna_alignment", {})
                        )
                        self.proposals[proposal.proposal_id] = proposal
            
            print(f"[提案エンジン] 📚 既存提案読み込み: {len(self.proposals)}件")
            
        except Exception as e:
            print(f"[提案エンジン] ⚠️ 既存提案読み込み失敗: {e}")
    
    def generate_proposals_from_session(self, 
                                      session_id: str,
                                      session_knowledge: Dict[str, Any],
                                      max_proposals: int = 3) -> List[ActivityProposal]:
        """
        セッション知識から活動提案生成
        
        Args:
            session_id: セッションID
            session_knowledge: セッション知識データ
            max_proposals: 最大提案数
            
        Returns:
            生成された提案リスト
        """
        try:
            print(f"[提案エンジン] 🎯 活動提案生成開始: {session_id}")
            
            # セッション知識分析
            knowledge_analysis = self._analyze_session_knowledge(session_knowledge)
            
            # 適用可能テンプレート特定
            applicable_templates = self._find_applicable_templates(knowledge_analysis)
            
            # 提案生成
            generated_proposals = []
            
            for i, template in enumerate(applicable_templates[:max_proposals]):
                proposal = self._generate_proposal_from_template(
                    template, session_id, session_knowledge, knowledge_analysis
                )
                if proposal:
                    generated_proposals.append(proposal)
                    self.proposals[proposal.proposal_id] = proposal
            
            # GPT-4による追加提案生成
            if len(generated_proposals) < max_proposals and self.openai_client:
                additional_proposals = self._generate_gpt_proposals(
                    session_knowledge, knowledge_analysis, max_proposals - len(generated_proposals)
                )
                generated_proposals.extend(additional_proposals)
            
            # 提案保存
            self._save_proposals(generated_proposals)
            
            # 統計更新
            self.stats["total_generated"] += len(generated_proposals)
            for proposal in generated_proposals:
                self.stats["by_type"][proposal.proposal_type] += 1
            
            print(f"[提案エンジン] ✅ 提案生成完了: {len(generated_proposals)}件")
            
            return generated_proposals
            
        except Exception as e:
            print(f"[提案エンジン] ❌ 提案生成失敗: {e}")
            return []
    
    def _analyze_session_knowledge(self, session_knowledge: Dict[str, Any]) -> Dict[str, Any]:
        """セッション知識分析"""
        analysis = {
            "main_topics": [],
            "technologies": [],
            "market_aspects": [],
            "practical_applications": [],
            "knowledge_depth": "basic",
            "innovation_potential": 0.5,
            "commercial_viability": 0.5
        }
        
        try:
            # 知識アイテムから分析
            knowledge_items = session_knowledge.get("knowledge_items", [])
            
            # カテゴリ別集計
            category_counts = defaultdict(int)
            all_keywords = []
            all_entities = []
            
            for item in knowledge_items:
                for category in item.get("categories", []):
                    category_counts[category] += 1
                
                all_keywords.extend(item.get("keywords", []))
                all_entities.extend(item.get("entities", []))
            
            # メイントピック抽出
            if category_counts:
                sorted_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)
                analysis["main_topics"] = [cat for cat, count in sorted_categories[:3]]
            
            # 技術・市場・実用の分類
            for category, count in category_counts.items():
                if "技術" in category or "AI" in category:
                    analysis["technologies"].append(category)
                elif "市場" in category or "トレンド" in category:
                    analysis["market_aspects"].append(category)
                elif "実用" in category or "ツール" in category:
                    analysis["practical_applications"].append(category)
            
            # 知識深度判定
            total_items = len(knowledge_items)
            if total_items >= 15:
                analysis["knowledge_depth"] = "comprehensive"
            elif total_items >= 8:
                analysis["knowledge_depth"] = "detailed"
            elif total_items >= 3:
                analysis["knowledge_depth"] = "moderate"
            
            # イノベーション・商用可能性評価
            innovation_keywords = ["最新", "新技術", "革新", "イノベーション", "breakthrough"]
            commercial_keywords = ["商用", "ビジネス", "市場", "収益", "製品"]
            
            keyword_text = " ".join(all_keywords).lower()
            analysis["innovation_potential"] = min(1.0, 
                sum(0.2 for kw in innovation_keywords if kw in keyword_text))
            analysis["commercial_viability"] = min(1.0,
                sum(0.2 for kw in commercial_keywords if kw in keyword_text))
            
        except Exception as e:
            print(f"[提案エンジン] ⚠️ 知識分析失敗: {e}")
        
        return analysis
    
    def _find_applicable_templates(self, knowledge_analysis: Dict[str, Any]) -> List[ProposalTemplate]:
        """適用可能テンプレート特定"""
        applicable_templates = []
        
        for template in self.proposal_templates:
            # 知識タイプマッチング
            knowledge_types = set()
            if knowledge_analysis["technologies"]:
                knowledge_types.add("技術")
            if knowledge_analysis["market_aspects"]:
                knowledge_types.add("市場")
            if knowledge_analysis["practical_applications"]:
                knowledge_types.add("実用")
            
            required_types = set(template.required_knowledge_types)
            if knowledge_types & required_types:  # 共通要素があれば適用可能
                applicable_templates.append(template)
        
        # せつな適合度でソート
        applicable_templates.sort(
            key=lambda t: sum(t.setsuna_characteristics.values()) / len(t.setsuna_characteristics),
            reverse=True
        )
        
        return applicable_templates
    
    def _generate_proposal_from_template(self,
                                       template: ProposalTemplate,
                                       session_id: str,
                                       session_knowledge: Dict[str, Any],
                                       knowledge_analysis: Dict[str, Any]) -> Optional[ActivityProposal]:
        """テンプレートから提案生成"""
        try:
            # 主要技術・分野特定
            main_topic = knowledge_analysis["main_topics"][0] if knowledge_analysis["main_topics"] else "AI技術"
            technologies = knowledge_analysis["technologies"]
            
            # タイトル・説明生成
            title = template.title_pattern.format(
                technology=main_topic,
                category=main_topic,
                field=main_topic,
                topic=main_topic,
                subject=main_topic
            )
            
            description = template.description_pattern.format(
                technology=main_topic,
                category=main_topic,
                field=main_topic,
                topic=main_topic,
                subject=main_topic,
                format="動画コンテンツ"
            )
            
            # せつな適合度計算
            setsuna_alignment = self._calculate_setsuna_alignment(template, knowledge_analysis)
            
            # 実装計画生成
            implementation_plan = self._generate_implementation_plan(template, knowledge_analysis)
            
            # 期待効果設定
            expected_impact = {
                "audience_growth": 0.7,
                "expertise_demonstration": 0.8,
                "community_value": 0.6
            }
            
            # テンプレートタイプに応じた調整
            if template.template_type == "content_creation":
                expected_impact["audience_growth"] = 0.8
            elif template.template_type == "market_research":
                expected_impact["expertise_demonstration"] = 0.9
            
            proposal_id = f"prop_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            
            proposal = ActivityProposal(
                proposal_id=proposal_id,
                generated_from=session_id,
                proposal_type=template.template_type,
                title=title,
                description=description,
                generated_at=datetime.now(),
                source_sessions=[session_id],
                key_knowledge=knowledge_analysis["main_topics"],
                market_opportunity=self._assess_market_opportunity(knowledge_analysis),
                technical_feasibility=self._assess_technical_feasibility(knowledge_analysis),
                target_audience=self._determine_target_audience(template, knowledge_analysis),
                difficulty_level=self._assess_difficulty_level(knowledge_analysis),
                required_resources=self._determine_required_resources(template, knowledge_analysis),
                estimated_duration=self._estimate_duration(template, knowledge_analysis),
                expected_impact=expected_impact,
                implementation_plan=implementation_plan,
                setsuna_alignment=setsuna_alignment
            )
            
            return proposal
            
        except Exception as e:
            print(f"[提案エンジン] ❌ テンプレート提案生成失敗: {e}")
            return None
    
    def _generate_gpt_proposals(self,
                              session_knowledge: Dict[str, Any],
                              knowledge_analysis: Dict[str, Any],
                              max_count: int) -> List[ActivityProposal]:
        """GPT-4による追加提案生成"""
        if not self.openai_client:
            return []
        
        try:
            # プロンプト構築
            knowledge_summary = self._build_knowledge_summary(session_knowledge, knowledge_analysis)
            setsuna_profile_text = self._build_setsuna_profile_text()
            
            prompt = f"""
以下の学習知識とせつなの特性を基に、具体的な活動提案を{max_count}件生成してください。

【学習知識】
{knowledge_summary}

【せつなの特性】
{setsuna_profile_text}

【要求】
1. せつなの特性に適合した活動提案
2. 学習知識を活用できる内容
3. 実行可能で具体的な計画
4. 視聴者・コミュニティに価値を提供

以下のJSON形式で{max_count}件の提案を出力してください：
[
  {{
    "title": "提案タイトル",
    "description": "詳細な説明",
    "type": "content_creation|tool_development|collaboration|market_research",
    "target_audience": "対象視聴者",
    "difficulty": "easy|medium|hard",
    "duration": "実行期間",
    "resources": ["必要なリソース"],
    "impact": {{"audience_growth": 0.8, "expertise_demonstration": 0.9, "community_value": 0.7}},
    "plan": {{"phase1": "計画1", "phase2": "計画2", "phase3": "計画3"}},
    "market_opportunity": "市場機会の説明",
    "technical_feasibility": 0.8
  }}
]
"""
            
            # GPT-4呼び出し
            response = self.openai_client.chat.completions.create(
                model=self.gpt_config["model"],
                messages=[{"role": "user", "content": prompt}],
                temperature=self.gpt_config["temperature"],
                max_tokens=self.gpt_config["max_tokens"]
            )
            
            # レスポンス解析
            response_text = response.choices[0].message.content.strip()
            
            # JSON抽出・解析
            proposals_data = self._extract_json_from_response(response_text)
            
            generated_proposals = []
            for proposal_data in proposals_data[:max_count]:
                proposal = self._create_proposal_from_gpt_data(
                    proposal_data, session_knowledge.get("session_id", "unknown")
                )
                if proposal:
                    generated_proposals.append(proposal)
                    self.proposals[proposal.proposal_id] = proposal
            
            return generated_proposals
            
        except Exception as e:
            print(f"[提案エンジン] ❌ GPT提案生成失敗: {e}")
            return []
    
    def _build_knowledge_summary(self, session_knowledge: Dict[str, Any], knowledge_analysis: Dict[str, Any]) -> str:
        """知識サマリー構築"""
        summary_parts = []
        
        # メイントピック
        if knowledge_analysis["main_topics"]:
            summary_parts.append(f"主要トピック: {', '.join(knowledge_analysis['main_topics'])}")
        
        # 技術要素
        if knowledge_analysis["technologies"]:
            summary_parts.append(f"技術要素: {', '.join(knowledge_analysis['technologies'])}")
        
        # 知識深度
        depth_text = {
            "basic": "基礎的",
            "moderate": "中程度",
            "detailed": "詳細",
            "comprehensive": "包括的"
        }
        summary_parts.append(f"知識深度: {depth_text.get(knowledge_analysis['knowledge_depth'], '不明')}")
        
        # 革新性・商用性
        summary_parts.append(f"イノベーション度: {knowledge_analysis['innovation_potential']:.1f}")
        summary_parts.append(f"商用可能性: {knowledge_analysis['commercial_viability']:.1f}")
        
        return "\n".join(summary_parts)
    
    def _build_setsuna_profile_text(self) -> str:
        """せつなプロファイルテキスト構築"""
        profile_parts = []
        
        # 性格特性
        personality_text = ", ".join([
            f"{trait}({score:.1f})" 
            for trait, score in self.setsuna_profile["personality"].items() 
            if score >= 0.7
        ])
        profile_parts.append(f"性格: {personality_text}")
        
        # スキル
        skills_text = ", ".join([
            f"{skill}({score:.1f})" 
            for skill, score in self.setsuna_profile["skills"].items() 
            if score >= 0.7
        ])
        profile_parts.append(f"スキル: {skills_text}")
        
        # 関心事
        interests_text = ", ".join([
            f"{interest}({score:.1f})" 
            for interest, score in self.setsuna_profile["interests"].items() 
            if score >= 0.7
        ])
        profile_parts.append(f"関心: {interests_text}")
        
        return "\n".join(profile_parts)
    
    def _extract_json_from_response(self, response_text: str) -> List[Dict]:
        """レスポンスからJSON抽出"""
        try:
            # JSONブロック抽出
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            elif "[" in response_text and "]" in response_text:
                json_start = response_text.find("[")
                json_end = response_text.rfind("]") + 1
                json_text = response_text[json_start:json_end]
            else:
                return []
            
            return json.loads(json_text)
            
        except json.JSONDecodeError as e:
            print(f"[提案エンジン] ⚠️ JSON解析失敗: {e}")
            return []
    
    def _create_proposal_from_gpt_data(self, proposal_data: Dict, session_id: str) -> Optional[ActivityProposal]:
        """GPTデータから提案作成"""
        try:
            proposal_id = f"gpt_prop_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            
            # せつな適合度計算（データに基づく）
            setsuna_alignment = self._calculate_gpt_setsuna_alignment(proposal_data)
            
            proposal = ActivityProposal(
                proposal_id=proposal_id,
                generated_from=session_id,
                proposal_type=proposal_data.get("type", "content_creation"),
                title=proposal_data.get("title", ""),
                description=proposal_data.get("description", ""),
                generated_at=datetime.now(),
                source_sessions=[session_id],
                key_knowledge=proposal_data.get("key_knowledge", []),
                market_opportunity=proposal_data.get("market_opportunity", ""),
                technical_feasibility=float(proposal_data.get("technical_feasibility", 0.7)),
                target_audience=proposal_data.get("target_audience", ""),
                difficulty_level=proposal_data.get("difficulty", "medium"),
                required_resources=proposal_data.get("resources", []),
                estimated_duration=proposal_data.get("duration", ""),
                expected_impact=proposal_data.get("impact", {}),
                implementation_plan=proposal_data.get("plan", {}),
                setsuna_alignment=setsuna_alignment
            )
            
            return proposal
            
        except Exception as e:
            print(f"[提案エンジン] ❌ GPT提案作成失敗: {e}")
            return None
    
    def _calculate_setsuna_alignment(self, template: ProposalTemplate, knowledge_analysis: Dict) -> Dict[str, float]:
        """せつな適合度計算"""
        return template.setsuna_characteristics.copy()
    
    def _calculate_gpt_setsuna_alignment(self, proposal_data: Dict) -> Dict[str, float]:
        """GPT提案のせつな適合度計算"""
        # 提案タイプに基づく基本適合度
        type_alignment = {
            "content_creation": {"personality_fit": 0.8, "skill_match": 0.8, "interest_level": 0.7},
            "market_research": {"personality_fit": 0.9, "skill_match": 0.9, "interest_level": 0.8},
            "tool_development": {"personality_fit": 0.6, "skill_match": 0.5, "interest_level": 0.6},
            "collaboration": {"personality_fit": 0.6, "skill_match": 0.7, "interest_level": 0.7}
        }
        
        proposal_type = proposal_data.get("type", "content_creation")
        return type_alignment.get(proposal_type, {"personality_fit": 0.7, "skill_match": 0.6, "interest_level": 0.7})
    
    def _generate_implementation_plan(self, template: ProposalTemplate, knowledge_analysis: Dict) -> Dict[str, str]:
        """実装計画生成"""
        if template.template_type == "content_creation":
            return {
                "phase1": "企画・構成設計（1-2日）",
                "phase2": "コンテンツ制作・収録（2-3日）",
                "phase3": "編集・最終調整（1-2日）",
                "phase4": "公開・フィードバック収集（1日）"
            }
        elif template.template_type == "market_research":
            return {
                "phase1": "調査設計・情報収集（2-3日）",
                "phase2": "データ分析・考察（2-3日）",
                "phase3": "レポート作成（1-2日）",
                "phase4": "結果共有・議論（1日）"
            }
        else:
            return {
                "phase1": "準備・計画（1-2日）",
                "phase2": "実行・開発（3-5日）",
                "phase3": "検証・改善（1-2日）",
                "phase4": "完成・公開（1日）"
            }
    
    def _assess_market_opportunity(self, knowledge_analysis: Dict) -> str:
        """市場機会評価"""
        if knowledge_analysis["commercial_viability"] > 0.7:
            return "高い市場ニーズと商用可能性"
        elif knowledge_analysis["innovation_potential"] > 0.7:
            return "革新的技術による新市場創出機会"
        elif knowledge_analysis["market_aspects"]:
            return "既存市場での活用機会"
        else:
            return "ニッチ市場での専門性発揮"
    
    def get_proposal_statistics(self) -> Dict[str, Any]:
        """提案統計情報取得"""
        try:
            total_proposals = len(self.proposals)
            accepted_proposals = sum(1 for p in self.proposals.values() if p.status == "accepted")
            completed_proposals = sum(1 for p in self.proposals.values() if p.status == "completed")
            
            # タイプ別統計
            type_stats = {}
            for proposal in self.proposals.values():
                ptype = proposal.proposal_type
                if ptype not in type_stats:
                    type_stats[ptype] = 0
                type_stats[ptype] += 1
            
            # 平均適合度
            avg_personality_fit = 0.0
            avg_skill_match = 0.0
            avg_interest_level = 0.0
            
            if total_proposals > 0:
                avg_personality_fit = sum(p.setsuna_alignment["personality_fit"] for p in self.proposals.values()) / total_proposals
                avg_skill_match = sum(p.setsuna_alignment["skill_match"] for p in self.proposals.values()) / total_proposals
                avg_interest_level = sum(p.setsuna_alignment["interest_level"] for p in self.proposals.values()) / total_proposals
            
            return {
                "total_proposals": total_proposals,
                "accepted_proposals": accepted_proposals,
                "completed_proposals": completed_proposals,
                "acceptance_rate": (accepted_proposals / total_proposals * 100) if total_proposals > 0 else 0,
                "completion_rate": (completed_proposals / total_proposals * 100) if total_proposals > 0 else 0,
                "type_distribution": type_stats,
                "average_alignment": {
                    "personality_fit": avg_personality_fit,
                    "skill_match": avg_skill_match,
                    "interest_level": avg_interest_level
                }
            }
            
        except Exception as e:
            print(f"[提案エンジン] ❌ 統計情報取得失敗: {e}")
            return {"error": str(e)}
            return "既存市場での差別化機会"
        else:
            return "ニッチ市場での専門性発揮機会"
    
    def _assess_technical_feasibility(self, knowledge_analysis: Dict) -> float:
        """技術的実現可能性評価"""
        depth_scores = {
            "basic": 0.9,
            "moderate": 0.8,
            "detailed": 0.7,
            "comprehensive": 0.6
        }
        return depth_scores.get(knowledge_analysis["knowledge_depth"], 0.7)
    
    def _determine_target_audience(self, template: ProposalTemplate, knowledge_analysis: Dict) -> str:
        """対象視聴者決定"""
        if template.template_type == "content_creation":
            if knowledge_analysis["knowledge_depth"] in ["detailed", "comprehensive"]:
                return "技術系エンジニア、研究者"
            else:
                return "技術に関心のある一般ユーザー"
        elif template.template_type == "market_research":
            return "業界関係者、投資家、技術トレンドに関心のある専門家"
        else:
            return "技術系クリエイター、開発者"
    
    def _assess_difficulty_level(self, knowledge_analysis: Dict) -> str:
        """難易度レベル評価"""
        if knowledge_analysis["knowledge_depth"] == "comprehensive":
            return "hard"
        elif knowledge_analysis["knowledge_depth"] in ["detailed", "moderate"]:
            return "medium"
        else:
            return "easy"
    
    def _determine_required_resources(self, template: ProposalTemplate, knowledge_analysis: Dict) -> List[str]:
        """必要リソース決定"""
        base_resources = ["時間", "調査資料"]
        
        if template.template_type == "content_creation":
            base_resources.extend(["録画環境", "編集ソフト"])
        elif template.template_type == "tool_development":
            base_resources.extend(["開発環境", "テストデータ"])
        elif template.template_type == "collaboration":
            base_resources.extend(["コミュニケーションツール", "共有プラットフォーム"])
        
        if knowledge_analysis["technologies"]:
            base_resources.append("技術検証環境")
        
        return base_resources
    
    def _estimate_duration(self, template: ProposalTemplate, knowledge_analysis: Dict) -> str:
        """期間見積もり"""
        base_durations = {
            "content_creation": "1週間",
            "market_research": "1-2週間", 
            "tool_development": "2-3週間",
            "collaboration": "1-2ヶ月"
        }
        
        duration = base_durations.get(template.template_type, "1週間")
        
        # 知識深度による調整
        if knowledge_analysis["knowledge_depth"] == "comprehensive":
            if "週間" in duration:
                duration = duration.replace("1週間", "2週間").replace("2週間", "3週間")
        
        return duration
    
    def _save_proposals(self, proposals: List[ActivityProposal]):
        """提案保存"""
        try:
            current_month = datetime.now().strftime("%Y%m")
            proposals_file = self.proposals_dir / f"proposals_{current_month}.json"
            
            # 既存データ読み込み
            if proposals_file.exists():
                with open(proposals_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = {
                    "month": current_month,
                    "generated_proposals": [],
                    "proposal_statistics": {}
                }
            
            # 新しい提案追加
            for proposal in proposals:
                proposal_dict = asdict(proposal)
                data["generated_proposals"].append(proposal_dict)
            
            # 統計更新
            data["proposal_statistics"] = {
                "total_generated": len(data["generated_proposals"]),
                "by_type": dict(self.stats["by_type"]),
                "last_updated": datetime.now().isoformat()
            }
            
            # 保存
            with open(proposals_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            
        except Exception as e:
            print(f"[提案エンジン] ❌ 提案保存失敗: {e}")
    
    def get_proposals_by_status(self, status: str) -> List[ActivityProposal]:
        """ステータス別提案取得"""
        return [p for p in self.proposals.values() if p.status == status]
    
    def get_top_proposals(self, limit: int = 5) -> List[ActivityProposal]:
        """高評価提案取得"""
        scored_proposals = []
        
        for proposal in self.proposals.values():
            # 総合スコア計算
            setsuna_score = sum(proposal.setsuna_alignment.values()) / len(proposal.setsuna_alignment)
            impact_score = sum(proposal.expected_impact.values()) / len(proposal.expected_impact)
            feasibility_score = proposal.technical_feasibility
            
            total_score = (setsuna_score * 0.4 + impact_score * 0.4 + feasibility_score * 0.2)
            scored_proposals.append((total_score, proposal))
        
        scored_proposals.sort(key=lambda x: x[0], reverse=True)
        return [proposal for _, proposal in scored_proposals[:limit]]
    
    def update_proposal_status(self, proposal_id: str, status: str, user_feedback: str = None) -> bool:
        """提案ステータス更新"""
        try:
            if proposal_id in self.proposals:
                proposal = self.proposals[proposal_id]
                proposal.status = status
                
                if user_feedback:
                    proposal.user_feedback = user_feedback
                
                if status == "accepted":
                    proposal.acceptance_date = datetime.now()
                elif status == "completed":
                    proposal.completion_date = datetime.now()
                
                # 統計更新
                self._update_statistics()
                
                print(f"[提案エンジン] ✅ ステータス更新: {proposal_id} -> {status}")
                return True
            
            return False
            
        except Exception as e:
            print(f"[提案エンジン] ❌ ステータス更新失敗: {e}")
            return False
    
    def _update_statistics(self):
        """統計更新"""
        total_proposals = len(self.proposals)
        if total_proposals == 0:
            return
        
        accepted_count = len([p for p in self.proposals.values() if p.status == "accepted"])
        completed_count = len([p for p in self.proposals.values() if p.status == "completed"])
        
        self.stats["acceptance_rate"] = accepted_count / total_proposals
        self.stats["completion_rate"] = completed_count / total_proposals if accepted_count > 0 else 0
    
    def get_proposal_statistics(self) -> Dict[str, Any]:
        """提案統計取得"""
        self._update_statistics()
        
        return {
            **self.stats,
            "total_proposals": len(self.proposals),
            "pending_proposals": len(self.get_proposals_by_status("pending")),
            "accepted_proposals": len(self.get_proposals_by_status("accepted")),
            "completed_proposals": len(self.get_proposals_by_status("completed")),
            "setsuna_alignment_average": self._calculate_average_setsuna_alignment()
        }
    
    def _calculate_average_setsuna_alignment(self) -> Dict[str, float]:
        """平均せつな適合度計算"""
        if not self.proposals:
            return {"personality_fit": 0.0, "skill_match": 0.0, "interest_level": 0.0}
        
        total_alignment = {"personality_fit": 0.0, "skill_match": 0.0, "interest_level": 0.0}
        
        for proposal in self.proposals.values():
            for key, value in proposal.setsuna_alignment.items():
                total_alignment[key] += value
        
        count = len(self.proposals)
        return {key: value / count for key, value in total_alignment.items()}


# テスト用コード
if __name__ == "__main__":
    print("=== ActivityProposalEngine テスト ===")
    
    engine = ActivityProposalEngine()
    
    # テスト用セッション知識
    test_session_knowledge = {
        "session_id": "test_session_001",
        "knowledge_items": [
            {
                "categories": ["AI技術", "音楽生成"],
                "keywords": ["Transformer", "音楽", "AI", "生成"],
                "entities": ["OpenAI", "Google", "MusicTransformer"],
                "importance_score": 0.8
            },
            {
                "categories": ["市場", "商用ツール"],
                "keywords": ["AIVA", "Amper Music", "商用", "市場"],
                "entities": ["AIVA", "Amper Music"],
                "importance_score": 0.7
            },
            {
                "categories": ["実用", "ツール比較"],
                "keywords": ["比較", "検証", "ユーザビリティ"],
                "entities": ["比較分析", "ユーザテスト"],
                "importance_score": 0.6
            }
        ]
    }
    
    # 提案生成テスト
    print("\n🎯 活動提案生成テスト:")
    proposals = engine.generate_proposals_from_session(
        session_id="test_session_001",
        session_knowledge=test_session_knowledge,
        max_proposals=3
    )
    
    print(f"\n📋 生成された提案: {len(proposals)}件")
    for i, proposal in enumerate(proposals, 1):
        print(f"\n提案{i}: {proposal.title}")
        print(f"  タイプ: {proposal.proposal_type}")
        print(f"  説明: {proposal.description[:100]}...")
        print(f"  対象: {proposal.target_audience}")
        print(f"  期間: {proposal.estimated_duration}")
        print(f"  難易度: {proposal.difficulty_level}")
        
        # せつな適合度
        alignment = proposal.setsuna_alignment
        avg_alignment = sum(alignment.values()) / len(alignment)
        print(f"  せつな適合度: {avg_alignment:.2f}")
    
    # 統計情報表示
    print(f"\n📊 提案エンジン統計:")
    stats = engine.get_proposal_statistics()
    print(f"  総提案数: {stats['total_proposals']}")
    print(f"  タイプ別: {dict(stats['by_type'])}")
    print(f"  平均適合度: {stats['setsuna_alignment_average']}")
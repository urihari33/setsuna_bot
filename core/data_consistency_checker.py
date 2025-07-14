#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
データ整合性チェックシステム - Phase 2F実装
全システム間のデータ整合性検証・矛盾検出・自動修復システム
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
from datetime import datetime, timedelta
import hashlib
import difflib
from statistics import mean

# プロジェクトルートをパスに追加
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Windowsパス設定
if os.name == 'nt':
    DATA_DIR = Path("D:/setsuna_bot/data")
    YOUTUBE_DATA_DIR = Path("D:/setsuna_bot/youtube_knowledge_system/data")
    CONSISTENCY_CACHE_DIR = Path("D:/setsuna_bot/data_consistency_cache")
else:
    DATA_DIR = Path("/mnt/d/setsuna_bot/data")
    YOUTUBE_DATA_DIR = Path("/mnt/d/setsuna_bot/youtube_knowledge_system/data")
    CONSISTENCY_CACHE_DIR = Path("/mnt/d/setsuna_bot/data_consistency_cache")

CONSISTENCY_CACHE_DIR.mkdir(parents=True, exist_ok=True)

@dataclass
class ConsistencyIssue:
    """整合性問題データクラス"""
    issue_id: str
    issue_type: str             # "duplication", "conflict", "missing_reference", "orphaned_data", "format_mismatch"
    severity: str               # "low", "medium", "high", "critical"
    affected_files: List[str]
    affected_entities: List[str]
    description: str
    conflict_details: Dict[str, Any]
    auto_fixable: bool
    suggested_resolution: str
    detected_at: str
    resolved_at: Optional[str]
    resolution_method: Optional[str]

@dataclass
class DataIntegrityReport:
    """データ整合性レポートデータクラス"""
    report_id: str
    check_timestamp: str
    total_files_checked: int
    total_entities_checked: int
    issues_found: int
    issues_by_severity: Dict[str, int]
    issues_by_type: Dict[str, int]
    auto_fixed_issues: int
    integrity_score: float       # 0.0-1.0
    recommendations: List[str]
    detailed_results: Dict[str, Any]

@dataclass
class DataReference:
    """データ参照データクラス"""
    reference_id: str
    source_file: str
    source_entity: str
    target_file: str
    target_entity: str
    reference_type: str          # "foreign_key", "entity_reference", "file_reference"
    is_valid: bool
    last_validated: str

@dataclass
class DataSchema:
    """データスキーマデータクラス"""
    schema_id: str
    file_path: str
    required_fields: List[str]
    optional_fields: List[str]
    field_types: Dict[str, str]
    validation_rules: Dict[str, Any]
    schema_version: str
    last_updated: str

class DataConsistencyChecker:
    """データ整合性チェックシステムクラス"""
    
    def __init__(self):
        """初期化"""
        # データパス
        self.consistency_issues_path = CONSISTENCY_CACHE_DIR / "consistency_issues.json"
        self.integrity_reports_path = CONSISTENCY_CACHE_DIR / "integrity_reports.json"
        self.data_references_path = CONSISTENCY_CACHE_DIR / "data_references.json"
        self.data_schemas_path = CONSISTENCY_CACHE_DIR / "data_schemas.json"
        self.consistency_log_path = CONSISTENCY_CACHE_DIR / "consistency_log.json"
        
        # データ
        self.consistency_issues = {}
        self.integrity_reports = {}
        self.data_references = {}
        self.data_schemas = {}
        self.consistency_log = []
        
        # チェック対象ファイル
        self.target_files = [
            DATA_DIR / "multi_turn_conversations.json",
            DATA_DIR / "video_conversation_history.json",
            DATA_DIR / "user_preferences.json",
            DATA_DIR / "conversation_context.json",
            YOUTUBE_DATA_DIR / "unified_knowledge_db.json"
        ]
        
        # 整合性チェックパラメータ
        self.max_issue_age_days = 30
        self.auto_fix_enabled = True
        self.critical_severity_threshold = 0.8
        
        # 初期化
        self._load_data()
        self._initialize_data_schemas()
        
    def _load_data(self):
        """データ読み込み"""
        try:
            if self.consistency_issues_path.exists():
                with open(self.consistency_issues_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.consistency_issues = {k: ConsistencyIssue(**v) for k, v in data.items()}
            
            if self.integrity_reports_path.exists():
                with open(self.integrity_reports_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.integrity_reports = {k: DataIntegrityReport(**v) for k, v in data.items()}
            
            if self.data_references_path.exists():
                with open(self.data_references_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.data_references = {k: DataReference(**v) for k, v in data.items()}
            
            if self.data_schemas_path.exists():
                with open(self.data_schemas_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.data_schemas = {k: DataSchema(**v) for k, v in data.items()}
            
            if self.consistency_log_path.exists():
                with open(self.consistency_log_path, 'r', encoding='utf-8') as f:
                    self.consistency_log = json.load(f)
                    
        except Exception as e:
            print(f"[整合性チェック] データ読み込みエラー: {e}")
    
    def _save_data(self):
        """データ保存"""
        try:
            # 整合性問題保存
            with open(self.consistency_issues_path, 'w', encoding='utf-8') as f:
                json.dump({k: asdict(v) for k, v in self.consistency_issues.items()}, f, 
                         ensure_ascii=False, indent=2)
            
            # 整合性レポート保存
            with open(self.integrity_reports_path, 'w', encoding='utf-8') as f:
                json.dump({k: asdict(v) for k, v in self.integrity_reports.items()}, f, 
                         ensure_ascii=False, indent=2)
            
            # データ参照保存
            with open(self.data_references_path, 'w', encoding='utf-8') as f:
                json.dump({k: asdict(v) for k, v in self.data_references.items()}, f, 
                         ensure_ascii=False, indent=2)
            
            # データスキーマ保存
            with open(self.data_schemas_path, 'w', encoding='utf-8') as f:
                json.dump({k: asdict(v) for k, v in self.data_schemas.items()}, f, 
                         ensure_ascii=False, indent=2)
            
            # 整合性ログ保存
            with open(self.consistency_log_path, 'w', encoding='utf-8') as f:
                json.dump(self.consistency_log[-1000:], f, ensure_ascii=False, indent=2)  # 最新1000件
                
        except Exception as e:
            print(f"[整合性チェック] データ保存エラー: {e}")
    
    def _initialize_data_schemas(self):
        """データスキーマ初期化"""
        if not self.data_schemas:
            schemas = [
                {
                    "schema_id": "multi_turn_conversations",
                    "file_path": str(DATA_DIR / "multi_turn_conversations.json"),
                    "required_fields": ["current_session", "session_history", "config"],
                    "optional_fields": ["last_updated"],
                    "field_types": {
                        "current_session": "object",
                        "session_history": "array",
                        "config": "object",
                        "last_updated": "string"
                    },
                    "validation_rules": {
                        "current_session.session_id": "required",
                        "current_session.turns": "array"
                    },
                    "schema_version": "1.0"
                },
                {
                    "schema_id": "unified_knowledge_db",
                    "file_path": str(YOUTUBE_DATA_DIR / "unified_knowledge_db.json"),
                    "required_fields": ["videos", "metadata"],
                    "optional_fields": ["last_updated", "version"],
                    "field_types": {
                        "videos": "array",
                        "metadata": "object"
                    },
                    "validation_rules": {
                        "videos[].video_id": "required",
                        "videos[].title": "required"
                    },
                    "schema_version": "1.0"
                },
                {
                    "schema_id": "user_preferences",
                    "file_path": str(DATA_DIR / "user_preferences.json"),
                    "required_fields": [],
                    "optional_fields": ["preferences", "last_updated"],
                    "field_types": {
                        "preferences": "object",
                        "last_updated": "string"
                    },
                    "validation_rules": {},
                    "schema_version": "1.0"
                }
            ]
            
            for schema_data in schemas:
                schema_data["last_updated"] = datetime.now().isoformat()
                schema = DataSchema(**schema_data)
                self.data_schemas[schema.schema_id] = schema
    
    def run_comprehensive_check(self) -> DataIntegrityReport:
        """包括的整合性チェック実行"""
        report_id = f"integrity_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        check_timestamp = datetime.now().isoformat()
        
        total_files_checked = 0
        total_entities_checked = 0
        issues_found = 0
        issues_by_severity = {"low": 0, "medium": 0, "high": 0, "critical": 0}
        issues_by_type = defaultdict(int)
        auto_fixed_issues = 0
        recommendations = []
        detailed_results = {}
        
        try:
            # 1. ファイル存在チェック
            file_check_results = self._check_file_existence()
            detailed_results["file_existence"] = file_check_results
            total_files_checked = len(self.target_files)
            
            # 2. スキーマ検証
            schema_check_results = self._validate_data_schemas()
            detailed_results["schema_validation"] = schema_check_results
            
            # 3. 参照整合性チェック
            reference_check_results = self._check_reference_integrity()
            detailed_results["reference_integrity"] = reference_check_results
            
            # 4. 重複データ検出
            duplication_check_results = self._detect_data_duplication()
            detailed_results["duplication_check"] = duplication_check_results
            
            # 5. データ矛盾検出
            conflict_check_results = self._detect_data_conflicts()
            detailed_results["conflict_detection"] = conflict_check_results
            
            # 6. 孤立データ検出
            orphaned_data_results = self._detect_orphaned_data()
            detailed_results["orphaned_data"] = orphaned_data_results
            
            # 結果集計
            all_check_results = [
                file_check_results, schema_check_results, reference_check_results,
                duplication_check_results, conflict_check_results, orphaned_data_results
            ]
            
            for check_result in all_check_results:
                total_entities_checked += check_result.get("entities_checked", 0)
                issues_found += len(check_result.get("issues", []))
                
                for issue in check_result.get("issues", []):
                    severity = issue.get("severity", "low")
                    issue_type = issue.get("issue_type", "unknown")
                    
                    issues_by_severity[severity] += 1
                    issues_by_type[issue_type] += 1
                    
                    # 自動修正試行
                    if self.auto_fix_enabled and issue.get("auto_fixable", False):
                        if self._attempt_auto_fix(issue):
                            auto_fixed_issues += 1
            
            # 整合性スコア計算
            integrity_score = self._calculate_integrity_score(issues_found, total_entities_checked, issues_by_severity)
            
            # 推奨事項生成
            recommendations = self._generate_recommendations(detailed_results, integrity_score)
            
        except Exception as e:
            detailed_results["error"] = str(e)
            integrity_score = 0.0
            recommendations = [f"チェック実行中にエラーが発生しました: {str(e)}"]
        
        # レポート作成
        report = DataIntegrityReport(
            report_id=report_id,
            check_timestamp=check_timestamp,
            total_files_checked=total_files_checked,
            total_entities_checked=total_entities_checked,
            issues_found=issues_found,
            issues_by_severity=dict(issues_by_severity),
            issues_by_type=dict(issues_by_type),
            auto_fixed_issues=auto_fixed_issues,
            integrity_score=integrity_score,
            recommendations=recommendations,
            detailed_results=detailed_results
        )
        
        # レポート保存
        self.integrity_reports[report_id] = report
        
        # ログ記録
        self._log_consistency_check(report)
        
        # データ保存
        self._save_data()
        
        return report
    
    def _check_file_existence(self) -> Dict[str, Any]:
        """ファイル存在チェック"""
        result = {
            "check_type": "file_existence",
            "entities_checked": len(self.target_files),
            "issues": []
        }
        
        for file_path in self.target_files:
            if not file_path.exists():
                issue = {
                    "issue_type": "missing_file",
                    "severity": "critical",
                    "description": f"必須ファイルが見つかりません: {file_path}",
                    "affected_files": [str(file_path)],
                    "auto_fixable": False,
                    "suggested_resolution": "ファイルを復元または再作成してください"
                }
                result["issues"].append(issue)
                
                # 整合性問題として記録
                self._record_consistency_issue(issue)
        
        return result
    
    def _validate_data_schemas(self) -> Dict[str, Any]:
        """データスキーマ検証"""
        result = {
            "check_type": "schema_validation",
            "entities_checked": 0,
            "issues": []
        }
        
        for schema_id, schema in self.data_schemas.items():
            file_path = Path(schema.file_path)
            
            if not file_path.exists():
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                result["entities_checked"] += 1
                
                # 必須フィールドチェック
                for required_field in schema.required_fields:
                    if required_field not in data:
                        issue = {
                            "issue_type": "missing_required_field",
                            "severity": "high",
                            "description": f"必須フィールドが不足: {required_field} in {file_path.name}",
                            "affected_files": [str(file_path)],
                            "affected_entities": [required_field],
                            "auto_fixable": False,
                            "suggested_resolution": f"フィールド {required_field} を追加してください"
                        }
                        result["issues"].append(issue)
                        self._record_consistency_issue(issue)
                
                # フィールドタイプチェック
                for field_name, expected_type in schema.field_types.items():
                    if field_name in data:
                        actual_type = type(data[field_name]).__name__
                        if not self._is_type_compatible(actual_type, expected_type):
                            issue = {
                                "issue_type": "type_mismatch",
                                "severity": "medium",
                                "description": f"型不一致: {field_name} (期待値: {expected_type}, 実際: {actual_type})",
                                "affected_files": [str(file_path)],
                                "affected_entities": [field_name],
                                "auto_fixable": True,
                                "suggested_resolution": f"フィールド {field_name} の型を {expected_type} に修正"
                            }
                            result["issues"].append(issue)
                            self._record_consistency_issue(issue)
                
            except Exception as e:
                issue = {
                    "issue_type": "file_parse_error",
                    "severity": "critical",
                    "description": f"ファイル解析エラー: {file_path.name} - {str(e)}",
                    "affected_files": [str(file_path)],
                    "auto_fixable": False,
                    "suggested_resolution": "ファイル形式を確認し、JSONエラーを修正してください"
                }
                result["issues"].append(issue)
                self._record_consistency_issue(issue)
        
        return result
    
    def _check_reference_integrity(self) -> Dict[str, Any]:
        """参照整合性チェック"""
        result = {
            "check_type": "reference_integrity",
            "entities_checked": 0,
            "issues": []
        }
        
        # 動画IDの参照整合性チェック
        video_ids = self._extract_video_ids_from_knowledge_db()
        conversation_video_refs = self._extract_video_references_from_conversations()
        
        result["entities_checked"] = len(conversation_video_refs)
        
        for ref_location, video_id in conversation_video_refs:
            if video_id not in video_ids:
                issue = {
                    "issue_type": "missing_reference",
                    "severity": "medium",
                    "description": f"存在しない動画IDが参照されています: {video_id} in {ref_location}",
                    "affected_files": [ref_location, str(YOUTUBE_DATA_DIR / "unified_knowledge_db.json")],
                    "affected_entities": [video_id],
                    "auto_fixable": False,
                    "suggested_resolution": "動画IDを修正するか、参照を削除してください"
                }
                result["issues"].append(issue)
                self._record_consistency_issue(issue)
        
        return result
    
    def _detect_data_duplication(self) -> Dict[str, Any]:
        """重複データ検出"""
        result = {
            "check_type": "duplication_detection",
            "entities_checked": 0,
            "issues": []
        }
        
        # 動画データの重複チェック
        video_duplicates = self._find_duplicate_videos()
        result["entities_checked"] += len(video_duplicates)
        
        for duplicate_group in video_duplicates:
            if len(duplicate_group) > 1:
                issue = {
                    "issue_type": "duplication",
                    "severity": "low",
                    "description": f"重複する動画データ: {duplicate_group}",
                    "affected_files": [str(YOUTUBE_DATA_DIR / "unified_knowledge_db.json")],
                    "affected_entities": duplicate_group,
                    "auto_fixable": True,
                    "suggested_resolution": "重複するエントリを統合または削除してください"
                }
                result["issues"].append(issue)
                self._record_consistency_issue(issue)
        
        return result
    
    def _detect_data_conflicts(self) -> Dict[str, Any]:
        """データ矛盾検出"""
        result = {
            "check_type": "conflict_detection",
            "entities_checked": 0,
            "issues": []
        }
        
        # 同一動画の異なる情報チェック
        video_conflicts = self._find_video_conflicts()
        result["entities_checked"] += len(video_conflicts)
        
        for video_id, conflicts in video_conflicts.items():
            for conflict in conflicts:
                issue = {
                    "issue_type": "conflict",
                    "severity": "medium",
                    "description": f"動画 {video_id} のデータ矛盾: {conflict['description']}",
                    "affected_files": conflict["affected_files"],
                    "affected_entities": [video_id],
                    "auto_fixable": False,
                    "suggested_resolution": "矛盾するデータを確認し、正しい値に統一してください"
                }
                result["issues"].append(issue)
                self._record_consistency_issue(issue)
        
        return result
    
    def _detect_orphaned_data(self) -> Dict[str, Any]:
        """孤立データ検出"""
        result = {
            "check_type": "orphaned_data_detection",
            "entities_checked": 0,
            "issues": []
        }
        
        # 参照されていない動画データの検出
        orphaned_videos = self._find_orphaned_videos()
        result["entities_checked"] += len(orphaned_videos)
        
        for video_id in orphaned_videos:
            issue = {
                "issue_type": "orphaned_data",
                "severity": "low",
                "description": f"参照されていない動画データ: {video_id}",
                "affected_files": [str(YOUTUBE_DATA_DIR / "unified_knowledge_db.json")],
                "affected_entities": [video_id],
                "auto_fixable": False,
                "suggested_resolution": "未使用データの削除または参照の追加を検討してください"
            }
            result["issues"].append(issue)
            self._record_consistency_issue(issue)
        
        return result
    
    def _extract_video_ids_from_knowledge_db(self) -> Set[str]:
        """知識DBから動画ID抽出"""
        video_ids = set()
        
        try:
            knowledge_db_path = YOUTUBE_DATA_DIR / "unified_knowledge_db.json"
            if knowledge_db_path.exists():
                with open(knowledge_db_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    if "videos" in data:
                        for video in data["videos"]:
                            if "video_id" in video:
                                video_ids.add(video["video_id"])
        
        except Exception as e:
            print(f"[整合性チェック] 動画ID抽出エラー: {e}")
        
        return video_ids
    
    def _extract_video_references_from_conversations(self) -> List[Tuple[str, str]]:
        """会話データから動画参照抽出"""
        references = []
        
        conversation_files = [
            (DATA_DIR / "multi_turn_conversations.json", "multi_turn_conversations"),
            (DATA_DIR / "video_conversation_history.json", "video_conversation_history")
        ]
        
        for file_path, file_name in conversation_files:
            if not file_path.exists():
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # 動画ID参照の検索（簡単なパターンマッチング）
                    references.extend(self._find_video_id_patterns(data, file_name))
            
            except Exception as e:
                print(f"[整合性チェック] 会話参照抽出エラー: {e}")
        
        return references
    
    def _find_video_id_patterns(self, data: Any, file_name: str, path: str = "") -> List[Tuple[str, str]]:
        """データ内の動画IDパターン検索"""
        references = []
        
        if isinstance(data, dict):
            for key, value in data.items():
                new_path = f"{path}.{key}" if path else key
                
                # 動画IDらしいキーをチェック
                if key == "video_id" and isinstance(value, str):
                    references.append((file_name, value))
                elif key in ["mentioned_videos", "active_topics"] and isinstance(value, (dict, list)):
                    references.extend(self._find_video_id_patterns(value, file_name, new_path))
                else:
                    references.extend(self._find_video_id_patterns(value, file_name, new_path))
        
        elif isinstance(data, list):
            for i, item in enumerate(data):
                new_path = f"{path}[{i}]" if path else f"[{i}]"
                references.extend(self._find_video_id_patterns(item, file_name, new_path))
        
        return references
    
    def _find_duplicate_videos(self) -> List[List[str]]:
        """重複動画検出"""
        duplicates = []
        
        try:
            knowledge_db_path = YOUTUBE_DATA_DIR / "unified_knowledge_db.json"
            if knowledge_db_path.exists():
                with open(knowledge_db_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    if "videos" in data:
                        videos_by_title = defaultdict(list)
                        
                        for video in data["videos"]:
                            title = video.get("title", "").strip().lower()
                            if title:
                                videos_by_title[title].append(video.get("video_id", "unknown"))
                        
                        # 重複グループを検出
                        for title, video_ids in videos_by_title.items():
                            if len(video_ids) > 1:
                                duplicates.append(video_ids)
        
        except Exception as e:
            print(f"[整合性チェック] 重複検出エラー: {e}")
        
        return duplicates
    
    def _find_video_conflicts(self) -> Dict[str, List[Dict[str, Any]]]:
        """動画データ矛盾検出"""
        conflicts = defaultdict(list)
        
        # 実装の例：同一動画IDで異なるタイトルなど
        # 実際の実装では、より詳細な矛盾検出ロジックが必要
        
        return dict(conflicts)
    
    def _find_orphaned_videos(self) -> List[str]:
        """孤立動画検出"""
        orphaned = []
        
        try:
            # 知識DBの全動画ID
            all_video_ids = self._extract_video_ids_from_knowledge_db()
            
            # 会話で参照されている動画ID
            referenced_video_ids = set()
            conversation_refs = self._extract_video_references_from_conversations()
            for _, video_id in conversation_refs:
                referenced_video_ids.add(video_id)
            
            # 参照されていない動画を検出
            orphaned = list(all_video_ids - referenced_video_ids)
        
        except Exception as e:
            print(f"[整合性チェック] 孤立データ検出エラー: {e}")
        
        return orphaned
    
    def _is_type_compatible(self, actual_type: str, expected_type: str) -> bool:
        """型互換性チェック"""
        type_mapping = {
            "str": "string",
            "dict": "object",
            "list": "array",
            "int": "number",
            "float": "number",
            "bool": "boolean"
        }
        
        normalized_actual = type_mapping.get(actual_type, actual_type)
        return normalized_actual == expected_type
    
    def _record_consistency_issue(self, issue_data: Dict[str, Any]):
        """整合性問題記録"""
        issue_id = f"issue_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hashlib.md5(str(issue_data).encode()).hexdigest()[:8]}"
        
        issue = ConsistencyIssue(
            issue_id=issue_id,
            issue_type=issue_data.get("issue_type", "unknown"),
            severity=issue_data.get("severity", "low"),
            affected_files=issue_data.get("affected_files", []),
            affected_entities=issue_data.get("affected_entities", []),
            description=issue_data.get("description", ""),
            conflict_details=issue_data.get("conflict_details", {}),
            auto_fixable=issue_data.get("auto_fixable", False),
            suggested_resolution=issue_data.get("suggested_resolution", ""),
            detected_at=datetime.now().isoformat(),
            resolved_at=None,
            resolution_method=None
        )
        
        self.consistency_issues[issue_id] = issue
    
    def _attempt_auto_fix(self, issue_data: Dict[str, Any]) -> bool:
        """自動修正試行"""
        try:
            issue_type = issue_data.get("issue_type")
            
            if issue_type == "duplication":
                return self._auto_fix_duplication(issue_data)
            elif issue_type == "type_mismatch":
                return self._auto_fix_type_mismatch(issue_data)
            else:
                return False
        
        except Exception as e:
            print(f"[整合性チェック] 自動修正エラー: {e}")
            return False
    
    def _auto_fix_duplication(self, issue_data: Dict[str, Any]) -> bool:
        """重複データ自動修正"""
        # 重複データの統合（実際の実装では慎重な処理が必要）
        return False  # 安全のため無効化
    
    def _auto_fix_type_mismatch(self, issue_data: Dict[str, Any]) -> bool:
        """型不一致自動修正"""
        # 型変換（実際の実装では慎重な処理が必要）
        return False  # 安全のため無効化
    
    def _calculate_integrity_score(self, issues_found: int, total_entities: int, 
                                  issues_by_severity: Dict[str, int]) -> float:
        """整合性スコア計算"""
        if total_entities == 0:
            return 1.0
        
        # 重要度による重み付け
        severity_weights = {"low": 1, "medium": 3, "high": 5, "critical": 10}
        
        weighted_issues = sum(
            issues_by_severity[severity] * weight
            for severity, weight in severity_weights.items()
        )
        
        # スコア計算（重み付けされた問題数を考慮）
        max_possible_weight = total_entities * severity_weights["critical"]
        if max_possible_weight > 0:
            score = 1.0 - (weighted_issues / max_possible_weight)
        else:
            score = 1.0
        
        return max(0.0, min(1.0, score))
    
    def _generate_recommendations(self, detailed_results: Dict[str, Any], 
                                integrity_score: float) -> List[str]:
        """推奨事項生成"""
        recommendations = []
        
        # 整合性スコアに基づく推奨事項
        if integrity_score < 0.5:
            recommendations.append("緊急：重要な整合性問題が検出されました。即座に対応が必要です。")
        elif integrity_score < 0.8:
            recommendations.append("注意：いくつかの整合性問題があります。計画的な修正を推奨します。")
        else:
            recommendations.append("良好：データ整合性は適切なレベルを維持しています。")
        
        # 問題タイプ別推奨事項
        for check_type, results in detailed_results.items():
            if results.get("issues"):
                issue_types = Counter([issue.get("issue_type") for issue in results["issues"]])
                
                for issue_type, count in issue_types.items():
                    if issue_type == "missing_reference":
                        recommendations.append(f"参照整合性の修正: {count}件の不正な参照を修正してください。")
                    elif issue_type == "duplication":
                        recommendations.append(f"重複データの整理: {count}件の重複を統合または削除してください。")
                    elif issue_type == "missing_file":
                        recommendations.append("重要ファイルの復元: 不足しているファイルを復元してください。")
        
        if not recommendations:
            recommendations.append("現在、特別な対応は必要ありません。定期的なチェックを継続してください。")
        
        return recommendations
    
    def _log_consistency_check(self, report: DataIntegrityReport):
        """整合性チェックログ記録"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "report_id": report.report_id,
            "integrity_score": report.integrity_score,
            "issues_found": report.issues_found,
            "auto_fixed_issues": report.auto_fixed_issues,
            "check_duration_files": report.total_files_checked,
            "check_duration_entities": report.total_entities_checked
        }
        
        self.consistency_log.append(log_entry)
    
    def get_consistency_summary(self) -> Dict[str, Any]:
        """整合性サマリー取得"""
        summary = {
            "current_status": {},
            "recent_trends": {},
            "active_issues": {},
            "recommendations": []
        }
        
        try:
            # 現在の状態
            if self.integrity_reports:
                latest_report = max(self.integrity_reports.values(), key=lambda r: r.check_timestamp)
                summary["current_status"] = {
                    "integrity_score": latest_report.integrity_score,
                    "total_issues": latest_report.issues_found,
                    "critical_issues": latest_report.issues_by_severity.get("critical", 0),
                    "last_check": latest_report.check_timestamp
                }
            
            # アクティブな問題
            active_issues = [issue for issue in self.consistency_issues.values() if not issue.resolved_at]
            summary["active_issues"] = {
                "total": len(active_issues),
                "by_severity": Counter([issue.severity for issue in active_issues]),
                "by_type": Counter([issue.issue_type for issue in active_issues])
            }
            
            # 最新のトレンド
            if len(self.consistency_log) >= 2:
                recent_scores = [entry["integrity_score"] for entry in self.consistency_log[-5:]]
                if len(recent_scores) > 1:
                    trend_direction = "improving" if recent_scores[-1] > recent_scores[0] else "declining"
                    summary["recent_trends"] = {
                        "direction": trend_direction,
                        "score_change": recent_scores[-1] - recent_scores[0]
                    }
            
            # 推奨事項
            if self.integrity_reports:
                latest_report = max(self.integrity_reports.values(), key=lambda r: r.check_timestamp)
                summary["recommendations"] = latest_report.recommendations[:3]
        
        except Exception as e:
            summary["error"] = f"サマリー生成エラー: {str(e)}"
        
        return summary

def main():
    """テスト実行"""
    print("=== データ整合性チェックシステムテスト ===")
    
    checker = DataConsistencyChecker()
    
    # 包括的チェック実行
    report = checker.run_comprehensive_check()
    print(f"整合性チェック完了:")
    print(f"  - 整合性スコア: {report.integrity_score:.3f}")
    print(f"  - 検出された問題: {report.issues_found}件")
    print(f"  - 自動修正: {report.auto_fixed_issues}件")
    
    # 整合性サマリー
    summary = checker.get_consistency_summary()
    print(f"整合性サマリー: {summary.get('current_status', {})}")

if __name__ == "__main__":
    main()
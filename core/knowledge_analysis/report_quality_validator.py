#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ReportQualityValidator - レポート品質検証システム
生成されたレポートの品質・一貫性・完整性を自動検証
"""

import json
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum

class ValidationSeverity(Enum):
    """検証問題の重要度レベル"""
    INFO = "info"
    WARNING = "warning" 
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class ValidationIssue:
    """検証で発見された問題"""
    severity: ValidationSeverity
    category: str
    field: str
    message: str
    actual_value: Any = None
    expected_value: Any = None
    suggestion: str = ""

@dataclass
class ValidationReport:
    """検証レポート"""
    validation_timestamp: str
    overall_score: float  # 0.0-1.0
    total_issues: int
    issues_by_severity: Dict[str, int] = field(default_factory=dict)
    issues: List[ValidationIssue] = field(default_factory=list)
    quality_metrics: Dict[str, float] = field(default_factory=dict)
    validation_summary: str = ""
    recommendations: List[str] = field(default_factory=list)

class ReportQualityValidator:
    """レポート品質検証システム"""
    
    def __init__(self):
        """初期化"""
        self.validation_history = []
        
        # 検証基準定義
        self.validation_criteria = {
            "required_fields": [
                "report_id", "timestamp", "user_prompt", "search_count",
                "analysis_summary", "key_insights", "categories", 
                "related_topics", "data_quality", "cost", "processing_time"
            ],
            "field_types": {
                "report_id": (int, "整数"),
                "timestamp": (str, "文字列（ISO形式）"),
                "user_prompt": (str, "文字列"),
                "search_count": (int, "整数"),
                "analysis_summary": (str, "文字列"),
                "key_insights": (list, "リスト"),
                "categories": (dict, "辞書"),
                "related_topics": (list, "リスト"),
                "data_quality": (float, "小数（0.0-1.0）"),
                "cost": (float, "小数"),
                "processing_time": (str, "文字列")
            },
            "value_ranges": {
                "data_quality": (0.0, 1.0),
                "cost": (0.0, 100.0),  # 上限100ドル
                "search_count": (0, 1000)  # 上限1000件
            },
            "content_quality": {
                "analysis_summary_min_length": 50,
                "analysis_summary_max_length": 10000,
                "key_insights_min_count": 1,
                "key_insights_max_count": 10,
                "related_topics_max_count": 8
            }
        }
    
    def validate_report(self, report: Dict) -> ValidationReport:
        """レポート全体の品質検証"""
        validation_start = datetime.now()
        issues = []
        
        # 1. 構造検証
        structural_issues = self._validate_structure(report)
        issues.extend(structural_issues)
        
        # 2. データ型検証
        type_issues = self._validate_data_types(report)
        issues.extend(type_issues)
        
        # 3. 値範囲検証
        range_issues = self._validate_value_ranges(report)
        issues.extend(range_issues)
        
        # 4. コンテンツ品質検証
        content_issues = self._validate_content_quality(report)
        issues.extend(content_issues)
        
        # 5. 一貫性検証
        consistency_issues = self._validate_consistency(report)
        issues.extend(consistency_issues)
        
        # 6. 検証結果集計
        validation_report = self._generate_validation_report(
            validation_start, issues, report
        )
        
        # 履歴に追加
        self.validation_history.append(validation_report)
        
        return validation_report
    
    def _validate_structure(self, report: Dict) -> List[ValidationIssue]:
        """構造検証 - 必須フィールドの存在確認"""
        issues = []
        
        for required_field in self.validation_criteria["required_fields"]:
            if required_field not in report:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    category="structure",
                    field=required_field,
                    message=f"必須フィールド '{required_field}' が存在しません",
                    suggestion=f"'{required_field}' フィールドを追加してください"
                ))
            elif report[required_field] is None:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    category="structure", 
                    field=required_field,
                    message=f"必須フィールド '{required_field}' がNullです",
                    actual_value=None,
                    suggestion=f"'{required_field}' に適切な値を設定してください"
                ))
        
        return issues
    
    def _validate_data_types(self, report: Dict) -> List[ValidationIssue]:
        """データ型検証"""
        issues = []
        
        for field, (expected_type, type_name) in self.validation_criteria["field_types"].items():
            if field in report and report[field] is not None:
                actual_value = report[field]
                if not isinstance(actual_value, expected_type):
                    # コアフィールドの型エラーは重大な問題とする
                    severity = ValidationSeverity.CRITICAL if field in ["report_id", "timestamp", "data_quality"] else ValidationSeverity.ERROR
                    
                    issues.append(ValidationIssue(
                        severity=severity,
                        category="data_type",
                        field=field,
                        message=f"'{field}' のデータ型が不正です",
                        actual_value=f"{type(actual_value).__name__}: {actual_value}",
                        expected_value=type_name,
                        suggestion=f"'{field}' を {type_name} 型に変更してください"
                    ))
        
        return issues
    
    def _validate_value_ranges(self, report: Dict) -> List[ValidationIssue]:
        """値範囲検証"""
        issues = []
        
        for field, (min_val, max_val) in self.validation_criteria["value_ranges"].items():
            if field in report and report[field] is not None:
                actual_value = report[field]
                
                # 数値型チェック
                if isinstance(actual_value, (int, float)):
                    if actual_value < min_val:
                        # 負の値やdata_qualityの範囲外は重大な問題
                        severity = ValidationSeverity.CRITICAL if field == "data_quality" or actual_value < 0 else ValidationSeverity.WARNING
                        issues.append(ValidationIssue(
                            severity=severity,
                            category="value_range",
                            field=field,
                            message=f"'{field}' の値が最小値を下回っています",
                            actual_value=actual_value,
                            expected_value=f">= {min_val}",
                            suggestion=f"'{field}' を {min_val} 以上に設定してください"
                        ))
                    elif actual_value > max_val:
                        # 極端に大きな値は重大な問題
                        severity = ValidationSeverity.CRITICAL if actual_value > max_val * 10 else ValidationSeverity.WARNING
                        issues.append(ValidationIssue(
                            severity=severity,
                            category="value_range", 
                            field=field,
                            message=f"'{field}' の値が最大値を上回っています",
                            actual_value=actual_value,
                            expected_value=f"<= {max_val}",
                            suggestion=f"'{field}' を {max_val} 以下に設定してください"
                        ))
        
        return issues
    
    def _validate_content_quality(self, report: Dict) -> List[ValidationIssue]:
        """コンテンツ品質検証"""
        issues = []
        criteria = self.validation_criteria["content_quality"]
        
        # analysis_summary 長さチェック
        if "analysis_summary" in report:
            summary = report["analysis_summary"]
            if isinstance(summary, str):
                length = len(summary)
                if length < criteria["analysis_summary_min_length"]:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        category="content_quality",
                        field="analysis_summary",
                        message="分析要約が短すぎます",
                        actual_value=f"{length}文字",
                        expected_value=f">= {criteria['analysis_summary_min_length']}文字",
                        suggestion="より詳細な分析要約を提供してください"
                    ))
                elif length > criteria["analysis_summary_max_length"]:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.INFO,
                        category="content_quality",
                        field="analysis_summary",
                        message="分析要約が長すぎます",
                        actual_value=f"{length}文字",
                        expected_value=f"<= {criteria['analysis_summary_max_length']}文字",
                        suggestion="分析要約を簡潔にまとめることを検討してください"
                    ))
                
                # 空白文字のみチェック
                if summary.strip() == "":
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        category="content_quality",
                        field="analysis_summary",
                        message="分析要約が空白です",
                        suggestion="意味のある分析要約を提供してください"
                    ))
        
        # key_insights 品質チェック
        if "key_insights" in report:
            insights = report["key_insights"]
            if isinstance(insights, list):
                insight_count = len(insights)
                
                if insight_count < criteria["key_insights_min_count"]:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        category="content_quality",
                        field="key_insights",
                        message="主要発見事項が不足しています",
                        actual_value=f"{insight_count}件",
                        expected_value=f">= {criteria['key_insights_min_count']}件",
                        suggestion="より多くの主要発見事項を抽出してください"
                    ))
                elif insight_count > criteria["key_insights_max_count"]:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.INFO,
                        category="content_quality",
                        field="key_insights",
                        message="主要発見事項が多すぎます",
                        actual_value=f"{insight_count}件",
                        expected_value=f"<= {criteria['key_insights_max_count']}件",
                        suggestion="最も重要な発見事項に絞り込んでください"
                    ))
                
                # 重複チェック
                unique_insights = set(insights)
                if len(unique_insights) < len(insights):
                    duplicate_count = len(insights) - len(unique_insights)
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        category="content_quality",
                        field="key_insights",
                        message="主要発見事項に重複があります",
                        actual_value=f"{duplicate_count}件の重複",
                        suggestion="重複する発見事項を除去してください"
                    ))
                
                # 空の発見事項チェック
                empty_insights = [i for i, insight in enumerate(insights) if not str(insight).strip()]
                if empty_insights:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        category="content_quality",
                        field="key_insights",
                        message="空の発見事項があります",
                        actual_value=f"インデックス: {empty_insights}",
                        suggestion="空の発見事項を除去してください"
                    ))
        
        # related_topics 数量チェック
        if "related_topics" in report:
            topics = report["related_topics"]
            if isinstance(topics, list):
                topic_count = len(topics)
                if topic_count > criteria["related_topics_max_count"]:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.INFO,
                        category="content_quality",
                        field="related_topics",
                        message="関連トピック数が多すぎます",
                        actual_value=f"{topic_count}件",
                        expected_value=f"<= {criteria['related_topics_max_count']}件",
                        suggestion="最も関連性の高いトピックに絞り込んでください"
                    ))
        
        return issues
    
    def _validate_consistency(self, report: Dict) -> List[ValidationIssue]:
        """一貫性検証"""
        issues = []
        
        # search_count vs detailed_data.search_results の整合性
        if ("search_count" in report and "detailed_data" in report and 
            isinstance(report["detailed_data"], dict)):
            
            reported_count = report.get("search_count", 0)
            search_results = report["detailed_data"].get("search_results", [])
            actual_count = len(search_results) if isinstance(search_results, list) else 0
            
            if reported_count != actual_count:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    category="consistency",
                    field="search_count",
                    message="検索件数と実際の検索結果数が一致しません",
                    actual_value=f"報告: {reported_count}, 実際: {actual_count}",
                    suggestion="search_count を実際の検索結果数に合わせてください"
                ))
        
        # data_quality vs search_count の妥当性
        if "data_quality" in report and "search_count" in report:
            quality = report.get("data_quality", 0.0)
            search_count = report.get("search_count", 0)
            
            # 検索結果がないのに品質スコアが高い場合
            if search_count == 0 and quality > 0.1:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    category="consistency",
                    field="data_quality",
                    message="検索結果がないのに品質スコアが高すぎます",
                    actual_value=f"品質: {quality}, 検索数: {search_count}",
                    suggestion="検索結果がない場合は品質スコアを低く設定してください"
                ))
            
            # 検索結果が多いのに品質スコアが低い場合
            elif search_count > 50 and quality < 0.3:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    category="consistency",
                    field="data_quality",
                    message="検索結果が多いのに品質スコアが低いです",
                    actual_value=f"品質: {quality}, 検索数: {search_count}",
                    suggestion="検索結果の品質計算を確認してください"
                ))
        
        # timestamp フォーマット検証
        if "timestamp" in report:
            timestamp = report["timestamp"]
            if isinstance(timestamp, str):
                try:
                    datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                except ValueError:
                    issues.append(ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        category="consistency",
                        field="timestamp",
                        message="タイムスタンプの形式が不正です",
                        actual_value=timestamp,
                        expected_value="ISO 8601形式",
                        suggestion="正しいISO 8601形式のタイムスタンプを使用してください"
                    ))
        
        return issues
    
    def _generate_validation_report(self, start_time: datetime, issues: List[ValidationIssue], report: Dict) -> ValidationReport:
        """検証レポート生成"""
        validation_end = datetime.now()
        
        # 重要度別集計
        issues_by_severity = {
            "critical": 0,
            "error": 0, 
            "warning": 0,
            "info": 0
        }
        
        for issue in issues:
            issues_by_severity[issue.severity.value] += 1
        
        # 全体品質スコア計算（重要度に基づく減点方式）
        base_score = 1.0
        score_penalties = {
            "critical": 0.3,
            "error": 0.1,
            "warning": 0.05,
            "info": 0.01
        }
        
        for severity, count in issues_by_severity.items():
            base_score -= count * score_penalties[severity]
        
        overall_score = max(0.0, min(1.0, base_score))
        
        # 品質メトリクス計算
        quality_metrics = self._calculate_quality_metrics(report, issues)
        
        # 検証サマリー生成
        total_issues = len(issues)
        critical_issues = issues_by_severity["critical"]
        error_issues = issues_by_severity["error"]
        
        if critical_issues > 0:
            summary = f"重大な問題が{critical_issues}件検出されました。緊急対応が必要です。"
        elif error_issues > 0:
            summary = f"エラーが{error_issues}件検出されました。修正をお勧めします。"
        elif total_issues > 0:
            summary = f"軽微な問題が{total_issues}件検出されました。品質向上のため確認してください。"
        else:
            summary = "検証完了：問題は検出されませんでした。"
        
        # 推奨事項生成
        recommendations = self._generate_recommendations(issues, quality_metrics)
        
        return ValidationReport(
            validation_timestamp=validation_end.isoformat(),
            overall_score=overall_score,
            total_issues=total_issues,
            issues_by_severity=issues_by_severity,
            issues=issues,
            quality_metrics=quality_metrics,
            validation_summary=summary,
            recommendations=recommendations
        )
    
    def _calculate_quality_metrics(self, report: Dict, issues: List[ValidationIssue]) -> Dict[str, float]:
        """品質メトリクス計算"""
        metrics = {}
        
        # 構造完整性スコア
        required_fields = self.validation_criteria["required_fields"]
        present_fields = sum(1 for field in required_fields if field in report)
        metrics["structural_completeness"] = present_fields / len(required_fields)
        
        # コンテンツ充実度スコア
        content_score = 0.0
        if "analysis_summary" in report:
            summary_length = len(str(report["analysis_summary"]))
            content_score += min(1.0, summary_length / 500)  # 500文字で満点
        
        if "key_insights" in report and isinstance(report["key_insights"], list):
            insights_count = len(report["key_insights"])
            content_score += min(1.0, insights_count / 5)  # 5個で満点
        
        metrics["content_richness"] = content_score / 2  # 2項目の平均
        
        # データ品質信頼度
        if "data_quality" in report:
            reported_quality = report["data_quality"]
            search_count = report.get("search_count", 0)
            
            # 検索数と品質の整合性チェック
            expected_quality = min(0.95, 0.5 + (search_count / 200))
            quality_deviation = abs(reported_quality - expected_quality)
            metrics["quality_reliability"] = max(0.0, 1.0 - quality_deviation * 2)
        else:
            metrics["quality_reliability"] = 0.0
        
        # エラー密度（問題数の逆数）
        total_fields = len(report)
        error_density = len(issues) / total_fields if total_fields > 0 else 1.0
        metrics["error_density"] = max(0.0, 1.0 - error_density)
        
        return metrics
    
    def _generate_recommendations(self, issues: List[ValidationIssue], metrics: Dict[str, float]) -> List[str]:
        """推奨事項生成"""
        recommendations = []
        
        # 重要度の高い問題への対応
        critical_issues = [issue for issue in issues if issue.severity == ValidationSeverity.CRITICAL]
        if critical_issues:
            recommendations.append("重大な問題が検出されました。システムの動作に影響する可能性があります。")
            for issue in critical_issues[:3]:  # 最大3件
                recommendations.append(f"- {issue.message} ({issue.field})")
        
        # メトリクス基準の推奨事項
        if metrics.get("structural_completeness", 1.0) < 0.9:
            recommendations.append("必須フィールドが不足しています。レポート構造を確認してください。")
        
        if metrics.get("content_richness", 1.0) < 0.5:
            recommendations.append("コンテンツが不足しています。より詳細な分析結果を提供することをお勧めします。")
        
        if metrics.get("quality_reliability", 1.0) < 0.7:
            recommendations.append("データ品質スコアの計算に問題がある可能性があります。品質評価ロジックを確認してください。")
        
        if metrics.get("error_density", 1.0) < 0.8:
            recommendations.append("多くの検証問題が検出されました。レポート生成プロセスの見直しをお勧めします。")
        
        # 一般的な推奨事項
        warning_issues = [issue for issue in issues if issue.severity == ValidationSeverity.WARNING]
        if len(warning_issues) > 5:
            recommendations.append("警告が多数検出されました。品質向上のため段階的な改善をお勧めします。")
        
        return recommendations
    
    def get_validation_summary(self) -> Dict:
        """検証履歴の要約統計"""
        if not self.validation_history:
            return {"message": "検証履歴がありません"}
        
        recent_validations = self.validation_history[-10:]  # 最新10件
        
        avg_score = sum(v.overall_score for v in recent_validations) / len(recent_validations)
        total_issues = sum(v.total_issues for v in recent_validations)
        
        return {
            "total_validations": len(self.validation_history),
            "recent_validations": len(recent_validations),
            "average_quality_score": avg_score,
            "total_issues_found": total_issues,
            "latest_validation": recent_validations[-1].validation_timestamp,
            "trend": "improving" if len(recent_validations) >= 2 and recent_validations[-1].overall_score > recent_validations[-2].overall_score else "stable"
        }
    
    def format_validation_report(self, validation_report: ValidationReport) -> str:
        """検証レポートを読みやすい形式でフォーマット"""
        lines = []
        
        lines.append("📊 レポート品質検証結果")
        lines.append("=" * 50)
        lines.append(f"🕐 検証時刻: {validation_report.validation_timestamp}")
        lines.append(f"🏆 総合スコア: {validation_report.overall_score:.2f} ({validation_report.overall_score * 100:.1f}%)")
        lines.append(f"📋 検出問題数: {validation_report.total_issues}件")
        lines.append("")
        
        # 重要度別サマリー
        if validation_report.total_issues > 0:
            lines.append("📈 問題内訳:")
            for severity, count in validation_report.issues_by_severity.items():
                if count > 0:
                    emoji = {"critical": "🔴", "error": "❌", "warning": "⚠️", "info": "ℹ️"}[severity]
                    lines.append(f"   {emoji} {severity.upper()}: {count}件")
            lines.append("")
        
        # 品質メトリクス
        lines.append("📊 品質メトリクス:")
        for metric, value in validation_report.quality_metrics.items():
            lines.append(f"   {metric}: {value:.2f} ({value * 100:.1f}%)")
        lines.append("")
        
        # 検証サマリー
        lines.append("📝 検証サマリー:")
        lines.append(f"   {validation_report.validation_summary}")
        lines.append("")
        
        # 推奨事項
        if validation_report.recommendations:
            lines.append("💡 推奨事項:")
            for rec in validation_report.recommendations:
                lines.append(f"   • {rec}")
            lines.append("")
        
        # 重要な問題の詳細
        critical_and_error_issues = [
            issue for issue in validation_report.issues 
            if issue.severity in [ValidationSeverity.CRITICAL, ValidationSeverity.ERROR]
        ]
        
        if critical_and_error_issues:
            lines.append("🔍 重要な問題詳細:")
            for issue in critical_and_error_issues[:5]:  # 最大5件
                severity_emoji = {"critical": "🔴", "error": "❌"}[issue.severity.value]
                lines.append(f"   {severity_emoji} [{issue.field}] {issue.message}")
                if issue.suggestion:
                    lines.append(f"      💡 {issue.suggestion}")
            lines.append("")
        
        return "\n".join(lines)

if __name__ == "__main__":
    """テスト実行"""
    validator = ReportQualityValidator()
    
    # テスト用レポート作成
    test_report = {
        "report_id": 1,
        "timestamp": "2025-07-13T20:30:00.000000",
        "user_prompt": "せつなの音楽活動について",
        "search_count": 10,
        "analysis_summary": "VTuberとしての音楽活動に関する詳細な分析結果。独自の楽曲制作と配信活動の特徴について。",
        "key_insights": [
            "オリジナル楽曲の制作に注力している",
            "視聴者との音楽を通じた交流を重視している",
            "独特の音楽スタイルを確立している"
        ],
        "categories": {
            "music": "音楽制作に関する情報",
            "streaming": "配信活動について"
        },
        "related_topics": ["VTuber音楽", "オリジナル楽曲", "音楽配信"],
        "data_quality": 0.75,
        "cost": 0.05,
        "processing_time": "5分",
        "detailed_data": {
            "search_results": [{} for _ in range(10)]  # 10件のダミー結果
        }
    }
    
    print("🧪 ReportQualityValidator テスト実行")
    print("=" * 60)
    
    # 検証実行
    validation_result = validator.validate_report(test_report)
    
    # 結果表示
    print(validator.format_validation_report(validation_result))
    
    # 履歴サマリー
    print("📊 検証履歴サマリー:")
    summary = validator.get_validation_summary()
    for key, value in summary.items():
        print(f"   {key}: {value}")
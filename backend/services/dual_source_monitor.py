"""
Dual-Source Monitoring Service
Tracks performance, validation, and quality of dual-source responses
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json


class DualSourceMonitor:
    """
    Monitor and track dual-source RAG performance.
    Ensures system is meeting zero-hallucination requirements.
    """

    def __init__(self):
        """Initialize monitoring service."""
        self.metrics = {
            'total_queries': 0,
            'dual_source_queries': 0,  # Both sources used
            'single_source_queries': 0,  # Only one source
            'no_source_queries': 0,  # Neither source had results
            'validated_responses': 0,
            'failed_validations': 0,
            'responses_with_citations': 0,
            'responses_without_citations': 0,
            'total_citations': 0,
            'vector_db_hits': 0,
            'web_search_hits': 0,
            'conflicts_detected': 0,
            'avg_response_time_ms': 0,
            'avg_retrieval_time_ms': 0
        }

        self.response_log = []  # Last 100 responses
        self.max_log_size = 100

    def log_dual_source_query(
        self,
        query: str,
        dual_results: Dict,
        merged_context: Dict,
        llm_result: Dict,
        response_time_ms: int
    ):
        """
        Log a complete dual-source query for monitoring.

        Args:
            query: User's question
            dual_results: Results from DualSourceRAG
            merged_context: Results from ContextMerger
            llm_result: Results from LLMService.generate_dual_source_response
            response_time_ms: Total response time
        """
        # Update counters
        self.metrics['total_queries'] += 1

        # Source usage
        vector_count = merged_context.get('vector_count', 0)
        web_count = merged_context.get('web_count', 0)

        if vector_count > 0 and web_count > 0:
            self.metrics['dual_source_queries'] += 1
        elif vector_count > 0 or web_count > 0:
            self.metrics['single_source_queries'] += 1
        else:
            self.metrics['no_source_queries'] += 1

        if vector_count > 0:
            self.metrics['vector_db_hits'] += 1

        if web_count > 0:
            self.metrics['web_search_hits'] += 1

        # Validation
        if llm_result.get('validated', False):
            self.metrics['validated_responses'] += 1
        else:
            self.metrics['failed_validations'] += 1

        # Citations
        if llm_result.get('has_citations', False):
            self.metrics['responses_with_citations'] += 1
        else:
            self.metrics['responses_without_citations'] += 1

        citation_count = llm_result.get('citation_count', 0)
        self.metrics['total_citations'] += citation_count

        # Conflicts
        if merged_context.get('has_conflicts', False):
            self.metrics['conflicts_detected'] += 1

        # Timing
        retrieval_time = dual_results.get('retrieval_time_ms', 0)
        self._update_avg_timing(response_time_ms, retrieval_time)

        # Create log entry
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'query': query[:100],  # Truncate for privacy
            'vector_count': vector_count,
            'web_count': web_count,
            'both_sources_used': vector_count > 0 and web_count > 0,
            'validated': llm_result.get('validated', False),
            'has_citations': llm_result.get('has_citations', False),
            'citation_count': citation_count,
            'response_time_ms': response_time_ms,
            'retrieval_time_ms': retrieval_time,
            'confidence': merged_context.get('combined_confidence', 0.0),
            'has_conflicts': merged_context.get('has_conflicts', False),
            'warnings': llm_result.get('validation_warnings', [])
        }

        # Add to response log
        self.response_log.append(log_entry)

        # Keep only last N responses
        if len(self.response_log) > self.max_log_size:
            self.response_log = self.response_log[-self.max_log_size:]

        # Log warnings if any
        if not llm_result.get('validated', False):
            print(f"[MONITOR] ⚠️  Validation failed: {query[:50]}...")
            for warning in llm_result.get('validation_warnings', []):
                print(f"[MONITOR]    - {warning}")

        if not llm_result.get('has_citations', False) and vector_count + web_count > 0:
            print(f"[MONITOR] ⚠️  No citations despite having sources: {query[:50]}...")

    def _update_avg_timing(self, response_time_ms: int, retrieval_time_ms: int):
        """Update average timing metrics."""
        total = self.metrics['total_queries']

        # Update average response time
        current_avg = self.metrics['avg_response_time_ms']
        self.metrics['avg_response_time_ms'] = (
            (current_avg * (total - 1) + response_time_ms) / total
        )

        # Update average retrieval time
        current_avg_retrieval = self.metrics['avg_retrieval_time_ms']
        self.metrics['avg_retrieval_time_ms'] = (
            (current_avg_retrieval * (total - 1) + retrieval_time_ms) / total
        )

    def get_metrics(self) -> Dict:
        """
        Get current monitoring metrics.

        Returns:
            Dict with all metrics
        """
        total = self.metrics['total_queries']

        if total == 0:
            return self.metrics

        # Calculate percentages
        metrics_with_percentages = {
            **self.metrics,
            'dual_source_percentage': (self.metrics['dual_source_queries'] / total) * 100,
            'validation_success_rate': (self.metrics['validated_responses'] / total) * 100,
            'citation_rate': (self.metrics['responses_with_citations'] / total) * 100,
            'avg_citations_per_response': self.metrics['total_citations'] / total if total > 0 else 0,
            'vector_db_usage_rate': (self.metrics['vector_db_hits'] / total) * 100,
            'web_search_usage_rate': (self.metrics['web_search_hits'] / total) * 100
        }

        return metrics_with_percentages

    def get_recent_failures(self, limit: int = 10) -> List[Dict]:
        """
        Get recent validation failures.

        Args:
            limit: Maximum number of failures to return

        Returns:
            List of recent failed validations
        """
        failures = [
            entry for entry in self.response_log
            if not entry.get('validated', False)
        ]

        return failures[-limit:]

    def get_quality_report(self) -> str:
        """
        Generate a human-readable quality report.

        Returns:
            Quality report string
        """
        metrics = self.get_metrics()
        total = metrics['total_queries']

        if total == 0:
            return "No queries processed yet."

        report = f"""
=== DUAL-SOURCE RAG QUALITY REPORT ===

Total Queries: {total}

SOURCE USAGE:
- Both sources used: {metrics['dual_source_queries']} ({metrics.get('dual_source_percentage', 0):.1f}%)
- Single source: {metrics['single_source_queries']}
- No sources: {metrics['no_source_queries']}
- Vector DB usage: {metrics.get('vector_db_usage_rate', 0):.1f}%
- Web search usage: {metrics.get('web_search_usage_rate', 0):.1f}%

VALIDATION:
- Validated responses: {metrics['validated_responses']} ({metrics.get('validation_success_rate', 0):.1f}%)
- Failed validations: {metrics['failed_validations']}

CITATIONS:
- Responses with citations: {metrics['responses_with_citations']} ({metrics.get('citation_rate', 0):.1f}%)
- Average citations per response: {metrics.get('avg_citations_per_response', 0):.1f}
- Total citations: {metrics['total_citations']}

CONFLICTS:
- Conflicts detected: {metrics['conflicts_detected']}

PERFORMANCE:
- Avg response time: {metrics['avg_response_time_ms']:.0f}ms
- Avg retrieval time: {metrics['avg_retrieval_time_ms']:.0f}ms

=== QUALITY SCORE ===
"""

        # Calculate quality score (0-100)
        score_components = {
            'dual_source_usage': metrics.get('dual_source_percentage', 0) * 0.30,  # 30% weight
            'validation_rate': metrics.get('validation_success_rate', 0) * 0.30,  # 30% weight
            'citation_rate': metrics.get('citation_rate', 0) * 0.40  # 40% weight (most important)
        }

        quality_score = sum(score_components.values())

        report += f"Overall Quality Score: {quality_score:.1f}/100\n"

        if quality_score >= 90:
            report += "Status: ✅ EXCELLENT - Zero hallucination requirements met\n"
        elif quality_score >= 75:
            report += "Status: ✓ GOOD - Minor improvements needed\n"
        elif quality_score >= 60:
            report += "Status: ⚠️  FAIR - Significant improvements needed\n"
        else:
            report += "Status: ❌ POOR - Critical issues detected\n"

        report += "="*40 + "\n"

        return report

    def get_hallucination_risk_assessment(self) -> Dict:
        """
        Assess the risk of hallucinations based on metrics.

        Returns:
            Dict with risk assessment
        """
        metrics = self.get_metrics()
        total = metrics['total_queries']

        if total == 0:
            return {
                'risk_level': 'UNKNOWN',
                'score': 0,
                'issues': ['No queries processed yet']
            }

        issues = []
        risk_score = 0  # Lower is better

        # Check citation rate
        citation_rate = metrics.get('citation_rate', 0)
        if citation_rate < 50:
            issues.append(f"Low citation rate: {citation_rate:.1f}% (target: 90%+)")
            risk_score += 30

        # Check validation rate
        validation_rate = metrics.get('validation_success_rate', 0)
        if validation_rate < 80:
            issues.append(f"Low validation rate: {validation_rate:.1f}% (target: 95%+)")
            risk_score += 25

        # Check dual-source usage
        dual_source_rate = metrics.get('dual_source_percentage', 0)
        if dual_source_rate < 70:
            issues.append(f"Low dual-source usage: {dual_source_rate:.1f}% (target: 80%+)")
            risk_score += 20

        # Check average citations
        avg_citations = metrics.get('avg_citations_per_response', 0)
        if avg_citations < 2:
            issues.append(f"Low average citations: {avg_citations:.1f} (target: 3+)")
            risk_score += 15

        # Determine risk level
        if risk_score == 0:
            risk_level = 'MINIMAL'
        elif risk_score < 20:
            risk_level = 'LOW'
        elif risk_score < 40:
            risk_level = 'MODERATE'
        elif risk_score < 60:
            risk_level = 'HIGH'
        else:
            risk_level = 'CRITICAL'

        return {
            'risk_level': risk_level,
            'risk_score': risk_score,
            'issues': issues,
            'recommendations': self._get_recommendations(issues)
        }

    def _get_recommendations(self, issues: List[str]) -> List[str]:
        """Generate recommendations based on issues."""
        recommendations = []

        for issue in issues:
            if 'citation rate' in issue.lower():
                recommendations.append("Review prompt to emphasize mandatory citation requirements")
                recommendations.append("Consider increasing temperature penalty for missing citations")

            if 'validation rate' in issue.lower():
                recommendations.append("Review validation logic for false positives")
                recommendations.append("Investigate common validation failure patterns")

            if 'dual-source usage' in issue.lower():
                recommendations.append("Check vector DB and web search connectivity")
                recommendations.append("Review query routing logic")

            if 'average citations' in issue.lower():
                recommendations.append("Enhance prompt examples to show multi-citation responses")
                recommendations.append("Add citation count to validation requirements")

        return list(set(recommendations))  # Remove duplicates

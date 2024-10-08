"""Aggregation and processing module for SEO insights"""

from typing import Dict, Any, List
from lib.logging import logger

class AggregationManager:
    def __init__(self, config):
        self.config = config

    def aggregate_insights(self, all_url_insights: List[Dict[str, Any]]) -> Dict[str, Any]:
        aggregated_insights = {
            "total_urls_analyzed": len(all_url_insights),
            "traffic_summary": {
                "increased": 0,
                "decreased": 0,
                "no_change": 0
            },
            "ranking_summary": {
                "improved": 0,
                "declined": 0,
                "no_change": 0
            },
            "page_speed_summary": {
                "improved": 0,
                "declined": 0,
                "no_change": 0
            },
            "critical_issues": {},
            "top_opportunities": {},
            "important_url_insights": {}
        }

        for insight in all_url_insights:
            url = insight.get("url", "Unknown URL")
            url_insights = insight.get("insights", {})

            # Summarize traffic changes
            if "traffic_change" in url_insights:
                direction = url_insights["traffic_change"]["direction"]
                aggregated_insights["traffic_summary"][direction] += 1

            # Summarize ranking changes
            if "ranking_changes" in url_insights:
                direction = url_insights["ranking_changes"]["direction"]
                aggregated_insights["ranking_summary"][direction] += 1

            # Summarize page speed changes
            if "page_speed_changes" in url_insights:
                direction = url_insights["page_speed_changes"]["direction"]
                aggregated_insights["page_speed_summary"][direction] += 1

            # Aggregate critical issues
            if "critical_issues" in url_insights:
                for issue in url_insights["critical_issues"]:
                    issue_type = issue["type"]
                    if issue_type in aggregated_insights["critical_issues"]:
                        aggregated_insights["critical_issues"][issue_type] += 1
                    else:
                        aggregated_insights["critical_issues"][issue_type] = 1

            # Aggregate opportunities
            if "opportunities" in url_insights:
                for opportunity in url_insights["opportunities"]:
                    opp_type = opportunity["type"]
                    if opp_type in aggregated_insights["top_opportunities"]:
                        aggregated_insights["top_opportunities"][opp_type] += 1
                    else:
                        aggregated_insights["top_opportunities"][opp_type] = 1

            # Identify important URL insights
            if self._is_important_insight(url_insights):
                aggregated_insights["important_url_insights"][url] = url_insights["overall_analysis"]

        # Sort and limit critical issues and opportunities
        aggregated_insights["critical_issues"] = dict(sorted(aggregated_insights["critical_issues"].items(), key=lambda x: x[1], reverse=True)[:5])
        aggregated_insights["top_opportunities"] = dict(sorted(aggregated_insights["top_opportunities"].items(), key=lambda x: x[1], reverse=True)[:5])

        return aggregated_insights

    def _is_important_insight(self, url_insights: Dict[str, Any]) -> bool:
        """
        Determine if a URL insight is important based on certain criteria.
        This is a simple example; you may want to expand this based on your specific needs.
        """
        if "traffic_change" in url_insights:
            traffic_change = url_insights["traffic_change"]
            if traffic_change["direction"] in ["increased", "decreased"] and abs(traffic_change["percentage"]) > 20:
                return True

        if "ranking_changes" in url_insights:
            if url_insights["ranking_changes"]["direction"] != "no_change":
                return True

        if "page_speed_changes" in url_insights:
            if url_insights["page_speed_changes"]["direction"] != "no_change":
                return True

        return False
import jinja2
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from typing import Dict, Any
from lib.logging import logger

class EmailHandler:
    def __init__(self, config):
        self.config = config
        self.sendgrid_api_key = config.api['sendgrid_api_key']
        self.sender_email = config.sender_email
        self.jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader('templates'))

    def send_report(self, recipient_email: str, subject: str, report_content: str):
        message = Mail(
            from_email=self.sender_email,
            to_emails=recipient_email,
            subject=subject,
            html_content=report_content)
        try:
            sg = SendGridAPIClient(self.sendgrid_api_key)
            response = sg.send(message)
            logger.info(f"Email sent. Status Code: {response.status_code}")
        except Exception as e:
            logger.error(f"Error sending email: {e}")


    def format_report(self, aggregated_insights: Dict[str, Any]) -> str:
        template = self.jinja_env.get_template('report_template.html')
        formatted_insights = self._format_insights(aggregated_insights)
        return template.render(insights=formatted_insights)

    def _format_insights(self, insights: Dict[str, Any]) -> Dict[str, Any]:
        formatted_insights = {
            'total_urls_analyzed': insights['total_urls_analyzed'],
            'traffic_summary': self._format_traffic_summary(insights['traffic_summary']),
            'ranking_summary': self._format_ranking_summary(insights['ranking_summary']),
            'page_speed_summary': self._format_page_speed_summary(insights['page_speed_summary']),
            'critical_issues': self._format_critical_issues(insights['critical_issues']),
            'top_opportunities': self._format_opportunities(insights['top_opportunities']),
            'important_url_insights': self._format_important_url_insights(insights.get('important_url_insights', {}))
        }
        return formatted_insights

    def _format_traffic_summary(self, traffic_summary: Dict[str, int]) -> str:
        return f"Increased: {traffic_summary['increased']}, Decreased: {traffic_summary['decreased']}, No Change: {traffic_summary['no_change']}"

    def _format_ranking_summary(self, ranking_summary: Dict[str, int]) -> str:
        return f"Improved: {ranking_summary['improved']}, Declined: {ranking_summary['declined']}, No Change: {ranking_summary['no_change']}"

    def _format_page_speed_summary(self, page_speed_summary: Dict[str, int]) -> str:
        return f"Improved: {page_speed_summary['improved']}, Declined: {page_speed_summary['declined']}, No Change: {page_speed_summary['no_change']}"

    def _format_critical_issues(self, critical_issues: Dict[str, int]) -> str:
        return ', '.join([f"{issue}: {count}" for issue, count in critical_issues.items()])

    def _format_opportunities(self, opportunities: Dict[str, int]) -> str:
        return ', '.join([f"{opportunity}: {count}" for opportunity, count in opportunities.items()])

    def _format_important_url_insights(self, important_url_insights: Dict[str, str]) -> str:
        return ', '.join([f"{url}: {insight}" for url, insight in important_url_insights.items()])
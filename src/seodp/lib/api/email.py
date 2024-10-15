"""Email handler module for sending reports via email."""

import jinja2
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List
from loguru import logger
import os

from settings import Config


class EmailHandler:
    def __init__(self, config: Config):
        self.config = config
        self.smtp_server = "live.smtp.mailtrap.io"
        self.port = 587
        self.login = config.api.mailtrap_login
        self.password = config.api.mailtrap_password
        self.sender_email = config.api.mailtrap_sender_email
        self.recipient_email = config.api.recipient_email
        self.report_email_subject = config.report_email_subject
        template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
        self.jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))

    def send_report(self, report_content: str):
        message = MIMEMultipart()
        message["From"] = self.sender_email
        message["To"] = self.recipient_email
        message["Subject"] = self.report_email_subject
        message.attach(MIMEText(report_content, "html"))

        try:
            with smtplib.SMTP(self.smtp_server, self.port) as server:
                server.starttls()
                server.login(self.login, self.password)
                server.sendmail(self.sender_email, self.recipient_email, message.as_string())
            logger.info(f"Email sent successfully to {self.recipient_email}")
        except Exception as e:
            logger.error(f"Error sending email: {e}")

    def format_report(self, aggregated_insights: Dict[str, Any]) -> str:
        template = self.jinja_env.get_template('report_template.html')
        formatted_insights = self._format_insights(aggregated_insights)
        return template.render(insights=formatted_insights)

    def _format_insights(self, insights: Dict[str, Any]) -> Dict[str, Any]:
        formatted_insights = {
            'total_urls_analyzed': insights['total_urls_analyzed'],
            'significant_traffic_changes': self._format_changes(insights.get('significant_traffic_changes', [])),
            'significant_keyword_changes': self._format_changes(insights.get('significant_keyword_changes', [])),
            'significant_content_changes': self._format_changes(insights.get('significant_content_changes', [])),
            'significant_changes_to_prior_or_next_pages': self._format_changes(insights.get('significant_changes_to_prior_or_next_pages', [])),
            'significant_changes_to_referral_sources': self._format_changes(insights.get('significant_changes_to_referral_sources', [])),
            'significant_changes_to_organic_search_sources': self._format_changes(insights.get('significant_changes_to_organic_search_sources', [])),
            'causal_relationships_between_changes': self._format_changes(insights.get('causal_relationships_between_changes', []))
        }
        return formatted_insights

    def _format_changes(self, changes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        formatted_changes = []
        for change in changes:
            formatted_change = {
                'description': change.get('description', ''),
                'details': change.get('details', ''),
                'importance_score': change.get('importance_score', 0),
                'current_value': change.get('current_value', 0),
                'prior_value': change.get('prior_value', 0),
                'change_absolute': change.get('change_absolute', 0),
                'change_percentage': change.get('change_percentage', 0),
                'url': change.get('url', '')
            }
            formatted_changes.append(formatted_change)
        return formatted_changes
"""Settings for the SEO Data Platform."""

from pathlib import Path
from typing import Type, Tuple, List, Optional

import pydantic
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
    PydanticBaseSettingsSource,
    YamlConfigSettingsSource,
)
from typing_extensions import Self


class APIConfig(BaseSettings):
    """Configuration settings for external APIs."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", frozen=True)

    service_account_file: pydantic.FilePath = pydantic.Field(validation_alias="service_account_file_path")
    subject_email: pydantic.EmailStr
    scrapingbee_api_key: str
    gemini_api_key: str
    psi_api_key: str
    mailtrap_login: str
    mailtrap_password: str
    mailtrap_sender_email: pydantic.EmailStr
    recipient_email: pydantic.EmailStr
    psi_timeout: pydantic.PositiveInt = 60


class Config(BaseSettings):
    """Configuration settings for the SEO Data Platform."""

    model_config = SettingsConfigDict(frozen=True)

    api: APIConfig

    db_file: Path
    gemini_model: str = 'gemini-1.5-pro'
    low_traffic_threshold: pydantic.NonNegativeInt = 100
    schedule: str = 'monthly'
    site_url: str
    property_id: str
    sitemap_file: Optional[str] = None
    sitemap_urls: Optional[List[str]] = None
    test_sitemap_urls: Optional[List[str]] = None
    report_email_subject: str = 'SEO Insights Report'
    report_significance_threshold: pydantic.NonNegativeInt = 25
    top_n: pydantic.NonNegativeInt = 10
    report_topics: List[str] = [
        'Significant traffic changes',
        'Significant keyword changes',
        'Significant content changes',
        'Significant changes to prior or next pages',
        'Significant changes to referral sources',
        'Significant changes to organic search sources',
        'Causal relationships between changes'
    ]
    max_insights: pydantic.NonNegativeInt = 5

    @pydantic.model_validator(mode="after")
    def check_sitemap_file_or_urls(self) -> Self:
        """Ensure that either a sitemap file or URLs are provided."""
        if not self.sitemap_file and not self.sitemap_urls:
            raise ValueError("No sitemap URLs or file provided in configuration.")
        return self

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        """Customizes the settings sources for the SEO Data Platform.

        Uses only init settings and a YAML file for configuration.
        """
        return (
            init_settings,
            # Add yaml config source
            YamlConfigSettingsSource(settings_cls, yaml_file="seodpconfig.yaml"),
        )


API_CONFIG = APIConfig()
CONFIG = Config(api=API_CONFIG)

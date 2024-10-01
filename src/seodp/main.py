"""Main module for the SEO Data Puller."""

from lib.extractors.ga4 import GA4Extractor
from lib.extractors.gsc import GSCExtractor
from settings import CONFIG

def main():
    ga4_extractor = GA4Extractor(CONFIG.api.service_account_file, CONFIG.api.subject_email)
    gsc_extractor = GSCExtractor(CONFIG.api.service_account_file, CONFIG.api.subject_email)

    ga4_extractor.authenticate()
    gsc_extractor.authenticate()

    ga4_data = ga4_extractor.extract_data(
        CONFIG.property_id,
        CONFIG.page_url,
        CONFIG.start_date,
        CONFIG.end_date
    )

    gsc_data = gsc_extractor.extract_data(
        CONFIG.site_url,
        CONFIG.page_url,
        CONFIG.start_date,
        CONFIG.end_date
    )

    # Combine the data
    combined_data = {**ga4_data, **gsc_data}

    print(f"Data for {CONFIG.page_url}:")
    print(f"Ranking keywords: {combined_data['ranking_keywords']}")
    print(f"Previous pages: {combined_data['previous_pages']}")
    print(f"Next pages: {combined_data['next_pages']}")
    print(f"Bounce rate: {combined_data['bounce_rate']}")
    print(f"Top referring sites: {combined_data['referring_sites']}")

if __name__ == "__main__":
    main()
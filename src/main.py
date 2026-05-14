"""
This is the main entry point for the newscaster application.
"""
import os
import sys
import django

def setup_django():
    """
    Sets up the Django environment for standalone script usage.
    """
    # Add the Django project to the Python path
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'newscaster_site')))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dj_newscaster.settings')
    django.setup()

def main():
    """
    Orchestrates the entire process of scraping, summarizing, and storing news.
    """
    setup_django()
    from news.models import WebSource, Article
    import scraper
    import summarizer

    print("Starting newscaster process...")

    # Step 1: Get the web source configuration from the Django database
    try:
        source = WebSource.objects.get(name="eduskunta_proposals")
    except WebSource.DoesNotExist:
        print("Could not find the 'eduskunta_proposals' source in the Django database.")
        print("Please run the setup_database.py script first.")
        return

    # Step 2: Scrape the source for new articles
    scraped_articles = scraper.scrape_news(source)

    if not scraped_articles:
        print("No new articles were scraped.")
        return

    print(f"\nSuccessfully scraped {len(scraped_articles)} articles. Now summarizing and saving...")

    for article_data in scraped_articles:
        # Check if the article already exists before processing
        if Article.objects.filter(source_url=article_data['source_url']).exists():
            print(f"Article '{article_data['title']}' already exists in DB, skipping.")
            continue

        # Add default values for missing fields
        article_data.setdefault('primary_category', None)
        article_data.setdefault('tags', [])

        # Step 3: Summarize the raw content in all three languages
        print(f"--- Summarizing article: {article_data['title']} ---")
        summary_fi = summarizer.summarize_text(
            article_data['title'],
            article_data['subject'], 
            article_data['state'], 
            article_data['stage'], 
            article_data['raw_content'], 
            article_data['primary_category'],
            article_data['tags'],
            language="Finnish"
        )
        summary_sv = summarizer.summarize_text(
            article_data['title'], 
            article_data['subject'], 
            article_data['state'], 
            article_data['stage'], 
            article_data['raw_content'], 
            article_data['primary_category'],
            article_data['tags'],
            language="Swedish"
        )
        summary_en = summarizer.summarize_text(
            article_data['title'], 
            article_data['subject'], 
            article_data['state'], 
            article_data['stage'], 
            article_data['raw_content'], 
            article_data['primary_category'],
            article_data['tags'],
            language="English"
        )

        if summary_fi and summary_sv and summary_en:
            # Step 4: Create and save a complete Article object using Django ORM
            article = Article.objects.create(
                title_fi=article_data['title'],
                subject_fi=article_data['subject'],
                state_fi=article_data['state'],
                stage_fi=article_data['stage'],
                title_sv=summary_sv.get("title"),
                subject_sv=summary_sv.get("subject"),
                state_sv=summary_sv.get("state"),
                stage_sv=summary_sv.get("stage"),
                title_en=summary_en.get("title"),
                subject_en=summary_en.get("subject"),
                state_en=summary_en.get("state"),
                stage_en=summary_en.get("stage"),
                progress_stages=article_data['progress_stages'],
                current_stage=article_data['current_stage'],
                source_url=article_data['source_url'],
                raw_content=article_data['raw_content'],
                
                summary_proposal_details_fi=summary_fi.get("proposal_details"),
                summary_citizen_impact_fi=summary_fi.get("citizen_impact"),

                summary_proposal_details_sv=summary_sv.get("proposal_details"),
                summary_citizen_impact_sv=summary_sv.get("citizen_impact"),

                summary_proposal_details_en=summary_en.get("proposal_details"),
                summary_citizen_impact_en=summary_en.get("citizen_impact"),
                
                source=source # Link to the WebSource object
            )
            
            print(f"Article '{article.title_fi}' saved to the Django database with all translations.")

        else:
            print(f"Failed to generate all summaries for article: {article_data['title']}")

    print("\nNewscaster process finished.")

if __name__ == "__main__":
    main()

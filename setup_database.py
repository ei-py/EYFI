"""
This is a one-off script to initialize the database and populate it with the
initial web source configurations.
"""
import os
import sys
import django

def setup_django():
    """
    Sets up the Django environment for standalone script usage.
    """
    # Add the Django project to the Python path
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'newscaster_site')))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dj_newscaster.settings')
    django.setup()

def main():
    """
    Initializes the Django database and adds/updates the eduskunta.fi source.
    """
    setup_django()
    from news.models import WebSource, Article # Import Django models after setup

    print("Populating Django database with WebSource configuration...")

    source_name = "eduskunta_proposals"
    
    source_data = {
        "description": "Finnish Parliament government proposals.",
        "base_url": "https://www.eduskunta.fi",
        "paths": {
            "start": "/FI/Sivut/default.aspx"
        },
        "selectors": {
            "cookie_accept_button": "button.btn-consent-accept",
            "proposals_page_link": "a[href*='asiatyyppinimi%3Ahallituksen%20esitys']",
            "article_link": "div.ms-srch-item-title h3 a",
            "progress_bar": "ul#edk-timeline li",
            "state": "//dt[contains(text(), \"Asian tila\")]/following-sibling::dd[1]",
            "stage": "dd#edk-kasittelyvaihe-value",
            "document_link": "div.ViiteTeksti > a:first-child",
            "document_number_title": "div#IdentifiointiOsa span.edk-EduskuntaTunniste", # e.g., HE 201/2025 vp
            "document_subject_text": "div#IdentifiointiOsa span.Nimeke", # The detailed subject
            "document_content": "div.HallituksenEsitys"
        }
    }

    # Use Django ORM's update_or_create to add/update the WebSource
    source_obj, created = WebSource.objects.update_or_create(
        name=source_name,
        defaults=source_data
    )

    if created:
        print(f"Source '{source_name}' created in the Django database.")
    else:
        print(f"Source '{source_name}' updated in the Django database.")
    
    # Clear any existing articles to ensure a fresh start
    print("Clearing all existing articles from the database...")
    Article.objects.all().delete()
    print("All articles cleared.")

    print("Setup complete.")

if __name__ == "__main__":
    main()

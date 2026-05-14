"""
This module handles saving and retrieving the summarized news articles.
"""
import sqlite3
import json
from news.models import WebSource, Article

DB_FILE = "newscaster.db"

def init_db():
    """
    Initializes the database and creates the necessary tables if they don't exist.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Create sources table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sources (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        description TEXT,
        base_url TEXT NOT NULL,
        paths TEXT,
        selectors TEXT,
        custom_logic TEXT
    )
    """)

    # Create articles table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS articles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_id INTEGER,
        title TEXT NOT NULL,
        source_url TEXT NOT NULL UNIQUE,
        raw_content TEXT,
        summary_proposal_details TEXT,
        summary_status_and_outcome TEXT,
        summary_citizen_impact TEXT,
        FOREIGN KEY (source_id) REFERENCES sources (id)
    )
    """)

    conn.commit()
    conn.close()
    print("Database initialized successfully.")

def add_source(source: WebSource):
    """
    Adds a new WebSource to the database.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO sources (name, description, base_url, paths, selectors, custom_logic) VALUES (?, ?, ?, ?, ?, ?)",
        (
            source.name,
            source.description,
            source.base_url,
            json.dumps(source.paths),
            json.dumps(source.selectors),
            json.dumps(source.custom_logic),
        ),
    )
    conn.commit()
    conn.close()
    print(f"Source '{source.name}' added to the database.")

def get_source_by_name(name: str) -> WebSource | None:
    """
    Retrieves a WebSource from the database by its unique name.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sources WHERE name = ?", (name,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return WebSource(
            id=row[0],
            name=row[1],
            description=row[2],
            base_url=row[3],
            paths=json.loads(row[4]),
            selectors=json.loads(row[5]),
            custom_logic=json.loads(row[6]) if row[6] else None,
        )
    return None

def article_exists(source_url: str) -> bool:
    """
    Checks if an article with the given source_url already exists in the database.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM articles WHERE source_url = ?", (source_url,))
    row = cursor.fetchone()
    conn.close()
    return row is not None

def save_article(article: Article):
    """
    Saves a single Article object to the database.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO articles (source_id, title, source_url, raw_content, 
                              summary_proposal_details, summary_status_and_outcome, summary_citizen_impact,
                              primary_category, tags)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            article.source_id,
            article.title,
            article.source_url,
            article.raw_content,
            article.summary.proposal_details,
            article.summary.status_and_outcome,
            article.summary.citizen_impact,
            article.primary_category,
            json.dumps(article.tags)
        ),
    )
    conn.commit()
    conn.close()
    print(f"Article '{article.title}' saved to the database.")

def get_all_articles() -> list[Article]:
    """
    Retrieves all articles from the database and returns them as a list of Article objects.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM articles")
    rows = cursor.fetchall()
    conn.close()

    articles = []
    for row in rows:
        #summary = Summary(
        #    proposal_details=row[5],
        #    status_and_outcome=row[6],
        #    citizen_impact=row[7],
        #)
        article = Article(
            id=row[0],
            source_id=row[1],
            title=row[2],
            source_url=row[3],
            raw_content=row[4],
        #    summary=summary,
        )
        articles.append(article)
    
    return articles

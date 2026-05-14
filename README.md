# EYFI - Eduskunta Voting Forum Interface

EYFI is a Python-based application that scrapes government legislative matters from the Finnish Parliament (Eduskunta), summarizes them using AI, and presents them as digestible cards in a Django web application. Visitors can view summaries of government matters affecting laws and policies, then cast their own votes to compare their positions against government voting records.

## Project Structure

- `newscaster_site/`: The Django web application for displaying government matters as interactive cards.
- `src/`: The Python source code for scraping Eduskunta matters and generating summaries.
- `requirements.txt`: A list of Python dependencies for the project.
- `setup_database.py`: A script to initialize the database with the Eduskunta web source configuration.
- `newscaster.db`: The SQLite database file storing matters, votes, and user data.

## LLM Instructions

This project uses a generative AI model in the `summarizer.py` module to summarize government matters and create voter-friendly summaries.

### Key Concepts

- **WebSource**: A model that configures the web scraper to extract legislative matters from `https://www.eduskunta.fi/FI/Sivut/default.aspx` using URLs, paths, and CSS selectors.
- **Matter**: The main model storing government legislative matters, including raw content and AI-generated summaries explaining the topic, proposed changes, and voter impact.
- **Vote**: A user vote model tracking how individual visitors vote on government matters, enabling comparison between citizen and government positions.
- **Scraper**: The `src/scraper.py` module uses `selenium` to scrape government matters from the Eduskunta website.
- **Summarizer**: The `src/summarizer.py` module uses a generative AI model (`gemini-2.0-flash`) to create concise, voter-friendly summaries that explain: (1) what the matter is about, (2) what changes are proposed, and (3) how it would impact voters and policies.

### How to Work with the Code

- **Virtual Environment**: The virtual environment for this project is located at `~/.venvs/newscaster/bin/activate`. Activate it with:
  ```bash
  source ~/.venvs/newscaster/bin/activate
  ```
- **Dependencies**: Install the required Python packages using pip:
  ```bash
  pip install -r requirements.txt
  ```
- **Environment**: The summarizer requires a Gemini API key. Create a `.env` file in the root directory and add your API key:
  ```
  GEMINI_API_KEY_UNSCRAMBLE="YOUR_API_KEY"
  ```
- **Database Setup**: Before running the application, you need to set up the database and create the initial `WebSource` configuration.
  - Apply Django migrations:
    ```bash
    python newscaster_site/manage.py migrate
    ```
  - Run the `setup_database.py` script:
    ```bash
    python setup_database.py
    ```
- **Running the Scraper**: To scrape and summarize new government matters, run the `main.py` script:
  ```bash
  python src/main.py
  ```
- **Running the Web Application**: To view government matters and cast votes, start the Django development server:
  ```bash
  python newscaster_site/manage.py runserver
  ```
  Then visit the voting forum to see matter cards and compare your votes against government positions.

### Goal for the LLM

The LLM serves a critical role in making government work accessible and engaging to voters. It must generate voter-friendly summaries that are:

1. **Clear and Concise**: Explain complex legislative matters in plain language
2. **Comprehensive**: Cover the topic, proposed changes, and voter impact
3. **Engaging**: Encourage voters to learn more by providing links to source material
4. **Neutral**: Present information objectively to enable informed voting

The prompt for the LLM is located in `src/summarizer.py` inside the `summarize_text` function. The LLM processes raw matter details and returns a JSON object containing a title, subject, summary of the matter, summary of proposed changes, and summary of voter/policy impact. The goal is to reduce time spent researching while increasing participation in understanding government decisions.

## Known Issues

### Search Bar and Results Styling
- The search bar functionality with HTMX is implemented, but the visual presentation of the expanding search box and floating results needs refinement to match the desired Google-like appearance. The integration of the search results within the navbar's layout requires further CSS adjustments.
- Each search result should ideally be a single row displaying only the subject, which has been attempted but may need further styling tweaks.

### Article Data Extraction
- **Article Titles**: Some article titles might not be extracted or processed correctly from the Eduskunta website. Specifically, the "vp" suffix sometimes remains in the displayed title, indicating an issue with the title parsing logic in `src/scraper.py`.
- **Missing Subjects**: Certain scraped articles may be missing their subjects. This could stem from inconsistencies in the web source's HTML structure or an issue with the subject extraction logic in `src/scraper.py`.
- **Missing Titles**: Some articles might still be scraped without a title, despite the updated selectors for `document_number_title`. This indicates that the `span.edk-EduskuntaTunniste` element might not always be present or might have varying content for certain article types.

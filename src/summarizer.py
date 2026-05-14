"""
This module handles the summarization of text using an LLM.
"""
import os
import json
import google.generativeai as genai
from dotenv import load_dotenv
#from news.models import Summary

def summarize_text(title: str, subject: str, state: str, stage: str, text: str, primary_category: str | None, tags: list[str], language: str = "Finnish") -> dict | None:
    """
    Takes a title, subject, state, stage, text, primary_category, tags, sends them to choice of LLM, 
    and returns a dictionary with the structured summary and translated 
    title/subject/state/stage in the specified language.
    """
    # Load environment variables from .env file
    load_dotenv()
    
    api_key = os.getenv("GEMINI_API_KEY_UNSCRAMBLE")
    print(f"DEBUG: Loaded GEMINI_API_KEY_UNSCRAMBLE: {api_key[:5]}...{api_key[-5:]}") # Print partial key for debugging, avoid full key in logs
    if not api_key:
        print("Error: GEMINI_API_KEY_UNSCRAMBLE not found in environment variables.")
        return None

    genai.configure(api_key=api_key)
    
    model = genai.GenerativeModel('gemini-2.0-flash')

    prompt = f"""
    You are a multilingual summarizer. Based on the following Finnish government proposal, please provide a structured response in {language}.
    The response must be a valid JSON object with eight specific keys: "title", "subject", "state", "stage", "proposal_details", "citizen_impact",
    "primary_category" and "tags".

    - "title": Translate the title "{title}" to {language}.
    - "subject": Translate the subject "{subject}" to {language}.
    - "state": Translate the state "{state}" to {language}.
    - "stage": Translate the stage "{stage}" to {language}.
    - "proposal_details": Explain what the proposal is about in {language}. Ideally within three sentences, do not exceed six sentences.
    - "citizen_impact": Explain the potential impact on a typical citizen in {language}. Ideally within three sentences, do not exceed six sentences.
    - "primary_category": Provide a category for the article based on its content, if a primary_category is provided, use it: {primary_category}. This category should highlight to the viewer what the article is about.
    - "tags": Create a maximum of six tags for the article which improve the chances for the user to find the article through a search, using the provided tags: {tags}, compatible with a models.JSONField() format.

    Here is the full text of the proposal to use for the summary:
    ---
    {text}
    ---
    """

    try:
        print("Generating summary with Gemini API...")
        response = model.generate_content(prompt)
        
        # Clean up the response to extract the JSON part.
        # Gemini sometimes wraps the JSON in ```json ... ```
        response_text = response.text.strip().replace("```json", "").replace("```", "").strip()
        
        summary_data = json.loads(response_text)
        
        print(f"Summary in {language} generated successfully.")
        return summary_data

    except Exception as e:
        print(f"An error occurred during summarization: {e}")
        return None

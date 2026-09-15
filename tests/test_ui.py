import pytest
import time
from streamlit.testing.v1 import AppTest
from unittest.mock import patch, MagicMock

# --- UI Integration / E2E Tests ---

def test_ui_initial_state():
    """Test that the app loads properly and shows initial state warnings."""
    at = AppTest.from_file("app.py", default_timeout=10).run()
    
    assert not at.exception
    assert at.title[0].value == "📡 ReferralRadar"
    
    # Check that sidebar headers exist
    assert "1. Upload Your Data" in [h.value for h in at.sidebar.header]
    
    # Check that it asks for files/keys in the main view when empty
    assert len(at.info) > 0
    assert "👈 Please upload your Resume and Connections CSV" in at.info[0].value

@patch("core.crawler.CrawlerClient.scrape_url")
@patch("core.ats_client.ATSClient.fetch_job")
@patch("core.llm.LLMClient.generate_templates")
def test_ui_targeted_link_flow(mock_generate_templates, mock_fetch_job, mock_scrape_url):
    """
    Simulate a user uploading files, entering API keys, and processing a targeted link.
    We mock the external API calls (Firecrawl/LLM) so it runs instantly without needing real keys.
    """
    at = AppTest.from_file("app.py", default_timeout=10).run()
    
    # Mocking the session state for uploaded files to bypass the file_uploader in tests.
    # Note: Streamlit AppTest doesn't natively support full file uploads via the UI element easily yet,
    # so we inject the parsed data into session state directly, simulating what happens after upload.
    at.session_state.resume_data = {
        "raw_text": "Python React SQL",
        "keywords": ["python", "react", "sql"]
    }
    
    # Simulate a ConnectionMatcher instance
    from core.matcher import ConnectionMatcher
    import io
    csv_content = "Notes\nNotes\nNotes\nFirst Name,Last Name,Email Address,Company,Position,Connected On\nJohn,Doe,,Google,SWE,"
    fake_file = io.StringIO(csv_content)
    at.session_state.matcher = ConnectionMatcher(fake_file)
    
    # Run the app with this state
    at.run()
    
    # Check that it now asks for Firecrawl API Key
    assert len(at.warning) > 0
    assert "Firecrawl API key" in at.warning[0].value
    
    # Simulate user typing in the Firecrawl API key in the sidebar
    # We find the text_input by its label
    for text_input in at.sidebar.text_input:
        if "Firecrawl" in text_input.label:
            text_input.input("fake_fc_key").run()
            break
            
    # The default LLM provider is "Cloud (Groq/OpenRouter/OpenAI)", so we need an LLM key too
    for text_input in at.sidebar.text_input:
        if "LLM API Key" in text_input.label:
            text_input.input("fake_llm_key").run()
            break
            
    # Now we should see the Mode radio buttons because requirements are met
    assert len(at.radio) > 0
    
    # Select Targeted Link mode
    at.radio[0].set_value("Targeted Link (Paste a specific job)").run()
    
    # Mock the API responses
    mock_fetch_job.return_value = {
        "title": "Software Engineer",
        "company": "Google",
        "description": "Needs python and react",
        "posted_date": "Today",
        "source": "Mock ATS"
    }
    
    mock_generate_templates.return_value = {
        "tier1_email": {"subject": "Test", "body": "Hi {first_name}"},
        "tier1_dm": {"body": "Hi {first_name}"}
    }
    
    # Enter URL and click process
    for text_input in at.text_input:
        if "Paste Job Posting URL" in text_input.label:
            text_input.input("https://boards.greenhouse.io/google/jobs/123").run()
            break
            
    # Click "Process Job" button
    for btn in at.button:
        if btn.label == "Process Job":
            btn.click().run()
            break
            
    # Verify the dataframe is populated
    assert at.session_state.results_df is not None
    assert not at.session_state.results_df.empty
    
    # Verify the results on screen
    assert len(at.dataframe) > 0
    assert len(at.expander) > 0 # Should expand to show messages
    assert "Message for John Doe" in at.expander[0].label

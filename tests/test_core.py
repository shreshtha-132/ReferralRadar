import pytest
import io
import pandas as pd
from core.parser import extract_keywords, analyze_job_match
from core.ats_client import ATSClient
from core.matcher import ConnectionMatcher
from core.llm import LLMClient
from config import SYSTEM_PROMPT

# --- 1. Parser Tests ---
def test_extract_keywords():
    sample_text = "I have 5 years of experience in Python, Javascript, and React. I also know SQL."
    keywords = extract_keywords(sample_text)
    
    assert "python" in keywords
    assert "javascript" in keywords
    assert "react" in keywords
    assert "sql" in keywords
    assert "java" not in keywords # Should not falsely match from javascript

def test_analyze_job_match():
    resume_kw = ["python", "react", "sql"]
    job_desc = "Looking for a fullstack dev with Python, React, and Node.js."
    
    result = analyze_job_match(resume_kw, job_desc)
    
    assert "python" in result["matching_keywords"]
    assert "react" in result["matching_keywords"]
    assert "node.js" in result["missing_keywords"]
    assert result["match_percent"] > 0
    assert result["match_percent"] < 100

# --- 2. ATS Client Tests ---
def test_identify_ats():
    greenhouse_url = "https://boards.greenhouse.io/openai/jobs/12345"
    lever_url = "https://jobs.lever.co/notion/67890"
    random_url = "https://careers.google.com/jobs/results/"
    
    ats, groups = ATSClient.identify_ats(greenhouse_url)
    assert ats == "greenhouse"
    assert groups == ("openai", "12345")
    
    ats, groups = ATSClient.identify_ats(lever_url)
    assert ats == "lever"
    
    ats, groups = ATSClient.identify_ats(random_url)
    assert ats is None

# --- 3. Matcher Tests ---
def test_connection_matcher():
    # Simulate a CSV file in memory
    csv_content = """Notes\nNotes\nNotes\nFirst Name,Last Name,Email Address,Company,Position,Connected On
John,Doe,john@example.com,Google LLC,Software Engineer,2023-01-01
Jane,Smith,,Microsoft,Product Manager,2023-01-02
Bob,Johnson,,Netflix,Data Scientist,2023-01-03
"""
    fake_file = io.StringIO(csv_content)
    
    matcher = ConnectionMatcher(fake_file)
    
    # Test Tier 1 (Direct Match)
    res_google = matcher.find_referrals("Google")
    assert len(res_google["tier1"]) == 1
    assert res_google["tier1"][0]["first_name"] == "John"
    
    # Test Tier 2 (Bridge Match) - Since Netflix and Microsoft are in the tech_giants cluster
    res_netflix_target = matcher.find_referrals("Apple") 
    # 'Apple' isn't in our CSV, but Netflix, Microsoft, and Google are in the same 'tech_giants' peer group.
    # So if we search Apple, Tier 2 should return John (Google), Jane (Microsoft), and Bob (Netflix).
    assert len(res_netflix_target["tier1"]) == 0
    assert len(res_netflix_target["tier2"]) == 3
    
    names = [c["first_name"] for c in res_netflix_target["tier2"]]
    assert "John" in names
    assert "Jane" in names
    assert "Bob" in names

# --- 4. LLM Tests (Deterministic fill only) ---
def test_fill_template():
    # We don't test the actual API call here to avoid needing an API key in unit tests.
    # We just test our deterministic templating logic.
    llm = LLMClient(provider="local") 
    
    template = {
        "subject": "Referral for {first_name}",
        "body": "Hi {first_name}, I saw a role at your company: {job_url}"
    }
    
    conn = {"first_name": "Alice"}
    job_url = "https://example.com/job"
    
    result = llm.fill_template(template, conn, job_url)
    
    assert "Subject: Referral for Alice" in result
    assert "Hi Alice," in result
    assert "https://example.com/job" in result

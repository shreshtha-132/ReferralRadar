import pdfplumber
import re

# A basic list of tech keywords for deterministic matching.
TECH_KEYWORDS = {
    "python", "java", "c++", "c#", "javascript", "typescript", "react", "angular", "vue",
    "node.js", "nodejs", "express", "django", "flask", "fastapi", "spring", "aws", "azure", "gcp",
    "docker", "kubernetes", "sql", "mysql", "postgresql", "mongodb", "redis",
    "machine learning", "data science", "pandas", "numpy", "scikit-learn", "tensorflow", "pytorch",
    "html", "css", "git", "linux", "agile", "scrum", "rest api", "graphql", "ci/cd",
    "frontend", "backend", "fullstack", "ui/ux", "figma", "golang", "rust", "ruby"
}

def extract_text_from_pdf(pdf_file):
    """Extracts all text from a given PDF file object."""
    text = ""
    try:
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
    except Exception as e:
        raise ValueError(f"Could not read PDF: {str(e)}")
    return text

def extract_keywords(text):
    """Finds known technical keywords in the text."""
    text_lower = text.lower()
    # Simple tokenization
    words = set(re.findall(r'\b[\w\.\+-]+\b', text_lower))
    
    found_keywords = set()
    for kw in TECH_KEYWORDS:
        if " " in kw or "/" in kw:
            # For multi-word keywords or things like ci/cd, check raw text
            if kw in text_lower:
                found_keywords.add(kw)
        else:
            # For single words, check exact word matches to avoid substring issues
            if kw in words:
                found_keywords.add(kw)
    
    return list(found_keywords)

def extract_skills_from_resume(pdf_file):
    """Processes a resume PDF and returns raw text and found keywords."""
    text = extract_text_from_pdf(pdf_file)
    keywords = extract_keywords(text)
    return {
        "raw_text": text,
        "keywords": keywords
    }

def analyze_job_match(resume_keywords, job_description):
    """Compares resume keywords to job description keywords to find gaps."""
    job_keywords = extract_keywords(job_description)
    
    if not job_keywords:
        return {
            "match_percent": 0,
            "matching_keywords": [],
            "missing_keywords": [],
            "job_keywords": []
        }
        
    resume_set = set(resume_keywords)
    job_set = set(job_keywords)
    
    matching = list(resume_set.intersection(job_set))
    missing = list(job_set.difference(resume_set))
    
    match_percent = int((len(matching) / len(job_set)) * 100) if job_set else 0
    
    return {
        "match_percent": match_percent,
        "matching_keywords": matching,
        "missing_keywords": missing,
        "job_keywords": list(job_set)
    }

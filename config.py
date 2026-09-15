import re

# ==========================================
# ATS (Applicant Tracking System) URL Patterns
# ==========================================
# We use these to detect if a URL belongs to a known ATS so we can hit their public API directly.
ATS_PATTERNS = {
    "greenhouse": re.compile(r"boards\.greenhouse\.io/([^/]+)/jobs/(\d+)"),
    "lever": re.compile(r"jobs\.lever\.co/([^/]+)/([^/]+)"),
    "ashby": re.compile(r"jobs\.ashbyhq\.com/([^/]+)/([^/]+)"),
}

# ==========================================
# Tier 2 (Peer/Bridge) Company Mappings
# ==========================================
# If the user doesn't have a connection at the target company (Tier 1),
# we look for connections at these peer companies (Tier 2) to ask for an introduction.
PEER_COMPANIES = {
    "tech_giants": ["Google", "Meta", "Apple", "Amazon", "Netflix", "Microsoft"],
    "finance": ["Goldman Sachs", "JPMorgan", "Morgan Stanley", "Citadel", "Jane Street"],
    "consulting": ["McKinsey", "Bain", "BCG", "Deloitte", "PwC", "EY", "KPMG"],
    # We map companies to their cluster. E.g., if target is Google, we look for tech_giants.
}

def get_peer_companies(target_company):
    """Returns a list of peer companies for a given target company."""
    target_lower = target_company.lower()
    for cluster, companies in PEER_COMPANIES.items():
        if any(c.lower() in target_lower or target_lower in c.lower() for c in companies):
            return [c for c in companies if c.lower() not in target_lower]
    return []

# ==========================================
# LLM Base Prompts (For generating 4 templates per job)
# ==========================================

# We prompt the LLM ONCE per job to generate these 4 templates.
# The LLM must leave {first_name} and other placeholders exactly as is, so we can fill them later.

SYSTEM_PROMPT = """You are an expert career coach helping a job seeker draft referral request messages.
You will be provided with:
1. Target Job Title
2. Target Company
3. Overlapping Keywords (skills the user has that the job requires)
4. Job URL (if available)

Your task is to generate EXACTLY 4 message templates. 
CRITICAL RULES:
- Keep them short (3-4 sentences max).
- Do not use cliché openings like "I was impressed by your profile" or "I hope this email finds you well".
- Mention the role and company.
- Include 2-3 of the provided overlapping keywords naturally.
- YOU MUST USE the exact placeholders `{first_name}` and `{job_url}` where appropriate. DO NOT fill them in.
- The tone should be professional but conversational and direct.

Generate the output in the following JSON format ONLY:
{
    "tier1_email": {"subject": "...", "body": "... (Direct referral ask, full email format) ..."},
    "tier1_dm": {"body": "... (Direct referral ask, short LinkedIn DM format) ..."},
    "tier2_email": {"subject": "...", "body": "... (Asking if they know anyone at the target company, full email) ..."},
    "tier2_dm": {"body": "... (Asking if they know anyone at the target company, short LinkedIn DM format) ..."}
}
"""

USER_PROMPT_TEMPLATE = """
Target Job Title: {job_title}
Target Company: {company}
Overlapping Keywords: {keywords}
Job URL: {job_url}

Generate the 4 templates as instructed.
"""

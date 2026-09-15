import streamlit as st
import pandas as pd
import time
import io
from core.parser import extract_skills_from_resume, analyze_job_match
from core.ats_client import ATSClient
from core.crawler import CrawlerClient
from core.matcher import ConnectionMatcher
from core.llm import LLMClient

st.set_page_config(page_title="ReferralRadar | AI-Powered Job Referral Finder", layout="wide", page_icon="🎯")

# --- UI Header ---
st.title("🎯 ReferralRadar")
st.markdown("""
Welcome to ReferralRadar! This tool helps you find jobs matching your resume and instantly tells you exactly **who** in your network can refer you, complete with a drafted message you can copy and send.
""")

# --- State Management ---
if 'resume_data' not in st.session_state:
    st.session_state.resume_data = None
if 'matcher' not in st.session_state:
    st.session_state.matcher = None
if 'results_df' not in st.session_state:
    st.session_state.results_df = None

# --- Sidebar: User Input & Config ---
st.sidebar.header("1. Upload Your Data")

st.sidebar.markdown("**Resume (PDF)**")
resume_file = st.sidebar.file_uploader("Upload your resume so we can understand your skills.", type=["pdf"])
if resume_file and not st.session_state.resume_data:
    try:
        with st.spinner("Reading resume..."):
            st.session_state.resume_data = extract_skills_from_resume(resume_file)
        st.sidebar.success(f"Resume parsed! Found {len(st.session_state.resume_data['keywords'])} keywords.")
    except Exception as e:
        st.sidebar.error(str(e))

st.sidebar.markdown("---")
st.sidebar.markdown("**LinkedIn Connections (CSV)**")
st.sidebar.caption("Don't have this? Go to LinkedIn Settings → Data Privacy → Get a copy of your data → select 'Connections' → download.")
connections_file = st.sidebar.file_uploader("Upload your Connections.csv", type=["csv"])
if connections_file and not st.session_state.matcher:
    try:
        with st.spinner("Processing network..."):
            st.session_state.matcher = ConnectionMatcher(connections_file)
        st.sidebar.success("Connections loaded successfully!")
    except Exception as e:
        st.sidebar.error(str(e))

st.sidebar.header("2. API Keys")
st.sidebar.markdown("""
**Why do I need these?**
ReferralRadar runs locally for privacy, which means you need to bring your own free keys for the AI services it uses.

1. **Firecrawl API Key**: Used to search the web and read job postings automatically.
   👉 [Get a free Firecrawl key here](https://www.firecrawl.dev/)
   
2. **LLM API Key**: The AI brain used to draft your referral messages.
   👉 [Get a free Groq key here](https://console.groq.com/keys) (Recommended)
""")

fc_api_key = st.sidebar.text_input("Firecrawl API Key (Free)", type="password")

llm_provider = st.sidebar.selectbox("LLM Provider", ["Cloud (Groq/OpenRouter/OpenAI)", "Local (Ollama)"])
llm_api_key = None
if llm_provider == "Cloud (Groq/OpenRouter/OpenAI)":
    llm_api_key = st.sidebar.text_input("LLM API Key", type="password")

if st.sidebar.button("Test API Keys ✅"):
    st.sidebar.markdown("---")
    
    # 1. Test Firecrawl
    if not fc_api_key:
        st.sidebar.error("❌ Firecrawl: No key provided.")
    else:
        import requests
        try:
            # A lightweight request to check authorization
            resp = requests.get("https://api.firecrawl.dev/v1/scrape", headers={"Authorization": f"Bearer {fc_api_key}"})
            if resp.status_code == 401:
                st.sidebar.error("❌ Firecrawl: Invalid API Key.")
            else:
                st.sidebar.success("✅ Firecrawl: Key is valid!")
        except Exception:
            st.sidebar.error("❌ Firecrawl: Could not reach server.")
            
    # 2. Test LLM
    if llm_provider.startswith("Cloud"):
        if not llm_api_key:
            st.sidebar.error("❌ LLM: No key provided.")
        else:
            from openai import OpenAI
            try:
                base = "https://api.groq.com/openai/v1" if llm_api_key.startswith("gsk_") else "https://openrouter.ai/api/v1"
                client = OpenAI(base_url=base, api_key=llm_api_key)
                client.models.list() # Doesn't cost tokens
                st.sidebar.success("✅ LLM: Key is valid!")
            except Exception:
                st.sidebar.error("❌ LLM: Invalid API Key or provider unreachable.")
    else:
        st.sidebar.success("✅ LLM: Using Local Ollama (No key needed).")

st.sidebar.markdown("---")
with st.sidebar.expander("🔒 Privacy & Legal"):
    st.markdown("""
    **ReferralRadar is local-first & privacy-by-default.**
    - All file processing (resumes, LinkedIn exports) happens in your computer's RAM.
    - We NEVER store or track your files, API keys, or data.
    - API keys are securely held in memory strictly for external AI requests.
    """)

st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style="text-align: center; color: #666; font-size: 0.9em;">
Made with ❤️ by <b>Shreshtha Kumar Gupta</b> (@shreshtha-132)<br>
<a href="https://github.com/shreshtha-132/ReferralRadar" target="_blank">Repository</a> | <a href="https://github.com/shreshtha-132" target="_blank">GitHub Profile</a> | <a href="https://shreshtxa.vercel.app" target="_blank">Portfolio</a>
</div>
""", unsafe_allow_html=True)

# --- Main Logic Function ---
def process_job(job_dict, resume_data, matcher, llm_client, target_url=""):
    # 1. Match Skills
    match_results = analyze_job_match(resume_data['keywords'], job_dict['description'])
    
    # 2. Find Connections
    target_company = job_dict['company']
    connections = matcher.find_referrals(target_company)
    
    # 3. Generate Base Templates
    templates = llm_client.generate_templates(
        job_title=job_dict['title'],
        company=target_company,
        keywords=match_results['matching_keywords'],
        job_url=target_url
    )
    
    # 4. Construct Rows
    rows = []
    
    def add_connection_rows(tier_list, tier_name, email_template_key, dm_template_key):
        for conn in tier_list:
            has_email = bool(conn.get('email'))
            template_key = email_template_key if has_email else dm_template_key
            
            draft = llm_client.fill_template(templates.get(template_key, {}), conn, target_url)
            
            rows.append({
                "Company": target_company,
                "Role": job_dict['title'],
                "Match %": f"{match_results['match_percent']}%",
                "Source": job_dict['source'],
                "Connection Name": f"{conn.get('first_name')} {conn.get('last_name')}",
                "Connection Role": conn.get('position'),
                "Tier": tier_name,
                "Channel": "Email" if has_email else "LinkedIn DM",
                "Missing Skills": ", ".join(match_results['missing_keywords'][:5]),
                "Message Draft": draft
            })
            
    add_connection_rows(connections['tier1'], "Tier 1 (Direct)", "tier1_email", "tier1_dm")
    add_connection_rows(connections['tier2'], "Tier 2 (Bridge)", "tier2_email", "tier2_dm")
    
    return rows

# --- Main Canvas: Modes ---
st.header("3. Find Jobs & Referrals")

if not st.session_state.resume_data or not st.session_state.matcher:
    st.info("👈 Please upload your Resume and Connections CSV in the sidebar to begin.")
    st.stop()
    
if not fc_api_key:
    st.warning("👈 Please enter your Firecrawl API key in the sidebar.")
    st.stop()

if llm_provider.startswith("Cloud") and not llm_api_key:
    st.warning("👈 Please enter your LLM API key in the sidebar.")
    st.stop()

mode = st.radio("Choose Mode:", ["Targeted Link (Paste a specific job)", "Auto-Discovery (Search for jobs matching your resume)"])

if mode == "Targeted Link (Paste a specific job)":
    job_url = st.text_input("Paste Job Posting URL:")
    
    if st.button("Process Job") and job_url:
        try:
            crawler = CrawlerClient(fc_api_key)
            llm_client = LLMClient(
                provider='cloud' if llm_provider.startswith('Cloud') else 'local',
                api_key=llm_api_key
            )
            
            with st.spinner("Fetching job details..."):
                # Try ATS first
                job_dict = ATSClient.fetch_job(job_url)
                if not job_dict:
                    # Fallback to Firecrawl
                    st.toast("Not a recognized direct ATS, falling back to web scraper...")
                    job_dict = crawler.scrape_url(job_url)
            
            with st.spinner("Analyzing match and drafting messages..."):
                rows = process_job(job_dict, st.session_state.resume_data, st.session_state.matcher, llm_client, job_url)
                
            if not rows:
                st.warning(f"No connections found (Tier 1 or Tier 2) for {job_dict['company']}.")
            else:
                st.session_state.results_df = pd.DataFrame(rows)
                
        except Exception as e:
            st.error(f"Error: {str(e)}")

elif mode == "Auto-Discovery (Search for jobs matching your resume)":
    job_title_query = st.text_input("Enter a target job title to search (e.g., 'Software Engineer at Google'):")
    
    if st.button("Auto-Discover") and job_title_query:
        try:
            crawler = CrawlerClient(fc_api_key)
            llm_client = LLMClient(
                provider='cloud' if llm_provider.startswith('Cloud') else 'local',
                api_key=llm_api_key
            )
            
            with st.spinner("Searching the web for recent postings..."):
                search_results = crawler.search_jobs(f"{job_title_query} job posting")
                
            if not search_results:
                st.warning("No search results found.")
            else:
                all_rows = []
                for res in search_results:
                    url = res['url']
                    with st.spinner(f"Processing: {res['title'][:30]}..."):
                        job_dict = ATSClient.fetch_job(url)
                        if not job_dict:
                            try:
                                job_dict = crawler.scrape_url(url)
                            except Exception:
                                continue # Skip if scrape fails
                                
                        if job_dict:
                            rows = process_job(job_dict, st.session_state.resume_data, st.session_state.matcher, llm_client, url)
                            all_rows.extend(rows)
                            
                if not all_rows:
                    st.warning("Processed jobs but found no connections in your network for them.")
                else:
                    st.session_state.results_df = pd.DataFrame(all_rows)
                    
        except Exception as e:
            st.error(f"Error: {str(e)}")


# --- Display Results ---
if st.session_state.results_df is not None and not st.session_state.results_df.empty:
    st.header("4. Your Referral Action Plan")
    
    df = st.session_state.results_df.sort_values(by="Match %", ascending=False)
    
    st.dataframe(
        df.drop(columns=["Message Draft"]), 
        use_container_width=True,
        hide_index=True
    )
    
    # Download Button
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Full Action Plan as CSV",
        data=csv,
        file_name='referral_action_plan.csv',
        mime='text/csv',
    )
    
    st.subheader("Your Drafted Messages")
    st.caption("Copy and paste these directly to your connections!")
    
    for idx, row in df.iterrows():
        with st.expander(f"Message for {row['Connection Name']} at {row['Company']} ({row['Tier']}, {row['Channel']})"):
            st.code(row['Message Draft'], language="markdown")

# ReferralRadar Architecture & Information

## What is ReferralRadar?
ReferralRadar is a local application designed to help you find jobs that match your resume and instantly discover who in your LinkedIn network can refer you to those jobs. It takes the guesswork out of networking by telling you exactly who to contact and what to say.

## How It Works (The Data Pipeline)
1. **You provide your data**: You upload your Resume (PDF) and your LinkedIn Connections (CSV).
2. **We understand you**: The app reads your resume to extract your core skills, experience level, and target job titles.
3. **We find jobs**: 
   - **Auto-Discovery Mode**: The app searches the internet (via Firecrawl) to find recent job postings that match your profile.
   - **Targeted Mode**: You paste a link to a job you want, and the app reads it directly (often bypassing searches by looking directly at the company's job board).
4. **We match skills**: The app compares the job requirements against your resume and gives you a Match Percentage, highlighting what keywords you might be missing.
5. **We find your network**: The app searches your LinkedIn connections to see if anyone works at the company hiring for the job (Tier 1). If not, it looks for connections at similar companies (Tier 2).
6. **We draft the message**: The app uses an AI (Language Model) to draft a highly personalized message you can copy and send to your connection to ask for a referral.

## Component Breakdown
- **Frontend (What you see)**: Built with Streamlit, providing a simple sidebar for your files/keys and a main area for your job results.
- **Parser**: Reads your PDF resume and extracts text and keywords.
- **ATS Client**: Communicates directly with popular job boards (Greenhouse, Lever, etc.) to get job details quickly and for free.
- **Crawler**: Uses Firecrawl to search the web for jobs or scrape job postings when the ATS Client can't.
- **Matcher**: Compares company names (e.g., matching "Google" with "Google LLC") to find your connections.
- **LLM**: The AI brain (OpenAI, Groq, or Ollama) that writes the personalized referral messages.

## API Requirements
To use ReferralRadar, you will need two free API keys:
1. **Firecrawl API Key**: Used to search the internet for jobs and read job postings. You can get a free key at [Firecrawl's website].
2. **LLM API Key**: Used to draft the personalized referral messages. We support multiple providers, ordered by utility for free users:
   - **Groq**: Extremely fast and offers a generous free tier. Highly recommended.
   - **OpenRouter**: Offers access to free models (like Google's Gemini or Meta's Llama 3) through a single API key.
   - **OpenAI**: The standard paid option if you already have an account.
   - **Ollama**: For advanced users who want to run models 100% locally and offline for free.

## Local Setup (For Both Technical and Non-Technical Users)
*A complete step-by-step setup guide will be available in the README.md file once the application is fully built, with instructions on how to get API keys for free.*

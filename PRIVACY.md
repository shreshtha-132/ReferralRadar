# Privacy Policy

**ReferralRadar is designed with a local-first, privacy-by-default architecture.**

## Data Processing
- **No Data Storage:** All data processing (parsing your resume, matching your connections) happens entirely in-memory (RAM) on your local machine.
- **No Database:** We do not store your Resume (PDF), your LinkedIn Connections (CSV), or your API keys in any external database.
- **API Keys:** Your API keys are strictly stored in your local session state and are never logged, tracked, or sent anywhere except directly to the official API endpoints (Firecrawl and your chosen LLM provider).

## External Services
When you use ReferralRadar, the app communicates with the following external services using the keys you provide:
1. **Firecrawl:** We send job URLs and search queries to Firecrawl to extract job descriptions.
2. **LLM Provider (Groq, OpenRouter, etc.):** We send the extracted job description and your matching resume keywords to the AI to draft your referral messages.

*If you use the local Ollama option, no data ever leaves your computer for the LLM step!*

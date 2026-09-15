# Architecture Decisions Log

## 1. Zero LLM Waste & Deterministic Templating
**Decision**: We will not call the LLM for every single LinkedIn connection to generate a referral message.
**Rationale**: LLMs are slow and can get expensive or hit rate limits if you have 50 connections at a company. Instead, we use the LLM to generate exactly 4 base templates per job posting (Tier 1 w/ email, Tier 1 w/o email, Tier 2 w/ email, Tier 2 w/o email). We then use Python's fast string replacement (e.g., `.format(first_name=...)`) to insert the connection's name deterministically.

## 2. Alma Mater Matching Excluded
**Decision**: We will not attempt to match connections based on alma mater (university/college).
**Rationale**: LinkedIn's standard `Connections.csv` data export does not include education data. It only includes First Name, Last Name, Email Address, Company, Position, and Connected On. Rather than building a fragile system that requires users to manually input their alumni database, we simply ignore alma mater matching and focus purely on Company matching.

## 3. Tier 2 (Bridge/Peer) Company Mapping
**Decision**: We will use a static configuration (`config.py`) to map companies to their peer groups (e.g., FAANG, Big 4 Consulting, FinTech).
**Rationale**: Dynamically clustering companies via an LLM per user upload is slow and unpredictable. A curated static list ensures reliable, instant categorization for Tier 2 matching (finding someone at Microsoft to refer you to Google).

## 4. ATS Direct Resolution
**Decision**: The app will attempt to recognize URLs from common ATS (Applicant Tracking System) providers like Greenhouse, Lever, Ashby, etc., and call their public, unauthenticated APIs first.
**Rationale**: Firecrawl charges credits and adds latency. Direct API calls to ATS providers are free, instantaneous, and provide perfectly structured JSON data, significantly improving the user experience and reducing costs.

## 5. Fuzzy Matching for Companies
**Decision**: Use `rapidfuzz` (specifically `token_sort_ratio` or `partial_ratio`) to compare the job posting's company name against the user's Connections.csv.
**Rationale**: A job posting might say "Google LLC", but the connection might list "Google" or "Google Cloud". Exact string matching would fail. `rapidfuzz` is extremely fast and handles these minor variations well.

## 6. Using `requests` vs Firecrawl SDK
**Decision**: We will use the standard `requests` library to interact with the Firecrawl API rather than installing their official Python SDK.
**Rationale**: The SDK is a thin wrapper over their REST API. Using `requests` keeps the dependency footprint small, avoids dealing with potential versioning issues of the SDK, and gives us complete control over error handling and timeouts to ensure a robust user experience.

## 7. Unified LLM Integration via `openai` package
**Decision**: We will use the official `openai` Python package to connect to all LLM providers (Groq, OpenRouter, OpenAI, and Ollama).
**Rationale**: All of these providers offer OpenAI-compatible endpoints. By simply changing the `base_url` and `api_key` in the `openai.Client`, we can seamlessly switch between cloud providers and local offline models without maintaining separate SDKs or duplicated logic.

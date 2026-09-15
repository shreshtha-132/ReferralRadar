# ReferralRadar 🎯

**Stop applying into the void.** ReferralRadar is an AI-powered, local-first tool that matches your resume against live job postings and instantly drafts personalized referral requests to your existing LinkedIn connections. 

---

### Step 0: Request Your LinkedIn Data
It takes LinkedIn ~10 minutes to process your data, so do this first:
1. Go to LinkedIn > Me > **Settings & Privacy** > **Data privacy**.
2. Click **Get a copy of your data**.
3. Select **Connections** and click **Request archive**. You'll get an email when the CSV is ready.

### Step 1: Install & Run
Open your terminal and run these commands:
```bash
# 1. Clone the repo and enter the folder
git clone https://github.com/shreshtha-132/ReferralRadar.git
cd ReferralRadar

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# 3. Install requirements
pip install -r requirements.txt

# 4. Start the app
streamlit run app.py
```

### Step 2: Add Free API Keys
ReferralRadar runs entirely on your local machine for privacy. You just need to provide your own free API keys to power the AI:
- **Firecrawl**: Used to search the web and read job postings. [Get a free key](https://www.firecrawl.dev/)
- **Groq**: The AI brain (LLM) that writes your messages. [Get a free key](https://console.groq.com/keys)

---

## Contributing
Released under the **MIT License**. Check out [CONTRIBUTING.md](CONTRIBUTING.md) to see how to run tests and submit a PR. Please read our [Privacy Policy](PRIVACY.md).

**Author:** Shreshtha Kumar Gupta (@shreshtha-132) | [Portfolio](https://shreshtxa.vercel.app)

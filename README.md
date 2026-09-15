# ReferralRadar

ReferralRadar is your personal AI assistant for job hunting. It takes your resume, finds relevant job postings, and automatically drafts personalized referral requests to your LinkedIn connections. 

Designed for both technical and non-technical users, it runs completely locally on your machine—meaning your data stays private.

## Quick Start Guide

### Step 0: Get Your LinkedIn Data
*(Note: It takes 0-48 hours for LinkedIn to process and provide your data, so do this first!)*
1. Go to LinkedIn and click your profile picture (Me) > **Settings & Privacy**.
2. Click **Data privacy** on the left menu.
3. Click **Get a copy of your data**.
4. Select **Want something in particular?**
5. Check the box for **Connections** and click **Request archive**.

### Step 1: Install Python
ReferralRadar is built with Python. If you don't have it installed:
- **Windows**: Download it from the [Microsoft Store](https://apps.microsoft.com/detail/9pjpw5ldxlz5?hl=en-us&gl=US) or the [official website](https://www.python.org/downloads/). (Make sure to check "Add Python to PATH" during installation).
- **Mac**: Install via [Homebrew](https://brew.sh/): `brew install python` or download from the [official website](https://www.python.org/downloads/).

### Step 2: Download the Application
1. Download this folder (if you haven't already).
2. Open your terminal or command prompt.
   - **Mac**: Press `Cmd + Space`, type `Terminal`, and press Enter.
   - **Windows**: Press the Windows key, type `cmd`, and press Enter.
3. Navigate to where you downloaded the folder. For example:
   `cd Downloads/ReferralRadar`

### Step 3: Create a Virtual Environment & Install Requirements
It's highly recommended to use a virtual environment so the app's dependencies don't interfere with other Python tools on your computer.

1. **Create the virtual environment**:
   ```bash
   python -m venv venv
   ```
2. **Activate the virtual environment**:
   - **Mac/Linux**: 
     ```bash
     source venv/bin/activate
     ```
   - **Windows**: 
     ```bash
     venv\Scripts\activate
     ```
   *(You should now see `(venv)` at the beginning of your terminal line).*

3. **Install the necessary tools**:
   ```bash
   pip install -r requirements.txt
   ```
### Step 4: Get Your Free API Keys
ReferralRadar uses two free AI services to power its search and messaging. You will need to get keys for them:

1. **Firecrawl API Key** (Used for searching the web for jobs)
   - Go to [Firecrawl](https://www.firecrawl.dev/) and sign up for a free account.
   - Go to your dashboard and generate an API key.

2. **LLM API Key** (Used for writing the referral messages)
   We recommend **Groq** for the fastest, free experience.
   - Go to the [Groq Console](https://console.groq.com/keys) and sign in.
   - Click "Create API Key".

*(Note: You can also use OpenRouter, OpenAI, or a local Ollama server if you prefer).*

### Step 5: Run the App!
Now that everything is set up, run this command in your terminal:
```bash
streamlit run app.py
```
A browser window will automatically open with the ReferralRadar app. Follow the on-screen instructions to upload your resume and LinkedIn connections!



---

## Contributing and Open Source
ReferralRadar is an open-source project released under the **MIT License**. We welcome contributions from the community!
- Check out [CONTRIBUTING.md](CONTRIBUTING.md) to see how to run tests and submit a PR.
- Please adhere to our [Code of Conduct](CODE_OF_CONDUCT.md).
- Read our [Privacy Policy](PRIVACY.md) and [Terms of Use](TERMS.md).

## Author
Built by **Shreshtha Kumar Gupta** (@shreshtha-132).
- 🌐 [Portfolio](https://shreshtxa.vercel.app)
- 🐙 [GitHub](https://github.com/shreshtha-132)

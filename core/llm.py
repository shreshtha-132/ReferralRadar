from openai import OpenAI
import json
from config import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE

class LLMClient:
    """Wrapper around OpenAI client to support multiple providers (Groq, OpenRouter, Ollama)."""
    
    def __init__(self, provider, api_key=None):
        """
        provider: 'cloud' (Groq/OpenRouter) or 'local' (Ollama)
        api_key: The user's API key
        """
        self.provider = provider
        
        if provider == 'cloud':
            if not api_key:
                raise ValueError("API Key is required for Cloud LLM providers.")
            # We assume Groq by default if it looks like a Groq key (starts with gsk_), 
            # otherwise OpenRouter or standard OpenAI.
            if api_key.startswith("gsk_"):
                base_url = "https://api.groq.com/openai/v1"
                self.model = "llama-3.1-8b-instant" # Fast and good
            else:
                base_url = "https://openrouter.ai/api/v1"
                self.model = "google/gemini-flash-1.5" # Good free model on OpenRouter fallback
                
            self.client = OpenAI(base_url=base_url, api_key=api_key)
            
        elif provider == 'local':
            # Ollama standard setup
            self.client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
            self.model = "llama3.2" # Default standard local model
        else:
            raise ValueError(f"Unknown LLM provider type: {provider}")

    def generate_templates(self, job_title, company, keywords, job_url):
        """
        Generates 4 message templates using the LLM.
        Returns a dictionary with the 4 templates.
        """
        user_prompt = USER_PROMPT_TEMPLATE.format(
            job_title=job_title,
            company=company,
            keywords=", ".join(keywords) if keywords else "None",
            job_url=job_url if job_url else "[Job Link]"
        )
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=800
            )
            
            raw_json = response.choices[0].message.content
            templates = json.loads(raw_json)
            
            # Basic validation to ensure keys exist
            required_keys = ["tier1_email", "tier1_dm", "tier2_email", "tier2_dm"]
            for key in required_keys:
                if key not in templates:
                    templates[key] = {"body": "Could not generate this template."}
                    
            return templates
            
        except Exception as e:
            # Fallback if LLM fails
            error_msg = f"Failed to generate template ({str(e)}). Please draft manually."
            return {
                "tier1_email": {"subject": f"Referral for {job_title}", "body": error_msg},
                "tier1_dm": {"body": error_msg},
                "tier2_email": {"subject": f"Connecting regarding {company}", "body": error_msg},
                "tier2_dm": {"body": error_msg}
            }

    def fill_template(self, template, connection, job_url):
        """
        Deterministically fills the {first_name} and {job_url} placeholders.
        """
        body = template.get("body", "")
        subject = template.get("subject", "")
        
        first_name = connection.get("first_name", "Connection")
        if not first_name:
            first_name = "Connection"
            
        # Fast python string replacement
        # Note: Some LLMs might use [First Name] instead of {first_name}. We can handle both.
        body = body.replace("{first_name}", first_name).replace("[First Name]", first_name)
        body = body.replace("{job_url}", job_url).replace("[Job Link]", job_url)
        
        subject = subject.replace("{first_name}", first_name).replace("[First Name]", first_name)
        
        if subject:
            return f"Subject: {subject}\n\n{body}"
        return body

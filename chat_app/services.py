import os
import json
import time
import requests

# The Gemini API Key is expected to be loaded in the views/settings, 
# but we retrieve it again here just in case.
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "") 
API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent"
MAX_RETRIES = 3

class MiceInfoAgent:
    """
    Service layer responsible for interacting with the Google Gemini API.
    It encapsulates the model configuration, API calls, and response parsing.
    """

    def __init__(self):
        # Define the agent's persona and role
        self.system_instruction = (
            "You are 'Mice Info Agent', a helpful and concise expert on rodents, "
            "specifically mice and rats, their behavior, care, and biology. "
            "Answer the user's questions accurately and based on current, grounded information. "
            "If asked a question outside of your expertise (rodents), politely decline. "
            "Keep your responses friendly, informative, and brief."
        )

    def _call_gemini_api(self, payload):
        """Internal function to handle the API call with exponential backoff."""
        if not GEMINI_API_KEY:
            return "Error: GEMINI_API_KEY not found. Please ensure it's set in your environment variables."

        headers = {'Content-Type': 'application/json'}
        
        for attempt in range(MAX_RETRIES):
            try:
                # Add API key to the URL
                url_with_key = f"{API_URL}?key={GEMINI_API_KEY}"
                
                # Make the POST request to the Gemini API
                response = requests.post(
                    url_with_key, 
                    headers=headers, 
                    data=json.dumps(payload),
                    timeout=20
                )
                response.raise_for_status() # Raises an exception for 4xx/5xx errors

                # Process successful response
                result = response.json()
                candidate = result.get('candidates', [None])[0]
                
                if candidate and candidate.get('content') and candidate['content'].get('parts'):
                    # Extract the generated text
                    text = candidate['content']['parts'][0].get('text', 'No response text generated.')
                    return text
                else:
                    return "AI response structure was invalid or empty."

            except requests.exceptions.RequestException as e:
                print(f"Attempt {attempt + 1} failed: {e}")
                if attempt < MAX_RETRIES - 1:
                    wait_time = 2 ** attempt
                    time.sleep(wait_time) # Exponential backoff
                else:
                    return f"Failed to get a response from Gemini API after {MAX_RETRIES} attempts."
            except Exception as e:
                return f"An unexpected error occurred during API call: {e}"
        
        return "An internal error occurred."

    def get_mouse_info(self, user_query):
        """
        Generates a response using the Gemini API, grounded with Google Search.
        """
        payload = {
            "contents": [
                {
                    "role": "user", 
                    "parts": [{"text": user_query}]
                }
            ],
            # Use Google Search for grounded, up-to-date information
            "tools": [{"google_search": {}}],
            
            # Set the agent's persona using the system instruction
            "config": {
                "systemInstruction": self.system_instruction
            }
        }

        # Delegate to the internal API caller
        return self._call_gemini_api(payload)

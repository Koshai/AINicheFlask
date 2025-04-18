import requests
from flask import current_app
import openai

def generate_content(engine, prompt):
    """Generate content using either Ollama or OpenAI"""
    if engine == 'ollama':
        return _generate_with_ollama(prompt)
    else:
        return _generate_with_openai(prompt)

def _generate_with_ollama(prompt):
    """Generate content using Ollama local LLM"""
    try:
        current_app.logger.info("Attempting to connect to Ollama at http://localhost:11434")
        
        # First check if Ollama is running with a quick GET request
        check_res = requests.get("http://localhost:11434/api/version", timeout=5)
        if check_res.status_code != 200:
            current_app.logger.error(f"Ollama server returned status code: {check_res.status_code}")
            return "Ollama is not responding correctly. Please make sure it's running."
            
        # Proceed with generation if Ollama is running
        res = requests.post(
            "http://localhost:11434/api/generate", 
            json={
                "model": "llama3.2:latest", 
                "prompt": prompt, 
                "stream": False
            },
            timeout=60  # Increased timeout for generation
        )
        
        if res.status_code != 200:
            current_app.logger.error(f"Ollama error: Status {res.status_code}, {res.text}")
            return f"Error generating content with Ollama (Status: {res.status_code})"
            
        return res.json().get("response", "No response from Ollama")
    except requests.exceptions.ConnectTimeout:
        current_app.logger.error("Ollama connection timed out: Is Ollama running?")
        return "Cannot connect to Ollama. Please make sure Ollama is running on your local machine (http://localhost:11434)."
    except requests.exceptions.ReadTimeout:
        current_app.logger.error("Ollama read timeout: The request took too long to process")
        return "Ollama took too long to generate content. Please try again with a simpler request or use OpenAI instead."
    except requests.exceptions.ConnectionError:
        current_app.logger.error("Ollama connection error: Is Ollama running?")
        return "Cannot connect to Ollama. Please make sure Ollama is running on your local machine (http://localhost:11434)."
    except Exception as e:
        current_app.logger.error(f"Ollama error: {str(e)}")
        return f"Error connecting to Ollama: {str(e)}"

def _generate_with_openai(prompt):
    """Generate content using OpenAI API"""
    try:
        api_key = current_app.config.get('OPENAI_API_KEY')
        if not api_key:
            current_app.logger.error("OpenAI API key not configured")
            return "OpenAI API key not configured. Please check your environment settings."
            
        client = openai.OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500
        )
        
        return response.choices[0].message.content
    except Exception as e:
        current_app.logger.error(f"OpenAI error: {str(e)}")
        return f"Error generating content with OpenAI: {str(e)}"
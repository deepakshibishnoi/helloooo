# HairCare Assistant — Streamlit App

A Gemini-powered haircare chatbot that runs locally or can be deployed to Streamlit Community Cloud.

## 1. Project files

- `app.py` — Streamlit chatbot application
- `requirements.txt` — Python dependencies
- `.streamlit/secrets.toml.example` — example location for your Gemini API key

## 2. Get a Gemini API key

Create an API key in Google AI Studio:
https://aistudio.google.com/app/apikey

Keep the key private. Do not paste it into `app.py` or upload it publicly.

## 3. Run in Google Colab

Upload and extract this ZIP in Colab, then run:

```python
!pip install -r requirements.txt
```

Set your key for the current Colab session:

```python
import os
os.environ["GEMINI_API_KEY"] = "YOUR_GEMINI_API_KEY"
```

Start Streamlit:

```python
!streamlit run app.py &>/content/streamlit.log &
```

To open the app from Colab, use a tunnel service such as `localtunnel` or `cloudflared`.
For example, with localtunnel:

```python
!npm install -g localtunnel
!lt --port 8501
```

Open the public URL printed by localtunnel. Do not share it if your app contains private information.

## 4. Run on your computer

Open a terminal in the project folder:

```bash
python -m venv .venv
```

Activate the environment, then install:

```bash
pip install -r requirements.txt
```

Set the API key.

macOS/Linux:
```bash
export GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
```

Windows PowerShell:
```powershell
$env:GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
```

Run:
```bash
streamlit run app.py
```

## 5. Deploy on Streamlit Community Cloud

1. Upload the project files to a private or public GitHub repository.
2. In Streamlit Community Cloud, create a new app and select `app.py`.
3. Open the app's **Settings → Secrets**.
4. Add:

```toml
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
```

5. Save and reboot the app.

## Notes

- The app uses the `google-genai` Python SDK and the `gemini-2.5-flash` model.
- User profile information is kept in the Streamlit session and included in prompts to personalize responses.
- The FAQ section is available without sending a Gemini request.
- The chatbot provides general information, not medical diagnosis or treatment.

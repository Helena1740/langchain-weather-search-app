# Research Desk

A small LangChain-powered research assistant that combines an LLM with web search and local weather tooling. The app is built with Streamlit and can be run in either an Anaconda environment or a standard Python virtual environment.

## Overview

This project uses:

- Python 3.11
- LangChain + LangChain Core
- Google Gemini for the model
- Tavily for web search
- Weatherstack for current weather lookup
- Streamlit for the UI
- Python-dotenv for environment variables

The application lets the user ask research questions and uses tools to fetch external information before returning an answer in a clean interface.

## Project structure

```text
.
├── app.py               # Main Streamlit app used in production
├── main.py              # Prototype / exploratory version
├── requirements.txt     # Python dependencies
├── .env                 # Local secrets (not committed)
├── .gitignore           # Ignore local env and cache files
├── README.md            # Project documentation
├── research/            # Research folder
└── .git/                # Git metadata
```

## Features

- Research assistant agent with tool use
- Web search via Tavily
- Weather queries via custom tool calling the Weatherstack API
- Gemini model integration
- Streamlit web UI
- Environment-based secret management using `.env`

## Required API keys

Create a `.env` file in the project root with the following values:

```env
GOOGLE_API_KEY=your_google_api_key
TAVILY_API_KEY=your_tavily_api_key
WEATHERSTACK_API_KEY=your_weatherstack_api_key
```

Important:
- Never commit `.env` to Git.
- Keep API keys private and local to your machine.

## Setup

### Option 1: Anaconda setup

If you use Anaconda, do the following:

1. Install Anaconda or Miniconda.
2. Open Anaconda Prompt.
3. Create the environment:

```bash
conda create -n langagent python=3.11 -y
```

4. Activate it:

```bash
conda activate langagent
```

5. Install project dependencies:

```bash
python -m pip install -r requirements.txt
```

6. Run the app:

```bash
streamlit run app.py
```

#### If `conda` is not recognized in PowerShell

In VS Code PowerShell, you may need to initialize Conda for PowerShell:

```powershell
& "C:\Users\AI 2\anaconda3\Scripts\conda.exe" init powershell
```

Then close and reopen PowerShell, and run:

```powershell
conda activate langagent
```

If PowerShell blocks scripts, use:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Then reopen the terminal.

---

### Option 2: Standard Python virtual environment setup

If you do not want to use Anaconda, create a local venv instead:

1. In the project folder, create the environment:

```bash
python -m venv .venv
```

2. Activate it:

- Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

- macOS/Linux:

```bash
source .venv/bin/activate
```

3. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

4. Start the app:

```bash
streamlit run app.py
```

## Checking the active environment

To verify you are in the correct Python environment:

```bash
where.exe python
```

or:

```powershell
Get-Command python
```

For Anaconda-specific checks:

```bash
conda list
conda list -n langagent
python -m pip show langchain
```

## Running the project

Once the environment is active and dependencies are installed:

```bash
streamlit run app.py
```

This launches the app in your browser or local Streamlit preview.

## Notes on the code

The app uses:

- `load_dotenv()` to read secrets from `.env`
- `os.environ["SSL_CERT_FILE"] = certifi.where()` for Windows certificate compatibility
- `TavilySearch` to perform up-to-date web search
- a custom `@tool` function called `get_weather_data(city: str)` to fetch weather information
- a `create_agent(...)` pattern to create a LangChain agent that can reason and call tools

The prototype file `main.py` contains the same concept in a simpler, script-style version, while `app.py` is the polished Streamlit interface.

## Common development workflow

```bash
git status
git add .
git commit -m "Describe your changes"
git push
```

## .gitignore

The repository already ignores local secrets and temporary files, including:

```gitignore
.env
__pycache__/
*.pyc
.ipynb_checkpoints/
.vscode/
```

## Troubleshooting

- If `conda` is not recognized, initialize Conda in PowerShell or use Anaconda Prompt.
- If `streamlit` is missing, reinstall dependencies in the active environment.
- If API requests fail, confirm your `.env` values are correct and your keys are valid.
- If you are unsure which Python is active, check `where.exe python` or `Get-Command python`.

## License

This project is for learning and local development use unless otherwise specified.

# AI Agent, Tools & Automation

A beginner-friendly AI agent demo built with Python, Streamlit, and OpenAI function calling.

## What it demonstrates

- Difference between a simple chatbot and a tool-using agent
- Task understanding and action selection
- Function/tool calling
- Processing tool results and responding
- Session history (state)
- Basic limits and safety: only a small set of explicitly defined tools is available
- Tool-call trace for transparency

## Agent workflow

**Understand Task → Decide Action → Use Tool → Process Result → Respond**

## Included tools

1. `calculator` — evaluates basic arithmetic only
2. `get_current_date` — returns the current date
3. `word_count` — counts words and characters

The app does not execute arbitrary code, browse the web, or modify external systems.

## Run locally

1. Install Python 3.10 or later.
2. Open a terminal in this folder.
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Start the app:

   ```bash
   streamlit run app.py
   ```

5. Enter your OpenAI API key in the sidebar. Keep your key private and do not commit it to GitHub.

## Deploy to Streamlit Community Cloud

1. Upload `app.py`, `requirements.txt`, and `README.md` to your GitHub repository.
2. Open Streamlit Community Cloud and connect your GitHub account.
3. Create an app from the repository and choose `app.py` as the main file.
4. Deploy the app.
5. Add the API key through the app's Secrets settings, then adjust the code to read `st.secrets["OPENAI_API_KEY"]` if you want to use a stored secret rather than entering it in the sidebar.

## Example tasks

- `Calculate (245 * 18) / 3`
- `What is today's date?`
- `Count the words in: AI agents can use tools to complete tasks.`

## Important

Using an LLM API may incur charges. Check your provider's pricing and usage limits. This sample is an educational starter project, not a production-hardened agent.

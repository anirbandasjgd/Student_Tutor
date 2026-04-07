# Student Tutor

A Streamlit chatbot that helps students with **Science**, **Math**, **English**, **General knowledge**, and **Essay** feedback. Each subject has its own Python module so you can change system prompts and settings independently.

Repository: [https://github.com/anirbandasjgd/Student_Tutor](https://github.com/anirbandasjgd/Student_Tutor)

## Prerequisites

- Python 3.10+ recommended
- An OpenAI API key

## Setup

1. Clone or copy this `StudentTutor` folder.

2. Create a virtual environment (optional but recommended):

   ```bash
   cd StudentTutor
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Configure the API key:

   ```bash
   cp .env.example .env
   ```

   Edit `.env` and set `OPENAI_API_KEY`.

5. **Model name:** The project defaults to `gpt-5.4-mini` (as specified for the assignment). If that model is not available on your account, set `OPENAI_MODEL` in `.env` to a model you can use (for example `gpt-4o-mini`).

## Run

From the `StudentTutor` directory:

```bash
streamlit run app.py
```

The app opens in your browser. Choose a subject in the sidebar, then chat. **General knowledge** is for questions that are not mainly Science, Math, or English. **Essay** mode enforces a **150-word maximum** on the student’s essay text and supports optional **grade level** (1–12) so feedback complexity matches the spec.

## Project layout

| Path | Purpose |
|------|--------|
| `app.py` | Streamlit UI, OpenAI calls, session handling |
| `config.py` | Model name and data paths |
| `chat_storage.py` | Save/load chat JSON under `data/chats/students/<key>/` (per student) |
| `student_identity.py` | Map student name to a stable storage key for isolation |
| `subjects/science.py` | Science system message, `max_tokens` |
| `subjects/math.py` | Math system message, `max_tokens` |
| `subjects/english.py` | English system message, `max_tokens` |
| `subjects/general_knowledge.py` | General knowledge system message, `max_tokens` |
| `subjects/essay.py` | Essay rules, grade bands, 150-word policy |

## Testing

See [TESTING.md](TESTING.md) for manual test steps.

## Chat history

Enter your **full name** in the sidebar (required). Chats are saved per student under `data/chats/students/<storage-key>/`; **Saved chats** lists only that student’s sessions, grouped by subject. Changing the name switches to that student’s history (or starts fresh).

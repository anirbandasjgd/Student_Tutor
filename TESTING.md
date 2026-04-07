# Testing Student Tutor

These checks assume you have completed [README.md](README.md) setup (virtual environment, `pip install -r requirements.txt`, `.env` with `OPENAI_API_KEY`).

## Smoke test (app starts)

```bash
cd StudentTutor
streamlit run app.py
```

Confirm the page loads, the subject radio options list Science / Math / English / Essay, and the chat input is visible.

## Subject modules

For each subject, send a short question and confirm you get a relevant reply:

- **Science:** e.g. “What is photosynthesis in one sentence?”
- **Math:** e.g. “What is the Pythagorean theorem?”
- **English:** e.g. “What’s the difference between ‘affect’ and ‘effect’?”

Science, Math, and English use **150 max output tokens** (see each file under `subjects/`).

## Essay mode

1. Select **Essay** in the sidebar.
2. **Over 150 words:** Paste text longer than 150 words and send. You should see a warning and the message should **not** be accepted as a valid essay submission until shortened.
3. **150 words or fewer:** Paste a short paragraph and send. The assistant should ask for **grade** if you did not set **Your grade (optional)** in the sidebar, or should tailor feedback if you set a grade.
4. Optional: set grade to **2** and confirm wording stays simple; set to **10** and confirm feedback targets stronger writing / college-style expectations per `subjects/essay.py`.

## Persistence

1. Send a few messages in any subject.
2. Click **New chat**, send another message.
3. In **Saved chats**, open a subject section (Science / Math / English / Essay), click a previous session, and confirm messages reload.

## API errors

If the model name is invalid, set `OPENAI_MODEL` in `.env` to a valid chat model and reload the app.

import os
import tempfile
import unittest

from bot.config import load_config
from bot.content import ContentStore
from bot.matcher import match_answer_key
from bot.storage import JsonFileStore


class ConfigTests(unittest.TestCase):
    def test_missing_token_fails_fast(self):
        old = dict(os.environ)
        os.environ.pop("TELEGRAM_BOT_TOKEN", None)
        os.environ["TELEGRAM_ADMIN_CHAT_ID"] = "123"
        try:
            with self.assertRaisesRegex(RuntimeError, "Missing TELEGRAM_BOT_TOKEN"):
                load_config()
        finally:
            os.environ.clear()
            os.environ.update(old)


class StorageTests(unittest.TestCase):
    def test_sessions_and_leads_persist(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            store = JsonFileStore(temp_dir)
            session = store.get_session("42", "en")
            session.language = "ru"
            session.current_flow = "contact"
            session.draft_payload = {"full_name": "Test User"}
            store.save_session(session)
            loaded = store.get_session("42", "en")
            self.assertEqual(loaded.language, "ru")
            self.assertEqual(loaded.draft_payload["full_name"], "Test User")

            lead = store.add_lead(
                {
                    "telegram_user_id": "42",
                    "username": "tester",
                    "full_name": "Test User",
                    "language": "ru",
                    "company_or_role": "Recruiter",
                    "preferred_contact": "Telegram",
                    "reason_for_contact": "Internship",
                }
            )
            self.assertEqual(lead.full_name, "Test User")
            self.assertTrue(store.leads_path.exists())


class ContentTests(unittest.TestCase):
    def test_known_questions_match(self):
        store = ContentStore("bot/content/portfolio_content.json")
        ru = store.catalog("ru")
        en = store.catalog("en")
        self.assertEqual(match_answer_key(ru, "Какие у нее навыки и языки?"), "skills")
        self.assertEqual(match_answer_key(en, "What experience does she have?"), "experience")
        self.assertIsNone(match_answer_key(en, "What is her favorite movie?"))


if __name__ == "__main__":
    unittest.main()

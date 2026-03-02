import unittest

from linkedin_bot.config import BotConfig, ConfigError


class BotConfigTests(unittest.TestCase):
    def test_from_env_loads_required_values(self) -> None:
        config = BotConfig.from_env(
            {
                "GEMINI_API_KEY": "gm-test",
                "LINKEDIN_ACCESS_TOKEN": "li-token",
                "LINKEDIN_PERSON_URN": "urn:li:person:123",
            }
        )

        self.assertEqual(config.gemini_api_key, "gm-test")
        self.assertEqual(config.linkedin_access_token, "li-token")
        self.assertEqual(config.linkedin_person_urn, "urn:li:person:123")
        self.assertEqual(config.gemini_model, "gemini-2.5-flash")
        self.assertEqual(config.max_retries, 3)

    def test_from_env_requires_mandatory_keys(self) -> None:
        with self.assertRaises(ConfigError):
            BotConfig.from_env({})

    def test_from_env_rejects_invalid_int(self) -> None:
        with self.assertRaises(ConfigError):
            BotConfig.from_env(
                {
                    "GEMINI_API_KEY": "gm-test",
                    "LINKEDIN_ACCESS_TOKEN": "li-token",
                    "LINKEDIN_PERSON_URN": "123",
                    "MAX_RETRIES": "zero",
                }
            )


if __name__ == "__main__":
    unittest.main()

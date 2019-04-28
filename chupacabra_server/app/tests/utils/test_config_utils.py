from unittest import TestCase
from unittest.mock import MagicMock

from utils.config_utils import get_variable_with_fallback


class TestConfigUtils(TestCase):
    def test_get_variable_with_fallback(self):
        mock_getenv = MagicMock()
        mock_getenv.return_value = None

        fallback_dict = {
            'MY_VARIABLE': 1
        }
        result = get_variable_with_fallback(
            'MY_VARIABLE',
            fallback_dict,
            is_required=True
        )
        self.assertEqual(1, result)

        result = get_variable_with_fallback(
            'MY_VARIABLE',
            fallback_dict,
            is_required=False
        )
        self.assertEqual(1, result)

        result = get_variable_with_fallback(
            'OTHER_VARIABLE',
            fallback_dict,
            is_required=False
        )
        self.assertIsNone(result)

        with self.assertRaises(AssertionError):
            get_variable_with_fallback(
                'OTHER_VARIABLE',
                fallback_dict,
                is_required=True
            )

import unittest
from copy import deepcopy

from astronverse.executor.flow.params import Param
from astronverse.executor.run_params import parse_run_params
from astronverse.executor.utils.utils import str_to_list_if_possible


class RunParamsTests(unittest.TestCase):
    def test_native_scalars_preserve_value_and_type(self):
        for value in (3, 1.5, 0, 0.0, -2, False, True):
            with self.subTest(value=value):
                result = parse_run_params([{"varName": "x", "varValue": value}], Param(None))["x"]
                assert result == value
                assert type(result) is type(value)

    def test_legacy_values_keep_existing_parser_behavior(self):
        for value in (
            "3",
            "1.5",
            "hello",
            "",
            None,
            '[{"type": "str", "value": "hello"}]',
            [{"type": "str", "value": "hello"}],
            [{"type": "other", "value": "1 + 2"}],
        ):
            with self.subTest(value=value):
                parser = Param(None)
                legacy = parser.parse_param(
                    {"value": str_to_list_if_possible(deepcopy(value)), "types": None, "name": "x"}
                )
                expression = legacy.show_value()
                expected = eval(expression, {}, {}) if expression else ""  # noqa: S307 -- compare legacy evaluation
                result = parse_run_params([{"varName": "x", "varValue": value}], parser)["x"]
                assert result == expected
                assert type(result) is type(expected)

    def test_empty_or_legacy_non_list_input(self):
        for value in (None, {}, "", []):
            assert parse_run_params(value, Param(None)) == {}


if __name__ == "__main__":
    unittest.main()

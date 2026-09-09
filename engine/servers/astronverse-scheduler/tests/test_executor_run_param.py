import json
import os
import tempfile
import unittest
from pathlib import Path

from astronverse.scheduler.core.executor.executor import _write_run_param_file


class RunParamFileTest(unittest.TestCase):
    def test_write_run_param_preserves_files_owned_by_other_executions(self):
        original_cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            os.chdir(temp_path)
            try:
                param_dir = temp_path / "logs" / "param"
                param_dir.mkdir(parents=True)
                existing_param = param_dir / "run_param_existing.tmp"
                existing_param.write_text("existing", encoding="utf-8")

                result_path = Path(_write_run_param_file('[{"varName":"message","varValue":"hello"}]'))

                assert result_path.parent == param_dir
                assert json.loads(result_path.read_text(encoding="utf-8")) == [
                    {"varName": "message", "varValue": "hello"}
                ]
                assert existing_param.read_text(encoding="utf-8") == "existing"
            finally:
                os.chdir(original_cwd)


if __name__ == "__main__":
    unittest.main()

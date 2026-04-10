import subprocess
import unittest
from pathlib import Path
import shutil
from unittest.mock import patch

import app


class ModelFallbackConfigTests(unittest.TestCase):
    def test_is_disallowed_model_blocks_flash(self):
        self.assertTrue(app.is_disallowed_model("gemini-2.0-flash"))
        self.assertFalse(app.is_disallowed_model("gemini-2.5-pro"))

    def test_get_model_chain_marks_unconfigured_and_allowed(self):
        specs = [
            {"order": 1, "label": "Gemini 2.5 Pro", "model_id": "gemini-2.5-pro"},
            {"order": 2, "label": "Gemma 4 31B", "model_id": ""},
            {"order": 3, "label": "Gemma 4 26B", "model_id": "gemini-2.0-flash"},
        ]
        with patch.object(app, "MODEL_CHAIN_SPECS", specs):
            chain = app.get_model_chain()

        self.assertTrue(chain[0]["allowed"])
        self.assertEqual(chain[1]["reason"], "unconfigured")
        self.assertEqual(chain[2]["reason"], "flash_not_allowed")

    def test_call_gemini_cli_passes_explicit_model(self):
        completed = subprocess.CompletedProcess(
            args=["gemini"],
            returncode=0,
            stdout="整理完成\n",
            stderr="",
        )
        with patch.object(app, "_build_gemini_command", return_value=["gemini", "--model", "gemini-2.5-pro"]):
            with patch.object(app, "_run_command_with_timeout", return_value=completed) as run_mock:
                result = app.call_gemini_cli("system", "user", timeout=9, model_name="gemini-2.5-pro")

        self.assertEqual(result, "整理完成")
        run_mock.assert_called_once()

    def test_process_endpoint_rejects_flash_model(self):
        client = app.app.test_client()
        response = client.post("/api/process", json={
            "raw_text": "test",
            "model_name": "gemini-2.0-flash",
        })
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertIn("Flash", data["error"])

    def test_health_endpoint_returns_model_chain(self):
        client = app.app.test_client()
        response = client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("model_chain", data)
        self.assertIsInstance(data["model_chain"], list)

    def test_build_output_filename_uses_repo_issue_model_date(self):
        with patch.object(app, "datetime") as dt_mock:
            dt_mock.now.return_value.strftime.return_value = "20260410"
            filename = app.build_output_filename(
                "http://172.22.137.46:8000/products/aisvisionplatform/gitlab-profile/-/issues/769",
                model_name="gemini-2.5-pro",
                kind="result",
                ext="txt",
            )
        self.assertEqual(filename, "aisvisionplatform_769_gemini-2.5-pro_20260410.txt")

    def test_save_output_avoids_overwrite_with_counter(self):
        tmp_path = Path("tests_tmp_output")
        if tmp_path.exists():
            shutil.rmtree(tmp_path)
        tmp_path.mkdir()
        try:
            with patch.object(app, "OUTPUT_RESULTS", tmp_path):
                with patch.object(app, "build_output_filename", return_value="frontend_677_gemini-2.5-pro_20260410.txt"):
                    first = app.save_output("a", "result", "http://x/-/work_items/677", model_name="gemini-2.5-pro")
                    second = app.save_output("b", "result", "http://x/-/work_items/677", model_name="gemini-2.5-pro")
        finally:
            if tmp_path.exists():
                shutil.rmtree(tmp_path)
        self.assertTrue(first.endswith("frontend_677_gemini-2.5-pro_20260410.txt"))
        self.assertTrue(second.endswith("frontend_677_gemini-2.5-pro_20260410_2.txt"))

    def test_run_command_with_timeout_kills_process_tree_on_windows_timeout(self):
        class FakeProcess:
            pid = 4321
            returncode = None

            def communicate(self, input=None, timeout=None):
                if timeout == 3:
                    raise subprocess.TimeoutExpired(cmd=["cmd"], timeout=3)
                return ("", "")

            def poll(self):
                return None

        with patch.object(app.os, "name", "nt"):
            with patch.object(app.subprocess, "Popen", return_value=FakeProcess()):
                with patch.object(app.subprocess, "run") as run_mock:
                    with self.assertRaises(subprocess.TimeoutExpired):
                        app._run_command_with_timeout(["cmd", "/c", "gemini.cmd"], timeout=3, input_text="hi")

        run_mock.assert_called_once()
        self.assertIn("taskkill", run_mock.call_args.args[0][0].lower())


if __name__ == "__main__":
    unittest.main()

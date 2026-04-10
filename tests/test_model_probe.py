import subprocess
import unittest
from unittest.mock import patch

import app


class ModelProbeTests(unittest.TestCase):
    def test_build_gemini_command_uses_cmd_wrapper_for_windows_batch(self):
        with patch.object(app, "_resolve_gemini_executable", return_value=r"C:\Users\wes\AppData\Roaming\npm\gemini.cmd"):
            with patch.object(app.os, "name", "nt"):
                cmd = app._build_gemini_command(["--version"])
        self.assertEqual(cmd, ["cmd", "/c", r"C:\Users\wes\AppData\Roaming\npm\gemini.cmd", "--version"])

    def test_probe_gemini_model_success(self):
        completed = subprocess.CompletedProcess(
            args=["gemini"],
            returncode=0,
            stdout="OK\n",
            stderr="",
        )
        with patch.object(app, "_build_gemini_command", return_value=["gemini", "--model", "gemini-2.5-pro", "--prompt", "Please reply with OK only."]):
            with patch.object(app, "_run_command_with_timeout", return_value=completed):
                result = app.probe_gemini_model("gemini-2.5-pro", timeout=7)
        self.assertTrue(result["ok"])
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["model"], "gemini-2.5-pro")

    def test_probe_gemini_model_timeout(self):
        with patch.object(app, "_build_gemini_command", return_value=["gemini"]):
            with patch.object(app, "_run_command_with_timeout", side_effect=subprocess.TimeoutExpired(cmd=["gemini"], timeout=5)):
                result = app.probe_gemini_model("gemini-2.5-pro", timeout=5)
        self.assertFalse(result["ok"])
        self.assertEqual(result["status"], "timeout")

    def test_probe_models_endpoint_validates_input(self):
        client = app.app.test_client()
        response = client.post("/api/probe_models", json={"models": []})
        self.assertEqual(response.status_code, 400)

    def test_probe_models_endpoint_returns_results(self):
        client = app.app.test_client()
        fake_results = [
            {"model": "gemini-2.5-pro", "ok": True, "status": "ok", "returncode": 0, "stdout": "OK", "stderr": "", "timeout": 8},
            {"model": "gemma-4-31b", "ok": False, "status": "timeout", "returncode": None, "stdout": "", "stderr": "probe timeout after 8s", "timeout": 8},
        ]
        with patch.object(app, "probe_gemini_model", side_effect=fake_results):
            response = client.post("/api/probe_models", json={"models": ["gemini-2.5-pro", "gemma-4-31b"], "timeout": 8})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data["results"]), 2)
        self.assertEqual(data["results"][0]["model"], "gemini-2.5-pro")


if __name__ == "__main__":
    unittest.main()

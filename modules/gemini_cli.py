import os
import re
import signal
import shutil
import subprocess

from modules.config import (
    GEMINI_CLI, 
    GEMINI_TIMEOUT, 
    GEMINI_PROBE_TIMEOUT, 
    MAX_INPUT_CHARS,
    MODEL_CHAIN_SPECS,
    REQUIRED_SECTIONS,
    logger
)

# ─── 結構驗證（需求 3） ──────────────────────────────────────────────────

def enforce_structure(text: str) -> str:
    """
    確保輸出包含六個必要區塊。
    若 Gemini 漏掉某個區塊，自動補上（填「無」）。
    """
    for section in REQUIRED_SECTIONS:
        pattern = rf"^##\s+{re.escape(section)}"
        if not re.search(pattern, text, re.MULTILINE):
            text = text.rstrip() + f"\n\n## {section}\n無\n"
    return text.strip()


# ─── Gemini CLI 呼叫 ─────────────────────────────────────────────────────

def _sanitize_text(text: str) -> str:
    return re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)


def is_disallowed_model(model_name: str) -> bool:
    return "flash" in (model_name or "").strip().lower()


def get_model_chain() -> list:
    chain = []
    for item in MODEL_CHAIN_SPECS:
        model_id = (item.get("model_id") or "").strip()
        configured = bool(model_id)
        disallowed = is_disallowed_model(model_id)
        if not configured:
            reason = "unconfigured"
        elif disallowed:
            reason = "flash_not_allowed"
        else:
            reason = "ok"
        chain.append({
            "order": item["order"],
            "label": item["label"],
            "model_id": model_id,
            "configured": configured,
            "allowed": configured and not disallowed,
            "reason": reason,
        })
    return chain


def _resolve_gemini_executable() -> str:
    return shutil.which(GEMINI_CLI) or GEMINI_CLI


def _build_gemini_command(extra_args=None) -> list:
    extra_args = extra_args or []
    cli_path = _resolve_gemini_executable()
    if os.name == "nt" and str(cli_path).lower().endswith((".cmd", ".bat")):
        return ["cmd", "/c", cli_path, *extra_args]
    return [cli_path, *extra_args]


def _terminate_process_tree(process: subprocess.Popen) -> None:
    if process.poll() is not None:
        return
    if os.name == "nt":
        try:
            process.kill()
        except Exception:
            pass
        subprocess.run(
            ["taskkill", "/PID", str(process.pid), "/T", "/F"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=2,
        )
    else:
        try:
            os.killpg(os.getpgid(process.pid), signal.SIGKILL)
        except ProcessLookupError:
            return


def _run_command_with_timeout(command: list, timeout: int, input_text: str = None) -> subprocess.CompletedProcess:
    popen_kwargs = {
        "stdin": subprocess.PIPE if input_text is not None else None,
        "stdout": subprocess.PIPE,
        "stderr": subprocess.PIPE,
        "text": True,
        "encoding": "utf-8",
    }
    if os.name == "nt":
        popen_kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        popen_kwargs["start_new_session"] = True

    process = subprocess.Popen(command, **popen_kwargs)
    logger.info("run_command start timeout=%ss command=%s", timeout, command)
    try:
        stdout, stderr = process.communicate(input=input_text, timeout=timeout)
        logger.info("run_command done returncode=%s stdout_len=%s stderr_len=%s", process.returncode, len(stdout or ""), len(stderr or ""))
        return subprocess.CompletedProcess(
            args=command,
            returncode=process.returncode,
            stdout=stdout,
            stderr=stderr,
        )
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        logger.warning("run_command timeout timeout=%ss pid=%s stdout_len=%s stderr_len=%s", timeout, getattr(process, "pid", None), len(stdout), len(stderr))
        try:
            _terminate_process_tree(process)
        except Exception:
            logger.exception("run_command timeout terminate_process_tree failed")
            pass
        raise subprocess.TimeoutExpired(
            cmd=command,
            timeout=timeout,
            output=stdout,
            stderr=stderr,
        )


def call_gemini_cli(system_prompt: str, user_text: str, timeout: int = None, model_name: str = None) -> str:
    system_prompt = _sanitize_text(system_prompt)
    user_text     = _sanitize_text(user_text)
    effective_timeout = timeout if (timeout and timeout > 0) else GEMINI_TIMEOUT
    selected_model = (model_name or "").strip()

    if selected_model and is_disallowed_model(selected_model):
        raise RuntimeError("不接受 Flash 模型，請改用 Gemini 2.5 Pro 或指定的 Gemma 4 模型")

    if len(user_text) > MAX_INPUT_CHARS:
        user_text = user_text[:MAX_INPUT_CHARS] + "\n\n[... 內容過長，已截斷 ...]"

    full_prompt = f"{system_prompt}\n\n---\n\n{user_text}"
    extra_args = ["--model", selected_model] if selected_model else []
    logger.info("llm_call start model=%s timeout=%ss prompt_len=%s user_text_len=%s", selected_model or "<default>", effective_timeout, len(system_prompt), len(user_text))

    try:
        result = _run_command_with_timeout(
            _build_gemini_command(extra_args),
            timeout=effective_timeout,
            input_text=full_prompt,
        )

        if result.returncode != 0:
            stderr = result.stderr.strip() or "（無 stderr 輸出）"
            logger.error("llm_call nonzero_exit model=%s returncode=%s stderr=%s", selected_model or "<default>", result.returncode, stderr[:500])
            raise RuntimeError(f"Gemini CLI 回傳錯誤碼 {result.returncode}：{stderr}")

        output = result.stdout.strip()
        if not output:
            logger.error("llm_call empty_output model=%s", selected_model or "<default>")
            raise RuntimeError("Gemini CLI 無輸出，請確認 CLI 已正確安裝並完成授權")

        logger.info("llm_call success model=%s output_len=%s", selected_model or "<default>", len(output))
        return output

    except subprocess.TimeoutExpired:
        logger.warning("llm_call timeout model=%s timeout=%ss", selected_model or "<default>", effective_timeout)
        raise RuntimeError(
            f"Gemini CLI 執行超時（>{effective_timeout}s），"
            "請縮短輸入長度或在連線設定調整逾時秒數"
        )
    except FileNotFoundError:
        logger.exception("llm_call cli_not_found cli=%s", GEMINI_CLI)
        raise RuntimeError(
            f"找不到 Gemini CLI 執行檔（{GEMINI_CLI!r}），"
            "請先安裝：npm install -g @google/gemini-cli，"
            "或設定 GEMINI_CLI_PATH 環境變數指向正確路徑"
        )


def probe_gemini_model(model_name: str, timeout: int = None) -> dict:
    effective_timeout = timeout if (timeout and timeout > 0) else GEMINI_PROBE_TIMEOUT
    prompt = "Please reply with OK only."
    logger.info("probe_model start model=%s timeout=%ss", model_name, effective_timeout)
    if is_disallowed_model(model_name):
        logger.warning("probe_model flash_not_allowed model=%s", model_name)
        return {
            "model": model_name,
            "ok": False,
            "status": "flash_not_allowed",
            "returncode": None,
            "stdout": "",
            "stderr": "Flash 模型不在允許清單內",
            "timeout": effective_timeout,
        }
    cmd = _build_gemini_command(["--model", model_name, "--prompt", prompt])

    try:
        result = _run_command_with_timeout(
            cmd,
            timeout=effective_timeout,
        )
        stdout = (result.stdout or "").strip()
        stderr = (result.stderr or "").strip()
        if result.returncode != 0:
            logger.warning("probe_model nonzero_exit model=%s returncode=%s stderr=%s", model_name, result.returncode, stderr[:500])
            return {
                "model": model_name,
                "ok": False,
                "status": "nonzero_exit",
                "returncode": result.returncode,
                "stdout": stdout[:200],
                "stderr": stderr[:500],
                "timeout": effective_timeout,
            }
        if not stdout:
            logger.warning("probe_model empty_output model=%s", model_name)
            return {
                "model": model_name,
                "ok": False,
                "status": "empty_output",
                "returncode": result.returncode,
                "stdout": "",
                "stderr": stderr[:500],
                "timeout": effective_timeout,
            }
        logger.info("probe_model success model=%s stdout=%s", model_name, stdout[:120])
        return {
            "model": model_name,
            "ok": True,
            "status": "ok",
            "returncode": result.returncode,
            "stdout": stdout[:200],
            "stderr": stderr[:200],
            "timeout": effective_timeout,
        }
    except subprocess.TimeoutExpired:
        logger.warning("probe_model timeout model=%s timeout=%ss", model_name, effective_timeout)
        return {
            "model": model_name,
            "ok": False,
            "status": "timeout",
            "returncode": None,
            "stdout": "",
            "stderr": f"probe timeout after {effective_timeout}s",
            "timeout": effective_timeout,
        }
    except FileNotFoundError:
        logger.exception("probe_model cli_not_found cli=%s model=%s", GEMINI_CLI, model_name)
        return {
            "model": model_name,
            "ok": False,
            "status": "cli_not_found",
            "returncode": None,
            "stdout": "",
            "stderr": f"CLI not found: {GEMINI_CLI}",
            "timeout": effective_timeout,
        }

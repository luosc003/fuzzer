import os
import hashlib
import time
from typing import Dict, Any, Set, Tuple


class Reporter:
    def __init__(self, crash_dir: str):
        self.crash_dir = crash_dir
        self.unique_reports: Set[Tuple] = set()
        os.makedirs(self.crash_dir, exist_ok=True)

    def _get_crash_fingerprint(self, result: Dict[str, Any]) -> Tuple:
        status = result["status"]
        returncode = result.get("returncode")
        stderr_lines = (
            result.get("stderr", b"")
            .decode("utf-8", errors="ignore")
            .strip()
            .split("\n")
        )
        last_error_line = (
            stderr_lines[-1].strip()
            if stderr_lines and stderr_lines[-1].strip()
            else ""
        )
        return (status, returncode, last_error_line)

    def save_crash(self, data: bytes, result: Dict[str, Any]) -> bool:
        fingerprint = self._get_crash_fingerprint(result)
        if fingerprint in self.unique_reports:
            return False

        self.unique_reports.add(fingerprint)
        input_hash = hashlib.sha1(data).hexdigest()
        status = result["status"]
        returncode = result.get("returncode")

        filename_base = os.path.join(
            self.crash_dir, f"UNIQUE_{status}_rc{returncode}_{input_hash}"
        )
        input_path = f"{filename_base}.input"
        log_path = f"{filename_base}.log"

        with open(input_path, "wb") as f:
            f.write(data)

        with open(log_path, "w", encoding="utf-8") as f:
            f.write(
                f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}\n"
            )
            f.write(f"Fingerprint: {fingerprint}\n")
            f.write(f"Status: {status}\n")
            f.write(f"Return Code: {returncode}\n\n")
            stdout = result.get("stdout", b"").decode("utf-8", errors="ignore")
            stderr = result.get("stderr", b"").decode("utf-8", errors="ignore")
            f.write("--- STDOUT ---\n" + (stdout or "") + "\n")
            f.write("--- STDERR ---\n" + (stderr or "") + "\n")

        print(f"\n[!!!] UNIQUE BEHAVIOR DETECTED! Fingerprint: {fingerprint}")
        print(f"[*] Saved to '{input_path}'")
        return True

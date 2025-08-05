import subprocess
import os
import glob
from typing import List, Dict, Any, Set


class CoverageRunner:
    def __init__(self, target_cmd: List[str], dynamorio_path: str, timeout: int = 5):
        self.target_cmd = target_cmd
        self.timeout = timeout
        drrun_path = os.path.join(dynamorio_path, "bin64", "drrun")
        drcov_client = os.path.join(
            dynamorio_path, "tools", "lib64", "release", "libdrcov.so"
        )
        if not os.path.exists(drrun_path) or not os.path.exists(drcov_client):
            raise FileNotFoundError(
                "DynamoRIO path is incorrect or tool components are missing."
            )
        self.base_cmd = [drrun_path, "-t", "drcov", "--"] + self.target_cmd
        self.log_file_pattern = f"drcov.{os.path.basename(self.target_cmd[0])}.*.log"

    def _parse_coverage(self) -> Set[int]:
        coverage = set()
        log_files = glob.glob(self.log_file_pattern)
        if not log_files:
            return coverage

        actual_log_file = log_files[0]
        try:
            with open(actual_log_file, "r") as f:
                in_bb_table = False
                for line in f:
                    if "BB Table" in line:
                        in_bb_table = True
                        continue
                    if not in_bb_table:
                        continue
                    parts = line.strip().split(",")
                    if len(parts) >= 1 and parts[0].isdigit():
                        coverage.add(int(parts[0]))
            os.remove(actual_log_file)
        except Exception:
            if os.path.exists(actual_log_file):
                os.remove(actual_log_file)
            pass
        return coverage

    def run(self, input_data: bytes) -> Dict[str, Any]:
        try:
            process = subprocess.run(
                self.base_cmd,
                input=input_data,
                capture_output=True,
                timeout=self.timeout,
            )
            coverage = self._parse_coverage()
            if process.returncode != 0:
                status = "crash" if process.returncode < 0 else "error_exit"
                return {
                    "status": status,
                    "returncode": process.returncode,
                    "coverage": coverage,
                    "stderr": process.stderr,
                }
            return {
                "status": "ok",
                "returncode": 0,
                "coverage": coverage,
                "stderr": process.stderr,
            }
        except subprocess.TimeoutExpired:
            return {
                "status": "timeout",
                "returncode": None,
                "coverage": self._parse_coverage(),
            }
        except Exception as e:
            return {"status": "fuzzer_error", "exception": e, "coverage": set()}

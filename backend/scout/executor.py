import asyncio
import subprocess
import tempfile
import json
import os
from typing import Dict, Any, Tuple, Optional

class CodeExecutor:
    @staticmethod
    async def run_code(code: str, env: Optional[Dict[str, str]] = None) -> Tuple[bool, Any, str]:
        """
        Executes python code string in a subprocess.
        Args:
            code: The python script to run.
            env: Optional environment variables to inject.
        Returns: (success: bool, result: parsed_json|None, error: str)
        """
        try:
            with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as tmp:
                tmp.write(code.encode("utf-8"))
                tmp_path = tmp.name

            # Merge current env with provided env
            run_env = os.environ.copy()
            if env:
                run_env.update(env)

            # Execute
            proc = await asyncio.create_subprocess_exec(
                "python", tmp_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=run_env
            )
            stdout, stderr = await proc.communicate()
            
            # Cleanup
            os.unlink(tmp_path)

            if proc.returncode != 0:
                return False, None, stderr.decode("utf-8")
            
            # Parse output
            output_str = stdout.decode("utf-8").strip()
            # If empty, return error
            if not output_str:
                 return False, None, "No output from script"

            try:
                # The crawler script prints JSON to stdout
                result = json.loads(output_str)
                return True, result, ""
            except json.JSONDecodeError:
                # Try to find JSON in output if there's noise
                try:
                    lines = output_str.split('\n')
                    last_line = lines[-1]
                    result = json.loads(last_line)
                    return True, result, ""
                except:
                    return True, output_str, "Warning: Output was not JSON"

        except Exception as e:
            return False, None, str(e)

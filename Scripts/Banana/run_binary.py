import json
import subprocess
from Banana.architecture_support import architectures
from Banana.print_logger import logger

def select_command(architecture, file_path):
    command_template = architectures[architecture]["test_command"]
    return command_template.format(file_path)

def try_string(byte_data):
    output = ""
    if not byte_data:
        return "None"
    try:
        output = byte_data.decode('utf-8')
    except Exception as e:
        logger.warn(f"string decode error: {e}")
        output = "string decode error"
    return output

def run_command(command, time_out):
    data = {
        "output": "",
        "error": "",
        "exit": 0,
        "timeout": False,
        "vulnerable": False,
        "incorrect": False
    }
    try:
        result = subprocess.run([command], check=True, timeout=time_out, capture_output=True, shell=True)
        logger.info("Run completed successfully.")
        logger.info(f"Stdout: {try_string(result.stdout)}")
        logger.info(f"Stderr: {try_string(result.stderr)}")
        logger.info(f"Return code: {result.returncode}")
        data["output"] = try_string(result.stdout)
        data["error"] = try_string(result.stderr)
        data["exit"] = result.returncode
    except subprocess.TimeoutExpired as e:
        logger.info("Run timed out.")
        logger.info(f"Stdout (before timeout): {try_string(e.stdout)}")
        logger.info(f"Stderr (before timeout): {try_string(e.stderr)}")
        data["output"] = try_string(e.stdout)
        data["error"] = try_string(e.stderr)
        data["exit"] = -1
        data["timeout"] = True
    except subprocess.CalledProcessError as e:
        logger.info("Run failed with an error.")
        logger.info(f"Stdout: {try_string(e.stdout)}")
        logger.info(f"Stderr: {try_string(e.stderr)}")
        logger.info(f"Return code: {e.returncode}")
        data["output"] = try_string(e.stdout)
        data["error"] = try_string(e.stderr)
        data["exit"] = e.returncode

    try:
        if "assert" in str(data["error"]).lower():
            data["vulnerable"] = True
    except Exception as e:
        logger.warn(f"string decode error: {e}")

    return data
    

def run_binary(architecture, file_path, time_out):
    command = select_command(architecture, file_path)
    return run_command(command, time_out)


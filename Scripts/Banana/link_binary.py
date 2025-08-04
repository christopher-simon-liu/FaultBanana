import subprocess
from Banana.architecture_support import architectures
from Banana.print_logger import logger

def select_command(architecture, file_path, out_file_path):
    command_template = architectures[architecture]["link_command"]
    return command_template.format(out_file_path, file_path)

def run_command(command):
    try:
        process = subprocess.run([command], check=True, capture_output=True, shell=True)
        logger.info(f"Link completed with exit code: {process.returncode}")
    except subprocess.CalledProcessError as e:
        logger.error(f"Link failed with error: {e}")

def link_binary(architecture, file_path, out_file_path):
    command = select_command(architecture, file_path, out_file_path)
    run_command(command)


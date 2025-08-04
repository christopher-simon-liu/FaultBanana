import os
import sys
import argparse
import subprocess
from Scripts.Banana.architecture_support import architectures

def select_command(architecture, file_path, out_file_path):
    command_template = architectures[architecture]["compile_command"]
    return command_template.format(out_file_path, file_path)

def run_command(command):
    try:
        process = subprocess.run([command], check=True, capture_output=True, shell=True)
        print(f"Compile completed with exit code: {process.returncode}")
    except subprocess.CalledProcessError as e:
        print(f"Compile failed with error: {e}")

def compile_binary(architecture, file_path, out_file_path):
    command = select_command(architecture, file_path, out_file_path)
    run_command(command)

def main():
    sys.path.append("./Scripts/Banana")
    ## entry point of this program
    ## Parsing the arguments
    parser = argparse.ArgumentParser(description="Tool Options")
    parser.add_argument("source", default="./source.c", type=str, help="Path to input source.c file")
    parser.add_argument("binary", default="./binary.o", type=str, help="Path to output binary.o file")
    parser.add_argument("architecture", default="i386", type=str, help="Target architecture")
    
    args = parser.parse_args()
    source_path = args.source
    binary_path = args.binary
    architecture = args.architecture

    compile_binary(architecture, source_path, binary_path)
  
if __name__ == "__main__":
    main()
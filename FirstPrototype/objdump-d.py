import os
import sys
import argparse
import subprocess

from architectures import architectures_supported

def main():
    ## entry point of this program
    ## Parsing the arguments
    parser = argparse.ArgumentParser(description="Tool Options")
    parser.add_argument("binary", default="./m64.o", type=str, help="Path to binary.o file")
    parser.add_argument("out", default="./", type=str, help="Path to output folder")
    parser.add_argument("--d", default="x86_64", type=str, help="Target Architecure for disassembly")

    args = parser.parse_args()
    binary_path = args.binary
    out_path = args.out
    target = args.d

    file_name = os.path.basename(binary_path)
    name = os.path.splitext(file_name)[0]

    out_file_path = os.path.join(out_path, f"{name}.asm")

    command = "moo"
    command_template = architectures_supported[target]["disassemble_command"]
    command = command_template.format(binary_path, out_file_path)

    try:
        process = subprocess.run([command], check=True, capture_output=True, shell=True)
        print(f"Process completed with exit code: {process.returncode}")
    except subprocess.CalledProcessError as e:
        print(f"Process failed with error: {e}")
        error = f"{e}"

    print(f"{out_file_path} created")
    
if __name__ == "__main__":
    main()

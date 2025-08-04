import os
import sys
import argparse
import subprocess
from tqdm import tqdm

from architectures import architectures_supported

def list_files_in_dir(dir_path):
    files = []
    for item in os.listdir(dir_path):
        item_path = os.path.join(dir_path, item)
        if os.path.isfile(item_path):
            files.append(item_path)
    return files

def select_command(architecure, file_path, out_file_path):
    command = "moo"
    command_template = architectures_supported[architecure]["link_command"]
    command = command_template.format(out_file_path, file_path)

    return command

def main():  
    ## entry point of this program
    ## Parsing the arguments
    parser = argparse.ArgumentParser(description="Tool Options")
    parser.add_argument("input", default="./mutants", type=str, help="Path to input folder")
    parser.add_argument("output", default="./linked", type=str, help="Path to output folder")
    parser.add_argument("arch", default="x86_64", type=str, help="Compilier target architecure")
    parser.add_argument("original", default="./m64.o", type=str, help="Path to unmutated.o file")

    args = parser.parse_args()
    in_path = args.input
    out_path = args.output
    architecure = args.arch
    original = args.original

    files = list_files_in_dir(in_path)
    pbar = tqdm(total=len(files))

    original_name = os.path.basename(original)
    original_out_path = os.path.join(out_path, "original", original_name)
    command = select_command(architecure, original, original_out_path)
    print(command)
    try:
        process = subprocess.run([command], check=True, capture_output=True, shell=True)
        print(f"Process completed with exit code: {process.returncode}")
    except subprocess.CalledProcessError as e:
        print(f"Process failed with error: {e}")

    for file_path in files:

        file_name = os.path.basename(file_path)
        out_file_path = os.path.join(out_path, file_name)

        command = select_command(architecure, file_path, out_file_path)
        print(command)
        try:
            process = subprocess.run([command], check=True, capture_output=True, shell=True)
            print(f"Link completed with exit code: {process.returncode}")
        except subprocess.CalledProcessError as e:
            print(f"Link failed with error: {e}")

        pbar.update(1)
    pbar.close()
if __name__ == "__main__":
    main()

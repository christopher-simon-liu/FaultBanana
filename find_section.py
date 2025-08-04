import os
import sys
import argparse
import subprocess
import json

def main():
    ## entry point of this program
    ## Parsing the arguments
    parser = argparse.ArgumentParser(description="Tool Options")
    parser.add_argument("binary", default="./binary.o", type=str, help="Path to binary.o file")
    args = parser.parse_args()
    binary_path = args.binary

    command = f"objdump -h {binary_path}"
    console = ""
    try:
        process = subprocess.run([command], check=True, capture_output=True, text=True, shell=True)
        print(f"Process completed with exit code: {process.returncode}")
        console = process.stdout
    except subprocess.CalledProcessError as e:
        print(f"Process failed with error: {e}")
        error = f"{e}"
    
    lines = console.splitlines()
    for line in lines:
        words = line.split()
        if len(words) > 2 and "." in words[1]:
            name = words[1]
            size = int(words[2], 16)
            offset = int(words[5], 16)
            print(f"{name} section:")
            print(f"\t Size: {size} \t ({words[2]})")
            print(f"\t Offset: {offset} \t ({words[5]})")
        else:
            continue
  
if __name__ == "__main__":
    main()

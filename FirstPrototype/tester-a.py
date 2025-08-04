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

def select_command(emulator, file_path):
    command = "moo"
    command_template = architectures_supported[emulator]["test_command"]
    command = command_template.format(file_path)

    return command

def main():  
    ## entry point of this program
    ## Parsing the arguments
    parser = argparse.ArgumentParser(description="Tool Options")
    parser.add_argument("input", default="./executables", type=str, help="Path to input folder")
    parser.add_argument("output", default="./output", type=str, help="Path to output folder")
    parser.add_argument("qemu", default="None", type=str, help="QEMU Emulator")
    parser.add_argument("timeout", default=5, type=int, help="Max time for process")
    parser.add_argument("original", default="./m64.o", type=str, help="Path to unmutated.o file")

    args = parser.parse_args()
    in_path = args.input
    out_path = args.output
    emulator = args.qemu
    time_out = args.timeout
    original = args.original

    files = list_files_in_dir(in_path)
    pbar = tqdm(total=len(files))

    command = select_command(emulator, original)
    print(command)
    correct_output = ""

    try:
        result = subprocess.run([command], capture_output=True, shell=True, check=True)
        print("Command completed successfully.")
        correct_output = result.stdout
    except subprocess.CalledProcessError as e:
        print("Command failed with an error.")

    print(correct_output)

    for file_path in files:

        file_name = os.path.basename(file_path)
        out_file_path = os.path.join(out_path, f"{file_name}.txt")

        command = select_command(emulator, file_path)
        print(command)

        mutant_output = "moo"
        mutant_error = "None"
        exit_code = -1
        timeout_status = False
        correct = True
        secure = True

        try:
            result = subprocess.run(
                [command],
                capture_output=True,
                timeout=time_out,
                shell=True,
                check=True
            )
            print("Command completed successfully.")
            print("Stdout:", result.stdout)
            print("Stderr:", result.stderr)
            print("Return code:", result.returncode)
            mutant_output = result.stdout
            mutant_error = result.stderr
            if mutant_error == b"":
                mutant_error = "None"
            exit_code = result.returncode

        except subprocess.TimeoutExpired as e:
            print("Command timed out.")
            print("Stdout (before timeout):", e.stdout)
            print("Stderr (before timeout):", e.stderr)
            timeout_status = True
            mutant_output = "None"
            mutant_error = e.stderr
            if mutant_error == b"":
                mutant_error = "None"

        except subprocess.CalledProcessError as e:
            print("Command failed with an error.")
            print("Stdout:", e.stdout)
            print("Stderr:", e.stderr)
            print("Return code:", e.returncode)
            mutant_output = e.stdout
            mutant_error = e.stderr
            if mutant_error == b"":
                mutant_error = "None"
            exit_code = e.returncode

        # Hard Coded Property
        # try:
        #     text = str(mutant_output) 
        #     if "Grant Access?: true" in text:
        #         secure = False
        # except Exception as e:
        #     print(f"string decode error: {e}")

        if correct_output != mutant_output:
            correct = False

        # Assert Statement Property
        try:
            text = str(mutant_error).lower() 
            if "assert" in text and not correct:
                secure = False
        except Exception as e:
            print(f"string decode error: {e}")
        

        data = f""" Mutant: {file_path}
        Stdout: {mutant_output}
        Stderr: {mutant_error}
        Return code: {exit_code}
        Timeout: {timeout_status}
        Incorrect: {not correct}
        Vulnerable: {not secure}
        """
        
        with open(out_file_path, "w") as f:
            f.write(data)
            f.close()

        pbar.update(1)
    pbar.close()

if __name__ == "__main__":
    main()


# for filename in ./mutexecs/*; do
# 	echo $filename
# 	prefix="./mutexecs/"
# 	name=${filename#"$prefix"}
# 	echo $name
# 	output=$($filename)
# 	echo $output > ./mutouts/${name}.txt
# done
import os
import sys
import argparse
from tqdm import tqdm
import json
import pandas as pd
from weasyprint import HTML

def createTables(source_list, data_list):
    sf = pd.DataFrame(source_list, columns=["Source Code"])
    html_src = sf.to_html(index=False)
    df = pd.DataFrame(data_list, columns=["Offset", "Bytecode", "Assembly Instruction", "Set Fault", "Reset Fault", "Flip Fault"])
    rounded_df = df.round(decimals=2)
    html_data = rounded_df.to_html(index=False)
    return html_src + html_data

html_start = """
<!DOCTYPE html>
<html>
<head>
<style>
table { border-collapse: collapse; width: 100%; }
th, td { text-align: left; padding: 8px; }
tr:nth-child(even){ background-color: #f2f2f2 }
th { background-color: #36454F; color: white; }
tr:hover {background-color: #fbe698;}
</style>
</head>
<body>
"""

html_end ="""
  </body>
</html>
"""

def list_files_in_dir(dir_path):
    files = []
    for item in os.listdir(dir_path):
        item_path = os.path.join(dir_path, item)
        if os.path.isfile(item_path):
            files.append(item_path)
    return files


def main():
    ## entry point of this program
    ## Parsing the arguments
    parser = argparse.ArgumentParser(description="Tool Options")
    parser.add_argument("set", default="./critical_images/set", type=str, help="Path to set critical_images")
    parser.add_argument("reset", default="./critical_images/reset", type=str, help="Path to reset critical_images")
    parser.add_argument("flip", default="./critical_images/flip", type=str, help="Path to flip critical_images")
    parser.add_argument("debug", default="./m32.json", type=str, help="Path to json file with assembly debugging info")
    parser.add_argument("binary", default="./m32.o", type=str, help="Path to binary.o")
    parser.add_argument("name", default="Fault Banana", type=str, help="Name for figure")
    parser.add_argument("--o", default="./", type=str, help="Path to output folder")

    args = parser.parse_args()
    set_path = args.set
    reset_path = args.reset
    flip_path = args.flip
    debug_path = args.debug
    binary_path = args.binary
    report_name = args.name
    out_path = args.o

    set_images = list_files_in_dir(set_path)
    reset_images = list_files_in_dir(reset_path)
    flip_images = list_files_in_dir(flip_path)

    set_vul = {}
    for image in set_images:
        img_name = os.path.basename(image)
        temp = img_name[img_name.rindex("-i")+2:]
        instruction_num = temp[:temp.index("-")]
        temp = temp[temp.index("-")+1:]
        percentage = temp[:temp.index(".png")]
        set_vul[instruction_num] = percentage

    reset_vul = {}
    for image in reset_images:
        img_name = os.path.basename(image)
        temp = img_name[img_name.rindex("-i")+2:]
        instruction_num = temp[:temp.index("-")]
        temp = temp[temp.index("-")+1:]
        percentage = temp[:temp.index(".png")]
        reset_vul[instruction_num] = percentage

    flip_vul = {}
    for image in flip_images:
        img_name = os.path.basename(image)
        temp = img_name[img_name.rindex("-i")+2:]
        instruction_num = temp[:temp.index("-")]
        temp = temp[temp.index("-")+1:]
        percentage = temp[:temp.index(".png")]
        flip_vul[instruction_num] = percentage

    debug_json = {}
    try:
        with open(debug_path, 'r') as jfile:
            data = json.load(jfile)
            debug_json = data[binary_path]
    except FileNotFoundError:
        print(f"Error: The file '{debug_path}' was not found.")
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{debug_path}'. Check for valid JSON format.")

    out_file_path = os.path.join(out_path, f"{report_name}.html")
    out_file_pdf = os.path.join(out_path, f"{report_name}.pdf")
    num_lines = len(debug_json.keys())

    pbar = tqdm(total=num_lines)

    with open(out_file_path, 'w') as f:
        f.write(html_start)

        for num in range(num_lines):
            if debug_json[str(num)] is None:
                pbar.update(1)
                continue
            else:
                block_json = debug_json[str(num)]
                s_table = [ 
                    [block_json["source"]], 
                ]
                d_table = [
                    [
                        inst["address"],
                        inst["byte_code"],
                        inst["asm"].replace("\t", "   "),
                        ( set_vul[str(inst["address"])] if str(inst["address"]) in set_vul.keys() else "0"),
                        ( reset_vul[str(inst["address"])] if str(inst["address"]) in reset_vul.keys() else "0"),
                        ( flip_vul[str(inst["address"])] if str(inst["address"]) in flip_vul.keys() else "0")
                    ] for inst in block_json["instructions"]
                ]
                to_write = createTables(s_table, d_table)
                f.write(to_write)
                pbar.update(1)
        pbar.close()
        f.write(html_end)
        f.close()

    HTML(out_file_path).write_pdf(out_file_pdf)
        
if __name__ == "__main__":
    main()

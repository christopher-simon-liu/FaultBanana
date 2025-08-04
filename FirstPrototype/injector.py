# Required imports
import mmap
import sys, getopt
import os
import argparse
from argparse import RawTextHelpFormatter,SUPPRESS

"""
Function ByteResetFM(infile,outfile,position)
	* Geneate the mutant of the input object file by setting one byte to zeros
	* Zero the "position" Byte
	* Create the Mutant as outfile
"""
def ByteResetFM(values,outfile,position):
  values[int(position)] = 0x00
  store = open(outfile, 'wb')
  store.write(values)
  store.close()

"""
Function ByteSetFM(infile,outfile,position)
	* Geneate the mutant of the input object file by setting one byte to ones
	* Zero the "position" Byte
	* Create the Mutant as outfile
"""
def ByteSetFM(values,outfile,position):
  values[int(position)] = 0xFF
  store = open(outfile, 'wb')
  store.write(values)
  store.close()

"""
Function ByteFlipFM(infile,outfile,position,subposition)
	* Geneate the mutant of the input object file by flipping bits 
	* Create the Mutant as outfile
"""
def FlipBitsFM(values,outfile,position):
  # Flip all bits of the byte at the specified index
  # XORing with 0xFF (255) flips all bits of an 8-bit byte
  values[int(position)] ^= 0xFF
  store = open(outfile, 'wb')
  store.write(values)
  store.close()

def main():  
    ## entry point of this program
    ## Parsing the arguments
    parser = argparse.ArgumentParser(description="Tool Options")
    parser.add_argument("binary", default="./motivating.o", type=str, help="Path to binary.o")
    parser.add_argument("offset", default=40, type=int, help="Starting binary byte index")
    parser.add_argument("size", default=124, type=int, help="Size of .text section")
    parser.add_argument("out", default="./mutants", type=str, help="Path to output folder")
    parser.add_argument("--fm", default="reset", type=str, help="Fault Model (set, reset, flip)")

    args = parser.parse_args()
    binary_path = args.binary
    offset = args.offset
    textsize = args.size
    out_path = args.out
    fault_model = args.fm

    file_name = os.path.basename(binary_path)
    name = os.path.splitext(file_name)[0]

    byte_array=[]
    
    with open(binary_path, "r+b") as f:
      mm = mmap.mmap(f.fileno(), 0)
      byte_array = bytearray(mm)
      sizefile=len(byte_array)
      print(f"{sizefile} bytes")
      f.close()

    i = 0
    while (i < textsize):
      mutant_file = os.path.join(out_path, f"{name}-{i}.o")
      binary_to_mutate = byte_array.copy()
      if fault_model == "flip":
        FlipBitsFM(binary_to_mutate, mutant_file, offset + i)
      elif fault_model == "set":
        ByteSetFM(binary_to_mutate, mutant_file, offset + i)
      else: # reset zero byte fault model
        ByteResetFM(binary_to_mutate, mutant_file, offset + i)
      print(f"{mutant_file} created")
      i = i + 1

if __name__ == "__main__":
    main()
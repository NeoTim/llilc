#!/usr/bin/env python
#
#title           :applyfilter.py
#description     :
# This script performs normalization of verbose LLVM IR dump generated by LLILC JIT. 
# Normalized cases include:
# 
# Suppress address difference from run to run
# Assume the address is at least 10-digit number
# Example 1:
# 
# Normalize
# %2 = call i64 inttoptr (i64 140704958972024 to i64 (i64)*)(i64 140704956891884)
# to
# %2 = call i64 inttoptr (i64 NORMALIZED_ADDRESS to i64 (i64)*)(i64 NORMALIZED_ADDRESS)
#
# Example 2:
#
# Normalize
# %3 = icmp eq i64 140704956891886, %2
# to
# %3 = icmp eq i64 NORMALIZED_ADDRESS, %2
#
# Example 3:
#
# Normalize
# %12 = phi i64 [ 709816494128, %3 ], [ 709816494128, %7 ]
# to
# %12 = phi i64 [ NORMALIZED_ADDRESS, %3 ], [ NORMALIZED_ADDRESS, %7 ]
#
# Suppress type id difference from run to run
#
# Example 1:
# 
# Normalize
# %3 = load %System.AppDomainSetup.239 addrspace(1)** %1
# to
# %3 = load %System.AppDomainSetup.NORMALIZED_TYPEID addrspace(1)** %1
#
# Example 2:
#
# Normalize
# %0 = alloca %AppDomain.24 addrspace(1)*
# to
# %0 = alloca %AppDomain.NORMALIZED_TYPEID addrspace(1)*
#
# Suppress type id difference from run to run, string name with double quotes
#==========================================================================================

import os
import sys
import re
import argparse

# Apply filter on src and create a normalized file dest
def ApplyOne(src, dest):
    re_addr = re.compile(r'i64 \d{10}\d*')
    re_type = re.compile(r'%("?)(.*?)\.\d+\1 addrspace')
    re_phi = re.compile(r'\[ \d{10}\d*, %')
    with open(src, 'r') as ins, open(dest, 'w') as outs:
        for line in ins:
            line = re_addr.sub(r'i64 NORMALIZED_ADDRESS', line)
            line = re_type.sub(r'%\1\2.NORMALIZED_TYPEID\1 addrspace', line)
            line = re_phi.sub(r'[ NORMALIZED_ADDRESS, %', line)
            outs.write(line)

# Apply filter recursively on directory walk_dir
def ApplyAll(walk_dir):
    for root, subdirs, files in os.walk(walk_dir):
        for filename in files:
            if filename.endswith("error.txt"):
                tmp_filename = filename + ".tmp"
                file_path = os.path.join(root, filename)
                tmp_file_path = os.path.join(root, tmp_filename)
                ApplyOne(file_path, tmp_file_path)
                os.remove(file_path)
                os.rename(tmp_file_path, file_path)

# The script itself applies the filter on one file
if __name__=='__main__':
    # Parse the command line
    parser = argparse.ArgumentParser()
    parser.add_argument("src", type=str, help="source result to apply filter on")
    parser.add_argument("dest", type=str, help="destination result after applying filter")
    args = parser.parse_args()

    # Apply the filter on one file
    ApplyOne(args.src, args.dest)
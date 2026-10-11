#!/usr/bin/env python

import argparse

def append_static(input_path, static_path, output_path, bytes_per_word=1):
    with open(input_path, 'r') as file_in, open(static_path, 'rb') as static_in, open(output_path, 'w') as file_out:
        data = bytes.fromhex(file_in.read())
        data_static = static_in.read()
        result = data + data_static[len(data):]

        for i in range(0, len(result), bytes_per_word):
            file_out.write(f"{int.from_bytes(result[i:i+bytes_per_word], "big"):0{bytes_per_word*2}x}\n")

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="ikjMatrix multiplication")
    parser.add_argument("input", help="bitstream ascii input file")
    parser.add_argument("static_bitstream", help="static bitstream input file")
    parser.add_argument("output", help="ascii output file")
    parser.add_argument("--bytes-per-word", type=int, default=1, help="number of bytes for one word")
    args = parser.parse_args()

    append_static(args.input, args.static_bitstream, args.output, args.bytes_per_word)

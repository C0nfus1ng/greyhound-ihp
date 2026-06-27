#!/usr/bin/env python
import argparse
from pathlib import Path

def load_bitstream(file:Path, tile_x_offset:int=0):
    with file.open("rb") as bitstream:
        # Find bitstream start
        loaded_bitstream = {"tiles":[], "usercode":1, "data":{"pre_frame":bytes(), "frame":{}, "post_frame":bytes()}}

        seek_word_raw = bitstream.read(4)
        loaded_bitstream["data"]["pre_frame"] += seek_word_raw
        seek_word = int.from_bytes(seek_word_raw, "big")
        seek_stream_start = -1
        seek_byte_counter = 4
        while 0xFAB0FAB1 != seek_word:
            if seek_word & 0xFFF00000 == 0x5E7<<20:
                loaded_bitstream["tiles"].append(seek_word)

            if seek_word == 0x00AAFF01:
                seek_stream_start = seek_byte_counter + 4

            if seek_stream_start == seek_byte_counter:
                loaded_bitstream["usercode"] = seek_word

            seek_byte_counter += 1
            seek_word_raw = bitstream.read(1)
            loaded_bitstream["data"]["pre_frame"] += seek_word_raw
            seek_word = ((seek_word & 0xFFFFFF) << 8) | int.from_bytes(seek_word_raw, "big")

        loaded_bitstream["tiles"].reverse()

        # Load frame data
        bytes_per_frame = 68
        data = bitstream.read(bytes_per_frame)
        while data:
            if len(data) != bytes_per_frame:
                break
            
            col = (int.from_bytes(data[:1], "big")>>3) + tile_x_offset
            strobe = int.from_bytes(data[1:4], "big") & 0xFFFFF
            frame_header = (col<<27) | strobe
            loaded_bitstream["data"]["frame"][frame_header] = frame_header.to_bytes(4)+data[4:]
            data = bitstream.read(bytes_per_frame)

        # Load bitstream end
        loaded_bitstream["data"]["post_frame"] += data
        
        post_data = bitstream.read(1)
        while post_data:
            loaded_bitstream["data"]["post_frame"] += post_data
            post_data = bitstream.read(1)

        return loaded_bitstream

def gen_bitstream_file(file:Path, static_file:Path=None, tile_x_offset:int=0) -> [int]:
    # Load static bitstream

    loaded_static_bitstream = None
    if static_file:
        loaded_static_bitstream = load_bitstream(static_file)

    # Load bitstream
    loaded_bitstream = load_bitstream(file, tile_x_offset)
    output_bitstream = []

    # Write bitstream to list
    len_pre_bitstream = int(len(loaded_bitstream["data"]["pre_frame"])/4)
    for i_word in range(len_pre_bitstream):
        bitstream_word = int.from_bytes(loaded_bitstream["data"]["pre_frame"][i_word*4:(i_word+1)*4], "big")
        output_bitstream.append(bitstream_word)

    len_bitstream = len(loaded_bitstream["data"]["frame"])*19
    for i_frame, (frame_header, frame_data) in enumerate(loaded_bitstream["data"]["frame"].items()):
        col = frame_header>>27
        use_frame_tile = loaded_bitstream["tiles"][i_frame] if (i_frame < len(loaded_bitstream["tiles"])) else 0x3ffff

        len_frame_data = int(len(frame_data)/4)
        for i_frame_word in range(len_frame_data):
            use_bitstream_tile = 1 if (i_frame_word == 0) else ((use_frame_tile >> (len_frame_data-i_frame_word-1)) & 0x1)

            if use_bitstream_tile:
                bitstream_word = int.from_bytes(frame_data[i_frame_word*4:(i_frame_word+1)*4], "big")
            elif loaded_static_bitstream:
                static_frame_header = (col<<27)
                for frame_bit in range(20):
                    if (frame_header >> frame_bit) & 0x1:
                        static_frame_header |= (1 << frame_bit)
                        break

                bitstream_word = int.from_bytes(loaded_static_bitstream["data"]["frame"][static_frame_header][i_frame_word*4:(i_frame_word+1)*4], "big")
            else:
                Exception("Couldn't find bitstream word, no static bitstream loaded")

            output_bitstream.append(bitstream_word)

    len_post_bitstream = int(len(loaded_bitstream["data"]["post_frame"])/4)
    for i_word in range(len_post_bitstream):
        bitstream_word = int.from_bytes(loaded_bitstream["data"]["post_frame"][i_word*4:(i_word+1)*4], "big")
        output_bitstream.append(bitstream_word)

    return output_bitstream

def build_lookup(input_file:Path, static_input_file:Path, output_file:Path, tile_x_offset:int=0):
    bitstream_words = gen_bitstream_file(input_file, static_input_file, tile_x_offset)

    with output_file.open("w") as c_file:
        c_file.write(f"static const uint32_t {output_file.stem}_bitstream[] = "+r"{"+f"\n0x")
        c_file.write(f"{",\n0x".join([f"{word:08x}" for word in bitstream_words])}")
        c_file.write(f"\n"+r"}"+f";\n")

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description="Build lookup table to speed up partial program")
    arg_parser.add_argument("i_bitstream", help="Path to input bitstream")
    arg_parser.add_argument("static_i_bitstream", help="Path to static input bitstream")
    arg_parser.add_argument("o_c_file", help="Path to output c file")
    arg_parser.add_argument("--tile_x_offset", type=int, default=0, help="Offset for the slot to generate")
    args = arg_parser.parse_args()
    
    build_lookup(Path(args.i_bitstream), Path(args.static_i_bitstream), Path(args.o_c_file), args.tile_x_offset)

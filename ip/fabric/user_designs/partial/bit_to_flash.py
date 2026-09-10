import argparse
import re
from math import ceil

def gen_flash_image(image_args:{(int, str):[str]}, output_file:str, warmboot_slots:int, flash_size:int, chunk_size:int) -> None:
    with open(output_file, "wb") as flash_image_file:
        flash_image = bytearray(b'\xff'*flash_size)
        warmboot_slot_offset = int(flash_size/warmboot_slots)

        for (warmboot_slot, bitstream_folder_path), bitstream_file_names in image_args.items():
            warmboot_slot_addr = warmboot_slot * warmboot_slot_offset
        
            for bitstream_file_name in bitstream_file_names:
                with open(f"{bitstream_folder_path}/{bitstream_file_name}.bit", "rb+") as bitstream_file:
                    bitstream = bytearray(bitstream_file.read())
                    stream_start_index = bitstream.find(0x00AAFF01.to_bytes(4))

                    if stream_start_index == -1:
                        raise RuntimeError("Stream start not found in bitstream. Is the file a bitstream in the correct format?")

                    stream_start_index += 4
                    bitstream[stream_start_index:stream_start_index+4] = ((int.from_bytes(bitstream[stream_start_index:stream_start_index+4], "big")&0xFFFF_E000) | ((warmboot_slot_addr>>11)&0x1FFF)).to_bytes(4)
                    print(f"USERCODE for {bitstream_folder_path}/{bitstream_file_name}.bit changed to 0x{int.from_bytes(bitstream[stream_start_index:stream_start_index+4], "big"):08x}")

                    if warmboot_slot_addr+len(bitstream) > (warmboot_slot+1) * warmboot_slot_offset:
                        raise RuntimeError(f"Cannot fit bitstream {bitstream_folder_path}/{bitstream_file_name}.bit into warmboot slot {warmboot_slot}, the warmboot slot is to small.")

                    flash_image[warmboot_slot_addr:warmboot_slot_addr+len(bitstream)] = bitstream
                    warmboot_slot_addr += ceil(len(bitstream)/chunk_size)*chunk_size

        flash_image_file.write(flash_image)

def parse_arg_line(arg_lines:str) -> {(int, str):[str]}:
    if not arg_lines:
        return None

    if not re.match(r"^([^=,\s]+:[^=,\s]+=[^=,\s]+(,[^=,\s]+)*)(\s+[^=,\s]+=[^=,\s]+(,[^=,\s]+)*)*$", arg_lines):
        raise RuntimeError(f"Invalid format --image \"{arg_lines}\"")
        return None

    arg_line = arg_lines.split(" ")
    args_dict = dict([arg.split("=") for arg in arg_line])
    args_dict_out = {}

    for trunk, args in args_dict.items():
        split_trunk = trunk.split(":", 1)
        dict_trunk = (int(split_trunk[0]), split_trunk[1])
        args_dict_out[dict_trunk] = args.split(",")

    return args_dict_out

if __name__ == "__main__":
    usage = "Generate flash image for the spi controller\n"\
            "Use -h, --help to get the help text for all flags\n"\
            "Run -d \"<Warmboot Slot nbr>:<base_dir>=Prog1,Prog2,... <Warmboot Slot nbr>:<base_dir2>=...\" to generate the flash image for the spi controller"

    arg_parser = argparse.ArgumentParser(description=usage)
    arg_parser.add_argument("-i", "--image", help="Pack bitstreams into a single flash image for the spi controller to load, like -d \"<Warmboot Slot nbr>:<base_dir>=Prog1,Prog2,... <Warmboot Slot nbr>:<base_dir2>=...\"")
    arg_parser.add_argument("-f", "--file", default="flash_image.bit", help="Output file to use")
    arg_parser.add_argument("--warmboot_slots", default=16, type=int, help="Number of warmboot slots")
    arg_parser.add_argument("--flash_size", default=16*1024*1024, type=int, help="Size of the connected flash")
    arg_parser.add_argument("--chunk_size", default=1<<11, type=int, help="Size of the connected flash")

    args = arg_parser.parse_args()
    
    if not any(vars(args).values()):
        print(usage)
        exit

    image_args = parse_arg_line(args.image)

    if args.image:
        gen_flash_image(image_args, args.file, args.warmboot_slots, args.flash_size, args.chunk_size)

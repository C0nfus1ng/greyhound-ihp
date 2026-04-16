#!/usr/bin/env python

from os import environ
from os import makedirs
import argparse
import csv
import re
import yaml
from loguru import logger
from FABulous.fabric_generator.parser import parse_csv
from FABulous.fabric_definition.Bel import Bel
from FABulous.fabric_definition.Fabric import Fabric
from FABulous.fabric_definition.Tile import Tile
from FABulous.fabric_definition.define import IO, Direction
from pathlib import Path
import FABulous.fabric_cad.gen_npnr_model as gen_npnr_model
import FABulous.fabric_cad.gen_bitstream_spec as gen_bitstream_spec
import copy
import pickle

# Workaround to import existing modules
import sys
bit_tool_dir = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(bit_tool_dir))
#import module_in_parent_dir
from bit_gen import genBitstream
from bit_to_hex import bit_to_hex
sys.path.remove(str(bit_tool_dir))

from fasm import (
    parse_fasm_filename,
    fasm_tuple_to_string,
    parse_fasm_string,
    set_feature_to_str,
)

class Format:
    format_string = ""

    def __init__(self):
        self.format_string = get_default()

    def __init__(self, formatting):
        self.format_string = formatting

    @classmethod
    def get_bold(cls):
        return "\033[1m"
    
    @classmethod
    def get_italic(cls):
        return "\033[3m"
    
    @classmethod
    def get_default(cls):
        return "\033[0m"
    
    @classmethod
    def to_yaml(cls, dumper, data):
        return dumper.represent_mapping("tag:yaml.org,2002:map",
                {"Specifier": data.format_string})

class Slot:
    start = 0
    end = 0
    name = ""
    formatting = None

    def __init__(self, start, end, name, formatting):
        self.start      = start
        self.end        = end
        self.name       = name
        self.formatting = formatting

    @classmethod
    def to_yaml(cls, dumper, data):
        return dumper.represent_mapping("tag:yaml.org,2002:map",
                {"Start": data.start, "End": data.end, "Name": data.name, "Format": data.formatting})

class Point:
    x = 0
    y = 0
    formatting = None

    def __init__(self, x, y, formatting): 
        self.x = x
        self.y = y
        self.formatting = formatting
    
    @classmethod
    def to_yaml(cls, dumper, data):
        return dumper.represent_mapping("tag:yaml.org,2002:map",
                {"x": data.x, "y": data.y, "Format": data.formatting})

class FabricLayout:
    fabric = None
    length = 0
    height = 0
    tile_name_max_length = 6
    last_color = 0
    slots = list()
    points = list()
    bridges = list()

    def get_color(self): # Cycle colors 
        color = self.last_color+1
        self.last_color = color%6
        return f"\033[3{color}m"

    def create_slot(self, start, end, name, color=None):
        if color:
            tmp_color = color
        else:
            tmp_color = self.get_color()
        
        slot = Slot(start, end, name, Format(tmp_color))
        self.slots.append(slot)

    @classmethod
    def to_yaml(cls, dumper, data):
        return dumper.represent_mapping("tag:yaml.org,2002:map",
                {"Length": data.length, "Height": data.height, "Column Length": data.tile_name_max_length, 
                 "Last Color": data.last_color, "Slots": data.slots, "Points": data.points, "Bridges": data.bridges})

def create_slot(layout: FabricLayout):
    print("Slots can only be vertical")
    print("There can only be 1 static slot")
    while True:
        slot_type = input("Slot type (static/dynamic): ")
        if slot_type == "dynamic":
            name = f"Slot{len(layout.slots)}"
            break
        elif slot_type == "static":
            name = f"Static"
            break

    for slot in layout.slots:
        if name == slot.name:
            print("This slot already exists, modify it with the e command")
            print()
            return

    first_column = int(input("First column: "))
    last_column = int(input("Last column: "))
    layout.create_slot(first_column, last_column, name)
    print()

def edit_slot(layout: FabricLayout, delete):
    while True:
        edit_slot = None
        user_input = input(f"Enter slot name to {"delete" if delete else "edit"}/Use x to leave: ")

        if user_input == "x":
            return

        for slot in layout.slots:
            if user_input == slot.name:
                edit_slot = slot
                break

        if edit_slot:
            break

    print(f"{"Deleting" if delete else "Editing"} slot {edit_slot.name}")

    # Remove slot
    layout.slots.remove(edit_slot)

    if delete:
        return

    print("Slots can only be vertical")
    first_column = int(input("First column: "))
    last_column = int(input("Last column: "))
    layout.create_slot(first_column, last_column, edit_slot.name, edit_slot.formatting.format_string)
    print()

def create_connection(layout: FabricLayout, bridge=False):
    if bridge:
        cell = input("Specify the bridge point as X<x>Y<y> (Should be placed between slots for connectivity): ")
    else:
        cell = input("Specify the slot connection point as X<x>Y<y> (Should be placed in a dynamic slot): ")

    slot_connection = [int(re.findall('[0-9]', x)[0]) for x in re.findall('X[0-9]+|Y[0-9]+', cell)]
    try:
        print(f"Added connection point at X{slot_connection[0]}Y{slot_connection[1]}")
    except:
        print("Wrong Point format")
        return

    if (slot_connection[0] >= layout.length or slot_connection[1] >= layout.height):
        print(f"{"Bridge" if bridge else "Connection"} point has to be in the fabric coordinates")
        return

    if bridge:
        layout.bridges.append(Point(slot_connection[0], slot_connection[1], Format(Format.get_italic())))
    else:
        layout.points.append(Point(slot_connection[0], slot_connection[1], Format(Format.get_bold())))
    print()
   
def edit_connection(layout: FabricLayout, delete, bridge=False):
    while True:
        edit_point = None
        user_input = input(f"Enter {"bridge" if bridge else "connection"} point to {"delete" if delete else "edit"} as XxYy/Use x to leave: ")

        if user_input == "x":
            return

        for point in layout.bridges if bridge else layout.points:
            if user_input == f"X{point.x}Y{point.y}":
                edit_point = point
                break

        if edit_point:
            break

        print(f"{"Bridge" if bridge else "Connection"} point not found")

    print(f"{"Deleting" if delete else "Editing"} {"bridge" if bridge else "connection"} point X{edit_point.x}Y{edit_point.y}")
    if bridge:
        layout.bridges.remove(edit_point)
    else:
        layout.points.remove(edit_point)

    if delete:
        return

    create_connection(layout, bridge=bridge)

def write_config(layout: FabricLayout, file_path = None):
    yaml.add_representer(FabricLayout, FabricLayout.to_yaml)
    yaml.add_representer(Slot, Slot.to_yaml)
    yaml.add_representer(Point, Point.to_yaml)
    yaml.add_representer(Format, Format.to_yaml)

    if file_path == None:
        file_path = input("Enter config file to write to: ")

        print()
        print(f"{file_path} will be created/overwritten")

        while True:
            user_input = input("Write file y/n: ")

            if user_input == "y":
                break
            elif user_input == "n":
                return

    with open(file_path, "w") as file:
        yaml.dump(layout, file, sort_keys=False)

    print("Wrote config successfully")

def load_config(layout: FabricLayout, file_path = None):
    if file_path == None:
        file_path = input("Enter config file to load: ")

        print()
        print(f"{file_path} will be loaded")

        while True:
            user_input = input("Load file y/n: ")

            if user_input == "y":
                break
            elif user_input == "n":
                return

    try:
        with open(file_path, 'r') as file:
            layout_config = yaml.safe_load(file)
    except FileNotFoundError:
        print("File to load not found")
        return
    except yaml.parser.ParserError:
        print("File cannot be parsed")
        return

    if layout_config == None:
        print("File to load is empty")
        return

    if not isinstance(layout_config, dict):
        print("File format is not supported")
        return

    try:
        if layout.height != layout_config["Height"] or layout.length != layout_config["Length"] or layout.tile_name_max_length != layout_config["Column Length"]:
            print("Loading file failed. Fabric size Mismatch")
            return

        # Load color
        layout.last_color = layout_config["Last Color"]

        # Load slots
        layout.slots.clear()
        for slot in layout_config["Slots"]:
            layout.slots.append(Slot(slot["Start"], slot["End"], slot["Name"], Format(slot["Format"]["Specifier"])))
        
        # Load Points
        layout.points.clear()
        for point in layout_config["Points"]:
            layout.points.append(Point(point["x"], point["y"], Format(point["Format"]["Specifier"])))

        # Load Bridges
        layout.bridges.clear()
        for bridge in layout_config["Bridges"]:
            layout.bridges.append(Point(bridge["x"], bridge["y"], Format(bridge["Format"]["Specifier"])))

    except KeyError:
        print("File has missing keys")
        return

def print_layout(layout: FabricLayout):
    # Point
    print(f"{Format.get_italic()}Italic{Format.get_default()} for non static bridging tiles")    
    print(f"{Format.get_bold()}Bold{Format.get_default()} for connection tiles between static and dynamic slots")    
    
    # Slot overview
    for slot in layout.slots:
        first = 10 + slot.start*layout.tile_name_max_length
        last = first - 2 + (slot.end-slot.start+1)*layout.tile_name_max_length
        mid = first + int((last-first)/2)-4
        print(f"{slot.formatting.format_string}{" "*(first)}|<{" "*(mid-first)}{slot.name}{" "*(last-mid-len(slot.name)-2)}>|{Format.get_default()}")

    # Table
    print("Row/Col | ", end='')
    for col in range(layout.length):
        print("%*.*s" % (-layout.tile_name_max_length, layout.tile_name_max_length, f"X{col:02}"), end='')

    print() # Newline
    print("-"*(10+layout.length*layout.tile_name_max_length))
    for row in range(layout.height):
        print("%-7.7s | " % (f"Y{row:02}"), end='')
        for col in range(layout.length):
            # Coloring
            for slot in layout.slots:
                if slot.start <= col and col <= slot.end:
                    print(slot.formatting.format_string, end='')
                    break
            
            # Connection
            for connection_point in layout.points:
                if col == connection_point.x and row == connection_point.y:
                    print(connection_point.formatting.format_string, end='')
                    break

            # Bridge
            for bridge_point in layout.bridges:
                if col == bridge_point.x and row == bridge_point.y:
                    print(bridge_point.formatting.format_string, end='')
                    break

            print("%*.*s" % (-layout.tile_name_max_length, layout.tile_name_max_length, layout.fabric.tile[row][col].name if layout.fabric.tile[row][col] else "NULL"), end='')
            print(Format.get_default(), end='')
        print()

def verilog_gen(tile:Tile, slot:Slot, base_dir:str, con_point:tuple[int, int], static_slot:bool):
    # Add special bels from connections
    io_ports = [p for p in tile.portsInfo if p.sourceName != "NULL" and p.wireDirection != Direction.JUMP]
    filename = Path(f"{base_dir}/{slot.name}/{slot.name}_slot_con_X{con_point.x}Y{con_point.y}.v")

    # Write verilog conn file
    slot_module_str = []
    slot_module_str.append(f"// Auto generated file, all changes to this file will be lost\n")

    slot_module_str.append(f"// Instantiate with (* keep, BEL=\"X{con_point.x}Y{con_point.y}.A\" *) {slot.name}_slot_con_X{con_point.x}Y{con_point.y} ...")
    slot_module_str.append("(* blackbox, keep*)")
    slot_module_str.append(f"module {slot.name}_slot_con_X{con_point.x}Y{con_point.y} (")

    for port in io_ports:
        if (static_slot and port.inOut == IO.INPUT) or (not static_slot and port.inOut == IO.OUTPUT):
            inout = "input"
        elif (static_slot and port.inOut == IO.OUTPUT) or (not static_slot and port.inOut == IO.INPUT):
            inout = "output"
        else:
            inout = "// unknown IO"

        for wire_nbr in range(port.wireCount):
            slot_module_str.append(f"  {inout} {port.name}{wire_nbr},")

    slot_module_str.append(");\nendmodule")

    verilog_module = "\n".join(slot_module_str)
    with open(filename, "w") as f:
        f.write(verilog_module)

def strip_bel_pips(bels:list[Bel]):
    remove_pips = []
    for bel in bels:
        remove_pips += bel.inputs
        remove_pips += bel.outputs

    return remove_pips

def bel_gen_from_slot(tile:Tile, slot:Slot, base_dir:str, con_point:tuple[int, int], static_slot:bool, filename:Path = None, module_name:str = None):
    filename = Path(f"{base_dir}/{slot.name}/{slot.name}_slot_con_X{con_point.x}Y{con_point.y}.v")
    module_name = f"{slot.name}_slot_con_X{con_point.x}Y{con_point.y}"
    return bel_gen(tile, filename, module_name, static_slot)

def bel_gen(tile:Tile, filename:Path, module_name:str, static_slot:bool):
    bel_prefix = ""
    internal: list[tuple[str, IO]] = []
    external: list[tuple[str, IO]] = []
    config: list[tuple[str, IO]] = []
    shared: list[tuple[str, IO]] = []
    bel_map_dic = {}
    user_clk = False
    ports_vectors: dict[str, dict[str, tuple[IO, int]]] = {}
    # define port types
    ports_vectors["internal"] = {}
    ports_vectors["external"] = {}
    ports_vectors["config"] = {}
    ports_vectors["shared"] = {}
    carry: dict[str, dict[IO, str]] = {}
    local_shared_ports: dict[str, tuple[str, IO]] = {}

    io_ports = [p for p in tile.portsInfo if p.sourceName != "NULL" and p.wireDirection != Direction.JUMP]

    for port in io_ports:
        if (static_slot and port.inOut == IO.INPUT) or (not static_slot and port.inOut == IO.OUTPUT):
            slot_port_inout = IO.INPUT
        elif (static_slot and port.inOut == IO.OUTPUT) or (not static_slot and port.inOut == IO.INPUT):
            slot_port_inout = IO.OUTPUT
        else:
            slot_port_inout = IO.INOUT

        for wire_nbr in range(port.wireCount):
            internal.append((f"{port.name}{wire_nbr}", slot_port_inout))
            ports_vectors["internal"][f"{port.name}{wire_nbr}"] = (slot_port_inout, 1)

    return Bel(filename, bel_prefix, module_name, internal, external, config, shared, 0, bel_map_dic, user_clk, ports_vectors, carry, local_shared_ports)

def npnr_file_gen(layout: FabricLayout, option_static, base_dir):
    if not option_static:
        fasm_parsed = parse_fasm_filename(f"{base_dir}/Static/Static.fasm")
        fasm_canon_str = fasm_tuple_to_string(fasm_parsed, True)
        fasm_canon_list = list(parse_fasm_string(fasm_canon_str))

        fasm_wires = {}
        for fasm_line in fasm_canon_list:
            fasm_tile_vals = set_feature_to_str(fasm_line.set_feature).split(".")
            fasm_tile_loc = fasm_tile_vals[0]

            if fasm_tile_loc not in fasm_wires.keys():
                fasm_wires[fasm_tile_loc] = []

            # tile:{(src_wire, dst_wire)}
            fasm_wires[fasm_tile_loc].append((fasm_tile_vals[1], fasm_tile_vals[2]))

    # Build fabric per slot
    for slot in layout.slots:
        static_slot = False
        makedirs(f"{base_dir}/{slot.name}/.FABulous", exist_ok=True)

        if slot.name == "Static" and option_static:
            static_slot = True
            print("Static Slot")
        elif slot.name != "Static" and not option_static:
            print(f"Dynamic Slot: {slot.name}")
        else:
            print(f"Skip Slot: {slot.name}")
            continue

        tmp_fabric = copy.deepcopy(layout.fabric)
        tmp_fabric.tile = [[None for x in range(layout.length)] for x in range(layout.height)]

        # Only use tiles and pips from slot
        for row in range(layout.height):
            for col in range(slot.start, slot.end+1):
                tmp_fabric.tile[row][col] = layout.fabric.tile[row][col]

        # Static slot gen
        if static_slot:
            remove_pips = {}

            # Add pips from bridges
            for bridge in layout.bridges:
                tile = layout.fabric.tile[bridge.y][bridge.x]
                if tile == None:
                    continue

                tmp_fabric.tile[bridge.y][bridge.x] = copy.deepcopy(tile)
                remove_pips[bridge] = strip_bel_pips(tmp_fabric.tile[bridge.y][bridge.x].bels) # Remove bel specific connections

            # Add pips from connections
            for con_point in layout.points:
                tile = layout.fabric.tile[con_point.y][con_point.x]
                if tile == None:
                    continue

                tmp_fabric.tile[con_point.y][con_point.x] = copy.deepcopy(tile)
                remove_pips[con_point] = strip_bel_pips(tmp_fabric.tile[con_point.y][con_point.x].bels)
                bel = bel_gen_from_slot(tile, slot, base_dir, con_point, static_slot)
                tmp_fabric.tile[con_point.y][con_point.x].bels.insert(0, bel) # Insert in front of all other bels, fixes some kind of npnr assert
                verilog_gen(tile, slot, base_dir, con_point, static_slot)

            tmp_npnr_model = gen_npnr_model.genNextpnrModel(tmp_fabric)

            # Remove pips of the undesired bels
            tmp_pips = tmp_npnr_model[0].split("\n")
            removed_pips = []

            for pos, tile_list in remove_pips.items():
                # Search and remove wires
                for wire in tile_list:
                    search_pip = f"X{pos.x}Y{pos.y},[^,]+,[^,]+,[^,]+,[^,]+,"+r"([^\.]+\."+f"{wire}$)|({wire}"+r"\..+$)"
                    for pip in tmp_pips:
                        if re.match(search_pip, pip):
                            removed_pips.append(pip)
                            tmp_pips.remove(pip)
        # Dynamic slot gen
        else:
            # Check overlap of static with this slot
            overlapping_bridge_tiles = {}
            overlapping_point_tiles = {}

            for bridge in layout.bridges:
                if slot.start <= bridge.x and bridge.x <= slot.end:
                    overlapping_bridge_tiles[bridge] = layout.fabric.tile[bridge.y][bridge.x]
            
            for point in layout.points:
                if slot.start <= point.x and point.x <= slot.end:
                    overlapping_point_tiles[point] = layout.fabric.tile[point.y][point.x]

            # Add custom bel
            for pos, tile in overlapping_point_tiles.items():
                if tile == None:
                    continue

                tmp_fabric.tile[pos.y][pos.x] = copy.deepcopy(tile)
                bel = bel_gen_from_slot(tile, slot, base_dir, pos, static_slot)
                tmp_fabric.tile[pos.y][pos.x].bels.insert(0, bel)
                verilog_gen(tile, slot, base_dir, pos, static_slot)

            tmp_npnr_model = gen_npnr_model.genNextpnrModel(tmp_fabric)            

            # Remove pips of the overlapping tiles
            tmp_pips = tmp_npnr_model[0].split("\n")
            removed_pips = []

            for pos, tile in overlapping_bridge_tiles.items():
                if tile == None:
                    continue

                # Search and remove wires
                for fasm_wire in fasm_wires[f"X{pos.x}Y{pos.y}"]:
                    search_pip = f"X{pos.x}Y{pos.y},[^,]+,[^,]+,[^,]+,[^,]+,{fasm_wire[0]}"+r"\."+f"{fasm_wire[1]}$"
                    for pip in tmp_pips:
                        if re.match(search_pip, pip):
                            removed_pips.append(pip)
                            tmp_pips.remove(pip)

            for pos, tile in overlapping_point_tiles.items():
                if tile == None:
                    continue
                                
                for fasm_wire in fasm_wires[f"X{pos.x}Y{pos.y}"]:
                    search_pip = f"X{pos.x}Y{pos.y},[^,]+,[^,]+,[^,]+,[^,]+,{fasm_wire[0]}"+r"\."+f"{fasm_wire[1]}$"
                    for pip in tmp_pips:
                        if re.match(search_pip, pip):
                            removed_pips.append(pip)
                            tmp_pips.remove(pip)

        npnr_model = ("\n".join(tmp_pips), tmp_npnr_model[1], tmp_npnr_model[2], tmp_npnr_model[3])
        print("Removed pips:")
        print("\n".join(removed_pips))

        # Generate files for NextPNR
        with open(f"{base_dir}/{slot.name}/.FABulous/pips.txt", "w") as f:
            f.write(npnr_model[0])

        with open(f"{base_dir}/{slot.name}/.FABulous/bel.v2.txt", "w") as f:
            f.write(npnr_model[2])

        spec_object = gen_bitstream_spec.generateBitstreamSpec(tmp_fabric)
        with open(f"{base_dir}/{slot.name}/bitStreamSpec.bin", "wb") as f:
            pickle.dump(spec_object, f)

def combine_fasm(layout: FabricLayout, base_dir):
    # Parse fasm file
    fasm_static_parsed = parse_fasm_filename(f"{base_dir}/Static/Static.fasm")
    fasm_static_str = fasm_tuple_to_string(fasm_static_parsed, True)
    fasm_static_list = list(parse_fasm_string(fasm_static_str))
    fasm_static_list_str = [set_feature_to_str(fasm_line.set_feature) for fasm_line in fasm_static_list]

    for slot in layout.slots:
        if slot.name == "Static":
            print("Skipped Static slot")
            continue

        fasm_dynamic_parsed = parse_fasm_filename(f"{base_dir}/{slot.name}/{slot.name}.fasm")
        fasm_dynamic_str = fasm_tuple_to_string(fasm_dynamic_parsed, True)
        fasm_dynamic_list = list(parse_fasm_string(fasm_dynamic_str))
        fasm_dynamic_list_str = [set_feature_to_str(fasm_line.set_feature) for fasm_line in fasm_dynamic_list]

        # Get slot intersection
        fasm_overlap_str = []
        fasm_overlap_str.append("# Lines from Static slot")
        for col in range(slot.start, slot.end+1):
            search_line = f"X{col}.*"

            for fasm_static_line_str in fasm_static_list_str:
                if re.match(search_line, fasm_static_line_str):
                    if fasm_static_line_str in fasm_dynamic_list_str:
                        raise RuntimeError("Dynamic slot uses same route as Static slot.")
                    
                    fasm_overlap_str.append(fasm_static_line_str)

        fasm_overlap_str.append("\n")
        print(f"Appending to {slot.name}")
        print("\n".join(fasm_overlap_str))

        makedirs(f"{base_dir}/{slot.name}", exist_ok=True)
        with open(f"{base_dir}/{slot.name}/{slot.name}-slot.fasm", "w") as fasm_file:
            fasm_file.write("\n".join(fasm_overlap_str))
            fasm_file.write(fasm_dynamic_str)

def gen_bitstream(layout: FabricLayout, base_dir):
    for slot in layout.slots:    
        if slot.name == "Static":
            # Create bitstream
            genBitstream(f"{base_dir}/Static/Static.fasm", f"{base_dir}/Static/bitStreamSpec.bin", f"{base_dir}/Static/Static.bit")

            # Make hex files
            bit_to_hex(f"{base_dir}/Static/Static.bit", f"{base_dir}/Static/Static.hex", bytes_per_word=1)
        else:
            genBitstream(f"{base_dir}/{slot.name}/{slot.name}-slot.fasm", f"{base_dir}/{slot.name}/bitStreamSpec.bin", f"{base_dir}/{slot.name}/{slot.name}.bit")

            bit_to_hex(f"{base_dir}/{slot.name}/{slot.name}.bit", f"{base_dir}/{slot.name}/{slot.name}.hex", bytes_per_word=1)

            # Create the slot representation
            with open(f"{base_dir}/{slot.name}/{slot.name}.bit", 'rb') as bitstream_file_in:
                with open(f"{base_dir}/{slot.name}/{slot.name}-slot.bit", 'wb') as bitstream_file_out:
                    # Add file header
                    bitstream_file_out.write(0xFAB0FAB1.to_bytes(4))

                    bitstream_file_in.seek(20)
                    data = bitstream_file_in.read(76)
                    
                    while data:
                        col = int.from_bytes(data[:1], "big")>>3
                        
                        if (col >= slot.start) and (col <= slot.end):
                            bitstream_file_out.write(data)

                        data = bitstream_file_in.read(76)
                    
                    # Add desync
                    bitstream_file_out.write(0x00100000.to_bytes(4))

            bit_to_hex(f"{base_dir}/{slot.name}/{slot.name}-slot.bit", f"{base_dir}/{slot.name}/{slot.name}-slot.hex", bytes_per_word=1)

def print_help():
    print("Help:")
    print("n for new slot or connection/bridge point")
    print("e to edit an existing slot or connection/bridge point")
    print("d to delete an existing slot or connection/bridge point")
    print("q to quit")
    print("p to view config")
    print("l to load/use another config")
    print("w to write the config and generate the nextpnr, combine the fasm files, generate the bitstream depending on the set flags")
    print("h for this help text")

def select_slot_connection(layout: FabricLayout, part_function, con_function, delete = None):
    print("s for slot")
    print("c for connection point")
    print("b for bridge point")
    while True:
        user_input = input("Select type: ")
        if user_input == "s":
            if delete == None:
                part_function(layout)
            else:
                part_function(layout, delete)
            break
        elif user_input == "c":
            if delete == None:
                con_function(layout)
            else:
                con_function(layout, delete)
            break
        elif user_input == "b":
            if delete == None:
                con_function(layout, bridge=True)
            else:
                con_function(layout, delete, bridge=True)
            break

# Initialize the config structure
def init_config(layout: FabricLayout, config_path, fabric_path):
    logger.disable("FABulous")
    fabric = parse_csv.parseFabricCSV(fabric_path)

    layout.height = fabric.numberOfRows
    layout.length = fabric.numberOfColumns
    layout.tile_name_max_length = len(max(fabric.tileDic, key=len))
    layout.fabric = fabric

    if config_path:
        load_config(layout, config_path)

# Interactivly partition into slots
def slot_part(generate_files, config_path, option_static, option_combine, option_bitstream, base_dir, fabric_path):
    fabric_layout = FabricLayout()
    init_config(fabric_layout, config_path, fabric_path)

    print_layout(fabric_layout)
    print()
    print_help()

    while True:
        user_input = input("Command: ")

        if user_input == "q":
            print("Quitting")
            break
        elif user_input == "n":
            select_slot_connection(fabric_layout, create_slot, create_connection)
        elif user_input == "e":
            select_slot_connection(fabric_layout, edit_slot, edit_connection, False)
        elif user_input == "d":
            select_slot_connection(fabric_layout, edit_slot, edit_connection, True)
        elif user_input == "p":
            print_layout(fabric_layout)
        elif user_input == "l":
            config_path = load_config(fabric_layout)
        elif user_input == "w":
            write_config(fabric_layout, config_path)
            if generate_files:
                npnr_file_gen(layout, option_static, base_dir)
            if option_combine:
                combine_fasm(layout, base_dir)
            if option_bitstream:
                gen_bitstream(layout, base_dir)
        elif user_input == "h":
            print_help()
        else:
            print("Command not found")
            print_help()

# Partial config flow: 
# 1) Create static parts and slots with defined handover point (Can handover happen at routing level? pips file?)
# 2) Partition by editing bel.v2.txt and note all used pips of static parts
# 3) Produce static bitstream as base for the FPGA
# 4) Edit bel.v2.txt for the slot to create and remove used routes of the static part from pips file
# 5) After PNR add static routes crossing/supplying slot to its fasm file (Don't forget lut for data out)
# 6) Generate slot bitstream, extract the wanted region as -part
# 7) Start over from 4 for other slots
# 8) When slots are symetrical allow changing the header to change uploaded slot
if __name__ == "__main__":
    usage = "Generate eFPGA Slots\n"\
            "Usage:\n"\
            "1) Run -i to create a config file\n"\
            "2) Run -gsf <conf_file> to generate the static slot config\n"\
            "3) Run yosys and nextpnr to generate the static slot fasm file\n"\
            "4) Run -gf <conf_file> to generate the dynamic slot configs\n"\
            "5) Run yosys and nextpnr to generate the dynamic slot fasm files\n"\
            "5) Run -cf <conf_file> to merge the static fasm file into the dynamic fasm files\n"\
            "6) Run -bf <conf_file> to generate the bitstream and hex files for all slots\n"\
            "--basedir, --fabric and --spec can be combined with all options and are used if applicable\n"\
            "-i can be combined with -g <conf_file>, -c <conf_file>, -b <conf_file>, the functions are called on w command"

    arg_parser = argparse.ArgumentParser(description=usage)
    arg_parser.add_argument("-i", "--interactive", action="store_true", help="Interactivly partition eFPGA into slots and write files")
    arg_parser.add_argument("-g", "--generate", action="store_true", help="Generate bel and pips files from config")
    arg_parser.add_argument("-f", "--file", help="Config file to use")
    arg_parser.add_argument("-s", "--static", action="store_true", help="Generate the static slot")
    arg_parser.add_argument("-c", "--combine", action="store_true", help="Combine the static and dynamic fasm files")
    arg_parser.add_argument("-b", "--bitstream", action="store_true", help="Generate the bitstream from the slots")
    arg_parser.add_argument("--basedir", help="Base build directory for the slot generation, defaults to .build")
    arg_parser.add_argument("--fabric", help="fabric.csv file path, defaults to fabric.csv")
    arg_parser.add_argument("--spec", help="bitStreamSpec.bin file path, defaults to bitStreamSpec.bin")

    args = arg_parser.parse_args()
    
    if not any(vars(args).values()):
        print(usage)
        exit

    if not args.basedir:
        base_dir = ".build"
    else:
        base_dir = args.basedir

    if not args.fabric:
        fabric_path = "fabric.csv"
    else:
        fabric_path = args.fabric

    # TODO force snyc slots?
    # TODO supertiles?
    # TODO external connections?
    if args.interactive:
        slot_part(args.generate, args.file, args.static, args.combine, args.bitstream, base_dir, fabric_path)
        exit

    fabric_layout = None

    if args.generate:
        if args.file:
            if fabric_layout == None:
                fabric_layout = FabricLayout()
                init_config(fabric_layout, args.file, fabric_path)

            npnr_file_gen(fabric_layout, args.static, base_dir)
        else:
            print("The -g parameter requires the -f parameter")
    
    if args.combine:
        if args.file:
            if fabric_layout == None:
                fabric_layout = FabricLayout()
                init_config(fabric_layout, args.file, fabric_path)

            combine_fasm(fabric_layout, base_dir)
        else:
            print("The -c parameter requires the -f parameter")

    if args.bitstream:
        if args.file:
            if fabric_layout == None:
                fabric_layout = FabricLayout()
                init_config(fabric_layout, args.file, fabric_path)

            gen_bitstream(fabric_layout, base_dir)
        else:
            print("The -b parameter requires the -f parameter")
        
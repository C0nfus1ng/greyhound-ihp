#!/usr/bin/env python

from os import environ
from os import makedirs
import argparse
import csv
import re
import yaml
from loguru import logger
from FABulous.fabric_generator.parser import parse_csv
from FABulous.fabric_generator.parser.parse_switchmatrix import (
    parseList,
    parseMatrix,
)
from FABulous.fabric_definition.Bel import Bel
from FABulous.fabric_definition.Fabric import Fabric
from FABulous.fabric_definition.Tile import Tile
from FABulous.fabric_definition.define import IO, Direction
from pathlib import Path
import FABulous.fabric_cad.gen_npnr_model as gen_npnr_model
import FABulous.fabric_cad.gen_bitstream_spec as gen_bitstream_spec
import copy
import pickle

# Workaround to import existing modules, slot_gen must be run from the makefiles so paths resolve correctly
import sys
for p in Path(__file__).parents:
    if p.resolve().name == "user_designs":
        bit_tool_dir = p.resolve()
        break

sys.path.insert(0, str(bit_tool_dir))
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
    format_string:str = ""

    def __init__(self, format_string:str) -> None:
        self.format_string = format_string

    @classmethod
    def get_bold(cls) -> str:
        return "\033[1m"
    
    @classmethod
    def get_italic(cls) -> str:
        return "\033[3m"
    
    @classmethod
    def get_default(cls) -> str:
        return "\033[0m"
    
    @classmethod
    def get_static(cls) -> str:
        return "\033[31m"

    @classmethod
    def to_yaml(cls, dumper, data) -> {}:
        return dumper.represent_mapping("tag:yaml.org,2002:map",
                {"Specifier": data.format_string} if data.format_string != Format.get_default() else {})

class Point:
    x:int = 0
    y:int = 0
    formatting:Format = None

    def __init__(self, x:int, y:int, formatting:Format) -> None: 
        self.x = x
        self.y = y
        self.formatting = formatting
    
    @classmethod
    def to_yaml(cls, dumper, data) -> {}:
        return dumper.represent_mapping("tag:yaml.org,2002:map",
                {"x": data.x, "y": data.y, "Format": data.formatting} if data.formatting.format_string != Format.get_default() else {"x": data.x, "y": data.y})

class Slot:
    name:str = ""
    formatting:Format = None
    tiles:[Point] = []
    lower_left:Point = None
    upper_right:Point = None

    def __init__(self, tiles_sorted:[Point], name:str, formatting:Format) -> None:
        self.name        = name
        self.formatting  = formatting
        self.tiles       = tiles_sorted

        sort_by_x = lambda point: point.x
        sort_by_y = lambda point: point.y
        self.lower_left  = Point(min(tiles_sorted, key=sort_by_x).x , max(tiles_sorted, key=sort_by_y).y, Format(Format.get_default()))
        self.upper_right = Point(max(tiles_sorted, key=sort_by_x).x , min(tiles_sorted, key=sort_by_y).y, Format(Format.get_default()))

    @classmethod
    def sort_x_then_y(cls, point:Point, layout_height:int) -> int:
        return (point.x*layout_height)+point.y
    
    @classmethod
    def sort_by_name(cls, slot) -> int:
        if slot.name == "Static":
            return 0
        
        slot_nbr = re.search('[0-9]+', slot.name)
        if slot_nbr.group():
            return int(slot_nbr.group())

        return 1000

    @classmethod
    def sort_by_x(cls, slot) -> int:
        return slot.lower_left.x

    @classmethod
    def to_yaml(cls, dumper, data) -> {}:
        return dumper.represent_mapping("tag:yaml.org,2002:map",
                {"Name": data.name, "Format": data.formatting, "Tiles": data.tiles} if data.formatting.format_string != Format.get_default() else {"Name": data.name, "Tiles": data.tiles})

class FabricLayout:
    fabric:Fabric = None
    length:int = 0
    height:int = 0
    tile_name_max_length:int = 6
    last_color:int = 0
    slots:[Slot] = []
    points:[Point] = []
    bridges:[Point] = []

    # Fabric constants
    bit_start = 0xFAB0FAB1
    desync = 0x00100000
    tile_use_header = 0x5E7<<20
    stream_start = 0x00AAFF01
    frames_per_tile = 20

    def get_color(self) -> str: # Cycle colors 
        color = self.last_color+1
        self.last_color = (color%5) # First color is reserved for static slot
        return f"\033[3{color+1}m"

    def create_slot(self, tiles:[Point], name:str, color:str=None) -> None:
        if color:
            tmp_color = color
        elif name == "Static":
            tmp_color = Format.get_static()
        else:
            tmp_color = self.get_color()

        tiles.sort(key=self.tile_sort)
        self.slots.append(Slot(tiles, name, Format(tmp_color)))

    def tile_sort(self, point:Point) -> int:
        return Slot.sort_x_then_y(point, self.height)

    @classmethod
    def to_yaml(cls, dumper, data) -> {}:
        return dumper.represent_mapping("tag:yaml.org,2002:map",
                {"Length": data.length, "Height": data.height, "Column length": data.tile_name_max_length, 
                 "Last color": data.last_color, "Slots": data.slots, "Points": data.points, "Bridges": data.bridges})

def check_slot_static_overlap(layout:FabricLayout, static_slot:bool, tiles:[Point]) -> bool:
    check_overlap_slots = []
    if len(layout.slots) > 0 and layout.slots[0].name == "Static":
        if static_slot and layout.slots[0].name == "Static": # Check if static slot overlaps with dynamic slot
            check_overlap_slots = layout.slots[1:]
        elif static_slot: # Check if static slot overlaps with dynamic slot
            check_overlap_slots = layout.slots
        else: # Check if dynamic slot overlaps with static slot
            check_overlap_slots = [layout.slots[0]]
    else:
        print(f"No static slot to check for overlaps exists yet")

    overlapped_flag = False
    for slot in check_overlap_slots:
        for slot_tile in slot.tiles:
            for tile in tiles:
                if tile.x == slot_tile.x and tile.y == slot_tile.y:
                    print(f"Entered slot overlaps with {slot.name} on Tile X{slot_tile.x}Y{slot_tile.y}")
                    overlapped_flag = True

    return overlapped_flag

def create_slot_tiles(layout:FabricLayout, static_slot:bool) -> [Point]:
    tiles = []
    
    while True:
        tiles_to_check = []
        if static_slot:
            select = input(f"Add a single tile(s), a rectangle(r), leave(x) or quit and do nothing(q) (s/r/x/q): ")
        else:
            select = "r"

        cells = []
        if select == "s":
            cells.append(input(f"Specify a tile for the slot as X<x>Y<y>: "))
        elif select == "r":
            for corner_str in ["lower left", "upper right"]:
                cells.append(input(f"Specify the {corner_str} slot corner as X<x>Y<y>: "))
        elif select == "x":
            return tiles if len(tiles) > 0 else None
        elif select == "q":
            return None

        slot_tiles = []
        try:
            for cell in cells:
                slot_tiles.append([int(x[1:]) for x in re.findall('X[0-9]+|Y[0-9]+', cell)])

            if len(slot_tiles) == 1: #point
                if (slot_tiles[0][0] >= layout.length or slot_tiles[0][1] >= layout.height):
                    print(f"Slot tile has to be in the fabric coordinates")
                    continue
                
                new_point = Point(slot_tiles[0][0], slot_tiles[0][1], Format(Format.get_default()))
                if new_point not in tiles:
                    tiles_to_check.append(new_point)

            elif len(slot_tiles) == 2: #rectangle
                if (slot_tiles[0][0] >= layout.length or slot_tiles[0][1] >= layout.height or slot_tiles[1][0] >= layout.length or slot_tiles[1][1] >= layout.height):
                    print(f"Slot rectangular has to be fully in the fabric coordinates")
                    
                    if static_slot:
                        continue
                    else:
                        return None

                if (slot_tiles[0][0] > slot_tiles[1][0] or slot_tiles[0][1] < slot_tiles[1][1]):
                    print(f"Slot coordinates do not span a rectangular")
                    
                    if static_slot:
                        continue
                    else:
                        return None

                for col in range(slot_tiles[0][0], slot_tiles[1][0]+1):
                    for row in range(slot_tiles[1][1], slot_tiles[0][1]+1):
                        new_point = Point(col, row, Format(Format.get_default()))

                        if new_point not in tiles:
                            tiles_to_check.append(new_point)

            print()
        except:
            print("Wrong Point format")
            if static_slot:
                continue
            else:
                return None

        if check_slot_static_overlap(layout, static_slot, tiles_to_check):
            print(f"Tiles overlapped with {"dynamic" if static_slot else "static"} slot, no tiles added")
            
            if static_slot:
                continue
            else:
                return None

        tiles += tiles_to_check

        if not static_slot:
            return tiles if len(tiles) > 0 else None

    return None

def create_slot(layout:FabricLayout) -> None:
    print("Dynamic slots can only be vertical and should not overlap each other horizontally")
    print("There can only be 1 static slot")
    while True:
        slot_type = input("Enter slot type static or dynamic (s/d): ")
        if slot_type == "d":
            name = f"Slot{len(layout.slots) if len(layout.slots)>0 and layout.slots[0].name == "Static" else len(layout.slots)+1}"
            break
        elif slot_type == "s":
            name = f"Static"
            break

    for slot in layout.slots:
        if name == slot.name:
            print("This slot already exists, modify it with the e command")
            print()
            return

    tiles = create_slot_tiles(layout, slot_type == "s")
    if tiles == None:
        return

    layout.create_slot(tiles, name)
    layout.slots.sort(key=Slot.sort_by_name)

def edit_slot(layout:FabricLayout, delete:bool) -> None:
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

    if delete:
        # Remove slot
        layout.slots.remove(edit_slot)
        return

    tiles = create_slot_tiles(layout, edit_slot.name == "Static")
    if tiles == None:
        return

    layout.slots.remove(edit_slot)
    layout.create_slot(tiles, edit_slot.name, edit_slot.formatting.format_string)
    layout.slots.sort(key=Slot.sort_by_name)

def create_connection(layout:FabricLayout, bridge:bool=False) -> None:
    if bridge:
        cell = input("Specify the bridge point as X<x>Y<y> (Should be placed between slots for connectivity): ")
    else:
        cell = input("Specify the slot connection point as X<x>Y<y> (Should be placed in a dynamic slot): ")

    slot_connection = [int(x[1:]) for x in re.findall('X[0-9]+|Y[0-9]+', cell)]
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
   
def edit_connection(layout:FabricLayout, delete:bool, bridge:bool=False) -> None:
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

    create_connection(layout, bridge)

def write_config(layout:FabricLayout,file_path:str=None) -> None:
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

def load_config(layout:FabricLayout, file_path:str=None) -> str:
    if file_path == None:
        file_path = input("Enter config file to load: ")

        print()
        print(f"{file_path} will be loaded")

        while True:
            user_input = input("Load file y/n: ")

            if user_input == "y":
                break
            elif user_input == "n":
                return None

    try:
        with open(file_path, 'r') as file:
            layout_config = yaml.safe_load(file)
    except FileNotFoundError:
        print("File to load not found")
        return None
    except yaml.parser.ParserError:
        print("File cannot be parsed")
        return None

    if layout_config == None:
        print("File to load is empty")
        return None

    if not isinstance(layout_config, dict):
        print("File format is not supported")
        return None

    try:
        if layout.height != layout_config["Height"] or layout.length != layout_config["Length"] or layout.tile_name_max_length != layout_config["Column length"]:
            print("Loading file failed. Fabric size Mismatch")
            return None

        # Load color
        layout.last_color = layout_config["Last color"]

        # Load slots
        layout.slots.clear()
        for slot_dict in layout_config["Slots"]:
            tiles = []
            for tile in slot_dict["Tiles"]:
                tiles.append(Point(tile["x"], tile["y"], Format(tile["Format"]["Specifier"] if "Format" in tile.keys() and "Specifier" in tile["Format"].keys() else Format.get_default())))

            layout.create_slot(tiles, slot_dict["Name"], slot_dict["Format"]["Specifier"] if "Format" in slot_dict.keys() and "Specifier" in slot_dict["Format"].keys() else Format.get_default())
        
        layout.slots.sort(key=Slot.sort_by_name)

        # Load Points
        layout.points.clear()
        for point in layout_config["Points"]:
            layout.points.append(Point(point["x"], point["y"], Format(point["Format"]["Specifier"] if "Format" in point.keys() and "Specifier" in point["Format"].keys() else Format.get_default())))

        # Load Bridges
        layout.bridges.clear()
        for bridge in layout_config["Bridges"]:
            layout.bridges.append(Point(bridge["x"], bridge["y"], Format(bridge["Format"]["Specifier"] if "Format" in bridge.keys() and "Specifier" in bridge["Format"].keys() else Format.get_default())))

    except KeyError:
        print("File has missing keys")
        return None

    return file_path

def print_layout_overview(base_slot:Slot, tile_name_max_length:int, sub_slots:[Slot]=None) -> None:
    if not sub_slots:
        sub_slots = [base_slot]

    slot_str_pre_len = 0
    for sub_slot in sorted(sub_slots, key=Slot.sort_by_x):
        slot_str_before = 10 + sub_slot.lower_left.x*tile_name_max_length
        slot_name_max_length = (sub_slot.upper_right.x-sub_slot.lower_left.x+1)*tile_name_max_length - 4
        slot_name_before = int((slot_name_max_length-len(base_slot.name))/2)
        slot_name_after = max(slot_name_max_length-(slot_name_before + len(base_slot.name)), 0)

        print_str = f"{sub_slot.formatting.format_string}{" "*(slot_str_before-slot_str_pre_len)}|<{pad_str(base_slot.name, slot_name_max_length, slot_name_before, slot_name_after)}>|{Format.get_default()}"
        slot_str_pre_len += len(print_str) - (len(sub_slot.formatting.format_string) + len(Format.get_default()))
        print(print_str, end="")
    print()

def pad_str_right(string:str, max_len:int) -> str:
    return pad_str(string, max_len, 0, max(max_len-len(string), 0))

def pad_str(string:str, max_len:int, before:int, after:int) -> str:
    return f"{" "*before}{string if len(string)<=max_len else string[:max_len-3]+"..."}{" "*after}"

def print_layout(layout:FabricLayout, option_nomerge:bool) -> None:
    merged_slots = gen_merged_slots(layout, option_nomerge, False)
    print()

    # Point
    print(f"{Format.get_italic()}Italic{Format.get_default()} for non static bridging tiles")
    print(f"{Format.get_bold()}Bold{Format.get_default()} for connection tiles between static and dynamic slots")
    # Slot overview
    for slot in layout.slots:
        print_layout_overview(slot, layout.tile_name_max_length)

    # Merged slot overview
    for slot, sub_slots in merged_slots.items():
        print_layout_overview(slot, layout.tile_name_max_length, sub_slots)

    # Table
    print(f"Row/Col | {"".join([pad_str_right(f"X{col:02}", layout.tile_name_max_length) for col in range(layout.length)])}")
    print("-"*(10+layout.length*layout.tile_name_max_length))
    for row in range(layout.height):
        print(f"{pad_str_right(f"Y{row:02}", 7)} | ", end='')

        for col in range(layout.length):
            # Coloring
            for slot in layout.slots:
                colored_tile = False
                for tile in slot.tiles:
                    if tile.x == col and tile.y == row:
                        print(slot.formatting.format_string, end='')
                        colored_tile = True
                        break
            
                if colored_tile:
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
            
            tile_name = layout.fabric.tile[row][col].name if layout.fabric.tile[row][col] else "NULL"
            print(pad_str_right(tile_name, layout.tile_name_max_length), end='')
            print(Format.get_default(), end='')
        print()

def verilog_gen(tile:Tile, slot:Slot, base_dir:str, con_point:tuple[int, int], static_slot:bool) -> None:
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

def strip_bel_pips(bels:list[Bel]) -> [str]:
    remove_pips = []
    for bel in bels:
        remove_pips += bel.inputs
        remove_pips += bel.outputs

    return remove_pips

def get_tile_matrix(filePath: Path) -> {str: [str]}:
    # Get the tile matrix from the path
    match filePath.suffix:
        case ".list":
            tile_matrix = parseList(filePath, "source")
        case "_matrix.csv":
            tile_matrix = parseMatrix(filePath, tileName)
        case _ :
            tile_matrix = {}

    return tile_matrix

def strip_config_pips(tile:Tile) -> [str]:
    # Strip everything with more than 1 output, so static cannot edit config bits here
    tile_matrix = get_tile_matrix(tile.matrixDir)

    remove_pips = []
    for source, sink_list in tile_matrix.items():
        if len(sink_list) >= 2:
            remove_pips += [f"{sink}"r"\."+f"{source}" for sink in sink_list]

    return remove_pips

def bel_gen_from_slot(tile:Tile, slot:Slot, base_dir:str, con_point:tuple[int, int], static_slot:bool) -> Bel:
    filename = Path(f"{base_dir}/{slot.name}/{slot.name}_slot_con_X{con_point.x}Y{con_point.y}.v")
    module_name = f"{slot.name}_slot_con_X{con_point.x}Y{con_point.y}"

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

def get_slot_match(layout:FabricLayout, slot:Slot, other_slot:Slot) -> bool:
    # Static slot is exempt
    if other_slot.name == "Static":
        return False

    # Slot cannot overlap with itself
    if other_slot == slot:
        return False

    # Slot size is different
    if (other_slot.upper_right.x-other_slot.lower_left.x) != (slot.upper_right.x-slot.lower_left.x) or (other_slot.upper_right.y-other_slot.lower_left.y) != (slot.upper_right.y-slot.lower_left.y):
        return False

    # Slots partially overlap
    if ((slot.lower_left.x >= other_slot.lower_left.x and slot.lower_left.x <= other_slot.upper_right.x) or (slot.upper_right.x >= other_slot.lower_left.x and slot.upper_right.x <= other_slot.upper_right.x)) and\
        ((slot.lower_left.y <= other_slot.lower_left.y and slot.lower_left.y >= other_slot.upper_right.y) or (slot.upper_right.y <= other_slot.lower_left.y and slot.upper_right.y >= other_slot.upper_right.y)):
        return False

    slot_cons = []
    other_slot_cons = []
    for bridge in layout.bridges:
        if slot.lower_left.x <= bridge.x and bridge.x <= slot.upper_right.x:
            slot_cons.append((bridge, layout.fabric.tile[bridge.y][bridge.x], 0))

        if other_slot.lower_left.x <= bridge.x and bridge.x <= other_slot.upper_right.x:
            other_slot_cons.append((bridge, layout.fabric.tile[bridge.y][bridge.x], 0))

    for point in layout.points:
        if slot.lower_left.x <= point.x and point.x <= slot.upper_right.x:
            slot_cons.append((point, layout.fabric.tile[point.y][point.x], 1))

        if other_slot.lower_left.x <= point.x and point.x <= other_slot.upper_right.x:
            other_slot_cons.append((point, layout.fabric.tile[point.y][point.x], 1))

    # Different amount of connectors
    if len(slot_cons) != len(other_slot_cons):
        return False

    # Sort for the slot cons
    sort_match = lambda point: (point[0].x*layout.height)+point[0].y
    slot_cons.sort(key=sort_match)
    other_slot_cons.sort(key=sort_match)
    
    for i in range(len(slot_cons)):
        if slot_cons[i][2] != other_slot_cons[i][2]: # Connector type mismatch
            return False

        if (slot_cons[i][0].x-slot.lower_left.x) != (other_slot_cons[i][0].x-other_slot.lower_left.x) or slot_cons[i][0].y != other_slot_cons[i][0].y: # Connector pos mismatch
            return False

        if slot_cons[i][1].name != other_slot_cons[i][1].name: # Connector tile mismatch
            return False

    # Clot connections are sorted now check the slot itself
    for i in range(len(slot.tiles)):
        if layout.fabric.tile[slot.tiles[i].y][slot.tiles[i].x].name != layout.fabric.tile[other_slot.tiles[i].y][other_slot.tiles[i].x].name:
            return False

    return True

def gen_merged_slots(layout:FabricLayout, option_nomerge:bool, quiet:bool=True) -> {Slot:[Slot]}:
    slots = {}
    checked = {}

    if option_nomerge:
        return slots

    for base_slot in layout.slots:
        if base_slot.name == "Static":
            checked[base_slot] = True
            continue

        if base_slot in checked.keys():
            continue
        
        overlapped_slots = []
        
        for slot in layout.slots:
            if slot in checked.keys():
                continue

            if get_slot_match(layout, base_slot, slot):
                if not quiet:
                    print(f"{base_slot.name} merged with {slot.name}")

                overlapped_slots.append(slot)
                checked[slot] = True

        checked[base_slot] = True
        if len(overlapped_slots) > 0:
            overlapped_slots.append(base_slot)
            overlapped_slots.sort(key=Slot.sort_by_name)

            slot_nbr_str = [found.group() if (found := re.search('[0-9]+', slot.name)) else "" for slot in overlapped_slots[1:]]
            slot_name = overlapped_slots[0].name + "_" + "_".join(slot_nbr_str)

            if not quiet:
                print(f"Slots merged into {slot_name}")
            
            slots[Slot(base_slot.tiles, slot_name, base_slot.formatting)] = overlapped_slots

    return slots

def get_overlapping_tiles(layout:FabricLayout, point_list:[Point], slot_list:[Slot]) -> {Point:{(int,int):Tile}}:
    overlapping_tiles = {}

    # Known that slots match exactly (Connectors, connector tiles, ...), and are sorted by col
    base_slot = slot_list[0]
    
    for slot in slot_list:
        for tile in slot.tiles:
            for point in point_list:
                if tile.x == point.x and tile.y == point.y:
                    if point not in overlapping_tiles.keys():
                        overlapping_tiles[point] = {}

                    pos_in_slot = point.x - slot.lower_left.x

                    if (base_slot.lower_left.x + pos_in_slot, point.y) in overlapping_tiles[point].keys():
                        continue

                    overlapping_tiles[point][(base_slot.lower_left.x + pos_in_slot, point.y)] = layout.fabric.tile[point.y][base_slot.lower_left.x  + pos_in_slot]

    return overlapping_tiles

def remove_pips_fasm(overlapping_tiles:{Point:{(int,int):Tile}}, fasm_wires:{str:(str,str)}, tmp_pips:[str], removed_pips:[str]) -> ([str],[str]):
    tmp_split_pips = split_pip_line(tmp_pips)

    for pos, tile_list in overlapping_tiles.items():
        for (x, y), tile in tile_list.items():
            if tile == None or f"X{pos.x}Y{pos.y}" not in fasm_wires.keys():
                continue

            tile_matrix = get_tile_matrix(tile.matrixDir)
            search_pip_list = []
            for fasm_wire in fasm_wires[f"X{pos.x}Y{pos.y}"]:
                if fasm_wire[1] in tile_matrix.keys():
                    search_pip_list += [re.compile(f"{wire}"+r"\."+f"{fasm_wire[1]}") for wire in tile_matrix[fasm_wire[1]]]
                else:
                    search_pip_list.append(re.compile(f"{fasm_wire[0]}"+r"\."+f"{fasm_wire[1]}"))

            for split_pip in tmp_split_pips[f"X{x}Y{y}"]:
                for search_pip in search_pip_list:
                    if search_pip.match(split_pip[1]):
                        removed_pips.append(tmp_pips[split_pip[0]])

    removed_pips = list(dict.fromkeys(removed_pips))
    return (list(set(tmp_pips) - set(removed_pips)), removed_pips)

def remove_pips_static(tmp_pips:[str], remove_pips:{str: {}, str: {}}) -> ([str],[str]):
    removed_pips = []
    tmp_split_pips = split_pip_line(tmp_pips)

    for key, tile_pips in remove_pips.items():
        for pos, wire_list in tile_pips.items():
            # Search and remove wires
            search_pip_list = []
            if key == "bels":
                search_pip_list = [re.compile(r"([^\.]+\."+f"{wire}$)|({wire}"+r"\..+$)") for wire in wire_list]
            elif key == "muxes":
                search_pip_list = [re.compile(f"{wire}$") for wire in wire_list]

            for split_pip in tmp_split_pips[f"X{pos.x}Y{pos.y}"]:
                for search_pip in search_pip_list:
                    if search_pip.match(split_pip[1]):
                        removed_pips.append(tmp_pips[split_pip[0]])

    removed_pips = list(dict.fromkeys(removed_pips))
    return (list(set(tmp_pips) - set(removed_pips)), removed_pips)

def split_pip_line(pips:[str]) -> {str:[(int, str)]}:
    split_pips = {}
    for pip_pos, pip in enumerate(pips):
        split_pip = pip.split(",")
        
        if len(split_pip) > 6 or len(split_pip) < 6:
            RuntimeError(f"PIP line is non conforming")

        if split_pip[0] not in split_pips.keys():
            split_pips[split_pip[0]] = []

        split_pips[split_pip[0]].append((pip_pos, split_pip[-1]))

    return split_pips

def check_tile_in_merged_slot(pos:Point, merged_slots:{Slot:[Slot]}) -> bool:
    for merged_slot, slots in merged_slots.items():
        for slot in slots:
            if slot.lower_left.x <= pos.x and pos.x <= slot.upper_right.x and slot.lower_left.y >= pos.y and pos.y >= slot.upper_right.y:
                return True

    return False

def npnr_file_gen(layout:FabricLayout, option_static:bool, option_nomerge:bool, base_dir:str, fasm_files:{str:[str]}) -> None:
    if not option_static:
        if not fasm_files or (fasm_files and "Static" not in fasm_files.keys()):
            static_prog = "Static"
        else:
            static_prog = fasm_files["Static"][0]

        fasm_parsed = parse_fasm_filename(f"{base_dir}/Static/{static_prog}.fasm")
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

    # create merged slots
    merged_slots = gen_merged_slots(layout, option_nomerge)
    all_slots = layout.slots + list(merged_slots.keys())

    # Build fabric per slot
    for slot in all_slots:
        static_slot = False
        dynamic_slot = False
        merged_slot = False
        makedirs(f"{base_dir}/{slot.name}/.FABulous", exist_ok=True)

        if slot.name == "Static" and option_static:
            static_slot = True
            print("Static slot")
        elif slot.name != "Static" and not option_static and slot not in merged_slots:
            dynamic_slot = True
            print(f"Dynamic slot: {slot.name}")
        elif slot.name != "Static" and not option_static and slot in merged_slots:
            merged_slot = True
            print(f"Merged slot: {slot.name}")
        else:
            print(f"Skip slot: {slot.name}")
            continue

        tmp_fabric = copy.deepcopy(layout.fabric)
        tmp_fabric.tile = [[None for x in range(layout.length)] for x in range(layout.height)]

        # Only use tiles and pips from slot
        for tile_point in slot.tiles:
            tmp_fabric.tile[tile_point.y][tile_point.x] = layout.fabric.tile[tile_point.y][tile_point.x]

        # Static slot gen
        if static_slot:
            remove_pips = {"bels": {}, "muxes": {}}

            # Add pips from bridges
            for bridge in layout.bridges:
                tile = layout.fabric.tile[bridge.y][bridge.x]
                if tile == None:
                    continue

                tmp_fabric.tile[bridge.y][bridge.x] = copy.deepcopy(tile)
                if check_tile_in_merged_slot(bridge, merged_slots):
                    remove_pips["bels"][bridge] = strip_bel_pips(tmp_fabric.tile[bridge.y][bridge.x].bels) # Remove bel specific connections, allow bel connections if slot is not merged
                    remove_pips["muxes"][bridge] = strip_config_pips(tmp_fabric.tile[bridge.y][bridge.x])

            # Add pips from connections
            for con_point in layout.points:
                tile = layout.fabric.tile[con_point.y][con_point.x]
                if tile == None:
                    continue

                tmp_fabric.tile[con_point.y][con_point.x] = copy.deepcopy(tile)
                remove_pips["bels"][con_point] = strip_bel_pips(tmp_fabric.tile[con_point.y][con_point.x].bels)
                if check_tile_in_merged_slot(con_point, merged_slots):
                    remove_pips["muxes"][con_point] = strip_config_pips(tmp_fabric.tile[con_point.y][con_point.x])

                bel = bel_gen_from_slot(tile, slot, base_dir, con_point, static_slot)
                tmp_fabric.tile[con_point.y][con_point.x].bels.insert(0, bel) # Insert in front of all other bels, fixes some kind of npnr assert
                verilog_gen(tile, slot, base_dir, con_point, static_slot)

            tmp_npnr_model = gen_npnr_model.genNextpnrModel(tmp_fabric)

            # Remove pips of the undesired bels
            (tmp_pips, removed_pips) = remove_pips_static(tmp_npnr_model[0].split("\n"), remove_pips)
        # Dynamic slot gen
        else:
            # Check overlap of static with this slot
            if dynamic_slot:
                overlapping_bridge_tiles = get_overlapping_tiles(layout, layout.bridges, [slot])
                overlapping_point_tiles = get_overlapping_tiles(layout, layout.points, [slot])
            elif merged_slot:
                overlapping_bridge_tiles = get_overlapping_tiles(layout, layout.bridges, merged_slots[slot])
                overlapping_point_tiles = get_overlapping_tiles(layout, layout.points, merged_slots[slot])
            else:
                raise RuntimeError(f"Error slot {slot.name} can not be categorized")
                continue

            # Add custom bel
            for pos, tile_list in overlapping_point_tiles.items():
                for (x, y), tile in tile_list.items():  
                    if (x != pos.x or y != pos.y) or tile == None:
                        continue
                    
                    print(f"Create Bel for tile X{pos.x}Y{pos.y}")
                    tmp_fabric.tile[pos.y][pos.x] = copy.deepcopy(tile)
                    bel = bel_gen_from_slot(tile, slot, base_dir, pos, static_slot)
                    tmp_fabric.tile[pos.y][pos.x].bels.insert(0, bel)
                    verilog_gen(tile, slot, base_dir, pos, static_slot)

            tmp_npnr_model = gen_npnr_model.genNextpnrModel(tmp_fabric)            

            # Remove pips of the overlapping tiles
            bridge_pips_fasm = remove_pips_fasm(overlapping_bridge_tiles, fasm_wires, tmp_npnr_model[0].split("\n"), [])
            (tmp_pips, removed_pips) = remove_pips_fasm(overlapping_point_tiles, fasm_wires, bridge_pips_fasm[0], bridge_pips_fasm[1])

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

def combine_fasm(layout:FabricLayout, option_nomerge:bool, base_dir:str, fasm_files:{str:[str]}) -> None:
    if not fasm_files or (fasm_files and "Static" not in fasm_files.keys()):
        static_prog = "Static"
    else:
        static_prog = fasm_files["Static"][0]

    # Parse fasm file
    fasm_static_parsed = parse_fasm_filename(f"{base_dir}/Static/{static_prog}.fasm")
    fasm_static_str = fasm_tuple_to_string(fasm_static_parsed, True)
    fasm_static_list = list(parse_fasm_string(fasm_static_str))
    fasm_static_list_str = [set_feature_to_str(fasm_line.set_feature) for fasm_line in fasm_static_list]

    merged_slots = gen_merged_slots(layout, option_nomerge)
    all_slots = layout.slots + list(merged_slots.keys())

    for slot in all_slots:
        if slot.name == "Static":
            continue

        # Slot has no fasm_file to build
        if fasm_files and slot.name not in fasm_files.keys():
            print(f"No fasm project for slot: {slot.name}")
            continue

        tmp_fasm_files = fasm_files
        if not fasm_files:
            tmp_fasm_files = {slot.name: slot.name}

        for fasm_file_name in tmp_fasm_files[slot.name]:
            fasm_dynamic_parsed = parse_fasm_filename(f"{base_dir}/{slot.name}/{fasm_file_name}.fasm")
            fasm_dynamic_str = fasm_tuple_to_string(fasm_dynamic_parsed, True)
            fasm_dynamic_list = list(parse_fasm_string(fasm_dynamic_str))
            fasm_dynamic_list_str = [set_feature_to_str(fasm_line.set_feature) for fasm_line in fasm_dynamic_list]

            if slot in merged_slots:
                merge_slots = merged_slots[slot]
            else:
                merge_slots = [slot]

            # Get slot intersection, dynamic slots are rectangular everything in a col overlaps
            fasm_overlap_str = []
            fasm_overlap_str.append("# Routing from Static slot\n")
            for merge_slot in merge_slots:
                for col in range(merge_slot.lower_left.x, merge_slot.upper_right.x+1):
                    pos_in_slot = col - merge_slot.lower_left.x
                    search_line = re.compile(f"X{col}Y.*")

                    for fasm_static_line_str in fasm_static_list_str:
                        if search_line.match(fasm_static_line_str):
                            if fasm_static_line_str in fasm_dynamic_list_str:
                                raise RuntimeError("Dynamic slot uses same route as Static slot.")

                            # Rewrite fasm line
                            fasm_static_start_pos = fasm_static_line_str.find("Y",0,4)
                            if fasm_static_start_pos == -1:
                                raise RuntimeError("Static slot fasm line Y pos not found.")

                            fasm_overlap_str.append(f"X{slot.lower_left.x+pos_in_slot}"+fasm_static_line_str[fasm_static_start_pos:])
            
            fasm_overlap_str = list(dict.fromkeys(fasm_overlap_str)) # Dedup but keep order
            fasm_overlap_str.append("\n")
            print(f"Appending to {slot.name}-{fasm_file_name}")
            print("\n".join(fasm_overlap_str), end="")

            makedirs(f"{base_dir}/{slot.name}", exist_ok=True)
            with open(f"{base_dir}/{slot.name}/{fasm_file_name}.fasm", "r") as fasm_file, open(f"{base_dir}/{slot.name}/{fasm_file_name}-slot.fasm", "w") as fasm_slot_file:
                fasm_slot_file.write("\n".join(fasm_overlap_str))

                while line := fasm_file.readline():
                    fasm_slot_file.write(line)

def reduce_enabled_tiles(enabled_tiles_bitstream:[bytes], usercode:int) -> [bytes]:
    for i, enabled_tiles in enumerate(enabled_tiles_bitstream):
        if int.from_bytes(enabled_tiles, "big") != (FabricLayout.tile_use_header | 0x3FFFF):
            enabled_tiles_bitstream_reduced = enabled_tiles_bitstream[i:]
            
            if (i != 0) and ((usercode & 0xFFF00000) == FabricLayout.tile_use_header):
                enabled_tiles_bitstream_reduced.append(0x0.to_bytes(4)) # Add break header, since thge usercode is the tile use canary
            
            enabled_tiles_bitstream_reduced.reverse()
            return enabled_tiles_bitstream_reduced
    
    return []

def gen_dedup_bitstream(layout_height:int, filename_in:str, filename_out:str, static_filename:str, slots:[Slot]) -> None:
    print(f"Deduplicate {filename_in} into {filename_out}")

    with open(filename_in, 'rb') as bitstream_file_in, open(filename_out, 'wb') as bitstream_file_out, open(static_filename, 'rb') as static_bitstream_file:
        enabled_tiles = []
        seek_word = int.from_bytes(bitstream_file_in.read(4), "big")
        usercode = 1
        seek_stream_start = -1
        seek_byte_counter = 4
        while FabricLayout.bit_start != seek_word:
            if seek_word & 0xFFF00000 == FabricLayout.tile_use_header:
                enabled_tiles.append(seek_word)

            if seek_word == FabricLayout.stream_start:
                seek_stream_start = seek_byte_counter + 4

            if seek_stream_start == seek_byte_counter:
                usercode = seek_word

            seek_byte_counter += 1
            seek_word = ((seek_word & 0xFFFFFF) << 8) | int.from_bytes(bitstream_file_in.read(1), "big")

        static_seek_word = int.from_bytes(static_bitstream_file.read(4), "big")
        while FabricLayout.bit_start != static_seek_word:
            static_seek_word = ((static_seek_word & 0xFFFFFF) << 8) | int.from_bytes(static_bitstream_file.read(1), "big")

        bytes_per_frame = (layout_height+1)*4
        data = bitstream_file_in.read(bytes_per_frame)
        static_data = static_bitstream_file.read(bytes_per_frame)
        static_slot_data = {}
        while static_data:
            if (len(static_data) != bytes_per_frame):
                break

            static_slot_data[static_data[:4]] = static_data
            static_data = static_bitstream_file.read(bytes_per_frame)

        # Create data struct
        loaded_bitstream = {}
        enabled_tiles_index = len(enabled_tiles)-1

        slot_x_offsets = [slot.lower_left.x - slots[0].lower_left.x for slot in slots]
        while data:
            if (len(data) != bytes_per_frame):
                break

            cols = [(int.from_bytes(data[:1], "big")>>3) + slot_x_offset for slot_x_offset in slot_x_offsets]
            for col in cols:
                frame_strobe = int.from_bytes(data[1:4], "big") & 0xFFFFF
                enabled_tiles_word = enabled_tiles[enabled_tiles_index] if enabled_tiles_index >= 0 else FabricLayout.tile_use_header | 0x3FFFF

                if col not in loaded_bitstream.keys():
                    loaded_bitstream[col] = {}

                if (filename_in == static_filename) or (enabled_tiles_index <= 0) or (enabled_tiles[enabled_tiles_index] == (FabricLayout.tile_use_header | 0x3FFFF)):
                    # Frame data from slot itself
                    frame_data_key = data[4:] # Split key and data so slot can be used in all merged slots independetly of the static slot
                else: 
                    frame_header = (col<<27 | frame_strobe).to_bytes(4)
                    static_frame_data = static_slot_data[frame_header]

                    # Merge with static frame
                    frame_data_key = bytes()
                    for i_tile in reversed(range(layout_height)):
                        use_tile = (enabled_tiles_word >> i_tile) & 0x1
                        tile_start = 4*(layout_height-i_tile)

                        if use_tile:
                            frame_data_key += data[tile_start:tile_start+4]
                        else:
                            frame_data_key += static_frame_data[tile_start:tile_start+4]

                if frame_data_key in loaded_bitstream[col].keys():
                    loaded_bitstream[col][frame_data_key]["strobe"] |= frame_strobe
                else:
                    loaded_bitstream[col][frame_data_key] = {"strobe": frame_strobe, "tiles": enabled_tiles_word, "data": data[4:]}

            enabled_tiles_index -= 1
            data = bitstream_file_in.read(bytes_per_frame)

        # Split data struct
        bitstream = []
        enabled_tiles_bitstream = [] # enabled tiles are the same for all frames
        bitstream.append(FabricLayout.stream_start.to_bytes(4))
        bitstream.append(usercode.to_bytes(4))
        bitstream.append(FabricLayout.bit_start.to_bytes(4))

        for col in range(slots[0].lower_left.x, slots[0].upper_right.x+1):
            frame_cols = [col + slot_x_offset for slot_x_offset in slot_x_offsets]
            frame_strobes = []

            # Split strobes for this col
            for frame_data_key, frame_data_dict in loaded_bitstream[frame_cols[0]].items():
                frame_strobes.append(frame_data_dict)

            for frame_col in frame_cols[1:] if len(frame_cols) > 0 else []:
                for frame_data_key, frame_data_dict in loaded_bitstream[frame_col].items():
                    strobe = frame_data_dict["strobe"]

                    # Dedup multiple slots
                    new_frame_strobes = []
                    for frame_strobe_dict in frame_strobes:
                        frame_strobe = frame_strobe_dict["strobe"]
                        frame_data   = frame_strobe_dict["data"]
                        frame_tiles  = frame_strobe_dict["tiles"]
                        split_strobe = strobe ^ frame_strobe
                        overlap_strobe = strobe & frame_strobe

                        if split_strobe and overlap_strobe: # Strobes split each other and overlap, and are no subset of requested
                            if overlap_strobe != frame_strobe: # Saved is no subset of requested
                                # Split at predefined pos
                                split_bit_mask = 0
                                for i_bit in range(FabricLayout.frames_per_tile):
                                    split_bit = (split_strobe >> i_bit) & 0x1

                                    if split_bit: # Safe all before mismatch
                                        tmp_frame_strobe = frame_strobe & split_bit_mask
                                        if tmp_frame_strobe:
                                            new_frame_strobes.append({"strobe": tmp_frame_strobe, "tiles": frame_tiles, "data": frame_data})

                                        split_bit_mask = 0
                                    split_bit_mask |= 1 << i_bit
                                tmp_frame_strobe = frame_strobe & split_bit_mask

                                if tmp_frame_strobe:
                                    new_frame_strobes.append({"strobe": tmp_frame_strobe, "tiles": frame_tiles, "data": frame_data})

                                frame_strobes.remove(frame_strobe_dict)
                    frame_strobes += new_frame_strobes

            for frame_strobe_dict in frame_strobes:
                frame_strobe = frame_strobe_dict["strobe"]
                frame_data = frame_strobe_dict["data"]
                frame_tiles = frame_strobe_dict["tiles"]
                enabled_tiles_bitstream.append(frame_tiles.to_bytes(4))
                frame_header = col<<27 | frame_strobe
                bitstream.append(frame_header.to_bytes(4) + frame_data)

        # Add desync
        bitstream.append(FabricLayout.desync.to_bytes(4))

        # Write out new structure
        enabled_tiles_bitstream = reduce_enabled_tiles(enabled_tiles_bitstream, usercode)
        bitstream_file_out.write(b''.join(bitstream[:2] + enabled_tiles_bitstream + bitstream[2:]))

def gen_bitstream(layout:FabricLayout, option_nomerge:bool, base_dir:str, fasm_files:{str:[str]}) -> None:
    if not fasm_files or (fasm_files and "Static" not in fasm_files.keys()):
        static_prog = "Static"
    else:
        static_prog = fasm_files["Static"][0]

    # Create Static bitstream and hex file
    genBitstream(f"{base_dir}/Static/{static_prog}.fasm", f"{base_dir}/Static/bitStreamSpec.bin", f"{base_dir}/Static/{static_prog}.bit")
    bit_to_hex(f"{base_dir}/Static/{static_prog}.bit", f"{base_dir}/Static/{static_prog}.hex", bytes_per_word=1)

    gen_dedup_bitstream(layout.height, f"{base_dir}/Static/{static_prog}.bit", f"{base_dir}/Static/{static_prog}-dedup.bit", f"{base_dir}/Static/{static_prog}.bit", [layout.slots[0]])
    bit_to_hex(f"{base_dir}/Static/{static_prog}-dedup.bit", f"{base_dir}/Static/{static_prog}-dedup.hex", bytes_per_word=1)

    merged_slots = gen_merged_slots(layout, option_nomerge)
    all_slots = layout.slots + list(merged_slots.keys())

    if len(all_slots) == 1 and all_slots[0].name == "Static":
        return

    usercode_bitsize = int(28/(len(all_slots)-1))
    print(f"There are up to 15 usercodes for the Static slot and up to {(1<<usercode_bitsize)-1} usercodes per dynamic slot available (Usercodes start at 1)")

    for i_slot, slot in enumerate(all_slots):
        if slot.name == "Static":
            continue

        # Slot has no fasm_file to build
        if fasm_files and slot.name not in fasm_files.keys():
            continue
        
        tmp_fasm_files = fasm_files

        if not fasm_files:
            tmp_fasm_files = {slot.name: slot.name}

        for i_fasm_file, fasm_file in enumerate(tmp_fasm_files[slot.name]):
            genBitstream(f"{base_dir}/{slot.name}/{fasm_file}-slot.fasm", f"{base_dir}/{slot.name}/bitStreamSpec.bin", f"{base_dir}/{slot.name}/{fasm_file}.bit")
            bit_to_hex(f"{base_dir}/{slot.name}/{fasm_file}.bit", f"{base_dir}/{slot.name}/{fasm_file}.hex", bytes_per_word=1)
            gen_dedup_bitstream(layout.height, f"{base_dir}/{slot.name}/{fasm_file}.bit", f"{base_dir}/{slot.name}/{fasm_file}-dedup.bit", f"{base_dir}/Static/{static_prog}.bit", [slot])
            bit_to_hex(f"{base_dir}/{slot.name}/{fasm_file}-dedup.bit", f"{base_dir}/{slot.name}/{fasm_file}-dedup.hex", bytes_per_word=1)
            usercode = ((i_fasm_file+1)<<(4+(usercode_bitsize*(i_slot-1)))) & 0xFFFFFFFF
            print(f"{slot.name}/{fasm_file} has usercode: {usercode:08x}")

            # Create the slot only representation
            with open(f"{base_dir}/{slot.name}/{fasm_file}.bit", 'rb') as bitstream_file_in, open(f"{base_dir}/{slot.name}/{fasm_file}-slot.bit", 'wb') as bitstream_file_out:
                slot_bitstream = []
                # Add file header
                slot_bitstream.append(FabricLayout.stream_start.to_bytes(4))
                slot_bitstream.append(usercode.to_bytes(4))
                slot_bitstream.append(FabricLayout.bit_start.to_bytes(4))

                seek_word = int.from_bytes(bitstream_file_in.read(4), "big")
                while(FabricLayout.bit_start != seek_word):
                    seek_word = ((seek_word & 0xFFFFFF) << 8) | int.from_bytes(bitstream_file_in.read(1), "big")

                bytes_per_frame = (layout.height+1)*4
                data = bitstream_file_in.read(bytes_per_frame)

                slot_enabled_tiles_bitstream = []
                while data:
                    if (len(data) != bytes_per_frame):
                        break

                    col = int.from_bytes(data[:1], "big")>>3
                    if (col >= slot.lower_left.x) and (col <= slot.upper_right.x):
                        slot_enabled_tiles = FabricLayout.tile_use_header
                        for tile in slot.tiles:
                            for i_height in range(layout.height):
                                if i_height == tile.y:
                                    slot_enabled_tiles |= 1<<i_height
                        
                        slot_enabled_tiles_bitstream.append(slot_enabled_tiles.to_bytes(4))

                        slot_bitstream.append(data)

                    data = bitstream_file_in.read(bytes_per_frame)

                # Add desync
                slot_bitstream.append(FabricLayout.desync.to_bytes(4))

                # Write to file
                slot_enabled_tiles_bitstream = reduce_enabled_tiles(slot_enabled_tiles_bitstream, usercode)
                bitstream_file_out.write(b''.join(slot_bitstream[:2]+slot_enabled_tiles_bitstream+slot_bitstream[2:]))

            bit_to_hex(f"{base_dir}/{slot.name}/{fasm_file}-slot.bit", f"{base_dir}/{slot.name}/{fasm_file}-slot.hex", bytes_per_word=1)
            gen_dedup_bitstream(layout.height, f"{base_dir}/{slot.name}/{fasm_file}-slot.bit", f"{base_dir}/{slot.name}/{fasm_file}-slot-dedup.bit", f"{base_dir}/Static/{static_prog}.bit", merged_slots[slot] if slot in merged_slots.keys() else [slot])
            bit_to_hex(f"{base_dir}/{slot.name}/{fasm_file}-slot-dedup.bit", f"{base_dir}/{slot.name}/{fasm_file}-slot-dedup.hex", bytes_per_word=1)

def print_help() -> None:
    print("Help:")
    print("n for new slot or connection/bridge point")
    print("e to edit an existing slot or connection/bridge point")
    print("d to delete an existing slot or connection/bridge point")
    print("q to quit")
    print("p to view config")
    print("l to load/use another config")
    print("w to write the config and generate the nextpnr, combine the fasm files, generate the bitstream depending on the set flags")
    print("h for this help text")

def select_slot_connection(layout:FabricLayout, part_function, con_function, delete:bool=None) -> None:
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
def init_config(layout:FabricLayout, config_path:str, fabric_path:str) -> None:
    logger.disable("FABulous")
    fabric = parse_csv.parseFabricCSV(fabric_path)

    layout.height = fabric.numberOfRows
    layout.length = fabric.numberOfColumns
    layout.tile_name_max_length = len(max(fabric.tileDic, key=len))
    layout.fabric = fabric

    if config_path:
        load_config(layout, config_path)

# Interactivly partition into slots
def slot_part(generate_files:bool, config_path:str, option_static:bool, option_combine:bool, option_bitstream:bool, option_nomerge:bool, base_dir:str, fabric_path:str, fasm_files:{str:[str]}) -> None:
    fabric_layout = FabricLayout()
    init_config(fabric_layout, config_path, fabric_path)
    print_layout(fabric_layout, option_nomerge)
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
            print_layout(fabric_layout, option_nomerge)
        elif user_input == "l":
            new_config_path = load_config(fabric_layout)

            if new_config_path and new_config_path != config_path:
                config_path = new_config_path
        elif user_input == "w":
            write_config(fabric_layout, config_path)
            if generate_files:
                npnr_file_gen(layout, option_static, option_nomerge, base_dir, fasm_files)
            if option_combine:
                combine_fasm(layout, option_nomerge, base_dir, fasm_files)
            if option_bitstream:
                gen_bitstream(layout, option_nomerge, base_dir, fasm_files)
        elif user_input == "h":
            print_help()
        else:
            print("Command not found")
            print_help()

def parse_prog(fasm_files:str) -> {str:[str]}:
    if not fasm_files:
        return None

    if not re.match(r"^([^=,\s]+=[^=,\s]+(,[^=,\s]+)*)(\s+[^=,\s]+=[^=,\s]+(,[^=,\s]+)*)*$", fasm_files):
        raise RuntimeError(f"Invalid format --fasm \"{fasm_files}\"")
        return None

    slot_progs_line = fasm_files.split(" ")
    slot_progs_dict = dict([slot_prog.split("=") for slot_prog in slot_progs_line])

    for slot, fasm_file in slot_progs_dict.items():
        if slot == "Static":
            static_progs = fasm_file.split(",")
            if len(static_progs) > 1:
                print(f"Warning: static can only do 1 fasm file per run, using first fasm file in list: {static_progs[0]}")
            
            slot_progs_dict[slot] = [static_progs[0]]
        else:
            slot_progs_dict[slot] = fasm_file.split(",")

    return slot_progs_dict

# TODO fix producing empty tiles in bitstream spec (Workaround applied in bit_gen.py)
# TODO allow slots to merge if size and tiles match but y coords don't
# TODO dedup relies on bit_gen only ever setting 1 strobe bit at a time
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
            "Use -h, --help to get the help text for all flags\n"\
            "Usage:\n"\
            "1) Run -i to create a config file\n"\
            "2) Run -gsf <conf_file> to generate the static slot config\n"\
            "3) Run yosys and nextpnr to generate the static slot fasm file\n"\
            "4) Run -gf <conf_file> to generate the dynamic slot configs\n"\
            "5) Run yosys and nextpnr to generate the dynamic slot fasm files\n"\
            "6) Run -cf <conf_file> to merge the static fasm file into the dynamic fasm files\n"\
            "7) Run -bf <conf_file> to generate the bitstream and hex files for all slots\n"\
            "--basedir, --fabric, --spec, --progdir and --nomerge can be combined with all options and are used if applicable\n"\
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
    arg_parser.add_argument("--fasm", help="FASM file to generate the bitstream for a slot, defaults to slot name=slot name. Use with specifiying the slot, like --fasm \"Slot1=Prog1,Prog2,.. Slot2=...\"")
    arg_parser.add_argument("--nomerge", action="store_true", help="Prevent merging of slots, may allow routing for static slot with high congestion by sacrificing slot interoperability")

    args = arg_parser.parse_args()
    
    if not any(vars(args).values()):
        print(usage)
        exit

    fasm_files = parse_prog(args.fasm)

    if not args.basedir:
        base_dir = ".build"
    else:
        base_dir = args.basedir

    if not args.fabric:
        fabric_path = "fabric.csv"
    else:
        fabric_path = args.fabric

    if args.interactive:
        slot_part(args.generate, args.file, args.static, args.combine, args.bitstream, args.nomerge, base_dir, fabric_path, fasm_files)
        exit

    fabric_layout = None

    if args.generate:
        if args.file:
            if fabric_layout == None:
                fabric_layout = FabricLayout()
                init_config(fabric_layout, args.file, fabric_path)

            npnr_file_gen(fabric_layout, args.static, args.nomerge, base_dir, fasm_files)
        else:
            print("The -g parameter requires the -f parameter")
    
    if args.combine:
        if args.file:
            if fabric_layout == None:
                fabric_layout = FabricLayout()
                init_config(fabric_layout, args.file, fabric_path)

            combine_fasm(fabric_layout, args.nomerge, base_dir, fasm_files)
        else:
            print("The -c parameter requires the -f parameter")

    if args.bitstream:
        if args.file:
            if fabric_layout == None:
                fabric_layout = FabricLayout()
                init_config(fabric_layout, args.file, fabric_path)

            gen_bitstream(fabric_layout, args.nomerge, base_dir, fasm_files)
        else:
            print("The -b parameter requires the -f parameter")

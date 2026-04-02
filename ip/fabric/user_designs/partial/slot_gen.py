#!/usr/bin/env python

from os import environ
import argparse
import csv
import re
import yaml
from loguru import logger
from FABulous.fabric_generator.parser import parse_csv
import FABulous.fabric_cad.gen_npnr_model as model_gen_npnr
import copy

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

def create_partition(layout: FabricLayout):
    print("Slots can only be vertical")
    print("There can only be 1 static slot")
    while True:
        slot_type = input("Slot type (static/dynamic): ")
        if slot_type == "dynamic":
            name = f"Slot{len(layout.slots):2}"
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

def edit_partition(layout: FabricLayout, delete):
    while True:
        edit_slot = None
        user_input = input(f"Enter partition name to {"delete" if delete else "edit"}/Use x to leave: ")

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





def file_gen(layout: FabricLayout, option_static):
    fabulous_root = environ.get("FABULOUS_ROOT", "../../macro/ihp-sg13g2/fabulous")
    print("hi")

    # Build fabric per slot
    for slot in layout.slots:
        if slot.name == "Static" and option_static:
            print("Static Slot")
        elif slot.name != "Static" and not option_static:
            print("Dynamic Slot: {slot.name}")
        else:
            print(f"Skip Slot: {slot.name}")
            continue

        tmp_fabric = copy.deepcopy(layout.fabric)
        tmp_fabric.tile = [[None]*layout.length]*layout.height

        # Tiles only
        for row in range(layout.height):
            for col in range(slot.start, slot.end+1):
                tmp_fabric.tile[row][col] = layout.fabric.tile[row][col]

        # Fix Tiles
        # TODO
        for row in range(layout.height):
            for col in range(0, slot.start) or range(slot.end+1, layout.length):
                print(f"Row {row}, Col {col}")

        return
        npnr_model = model_gen_npnr.genNextpnrModel(tmp_fabric)

        # TODO allow folder change
        with open(f".build/{slot.name}/pips.txt", "w") as f:
            f.write(npnr_model[0])

        with open(f".build/{slot.name}/bel.v2.txt", "w") as f:
            f.write(npnr_model[2])

        # TODO
        # Static slot gen

        # Dynamic slot gen



    # print(layout.fabric.tile[1][0].bels[0].belFeatureMap)
    # print(npnr_model)

def print_help():
    print("Help:")
    print("n for new slot or connection/bridge point")
    print("e to edit an existing slot or connection/bridge point")
    print("d to delete an existing slot or connection/bridge point")
    print("q to quit")
    print("p to view config")
    print("l to load/use another config")
    print("w to write the config")
    print("h for this help text")

def select_partition_connection(layout: FabricLayout, part_function, con_function, delete = None):
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
def init_config(layout: FabricLayout, config_path):
    fabulous_fabric = environ.get("FABULOUS_FABRIC", "../../fabric.csv")

    logger.disable("FABulous")
    fabric = parse_csv.parseFabricCSV("../../fabric.csv")

    layout.height = fabric.numberOfRows
    layout.length = fabric.numberOfColumns
    layout.tile_name_max_length = len(max(fabric.tileDic, key=len))
    layout.fabric = fabric

    if config_path:
        load_config(layout, config_path)

# Interactivly partition slots
def slot_part(generate_files, config_path, option_static):
    fabric_layout = FabricLayout()
    init_config(fabric_layout, config_path)

    print_layout(fabric_layout)
    print()
    print_help()

    while True:
        user_input = input("Command: ")

        if user_input == "q":
            print("Quitting")
            break
        elif user_input == "n":
            select_partition_connection(fabric_layout, create_partition, create_connection)
        elif user_input == "e":
            select_partition_connection(fabric_layout, edit_partition, edit_connection, False)
        elif user_input == "d":
            select_partition_connection(fabric_layout, edit_partition, edit_connection, True)
        elif user_input == "p":
            print_layout(fabric_layout)
        elif user_input == "l":
            config_path = load_config(fabric_layout)
        elif user_input == "w":
            write_config(fabric_layout, config_path)
            if generate_files:
                file_gen(layout, option_static)
        elif user_input == "h":
            print_help()
        else:
            print("Command not found")
            print_help()


    # TODO Partial config flow: 
    # 1) Create static parts and slots with defined handover point (Can handover happen at routing level? pips file?)
    # 2) Partition by editing bel.v2.txt and note all used pips of static parts
    # 3) Produce static bitstream as base for the FPGA
    # 4) Edit bel.v2.txt for the slot to create and remove used routes of the static part from pips file
    # 5) After PNR add static routes crossing/supplying slot to its fasm file (Don't forget lut for data out)
    # 6) Generate slot bitstream, extract the wanted region as -part
    # 7) Start over from 4 for other slots
    # 8) When slots are symetrical allow changing the header to change uploaded slot


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description="Generate eFPGA Slots")
    arg_parser.add_argument("-p", "--partition", action="store_true", help="Interactivly create partitioning and write files")
    arg_parser.add_argument("-g", "--generate", action="store_true", help="Generate bel and pips files from config")
    arg_parser.add_argument("-f", "--file", help="Config file to use")
    arg_parser.add_argument("-s", "--static", action="store_true", help="Generate the static slot")

    args = arg_parser.parse_args()

    if args.partition:
        slot_part(args.generate, args.file, args.static)
    elif args.generate:
        if args.file:
            fabric_layout = FabricLayout()
            init_config(fabric_layout, args.file)
            file_gen(fabric_layout, args.static)
        else:
            print("The -g parameter requires the -f parameter")

#!/usr/bin/env python

from os import environ
import argparse
import csv
import re
import yaml
from loguru import logger
from FABulous.fabric_generator.parser import parse_csv

from fasm import (
    parse_fasm_filename,
    fasm_tuple_to_string,
    parse_fasm_string,
    set_feature_to_str,
)

class Slot:
    start = 0
    end = 0
    name = ""
    format_ = ""

    def __init__(self, start, end, name, format_):
        self.start   = start
        self.end     = end
        self.name    = name
        self.format_ = format_

    @classmethod
    def to_yaml(cls, dumper, data):
        return dumper.represent_mapping("tag:yaml.org,2002:map",
                {"Start": data.start, "End": data.end, "Name": data.name, "Format": data.format_})

class Point:
    x = 0
    y = 0

    def __init__(self, x, y): 
        self.x = x
        self.y = y
    
    @classmethod
    def to_yaml(cls, dumper, data):
        return dumper.represent_mapping("tag:yaml.org,2002:map",
                {"x": data.x, "y": data.y})

class FabricLayout:
    fabric = None
    layout_format = dict()
    length = 0
    height = 0
    tile_name_max_length = 6
    last_color = 0
    slots = list()
    points = list()

    def get_color_string(self): # Cycle colors 
        color = self.last_color+1
        self.last_color = color%6
        return f"\033[3{color}m"

    def create_slot(self, start, end, name, format_=None):
        if format_:
            color = format_
        else:
            color = self.get_color_string()
        
        for col in range(start, end+1):
            for row in range(self.height):
                self.layout_format[f"X{col}Y{row}"] += color
        slot = Slot(start, end, name, color)
        self.slots.append(slot)

    def strip_slot(self, slot):
        for col in range(slot.start, slot.end+1):
            for row in range(self.height):
                self.layout_format[f"X{col}Y{row}"] = self.layout_format[f"X{col}Y{row}"].replace(slot.format_, "")

        self.slots.remove(slot)

    @classmethod
    def to_yaml(cls, dumper, data):
        return dumper.represent_mapping("tag:yaml.org,2002:map",
                {"Length": data.length, "Height": data.height, "Column Length": data.tile_name_max_length, 
                 "Last Color": data.last_color, "Slots": data.slots, "Points": data.points, "Format": data.layout_format})

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

def delete_partition(layout: FabricLayout):
    while True:
        edit_slot = None
        user_input = input("Enter partition name to delete/Use x to leave: ")

        if user_input == "x":
            return

        for slot in layout.slots:
            if user_input == slot.name:
                edit_slot = slot
                break

        if edit_slot:
            break

    print(f"Deleting slot {edit_slot.name}")

    # Remove slot
    layout.strip_slot(edit_slot)

def edit_partition(layout: FabricLayout):
    while True:
        edit_slot = None
        user_input = input("Enter partition name to edit/Use x to leave: ")

        if user_input == "x":
            return

        for slot in layout.slots:
            if user_input == slot.name:
                edit_slot = slot
                break

        if edit_slot:
            break

    print(f"Editing slot {edit_slot.name}")
    print("Slots can only be vertical")

    # Remove slot
    layout.strip_slot(edit_slot)

    first_column = int(input("First column: "))
    last_column = int(input("Last column: "))
    layout.create_slot(first_column, last_column, edit_slot.name, edit_slot.format_)
    print()

def create_connection(layout: FabricLayout):
    cell = input("Specify the slot connection point as X<x>Y<y> (Should be routed into a dynamic slot): ")
    slot_connection = [int(re.findall('[0-9]', x)[0]) for x in re.findall('X[0-9]+|Y[0-9]+', cell)]
    try:
        print(f"Added connection point at X{slot_connection[0]}Y{slot_connection[1]}")
    except:
        print()
        return

    layout.points.append(Point(slot_connection[0], slot_connection[1]))
    layout.layout_format[f"X{slot_connection[0]}Y{slot_connection[1]}"] += "\033[1m\033[3m"
    print()

def delete_connection(layout: FabricLayout):
    while True:
        edit_point = None
        user_input = input("Enter connection point to delete as XxYy/Use x to leave: ")

        if user_input == "x":
            return

        for point in layout.points:
            if user_input == f"X{point.x}Y{point.y}":
                edit_point = point
                break

        if edit_point:
            break

    print(f"Deleting connection point X{edit_point.x}Y{point.y}")
    layout.layout_format[f"X{edit_point.x}Y{edit_point.y}"] = layout.layout_format[f"X{edit_point.x}Y{edit_point.y}"].replace("\033[1m\033[3m", "")
    layout.points.remove(edit_point)
    
def edit_connection(layout: FabricLayout):
    while True:
        edit_point = None
        user_input = input("Enter connection point to edit as XxYy/Use x to leave: ")

        if user_input == "x":
            return

        for point in layout.points:
            if user_input == f"X{point.x}Y{point.y}":
                edit_point = point
                break

        if edit_point:
            break

    print(f"Editing connection point X{edit_point.x}Y{edit_point.y}")
    layout.layout_format[f"X{edit_point.x}Y{edit_point.y}"] = layout.layout_format[f"X{edit_point.x}Y{edit_point.y}"].replace("\033[1m\033[3m", "")
    layout.points.remove(edit_point)
    create_connection(layout)

def write_config(layout: FabricLayout, file_path = None):
    yaml.add_representer(FabricLayout, FabricLayout.to_yaml)
    yaml.add_representer(Slot, Slot.to_yaml)
    yaml.add_representer(Point, Point.to_yaml)

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
            print("Loading file failed. Size Mismatch")
            return

        # Load color
        layout.last_color = layout_config["Last Color"]

        # Load slots
        layout.slots.clear()
        for slot in layout_config["Slots"]:
            layout.slots.append(Slot(slot["Start"], slot["End"], slot["Name"], slot["Format"]))
        
        # Load Points
        layout.points.clear()
        for point in layout_config["Points"]:
            layout.points.append(Point(point["x"], point["y"]))

        # Load format
        for row in range(layout.height):
            for col in range(layout.length):
                layout.layout_format = layout_config["Format"]
    except KeyError:
        print("File has missing keys")
        return

def print_layout(layout: FabricLayout):
    # Slot overview
    for slot in layout.slots:
        first = 10 + slot.start*layout.tile_name_max_length
        last = first - 2 + (slot.end-slot.start+1)*layout.tile_name_max_length
        mid = first + int((last-first)/2)-4
        print(slot.format_ + " "*(first) + "|<" + " "*(mid-first) + slot.name + " "*(last-mid-len(slot.name)-2) + ">|\033[0m")

    # Table
    print("Row/Col | ", end='')
    for col in range(layout.length):
        print("%*.*s" % (-layout.tile_name_max_length, layout.tile_name_max_length, f"X{col:02}"), end='')

    print() # Newline
    print("-"*(10+layout.length*layout.tile_name_max_length))
    for row in range(layout.height):
        print("%-7.7s | " % (f"Y{row:02}"), end='')
        for col in range(layout.length):
            print(layout.layout_format[f"X{col}Y{row}"], end='')
            print("%*.*s" % (-layout.tile_name_max_length, layout.tile_name_max_length, layout.fabric.tile[row][col].name if layout.fabric.tile[row][col] else "NULL"), end='')
            print("\033[0m", end='')
        print()

def file_gen(layout: FabricLayout):
    print("hi")

def print_help():
    print("Help:")
    print("n for new slot or connection point")
    print("e to edit an existing slot or connection point")
    print("d to delete an existing slot or connection point")
    print("q to quit")
    print("p to view config")
    print("l to load/use another config")
    print("w to write the config")
    print("h for this help text")

def select_partition_connection(layout: FabricLayout, part_function, con_function):
    print("s for slot")
    print("c for connection point")
    while True:
        user_input = input("Select type: ")
        if user_input == "s":
            part_function(layout)
            break
        elif user_input == "c":
            con_function(layout)
            break

# Initialize the config structure
def init_config(layout: FabricLayout, config_path):
    fabulous_fabric = environ.get("FABULOUS_FABRIC", "../../fabric.csv")

    logger.disable("FABulous")
    fabric = parse_csv.parseFabricCSV("../../fabric.csv")

    layout.layout_format = dict.fromkeys([f"X{x%fabric.numberOfColumns}Y{int(x/fabric.numberOfColumns)}" for x in range(fabric.numberOfRows*fabric.numberOfColumns)], "")
    layout.height = fabric.numberOfRows
    layout.length = fabric.numberOfColumns
    layout.tile_name_max_length = len(max(fabric.tileDic, key=len))
    layout.fabric = fabric

    if config_path:
        load_config(layout, config_path)

# Interactivly partition slots
def slot_part(generate_files, config_path):
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
            select_partition_connection(fabric_layout, edit_partition, edit_connection)
        elif user_input == "d":
            select_partition_connection(fabric_layout, delete_partition, delete_connection)
        elif user_input == "p":
            print_layout(fabric_layout)
        elif user_input == "l":
            config_path = load_config(fabric_layout)
        elif user_input == "w":
            write_config(fabric_layout, config_path)
            if generate_files:
                file_gen(layout)
        elif user_input == "h":
            print_help()
        else:
            print("Command not found")
            print_help()


    fabulous_root = environ.get("FABULOUS_ROOT", "../../macro/ihp-sg13g2/fabulous")

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

    args = arg_parser.parse_args()

    if args.partition:
        slot_part(args.generate, args.file)
    elif args.generate:
        fabric_layout = FabricLayout()
        init_config(fabric_layout, args.file)
        file_gen(fabric_layout)

    print("Done")

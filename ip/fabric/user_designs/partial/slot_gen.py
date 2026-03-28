#!/usr/bin/env python

from os import environ
import argparse
import csv
import re
import yaml

from fasm import (
    parse_fasm_filename,
    fasm_tuple_to_string,
    parse_fasm_string,
    set_feature_to_str,
)

class Slot:
    start = 0
    end = 0
    slot_name = ""
    slot_format = ""

    def __init__(self, start, end, slot_name, slot_format):
        self.start       = start
        self.end         = end
        self.slot_name   = slot_name
        self.slot_format = slot_format

    @classmethod
    def to_yaml(cls, dumper, data):
        return dumper.represent_mapping("tag:yaml.org,2002:map",
                {"Start": data.start, "End": data.end, "Name": data.slot_name, "Format": data.slot_format})

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
    layout = list(list())
    layout_format = list(list())
    length = 0
    height = 0
    longest_tile_name = 6
    last_color = 0
    slots = list()
    connection_point = list()

    def getColorString(self): # Cycle colors 
        color = self.last_color+1
        self.last_color = color%6
        return f"\033[3{color}m"

    def createSlot(self, start, end, slot_name, slot_format=None):
        if slot_format:
            color = slot_format
        else:
            color = self.getColorString()
        
        for col in range(start, end+1):
            for row in range(self.height):
                self.layout_format[row][col] += color
        slot = Slot(start, end, slot_name, color)
        self.slots.append(slot)

    def stripSlot(self, slot):
        for col in range(slot.start, slot.end+1):
            for row in range(self.height):
                self.layout_format[row][col] = self.layout_format[row][col].replace(slot.slot_format, "")

        self.slots.remove(slot)

    @classmethod
    def to_yaml(cls, dumper, data):
        layout_format_dict = {}

        for row in range(len(data.layout_format)):
            for col in range(len(data.layout_format[row])):
                if data.layout_format[row][col]:
                    layout_format_dict[f"X{col}Y{row}"] = data.layout_format[row][col]

        return dumper.represent_mapping("tag:yaml.org,2002:map",
                {"Length": data.length, "Height": data.height, "Column Length": data.longest_tile_name, 
                 "Last Color": data.last_color, "Slots": data.slots, "Points": data.connection_point, "Format": layout_format_dict})

def create_partition(layout: FabricLayout):
    print("Slots can only be vertical")
    print("There can only be 1 static slot")
    while True:
        slot_type = input("Slot type (static/dynamic): ")
        if slot_type == "dynamic":
            slot_name = f"Slot{len(layout.slots):2}"
            break
        elif slot_type == "static":
            slot_name = f"Static"
            break

    for slot in layout.slots:
        if slot_name == slot.slot_name:
            print("This slot already exists, modify it with the e command")
            print()
            return

    first_column = int(input("First column: "))
    last_column = int(input("Last column: "))
    layout.createSlot(first_column, last_column, slot_name)
    print()

def delete_partition(layout: FabricLayout):
    while True:
        edit_slot = None
        user_input = input("Enter partition name to delete/Use x to leave: ")

        if user_input == "x":
            return

        for slot in layout.slots:
            if user_input == slot.slot_name:
                edit_slot = slot
                break

        if edit_slot:
            break

    print(f"Deleting slot {edit_slot.slot_name}")
    # Remove slot
    layout.stripSlot(edit_slot)

def edit_partition(layout: FabricLayout):
    while True:
        edit_slot = None
        user_input = input("Enter partition name to edit/Use x to leave: ")

        if user_input == "x":
            return

        for slot in layout.slots:
            if user_input == slot.slot_name:
                edit_slot = slot
                break

        if edit_slot:
            break

    print(f"Editing slot {edit_slot.slot_name}")
    print("Slots can only be vertical")
    # Remove slot
    layout.stripSlot(edit_slot)

    first_column = int(input("First column: "))
    last_column = int(input("Last column: "))
    layout.createSlot(first_column, last_column, edit_slot.slot_name, edit_slot.slot_format)
    print()

def create_connection(layout: FabricLayout):
    cell = input("Specify the slot connection point as X<x>Y<y> (Should be routed into a dynamic slot): ")
    slot_connection = [int(re.findall('[0-9]', x)[0]) for x in re.findall('X[0-9]+|Y[0-9]+', cell)]
    try:
        print(f"Added connection point at X{slot_connection[0]}Y{slot_connection[1]}")
    except:
        print()
        return

    layout.connection_point.append(Point(slot_connection[0], slot_connection[1]))
    layout.layout_format[slot_connection[1]][slot_connection[0]] += "\033[1m\033[3m"
    print()

def delete_connection(layout: FabricLayout):
    while True:
        edit_point = None
        user_input = input("Enter connection point to delete as XxYy/Use x to leave: ")

        if user_input == "x":
            return

        for point in layout.connection_point:
            if user_input == f"X{point.x}Y{point.y}":
                edit_point = point
                break

        if edit_point:
            break

    print(f"Deleting connection point X{edit_point.x}Y{point.y}")
    layout.layout_format[edit_point.y][edit_point.x] = layout.layout_format[edit_point.y][edit_point.x].replace("\033[1m\033[3m", "")
    layout.connection_point.remove(edit_point)
    
def edit_connection(layout: FabricLayout):
    while True:
        edit_point = None
        user_input = input("Enter connection point to edit as XxYy/Use x to leave: ")

        if user_input == "x":
            return

        for point in layout.connection_point:
            if user_input == f"X{point.x}Y{point.y}":
                edit_point = point
                break

        if edit_point:
            break

    print(f"Editing connection point X{edit_point.x}Y{edit_point.y}")
    layout.layout_format[edit_point.y][edit_point.x] = layout.layout_format[edit_point.y][edit_point.x].replace("\033[1m\033[3m", "")
    layout.connection_point.remove(edit_point)
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
        yaml.dump(fabric_layout, file, sort_keys=False)

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

    with open(file_path, 'r') as file:
        layout_config = yaml.safe_load(file)

    if layout.height != layout_config["Height"] or layout.length != layout_config["Length"] or layout.longest_tile_name != layout_config["Column Length"]:
        print("Loading file failed. Size Mismatch")
        return

    # Load color
    layout.last_color = layout_config["Last Color"]

    # Load slots
    layout.slots.clear()
    for slot in layout_config["Slots"]:
        layout.slots.append(Slot(slot["Start"], slot["End"], slot["Name"], slot["Format"]))
    
    # Load Points
    layout.connection_point.clear()
    for point in layout_config["Points"]:
        layout.connection_point.append(Point(point["x"], point["y"]))

    # Load format
    for row in range(layout.height):
        for col in range(layout.length):
            try:
                layout.layout_format[row][col] = layout_config["Format"][f"X{col}Y{row}"]
            except:
                layout.layout_format[row][col] = "\033[0m"

    #print(layout_config)

def print_layout(layout: FabricLayout):
    # Slot overview
    for slot in layout.slots:
        first = 10 + slot.start*layout.longest_tile_name
        last = first - 2 + (slot.end-slot.start+1)*layout.longest_tile_name
        mid = first + int((last-first)/2)-4
        print(slot.slot_format + " "*(first) + "|<" + " "*(mid-first) + slot.slot_name + " "*(last-mid-len(slot.slot_name)-2) + ">|\033[0m")

    # Table
    print("Row/Col | ", end='')
    for col in range(layout.length):
        print("%*.*s" % (-layout.longest_tile_name, layout.longest_tile_name, f"X{col:02}"), end='')

    print() # Newline
    print("-"*(10+layout.length*layout.longest_tile_name))
    for row in range(layout.height):
        print("%-7.7s | " % (f"Y{row:02}"), end='')
        for col in range(layout.length):
            if layout.layout_format[row][col] != "":
                print(layout.layout_format[row][col], end='')
                print("%*.*s" % (-layout.longest_tile_name, layout.longest_tile_name, layout.layout[row][col]), end='')
                print("\033[0m", end='')
            else:
                print("%*.*s" % (-layout.longest_tile_name, layout.longest_tile_name, layout.layout[row][col]), end='')
        print()

def print_help():
    print("Help:")
    print("n for new slot or connection point")
    print("e to edit an existing slot or connection point")
    print("d to delete an existing slot or connection point")
    print("q to quit")
    print("p to view config")
    print("l to load another config")
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

def slot_part(generate_files, config_path):
    # Partition eFPGA
    # Write static bel and pips
    fabulous_fabric = environ.get("FABULOUS_FABRIC", "../../fabric.csv")
    fabric_layout = FabricLayout()

    with open(fabulous_fabric, newline='') as fabric_file:
        fabric_layout_reader = csv.reader(fabric_file)
        read_fabric_layout = False
        for row in fabric_layout_reader:
            if (row[0] == "FabricBegin"):
                read_fabric_layout = True
                continue
            elif (row[0] == "FabricEnd"):
                break
            
            if read_fabric_layout:
                fabric_layout.layout.append(row)
                fabric_layout.layout_format.append([""]*len(row))
                fabric_layout.height = fabric_layout.height+1
                fabric_layout.length = max(fabric_layout.length, len(row))
                fabric_layout.longest_tile_name = max(fabric_layout.longest_tile_name, len(max(row, key=len)))

    if config_path:
        load_config(fabric_layout, config_path)

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
                print("hi")
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
    parser = argparse.ArgumentParser(description="Generate eFPGA Slots")
    parser.add_argument("-p", "--partition", action="store_true", help="Interactivly create partitioning")
    parser.add_argument("-g", "--generate", action="store_true", help="Generate bel and pips files")
    parser.add_argument("-f", "--file", help="Config file to use")

    args = parser.parse_args()

    if args.partition:
        slot_part(args.generate, args.file)
    elif args.generate:
        print("hi")

    print("Done")

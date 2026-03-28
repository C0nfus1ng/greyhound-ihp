# Paths
# FABULOUS_ROOT = ../../macro/ihp-sg13g2/fabulous
FABULOUS_ROOT = .build/static
EXTRA_PRIMITIVES_PATH = ../extra_primitives.v
BIT_GEN = ../bit_gen.py
BIT_TO_HEX = ../bit_to_hex.py

# Adjust sources
# RTL = top_wrapper.v partial.sv slot0.sv slot1.sv slot2.sv ../primitive_wrappers.v
RTL = ../top_wrapper.v static_slot.sv static_top.sv ../primitive_wrappers.v
TOP = top_wrapper
DESIGN_NAME = static

# Include base Makefile
include ../makefile.include

slot0-synth: RTL = slot0_wrapper.v slot0.sv ../primitive_wrappers.v
slot0-synth: TOP = slot0_wrapper
slot0-synth: DESIGN_NAME = slot0
slot0-synth: FABULOUS_ROOT = .build/slot0
slot0-synth: synth
.PHONY: slot0-synth

slot0-pnr: RTL = slot0_wrapper.v slot0.sv ../primitive_wrappers.v
slot0-pnr: TOP = slot0_wrapper
slot0-pnr: DESIGN_NAME = slot0
slot0-pnr: FABULOUS_ROOT = .build/slot0
slot0-pnr: pnr
.PHONY: slot0-pnr

slot0-bit: RTL = slot0_wrapper.v slot0.sv ../primitive_wrappers.v
slot0-bit: TOP = slot0_wrapper
slot0-bit: DESIGN_NAME = slot0
slot0-bit: FABULOUS_ROOT = .build/slot0
slot0-bit: bitstream hex
.PHONY: slot0-bit

slot1-pnr: RTL = slot1_wrapper.v slot1.sv ../primitive_wrappers.v
slot1-pnr: TOP = slot1_wrapper
slot1-pnr: DESIGN_NAME = slot1
slot1-pnr: FABULOUS_ROOT = .build/slot1
slot1-pnr: synth pnr
.PHONY: slot1-pnr

slot1-bit: RTL = slot1_wrapper.v slot1.sv ../primitive_wrappers.v
slot1-bit: TOP = slot1_wrapper
slot1-bit: DESIGN_NAME = slot1
slot1-bit: FABULOUS_ROOT = .build/slot1
slot1-bit: bitstream hex
.PHONY: slot1-bit
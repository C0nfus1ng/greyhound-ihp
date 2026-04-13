# Paths
EXTRA_PRIMITIVES_PATH = ../extra_primitives.v
BIT_GEN = ../bit_gen.py
BIT_TO_HEX = ../bit_to_hex.py
BASE_FOLDER = .build

# Adjust sources
static-fasm: RTL = ../top_wrapper.v .build/Static/Static_slot_con_X2Y1.v .build/Static/Static_slot_con_X4Y1.v  static_slot.sv static_top.sv ../primitive_wrappers.v
static-fasm: TOP = top_wrapper
static-fasm: SLOT_ROOT = Static
static-fasm: synth pnr
.PHONY: static-fasm

slot1-fasm: RTL = .build/Slot1/Slot1_slot_con_X2Y1.v slot1_wrapper.v slot1.sv ../primitive_wrappers.v
slot1-fasm: TOP = slot1_wrapper
slot1-fasm: SLOT_ROOT = Slot1
slot1-fasm: synth pnr
.PHONY: slot1-fasm

slot2-fasm: RTL = .build/Slot2/Slot2_slot_con_X4Y1.v slot2_wrapper.v slot2.sv ../primitive_wrappers.v
slot2-fasm: TOP = slot2_wrapper
slot2-fasm: SLOT_ROOT = Slot2
slot2-fasm: synth pnr
.PHONY: slot2-fasm

synth:
	yosys \
	-p \
	"synth_fabulous \
	-top $(TOP) \
	-json $(BASE_FOLDER)/$(SLOT_ROOT)/$(SLOT_ROOT).json \
	-lut 4 \
	-extra-plib $(EXTRA_PRIMITIVES_PATH)" \
	$(RTL)
.PHONY: synth

pnr:
	FAB_ROOT=$(BASE_FOLDER)/$(SLOT_ROOT)/ \
	nextpnr-generic \
	--uarch fabulous \
	--json $(BASE_FOLDER)/$(SLOT_ROOT)/$(SLOT_ROOT).json \
	-o fasm=$(BASE_FOLDER)/$(SLOT_ROOT)/$(SLOT_ROOT).fasm \
	--verbose \
	--log $(BASE_FOLDER)/$(SLOT_ROOT)/$(SLOT_ROOT)_log.txt \
	--timing-allow-fail
.PHONY: pnr

clean:
	rm -rf $(BASE_FOLDER)
.PHONY: clean

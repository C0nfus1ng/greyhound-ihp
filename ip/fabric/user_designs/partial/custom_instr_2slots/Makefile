# Paths
EXTRA_PRIMITIVES_PATH = ../../../../fabulous_fabric/fabric_ihp/user_designs/extra_primitives.v
BASE_FOLDER = .build
SLOT_GEN = ../slot_gen.py
SLOT_CONFIG = slot_config.yaml
FABRIC = ../../../../fabulous_fabric/fabric_ihp/fabric.csv
FASM_FILES = "Static=Static Slot1_2=Reverse,Interleave"

# Make all slots
all:
	@echo '------------------------------------------------------'
	@echo 'Generate static slot'
	@echo '------------------------------------------------------'
	@echo ''
	$(MAKE) static-gen

	@echo ''
	@echo '------------------------------------------------------'
	@echo 'Generate static fasm file'
	@echo '------------------------------------------------------'
	@echo ''
	$(MAKE) static-fasm

	@echo ''
	@echo '------------------------------------------------------'
	@echo 'Generate dynamic slot'
	@echo '------------------------------------------------------'
	@echo ''
	@$(MAKE) dynamic-gen

	@echo ''
	@echo '------------------------------------------------------'
	@echo 'Generate Slot1_2 reverse fasm file'
	@echo '------------------------------------------------------'
	@echo ''
	$(MAKE) slot1_2-reverse-fasm

	@echo ''
	@echo '------------------------------------------------------'
	@echo 'Generate Slot1_2 interleave fasm file'
	@echo '------------------------------------------------------'
	@echo ''
	$(MAKE) slot1_2-interleave-fasm

	@echo ''
	@echo '------------------------------------------------------'
	@echo 'Generate bitstreams'
	@echo '------------------------------------------------------'
	@echo ''
	$(MAKE) bit-gen
.PHONY: all

# Slot sources
static-fasm: RTL = static_slot.sv io_wrapper.sv ../../../../fabulous_fabric/fabric_ihp/user_designs/primitive_wrappers.v \
					.build/Static/Static_slot_con_X1Y7.v .build/Static/Static_slot_con_X3Y7.v
static-fasm: TOP = static_slot
static-fasm: SLOT_ROOT = Static
static-fasm: PROG_ROOT = Static
static-fasm: synth pnr
.PHONY: static-fasm

slot1_2-reverse-fasm: RTL = slot1_2_wrapper.sv slot1_2_reverse.sv ../../../../fabulous_fabric/fabric_ihp/user_designs/primitive_wrappers.v \
							.build/Slot1_2/Slot1_2_slot_con_X1Y7.v
slot1_2-reverse-fasm: TOP = slot1_2_reverse
slot1_2-reverse-fasm: SLOT_ROOT = Slot1_2
slot1_2-reverse-fasm: PROG_ROOT = Reverse
slot1_2-reverse-fasm: synth pnr
.PHONY: slot1_2-reverse-fasm

slot1_2-interleave-fasm: RTL = slot1_2_wrapper.sv slot1_2_interleave.sv ../../../../fabulous_fabric/fabric_ihp/user_designs/primitive_wrappers.v \
							.build/Slot1_2/Slot1_2_slot_con_X1Y7.v
slot1_2-interleave-fasm: TOP = slot1_2_interleave
slot1_2-interleave-fasm: SLOT_ROOT = Slot1_2
slot1_2-interleave-fasm: PROG_ROOT = Interleave
slot1_2-interleave-fasm: synth pnr
.PHONY: slot1_2-interleave-fasm

# Helper functions
static-gen:
	python3 $(SLOT_GEN) -gsf $(SLOT_CONFIG) --basedir $(BASE_FOLDER) --fabric $(FABRIC)
.PHONY: static-gen

dynamic-gen:
	python3 $(SLOT_GEN) -gf $(SLOT_CONFIG) --basedir $(BASE_FOLDER) --fabric $(FABRIC)
.PHONY: dynamic-gen

bit-gen:
	python3 $(SLOT_GEN) -cbf $(SLOT_CONFIG) --basedir $(BASE_FOLDER) --fabric $(FABRIC) --fasm $(FASM_FILES)
.PHONY: bit-gen

open-config:
	python3 $(SLOT_GEN) -if $(SLOT_CONFIG) --basedir $(BASE_FOLDER) --fabric $(FABRIC) --fasm $(FASM_FILES)
.PHONY: open-config

show-config:
	@echo 'q' | python3 $(SLOT_GEN) -if $(SLOT_CONFIG) --basedir $(BASE_FOLDER) --fabric $(FABRIC) --fasm $(FASM_FILES)
.PHONY: show-config

synth:
	yosys \
	-p \
	"synth_fabulous \
	-top $(TOP) \
	-json $(BASE_FOLDER)/$(SLOT_ROOT)/$(PROG_ROOT).json \
	-lut 4 \
	-extra-plib $(EXTRA_PRIMITIVES_PATH)" \
	$(RTL)
.PHONY: synth

pnr:
	FAB_ROOT=$(BASE_FOLDER)/$(SLOT_ROOT)/ \
	nextpnr-generic \
	--uarch fabulous \
	--json $(BASE_FOLDER)/$(SLOT_ROOT)/$(PROG_ROOT).json \
	-o fasm=$(BASE_FOLDER)/$(SLOT_ROOT)/$(PROG_ROOT).fasm \
	--verbose \
	--log $(BASE_FOLDER)/$(SLOT_ROOT)/$(PROG_ROOT)_log.txt \
	--timing-allow-fail
.PHONY: pnr

clean:
	rm -rf $(BASE_FOLDER)
.PHONY: clean

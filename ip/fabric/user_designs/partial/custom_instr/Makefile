# Paths
EXTRA_PRIMITIVES_PATH = ../../extra_primitives.v
BASE_FOLDER = .build
SLOT_GEN = ../slot_gen.py
SLOT_CONFIG = slot_config.yaml
FABRIC = ../../../fabric.csv
FASM_FILES = ""

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
	@echo 'Generate Slot3 straight through fasm file'
	@echo '------------------------------------------------------'
	@echo ''
	$(MAKE) slot3-straight-through-fasm

	@echo ''
	@echo '------------------------------------------------------'
	@echo 'Generate Slot3 crossover fasm file'
	@echo '------------------------------------------------------'
	@echo ''
	$(MAKE) slot3-crossover-fasm

	@echo ''
	@echo '------------------------------------------------------'
	@echo 'Generate bitstreams'
	@echo '------------------------------------------------------'
	@echo ''
	$(MAKE) bit-gen
.PHONY: all

# Slot sources
static-fasm: RTL = static_slot.sv ../../primitive_wrappers.v \
					.build/Static/Static_slot_con_X2Y1.v .build/Static/Static_slot_con_X2Y2.v .build/Static/Static_slot_con_X2Y3.v .build/Static/Static_slot_con_X2Y4.v .build/Static/Static_slot_con_X2Y5.v .build/Static/Static_slot_con_X2Y6.v .build/Static/Static_slot_con_X2Y7.v .build/Static/Static_slot_con_X2Y8.v \
					.build/Static/Static_slot_con_X4Y1.v .build/Static/Static_slot_con_X4Y2.v .build/Static/Static_slot_con_X4Y3.v .build/Static/Static_slot_con_X4Y4.v .build/Static/Static_slot_con_X4Y5.v .build/Static/Static_slot_con_X4Y6.v .build/Static/Static_slot_con_X4Y7.v .build/Static/Static_slot_con_X4Y8.v \
					.build/Static/Static_slot_con_X8Y1.v
static-fasm: TOP = static_slot
static-fasm: SLOT_ROOT = Static
static-fasm: PROG_ROOT = Static
static-fasm: synth pnr
.PHONY: static-fasm

slot3-straight-through-fasm: RTL = slot3_wrapper.sv io_wrapper.sv slot3_straight_through.sv \
									.build/Slot3/Slot3_slot_con_X2Y1.v .build/Slot3/Slot3_slot_con_X2Y2.v .build/Slot3/Slot3_slot_con_X2Y3.v .build/Slot3/Slot3_slot_con_X2Y4.v .build/Slot3/Slot3_slot_con_X2Y5.v .build/Slot3/Slot3_slot_con_X2Y6.v .build/Slot3/Slot3_slot_con_X2Y7.v .build/Slot3/Slot3_slot_con_X2Y8.v
slot3-straight-through-fasm: TOP = slot3_straight_through
slot3-straight-through-fasm: SLOT_ROOT = Slot3
slot3-straight-through-fasm: PROG_ROOT = StraightThrough
slot3-straight-through-fasm: synth pnr
.PHONY: slot3-straight-through-fasm

slot3-crossover-fasm: RTL = slot3_wrapper.sv io_wrapper.sv slot3_crossover.sv \
								.build/Slot3/Slot3_slot_con_X2Y1.v .build/Slot3/Slot3_slot_con_X2Y2.v .build/Slot3/Slot3_slot_con_X2Y3.v .build/Slot3/Slot3_slot_con_X2Y4.v .build/Slot3/Slot3_slot_con_X2Y5.v .build/Slot3/Slot3_slot_con_X2Y6.v .build/Slot3/Slot3_slot_con_X2Y7.v .build/Slot3/Slot3_slot_con_X2Y8.v
slot3-crossover-fasm: TOP = slot3_straight_through
slot3-crossover-fasm: SLOT_ROOT = Slot3
slot3-crossover-fasm: PROG_ROOT = Crossover
slot3-crossover-fasm: synth pnr
.PHONY: slot3-crossover-fasm

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

# Paths
EXTRA_PRIMITIVES_PATH = ../extra_primitives.v
BASE_FOLDER = .build
SLOT_GEN = slot_gen.py
SLOT_CONFIG = slot_config.yaml
FABRIC = ../../fabric.csv

# Make all slots
all:
	@echo '---------------------------'
	@echo 'Generate static slot'
	@echo '---------------------------'
	@echo ''
	$(MAKE) static-gen

	@echo ''
	@echo '---------------------------'
	@echo 'Generate static fasm file'
	@echo '---------------------------'
	@echo ''
	$(MAKE) static-fasm

	@echo ''
	@echo '---------------------------'
	@echo 'Generate dynamic slot'
	@echo '---------------------------'
	@echo ''
	@$(MAKE) dynamic-gen
	
	$(MAKE) slot1-fasm-wrapper
	$(MAKE) slot2-fasm-wrapper

	@echo ''
	@echo '---------------------------'
	@echo 'Generate bitstreams'
	@echo '---------------------------'
	@echo ''
	$(MAKE) bit-gen
.PHONY: all

# Slot sources
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

slot1-fasm-wrapper slot2-fasm-wrapper: slot%-fasm-wrapper:
	@echo ''
	@echo '---------------------------'
	@echo 'Generate dynamic fasm file'
	@echo '---------------------------'
	@echo ''
	$(MAKE) slot$*-fasm
.PHONY: slot%-fasm-wrapper

# Helper functions
static-gen:
	python3 slot_gen.py -gsf $(SLOT_CONFIG) --basedir $(BASE_FOLDER) --fabric $(FABRIC)
.PHONY: static-gen

dynamic-gen:
	python3 slot_gen.py -gf $(SLOT_CONFIG) --basedir $(BASE_FOLDER) --fabric $(FABRIC)
.PHONY: dynamic-gen

bit-gen:
	python3 slot_gen.py -cbf $(SLOT_CONFIG) --basedir $(BASE_FOLDER) --fabric $(FABRIC)
.PHONY: bit-gen

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

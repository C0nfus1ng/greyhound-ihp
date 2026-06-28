# Paths
EXTRA_PRIMITIVES_PATH = ../../../../fabulous_fabric/fabric_ihp/user_designs/extra_primitives.v
BASE_FOLDER_PERIPHERAL = .build_peripheral
BASE_FOLDER_XIF = .build_xif 
SLOT_GEN = ../slot_gen.py
SLOT_CONFIG = slot_config.yaml
FABRIC = ../../../../fabulous_fabric/fabric_ihp/fabric.csv
FASM_FILES = Static=Peripheral
BOARD = board

# Make all slots
all:
	@echo '------------------------------------------------------'
	@echo 'Generate peripheral'
	@echo '------------------------------------------------------'
	@echo ''
	$(MAKE) peripheral-gen

	@echo '------------------------------------------------------'
	@echo 'Generate xif'
	@echo '------------------------------------------------------'
	@echo ''
	$(MAKE) xif-gen

	@echo ''
	@echo '------------------------------------------------------'
	@echo 'Generate peripheral fasm file'
	@echo '------------------------------------------------------'
	@echo ''
	$(MAKE) peripheral-fasm -e BASE_FOLDER=$(BASE_FOLDER_PERIPHERAL)

	@echo ''
	@echo '------------------------------------------------------'
	@echo 'Generate xif fasm file'
	@echo '------------------------------------------------------'
	@echo ''
	$(MAKE) xif-fasm -e BASE_FOLDER=$(BASE_FOLDER_XIF)

	@echo ''
	@echo '------------------------------------------------------'
	@echo 'Generate bitstreams'
	@echo '------------------------------------------------------'
	@echo ''
	$(MAKE) bit-gen
	$(MAKE) bit-gen -e FASM_FILES=Static=Xif BASE_FOLDER=$(BASE_FOLDER_XIF)

	@echo ''
	@echo '------------------------------------------------------'
	@echo 'Copy bitstreams into destination'
	@echo '------------------------------------------------------'
	@echo ''
	$(MAKE) board
	$(MAKE) board -e FASM_FILES=Static=Xif BASE_FOLDER=$(BASE_FOLDER_XIF)
.PHONY: all

# Slot sources
peripheral-fasm: RTL = peripheral.sv io_wrapper.sv ../../../../fabulous_fabric/fabric_ihp/user_designs/primitive_wrappers.v
peripheral-fasm: TOP = peripheral
peripheral-fasm: SLOT_ROOT = Static
peripheral-fasm: PROG_ROOT = Peripheral
peripheral-fasm: synth pnr
.PHONY: peripheral-fasm

xif-fasm: RTL = xif.sv io_wrapper.sv ../../../../fabulous_fabric/fabric_ihp/user_designs/primitive_wrappers.v
xif-fasm: TOP = xif
xif-fasm: SLOT_ROOT = Static
xif-fasm: PROG_ROOT = Xif
xif-fasm: synth pnr
.PHONY: xif-fasm

# Helper functions
peripheral-gen:
	python3 $(SLOT_GEN) -gsf $(SLOT_CONFIG) --basedir $(BASE_FOLDER_PERIPHERAL) --fabric $(FABRIC)
.PHONY: peripheral-gen

xif-gen:
	python3 $(SLOT_GEN) -gsf $(SLOT_CONFIG) --basedir $(BASE_FOLDER_XIF) --fabric $(FABRIC)
.PHONY: xif-gen

bit-gen: BASE_FOLDER = $(BASE_FOLDER_PERIPHERAL)
bit-gen:
	python3 $(SLOT_GEN) -cbf $(SLOT_CONFIG) --basedir $(BASE_FOLDER) --fabric $(FABRIC) --fasm "$(FASM_FILES)"
.PHONY: bit-gen

open-config: BASE_FOLDER = $(BASE_FOLDER_PERIPHERAL)
open-config:
	python3 $(SLOT_GEN) -if $(SLOT_CONFIG) --basedir $(BASE_FOLDER) --fabric $(FABRIC) --fasm "$(FASM_FILES)"
.PHONY: open-config

show-config: BASE_FOLDER = $(BASE_FOLDER_PERIPHERAL)
show-config:
	@echo 'q' | python3 $(SLOT_GEN) -if $(SLOT_CONFIG) --basedir $(BASE_FOLDER) --fabric $(FABRIC) --fasm "$(FASM_FILES)"
.PHONY: show-config

synth: BASE_FOLDER = $(BASE_FOLDER_PERIPHERAL)
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

pnr: BASE_FOLDER = $(BASE_FOLDER_PERIPHERAL)
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
	rm -rf $(BASE_FOLDER_PERIPHERAL)
	rm -rf $(BASE_FOLDER_XIF)
.PHONY: clean

board: BASE_FOLDER = $(BASE_FOLDER_PERIPHERAL)
board: # Parse config param and copy wanted files in priority order to board dir
	mkdir -p $(BOARD)/bitstreams; \
	for pair in $(FASM_FILES); do \
		folder=$$(printf '%s' "$$pair" | cut -d= -f1); \
		files=$$(printf '%s' "$$pair" | cut -d= -f2-); \
		for file in $$(printf '%s' "$$files" | tr ',' '\n'); do \
			for suffix in -slot-dedup -slot -dedup ""; do \
				if [ -f "$(BASE_FOLDER)/$$folder/$$file$$suffix.bit" ]; then \
					bitstream="$(BASE_FOLDER)/$$folder/$$file$$suffix.bit"; \
					break; \
				fi; \
			done; \
			if [ -z "$$bitstream" ]; then \
				echo "No source file found for $(BASE_FOLDER)/$$folder/$$file"; \
				exit 1; \
			fi; \
			echo "Copy $$bitstream into $(BOARD)/bitstreams/$$file.bit"; \
 			cp "$$bitstream" "$(BOARD)/bitstreams/$$file.bit"; \
		done; \
	done; \
	if [ -f "$(BASE_FOLDER)/Static/Static.bit" ]; then \
		echo "Copy $(BASE_FOLDER)/Static/Static.bit into $(BOARD)/bitstreams/Static-full.bit"; \
		cp "$(BASE_FOLDER)/Static/Static.bit" "$(BOARD)/bitstreams/Static-full.bit"; \
	fi ;
.PHONY: board

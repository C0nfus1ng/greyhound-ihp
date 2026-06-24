# Paths
EXTRA_PRIMITIVES_PATH = ../../../../fabulous_fabric/fabric_ihp/user_designs/extra_primitives.v
BASE_FOLDER = .build
SLOT_GEN = ../slot_gen.py
SLOT_CONFIG = slot_config.yaml
FABRIC = ../../../../fabulous_fabric/fabric_ihp/fabric.csv
FASM_FILES = Static=Static Slot1=Graycode,DirectOut,Crossover,Stage Slot2=XifLeftRoll,XifRightRoll,Peripheral,Counter
BOARD = board

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
	@echo 'Generate Slot1 graycode fasm file'
	@echo '------------------------------------------------------'
	@echo ''
	$(MAKE) slot1-graycode-fasm

	@echo ''
	@echo '------------------------------------------------------'
	@echo 'Generate Slot1 direct out fasm file'
	@echo '------------------------------------------------------'
	@echo ''
	$(MAKE) slot1-direct-out-fasm

	@echo ''
	@echo '------------------------------------------------------'
	@echo 'Generate Slot1 crossover fasm file'
	@echo '------------------------------------------------------'
	@echo ''
	$(MAKE) slot1-crossover-fasm

	@echo ''
	@echo '------------------------------------------------------'
	@echo 'Generate Slot1 stage fasm file'
	@echo '------------------------------------------------------'
	@echo ''
	$(MAKE) slot1-stage-fasm

	@echo ''
	@echo '------------------------------------------------------'
	@echo 'Generate Slot2 xif left roll fasm file'
	@echo '------------------------------------------------------'
	@echo ''
	$(MAKE) slot2-xif-left-roll-fasm

	@echo ''
	@echo '------------------------------------------------------'
	@echo 'Generate Slot2 xif right roll fasm file'
	@echo '------------------------------------------------------'
	@echo ''
	$(MAKE) slot2-xif-right-roll-fasm

	@echo ''
	@echo '------------------------------------------------------'
	@echo 'Generate Slot2 peripheral fasm file'
	@echo '------------------------------------------------------'
	@echo ''
	$(MAKE) slot2-peripheral-fasm

	@echo ''
	@echo '------------------------------------------------------'
	@echo 'Generate Slot2 counter fasm file'
	@echo '------------------------------------------------------'
	@echo ''
	$(MAKE) slot2-counter-fasm

	@echo ''
	@echo '------------------------------------------------------'
	@echo 'Generate bitstreams'
	@echo '------------------------------------------------------'
	@echo ''
	$(MAKE) bit-gen

	@echo ''
	@echo '------------------------------------------------------'
	@echo 'Copy bitstreams into destination'
	@echo '------------------------------------------------------'
	@echo ''
	$(MAKE) board
.PHONY: all

# Slot sources
static-fasm: RTL = static_slot.sv ../../../../fabulous_fabric/fabric_ihp/user_designs/primitive_wrappers.v \
					$(BASE_FOLDER)/Static/Static_slot_con_X3Y1.v $(BASE_FOLDER)/Static/Static_slot_con_X3Y2.v $(BASE_FOLDER)/Static/Static_slot_con_X3Y3.v $(BASE_FOLDER)/Static/Static_slot_con_X3Y4.v $(BASE_FOLDER)/Static/Static_slot_con_X3Y5.v $(BASE_FOLDER)/Static/Static_slot_con_X3Y6.v $(BASE_FOLDER)/Static/Static_slot_con_X3Y7.v $(BASE_FOLDER)/Static/Static_slot_con_X3Y8.v $(BASE_FOLDER)/Static/Static_slot_con_X3Y9.v $(BASE_FOLDER)/Static/Static_slot_con_X3Y10.v $(BASE_FOLDER)/Static/Static_slot_con_X3Y11.v $(BASE_FOLDER)/Static/Static_slot_con_X3Y12.v $(BASE_FOLDER)/Static/Static_slot_con_X3Y13.v \
					$(BASE_FOLDER)/Static/Static_slot_con_X4Y1.v $(BASE_FOLDER)/Static/Static_slot_con_X4Y2.v $(BASE_FOLDER)/Static/Static_slot_con_X4Y3.v $(BASE_FOLDER)/Static/Static_slot_con_X4Y4.v $(BASE_FOLDER)/Static/Static_slot_con_X4Y5.v $(BASE_FOLDER)/Static/Static_slot_con_X4Y6.v $(BASE_FOLDER)/Static/Static_slot_con_X4Y7.v $(BASE_FOLDER)/Static/Static_slot_con_X4Y8.v $(BASE_FOLDER)/Static/Static_slot_con_X4Y9.v $(BASE_FOLDER)/Static/Static_slot_con_X4Y10.v $(BASE_FOLDER)/Static/Static_slot_con_X4Y11.v $(BASE_FOLDER)/Static/Static_slot_con_X4Y12.v $(BASE_FOLDER)/Static/Static_slot_con_X4Y13.v
static-fasm: TOP = static_slot
static-fasm: SLOT_ROOT = Static
static-fasm: PROG_ROOT = Static
static-fasm: synth pnr
.PHONY: static-fasm

slot1-graycode-fasm: RTL = slot1_wrapper.sv io_wrapper.sv slot1_graycode.sv ../../../../fabulous_fabric/fabric_ihp/user_designs/primitive_wrappers.v \
							$(BASE_FOLDER)/Slot1/Slot1_slot_con_X3Y1.v $(BASE_FOLDER)/Slot1/Slot1_slot_con_X3Y2.v $(BASE_FOLDER)/Slot1/Slot1_slot_con_X3Y3.v $(BASE_FOLDER)/Slot1/Slot1_slot_con_X3Y4.v $(BASE_FOLDER)/Slot1/Slot1_slot_con_X3Y5.v $(BASE_FOLDER)/Slot1/Slot1_slot_con_X3Y6.v $(BASE_FOLDER)/Slot1/Slot1_slot_con_X3Y7.v $(BASE_FOLDER)/Slot1/Slot1_slot_con_X3Y8.v $(BASE_FOLDER)/Slot1/Slot1_slot_con_X3Y9.v $(BASE_FOLDER)/Slot1/Slot1_slot_con_X3Y10.v $(BASE_FOLDER)/Slot1/Slot1_slot_con_X3Y11.v $(BASE_FOLDER)/Slot1/Slot1_slot_con_X3Y12.v $(BASE_FOLDER)/Slot1/Slot1_slot_con_X3Y13.v
slot1-graycode-fasm: TOP = slot1_graycode
slot1-graycode-fasm: SLOT_ROOT = Slot1
slot1-graycode-fasm: PROG_ROOT = Graycode
slot1-graycode-fasm: synth pnr
.PHONY: slot1-graycode-fasm

slot1-direct-out-fasm: RTL = slot1_wrapper.sv io_wrapper.sv slot1_direct_out.sv ../../../../fabulous_fabric/fabric_ihp/user_designs/primitive_wrappers.v \
							$(BASE_FOLDER)/Slot1/Slot1_slot_con_X3Y1.v $(BASE_FOLDER)/Slot1/Slot1_slot_con_X3Y2.v $(BASE_FOLDER)/Slot1/Slot1_slot_con_X3Y3.v $(BASE_FOLDER)/Slot1/Slot1_slot_con_X3Y4.v $(BASE_FOLDER)/Slot1/Slot1_slot_con_X3Y5.v $(BASE_FOLDER)/Slot1/Slot1_slot_con_X3Y6.v $(BASE_FOLDER)/Slot1/Slot1_slot_con_X3Y7.v $(BASE_FOLDER)/Slot1/Slot1_slot_con_X3Y8.v $(BASE_FOLDER)/Slot1/Slot1_slot_con_X3Y9.v $(BASE_FOLDER)/Slot1/Slot1_slot_con_X3Y10.v $(BASE_FOLDER)/Slot1/Slot1_slot_con_X3Y11.v $(BASE_FOLDER)/Slot1/Slot1_slot_con_X3Y12.v $(BASE_FOLDER)/Slot1/Slot1_slot_con_X3Y13.v
slot1-direct-out-fasm: TOP = slot1_direct_out
slot1-direct-out-fasm: SLOT_ROOT = Slot1
slot1-direct-out-fasm: PROG_ROOT = DirectOut
slot1-direct-out-fasm: synth pnr
.PHONY: slot1-direct-out-fasm

slot1-crossover-fasm: RTL = slot1_wrapper.sv io_wrapper.sv slot1_crossover.sv  ../../../../fabulous_fabric/fabric_ihp/user_designs/primitive_wrappers.v \
							$(BASE_FOLDER)/Slot1/Slot1_slot_con_X3Y1.v $(BASE_FOLDER)/Slot1/Slot1_slot_con_X3Y2.v $(BASE_FOLDER)/Slot1/Slot1_slot_con_X3Y3.v $(BASE_FOLDER)/Slot1/Slot1_slot_con_X3Y4.v $(BASE_FOLDER)/Slot1/Slot1_slot_con_X3Y5.v $(BASE_FOLDER)/Slot1/Slot1_slot_con_X3Y6.v $(BASE_FOLDER)/Slot1/Slot1_slot_con_X3Y7.v $(BASE_FOLDER)/Slot1/Slot1_slot_con_X3Y8.v $(BASE_FOLDER)/Slot1/Slot1_slot_con_X3Y9.v $(BASE_FOLDER)/Slot1/Slot1_slot_con_X3Y10.v $(BASE_FOLDER)/Slot1/Slot1_slot_con_X3Y11.v $(BASE_FOLDER)/Slot1/Slot1_slot_con_X3Y12.v $(BASE_FOLDER)/Slot1/Slot1_slot_con_X3Y13.v
slot1-crossover-fasm: TOP = slot1_crossover
slot1-crossover-fasm: SLOT_ROOT = Slot1
slot1-crossover-fasm: PROG_ROOT = Crossover
slot1-crossover-fasm: synth pnr
.PHONY: slot1-crossover-fasm

slot1-stage-fasm: RTL = slot1_wrapper.sv io_wrapper.sv slot1_stage.sv ../../../../fabulous_fabric/fabric_ihp/user_designs/primitive_wrappers.v \
							$(BASE_FOLDER)/Slot1/Slot1_slot_con_X3Y1.v $(BASE_FOLDER)/Slot1/Slot1_slot_con_X3Y2.v $(BASE_FOLDER)/Slot1/Slot1_slot_con_X3Y3.v $(BASE_FOLDER)/Slot1/Slot1_slot_con_X3Y4.v $(BASE_FOLDER)/Slot1/Slot1_slot_con_X3Y5.v $(BASE_FOLDER)/Slot1/Slot1_slot_con_X3Y6.v $(BASE_FOLDER)/Slot1/Slot1_slot_con_X3Y7.v $(BASE_FOLDER)/Slot1/Slot1_slot_con_X3Y8.v $(BASE_FOLDER)/Slot1/Slot1_slot_con_X3Y9.v $(BASE_FOLDER)/Slot1/Slot1_slot_con_X3Y10.v $(BASE_FOLDER)/Slot1/Slot1_slot_con_X3Y11.v $(BASE_FOLDER)/Slot1/Slot1_slot_con_X3Y12.v $(BASE_FOLDER)/Slot1/Slot1_slot_con_X3Y13.v
slot1-stage-fasm: TOP = slot1_stage
slot1-stage-fasm: SLOT_ROOT = Slot1
slot1-stage-fasm: PROG_ROOT = Stage
slot1-stage-fasm: synth pnr
.PHONY: slot1-stage-fasm

slot2-xif-left-roll-fasm: RTL = slot2_wrapper.sv slot2_xif_left_roll.sv ../../../../fabulous_fabric/fabric_ihp/user_designs/primitive_wrappers.v \
							$(BASE_FOLDER)/Slot2/Slot2_slot_con_X4Y1.v $(BASE_FOLDER)/Slot2/Slot2_slot_con_X4Y2.v $(BASE_FOLDER)/Slot2/Slot2_slot_con_X4Y3.v $(BASE_FOLDER)/Slot2/Slot2_slot_con_X4Y4.v $(BASE_FOLDER)/Slot2/Slot2_slot_con_X4Y5.v $(BASE_FOLDER)/Slot2/Slot2_slot_con_X4Y6.v $(BASE_FOLDER)/Slot2/Slot2_slot_con_X4Y7.v $(BASE_FOLDER)/Slot2/Slot2_slot_con_X4Y8.v $(BASE_FOLDER)/Slot2/Slot2_slot_con_X4Y9.v $(BASE_FOLDER)/Slot2/Slot2_slot_con_X4Y10.v $(BASE_FOLDER)/Slot2/Slot2_slot_con_X4Y11.v $(BASE_FOLDER)/Slot2/Slot2_slot_con_X4Y12.v $(BASE_FOLDER)/Slot2/Slot2_slot_con_X4Y13.v
slot2-xif-left-roll-fasm: TOP = slot2_xif_left_roll
slot2-xif-left-roll-fasm: SLOT_ROOT = Slot2
slot2-xif-left-roll-fasm: PROG_ROOT = XifLeftRoll
slot2-xif-left-roll-fasm: synth pnr
.PHONY: slot2-xif-left-roll-fasm

slot2-xif-right-roll-fasm: RTL = slot2_wrapper.sv slot2_xif_right_roll.sv ../../../../fabulous_fabric/fabric_ihp/user_designs/primitive_wrappers.v \
							$(BASE_FOLDER)/Slot2/Slot2_slot_con_X4Y1.v $(BASE_FOLDER)/Slot2/Slot2_slot_con_X4Y2.v $(BASE_FOLDER)/Slot2/Slot2_slot_con_X4Y3.v $(BASE_FOLDER)/Slot2/Slot2_slot_con_X4Y4.v $(BASE_FOLDER)/Slot2/Slot2_slot_con_X4Y5.v $(BASE_FOLDER)/Slot2/Slot2_slot_con_X4Y6.v $(BASE_FOLDER)/Slot2/Slot2_slot_con_X4Y7.v $(BASE_FOLDER)/Slot2/Slot2_slot_con_X4Y8.v $(BASE_FOLDER)/Slot2/Slot2_slot_con_X4Y9.v $(BASE_FOLDER)/Slot2/Slot2_slot_con_X4Y10.v $(BASE_FOLDER)/Slot2/Slot2_slot_con_X4Y11.v $(BASE_FOLDER)/Slot2/Slot2_slot_con_X4Y12.v $(BASE_FOLDER)/Slot2/Slot2_slot_con_X4Y13.v
slot2-xif-right-roll-fasm: TOP = slot2_xif_right_roll
slot2-xif-right-roll-fasm: SLOT_ROOT = Slot2
slot2-xif-right-roll-fasm: PROG_ROOT = XifRightRoll
slot2-xif-right-roll-fasm: synth pnr
.PHONY: slot2-xif-right-roll-fasm

slot2-peripheral-fasm: RTL = slot2_wrapper.sv slot2_peripheral.sv ../../../../fabulous_fabric/fabric_ihp/user_designs/primitive_wrappers.v \
							$(BASE_FOLDER)/Slot2/Slot2_slot_con_X4Y1.v $(BASE_FOLDER)/Slot2/Slot2_slot_con_X4Y2.v $(BASE_FOLDER)/Slot2/Slot2_slot_con_X4Y3.v $(BASE_FOLDER)/Slot2/Slot2_slot_con_X4Y4.v $(BASE_FOLDER)/Slot2/Slot2_slot_con_X4Y5.v $(BASE_FOLDER)/Slot2/Slot2_slot_con_X4Y6.v $(BASE_FOLDER)/Slot2/Slot2_slot_con_X4Y7.v $(BASE_FOLDER)/Slot2/Slot2_slot_con_X4Y8.v $(BASE_FOLDER)/Slot2/Slot2_slot_con_X4Y9.v $(BASE_FOLDER)/Slot2/Slot2_slot_con_X4Y10.v $(BASE_FOLDER)/Slot2/Slot2_slot_con_X4Y11.v $(BASE_FOLDER)/Slot2/Slot2_slot_con_X4Y12.v $(BASE_FOLDER)/Slot2/Slot2_slot_con_X4Y13.v
slot2-peripheral-fasm: TOP = slot2_peripheral
slot2-peripheral-fasm: SLOT_ROOT = Slot2
slot2-peripheral-fasm: PROG_ROOT = Peripheral
slot2-peripheral-fasm: synth pnr
.PHONY: slot2-peripheral-fasm

slot2-counter-fasm: RTL = slot2_wrapper.sv slot2_counter.sv ../../../../fabulous_fabric/fabric_ihp/user_designs/primitive_wrappers.v \
							$(BASE_FOLDER)/Slot2/Slot2_slot_con_X4Y1.v $(BASE_FOLDER)/Slot2/Slot2_slot_con_X4Y2.v $(BASE_FOLDER)/Slot2/Slot2_slot_con_X4Y3.v $(BASE_FOLDER)/Slot2/Slot2_slot_con_X4Y4.v $(BASE_FOLDER)/Slot2/Slot2_slot_con_X4Y5.v $(BASE_FOLDER)/Slot2/Slot2_slot_con_X4Y6.v $(BASE_FOLDER)/Slot2/Slot2_slot_con_X4Y7.v $(BASE_FOLDER)/Slot2/Slot2_slot_con_X4Y8.v $(BASE_FOLDER)/Slot2/Slot2_slot_con_X4Y9.v $(BASE_FOLDER)/Slot2/Slot2_slot_con_X4Y10.v $(BASE_FOLDER)/Slot2/Slot2_slot_con_X4Y11.v $(BASE_FOLDER)/Slot2/Slot2_slot_con_X4Y12.v $(BASE_FOLDER)/Slot2/Slot2_slot_con_X4Y13.v
slot2-counter-fasm: TOP = slot2_counter
slot2-counter-fasm: SLOT_ROOT = Slot2
slot2-counter-fasm: PROG_ROOT = Counter
slot2-counter-fasm: synth pnr
.PHONY: slot2-counter-fasm

# Helper functions
static-gen:
	python3 $(SLOT_GEN) -gsf $(SLOT_CONFIG) --basedir $(BASE_FOLDER) --fabric $(FABRIC)
.PHONY: static-gen

dynamic-gen:
	python3 $(SLOT_GEN) -gf $(SLOT_CONFIG) --basedir $(BASE_FOLDER) --fabric $(FABRIC)
.PHONY: dynamic-gen

bit-gen:
	python3 $(SLOT_GEN) -cbf $(SLOT_CONFIG) --basedir $(BASE_FOLDER) --fabric $(FABRIC) --fasm "$(FASM_FILES)"
.PHONY: bit-gen

open-config:
	python3 $(SLOT_GEN) -if $(SLOT_CONFIG) --basedir $(BASE_FOLDER) --fabric $(FABRIC) --fasm "$(FASM_FILES)"
.PHONY: open-config

show-config:
	@echo 'q' | python3 $(SLOT_GEN) -if $(SLOT_CONFIG) --basedir $(BASE_FOLDER) --fabric $(FABRIC) --fasm "$(FASM_FILES)"
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

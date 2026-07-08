# Paths
EXTRA_PRIMITIVES_PATH = ../../extra_primitives.v
BASE_FOLDER = .build
SLOT_GEN = ../slot_gen.py
SLOT_CONFIG = slot_config.yaml
FABRIC = ../../../fabric.csv
FASM_FILES = Static=Static Slot1_2=Interleave,Combine,Function
USERCODES  = 2,2,2,2
BOARD = .board

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
	@echo 'Generate Slot1_2 interleave fasm file'
	@echo '------------------------------------------------------'
	@echo ''
	$(MAKE) slot1_2-interleave-fasm

	@echo ''
	@echo '------------------------------------------------------'
	@echo 'Generate Slot1_2 combine out fasm file'
	@echo '------------------------------------------------------'
	@echo ''
	$(MAKE) slot1_2-combine-fasm

	@echo ''
	@echo '------------------------------------------------------'
	@echo 'Generate Slot1_2 function out fasm file'
	@echo '------------------------------------------------------'
	@echo ''
	$(MAKE) slot1_2-function-fasm

	@echo ''
	@echo '------------------------------------------------------'
	@echo 'Generate bitstreams'
	@echo '------------------------------------------------------'
	@echo ''
	$(MAKE) bit-gen

	@echo ''
	@echo '------------------------------------------------------'
	@echo 'Copy bitstreams'
	@echo '------------------------------------------------------'
	@echo ''
	$(MAKE) board
.PHONY: all

# Slot sources
static-fasm: RTL = static_slot.sv ../../primitive_wrappers.v \
					.build/Static/Static_slot_con_X2Y1.v .build/Static/Static_slot_con_X2Y2.v .build/Static/Static_slot_con_X2Y3.v .build/Static/Static_slot_con_X2Y4.v .build/Static/Static_slot_con_X2Y5.v .build/Static/Static_slot_con_X2Y6.v .build/Static/Static_slot_con_X2Y7.v .build/Static/Static_slot_con_X2Y8.v .build/Static/Static_slot_con_X2Y9.v .build/Static/Static_slot_con_X2Y10.v .build/Static/Static_slot_con_X2Y11.v .build/Static/Static_slot_con_X2Y12.v .build/Static/Static_slot_con_X2Y13.v .build/Static/Static_slot_con_X2Y14.v .build/Static/Static_slot_con_X2Y15.v \
					.build/Static/Static_slot_con_X6Y1.v .build/Static/Static_slot_con_X6Y2.v .build/Static/Static_slot_con_X6Y3.v .build/Static/Static_slot_con_X6Y4.v .build/Static/Static_slot_con_X6Y5.v .build/Static/Static_slot_con_X6Y6.v .build/Static/Static_slot_con_X6Y7.v .build/Static/Static_slot_con_X6Y8.v .build/Static/Static_slot_con_X6Y9.v .build/Static/Static_slot_con_X6Y10.v .build/Static/Static_slot_con_X6Y11.v .build/Static/Static_slot_con_X6Y12.v .build/Static/Static_slot_con_X6Y13.v .build/Static/Static_slot_con_X6Y14.v .build/Static/Static_slot_con_X6Y15.v
static-fasm: TOP = static_slot
static-fasm: SLOT_ROOT = Static
static-fasm: PROG_ROOT = Static
static-fasm: synth pnr
.PHONY: static-fasm

slot1_2-interleave-fasm: RTL = slot1_2_wrapper.sv slot1_2_interleave.sv ../../primitive_wrappers.v \
								.build/Slot1_2/Slot1_2_slot_con_X6Y1.v .build/Slot1_2/Slot1_2_slot_con_X6Y2.v .build/Slot1_2/Slot1_2_slot_con_X6Y3.v .build/Slot1_2/Slot1_2_slot_con_X6Y4.v .build/Slot1_2/Slot1_2_slot_con_X6Y5.v .build/Slot1_2/Slot1_2_slot_con_X6Y6.v .build/Slot1_2/Slot1_2_slot_con_X6Y7.v .build/Slot1_2/Slot1_2_slot_con_X6Y8.v .build/Slot1_2/Slot1_2_slot_con_X6Y9.v .build/Slot1_2/Slot1_2_slot_con_X6Y10.v .build/Slot1_2/Slot1_2_slot_con_X6Y11.v .build/Slot1_2/Slot1_2_slot_con_X6Y12.v .build/Slot1_2/Slot1_2_slot_con_X6Y13.v .build/Slot1_2/Slot1_2_slot_con_X6Y14.v .build/Slot1_2/Slot1_2_slot_con_X6Y15.v
slot1_2-interleave-fasm: TOP = slot1_2_interleave
slot1_2-interleave-fasm: SLOT_ROOT = Slot1_2
slot1_2-interleave-fasm: PROG_ROOT = Interleave
slot1_2-interleave-fasm: synth pnr
.PHONY: slot1_2-interleave-fasm

slot1_2-combine-fasm: RTL = slot1_2_wrapper.sv slot1_2_combine.sv ../../primitive_wrappers.v \
								.build/Slot1_2/Slot1_2_slot_con_X6Y1.v .build/Slot1_2/Slot1_2_slot_con_X6Y2.v .build/Slot1_2/Slot1_2_slot_con_X6Y3.v .build/Slot1_2/Slot1_2_slot_con_X6Y4.v .build/Slot1_2/Slot1_2_slot_con_X6Y5.v .build/Slot1_2/Slot1_2_slot_con_X6Y6.v .build/Slot1_2/Slot1_2_slot_con_X6Y7.v .build/Slot1_2/Slot1_2_slot_con_X6Y8.v .build/Slot1_2/Slot1_2_slot_con_X6Y9.v .build/Slot1_2/Slot1_2_slot_con_X6Y10.v .build/Slot1_2/Slot1_2_slot_con_X6Y11.v .build/Slot1_2/Slot1_2_slot_con_X6Y12.v .build/Slot1_2/Slot1_2_slot_con_X6Y13.v .build/Slot1_2/Slot1_2_slot_con_X6Y14.v .build/Slot1_2/Slot1_2_slot_con_X6Y15.v
slot1_2-combine-fasm: TOP = slot1_2_combine
slot1_2-combine-fasm: SLOT_ROOT = Slot1_2
slot1_2-combine-fasm: PROG_ROOT = Combine
slot1_2-combine-fasm: synth pnr
.PHONY: slot1_2-combine-fasm

slot1_2-function-fasm: RTL = slot1_2_wrapper.sv slot1_2_function.sv ../../primitive_wrappers.v \
								.build/Slot1_2/Slot1_2_slot_con_X6Y1.v .build/Slot1_2/Slot1_2_slot_con_X6Y2.v .build/Slot1_2/Slot1_2_slot_con_X6Y3.v .build/Slot1_2/Slot1_2_slot_con_X6Y4.v .build/Slot1_2/Slot1_2_slot_con_X6Y5.v .build/Slot1_2/Slot1_2_slot_con_X6Y6.v .build/Slot1_2/Slot1_2_slot_con_X6Y7.v .build/Slot1_2/Slot1_2_slot_con_X6Y8.v .build/Slot1_2/Slot1_2_slot_con_X6Y9.v .build/Slot1_2/Slot1_2_slot_con_X6Y10.v .build/Slot1_2/Slot1_2_slot_con_X6Y11.v .build/Slot1_2/Slot1_2_slot_con_X6Y12.v .build/Slot1_2/Slot1_2_slot_con_X6Y13.v .build/Slot1_2/Slot1_2_slot_con_X6Y14.v .build/Slot1_2/Slot1_2_slot_con_X6Y15.v
slot1_2-function-fasm: TOP = slot1_2_function
slot1_2-function-fasm: SLOT_ROOT = Slot1_2
slot1_2-function-fasm: PROG_ROOT = Function
slot1_2-function-fasm: synth pnr
.PHONY: slot1_2-function-fasm

# Helper functions
static-gen:
	python3 $(SLOT_GEN) -gsf $(SLOT_CONFIG) --basedir $(BASE_FOLDER) --fabric $(FABRIC)
.PHONY: static-gen

dynamic-gen:
	python3 $(SLOT_GEN) -gf $(SLOT_CONFIG) --basedir $(BASE_FOLDER) --fabric $(FABRIC)
.PHONY: dynamic-gen

bit-gen:
	python3 $(SLOT_GEN) -cbf $(SLOT_CONFIG) --basedir $(BASE_FOLDER) --fabric $(FABRIC) --fasm "$(FASM_FILES)" --usercode "$(USERCODES)"
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
	rm -rf $(BASE_FOLDER) $(BOARD)
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
			echo "Copy $$bitstream into $(BOARD)/bitstreams/$$folder-$$file.bit"; \
 			cp "$$bitstream" "$(BOARD)/bitstreams/$$folder-$$file.bit"; \
		done; \
	done; \
	if [ -f "$(BASE_FOLDER)/Static/Static.bit" ]; then \
		echo "Copy $(BASE_FOLDER)/Static/Static.bit into $(BOARD)/bitstreams/Static-Full.bit"; \
		cp "$(BASE_FOLDER)/Static/Static.bit" "$(BOARD)/bitstreams/Static-Full.bit"; \
	fi ;
.PHONY: board

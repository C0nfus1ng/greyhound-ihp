# Paths
EXTRA_PRIMITIVES_PATH = ../../extra_primitives.v
BASE_FOLDER = .build
SLOT_GEN = ../slot_gen.py
SLOT_CONFIG = slot_config.yaml
FABRIC = ../../../fabric.csv
FASM_FILES = Static=Static Slot1=Graycode,DirectOut Slot2=LeftShift,RightShift Slot3=StraightThrough,Crossover
USERCODES  = 2,2,2,2,2,2,2
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
	@echo 'Generate Slot1 graycode fasm file'
	@echo '------------------------------------------------------'
	@echo ''
	$(MAKE) slot1-graycode-fasm

	@echo ''
	@echo '------------------------------------------------------'
	@echo 'Generate Slot1 direct out fasm file'
	@echo '------------------------------------------------------'
	@echo ''
	$(MAKE) slot1-direct-out

	@echo ''
	@echo '------------------------------------------------------'
	@echo 'Generate Slot2 left shift fasm file'
	@echo '------------------------------------------------------'
	@echo ''
	$(MAKE) slot2-left-shift

	@echo ''
	@echo '------------------------------------------------------'
	@echo 'Generate Slot2 right shift fasm file'
	@echo '------------------------------------------------------'
	@echo ''
	$(MAKE) slot2-right-shift

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

	@echo ''
	@echo '------------------------------------------------------'
	@echo 'Copy bitstreams'
	@echo '------------------------------------------------------'
	@echo ''
	$(MAKE) board
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

slot1-graycode-fasm: RTL = slot1_wrapper.sv slot1_graycode.sv ../../primitive_wrappers.v \
							.build/Slot1/Slot1_slot_con_X4Y1.v .build/Slot1/Slot1_slot_con_X4Y2.v .build/Slot1/Slot1_slot_con_X4Y3.v .build/Slot1/Slot1_slot_con_X4Y4.v .build/Slot1/Slot1_slot_con_X4Y5.v .build/Slot1/Slot1_slot_con_X4Y6.v .build/Slot1/Slot1_slot_con_X4Y7.v .build/Slot1/Slot1_slot_con_X4Y8.v
slot1-graycode-fasm: TOP = slot1_graycode
slot1-graycode-fasm: SLOT_ROOT = Slot1
slot1-graycode-fasm: PROG_ROOT = Graycode
slot1-graycode-fasm: synth pnr
.PHONY: slot1-graycode-fasm

slot1-direct-out: RTL = slot1_wrapper.sv slot1_direct_out.sv ../../primitive_wrappers.v \
							.build/Slot1/Slot1_slot_con_X4Y1.v .build/Slot1/Slot1_slot_con_X4Y2.v .build/Slot1/Slot1_slot_con_X4Y3.v .build/Slot1/Slot1_slot_con_X4Y4.v .build/Slot1/Slot1_slot_con_X4Y5.v .build/Slot1/Slot1_slot_con_X4Y6.v .build/Slot1/Slot1_slot_con_X4Y7.v .build/Slot1/Slot1_slot_con_X4Y8.v
slot1-direct-out: TOP = slot1_direct_out
slot1-direct-out: SLOT_ROOT = Slot1
slot1-direct-out: PROG_ROOT = DirectOut
slot1-direct-out: synth pnr
.PHONY: slot1_direct_out

slot2-left-shift: RTL = slot2_wrapper.sv slot2_left_shift.sv ../../primitive_wrappers.v \
							.build/Slot2/Slot2_slot_con_X8Y1.v
slot2-left-shift: TOP = slot2_left_shift
slot2-left-shift: SLOT_ROOT = Slot2
slot2-left-shift: PROG_ROOT = LeftShift
slot2-left-shift: synth pnr
.PHONY: slot2-left-shift

slot2-right-shift: RTL = slot2_wrapper.sv slot2_right_shift.sv ../../primitive_wrappers.v \
							.build/Slot2/Slot2_slot_con_X8Y1.v
slot2-right-shift: TOP = slot2_right_shift
slot2-right-shift: SLOT_ROOT = Slot2
slot2-right-shift: PROG_ROOT = RightShift
slot2-right-shift: synth pnr
.PHONY: slot2-right-shift

slot3-straight-through-fasm: RTL = slot3_wrapper.sv io_wrapper.sv slot3_straight_through.sv \
									.build/Slot3/Slot3_slot_con_X2Y1.v .build/Slot3/Slot3_slot_con_X2Y2.v .build/Slot3/Slot3_slot_con_X2Y3.v .build/Slot3/Slot3_slot_con_X2Y4.v .build/Slot3/Slot3_slot_con_X2Y5.v .build/Slot3/Slot3_slot_con_X2Y6.v .build/Slot3/Slot3_slot_con_X2Y7.v .build/Slot3/Slot3_slot_con_X2Y8.v
slot3-straight-through-fasm: TOP = slot3_straight_through
slot3-straight-through-fasm: SLOT_ROOT = Slot3
slot3-straight-through-fasm: PROG_ROOT = StraightThrough
slot3-straight-through-fasm: synth pnr
.PHONY: slot3-straight-through-fasm

slot3-crossover-fasm: RTL = slot3_wrapper.sv io_wrapper.sv slot3_crossover.sv \
								.build/Slot3/Slot3_slot_con_X2Y1.v .build/Slot3/Slot3_slot_con_X2Y2.v .build/Slot3/Slot3_slot_con_X2Y3.v .build/Slot3/Slot3_slot_con_X2Y4.v .build/Slot3/Slot3_slot_con_X2Y5.v .build/Slot3/Slot3_slot_con_X2Y6.v .build/Slot3/Slot3_slot_con_X2Y7.v .build/Slot3/Slot3_slot_con_X2Y8.v
slot3-crossover-fasm: TOP = slot3_crossover
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

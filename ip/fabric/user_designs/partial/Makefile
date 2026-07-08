FLASH_LAYOUT = "0:custom_instr/.board/bitstreams=Static-Full,Static-Static,Slot1-DirectOut,Slot2-LeftShift,Slot2-RightShift,Slot3-Crossover,Slot3-StraightThrough \
				1:custom_instr_2slot/.board/bitstreams=Static-Full,Static-Static,Slot1_2-Combine,Slot1_2-Function,Slot1_2-Interleave"

all:
	cd function_test; make
	cd custom_instr; make

	@echo '------------------------------------------------------'
	@echo 'Build flash image'
	@echo '------------------------------------------------------'
	@echo ''
	$(MAKE) bit-to-flash
.PHONY: all

clean:
	cd function_test; make clean
	cd custom_instr; make clean
.PHONY: clean

bit-to-flash:
	python3 bit_to_flash.py -f flash_image.bit -i $(FLASH_LAYOUT)
.PHONY: bit-to-flash

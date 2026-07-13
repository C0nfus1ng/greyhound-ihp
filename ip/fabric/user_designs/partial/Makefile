FLASH_LAYOUT = "0:custom_instr/.board/bitstreams=Static-Full,Static-Static,Slot1-DirectOut,Slot1-Graycode,Slot2-LeftShift,Slot2-RightShift,Slot3-Crossover,Slot3-StraightThrough \
				1:custom_instr_2slot/.board/bitstreams=Static-Full,Static-Static,Slot1_2-Combine,Slot1_2-Function,Slot1_2-Interleave"

all:
	cd custom_instr; make
	cd custom_instr_2slot; make

	@echo '------------------------------------------------------'
	@echo 'Build flash image'
	@echo '------------------------------------------------------'
	@echo ''
	$(MAKE) bit-to-flash
	$(MAKE) bit-to-hex
.PHONY: all

clean:
	cd custom_instr; make clean
	cd custom_instr_2slot; make clean
.PHONY: clean

bit-to-flash:
	python3 bit_to_flash.py -f flash_image.bit -i $(FLASH_LAYOUT)
.PHONY: bit-to-flash

bit-to-hex:
	python3 ../bit_to_hex.py flash_image.bit flash_image.hex
.PHONY: bit-to-hex

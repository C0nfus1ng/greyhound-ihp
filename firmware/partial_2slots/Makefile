CV_SW_TOOLCHAIN  ?= /opt/riscv
RISCV            ?= $(CV_SW_TOOLCHAIN)
RISCV_EXE_PREFIX ?= $(RISCV)/bin/riscv32-unknown-elf-
RISCV_CC         ?= gcc
RISCV_GCC = $(RISCV_EXE_PREFIX)$(RISCV_CC)
RISCV_AR = $(RISCV_EXE_PREFIX)ar
RISCV_MARCH ?= rv32ima_zicsr #rv32imc_zicsr
PYTHON ?= python3
SRC = partial_2slots.c
OBJ = partial_2slots.o
CFLAGS ?= -Os -g -static -mabi=ilp32 -march=$(RISCV_MARCH) -Wall -pedantic $(RISCV_CFLAGS) -I ../bsp -I ../bsp/drivers/EF_UART

TARGET = partial_2slots
SLOT_NAMES = Static Slot1-Interleave Slot1-Reverse Slot2-Interleave Slot2-Reverse
SLOT_HEADERS = $(addsuffix .h, $(SLOT_NAMES))
ELF_TARGET = $(TARGET).elf
BIN_TARGET = $(TARGET).bin
HEX_TARGET= $(TARGET).hex

BSP_PATH = ../bsp
LINKER_SCRIPT = $(BSP_PATH)/link.ld

LDFLAGS += -T $(LINKER_SCRIPT) -nostartfiles
LDFLAGS += -L$(ENV_DIR) --specs=nano.specs

all: $(HEX_TARGET)

%.o : %.c
	$(RISCV_GCC) $(CFLAGS) -c $< -o $@

%.o : %.S
	$(RISCV_GCC) $(CFLAGS) -c $< -o $@

tile_offset = $(if $(filter Slot1-%,$1),0,$(if $(filter Slot2-%,$1),2,0))
bit_name = $(patsubst Slot1-%,%,$(patsubst Slot2-%,%,$1))

define SLOT_HEADER_RULE
$1.h: ../../ip/fabric/user_designs/partial/custom_instr_2slots/board/bitstreams/$(call bit_name,$1).bit
	$$(PYTHON) build_lookup.py --bytes_per_frame 68 --tile_x_offset $(call tile_offset,$1) $$< ../../ip/fabric/user_designs/partial/custom_instr_2slots/board/bitstreams/Static-full.bit $$@
endef

$(foreach name,$(SLOT_NAMES),$(eval $(call SLOT_HEADER_RULE,$(name))))


$(OBJ): $(SLOT_HEADERS)

$(ELF_TARGET): $(OBJ)
	$(RISCV_GCC) $(CFLAGS) $< -L$(BSP_PATH) -l:bsp.a -o $@ $(LDFLAGS)

$(BIN_TARGET): $(ELF_TARGET)
	$(RISCV_EXE_PREFIX)objcopy -O binary $< $@

$(HEX_TARGET): $(BIN_TARGET)
	$(PYTHON) ../makehex.py $< $@

dump: $(ELF_TARGET)
	$(RISCV_EXE_PREFIX)objdump -d -x $<
.phony: dump


clean:
	rm -f $(SLOT_HEADERS) $(OBJ) $(ELF_TARGET) $(BIN_TARGET) $(HEX_TARGET)
.phony: clean

vars:
	@echo "make variables:"
	@echo "   CV_SW_TOOLCHAIN  = $(CV_SW_TOOLCHAIN)"
	@echo "   RISCV            = $(RISCV)"
	@echo "   RISCV_EXE_PREFIX = $(RISCV_EXE_PREFIX)"
	@echo "   RISCV_GCC        = $(RISCV_GCC)"
	@echo "   RISCV_MARCH      = $(RISCV_MARCH)"
	@echo "   RISCV_CFLAGS     = $(RISCV_CFLAGS)"
	@echo "   CFLAGS           = $(CFLAGS)"

.phony: vars

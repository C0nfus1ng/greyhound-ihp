#include <stdio.h>
#include <stdint.h>
#include <soc.h>

#include "static.h"
#include "slot1_crossover.h"
#include "slot1_direct_out.h"
#include "slot1_graycode.h"
#include "slot1_stage.h"
#include "slot2_peripheral.h"
#include "slot2_xif_left_roll.h"
#include "slot2_xif_right_roll.h"

#define F_CPU 50000000
#define BAUDRATE 115200

void wait_nop(uint16_t wait) {
  for (uint16_t  i = 0; i < wait; i++) {
    asm volatile ("nop");
  }
}

uint32_t custom_instruction(uint32_t op1, uint32_t op2) {
  uint32_t ret;
  
  __asm__ volatile (".insn r 0x5b, 0, 13, %0, %1, %2" : "=r" (ret)
                                                      : "r"  (op1),
                                                        "r"  (op2));

  return ret;
}

int main()
{
  // Write static bitstream
  for (uint32_t i = 0; i < sizeof(static_bitstream)/sizeof(uint32_t); i++) {
    *REG_BITSTREAM = static_bitstream[i];
  }

  // Write Slot1 bitstream
  for (uint32_t i = 0; i < sizeof(slot1_direct_out_bitstream)/sizeof(uint32_t); i++) {
    *REG_BITSTREAM = slot1_direct_out_bitstream[i];
  }

  // Write Slot2 bitstream
  for (uint32_t i = 0; i < sizeof(slot2_peripheral_bitstream)/sizeof(uint32_t); i++) {
    *REG_BITSTREAM = slot2_peripheral_bitstream[i];
  }
  wait_nop(0x10);

  // Test Peripheral
  *REG_XIF_OR_PERIPH = 1; // Set CPU_IF to peripheral

  *((int*)FABRIC_BASE) = 0x0;
  for (int i=1; i<4; i++) {
    *((int*)FABRIC_BASE + i) = 0x8 + i;
  }

  for (int i=1; i<4; i++) {
    *((int*)FABRIC_BASE) = i;
    wait_nop(0x10);
  }
  
  *((int*)FABRIC_BASE) = 0x0;

  // Write Slot1 bitstream
  for (uint32_t i = 0; i < sizeof(slot1_crossover_bitstream)/sizeof(uint32_t); i++) {
    *REG_BITSTREAM = slot1_crossover_bitstream[i];
  }

  *((int*)FABRIC_BASE) = 0x0;
  for (int i=1; i<4; i++) {
    *((int*)FABRIC_BASE + i) = 0x8 + i;
  }

  for (int i=1; i<4; i++) {
    *((int*)FABRIC_BASE) = i;
    wait_nop(0x10);
  }

  *((int*)FABRIC_BASE) = 0x0;
  
  // Test Xif
  *REG_XIF_OR_PERIPH = 0; // Set CPU_IF to xif
  // Write Slot2 bitstream
  for (uint32_t i = 0; i < sizeof(slot2_xif_left_roll_bitstream)/sizeof(uint32_t); i++) {
    *REG_BITSTREAM = slot2_xif_left_roll_bitstream[i];
  }

  custom_instruction(0xA012789F, 0x2);
  wait_nop(0x10);

  // Write Slot1 bitstream
  for (uint32_t i = 0; i < sizeof(slot1_graycode_bitstream)/sizeof(uint32_t); i++) {
    *REG_BITSTREAM = slot1_graycode_bitstream[i];
  }

  custom_instruction(0xA012789F, 0x2);
  wait_nop(0x10);

  // Write Slot2 bitstream
  for (uint32_t i = 0; i < sizeof(slot2_xif_right_roll_bitstream)/sizeof(uint32_t); i++) {
    *REG_BITSTREAM = slot2_xif_right_roll_bitstream[i];
  }

  custom_instruction(0xA012789F, 0x2);
  wait_nop(0x10);

  // Write Slot1 bitstream
  for (uint32_t i = 0; i < sizeof(slot1_stage_bitstream)/sizeof(uint32_t); i++) {
    *REG_BITSTREAM = slot1_stage_bitstream[i];
  }

  custom_instruction(0xA012789F, 0x2);
  wait_nop(0x10);

  return 0;
}

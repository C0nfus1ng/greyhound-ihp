#include <stdio.h>
#include <stdint.h>
#include <soc.h>

#include "static.h"
#include "slot1_2_interleave_slot1.h"
#include "slot1_2_interleave_slot2.h"
#include "slot1_2_reverse_slot1.h"
#include "slot1_2_reverse_slot2.h"


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
  wait_nop(0x100);

  // Write Slot1 bitstream
  for (uint32_t i = 0; i < sizeof(slot1_2_interleave_slot1_bitstream)/sizeof(uint32_t); i++) {
    *REG_BITSTREAM = slot1_2_interleave_slot1_bitstream[i];
  }
  wait_nop(0x100);

  // Write Slot2 bitstream
  for (uint32_t i = 0; i < sizeof(slot1_2_reverse_slot2_bitstream)/sizeof(uint32_t); i++) {
    *REG_BITSTREAM = slot1_2_reverse_slot2_bitstream[i];
  }
  wait_nop(0x100);

  custom_instruction(0xa, 0x0);

  for (uint32_t i = 0; i < sizeof(slot1_2_interleave_slot2_bitstream)/sizeof(uint32_t); i++) {
    *REG_BITSTREAM = slot1_2_interleave_slot2_bitstream[i];
  }

  custom_instruction(0xa, 0x0);
  wait_nop(0x100);

  for (uint32_t i = 0; i < sizeof(slot1_2_reverse_slot1_bitstream)/sizeof(uint32_t); i++) {
    *REG_BITSTREAM = slot1_2_reverse_slot1_bitstream[i];
  }

  custom_instruction(0xa, 0x0);
  wait_nop(0x100);
  
  return 0;
}

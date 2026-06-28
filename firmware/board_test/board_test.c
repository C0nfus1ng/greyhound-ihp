#include <stdio.h>
#include <stdint.h>
#include <soc.h>

#include "peripheral.h"
#include "xif.h"

#define F_CPU 50000000

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
  // Write bitstream to output 8 bit with the peripheral
  for (uint32_t i = 0; i < sizeof(peripheral_bitstream)/sizeof(uint32_t); i++) {
    *REG_BITSTREAM = peripheral_bitstream[i];
  }

  // Test Peripheral by writing an 8 bit value. Bitstream will write the value through to the GPIOs
  *REG_XIF_OR_PERIPH = 1; // Set CPU_IF to peripheral
  wait_nop(0x100);
  *((int*)FABRIC_BASE) = 0x0;
  wait_nop(0x100);
  *((int*)FABRIC_BASE) = 0x1;
  wait_nop(0x100);
  *((int*)FABRIC_BASE) = 0x2;
  wait_nop(0x100);
  *((int*)FABRIC_BASE) = 0x3;
  wait_nop(0x100);
  *((int*)FABRIC_BASE) = 0x4;
  wait_nop(0x100);

  // Write bitstream to output 8 bit with the xif
  for (uint32_t i = 0; i < sizeof(xif_bitstream)/sizeof(uint32_t); i++) {
    *REG_BITSTREAM = xif_bitstream[i];
  }

  // Test xif by writing some values. Bitstream will combine op1 and 2 into a single 8 bit value on the GPIOs
  *REG_XIF_OR_PERIPH = 0; // Set CPU_IF to xif
  wait_nop(0x100);
  custom_instruction(0x0, 0x0);
  wait_nop(0x100);
  custom_instruction(0x1, 0x0);
  wait_nop(0x100);
  custom_instruction(0x2, 0x0);
  wait_nop(0x100);
  custom_instruction(0x3, 0x0);
  wait_nop(0x100);
  custom_instruction(0x4, 0x0);
  wait_nop(0x100);

  return 0;
}

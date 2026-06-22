#include <stdio.h>
#include <stdint.h>
#include <soc.h>
#include <EF_UART.h>

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
  EF_UART_setGclkEnable(UART0_BASE, 1);
  EF_UART_enable(UART0_BASE);
  EF_UART_enableRx(UART0_BASE);
  EF_UART_enableTx(UART0_BASE);
  EF_UART_disableLoopBack(UART0_BASE);
  EF_UART_disableGlitchFilter(UART0_BASE);

  EF_UART_setDataSize(UART0_BASE, 8);
  EF_UART_setTwoStopBitsSelect(UART0_BASE, false);
  EF_UART_setParityType(UART0_BASE, NONE);
  EF_UART_setTimeoutBits(UART0_BASE, 0);
  // baudrate = clock_f / ((PR+1)*8)
  EF_UART_setPrescaler(UART0_BASE, F_CPU/(BAUDRATE*8)-1);

  printf("Start\n");

  // Write static bitstream
  for (uint32_t i = 0; i < sizeof(static_bitstream)/sizeof(uint32_t); i++) {
    *REG_BITSTREAM = static_bitstream[i];
  }
  printf("Loaded Static\n");

  // Write Slot1 bitstream
  for (uint32_t i = 0; i < sizeof(slot1_direct_out_bitstream)/sizeof(uint32_t); i++) {
    *REG_BITSTREAM = slot1_direct_out_bitstream[i];
  }
  printf("Loaded Slot1 direct out\n");

  // Write Slot2 bitstream
  for (uint32_t i = 0; i < sizeof(slot2_peripheral_bitstream)/sizeof(uint32_t); i++) {
    *REG_BITSTREAM = slot2_peripheral_bitstream[i];
  }
  printf("Loaded Slot2 peripheraal\n");
  wait_nop(0x10);

  // Test Peripheral
  *REG_XIF_OR_PERIPH = 1; // Set CPU_IF to peripheral

  *((int*)FABRIC_BASE) = 0x0;
  for (int i=1; i<4; i++) {
    *((int*)FABRIC_BASE + i) = 0x21787456 + i;
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
  printf("Loaded Slot1 crossover\n");

  for (int i=1; i<4; i++) {
    *((int*)FABRIC_BASE) = i;
    wait_nop(0x10);
  }

  *((int*)FABRIC_BASE) = 0x0;
  
  printf("Tested peripheral\n");

  // Test Xif
  *REG_XIF_OR_PERIPH = 0; // Set CPU_IF to xif
  // Write Slot2 bitstream
  for (uint32_t i = 0; i < sizeof(slot2_xif_left_roll_bitstream)/sizeof(uint32_t); i++) {
    *REG_BITSTREAM = slot2_xif_left_roll_bitstream[i];
  }
  printf("Loaded Slot2 xif left roll\n");

  uint32_t ret = custom_instruction(0xA012789F, 0x2);
  printf("Ret: %lx\n", ret);

  // Write Slot1 bitstream
  for (uint32_t i = 0; i < sizeof(slot1_graycode_bitstream)/sizeof(uint32_t); i++) {
    *REG_BITSTREAM = slot1_graycode_bitstream[i];
  }
  printf("Loaded Slot1 graycode\n");

  ret = custom_instruction(0xA012789F, 0x2);
  printf("Ret: %lx\n", ret);

  // Write Slot2 bitstream
  for (uint32_t i = 0; i < sizeof(slot2_xif_right_roll_bitstream)/sizeof(uint32_t); i++) {
    *REG_BITSTREAM = slot2_xif_right_roll_bitstream[i];
  }
  printf("Loaded Slot2 xif right roll\n");

  ret = custom_instruction(0xA012789F, 0x2);
  printf("Ret: %lx\n", ret);

  // Write Slot1 bitstream
  for (uint32_t i = 0; i < sizeof(slot1_stage_bitstream)/sizeof(uint32_t); i++) {
    *REG_BITSTREAM = slot1_stage_bitstream[i];
  }
  printf("Loaded Slot1 stage\n");

  ret = custom_instruction(0xA012789F, 0x2);
  printf("Ret: %lx\n", ret);

  wait_nop(0x10);

  return 0;
}

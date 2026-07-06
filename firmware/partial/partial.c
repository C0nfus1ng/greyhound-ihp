#include <stdio.h>
#include <stdint.h>
#include <soc.h>
#include <EF_UART.h>

#include "Static-Static.h"
#include "Slot1-DirectOut.h"
#include "Slot1-Graycode.h"
#include "Slot2-LeftShift.h"
#include "Slot2-RightShift.h"
#include "Slot3-Crossover.h"
#include "Slot3-StraightThrough.h"

#define F_CPU 50000000
#define BAUDRATE 115200

uint32_t left_shift(uint32_t op1, uint32_t op2) {
  uint32_t ret;
  
  //Instr: .insn <type> <opcode>, <func3>, <func 7>, rd, rs1, rs2
  __asm__ volatile (".insn r 0x5b, 1, 0, %0, %1, %2" : "=r" (ret)
                                                     : "r"  (op1),
                                                       "r"  (op2));

  return ret;
}

uint32_t right_shift(uint32_t op1, uint32_t op2) {
  uint32_t ret;
  
  __asm__ volatile (".insn r 0x5b, 2, 0, %0, %1, %2" : "=r" (ret)
                                                     : "r"  (op1),
                                                       "r"  (op2));

  return ret;
}

void wait_nop(uint16_t wait) {
  for (uint16_t  i = 0; i < wait; i++) {
    asm volatile ("nop");
  }
}

int main() {
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
  for (uint32_t i = 0; i < sizeof(static_static_bitstream)/sizeof(uint32_t); i++) {
    *REG_BITSTREAM = static_static_bitstream[i];
  }
  printf("Loaded Static\n");

  // Write Slot1 bitstream
  for (uint32_t i = 0; i < sizeof(slot1_directOut_bitstream)/sizeof(uint32_t); i++) {
    *REG_BITSTREAM = slot1_directOut_bitstream[i];
  }
  printf("Loaded Slot1 direct out\n");

  // Write Slot2 bitstream
  for (uint32_t i = 0; i < sizeof(slot2_leftShift_bitstream)/sizeof(uint32_t); i++) {
    *REG_BITSTREAM = slot2_leftShift_bitstream[i];
  }
  printf("Loaded Slot2 left shift\n");

  // Write Slot3 bitstream
  for (uint32_t i = 0; i < sizeof(slot3_straightThrough_bitstream)/sizeof(uint32_t); i++) {
    *REG_BITSTREAM = slot3_straightThrough_bitstream[i];
  }
  printf("Loaded Slot3 straight through\n");

  // Test instr. and OBI
  uint32_t word = 0xcafecafe;
  uint8_t overflow = 0;
  for (uint8_t i = 0; i < sizeof(uint32_t)*2; i++) {
    overflow = word & 0xf;
    word = (word>>4)|(overflow<<28);
    *((int*)FABRIC_BASE) = word;
    wait_nop(0x100);
  }
  printf("IO reg %x\n", *((int*)FABRIC_BASE));

  uint32_t test_left_shift = left_shift(0xdeadbeef, 0x10);
  printf("Left shift 1: %lx\n", test_left_shift);
  
  wait_nop(0x100);
  test_left_shift = left_shift(0xbeefdead, 0x5);
  wait_nop(0x100);
  printf("Left shift 2: %lx\n", test_left_shift);

  // Write Slot2 bitstream
  for (uint32_t i = 0; i < sizeof(slot2_rightShift_bitstream)/sizeof(uint32_t); i++) {
    *REG_BITSTREAM = slot2_rightShift_bitstream[i];
  }
  printf("Loaded Slot2 right shift\n");

  uint32_t test_right_shift = right_shift(0xdeadbeef, 0x3);
  wait_nop(0x100);
  printf("Right shift 1: %lx\n", test_right_shift);

  test_right_shift = right_shift(0xdeadbeef, 0x10);
  wait_nop(0x100);
  printf("Right shift 2: %lx\n", test_right_shift);

  // Write Slot3 bitstream
  for (uint32_t i = 0; i < sizeof(slot3_crossover_bitstream)/sizeof(uint32_t); i++) {
    *REG_BITSTREAM = slot3_crossover_bitstream[i];
  }
  printf("Loaded Slot3 crossover\n");

  word = 0xcafecafe;
  overflow = 0;
  for (uint8_t i = 0; i < sizeof(uint32_t)*2; i++) {
    overflow = word & 0xf;
    word = (word>>4)|(overflow<<28);
    *((int*)FABRIC_BASE) = word;
    wait_nop(0x100);
  }
  printf("IO reg %x\n", *((int*)FABRIC_BASE));

  // Write Slot1 bitstream
  for (uint32_t i = 0; i < sizeof(slot1_graycode_bitstream)/sizeof(uint32_t); i++) {
    *REG_BITSTREAM = slot1_graycode_bitstream[i];
  }
  printf("Loaded Slot1 graycode\n");
  
  word = 0xcafecafe;
  overflow = 0;
  for (uint8_t i = 0; i < sizeof(uint32_t)*2; i++) {
    overflow = word & 0xf;
    word = (word>>4)|(overflow<<28);
    *((int*)FABRIC_BASE) = word;
    wait_nop(0x100);
  }
  printf("IO reg %x\n", *((int*)FABRIC_BASE));

  // Write Slot3 bitstream
  for (uint32_t i = 0; i < sizeof(slot3_straightThrough_bitstream)/sizeof(uint32_t); i++) {
    *REG_BITSTREAM = slot3_straightThrough_bitstream[i];
  }
  printf("Loaded Slot3 straight through\n");
  
  word = 0xcafecafe;
  overflow = 0;
  for (uint8_t i = 0; i < sizeof(uint32_t)*2; i++) {
    overflow = word & 0xf;
    word = (word>>4)|(overflow<<28);
    *((int*)FABRIC_BASE) = word;
    wait_nop(0x100);
  }
  printf("IO reg %x\n", *((int*)FABRIC_BASE));

  return 0;
}

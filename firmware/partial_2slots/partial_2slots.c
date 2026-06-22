#include <stdio.h>
#include <stdint.h>
#include <soc.h>
#include <EF_UART.h>

#define F_CPU 50000000
#define BAUDRATE 115200

uint32_t custom_instr(uint32_t op0, uint32_t op1) {
  uint32_t ret;
  
  __asm__ volatile (".insn r 0x5b, 0, 13, %0, %1, %2" : "=r" (ret)
                                                      : "r"  (op0),
                                                        "r"  (op1));

  return ret;
}

void wait_nop(uint16_t wait) {
  for (uint16_t  i = 0; i < wait; i++) {
    asm volatile ("nop");
  }
}

void wait_for_config() {
  uint8_t busy = 0;
  uint8_t busy_prev = 0;

  while (!busy_prev || busy) {
    busy_prev = busy;
    busy = (uint8_t)*REG_FABRIC_CONFIG_BUSY;
    wait_nop(0x10);
  }
}

int main() {
  uint32_t ret = 0;

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
  
  printf("Init\n");

  // Wait for static bitstream
  wait_for_config();
  printf("Static\n");

  // Wait for Slot 1
  wait_for_config();
  printf("Slot1\n");

  // Wait for Slot 2
  wait_for_config();
  printf("Slot2\n");

  ret = custom_instr(0x3, 0x1);
  printf("Ret: %04lx\n", ret);
  wait_nop(0x10);
  ret = custom_instr(0x1, 0x3);
  printf("Ret: %04lx\n", ret);

  // Wait for Slot 1
  wait_for_config();
  printf("Slot1\n");

  // Wait for Slot 2
  wait_for_config();
  printf("Slot2\n");

  ret = custom_instr(0x3, 0x1);
  printf("Ret: %04lx\n", ret);
  wait_nop(0x10);
  ret = custom_instr(0x1, 0x3);
  printf("Ret: %04lx\n", ret);
  wait_nop(0x10);
  ret = custom_instr(0x2, 0x7);
  printf("Ret: %04lx\n", ret);
  wait_nop(0x10);
  ret = custom_instr(0x2, 0x6);
  printf("Ret: %04lx\n", ret);
  wait_nop(0x10);
  ret = custom_instr(0xb, 0x4);
  printf("Ret: %04lx\n", ret);

  printf("End\n");
  return 0;
}

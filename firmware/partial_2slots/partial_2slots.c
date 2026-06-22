#include <stdio.h>
#include <stdint.h>
#include <soc.h>
#include <EF_UART.h>

#define F_CPU 50000000
#define BAUDRATE 115200

uint32_t custom_instr(uint32_t op1, uint32_t op2) {
  uint32_t ret;
  
  __asm__ volatile (".insn r 0x0b, 0, 13, %0, %1, %2" : "=r" (ret)
                                                      : "r"  (op1),
                                                        "r"  (op2));

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

  uint32_t ret = custom_instr(0x01234567, 0x89abcdef);
  printf("Ret: %04lx\n", ret);
  
  wait_nop(0x10);
  ret = custom_instr(0x89abcdef, 0x01234567);
  printf("Ret: %04lx\n", ret);

  printf("End\n");
  return 0;
}

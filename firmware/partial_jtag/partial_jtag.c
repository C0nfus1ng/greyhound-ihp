#include <stdio.h>
#include <stdint.h>
#include <soc.h>

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
  }
}

int main() {
  // Wait for static bitstream
  wait_for_config();
  // Wait for Slot 1
  wait_for_config();
  // Wait for Slot 3
  wait_for_config();

  uint32_t word = 0xcafe7007;
  uint8_t overflow = 0;
  for (uint8_t i = 0; i < 8; i++) {
    overflow = word & 0xf;
    word = (word>>4)|(overflow<<28);
    *((int*)FABRIC_BASE) = word;
    wait_nop(0x10);
  }

  // Wait for Slot 3
  wait_for_config();
  word = 0xcafe0707;
  for (uint8_t i = 0; i < sizeof(uint32_t)*2; i++) {
    overflow = word & 0xf;
    word = (word>>4)|(overflow<<28);
    *((int*)FABRIC_BASE) = word;
    wait_nop(0x10);
  }

  // Wait for Slot 1
  wait_for_config();
  word = 0xcafe7070;
  for (uint8_t i = 0; i < sizeof(uint32_t)*2; i++) {
    overflow = word & 0xf;
    word = (word>>4)|(overflow<<28);
    *((int*)FABRIC_BASE) = word;
    wait_nop(0x10);
  }

  // Wait for Slot3
  wait_for_config();
  word = 0xcafe0770;
  for (uint8_t i = 0; i < sizeof(uint32_t)*2; i++) {
    overflow = word & 0xf;
    word = (word>>4)|(overflow<<28);
    *((int*)FABRIC_BASE) = word;
    wait_nop(0x10);
  }

  return 0;
}

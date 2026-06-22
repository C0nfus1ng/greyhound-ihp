#include <stdio.h>
#include <stdint.h>
#include <soc.h>
#include <EF_UART.h>

#include "static.h"
#include "slot1_direct_out.h"
#include "slot1_graycode.h"
#include "slot2_left_shift.h"
#include "slot2_right_shift.h"
#include "slot3_crossover.h"
#include "slot3_straight_through.h"

#define F_CPU 50000000
#define BAUDRATE 115200
#define SLOT_START 0xfab0fab1
#define FRAME_PRE_HEADER 0x5e700000
#define FPGA_HEIGHT 18
#define FPGA_LENGTH 12
#define FPGA_FRAMES_PER_TILE 24

// Tiles below the dynamic slot
uint32_t pseudo_bitstream(uint32_t bitstream_word, bool write, int8_t fpga_height, int8_t fpga_length, int8_t fpga_frame) {
  static uint32_t loaded_bitstream[3*FPGA_FRAMES_PER_TILE] = {0};

  if ((fpga_height > 16) && (fpga_length < 3)) {

    if (write) {
      loaded_bitstream[fpga_frame+(fpga_length*FPGA_FRAMES_PER_TILE)] = bitstream_word;
      return 0;
    }

    return loaded_bitstream[fpga_frame*(FPGA_HEIGHT+1)+(fpga_length*(FPGA_HEIGHT+1)*FPGA_FRAMES_PER_TILE)];
  }

  return static_bitstream[5+(fpga_height+1)+fpga_frame*(FPGA_HEIGHT+1)+(fpga_length*(FPGA_HEIGHT+1)*FPGA_FRAMES_PER_TILE)];
}

void write_bitstream(const uint32_t *bitstream, uint32_t length) {
  uint32_t tile_lookup = 0x3ffff;
  uint32_t bitstream_word = 0;
  int32_t slot_bitstream_word = 0;
  uint8_t frame_length = FPGA_HEIGHT;
  int8_t frame_x_coord = 0;
  int8_t frame_y_coord = 0;
  int8_t frame_strobe[FPGA_FRAMES_PER_TILE] = {0};
  bool slot_started = false;
  bool use_tile = false;
  bool use_frame_tiles = true;

  for (uint32_t i = 0; i < length; i++) {
    if (!slot_started) {
      if (bitstream[i] == SLOT_START) {
        slot_started = true;
        use_frame_tiles = true;  
        slot_bitstream_word = i-1;
        tile_lookup = 0x3ffff;
        frame_length = FPGA_HEIGHT+1;
      }

      *REG_BITSTREAM = bitstream[i];
      continue;
    }

    // Slot started
    if (use_frame_tiles) {
      tile_lookup = bitstream[slot_bitstream_word--];

      if ((slot_bitstream_word < 0) || (tile_lookup & 0xfff00000) != FRAME_PRE_HEADER) {
        tile_lookup = 0x3ffff;
        use_frame_tiles = false;
      }
    }

    if (frame_length-- == FPGA_HEIGHT) {
      *REG_BITSTREAM = bitstream[i];
      frame_x_coord = bitstream[i] >> 27;
      frame_y_coord = i+1;

      for (int8_t j = FPGA_FRAMES_PER_TILE-1; j >= 0; j--) {
        frame_strobe[j] = ((bitstream[i] >> j)&0x1);
      }
      continue;
    }

    use_tile = (tile_lookup >> frame_length) & 0x1;
    bitstream_word = bitstream[i];

    if (use_tile) {
      for (int8_t j = FPGA_FRAMES_PER_TILE-1; j >= 0; j--) {
        if (frame_strobe[j]) {
          pseudo_bitstream(bitstream[i], true, i-frame_y_coord, frame_x_coord, j);
        }
      }
    } else {
      for (int8_t j = FPGA_FRAMES_PER_TILE-1; j >= 0; j--) {
        if (frame_strobe[j]) {
          bitstream_word = pseudo_bitstream(0, false, i-frame_y_coord, frame_x_coord, j);
        }
      }
    }

    if (frame_length == 0) {
      frame_length = FPGA_HEIGHT+1;
      tile_lookup = 0x3ffff;
      use_frame_tiles = true;
    }

    *REG_BITSTREAM = bitstream_word;
  }
}

uint32_t left_shift(uint32_t op1, uint32_t op2) {
  uint32_t ret;
  
  __asm__ volatile (".insn r 0x5b, 0, 13, %0, %1, %2" : "=r" (ret)
                                                      : "r"  (op1),
                                                        "r"  (op2));

  return ret ;
}

uint32_t right_shift(uint32_t op1, uint32_t op2) {
  uint32_t ret;
  
  __asm__ volatile (".insn r 0x7b, 0, 13, %0, %1, %2" : "=r" (ret)
                                                      : "r"  (op1),
                                                        "r"  (op2));

  return ret ;
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

  // TODO read back USERCODE
  // Write static bitstream
  write_bitstream(static_bitstream, sizeof(static_bitstream)/sizeof(uint32_t));
  printf("Loaded Static\n");

  // Write Slot1 bitstream
  write_bitstream(slot1_direct_out_bitstream, sizeof(slot1_direct_out_bitstream)/sizeof(uint32_t));
  printf("Loaded Slot1 direct out\n");

  // Write Slot2 bitstream
  write_bitstream(slot2_left_shift_bitstream, sizeof(slot2_left_shift_bitstream)/sizeof(uint32_t));
  printf("Loaded Slot2 left shift\n");

  // Write Slot3 bitstream
  write_bitstream(slot3_straight_through_bitstream, sizeof(slot3_straight_through_bitstream)/sizeof(uint32_t));
  printf("Loaded Slot3 straight through\n");

  // Test instr. and OBI
  uint32_t test_left_shift = left_shift(0xdeadbeef, 0x10);
  *((int*)FABRIC_BASE) = 0xcafecafe;

  printf("Left shift: %lx\n", test_left_shift);

  // uint32_t test_right_shift = right_shift(0xdeadbeef, 0x4);

  return 0;
}

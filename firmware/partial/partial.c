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
uint32_t pseudo_bitstream(uint32_t bitstream_word, bool use_new_tile, int8_t fpga_y_coord, int8_t fpga_x_coord, uint32_t fpga_frame_strobe) {
  static uint32_t loaded_bitstream[3*FPGA_FRAMES_PER_TILE] = {0};
  bool use_frame = false;
  uint32_t loaded_bitstream_word = 0;
  uint32_t prev_loaded_bitstream_word = 0;
  uint32_t frame_strobe = fpga_frame_strobe;

  // Frame is in the tile array
  if ((fpga_y_coord == 17) && (fpga_x_coord < 3)) { // Use tile frame from array
    if (use_new_tile) { // Save new tile frame into array
      for (uint8_t fpga_frame = 0; fpga_frame < FPGA_FRAMES_PER_TILE; fpga_frame++) {
        use_frame = (frame_strobe >> fpga_frame) & 0x1;

        if (use_frame) {
          loaded_bitstream[fpga_frame+(fpga_x_coord*FPGA_FRAMES_PER_TILE)] = bitstream_word;
        }
      }

      return bitstream_word;
    } else { // Use old tile frame from array
      for (uint8_t fpga_frame = 0; fpga_frame < FPGA_FRAMES_PER_TILE; fpga_frame++) {
        use_frame = (frame_strobe >> fpga_frame) & 0x1;

        if (use_frame) {
          // Strobe must only have bits set were static frames are the same, otherwise static config may be changed
          prev_loaded_bitstream_word = loaded_bitstream_word;
          loaded_bitstream_word = loaded_bitstream[fpga_frame+(fpga_x_coord*FPGA_FRAMES_PER_TILE)];
        }
      }
      
      return loaded_bitstream_word;
    }
  }

  uint32_t i_word = 0;
  int8_t header_x_coord = 0;
  uint32_t header_strobe = 0;

  // Frame is not in the tile array
  if (use_new_tile) { // Use new tile frame from bitstream
    return bitstream_word;
  } else { // Use old tile frame from bitstream
    for (; i_word < sizeof(static_bitstream)/sizeof(uint32_t); i_word++) {
      if (static_bitstream[i_word] == SLOT_START) {
        i_word++;
        break;
      }
    }

    // Found slot start, iterate over the headers now
    for (; i_word < sizeof(static_bitstream)/sizeof(uint32_t); i_word += (FPGA_HEIGHT+1)) {
      // Check if X matches, then check for strobing and data
      // Can break if X is larger than requested
      header_x_coord = static_bitstream[i_word]>>27;
      header_strobe = static_bitstream[i_word] & 0xfffff;

      if (header_x_coord > fpga_x_coord) {
        break;
      }
      
      if (header_x_coord == fpga_x_coord) {
        for (uint8_t fpga_frame = 0; fpga_frame < FPGA_FRAMES_PER_TILE; fpga_frame++) {
          use_frame = ((frame_strobe&header_strobe) >> fpga_frame) & 0x1;
          
          if (use_frame) {
            // Strobe must only have bits set were static frames are the same, otherwise static config may be changed
            prev_loaded_bitstream_word = loaded_bitstream_word;
            loaded_bitstream_word = static_bitstream[i_word+FPGA_HEIGHT-fpga_y_coord];
            break;
          }
        }

        frame_strobe &= ~header_strobe;
      }
    }

    return loaded_bitstream_word;
  }

  return 0;
}

void write_bitstream(const uint32_t *bitstream, uint32_t length) {
  uint32_t tile_lookup = 0x3ffff;
  uint32_t bitstream_word = 0;
  int32_t slot_bitstream_word = 0;
  uint8_t frame_height = FPGA_HEIGHT;
  int8_t frame_x_coord = 0;
  int8_t frame_y_coord = 0;
  uint32_t frame_strobe = 0;
  bool slot_started = false;
  bool use_new_tile = false;
  bool use_frame_tiles = true;

  for (uint32_t i = 0; i < length; i++) {
    if (!slot_started) {
      if (bitstream[i] == SLOT_START) {
        slot_started = true;
        use_frame_tiles = true;  
        slot_bitstream_word = i-1;
        tile_lookup = 0x3ffff;
        frame_height = FPGA_HEIGHT+1;
      }

      *REG_BITSTREAM = bitstream[i];
      continue;
    }

    // Slot started
    frame_height--;

    if (frame_height == FPGA_HEIGHT) { // Frame header
      *REG_BITSTREAM = bitstream[i];
      frame_x_coord = bitstream[i] >> 27;
      frame_y_coord = i+FPGA_HEIGHT; // i+1

      frame_strobe = bitstream[i]&0xfffff;

      if (use_frame_tiles) { // Cnt down to another tile usage
        tile_lookup = bitstream[slot_bitstream_word--];

        if ((slot_bitstream_word < 0) || (tile_lookup & 0xfff00000) != FRAME_PRE_HEADER) {
          tile_lookup = 0x3ffff;
          use_frame_tiles = false;
        }
      }

      continue;
    }

    use_new_tile = (tile_lookup >> frame_height) & 0x1;     //    i-frame_y_coord
    bitstream_word = pseudo_bitstream(bitstream[i], use_new_tile, frame_y_coord-i, frame_x_coord, frame_strobe);

    if (frame_height == 0) {
      frame_height = FPGA_HEIGHT+1;
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

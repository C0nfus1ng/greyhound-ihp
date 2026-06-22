#include <stdio.h>
#include <stdint.h>
#include <soc.h>
#include <EF_UART.h>

#include "static.h"
#include "slot1_2_interleave.h"
#include "slot1_2_reverse.h"


#define F_CPU 50000000
#define BAUDRATE 115200
#define SLOT_START 0xfab0fab1
#define FRAME_PRE_HEADER 0x5e700000
#define FPGA_HEIGHT 16
#define FPGA_LENGTH 11
#define FPGA_FRAMES_PER_TILE 24

// Tiles below the dynamic slot
uint32_t pseudo_bitstream(uint32_t bitstream_word, bool use_new_tile, int8_t fpga_y_coord, int8_t fpga_x_coord, uint32_t fpga_frame_strobe) {
  bool use_frame = false;
  uint32_t loaded_bitstream_word = 0;
  uint32_t frame_strobe = fpga_frame_strobe;
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

void write_bitstream(const uint32_t *bitstream, uint32_t length, uint8_t col_offset) {
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
      frame_x_coord = (bitstream[i] >> 27) + col_offset;
      frame_y_coord = i+FPGA_HEIGHT; // i+1
      frame_strobe = bitstream[i]&0xfffff;

      *REG_BITSTREAM = (frame_x_coord << 27) | frame_strobe; // Build new header with offset

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
  write_bitstream(static_bitstream, sizeof(static_bitstream)/sizeof(uint32_t), 0);
  printf("Loaded Static\n");

  // Write Slot1 bitstream
  write_bitstream(slot1_2_interleave_bitstream, sizeof(slot1_2_interleave_bitstream)/sizeof(uint32_t), 0);
  printf("Loaded Slot1_2 interleave in Slot 1\n");

  // Write Slot2 bitstream
  write_bitstream(slot1_2_reverse_bitstream, sizeof(slot1_2_reverse_bitstream)/sizeof(uint32_t), 2);
  printf("Loaded Slot1_2 reverse in Slot 2\n");

  uint32_t ret = custom_instruction(0xa, 0x0);
  printf("Ret: %lx\n", ret);

  write_bitstream(slot1_2_interleave_bitstream, sizeof(slot1_2_interleave_bitstream)/sizeof(uint32_t), 2);
  printf("Loaded Slot1_2 interleave in Slot 2\n");

  ret = custom_instruction(0xa, 0x0);
  printf("Ret: %lx\n", ret);

  write_bitstream(slot1_2_reverse_bitstream, sizeof(slot1_2_reverse_bitstream)/sizeof(uint32_t), 0);
  printf("Loaded Slot1_2 reverse in Slot 1\n");

  ret = custom_instruction(0xa, 0x0);
  printf("Ret: %lx\n", ret);
  
  return 0;
}

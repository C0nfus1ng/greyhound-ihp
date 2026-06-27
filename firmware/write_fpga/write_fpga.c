#include <stdio.h>
#include <stdint.h>
#include <soc.h>

#include "all_ones.h"

int main()
{
  // Write bitstream to fpga
  for (uint32_t i = 0; i < sizeof(fpga_all_ones_bitstream)/sizeof(uint32_t); i++) {
    *REG_BITSTREAM = fpga_all_ones_bitstream[i];
  }

  return 0;
}

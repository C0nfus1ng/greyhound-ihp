#include <stdio.h>

#include <soc.h>

int main()
{
  // Set flash size
  *REG_FABRIC_CONFIG = 0x6<<FABRIC_CONFIG_SLOT_OFFSET;

  // Trigger configuration from slot 0
  *REG_TRIGGER_SLOT = FABRIC_WARMBOOT_BASE_SLOT0;

  // Wait for FPGA to finish configuration
  while (REG_FABRIC_CONFIG_BUSY) {;}

  // Trigger configuration from slot 1
  *REG_TRIGGER_SLOT = FABRIC_WARMBOOT_BASE_SLOT1;

  // Wait for FPGA to finish configuration
  while (REG_FABRIC_CONFIG_BUSY) {;}

  return 0;
}

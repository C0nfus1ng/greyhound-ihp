#include <stdio.h>
#include <stdint.h>
#include <soc.h>
#include <EF_UART.h>

#define F_CPU 50000000
#define BAUDRATE 115200

#define WARMBOOT0_STATIC_FULL_USERCODE 0x00010000
#define WARMBOOT0_STATIC_USERCODE 0x00010009
#define WARMBOOT0_DIRECTOUT_USERCODE 0x0001000b
#define WARMBOOT0_GRAYCODE_USERCODE 0x0001000e
#define WARMBOOT0_LEFTSHIFT_USERCODE 0x00010011
#define WARMBOOT0_RIGHTSHIFT_USERCODE 0x00010014
#define WARMBOOT0_CROSSOVER_USERCODE 0x00010017
#define WARMBOOT0_STRAIGHTTHROUGH_USERCODE 0x00010019
#define WARMBOOT1_STATIC_FULL_USERCODE 0x00010200
#define WARMBOOT1_STATIC_USERCODE 0x00010209
#define WARMBOOT1_COMBINE_USERCODE 0x0001020d
#define WARMBOOT1_FUNCTION_USERCODE 0x0001020f
#define WARMBOOT1_INTERLEAVE_USERCODE 0x00010211
#define WARMBOOT2_ALLZEROS 0x00000400

#define SLOT_OPCODE 0x5b
#define WARMBOOT0_LEFTSHIFT_FUNC3 0x1
#define WARMBOOT0_RIGHTSHIFT_FUNC3 0x2
#define WARMBOOT1_COMBINE_FUNC7 0x0
#define WARMBOOT1_FUNCTION_FUNC7 0x1
#define WARMBOOT1_INTERLEAVE_FUNC7 0x2

volatile uint32_t loaded_slots[4] = {0};
volatile uint8_t  merged_slot = 1;
volatile uint8_t  triggered_irq = 0;

// !!!XIF write back hazards may be ignored by the cpu!!!
// Must never inline the function so gcc is forced to only ever writeback into rd.
// On illegal instruction while mepc is set rd will be set to the value in any register, which is currently in the wb stage.
// Preventing inlining forces the write into a2 in the functions below, since op0=a0 and op1=a1, while ret needs a0 to return.

__attribute__ ((noinline)) uint32_t warmboot0_left_shift(uint32_t op0, uint32_t op1) {
  uint32_t ret;

  //Instr: .insn <type> <opcode>, <func3>, <func7>, rd, rs1, rs2
  __asm__ volatile (".insn r 0x5b, 1, 0, a2, %1, %2\t\n"
                    "mv %0, a2" 
                    : "=r" (ret)
                    : "r"  (op0),
                      "r"  (op1)
                    : "a2");
  return ret;
}

__attribute__ ((noinline)) uint32_t warmboot0_right_shift(uint32_t op0, uint32_t op1) {
  uint32_t ret;

  __asm__ volatile (".insn r 0x5b, 2, 0, a2, %1, %2\t\n"
                    "mv %0, a2" 
                    : "=r" (ret)
                    : "r"  (op0),
                      "r"  (op1)
                    : "a2");

  return ret;
}

__attribute__ ((noinline)) void warmboot1_set_provided(uint32_t op0, uint32_t op1, uint8_t set_mask) {
  static uint32_t op0_q = 0x3;
  static uint32_t op1_q = 0x3;
  
  switch (set_mask)
  {
    case 1:
      op0_q = op0;
      break;
  
    case 2:
      op1_q = op1;
      break;

    default:
      op0_q = op0;
      op1_q = op1;
      break;
  }
  
  __asm__ volatile (".insn r 0x5b, 0, 0x3, x0, %0, %1" :: "r"  (op0_q),
                                                          "r"  (op1_q));
}

__attribute__ ((noinline)) uint8_t warmboot1_combine(uint32_t op0, uint32_t op1) {
  uint32_t ret;
  
  __asm__ volatile (".insn r 0x5b, 0, 0x0, a2, %1, %2\t\n"
                    "mv %0, a2" 
                    : "=r" (ret)
                    : "r"  (op0),
                      "r"  (op1)
                    : "a2");

  if (loaded_slots[1] == WARMBOOT1_COMBINE_USERCODE) {
    return (ret>>4)&0xf;
  }

  return ret&0xf;
}

__attribute__ ((noinline)) uint8_t warmboot1_function(uint32_t op0, uint32_t op1) {
  uint32_t ret;
  
  __asm__ volatile (".insn r 0x5b, 0, 0x1, a2, %1, %2\t\n"
                    "mv %0, a2" 
                    : "=r" (ret)
                    : "r"  (op0),
                      "r"  (op1)
                    : "a2");

  if (loaded_slots[1] == WARMBOOT1_FUNCTION_USERCODE) {
    return (ret>>4)&0xf;
  }

  return ret&0xf;
}

__attribute__ ((noinline)) uint8_t warmboot1_interleave(uint32_t op0, uint32_t op1) {
  uint32_t ret;
  
  __asm__ volatile (".insn r 0x5b, 0, 0x2, a2, %1, %2\t\n"
                    "mv %0, a2" 
                    : "=r" (ret)
                    : "r"  (op0),
                      "r"  (op1)
                    : "a2");

  if (loaded_slots[1] == WARMBOOT1_INTERLEAVE_USERCODE) {
    return (ret>>4)&0xf;
  }

  return ret&0xf;
}

void wait_nop(uint16_t wait) {
  for (uint16_t  i = 0; i < wait; i++) {
    __asm__ volatile ("nop");
  }
}

void test_io() {
  uint32_t word = 0xcafecafe;
  uint8_t overflow = 0;

  for (uint8_t i = 0; i < sizeof(uint32_t)*2; i++) {
    overflow = word & 0xf;
    word = (word>>4)|(overflow<<28);
    *((int*)FABRIC_BASE) = word;
    wait_nop(0x100);
  }

  printf("IO %x\n", *((int*)FABRIC_BASE));
}

// System trap handler
inline __attribute__((always_inline)) uint32_t load_reg_value(uint8_t reg) {
  // Load saved regs from stack
  uint32_t reg_val;
  
  switch(reg) { // ra, sp, gp and tp use is prohibited
    case 5: // t0
      __asm__ volatile ("lw %0, 84(sp)" : "=r" (reg_val));
      break;
    case 6: // t1
      __asm__ volatile ("lw %0, 88(sp)" : "=r" (reg_val));
      break;
    case 7: // t2
      __asm__ volatile ("lw %0, 92(sp)" : "=r" (reg_val));
      break;
    case 8: // fp
      __asm__ volatile ("lw %0, 0(sp)" : "=r" (reg_val));
      break;
    case 9: // s1
      __asm__ volatile ("lw %0, 4(sp)" : "=r" (reg_val));
      break;
    case 10: // a0
      __asm__ volatile ("lw %0, 52(sp)" : "=r" (reg_val));
      break;
    case 11: // a1
      __asm__ volatile ("lw %0, 56(sp)" : "=r" (reg_val));
      break;
    case 12: // a2
      __asm__ volatile ("lw %0, 60(sp)" : "=r" (reg_val));
      break;
    case 13: // a3
      __asm__ volatile ("lw %0, 64(sp)" : "=r" (reg_val));
      break;
    case 14: // a4
      __asm__ volatile ("lw %0, 68(sp)" : "=r" (reg_val));
      break;
    case 15: // a5
      __asm__ volatile ("lw %0, 72(sp)" : "=r" (reg_val));
      break;
    case 16: // a6
      __asm__ volatile ("lw %0, 76(sp)" : "=r" (reg_val));
      break;
    case 17: // a7
      __asm__ volatile ("lw %0, 80(sp)" : "=r" (reg_val));
      break;
    case 18: // s2
      __asm__ volatile ("lw %0, 8(sp)" : "=r" (reg_val));
      break;
    case 19: // s3
      __asm__ volatile ("lw %0, 12(sp)" : "=r" (reg_val));
      break;
    case 20: // s4
      __asm__ volatile ("lw %0, 16(sp)" : "=r" (reg_val));
      break;
    case 21: // s5
      __asm__ volatile ("lw %0, 20(sp)" : "=r" (reg_val));
      break;
    case 22: // s6
      __asm__ volatile ("lw %0, 24(sp)" : "=r" (reg_val));
      break;
    case 23: // s7
      __asm__ volatile ("lw %0, 28(sp)" : "=r" (reg_val));
      break;
    case 24: // s8
      __asm__ volatile ("lw %0, 32(sp)" : "=r" (reg_val));
      break;
    case 25: // s9
      __asm__ volatile ("lw %0, 36(sp)" : "=r" (reg_val));
      break;
    case 26: // s10
      __asm__ volatile ("lw %0, 40(sp)" : "=r" (reg_val));
      break;
    case 27: // s11
      __asm__ volatile ("lw %0, 44(sp)" : "=r" (reg_val));
      break;
    case 28: // t3
      __asm__ volatile ("lw %0, 96(sp)" : "=r" (reg_val));
      break;
    case 29: // t4
      __asm__ volatile ("lw %0, 100(sp)" : "=r" (reg_val));
      break;
    case 30: // t5
      __asm__ volatile ("lw %0, 104(sp)" : "=r" (reg_val));
      break;
    case 31: // t6
      __asm__ volatile ("lw %0, 108(sp)" : "=r" (reg_val));
      break;
    default: // zero
      __asm__ volatile ("mv %0, x0" : "=r" (reg_val));
      break;
  }

  return reg_val;
}

inline __attribute__((always_inline)) void store_reg_value(uint8_t reg, uint32_t reg_val) {
  // Store the reg value on the stack for the saved regs

  switch(reg) {  // ra, sp, gp and tp use is prohibited
    case 5: // t0
      __asm__ volatile ("sw %0, 84(sp)" :: "r" (reg_val));
      break;
    case 6: // t1
      __asm__ volatile ("sw %0, 88(sp)" :: "r" (reg_val));
      break;
    case 7: // t2
      __asm__ volatile ("sw %0, 92(sp)" :: "r" (reg_val));
      break;
    case 8: // fp
      __asm__ volatile ("sw %0, 0(sp)" :: "r" (reg_val));
      break;
    case 9: // s1
      __asm__ volatile ("sw %0, 4(sp)" :: "r" (reg_val));
      break;
    case 10: // a0
      __asm__ volatile ("sw %0, 52(sp)" :: "r" (reg_val));
      break;
    case 11: // a1
      __asm__ volatile ("sw %0, 56(sp)" :: "r" (reg_val));
      break;
    case 12: // a2
      __asm__ volatile ("sw %0, 60(sp)" :: "r" (reg_val));
      break;
    case 13: // a3
      __asm__ volatile ("sw %0, 64(sp)" :: "r" (reg_val));
      break;
    case 14: // a4
      __asm__ volatile ("sw %0, 68(sp)" :: "r" (reg_val));
      break;
    case 15: // a5
      __asm__ volatile ("sw %0, 72(sp)" :: "r" (reg_val));
      break;
    case 16: // a6
      __asm__ volatile ("sw %0, 76(sp)" :: "r" (reg_val));
      break;
    case 17: // a7
      __asm__ volatile ("sw %0, 80(sp)" :: "r" (reg_val));
      break;
    case 18: // s2
      __asm__ volatile ("sw %0, 8(sp)" :: "r" (reg_val));
      break;
    case 19: // s3
      __asm__ volatile ("sw %0, 12(sp)" :: "r" (reg_val));
      break;
    case 20: // s4
      __asm__ volatile ("sw %0, 16(sp)" :: "r" (reg_val));
      break;
    case 21: // s5
      __asm__ volatile ("sw %0, 20(sp)" :: "r" (reg_val));
      break;
    case 22: // s6
      __asm__ volatile ("sw %0, 24(sp)" :: "r" (reg_val));
      break;
    case 23: // s7
      __asm__ volatile ("sw %0, 28(sp)" :: "r" (reg_val));
      break;
    case 24: // s8
      __asm__ volatile ("sw %0, 32(sp)" :: "r" (reg_val));
      break;
    case 25: // s9
      __asm__ volatile ("sw %0, 36(sp)" :: "r" (reg_val));
      break;
    case 26: // s10
      __asm__ volatile ("sw %0, 40(sp)" :: "r" (reg_val));
      break;
    case 27: // s11
      __asm__ volatile ("sw %0, 44(sp)" :: "r" (reg_val));
      break;
    case 28: // t3
      __asm__ volatile ("sw %0, 96(sp)" :: "r" (reg_val));
      break;
    case 29: // t4
      __asm__ volatile ("sw %0, 100(sp)" :: "r" (reg_val));
      break;
    case 30: // t5
      __asm__ volatile ("sw %0, 104(sp)" :: "r" (reg_val));
      break;
    case 31: // t6
      __asm__ volatile ("sw %0, 108(sp)" :: "r" (reg_val));
      break;
    default:
      break;
  }
}

void soft_illegal_insn(uint32_t rs1, uint32_t rs2, uint32_t insn) {
  uint32_t rd = 0;
  uint32_t rd_valid = 1;
  uint32_t mip;
  __asm__ volatile ("csrr %0, mip" : "=r" (mip));
  bool fabric_irq_pending = mip&(1<<FABRIC_IRQ);
  bool fabric_busy = (*REG_FABRIC_CONFIG&(1<<FABRIC_CONFIG_BUSY)) | fabric_irq_pending;

  switch (insn&0x600707f)
  {
    case ((WARMBOOT0_LEFTSHIFT_FUNC3<<12)|SLOT_OPCODE): // Slot 2 Left shift
      if (!fabric_busy && ((loaded_slots[0] == WARMBOOT0_STATIC_FULL_USERCODE) || (loaded_slots[0] == WARMBOOT0_STATIC_USERCODE))) {
        *REG_TRIGGER_SLOT = WARMBOOT0_LEFTSHIFT_USERCODE;
      }

      rd = rs1 << rs2;
      break;

    case ((WARMBOOT0_RIGHTSHIFT_FUNC3<<12)|SLOT_OPCODE):  // Slot 2 Right shift
      if (!fabric_busy && ((loaded_slots[0] == WARMBOOT0_STATIC_FULL_USERCODE) || (loaded_slots[0] == WARMBOOT0_STATIC_USERCODE))) {
        *REG_TRIGGER_SLOT = WARMBOOT0_RIGHTSHIFT_USERCODE;
      }

      rd = rs1 >> rs2;
      break;

    case ((WARMBOOT1_COMBINE_FUNC7<<25)|SLOT_OPCODE): // Slot 1_2 combine
      if (!fabric_busy) {
        if ((loaded_slots[0] == WARMBOOT1_STATIC_FULL_USERCODE) || (loaded_slots[0] == WARMBOOT1_STATIC_USERCODE)) {
          if (merged_slot == 1) {
            merged_slot = 2;
            *REG_FABRIC_CONFIG |= 0x1c<<FABRIC_CONFIG_COL_OFFSET; // -4
          } else if (merged_slot == 2){
            merged_slot = 1;
          }
          *REG_TRIGGER_SLOT = WARMBOOT1_COMBINE_USERCODE;
        } else {
          *REG_TRIGGER_SLOT = WARMBOOT1_STATIC_USERCODE;
        }
      }

      rd = ((rs1&0x3)<<2) | (rs2&0x3);

      if (loaded_slots[1] == WARMBOOT1_COMBINE_USERCODE) {
        rd <<= 4;
      }
      break;

    case ((WARMBOOT1_FUNCTION_FUNC7<<25)|SLOT_OPCODE): // Slot 1_2 function
      if (!fabric_busy) {
        if ((loaded_slots[0] == WARMBOOT1_STATIC_FULL_USERCODE) || (loaded_slots[0] == WARMBOOT1_STATIC_USERCODE)) {
          if (merged_slot == 1) {
            merged_slot = 2;
            *REG_FABRIC_CONFIG |= 0x1c<<FABRIC_CONFIG_COL_OFFSET; // -4
          } else if (merged_slot == 2){
            merged_slot = 1;
          }
          *REG_TRIGGER_SLOT = WARMBOOT1_FUNCTION_USERCODE;
        } else {
          *REG_TRIGGER_SLOT = WARMBOOT1_STATIC_USERCODE;
        }
      }
      
      switch(rs1&0x7) {
        case 0:
          rd = rs2;
          break;
        case 1:
          rd = ~rs2;
          break;
        case 2:
          rd = ((rs2&0x1)<<3) | ((rs2&0x2)<<1) | ((rs2&0x4)>>1)| ((rs2&0x8)>>3);
          break;
        case 3:
          rd = ((rs2&0x1)<<3) | ((rs2&0x8)>>1) | (rs2&0x2)| ((rs2&0x4)>>2);
          break;
        case 4:
          rd = ((rs2&0x7)<<1) | ((rs2&0x8)>>3);
          break;
        case 5:
          rd = ((rs2&0x1)<<3) | ((rs2&0xe)>>1);
          break;
        case 6:
          rd = rs2+1;
          break;
        case 7:
          rd = rs2+rs2;
          break;
      }

      if (loaded_slots[1] == WARMBOOT1_FUNCTION_USERCODE) {
        rd <<= 4;
      }
      break;

    case ((WARMBOOT1_INTERLEAVE_FUNC7<<25)|SLOT_OPCODE): // Slot 1_2 interleave
      if (!fabric_busy) {
        if ((loaded_slots[0] == WARMBOOT1_STATIC_FULL_USERCODE) || (loaded_slots[0] == WARMBOOT1_STATIC_USERCODE)) {
          if (merged_slot == 1) {
            merged_slot = 2;
            *REG_FABRIC_CONFIG |= 0x1c<<FABRIC_CONFIG_COL_OFFSET; // -4
          } else if (merged_slot == 2){
            merged_slot = 1;
          }
          *REG_TRIGGER_SLOT = WARMBOOT1_INTERLEAVE_USERCODE;
        } else {
          *REG_TRIGGER_SLOT = WARMBOOT1_STATIC_USERCODE;
        }
      }
      
      rd = ((rs1&0x2)<<2) | ((rs2&0x2)<<1) | ((rs1&0x1)<<1) | ((rs2&0x1));

      if (loaded_slots[1] == WARMBOOT1_INTERLEAVE_USERCODE) {
        rd <<= 4;
      }
      break;

    default:
      printf("Illegal instruction!\n");
      rd_valid = 0;
      break;
  }

  __asm__ volatile ("mv a0, %0" :: "r" (rd) : "a0");
  __asm__ volatile ("mv a1, %0" :: "r" (rd_valid) : "a1");
}

__attribute__((naked)) void handle_illegal_insn() {
  // Mostly used to wrap and prepare for software execution
  // Naked function so sp does not move when called from insn handler. 
  // No stack initialized in this function, all vars used are traceable to asm reg statements.
  // Get and return reg functions are always inlined so only regs are used. 
  // The software function implementation is wrapped in a function so the stack can be used.

  // Save all callee registers
  __asm__ volatile ("addi sp, sp, -48\n\t"
                    "sw s0, 0(sp)\n\t"
                    "sw s1, 4(sp)\n\t"
                    "sw s2, 8(sp)\n\t"
                    "sw s3, 12(sp)\n\t"
                    "sw s4, 16(sp)\n\t"
                    "sw s5, 20(sp)\n\t"
                    "sw s6, 24(sp)\n\t"
                    "sw s7, 28(sp)\n\t"
                    "sw s8, 32(sp)\n\t"
                    "sw s9, 36(sp)\n\t"
                    "sw s10, 40(sp)\n\t"
                    "sw s11, 44(sp)");

  // mepc points to failing instruction, mtval does not contain instruction on this cpu
  uint32_t* insn_addr;
  __asm__ volatile ("csrr %0, mepc" : "=r" (insn_addr));

  if (((*insn_addr)&0x7f) == SLOT_OPCODE) {
    uint32_t rs1 = load_reg_value((*insn_addr&0xf8000) >> 15);
    uint32_t rs2 = load_reg_value((*insn_addr&0x1f00000) >> 20);
    // Use a0 and a1 to return values, so no stack is used
    soft_illegal_insn(rs1, rs2, *insn_addr); // Do software instr.

    uint32_t rd;
    uint32_t rd_valid;
    __asm__ volatile ("mv %0, a0" : "=r" (rd));
    __asm__ volatile ("mv %0, a1" : "=r" (rd_valid));

    if (rd_valid) {
      store_reg_value((*insn_addr&0xf80) >> 7, rd); // Store result, where it would be expected
    }
  } else {
    printf("Illegal instruction!\n");
  }

  // Restore used callee registers and jump to mepc exit handler
  __asm__ volatile ("lw s0, 0(sp)\n\t"
                    "lw s1, 4(sp)\n\t"
                    "lw s2, 8(sp)\n\t"
                    "lw s3, 12(sp)\n\t"
                    "lw s4, 16(sp)\n\t"
                    "lw s5, 20(sp)\n\t"
                    "lw s6, 24(sp)\n\t"
                    "lw s7, 28(sp)\n\t"
                    "lw s8, 32(sp)\n\t"
                    "lw s9, 36(sp)\n\t"
                    "lw s10, 40(sp)\n\t"
                    "lw s11, 44(sp)\n\t"
                    "addi sp, sp, 48\n\t"
                    "j end_handler_incr_mepc"
                    :::"s0", "s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8", "s9", "s10", "s11");
}

// FPGA config handler
__attribute__ ((interrupt ("machine"))) void m_fast5_irq_handler() {
  *REG_FABRIC_CONFIG |= (1<<FABRIC_CONFIG_ACK);
  triggered_irq++;

  uint8_t slot1_2_func7 = 0x3;

  switch (*REG_USERCODE&0x7fff)
  {
    // Static Slot
    case (WARMBOOT1_STATIC_FULL_USERCODE&0x7fff):
    case (WARMBOOT1_STATIC_USERCODE&0x7fff):
      warmboot1_set_provided(0x3, 0x3, 0x3);
    case (WARMBOOT0_STATIC_FULL_USERCODE&0x7fff):
    case (WARMBOOT0_STATIC_USERCODE&0x7fff):
      loaded_slots[0] = *REG_USERCODE;
      loaded_slots[1] = 0;
      loaded_slots[2] = 0;
      loaded_slots[3] = 0;
      break;
  
    // Slot1
    case (WARMBOOT0_DIRECTOUT_USERCODE&0x7fff):
    case (WARMBOOT0_GRAYCODE_USERCODE&0x7fff):
      loaded_slots[1] = *REG_USERCODE;
      break;

    // Slot2
    case (WARMBOOT0_LEFTSHIFT_USERCODE&0x7fff):
    case (WARMBOOT0_RIGHTSHIFT_USERCODE&0x7fff):
      loaded_slots[2] = *REG_USERCODE;
      break;

    // Slot3
    case (WARMBOOT0_CROSSOVER_USERCODE&0x7fff):
    case (WARMBOOT0_STRAIGHTTHROUGH_USERCODE&0x7fff):
      loaded_slots[3] = *REG_USERCODE;
      break;

    // Slot1_2
    case (WARMBOOT1_COMBINE_USERCODE&0x7fff):
      slot1_2_func7--;
    case (WARMBOOT1_FUNCTION_USERCODE&0x7fff):
      slot1_2_func7--;
    case (WARMBOOT1_INTERLEAVE_USERCODE&0x7fff):
      slot1_2_func7--;

      if (merged_slot == 1) {
        loaded_slots[1] = *REG_USERCODE;
        warmboot1_set_provided(slot1_2_func7, 0x3, 0x1);
      } else if (merged_slot == 2) {
        loaded_slots[2] = *REG_USERCODE;
        warmboot1_set_provided(0x3, slot1_2_func7, 0x2);
      } else {
        printf("No such merged slot\n");
      }
      break;

    default:
      printf("No such slot\n");
      break;
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

  *REG_FABRIC_CONFIG = 0x6<<FABRIC_CONFIG_SLOT_OFFSET;

  // enable machine mode interrupts, mstatus.mie
  __asm__ volatile ("csrs mstatus, 0x8");

  // enable fabric interrupt
  int enable_fpga_configured_interrupt = (1<<FABRIC_IRQ);
  __asm__ volatile ("csrs mie, %0" :: "r" (enable_fpga_configured_interrupt));

  for (uint8_t i = 0; i < 13; i++) { // TODO retest and recheckout 2 slots must set funct3 in interrupt
    switch (i)
    {
      default:
        // Wait for Static slot
        break;
      
      case 1: // TODO Test waited
        *REG_TRIGGER_SLOT = WARMBOOT0_DIRECTOUT_USERCODE;
        break;
        
      case 2: // TODO Test waited
        *REG_TRIGGER_SLOT = WARMBOOT0_STRAIGHTTHROUGH_USERCODE;
        break;

      case 3: // XIF must be initialized, to prevent stalling and force illegal instruction exceptions // TODO Test waited
        *REG_TRIGGER_SLOT = WARMBOOT0_LEFTSHIFT_USERCODE;
        break;

      case 4: // TODO Test IO out and left shift printf
        test_io();
        *REG_TRIGGER_SLOT = WARMBOOT0_CROSSOVER_USERCODE;

        printf("L1: %lx\n", warmboot0_left_shift(0xdeadbeef, 0x10)); // Ret 0xbeef0000
        wait_nop(0x10);
        printf("L2: %lx\n", warmboot0_left_shift(0xbeefdead, 0x5)); // Ret 0xddfbd5a0
        break;

      case 5: // TODO Test IO out and software substitution
        test_io();

        printf("R1: %lx\n", warmboot0_right_shift(0xdeadbeef, 0x3)); // Ret 0x1bd5b7dd
        wait_nop(0x10);
        printf("R2: %lx\n", warmboot0_right_shift(0xdeadbeef, 0x10)); // Ret 0x0000dead
        break;

      case 6: // TODO Test right shift print and software substitution
        printf("R3: %lx\n", warmboot0_right_shift(0xdeadbeef, 0x3)); // Ret 0x1bd5b7dd
        wait_nop(0x10);
        printf("L3: %lx\n", warmboot0_left_shift(0xbeefdead, 0x10)); // Ret 0xdead0000
        break;

      case 7: // TODO IO
        *REG_TRIGGER_SLOT = WARMBOOT0_GRAYCODE_USERCODE;
        break;

      case 8: // TODO IO and software substitution
        test_io();
        printf("I1: %x\n", warmboot1_interleave(0x3, 0x1)); // Ret 0xb
        break;

      case 9: // TODO check software substitution
        printf("L4: %lx\n", warmboot0_left_shift(0xbeefdead, 0x10)); // Ret 0xdead0000
        wait_nop(0x10);
        printf("C1: %x\n", warmboot1_combine(0x1, 0x3)); // Ret 0x7
        break;

      case 10: // TODO check combine and software substitution
        printf("C2: %x\n", warmboot1_combine(0x1, 0x3)); // Ret 0x7
        wait_nop(0x10);
        printf("I2: %x\n", warmboot1_interleave(0x3, 0x1)); // Ret 0xb
        break;

      case 11: // TODO check combine, interleave, function software substitution and if interleave works while other slot reconfigures
        printf("C3: %x\n", warmboot1_combine(0x1, 0x3)); // Ret 0x7
        wait_nop(0x10);
        printf("I3: %x\n", warmboot1_interleave(0x3, 0x1)); // Ret 0xb
        wait_nop(0x10);
        printf("F1: %x\n", warmboot1_function(0x3, 0x1)); // Ret 0x8
        wait_nop(0x10);
        printf("I4: %x\n", warmboot1_interleave(0x3, 0x1)); // Ret 0xb
        break;

      case 12: // TODO check function, interleave, right_shift software substitution
        printf("F2: %x\n", warmboot1_function(0x1, 0x3)); // Ret 0xc
        wait_nop(0x10);
        printf("F3: %x\n", warmboot1_function(0x2, 0x7)); // Ret 0xe
        wait_nop(0x10);
        printf("F4: %x\n", warmboot1_function(0x2, 0x6)); // Ret 0x6
        wait_nop(0x10);
        printf("F5: %x\n", warmboot1_function(0xb, 0x4)); // Ret 0x1
        wait_nop(0x10);
        printf("I5: %x\n", warmboot1_interleave(0x3, 0x1)); // Ret 0xb
        wait_nop(0x10);
        printf("R4: %lx\n", warmboot0_right_shift(0xdeadbeef, 0x3)); // Ret 0x1bd5b7dd
        triggered_irq++;
        break;
    }

    if (triggered_irq <= i) {
      // Wait for slot is configured interrupt
      __asm__ volatile ("wfi");
    }
  }

  // Trigger IOs zero TODO test if IOs are zero
  *REG_TRIGGER_SLOT = WARMBOOT2_ALLZEROS;
  __asm__ volatile ("wfi");
  printf("Finished\n");

  return 0;
}

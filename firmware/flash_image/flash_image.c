#include <stdio.h>
#include <stdint.h>
#include <soc.h>
#include <EF_UART.h>

#define F_CPU 50000000
#define BAUDRATE 115200

volatile uint32_t loaded_slots[4] = {0};
volatile uint8_t  merged_slot = 1; // TODO add controller functionality, look how to use it

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
    __asm__ volatile ("nop");
  }
}

// USERCODE for custom_instr/.board/bitstreams/Static-Full.bit changed to 0x00010000
// USERCODE for custom_instr/.board/bitstreams/Static-Static.bit changed to 0x00010009
// USERCODE for custom_instr/.board/bitstreams/Slot1-DirectOut.bit changed to 0x0001000b
// USERCODE for custom_instr/.board/bitstreams/Slot1-Graycode.bit changed to 0x0001000e
// USERCODE for custom_instr/.board/bitstreams/Slot2-LeftShift.bit changed to 0x00010011
// USERCODE for custom_instr/.board/bitstreams/Slot2-RightShift.bit changed to 0x00010014
// USERCODE for custom_instr/.board/bitstreams/Slot3-Crossover.bit changed to 0x00010017
// USERCODE for custom_instr/.board/bitstreams/Slot3-StraightThrough.bit changed to 0x00010019
// USERCODE for custom_instr_2slot/.board/bitstreams/Static-Full.bit changed to 0x00010200
// USERCODE for custom_instr_2slot/.board/bitstreams/Static-Static.bit changed to 0x00010209
// USERCODE for custom_instr_2slot/.board/bitstreams/Slot1_2-Combine.bit changed to 0x0001020d
// USERCODE for custom_instr_2slot/.board/bitstreams/Slot1_2-Function.bit changed to 0x0001020f
// USERCODE for custom_instr_2slot/.board/bitstreams/Slot1_2-Interleave.bit changed to 0x00010211

// System trap handler
inline __attribute__((always_inline)) uint32_t get_reg_value(uint8_t reg) {
  // Return the reg value, load caller saved regs from stack
  
  uint32_t reg_val;
  
  switch(reg) {
    case 0: // zero
      __asm__ volatile ("mv %0, x0" : "=r" (reg_val));
      break;
    case 1: // ra
      __asm__ volatile ("lw %0, 0(sp)" : "=r" (reg_val));
      break;
    case 2: // sp
      __asm__ volatile ("mv %0, x2" : "=r" (reg_val));
      break;
    case 3: // gp
      __asm__ volatile ("mv %0, x3" : "=r" (reg_val));
      break;
    case 4: // tp
      __asm__ volatile ("mv %0, x4" : "=r" (reg_val));
      break;
    case 5: // t0
      __asm__ volatile ("lw %0, 36(sp)" : "=r" (reg_val));
      break;
    case 6: // t1
      __asm__ volatile ("lw %0, 40(sp)" : "=r" (reg_val));
      break;
    case 7: // t2
      __asm__ volatile ("lw %0, 44(sp)" : "=r" (reg_val));
      break;
    case 8: // fp
      __asm__ volatile ("mv %0, x8" : "=r" (reg_val));
      break;
    case 9: // s1
      __asm__ volatile ("mv %0, x9" : "=r" (reg_val));
      break;
    case 10: // a0
      __asm__ volatile ("lw %0, 4(sp)" : "=r" (reg_val));
      break;
    case 11: // a1
      __asm__ volatile ("lw %0, 8(sp)" : "=r" (reg_val));
      break;
    case 12: // a2
      __asm__ volatile ("lw %0, 12(sp)" : "=r" (reg_val));
      break;
    case 13: // a3
      __asm__ volatile ("lw %0, 16(sp)" : "=r" (reg_val));
      break;
    case 14: // a4
      __asm__ volatile ("lw %0, 20(sp)" : "=r" (reg_val));
      break;
    case 15: // a5
      __asm__ volatile ("lw %0, 24(sp)" : "=r" (reg_val));
      break;
    case 16: // a6
      __asm__ volatile ("lw %0, 28(sp)" : "=r" (reg_val));
      break;
    case 17: // a7
      __asm__ volatile ("lw %0, 32(sp)" : "=r" (reg_val));
      break;
    case 18: // s2
      __asm__ volatile ("mv %0, x18" : "=r" (reg_val));
      break;
    case 19: // s3
      __asm__ volatile ("mv %0, x19" : "=r" (reg_val));
      break;
    case 20: // s4
      __asm__ volatile ("mv %0, x20" : "=r" (reg_val));
      break;
    case 21: // s5
      __asm__ volatile ("mv %0, x21" : "=r" (reg_val));
      break;
    case 22: // s6
      __asm__ volatile ("mv %0, x22" : "=r" (reg_val));
      break;
    case 23: // s7
      __asm__ volatile ("mv %0, x23" : "=r" (reg_val));
      break;
    case 24: // s8
      __asm__ volatile ("mv %0, x24" : "=r" (reg_val));
      break;
    case 25: // s9
      __asm__ volatile ("mv %0, x25" : "=r" (reg_val));
      break;
    case 26: // s10
      __asm__ volatile ("mv %0, x26" : "=r" (reg_val));
      break;
    case 27: // s11
      __asm__ volatile ("mv %0, x27" : "=r" (reg_val));
      break;
    case 28: // t3
      __asm__ volatile ("lw %0, 48(sp)" : "=r" (reg_val));
      break;
    case 29: // t4
      __asm__ volatile ("lw %0, 52(sp)" : "=r" (reg_val));
      break;
    case 30: // t5
      __asm__ volatile ("lw %0, 56(sp)" : "=r" (reg_val));
      break;
    case 31: // t6
      __asm__ volatile ("lw %0, 60(sp)" : "=r" (reg_val));
      break;
    default:
      break;
  }

  return reg_val;
}

inline __attribute__((always_inline)) void return_reg_value(uint8_t reg, uint32_t reg_val) {
  // Store the reg value in the wanted reg or on the stack for calle saved regs

  switch(reg) {
    case 1: // ra
      __asm__ volatile ("sw %0, 0(sp)" :: "r" (reg_val));
      break;
    case 2: // sp
      __asm__ volatile ("mv x2, %0" :: "r" (reg_val)); // sp cannot be clobbered
      break;
    case 3: // gp
      __asm__ volatile ("mv x3, %0" :: "r" (reg_val) : "x3");
      break;
    case 4: // tp
      __asm__ volatile ("mv x4, %0" :: "r" (reg_val) : "x4");
      break;
    case 5: // t0
      __asm__ volatile ("sw %0, 36(sp)" :: "r" (reg_val));
      break;
    case 6: // t1
      __asm__ volatile ("sw %0, 40(sp)" :: "r" (reg_val));
      break;
    case 7: // t2
      __asm__ volatile ("sw %0, 44(sp)" :: "r" (reg_val));
      break;
    case 8: // fp
      __asm__ volatile ("mv x8, %0" :: "r" (reg_val) : "x8");
      break;
    case 9: // s1
      __asm__ volatile ("mv x9, %0" :: "r" (reg_val) : "x9");
      break;
    case 10: // a0
      __asm__ volatile ("sw %0, 4(sp)" :: "r" (reg_val));
      break;
    case 11: // a1
      __asm__ volatile ("sw %0, 8(sp)" :: "r" (reg_val));
      break;
    case 12: // a2
      __asm__ volatile ("sw %0, 12(sp)" :: "r" (reg_val));
      break;
    case 13: // a3
      __asm__ volatile ("sw %0, 16(sp)" :: "r" (reg_val));
      break;
    case 14: // a4
      __asm__ volatile ("sw %0, 20(sp)" :: "r" (reg_val));
      break;
    case 15: // a5
      __asm__ volatile ("sw %0, 24(sp)" :: "r" (reg_val));
      break;
    case 16: // a6
      __asm__ volatile ("sw %0, 28(sp)" :: "r" (reg_val));
      break;
    case 17: // a7
      __asm__ volatile ("sw %0, 32(sp)" :: "r" (reg_val));
      break;
    case 18: // s2
      __asm__ volatile ("mv x18, %0" :: "r" (reg_val) : "x18");
      break;
    case 19: // s3
      __asm__ volatile ("mv x19, %0" :: "r" (reg_val) : "x19");
      break;
    case 20: // s4
      __asm__ volatile ("mv x20, %0" :: "r" (reg_val) : "x20");
      break;
    case 21: // s5
      __asm__ volatile ("mv x21, %0" :: "r" (reg_val) : "x21");
      break;
    case 22: // s6
      __asm__ volatile ("mv x22, %0" :: "r" (reg_val) : "x22");
      break;
    case 23: // s7
      __asm__ volatile ("mv x23, %0" :: "r" (reg_val) : "x23");
      break;
    case 24: // s8
      __asm__ volatile ("mv x24, %0" :: "r" (reg_val) : "x24");
      break;
    case 25: // s9
      __asm__ volatile ("mv x25, %0" :: "r" (reg_val) : "x25");
      break;
    case 26: // s10
      __asm__ volatile ("mv x26, %0" :: "r" (reg_val) : "x26");
      break;
    case 27: // s11
      __asm__ volatile ("mv x27, %0" :: "r" (reg_val) : "x27");
      break;
    case 28: // t3
      __asm__ volatile ("sw %0, 48(sp)" :: "r" (reg_val));
      break;
    case 29: // t4
      __asm__ volatile ("sw %0, 52(sp)" :: "r" (reg_val));
      break;
    case 30: // t5
      __asm__ volatile ("sw %0, 56(sp)" :: "r" (reg_val));
      break;
    case 31: // t6
      __asm__ volatile ("sw %0, 60(sp)" :: "r" (reg_val));
      break;
    default:
      break;
  }
}

void soft_illegal_insn(uint32_t rs1, uint32_t rs2, uint32_t insn) {
  uint32_t rd = 0;
  uint32_t rd_valid = 1;

  printf("INSN: 0x%08lx\n", insn);

  switch (insn&0x707f)
  {
    case 0x105b: // Slot 2 Left shift
      if (!*REG_FABRIC_CONFIG_BUSY) {
        *REG_TRIGGER_SLOT = 0x11;
      }

      rd = rs1 << rs2;
      break;

    case 0x205b:  // Slot 2 Right shift
      if (!*REG_FABRIC_CONFIG_BUSY) {
        *REG_TRIGGER_SLOT = 0x14;
      }

      rd = rs1 >> rs2;
      break;

    case 0x305b: // Slot 1_2 combine
      if (!*REG_FABRIC_CONFIG_BUSY) {
        if (merged_slot == 1) {
          merged_slot = 2;
        } else if (merged_slot == 2){
          merged_slot = 1;
        }
        *REG_TRIGGER_SLOT = 0x20d;
      }

      rd = ((rs1&0x3)<<2) | (rs2&0x3);
      break;

    case 0x405b: // Slot 1_2 interleave
      if (!*REG_FABRIC_CONFIG_BUSY) {
        if (merged_slot == 1) {
          merged_slot = 2;
        } else if (merged_slot == 2){
          merged_slot = 1;
        }
        *REG_TRIGGER_SLOT = 0x20f;
      }
      
      rd = ((rs1&0x2)<<2) | ((rs2&0x2)<<1) | ((rs1&0x1)<<1) | ((rs2&0x1));
      break;

    case 0x505b: // Slot 1_2 function
      if (!*REG_FABRIC_CONFIG_BUSY) {
        if (merged_slot == 1) {
          merged_slot = 2;
        } else if (merged_slot == 2){
          merged_slot = 1;
        }
        *REG_TRIGGER_SLOT = 0x211;
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

  // Save used callee reg
  __asm__ volatile ("addi sp, sp, -4\n\t"
                    "sw s1, 64(sp)");

  // mepc points to failing instruction, mtval does not contain instruction on this cpu
  register uint32_t* insn_addr asm ("s1"); // Use callee saved reg, can be used after function call
  __asm__ volatile ("csrr %0, mepc" : "=r" (insn_addr));

  if (((*insn_addr)&0x7f) == 0x5b) {
    register uint32_t rs1 asm ("a0") = get_reg_value((*insn_addr&0xf8000) >> 14);
    register uint32_t rs2 asm ("a1") = get_reg_value((*insn_addr&0x1f00000) >> 19);
    // Use a0 and a1 to return values, so no stack is used
    soft_illegal_insn(rs1, rs2, *insn_addr); // Do software instr.

    register uint32_t rd asm ("t0");
    register uint32_t rd_valid asm ("t1");
    __asm__ volatile ("mv %0, a0" : "=r" (rd));
    __asm__ volatile ("mv %0, a1" : "=r" (rd_valid));

    if (rd_valid) {
      return_reg_value((*insn_addr&0xf80) >> 6, rd); // Store result, where it would be expected
    }
  } else {
    printf("Illegal instruction!\n");
  }

  // Restore used callee reg and jump to mepc exit handler
  __asm__ volatile ("lw s1, 64(sp)\n\t"
                    "addi sp, sp, 4\n\t"
                    "j end_handler_incr_mepc"
                    :::"s1");
}

// FPGA config handler
void m_fast5_irq_handler() {
  printf("Interrupt!\n");

  switch (*REG_USERCODE&0x7fff)
  {
    // Static Slot
    case 0x0:
    case 0x9:
    case 0x200:
    case 0x209:
      loaded_slots[0] = *REG_USERCODE;
      loaded_slots[1] = 0;
      loaded_slots[2] = 0;
      loaded_slots[3] = 0;
      break;
  
    // Slot1
    case 0xb:
    case 0xe:
      loaded_slots[1] = *REG_USERCODE;
      break;

    // Slot2
    case 0x11:
    case 0x14:
      loaded_slots[2] = *REG_USERCODE;
      break;

    // Slot3
    case 0x17:
    case 0x19:
      loaded_slots[3] = *REG_USERCODE;
      break;

    // Slot1_2
    case 0x20d:
    case 0x20f:
    case 0x211:
      if (merged_slot == 1) {
        loaded_slots[1] = *REG_USERCODE;
      } else if (merged_slot == 2) {
        loaded_slots[2] = *REG_USERCODE;
      } else {
        printf("No such slot merged\n");
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

  *REG_WARMBOOT_OFFSET = 0x20;

  // enable machine mode interrupts, mstatus.mie
  __asm__ volatile ("csrs mstatus, 0x8");

  // enable fast interrupts 0-3
  int enable_fpga_configured_interrupt = 0x00200000;
  __asm__ volatile ("csrs mie, %0" :: "r" (enable_fpga_configured_interrupt));

  for (uint8_t i = 0; i < 8; i++) { // TODO
    switch (i)
    {
      case 0:
        // Wait for Static slot
        break;
      
      case 1:
        *REG_TRIGGER_SLOT = 0x0001000b;
        break;
        
      case 2:
        *REG_TRIGGER_SLOT = 0x00010019;
        break;

      case 3:
        left_shift(0xdeadbeef, 0x10);
        break;

      default:
        break;
    }

    printf("Slots - 0:0x%08lx 1:0x%08lx 2:0x%08lx 3:0x%08lx\n", loaded_slots[0], loaded_slots[1], loaded_slots[2], loaded_slots[3]);

    // Wait for slot is configured interrupt
    __asm__ volatile ("wfi");
  }

  printf("Finished\n");

  return 0;
}

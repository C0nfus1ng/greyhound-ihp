# SPDX-FileCopyrightText: © 2025 Leo Moser <leomoser99@gmail.com>
# SPDX-License-Identifier: Apache-2.0

import os
import random
import cocotb
from pathlib import Path
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles
from cocotb.triggers import Timer, Edge, RisingEdge, FallingEdge
from cocotb.regression import TestFactory
from cocotb_tools.runner import get_runner
from cocotbext.uart import UartSource, UartSink

from cocotbext.spi import SpiBus, SpiConfig, SpiMaster

fpga_blinky = {
    'flash0_slot0': '',
    'flash0_slot1': '',
    'flash1_slot0': '../../../ip/fabulous_fabric/fabric_ihp/user_designs/trigger_slot1/trigger_slot1.hex',
    'flash1_slot1': '../../../ip/fabulous_fabric/fabric_ihp/user_designs/trigger_slot0/trigger_slot0.hex',
    'connect_flash1': True,
    'dump_waveforms': False,
}

partial = {
    'flash0_slot0': '../../../firmware/partial/partial.hex',
    'flash0_slot1': '',
    'flash1_slot0': '',
    'flash1_slot1': '',
    'connect_flash1': False,
    'dump_waveforms': True,
}

partial_2slots = {
    'flash0_slot0': '../../../firmware/partial_2slots/partial_2slots.hex',
    'flash0_slot1': '',
    'flash1_slot0': '',
    'flash1_slot1': '',
    'connect_flash1': False,
    'dump_waveforms': True,
}

enabled = partial

async def start_clock(clock, freq=50):
    """ Start the clock @ freq MHz """
    c = Clock(clock, 1/freq*1000, 'ns')
    await cocotb.start(c.start())

async def reset(reset, active_low=True, time_ns=1000):
    """ Reset dut """
    cocotb.log.info("Reset asserted...")
    
    reset.value = not active_low
    await Timer(time_ns, "ns")
    reset.value = active_low
    
    cocotb.log.info("Reset deasserted.")

async def start_up(dut):
    """ Startup sequence """
    await start_clock(dut.io_clock_PAD)
    await reset(dut.io_reset_PAD)

@cocotb.test(skip=enabled!=fpga_blinky)
async def test_fpga_blinky(dut):
    """Alternate between two bistreams in slot 0 and slot 1"""

    # Static setup
    dut.io_fetch_enable_PAD.value = 0
    dut.io_fpga_mode_PAD.value = 0 # Configure FPGA as controller

    # Start up
    await start_up(dut)
    
    print("Waiting for configuration to start.")
    await RisingEdge( dut.io_config_busy_PAD)
    print("Waiting for configuration to end.")
    await FallingEdge(dut.io_config_busy_PAD)
    
    print("FPGA configured!")
    
    await ClockCycles(dut.io_clock_PAD, 10)
    assert(dut.io_gpio_PAD.value == 0x00000000)
    
    print("Waiting for configuration to start.")
    await RisingEdge( dut.io_config_busy_PAD)
    print("Waiting for configuration to end.")
    await FallingEdge(dut.io_config_busy_PAD)
    
    print("FPGA configured!")
    
    await ClockCycles(dut.io_clock_PAD, 10)
    assert(dut.io_gpio_PAD.value == 0xFFFFFFFF)
    
    print("Waiting for configuration to start.")
    await RisingEdge( dut.io_config_busy_PAD)
    print("Waiting for configuration to end.")
    await FallingEdge(dut.io_config_busy_PAD)
    
    print("FPGA configured!")
    
    await ClockCycles(dut.io_clock_PAD, 10)
    assert(dut.io_gpio_PAD.value == 0x00000000)

@cocotb.test(skip=enabled!=partial)
async def test_partial(dut):
    """Run the "Partial" program"""

    # Static setup
    dut.io_fetch_enable_PAD.value = 1
    dut.io_fpga_mode_PAD.value = 1 # Configure FPGA as receiver

    # Start up
    await start_up(dut)

    # Wait for first 3 slots to upload
    await FallingEdge(dut.io_config_busy_PAD)
    await FallingEdge(dut.io_config_busy_PAD)
    await FallingEdge(dut.io_config_busy_PAD)
    cocotb.log.info(f"ASSERT VAL = {dut.io_gpio_PAD.value}")
    assert(dut.io_gpio_PAD.value == 0x0)
    await ClockCycles(dut.io_clock_PAD, int(50*30)) # 30µs
    cocotb.log.info(f"ASSERT VAL = {dut.io_gpio_PAD.value}")
    assert(dut.io_gpio_PAD.value == 0x9)
    await ClockCycles(dut.io_clock_PAD, int(50*10)) # 10µs
    cocotb.log.info(f"ASSERT VAL = {dut.io_gpio_PAD.value}")
    assert(dut.io_gpio_PAD.value == 0xA)
    await ClockCycles(dut.io_clock_PAD, int(50*10)) # 10µs
    cocotb.log.info(f"ASSERT VAL = {dut.io_gpio_PAD.value}")
    assert(dut.io_gpio_PAD.value == 0xB)
    
    # Wait to reconfigure to crossover slot
    await FallingEdge(dut.io_config_busy_PAD)
    await ClockCycles(dut.io_clock_PAD, int(50*5)) # 5µs
    cocotb.log.info(f"ASSERT VAL = {dut.io_gpio_PAD.value}")
    assert(dut.io_gpio_PAD.value == 0x0)
    await ClockCycles(dut.io_clock_PAD, int(50*10)) # 10µs
    cocotb.log.info(f"ASSERT VAL = {dut.io_gpio_PAD.value}")
    assert(dut.io_gpio_PAD.value == 0x9000_0000)
    await ClockCycles(dut.io_clock_PAD, int(50*10)) # 10µs
    cocotb.log.info(f"ASSERT VAL = {dut.io_gpio_PAD.value}")
    assert(dut.io_gpio_PAD.value == 0x5000_0000)
    await ClockCycles(dut.io_clock_PAD, int(50*10)) # 10µs
    cocotb.log.info(f"ASSERT VAL = {dut.io_gpio_PAD.value}")
    assert(dut.io_gpio_PAD.value == 0xD000_0000)

    # Wait for first Xif instr
    await FallingEdge(dut.io_config_busy_PAD)
    await ClockCycles(dut.io_clock_PAD, int(50*10)) # 10µs
    cocotb.log.info(f"ASSERT VAL = {dut.io_gpio_PAD.value}")
    assert(dut.io_gpio_PAD.value == 0x7E47_9201)

    # Wait for second Xif instr
    await FallingEdge(dut.io_config_busy_PAD)
    await ClockCycles(dut.io_clock_PAD, int(50*10)) # 1µs
    cocotb.log.info(f"ASSERT VAL = {dut.io_gpio_PAD.value}")
    assert(dut.io_gpio_PAD.value == 0xC06D_1341)

    # Wait for third Xif instr
    await FallingEdge(dut.io_config_busy_PAD)
    await ClockCycles(dut.io_clock_PAD, int(50*10)) # 1µs
    cocotb.log.info(f"ASSERT VAL = {dut.io_gpio_PAD.value}")
    assert(dut.io_gpio_PAD.value == 0x9C06_D134)

    # Wait for fourth Xif instr
    await FallingEdge(dut.io_config_busy_PAD)
    await FallingEdge(dut.io_clock_PAD)
    await FallingEdge(dut.io_clock_PAD)
    cocotb.log.info(f"ASSERT VAL = {dut.io_gpio_PAD.value}")
    assert(dut.io_gpio_PAD.value == 0x07E5_E727)
    await FallingEdge(dut.io_clock_PAD)
    cocotb.log.info(f"ASSERT VAL = {dut.io_gpio_PAD.value}")
    assert(dut.io_gpio_PAD.value == 0xE5E7_2702)
    await FallingEdge(dut.io_clock_PAD)
    cocotb.log.info(f"ASSERT VAL = {dut.io_gpio_PAD.value}")
    assert(dut.io_gpio_PAD.value == 0xE727_0200)
    await FallingEdge(dut.io_clock_PAD)
    cocotb.log.info(f"ASSERT VAL = {dut.io_gpio_PAD.value}")
    assert(dut.io_gpio_PAD.value == 0x2702_001E)
    await FallingEdge(dut.io_clock_PAD)
    cocotb.log.info(f"ASSERT VAL = {dut.io_gpio_PAD.value}")
    assert(dut.io_gpio_PAD.value == 0x0)
    await FallingEdge(dut.io_clock_PAD)
    cocotb.log.info(f"ASSERT VAL = {dut.io_gpio_PAD.value}")
    assert(dut.io_gpio_PAD.value == 0x2)
    await FallingEdge(dut.io_clock_PAD)
    cocotb.log.info(f"ASSERT VAL = {dut.io_gpio_PAD.value}")
    assert(dut.io_gpio_PAD.value == 0x200)
    await FallingEdge(dut.io_clock_PAD)
    cocotb.log.info(f"ASSERT VAL = {dut.io_gpio_PAD.value}")
    assert(dut.io_gpio_PAD.value == 0x2_001E)
    await FallingEdge(dut.io_clock_PAD)
    cocotb.log.info(f"ASSERT VAL = {dut.io_gpio_PAD.value}")
    assert(dut.io_gpio_PAD.value == 0x0)
    
    await ClockCycles(dut.io_clock_PAD, int(50*1)) # 1us

@cocotb.test(skip=enabled!=partial_2slots)
async def test_partial_2slots(dut):
    """Run the "Partial 2slots" program"""

    # Static setup
    dut.io_fetch_enable_PAD.value = 1
    dut.io_fpga_mode_PAD.value = 1 # Configure FPGA as receiver

    # Start up
    await start_up(dut)
    
    # Wait for firts 3 slots to upload
    await FallingEdge(dut.io_config_busy_PAD)
    await FallingEdge(dut.io_config_busy_PAD)
    await FallingEdge(dut.io_config_busy_PAD)
    await ClockCycles(dut.io_clock_PAD, int(50*120)) # 120µs
    cocotb.log.info(f"ASSERT VAL = {dut.io_gpio_PAD.value}")
    assert(dut.io_gpio_PAD.value[7:0] == 0x59)

    # Wait for seconf Xif instr
    await FallingEdge(dut.io_config_busy_PAD)
    await ClockCycles(dut.io_clock_PAD, int(50*1)) # 1µs
    cocotb.log.info(f"ASSERT VAL = {dut.io_gpio_PAD.value}")
    assert(dut.io_gpio_PAD.value[7:0] == 0x99)

    # Wait for third Xif instr
    await FallingEdge(dut.io_config_busy_PAD)
    await ClockCycles(dut.io_clock_PAD, int(50*1)) # 1µs
    cocotb.log.info(f"ASSERT VAL = {dut.io_gpio_PAD.value}")
    assert(dut.io_gpio_PAD.value[7:0] == 0x95)

    await ClockCycles(dut.io_clock_PAD, int(50*1)) # 1us

if __name__ == "__main__":

    sim         = os.getenv("SIM", "icarus")
    pdk_root    = os.getenv("PDK_ROOT", "../../../greyhound_v2_base/IHP-Open-PDK/")
    pdk         = os.getenv("PDK", "ihp-sg13g2")
    scl         = os.getenv("SCL", "sg13g2_stdcell")
    gl          = os.getenv("GL", False)

    testbench_path = Path(__file__).resolve().parent
    
    includes = [testbench_path / '../../rtl/include']
    
    verilog_sources = [
        testbench_path / 'greyhound_ihp_top_tb.v',
        testbench_path / 'spiflash.v',
        testbench_path / 'spiflash_powered.v',
        
        # SRAM models
        Path(pdk_root).expanduser() / pdk / "libs.ref" / "sg13g2_sram" / "verilog" / "RM_IHPSG13_1P_1024x16_c2_bm_bist.v",
        Path(pdk_root).expanduser() / pdk / "libs.ref" / "sg13g2_sram" / "verilog" / "RM_IHPSG13_1P_core_behavioral_bm_bist.v",
        
        # IO Pad models
        Path(pdk_root).expanduser() / pdk / "libs.ref" / "sg13g2_io" / "verilog" / "sg13g2_io.v",
        
    ]
    defines = {}

    if gl:
        # SCL models
        verilog_sources.append(Path(pdk_root).expanduser() / pdk / "libs.ref" / scl / "verilog" / f"{scl}.v" )
        
        verilog_sources.append(testbench_path / '../../final/nl_edit/greyhound_ihp_top.nl.v')
        
        defines = {'FUNCTIONAL': True, 'UNIT_DELAY': '#0'}
    else:
        verilog_sources.extend([
            testbench_path / '../../src/greyhound_ihp_top.v',
            testbench_path / '../../src/greyhound_ihp.sv',
            testbench_path / '../../src/soc/greyhound_soc.v',
            testbench_path / '../../ip/cv32e40x/bhv/cv32e40x_sim_clock_gate.sv',
            
            testbench_path / '../../ip/EF_QSPI_XIP_CTRL/hdl/rtl/EF_QSPI_XIP_CTRL.v',
            testbench_path / '../../ip/EF_QSPI_XIP_CTRL/hdl/rtl/DMC.v',
            testbench_path / '../../ip/EF_QSPI_XIP_CTRL/hdl/rtl/bus_wrappers/EF_QSPI_XIP_CTRL_AHBL.v',

            testbench_path / '../../ip/EF_PSRAM_CTRL/hdl/rtl/EF_PSRAM_CTRL.v',
            testbench_path / '../../ip/EF_PSRAM_CTRL/hdl/rtl/bus_wrapper/EF_PSRAM_CTRL_AHBL.v',

            testbench_path / '../../ip/EF_UART/hdl/rtl/EF_UART.v',
            testbench_path / '../../ip/EF_UART/hdl/rtl/bus_wrappers/EF_UART_AHBL.v',

            testbench_path / '../../ip/EF_IP_UTIL/hdl/ef_util_lib.v',
            
            testbench_path / '../../ip/fabulous_fabric/fabric_ihp/rtl/fabric_wrapper.sv',
            testbench_path / '../../ip/fabulous_fabric/rtl/fabric_config.sv',
            testbench_path / '../../ip/fabulous_fabric/rtl/fabric_spi_receiver.sv',
            testbench_path / '../../ip/fabulous_fabric/rtl/fabric_spi_controller.sv',
        ])
        
        defines = {'RTL': True, 'FUNCTIONAL': True, 'UNIT_DELAY': '#0'}
        
    # Add FPGA fabric
    verilog_sources.append(testbench_path / f'../../ip/fabulous_fabric/fabric_ihp/macro/{pdk}/fabulous/eFPGA.v')

    # Add tiles
    TILES_ROOT = testbench_path / '../../ip/fabulous_fabric/fabulous_tiles/tiles'
    
    # DSP
    verilog_sources.append(f'{TILES_ROOT}/DSP/DSP.v')
    verilog_sources.append(f'{TILES_ROOT}/DSP/DSP_bot/DSP_bot.v')
    verilog_sources.append(f'{TILES_ROOT}/DSP/DSP_bot/DSP_bot_ConfigMem.v')
    verilog_sources.append(f'{TILES_ROOT}/DSP/DSP_bot/DSP_bot_switch_matrix.v')
    verilog_sources.append(f'{TILES_ROOT}/DSP/DSP_bot/MULADD.v')
    verilog_sources.append(f'{TILES_ROOT}/DSP/DSP_top/DSP_top.v')
    verilog_sources.append(f'{TILES_ROOT}/DSP/DSP_top/DSP_top_ConfigMem.v')
    verilog_sources.append(f'{TILES_ROOT}/DSP/DSP_top/DSP_top_switch_matrix.v')
    
    # LUT4AB
    verilog_sources.append(f'{TILES_ROOT}/LUT4AB/LUT4AB.v')
    verilog_sources.append(f'{TILES_ROOT}/LUT4AB/LUT4AB_ConfigMem.v')
    verilog_sources.append(f'{TILES_ROOT}/LUT4AB/LUT4AB_switch_matrix.v')
    verilog_sources.append(f'{TILES_ROOT}/LUT4AB/LUT4c_frame_config_dffesr.v')
    verilog_sources.append(f'{TILES_ROOT}/LUT4AB/MUX8LUT_frame_config_mux.v')
    
    # N_term_DSP
    verilog_sources.append(f'{TILES_ROOT}/N_term_DSP/N_term_DSP.v')
    verilog_sources.append(f'{TILES_ROOT}/N_term_DSP/N_term_DSP_ConfigMem.v')
    verilog_sources.append(f'{TILES_ROOT}/N_term_DSP/N_term_DSP_switch_matrix.v')
    
    # N_term_single
    verilog_sources.append(f'{TILES_ROOT}/N_term_single/N_term_single.v')
    verilog_sources.append(f'{TILES_ROOT}/N_term_single/N_term_single_ConfigMem.v')
    verilog_sources.append(f'{TILES_ROOT}/N_term_single/N_term_single_switch_matrix.v')
    
    # N_term_single2
    verilog_sources.append(f'{TILES_ROOT}/N_term_single2/N_term_single2.v')
    verilog_sources.append(f'{TILES_ROOT}/N_term_single2/N_term_single2_ConfigMem.v')
    verilog_sources.append(f'{TILES_ROOT}/N_term_single2/N_term_single2_switch_matrix.v')

    # RegFile
    verilog_sources.append(f'{TILES_ROOT}/RegFile/RegFile.v')
    verilog_sources.append(f'{TILES_ROOT}/RegFile/RegFile_ConfigMem.v')
    verilog_sources.append(f'{TILES_ROOT}/RegFile/RegFile_switch_matrix.v')
    verilog_sources.append(f'{TILES_ROOT}/RegFile/RegFile_32x4.v')
    
    # S_term_DSP
    verilog_sources.append(f'{TILES_ROOT}/S_term_DSP/S_term_DSP.v')
    verilog_sources.append(f'{TILES_ROOT}/S_term_DSP/S_term_DSP_ConfigMem.v')
    verilog_sources.append(f'{TILES_ROOT}/S_term_DSP/S_term_DSP_switch_matrix.v')
    
    # S_term_single
    verilog_sources.append(f'{TILES_ROOT}/S_term_single/S_term_single.v')
    verilog_sources.append(f'{TILES_ROOT}/S_term_single/S_term_single_ConfigMem.v')
    verilog_sources.append(f'{TILES_ROOT}/S_term_single/S_term_single_switch_matrix.v')

    # S_term_single2
    verilog_sources.append(f'{TILES_ROOT}/S_term_single2/S_term_single2.v')
    verilog_sources.append(f'{TILES_ROOT}/S_term_single2/S_term_single2_ConfigMem.v')
    verilog_sources.append(f'{TILES_ROOT}/S_term_single2/S_term_single2_switch_matrix.v')

    # W_IO
    verilog_sources.append(f'{TILES_ROOT}/W_IO/W_IO.v')
    verilog_sources.append(f'{TILES_ROOT}/W_IO/W_IO_ConfigMem.v')
    verilog_sources.append(f'{TILES_ROOT}/W_IO/W_IO_switch_matrix.v')
    verilog_sources.append(f'{TILES_ROOT}/W_IO/IO_1_bidirectional_frame_config_pass.v')
    verilog_sources.append(f'{TILES_ROOT}/W_IO/Config_access.v')

    # N_IO
    verilog_sources.append(f'{TILES_ROOT}/N_IO/N_IO.v')
    verilog_sources.append(f'{TILES_ROOT}/N_IO/N_IO_ConfigMem.v')
    verilog_sources.append(f'{TILES_ROOT}/N_IO/N_IO_switch_matrix.v')
    #verilog_sources.append(f'{TILES_ROOT}/N_IO/IO_1_bidirectional_frame_config_pass.v')
    #verilog_sources.append(f'{TILES_ROOT}/N_IO/Config_access.v')

    # S_WARMBOOT
    verilog_sources.append(f'{TILES_ROOT}/S_WARMBOOT/S_WARMBOOT.v')
    verilog_sources.append(f'{TILES_ROOT}/S_WARMBOOT/S_WARMBOOT_ConfigMem.v')
    verilog_sources.append(f'{TILES_ROOT}/S_WARMBOOT/S_WARMBOOT_switch_matrix.v')
    verilog_sources.append(f'{TILES_ROOT}/S_WARMBOOT/WARMBOOT.v')
    
    # S_CPU_IF
    verilog_sources.append(f'{TILES_ROOT}/S_CPU_IF/S_CPU_IF.v')
    verilog_sources.append(f'{TILES_ROOT}/S_CPU_IF/S_CPU_IF_ConfigMem.v')
    verilog_sources.append(f'{TILES_ROOT}/S_CPU_IF/S_CPU_IF_switch_matrix.v')
    verilog_sources.append(f'{TILES_ROOT}/S_CPU_IF/CPU_IF.v')

    # S_CPU_IRQ
    verilog_sources.append(f'{TILES_ROOT}/S_CPU_IRQ/S_CPU_IRQ.v')
    verilog_sources.append(f'{TILES_ROOT}/S_CPU_IRQ/S_CPU_IRQ_ConfigMem.v')
    verilog_sources.append(f'{TILES_ROOT}/S_CPU_IRQ/S_CPU_IRQ_switch_matrix.v')
    verilog_sources.append(f'{TILES_ROOT}/S_CPU_IRQ/CPU_IRQ.v')

    # IHP_SRAM
    verilog_sources.append(f'{TILES_ROOT}/IHP_SRAM/IHP_SRAM.v')
    verilog_sources.append(f'{TILES_ROOT}/IHP_SRAM/IHP_SRAM_bot/IHP_SRAM_bot.v')
    verilog_sources.append(f'{TILES_ROOT}/IHP_SRAM/IHP_SRAM_bot/IHP_SRAM_bot_ConfigMem.v')
    verilog_sources.append(f'{TILES_ROOT}/IHP_SRAM/IHP_SRAM_bot/IHP_SRAM_bot_switch_matrix.v')
    verilog_sources.append(f'{TILES_ROOT}/IHP_SRAM/IHP_SRAM_bot/IHP_SRAM_1024x32.v')
    verilog_sources.append(f'{TILES_ROOT}/IHP_SRAM/IHP_SRAM_top/IHP_SRAM_top.v')
    verilog_sources.append(f'{TILES_ROOT}/IHP_SRAM/IHP_SRAM_top/IHP_SRAM_top_ConfigMem.v')
    verilog_sources.append(f'{TILES_ROOT}/IHP_SRAM/IHP_SRAM_top/IHP_SRAM_top_switch_matrix.v')

    # N_term_IHP_SRAM
    verilog_sources.append(f'{TILES_ROOT}/N_term_IHP_SRAM/N_term_IHP_SRAM.v')
    verilog_sources.append(f'{TILES_ROOT}/N_term_IHP_SRAM/N_term_IHP_SRAM_ConfigMem.v')
    verilog_sources.append(f'{TILES_ROOT}/N_term_IHP_SRAM/N_term_IHP_SRAM_switch_matrix.v')

    # S_term_IHP_SRAM
    verilog_sources.append(f'{TILES_ROOT}/S_term_IHP_SRAM/S_term_IHP_SRAM.v')
    verilog_sources.append(f'{TILES_ROOT}/S_term_IHP_SRAM/S_term_IHP_SRAM_ConfigMem.v')
    verilog_sources.append(f'{TILES_ROOT}/S_term_IHP_SRAM/S_term_IHP_SRAM_switch_matrix.v')

    verilog_sources.append(testbench_path / '../../ip/fabulous_fabric/fabulous_tiles/models_pack.v')

    defines['USE_POWER_PINS'] = True
    
    if enabled["connect_flash1"]:
        defines['BITSTREAM_FLASH'] = True
    
    if enabled["dump_waveforms"]:
        defines['DUMP_WAVEFORMS'] = True
    
    hdl_toplevel = "greyhound_ihp_top_tb"

    build_args = []

    if sim == 'icarus':
        build_args = ['-Winfloop']

    if sim == 'verilator':
        build_args = ['--timing', '--trace', '--trace-fst', '--trace-structs']

    runner = get_runner(sim)
    runner.build(
        verilog_sources=verilog_sources,
        hdl_toplevel=hdl_toplevel,
        defines=defines,
        always=True,
        includes=includes,
        build_args=build_args,
    )

    plusargs = []
    plusargs += [f'+flash0_slot0={enabled["flash0_slot0"]}']
    plusargs += [f'+flash0_slot1={enabled["flash0_slot1"]}']
    plusargs += [f'+flash1_slot0={enabled["flash1_slot0"]}']
    plusargs += [f'+flash1_slot1={enabled["flash1_slot1"]}']

    if sim == 'icarus':
        plusargs += ['-fst']

    runner.test(
        hdl_toplevel=hdl_toplevel,
        test_module="greyhound_ihp_top_tb,",
        plusargs=plusargs,
        waves=True,
    )

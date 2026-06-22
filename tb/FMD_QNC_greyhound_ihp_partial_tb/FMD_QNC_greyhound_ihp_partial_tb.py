# SPDX-FileCopyrightText: © 2025 Leo Moser <leomoser99@gmail.com>
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileContributor: Modified by Stefan Huwar <stefan.huwar@gmail.com>

import os
import cocotb
from pathlib import Path
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles
from cocotb.triggers import Timer, Edge, RisingEdge, FallingEdge
from cocotb.regression import TestFactory
from cocotb_tools.runner import get_runner
from cocotbext.uart import UartSource, UartSink
from cocotbext.spi import SpiBus, SpiConfig, SpiMaster
from cocotbext.jtag import JTAGDriver, JTAGBus, JTAGDevice
from cocotb.types import LogicArray, Range

partial_extension_cpu = {
    'flash0_slot0': '../../../firmware/partial/partial.hex',
    'flash0_slot1': '',
    'flash1_slot0': '',
    'flash1_slot1': '',
    'connect_flash1': False,
    'dump_waveforms': True,
}

enabled = partial_extension_cpu

async def start_clock(clock, freq=50):
    """ Start the clock @ freq MHz """
    c = Clock(clock, 1/freq*1000, 'ns')
    cocotb.start_soon(c.start())

async def reset(system_reset, tap_reset, active_low=True, time_ns=1000):
    """ Reset dut """
    cocotb.log.info("Reset asserted...")
    
    system_reset.value = not active_low
    if tap_reset is not None: 
        tap_reset.value = not active_low
    await Timer(time_ns, "ns")
    system_reset.value = active_low
    if tap_reset is not None: 
        tap_reset.value = active_low
    
    cocotb.log.info("Reset deasserted.")

async def start_up(dut, tap_reset=True):
    """ Startup sequence """
    await start_clock(dut.io_clock_PAD)
    
    trst_pad = None
    if tap_reset:
        trst_pad = dut.io_fpga_mode_PAD
    
    await reset(dut.io_reset_PAD, trst_pad) # Tap reset is shared with fpga mode

async def write_bitstream_spi(filename, spi_master):
    with open(filename, 'br') as f:
        data = f.read(4)
        while data:
            number = int.from_bytes(data, "big")
            
            number_bytes = []            
            for _ in range(4):
                number_bytes.append((number & 0xFF000000) >> 24)
                number = number << 8
            
            print(f'Bitstream data: {number_bytes}')
            await spi_master.write(number_bytes)

            data = f.read(4)

@cocotb.test(skip=enabled!=partial_extension_cpu)
async def test_partial_extension_cpu(dut):
    """Run the "Partial Extension CPU" program"""

    # Setup UART
    uart_source = UartSource(dut.io_ser_rx_PAD, baud=115200, bits=8)
    uart_sink = UartSink(dut.io_ser_tx_PAD, baud=115200, bits=8)

    # Static setup
    dut.io_fetch_enable_PAD.value = 1

    # Start up
    await start_up(dut)
    
    # Static setup, apply after reset happened (fpga_mode and tap reset share a line)
    dut.io_fpga_mode_PAD.value = 1 # Configure FPGA as receiver

    # Wait for UART to get clocked
    await ClockCycles(dut.io_clock_PAD, int(50000*2.5))

    # Wait for all messages
    await ClockCycles(dut.io_clock_PAD, int(50000*30.0))

    data = uart_sink.read_nowait(-1)
    print(data)

    print("\nFinished program")


if __name__ == "__main__":
    testbench_path = Path(__file__).resolve().parent
    sim         = os.getenv("SIM", "icarus")
    pdk_root    = os.getenv("PDK_ROOT", testbench_path / '../../IHP-Open-PDK')
    pdk         = os.getenv("PDK", "ihp-sg13g2")
    scl         = os.getenv("SCL", "sg13g2_stdcell")
    gl          = os.getenv("GL", False)
    
    includes = [testbench_path / '../../rtl/include']
    
    verilog_sources = []
    defines = {}

    if gl:
        # SCL models
        verilog_sources.append(Path(pdk_root) / pdk / "libs.ref" / scl / "verilog" / f"{scl}.v" )
        
        verilog_sources.append(testbench_path / '../../final/nl/FMD_QNC_greyhound_ihp.nl.v')
        #verilog_sources.append(testbench_path / '../../final/pnl/FMD_QNC_greyhound_ihp.pnl.v')
        
        verilog_sources.append(testbench_path / '../../ip/bondpad_70x70/bondpad_70x70.v')
        
        defines = {'FUNCTIONAL': True, 'UNIT_DELAY': '#0'}
    else:
        # SCL models (for the clock gate)
        verilog_sources.append(Path(pdk_root) / pdk / "libs.ref" / scl / "verilog" / f"{scl}.v" )
    
        verilog_sources.append(testbench_path / '../FMD_QNC_greyhound_ihp_tb/FMD_QNC_greyhound_ihp_slang.sv')
        verilog_sources.append(testbench_path / '../simlib.v')
        
        defines = {'RTL': True, 'FUNCTIONAL': True, 'UNIT_DELAY': '#0'}
    
    verilog_sources += [
        testbench_path / 'FMD_QNC_greyhound_ihp_partial_tb.v',
        testbench_path / 'spiflash.v',
        testbench_path / 'spiflash_powered.v',
        
        # SRAM models
        Path(pdk_root) / pdk / "libs.ref" / "sg13g2_sram" / "verilog" / "RM_IHPSG13_1P_1024x32_c2_bm_bist.v",
        Path(pdk_root) / pdk / "libs.ref" / "sg13g2_sram" / "verilog" / "RM_IHPSG13_1P_core_behavioral_bm_bist.v",
        
        # BRAM models
        Path(pdk_root) / pdk / "libs.ref" / "sg13g2_sram" / "verilog" / "RM_IHPSG13_2P_1024x16_c2_bm_bist.v",
        Path(pdk_root) / pdk / "libs.ref" / "sg13g2_sram" / "verilog" / "RM_IHPSG13_2P_core_behavioral_bm_bist_ideal.v",
        
        # IO Pad models
        Path(pdk_root) / pdk / "libs.ref" / "sg13g2_io" / "verilog" / "sg13g2_io.v",
        
    ]
    
    # Add FPGA fabric
    verilog_sources.append(testbench_path / f'../../ip/fabric/macro/{pdk}/fabulous/eFPGA.v')

    # Paths
    TILES_ROOT = testbench_path / '../../ip/tile_library/tiles'
    PRIMITIVES_ROOT = testbench_path / '../../ip/tile_library/primitives/'
    
    # Primitives
    verilog_sources.append(f'{PRIMITIVES_ROOT}/CPU_IRQ/CPU_IRQ.v')
    verilog_sources.append(f'{PRIMITIVES_ROOT}/CUSTOM_INSTRUCTION/CUSTOM_INSTRUCTION.v')
    verilog_sources.append(f'{PRIMITIVES_ROOT}/IHP_SRAM_1024x32/IHP_SRAM_1024x32.v')
    verilog_sources.append(f'{PRIMITIVES_ROOT}/IHP_BRAM_1024x16/IHP_BRAM_1024x16.v')
    verilog_sources.append(f'{PRIMITIVES_ROOT}/IO_1_bidirectional_frame_config_pass/IO_1_bidirectional_frame_config_pass.v')
    verilog_sources.append(f'{PRIMITIVES_ROOT}/LUT4c_frame_config_dffesr/LUT4c_frame_config_dffesr.v')
    verilog_sources.append(f'{PRIMITIVES_ROOT}/MULADD/MULADD.v')
    verilog_sources.append(f'{PRIMITIVES_ROOT}/MUX8LUT_frame_config_mux/MUX8LUT_frame_config_mux.v')
    verilog_sources.append(f'{PRIMITIVES_ROOT}/OBI_PERIPHERAL/OBI_PERIPHERAL.v')
    verilog_sources.append(f'{PRIMITIVES_ROOT}/RegFile_32x4/RegFile_32x4.v')
    verilog_sources.append(f'{PRIMITIVES_ROOT}/WARMBOOT/WARMBOOT.v')
    
    # DSP
    verilog_sources.append(f'{TILES_ROOT}/DSP/DSP.v')
    verilog_sources.append(f'{TILES_ROOT}/DSP/DSP_bot/DSP_bot.v')
    verilog_sources.append(f'{TILES_ROOT}/DSP/DSP_bot/DSP_bot_ConfigMem.v')
    verilog_sources.append(f'{TILES_ROOT}/DSP/DSP_bot/DSP_bot_switch_matrix.v')
    verilog_sources.append(f'{TILES_ROOT}/DSP/DSP_top/DSP_top.v')
    verilog_sources.append(f'{TILES_ROOT}/DSP/DSP_top/DSP_top_ConfigMem.v')
    verilog_sources.append(f'{TILES_ROOT}/DSP/DSP_top/DSP_top_switch_matrix.v')
    
    # LUT4AB
    verilog_sources.append(f'{TILES_ROOT}/LUT4AB/LUT4AB.v')
    verilog_sources.append(f'{TILES_ROOT}/LUT4AB/LUT4AB_ConfigMem.v')
    verilog_sources.append(f'{TILES_ROOT}/LUT4AB/LUT4AB_switch_matrix.v')
    
    # N_term_DSP
    verilog_sources.append(f'{TILES_ROOT}/N_term_DSP/N_term_DSP.v')
    verilog_sources.append(f'{TILES_ROOT}/N_term_DSP/N_term_DSP_switch_matrix.v')
    
    # N_term_single
    verilog_sources.append(f'{TILES_ROOT}/N_term_single/N_term_single.v')
    verilog_sources.append(f'{TILES_ROOT}/N_term_single/N_term_single_switch_matrix.v')
    
    # N_term_single2
    verilog_sources.append(f'{TILES_ROOT}/N_term_single2/N_term_single2.v')
    verilog_sources.append(f'{TILES_ROOT}/N_term_single2/N_term_single2_switch_matrix.v')

    # RegFile
    verilog_sources.append(f'{TILES_ROOT}/RegFile/RegFile.v')
    verilog_sources.append(f'{TILES_ROOT}/RegFile/RegFile_ConfigMem.v')
    verilog_sources.append(f'{TILES_ROOT}/RegFile/RegFile_switch_matrix.v')
    
    # S_term_DSP
    verilog_sources.append(f'{TILES_ROOT}/S_term_DSP/S_term_DSP.v')
    verilog_sources.append(f'{TILES_ROOT}/S_term_DSP/S_term_DSP_switch_matrix.v')
    
    # S_term_single
    verilog_sources.append(f'{TILES_ROOT}/S_term_single/S_term_single.v')
    verilog_sources.append(f'{TILES_ROOT}/S_term_single/S_term_single_switch_matrix.v')

    # S_term_single2
    verilog_sources.append(f'{TILES_ROOT}/S_term_single2/S_term_single2.v')
    verilog_sources.append(f'{TILES_ROOT}/S_term_single2/S_term_single2_switch_matrix.v')

    # W_IO
    verilog_sources.append(f'{TILES_ROOT}/W_IO/W_IO.v')
    verilog_sources.append(f'{TILES_ROOT}/W_IO/W_IO_ConfigMem.v')
    verilog_sources.append(f'{TILES_ROOT}/W_IO/W_IO_switch_matrix.v')

    # S_WARMBOOT
    verilog_sources.append(f'{TILES_ROOT}/S_WARMBOOT/S_WARMBOOT.v')
    verilog_sources.append(f'{TILES_ROOT}/S_WARMBOOT/S_WARMBOOT_ConfigMem.v')
    verilog_sources.append(f'{TILES_ROOT}/S_WARMBOOT/S_WARMBOOT_switch_matrix.v')
    
    # S_CPU_IF
    verilog_sources.append(f'{TILES_ROOT}/S_CPU_IF/S_CPU_IF.v')
    verilog_sources.append(f'{TILES_ROOT}/S_CPU_IF/S_CPU_IF_ConfigMem.v')
    verilog_sources.append(f'{TILES_ROOT}/S_CPU_IF/S_CPU_IF_switch_matrix.v')

    # S_CPU_IRQ
    verilog_sources.append(f'{TILES_ROOT}/S_CPU_IRQ/S_CPU_IRQ.v')
    verilog_sources.append(f'{TILES_ROOT}/S_CPU_IRQ/S_CPU_IRQ_ConfigMem.v')
    verilog_sources.append(f'{TILES_ROOT}/S_CPU_IRQ/S_CPU_IRQ_switch_matrix.v')

    # IHP_SRAM
    verilog_sources.append(f'{TILES_ROOT}/IHP_SRAM/IHP_SRAM.v')
    verilog_sources.append(f'{TILES_ROOT}/IHP_SRAM/IHP_SRAM_bot/IHP_SRAM_bot.v')
    verilog_sources.append(f'{TILES_ROOT}/IHP_SRAM/IHP_SRAM_bot/IHP_SRAM_bot_ConfigMem.v')
    verilog_sources.append(f'{TILES_ROOT}/IHP_SRAM/IHP_SRAM_bot/IHP_SRAM_bot_switch_matrix.v')
    verilog_sources.append(f'{TILES_ROOT}/IHP_SRAM/IHP_SRAM_top/IHP_SRAM_top.v')
    verilog_sources.append(f'{TILES_ROOT}/IHP_SRAM/IHP_SRAM_top/IHP_SRAM_top_ConfigMem.v')
    verilog_sources.append(f'{TILES_ROOT}/IHP_SRAM/IHP_SRAM_top/IHP_SRAM_top_switch_matrix.v')

    # IHP_BRAM
    verilog_sources.append(f'{TILES_ROOT}/IHP_BRAM/IHP_BRAM.v')
    verilog_sources.append(f'{TILES_ROOT}/IHP_BRAM/IHP_BRAM_bot/IHP_BRAM_bot.v')
    verilog_sources.append(f'{TILES_ROOT}/IHP_BRAM/IHP_BRAM_bot/IHP_BRAM_bot_ConfigMem.v')
    verilog_sources.append(f'{TILES_ROOT}/IHP_BRAM/IHP_BRAM_bot/IHP_BRAM_bot_switch_matrix.v')
    verilog_sources.append(f'{TILES_ROOT}/IHP_BRAM/IHP_BRAM_top/IHP_BRAM_top.v')
    verilog_sources.append(f'{TILES_ROOT}/IHP_BRAM/IHP_BRAM_top/IHP_BRAM_top_ConfigMem.v')
    verilog_sources.append(f'{TILES_ROOT}/IHP_BRAM/IHP_BRAM_top/IHP_BRAM_top_switch_matrix.v')

    # N_term_IHP_SRAM
    verilog_sources.append(f'{TILES_ROOT}/N_term_IHP_SRAM/N_term_IHP_SRAM.v')
    verilog_sources.append(f'{TILES_ROOT}/N_term_IHP_SRAM/N_term_IHP_SRAM_switch_matrix.v')

    # S_term_IHP_SRAM
    verilog_sources.append(f'{TILES_ROOT}/S_term_IHP_SRAM/S_term_IHP_SRAM.v')
    verilog_sources.append(f'{TILES_ROOT}/S_term_IHP_SRAM/S_term_IHP_SRAM_switch_matrix.v')

    # S_OBI
    verilog_sources.append(f'{TILES_ROOT}/S_OBI/S_OBI.v')
    verilog_sources.append(f'{TILES_ROOT}/S_OBI/S_OBI_left/S_OBI_left.v')
    verilog_sources.append(f'{TILES_ROOT}/S_OBI/S_OBI_left/S_OBI_left_ConfigMem.v')
    verilog_sources.append(f'{TILES_ROOT}/S_OBI/S_OBI_left/S_OBI_left_switch_matrix.v')
    verilog_sources.append(f'{TILES_ROOT}/S_OBI/S_OBI_middle/S_OBI_middle.v')
    verilog_sources.append(f'{TILES_ROOT}/S_OBI/S_OBI_middle/S_OBI_middle_ConfigMem.v')
    verilog_sources.append(f'{TILES_ROOT}/S_OBI/S_OBI_middle/S_OBI_middle_switch_matrix.v')
    verilog_sources.append(f'{TILES_ROOT}/S_OBI/S_OBI_right/S_OBI_right.v')
    verilog_sources.append(f'{TILES_ROOT}/S_OBI/S_OBI_right/S_OBI_right_ConfigMem.v')
    verilog_sources.append(f'{TILES_ROOT}/S_OBI/S_OBI_right/S_OBI_right_switch_matrix.v')

    # S_XIF
    verilog_sources.append(f'{TILES_ROOT}/S_XIF/S_XIF.v')
    verilog_sources.append(f'{TILES_ROOT}/S_XIF/S_XIF_left/S_XIF_left.v')
    verilog_sources.append(f'{TILES_ROOT}/S_XIF/S_XIF_left/S_XIF_left_ConfigMem.v')
    verilog_sources.append(f'{TILES_ROOT}/S_XIF/S_XIF_left/S_XIF_left_switch_matrix.v')
    verilog_sources.append(f'{TILES_ROOT}/S_XIF/S_XIF_middle/S_XIF_middle.v')
    verilog_sources.append(f'{TILES_ROOT}/S_XIF/S_XIF_middle/S_XIF_middle_ConfigMem.v')
    verilog_sources.append(f'{TILES_ROOT}/S_XIF/S_XIF_middle/S_XIF_middle_switch_matrix.v')
    verilog_sources.append(f'{TILES_ROOT}/S_XIF/S_XIF_right/S_XIF_right.v')
    verilog_sources.append(f'{TILES_ROOT}/S_XIF/S_XIF_right/S_XIF_right_ConfigMem.v')
    verilog_sources.append(f'{TILES_ROOT}/S_XIF/S_XIF_right/S_XIF_right_switch_matrix.v')

    verilog_sources.append(testbench_path / '../../ip/tile_library/models_pack.v')

    defines['USE_POWER_PINS'] = True
    
    if enabled["connect_flash1"]:
        defines['BITSTREAM_FLASH'] = True
    
    if enabled["dump_waveforms"]:
        defines['DUMP_WAVEFORMS'] = True
    
    hdl_toplevel = "FMD_QNC_greyhound_ihp_partial_tb"

    build_args = []

    if sim == 'icarus':
        build_args = ['-Winfloop', '-pfileline=1']

    if sim == 'verilator':
        build_args = ['--timing', '--trace', '--trace-fst', '--trace-structs']

    runner = get_runner(sim)
    runner.build(
        sources=verilog_sources,
        hdl_toplevel=hdl_toplevel,
        defines=defines,
        always=True,
        includes=includes,
        build_args=build_args,
    )

    plusargs = []
    if enabled["flash0_slot0"]:
        plusargs += [f'+flash0_slot0={enabled["flash0_slot0"]}']
    if enabled["flash0_slot1"]:
        plusargs += [f'+flash0_slot1={enabled["flash0_slot1"]}']
    if enabled["flash1_slot0"]:
        plusargs += [f'+flash1_slot0={enabled["flash1_slot0"]}']
    if enabled["flash1_slot1"]:
        plusargs += [f'+flash1_slot1={enabled["flash1_slot1"]}']

    if sim == 'icarus':
        plusargs += ['-fst']

    runner.test(
        hdl_toplevel=hdl_toplevel,
        test_module="FMD_QNC_greyhound_ihp_partial_tb,",
        plusargs=plusargs,
        waves=True,
        extra_env = {"COCOTB_RESOLVE_X": "ZEROS"}, # Needed because JTAG pins are not always reserved
    )

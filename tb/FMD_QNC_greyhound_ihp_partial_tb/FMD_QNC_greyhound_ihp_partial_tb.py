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
    'flash1_slot2': '',
    'flash1_slot3': '',
    'connect_flash1': False,
    'dump_waveforms': True,
}

partial_extension_jtag = {
    'flash0_slot0': '../../../firmware/partial_jtag/partial_jtag.hex',
    'flash0_slot1': '',
    'flash1_slot0': '',
    'flash1_slot1': '',
    'flash1_slot2': '',
    'flash1_slot3': '',
    'connect_flash1': False,
    'dump_waveforms': True,
}

partial_2slots_jtag = {
    'flash0_slot0': '../../../firmware/partial_2slots/partial_2slots.hex',
    'flash0_slot1': '',
    'flash1_slot0': '',
    'flash1_slot1': '',
    'flash1_slot2': '',
    'flash1_slot3': '',
    'connect_flash1': False,
    'dump_waveforms': True,
}

flash_image = {
    'flash0_slot0': '../../../firmware/flash_image/flash_image.hex',
    'flash0_slot1': '',
    'flash1_slot0': '../../../ip/fabric/user_designs/partial/flash_image.hex',
    'flash1_slot1': '',
    'flash1_slot2': '',
    'flash1_slot3': '',
    'connect_flash1': True,
    'dump_waveforms': True,
}

trigger_slots = {
    'flash0_slot0': '',
    'flash0_slot1': '',
    'flash1_slot0': '../../../ip/fabric/user_designs/partial/standalone/.board/bitstreams_hex/Static-Static.hex',
    'flash1_slot1': '../../../ip/fabric/user_designs/partial/standalone/.board/bitstreams_hex/Slot1_2-Interleave.hex',
    'flash1_slot2': '../../../ip/fabric/user_designs/partial/standalone/.board/bitstreams_hex/Slot1_2-Combine.hex',
    'flash1_slot3': '../../../ip/fabric/user_designs/partial/standalone/.board/bitstreams_hex/Slot1_2-Function.hex',
    'connect_flash1': True,
    'dump_waveforms': True,
}

enabled = flash_image

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
    """Run the "Partial Extension CPU" program (~8h)"""
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
    await FallingEdge(dut.io_config_busy_PAD)
    assert(uart_sink.read_nowait(-1) == b'Start\n')
    await FallingEdge(dut.io_config_busy_PAD)
    assert(uart_sink.read_nowait(-1) == b'Loaded Static\n')
    await FallingEdge(dut.io_config_busy_PAD)
    assert(uart_sink.read_nowait(-1) == b'Loaded Slot1 direct out\n')
    await FallingEdge(dut.io_config_busy_PAD)
    assert(uart_sink.read_nowait(-1) == b'Loaded Slot2 left shift\n')
    await ClockCycles(dut.io_clock_PAD, int(50000*2.95)) # 2.95ms
    cocotb.log.info(f"ASSERT {dut.io_gpio_PAD.value.to_unsigned():x} == 0xECAFECAF")
    assert(dut.io_gpio_PAD.value == 0xECAF_ECAF)

    await ClockCycles(dut.io_clock_PAD, int(50*82)) # 82µs
    cocotb.log.info(f"ASSERT {dut.io_gpio_PAD.value.to_unsigned():x} == 0xFECAFECA")
    assert(dut.io_gpio_PAD.value == 0xFECA_FECA)

    await ClockCycles(dut.io_clock_PAD, int(50*82)) # 82µs
    cocotb.log.info(f"ASSERT {dut.io_gpio_PAD.value.to_unsigned():x} == 0xAFECAFEC")
    assert(dut.io_gpio_PAD.value == 0xAFEC_AFEC)

    await ClockCycles(dut.io_clock_PAD, int(50*82)) # 82µs
    cocotb.log.info(f"ASSERT {dut.io_gpio_PAD.value.to_unsigned():x} == 0xCAFECAFE")
    assert(dut.io_gpio_PAD.value == 0xCAFE_CAFE)

    await ClockCycles(dut.io_clock_PAD, int(50*82)) # 82µs
    cocotb.log.info(f"ASSERT {dut.io_gpio_PAD.value.to_unsigned():x} == 0xECAFECAF")
    assert(dut.io_gpio_PAD.value == 0xECAF_ECAF)

    await ClockCycles(dut.io_clock_PAD, int(50*82)) # 82µs
    cocotb.log.info(f"ASSERT {dut.io_gpio_PAD.value.to_unsigned():x} == 0xFECAFECA")
    assert(dut.io_gpio_PAD.value == 0xFECA_FECA)

    await ClockCycles(dut.io_clock_PAD, int(50*82)) # 82µs
    cocotb.log.info(f"ASSERT {dut.io_gpio_PAD.value.to_unsigned():x} == 0xAFECAFEC")
    assert(dut.io_gpio_PAD.value == 0xAFEC_AFEC)

    await ClockCycles(dut.io_clock_PAD, int(50*82)) # 82µs
    cocotb.log.info(f"ASSERT {dut.io_gpio_PAD.value.to_unsigned():x} == 0xCAFECAFE")
    assert(dut.io_gpio_PAD.value == 0xCAFE_CAFE)
    assert(uart_sink.read_nowait(-1) == b'Loaded Slot3 straight through\n')

    await FallingEdge(dut.io_config_busy_PAD)
    assert(uart_sink.read_nowait(-1) == b'IO reg cafecafe\nLeft shift 1: beef0000\nLeft shift 2: ddfbd5a0\n')

    await FallingEdge(dut.io_config_busy_PAD)
    assert(uart_sink.read_nowait(-1) == b'Loaded Slot2 right shift\nRight shift 1: 1bd5b7dd\nRight shift 2: dead\n')
    await ClockCycles(dut.io_clock_PAD, int(50000*2.3)) # 2.3ms
    cocotb.log.info(f"ASSERT {dut.io_gpio_PAD.value.to_unsigned():x} == 0xF537F537")
    assert(dut.io_gpio_PAD.value == 0xF537_F537)

    await ClockCycles(dut.io_clock_PAD, int(50*90)) # 90µs
    cocotb.log.info(f"ASSERT {dut.io_gpio_PAD.value.to_unsigned():x} == 0x537F537F")
    assert(dut.io_gpio_PAD.value == 0x537F_537F)

    await ClockCycles(dut.io_clock_PAD, int(50*90)) # 90µs
    cocotb.log.info(f"ASSERT {dut.io_gpio_PAD.value.to_unsigned():x} == 0x37F537F5")
    assert(dut.io_gpio_PAD.value == 0x37F5_37F5)

    await ClockCycles(dut.io_clock_PAD, int(50*90)) # 90µs
    cocotb.log.info(f"ASSERT {dut.io_gpio_PAD.value.to_unsigned():x} == 0x7F537F53")
    assert(dut.io_gpio_PAD.value == 0x7F53_7F53)

    await ClockCycles(dut.io_clock_PAD, int(50*90)) # 90µs
    cocotb.log.info(f"ASSERT {dut.io_gpio_PAD.value.to_unsigned():x} == 0xF537F537")
    assert(dut.io_gpio_PAD.value == 0xF537_F537)

    await ClockCycles(dut.io_clock_PAD, int(50*90)) # 90µs
    cocotb.log.info(f"ASSERT {dut.io_gpio_PAD.value.to_unsigned():x} == 0x537F537F")
    assert(dut.io_gpio_PAD.value == 0x537F_537F)

    await ClockCycles(dut.io_clock_PAD, int(50*90)) # 90µs
    cocotb.log.info(f"ASSERT {dut.io_gpio_PAD.value.to_unsigned():x} == 0x37F537F5")
    assert(dut.io_gpio_PAD.value == 0x37F5_37F5)

    await ClockCycles(dut.io_clock_PAD, int(50*90)) # 90µs
    cocotb.log.info(f"ASSERT {dut.io_gpio_PAD.value.to_unsigned():x} == 0x7F537F53")
    assert(dut.io_gpio_PAD.value == 0x7F53_7F53)
    assert(uart_sink.read_nowait(-1) == b'Loaded Slot3 crossover\n')

    await FallingEdge(dut.io_config_busy_PAD)
    assert(uart_sink.read_nowait(-1) == b'IO reg cafecafe\n')
    await ClockCycles(dut.io_clock_PAD, int(50000*2.25)) # 2.25ms
    cocotb.log.info(f"ASSERT {dut.io_gpio_PAD.value.to_unsigned():x} == 0x1F581F59")
    assert(dut.io_gpio_PAD.value == 0x1F58_1F59)

    await ClockCycles(dut.io_clock_PAD, int(50*82)) # 82µs
    cocotb.log.info(f"ASSERT {dut.io_gpio_PAD.value.to_unsigned():x} == 0xF581F581")
    assert(dut.io_gpio_PAD.value == 0xF581_F581)

    await ClockCycles(dut.io_clock_PAD, int(50*82)) # 82µs
    cocotb.log.info(f"ASSERT {dut.io_gpio_PAD.value.to_unsigned():x} == 0x581F581F")
    assert(dut.io_gpio_PAD.value == 0x581F_581F)

    await ClockCycles(dut.io_clock_PAD, int(50*82)) # 82µs
    cocotb.log.info(f"ASSERT {dut.io_gpio_PAD.value.to_unsigned():x} == 0x81F581F5")
    assert(dut.io_gpio_PAD.value == 0x81F5_81F5)

    await ClockCycles(dut.io_clock_PAD, int(50*82)) # 82µs
    cocotb.log.info(f"ASSERT {dut.io_gpio_PAD.value.to_unsigned():x} == 0x1F581F59")
    assert(dut.io_gpio_PAD.value == 0x1F58_1F59)

    await ClockCycles(dut.io_clock_PAD, int(50*82)) # 82µs
    cocotb.log.info(f"ASSERT {dut.io_gpio_PAD.value.to_unsigned():x} == 0xF581F581")
    assert(dut.io_gpio_PAD.value == 0xF581_F581)

    await ClockCycles(dut.io_clock_PAD, int(50*82)) # 82µs
    cocotb.log.info(f"ASSERT {dut.io_gpio_PAD.value.to_unsigned():x} == 0x581F581F")
    assert(dut.io_gpio_PAD.value == 0x581F_581F)

    await ClockCycles(dut.io_clock_PAD, int(50*82)) # 82µs
    cocotb.log.info(f"ASSERT {dut.io_gpio_PAD.value.to_unsigned():x} == 0x81F581F5")
    assert(dut.io_gpio_PAD.value == 0x81F5_81F5)
    assert(uart_sink.read_nowait(-1) == b'Loaded Slot1 graycode\n')

    await FallingEdge(dut.io_config_busy_PAD)
    assert(uart_sink.read_nowait(-1) == b'IO reg af81af81\n')
    await ClockCycles(dut.io_clock_PAD, int(50000*2.95)) # 2.95ms
    cocotb.log.info(f"ASSERT {dut.io_gpio_PAD.value.to_unsigned():x} == 0x9AF81AF8")
    assert(dut.io_gpio_PAD.value == 0x9AF8_1AF8)

    await ClockCycles(dut.io_clock_PAD, int(50*82)) # 82µs
    cocotb.log.info(f"ASSERT {dut.io_gpio_PAD.value.to_unsigned():x} == 0x81AF81AF")
    assert(dut.io_gpio_PAD.value == 0x81AF_81AF)

    await ClockCycles(dut.io_clock_PAD, int(50*82)) # 82µs
    cocotb.log.info(f"ASSERT {dut.io_gpio_PAD.value.to_unsigned():x} == 0xF81AF81A")
    assert(dut.io_gpio_PAD.value == 0xF81A_F81A)

    await ClockCycles(dut.io_clock_PAD, int(50*82)) # 82µs
    cocotb.log.info(f"ASSERT {dut.io_gpio_PAD.value.to_unsigned():x} == 0xAF81AF81")
    assert(dut.io_gpio_PAD.value == 0xAF81_AF81)

    await ClockCycles(dut.io_clock_PAD, int(50*82)) # 82µs
    cocotb.log.info(f"ASSERT {dut.io_gpio_PAD.value.to_unsigned():x} == 0x9AF81AF8")
    assert(dut.io_gpio_PAD.value == 0x9AF8_1AF8)

    await ClockCycles(dut.io_clock_PAD, int(50*82)) # 82µs
    cocotb.log.info(f"ASSERT {dut.io_gpio_PAD.value.to_unsigned():x} == 0x81AF81AF")
    assert(dut.io_gpio_PAD.value == 0x81AF_81AF)

    await ClockCycles(dut.io_clock_PAD, int(50*82)) # 82µs
    cocotb.log.info(f"ASSERT {dut.io_gpio_PAD.value.to_unsigned():x} == 0xF81AF81A")
    assert(dut.io_gpio_PAD.value == 0xF81A_F81A)

    await ClockCycles(dut.io_clock_PAD, int(50*82)) # 82µs
    cocotb.log.info(f"ASSERT {dut.io_gpio_PAD.value.to_unsigned():x} == 0xAF81AF81")
    assert(dut.io_gpio_PAD.value == 0xAF81_AF81)

    assert(uart_sink.read_nowait(-1) == b'Loaded Slot3 straight through\n')

    await RisingEdge(dut.io_core_sleep_PAD)
    assert(uart_sink.read_nowait(-1) == b'IO reg af81af81\n')
    await ClockCycles(dut.io_clock_PAD, int(50*100.0)) # 100µs

    print("\nFinished program")

# Define JTAG devices
class JTAGCore(JTAGDevice):
    def __init__(self, name="jtagcore", idcode=0x2_5256_001, ir_len=5):
        super().__init__(name, idcode, ir_len)
        self.add_jtag_reg("IDCODE", 32, 0x1)
        self.idle_delay = 10

class JTAGFPGA(JTAGDevice):
    def __init__(self, name="jtagfpga", idcode=0x2_4646_001, ir_len=5):
        super().__init__(name, idcode, ir_len)
        self.add_jtag_reg("IDCODE", 32, 0x1)
        self.add_jtag_reg("USERCODE", 32,0x2)
        bsr_length = 1

        if 'bsr_length' in enabled:
            bsr_length = enabled['bsr_length']
        
        self.add_jtag_reg("SAMPLE", bsr_length, 0x3)
        self.add_jtag_reg("PRELOAD", bsr_length, 0x3, write=True)
        self.add_jtag_reg("EXTEST", bsr_length, 0x4, write=True)
        self.add_jtag_reg("INTEST", bsr_length, 0x5, write=True)

        self.add_jtag_reg("EJTAG", 1, 0x10, write=True)
        self.add_jtag_reg("ISC_ENABLE", 1, 0x14)
        self.add_jtag_reg("ISC_DISABLE", 1,0x15)
        self.add_jtag_reg("ISC_PROGRAM", 32,0x16, write=True)
        self.add_jtag_reg("ISC_NOOP", 1, 0x17)

        self.idle_delay = 10

async def setup_for_jtag(dut):
    """Setup soc for jtag"""
    # Setup JTAG
    jtag_signals:dict = {"tck" :"io_fpga_sclk_PAD",
                         "tms" :"io_fpga_cs_n_PAD",
                         "tdi" :"io_fpga_mosi_PAD",
                         "tdo" :"io_fpga_miso_PAD",
                         "trst":"io_fpga_mode_PAD"}

    bus = JTAGBus(dut, signals=jtag_signals)
    jtag = JTAGDriver(bus)
    jtag.add_device(JTAGCore())
    jtag.add_device(JTAGFPGA())
    jtag.devices[0].print_regs()
    jtag.devices[1].print_regs()

    # Static setup
    dut.io_fetch_enable_PAD.value = 1

    # Start up
    await start_up(dut, False)

    # Enable JTAG mode of FPGA
    await ClockCycles(dut.io_clock_PAD, 10)
    cocotb.log.info("Enable JTAG interface.")
    dut.io_reset_PAD.value = 0
    await ClockCycles(dut.io_clock_PAD, 10)

    # All jtag operations have to be one after the other, else jtag lib runs into issues
    # Test perm enable of JTAG interface
    await jtag.write("EJTAG", 0x1, device=1)
    await jtag.write("BYPASS", 0x1, device=1)
    await jtag.write("BYPASS", 0x1, device=1)
    dut.io_reset_PAD.value = 1
    cocotb.log.info("JTAG interface enabled.")
    jtag.devices[0].idle_delay = 0
    jtag.devices[1].idle_delay = 0
    return jtag

async def load_bitstream(file:Path, tile_x_offset:int=0):
    with file.open("rb") as bitstream:
        # Find bitstream start
        loaded_bitstream = {"tiles":[], "usercode":1, "data":{"pre_frame":bytes(), "frame":{}, "post_frame":bytes()}}

        seek_word_raw = bitstream.read(4)
        loaded_bitstream["data"]["pre_frame"] += seek_word_raw
        seek_word = int.from_bytes(seek_word_raw, "big")
        seek_stream_start = -1
        seek_byte_counter = 4
        while 0xFAB0FAB1 != seek_word:
            if seek_word & 0xFFF00000 == 0x5E7<<20:
                loaded_bitstream["tiles"].append(seek_word)

            if seek_word == 0x00AAFF01:
                seek_stream_start = seek_byte_counter + 4

            if seek_stream_start == seek_byte_counter:
                loaded_bitstream["usercode"] = seek_word

            seek_byte_counter += 1
            seek_word_raw = bitstream.read(1)
            loaded_bitstream["data"]["pre_frame"] += seek_word_raw
            seek_word = ((seek_word & 0xFFFFFF) << 8) | int.from_bytes(seek_word_raw, "big")

        loaded_bitstream["tiles"].reverse()

        # Load frame data
        bytes_per_frame = 76
        data = bitstream.read(bytes_per_frame)
        while data:
            if (len(data) != bytes_per_frame):
                break
            
            col = (int.from_bytes(data[:1], "big")>>3) + tile_x_offset
            strobe = int.from_bytes(data[1:4], "big") & 0xFFFFF
            frame_header = (col<<27) | strobe
            loaded_bitstream["data"]["frame"][frame_header] = frame_header.to_bytes(4)+data[4:]
            data = bitstream.read(bytes_per_frame)

        # Load bitstream end
        loaded_bitstream["data"]["post_frame"] += data
        
        post_data = bitstream.read(1)
        loaded_bitstream["data"]["post_frame"] += post_data
        while post_data:
            post_data = bitstream.read(1)
            loaded_bitstream["data"]["post_frame"] += post_data

        return loaded_bitstream

async def write_bitstream_jtag(file:Path, jtag, static_file:Path=None, tile_x_offset:int=0):
    # Load static bitstream
    loaded_static_bitstream = None
    if static_file:
        loaded_static_bitstream = await load_bitstream(static_file)

    # Load bitstream
    loaded_bitstream = await load_bitstream(file, tile_x_offset)

    # Write bitstream to jtag
    len_pre_bitstream = int(len(loaded_bitstream["data"]["pre_frame"])/4)
    for i_word in range(len_pre_bitstream):
        bitstream_word = int.from_bytes(loaded_bitstream["data"]["pre_frame"][i_word*4:(i_word+1)*4], "big")
        cocotb.log.info("Bitstream pre word %d of %d" % (i_word, len_pre_bitstream-1))
        await jtag.write("ISC_PROGRAM", bitstream_word, device=1)

    len_bitstream = len(loaded_bitstream["data"]["frame"])*19
    for i_frame, (frame_header, frame_data) in enumerate(loaded_bitstream["data"]["frame"].items()):
        col = frame_header>>27
        use_frame_tile = loaded_bitstream["tiles"][i_frame] if (i_frame < len(loaded_bitstream["tiles"])) else 0x3ffff

        len_frame_data = int(len(frame_data)/4)
        for i_frame_word in range(len_frame_data):
            use_bitstream_tile = 1 if (i_frame_word == 0) else ((use_frame_tile >> (len_frame_data-i_frame_word-1)) & 0x1)

            if use_bitstream_tile:
                bitstream_word = int.from_bytes(frame_data[i_frame_word*4:(i_frame_word+1)*4], "big")
            elif loaded_static_bitstream:
                static_frame_header = (col<<27)
                for frame_bit in range(20):
                    if (frame_header >> frame_bit) & 0x1:
                        static_frame_header |= (1 << frame_bit)
                        break

                bitstream_word = int.from_bytes(loaded_static_bitstream["data"]["frame"][static_frame_header][i_frame_word*4:(i_frame_word+1)*4], "big")
            else:
                Exception("Couldn't find bitstream word, no static bitstream loaded")

            cocotb.log.info("Bitstream word %d of %d" % ((i_frame*19)+i_frame_word, len_bitstream-1))
            await jtag.write("ISC_PROGRAM", bitstream_word, device=1)

    len_post_bitstream = int(len(loaded_bitstream["data"]["post_frame"])/4)
    for i_word in range(len_post_bitstream):
        bitstream_word = int.from_bytes(loaded_bitstream["data"]["post_frame"][i_word*4:(i_word+1)*4], "big")
        cocotb.log.info("Bitstream post word %d of %d" % (i_word, len_post_bitstream-1))
        await jtag.write("ISC_PROGRAM", bitstream_word, device=1)

    cocotb.log.info("Finished bitstream upload")

async def wait_jtag(jtag, noops:int):
    # 1 NOOP takes ~0.7µs
    for i in range(noops):
        await jtag.write("ISC_NOOP", 0x1, device=1)

@cocotb.test(skip=enabled!=partial_extension_jtag)
async def test_partial_extension_jtag(dut):
    """Run the "Partial Extension over JTAG" program"""
    jtag = await setup_for_jtag(dut)
    gl   = int(os.getenv("GL", 0))

    await jtag.write("ISC_ENABLE", 0x1, device=1)
    cocotb.log.info("Upload Static Slot.")
    await write_bitstream_jtag(Path('../../../ip/fabric/user_designs/partial/custom_instr/.board/bitstreams/Static-Static.bit'), jtag)
    await jtag.write("ISC_DISABLE", 0x1, device=1)

    await jtag.write("ISC_ENABLE", 0x1, device=1)
    cocotb.log.info("Upload Slot 1 DirectOut.")
    await write_bitstream_jtag(Path('../../../ip/fabric/user_designs/partial/custom_instr/.board/bitstreams/Slot1-DirectOut.bit'), jtag, Path('../../../ip/fabric/user_designs/partial/custom_instr/.board/bitstreams/Static-Full.bit'))
    await jtag.write("ISC_DISABLE", 0x1, device=1)

    await jtag.write("ISC_ENABLE", 0x1, device=1)
    cocotb.log.info("Upload Slot 3 StraightThrough.")
    await write_bitstream_jtag(Path('../../../ip/fabric/user_designs/partial/custom_instr/.board/bitstreams/Slot3-StraightThrough.bit'), jtag, Path('../../../ip/fabric/user_designs/partial/custom_instr/.board/bitstreams/Static-Full.bit'))
    await jtag.write("ISC_DISABLE", 0x1, device=1)

    await wait_jtag(jtag, 2) # +2.9µs
    cocotb.log.info(f"ASSERT {dut.io_gpio_PAD.value.to_unsigned():x} == 0x7CAFE700")
    assert(dut.io_gpio_PAD.value == 0x7CAFE700)
    await wait_jtag(jtag, 14) # +9.8µs
    cocotb.log.info(f"ASSERT {dut.io_gpio_PAD.value.to_unsigned():x} == 0x07CAFE70")
    assert(dut.io_gpio_PAD.value == 0x07CAFE70)
    await wait_jtag(jtag, 8) # +5.6µs
    cocotb.log.info(f"ASSERT {dut.io_gpio_PAD.value.to_unsigned():x} == 0x007CAFE7")
    assert(dut.io_gpio_PAD.value == 0x007CAFE7)
    await wait_jtag(jtag, 9) # +6.3µs
    cocotb.log.info(f"ASSERT {dut.io_gpio_PAD.value.to_unsigned():x} == 0x7007CAFE")
    assert(dut.io_gpio_PAD.value == 0x7007CAFE)
    await wait_jtag(jtag, 9) # +6.3µs
    cocotb.log.info(f"ASSERT {dut.io_gpio_PAD.value.to_unsigned():x} == 0xE7007CAF")
    assert(dut.io_gpio_PAD.value == 0xE7007CAF)
    await wait_jtag(jtag, 9) # +6.3µs
    cocotb.log.info(f"ASSERT {dut.io_gpio_PAD.value.to_unsigned():x} == 0xFE7007CA")
    assert(dut.io_gpio_PAD.value == 0xFE7007CA)
    await wait_jtag(jtag, 8) # +5.6µs
    cocotb.log.info(f"ASSERT {dut.io_gpio_PAD.value.to_unsigned():x} == 0xAFE7007C")
    assert(dut.io_gpio_PAD.value == 0xAFE7007C)
    await wait_jtag(jtag, 9) # +6.3µs
    cocotb.log.info(f"ASSERT {dut.io_gpio_PAD.value.to_unsigned():x} == 0xCAFE7007")
    assert(dut.io_gpio_PAD.value == 0xCAFE7007)
    
    await jtag.write("ISC_ENABLE", 0x1, device=1)
    cocotb.log.info("Upload Slot 3 Crossover.")
    await write_bitstream_jtag(Path('../../../ip/fabric/user_designs/partial/custom_instr/.board/bitstreams/Slot3-Crossover.bit'), jtag, Path('../../../ip/fabric/user_designs/partial/custom_instr/.board/bitstreams/Static-Full.bit'))
    await jtag.write("ISC_DISABLE", 0x1, device=1)

    await wait_jtag(jtag, 2) # +2.9µs
    cocotb.log.info(f"ASSERT {dut.io_gpio_PAD.value.to_unsigned():x} == 0x0E07F53E")
    assert(dut.io_gpio_PAD.value == 0x0E07F53E)
    await wait_jtag(jtag, 16) # +11.2µs
    cocotb.log.info(f"ASSERT {dut.io_gpio_PAD.value.to_unsigned():x} == 0xE07F53E0")
    assert(dut.io_gpio_PAD.value == 0xE07F53E0)
    await wait_jtag(jtag, 16) # +11.2µs
    cocotb.log.info(f"ASSERT {dut.io_gpio_PAD.value.to_unsigned():x} == 0x07F53E0E")
    assert(dut.io_gpio_PAD.value == 0x07F53E0E)
    await wait_jtag(jtag, 16) # +11.2µs
    cocotb.log.info(f"ASSERT {dut.io_gpio_PAD.value.to_unsigned():x} == 0x7F53E0E0")
    assert(dut.io_gpio_PAD.value == 0x7F53E0E0)
    await wait_jtag(jtag, 21) # +14.7µs
    cocotb.log.info(f"ASSERT {dut.io_gpio_PAD.value.to_unsigned():x} == 0xF53E0E07")
    assert(dut.io_gpio_PAD.value == 0xF53E0E07)
    await wait_jtag(jtag, 16) # +11.2µs
    cocotb.log.info(f"ASSERT {dut.io_gpio_PAD.value.to_unsigned():x} == 0x53E0E07F")
    assert(dut.io_gpio_PAD.value == 0x53E0E07F)
    await wait_jtag(jtag, 16) # +11.2µs
    cocotb.log.info(f"ASSERT {dut.io_gpio_PAD.value.to_unsigned():x} == 0x3E0E07F5")
    assert(dut.io_gpio_PAD.value == 0x3E0E07F5)
    await wait_jtag(jtag, 17) # +11.8µs
    cocotb.log.info(f"ASSERT {dut.io_gpio_PAD.value.to_unsigned():x} == 0xE0E07F53")
    assert(dut.io_gpio_PAD.value == 0xE0E07F53)

    await jtag.write("ISC_ENABLE", 0x1, device=1)
    cocotb.log.info("Upload Slot 1 Graycode.")
    await write_bitstream_jtag(Path('../../../ip/fabric/user_designs/partial/custom_instr/.board/bitstreams/Slot1-Graycode.bit'), jtag, Path('../../../ip/fabric/user_designs/partial/custom_instr/.board/bitstreams/Static-Full.bit'))
    await jtag.write("ISC_DISABLE", 0x1, device=1)

    await wait_jtag(jtag, 14) # +11.3µs
    cocotb.log.info(f"ASSERT {dut.io_gpio_PAD.value.to_unsigned():x} == 0x21281F50")
    assert(dut.io_gpio_PAD.value == 0x21281F50)
    await wait_jtag(jtag, 27) # +18.9µs
    cocotb.log.info(f"ASSERT {dut.io_gpio_PAD.value.to_unsigned():x} == 0x1281F512")
    assert(dut.io_gpio_PAD.value == 0x1281F512)
    await wait_jtag(jtag, 27) # +18.9µs
    cocotb.log.info(f"ASSERT {dut.io_gpio_PAD.value.to_unsigned():x} == 0x281F5120")
    assert(dut.io_gpio_PAD.value == 0x281F5120)
    await wait_jtag(jtag, 27) # +18.9µs
    cocotb.log.info(f"ASSERT {dut.io_gpio_PAD.value.to_unsigned():x} == 0x81F51212")
    assert(dut.io_gpio_PAD.value == 0x81F51212)
    await wait_jtag(jtag, 27) # +18.9µs
    cocotb.log.info(f"ASSERT {dut.io_gpio_PAD.value.to_unsigned():x} == 0x1F512129")
    assert(dut.io_gpio_PAD.value == 0x1F512129)
    await wait_jtag(jtag, 27) # +18.9µs
    cocotb.log.info(f"ASSERT {dut.io_gpio_PAD.value.to_unsigned():x} == 0xF5121281")
    assert(dut.io_gpio_PAD.value == 0xF5121281)
    await wait_jtag(jtag, 27) # +18.9µs
    cocotb.log.info(f"ASSERT {dut.io_gpio_PAD.value.to_unsigned():x} == 0x5121281F")
    assert(dut.io_gpio_PAD.value == 0x5121281F)
    await wait_jtag(jtag, 27) # +18.9µs
    cocotb.log.info(f"ASSERT {dut.io_gpio_PAD.value.to_unsigned():x} == 0x121281F5")
    assert(dut.io_gpio_PAD.value == 0x121281F5)

    await jtag.write("ISC_ENABLE", 0x1, device=1)
    cocotb.log.info("Upload Slot 3 StraightThrough.")
    await write_bitstream_jtag(Path('../../../ip/fabric/user_designs/partial/custom_instr/.board/bitstreams/Slot3-StraightThrough.bit'), jtag, Path('../../../ip/fabric/user_designs/partial/custom_instr/.board/bitstreams/Static-Full.bit'))
    await jtag.write("ISC_DISABLE", 0x1, device=1)

    await wait_jtag(jtag, 9) # +7.6µs
    cocotb.log.info(f"ASSERT {dut.io_gpio_PAD.value.to_unsigned():x} == 0x0AF8104C")
    assert(dut.io_gpio_PAD.value == 0x0AF8104C)
    await wait_jtag(jtag, 8) # +5.6µs
    cocotb.log.info(f"ASSERT {dut.io_gpio_PAD.value.to_unsigned():x} == 0x48AF8104")
    assert(dut.io_gpio_PAD.value == 0x48AF8104)
    await wait_jtag(jtag, 8) # +5.6µs
    cocotb.log.info(f"ASSERT {dut.io_gpio_PAD.value.to_unsigned():x} == 0x4C8AF810")
    assert(dut.io_gpio_PAD.value == 0x4C8AF810)
    await wait_jtag(jtag, 8) # +5.6µs
    cocotb.log.info(f"ASSERT {dut.io_gpio_PAD.value.to_unsigned():x} == 0x04C8AF81")
    assert(dut.io_gpio_PAD.value == 0x04C8AF81)
    await wait_jtag(jtag, 8) # +5.6µs
    cocotb.log.info(f"ASSERT {dut.io_gpio_PAD.value.to_unsigned():x} == 0x904C8AF8")
    assert(dut.io_gpio_PAD.value == 0x904C8AF8)
    await wait_jtag(jtag, 8) # +5.6µs
    cocotb.log.info(f"ASSERT {dut.io_gpio_PAD.value.to_unsigned():x} == 0x8104C8AF")
    assert(dut.io_gpio_PAD.value == 0x8104C8AF)
    await wait_jtag(jtag, 8) # +5.6µs
    cocotb.log.info(f"ASSERT {dut.io_gpio_PAD.value.to_unsigned():x} == 0xF8104C8A")
    assert(dut.io_gpio_PAD.value == 0xF8104C8A)
    await wait_jtag(jtag, 8) # +5.6µs
    cocotb.log.info(f"ASSERT {dut.io_gpio_PAD.value.to_unsigned():x} == 0xAF8104C8")
    assert(dut.io_gpio_PAD.value == 0xAF8104C8)

    await wait_jtag(jtag, 16)

    cocotb.log.info("Uploaded all.")

@cocotb.test(skip=enabled!=partial_2slots_jtag)
async def test_partial_2slots_jtag(dut):
    """Run the "Partial 2slots over JTAG" program"""
    # Setup UART
    uart_source = UartSource(dut.io_ser_rx_PAD, baud=115200, bits=8)
    uart_sink = UartSink(dut.io_ser_tx_PAD, baud=115200, bits=8)

    jtag = await setup_for_jtag(dut)
    gl   = int(os.getenv("GL", 0))

    await jtag.write("ISC_ENABLE", 0x1, device=1)
    cocotb.log.info("Upload Static Slot.")
    await write_bitstream_jtag(Path('../../../ip/fabric/user_designs/partial/custom_instr_2slot/.board/bitstreams/Static-Static.bit'), jtag)
    await jtag.write("ISC_DISABLE", 0x1, device=1)

    await jtag.write("ISC_ENABLE", 0x1, device=1)
    cocotb.log.info("Upload Slot 1_2 Interleave in Slot 1.")
    await write_bitstream_jtag(Path('../../../ip/fabric/user_designs/partial/custom_instr_2slot/.board/bitstreams/Slot1_2-Interleave.bit'), jtag, Path('../../../ip/fabric/user_designs/partial/custom_instr_2slot/.board/bitstreams/Static-Full.bit'))
    await jtag.write("ISC_DISABLE", 0x1, device=1)

    await jtag.write("ISC_ENABLE", 0x1, device=1)
    cocotb.log.info("Upload Slot 1_2 Combine in Slot 2.")
    await write_bitstream_jtag(Path('../../../ip/fabric/user_designs/partial/custom_instr_2slot/.board/bitstreams/Slot1_2-Combine.bit'), jtag, Path('../../../ip/fabric/user_designs/partial/custom_instr_2slot/.board/bitstreams/Static-Full.bit'), -4)
    await jtag.write("ISC_DISABLE", 0x1, device=1)

    # Wait for all messages
    await wait_jtag(jtag, int(4*1000/0.7)) # Wait 4ms
    data1 = uart_sink.read_nowait(-1)
    cocotb.log.info(f"Data1: {data1}")

    assert(data1 == b'Init\nStatic\nSlot1\nSlot2\nRet: 00bd\nRet: 0077\n')

    await jtag.write("ISC_ENABLE", 0x1, device=1)
    cocotb.log.info("Upload Slot 1_2 Combine in Slot 1.")
    await write_bitstream_jtag(Path('../../../ip/fabric/user_designs/partial/custom_instr_2slot/.board/bitstreams/Slot1_2-Combine.bit'), jtag, Path('../../../ip/fabric/user_designs/partial/custom_instr_2slot/.board/bitstreams/Static-Full.bit'))
    await jtag.write("ISC_DISABLE", 0x1, device=1)

    await jtag.write("ISC_ENABLE", 0x1, device=1)
    cocotb.log.info("Upload Slot 1_2 Function in Slot 2.")
    await write_bitstream_jtag(Path('../../../ip/fabric/user_designs/partial/custom_instr_2slot/.board/bitstreams/Slot1_2-Function.bit'), jtag, Path('../../../ip/fabric/user_designs/partial/custom_instr_2slot/.board/bitstreams/Static-Full.bit'), -4)
    await jtag.write("ISC_DISABLE", 0x1, device=1)

    await wait_jtag(jtag, int(9*1000/0.7)) # Wait 9ms
    data2 = uart_sink.read_nowait(-1)
    cocotb.log.info(f"Data2: {data2}")
    
    assert(data2 == b'Slot1\nSlot2\nRet: 00d8\nRet: 007c\nRet: 00be\nRet: 00a6\nRet: 00c1\nEnd\n')

    cocotb.log.info("Uploaded all.")

@cocotb.test(skip=enabled!=flash_image)
async def test_flash_image(dut):
    """Run the "Flash image" program"""
    # Setup UART
    uart_source = UartSource(dut.io_ser_rx_PAD, baud=115200, bits=8)
    uart_sink = UartSink(dut.io_ser_tx_PAD, baud=115200, bits=8)

    # Static setup
    dut.io_fetch_enable_PAD.value = 1

    # Start up
    await start_up(dut)
    
    # Static setup, apply after reset happened (fpga_mode and tap reset share a line)
    dut.io_fpga_mode_PAD.value = 0 # Configure FPGA as controller

    # Ignore x -> 0 rising edge
    await ClockCycles(dut.io_clock_PAD, 10)

    # Wait until core is sleeping
    # await RisingEdge(dut.io_core_sleep_PAD)

    # cocotb.log.info("Core is sleeping!")

    # # Wait until core has woken up from the IRQ
    # await FallingEdge(dut.io_core_sleep_PAD)

    # cocotb.log.info("Core has woken up!")

    # Wait for all messages
    data = bytearray()
    for i in range(1, 12):
        await ClockCycles(dut.io_clock_PAD, int(50000*10.0))
        data += uart_sink.read_nowait(-1)
        cocotb.log.info(f"Data thus far: {data}")

    cocotb.log.info(f"Finished. UART:\n {data}")

@cocotb.test(skip=enabled!=trigger_slots)
async def test_trigger_slots(dut):
    """Run the "Trigger Slots" program"""
    # Static setup
    dut.io_fetch_enable_PAD.value = 1

    # Start up
    await start_up(dut)
    
    # Static setup, apply after reset happened (fpga_mode and tap reset share a line)
    dut.io_fpga_mode_PAD.value = 0 # Configure FPGA as controller
    dut.io_gpio_PAD.value = LogicArray("ZZZZZZZZZZZZ000000000000ZZZZZZZZ")
    await ClockCycles(dut.io_clock_PAD, int(50000*1))
    await FallingEdge(dut.io_config_busy_PAD)
    await ClockCycles(dut.io_clock_PAD, 10)

    # Load Slot 1
    cocotb.log.info(f"Load Slot 1")

    dut.io_gpio_PAD.value = LogicArray("ZZZZZZZZZZZZ000000010000ZZZZZZZZ")
    await ClockCycles(dut.io_clock_PAD, 1)
    dut.io_gpio_PAD.value = LogicArray("ZZZZZZZZZZZZ000000010001ZZZZZZZZ")
    await ClockCycles(dut.io_clock_PAD, 1)
    dut.io_gpio_PAD.value = LogicArray("ZZZZZZZZZZZZ000000000110ZZZZZZZZ")
    await ClockCycles(dut.io_clock_PAD, 1)
    dut.io_gpio_PAD.value = LogicArray("ZZZZZZZZZZZZ000000000000ZZZZZZZZ")
    await FallingEdge(dut.io_config_busy_PAD)
    await ClockCycles(dut.io_clock_PAD, 10)
    
    # Load Slot 2
    cocotb.log.info(f"Load Slot 2")

    dut.io_gpio_PAD.value = LogicArray("ZZZZZZZZZZZZ000000010000ZZZZZZZZ")
    await ClockCycles(dut.io_clock_PAD, 1)
    dut.io_gpio_PAD.value = LogicArray("ZZZZZZZZZZZZ000000010010ZZZZZZZZ")
    await ClockCycles(dut.io_clock_PAD, 1)
    dut.io_gpio_PAD.value = LogicArray("ZZZZZZZZZZZZ000000010110ZZZZZZZZ")
    await ClockCycles(dut.io_clock_PAD, 1)
    dut.io_gpio_PAD.value = LogicArray("ZZZZZZZZZZZZ000000000010ZZZZZZZZ")
    await ClockCycles(dut.io_clock_PAD, 1)
    dut.io_gpio_PAD.value = LogicArray("ZZZZZZZZZZZZ000000000000ZZZZZZZZ")
    await FallingEdge(dut.io_config_busy_PAD)
    await ClockCycles(dut.io_clock_PAD, 10)
    
    # Test
    dut.io_gpio_PAD.value = LogicArray("ZZZZZZZZZZZZ001100100000ZZZZZZZZ")
    await ClockCycles(dut.io_clock_PAD, 1)
    assert(dut.io_gpio_PAD.value[7:4] == 0x7)
    assert(dut.io_gpio_PAD.value[3:0] == 0x7)

    dut.io_gpio_PAD.value = LogicArray("ZZZZZZZZZZZZ000101100000ZZZZZZZZ")
    await ClockCycles(dut.io_clock_PAD, 1)
    assert(dut.io_gpio_PAD.value[7:4] == 0xD)
    assert(dut.io_gpio_PAD.value[3:0] == 0xB)

    dut.io_gpio_PAD.value = LogicArray("ZZZZZZZZZZZZ000000000000ZZZZZZZZ")
    await ClockCycles(dut.io_clock_PAD, 1)

    # Load Slot 3
    cocotb.log.info(f"Load Slot 3")

    dut.io_gpio_PAD.value = LogicArray("ZZZZZZZZZZZZ000000010000ZZZZZZZZ")
    await ClockCycles(dut.io_clock_PAD, 1)
    dut.io_gpio_PAD.value = LogicArray("ZZZZZZZZZZZZ000000010011ZZZZZZZZ")
    await ClockCycles(dut.io_clock_PAD, 1)
    dut.io_gpio_PAD.value = LogicArray("ZZZZZZZZZZZZ000000000110ZZZZZZZZ")
    await ClockCycles(dut.io_clock_PAD, 1)
    dut.io_gpio_PAD.value = LogicArray("ZZZZZZZZZZZZ000000000000ZZZZZZZZ")
    await FallingEdge(dut.io_config_busy_PAD)
    await ClockCycles(dut.io_clock_PAD, 10)

    # Test
    dut.io_gpio_PAD.value = LogicArray("ZZZZZZZZZZZZ001100100000ZZZZZZZZ")
    await ClockCycles(dut.io_clock_PAD, 1)
    assert(dut.io_gpio_PAD.value[7:4] == 0x7)
    assert(dut.io_gpio_PAD.value[3:0] == 0xC)

    dut.io_gpio_PAD.value = LogicArray("ZZZZZZZZZZZZ000101100000ZZZZZZZZ")
    await ClockCycles(dut.io_clock_PAD, 1)
    assert(dut.io_gpio_PAD.value[7:4] == 0xD)
    assert(dut.io_gpio_PAD.value[3:0] == 0x8)

    dut.io_gpio_PAD.value = LogicArray("ZZZZZZZZZZZZ001011100000ZZZZZZZZ")
    await ClockCycles(dut.io_clock_PAD, 1)
    assert(dut.io_gpio_PAD.value[7:4] == 0xE)
    assert(dut.io_gpio_PAD.value[3:0] == 0x4)

    dut.io_gpio_PAD.value = LogicArray("ZZZZZZZZZZZZ001011000000ZZZZZZZZ")
    await ClockCycles(dut.io_clock_PAD, 1)
    assert(dut.io_gpio_PAD.value[7:4] == 0xA)
    assert(dut.io_gpio_PAD.value[3:0] == 0x3)

    dut.io_gpio_PAD.value = LogicArray("ZZZZZZZZZZZZ101110000000ZZZZZZZZ")
    await ClockCycles(dut.io_clock_PAD, 1)
    assert(dut.io_gpio_PAD.value[7:4] == 0x3)
    assert(dut.io_gpio_PAD.value[3:0] == 0x7)

    dut.io_gpio_PAD.value = LogicArray("ZZZZZZZZZZZZ000000000000ZZZZZZZZ")
    await ClockCycles(dut.io_clock_PAD, 100)

if __name__ == "__main__":
    testbench_path = Path(__file__).resolve().parent
    sim         = os.getenv("SIM", "icarus")
    pdk_root    = os.getenv("PDK_ROOT", testbench_path / '../../IHP-Open-PDK')
    pdk         = os.getenv("PDK", "ihp-sg13g2")
    scl         = os.getenv("SCL", "sg13g2_stdcell")
    gl          = int(os.getenv("GL", 0))
    
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
    if enabled["flash1_slot2"]:
        plusargs += [f'+flash1_slot2={enabled["flash1_slot2"]}']
    if enabled["flash1_slot3"]:
        plusargs += [f'+flash1_slot3={enabled["flash1_slot3"]}']

    if sim == 'icarus':
        plusargs += ['-fst']

    runner.test(
        hdl_toplevel=hdl_toplevel,
        test_module="FMD_QNC_greyhound_ihp_partial_tb,",
        plusargs=plusargs,
        waves=True,
        extra_env = {"COCOTB_RESOLVE_X": "ZEROS"}, # Needed because JTAG pins are not always reserved
    )

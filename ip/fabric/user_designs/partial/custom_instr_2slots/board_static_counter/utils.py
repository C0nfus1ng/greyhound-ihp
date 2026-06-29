import os
import time
import machine
from winbond import W25QFlash

def write_bitstream_spi(filename, spi_master, cs, active_low=True):
    with open(filename, 'br') as f:
        data = f.read(4)
        while data:
            try:
                cs(not active_low)
                spi_master.write(data)
            finally:
                cs(active_low)
            
            # Next word
            data = f.read(4)

# from utils import upload_firmware
# upload_firmware("/firmware/hello_world.bin")
def verify_bitstream_spi(filename, spi_master, cs, active_low=True):
    with open(filename, 'br') as f:
        txdata = f.read(4)
        #rxdata = bytearray(4)
        while txdata:
            try:
                cs(not active_low)
                rxdata = spi_master.read(4)
                if (txdata != rxdata):
                    print(f"Data {int.from_bytes(txdata, "big"):x}, read {int.from_bytes(rxdata, "big"):x}")
                    assert(txdata == rxdata)
            finally:
                cs(active_low)
            
            # Next word
            txdata = f.read(4)

def load_bitstream(filepath:str, tile_x_offset:int=0):
    with open(filepath, "rb") as bitstream:
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
        bytes_per_frame = 68
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

def write_bitstream(filepath:str, spi_master, cs, static_file:Path=None, tile_x_offset:int=0, active_low=True):
    # Load static bitstream
    loaded_static_bitstream = None
    if static_file:
        loaded_static_bitstream = load_bitstream(static_file)

    # Load bitstream
    loaded_bitstream = load_bitstream(filepath, tile_x_offset)

    # Write bitstream to spi
    len_pre_bitstream = int(len(loaded_bitstream["data"]["pre_frame"])/4)
    for i_word in range(len_pre_bitstream):
        bitstream_word = loaded_bitstream["data"]["pre_frame"][i_word*4:(i_word+1)*4]
        try:
            cs(not active_low)
            spi_master.write(bitstream_word)
        finally:
            cs(active_low)

    len_bitstream = len(loaded_bitstream["data"]["frame"])*19
    for i_frame, (frame_header, frame_data) in enumerate(loaded_bitstream["data"]["frame"].items()):
        col = frame_header>>27
        use_frame_tile = loaded_bitstream["tiles"][i_frame] if (i_frame < len(loaded_bitstream["tiles"])) else 0x3ffff

        len_frame_data = int(len(frame_data)/4)
        for i_frame_word in range(len_frame_data):
            use_bitstream_tile = 1 if (i_frame_word == 0) else ((use_frame_tile >> (len_frame_data-i_frame_word-1)) & 0x1)

            if use_bitstream_tile:
                bitstream_word = frame_data[i_frame_word*4:(i_frame_word+1)*4]
            elif loaded_static_bitstream:
                static_frame_header = (col<<27)
                for frame_bit in range(20):
                    if (frame_header >> frame_bit) & 0x1:
                        static_frame_header |= (1 << frame_bit)
                        break

                bitstream_word = loaded_static_bitstream["data"]["frame"][static_frame_header][i_frame_word*4:(i_frame_word+1)*4]
            else:
                Exception("Couldn't find bitstream word, no static bitstream loaded")

            try:
                cs(not active_low)
                spi_master.write(bitstream_word)
            finally:
                cs(active_low)

    len_post_bitstream = int(len(loaded_bitstream["data"]["post_frame"])/4)
    for i_word in range(len_post_bitstream):
        bitstream_word = loaded_bitstream["data"]["post_frame"][i_word*4:(i_word+1)*4]
        try:
            cs(not active_low)
            spi_master.write(bitstream_word)
        finally:
            cs(active_low)

    print("Finished bitstream upload")

def upload_bitstream(bitstream, freq=25_175_000, tile_x_offset=0):
    print(f"freq: {machine.freq()}")

    # Setup
    clock   = machine.Pin(0, machine.Pin.OUT)
    reset_n = machine.Pin(1, machine.Pin.OUT)

    # SPI
    fpga_miso = machine.Pin(4, machine.Pin.IN)
    fpga_cs_n = machine.Pin(5, machine.Pin.OUT)
    fpga_sclk = machine.Pin(6, machine.Pin.OUT)
    fpga_mosi = machine.Pin(7, machine.Pin.OUT)

    fpga_spi = machine.SPI(
        mosi=fpga_mosi,
        sck=fpga_sclk,
        miso=fpga_miso,
        polarity=0,
        phase=1,
        baudrate=1_000_000, # Let's try 1 MBaud/s
        bits=8,
        firstbit=machine.SPI.MSB,
    )

    # Inputs
    fpga_mode = machine.Pin(2, machine.Pin.IN)
    fetch_enable = machine.Pin(3, machine.Pin.IN)

    config_busy = machine.Pin(16, machine.Pin.IN)
    core_sleep  = machine.Pin(17, machine.Pin.IN)

    print(f"fpga_mode: {fpga_mode.value()}")
    print(f"fetch_enable: {fetch_enable.value()}")
    print(f"config_busy: {config_busy.value()}")
    print(f"core_sleep: {core_sleep.value()}")

    print(f"Starting the clock!")
    
    pwm0 = machine.PWM(clock, freq=25_175_000, duty_u16=32768) # 50% duty
    print(pwm0.freq())

    print(f"Reset!")

    reset_n(0)
    time.sleep_ms(10)
    reset_n(1)

    print(f"Writing the bitstream {bitstream} !")
    write_bitstream(bitstream, fpga_spi, fpga_cs_n, static_file="bitstreams/Static-full.bit", tile_x_offset=tile_x_offset)
    
    pwm0 = machine.PWM(clock, freq=freq, duty_u16=32768) # 50% duty
    print(pwm0.freq())

def write_firmware(flash, firmware):
    with open(firmware, 'br') as f:
        data = f.read(256) # Read 1 page
        data_addr = 0

        while data:
            if len(data) < 256:
                firmware_data = data + b'\xFF'*(256-len(data))
            else:
                firmware_data = data

            flash._write(firmware_data, data_addr)
            data = f.read(256)
            data_addr += 256

def verify_firmware(flash, firmware):    
    with open(firmware, 'br') as f:
        data = f.read(256) # Read 1 page
        data_addr = 0

        while data:
            if len(data) < 256:
                firmware_data = data + b'\xFF'*(256-len(data))
            else:
                firmware_data = data

            firmware_read = bytearray(256)
            flash._read(firmware_read, data_addr)

            data = f.read(256)
            data_addr += 256
            assert(firmware_data == firmware_read)

def format_flash():
    # Setup
    clock   = machine.Pin(0, machine.Pin.OUT)
    reset_n = machine.Pin(1, machine.Pin.OUT)

    # Check if Greyhound is disabled and wait until it is
    reset_n(0)
    time.sleep_ms(10)
    input("Power down Greyhound by removing the power jumpers. Then press Enter to continue...")

    # FLASH: FLASH_CLK (10) -> SCLK, FLASH_CS_N (11) -> SCS_N, IO0 (12)-> MOSI, IO1 (13)-> MISO
    flash_sclk = machine.Pin(10, machine.Pin.OUT)
    flash_cs_n = machine.Pin(11, machine.Pin.OUT)
    flash_mosi = machine.Pin(12, machine.Pin.OUT)
    flash_miso = machine.Pin(13, machine.Pin.IN)

    fpga_spi = machine.SoftSPI(
        mosi=flash_mosi,
        sck=flash_sclk,
        miso=flash_miso,
        polarity=0,
        phase=1,
        baudrate=1_000_000, # Let's try 1 MBaud/s
        bits=8,
        firstbit=machine.SPI.MSB,
    )

    flash = W25QFlash(spi=fpga_spi, cs=flash_cs_n, baud=115200, software_reset=True)

    print(f"Erase flash")
    flash.format()
    print(f"Done")

def upload_firmware(firmware:str, freq=25_175_000):
    print(f"freq: {machine.freq()}")

    # Setup
    clock   = machine.Pin(0, machine.Pin.OUT)
    reset_n = machine.Pin(1, machine.Pin.OUT)

    # Check if Greyhound is disabled and wait until it is
    reset_n(0)
    time.sleep_ms(10)
    input("Power down Greyhound by removing the power jumpers. Then press Enter to continue...")

    # FLASH: FLASH_CLK (10) -> SCLK, FLASH_CS_N (11) -> SCS_N, IO0 (12)-> MOSI, IO1 (13)-> MISO
    flash_sclk = machine.Pin(10, machine.Pin.OUT)
    flash_cs_n = machine.Pin(11, machine.Pin.OUT)
    flash_mosi = machine.Pin(12, machine.Pin.OUT)
    flash_miso = machine.Pin(13, machine.Pin.IN)

    fpga_spi = machine.SoftSPI(
        mosi=flash_mosi,
        sck=flash_sclk,
        miso=flash_miso,
        polarity=0,
        phase=1,
        baudrate=1_000_000, # Let's try 1 MBaud/s
        bits=8,
        firstbit=machine.SPI.MSB,
    )

    flash = W25QFlash(spi=fpga_spi, cs=flash_cs_n, baud=115200, software_reset=True)

    print(f"Erase flash")
    flash.format()

    print(f"Write firmware")
    write_firmware(flash, firmware)

    print(f"Verify Integrity")
    verify_firmware(flash, firmware)

    print(f"Deassert SPI")
    fpga_spi.deinit()
    flash_sclk.init(machine.Pin.IN)
    flash_cs_n.init(machine.Pin.IN)
    flash_mosi.init(machine.Pin.IN)

    input("Firmware upload complete power up Greyhound by inserting the power jumpers. Then press Enter to continue...")

    # Inputs
    fpga_mode = machine.Pin(2, machine.Pin.IN)
    fetch_enable = machine.Pin(3, machine.Pin.IN)
    config_busy = machine.Pin(16, machine.Pin.IN)
    core_sleep  = machine.Pin(17, machine.Pin.IN)

    if fetch_enable.value() != 1:
        input("FETCH_ENABLE jumper is low. Resolve then press Enter to continue...")

    pwm0 = machine.PWM(clock, freq=25_175_000, duty_u16=32768) # 50% duty
    print(pwm0.freq())
    
    print("Flash bus released; project_clk requested %d Hz, PWM actual %d Hz"
          % (freq, pwm0.freq()))

    boot_uart(release_rst=True, baudrate=57600) # Use half baudrate, Greyhound is clocked slower than sim

def boot_uart(freq=25_175_000, release_rst=False, baudrate=115200):
    # Setup
    clock   = machine.Pin(0, machine.Pin.OUT)
    reset_n = machine.Pin(1, machine.Pin.OUT)
    tx_pin = machine.Pin(8)
    rx_pin = machine.Pin(9)

    uart = machine.UART(1, baudrate=baudrate, tx=tx_pin, rx=rx_pin, bits=8, parity=None, stop=1, timeout=1000)

    if release_rst:
        pwm0 = machine.PWM(clock, freq=25_175_000, duty_u16=32768) # 50% duty
        time.sleep_ms(5)
        reset_n.value(1)
    else:
        reset_n.value(0)
        time.sleep_ms(1)
        pwm0 = machine.PWM(clock, freq=25_175_000, duty_u16=32768) # 50% duty
        print(pwm0.freq())
        time.sleep_ms(5)
        reset_n.value(1)

    print(f"Received from Greyhound:")
    time_wait = 100
    while(time_wait > 0):
        recv = uart.read()
        if recv:
            print(recv)
        else:
            print("Timeout")

        time_wait -= 1
        time.sleep_ms(100)

    print(f"Stop receiving now")

def test_standalone():
    upload_bitstream("bitstreams/all_zeros.bit")
    time.sleep_ms(1)

    print(f"Writing the bitstream bitstreams/Static.bit !")
    upload_bitstream("bitstreams/Static.bit")

    print(f"Writing the bitstream bitstreams/Interleave.bit in Slot 1 !")
    upload_bitstream("bitstreams/Interleave.bit")

    print(f"Writing the bitstream bitstreams/Reverse.bit in Slot 2 !")
    upload_bitstream("bitstreams/Reverse.bit", tile_x_offset=2)
    time.sleep_ms(1)

    print(f"Writing the bitstream bitstreams/Interleave.bit in Slot 2 !")
    upload_bitstream("bitstreams/Interleave.bit", tile_x_offset=2)

    time.sleep_ms(1)
    print(f"Writing the bitstream bitstreams/Reverse.bit in Slot 1!")
    upload_bitstream("bitstreams/Reverse.bit")

    time.sleep_ms(1)
    print("Finished test")

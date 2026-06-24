import os
import time
import machine

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

def verify_bitstream_spi(filename, spi_master, cs, active_low=True):
    with open(filename, 'br') as f:
        txdata = f.read(4)
        rxdata = bytearray(4)
        while txdata:
            try:
                cs(not active_low)
                spi_master.write_readinto(txdata, rxdata)
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

def write_bitstream(filepath:str, spi_master, cs, static_file:Path=None, tile_x_offset:int=0):
    # Load static bitstream
    loaded_static_bitstream = None
    if static_file:
        loaded_static_bitstream = await load_bitstream(static_file)

    # Load bitstream
    loaded_bitstream = await load_bitstream(filepath, tile_x_offset)

    # Write bitstream to spi
    len_pre_bitstream = int(len(loaded_bitstream["data"]["pre_frame"])/4)
    for i_word in range(len_pre_bitstream):
        bitstream_word = loaded_bitstream["data"]["pre_frame"][i_word*4:(i_word+1)*4]
        print("Bitstream pre word %d of %d" % (i_word, len_pre_bitstream-1))
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

            print("Bitstream word %d of %d" % ((i_frame*19)+i_frame_word, len_bitstream-1))
            try:
                cs(not active_low)
                spi_master.write(bitstream_word)
            finally:
                cs(active_low)

    len_post_bitstream = int(len(loaded_bitstream["data"]["post_frame"])/4)
    for i_word in range(len_post_bitstream):
        bitstream_word = loaded_bitstream["data"]["post_frame"][i_word*4:(i_word+1)*4]
        print("Bitstream post word %d of %d" % (i_word, len_post_bitstream-1))
        try:
            cs(not active_low)
            spi_master.write(bitstream_word)
        finally:
            cs(active_low)

    print("Finished bitstream upload")

def upload_bitstream(bitstream, freq=25_175_000):
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
    write_bitstream_spi(bitstream, fpga_spi, fpga_cs_n)
    
    pwm0 = machine.PWM(clock, freq=freq, duty_u16=32768) # 50% duty
    print(pwm0.freq())

def upload_firmware(firmware, freq=25_175_000):
    print(f"freq: {machine.freq()}")

    # Setup
    clock   = machine.Pin(0, machine.Pin.OUT)
    reset_n = machine.Pin(1, machine.Pin.OUT)

    # Check if Greyhound is disabled and wait until it is
    input("Power down Greyhound by removing the power jumpers. Then press Enter to continue...")

    # FLASH
    # FLASH_CLK -> SCLK
    # FLASH_CS_N -> SCS_N
    # IO0 -> MOSI
    # IO1 -> MISO

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

    print(f"Writing the firmware {firmware} !")
    write_bitstream_spi(firmware, fpga_spi, flash_cs_n)

    print(f"Check firmware integrity")
    verify_bitstream_spi(firmware, fpga_spi, flash_cs_n)

    input("Firmware upload complete power up Greyhound by inserting the power jumpers. Then press Enter to continue...")

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

    pwm0 = machine.PWM(clock, freq=freq, duty_u16=32768) # 50% duty
    print(pwm0.freq())

def test_standalone():
    upload_bitstream("bitstreams/Static.bit")

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

    print(f"Writing the bitstream bitstreams/Static.bit !")
    write_bitstream("bitstreams/Static.bit", fpga_spi, fpga_cs_n)
    print("Uploaded static bitstream")

    print(f"Writing the bitstream bitstreams/Counter.bit !")
    write_bitstream("bitstreams/Counter.bit", fpga_spi, fpga_cs_n, "bitstreams/Static-full.bit")
    print("Uploaded bitstream")

    print(f"Writing the bitstream bitstreams/DirectOut.bit !")
    write_bitstream("bitstreams/DirectOut.bit", fpga_spi, fpga_cs_n, "bitstreams/Static-full.bit")
    print("Uploaded bitstream")
    time.sleep_ms(10)
    
    print(f"Writing the bitstream bitstreams/Crossover.bit !")
    write_bitstream("bitstreams/Crossover.bit", fpga_spi, fpga_cs_n, "bitstreams/Static-full.bit")
    print("Uploaded bitstream")
    
    time.sleep_ms(10)
    print(f"Writing the bitstream bitstreams/Graycode.bit !")
    write_bitstream("bitstreams/Graycode.bit", fpga_spi, fpga_cs_n, "bitstreams/Static-full.bit")
    print("Uploaded bitstream")
    
    time.sleep_ms(10)
    print(f"Writing the bitstream bitstreams/DirectOut.bit !")
    write_bitstream("bitstreams/DirectOut.bit", fpga_spi, fpga_cs_n, "bitstreams/Static-full.bit")
    print("Uploaded bitstream")

    time.sleep_ms(10)
    print("Finished test")
    
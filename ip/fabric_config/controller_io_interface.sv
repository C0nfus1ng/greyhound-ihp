// SPDX-FileCopyrightText: © 2026 Stefan Huwar <stefan.huwar@gmail.com>
// SPDX-License-Identifier: Apache-2.0

module controller_io_interface (
    // IOs
    input  logic clk_i,
    input  logic rst_n_sync_i,
    input  logic mode_i,      // fpga_mode
    input  logic c_clk_i,     // sclk/jtck
    input  logic select_i,    // cs_n/tms
    input  logic pico_i,      // mosi/tdi
    input  logic poci_i,      // miso/tdo
    output logic select_o,    // cs_n/tms
    output logic pico_o,      // mosi/tdi
    output logic poci_o,      // miso/tdo
    output logic c_clk_o,     // sclk/jtck
    output logic c_clk_oe_o,  // sclk/jtck
    output logic select_oe_o, // cs_n/tms
    output logic pico_oe_o,   // mosi/tdi
    output logic poci_oe_o,   // miso/tdo

    // SPI controller
    input  logic spi_controller_cs_ni,
    input  logic spi_controller_mosi_i,
    output logic spi_controller_miso_o,
    input  logic spi_controller_sclk_i,

    output logic [12:0] spi_controller_slot_chunk_addr_o,
    output logic [2:0]  spi_controller_slot_offset_o,
    output logic [4:0]  spi_controller_col_offset_o,
    output logic        spi_controller_start_o,
    input  logic [31:0] spi_controller_bitstream_data_i,
    input  logic        spi_controller_bitstream_valid_i,
    output logic        spi_controller_bitstream_finish_o,

    input  logic        fabric_warmboot_boot_i,
    input  logic [12:0] fabric_warmboot_slot_chunk_addr_i,
    input  logic        cpu_warmboot_boot_i,
    input  logic [12:0] cpu_warmboot_slot_chunk_addr_i,
    input  logic [2:0]  cpu_warmboot_slot_offset_i,
    input  logic [4:0]  cpu_warmboot_col_offset_i,
    input  logic        fabric_busy_i,
    input  logic        fabric_configured_i,

    // SPI receiver
    output logic spi_receiver_cs_no,
    output logic spi_receiver_mosi_o,
    input  logic spi_receiver_miso_i,
    
    output logic spi_receiver_enable_o,
    input  logic [31:0] spi_receiver_bitstream_data_i,
    input  logic spi_receiver_bitstream_valid_i,

    output logic [31:0] spi_bitstream_data_o,
    output logic spi_bitstream_valid_o,

    // JTAG
    input  logic en_jtag_receiver_i,
    input  logic jtag_tdo_i,
    output logic jtag_tms_o,
    output logic jtag_tdi_o,
    output logic jtag_trst_n_sync_o,

    output logic c_clk_rising_o,
    output logic c_clk_falling_o
);
    // Due to lack of pins fpga_mode_i is double used

    // Sync mode pin
    logic [1:0] mode_d;
    logic mode_sync;
    always_ff @(posedge clk_i) begin
        mode_d <= {mode_d[0], mode_i};
    end
    assign mode_sync = mode_d[1];
    assign spi_receiver_enable_o = mode_sync;

    // Create rst signal for the jtag modules
    assign jtag_trst_n_sync_o = (en_jtag_receiver_i | !rst_n_sync_i) ? mode_sync : 1'b1;

    // Create synced clk
    logic [2:0] c_clk_d;
    always_ff @(posedge clk_i) begin
        if (!jtag_trst_n_sync_o) begin
            c_clk_d <= '0;
        end
        else begin
            c_clk_d <= {c_clk_d[1:0], c_clk_i};
        end
    end

    assign c_clk_falling_o = c_clk_d[2] && !c_clk_d[1];
    assign c_clk_rising_o  = !c_clk_d[2] && c_clk_d[1];

    // Sync select_i
    logic [1:0] select_d;
    logic select_sync;
    always_ff @(posedge clk_i) begin
        select_d <= {select_d[0], select_i};
    end
    assign select_sync = select_d[1];

    // Sync pico_i
    logic [1:0] pico_d;
    logic pico_sync;
    always_ff @(posedge clk_i) begin
        pico_d <= {pico_d[0], pico_i};
    end
    assign pico_sync = pico_d[1];

    // At startup, trigger configuration
    // when fpga_mode_sync == 1'b0
    logic startup_trigger;
    always_ff @(posedge clk_i) begin
        if (!rst_n_sync_i) begin
            startup_trigger <= 1'b1;
        end else begin
            startup_trigger <= 1'b0;
        end
    end

    logic        fabric_warmboot_boot;
    logic [ 2:0] fabric_warmboot_slot_offset;
    logic [ 4:0] fabric_warmboot_col_offset;
    logic [12:0] fabric_warmboot_slot_chunk_addr;

    // IO <--> Controller mux
    always_comb begin
        // Default IOs
        c_clk_o     = 1'b0;
        select_o    = 1'b0;
        pico_o      = 1'b0;
        poci_o      = 1'b0;
        
        c_clk_oe_o  = 1'b0;
        select_oe_o = 1'b0;
        pico_oe_o   = 1'b0;
        poci_oe_o   = 1'b0;

        // JTAG not selected
        jtag_tms_o = 1'b0;
        jtag_tdi_o = 1'b0;

        // SPI receiver not selected
        spi_receiver_cs_no  = 1'b1;
        spi_receiver_mosi_o = 1'b0;

        // SPI controller not selected
        spi_controller_miso_o = 1'b0;
        spi_controller_start_o  = '0;
        spi_controller_slot_chunk_addr_o = '0;
        spi_controller_slot_offset_o = '0;
        spi_controller_col_offset_o = '0;

        // No bitstream
        spi_bitstream_data_o  = '0;
        spi_bitstream_valid_o = '0;

        if (en_jtag_receiver_i) begin // JTAG
            poci_oe_o  = 1'b1;
            jtag_tms_o = select_sync;
            jtag_tdi_o = pico_sync;
            poci_o     = jtag_tdo_i;
        end
        else if (rst_n_sync_i && mode_sync) begin // SPI receiver
            poci_oe_o = 1'b1;

            spi_receiver_cs_no  = select_sync;
            spi_receiver_mosi_o = pico_sync;
            poci_o              = spi_receiver_miso_i;

            spi_bitstream_data_o  = spi_receiver_bitstream_data_i;
            spi_bitstream_valid_o = spi_receiver_bitstream_valid_i;
        end
        else if (rst_n_sync_i && !mode_sync) begin // SPI controller
            c_clk_oe_o  = 1'b1;
            select_oe_o = 1'b1;
            pico_oe_o   = 1'b1;

            c_clk_o               = spi_controller_sclk_i;
            select_o              = spi_controller_cs_ni;
            pico_o                = spi_controller_mosi_i;
            spi_controller_miso_o = poci_i;
        
            spi_bitstream_data_o  = spi_controller_bitstream_data_i;
            spi_bitstream_valid_o = spi_controller_bitstream_valid_i;
            spi_controller_start_o = startup_trigger || ((fabric_warmboot_boot || cpu_warmboot_boot_i) && !fabric_busy_i);
            spi_controller_slot_chunk_addr_o  = startup_trigger ? '0 : cpu_warmboot_boot_i ? cpu_warmboot_slot_chunk_addr_i : fabric_warmboot_slot_chunk_addr;
            spi_controller_slot_offset_o = startup_trigger ? '0 : cpu_warmboot_boot_i ? cpu_warmboot_slot_offset_i : fabric_warmboot_slot_offset;
            spi_controller_col_offset_o = startup_trigger ? '0 : cpu_warmboot_boot_i ? cpu_warmboot_col_offset_i : fabric_warmboot_col_offset;
        end
        else if (!rst_n_sync_i && mode_sync) begin // srst pulled, trst not -> do special init (configure for jtag input instead of spi)
            poci_oe_o = 1'b1;
            jtag_tms_o = select_sync;
            jtag_tdi_o = pico_sync;
            poci_o = jtag_tdo_i;
        end
    end

    logic fabric_configured_q, fabric_configured_pulse;
    logic [2:0] warmboot_boot_shift;
    always_ff @(posedge clk_i) begin
        if (!rst_n_sync_i) begin
            warmboot_boot_shift <= '0;
        end else begin
            if (fabric_configured_pulse) warmboot_boot_shift <= '0;
            else warmboot_boot_shift <= {warmboot_boot_shift[1:0], fabric_warmboot_boot_i};
        end
    end

    always_ff @(posedge clk_i) begin
        if (!rst_n_sync_i) begin
            fabric_configured_q <= '0;
        end else begin
            fabric_configured_q <= fabric_configured_i;
        end
    end

    assign fabric_configured_pulse = !fabric_configured_q & fabric_configured_i;

    always_ff @(posedge clk_i) begin
        if (!rst_n_sync_i) begin
            fabric_warmboot_slot_offset <= '0;
            fabric_warmboot_col_offset <= '0;
            fabric_warmboot_slot_chunk_addr <= '0;
            fabric_warmboot_boot <= 1'b0;
        end else begin
            fabric_warmboot_slot_chunk_addr[8:0] <= fabric_warmboot_slot_chunk_addr_i[8:0];
            fabric_warmboot_boot <= 1'b0;

            if (fabric_configured_pulse) fabric_warmboot_col_offset <= '0;

            case (warmboot_boot_shift)
                3'h1: begin
                    fabric_warmboot_slot_chunk_addr[12:9] <= fabric_warmboot_slot_chunk_addr_i[12:9];
                    if (!fabric_warmboot_boot_i) fabric_warmboot_boot <= 1'b1;
                end
                3'h3: begin
                    fabric_warmboot_slot_offset   <= fabric_warmboot_slot_chunk_addr_i[11:9];
                    fabric_warmboot_col_offset[0] <= fabric_warmboot_slot_chunk_addr_i[12];
                    if (!fabric_warmboot_boot_i) fabric_warmboot_boot <= 1'b1;
                end
                3'h7: begin
                    fabric_warmboot_col_offset[4:1] <= fabric_warmboot_slot_chunk_addr_i[12:9];
                    if (!fabric_warmboot_boot_i) fabric_warmboot_boot <= 1'b1;
                end
                default: ;
            endcase
        end
    end

    assign spi_controller_bitstream_finish_o = fabric_configured_pulse;
endmodule

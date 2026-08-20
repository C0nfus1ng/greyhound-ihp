// SPDX-FileCopyrightText: © 2025 Leo Moser <leo.moser@pm.me>
// SPDX-License-Identifier: Apache-2.0
// SPDX-FileContributor: Modified by Stefan Huwar <stefan.huwar@gmail.com>

`default_nettype none

/*
This SPI controller reads a bitstream from an
SPI Flash upon receiving a start_i pulse.
The starting address can be changed using the
slot_chunk_addr_i input.
The controller is for 16 warmboot slots and up to 16MB flash
*/

module fabric_spi_controller #(
    parameter FrameBitsPerRow = 32,
    parameter FrameSelectWidth = 5,
    parameter MaxFramesPerCol = 20,
    parameter NumColumns = 12,
	parameter NumRows = 18
)(
    input  logic  clk_i,
    input  logic  rst_ni,
    
    // Start reading data at selected slot
    input logic        start_i,
    input logic [12:0] slot_chunk_addr_i,
    
    // Bitstream data
    output logic [31:0] bitstream_data_o,
    output logic        bitstream_valid_o,
    
    // Reading in progress
    output logic  busy_o,
    
    // SPI
    output logic sclk_o,
    output logic cs_no,
    output logic mosi_o,
    input  logic miso_i,
    
    // Control
    input logic [2:0] slot_offset_i,
    input logic bitstream_finish_i,
    input logic [FrameSelectWidth-1:0] col_offset_i,
    input logic nextw_fheader_i
);
    // CPOL = 0, CPHA = 0
    localparam ROW_TILE_WORD = 12'h5E7;
    localparam READ_CMD = 8'h03;
    
    // Addr, generation
    logic [2:0] slot_offset;
    logic [12:0] slot_chunk_addr;
    always_comb begin
        casez (slot_offset_i)
            3'h0:    slot_chunk_addr = {9'h0, slot_chunk_addr_i[3:0]};
            3'h1:    slot_chunk_addr = {5'h0, slot_chunk_addr_i[12:9], slot_chunk_addr_i[3:0]};
            3'h2:    slot_chunk_addr = {4'h0, slot_chunk_addr_i[12:9], slot_chunk_addr_i[4:0]};
            3'h3:    slot_chunk_addr = {3'h0, slot_chunk_addr_i[12:9], slot_chunk_addr_i[5:0]};
            3'h4:    slot_chunk_addr = {2'h0, slot_chunk_addr_i[12:9], slot_chunk_addr_i[6:0]};
            3'h5:    slot_chunk_addr = {1'h0, slot_chunk_addr_i[12:9], slot_chunk_addr_i[7:0]};
            3'h6:    slot_chunk_addr = slot_chunk_addr_i;
            default: slot_chunk_addr = '0;
        endcase
    end

    logic [31:0] shift_register;
    logic [4:0] shift_cnt;
    logic [21:0] address_counter_words;
    
    // States
    typedef enum {
        S_IDLE,
        S_LOAD_ADDR,
        S_SHIFT_ADDR,
        S_LOAD_DATA,
        S_SHIFT_DATA,
        S_WRITE_DATA,
        S_JUMP_ADDR
    } state_t;
    
    state_t curr_state;
    state_t next_state;

    logic inhibit_load_row_tiles;
    logic [1:0] use_tile;
    logic [1:0] loaded_row_tiles_word;

    // Next state logic
    always_comb begin
        next_state = curr_state;

        case (curr_state)
            S_IDLE:
                if (start_i) next_state = S_LOAD_ADDR;
            S_LOAD_ADDR:
                next_state = S_SHIFT_ADDR;
            S_SHIFT_ADDR:
                if (shift_cnt == '0 && sclk_o) next_state = S_LOAD_DATA;
            S_LOAD_DATA:
                next_state = S_SHIFT_DATA;
            S_SHIFT_DATA:
                if (shift_cnt == '0 && sclk_o) next_state = S_WRITE_DATA;
            S_WRITE_DATA:
                if (((nextw_fheader_i || loaded_row_tiles_word[0]) && !inhibit_load_row_tiles) || use_tile == 2'h1 || use_tile == 2'h2) next_state = S_JUMP_ADDR;
                else next_state = S_LOAD_DATA;
            S_JUMP_ADDR:
                if (sclk_o) next_state = S_SHIFT_ADDR;
        endcase

        if (bitstream_finish_i) next_state = S_IDLE;
    end

    assign busy_o = curr_state != S_IDLE;

    // State transition
    always_ff @(posedge clk_i, negedge rst_ni) begin
        if (!rst_ni) begin
            curr_state <= S_IDLE;
        end else begin
            curr_state <= next_state;
        end
    end
    
    // Add offset to bitstream
    logic [31:0] bitstream_data;
    logic [21:0] address_words;
    logic [21:0] row_tiles_address_counter_words;
    logic [FrameSelectWidth-1:0] col_offset;
    logic fabric_bitstream_started;

    always_ff @(posedge clk_i, negedge rst_ni) begin
        if (!rst_ni) begin
            shift_cnt <= '0;
            shift_register <= '0;
            sclk_o <= 1'b0;
            bitstream_data_o <= '0;
            bitstream_valid_o <= '0;
            address_counter_words <= '0;
            col_offset <= '0;
            loaded_row_tiles_word <= '0;
            slot_offset <= '0;
        end else begin
            bitstream_valid_o <= 1'b0;
            loaded_row_tiles_word[1] <= '0;
        
            case (curr_state)
                S_IDLE: begin
                    if (start_i) begin
                        address_counter_words <= {slot_chunk_addr, 9'h0};
                        col_offset <= col_offset_i;
                        slot_offset <= slot_offset_i;
                    end
                    
                    sclk_o <= 1'b0;
                end
                S_LOAD_ADDR: begin
                    shift_cnt <= 31;
                    shift_register <= {READ_CMD, {address_words, 2'b00}};
                    sclk_o <= 1'b0;
                end
                S_SHIFT_ADDR: begin
                    sclk_o <= !sclk_o;

                    // On falling edge of sclk
                    if (sclk_o) begin
                        shift_cnt <= shift_cnt-1;
                        shift_register <= {shift_register[30:0], miso_i};
                    end
                end

                S_LOAD_DATA: begin
                    shift_cnt <= 31;
                    sclk_o <= 1'b0;
                end
                S_SHIFT_DATA: begin
                    sclk_o <= !sclk_o;

                    // On falling edge of sclk
                    if (!bitstream_finish_i & sclk_o) begin
                        shift_cnt <= shift_cnt-1;
                        shift_register <= {shift_register[30:0], miso_i};
                    end
                end
                S_WRITE_DATA: begin
                    if ((nextw_fheader_i || loaded_row_tiles_word[0]) && !inhibit_load_row_tiles) begin
                        loaded_row_tiles_word[0] <= ~loaded_row_tiles_word[0];
                        loaded_row_tiles_word[1] <= loaded_row_tiles_word[0];
                    end
                    
                    if (!loaded_row_tiles_word[0]) begin
                        address_counter_words <= address_counter_words + 22'd1;

                        bitstream_data_o <= bitstream_data;
                        bitstream_valid_o <= 1'b1;
                    end
                end
                S_JUMP_ADDR: begin
                    sclk_o <= !sclk_o;

                    shift_cnt <= 31;
                    shift_register <= {READ_CMD, {address_words, 2'b00}};
                end
            endcase
        end
    end

    // MSB first
    assign mosi_o = shift_register[31];
    
    // CS active when not idle
    assign cs_no = (curr_state == S_IDLE) || bitstream_finish_i || (curr_state == S_JUMP_ADDR);

    logic currw_fheader;
    logic [NumRows-2:0] row_tiles;
    logic [31:0] header_word;

    always_ff @(posedge clk_i, negedge rst_ni) begin
        if (!rst_ni) begin
            fabric_bitstream_started <= '0;
            row_tiles_address_counter_words <= '0;
            row_tiles <= '1;
            inhibit_load_row_tiles <= '0;
            currw_fheader <= '0;
            use_tile <= '1;
            header_word <= '0;
        end else begin
            currw_fheader <= '0;

            if (nextw_fheader_i && (curr_state == S_WRITE_DATA)) begin
                row_tiles_address_counter_words <= row_tiles_address_counter_words - 1;
                currw_fheader <= 1'b1;
                header_word <= bitstream_data;
            end

            if (!fabric_bitstream_started && nextw_fheader_i && (curr_state == S_WRITE_DATA)) begin 
                row_tiles_address_counter_words <= address_counter_words - 2;
                fabric_bitstream_started <= '1;
            end
            
            if (bitstream_finish_i) inhibit_load_row_tiles <= '0;

            if (loaded_row_tiles_word[1]) begin
                if (shift_register[31:20] == ROW_TILE_WORD) begin
                    {use_tile[0], row_tiles} <= shift_register[NumRows-1:0];
                end 
                else begin
                    inhibit_load_row_tiles <= '1;
                    row_tiles <= '1;
                    use_tile[0] <= '1;
                end
            end

            if (start_i) fabric_bitstream_started <= '0;

            if (next_state == S_WRITE_DATA) begin
                row_tiles <= {row_tiles[NumRows-3:0], 1'b1};
                use_tile <= {use_tile[0], row_tiles[NumRows-2]};
            end
        end
    end

    logic [12:0] header_addr;
    logic [12:0] header_col_addr;
    logic [12:0] header_frame_addr;

    always_ff @(posedge clk_i, negedge rst_ni) begin
        if (!rst_ni) begin
            header_addr <= '0;
        end else begin
            if (!loaded_row_tiles_word[0] && (curr_state == S_WRITE_DATA)) begin
                header_addr <= header_addr + 13'd1;
            end
            
            if (currw_fheader) begin
                header_addr <= header_frame_addr;
            end
        end
    end

    generate
        always_comb begin
            header_col_addr = '0;

            for (logic [$clog2(NumColumns)-1:0] i = 0; i < NumColumns; i++) begin
                if (i == $clog2(NumColumns)'(header_word[FrameBitsPerRow-1:FrameBitsPerRow-FrameSelectWidth])) begin
                    header_col_addr = 13'(6+(MaxFramesPerCol*(NumRows+1)*i));
                end
            end
        end

        always_comb begin
            header_frame_addr = '0;

            for (int i = 0; i < MaxFramesPerCol; i++) begin
                if (header_word[i]) begin
                    header_frame_addr = header_col_addr + 13'((MaxFramesPerCol-1)*i);
                end
            end
        end
    endgenerate

    always_comb begin
        bitstream_data = shift_register;
        address_words = address_counter_words;

        if (loaded_row_tiles_word[0]) address_words = row_tiles_address_counter_words;
        if (nextw_fheader_i) bitstream_data[FrameBitsPerRow-1:FrameBitsPerRow-FrameSelectWidth] = shift_register[FrameBitsPerRow-1:FrameBitsPerRow-FrameSelectWidth] + col_offset;

        if ((use_tile == 2'h2) && !inhibit_load_row_tiles) begin
            casez (slot_offset)
                3'h0:    address_words = {9'h0, header_addr};
                3'h1:    address_words = {5'h0, address_counter_words[16:13], header_addr};
                3'h2:    address_words = {4'h0, address_counter_words[17:14], 1'h0, header_addr};
                3'h3:    address_words = {3'h0, address_counter_words[18:15], 2'h0, header_addr};
                3'h4:    address_words = {2'h0, address_counter_words[19:16], 3'h0, header_addr};
                3'h5:    address_words = {1'h0, address_counter_words[20:17], 4'h0, header_addr};
                3'h6:    address_words = {address_counter_words[21:18], 5'h0, header_addr};
                default: address_words = '0;
            endcase
        end
    end
endmodule

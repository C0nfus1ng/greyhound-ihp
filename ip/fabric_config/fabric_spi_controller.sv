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

module fabric_spi_controller (
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
    input logic [5:0] slot_offset_i,
    input logic bitstream_finish
);
    // CPOL = 0, CPHA = 0

    localparam READ_CMD = 8'h03;
    
    // Addr, generation
    logic [12:0] slot_chunk_addr;
    always_comb begin
        case (slot_offset_i)
            6'b000000: slot_chunk_addr = {9'h0, slot_chunk_addr_i[3:0]};
            6'b?????1: slot_chunk_addr = {5'h0, slot_chunk_addr_i[12:9], slot_chunk_addr_i[3:0]};
            6'b????1?: slot_chunk_addr = {4'h0, slot_chunk_addr_i[12:9], slot_chunk_addr_i[4:0]};
            6'b???1??: slot_chunk_addr = {3'h0, slot_chunk_addr_i[12:9], slot_chunk_addr_i[5:0]};
            6'b??1???: slot_chunk_addr = {2'h0, slot_chunk_addr_i[12:9], slot_chunk_addr_i[6:0]};
            6'b?1????: slot_chunk_addr = {1'h0, slot_chunk_addr_i[12:9], slot_chunk_addr_i[7:0]};
            6'b1?????: slot_chunk_addr = {slot_chunk_addr_i[12:9], slot_chunk_addr_i[8:0]};
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
        S_WRITE_DATA
    } state_t;
    
    state_t curr_state;
    state_t next_state;

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
                if (bitstream_finish) next_state = S_IDLE;
                else next_state = S_SHIFT_DATA;
            S_SHIFT_DATA:
                if (shift_cnt == '0 && sclk_o) next_state = S_WRITE_DATA;
            S_WRITE_DATA:
                next_state = S_LOAD_DATA;
        endcase
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
    
    always_ff @(posedge clk_i, negedge rst_ni) begin
        if (!rst_ni) begin
            shift_cnt <= '0;
            shift_register <= '0;
            sclk_o <= 1'b0;
            bitstream_data_o <= '0;
            bitstream_valid_o <= '0;
            address_counter_words <= '0;
        end else begin
            bitstream_valid_o <= 1'b0;
        
            case (curr_state)
                S_IDLE: begin
                    if (start_i) begin
                        address_counter_words <= {slot_chunk_addr, 9'h0};
                    end
                    
                    sclk_o <= 1'b0;
                end
                S_LOAD_ADDR: begin
                    shift_cnt <= 31;
                    shift_register <= {READ_CMD, {address_counter_words, 2'b00}};
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
                    //shift_register <= {READ_CMD, address_counter_words};
                    sclk_o <= 1'b0;
                end
                S_SHIFT_DATA: begin
                    sclk_o <= !sclk_o;

                    // On falling edge of sclk
                    if (sclk_o) begin
                        shift_cnt <= shift_cnt-1;
                        shift_register <= {shift_register[30:0], miso_i};
                    end
                end
                S_WRITE_DATA: begin
                    address_counter_words <= address_counter_words + 1;
                    
                    bitstream_data_o <= shift_register;
                    bitstream_valid_o <= 1'b1;
                end
            endcase
        end
    end

    // MSB first
    assign mosi_o = shift_register[31];
    
    // CS active when not idle
    assign cs_no = !(curr_state != S_IDLE);

endmodule

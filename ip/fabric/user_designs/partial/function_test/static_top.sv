`default_nettype none

module top(
    input  wire        clk,
    input  wire [`NUM_IO-1:0] io_in,
    output wire [`NUM_IO-1:0] io_out,
    output wire [`NUM_IO-1:0] io_oeb,
);
    logic rst;

    static_slot slot_i(
        .clk,

        .slot1_o (io_out[0]),
        .slot1_i ({3'b0, rst}),
        .slot2_o (io_out[1]),
        .slot2_i ({3'b0, rst}),
        .slot3_o (io_out[2]),
        .slot3_i ({3'b0, rst}),
    );

    assign io_oeb = '0;
    assign io_out[31:3] = '0;

    WARMBOOT_wrapper WARMBOOT_wrapper (
        .SLOT   (4'd0),
        .BOOT   (1'b0),
        .RESET  (rst)
    );
endmodule
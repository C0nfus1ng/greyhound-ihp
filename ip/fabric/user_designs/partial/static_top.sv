`default_nettype none

module top(
    input  wire        clk,
    input  wire [`NUM_IO-1:0] io_in,
    output wire [`NUM_IO-1:0] io_out,
    output wire [`NUM_IO-1:0] io_oeb,
);
    logic rst;

    wire       lut0_o, lut1_o;
    wire [3:0] lut0_i, lut1_i;

    static_slot slot_i(
    .clk,

    .lut0_o(lut0_o),
    .lut0_i(lut0_i),
    .lut1_o(lut1_o),
    .lut1_i(lut1_i),
    );

    assign io_oeb = '0;
    assign io_out[0]    = lut0_o;
    assign io_out[1]    = lut1_o;
    assign io_out[31:2] = '0;
    assign lut0_i[3:1]  = '0;
    assign lut0_i[0]    = rst;
    assign lut1_i[3:1]  = '0;
    assign lut1_i[0]    = rst;

    WARMBOOT_wrapper WARMBOOT_wrapper (
        .SLOT   (4'd0),
        .BOOT   (1'b0),
        .RESET  (rst)
    );
endmodule
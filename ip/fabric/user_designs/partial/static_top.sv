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
    // assign io_out = 32'hdeadbeef;
    assign io_out[0]    = lut0_o;
    assign io_out[1]    = lut1_o;
    assign io_out[31:2] = '0;
    assign lut0_i[3:1]  = '0;
    assign lut0_i[0]    = rst;
    assign lut1_i[3:1]  = '0;
    assign lut1_i[0]    = rst;

    // IO Arbiter
    // logic rst;
    // logic [1:0] slot_q, slot_d;
    // logic [`NUM_IO-1:0] io_out_buf_q, io_out_buf_d, io_oeb_q, io_oeb_d;
    // logic [`NUM_IO-1:0] io_out_slot_0, io_out_slot_1, io_out_slot_2, io_oeb_slot_0, io_oeb_slot_1, io_oeb_slot_2;

    // assign io_oeb = io_oeb_q;
    // assign io_out = io_out_buf_q;
    // always_comb begin
    //     case (slot_q)
    //         2'h0: begin
    //             io_out_buf_d = io_out_slot_0;
    //             io_oeb_d     = io_oeb_slot_0;
    //         end
    //         2'h1: begin
    //             io_out_buf_d = io_out_slot_1;
    //             io_oeb_d     = io_oeb_slot_1;
    //         end
    //         2'h2: begin
    //             io_out_buf_d = io_out_slot_2;
    //             io_oeb_d     = io_oeb_slot_2;
    //         end
    //         default: begin
    //             io_out_buf_d = '0;
    //             io_oeb_d     = '0;
    //         end
    //     endcase
    // end

    // assign slot_d = slot_q + 2'h1;
    // always_ff @(posedge clk) begin
    //     if (rst) begin
    //         io_out_buf_q <= '0;
    //         io_oeb_q     <= '0;
    //         slot_q       <= '0;
    //     end
    //     else begin
    //         io_out_buf_q <= io_out_buf_d;
    //         io_oeb_q     <= io_oeb_d;
    //         slot_q       <= slot_d;
    //     end
    // end

    WARMBOOT_wrapper WARMBOOT_wrapper (
        .SLOT   (4'd0),
        .BOOT   (1'b0),
        .RESET  (rst)
    );

    // // Slot logic (TODO as pre compiled module bitstream...?)
    // slot0 zero (
    //     .clk,
    //     .rst,
    //     .io_in  ( '0            ),
    //     .io_out ( io_out_slot_0 ),
    //     .io_oeb ( io_oeb_slot_0 )
    // );

    // slot1 one (
    //     .clk,
    //     .rst,
    //     .io_in  ( '0            ),
    //     .io_out ( io_out_slot_1 ),
    //     .io_oeb ( io_oeb_slot_1 )
    // );

    // slot2 two (
    //     .clk,
    //     .rst,
    //     .io_in  ( '0            ),
    //     .io_out ( io_out_slot_2 ),
    //     .io_oeb ( io_oeb_slot_2)
    // );

endmodule
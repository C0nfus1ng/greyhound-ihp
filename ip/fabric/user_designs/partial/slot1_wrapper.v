module slot1_wrapper;

// Slot

wire lut_o;
wire [3:0] lut_in;
// Regex: #Tile_X(?:[0,1,3-9]|1[0-1])Y(?:[0-9]|1[0-7])([\s\S\n]*?)(?=\n#)
// (* keep, BEL="X4Y1.A" *) LUT4 #(.INIT(16'h2)) lut4_x4y1a (.I0(lut_in[0]), .I1(lut_in[1]), .I2(lut_in[2]), .I3(lut_in[3]));
// (* keep, BEL="X4Y1.B" *) LUT4 #(.INIT(16'h2)) lut4_x4y1b (.O(lut_o));

(* keep, BEL="X4Y1.S" *) slot_con x2y1b (.E1END0(lut_in[0]), .E1END1(lut_in[1]), .E1END2(lut_in[2]), .E1END3(lut_in[3]), .W1BEG0(lut_o));

wire clk;
(* keep *) Global_Clock clk_i (.CLK(clk));

slot1 slot1_i(.clk(clk), .lut4_o_i(lut_in), .lut4_in_o(lut_o));

endmodule

(* blackbox, keep *)
module slot_con (
    // input wire N1END0,
    // input wire N1END1,
    // input wire N1END2,
    // input wire N1END3,
    output E1END0,
    output E1END1,
    output E1END2,
    output E1END3,

    input W1BEG0,
    // input wire E1BEG1,
    // input wire E1BEG2,
    // input wire E1BEG3,
    // input wire E2BEG0,
    // input wire E2BEG1,
    // input wire E2BEG2,
    // input wire E2BEG3,
    // input wire E2BEG4,
    // input wire E2BEG5,
    // input wire E2BEG6,
    // input wire E2BEG7,

    // input wire LA_I0,
    // input wire LA_I1,
    // input wire LA_I2,
    // input wire LA_I3,

    // input wire  E2MID5,
);
endmodule

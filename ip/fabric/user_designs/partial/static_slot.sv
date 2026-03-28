module static_slot(
    input  wire        clk,

    output wire        lut0_o,
    input  wire [3:0]  lut0_i,
    output wire        lut1_o,
    input  wire [3:0]  lut1_i,
);

// Slot BEL placement TODO rework

// Regex: #Tile_X(?:[0,1,3-9]|1[0-1])Y(?:[0-9]|1[0-7])([\s\S\n]*?)(?=\n#)
// (* keep, BEL="X2Y1.A" *) LUT4 #(.INIT(16'h2)) lut4_x2y1a (.O(lut0_o));
// (* keep, BEL="X2Y1.B" *) LUT4 #(.INIT(16'h2)) lut4_x2y1b (.I0(lut0_i[0]), .I1(lut0_i[1]), .I2(lut0_i[2]), .I3(lut0_i[3]));

//(* keep, BEL="X4Y1.A" *) LUT4 #(.INIT(16'h2)) lut4_x4y1a (.O(lut1_o));
//(* keep, BEL="X4Y1.B" *) LUT4 #(.INIT(16'h2)) lut4_x4y1b (.I0(lut1_i[0]), .I1(lut1_i[1]), .I2(lut1_i[2]), .I3(lut1_i[3]));

(* keep, BEL="X2Y1.S" *) slot_con slot0_x2y1 (.E1END0(lut0_i[0]), .E1END1(lut0_i[1]), .E1END2(lut0_i[2]), .E1END3(lut0_i[3]), .W1BEG0(lut0_o));

(* keep, BEL="X4Y1.S" *) slot_con slot1_x4y1 (.E1END0(lut1_i[0]), .E1END1(lut1_i[1]), .E1END2(lut1_i[2]), .E1END3(lut1_i[3]), .W1BEG0(lut1_o));


endmodule


(* blackbox, keep *)
module slot_con (
    // input wire N1END0,
    // input wire N1END1,
    // input wire N1END2,
    // input wire N1END3,
    input E1END0,
    input E1END1,
    input E1END2,
    input E1END3,

    output W1BEG0,
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

module static_slot(
    input  wire        clk,

    output wire        lut0_o,
    input  wire [3:0]  lut0_i,
    output wire        lut1_o,
    input  wire [3:0]  lut1_i,
);

// Slot BEL placement
(* keep, BEL="X2Y1.A" *) Static_slot_con_X2Y1 slot1_x2y1 (.E1END0(lut0_i[0]), .E1END1(lut0_i[1]), .E1END2(lut0_i[2]), .E1END3(lut0_i[3]), .W1BEG0(lut0_o));
(* keep, BEL="X4Y1.A" *) Static_slot_con_X4Y1 slot2_x4y1 (.E1END0(lut1_i[0]), .E1END1(lut1_i[1]), .E1END2(lut1_i[2]), .E1END3(lut1_i[3]), .W1BEG0(lut1_o));
endmodule

module static_slot(
    input  wire        clk,

    output wire        slot1_o,
    input  wire [3:0]  slot1_i,
    output wire        slot2_o,
    input  wire [3:0]  slot2_i,
    output wire        slot3_o,
    input  wire [3:0]  slot3_i,
);

// Slot BEL placement
(* keep, BEL="X2Y1.A" *) Static_slot_con_X2Y1 slot1_x2y1 (.E1END0(slot1_i[0]), .E1END1(slot1_i[1]), .E1END2(slot1_i[2]), .E1END3(slot1_i[3]), .W1BEG0(slot1_o));
(* keep, BEL="X4Y1.A" *) Static_slot_con_X4Y1 slot2_x4y1 (.E1END0(slot2_i[0]), .E1END1(slot2_i[1]), .E1END2(slot2_i[2]), .E1END3(slot2_i[3]), .W1BEG0(slot2_o));
(* keep, BEL="X5Y1.A" *) Static_slot_con_X5Y1 slot3_x5y1 (.E1END0(slot3_i[0]), .E1END1(slot3_i[1]), .E1END2(slot3_i[2]), .E1END3(slot3_i[3]), .W1BEG0(slot3_o));
endmodule

module slot4_wrapper;

// Slot
wire [1:0] slot_o;
wire [7:0] slot_i;

(* keep, BEL="X4Y1.A" *) Slot4_slot_con_X4Y1 x4y1 (.E1END0(slot_i[0]), .E1END1(slot_i[1]), .E1END2(slot_i[2]), .E1END3(slot_i[3]), .W1BEG0(slot_o[0]));
(* keep, BEL="X5Y1.A" *) Slot4_slot_con_X5Y1 x5y1 (.E1END0(slot_i[4]), .E1END1(slot_i[5]), .E1END2(slot_i[6]), .E1END3(slot_i[7]), .W1BEG0(slot_o[1]));

wire clk;
(* keep *) Global_Clock clk_i (.CLK(clk));

slot4 slot4_i(.clk, .slot_i, .slot_o);

endmodule

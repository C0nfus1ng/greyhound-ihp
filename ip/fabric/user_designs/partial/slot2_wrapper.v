module slot2_wrapper;

// Slot
wire slot_o;
wire [3:0] slot_i;

(* keep, BEL="X4Y1.A" *) Slot2_slot_con_X4Y1 x4y1 (.E1END0(slot_i[0]), .E1END1(slot_i[1]), .E1END2(slot_i[2]), .E1END3(slot_i[3]), .W1BEG0(slot_o));

wire clk;
(* keep *) Global_Clock clk_i (.CLK(clk));

slot2 slot2_i(.clk, .slot_i, .slot_o);

endmodule

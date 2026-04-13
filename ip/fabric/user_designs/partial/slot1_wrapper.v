module slot1_wrapper;

// Slot
wire lut_o;
wire [3:0] lut_in;

(* keep, BEL="X2Y1.A" *) Slot1_slot_con_X2Y1 x2y1 (.E1END0(lut_in[0]), .E1END1(lut_in[1]), .E1END2(lut_in[2]), .E1END3(lut_in[3]), .W1BEG0(lut_o));

wire clk;
(* keep *) Global_Clock clk_i (.CLK(clk));

slot1 slot1_i(.clk(clk), .lut4_o_i(lut_in), .lut4_in_o(lut_o));

endmodule

module slot2_wrapper;

// Slot
wire lut_o;
wire [3:0] lut_in;

(* keep, BEL="X4Y1.A" *) Slot2_slot_con_X4Y1 x4y1 (.E1END0(lut_in[0]), .E1END1(lut_in[1]), .E1END2(lut_in[2]), .E1END3(lut_in[3]), .W1BEG0(lut_o));

wire clk;
(* keep *) Global_Clock clk_i (.CLK(clk));

slot2 slot2_i(.clk(clk), .lut4_o_i(lut_in), .lut4_in_o(lut_o));

endmodule

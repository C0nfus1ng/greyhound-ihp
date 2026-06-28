module io_wrapper #(
    parameter NUM_IO = 32
) (
    input  logic [NUM_IO-1:0] io_i,
    input  logic [NUM_IO-1:0] io_oeb_i,
    output logic [NUM_IO-1:0] io_o,
);
    // West
    (* keep, BEL="X0Y1.A" *) IO_1_bidirectional_frame_config_pass io27_i (.O(io_o[27]), .I(io_i[27]), .T(io_oeb_i[27]));
    (* keep, BEL="X0Y1.B" *) IO_1_bidirectional_frame_config_pass io26_i (.O(io_o[26]), .I(io_i[26]), .T(io_oeb_i[26]));
    (* keep, BEL="X0Y2.A" *) IO_1_bidirectional_frame_config_pass io25_i (.O(io_o[25]), .I(io_i[25]), .T(io_oeb_i[25]));
    (* keep, BEL="X0Y2.B" *) IO_1_bidirectional_frame_config_pass io24_i (.O(io_o[24]), .I(io_i[24]), .T(io_oeb_i[24]));
    (* keep, BEL="X0Y3.A" *) IO_1_bidirectional_frame_config_pass io23_i (.O(io_o[23]), .I(io_i[23]), .T(io_oeb_i[23]));
    (* keep, BEL="X0Y3.B" *) IO_1_bidirectional_frame_config_pass io22_i (.O(io_o[22]), .I(io_i[22]), .T(io_oeb_i[22]));
    (* keep, BEL="X0Y4.A" *) IO_1_bidirectional_frame_config_pass io21_i (.O(io_o[21]), .I(io_i[21]), .T(io_oeb_i[21]));
    (* keep, BEL="X0Y4.B" *) IO_1_bidirectional_frame_config_pass io20_i (.O(io_o[20]), .I(io_i[20]), .T(io_oeb_i[20]));
    (* keep, BEL="X0Y5.A" *) IO_1_bidirectional_frame_config_pass io19_i (.O(io_o[19]), .I(io_i[19]), .T(io_oeb_i[19]));
    (* keep, BEL="X0Y5.B" *) IO_1_bidirectional_frame_config_pass io18_i (.O(io_o[18]), .I(io_i[18]), .T(io_oeb_i[18]));
    (* keep, BEL="X0Y6.A" *) IO_1_bidirectional_frame_config_pass io17_i (.O(io_o[17]), .I(io_i[17]), .T(io_oeb_i[17]));
    (* keep, BEL="X0Y6.B" *) IO_1_bidirectional_frame_config_pass io16_i (.O(io_o[16]), .I(io_i[16]), .T(io_oeb_i[16]));
    (* keep, BEL="X0Y7.A" *) IO_1_bidirectional_frame_config_pass io15_i (.O(io_o[15]), .I(io_i[15]), .T(io_oeb_i[15]));
    (* keep, BEL="X0Y7.B" *) IO_1_bidirectional_frame_config_pass io14_i (.O(io_o[14]), .I(io_i[14]), .T(io_oeb_i[14]));
    (* keep, BEL="X0Y8.A" *) IO_1_bidirectional_frame_config_pass io13_i (.O(io_o[13]), .I(io_i[13]), .T(io_oeb_i[13]));
    (* keep, BEL="X0Y8.B" *) IO_1_bidirectional_frame_config_pass io12_i (.O(io_o[12]), .I(io_i[12]), .T(io_oeb_i[12]));
    (* keep, BEL="X0Y9.A" *) IO_1_bidirectional_frame_config_pass io11_i (.O(io_o[11]), .I(io_i[11]), .T(io_oeb_i[11]));
    (* keep, BEL="X0Y9.B" *) IO_1_bidirectional_frame_config_pass io10_i (.O(io_o[10]), .I(io_i[10]), .T(io_oeb_i[10]));
    (* keep, BEL="X0Y10.A" *) IO_1_bidirectional_frame_config_pass io9_i (.O(io_o[9]), .I(io_i[9]), .T(io_oeb_i[9]));
    (* keep, BEL="X0Y10.B" *) IO_1_bidirectional_frame_config_pass io8_i (.O(io_o[8]), .I(io_i[8]), .T(io_oeb_i[8]));
    (* keep, BEL="X0Y11.A" *) IO_1_bidirectional_frame_config_pass io7_i (.O(io_o[7]), .I(io_i[7]), .T(io_oeb_i[7]));
    (* keep, BEL="X0Y11.B" *) IO_1_bidirectional_frame_config_pass io6_i (.O(io_o[6]), .I(io_i[6]), .T(io_oeb_i[6]));
    (* keep, BEL="X0Y12.A" *) IO_1_bidirectional_frame_config_pass io5_i (.O(io_o[5]), .I(io_i[5]), .T(io_oeb_i[5]));
    (* keep, BEL="X0Y12.B" *) IO_1_bidirectional_frame_config_pass io4_i (.O(io_o[4]), .I(io_i[4]), .T(io_oeb_i[4]));
    (* keep, BEL="X0Y13.A" *) IO_1_bidirectional_frame_config_pass io3_i (.O(io_o[3]), .I(io_i[3]), .T(io_oeb_i[3]));
    (* keep, BEL="X0Y13.B" *) IO_1_bidirectional_frame_config_pass io2_i (.O(io_o[2]), .I(io_i[2]), .T(io_oeb_i[2]));
    (* keep, BEL="X0Y14.A" *) IO_1_bidirectional_frame_config_pass io1_i (.O(io_o[1]), .I(io_i[1]), .T(io_oeb_i[1]));
    (* keep, BEL="X0Y14.B" *) IO_1_bidirectional_frame_config_pass io0_i (.O(io_o[0]), .I(io_i[0]), .T(io_oeb_i[0]));
endmodule
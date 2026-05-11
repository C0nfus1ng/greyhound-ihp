// 0x0B, 0x2B, 0x5B and 0x7B are free for custom use
typedef enum logic [6:0]
{
    INSTR1 = 7'h0B,
    INSTR2 = 7'h2B,
    INSTR3 = 7'h5B,
    INSTR4 = 7'h7B,
} OPCODE_XIF_BASE;

// TODO multi bitshift (XIF), bin to bcd/7seg (OBI), Wire crossings(IOs subslot?)
module static_slot();
    // CLK
    logic clk;
    (* keep *) Global_Clock clk_i (.CLK(clk));

    // RST
    logic rst;
    WARMBOOT_wrapper WARMBOOT_wrapper (
        .SLOT   (4'd0),
        .BOOT   (1'b0),
        .RESET  (rst)
    );

    // IOs
    logic [31:0] io_i, io_oeb, io_o;
    io_wrapper io (
        .io_i     (io_i),
        .io_oeb_i (io_oeb),
        .io_o     (io_o),
    );

    // Slots
    slot1_wrapper slot1 (
        .rst_i    (rst),
        .io_i     (io_i),
        .io_o     (io_o),
        .io_oeb_o (io_oeb),
    );

    slot2_wrapper slot2 (
        .rst_i    (rst),
    );

endmodule

module io_wrapper #(
    parameter NUM_IO = 32
) (
    input  logic [NUM_IO-1:0] io_i,
    input  logic [NUM_IO-1:0] io_oeb_i,
    output logic [NUM_IO-1:0] io_o,
);
    (* keep, BEL="X0Y1.A" *) IO_1_bidirectional_frame_config_pass io31_i (.O(io_i[31]), .I(io_o[31]), .T(io_oeb_i[31]));
    (* keep, BEL="X0Y1.B" *) IO_1_bidirectional_frame_config_pass io30_i (.O(io_i[30]), .I(io_o[30]), .T(io_oeb_i[30]));
    (* keep, BEL="X0Y2.A" *) IO_1_bidirectional_frame_config_pass io29_i (.O(io_i[29]), .I(io_o[29]), .T(io_oeb_i[29]));
    (* keep, BEL="X0Y2.B" *) IO_1_bidirectional_frame_config_pass io28_i (.O(io_i[28]), .I(io_o[28]), .T(io_oeb_i[28]));
    (* keep, BEL="X0Y3.A" *) IO_1_bidirectional_frame_config_pass io27_i (.O(io_i[27]), .I(io_o[27]), .T(io_oeb_i[27]));
    (* keep, BEL="X0Y3.B" *) IO_1_bidirectional_frame_config_pass io26_i (.O(io_i[26]), .I(io_o[26]), .T(io_oeb_i[26]));
    (* keep, BEL="X0Y4.A" *) IO_1_bidirectional_frame_config_pass io25_i (.O(io_i[25]), .I(io_o[25]), .T(io_oeb_i[25]));
    (* keep, BEL="X0Y4.B" *) IO_1_bidirectional_frame_config_pass io24_i (.O(io_i[24]), .I(io_o[24]), .T(io_oeb_i[24]));
    (* keep, BEL="X0Y5.A" *) IO_1_bidirectional_frame_config_pass io23_i (.O(io_i[23]), .I(io_o[23]), .T(io_oeb_i[23]));
    (* keep, BEL="X0Y5.B" *) IO_1_bidirectional_frame_config_pass io22_i (.O(io_i[22]), .I(io_o[22]), .T(io_oeb_i[22]));
    (* keep, BEL="X0Y6.A" *) IO_1_bidirectional_frame_config_pass io21_i (.O(io_i[21]), .I(io_o[21]), .T(io_oeb_i[21]));
    (* keep, BEL="X0Y6.B" *) IO_1_bidirectional_frame_config_pass io20_i (.O(io_i[20]), .I(io_o[20]), .T(io_oeb_i[20]));
    (* keep, BEL="X0Y7.A" *) IO_1_bidirectional_frame_config_pass io19_i (.O(io_i[19]), .I(io_o[19]), .T(io_oeb_i[19]));
    (* keep, BEL="X0Y7.B" *) IO_1_bidirectional_frame_config_pass io18_i (.O(io_i[18]), .I(io_o[18]), .T(io_oeb_i[18]));
    (* keep, BEL="X0Y8.A" *) IO_1_bidirectional_frame_config_pass io17_i (.O(io_i[17]), .I(io_o[17]), .T(io_oeb_i[17]));
    (* keep, BEL="X0Y8.B" *) IO_1_bidirectional_frame_config_pass io16_i (.O(io_i[16]), .I(io_o[16]), .T(io_oeb_i[16]));
    (* keep, BEL="X0Y9.A" *) IO_1_bidirectional_frame_config_pass io15_i (.O(io_i[15]), .I(io_o[15]), .T(io_oeb_i[15]));
    (* keep, BEL="X0Y9.B" *) IO_1_bidirectional_frame_config_pass io14_i (.O(io_i[14]), .I(io_o[14]), .T(io_oeb_i[14]));
    (* keep, BEL="X0Y10.A" *) IO_1_bidirectional_frame_config_pass io13_i (.O(io_i[13]), .I(io_o[13]), .T(io_oeb_i[13]));
    (* keep, BEL="X0Y10.B" *) IO_1_bidirectional_frame_config_pass io12_i (.O(io_i[12]), .I(io_o[12]), .T(io_oeb_i[12]));
    (* keep, BEL="X0Y11.A" *) IO_1_bidirectional_frame_config_pass io11_i (.O(io_i[11]), .I(io_o[11]), .T(io_oeb_i[11]));
    (* keep, BEL="X0Y11.B" *) IO_1_bidirectional_frame_config_pass io10_i (.O(io_i[10]), .I(io_o[10]), .T(io_oeb_i[10]));
    (* keep, BEL="X0Y12.A" *) IO_1_bidirectional_frame_config_pass io9_i (.O(io_i[9]), .I(io_o[9]), .T(io_oeb_i[9]));
    (* keep, BEL="X0Y12.B" *) IO_1_bidirectional_frame_config_pass io8_i (.O(io_i[8]), .I(io_o[8]), .T(io_oeb_i[8]));
    (* keep, BEL="X0Y13.A" *) IO_1_bidirectional_frame_config_pass io7_i (.O(io_i[7]), .I(io_o[7]), .T(io_oeb_i[7]));
    (* keep, BEL="X0Y13.B" *) IO_1_bidirectional_frame_config_pass io6_i (.O(io_i[6]), .I(io_o[6]), .T(io_oeb_i[6]));
    (* keep, BEL="X0Y14.A" *) IO_1_bidirectional_frame_config_pass io5_i (.O(io_i[5]), .I(io_o[5]), .T(io_oeb_i[5]));
    (* keep, BEL="X0Y14.B" *) IO_1_bidirectional_frame_config_pass io4_i (.O(io_i[4]), .I(io_o[4]), .T(io_oeb_i[4]));
    (* keep, BEL="X0Y15.A" *) IO_1_bidirectional_frame_config_pass io3_i (.O(io_i[3]), .I(io_o[3]), .T(io_oeb_i[3]));
    (* keep, BEL="X0Y15.B" *) IO_1_bidirectional_frame_config_pass io2_i (.O(io_i[2]), .I(io_o[2]), .T(io_oeb_i[2]));
    (* keep, BEL="X0Y16.A" *) IO_1_bidirectional_frame_config_pass io1_i (.O(io_i[1]), .I(io_o[1]), .T(io_oeb_i[1]));
    (* keep, BEL="X0Y16.B" *) IO_1_bidirectional_frame_config_pass io0_i (.O(io_i[0]), .I(io_o[0]), .T(io_oeb_i[0]));
endmodule

module slot1_wrapper (
    input  logic        rst_i,
    input  logic [31:0] io_i,
    output logic [31:0] io_o,
    output logic [31:0] io_oeb_o,
);
    (* keep, BEL="X4Y1.A" *) Static_slot_con_X4Y1 slot1_x4y1 (
        .E1END0(rst_i),
        .E2END4(io_i[31]),
        .E2END5(io_i[30]),
        .E2END6(io_i[29]),
        .E2END7(io_i[28]),

        .W1BEG0(io_oeb_o[31]),
        .W1BEG1(io_oeb_o[30]),
        .W1BEG2(io_oeb_o[29]),
        .W1BEG3(io_oeb_o[28]),
        .W2BEG0(io_o[31]),
        .W2BEG1(io_o[30]),
        .W2BEG2(io_o[29]),
        .W2BEG3(io_o[28]),
    );
    (* keep, BEL="X4Y2.A" *) Static_slot_con_X4Y2 slot1_x4y2 (
        .E2END0(io_i[27]),
        .E2END1(io_i[26]),
        .E2END2(io_i[25]),
        .E2END3(io_i[24]),

        .W1BEG0(io_o[27]),
        .W1BEG1(io_o[26]),
        .W1BEG2(io_o[25]),
        .W1BEG3(io_o[24]),
        .W2BEG0(io_oeb_o[27]),
        .W2BEG1(io_oeb_o[26]),
        .W2BEG2(io_oeb_o[25]),
        .W2BEG3(io_oeb_o[24]),
    );
    (* keep, BEL="X4Y3.A" *) Static_slot_con_X4Y3 slot1_x4y3 (
        .E2END4(io_i[23]),
        .E2END5(io_i[22]),
        .E2END6(io_i[21]),
        .E2END7(io_i[20]),

        .W1BEG0(io_oeb_o[23]),
        .W1BEG1(io_oeb_o[22]),
        .W1BEG2(io_oeb_o[21]),
        .W1BEG3(io_oeb_o[20]),
        .W2BEG0(io_o[23]),
        .W2BEG1(io_o[22]),
        .W2BEG2(io_o[21]),
        .W2BEG3(io_o[20]),
    );
    (* keep, BEL="X4Y4.A" *) Static_slot_con_X4Y4 slot1_x4y4 (
        .E2END0(io_i[19]),
        .E2END1(io_i[18]),
        .E2END2(io_i[17]),
        .E2END3(io_i[16]),

        .W1BEG0(io_o[19]),
        .W1BEG1(io_o[18]),
        .W1BEG2(io_o[17]),
        .W1BEG3(io_o[16]),
        .W2BEG0(io_oeb_o[19]),
        .W2BEG1(io_oeb_o[18]),
        .W2BEG2(io_oeb_o[17]),
        .W2BEG3(io_oeb_o[16]),
    );
    (* keep, BEL="X4Y5.A" *) Static_slot_con_X4Y5 slot1_x4y5 (
        .E2END4(io_i[15]),
        .E2END5(io_i[14]),
        .E2END6(io_i[13]),
        .E2END7(io_i[12]),

        .W1BEG0(io_oeb_o[15]),
        .W1BEG1(io_oeb_o[14]),
        .W1BEG2(io_oeb_o[13]),
        .W1BEG3(io_oeb_o[12]),
        .W2BEG0(io_o[15]),
        .W2BEG1(io_o[14]),
        .W2BEG2(io_o[13]),
        .W2BEG3(io_o[12]),
    );
    (* keep, BEL="X4Y6.A" *) Static_slot_con_X4Y6 slot1_x4y6 (
        .E2END0(io_i[11]),
        .E2END1(io_i[10]),
        .E2END2(io_i[9]),
        .E2END3(io_i[8]),

        .W1BEG0(io_o[11]),
        .W1BEG1(io_o[10]),
        .W1BEG2(io_o[9]),
        .W1BEG3(io_o[8]),
        .W2BEG0(io_oeb_o[11]),
        .W2BEG1(io_oeb_o[10]),
        .W2BEG2(io_oeb_o[9]),
        .W2BEG3(io_oeb_o[8]),
    );
    (* keep, BEL="X4Y7.A" *) Static_slot_con_X4Y7 slot1_x4y7 (
        .E2END4(io_i[7]),
        .E2END5(io_i[6]),
        .E2END6(io_i[5]),
        .E2END7(io_i[4]),

        .W1BEG0(io_oeb_o[7]),
        .W1BEG1(io_oeb_o[6]),
        .W1BEG2(io_oeb_o[5]),
        .W1BEG3(io_oeb_o[4]),
        .W2BEG0(io_o[7]),
        .W2BEG1(io_o[6]),
        .W2BEG2(io_o[5]),
        .W2BEG3(io_o[4]),
    );
    (* keep, BEL="X4Y8.A" *) Static_slot_con_X4Y8 slot1_x4y8 (
        .E2END0(io_i[3]),
        .E2END1(io_i[2]),
        .E2END2(io_i[1]),
        .E2END3(io_i[0]),

        .W1BEG0(io_o[3]),
        .W1BEG1(io_o[2]),
        .W1BEG2(io_o[1]),
        .W1BEG3(io_o[0]),
        .W2BEG0(io_oeb_o[3]),
        .W2BEG1(io_oeb_o[2]),
        .W2BEG2(io_oeb_o[1]),
        .W2BEG3(io_oeb_o[0]),
    );
endmodule

module slot2_wrapper (
    input logic rst_i,
);
    (* keep, BEL="X8Y1.A" *) Static_slot_con_X8Y1 slot2_x8y1 (
        .E1END0(rst_i),
    );
endmodule

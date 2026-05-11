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

    // Slots
    logic [31:0] slot_io_i, slot_io_oeb, slot_io_o;
    slot1_wrapper slot1 (
        .rst_i    (rst),
        .io_i     (slot_io_i),
        .io_o     (slot_io_o),
        .io_oeb_o (slot_io_oeb),
    );
    
    slot2_wrapper slot2 (
        .rst_i    (rst),
    );

    slot3_wrapper slot3 (
        .rst_i          (rst),
        .slot_io_o      (slot_io_i),
        .slot_io_i      (slot_io_o),
        .slot_io_oeb_i  (slot_io_oeb),
    );

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

module slot3_wrapper (
    input  logic        rst_i,
    output logic [31:0] slot_io_o,
    input  logic [31:0] slot_io_i,
    input  logic [31:0] slot_io_oeb_i,
);
    (* keep, BEL="X2Y1.A" *) Static_slot_con_X2Y1 slot3_x2y1 (
        .E2BEG4(slot_io_o[31]),
        .E2BEG5(slot_io_o[30]),
        .E2BEG6(slot_io_o[29]),
        .E2BEG7(slot_io_o[28]),

        .W1END0(slot_io_oeb_i[31]),
        .W1END1(slot_io_oeb_i[30]),
        .W1END2(slot_io_oeb_i[29]),
        .W1END3(slot_io_oeb_i[28]),
        .W2END0(slot_io_i[31]),
        .W2END1(slot_io_i[30]),
        .W2END2(slot_io_i[29]),
        .W2END3(slot_io_i[28]),
    );
    (* keep, BEL="X2Y2.A" *) Static_slot_con_X2Y2 slot3_x2y2 (
        .E2BEG0(slot_io_o[27]),
        .E2BEG1(slot_io_o[26]),
        .E2BEG2(slot_io_o[25]),
        .E2BEG3(slot_io_o[24]),

        .W1END0(slot_io_i[27]),
        .W1END1(slot_io_i[26]),
        .W1END2(slot_io_i[25]),
        .W1END3(slot_io_i[24]),
        .W2END0(slot_io_oeb_i[27]),
        .W2END1(slot_io_oeb_i[26]),
        .W2END2(slot_io_oeb_i[25]),
        .W2END3(slot_io_oeb_i[24]),
    );
    (* keep, BEL="X2Y3.A" *) Static_slot_con_X2Y3 slot3_x2y3 (
        .E2BEG4(slot_io_o[23]),
        .E2BEG5(slot_io_o[22]),
        .E2BEG6(slot_io_o[21]),
        .E2BEG7(slot_io_o[20]),

        .W1END0(slot_io_oeb_i[23]),
        .W1END1(slot_io_oeb_i[22]),
        .W1END2(slot_io_oeb_i[21]),
        .W1END3(slot_io_oeb_i[20]),
        .W2END0(slot_io_i[23]),
        .W2END1(slot_io_i[22]),
        .W2END2(slot_io_i[21]),
        .W2END3(slot_io_i[20]),
    );
    (* keep, BEL="X2Y4.A" *) Static_slot_con_X2Y4 slot3_x2y4 (
        .E2BEG4(slot_io_o[19]),
        .E2BEG5(slot_io_o[18]),
        .E2BEG6(slot_io_o[17]),
        .E2BEG7(slot_io_o[16]),

        .W1END0(slot_io_i[19]),
        .W1END1(slot_io_i[18]),
        .W1END2(slot_io_i[17]),
        .W1END3(slot_io_i[16]),
        .W2END0(slot_io_oeb_i[19]),
        .W2END1(slot_io_oeb_i[18]),
        .W2END2(slot_io_oeb_i[17]),
        .W2END3(slot_io_oeb_i[16]),
    );
    (* keep, BEL="X2Y5.A" *) Static_slot_con_X2Y5 slot3_x2y5 (
        .E2BEG4(slot_io_o[15]),
        .E2BEG5(slot_io_o[14]),
        .E2BEG6(slot_io_o[13]),
        .E2BEG7(slot_io_o[12]),

        .W1END0(slot_io_oeb_i[15]),
        .W1END1(slot_io_oeb_i[14]),
        .W1END2(slot_io_oeb_i[13]),
        .W1END3(slot_io_oeb_i[12]),
        .W2END0(slot_io_i[15]),
        .W2END1(slot_io_i[14]),
        .W2END2(slot_io_i[13]),
        .W2END3(slot_io_i[12]),
    );
    (* keep, BEL="X2Y6.A" *) Static_slot_con_X2Y6 slot3_x2y6 (
        .E2BEG0(slot_io_o[11]),
        .E2BEG1(slot_io_o[10]),
        .E2BEG2(slot_io_o[9]),
        .E2BEG3(slot_io_o[8]),

        .W1END0(slot_io_i[11]),
        .W1END1(slot_io_i[10]),
        .W1END2(slot_io_i[9]),
        .W1END3(slot_io_i[8]),
        .W2END0(slot_io_oeb_i[11]),
        .W2END1(slot_io_oeb_i[10]),
        .W2END2(slot_io_oeb_i[9]),
        .W2END3(slot_io_oeb_i[8]),
    );
    (* keep, BEL="X2Y7.A" *) Static_slot_con_X2Y7 slot3_x2y7 (
        .E2BEG4(slot_io_o[7]),
        .E2BEG5(slot_io_o[6]),
        .E2BEG6(slot_io_o[5]),
        .E2BEG7(slot_io_o[4]),

        .W1END0(slot_io_oeb_i[7]),
        .W1END1(slot_io_oeb_i[6]),
        .W1END2(slot_io_oeb_i[5]),
        .W1END3(slot_io_oeb_i[4]),
        .W2END0(slot_io_i[7]),
        .W2END1(slot_io_i[6]),
        .W2END2(slot_io_i[5]),
        .W2END3(slot_io_i[4]),
    );
    (* keep, BEL="X2Y8.A" *) Static_slot_con_X2Y8 slot3_x2y8 (
        .E2BEG0(slot_io_o[3]),
        .E2BEG1(slot_io_o[2]),
        .E2BEG2(slot_io_o[1]),
        .E2BEG3(slot_io_o[0]),

        .W1END0(slot_io_i[3]),
        .W1END1(slot_io_i[2]),
        .W1END2(slot_io_i[1]),
        .W1END3(slot_io_i[0]),
        .W2END0(slot_io_oeb_i[3]),
        .W2END1(slot_io_oeb_i[2]),
        .W2END2(slot_io_oeb_i[1]),
        .W2END3(slot_io_oeb_i[0]),

        .S1END0(rst_i),
    );
endmodule
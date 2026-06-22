// 0x0B, 0x2B, 0x5B and 0x7B are free for custom use
typedef enum logic [6:0]
{
    INSTR1 = 7'h0B,
    INSTR2 = 7'h2B,
    INSTR3 = 7'h5B,
    INSTR4 = 7'h7B,
} OPCODE_XIF_BASE;

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
    logic [31:0] slot_io_i, slot_io_o;
    slot1_wrapper slot1 (
        .rst_i    (rst),
        .io_i     (slot_io_i),
        .io_o     (slot_io_o),
    );
    
    slot2_wrapper slot2 (
        .rst_i    (rst),
    );

    slot3_wrapper slot3 (
        .rst_i          (rst),
        .slot_io_o      (slot_io_i),
        .slot_io_i      (slot_io_o),
    );

endmodule

module slot1_wrapper (
    input  logic        rst_i,
    input  logic [31:0] io_i,
    output logic [31:0] io_o,
);
    (* keep, BEL="X4Y1.A" *) Static_slot_con_X4Y1 slot1_x4y1 (
        .E1END0(io_i[31]),
        .E1END1(io_i[30]),
        .E1END2(io_i[29]),
        .E1END3(io_i[28]),

        .W1BEG0(io_o[31]),
        .W1BEG1(io_o[30]),
        .W1BEG2(io_o[29]),
        .W1BEG3(io_o[28]),
    );
    (* keep, BEL="X4Y2.A" *) Static_slot_con_X4Y2 slot1_x4y2 (
        .E1END0(io_i[27]),
        .E1END1(io_i[26]),
        .E1END2(io_i[25]),
        .E1END3(io_i[24]),

        .W1BEG0(io_o[27]),
        .W1BEG1(io_o[26]),
        .W1BEG2(io_o[25]),
        .W1BEG3(io_o[24]),
    );
    (* keep, BEL="X4Y3.A" *) Static_slot_con_X4Y3 slot1_x4y3 (
        .E1END0(io_i[23]),
        .E1END1(io_i[22]),
        .E1END2(io_i[21]),
        .E1END3(io_i[20]),

        .W1BEG0(io_o[23]),
        .W1BEG1(io_o[22]),
        .W1BEG2(io_o[21]),
        .W1BEG3(io_o[20]),
    );
    (* keep, BEL="X4Y4.A" *) Static_slot_con_X4Y4 slot1_x4y4 (
        .E1END0(io_i[19]),
        .E1END1(io_i[18]),
        .E1END2(io_i[17]),
        .E1END3(io_i[16]),

        .W1BEG0(io_o[19]),
        .W1BEG1(io_o[18]),
        .W1BEG2(io_o[17]),
        .W1BEG3(io_o[16]),
    );
    (* keep, BEL="X4Y5.A" *) Static_slot_con_X4Y5 slot1_x4y5 (
        .E1END0(io_i[15]),
        .E1END1(io_i[14]),
        .E1END2(io_i[13]),
        .E1END3(io_i[12]),

        .W1BEG0(io_o[15]),
        .W1BEG1(io_o[14]),
        .W1BEG2(io_o[13]),
        .W1BEG3(io_o[12]),
    );
    (* keep, BEL="X4Y6.A" *) Static_slot_con_X4Y6 slot1_x4y6 (
        .E1END0(io_i[11]),
        .E1END1(io_i[10]),
        .E1END2(io_i[9]),
        .E1END3(io_i[8]),

        .W1BEG0(io_o[11]),
        .W1BEG1(io_o[10]),
        .W1BEG2(io_o[9]),
        .W1BEG3(io_o[8]),
    );
    (* keep, BEL="X4Y7.A" *) Static_slot_con_X4Y7 slot1_x4y7 (
        .E1END0(io_i[7]),
        .E1END1(io_i[6]),
        .E1END2(io_i[5]),
        .E1END3(io_i[4]),

        .W1BEG0(io_o[7]),
        .W1BEG1(io_o[6]),
        .W1BEG2(io_o[5]),
        .W1BEG3(io_o[4]),
    );
    (* keep, BEL="X4Y8.A" *) Static_slot_con_X4Y8 slot1_x4y8 (
        .E1END0(io_i[3]),
        .E1END1(io_i[2]),
        .E1END2(io_i[1]),
        .E1END3(io_i[0]),

        .W1BEG0(io_o[3]),
        .W1BEG1(io_o[2]),
        .W1BEG2(io_o[1]),
        .W1BEG3(io_o[0]),
        .S1END0(rst_i),
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
);
    (* keep, BEL="X2Y1.A" *) Static_slot_con_X2Y1 slot3_x2y1 (
        .E1BEG0(slot_io_o[31]),
        .E1BEG1(slot_io_o[30]),
        .E1BEG2(slot_io_o[29]),
        .E1BEG3(slot_io_o[28]),

        .W1END0(slot_io_i[31]),
        .W1END1(slot_io_i[30]),
        .W1END2(slot_io_i[29]),
        .W1END3(slot_io_i[28]),
    );
    (* keep, BEL="X2Y2.A" *) Static_slot_con_X2Y2 slot3_x2y2 (
        .E1BEG0(slot_io_o[27]),
        .E1BEG1(slot_io_o[26]),
        .E1BEG2(slot_io_o[25]),
        .E1BEG3(slot_io_o[24]),

        .W1END0(slot_io_i[27]),
        .W1END1(slot_io_i[26]),
        .W1END2(slot_io_i[25]),
        .W1END3(slot_io_i[24]),
    );
    (* keep, BEL="X2Y3.A" *) Static_slot_con_X2Y3 slot3_x2y3 (
        .E1BEG0(slot_io_o[23]),
        .E1BEG1(slot_io_o[22]),
        .E1BEG2(slot_io_o[21]),
        .E1BEG3(slot_io_o[20]),

        .W1END0(slot_io_i[23]),
        .W1END1(slot_io_i[22]),
        .W1END2(slot_io_i[21]),
        .W1END3(slot_io_i[20]),
    );
    (* keep, BEL="X2Y4.A" *) Static_slot_con_X2Y4 slot3_x2y4 (
        .E1BEG0(slot_io_o[19]),
        .E1BEG1(slot_io_o[18]),
        .E1BEG2(slot_io_o[17]),
        .E1BEG3(slot_io_o[16]),

        .W1END0(slot_io_i[19]),
        .W1END1(slot_io_i[18]),
        .W1END2(slot_io_i[17]),
        .W1END3(slot_io_i[16]),
    );
    (* keep, BEL="X2Y5.A" *) Static_slot_con_X2Y5 slot3_x2y5 (
        .E1BEG0(slot_io_o[15]),
        .E1BEG1(slot_io_o[14]),
        .E1BEG2(slot_io_o[13]),
        .E1BEG3(slot_io_o[12]),

        .W1END0(slot_io_i[15]),
        .W1END1(slot_io_i[14]),
        .W1END2(slot_io_i[13]),
        .W1END3(slot_io_i[12]),
    );
    (* keep, BEL="X2Y6.A" *) Static_slot_con_X2Y6 slot3_x2y6 (
        .E1BEG0(slot_io_o[11]),
        .E1BEG1(slot_io_o[10]),
        .E1BEG2(slot_io_o[9]),
        .E1BEG3(slot_io_o[8]),

        .W1END0(slot_io_i[11]),
        .W1END1(slot_io_i[10]),
        .W1END2(slot_io_i[9]),
        .W1END3(slot_io_i[8]),
    );
    (* keep, BEL="X2Y7.A" *) Static_slot_con_X2Y7 slot3_x2y7 (
        .E1BEG0(slot_io_o[7]),
        .E1BEG1(slot_io_o[6]),
        .E1BEG2(slot_io_o[5]),
        .E1BEG3(slot_io_o[4]),

        .W1END0(slot_io_i[7]),
        .W1END1(slot_io_i[6]),
        .W1END2(slot_io_i[5]),
        .W1END3(slot_io_i[4]),
    );
    (* keep, BEL="X2Y8.A" *) Static_slot_con_X2Y8 slot3_x2y8 (
        .E1BEG0(slot_io_o[3]),
        .E1BEG1(slot_io_o[2]),
        .E1BEG2(slot_io_o[1]),
        .E1BEG3(slot_io_o[0]),

        .W1END0(slot_io_i[3]),
        .W1END1(slot_io_i[2]),
        .W1END2(slot_io_i[1]),
        .W1END3(slot_io_i[0]),
        .S1END0(rst_i),
    );
endmodule
// 0x0B, 0x2B, 0x5B and 0x7B are free for custom use
typedef enum logic [6:0]
{
    INSTR1 = 7'h0B,
    INSTR2 = 7'h2B,
    INSTR3 = 7'h5B,
    INSTR4 = 7'h7B,
} OPCODE_XIF_BASE;

// TODO multi bitshift, bin to bcd/7seg
module static_slot();
    // CLK
    logic clk;
    (* keep *) Global_Clock clk_i (.CLK(clk));

    // Slot BEL placement
    logic [31:0] slot1_result, slot2_result;
    logic [2:0] slot1_opcode, slot2_opcode;

    slot1_wrapper slot1 (
        .op0_i      (issue_op0_i),
        .op1_i      (issue_op1_i),
        .result_o   (slot1_result),
        .opcode_o   (slot1_opcode),
    );

    slot2_wrapper slot2 (
        .op0_i      (issue_op0_i),
        .op1_i      (issue_op1_i),
        .result_o   (slot2_result),
        .opcode_o   (slot2_opcode),
    );

    // Slot selecting
    logic [6:0]  opcode;
    logic [4:0]  rd;
    logic        issue_valid_q, select_slot1, select_slot2;

    assign opcode = issue_instr_i[6:0];
    assign rd     = issue_instr_i[11:7];

    assign select_slot1 = opcode == {slot1_opcode, 4'hB};
    assign select_slot2 = opcode == {slot2_opcode, 4'hB};

    assign issue_accept_o = issue_valid_i && (select_slot1 || select_slot2);
    assign issue_ready_o  = 1'b1;

    always_comb begin : OutputStage
        result_rd_o    = rd;
        result_valid_o = issue_valid_q;
        result_id_o    = issue_id_i;
    end

    always_comb begin : SlotSelector
        result_o       = '0;

        if (opcode == {3'b0, slot1_opcode}) begin
            result_o = slot1_result;
        end

        if (opcode == {3'b0, slot2_opcode}) begin
            result_o = slot2_result;
        end
    end 

    always_ff @(posedge clk) begin : ValidBuffer
        issue_valid_q <= issue_valid_i;
    end
endmodule

module slot1_wrapper (
    input  logic [31:0] op0_i,
    input  logic [31:0] op1_i,
    output logic [31:0] result_o,
    output logic [2:0]  opcode_o,
);
    (* keep, BEL="X5Y1.A" *) Static_slot_con_X5Y1 slot1_x5y1 (
        .E2END0(op0_i[0]),
        .E2END1(op0_i[1]),
        .E2END2(op0_i[2]),
        .E2END3(op0_i[3]),

        .E2BEG0(result_o[0]),
        .E2BEG1(result_o[1]),
    );
    (* keep, BEL="X6Y1.A" *) Static_slot_con_X6Y1 slot1_x6y1 (
        .E2END4(op1_i[0]),
        .E2END5(op1_i[1]),
        .E2END6(op1_i[2]),
        .E2END7(op1_i[3]),

        .E2BEG2(result_o[2]),
        .E2BEG3(result_o[3]),,
    );
    (* keep, BEL="X5Y2.A" *) Static_slot_con_X5Y2 slot1_x5y2 (
        .E2END4(op0_i[4]),
        .E2END5(op0_i[5]),
        .E2END6(op0_i[6]),
        .E2END7(op0_i[7]),

        .E2BEG4(result_o[4]),
        .E2BEG5(result_o[5]),
    );
    (* keep, BEL="X6Y2.A" *) Static_slot_con_X6Y2 slot1_x6y2 (
        .E2END0(op1_i[4]),
        .E2END1(op1_i[5]),
        .E2END2(op1_i[6]),
        .E2END3(op1_i[7]),

        .E2BEG6(result_o[6]),
        .E2BEG7(result_o[7]),
    );
    (* keep, BEL="X5Y3.A" *) Static_slot_con_X5Y3 slot1_x5y3 (
        .E2END0(op0_i[8]),
        .E2END1(op0_i[9]),
        .E2END2(op0_i[10]),
        .E2END3(op0_i[11]),

        .E2BEG0(result_o[8]),
        .E2BEG1(result_o[9]),
    );
    (* keep, BEL="X6Y3.A" *) Static_slot_con_X6Y3 slot1_x6y3 (
        .E2END4(op1_i[8]),
        .E2END5(op1_i[9]),
        .E2END6(op1_i[10]),
        .E2END7(op1_i[11]),

        .E2BEG2(result_o[10]),
        .E2BEG3(result_o[11]),
    );
    (* keep, BEL="X5Y4.A" *) Static_slot_con_X5Y4 slot1_x5y4 (
        .E2END4(op0_i[12]),
        .E2END5(op0_i[13]),
        .E2END6(op0_i[14]),
        .E2END7(op0_i[15]),

        .E2BEG4(result_o[12]),
        .E2BEG5(result_o[13]),
    );
    (* keep, BEL="X6Y4.A" *) Static_slot_con_X6Y4 slot1_x6y4 (
        .E2END0(op1_i[12]),
        .E2END1(op1_i[13]),
        .E2END2(op1_i[14]),
        .E2END3(op1_i[15]),

        .E2BEG6(result_o[14]),
        .E2BEG7(result_o[15]),
    );
    (* keep, BEL="X5Y5.A" *) Static_slot_con_X5Y5 slot1_x5y5 (
        .E2END0(op0_i[16]),
        .E2END1(op0_i[17]),
        .E2END2(op0_i[18]),
        .E2END3(op0_i[19]),

        .E2BEG0(result_o[16]),
        .E2BEG1(result_o[17]),
    );
    (* keep, BEL="X6Y5.A" *) Static_slot_con_X6Y5 slot1_x6y5 (
        .E2END4(op1_i[16]),
        .E2END5(op1_i[17]),
        .E2END6(op1_i[18]),
        .E2END7(op1_i[19]),

        .E2BEG2(result_o[18]),
        .E2BEG3(result_o[19]),
    );
    (* keep, BEL="X5Y6.A" *) Static_slot_con_X5Y6 slot1_x5y6 (
        .E2END4(op0_i[20]),
        .E2END5(op0_i[21]),
        .E2END6(op0_i[22]),
        .E2END7(op0_i[23]),

        .E2BEG4(result_o[20]),
        .E2BEG5(result_o[21]),
    );
    (* keep, BEL="X6Y6.A" *) Static_slot_con_X6Y6 slot1_x6y6 (
        .E2END0(op1_i[20]),
        .E2END1(op1_i[21]),
        .E2END2(op1_i[22]),
        .E2END3(op1_i[23]),

        .E2BEG6(result_o[22]),
        .E2BEG7(result_o[23]),
    );
    (* keep, BEL="X5Y7.A" *) Static_slot_con_X5Y7 slot1_x5y7 (
        .E2END0(op0_i[24]),
        .E2END1(op0_i[25]),
        .E2END2(op0_i[26]),
        .E2END3(op0_i[27]),

        .E2BEG0(result_o[24]),
        .E2BEG1(result_o[25]),
    );
    (* keep, BEL="X6Y7.A" *) Static_slot_con_X6Y7 slot1_x6y7 (
        .E2END4(op1_i[24]),
        .E2END5(op1_i[25]),
        .E2END6(op1_i[26]),
        .E2END7(op1_i[27]),

        .E2BEG2(result_o[26]),
        .E2BEG3(result_o[27]),
    );
    (* keep, BEL="X5Y8.A" *) Static_slot_con_X5Y8 slot1_x5y8 (
        .E2END4(op0_i[28]),
        .E2END5(op0_i[29]),
        .E2END6(op0_i[30]),
        .E2END7(op0_i[31]),

        .E2BEG4(result_o[28]),
        .E2BEG5(result_o[29]),
        .E2BEG6(opcode_o[0]),
        .E2BEG7(opcode_o[1]),
    );
    (* keep, BEL="X6Y8.A" *) Static_slot_con_X6Y8 slot1_x6y8 (
        .E2END0(op1_i[28]),
        .E2END1(op1_i[29]),
        .E2END2(op1_i[30]),
        .E2END3(op1_i[31]),

        .E2BEG0(result_o[30]),
        .E2BEG1(result_o[31]),
        .E2BEG2(opcode_o[2]),
    );
endmodule

module slot2_wrapper (
    input  logic [31:0] op0_i,
    input  logic [31:0] op1_i,
    output logic [31:0] result_o,
    output logic [2:0]  opcode_o,
);
    (* keep, BEL="X1Y1.A" *) Static_slot_con_X1Y1 slot1_x1y1 (
        .E2END0(op0_i[0]),
        .E2END1(op0_i[1]),
        .E2END2(op0_i[2]),
        .E2END3(op0_i[3]),

        .E2BEG0(result_o[0]),
        .E2BEG1(result_o[1]),
    );
    (* keep, BEL="X2Y1.A" *) Static_slot_con_X2Y1 slot1_x2y1 (
        .E2END4(op1_i[0]),
        .E2END5(op1_i[1]),
        .E2END6(op1_i[2]),
        .E2END7(op1_i[3]),

        .E2BEG2(result_o[2]),
        .E2BEG3(result_o[3]),,
    );
    (* keep, BEL="X1Y2.A" *) Static_slot_con_X1Y2 slot1_x1y2 (
        .E2END4(op0_i[4]),
        .E2END5(op0_i[5]),
        .E2END6(op0_i[6]),
        .E2END7(op0_i[7]),

        .E2BEG4(result_o[4]),
        .E2BEG5(result_o[5]),
    );
    (* keep, BEL="X2Y2.A" *) Static_slot_con_X2Y2 slot1_x2y2 (
        .E2END0(op1_i[4]),
        .E2END1(op1_i[5]),
        .E2END2(op1_i[6]),
        .E2END3(op1_i[7]),

        .E2BEG6(result_o[6]),
        .E2BEG7(result_o[7]),
    );
    (* keep, BEL="X1Y3.A" *) Static_slot_con_X1Y3 slot1_x1y3 (
        .E2END0(op0_i[8]),
        .E2END1(op0_i[9]),
        .E2END2(op0_i[10]),
        .E2END3(op0_i[11]),

        .E2BEG0(result_o[8]),
        .E2BEG1(result_o[9]),
    );
    (* keep, BEL="X2Y3.A" *) Static_slot_con_X2Y3 slot1_x2y3 (
        .E2END4(op1_i[8]),
        .E2END5(op1_i[9]),
        .E2END6(op1_i[10]),
        .E2END7(op1_i[11]),

        .E2BEG2(result_o[10]),
        .E2BEG3(result_o[11]),
    );
    (* keep, BEL="X1Y4.A" *) Static_slot_con_X1Y4 slot1_x1y4 (
        .E2END4(op0_i[12]),
        .E2END5(op0_i[13]),
        .E2END6(op0_i[14]),
        .E2END7(op0_i[15]),

        .E2BEG4(result_o[12]),
        .E2BEG5(result_o[13]),
    );
    (* keep, BEL="X2Y4.A" *) Static_slot_con_X2Y4 slot1_x2y4 (
        .E2END0(op1_i[12]),
        .E2END1(op1_i[13]),
        .E2END2(op1_i[14]),
        .E2END3(op1_i[15]),

        .E2BEG6(result_o[14]),
        .E2BEG7(result_o[15]),
    );
    (* keep, BEL="X1Y5.A" *) Static_slot_con_X1Y5 slot1_x1y5 (
        .E2END0(op0_i[16]),
        .E2END1(op0_i[17]),
        .E2END2(op0_i[18]),
        .E2END3(op0_i[19]),

        .E2BEG0(result_o[16]),
        .E2BEG1(result_o[17]),
    );
    (* keep, BEL="X2Y5.A" *) Static_slot_con_X2Y5 slot1_x2y5 (
        .E2END4(op1_i[16]),
        .E2END5(op1_i[17]),
        .E2END6(op1_i[18]),
        .E2END7(op1_i[19]),

        .E2BEG2(result_o[18]),
        .E2BEG3(result_o[19]),
    );
    (* keep, BEL="X1Y6.A" *) Static_slot_con_X1Y6 slot1_x1y6 (
        .E2END4(op0_i[20]),
        .E2END5(op0_i[21]),
        .E2END6(op0_i[22]),
        .E2END7(op0_i[23]),

        .E2BEG4(result_o[20]),
        .E2BEG5(result_o[21]),
    );
    (* keep, BEL="X2Y6.A" *) Static_slot_con_X2Y6 slot1_x2y6 (
        .E2END0(op1_i[20]),
        .E2END1(op1_i[21]),
        .E2END2(op1_i[22]),
        .E2END3(op1_i[23]),

        .E2BEG6(result_o[22]),
        .E2BEG7(result_o[23]),
    );
    (* keep, BEL="X1Y7.A" *) Static_slot_con_X1Y7 slot1_x1y7 (
        .E2END0(op0_i[24]),
        .E2END1(op0_i[25]),
        .E2END2(op0_i[26]),
        .E2END3(op0_i[27]),

        .E2BEG0(result_o[24]),
        .E2BEG1(result_o[25]),
    );
    (* keep, BEL="X2Y7.A" *) Static_slot_con_X2Y7 slot1_x2y7 (
        .E2END4(op1_i[24]),
        .E2END5(op1_i[25]),
        .E2END6(op1_i[26]),
        .E2END7(op1_i[27]),

        .E2BEG2(result_o[26]),
        .E2BEG3(result_o[27]),
    );
    (* keep, BEL="X1Y8.A" *) Static_slot_con_X1Y8 slot1_x1y8 (
        .E2END4(op0_i[28]),
        .E2END5(op0_i[29]),
        .E2END6(op0_i[30]),
        .E2END7(op0_i[31]),

        .E2BEG4(result_o[28]),
        .E2BEG5(result_o[29]),
        .E2BEG6(opcode_o[0]),
        .E2BEG7(opcode_o[1]),
    );
    (* keep, BEL="X2Y8.A" *) Static_slot_con_X2Y8 slot1_x2y8 (
        .E2END0(op1_i[28]),
        .E2END1(op1_i[29]),
        .E2END2(op1_i[30]),
        .E2END3(op1_i[31]),

        .E2BEG0(result_o[30]),
        .E2BEG1(result_o[31]),
        .E2BEG2(opcode_o[2]),
    );
endmodule

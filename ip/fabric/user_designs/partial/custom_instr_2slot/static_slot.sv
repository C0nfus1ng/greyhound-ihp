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

    logic        issue_ready_o;
    logic        issue_accept_o;
    logic        issue_valid_i;
    logic [31:0] issue_instr_i;
    logic [31:0] issue_op0_i;
    logic [31:0] issue_op1_i;
    logic [ 3:0] issue_id_i;
    
    logic        result_valid_o;
    logic [ 3:0] result_id_o;
    logic [ 4:0] result_rd_o;
    logic [31:0] result_o;

    CUSTOM_INSTRUCTION_wrapper xif (
        .ISSUE_READY    (issue_ready_o),
        .ISSUE_ACCEPT   (issue_accept_o),
        .ISSUE_VALID    (issue_valid_i),
        .ISSUE_INSTR    (issue_instr_i),
        .ISSUE_OPA      (issue_op0_i),
        .ISSUE_OPB      (issue_op1_i),
        .ISSUE_ID       (issue_id_i),
        
        .RESULT_VALID   (result_valid_o),
        .RESULT_ID      (result_id_o),
        .RESULT_RD      (result_rd_o),
        .RESULT         (result_o),
    );

    // Slot BEL placement
    logic [15:0] slot1_result, slot2_result;

    slot1_wrapper slot1 (
        .op0_i      (issue_op0_i[15:0]),
        .op1_i      (issue_op1_i[15:0]),
        .result_o   (slot1_result),
    );

    slot2_wrapper slot2 (
        .op0_i      (issue_op0_i[31:16]),
        .op1_i      (issue_op1_i[31:16]),
        .result_o   (slot2_result),
    );

    // Slot selecting
    logic [6:0]  opcode;
    logic [4:0]  rd;
    logic        issue_valid_q;

    assign opcode = issue_instr_i[6:0];
    assign rd     = issue_instr_i[11:7];

    assign issue_accept_o = issue_valid_i && (opcode == INSTR1);
    assign issue_ready_o  = 1'b1;

    always_comb begin : OutputStage
        result_rd_o    = rd;
        result_valid_o = issue_valid_q;
        result_id_o    = issue_id_i;
        result_o       = {slot2_result, slot1_result};
    end

    always_ff @(posedge clk) begin : ValidBuffer
        issue_valid_q <= issue_valid_i;
    end
endmodule

module slot1_wrapper (
    input  logic [15:0] op0_i,
    input  logic [15:0] op1_i,
    output logic [15:0] result_o,
);
    (* keep, BEL="X6Y1.A" *) Static_slot_con_X6Y1 slot1_x6y1 (
        .W2END0(op1_i[15]),
        .W2END1(op1_i[14]),
        .W2END2(op1_i[13]),
        .W2END3(op1_i[12]),
        .W2END4(op1_i[11]),
        .W2END5(op1_i[10]),
        .W2END6(op1_i[9]),
        .W2END7(op1_i[8]),
    );
    (* keep, BEL="X6Y2.A" *) Static_slot_con_X6Y2 slot1_x6y2 (
        .W2END0(op1_i[7]),
        .W2END1(op1_i[6]),
        .W2END2(op1_i[5]),
        .W2END3(op1_i[4]),
        .W2END4(op1_i[3]),
        .W2END5(op1_i[2]),
        .W2END6(op1_i[1]),
        .W2END7(op1_i[0]),
    );
    (* keep, BEL="X6Y5.A" *) Static_slot_con_X6Y5 slot1_x6y5 (
        .E2BEG0(result_o[15]),
        .E2BEG1(result_o[14]),
        .E2BEG2(result_o[13]),
        .E2BEG3(result_o[12]),
        .E2BEG4(result_o[11]),
        .E2BEG5(result_o[10]),
        .E2BEG6(result_o[9]),
        .E2BEG7(result_o[8]),
    );
    (* keep, BEL="X6Y6.A" *) Static_slot_con_X6Y6 slot1_x6y6 (
        .E2BEG0(result_o[7]),
        .E2BEG1(result_o[6]),
        .E2BEG2(result_o[5]),
        .E2BEG3(result_o[4]),
        .E2BEG4(result_o[3]),
        .E2BEG5(result_o[2]),
        .E2BEG6(result_o[1]),
        .E2BEG7(result_o[0]),
    );
    (* keep, BEL="X6Y9.A" *) Static_slot_con_X6Y9 slot1_x6y9 (
        .W2END0(op0_i[15]),
        .W2END1(op0_i[14]),
        .W2END2(op0_i[13]),
        .W2END3(op0_i[12]),
        .W2END4(op0_i[11]),
        .W2END5(op0_i[10]),
        .W2END6(op0_i[9]),
        .W2END7(op0_i[8]),
    );
    (* keep, BEL="X6Y10.A" *) Static_slot_con_X6Y10 slot1_x6y10 (
        .W2END0(op0_i[7]),
        .W2END1(op0_i[6]),
        .W2END2(op0_i[5]),
        .W2END3(op0_i[4]),
        .W2END4(op0_i[3]),
        .W2END5(op0_i[2]),
        .W2END6(op0_i[1]),
        .W2END7(op0_i[0]),
    );
endmodule

module slot2_wrapper (
    input  logic [15:0] op0_i,
    input  logic [15:0] op1_i,
    output logic [15:0] result_o,
);
    (* keep, BEL="X2Y1.A" *) Static_slot_con_X2Y1 slot2_x2y1 (
        .W2END0(op1_i[15]),
        .W2END1(op1_i[14]),
        .W2END2(op1_i[13]),
        .W2END3(op1_i[12]),
        .W2END4(op1_i[11]),
        .W2END5(op1_i[10]),
        .W2END6(op1_i[9]),
        .W2END7(op1_i[8]),
    );
    (* keep, BEL="X2Y2.A" *) Static_slot_con_X2Y2 slot2_x2y2 (
        .W2END0(op1_i[7]),
        .W2END1(op1_i[6]),
        .W2END2(op1_i[5]),
        .W2END3(op1_i[4]),
        .W2END4(op1_i[3]),
        .W2END5(op1_i[2]),
        .W2END6(op1_i[1]),
        .W2END7(op1_i[0]),
    );
    (* keep, BEL="X2Y5.A" *) Static_slot_con_X2Y5 slot2_x2y5 (
        .E2BEG0(result_o[15]),
        .E2BEG1(result_o[14]),
        .E2BEG2(result_o[13]),
        .E2BEG3(result_o[12]),
        .E2BEG4(result_o[11]),
        .E2BEG5(result_o[10]),
        .E2BEG6(result_o[9]),
        .E2BEG7(result_o[8]),
    );
    (* keep, BEL="X2Y6.A" *) Static_slot_con_X2Y6 slot2_x2y6 (
        .E2BEG0(result_o[7]),
        .E2BEG1(result_o[6]),
        .E2BEG2(result_o[5]),
        .E2BEG3(result_o[4]),
        .E2BEG4(result_o[3]),
        .E2BEG5(result_o[2]),
        .E2BEG6(result_o[1]),
        .E2BEG7(result_o[0]),
    );
    (* keep, BEL="X2Y9.A" *) Static_slot_con_X2Y9 slot2_x2y9 (
        .W2END0(op0_i[15]),
        .W2END1(op0_i[14]),
        .W2END2(op0_i[13]),
        .W2END3(op0_i[12]),
        .W2END4(op0_i[11]),
        .W2END5(op0_i[10]),
        .W2END6(op0_i[9]),
        .W2END7(op0_i[8]),
    );
    (* keep, BEL="X2Y10.A" *) Static_slot_con_X2Y10 slot2_x2y10 (
        .W2END0(op0_i[7]),
        .W2END1(op0_i[6]),
        .W2END2(op0_i[5]),
        .W2END3(op0_i[4]),
        .W2END4(op0_i[3]),
        .W2END5(op0_i[2]),
        .W2END6(op0_i[1]),
        .W2END7(op0_i[0]),
    );
endmodule

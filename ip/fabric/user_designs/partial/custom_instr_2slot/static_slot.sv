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
    logic [3:0] slot1_result, slot2_result;

    slot1_wrapper slot1 (
        .op0_i      (op0_d),
        .op1_i      (op1_d),
        .result_o   (slot1_result),
    );

    slot2_wrapper slot2 (
        .op0_i      (op0_d),
        .op1_i      (op1_d),
        .result_o   (slot2_result),
    );

    // Slot selecting
    logic [6:0]  opcode;
    logic [4:0]  rd;

    assign opcode = issue_instr_i[6:0];
    assign rd     = issue_instr_i[11:7];

    assign issue_accept_o = issue_valid_i && (opcode == INSTR3);
    assign issue_ready_o  = 1'b1;

    logic [2:0] op0_d;
    logic [3:0] op1_d;
    logic [3:0] id_d;
    logic [3:0] rd_d;
    logic issue_valid_d;

    always_ff @(posedge clk) begin
        if (rst) begin
            issue_valid_d <= 1'b0;
        end else begin
            issue_valid_d <= issue_valid_i;

            if (issue_valid_i) begin
                id_d  <= issue_id_i;
                rd_d  <= rd;
                op0_d <= issue_op0_i[2:0];
                op1_d <= issue_op1_i[3:0];
            end
        end
    end

    always_ff @(posedge clk) begin
        if (rst) begin
            result_valid_o  <= 1'b0;
        end else begin
            result_valid_o <= 1'b0;

            if (issue_valid_d) begin
                result_valid_o  <= 1'b1;
                result_id_o     <= id_d;
                result_rd_o     <= rd_d;
                result_o        <= {24'h0, slot1_result, slot2_result};  
            end
        end
    end
endmodule

module slot1_wrapper (
    input  logic [2:0] op0_i,
    input  logic [3:0] op1_i,
    output logic [3:0] result_o,
);
    (* keep, BEL="X6Y2.A" *) Static_slot_con_X6Y2 slot1_x6y2 (
        .W2END0(op1_i[3]),
        .W2END1(op1_i[2]),
        .W2END2(op1_i[1]),
        .W2END3(op1_i[0]),
    );
    (* keep, BEL="X6Y6.A" *) Static_slot_con_X6Y6 slot1_x6y6 (
        .E2BEG0(result_o[3]),
        .E2BEG1(result_o[2]),
        .E2BEG2(result_o[1]),
        .E2BEG3(result_o[0]),
    );
    (* keep, BEL="X6Y10.A" *) Static_slot_con_X6Y10 slot1_x6y10 (
        .W2END1(op0_i[2]),
        .W2END2(op0_i[1]),
        .W2END3(op0_i[0]),
    );
endmodule

module slot2_wrapper (
    input  logic [2:0] op0_i,
    input  logic [3:0] op1_i,
    output logic [3:0] result_o,
);
    (* keep, BEL="X2Y2.A" *) Static_slot_con_X2Y2 slot2_x2y2 (
        .W2END0(op1_i[3]),
        .W2END1(op1_i[2]),
        .W2END2(op1_i[1]),
        .W2END3(op1_i[0]),
    );
    (* keep, BEL="X2Y6.A" *) Static_slot_con_X2Y6 slot2_x2y6 (
        .E2BEG0(result_o[3]),
        .E2BEG1(result_o[2]),
        .E2BEG2(result_o[1]),
        .E2BEG3(result_o[0]),
    );
    (* keep, BEL="X2Y10.A" *) Static_slot_con_X2Y10 slot2_x2y10 (
        .W2END1(op0_i[2]),
        .W2END2(op0_i[1]),
        .W2END3(op0_i[0]),
    );
endmodule

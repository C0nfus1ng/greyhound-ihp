module slot1_2_wrapper (
    output logic [2:0] op0_o,
    output logic [3:0] op1_o,
    input  logic [3:0] result_i,
);
    (* keep, BEL="X5Y2.A" *) Slot1_2_slot_con_X5Y2 slot1_2_x5y2 (
        .E2END0(op1_o[3]),
        .E2END1(op1_o[2]),
        .E2END2(op1_o[1]),
        .E2END3(op1_o[0]),
    );
    (* keep, BEL="X5Y6.A" *) Slot1_2_slot_con_X5Y6 slot1_2_x5y6 (
        .W2BEG0(result_i[3]),
        .W2BEG1(result_i[2]),
        .W2BEG2(result_i[1]),
        .W2BEG3(result_i[0]),
    );
    (* keep, BEL="X5Y10.A" *) Slot1_2_slot_con_X5Y10 slot1_2_x5y10 (
        .E2END1(op0_o[2]),
        .E2END2(op0_o[1]),
        .E2END3(op0_o[0]),
    );
endmodule

module slot1_2_wrapper (
    output logic [2:0] op0_o,
    output logic [3:0] op1_o,
    input  logic [3:0] result_i,
);
    (* keep, BEL="X6Y2.A" *) Slot1_2_slot_con_X6Y2 slot1_2_x6y2 (
        .W2END0(op1_o[3]),
        .W2END1(op1_o[2]),
        .W2END2(op1_o[1]),
        .W2END3(op1_o[0]),
    );
    (* keep, BEL="X6Y6.A" *) Slot1_2_slot_con_X6Y6 slot1_2_x6y6 (
        .E2BEG0(result_i[3]),
        .E2BEG1(result_i[2]),
        .E2BEG2(result_i[1]),
        .E2BEG3(result_i[0]),
    );
    (* keep, BEL="X6Y10.A" *) Slot1_2_slot_con_X6Y10 slot1_2_x6y10 (
        .W2END1(op0_o[2]),
        .W2END2(op0_o[1]),
        .W2END3(op0_o[0]),
    );
endmodule

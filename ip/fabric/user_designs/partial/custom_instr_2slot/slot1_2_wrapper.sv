module slot1_2_wrapper (
    output logic [15:0] op0_o,
    output logic [15:0] op1_o,
    input  logic [15:0] result_i,
);
    (* keep, BEL="X6Y1.A" *) Slot1_2_slot_con_X6Y1 slot1_2_x6y1 (
        .W2END0(op1_o[15]),
        .W2END1(op1_o[14]),
        .W2END2(op1_o[13]),
        .W2END3(op1_o[12]),
        .W2END4(op1_o[11]),
        .W2END5(op1_o[10]),
        .W2END6(op1_o[9]),
        .W2END7(op1_o[8]),
    );
    (* keep, BEL="X6Y2.A" *) Slot1_2_slot_con_X6Y2 slot1_2_x6y2 (
        .W2END0(op1_o[7]),
        .W2END1(op1_o[6]),
        .W2END2(op1_o[5]),
        .W2END3(op1_o[4]),
        .W2END4(op1_o[3]),
        .W2END5(op1_o[2]),
        .W2END6(op1_o[1]),
        .W2END7(op1_o[0]),
    );
    (* keep, BEL="X6Y5.A" *) Slot1_2_slot_con_X6Y5 slot1_2_x6y5 (
        .E2BEG0(result_i[15]),
        .E2BEG1(result_i[14]),
        .E2BEG2(result_i[13]),
        .E2BEG3(result_i[12]),
        .E2BEG4(result_i[11]),
        .E2BEG5(result_i[10]),
        .E2BEG6(result_i[9]),
        .E2BEG7(result_i[8]),
    );
    (* keep, BEL="X6Y6.A" *) Slot1_2_slot_con_X6Y6 slot1_2_x6y6 (
        .E2BEG0(result_i[7]),
        .E2BEG1(result_i[6]),
        .E2BEG2(result_i[5]),
        .E2BEG3(result_i[4]),
        .E2BEG4(result_i[3]),
        .E2BEG5(result_i[2]),
        .E2BEG6(result_i[1]),
        .E2BEG7(result_i[0]),
    );
    (* keep, BEL="X6Y9.A" *) Slot1_2_slot_con_X6Y9 slot1_2_x6y9 (
        .W2END0(op0_o[15]),
        .W2END1(op0_o[14]),
        .W2END2(op0_o[13]),
        .W2END3(op0_o[12]),
        .W2END4(op0_o[11]),
        .W2END5(op0_o[10]),
        .W2END6(op0_o[9]),
        .W2END7(op0_o[8]),
    );
    (* keep, BEL="X6Y10.A" *) Slot1_2_slot_con_X6Y10 slot1_2_x6y10 (
        .W2END0(op0_o[7]),
        .W2END1(op0_o[6]),
        .W2END2(op0_o[5]),
        .W2END3(op0_o[4]),
        .W2END4(op0_o[3]),
        .W2END5(op0_o[2]),
        .W2END6(op0_o[1]),
        .W2END7(op0_o[0]),
    );
endmodule
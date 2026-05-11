module slot1_wrapper (
    output logic        rst_o,
    output logic [31:0] io_o,
    input  logic [31:0] io_i,
);
    (* keep, BEL="X4Y1.A" *) Slot1_slot_con_X4Y1 slot1_x4y1 (
        .E1END0(rst_o),
        .E2END0(io_o[31]),
        .E2END1(io_o[30]),
        .E2END2(io_o[29]),
        .E2END3(io_o[28]),

        .W1BEG0(io_i[31]),
        .W1BEG1(io_i[30]),
        .W1BEG2(io_i[29]),
        .W1BEG3(io_i[28]),
    );
    (* keep, BEL="X4Y2.A" *) Slot1_slot_con_X4Y2 slot1_x4y2 (
        .E2END0(io_o[27]),
        .E2END1(io_o[26]),
        .E2END2(io_o[25]),
        .E2END3(io_o[24]),

        .W1BEG0(io_i[27]),
        .W1BEG1(io_i[26]),
        .W1BEG2(io_i[25]),
        .W1BEG3(io_i[24]),
    );
    (* keep, BEL="X4Y3.A" *) Slot1_slot_con_X4Y3 slot1_x4y3 (
        .E2END4(io_o[23]),
        .E2END5(io_o[22]),
        .E2END6(io_o[21]),
        .E2END7(io_o[20]),

        .W1BEG0(io_i[23]),
        .W1BEG1(io_i[22]),
        .W1BEG2(io_i[21]),
        .W1BEG3(io_i[20]),
    );
    (* keep, BEL="X4Y4.A" *) Slot1_slot_con_X4Y4 slot1_x4y4 (
        .E1END0(io_o[19]),
        .E1END1(io_o[18]),
        .E1END2(io_o[17]),
        .E1END3(io_o[16]),

        .W1BEG0(io_i[19]),
        .W1BEG1(io_i[18]),
        .W1BEG2(io_i[17]),
        .W1BEG3(io_i[16]),
    );
    (* keep, BEL="X4Y5.A" *) Slot1_slot_con_X4Y5 slot1_x4y5 (
        .E1END0(io_o[15]),
        .E1END1(io_o[14]),
        .E1END2(io_o[13]),
        .E1END3(io_o[12]),

        .W1BEG0(io_i[15]),
        .W1BEG1(io_i[14]),
        .W1BEG2(io_i[13]),
        .W1BEG3(io_i[12]),
    );
    (* keep, BEL="X4Y6.A" *) Slot1_slot_con_X4Y6 slot1_x4y6 (
        .E1END0(io_o[11]),
        .E1END1(io_o[10]),
        .E1END2(io_o[9]),
        .E1END3(io_o[8]),

        .W1BEG0(io_i[11]),
        .W1BEG1(io_i[10]),
        .W1BEG2(io_i[9]),
        .W1BEG3(io_i[8]),
    );
    (* keep, BEL="X4Y7.A" *) Slot1_slot_con_X4Y7 slot1_x4y7 (
        .E1END0(io_o[7]),
        .E1END1(io_o[6]),
        .E1END2(io_o[5]),
        .E1END3(io_o[4]),

        .W1BEG0(io_i[7]),
        .W1BEG1(io_i[6]),
        .W1BEG2(io_i[5]),
        .W1BEG3(io_i[4]),
    );
    (* keep, BEL="X4Y8.A" *) Slot1_slot_con_X4Y8 slot1_x4y8 (
        .E2END0(io_o[3]),
        .E2END1(io_o[2]),
        .E2END2(io_o[1]),
        .E2END3(io_o[0]),

        .W1BEG0(io_i[3]),
        .W1BEG1(io_i[2]),
        .W1BEG2(io_i[1]),
        .W1BEG3(io_i[0]),
    );
endmodule
module slot3_wrapper (
    output logic        rst_o,
    input  logic [31:0] slot_io_i,
    output logic [31:0] slot_io_o,
);
    (* keep, BEL="X2Y1.A" *) Slot3_slot_con_X2Y1 slot3_x2y1 (
        .E1BEG0(slot_io_i[31]),
        .E1BEG1(slot_io_i[30]),
        .E1BEG2(slot_io_i[29]),
        .E1BEG3(slot_io_i[28]),

        .W1END0(slot_io_o[31]),
        .W1END1(slot_io_o[30]),
        .W1END2(slot_io_o[29]),
        .W1END3(slot_io_o[28]),
    );
    (* keep, BEL="X2Y2.A" *) Slot3_slot_con_X2Y2 slot3_x2y2 (
        .E1BEG0(slot_io_i[27]),
        .E1BEG1(slot_io_i[26]),
        .E1BEG2(slot_io_i[25]),
        .E1BEG3(slot_io_i[24]),

        .W1END0(slot_io_o[27]),
        .W1END1(slot_io_o[26]),
        .W1END2(slot_io_o[25]),
        .W1END3(slot_io_o[24]),
    );
    (* keep, BEL="X2Y3.A" *) Slot3_slot_con_X2Y3 slot3_x2y3 (
        .E1BEG0(slot_io_i[23]),
        .E1BEG1(slot_io_i[22]),
        .E1BEG2(slot_io_i[21]),
        .E1BEG3(slot_io_i[20]),

        .W1END0(slot_io_o[23]),
        .W1END1(slot_io_o[22]),
        .W1END2(slot_io_o[21]),
        .W1END3(slot_io_o[20]),
    );
    (* keep, BEL="X2Y4.A" *) Slot3_slot_con_X2Y4 slot3_x2y4 (
        .E1BEG0(slot_io_i[19]),
        .E1BEG1(slot_io_i[18]),
        .E1BEG2(slot_io_i[17]),
        .E1BEG3(slot_io_i[16]),

        .W1END0(slot_io_o[19]),
        .W1END1(slot_io_o[18]),
        .W1END2(slot_io_o[17]),
        .W1END3(slot_io_o[16]),
    );
    (* keep, BEL="X2Y5.A" *) Slot3_slot_con_X2Y5 slot3_x2y5 (
        .E1BEG0(slot_io_i[15]),
        .E1BEG1(slot_io_i[14]),
        .E1BEG2(slot_io_i[13]),
        .E1BEG3(slot_io_i[12]),

        .W1END0(slot_io_o[15]),
        .W1END1(slot_io_o[14]),
        .W1END2(slot_io_o[13]),
        .W1END3(slot_io_o[12]),
    );
    (* keep, BEL="X2Y6.A" *) Slot3_slot_con_X2Y6 slot3_x2y6 (
        .E1BEG0(slot_io_i[11]),
        .E1BEG1(slot_io_i[10]),
        .E1BEG2(slot_io_i[9]),
        .E1BEG3(slot_io_i[8]),

        .W1END0(slot_io_o[11]),
        .W1END1(slot_io_o[10]),
        .W1END2(slot_io_o[9]),
        .W1END3(slot_io_o[8]),
    );
    (* keep, BEL="X2Y7.A" *) Slot3_slot_con_X2Y7 slot3_x2y7 (
        .E1BEG0(slot_io_i[7]),
        .E1BEG1(slot_io_i[6]),
        .E1BEG2(slot_io_i[5]),
        .E1BEG3(slot_io_i[4]),

        .W1END0(slot_io_o[7]),
        .W1END1(slot_io_o[6]),
        .W1END2(slot_io_o[5]),
        .W1END3(slot_io_o[4]),
    );
    (* keep, BEL="X2Y8.A" *) Slot3_slot_con_X2Y8 slot3_x2y8 (
        .E1BEG0(slot_io_i[3]),
        .E1BEG1(slot_io_i[2]),
        .E1BEG2(slot_io_i[1]),
        .E1BEG3(slot_io_i[0]),

        .W1END0(slot_io_o[3]),
        .W1END1(slot_io_o[2]),
        .W1END2(slot_io_o[1]),
        .W1END3(slot_io_o[0]),
        .S1END0(rst_o),
    );
endmodule
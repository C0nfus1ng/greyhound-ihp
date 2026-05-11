module slot3_wrapper (
    output logic        rst_o,
    input  logic [31:0] slot_io_i,
    output logic [31:0] slot_io_o,
    output logic [31:0] slot_io_oeb_o,
);
    (* keep, BEL="X2Y1.A" *) Slot3_slot_con_X2Y1 slot3_x2y1 (
        .E2BEG4(slot_io_i[31]),
        .E2BEG5(slot_io_i[30]),
        .E2BEG6(slot_io_i[29]),
        .E2BEG7(slot_io_i[28]),

        .W1END0(slot_io_oeb_o[31]),
        .W1END1(slot_io_oeb_o[30]),
        .W1END2(slot_io_oeb_o[29]),
        .W1END3(slot_io_oeb_o[28]),
        .W2END0(slot_io_o[31]),
        .W2END1(slot_io_o[30]),
        .W2END2(slot_io_o[29]),
        .W2END3(slot_io_o[28]),
    );
    (* keep, BEL="X2Y2.A" *) Slot3_slot_con_X2Y2 slot3_x2y2 (
        .E2BEG0(slot_io_i[27]),
        .E2BEG1(slot_io_i[26]),
        .E2BEG2(slot_io_i[25]),
        .E2BEG3(slot_io_i[24]),

        .W1END0(slot_io_o[27]),
        .W1END1(slot_io_o[26]),
        .W1END2(slot_io_o[25]),
        .W1END3(slot_io_o[24]),
        .W2END0(slot_io_oeb_o[27]),
        .W2END1(slot_io_oeb_o[26]),
        .W2END2(slot_io_oeb_o[25]),
        .W2END3(slot_io_oeb_o[24]),
    );
    (* keep, BEL="X2Y3.A" *) Slot3_slot_con_X2Y3 slot3_x2y3 (
        .E2BEG4(slot_io_i[23]),
        .E2BEG5(slot_io_i[22]),
        .E2BEG6(slot_io_i[21]),
        .E2BEG7(slot_io_i[20]),

        .W1END0(slot_io_oeb_o[23]),
        .W1END1(slot_io_oeb_o[22]),
        .W1END2(slot_io_oeb_o[21]),
        .W1END3(slot_io_oeb_o[20]),
        .W2END0(slot_io_o[23]),
        .W2END1(slot_io_o[22]),
        .W2END2(slot_io_o[21]),
        .W2END3(slot_io_o[20]),
    );
    (* keep, BEL="X2Y4.A" *) Slot3_slot_con_X2Y4 slot3_x2y4 (
        .E2BEG4(slot_io_i[19]),
        .E2BEG5(slot_io_i[18]),
        .E2BEG6(slot_io_i[17]),
        .E2BEG7(slot_io_i[16]),

        .W1END0(slot_io_o[19]),
        .W1END1(slot_io_o[18]),
        .W1END2(slot_io_o[17]),
        .W1END3(slot_io_o[16]),
        .W2END0(slot_io_oeb_o[19]),
        .W2END1(slot_io_oeb_o[18]),
        .W2END2(slot_io_oeb_o[17]),
        .W2END3(slot_io_oeb_o[16]),
    );
    (* keep, BEL="X2Y5.A" *) Slot3_slot_con_X2Y5 slot3_x2y5 (
        .E2BEG4(slot_io_i[15]),
        .E2BEG5(slot_io_i[14]),
        .E2BEG6(slot_io_i[13]),
        .E2BEG7(slot_io_i[12]),

        .W1END0(slot_io_oeb_o[15]),
        .W1END1(slot_io_oeb_o[14]),
        .W1END2(slot_io_oeb_o[13]),
        .W1END3(slot_io_oeb_o[12]),
        .W2END0(slot_io_o[15]),
        .W2END1(slot_io_o[14]),
        .W2END2(slot_io_o[13]),
        .W2END3(slot_io_o[12]),
    );
    (* keep, BEL="X2Y6.A" *) Slot3_slot_con_X2Y6 slot3_x2y6 (
        .E2BEG0(slot_io_i[11]),
        .E2BEG1(slot_io_i[10]),
        .E2BEG2(slot_io_i[9]),
        .E2BEG3(slot_io_i[8]),

        .W1END0(slot_io_o[11]),
        .W1END1(slot_io_o[10]),
        .W1END2(slot_io_o[9]),
        .W1END3(slot_io_o[8]),
        .W2END0(slot_io_oeb_o[11]),
        .W2END1(slot_io_oeb_o[10]),
        .W2END2(slot_io_oeb_o[9]),
        .W2END3(slot_io_oeb_o[8]),
    );
    (* keep, BEL="X2Y7.A" *) Slot3_slot_con_X2Y7 slot3_x2y7 (
        .E2BEG4(slot_io_i[7]),
        .E2BEG5(slot_io_i[6]),
        .E2BEG6(slot_io_i[5]),
        .E2BEG7(slot_io_i[4]),

        .W1END0(slot_io_oeb_o[7]),
        .W1END1(slot_io_oeb_o[6]),
        .W1END2(slot_io_oeb_o[5]),
        .W1END3(slot_io_oeb_o[4]),
        .W2END0(slot_io_o[7]),
        .W2END1(slot_io_o[6]),
        .W2END2(slot_io_o[5]),
        .W2END3(slot_io_o[4]),
    );
    (* keep, BEL="X2Y8.A" *) Slot3_slot_con_X2Y8 slot3_x2y8 (
        .E2BEG0(slot_io_i[3]),
        .E2BEG1(slot_io_i[2]),
        .E2BEG2(slot_io_i[1]),
        .E2BEG3(slot_io_i[0]),

        .W1END0(slot_io_o[3]),
        .W1END1(slot_io_o[2]),
        .W1END2(slot_io_o[1]),
        .W1END3(slot_io_o[0]),
        .W2END0(slot_io_oeb_o[3]),
        .W2END1(slot_io_oeb_o[2]),
        .W2END2(slot_io_oeb_o[1]),
        .W2END3(slot_io_oeb_o[0]),
    );
endmodule
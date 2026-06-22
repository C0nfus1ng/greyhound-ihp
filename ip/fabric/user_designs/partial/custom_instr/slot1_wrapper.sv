module slot1_wrapper (
    output logic        rst_o,
    output logic [31:0] io_o,
);
    (* keep, BEL="X3Y1.A" *) Slot1_slot_con_X3Y1 slot1_x3y1 (
        .W1END0(io_o[0]),
        .W1END1(io_o[1]),
        .W1END2(io_o[2]),
        .W1END3(io_o[3]),
    );
    (* keep, BEL="X3Y2.A" *) Slot1_slot_con_X3Y2 slot1_x3y2 (
        .W1END0(io_o[4]),
        .W1END1(io_o[5]),
        .W1END2(io_o[6]),
        .W1END3(io_o[7]),
    );
    (* keep, BEL="X3Y3.A" *) Slot1_slot_con_X3Y3 slot1_x3y3 (
        .W1END0(io_o[8]),
        .W1END1(io_o[9]),
        .W1END2(io_o[10]),
        .W1END3(io_o[11]),
    );
    (* keep, BEL="X3Y4.A" *) Slot1_slot_con_X3Y4 slot1_x3y4 (
        .W1END0(io_o[12]),
        .W1END1(io_o[13]),
        .W1END2(io_o[14]),
        .W1END3(io_o[15]),
    );
    (* keep, BEL="X3Y5.A" *) Slot1_slot_con_X3Y5 slot1_x3y5 (
        .W1END0(io_o[16]),
        .W1END1(io_o[17]),
        .W1END2(io_o[18]),
        .W1END3(io_o[19]),
    );
    (* keep, BEL="X3Y6.A" *) Slot1_slot_con_X3Y6 slot1_x3y6 (
        .W1END0(io_o[20]),
        .W1END1(io_o[21]),
        .W1END2(io_o[22]),
        .W1END3(io_o[23]),
    );
    (* keep, BEL="X3Y7.A" *) Slot1_slot_con_X3Y7 slot1_x3y7 (
        .W1END0(io_o[24]),
        .W1END1(io_o[25]),
        .W1END2(io_o[26]),
        .W1END3(io_o[27]),
    );
    (* keep, BEL="X3Y8.A" *) Slot1_slot_con_X3Y8 slot1_x3y8 (
        .W1END0(io_o[28]),
        .W1END1(io_o[29]),
        .W1END2(io_o[30]),
        .W1END3(io_o[31]),
    );
    (* keep, BEL="X3Y13.A" *) Slot1_slot_con_X3Y13 slot1_x3y13 (
        .W1END0(rst_o),
    );
endmodule
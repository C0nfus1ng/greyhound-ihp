module slot2_wrapper (
    output logic        rst_o,
    input  logic [31:0] io_i,
);
    (* keep, BEL="X4Y1.A" *) Slot2_slot_con_X4Y1 slot2_x4y1 (
        .W1BEG0(io_i[0]),
        .W1BEG1(io_i[1]),
        .W1BEG2(io_i[2]),
        .W1BEG3(io_i[3]),
    );
    (* keep, BEL="X4Y2.A" *) Slot2_slot_con_X4Y2 slot2_x4y2 (
        .W1BEG0(io_i[4]),
        .W1BEG1(io_i[5]),
        .W1BEG2(io_i[6]),
        .W1BEG3(io_i[7]),
    );
    (* keep, BEL="X4Y3.A" *) Slot2_slot_con_X4Y3 slot2_x4y3 (
        .W1BEG0(io_i[8]),
        .W1BEG1(io_i[9]),
        .W1BEG2(io_i[10]),
        .W1BEG3(io_i[11]),
    );
    (* keep, BEL="X4Y4.A" *) Slot2_slot_con_X4Y4 slot2_x4y4 (
        .W1BEG0(io_i[12]),
        .W1BEG1(io_i[13]),
        .W1BEG2(io_i[14]),
        .W1BEG3(io_i[15]),
    );
    (* keep, BEL="X4Y5.A" *) Slot2_slot_con_X4Y5 slot2_x4y5 (
        .W1BEG0(io_i[16]),
        .W1BEG1(io_i[17]),
        .W1BEG2(io_i[18]),
        .W1BEG3(io_i[19]),
    );
    (* keep, BEL="X4Y6.A" *) Slot2_slot_con_X4Y6 slot2_x4y6 (
        .W1BEG0(io_i[20]),
        .W1BEG1(io_i[21]),
        .W1BEG2(io_i[22]),
        .W1BEG3(io_i[23]),
    );
    (* keep, BEL="X4Y7.A" *) Slot2_slot_con_X4Y7 slot2_x4y7 (
        .W1BEG0(io_i[24]),
        .W1BEG1(io_i[25]),
        .W1BEG2(io_i[26]),
        .W1BEG3(io_i[27]),
    );
    (* keep, BEL="X4Y8.A" *) Slot2_slot_con_X4Y8 slot2_x4y8 (
        .W1BEG0(io_i[28]),
        .W1BEG1(io_i[29]),
        .W1BEG2(io_i[30]),
        .W1BEG3(io_i[31]),
    );
    (* keep, BEL="X4Y13.A" *) Slot2_slot_con_X4Y13 slot2_x4y13 (
        .E1END0(rst_o),
    );
endmodule
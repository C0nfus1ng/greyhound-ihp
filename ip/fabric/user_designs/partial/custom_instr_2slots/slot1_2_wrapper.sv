module slot1_2_wrapper (
    output logic [3:0] io_o,
    input  logic [3:0] io_i,
);
    (* keep, BEL="X1Y7.A" *) Slot1_2_slot_con_X1Y7 slot1_2_x1y7 (
        .N1END0(io_o[0]),
        .N1END1(io_o[1]),
        .N1END2(io_o[2]),
        .N1END3(io_o[3]),

        .S1BEG0(io_i[0]),
        .S1BEG1(io_i[1]),
        .S1BEG2(io_i[2]),
        .S1BEG3(io_i[3]),
    );
endmodule
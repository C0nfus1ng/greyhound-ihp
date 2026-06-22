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

    logic [31:0] io_shim;
    slot1_wrapper slot1 (
        .rst_i ( rst     ),
        .io_i  ( io_shim ),
    );

    slot2_wrapper slot2 (
        .rst_i ( rst     ),
        .io_o  ( io_shim ),
    );

endmodule

module slot1_wrapper (
    input logic        rst_i,
    input logic [31:0] io_i,
);
    (* keep, BEL="X3Y1.A" *) Static_slot_con_X3Y1 slot1_x3y1 (
        .W1END0(io_i[0]),
        .W1END1(io_i[1]),
        .W1END2(io_i[2]),
        .W1END3(io_i[3]),
    );
    (* keep, BEL="X3Y2.A" *) Static_slot_con_X3Y2 slot1_x3y2 (
        .W1END0(io_i[4]),
        .W1END1(io_i[5]),
        .W1END2(io_i[6]),
        .W1END3(io_i[7]),
    );
    (* keep, BEL="X3Y3.A" *) Static_slot_con_X3Y3 slot1_x3y3 (
        .W1END0(io_i[8]),
        .W1END1(io_i[9]),
        .W1END2(io_i[10]),
        .W1END3(io_i[11]),
    );
    (* keep, BEL="X3Y4.A" *) Static_slot_con_X3Y4 slot1_x3y4 (
        .W1END0(io_i[12]),
        .W1END1(io_i[13]),
        .W1END2(io_i[14]),
        .W1END3(io_i[15]),
    );
    (* keep, BEL="X3Y5.A" *) Static_slot_con_X3Y5 slot1_x3y5 (
        .W1END0(io_i[16]),
        .W1END1(io_i[17]),
        .W1END2(io_i[18]),
        .W1END3(io_i[19]),
    );
    (* keep, BEL="X3Y6.A" *) Static_slot_con_X3Y6 slot1_x3y6 (
        .W1END0(io_i[20]),
        .W1END1(io_i[21]),
        .W1END2(io_i[22]),
        .W1END3(io_i[23]),
    );
    (* keep, BEL="X3Y7.A" *) Static_slot_con_X3Y7 slot1_x3y7 (
        .W1END0(io_i[24]),
        .W1END1(io_i[25]),
        .W1END2(io_i[26]),
        .W1END3(io_i[27]),
    );
    (* keep, BEL="X3Y8.A" *) Static_slot_con_X3Y8 slot1_x3y8 (
        .W1END0(io_i[28]),
        .W1END1(io_i[29]),
        .W1END2(io_i[30]),
        .W1END3(io_i[31]),
    );
    (* keep, BEL="X3Y13.A" *) Static_slot_con_X3Y13 slot1_x3y13 (
        .W1END0(rst_i),
    );
endmodule

module slot2_wrapper (
    input  logic        rst_i,
    output logic [31:0] io_o,
);
    (* keep, BEL="X4Y1.A" *) Static_slot_con_X4Y1 slot2_x4y1 (
        .W1BEG0(io_o[0]),
        .W1BEG1(io_o[1]),
        .W1BEG2(io_o[2]),
        .W1BEG3(io_o[3]),
    );
    (* keep, BEL="X4Y2.A" *) Static_slot_con_X4Y2 slot2_x4y2 (
        .W1BEG0(io_o[4]),
        .W1BEG1(io_o[5]),
        .W1BEG2(io_o[6]),
        .W1BEG3(io_o[7]),
    );
    (* keep, BEL="X4Y3.A" *) Static_slot_con_X4Y3 slot2_x4y3 (
        .W1BEG0(io_o[8]),
        .W1BEG1(io_o[9]),
        .W1BEG2(io_o[10]),
        .W1BEG3(io_o[11]),
    );
    (* keep, BEL="X4Y4.A" *) Static_slot_con_X4Y4 slot2_x4y4 (
        .W1BEG0(io_o[12]),
        .W1BEG1(io_o[13]),
        .W1BEG2(io_o[14]),
        .W1BEG3(io_o[15]),
    );
    (* keep, BEL="X4Y5.A" *) Static_slot_con_X4Y5 slot2_x4y5 (
        .W1BEG0(io_o[16]),
        .W1BEG1(io_o[17]),
        .W1BEG2(io_o[18]),
        .W1BEG3(io_o[19]),
    );
    (* keep, BEL="X4Y6.A" *) Static_slot_con_X4Y6 slot2_x4y6 (
        .W1BEG0(io_o[20]),
        .W1BEG1(io_o[21]),
        .W1BEG2(io_o[22]),
        .W1BEG3(io_o[23]),
    );
    (* keep, BEL="X4Y7.A" *) Static_slot_con_X4Y7 slot2_x4y7 (
        .W1BEG0(io_o[24]),
        .W1BEG1(io_o[25]),
        .W1BEG2(io_o[26]),
        .W1BEG3(io_o[27]),
    );
    (* keep, BEL="X4Y8.A" *) Static_slot_con_X4Y8 slot2_x4y8 (
        .W1BEG0(io_o[28]),
        .W1BEG1(io_o[29]),
        .W1BEG2(io_o[30]),
        .W1BEG3(io_o[31]),
    );
    (* keep, BEL="X4Y13.A" *) Static_slot_con_X4Y13 slot2_x4y13 (
        .E1END0(rst_i),
    );
endmodule

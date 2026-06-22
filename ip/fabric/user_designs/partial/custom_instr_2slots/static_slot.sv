module static_slot();
    // CLK
    logic clk;
    (* keep *) Global_Clock clk_i (.CLK(clk));

    logic [3:0] slot_io_i, slot1_io_o, slot2_io_o;
    slot1_wrapper slot1 (
        .io_i  ( slot_io_i ),
        .io_o  ( slot1_io_o ),
    );

    slot2_wrapper slot2 (
        .io_i  ( slot_io_i ),
        .io_o  ( slot2_io_o ),
    );

    wire [31:0] RS1;
    wire [31:0] RS2;
    wire [31:0] RESULT;

    xif_wrapper i_xif_wrapper (
        .RS1,
        .RS2,
        .RESULT
    );
    assign slot_io_i = RS1[3:0];
    assign RESULT = {24'h0, slot2_io_o, slot1_io_o};

    // Phys IOs
    logic [31:0] phys_io_i, phys_io_oeb, phys_io_o;
    (* keep *) io_wrapper io (
        .io_i     (phys_io_i),
        .io_oeb_i (phys_io_oeb),
        .io_o     (phys_io_o),
    );
    assign phys_io_oeb[31:8] = '1;
    assign phys_io_oeb[7:0]  = '0;

    assign phys_io_i[7:4] = slot2_io_o;
    assign phys_io_i[3:0] = slot1_io_o;
endmodule

module slot1_wrapper (
    input  logic [3:0] io_i,
    output logic [3:0] io_o,
);
    (* keep, BEL="X1Y7.A" *) Static_slot_con_X1Y7 slot1_x1y7 (
        .N1END0(io_i[0]),
        .N1END1(io_i[1]),
        .N1END2(io_i[2]),
        .N1END3(io_i[3]),

        .S1BEG0(io_o[0]),
        .S1BEG1(io_o[1]),
        .S1BEG2(io_o[2]),
        .S1BEG3(io_o[3]),
    );
endmodule

module slot2_wrapper (
    input  logic [3:0] io_i,
    output logic [3:0] io_o,
);
    (* keep, BEL="X3Y7.A" *) Static_slot_con_X3Y7 slot2_x3y7 (
        .N1END0(io_i[0]),
        .N1END1(io_i[1]),
        .N1END2(io_i[2]),
        .N1END3(io_i[3]),

        .S1BEG0(io_o[0]),
        .S1BEG1(io_o[1]),
        .S1BEG2(io_o[2]),
        .S1BEG3(io_o[3]),
    );
endmodule

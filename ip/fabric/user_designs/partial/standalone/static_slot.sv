module static_slot();
    // CLK
    logic clk;
    (* keep *) Global_Clock clk_i (.CLK(clk));

    // RST
    logic rst, boot;
    logic [3:0] slot;
    WARMBOOT_wrapper WARMBOOT_wrapper (
        .SLOT   (slot),
        .BOOT   (boot),
        .RESET  (rst)
    );

    // Slot IOs
    logic [31:0] phys_io_i, phys_io_oeb, phys_io_o;
    (* keep *) io_wrapper io (
        .io_i     (phys_io_o),
        .io_oeb_i (phys_io_oeb),
        .io_o     (phys_io_i),
    );

    // Slot BEL placement
    logic [3:0] slot1_result, slot2_result;
    logic [2:0] op0;
    logic [3:0] op1;

    slot1_wrapper slot1 (
        .op0_i      (op0),
        .op1_i      (op1),
        .result_o   (slot1_result),
    );

    slot2_wrapper slot2 (
        .op0_i      (op0),
        .op1_i      (op1),
        .result_o   (slot2_result),
    );

    assign slot = phys_io_i[11:8];
    assign boot = phys_io_i[12];
    assign op0  = phys_io_i[15:13];
    assign op1  = phys_io_i[19:16];

    assign phys_io_oeb[19:8] = '1;
    assign phys_io_oeb[7:0]  = '0;
    assign phys_io_o[7:4] = slot2_result;
    assign phys_io_o[3:0] = slot1_result;

endmodule

module slot1_wrapper (
    input  logic [2:0] op0_i,
    input  logic [3:0] op1_i,
    output logic [3:0] result_o,
);
    (* keep, BEL="X5Y2.A" *) Static_slot_con_X5Y2 slot1_x5y2 (
        .E2END0(op1_i[3]),
        .E2END1(op1_i[2]),
        .E2END2(op1_i[1]),
        .E2END3(op1_i[0]),
    );
    (* keep, BEL="X5Y6.A" *) Static_slot_con_X5Y6 slot1_x5y6 (
        .W2BEG0(result_o[3]),
        .W2BEG1(result_o[2]),
        .W2BEG2(result_o[1]),
        .W2BEG3(result_o[0]),
    );
    (* keep, BEL="X5Y10.A" *) Static_slot_con_X5Y10 slot1_x5y10 (
        .E2END1(op0_i[2]),
        .E2END2(op0_i[1]),
        .E2END3(op0_i[0]),
    );
endmodule

module slot2_wrapper (
    input  logic [2:0] op0_i,
    input  logic [3:0] op1_i,
    output logic [3:0] result_o,
);
    (* keep, BEL="X9Y2.A" *) Static_slot_con_X9Y2 slot2_x9y2 (
        .E2END0(op1_i[3]),
        .E2END1(op1_i[2]),
        .E2END2(op1_i[1]),
        .E2END3(op1_i[0]),
    );
    (* keep, BEL="X9Y6.A" *) Static_slot_con_X9Y6 slot2_x9y6 (
        .W2BEG0(result_o[3]),
        .W2BEG1(result_o[2]),
        .W2BEG2(result_o[1]),
        .W2BEG3(result_o[0]),
    );
    (* keep, BEL="X9Y10.A" *) Static_slot_con_X9Y10 slot2_x9y10 (
        .E2END1(op0_i[2]),
        .E2END2(op0_i[1]),
        .E2END3(op0_i[0]),
    );
endmodule

module slot1_2_combine ();
    // Slot IOs
    logic [2:0] op0;
    logic [3:0] op1, result;
    (* keep *) slot1_2_wrapper wrapper (
        .op0_o    (op0),
        .op1_o    (op1),
        .result_i (result),
    );

    assign result[3] = op0[1];
    assign result[2] = op0[0];
    assign result[1] = op1[1];
    assign result[0] = op1[0];

endmodule
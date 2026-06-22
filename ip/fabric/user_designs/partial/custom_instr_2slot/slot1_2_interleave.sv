module slot1_2_interleave ();
    // Slot IOs
    logic [15:0] op0, op1, result;
    (* keep *) slot1_2_wrapper wrapper (
        .op0_o    (op0),
        .op1_o    (op1),
        .result_i (result),
    );

    assign result[7] = op0[4];
    assign result[6] = op1[4];
    assign result[5] = op0[5];
    assign result[4] = op1[5];
    assign result[3] = op0[6];
    assign result[2] = op1[6];
    assign result[1] = op0[7];
    assign result[0] = op1[7];

endmodule
module slot1_2_function ();
    // Slot IOs
    logic [2:0] op0;
    logic [3:0] op1, result;
    (* keep *) slot1_2_wrapper wrapper (
        .op0_o    (op0),
        .op1_o    (op1),
        .result_i (result),
    );

    always_comb begin
        case (op0)
            3'h0: result = op1;
            3'h1: result = ~op1;
            3'h2: result = {op1[0], op1[1], op1[2], op1[3]};
            3'h3: result = {op1[0], op1[3], op1[1], op1[2]};
            3'h4: result = {op1[2:0], op1[3]};
            3'h5: result = {op1[0], op1[3:1]};
            3'h6: result = op1+1;
            3'h7: result = op1+op1;
        endcase
    end
endmodule
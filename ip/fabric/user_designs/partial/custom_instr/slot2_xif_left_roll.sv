module slot2_xif_left_roll ();
    wire [31:0] RS1;
    wire [31:0] RS2;
    wire [31:0] RESULT;

    xif_wrapper i_xif_wrapper (
        .RS1,
        .RS2,
        .RESULT
    );

    // Slot IOs
    logic rst;
    slot2_wrapper wrapper(
        .rst_o ( rst    ),
        .io_i  ( RESULT ),
    );

    always_comb begin
        if (RS2[4:0] == 0) begin
            RESULT = RS1;
        end
        else begin
            RESULT = {RS1[31-RS2[4:0]:0], RS1[31:32-RS2[4:0]]};
        end
    end
endmodule

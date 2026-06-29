module slot2_xif_right_roll ();
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

    wire [63:0] tmp;
    assign tmp = {RS1, RS1};
    assign RESULT = tmp[RS2[4:0]+:32];
endmodule

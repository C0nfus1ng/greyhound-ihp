module xif();
    wire [31:0] RS1;
    wire [31:0] RS2;
    wire [31:0] RESULT;

    xif_wrapper i_xif_wrapper (
        .RS1,
        .RS2,
        .RESULT
    );

    assign RESULT = {24'h0, RS2[3:0], RS1[3:0]};

    // Phys IOs
    logic [31:0] phys_io_i, phys_io_oeb, phys_io_o;
    (* keep *) io_wrapper io (
        .io_i     (phys_io_i),
        .io_oeb_i (phys_io_oeb),
        .io_o     (phys_io_o),
    );
    assign phys_io_oeb[31:8] = '1;
    assign phys_io_oeb[7:0]  = '0;

    assign phys_io_i[7:4] = RS2[3:0];
    assign phys_io_i[3:0] = RS1[3:0];
endmodule

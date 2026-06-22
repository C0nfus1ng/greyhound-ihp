module slot1_direct_out();
    logic rst;

    // Phys IOs
    logic [31:0] io_i, io_oeb, io_o;
    (* keep *) io_wrapper io (
        .io_i     (io_o),
        .io_oeb_i (io_oeb),
        .io_o     (io_i),
    );

    assign io_oeb = '0;

    // Slot IOs
    (* keep *) slot1_wrapper wrapper (
        .rst_o (rst),
        .io_o  (io_o),
    );
endmodule

module slot3_straight_through();
    logic rst;

    // Phys IOs
    logic [31:0] io_i, io_oeb, io_o;
    (* keep *) io_wrapper io (
        .io_i     (io_i),
        .io_oeb_i (io_oeb),
        .io_o     (io_o),
    );

    // Slot IOs
    (* keep *) slot3_wrapper wrapper (
        .rst_o          (rst),
        .slot_io_i      (io_i),
        .slot_io_o      (io_o),
        .slot_io_oeb_o  (io_oeb),
    );
endmodule
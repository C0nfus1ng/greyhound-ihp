module slot1_graycode();
    logic rst;

    // Phys IOs
    logic [31:0] phys_io_i, phys_io_oeb, phys_io_o;
    (* keep *) io_wrapper io (
        .io_i     (phys_io_i),
        .io_oeb_i (phys_io_oeb),
        .io_o     (phys_io_o),
    );
    assign phys_io_oeb = '0;

    // Slot IOs
    logic [31:0] slot_io_o;
    (* keep *) slot1_wrapper wrapper (
        .rst_o (rst),
        .io_o  (slot_io_o),
    );

    assign phys_io_i = slot_io_o ^ {1'b0, slot_io_o[31:1]};
endmodule

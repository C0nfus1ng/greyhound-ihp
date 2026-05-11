module slot3_straight_through();
    logic rst;

    // Phys IOs
    logic [31:0] phys_io_i, phys_io_oeb, phys_io_o;
    (* keep *) io_wrapper io (
        .io_i     (phys_io_o),
        .io_oeb_i (phys_io_oeb),
        .io_o     (phys_io_i),
    );

    // Slot IOs
    logic [31:0] slot_io_i, slot_io_oeb, slot_io_o;
    (* keep *) slot3_wrapper wrapper (
        .rst_o          (rst),
        .slot_io_i      (slot_io_i),
        .slot_io_o      (slot_io_o),
        .slot_io_oeb_o  (slot_io_oeb),
    );

    for (genvar i = 0; i < 32; i++) begin
        assign phys_io_o[31-i]   = slot_io_i[i];
        assign phys_io_oeb[31-i] = slot_io_oeb[i];
        assign slot_io_o[31-i]   = phys_io_i[i];
    end

endmodule
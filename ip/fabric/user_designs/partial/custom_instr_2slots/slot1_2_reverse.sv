module slot1_2_reverse();
    // Slot IOs
    logic [3:0] io_i, io_o;
    (* keep *) slot1_2_wrapper wrapper (
        .io_i    (io_i),
        .io_o    (io_o),
    );

    assign io_i[3] = io_o[0];
    assign io_i[2] = io_o[1];
    assign io_i[1] = io_o[2];
    assign io_i[0] = io_o[3];
endmodule

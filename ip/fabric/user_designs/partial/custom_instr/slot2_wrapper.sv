module slot2_wrapper (
    output logic rst_o,
);
    (* keep, BEL="X8Y1.A" *) Slot2_slot_con_X8Y1 slot2_x8y1 (
        .E1END0(rst_o),
    );
endmodule
module slot1_stage ();
    logic clk;
    (* keep *) Global_Clock clk_i (.CLK(clk));
    
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

    logic [7:0] io_byte [4];
    logic [1:0] byte_cnt;
    logic overflow;

    for (genvar i = 0; i < 4; i++) begin
        assign io_byte[i] = slot_io_o[(i*4):+8];
    end

    always_ff @(posedge clk) begin
        if (rst) begin
            {overflow, byte_cnt} <= '0;
        end
        else begin
            {overflow, byte_cnt} <= byte_cnt + 1;
        end
    end

    always_ff @(posedge clk) begin
        if (rst) begin
            phys_io_i <= 32'hb007e5e7;
        end
        else begin
            if (overflow) begin
                phys_io_i <= '0;            
            end
            else begin
                phys_io_i <= {phys_io_i[23:0], io_byte[byte_cnt]};            
            end
        end
    end

endmodule
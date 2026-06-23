module slot2_counter ();
    // CLK
    logic clk;
    (* keep *) Global_Clock clk_i (.CLK(clk));

    // Slot IOs
    logic rst;
    slot2_wrapper wrapper(
        .rst_o ( rst      ),
        .io_i  ( cnt ),
    );

    logic [31:0] cnt;
    logic [11:0] wait_cnt;

    always_ff @(posedge clk) begin
        if (rst) begin
            wait_cnt <= '0;
        end
        else begin
            wait_cnt <= wait_cnt+12'h1;
        end
    end

    always_ff @(posedge clk) begin
        if (rst) begin
            cnt <= 32'hdeadbeef;
        end
        else begin
            if (wait_cnt == 0) begin
                cnt <= cnt+32'h1;
            end
        end
    end
endmodule

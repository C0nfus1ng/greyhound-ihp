module slot1(
    input  wire       clk,
    input  wire [3:0] lut4_o_i,
    output wire       lut4_in_o,
);
    wire rst;
    logic [1:0] roll;

	// assign lut4_in_o = '1;

    assign rst = lut4_o_i[0];

    always_ff @(posedge clk) begin
        if (rst) begin
            lut4_in_o <= '0;
            roll      <= 2'b01;
        end
        else begin
            lut4_in_o <= roll[0];
            roll      <= {roll[0], roll[1]};
        end
    end

endmodule
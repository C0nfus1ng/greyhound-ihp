module slot1(
    input  wire       clk,
    input  wire [3:0] lut4_o_i,
    output wire       lut4_in_o,
);
    wire rst;
    logic [3:0] roll;

    assign rst = lut4_o_i[0];

    always_ff @(posedge clk) begin
        if (rst) begin
            lut4_in_o <= '0;
            roll      <= 4'b0011;
        end
        else begin
            lut4_in_o <= roll[0];
            roll      <= {roll[2:0], roll[3]};
        end
    end

endmodule
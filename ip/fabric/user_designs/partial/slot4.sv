module slot4(
    input  wire       clk,
    input  wire [7:0] slot_i,
    output wire [1:0] slot_o,
);
    wire rst;
    logic [5:0] roll1, roll2;

    assign rst = slot_i[0];

    always_ff @(posedge clk) begin
        if (rst) begin
            slot_o <= '0;
            roll1  <= 6'b100110;
            roll2  <= 6'b110100;
        end
        else begin
            slot_o[0] <= roll1[0];
            slot_o[1] <= roll2[0];
            roll1     <= {roll1[4:0], roll1[5]};
            roll2     <= {roll2[4:0], roll2[5]};
        end
    end

endmodule
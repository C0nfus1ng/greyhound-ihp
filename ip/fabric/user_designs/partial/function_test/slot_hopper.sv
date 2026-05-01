module slot_hopper(
    input  wire       clk,
    input  wire [3:0] slot_i,
    output wire       slot_o,
);
    wire rst;
    logic [11:0] roll;

    assign rst = slot_i[0];

    always_ff @(posedge clk) begin
        if (rst) begin
            slot_o <= '0;
            roll   <= 12'b001100110101;
        end
        else begin
            slot_o <= roll[0];
            roll   <= {roll[10:0], roll[11]};
        end
    end

endmodule
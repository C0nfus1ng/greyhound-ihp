module slot2(
    input  wire       clk,
    input  wire [3:0] slot_i,
    output wire       slot_o,
);
    wire rst;
    logic [1:0] roll;

    assign rst = slot_i[0];

    always_ff @(posedge clk) begin
        if (rst) begin
            slot_o <= '0;
            roll   <= 2'b01;
        end
        else begin
            slot_o <= roll[0];
            roll   <= {roll[0], roll[1]};
        end
    end

endmodule
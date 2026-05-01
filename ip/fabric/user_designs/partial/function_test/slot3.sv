module slot3(
    input  wire       clk,
    input  wire [3:0] slot_i,
    output wire       slot_o,
);
    wire rst;
    logic [5:0] roll;

    assign rst = slot_i[0];

    always_ff @(posedge clk) begin
        if (rst) begin
            slot_o <= '0;
            roll   <= 6'b010011;
        end
        else begin
            slot_o <= roll[0];
            roll   <= {roll[4:0], roll[5]};
        end
    end

endmodule
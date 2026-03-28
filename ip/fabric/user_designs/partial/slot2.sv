module slot2(
    input  wire        clk,
    input  wire        rst,
    input  wire [`NUM_IO-1:0] io_in,
    output wire [`NUM_IO-1:0] io_out,
    output wire [`NUM_IO-1:0] io_oeb
);
	assign io_oeb = '0;

    always_ff @(posedge clk) begin
        if (rst) begin
            io_out <= 32'h1;
        end
        else begin
            io_out <= io_out * 32'h3;
        end
    end
endmodule
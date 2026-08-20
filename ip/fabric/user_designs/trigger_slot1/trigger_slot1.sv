// SPDX-FileCopyrightText: © 2025 Leo Moser <leo.moser@pm.me>
// SPDX-License-Identifier: Apache-2.0

`default_nettype none

module top(
    input  wire        clk,
    input  wire [`NUM_IO-1:0] io_in,
    output wire [`NUM_IO-1:0] io_out,
    output wire [`NUM_IO-1:0] io_oeb
);
    
    // Boot from slot 1
    logic RESET;
    logic [1:0] counter;
    logic boot;
    logic [3:0] slot;
    
    always_ff @(posedge clk) begin
        if (RESET) begin
            boot <= 1'b0;
            counter <= '0;
            slot <= '0;
        end else begin
            boot <= 1'b0;
            if (counter < 3) begin
                counter <= counter + 1;
            end

            if (counter < 2) begin
                boot <= 1'b1;
            end

            if (counter == 1) begin
                slot <= 4'h1;
            end

            if (counter == 2) begin
                slot <= 4'h6;
            end
        end
    end


    WARMBOOT_wrapper WARMBOOT_wrapper (
        .SLOT   (slot),
        .BOOT   (boot),
        .RESET  (RESET)
    );
    
    assign io_out = '0;
	assign io_oeb = '0;

endmodule

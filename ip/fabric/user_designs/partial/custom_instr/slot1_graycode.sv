module slot1_graycode();
    // CLK
    logic clk;
    (* keep *) Global_Clock clk_i (.CLK(clk));

    // Slot IOs
    logic [31:0] io_i, io_oeb, io_o;
    (* keep *) slot1_wrapper wrapper (
        .rst_o     (rst),
        .io_o      (io_i),
        .io_i      (io_o),
    );

    // OBI periph
    logic        REQ;
    logic        WE;
    logic [ 3:0] BE;
    logic [23:0] ADDR;
    logic [31:0] WDATA;
    
    logic        GNT;
    logic        RVALID;
    logic [31:0] RDATA;

    OBI_PERIPHERAL_wrapper i_OBI_PERIPHERAL_wrapper (
        .REQ,
        .WE,
        .BE,
        .ADDR,
        .WDATA,
        
        .GNT,
        .RVALID,
        .RDATA,
    );

    logic [31:0] io_hold;

    assign GNT = 1'b1;

	always_ff @(posedge clk) begin
        RVALID = 1'b0;
		if (REQ) begin
            RVALID = 1'b1;
		    if (WE) begin
		        if (BE[0]) io_hold[ 7: 0] <= WDATA[7 : 0];
                if (BE[1]) io_hold[15: 8] <= WDATA[15: 8];
                if (BE[2]) io_hold[23:16] <= WDATA[23:16];
                if (BE[3]) io_hold[31:24] <= WDATA[31:24];
		    end else begin
		        RDATA <= graycode;
		    end
		end
    end

    logic [31:0] graycode;

    assign graycode = io_hold ^ {1'b0, io_hold[31:1]};
    assign io_o     = graycode;

endmodule
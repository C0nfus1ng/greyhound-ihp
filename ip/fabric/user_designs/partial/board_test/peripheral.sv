module peripheral();
    // CLK
    logic clk;
    (* keep *) Global_Clock clk_i (.CLK(clk));

    // RST
    logic rst;
    WARMBOOT_wrapper WARMBOOT_wrapper (
        .SLOT   (4'd0),
        .BOOT   (1'b0),
        .RESET  (rst)
    );

    logic        REQ;
    logic        WE;
    logic [3: 0] BE;
    logic [23:0] ADDR;
    logic [31:0] WDATA;
    
    logic        GNT;
    logic        RVALID;
    logic [31:0] RDATA;

    peripheral_wrapper i_peripheral_wrapper (
        .REQ,
        .WE,
        .BE,
        .ADDR,
        .WDATA,
        
        .GNT,
        .RVALID,
        .RDATA
    );

    logic [31:0] periph_reg;
    // Phys IOs
    logic [31:0] phys_io_i, phys_io_oeb, phys_io_o;
    (* keep *) io_wrapper io (
        .io_i     (phys_io_i),
        .io_oeb_i (phys_io_oeb),
        .io_o     (phys_io_o),
    );
    assign phys_io_oeb  = '0;
    assign phys_io_i    = periph_reg;
    assign GNT = 1'b1;

	always_ff @(posedge clk) begin
        if (rst) begin
            periph_reg <= '0;
        end
        else begin
            RVALID = 1'b0;
            if (REQ) begin
                RVALID = 1'b1;
                if (WE) begin
                    if (BE[0]) periph_reg[ 7: 0] <= WDATA[7 : 0];
                    if (BE[1]) periph_reg[15: 8] <= WDATA[15: 8];
                    if (BE[2]) periph_reg[23:16] <= WDATA[23:16];
                    if (BE[3]) periph_reg[31:24] <= WDATA[31:24];
                end else begin
                    RDATA <= periph_reg;
                end
            end
        end
    end
endmodule

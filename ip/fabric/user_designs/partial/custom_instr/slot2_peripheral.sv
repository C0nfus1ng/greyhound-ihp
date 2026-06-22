module slot2_peripheral ();
    // CLK
    logic clk;
    (* keep *) Global_Clock clk_i (.CLK(clk));

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

    // Slot IOs
    logic rst;
    slot2_wrapper wrapper(
        .rst_o ( rst           ),
        .io_i  ( regs[regs[0][1:0]] ),
    );

    logic [31:0] regs [4];

    assign GNT = 1'b1;

	always_ff @(posedge clk) begin
        if (rst) begin
            regs[0] <= '0;
            regs[1] <= '0;
        end
        else begin
            RVALID = 1'b0;
            if (REQ) begin
                RVALID = 1'b1;
                if (WE) begin
                    if (BE[0]) regs[ADDR[3:2]][ 7: 0] <= WDATA[7 : 0];
                    if (BE[1]) regs[ADDR[3:2]][15: 8] <= WDATA[15: 8];
                    if (BE[2]) regs[ADDR[3:2]][23:16] <= WDATA[23:16];
                    if (BE[3]) regs[ADDR[3:2]][31:24] <= WDATA[31:24];
                end else begin
                    RDATA <= regs[ADDR[3:2]];
                end
            end
        end
    end
endmodule

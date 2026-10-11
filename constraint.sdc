current_design $::env(DESIGN_NAME)
set_units -time ns

set clock_port __VIRTUAL_CLK__
if { [info exists ::env(CLOCK_PORT)] } {
    set port_count [llength $::env(CLOCK_PORT)]

    if { $port_count == "0" } {
        puts "\[WARNING] No CLOCK_PORT found. A dummy clock will be used."
    } elseif { $port_count != "1" } {
        puts "\[WARNING] Multi-clock files are not currently supported by the base SDC file. Only the first clock will be constrained."
    }

    if { $port_count > "0" } {
        set ::clock_port [lindex $::env(CLOCK_PORT) 0]
    }
}

if { $::env(CLOCK_PORT) == $::env(CLOCK_NET) } {
    set port_args [get_ports $clock_port]
} else {
    # This should actually use CLOCK_PIN?
    set port_args [get_pins [lindex $::env(CLOCK_NET) 0]]
}

puts "\[INFO] Using clock $clock_port…"
create_clock {*}$port_args -name $clock_port -period $::env(CLOCK_PERIOD)

set input_delay_value [expr $::env(CLOCK_PERIOD) * $::env(IO_DELAY_CONSTRAINT) / 100]
set output_delay_value [expr $::env(CLOCK_PERIOD) * $::env(IO_DELAY_CONSTRAINT) / 100]
puts "\[INFO] Setting output delay to: $output_delay_value"
puts "\[INFO] Setting input delay to: $input_delay_value"

set_max_fanout $::env(MAX_FANOUT_CONSTRAINT) [current_design]
if { [info exists ::env(MAX_TRANSITION_CONSTRAINT)] } {
    set_max_transition $::env(MAX_TRANSITION_CONSTRAINT) [current_design]
}
if { [info exists ::env(MAX_CAPACITANCE_CONSTRAINT)] } {
    set_max_capacitance $::env(MAX_CAPACITANCE_CONSTRAINT) [current_design]
}

set clocks [get_clocks $clock_port]

# Input-only pads
set clk_core_input_ports [get_ports { 
	io_reset_PAD 
	io_ser_rx_PAD
	io_fpga_mode_PAD
	io_fetch_enable_PAD
}] 

set_input_delay -min 0 -clock $clocks $clk_core_input_ports
set_input_delay -max $input_delay_value -clock $clocks $clk_core_input_ports

# Output-only pads
set clk_core_output_ports [get_ports { 
    io_flash_clk_PAD
    io_flash_cs_n_PAD
    io_psram_clk_PAD
    io_psram_cs_n_PAD
    io_ser_tx_PAD
    io_config_busy_PAD
    io_core_sleep_PAD
}] 

set_output_delay $output_delay_value -clock $clocks $clk_core_output_ports

# Bidirectional pads
set clk_core_inout_ports [get_ports { 
	io_flash_io_PAD[*]
	io_gpio_PAD[*]
}]

set_input_delay -min 0 -clock $clocks $clk_core_inout_ports
set_input_delay -max $input_delay_value -clock $clocks $clk_core_inout_ports
set_output_delay $output_delay_value -clock $clocks $clk_core_inout_ports

# Bidirectional SPI synchronized pads (Input is async until synchronizer)
set spi_jtag_inout_ports [get_ports { 
	io_fpga_sclk_PAD
	io_fpga_cs_n_PAD
	io_fpga_mosi_PAD
	io_fpga_miso_PAD
}]

set_output_delay $output_delay_value -clock $clocks $spi_jtag_inout_ports

# Output load
set cap_load [expr $::env(OUTPUT_CAP_LOAD) / 1000.0]
puts "\[INFO] Setting load to: $cap_load"
set_load $cap_load [all_outputs]

puts "\[INFO] Setting clock uncertainty to: $::env(CLOCK_UNCERTAINTY_CONSTRAINT)"
set_clock_uncertainty $::env(CLOCK_UNCERTAINTY_CONSTRAINT) $clocks

puts "\[INFO] Setting clock transition to: $::env(CLOCK_TRANSITION_CONSTRAINT)"
set_clock_transition $::env(CLOCK_TRANSITION_CONSTRAINT) $clocks

puts "\[INFO] Setting timing derate to: $::env(TIME_DERATING_CONSTRAINT)%"
set_timing_derate -early [expr 1-[expr $::env(TIME_DERATING_CONSTRAINT) / 100]]
set_timing_derate -late [expr 1+[expr $::env(TIME_DERATING_CONSTRAINT) / 100]]

if { [info exists ::env(OPENLANE_SDC_IDEAL_CLOCKS)] && $::env(OPENLANE_SDC_IDEAL_CLOCKS) } {
    unset_propagated_clock [all_clocks]
} else {
    set_propagated_clock [all_clocks]
}

# False paths

set_false_path -setup -hold -from [get_ports {io_reset_PAD}]

set_false_path -setup -hold -from [get_ports {io_fpga_mode_PAD}]
set_false_path -setup -hold -from [get_ports {io_fetch_enable_PAD}]

set_false_path -setup -hold -from [get_ports {io_ser_rx_PAD}]

set_false_path -setup -hold -through [get_ports {io_gpio_PAD[*]}]

# SPI/JTAG synchronizer interface
# Find first FF/D to constrain edge pin input with synchronizer without hold buffers
proc getFFCellfromQNet {qnet_name} {
    set qnet [get_nets -quiet $qnet_name]

    if {[llength $qnet] != 1} {
        foreach qn $qnet {
            puts "Q net: [get_name $qn]"
        }

        error "Multiple Q nets."
    }

    set qnet [lindex $qnet 0]
    set qpins [get_pins -of_objects $qnet]

    if {[llength $qpins] == 0} {
        error "No pins found on Q net: ${qnet_name}"
    }

    set ff_cell ""

    foreach qp $qpins {
        set cell [get_cells -of_objects $qp]

        if {[llength $cell] != 1} {
            continue
        }

        set c [lindex $cell 0]
        set pin_name [get_property $qp name]
        set ref_name [get_property $c ref_name]

        # Only Q pins can be the FF driver.
        if {$pin_name ne "Q"} {
            continue
        }

        if {$ref_name ne "sg13g2_dfrbpq_1"} {
            error "Q net is driven by non sg13g2_dfrbpq_1 cell."
        }

        set ff_cell $c
    }

    if {$ff_cell eq ""} {
        error "No FF for Q net found."
    }

    return $ff_cell
}

proc getCDCDPinFromQNet {port qnet_name} {
    puts "Find FF/D ${port} -> ${qnet_name}."

    set ff_cell [getFFCellfromQNet $qnet_name]
    if {[llength $ff_cell] == 0} {
        return {}
    }
    
    set ff_name [get_property $ff_cell name]
    set dpins [get_pins -of_objects $ff_cell -filter {name == D}]
    set dpin [lindex $dpins 0]
    set dnets [get_nets -of_objects $dpin]
    set dnet [lindex $dnets 0]
    set dnet_name [get_property $dnet full_name]
    puts "  CDC: ${port} -> ... -> ${dnet_name} -> ${ff_name}/D"

    return $dpin
}

set max_delay [expr {$::env(CLOCK_PERIOD) / 2.0}]
set min_delay [expr {-$::env(CLOCK_UNCERTAINTY_CONSTRAINT)}]

set select_dpin [getCDCDPinFromQNet {io_fpga_cs_n_PAD} {i_greyhound_ihp.controller_io_interface.select_d[0]}]
set_max_delay $max_delay -from [get_ports {io_fpga_cs_n_PAD}] -to $select_dpin -ignore_clock_latency
set_min_delay $min_delay -from [get_ports {io_fpga_cs_n_PAD}] -to $select_dpin -ignore_clock_latency

set c_clk_dpin [getCDCDPinFromQNet {io_fpga_sclk_PAD} {i_greyhound_ihp.controller_io_interface.c_clk_d[0]}]
set_max_delay $max_delay -from [get_ports {io_fpga_sclk_PAD}] -to $c_clk_dpin -ignore_clock_latency
set_min_delay $min_delay -from [get_ports {io_fpga_sclk_PAD}] -to $c_clk_dpin -ignore_clock_latency

set pico_dpin [getCDCDPinFromQNet {io_fpga_mosi_PAD} {i_greyhound_ihp.controller_io_interface.pico_d[0]}]
set_max_delay $max_delay -from [get_ports {io_fpga_mosi_PAD}] -to $pico_dpin -ignore_clock_latency
set_min_delay $min_delay -from [get_ports {io_fpga_mosi_PAD}] -to $pico_dpin -ignore_clock_latency

set shift_dpin [getCDCDPinFromQNet {io_fpga_miso_PAD} {i_greyhound_ihp.fabric_spi_controller/bitstream_data[0]}]
set_max_delay $max_delay -from [get_ports {io_fpga_miso_PAD}] -to $shift_dpin -ignore_clock_latency
set_min_delay $min_delay -from [get_ports {io_fpga_miso_PAD}] -to $shift_dpin -ignore_clock_latency


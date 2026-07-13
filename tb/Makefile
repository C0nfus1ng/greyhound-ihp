MAX_JOBS   		   ?= 4
TIMEOUT    		   ?= 43200 # 12h whole test timeout in s
MFILE_TIMEOUT      ?= 300 # 5m last file modification timeout in s
SIM_DELAY  		   ?= 30 # Sim parallel startup delay in s
SIM_RUNNER_FOLDER  ?= sim_build
SIM_RESULTS_FOLDER ?= results
PDK_ROOT		   ?= ../../../IHP-Open-PDK

ALL_TESTS ?= FMD_QNC_greyhound_ihp_dbg_tb=hello_world,bitstream_upload FMD_QNC_greyhound_ihp_partial_tb=partial_extension_cpu,partial_extension_jtag,partial_2slots_jtag,flash_image FMD_QNC_greyhound_ihp_tb=hello_world,fpga_all_ones,fpga_all_zeros,cou_trigger_foga,custom_instruction,fpga_peripheral,fpga_peripheral_sram,fpga_irq,fpga_blinky,jtag_bsr_none,jtag_cpu
GL = 0 # Gate level sim

# Test everything specified by ALL_TESTS. Start up to MAX_JOBS runs at the same time. Start them apart by 30s to avoid memory crunch while compiling. Run until everything is done. Then write the results in the results folder.
test-all:
	@for pair in $(ALL_TESTS); do \
		testbench=$$(printf '%s' "$$pair" | cut -d= -f1); \
		mkdir -p $(SIM_RUNNER_FOLDER)/$$testbench/FMD_QNC_greyhound_ihp_tb; \
		mkdir -p $(SIM_RUNNER_FOLDER)/$$testbench/greyhound_soc_dbg_tb/sim_build; \
		cp FMD_QNC_greyhound_ihp_tb/FMD_QNC_greyhound_ihp_slang.sv $(SIM_RUNNER_FOLDER)/$$testbench/FMD_QNC_greyhound_ihp_tb/; \
		cp greyhound_soc_dbg_tb/SimJTAG.sv $(SIM_RUNNER_FOLDER)/$$testbench/greyhound_soc_dbg_tb/SimJTAG.sv; \
		cp greyhound_soc_dbg_tb/sim_build/remote_bitbang.vpi $(SIM_RUNNER_FOLDER)/$$testbench/greyhound_soc_dbg_tb/sim_build/remote_bitbang.vpi; \
		cp *.v $(SIM_RUNNER_FOLDER)/$$testbench/; \
	done;

	@start_time=$$(date +%s); \
	pids=""; \
	running=0; \
	for pair in $(ALL_TESTS); do \
		testbench=$$(printf '%s' "$$pair" | cut -d= -f1); \
		tests=$$(printf '%s' "$$pair" | cut -d= -f2-); \
		for test in $$(printf '%s' "$$tests" | tr ',' '\n'); do \
			while [ $$running -ge $(MAX_JOBS) ]; do \
				new_pids=""; \
				running=0; \
				for pid in $$pids; do \
					if kill -0 $$pid 2>/dev/null; then \
						new_pids="$$new_pids $$pid"; \
						running=$$((running + 1)); \
					else \
						wait $$pid >/dev/null 2>&1 || true; \
					fi; \
				done; \
				pids="$$new_pids"; \
				if [ $$running -ge $(MAX_JOBS) ]; then \
					printf "."; \
					sleep $(SIM_DELAY); \
				fi; \
			done; \
			\
			( $(MAKE) -e TESTBENCH=$$testbench TEST=$$test test || true; ) & \
			pids="$$pids $$!"; \
			running=$$((running + 1)); \
			sleep $(SIM_DELAY); \
		done; \
	done; \
	\
	while [ $$running -gt 0 ]; do \
		new_pids=""; \
		running=0; \
		for pid in $$pids; do \
			if kill -0 $$pid 2>/dev/null; then \
				new_pids="$$new_pids $$pid"; \
				running=$$((running + 1)); \
			else \
				wait $$pid >/dev/null 2>&1 || true; \
			fi; \
		done; \
		pids="$$new_pids"; \
		if [ $$running -gt 0 ]; then \
			printf "."; \
			sleep $(SIM_DELAY); \
		fi; \
	done; \
	echo "All tests finished running. Took $$(($$(date +%s) - start_time))s."

	$(MAKE) result -e SIM_RESULTS_FOLDER=results_$$(date +"%d-%m-%Y_%H-%M-%S")
.phony: test-all

# Do a single test
test-single: TESTBENCH=FMD_QNC_greyhound_ihp_partial_tb
test-single: TEST=partial_extension_cpu
test-single:
	$(MAKE) test-all -e ALL_TESTS=$(TESTBENCH)=$(TEST)
.phony: test-single

# Copy the test into a tmp folder
copy-test:
	@mkdir -p $(SIM_RUNNER_FOLDER)/$(TESTBENCH)/$(TEST); \
	cp $(TESTBENCH)/*.py $(SIM_RUNNER_FOLDER)/$(TESTBENCH)/$(TEST)/ 2>/dev/null || true; \
	cp $(TESTBENCH)/*.v $(SIM_RUNNER_FOLDER)/$(TESTBENCH)/$(TEST)/ 2>/dev/null || true; \
	cp $(TESTBENCH)/*.sv $(SIM_RUNNER_FOLDER)/$(TESTBENCH)/$(TEST)/ 2>/dev/null || true; \
 	cp $(TESTBENCH)/*.cfg $(SIM_RUNNER_FOLDER)/$(TESTBENCH)/$(TEST)/ 2>/dev/null || true;
.phony: copy-test

# Replace all relative paths and mark the selected test to run.
replace-paths:
	@sed -i \
		-e "s/^enabled *=.*/enabled = $(TEST)/" \
		-e 's|\.\./\.\./|../../../../|g' \
		-e "s/\('dump_waveforms':[[:space:]]*\).*/\1False,/" \
		$(SIM_RUNNER_FOLDER)/$(TESTBENCH)/$(TEST)/$(TESTBENCH).py

	@sed -i \
		"/^$(TEST)[[:space:]]*=[[:space:]]*{/,/^}/{s/\('dump_waveforms':[[:space:]]*\).*/\1True,/}" \
		$(SIM_RUNNER_FOLDER)/$(TESTBENCH)/$(TEST)/$(TESTBENCH).py
.phony: replace-paths

# Run a test and check if it is stalled (Test stalled after not writing to the waveform file or if timeout is reached)
test: TESTBENCH=FMD_QNC_greyhound_ihp_partial_tb
test: TEST=partial_extension_cpu
test: copy-test replace-paths
test:
	@set -eu; \
	echo "Starting $(TESTBENCH).$(TEST)"; \
	cd "$(SIM_RUNNER_FOLDER)/$(TESTBENCH)/$(TEST)"; \
	GL=$(GL) setsid python3 "$(TESTBENCH).py" >stdout.log 2>stderr.log & \
	pid=$$!; \
	\
	start_time=$$(date +%s); \
	last_mtime=0; \
	last_change=$$(date +%s); \
	\
	if [ -f "sim_build/$(TESTBENCH).fst" ]; then \
		last_mtime=$$(stat -c %Y "sim_build/$(TESTBENCH).fst"); \
	fi; \
	\
	echo "EXIT=0" >testerr.log; \
	\
	while kill -0 -$$pid 2>/dev/null; do \
		now=$$(date +%s); \
		\
		if [ -f "sim_build/$(TESTBENCH).fst" ]; then \
			mtime=$$(stat -c %Y "sim_build/$(TESTBENCH).fst"); \
			if [ "$$mtime" != "$$last_mtime" ]; then \
				last_mtime=$$mtime; \
				last_change=$$now; \
			fi; \
		fi; \
		\
		if [ $$((now - last_change)) -ge $(MFILE_TIMEOUT) ] || [ $$((now - start_time)) -ge $(TIMEOUT) ]; then \
			kill -TERM -$$pid; \
			sleep 1; \
			\
			if [ $$((now - last_change)) -ge $(MFILE_TIMEOUT) ]; then \
				echo "No output file updates for $(MFILE_TIMEOUT) seconds. Sent SIGTERM\nEXIT=1" >testerr.log; \
			else \
				echo "Test (pid=$$pid) reached timeout of $(TIMEOUT) seconds. Sent SIGTERM\nEXIT=2" >testerr.log; \
			fi; \
			\
			deadline=$$((now + 60)); \
			while kill -0 -$$pid 2>/dev/null && [ $$(date +%s) -lt $$deadline ]; do \
				sleep 30; \
			done; \
			\
			if kill -0 -$$pid 2>/dev/null; then \
				kill -KILL -$$pid; \
				echo "Process did not exit after 60s. Sent SIGKILL\nEXIT=3" >>testerr.log; \
			fi; \
			break; \
		fi; \
		\
		sleep $$(($(MFILE_TIMEOUT)/2)); \
	done; \
	\
	wait; \
	echo "Finished $(TESTBENCH).$(TEST). Took $$(($$(date +%s) - start_time))s.";
.phony: test

# Build a nice result table with all sim results in a single folder
result:
	@mkdir -p $(SIM_RUNNER_FOLDER)/$(SIM_RESULTS_FOLDER); \
	printf '*****************************************************************************************************************************************************************************\n' >$(SIM_RUNNER_FOLDER)/$(SIM_RESULTS_FOLDER)/results.log; \
	printf "** " >>$(SIM_RUNNER_FOLDER)/$(SIM_RESULTS_FOLDER)/results.log; \
	printf "%-105.105s " "TEST" >>$(SIM_RUNNER_FOLDER)/$(SIM_RESULTS_FOLDER)/results.log; \
	printf "%-6.6s " "STATUS" >>$(SIM_RUNNER_FOLDER)/$(SIM_RESULTS_FOLDER)/results.log; \
	printf "%-13.13s " "SIM TIME (ns)" >>$(SIM_RUNNER_FOLDER)/$(SIM_RESULTS_FOLDER)/results.log; \
	printf "%-13.13s " "REAL TIME (s)" >>$(SIM_RUNNER_FOLDER)/$(SIM_RESULTS_FOLDER)/results.log; \
	printf "%-12.12s " "RATIO (ns/s)" >>$(SIM_RUNNER_FOLDER)/$(SIM_RESULTS_FOLDER)/results.log; \
	printf "%-13.13s " "RETURN VALUE" >>$(SIM_RUNNER_FOLDER)/$(SIM_RESULTS_FOLDER)/results.log; \
	printf "**\n" >>$(SIM_RUNNER_FOLDER)/$(SIM_RESULTS_FOLDER)/results.log; \
	printf '*****************************************************************************************************************************************************************************\n' >>$(SIM_RUNNER_FOLDER)/$(SIM_RESULTS_FOLDER)/results.log; \
	for pair in $(ALL_TESTS); do \
		testbench=$$(printf '%s' "$$pair" | cut -d= -f1); \
		tests=$$(printf '%s' "$$pair" | cut -d= -f2-); \
		for test in $$(printf '%s' "$$tests" | tr ',' '\n'); do \
			$(MAKE) -e TESTBENCH=$$testbench TEST=$$test parse-result copy-result; \
		done; \
	done; \
	awk 'NR >= 4 { \
		tests++; \
		status[$$3]++; \
		sim += $$4; \
		real += $$5; \
		ret[$$7]++; \
	} \
	END { \
		printf "*****************************************************************************************************************************************************************************\n"; \
		printf "** TESTS=%-3d PASS=%-3d FAIL=%-3d SKIP=%-3d SUCCESS=%-3d TIMEOUT=%-3d HUNGUP=%-3d KILLED=%-3d NOT_FOUND=%-3d UNKNOWN=%-3d     %-13.2f %-13.2f %-12.2f               **\n", \
				tests, status["PASS"]+0, status["FAIL"]+0, status["SKIP"]+0, ret["SUCCESS"]+0, ret["TIMEOUT"]+0, ret["HUNGUP"]+0, ret["KILLED"]+0, ret["NOT_FOUND"]+0, ret["UNKNOWN"]+0, sim, real, (real == 0) ? 0 : sim/real; \
	}' $(SIM_RUNNER_FOLDER)/$(SIM_RESULTS_FOLDER)/results.log >>$(SIM_RUNNER_FOLDER)/$(SIM_RESULTS_FOLDER)/results.log; \
	printf '*****************************************************************************************************************************************************************************\n' >>$(SIM_RUNNER_FOLDER)/$(SIM_RESULTS_FOLDER)/results.log;
.phony: result

# Write an result tile summary
parse-result: TESTBENCH=FMD_QNC_greyhound_ihp_partial_tb
parse-result: TEST=partial_extension_cpu
parse-result:
	@mkdir -p $(SIM_RUNNER_FOLDER)/$(SIM_RESULTS_FOLDER); \
	cd "$(SIM_RUNNER_FOLDER)/$(TESTBENCH)/$(TEST)"; \
	exit_code=$$(grep -o 'EXIT=[0-9]\+' testerr.log | tail -n1 | cut -d= -f2); \
	printf '** ' >>../../$(SIM_RESULTS_FOLDER)/results.log; \
	if [ "$$exit_code" = "0" ]; then \
		line=$$(tac stdout.log | grep -m1 '$(TESTBENCH)\.test_$(TEST)'); \
		if [ -n "$$line" ]; then \
			line_clean=$$(echo "$$line" | tr '*' ' '); \
			set -- $$line_clean; \
			printf "%-105.105s " "$$1" >>../../$(SIM_RESULTS_FOLDER)/results.log; \
			printf "%-6.6s " "$$2" >>../../$(SIM_RESULTS_FOLDER)/results.log; \
			printf "%-13.13s " "$$3" >>../../$(SIM_RESULTS_FOLDER)/results.log; \
			printf "%-13.13s " "$$4" >>../../$(SIM_RESULTS_FOLDER)/results.log; \
			printf "%-12.12s " "$$5" >>../../$(SIM_RESULTS_FOLDER)/results.log; \
			printf "%-13.13s " "SUCCESS (0)" >>../../$(SIM_RESULTS_FOLDER)/results.log; \
		else \
			printf "%-105.105s " "$(TESTBENCH).test_$(TEST)" >>../../$(SIM_RESULTS_FOLDER)/results.log; \
			printf "%-6.6s " "SKIP" >>../../$(SIM_RESULTS_FOLDER)/results.log; \
			printf "%-13.13s " "-.--" >>../../$(SIM_RESULTS_FOLDER)/results.log; \
			printf "%-13.13s " "-.--" >>../../$(SIM_RESULTS_FOLDER)/results.log; \
			printf "%-12.12s " "-.--" >>../../$(SIM_RESULTS_FOLDER)/results.log; \
			printf "%-13.13s " "NOT_FOUND (4)" >>../../$(SIM_RESULTS_FOLDER)/results.log; \
		fi; \
	else \
		printf "%-105.105s " "$(TESTBENCH).test_$(TEST)" >>../../$(SIM_RESULTS_FOLDER)/results.log; \
		printf "%-6.6s " "FAIL" >>../../$(SIM_RESULTS_FOLDER)/results.log; \
		printf "%-13.13s " "-.--" >>../../$(SIM_RESULTS_FOLDER)/results.log; \
		printf "%-13.13s " "-.--" >>../../$(SIM_RESULTS_FOLDER)/results.log; \
		printf "%-12.12s " "-.--" >>../../$(SIM_RESULTS_FOLDER)/results.log; \
		if [ "$$exit_code" = "1" ]; then \
			printf "%-13.13s " "HUNGUP (1)" >>../../$(SIM_RESULTS_FOLDER)/results.log; \
		elif [ "$$exit_code" = "2" ]; then \
			printf "%-13.13s " "TIMEOUT (2)" >>../../$(SIM_RESULTS_FOLDER)/results.log; \
		elif [ "$$exit_code" = "3" ]; then \
			printf "%-13.13s " "KILLED (3)" >>../../$(SIM_RESULTS_FOLDER)/results.log; \
		else \
			printf "%-13.13s " "UNKNOWN ($$exit_code)" >>../../$(SIM_RESULTS_FOLDER)/results.log; \
		fi; \
	fi; \
	printf '**\n' >>../../$(SIM_RESULTS_FOLDER)/results.log;
.phony: parse-result

# Copy a result
copy-result: TESTBENCH=FMD_QNC_greyhound_ihp_partial_tb
copy-result: TEST=partial_extension_cpu
copy-result:
	@mkdir -p $(SIM_RUNNER_FOLDER)/$(SIM_RESULTS_FOLDER)/$(TESTBENCH)/$(TEST); \
	cp "$(SIM_RUNNER_FOLDER)/$(TESTBENCH)/$(TEST)/"*.log "$(SIM_RUNNER_FOLDER)/$(SIM_RESULTS_FOLDER)/$(TESTBENCH)/$(TEST)/"; \
	cp "$(SIM_RUNNER_FOLDER)/$(TESTBENCH)/$(TEST)/sim_build/$(TESTBENCH).fst" "$(SIM_RUNNER_FOLDER)/$(SIM_RESULTS_FOLDER)/$(TESTBENCH)/$(TEST)/sim_waves.fst";
.phony: copy-result

# Delete all generated sim files
clean-all:
	for pair in $(ALL_TESTS); do \
		folder=$$(printf '%s' "$$pair" | cut -d= -f1); \
		$(MAKE) clean -e TESTBENCH=$$folder; \
	done;
.phony: clean-all

# Delete a single test
clean: TESTBENCH=FMD_QNC_greyhound_ihp_partial_tb
clean:
	rm -rf $(SIM_RUNNER_FOLDER)/$(TESTBENCH)
.phony: clean

MICROBIT_BIN = ./build/bbc-microbit-classic-gcc/src/firmware/bluescan-advsniff-combined.hex
MICROBIT_PATH = /media/${USER}/MICROBIT

.PHONY: all
all:
	@yotta build


.PHONY: flash
flash:
	@yotta build

	@if [ -d $(MICROBIT_PATH) ]; then \
		cp $(MICROBIT_BIN) $(MICROBIT_PATH); \
	fi
	
	@if [ -d $(MICROBIT_PATH)1 ]; then \
		cp $(MICROBIT_BIN) $(MICROBIT_PATH)1; \
	fi
	
	@if [ -d $(MICROBIT_PATH)2 ]; then \
		cp $(MICROBIT_BIN) $(MICROBIT_PATH)2; \
	fi


.PHONY: clean
clean:
	@yotta clean


.PHONY: microbit-purge
purge:
	-@yotta clean
	-@rm -r yotta_modules
	-@rm -r yotta_targets

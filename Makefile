include /home/x/OneDrive/Projects/makefile-common/src/Makefile.twine
include /home/x/OneDrive/Projects/makefile-common/src/Makefile.python
include /home/x/OneDrive/Projects/makefile-common/src/Makefile.nethunter


$(info PROJECT_NAME: $(PROJECT_NAME))
$(info machine: $(MACHINE))
$(info INSTALL_REQUIRED_PY_PKGS: $(INSTALL_REQUIRED_PY_PKGS))


MICROBIT_BIN = ./build/bbc-microbit-classic-gcc/src/firmware/bluescan-advsniff-combined.hex
MICROBIT_PATH = /media/${USER}/MICROBIT


.PHONY: build
build:
	$(call python-build)


.PHONY: install
install:
	$(call python-install)


.PHONY: flash
flash:
	@yotta build bluescan-advsniff

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
	$(call python-clean)
	-@yotta clean


.PHONY: microbit-purge
microbit-purge:
	-@yotta clean
	-@rm -r yotta_modules
	-@rm -r yotta_targets


.PHONY: release
release:
	$(call twine-release)


.PHONY: push
push:
	$(call push-to-nethunter)
	@scp dist/*.whl Raspberry-Pi-4-via-Local-Ethernet:~/Desktop/temp

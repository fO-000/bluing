
include /home/x/OneDrive/Projects/makefile-common/src/Makefile.twine
include /home/x/OneDrive/Projects/makefile-common/src/Makefile.python
include /home/x/OneDrive/Projects/makefile-common/src/Makefile.nethunter
include ./plugins/Makefile

$(info PROJECT_NAME: $(PROJECT_NAME))
$(info MACHINE: $(MACHINE))
$(info DEPENDENCY_PY_PKGS: $(DEPENDENCY_PY_PKGS))
$(info )

.DEFAULT_GOAL := build
PKG_NAME := $(PY_PKG_NAME)
MICROBIT_BIN = ./build/bbc-microbit-classic-gcc/src/firmware/bluing-advsniff-combined.hex
MICROBIT_PATH = /media/${USER}/MICROBIT


.PHONY: build
build:
	$(call python-build)


.PHONY: update-oui
	wget https://standards-oui.ieee.org/oui/oui.txt -O src/bluing/res/oui.txt


.PHONY: install
install:
	$(call python-install)


.PHONY: flash
flash:
	@yotta build bluing-advsniff

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


.PHONY: push-to-ubuntu-server-vm
push-to-ubuntu-server-vm:
	scp dist/$(PKG_NAME)-*-py3-none-any.whl Ubuntu-Server-VM:~/Downloads/

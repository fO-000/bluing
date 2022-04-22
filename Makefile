$(info machine: $(shell uname -m))

PROJECT_NAME := $(shell basename `pwd`)
MICROBIT_BIN = ./build/bbc-microbit-classic-gcc/src/firmware/bluescan-advsniff-combined.hex
MICROBIT_PATH = /media/${USER}/MICROBIT

TWINE_PROXY := HTTPS_PROXY=http://localhost:7890


.PHONY: build
build:
	@pip3 install -U xpycommon pyclui bthci btsmp btatt btgatt

    # @pyarmor obfuscate --recursive \
    #                    --output dist/obfuscated/$(PROJECT_NAME) \
    #                    src/$(PROJECT_NAME)/__init__.py
	@python3 -m build --no-isolation


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
	-@rm -r dist/* src/$(PROJECT_NAME)/__pycache__ src/*.egg-info
	-@yotta clean


.PHONY: microbit-purge
microbit-purge:
	-@yotta clean
	-@rm -r yotta_modules
	-@rm -r yotta_targets


.PHONY: release
release:
	$(TWINE_PROXY) twine upload dist/*.whl dist/*.tar.gz

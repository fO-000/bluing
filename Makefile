PROJECT_NAME := bluescan
MICROBIT_BIN = ./build/bbc-microbit-classic-gcc/src/firmware/bluescan-advsniff-combined.hex
MICROBIT_PATH = /media/${USER}/MICROBIT

.PHONY: build
build:
	# @pyarmor obfuscate --recursive \
    #                    --output dist/obfuscated/$(PROJECT_NAME) \
    #                    src/$(PROJECT_NAME)/__init__.py
	@python3 -m build --no-isolation

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
	-@rm -r dist/* src/$(PROJECT_NAME)/__pycache__ src/*.egg-info
	-@yotta clean


.PHONY: microbit-purge
purge:
	-@yotta clean
	-@rm -r yotta_modules
	-@rm -r yotta_targets

.PHONY: release
release:
	twine upload dist/*.whl dist/*.tar.gz

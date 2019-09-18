INSTALL_PATH = /bin
PROMPT_PATH = /etc/bash_completion.d
SRC = ./src
MAIN_SCRIPT = $(SRC)/bluescan.py
# BLUEPY_PATH = /usr/local/lib/python3.7/dist-packages/bluepy

.PHONY: all
all:
	-@echo BLUEPY_PATH = $(BLUEPY_PATH)
	-pyinstaller -F --distpath ./bin --add-data $(BLUEPY_PATH):bluepy $(MAIN_SCRIPT)
	-@rm -rf build bluescan.spec


.PHONY: clean
clean:
	-@rm -rf bin/
	-@rm -rf $(SRC)/__pycache__
	-@rm -rf build dist bluescan.spec


.PHONY: install
install:
	cp bin/bluescan $(INSTALL_PATH)/
	-cp $(SRC)/bluescan_prompt.bash $(PROMPT_PATH)/


.PHONY: uninstall
uninstall:
	-@rm -f $(PROMPT_PATH)/bluescan_prompt.bash
	-@rm -f $(INSTALL_PATH)/bluescan

# Variables
SRC_FILES := $(wildcard *.py)
INSTALL_DIR := /usr/bin

# Default target
all: $(BINARIES)

# Rule to compile Python files to binaries

# Install binaries to /usr/bin
install: $(BINARIES)
	@echo "Installing to $(INSTALL_DIR)"
	@mkdir -p $(INSTALL_DIR)  # Ensure the installation directory exists
	@for file in $(SRC_FILES); do \
		filename=$$(basename $$file .py); \
		cp $$file $(INSTALL_DIR)/$$filename; \
	done


# Clean up build and dist directories
clean:
	rm -rf dist build __pycache__ *.spec

# Phony targets
.PHONY: all install clean

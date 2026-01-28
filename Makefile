# Professional RISC-V UART Bootloader - Makefile

# Toolchain
CROSS_COMPILE ?= riscv64-unknown-elf-
CC = $(CROSS_COMPILE)gcc
OBJCOPY = $(CROSS_COMPILE)objcopy
OBJDUMP = $(CROSS_COMPILE)objdump

# Directories
SRC_DIR = src
INC_DIR = include
LNK_DIR = linker
BRD_DIR = boards/qemu_virt
OBJ_DIR = obj

# Target
TARGET = bootloader.elf
BINARY = bootloader.bin

# Compilation Flags
# RV32IM, no standard library, freestanding
CFLAGS = -march=rv32im_zicsr -mabi=ilp32 -ffreestanding -nostdlib -O2 -Wall -Wextra -I$(INC_DIR) -I$(BRD_DIR)
LDFLAGS = -T $(LNK_DIR)/memory.ld -nostdlib -nostartfiles

# Source Files
SRCS = $(SRC_DIR)/start.S \
       $(SRC_DIR)/main.c \
       $(SRC_DIR)/uart.c \
       $(SRC_DIR)/flash.c \
       $(SRC_DIR)/crc32.c \
       $(BRD_DIR)/platform.c

# Object Files
OBJS = $(patsubst %.c, $(OBJ_DIR)/%.o, $(filter %.c, $(SRCS)))
OBJS += $(patsubst %.S, $(OBJ_DIR)/%.o, $(filter %.S, $(SRCS)))

# Rules
.PHONY: all clean qemu

all: $(BINARY)

$(BINARY): $(TARGET)
	$(OBJCOPY) -O binary $< $@

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) $(OBJS) -o $@ $(LDFLAGS)
	@echo "Build complete: $@"

$(OBJ_DIR)/%.o: %.c
	@mkdir -p $(dir $@)
	$(CC) $(CFLAGS) -c $< -o $@

$(OBJ_DIR)/%.o: %.S
	@mkdir -p $(dir $@)
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -rf $(OBJ_DIR) $(TARGET) $(BINARY)

# Helper to run in QEMU (bare-metal virt machine)
qemu: $(TARGET)
	qemu-system-riscv32 -M virt -display none -serial stdio -bios none -kernel $(TARGET)

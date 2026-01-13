# FaultBanana
Research Prototype for detecting fault injection vulnerabilities in binaries

## Setup

Tested on Python 3.8 for Debian/Ubuntu.

```bash
pip install -Ur requirements.txt
```

## Usage

```bash
python banana.py
```

Modify Scripts\Banana\architecture_support.py accordingly

```bash
python compile_binary.py
python find_section.py
```

## Case Studies

- Simple PIN Verification (pin-verify.c)

## Other Dependencies

```
$sudo apt install gcc
$sudo apt install gcc-multilib
$sudo apt install libc6-dev-armhf-cross gcc-arm-linux-gnueabihf
$sudo apt install libc6-dev-arm64-cross gcc-aarch64-linux-gnu 
$sudo apt install libc6-armel-cross gcc-arm-none-eabi
$sudo apt install gcc-riscv64-linux-gnu libc6-dev-riscv64-cross
$sudo apt install qemu-user-static
$sudo apt install qemu-user
$sudo apt install qemu-system
```

Risc-V 32-bit gcc

https://github.com/riscv-collab/riscv-gnu-toolchain/releases/tag/2024.12.16

## Authors

- [@christopher-simon-liu](https://github.com/christopher-simon-liu)

moo

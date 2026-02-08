#!/usr/bin/env python3
"""RISC-V Bootloader UART Protocol Test & Validation"""
import subprocess
import time
import sys
import threading
import queue
import os
import shutil
from binascii import crc32

# Constants
FIRMWARE_SIZE = 1024
PROGRESS_BAR_DELAY = 0.2  # Show progress bar only after 0.2 secs
PROGRESS_BAR_MIN_DURATION = 0.5  # Only if it will take more than 2 secs

# ANSI colors
class C:
    GREEN, RED, CYAN, BOLD, END = '\033[92m', '\033[91m', '\033[96m', '\033[1m', '\033[0m'

def step(num, total, msg):
    print(f"{C.BOLD}[{num}/{total}]{C.END} {C.CYAN}{msg}{C.END}")

def ok(msg):
    print(f"  {C.GREEN}✓{C.END}  {msg}")

def fail(msg):
    print(f"  {C.RED}✗{C.END}  {msg}")

# Progress tracking globals
_progress_start_time = None
_progress_shown = False

def progress(curr, total, byte_delay=0.0003):
    global _progress_start_time, _progress_shown
    
    # Initialize on first call
    if curr == 0 or _progress_start_time is None:
        _progress_start_time = time.time()
        _progress_shown = False
    
    estimated_total_time = total * byte_delay
    elapsed = time.time() - _progress_start_time
    
    # Only show if estimated time > PROGRESS_BAR_MIN_DURATION and elapsed > PROGRESS_BAR_DELAY
    if estimated_total_time > PROGRESS_BAR_MIN_DURATION and elapsed > PROGRESS_BAR_DELAY:
        _progress_shown = True
        width = 30
        done = int(width * curr / total)
        bar = '█' * done + '░' * (width - done)
        pct = 100 * curr / total
        print(f"\r  [{bar}] {pct:5.1f}%", end='', flush=True)
    
    if curr >= total:
        if _progress_shown:
            print("\r" + " " * 50 + "\r", end="")
        _progress_start_time = None
        _progress_shown = False

def animated_wait(duration):
    """Show progress bar while waiting"""
    start = time.time()
    show_progress = duration > PROGRESS_BAR_MIN_DURATION
    progress_started = False
    
    while time.time() - start < duration:
        elapsed = time.time() - start
        
        # Only show progress if duration > PROGRESS_BAR_MIN_DURATION and elapsed > PROGRESS_BAR_DELAY
        if show_progress and elapsed > PROGRESS_BAR_DELAY:
            progress_started = True
            pct = min(100, int(100 * elapsed / duration))
            bar_width = 30
            filled = int(bar_width * elapsed / duration)
            bar = '█' * filled + '░' * (bar_width - filled)
            print(f"\r  [{bar}] {pct:5.1f}%", end='', flush=True)
        
        time.sleep(0.05)
    
    if progress_started:
        print("\r" + " " * 50 + "\r", end="")

def find_qemu():
    """Find QEMU executable"""
    exe = "qemu-system-riscv32" + (".exe" if sys.platform.startswith('win') else "")
    qemu = shutil.which(exe)
    if qemu:
        return qemu
    if sys.platform.startswith('win'):
        for path in [r"C:\Program Files\qemu", r"C:\Program Files (x86)\qemu", r"C:\qemu"]:
            full = f"{path}\\{exe}"
            if os.path.exists(full):
                return full
    return None

def kill_all_qemu():
    """Kill any running QEMU instances"""
    try:
        cmd = ['taskkill', '/F', '/IM', 'qemu-system-riscv32.exe'] if sys.platform.startswith('win') else ['pkill', '-9', 'qemu-system-riscv32']
        subprocess.run(cmd, capture_output=True)
    except:
        pass

def bg_reader(proc, q):
    """Background thread to read QEMU stdout"""
    try:
        while True:
            byte = proc.stdout.read(1)
            if not byte:
                break
            q.put(byte)
    finally:
        q.put(None)

# Global queue and reader thread
_reader_queue = None
_reader_thread = None

def init_reader(proc):
    """Start background stdout reader"""
    global _reader_queue, _reader_thread
    _reader_queue = queue.Queue()
    _reader_thread = threading.Thread(target=bg_reader, args=(proc, _reader_queue), daemon=True)
    _reader_thread.start()
    time.sleep(0.03)

def wait_for(proc, pattern, timeout=5.0):
    """Wait for pattern in bootloader output"""
    global _reader_queue
    buf, end, pat = b'', time.time() + timeout, pattern.encode()
    
    while time.time() < end:
        try:
            b = _reader_queue.get(timeout=0.05)
            if b is None:
                return False, buf.decode('ascii', errors='ignore')
            buf += b
            if pat in buf:
                return True, buf.decode('ascii', errors='ignore')
        except queue.Empty:
            continue
    return False, buf.decode('ascii', errors='ignore')

def send(proc, data):
    """Send data to bootloader"""
    data = data.encode() if isinstance(data, str) else data
    proc.stdin.write(data)
    proc.stdin.flush()
    return True

def make_firmware(size=FIRMWARE_SIZE):
    """Generate test firmware with CRC"""
    app = (bytes(range(256)) * (size // 256 + 1))[:size]
    return app, crc32(app) & 0xFFFFFFFF

def test():
    kill_all_qemu()
    
    print(f"\n{C.BOLD}RISC-V Bootloader Validation Test{C.END}\n")
    
    proc = None
    try:
        step(1, 7, "Starting QEMU bootloader")
        qemu_exe = find_qemu()
        if not qemu_exe:
            fail("QEMU not found. Install QEMU or add to PATH.")
            return False
        
        cmd = [qemu_exe, "-M", "virt", "-display", "none", "-serial", "stdio",
               "-bios", "none", "-kernel", "bootloader.elf"]
        
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, bufsize=0)
        time.sleep(0.2)
        ok("QEMU running")
        init_reader(proc)
        
        step(2, 7, "Waiting for bootloader")
        success, resp = wait_for(proc, "BOOT?", timeout=3)
        if not success:
            fail(f"No BOOT? prompt (got: {repr(resp[:50])})")
            return False
        ok("Bootloader ready")
        
        step(3, 7, "Entering update mode")
        send(proc, 'u')
        time.sleep(0.03)
        success, resp = wait_for(proc, "OK", timeout=3)
        if not success:
            fail(f"Update mode failed")
            return False
        ok("Update mode active")
        
        step(4, 7, "Generating test application")
        firmware, fw_crc = make_firmware()
        ok("Test application ready")
        
        step(5, 7, "Uploading firmware")
        cmd = f"SEND {len(firmware)}\n"
        for c in cmd:
            send(proc, c)
            time.sleep(0.001)
        time.sleep(0.03)
        success, resp = wait_for(proc, "READY", timeout=5)
        if not success:
            fail(f"Flash not ready")
            return False
        ok("Flash erased, ready for data")
        
        for i, byte in enumerate(firmware):
            if not send(proc, bytes([byte])):
                fail(f"Send failed at byte {i}")
                return False
            if i % 40 == 0:
                progress(i, len(firmware))
            time.sleep(0.0003)
        progress(len(firmware), len(firmware))
        ok(f"Uploaded {len(firmware)} bytes")
        
        proc.stdin.write(b'\x00' * 32)
        proc.stdin.flush()
        
        step(6, 7, "Validating CRC")
        wait_duration = max(3.5, len(firmware) / 160.0)
        animated_wait(wait_duration)
        success, resp = wait_for(proc, "CRC?", timeout=20)
        if not success:
            fail("CRC check timeout")
            return False
        
        success, resp = wait_for(proc, "OK", timeout=3)
        if not success:
            fail(f"CRC validation failed")
            return False
        ok("CRC validation passed")
        
        step(7, 7, "Finalizing")
        success, resp = wait_for(proc, "REBOOT", timeout=2)
        if success:
            ok("Reboot initiated")
        
        proc.terminate()
        print(f"\n{C.GREEN}{C.BOLD}✓ ALL TESTS PASSED{C.END}\n")
        return True
        
    except Exception as e:
        fail(f"Error: {e}")
        return False
    finally:
        if proc:
            try:
                proc.terminate()
                proc.wait(timeout=1)
            except:
                proc.kill()

if __name__ == '__main__':
    try:
        success = test()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted")
        sys.exit(1)

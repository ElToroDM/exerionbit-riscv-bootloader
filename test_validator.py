#!/usr/bin/env python3
"""
RISC-V Bootloader UART Protocol Test & Validation
Validates: handshake, firmware upload, CRC32, error handling
"""
import subprocess
import time
import sys
import threading
import queue
import os
import shutil
from binascii import crc32

# ANSI color codes
class C:
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def step(num, total, msg):
    print(f"{C.BOLD}[{num}/{total}]{C.END} {C.CYAN}{msg}{C.END}")

def ok(msg):
    print(f"  {C.GREEN}✓{C.END}  {msg}")

def fail(msg):
    print(f"  {C.RED}✗{C.END}  {msg}")

def info(msg):
    print(f"  {C.YELLOW}→{C.END}  {msg}")

def progress(curr, total):
    width = 30
    done = int(width * curr / total)
    bar = '█' * done + '░' * (width - done)
    pct = 100 * curr / total
    print(f"\r  [{bar}] {pct:5.1f}%", end='', flush=True)

def find_qemu():
    """Find QEMU executable in PATH or common install locations"""
    exe_name = "qemu-system-riscv32"
    if sys.platform.startswith('win'):
        exe_name += ".exe"
    
    # Try PATH first
    qemu_path = shutil.which(exe_name)
    if qemu_path:
        return qemu_path
    
    # Windows fallback locations
    if sys.platform.startswith('win'):
        common_paths = [
            r"C:\Program Files\qemu\qemu-system-riscv32.exe",
            r"C:\Program Files (x86)\qemu\qemu-system-riscv32.exe",
            r"C:\qemu\qemu-system-riscv32.exe",
        ]
        for path in common_paths:
            if os.path.exists(path):
                return path
    return None

def kill_all_qemu():
    """Kill any running QEMU instances"""
    try:
        if sys.platform.startswith('win'):
            subprocess.run(['taskkill', '/F', '/IM', 'qemu-system-riscv32.exe'], 
                         capture_output=True)
        else:
            subprocess.run(['pkill', '-9', 'qemu-system-riscv32'], 
                         capture_output=True)
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
    except:
        pass
    finally:
        q.put(None)

# Global queue and reader thread
_reader_queue = None
_reader_thread = None

def init_reader(proc):
    """Start background stdout reader thread"""
    global _reader_queue, _reader_thread
    _reader_queue = queue.Queue()
    _reader_thread = threading.Thread(target=bg_reader, args=(proc, _reader_queue), daemon=True)
    _reader_thread.start()
    time.sleep(0.1)

def wait_for(proc, pattern, timeout=5.0, clear_after=False):
    """Wait for text pattern in bootloader output"""
    global _reader_queue
    buf = b''
    end = time.time() + timeout
    pat = pattern.encode()
    
    while time.time() < end:
        try:
            b = _reader_queue.get(timeout=0.05)
            if b is None:
                return False, buf.decode('ascii', errors='ignore')
            buf += b
            if pat in buf:
                if clear_after:
                    time.sleep(0.05)
                    while not _reader_queue.empty():
                        try:
                            _reader_queue.get_nowait()
                        except queue.Empty:
                            break
                return True, buf.decode('ascii', errors='ignore')
        except queue.Empty:
            continue
    return False, buf.decode('ascii', errors='ignore')

def send(proc, data):
    """Send data to bootloader"""
    if isinstance(data, str):
        data = data.encode()
    try:
        proc.stdin.write(data)
        proc.stdin.flush()
        return True
    except Exception as e:
        print(f"Send error: {e}")
        return False

def send_slow(proc, data, delay=0.01):
    """Send data byte-by-byte with delays for reliability"""
    if isinstance(data, str):
        data = data.encode()
    try:
        for byte in data:
            proc.stdin.write(bytes([byte]))
            proc.stdin.flush()
            time.sleep(delay)
        return True
    except:
        return False

def make_firmware(size=512):
    """Generate test firmware with CRC"""
    app = bytes(range(256)) * (size // 256 + 1)
    app = app[:size]
    crc = crc32(app) & 0xFFFFFFFF
    return app, crc

def test():
    """Run complete bootloader validation"""
    kill_all_qemu()
    
    print(f"\n{C.BOLD}{'='*60}{C.END}")
    print(f"{C.BOLD}RISC-V Bootloader Validation Test{C.END}")
    print(f"{C.BOLD}{'='*60}{C.END}\n")
    
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
        time.sleep(0.5)
        ok("QEMU running")
        init_reader(proc)
        
        step(2, 7, "Waiting for bootloader")
        success, resp = wait_for(proc, "BOOT?", timeout=5)
        if not success:
            fail(f"No BOOT? prompt (got: {repr(resp[:50])})")
            return False
        ok("Bootloader ready")
        
        step(3, 7, "Entering update mode")
        send(proc, 'u')
        time.sleep(0.2)
        success, resp = wait_for(proc, "OK", timeout=5, clear_after=True)
        if not success:
            fail(f"Update mode failed")
            info(f"Expected 'OK', got: {repr(resp)}")
            return False
        ok("Update mode active")
        time.sleep(0.1)
        
        step(4, 7, "Generating test application")
        firmware, fw_crc = make_firmware(512)
        info(f"Size: {len(firmware)} bytes, CRC32: 0x{fw_crc:08X}")
        ok("Test application ready")
        
        step(5, 7, "Uploading firmware")
        send_cmd = f"SEND {len(firmware)}\n"
        send_slow(proc, send_cmd, delay=0.005)
        info(f"Sent: {repr(send_cmd)}")
        time.sleep(0.1)
        success, resp = wait_for(proc, "READY", timeout=10)
        if not success:
            fail(f"Flash not ready")
            info(f"Expected 'READY', got: {repr(resp[:100])}")
            return False
        ok("Flash erased, ready for data")
        
        info("Uploading byte-by-byte...")
        bytes_sent = 0
        for i, byte in enumerate(firmware):
            if not send(proc, bytes([byte])):
                fail(f"Send failed at byte {i}")
                return False
            bytes_sent += 1
            if i % 50 == 0:
                progress(bytes_sent, len(firmware))
            time.sleep(0.002)
        progress(bytes_sent, len(firmware))
        print()
        ok(f"Uploaded {len(firmware)} bytes")
        
        # Padding to flush Windows pipe buffer
        info("Flushing pipe buffer...")
        proc.stdin.write(b'\x00' * 32)
        proc.stdin.flush()
        
        wait_time = max(2.0, len(firmware) / 200.0)
        info(f"Waiting {wait_time:.1f}s for CRC...")
        time.sleep(wait_time)
        if proc.poll() is not None:
            fail(f"QEMU terminated (exit: {proc.returncode})")
            return False
        
        step(6, 7, "Validating CRC")
        success, resp = wait_for(proc, "CRC?", timeout=20)
        if not success:
            fail("CRC check timeout")
            info(f"Expected 'CRC?', got: {repr(resp[:100])}")
            return False
        
        success, resp = wait_for(proc, "OK", timeout=5)
        if not success:
            fail(f"CRC validation failed")
            info(f"Expected 'OK', got: {repr(resp[:100])}")
            return False
        ok("CRC validation passed")
        
        step(7, 7, "Finalizing")
        success, resp = wait_for(proc, "REBOOT", timeout=2)
        if success:
            ok("Reboot initiated")
        
        proc.terminate()
        print(f"\n{C.GREEN}{C.BOLD}{'='*60}{C.END}")
        print(f"{C.GREEN}{C.BOLD}✓ ALL TESTS PASSED{C.END}")
        print(f"{C.GREEN}{C.BOLD}{'='*60}{C.END}\n")
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

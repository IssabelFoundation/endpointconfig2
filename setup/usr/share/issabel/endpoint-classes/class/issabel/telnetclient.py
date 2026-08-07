"""Minimal Telnet client replacing stdlib telnetlib.

Provides a compatible subset of telnetlib.Telnet used by endpoint vendor
classes: open, read_until, expect, write, close, get_socket.
Handles IAC negotiation and accepts both str and bytes.
"""
import re
import socket
import time

# Telnet protocol constants
IAC  = bytes([255])  # Interpret As Command
DONT = bytes([254])
DO   = bytes([253])
WONT = bytes([252])
WILL = bytes([251])
SB   = bytes([250])
SE   = bytes([240])
NOP  = bytes([241])


class Telnet:
    def __init__(self):
        self._sock = None
        self._buf = b''

    def open(self, host, port=23, timeout=10):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.settimeout(timeout)
        self._sock.connect((host, port))
        self._buf = b''

    def get_socket(self):
        return self._sock

    def write(self, data):
        if isinstance(data, str):
            data = data.encode('latin-1', errors='replace')
        self._sock.sendall(data)

    def close(self):
        if self._sock:
            try:
                self._sock.close()
            except Exception:
                pass
            self._sock = None

    def read_until(self, expected, timeout=30):
        if isinstance(expected, str):
            expected = expected.encode('latin-1')
        deadline = time.time() + timeout
        while True:
            idx = self._buf.find(expected)
            if idx >= 0:
                result = self._buf[:idx + len(expected)]
                self._buf = self._buf[idx + len(expected):]
                return self._decode(result)
            remaining = deadline - time.time()
            if remaining <= 0:
                result = self._buf
                self._buf = b''
                return self._decode(result)
            self._fill(timeout=max(0.1, remaining))

    def expect(self, list, timeout=30):
        if isinstance(list, (list, tuple)):
            compiled = [re.compile(p) if not isinstance(p, re.Pattern) else p
                        for p in list]
        else:
            compiled = [re.compile(list)]
        deadline = time.time() + timeout
        cumulative = b''
        while True:
            for i, pattern in enumerate(compiled):
                m = pattern.search(self._decode(self._buf))
                if m:
                    end = m.end()
                    consumed = self._encode(self._buf)[:end]
                    result_buf = cumulative + consumed
                    self._buf = self._buf[end:]
                    return (i, m, self._decode(result_buf))
            remaining = deadline - time.time()
            if remaining <= 0:
                return (-1, None, self._decode(cumulative + self._buf))
            old_len = len(self._buf)
            self._fill(timeout=max(0.1, remaining))
            if len(self._buf) > old_len:
                cumulative += self._buf[old_len:]
                self._buf = self._buf[old_len:]

    def _fill(self, timeout=10):
        self._sock.settimeout(timeout)
        try:
            chunk = self._sock.recv(4096)
        except socket.timeout:
            return
        if not chunk:
            return
        cleaned = self._strip_iac(chunk)
        self._buf += cleaned

    def _strip_iac(self, data):
        result = bytearray()
        i = 0
        while i < len(data):
            if data[i:i+1] == IAC:
                if i + 1 < len(data):
                    cmd = data[i+1]
                    if cmd in (WILL, WONT, DO, DONT):
                        # Negotiate: reply opposite to refuse
                        if cmd == WILL:
                            result.extend(IAC + DONT + data[i+2:i+3])
                        elif cmd == DO:
                            result.extend(IAC + WONT + data[i+2:i+3])
                        i += 3
                    elif cmd == SB:
                        # Skip sub-negotiation until IAC SE
                        end = data.find(IAC + SE, i + 2)
                        if end >= 0:
                            i = end + 2
                        else:
                            i = len(data)
                    elif cmd == IAC:
                        result.append(IAC)
                        i += 2
                    else:
                        i += 2
                else:
                    i += 1
            else:
                result.append(data[i])
                i += 1
        return bytes(result)

    @staticmethod
    def _decode(data):
        if isinstance(data, bytes):
            return data.decode('latin-1', errors='replace')
        return data

    @staticmethod
    def _encode(data):
        if isinstance(data, str):
            return data.encode('latin-1')
        return data

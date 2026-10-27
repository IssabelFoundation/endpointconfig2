"""Minimal Asterisk Manager Interface client using stdlib socket.

Replaces pyst2/py-Asterisk dependency. Provides only the subset used by
issabel-endpointconfig: connect, login, Command.
"""
import socket
import threading
import logging

logger = logging.getLogger(__name__)


class AMIError(Exception):
    pass


class AMIClient:
    def __init__(self):
        self._sock = None
        self._lock = threading.Lock()
        self._seq = 0

    def _next_seq(self):
        self._seq += 1
        return self._seq

    def connect(self, host, port=5038, timeout=10):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.settimeout(timeout)
        self._sock.connect((host, port))
        self._buf = b''
        banner = self._read_until(b'\r\n\r\n', timeout)
        if not banner:
            raise AMIError('No banner from AMI')
        logger.debug('AMI banner: %s', banner)

    def login(self, user, passwd):
        action_id = 'login-%08x' % self._next_seq()
        cmd = (
            'Action: Login\r\n'
            'Username: %s\r\n'
            'Secret: %s\r\n'
            'ActionID: %s\r\n'
            '\r\n' % (user, passwd, action_id)
        )
        with self._lock:
            self._sock.sendall(cmd.encode('ascii'))
            headers = self._read_headers(timeout=10)
        if headers.get('Response') == 'Error':
            raise AMIError(headers.get('Message', 'Login failed'))
        return headers

    def Command(self, command):
        action_id = 'cmd-%08x' % self._next_seq()
        cmd = (
            'Action: Command\r\n'
            'Command: %s\r\n'
            'ActionID: %s\r\n'
            '\r\n' % (command, action_id)
        )
        with self._lock:
            self._sock.sendall(cmd.encode('ascii'))
            output_lines = self._read_command_response(action_id, timeout=30)
        return output_lines

    def close(self):
        if self._sock:
            try:
                self._sock.close()
            except Exception:
                pass
            self._sock = None

    def _read_headers(self, timeout=10):
        self._sock.settimeout(timeout)
        raw = self._read_until(b'\r\n\r\n', timeout)
        if not raw:
            return {}
        headers = {}
        for line in raw.decode('ascii', errors='replace').split('\r\n'):
            if ':' in line:
                key, val = line.split(':', 1)
                headers[key.strip()] = val.strip()
        return headers

    def _read_command_response(self, action_id, timeout=30):
        self._sock.settimeout(timeout)
        lines = []
        while True:
            line = self._read_line(timeout)
            if not line:
                break
            decoded = line.decode('ascii', errors='replace').strip()
            if decoded == '--END COMMAND--':
                break
            if decoded.startswith('ActionID:'):
                continue
            if decoded.startswith('Response:'):
                if 'Error' in decoded:
                    raise AMIError('AMI command failed')
                continue
            if decoded.startswith('Privilege:'):
                continue
            if decoded:
                lines.append(decoded)
        return lines

    def _read_until(self, needle, timeout=30):
        import time
        deadline = time.time() + timeout
        while True:
            idx = self._buf.find(needle)
            if idx >= 0:
                result = self._buf[:idx + len(needle)]
                self._buf = self._buf[idx + len(needle):]
                return result
            remaining = deadline - time.time()
            if remaining <= 0:
                result = self._buf
                self._buf = b''
                return result
            try:
                self._sock.settimeout(max(0.1, remaining))
                chunk = self._sock.recv(4096)
                if not chunk:
                    result = self._buf
                    self._buf = b''
                    return result
                self._buf += chunk
            except socket.timeout:
                continue

    def _read_line(self, timeout=30):
        return self._read_until(b'\r\n', timeout)

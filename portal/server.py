# famguard enrollment portal - stdlib only, no dependencies.
import os
import html
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = int(os.environ.get("PORTAL_PORT", "8080"))
DOH_URL = os.environ.get("DOH_URL", "https://dns.example.com/dns-query")
PRIVATE_DNS_HOST = os.environ.get("PRIVATE_DNS_HOST", "dns.example.com")

ROOT = os.path.dirname(os.path.abspath(__file__))

MOBILECONFIG = """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>PayloadContent</key>
  <array>
    <dict>
      <key>DNSSettings</key>
      <dict>
        <key>DNSProtocol</key>
        <string>HTTPS</string>
        <key>ServerURL</key>
        <string>{doh_url}</string>
      </dict>
      <key>EncryptedPayloadIdentifier</key>
      <string>famguard.dns.profile</string>
      <key>PayloadDisplayName</key>
      <string>FamGuard Secure DNS</string>
      <key>PayloadIdentifier</key>
      <string>com.famguard.dns</string>
      <key>PayloadType</key>
      <string>com.apple.dnsSettings.managed</string>
      <key>PayloadUUID</key>
      <string>4B7A9C21-6E1F-4E1B-9C0A-F1F7B1E9A111</string>
      <key>PayloadVersion</key>
      <integer>1</integer>
      <key>ProhibitDisablement</key>
      <false/>
    </dict>
  </array>
  <key>PayloadDisplayName</key>
  <string>FamGuard Secure DNS</string>
  <key>PayloadIdentifier</key>
  <string>com.famguard.dns</string>
  <key>PayloadRemovalDisallowed</key>
  <false/>
  <key>PayloadType</key>
  <string>Configuration</string>
  <key>PayloadUUID</key>
  <string>4B7A9C21-6E1F-4E1B-9C0A-F1F7B1E9A112</string>
  <key>PayloadVersion</key>
  <integer>1</integer>
</dict>
</plist>
""".format(doh_url=html.escape(DOH_URL, quote=True))


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, ctype, body, extra=None):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/healthz":
            return self._send(200, "text/plain", b"ok")
        if path in ("/apple/profile.mobileconfig", "/profile.mobileconfig"):
            return self._send(200, "application/x-apple-aspen-config",
                              MOBILECONFIG.encode(),
                              {"Content-Disposition": "attachment; filename=famguard.mobileconfig"})
        if path == "/dns-query":
            # convenience: DoH passthrough hint (real DoH terminates on the same hostname)
            return self._send(405, "text/plain", b"Use HTTPS DoH on this hostname via the tunnel")
        if path in ("/", ""):
            path = "/index.html"
        safe = os.path.normpath(path).lstrip("/")
        full = os.path.join(ROOT, safe)
        if not full.startswith(ROOT) or not os.path.isfile(full):
            return self._send(404, "text/plain", b"not found")
        ctype = "text/html" if full.endswith(".html") else "text/javascript" if full.endswith(".js") else "text/plain"
        try:
            with open(full, "rb") as f:
                body = f.read()
            if full.endswith(".html"):
                body = body.replace(b"__DOH_URL__", DOH_URL.encode()).replace(b"__PRIVATE_DNS_HOST__", PRIVATE_DNS_HOST.encode())
            return self._send(200, ctype, body)
        except OSError:
            return self._send(404, "text/plain", b"not found")

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    print(f"[famguard] portal on 0.0.0.0:{PORT} | DoH {DOH_URL} | Private DNS {PRIVATE_DNS_HOST}")
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()

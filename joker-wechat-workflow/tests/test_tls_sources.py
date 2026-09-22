"""Exercise both actual fetch functions against a local untrusted TLS endpoint."""
import importlib.util
import socket
import ssl
import subprocess
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]
def load(relative):
 spec=importlib.util.spec_from_file_location('source_'+str(abs(hash(relative))),ROOT/relative)
 module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

class TLS(unittest.TestCase):
 def test_untrusted_server_is_rejected_by_both_fetchers(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t)
   subprocess.run(['openssl','req','-x509','-newkey','rsa:2048','-nodes','-keyout',str(p/'key'),'-out',str(p/'cert'),'-days','1','-subj','/CN=localhost'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
   ctx=ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER);ctx.load_cert_chain(p/'cert',p/'key')
   modules=[load('gzh-explosive-content-detector/scripts/fetch_gzh_trends.py'),load('baokuan-article-analysis/scripts/daily_sector_trends.py')]
   for module in modules:
    server=socket.socket();server.bind(('127.0.0.1',0));server.listen();address=server.getsockname()
    def serve():
     conn,_=server.accept()
     try:
      with ctx.wrap_socket(conn,server_side=True): pass
     except ssl.SSLError: conn.close()
     finally:server.close()
    worker=threading.Thread(target=serve,daemon=True);worker.start()
    connect=socket.create_connection
    with patch.object(module.socket,'create_connection',side_effect=lambda *a,**k:connect(address,timeout=2)):
     with self.assertRaises(ssl.SSLCertVerificationError):
      if hasattr(module,'fetch_via_no_sni'):module.fetch_via_no_sni('https://localhost/path',{}, {},timeout=2)
      else:module.fetch_no_sni({},timeout=2)
    worker.join(3);self.assertFalse(worker.is_alive())

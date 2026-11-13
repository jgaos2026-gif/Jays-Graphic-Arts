import json
import tempfile
import unittest
from pathlib import Path

from jga_universal import BCTVault, ScanResult, Verdict, split_for_mail, join_mail_parts, BCTRuntime


class UnknownScanner:
    def scan(self, path):
        return ScanResult(Verdict.UNKNOWN, "test", "no scanner")


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_vault_round_trip_and_dedup(self):
        vault = BCTVault(self.root / "vault")
        data = b"A" * 100000 + b"binary\x00payload"
        first = vault.put(data)
        second = vault.put(data)
        self.assertFalse(first["deduplicated"])
        self.assertTrue(second["deduplicated"])
        self.assertEqual(vault.get(first["sha256"]), data)

    def test_file_manifest_restore(self):
        src = self.root / "source.bin"
        src.write_bytes(b"payload" * 20000)
        vault = BCTVault(self.root / "vault")
        manifest = vault.put_file(src, block_size=4096)
        dst = self.root / "restored.bin"
        vault.restore_file(manifest, dst)
        self.assertEqual(src.read_bytes(), dst.read_bytes())

    def test_corrupt_manifest_rejected(self):
        src = self.root / "source.bin"
        src.write_bytes(b"payload")
        vault = BCTVault(self.root / "vault")
        manifest = vault.put_file(src)
        manifest["size"] += 1
        with self.assertRaises(IOError):
            vault.restore_file(manifest, self.root / "out")

    def test_mail_split_join(self):
        src = self.root / "large.bin"
        src.write_bytes(bytes(range(256)) * 10000)
        out = self.root / "parts"
        manifest = split_for_mail(src, out, part_bytes=100000)
        mp = out / (src.name + ".bct-manifest.json")
        dst = self.root / "joined.bin"
        join_mail_parts(mp, out, dst)
        self.assertEqual(src.read_bytes(), dst.read_bytes())
        self.assertGreater(len(manifest["parts"]), 1)

    def test_mail_tamper_rejected(self):
        src = self.root / "large.bin"
        src.write_bytes(b"x" * 200000)
        out = self.root / "parts"
        split_for_mail(src, out, part_bytes=100000)
        part = out / (src.name + ".bctpart00000")
        part.write_bytes(b"tampered")
        with self.assertRaises(IOError):
            join_mail_parts(out / (src.name + ".bct-manifest.json"), out, self.root / "joined")

    def test_unknown_scan_quarantines_without_mutating_source(self):
        src = self.root / "incoming.bin"
        original = b"untrusted input"
        src.write_bytes(original)
        runtime = BCTRuntime(self.root / "runtime", scanner=UnknownScanner())
        result = runtime.ingest(src)
        self.assertEqual(result["status"], "quarantined")
        self.assertEqual(src.read_bytes(), original)
        self.assertTrue(Path(result["path"]).exists())


if __name__ == "__main__":
    unittest.main()

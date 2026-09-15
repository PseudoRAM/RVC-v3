import io
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from model_cache import DownloadCache, ModelCache


class Response(io.BytesIO):
    def geturl(self):
        return "https://example.test/voice.zip"


def archive(files):
    data = io.BytesIO()
    with zipfile.ZipFile(data, "w") as bundle:
        for name, content in files.items():
            bundle.writestr(name, content)
    return data.getvalue()


class CacheTests(unittest.TestCase):
    def test_memory_reuse_and_eviction(self):
        cache = ModelCache(1)
        a, hit = cache.get("a", object)
        self.assertFalse(hit)
        self.assertEqual(cache.get("a", lambda: self.fail("Reloaded cached model")), (a, True))
        cache.get("b", object)
        self.assertNotIn("a", cache.items)
        self.assertIsNot(cache.get("a", object)[0], a)

    def test_failed_load_does_not_poison_cache(self):
        cache = ModelCache(1)
        with self.assertRaises(ValueError):
            cache.get("a", lambda: (_ for _ in ()).throw(ValueError()))
        self.assertFalse(cache.get("a", object)[1])

    def test_download_hit_refresh_and_failed_refresh(self):
        data = archive({"nested/voice.pth": b"weights"})
        with tempfile.TemporaryDirectory() as root:
            cache = DownloadCache(root)
            with patch("urllib.request.urlopen", side_effect=lambda *a, **k: Response(data)) as fetch:
                folder, hit = cache.get("https://example.test/a.zip")
                self.assertFalse(hit)
                self.assertTrue(cache.get("https://example.test/a.zip")[1])
                self.assertEqual(fetch.call_count, 1)
                self.assertFalse(cache.get("https://example.test/a.zip", refresh=True)[1])
            with patch("urllib.request.urlopen", side_effect=OSError("offline")):
                with self.assertRaises(OSError):
                    cache.get("https://example.test/a.zip", refresh=True)
            self.assertEqual((folder / "voice.pth").read_bytes(), b"weights")
            self.assertTrue(cache.get("https://example.test/a.zip")[1])

    def test_url_identity_and_disk_limit(self):
        data = archive({"voice.pth": b"weights"})
        with tempfile.TemporaryDirectory() as root:
            cache = DownloadCache(root, capacity=1)
            with patch("urllib.request.urlopen", side_effect=lambda *a, **k: Response(data)):
                first, _ = cache.get("https://a.test/model.zip?version=1")
                second, _ = cache.get("https://a.test/model.zip?version=2")
            self.assertNotEqual(first, second)
            self.assertFalse(first.exists())
            self.assertTrue(second.exists())

    def test_archive_paths_cannot_escape_cache(self):
        data = archive({"../../escape.pth": b"weights", "../../ignored.txt": b"bad"})
        with tempfile.TemporaryDirectory() as root:
            with patch("urllib.request.urlopen", return_value=Response(data)):
                folder, _ = DownloadCache(root).get("https://a.test/model.zip")
            self.assertEqual((folder / "escape.pth").read_bytes(), b"weights")
            self.assertFalse((Path(root) / "ignored.txt").exists())

    def test_invalid_archive_and_size_limits(self):
        for data, limit in [(archive({"a.pth": b"a", "b.pth": b"b"}), 10000),
                            (archive({"a.pth": b"weights"}), 1)]:
            with tempfile.TemporaryDirectory() as root:
                with patch("urllib.request.urlopen", return_value=Response(data)):
                    with self.assertRaises(ValueError):
                        DownloadCache(root, max_bytes=limit).get("https://a.test/model.zip")
                self.assertEqual(list(Path(root).iterdir()), [])


if __name__ == "__main__":
    unittest.main()

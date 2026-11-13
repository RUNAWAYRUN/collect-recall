"""关键行为：首轮记基线、第二轮不重复、新增能被识别、firstSeen 不重置。"""
import json, os, subprocess, sys, tempfile, unittest

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts")

def run(*args):
    return subprocess.run([sys.executable, *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout

class T(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        for f in ("x-export.json", "yt-export.json", "stars.json"):
            open(os.path.join(self.d, f), "w").write(open(os.path.join(ROOT, "sample", f)).read())

    def merge(self):
        return run("merge_inventory.py", "--x", f"{self.d}/x-export.json",
                   "--yt", f"{self.d}/yt-export.json", "--stars", f"{self.d}/stars.json",
                   "--out-dir", self.d)

    def test_baseline_then_stable(self):
        self.merge()
        first = run("review_delta.py", "--dir", self.d)
        second = run("review_delta.py", "--dir", self.d)
        self.assertIn("新增 5", first)
        self.assertIn("新增 0", second)

    def test_duplicate_video_keeps_first_metadata(self):
        p = os.path.join(self.d, "yt-export.json")
        with open(p, "w") as f:
            json.dump({"watchLater": [
                {"url": "https://www.youtube.com/watch?v=AAA&t=30", "title": "first"},
                {"url": "https://youtu.be/AAA", "title": "duplicate"}]}, f)
        self.merge()
        with open(os.path.join(self.d, "inventory.json")) as f:
            videos = [i for i in json.load(f)["items"] if i["platform"] == "YouTube"]
        self.assertEqual(len(videos), 1)
        self.assertEqual(videos[0]["title"], "first")

    def test_invalid_json_keeps_old_inventory(self):
        self.merge()
        p = os.path.join(self.d, "inventory.json")
        with open(p) as f:
            before = f.read()
        with open(os.path.join(self.d, "stars.json"), "w") as f:
            f.write("{")
        with self.assertRaises(subprocess.CalledProcessError):
            self.merge()
        with open(p) as f:
            self.assertEqual(f.read(), before)

    def test_first_seen_persists(self):
        self.merge()
        before = json.load(open(os.path.join(self.d, "inventory.json")))["items"][0]["firstSeen"]
        self.merge()
        after = json.load(open(os.path.join(self.d, "inventory.json")))["items"][0]["firstSeen"]
        self.assertEqual(before, after)

    def test_new_item_detected(self):
        self.merge(); run("review_delta.py", "--dir", self.d)
        p = os.path.join(self.d, "inventory.json")
        data = json.load(open(p))
        data["items"].append({"platform": "X", "kind": "书签", "title": "n", "url": "https://e/x", "tier": "近期", "note": "", "firstSeen": "2026-01-01T00:00:00Z"})
        json.dump(data, open(p, "w"))
        self.assertIn("新增 1", run("review_delta.py", "--dir", self.d))


class URLKeyTest(unittest.TestCase):
    def test_two_youtube_videos_are_distinct(self):
        sys.path.insert(0, ROOT)
        from keys import normalize
        self.assertNotEqual(normalize("https://www.youtube.com/watch?v=AAA"), normalize("https://www.youtube.com/watch?v=BBB"))

    def test_same_video_different_tracking_collapses(self):
        sys.path.insert(0, ROOT)
        from keys import normalize
        self.assertEqual(normalize("https://www.youtube.com/watch?v=AAA&list=WL&index=2&t=30s"),
                         normalize("https://youtu.be/AAA"))

    def test_deleting_one_of_two_videos_is_reported(self):
        d = tempfile.mkdtemp()
        inv = {"items": [
            {"platform": "YouTube", "kind": "稍后观看", "title": "a", "url": "https://www.youtube.com/watch?v=AAA", "tier": "近期", "note": ""},
            {"platform": "YouTube", "kind": "稍后观看", "title": "b", "url": "https://www.youtube.com/watch?v=BBB", "tier": "近期", "note": ""}]}
        json.dump(inv, open(os.path.join(d, "inventory.json"), "w"))
        run("review_delta.py", "--dir", d)                      # 基线：2 条
        inv["items"] = inv["items"][:1]                          # 删掉 BBB
        json.dump(inv, open(os.path.join(d, "inventory.json"), "w"))
        out = run("review_delta.py", "--dir", d)
        self.assertIn("本次未观测 1", out)
        self.assertIn("BBB", out)

class FailClosedTest(unittest.TestCase):
    def test_missing_input_fails_and_keeps_old_inventory(self):
        d = tempfile.mkdtemp()
        good = os.path.join(d, "inventory.json")
        json.dump({"items": [{"platform": "X", "kind": "书签", "title": "old",
                              "url": "https://e/old", "tier": "近期", "note": "", "firstSeen": "x"}]},
                  open(good, "w"))
        before = open(good).read()
        r = subprocess.run([sys.executable, "merge_inventory.py", "--x", os.path.join(d, "nope.json"),
                            "--yt", os.path.join(ROOT, "sample/yt-export.json"),
                            "--stars", os.path.join(ROOT, "sample/stars.json"), "--out-dir", d],
                           cwd=ROOT, capture_output=True, text=True)
        self.assertNotEqual(r.returncode, 0)
        self.assertEqual(before, open(good).read())   # 旧文件未被破坏


class BusinessParamTest(unittest.TestCase):
    def test_business_params_are_kept(self):
        sys.path.insert(0, ROOT)
        from keys import normalize
        self.assertNotEqual(normalize("https://example.com/p?a=1&t=30"),
                            normalize("https://example.com/p?a=1"))

    def test_only_tracking_params_are_stripped(self):
        sys.path.insert(0, ROOT)
        from keys import normalize
        self.assertEqual(normalize("https://example.com/p?a=1&utm_source=x&fbclid=y"),
                         normalize("https://example.com/p?a=1"))

if __name__ == "__main__":
    unittest.main()

"""WERKBANK T1 — Tests fuer Gate-Runner + deterministische Checks E1/D3/E2.

Verification-first: Negativtests synthetisieren den Verstoss zur LAUFZEIT in einem
Tempdir (nie committet -> Repo bleibt secret-/PII-frei). Positivtest gegen das
committete clean-Fixture.

Lauf:  python3 -m unittest discover -s gates/checks/tests   (vom Repo-Root)
"""
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
GATES_DIR = os.path.abspath(os.path.join(HERE, "..", ".."))   # .../gates
REPO_ROOT = os.path.abspath(os.path.join(GATES_DIR, ".."))
sys.path.insert(0, GATES_DIR)

from checks import e1_eu_routing, e2_pii_scan, d3_secret_scan, common  # noqa: E402
import runner  # noqa: E402

CLEAN = os.path.join(HERE, "fixtures", "clean")


def _write(d, rel, content):
    p = os.path.join(d, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)
    return p


class CleanFixturePasses(unittest.TestCase):
    def test_e1_clean_pass(self):
        self.assertEqual(e1_eu_routing.run(CLEAN).status, common.PASS)

    def test_e2_clean_pass(self):
        self.assertEqual(e2_pii_scan.run(CLEAN).status, common.PASS)

    def test_d3_clean_pass(self):
        self.assertEqual(d3_secret_scan.run(CLEAN).status, common.PASS)


class E1CatchesNonEu(unittest.TestCase):
    def test_non_eu_endpoint_fails(self):
        with tempfile.TemporaryDirectory() as d:
            # Literale gesplittet -> kein zusammenhaengender Verstoss im Repo selbst
            endpoint = "https://api.openai." + "com/v1/chat"
            region = "us-" + "east-1"
            _write(d, "router.py",
                   'ENDPOINT = "%s"\nREGION = "%s"\n' % (endpoint, region))
            res = e1_eu_routing.run(d)
            self.assertEqual(res.status, common.FAIL)
            self.assertTrue(res.findings)

    def test_azure_us_region_fails(self):
        with tempfile.TemporaryDirectory() as d:
            ep = "https://my." + "east" + "us" + ".api.cognitive.microsoft.com"
            _write(d, "azure.json", '{"endpoint": "%s"}\n' % ep)
            self.assertEqual(e1_eu_routing.run(d).status, common.FAIL)

    def test_us_cross_region_model_id_fails(self):
        with tempfile.TemporaryDirectory() as d:
            mid = "us." + "anthropic.claude-x"
            _write(d, "bedrock.yaml", "model_id: %s\n" % mid)
            self.assertEqual(e1_eu_routing.run(d).status, common.FAIL)

    def test_eu_region_stays_clean(self):
        # Regressionsschutz: EU-Marker duerfen NICHT geflaggt werden.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "ok.yaml", "region: eu-central-1\nmodel_id: eu.anthropic.claude\n")
            self.assertEqual(e1_eu_routing.run(d).status, common.PASS)

    def test_secret_does_not_trip_e1(self):
        # Isolation: ein gepflanztes Secret darf E1 nicht ausloesen.
        with tempfile.TemporaryDirectory() as d:
            _write(d, "creds.env", "AWS_SECRET=" + ("A1b2C3d4" * 5) + "\n")
            self.assertEqual(e1_eu_routing.run(d).status, common.PASS)


class D3CatchesSecret(unittest.TestCase):
    def test_planted_secret_fails(self):
        with tempfile.TemporaryDirectory() as d:
            # zur Laufzeit erzeugt, nie committet
            akia = "AKIA" + "QURTZ7XMPLE4KLMN"  # AKIA + 16 Zeichen
            secret = "wJalrXUtnFEMI" + "K7MDENGbPxRfiCYEXAMPLEKEY"
            _write(d, "creds.env", "AWS_ACCESS_KEY_ID=%s\nAWS_SECRET_ACCESS_KEY=%s\n" % (akia, secret))
            res = d3_secret_scan.run(d)
            self.assertEqual(res.status, common.FAIL)
            self.assertTrue(res.findings)

    def test_private_key_fails(self):
        with tempfile.TemporaryDirectory() as d:
            header = "-----BEGIN RSA PRIVATE" + " KEY-----"   # gesplittet: kein Literal im Repo
            footer = "-----END RSA PRIVATE" + " KEY-----"
            _write(d, "id_rsa", header + "\nMIIEowIBAAKCAQEA\n" + footer + "\n")
            self.assertEqual(d3_secret_scan.run(d).status, common.FAIL)

    def test_pii_does_not_trip_d3(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "logs/x.log", "user max.mustermann@example.com angemeldet\n")
            self.assertEqual(d3_secret_scan.run(d).status, common.PASS)


class E2CatchesPii(unittest.TestCase):
    def test_email_and_phone_in_log_fails(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "logs/leak.log",
                   "2026 INFO user=max.mustermann@example.com phone=+49 151 23456789\n")
            res = e2_pii_scan.run(d)
            self.assertEqual(res.status, common.FAIL)
            self.assertTrue(res.findings)

    def test_iban_in_output_fails(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "outputs/dump.txt", "IBAN DE89370400440532013000 ueberwiesen\n")
            self.assertEqual(e2_pii_scan.run(d).status, common.FAIL)

    def test_secret_does_not_trip_e2(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "logs/x.log", "token=" + ("Zx9" * 12) + "\n")
            self.assertEqual(e2_pii_scan.run(d).status, common.PASS)


class ReportRedacts(unittest.TestCase):
    """Self-consistency: der Report selbst darf keine Klartext-PII/Secrets enthalten."""
    def test_secret_value_not_in_report(self):
        with tempfile.TemporaryDirectory() as d:
            secret = "wJalrXUtnFEMI" + "K7MDENGbPxRfiCYEXAMPLEKEY"
            _write(d, "creds.env", "AWS_SECRET_ACCESS_KEY=%s\n" % secret)
            res = d3_secret_scan.run(d)
            blob = res.to_report_lines()
            self.assertNotIn(secret, "\n".join(blob))

    def test_email_not_in_report(self):
        with tempfile.TemporaryDirectory() as d:
            _write(d, "logs/leak.log", "user=alice.beispiel@example.com\n")
            res = e2_pii_scan.run(d)
            self.assertNotIn("alice.beispiel@example.com", "\n".join(res.to_report_lines()))


class RunnerEndToEnd(unittest.TestCase):
    def test_parses_gates_yaml(self):
        gates = runner.load_gates(os.path.join(REPO_ROOT, "gates", "gates.yaml"))
        ids = {g["id"] for st in gates["stages"] for g in st["gates"]}
        for expected in ("A1", "D3", "E1", "E2", "I1"):
            self.assertIn(expected, ids)
        self.assertEqual(gates["meta"]["promise"], "GRUEN")

    def test_runner_clean_is_green_and_writes_report(self):
        with tempfile.TemporaryDirectory() as out:
            report = os.path.join(out, "GATE-REPORT.md")
            result = runner.run_gates(
                gates_path=os.path.join(REPO_ROOT, "gates", "gates.yaml"),
                target=CLEAN,
                report_path=report,
            )
            self.assertEqual(result["overall"], "GRUEN")
            self.assertTrue(os.path.exists(report))
            with open(report, encoding="utf-8") as f:
                txt = f.read()
            self.assertIn("E1", txt)
            self.assertIn("GRUEN", txt)
            # implementierte Checks muessen PASS sein
            self.assertEqual(result["results"]["E1"]["status"], common.PASS)
            self.assertEqual(result["results"]["E2"]["status"], common.PASS)
            self.assertEqual(result["results"]["D3"]["status"], common.PASS)

    def test_runner_blocks_on_planted_secret(self):
        with tempfile.TemporaryDirectory() as target, tempfile.TemporaryDirectory() as out:
            _write(target, "service.py", 'E = "https://eu-central-1.example/v1"\n')
            _write(target, "creds.env",
                   "AWS_ACCESS_KEY_ID=AKIA%s\n" % "QURTZ7XMPLE4KLMN")
            report = os.path.join(out, "GATE-REPORT.md")
            result = runner.run_gates(
                gates_path=os.path.join(REPO_ROOT, "gates", "gates.yaml"),
                target=target, report_path=report)
            self.assertEqual(result["overall"], "ROT")
            self.assertEqual(result["results"]["D3"]["status"], common.FAIL)


if __name__ == "__main__":
    unittest.main(verbosity=2)

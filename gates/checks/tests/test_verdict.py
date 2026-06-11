"""Tests fuer das HARTE Verdikt (gates/verdict.py) — das Herz von 'Gruen heisst bewiesen'.

Deckt die Regel ab, an der das alte System scheiterte:
  Ein Pflicht-Gate, das SKIPt (Tool fehlt / kein Check / kein Kontext), ist NICHT gruen.

Aufbau:
  PflichtenheftParser  — Mini-YAML, default_profile, extends-Vererbung, Fehlerfaelle
  ResolveRequired      — Pflichtmengen inkl. extends-Ketten
  ComputeVerdict       — Wahrheitstabelle PASS/FAIL/SKIP/WARN/fehlend x Pflicht/optional
  RegressionFalseGreen — der konkrete ChatGPT-Befund: 32 SKIPs duerfen nie GRUEN sein
"""
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO_ROOT, "gates"))

import verdict  # noqa: E402
from checks import common  # noqa: E402

SHIPPED = os.path.join(REPO_ROOT, "gates", "pflichtenheft.yaml")


def _res(status, skip_reason=None, summary=""):
    """Kompakter Ergebnis-Eintrag, wie der Runner ihn in results[gid] ablegt."""
    return {"status": status, "skip_reason": skip_reason, "summary": summary}


def _passing(gates):
    return {g: _res(common.PASS) for g in gates}


# ----------------------------------------------------------------------------

class PflichtenheftParser(unittest.TestCase):
    def setUp(self):
        self.pf = verdict.load_pflichtenheft(SHIPPED)

    def test_default_profile_parsed(self):
        self.assertEqual(self.pf["default_profile"], "basis")

    def test_all_shipped_profiles_present(self):
        for name in ("static_min", "basis", "spec_driven", "pii", "multi_tenant", "werkbank_self"):
            self.assertIn(name, self.pf["profiles"], "Profil %s fehlt" % name)

    def test_required_is_list_of_gate_ids(self):
        req = self.pf["profiles"]["static_min"]["required"]
        self.assertEqual(req, ["B3", "D3", "F1", "H4"])

    def test_desc_unquoted(self):
        self.assertIn("Minimal", self.pf["profiles"]["static_min"]["desc"])
        self.assertNotIn('"', self.pf["profiles"]["static_min"]["desc"])

    def test_inline_comment_not_in_default(self):
        # default_profile darf keinen angehaengten '# ...'-Kommentar einschleppen
        self.assertNotIn("#", self.pf["default_profile"])

    def test_parses_from_string_via_tempfile(self):
        text = (
            "default_profile: x\n"
            "profiles:\n"
            "  x:\n"
            "    desc: \"demo\"\n"
            "    required: [A1, B2, C3]\n"
        )
        with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as f:
            f.write(text)
            path = f.name
        try:
            pf = verdict.load_pflichtenheft(path)
            self.assertEqual(pf["profiles"]["x"]["required"], ["A1", "B2", "C3"])
        finally:
            os.unlink(path)


class ResolveRequired(unittest.TestCase):
    def setUp(self):
        self.profiles = verdict.load_pflichtenheft(SHIPPED)["profiles"]

    def test_flat_profile(self):
        self.assertEqual(set(verdict.resolve_required(self.profiles, "static_min")),
                         {"B3", "D3", "F1", "H4"})

    def test_extends_one_level(self):
        # basis extends static_min -> Vereinigung
        req = set(verdict.resolve_required(self.profiles, "basis"))
        self.assertTrue({"B3", "D3", "F1", "H4"}.issubset(req))   # geerbt
        self.assertTrue({"B1", "B2", "C1", "C2"}.issubset(req))   # eigen

    def test_extends_chain_three_levels(self):
        # pii extends spec_driven extends basis extends static_min
        req = set(verdict.resolve_required(self.profiles, "pii"))
        for g in ("B3", "D3", "F1", "H4", "B1", "B2", "C1", "C2", "A1", "A2", "A3",
                  "D1", "E1", "E2", "E4", "E5", "E6"):
            self.assertIn(g, req, "%s sollte in pii-Pflicht sein" % g)

    def test_no_duplicates_in_chain(self):
        req = verdict.resolve_required(self.profiles, "multi_tenant")
        self.assertEqual(len(req), len(set(req)), "Pflichtliste enthaelt Duplikate")

    def test_unknown_profile_raises(self):
        with self.assertRaises(KeyError):
            verdict.resolve_required(self.profiles, "gibtsnicht")

    def test_unknown_extends_raises(self):
        profiles = {"a": {"extends": "ghost", "required": ["X1"]}}
        with self.assertRaises(KeyError):
            verdict.resolve_required(profiles, "a")


class ComputeVerdict(unittest.TestCase):
    REQUIRED = ["B3", "D3", "F1", "H4"]

    def test_all_required_pass_is_green(self):
        vd = verdict.compute_verdict(self.REQUIRED, _passing(self.REQUIRED))
        self.assertEqual(vd["verdict"], verdict.GRUEN)
        self.assertEqual(len(vd["passed"]), 4)
        self.assertEqual(vd["violated"], [])
        self.assertEqual(vd["uncovered"], [])

    def test_one_required_fail_is_red_and_listed_as_violated(self):
        results = _passing(self.REQUIRED)
        results["D3"] = _res(common.FAIL, summary="Secret gefunden")
        vd = verdict.compute_verdict(self.REQUIRED, results)
        self.assertEqual(vd["verdict"], verdict.ROT)
        self.assertEqual([v["gate"] for v in vd["violated"]], ["D3"])
        self.assertEqual(vd["violated"][0]["summary"], "Secret gefunden")

    def test_required_skip_any_reason_is_red_and_uncovered(self):
        # DIE Kernregel: SKIP eines Pflicht-Gates ist NIE gruen — egal welcher Grund.
        for reason in (common.TOOL_MISSING, common.NOT_IMPLEMENTED, common.NOT_APPLICABLE, None):
            with self.subTest(reason=reason):
                results = _passing(self.REQUIRED)
                results["F1"] = _res(common.SKIP, skip_reason=reason)
                vd = verdict.compute_verdict(self.REQUIRED, results)
                self.assertEqual(vd["verdict"], verdict.ROT)
                self.assertEqual([u["gate"] for u in vd["uncovered"]], ["F1"])

    def test_uncovered_carries_reason(self):
        results = _passing(self.REQUIRED)
        results["B3"] = _res(common.SKIP, skip_reason=common.TOOL_MISSING, summary="ruff nicht installiert")
        vd = verdict.compute_verdict(self.REQUIRED, results)
        self.assertEqual(vd["uncovered"][0]["reason"], common.TOOL_MISSING)

    def test_required_gate_absent_from_results_is_uncovered(self):
        results = _passing(["B3", "D3", "F1"])  # H4 fehlt voellig
        vd = verdict.compute_verdict(self.REQUIRED, results)
        self.assertEqual(vd["verdict"], verdict.ROT)
        self.assertEqual([u["gate"] for u in vd["uncovered"]], ["H4"])
        self.assertEqual(vd["uncovered"][0]["reason"], "nicht gelaufen")

    def test_required_warn_is_not_green(self):
        results = _passing(self.REQUIRED)
        results["H4"] = _res(common.WARN)
        vd = verdict.compute_verdict(self.REQUIRED, results)
        self.assertEqual(vd["verdict"], verdict.ROT)
        self.assertEqual([u["gate"] for u in vd["uncovered"]], ["H4"])

    def test_optional_gate_fail_does_not_block(self):
        # Ein NICHT-Pflicht-Gate, das FAILt, aber nicht als block-fail gemeldet wird,
        # aendert das Verdikt nicht.
        results = _passing(self.REQUIRED)
        results["E1"] = _res(common.FAIL, summary="non-eu endpoint")
        vd = verdict.compute_verdict(self.REQUIRED, results)
        self.assertEqual(vd["verdict"], verdict.GRUEN)

    def test_extra_block_fail_outside_pflicht_is_surfaced_but_not_blocking(self):
        # Ein block-Gate ausserhalb des Profils, das FAILt, wird beratend gemeldet,
        # aendert das Verdikt aber NICHT — sonst koennten Fremd-Befunde ein bewusst
        # schmales Profil aushebeln.
        results = _passing(self.REQUIRED)
        results["E1"] = _res(common.FAIL, summary="non-eu endpoint")
        vd = verdict.compute_verdict(self.REQUIRED, results, block_fail_gates=["E1"])
        self.assertEqual(vd["verdict"], verdict.GRUEN)
        self.assertEqual([e["gate"] for e in vd["extra_block_fails"]], ["E1"])

    def test_block_fail_that_is_also_required_counts_as_violated_not_extra(self):
        results = _passing(self.REQUIRED)
        results["D3"] = _res(common.FAIL)
        vd = verdict.compute_verdict(self.REQUIRED, results, block_fail_gates=["D3"])
        self.assertEqual([v["gate"] for v in vd["violated"]], ["D3"])
        self.assertEqual(vd["extra_block_fails"], [])  # nicht doppelt zaehlen

    def test_empty_required_with_no_block_fail_is_green(self):
        vd = verdict.compute_verdict([], {})
        self.assertEqual(vd["verdict"], verdict.GRUEN)


class RegressionFalseGreen(unittest.TestCase):
    """Der konkrete Befund aus dem GATE-REPORT: GRUEN trotz 32 SKIPs. Darf nie wieder vorkommen."""

    def test_thirtytwo_skips_under_basis_is_red_not_green(self):
        required = verdict.resolve_required(
            verdict.load_pflichtenheft(SHIPPED)["profiles"], "basis")
        # Genau die alte Situation: nur ein paar PASS, der Rest der Pflicht SKIP.
        results = {g: _res(common.SKIP, skip_reason=common.TOOL_MISSING) for g in required}
        for g in ("B3", "D3", "F1", "H4"):
            results[g] = _res(common.PASS)
        vd = verdict.compute_verdict(required, results)
        self.assertEqual(vd["verdict"], verdict.ROT,
                         "SKIP-lastiges Profil darf nie GRUEN sein (alter False-Green-Bug)")
        self.assertGreater(len(vd["uncovered"]), 0)

    def test_green_only_when_every_required_passes(self):
        required = verdict.resolve_required(
            verdict.load_pflichtenheft(SHIPPED)["profiles"], "basis")
        vd = verdict.compute_verdict(required, _passing(required))
        self.assertEqual(vd["verdict"], verdict.GRUEN)
        self.assertEqual(len(vd["passed"]), len(required))


if __name__ == "__main__":
    unittest.main(verbosity=2)

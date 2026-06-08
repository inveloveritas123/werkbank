"""GP06 — RAG über interne Dokumente mit PII-Filter. Soll-Ist-Tests.

SPEC: Antwort fachlich korrekt · Quelle genannt · keine unnötige PII-Ausgabe ·
keine Halluzination ohne Quelle · Löschung aus Index funktioniert.
"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
GATES_DIR = os.path.abspath(os.path.join(HERE, "..", ".."))
REPO_ROOT = os.path.abspath(os.path.join(GATES_DIR, ".."))
APP_DIR = os.path.join(REPO_ROOT, "golden-projects", "06-rag-pii-filter", "app")
ARTE = os.path.join(REPO_ROOT, "golden-projects", "06-rag-pii-filter", "artefakte")
sys.path.insert(0, GATES_DIR)
sys.path.insert(0, APP_DIR)

from checks import common, e5_artefakte  # noqa: E402
import rag_index as rag  # noqa: E402


def _idx():
    ix = rag.RagIndex()
    ix.add("d1", "Die Rueckgabefrist betraegt 14 Tage ab Erhalt der Ware.", source="FAQ#rueckgabe")
    ix.add("d2", "Der Versand innerhalb Deutschlands ist kostenlos.", source="FAQ#versand")
    ix.add("d3", "Fuer Reklamationen ist Herr Max Mustermann zustaendig, "
                 "erreichbar unter max.mustermann@example.com.", source="Intern#kontakt")
    return ix


class CorrectAnswerWithSource(unittest.TestCase):
    def test_factual_answer_and_source(self):
        a = _idx().answer("Wie lange ist die Rueckgabefrist?")
        self.assertTrue(a.grounded)
        self.assertIn("14 Tage", a.text)
        self.assertEqual(a.source, "FAQ#rueckgabe")


class NoHallucination(unittest.TestCase):
    def test_unknown_question_refuses(self):
        a = _idx().answer("Welche Farbe hat der Firmenwagen?")
        self.assertFalse(a.grounded)
        self.assertIsNone(a.source)
        self.assertNotIn("14 Tage", a.text)


class NoUnnecessaryPii(unittest.TestCase):
    def test_pii_in_answer_is_redacted(self):
        a = _idx().answer("Wer ist fuer Reklamationen zustaendig?")
        self.assertTrue(a.grounded)
        self.assertEqual(a.source, "Intern#kontakt")
        self.assertNotIn("max.mustermann@example.com", a.text)
        self.assertNotIn("Max Mustermann", a.text)
        self.assertIn("[", a.text)   # Platzhalter vorhanden


class DeleteFromIndex(unittest.TestCase):
    def test_delete_removes_doc(self):
        ix = _idx()
        self.assertTrue(ix.delete("d1"))
        a = ix.answer("Wie lange ist die Rueckgabefrist?")
        self.assertFalse(a.grounded)        # Quelle weg -> keine belegte Antwort mehr


class ReviewHardening(unittest.TestCase):
    """Review-Befunde: Name-ohne-Anrede, Quelle-PII, Halluzination bei 1-Token-Überlappung."""

    def test_name_without_salutation_redacted(self):
        ix = rag.RagIndex()
        ix.add("k", "Ansprechpartner fuer Reklamationen ist Anna Schmidt.", "Intern#kontakt")
        a = ix.answer("Wer ist Ansprechpartner fuer Reklamationen?")
        self.assertTrue(a.grounded)
        self.assertNotIn("Anna Schmidt", a.text)
        self.assertIn("[NAME]", a.text)

    def test_source_pii_redacted(self):
        ix = rag.RagIndex()
        ix.add("k", "Die Garantie betraegt zwei Jahre.", source="Mail von max.mustermann@example.com")
        a = ix.answer("Wie lange ist die Garantie?")
        self.assertTrue(a.grounded)
        self.assertNotIn("max.mustermann@example.com", a.source)

    def test_single_token_overlap_refuses(self):
        ix = rag.RagIndex()
        ix.add("p", "Mitarbeiter erhalten Zugang zum Parkhaus.", "FAQ#parken")
        a = ix.answer("Welche Mitarbeiter duerfen das Firmenfahrrad nutzen?")
        self.assertFalse(a.grounded)   # nur 'mitarbeiter' geteilt -> nicht belegt


class ArtefactsComplete(unittest.TestCase):
    def test_e5_on_artefacts(self):
        res = e5_artefakte.run(ARTE, privacy_dir=ARTE,
                               required=["DATA-FLOW.md", "RETENTION-DELETION.md"])
        self.assertEqual(res.status, common.PASS, res.summary)


if __name__ == "__main__":
    unittest.main(verbosity=2)

"""GP06 — lauffähige Demo des RAG mit PII-Filter.

Lauf:  python3 demo.py [evidence_dir]
Zeigt: korrekte Antwort + Quelle · keine Halluzination ohne Quelle · PII maskiert ·
Löschung aus Index. Optional wird ein PII-freies Antwort-Log als Evidence geschrieben.
"""
import os
import sys

import rag_index as rag


def _build():
    ix = rag.RagIndex()
    ix.add("d1", "Die Rueckgabefrist betraegt 14 Tage ab Erhalt der Ware.", "FAQ#rueckgabe")
    ix.add("d2", "Der Versand innerhalb Deutschlands ist kostenlos.", "FAQ#versand")
    ix.add("d3", "Fuer Reklamationen ist Herr Max Mustermann zustaendig, "
                 "erreichbar unter max.mustermann@example.com.", "Intern#kontakt")
    return ix


def run(evidence_dir=None):
    ix = _build()
    lines = []
    for q in ["Wie lange ist die Rueckgabefrist?",
              "Wer ist fuer Reklamationen zustaendig?",
              "Welche Farbe hat der Firmenwagen?"]:
        a = ix.answer(q)
        line = "Frage: %s\n  -> %s [Quelle: %s | belegt: %s]" % (q, a.text, a.source, a.grounded)
        print(line)
        lines.append("query grounded=%s source=%s answer=%s" % (a.grounded, a.source, a.text))
    ix.delete("d1")
    after = ix.answer("Wie lange ist die Rueckgabefrist?")
    print("Nach Index-Loeschung belegt:", after.grounded)
    lines.append("after_delete grounded=%s" % after.grounded)
    if evidence_dir:
        os.makedirs(os.path.join(evidence_dir, "logs"), exist_ok=True)
        with open(os.path.join(evidence_dir, "logs", "answers.log"), "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
        print("Evidence (PII-frei) ->", evidence_dir)


if __name__ == "__main__":
    run(sys.argv[1] if len(sys.argv) > 1 else None)

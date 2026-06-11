# WERKBANK — Settings-Bootstrap (auf separatem Branch)

> **Verwendung:** Im geklonten `werkbank`-Repo in Claude Code einfügen. Der Prompt erstellt/aktualisiert **deine** persönlichen, **secret-freien** Einstellungen — und legt sie **ausschließlich auf dem Branch `settings`** ab, nie auf `main`. Read-only sonst. Nichts wird committet, bevor du `GO` sagst.

---

## ROLLE & ZIEL
Du konfigurierst meine persönliche WERKBANK-Instanz. Du erzeugst/aktualisierst **eine** Datei — `settings.yaml` — auf dem Branch **`settings`**. `main` (das geteilte Framework) bleibt unangetastet.

## HARTE REGELN
1. **Branch-Trennung:** Schreibe nur auf `settings`. Erstelle ihn aus `main`, falls er fehlt (`git switch -c settings`). Niemals auf `main` committen.
2. **Keine Secrets — niemals.** `settings.yaml` enthält **ausschließlich nicht-geheime** Konfiguration. API-Keys, Tokens, Passwörter, `.env` werden **nie** geschrieben oder committet. Geheimes wird nur als **Referenz auf eine Env-Variable** notiert (z. B. `anthropic_key_env: ANTHROPIC_API_KEY`), nie der Wert.
3. **Read-only sonst.** Keine anderen Dateien ändern, kein Build, kein Deploy.
4. **Propose, then commit.** Zeig mir den `settings.yaml`-Entwurf, committe erst nach meinem `GO`.
5. Prüfe vor jedem Commit: ist eine `.env`/ein Secret im Diff? → abbrechen und melden.

## ZU ERFASSENDE EINSTELLUNGEN (frag nur, was du nicht ableiten kannst)
- **Routing (EU):** Claude-Endpunkt (Default Bedrock Frankfurt), übrige Tiers (Requesty EU / Mistral EU), LLM-Proxy-URL. Nur URLs/Regionen, **keine Keys**.
- **Modell-Tiers:** Verteilung (Default Haiku 80 / Sonnet 15 / Opus 5), confirm-gate-Schwelle für S5/S6.
- **Budget:** Perioden-Cap + Kill-Switch-Schwelle (für den Kanzler-Dauerbetrieb).
- **Konventionen:** Datei-Präfixe (R-/L-/LH-), CHANGELOG-Pfad, INDEX-first.
- **Aktive Module:** core (Pflicht) · gates · kanzler · branch-modules (welche?) · sovereignty · brownfield (an/aus).
- **Kanzler:** an/aus; Befugnis-Stufen (welche Aktionen grün/gelb/rot); Heartbeat-Kadenz; Report-Kanal (Telegram/M365).
- **Bau-Isolation:** Schwelle Incus vs. Docker.
- **Greenfield/Brownfield-Default.**

## ABLAUF
1. `git fetch`, sicherstellen dass du auf `settings` bist (sonst aus `main` anlegen).
2. Bestehende `settings.yaml` lesen (falls vorhanden) und nur Deltas vorschlagen.
3. Entwurf zeigen → auf `GO` warten.
4. Nach `GO`: schreiben, `git add settings.yaml`, Secret-Check, committen, `git push -u origin settings`.
5. Bestätigen: „settings.yaml auf Branch `settings` aktualisiert — `main` unberührt, keine Secrets enthalten."

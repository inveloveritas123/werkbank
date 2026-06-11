# Sichere Installation

`curl -fsSL .../bootstrap.sh | bash` lädt ein Skript aus dem Netz und führt es
**ungeprüft** aus ("curl | bash blind execution"). Wer pipt, vertraut blind dem
Server, dem Transportweg und dem aktuellen Stand des Default-Branches (`main`).
Das ist bequem — und für Wegwerf-/Testsysteme vertretbar —, aber für echte oder
Kundensysteme die falsche Voreinstellung.

Dieses Dokument beschreibt den gehärteten Weg.

## TL;DR — der empfohlene Weg für echte/Kundensysteme

```bash
# 1) Herunterladen, gepinnt auf einen RELEASE-TAG (nicht 'main'):
curl -fsSL https://raw.githubusercontent.com/inveloveritas123/werkbank/v1.0/bootstrap.sh -o bootstrap.sh

# 2) Prüfsumme gegen den veröffentlichten Hash vergleichen:
shasum -a 256 bootstrap.sh        # mit veroeffentlichtem Hash vergleichen

# 3) Selbst lesen — verstehen, was läuft:
less bootstrap.sh

# 4) Erst dann ausführen, gepinnt auf denselben Ref:
WERKBANK_REF=v1.0 bash bootstrap.sh
```

Warum das hilft:
- **Pinnen auf einen Tag** statt `main` → reproduzierbar; `main` kann sich zwischen
  zwei Installationen ändern (oder kompromittiert werden), ein Release-Tag nicht.
- **Herunterladen + Hash-Vergleich** → erkennt manipulierten Transport oder Server.
- **Selbst lesen** → kein blindes Vertrauen; du führst nur aus, was du gesehen hast.

## Umgebungsvariablen

| Variable | Default | Wirkung |
|---|---|---|
| `WERKBANK_REF` | `main` | git-Ref (Tag/Branch/Commit), der installiert wird. Beim Klon via `git clone --depth 1 --branch "$WERKBANK_REF"` (akzeptiert auch Tags). Ein **bestehender** Klon wird per `git fetch --depth 1 origin "$WERKBANK_REF"` + `git checkout`/`git reset --hard FETCH_HEAD` deterministisch auf genau diesen Ref bewegt. |
| `WERKBANK_EXPECT_SHA` | _(leer)_ | Optionaler harter Integritäts-Pin. Nach Klon/Checkout wird der tatsächliche Commit (`git rev-parse HEAD`) mit diesem Wert verglichen. Bei Abweichung **Abbruch** vor jedem Setup. |
| `WERKBANK_REPO` | `https://github.com/inveloveritas123/werkbank.git` | Quell-Repository (z. B. für Mirror/Fork). |
| `WERKBANK_HOME` | `~/werkbank` | Zielverzeichnis des Klons. |

Der Installer gibt unabhängig vom Pin den aufgelösten Commit aus:

```
▶ WERKBANK @ <sha> (ref=<ref>)
```

So siehst du **exakt**, welcher Stand installiert wurde.

## Hartes Pinnen auf einen Commit

Für maximale Reproduzierbarkeit Ref **und** SHA gemeinsam pinnen:

```bash
WERKBANK_REF=v1.0 \
WERKBANK_EXPECT_SHA=<commit-sha-des-tags> \
bash bootstrap.sh
```

Stimmt der ausgecheckte Commit nicht mit `WERKBANK_EXPECT_SHA` überein, bricht der
Installer ab, **bevor** `werkbank-init.sh` läuft — es wird nichts eingerichtet.

## Update-Pfad

Ein bereits vorhandener Klon (`$WERKBANK_HOME/.git`) wird nicht mehr blind
`git pull --ff-only` gemacht, sondern deterministisch auf `$WERKBANK_REF` gesetzt:

```bash
git -C "$WERKBANK_HOME" fetch --depth 1 origin "$WERKBANK_REF"
git -C "$WERKBANK_HOME" checkout --force FETCH_HEAD
git -C "$WERKBANK_HOME" reset --hard FETCH_HEAD
```

Damit landet ein bestehender Klon auf demselben gepinnten Stand wie eine
Neuinstallation — kein Drift durch lokale Branch-Historie.

## Wegwerf-/Testsysteme

Wer nur schnell ausprobieren will, kann weiter pipen:

```bash
curl -fsSL https://raw.githubusercontent.com/inveloveritas123/werkbank/main/bootstrap.sh | bash
```

Das ist bewusst weiterhin möglich — nur eben **nicht** für Produktiv- oder
Kundensysteme empfohlen.

# PyPI-Demo: erste Veröffentlichung ohne dauerhaftes Registry-Token

Recherche: 7. Oktober 2026. Ziel: ein Wheel und eine Quelldistribution auf **TestPyPI** publizieren, anschließend Herkunft und Integrität prüfen. Für die eigentliche Veröffentlichung braucht diese Demo GitHub Actions. Ein lokaler Probelauf prüft Paketbau und Tests, führt aber keinen OIDC-Austausch aus.

## 1. Eigenes Repository vorbereiten

Den Inhalt dieses Ordners einschließlich `.github` in das Wurzelverzeichnis eines eigenen GitHub-Repositorys kopieren. Der Workflow erwartet den Standardbranch `main`. Für einen anderen Branch die Bedingung im Publish-Job anpassen.

In `pyproject.toml` den Distributionsnamen `tp-python-your-unique-name` durch einen freien, eigenen Namen ersetzen, beispielsweise `tp-python-fd-20261007-abc123`. Der Python-Importname `tp_demo` bleibt gleich. Spätere Veröffentlichungen benötigen eine neue Versionsnummer. Ein bereits belegter Dateiname lässt sich bei PyPI und TestPyPI nicht durch eine neue Datei ersetzen.

## 2. Lokal bauen und prüfen

Python ab 3.11 installieren. Die folgenden Befehle gelten für PowerShell; unter Linux/macOS statt `.venv/Scripts/python.exe` jeweils `.venv/bin/python` nutzen.

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install build twine
.venv/Scripts/python.exe -m build
.venv/Scripts/python.exe -m twine check --strict dist/*
.venv/Scripts/python.exe -m pip install --no-deps .
.venv/Scripts/python.exe -m unittest discover -s tests -v
```

Hinweis zu PowerShell: Falls `twine` die Wildcard nicht auflöst, die beiden vollständigen Dateinamen aus `dist` als Argumente angeben. `python -m build` erstellt eine isolierte Build-Umgebung und lädt das deklarierte Build-Backend. Für reproduzierbare Produktionsreleases zusätzlich die Build-Abhängigkeiten festlegen und per Hash absichern.

## 3. TestPyPI und GitHub verbinden

1. Eigenes Konto unter https://test.pypi.org/ anlegen und die erforderlichen Kontosicherheitsmaßnahmen abschließen. PyPI und TestPyPI besitzen getrennte Konten und Konfigurationen.
2. In GitHub unter **Settings → Environments** ein Environment namens `testpypi` anlegen. Deployments auf `main` einschränken und, soweit für Konto und Repository verfügbar, eine manuelle Freigabe einrichten. Der Name allein stellt noch keine Schutzregel dar.
3. https://test.pypi.org/manage/account/publishing/ öffnen und einen **pending publisher** eintragen:

| Feld | Wert |
|---|---|
| PyPI Project Name | Der neue Name aus `pyproject.toml` |
| Owner | GitHub-Benutzer oder Organisation |
| Repository name | Name des eigenen GitHub-Repositorys |
| Workflow name | `publish-testpypi.yml` |
| Environment name | `testpypi` |

Der Workflowname meint den Dateinamen, nicht den Text hinter YAML-`name:`. Der pending publisher reserviert den Paketnamen nicht. Erst der erste erfolgreiche Upload legt das Projekt an.

## 4. Workflow ausführen

Änderungen auf `main` committen und hochladen. Auf GitHub unter **Actions → Python Trusted Publishing demo → Run workflow** zunächst `publish` abgewählt lassen. Der Build erstellt Wheel und sdist, prüft die Metadaten und testet das gebaute Wheel. Das Ergebnis liegt als Workflow-Artefakt vor.

Danach auf `main` mit aktivierter Option `publish` starten und eine gegebenenfalls konfigurierte Freigabe erteilen. Dieser Lauf **veröffentlicht tatsächlich** auf TestPyPI. Der Publish-Job lädt nur die fertigen Artefakte. Ausschließlich dieser Job erhält `id-token: write`. Der PyPA-Schritt erledigt Tokenaustausch und Upload; `repository-url` wählt TestPyPI samt passender Audience. Kein `password`, kein `PYPI_API_TOKEN` und keine `.pypirc` ergänzen.

Die Action erzeugt standardmäßig PyPI-Publish-Attestierungen. Das ist ein Nachweis über veröffentlichende Identität und Dateidigest, kein automatischer Nachweis eines isolierten oder reproduzierbaren Builds.

## 5. Attestierung überprüfen

Nach dem erfolgreichen Upload:

```powershell
.venv/Scripts/python.exe -m pip install pypi-attestations
.venv/Scripts/python.exe verify_testpypi.py DEIN-PAKETNAME --repository https://github.com/OWNER/REPO
```

Das Skript lädt genau das Wheel und dessen Provenance-Objekt von TestPyPI. Es installiert und startet das heruntergeladene Paket nicht. Anschließend prüft das offizielle CLI die lokale Datei gegen das Provenance-Objekt und das erwartete Repository. Für spätere Releases `--version 0.0.2` ergänzen.

Zwei Negativproben:

```powershell
.venv/Scripts/python.exe verify_testpypi.py DEIN-PAKETNAME --repository https://github.com/OWNER/FALSCH
.venv/Scripts/python.exe verify_testpypi.py DEIN-PAKETNAME --repository https://github.com/OWNER/REPO --tamper
```

Erwartung: Beide Aufrufe schlagen mit einem Exit-Code ungleich null fehl. Die erste Probe verletzt die Identitätserwartung; die zweite verändert lokal die Datei nach dem Download. Ein bloßes Anzeigen des JSON entspricht keiner kryptografischen Prüfung. Die `pypi-attestations`-CLI ist ausdrücklich experimentell; für langfristige Integration deren API und aktuelle Dokumentation prüfen.

## Grenzen und Versionen

`pypa/gh-action-pypi-publish` ist auf den verifizierten Commit von v1.14.2 festgelegt. Die übrigen Action-Major-Tags stammen aus dem aktuellen PyPA-Guide. Für einen Produktivworkflow auch diese auf geprüfte vollständige Commit-SHAs pinnen und Updates verwalten. Das Environment mit Schutzregeln, Berechtigungen für Workflowänderungen und Reviewregeln gehören ebenfalls zur Vertrauensentscheidung.

Der Publish-Job nutzt einen GitHub-Ubuntu-Runner. Die PyPA-Action läuft nur in Linux-Jobs; Self-hosted Runner behandelt sie als Best Effort. Reusable Workflows für den eigentlichen Trusted-Publishing-Schritt führt die Action-Dokumentation weiterhin als nicht freigegeben.

**Prüfstatus bei Erstellung:** Syntax, Paketbau über das lokal vorhandene setuptools-Backend, Import und Unit-Test lokal geprüft. Kein GitHub-Workflow gestartet, keine Registry-Veröffentlichung, kein Live-OIDC-Austausch und keine echte Attestierungsprüfung ausgeführt. `verify_testpypi.py` ist syntaxgeprüft; sein Live-Lauf setzt den eigenen TestPyPI-Upload voraus.

## Primärquellen

- https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/
- https://docs.pypi.org/trusted-publishers/using-a-publisher/
- https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/
- https://github.com/pypa/gh-action-pypi-publish
- https://github.com/pypa/gh-action-pypi-publish/releases
- https://docs.pypi.org/attestations/consuming-attestations/
- https://docs.pypi.org/api/integrity/
- https://github.com/pypi/pypi-attestations

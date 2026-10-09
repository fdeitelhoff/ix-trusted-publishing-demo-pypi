# Realer Durchlauf – 9. Oktober 2026

Distribution `ix-trusted-publishing-demo-pypi` (Importname `tp_demo`), Repository https://github.com/fdeitelhoff/ix-trusted-publishing-demo-pypi (öffentlich, Environment `testpypi` mit Pflicht-Reviewer und Deployment nur von `main`).

| Punkt | Ergebnis |
|---|---|
| Lokale Prüfung | Windows, Python 3.11.3, build 1.6.1, twine 7.0.0: `python -m build`, `twine check --strict` (Wheel + sdist PASSED), Installation, `unittest` (1/1) erfolgreich |
| Pending Publisher | TestPyPI, GitHub, `fdeitelhoff` / `ix-trusted-publishing-demo-pypi`, `publish-testpypi.yml`, Environment `testpypi` |
| Build-Lauf (`publish` abgewählt) | https://github.com/fdeitelhoff/ix-trusted-publishing-demo-pypi/actions/runs/37950005767 – Build 16 s, Publish-Job übersprungen |
| Erster Publish-Lauf | https://github.com/fdeitelhoff/ix-trusted-publishing-demo-pypi/actions/runs/37959472474 – fehlgeschlagen: `invalid-publisher: valid token, but no corresponding publisher`; Ursache: Eintrag im Pending Publisher stimmte nicht, nach Korrektur erneut gestartet |
| Zweiter Publish-Lauf | https://github.com/fdeitelhoff/ix-trusted-publishing-demo-pypi/actions/runs/37960523219 – Build 15 s, Publish 22 s nach Environment-Freigabe; Commit `94c101d781e7da3a13cd1cdc7a5601ef757a3abe` |
| Projektseite | https://test.pypi.org/project/ix-trusted-publishing-demo-pypi/0.0.1/ |
| Wheel | `ix_trusted_publishing_demo_pypi-0.0.1-py3-none-any.whl`, SHA-256 `0669b217537c3fde4a27e430b1aa3ae36ebfa5b67ddf45f2edbe1109602552eb` |
| sdist | `ix_trusted_publishing_demo_pypi-0.0.1.tar.gz`, SHA-256 `40e8409f50af92c24d02c7d5febcea3599576d36b04685a6d24db5c6e71a86bd`, Provenance ebenfalls vorhanden |
| Provenance-Inhalt | Predicate `https://docs.pypi.org/attestations/publish/v1`; Publisher `GitHub`, Repository, Workflow `publish-testpypi.yml`, Environment `testpypi`; Subject = Wheel-Digest; Rekor-Eintrag 3167854358 |
| Prüfung | `verify_testpypi.py` mit pypi-attestations 0.0.30: `OK: …whl`, Exit 0 |
| Negativprobe Repository | `--repository …/FALSCH`: „provenance was signed by repository "fdeitelhoff/ix-trusted-publishing-demo-pypi", expected "fdeitelhoff/FALSCH"“, Exit 1 |
| Negativprobe Manipulation | `--tamper`: „subject does not match distribution digest“, Exit 1 |

Beobachtungen, die das README nicht nennt:

- Ein falsch eingetragener Pending Publisher führt zu `invalid-publisher`. Die Action gibt dabei die Claims des OIDC-Tokens aus (`repository`, `repository_owner_id`, `workflow_ref`, `environment` usw.), was die Fehlersuche erleichtert. Beim Fehlversuch wurde nichts hochgeladen und kein Projekt angelegt; jeder neue Versuch braucht eine erneute Environment-Freigabe.
- GitHub stellt für neue Repositorys standardmäßig den unveränderlichen Subject-Claim aus (`use_immutable_subject: true`, `sub` = `repo:fdeitelhoff@1618135/ix-trusted-publishing-demo-pypi@1412042244:environment:testpypi`). TestPyPI hat diesen Claim akzeptiert.
- Anders als bei npm waren Dateien und Provenance unmittelbar nach dem Lauf über die JSON- und Integrity-API abrufbar.
- Die PyPA-Action prüft vor dem Upload selbst noch einmal die Metadaten (`twine check`) und meldet „Generating and uploading digital attestations“.
- GitHub-Warnung im Build-Job: `actions/upload-artifact@v5` zielt auf Node.js 20 und wird zwangsweise unter Node.js 24 ausgeführt.
- Die Publish-Attestierung (`publish/v1`) hat ein leeres Predicate; das Statement selbst nennt nur Dateiname und Digest. Commit `94c101d…`, Workflow-Ref `…/publish-testpypi.yml@refs/heads/main` und Run-URL `…/actions/runs/37960523219/attempts/1` stehen stattdessen im Sigstore-Signaturzertifikat. Bei npm (`slsa.dev/provenance/v1`) stehen diese Angaben im Predicate.

Nicht ausgeführt: Veröffentlichung auf dem echten PyPI, zweite Version mit `--version`, Negativtest mit abweichendem Environmentnamen.

# MITRE and STICKS Boundary

The local machine contains STICKS/STICKS-Docker artifacts outside this
repository. ArenaWealth Pro is a portfolio-analysis artifact and does not
execute MITRE ATT&CK campaigns.

## Why This Boundary Matters

Mixing STICKS claims into ArenaWealth would mislead reviewers. Security campaign
coverage belongs to the STICKS artifact. ArenaWealth can reuse the same
reproducibility discipline: quickstart, coverage matrices, claim-evidence
traceability, runtime context, and paper-value synchronization.

## If a Paper Combines Both Artifacts

- Treat STICKS as an external artifact with its own repository, setup, and
  evidence package.
- Import only explicit, versioned outputs from STICKS.
- Do not copy MITRE campaign claims into this repository unless executable
  campaign code and data are added here.
- Keep investment claims and cybersecurity campaign claims in separate tables.

## Current Status

No MITRE executor, campaign corpus, or STICKS runtime is part of ArenaWealth Pro.

# UI-FACTORY-003 — Professor cold-start acceptance

Date: 2026-07-31 KST  
Owner task: `019fb1f6-6913-7020-92cb-852d57d4f8d1`  
Settings: `IDX-URP4-1-DEMO-OPT / CFG-DEMO-OPT-FACTORY-v0.4 r4`  
Status: `passed`

## Delivery contract

The delivery unit is one ZIP. The recipient must extract the whole ZIP and
start only the package-root `START_HERE.cmd`. No individual source file should
be moved outside the extracted root.

`START_HERE.cmd`:

1. resolves a package-local pointer, explicitly supplied path, common conda
   location, or restricted project-local KMK312 search result;
2. runs Python/import/protected-source/package-manifest preflight fail-closed;
3. prints `http://127.0.0.1:8765/`;
4. starts the copied local server and opens that URL;
5. leaves shutdown under the user's foreground `Ctrl+C`.

All executable program paths are derived from `%~dp0`, the extracted package
root. The Python environment is not duplicated in the ZIP.

If automatic discovery is unavailable, `CONFIGURE_KMK312_PATH.cmd` records only
the selected interpreter location in package-local `KMK312_PATH.txt`, then
replays preflight. The environment itself remains external and unchanged.

## Acceptance evidence

- builder/acceptance scripts compile under canonical KMK312 / Python 3.12.12;
- package-root `START_HERE.cmd --check-only`: PASS;
- conservative Windows runtime-path budget checked before server start;
- local HTTP `capabilities` and `default-request`: PASS;
- performance target remains fail-closed;
- ZIP extracted under a path containing spaces and Korean characters: PASS;
- one-candidate smoke from that relocated extraction: PASS;
- relocated package Engineer Console regression: 13/13 PASS;
- no server process remains after the acceptance probe.

## User-visible entry points

- `00_먼저_읽어주세요.txt`
- `START_HERE.cmd`
- `PROFESSOR_QUICKSTART.md`
- `FACTORY_URL.txt`
- Engineer view → `05 Run inspector`

## Claim boundary

This acceptance proves portable technical execution of the current
`structural target → Type-A theta search → STL/evidence` development route.
It does not prove a performance-driven inverse map, physical performance,
printability, or scientific production qualification.

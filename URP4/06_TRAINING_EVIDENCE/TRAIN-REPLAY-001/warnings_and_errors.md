# TRAIN-REPLAY-001 warnings and errors

## Attempt 1 — preserved compatibility failure

- Status: `BLOCKED_WITH_EVIDENCE`
- Cause: Windows MAX_PATH prevented a nested output filename from opening.
- Scientific calculation had not started; three code cells passed.
- Evidence: `a1/state.json`, `a1/executed.ipynb`, `a1/cells.csv`.

## Attempt 2 — notebook error outputs

- None.

## Runtime warnings

- Exception in thread Thread-1 (_readerthread):
- Traceback (most recent call last):
-   File "C:\Users\chuck\Documents\Codex\2026-06-22\a2f23dee1d9a824b840a0175ca9a1f4b-https-app-notion-com-p\tools\envs\KMK312\Lib\threading.py", line 1075, in _bootstrap_inner
-     self.run()
-   File "C:\Users\chuck\Documents\Codex\2026-06-22\a2f23dee1d9a824b840a0175ca9a1f4b-https-app-notion-com-p\tools\envs\KMK312\Lib\threading.py", line 1012, in run
-     self._target(*self._args, **self._kwargs)
-   File "C:\Users\chuck\Documents\Codex\2026-06-22\a2f23dee1d9a824b840a0175ca9a1f4b-https-app-notion-com-p\tools\envs\KMK312\Lib\subprocess.py", line 1599, in _readerthread
-     buffer.append(fh.read())
-                   ^^^^^^^^^
-   File "<frozen codecs>", line 322, in decode
- UnicodeDecodeError: 'utf-8' codec can't decode byte 0xbf in position 266: invalid start byte
- C:\Users\chuck\Documents\Codex\2026-06-22\a2f23dee1d9a824b840a0175ca9a1f4b-https-app-notion-com-p\tools\envs\KMK312\Lib\site-packages\zmq\_future.py:718: RuntimeWarning: Proactor event loop does not implement add_reader family of methods required for zmq. Registering an additional selector thread for add_reader support via tornado. Use `asyncio.set_event_loop_policy(WindowsSelectorEventLoopPolicy())` to avoid this warning.
-   self._get_loop()

## Interpretation boundary

- Runtime warnings are recorded, not silently discarded.
- The Windows path junction is a declared I/O compatibility delta only.
- No target, feature, split, seed, estimator, hyperparameter, or metric was changed.

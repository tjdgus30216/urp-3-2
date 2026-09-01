# Runtime path discovery correction

- Incorrect discovery statement: KMK312 was thought absent because only user-profile Anaconda paths were searched.
- Correct canonical runtime: `tools/envs/KMK312/python.exe` inside the URP4-1 project.
- Verified version: Python 3.12.12 packaged by Anaconda.
- The partial duplicate under `C:\Users\chuck\anaconda3\envs\KMK312` is quarantined and never selected.
- No previous KMK312 execution, scientific evidence or result was changed or invalidated.

from __future__ import annotations

import contextlib
import os
from dataclasses import dataclass
from unittest.mock import patch


@dataclass
class CallCounter:
    attempted_fit: int = 0
    attempted_predict: int = 0
    completed_fit: int = 0
    completed_predict: int = 0


class NoFitViolation(RuntimeError):
    pass


class NoFitGuard:
    def __init__(self) -> None:
        self.counter = CallCounter()

    def _deny_fit(self, *_args, **_kwargs):
        self.counter.attempted_fit += 1
        raise NoFitViolation("NO_FIT_GUARD: estimator.fit() prohibited in TRAIN-PARITY-002")

    def _deny_predict(self, *_args, **_kwargs):
        self.counter.attempted_predict += 1
        raise NoFitViolation("NO_FIT_GUARD: estimator.predict() prohibited in TRAIN-PARITY-002")

    @contextlib.contextmanager
    def patch_known_estimators(self):
        targets = [
            "sklearn.linear_model.Ridge.fit",
            "sklearn.linear_model.Ridge.predict",
            "sklearn.linear_model.ElasticNetCV.fit",
            "sklearn.linear_model.ElasticNetCV.predict",
            "sklearn.linear_model.BayesianRidge.fit",
            "sklearn.linear_model.BayesianRidge.predict",
            "sklearn.linear_model.HuberRegressor.fit",
            "sklearn.linear_model.HuberRegressor.predict",
            "sklearn.cross_decomposition.PLSRegression.fit",
            "sklearn.cross_decomposition.PLSRegression.predict",
            "sklearn.kernel_ridge.KernelRidge.fit",
            "sklearn.kernel_ridge.KernelRidge.predict",
            "sklearn.svm.SVR.fit",
            "sklearn.svm.SVR.predict",
        ]
        stack = contextlib.ExitStack()
        try:
            for target in targets:
                stack.enter_context(patch(target, self._deny_fit if target.endswith(".fit") else self._deny_predict))
            yield self
        finally:
            stack.close()

    def proof(self) -> dict[str, int | str]:
        return {
            "execution_status": "no_fit_no_prediction",
            "attempted_fit_calls": self.counter.attempted_fit,
            "attempted_predict_calls": self.counter.attempted_predict,
            "completed_fit_calls": self.counter.completed_fit,
            "completed_predict_calls": self.counter.completed_predict,
        }


def assert_runtime_contract() -> None:
    required = {
        "PYTHONHASHSEED": "42",
        "OMP_NUM_THREADS": "1",
        "MKL_NUM_THREADS": "1",
        "OPENBLAS_NUM_THREADS": "1",
        "NUMEXPR_NUM_THREADS": "1",
        "CUDA_VISIBLE_DEVICES": "-1",
    }
    drift = {key: (os.environ.get(key), value) for key, value in required.items() if os.environ.get(key) != value}
    if drift:
        raise RuntimeError(f"RUNTIME_CONTRACT_MISMATCH: {drift}")

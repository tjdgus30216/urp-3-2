from __future__ import annotations

import contextlib
from dataclasses import dataclass
from unittest.mock import patch


class NoFitViolation(RuntimeError):
    pass


@dataclass
class Counters:
    attempted_fit: int = 0
    attempted_predict: int = 0
    completed_fit: int = 0
    completed_predict: int = 0


class NoFitGuard:
    def __init__(self):
        self.counters = Counters()

    def deny_fit(self, *_args, **_kwargs):
        self.counters.attempted_fit += 1
        raise NoFitViolation("NO_FIT_GUARD")

    def deny_predict(self, *_args, **_kwargs):
        self.counters.attempted_predict += 1
        raise NoFitViolation("NO_PREDICT_GUARD")

    @contextlib.contextmanager
    def active(self):
        targets = [
            "sklearn.linear_model.Ridge.fit", "sklearn.linear_model.Ridge.predict",
            "sklearn.linear_model.LassoCV.fit", "sklearn.linear_model.LassoCV.predict",
            "sklearn.linear_model.ElasticNetCV.fit", "sklearn.linear_model.ElasticNetCV.predict",
            "sklearn.linear_model.BayesianRidge.fit", "sklearn.linear_model.BayesianRidge.predict",
            "sklearn.linear_model.HuberRegressor.fit", "sklearn.linear_model.HuberRegressor.predict",
            "sklearn.cross_decomposition.PLSRegression.fit", "sklearn.cross_decomposition.PLSRegression.predict",
            "sklearn.kernel_ridge.KernelRidge.fit", "sklearn.kernel_ridge.KernelRidge.predict",
            "sklearn.svm.SVR.fit", "sklearn.svm.SVR.predict",
        ]
        with contextlib.ExitStack() as stack:
            for target in targets:
                stack.enter_context(patch(target, self.deny_fit if target.endswith(".fit") else self.deny_predict))
            yield self

"""Adapters around third-party baselines."""

from revision_context.baselines.stub_model import PLACEHOLDER_PREDICTION, predict_with_stub_model

__all__ = ["PLACEHOLDER_PREDICTION", "predict_with_stub_model"]

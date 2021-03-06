# Lint as: python3
# Copyright 2019 DeepMind Technologies Limited. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""JAX implementation of common losses.

Deep reinforcement learning algorithms are often expressed as gradients of
suitable pseudo-loss functions constructed from the observations and rewards
collected in the environment. In this subpackage we collate common mathematical
transformations used to construct such losses.
"""

from typing import Optional
import jax.numpy as jnp
from rlax._src import base

ArrayLike = base.ArrayLike


def l2_loss(predictions: ArrayLike,
            targets: Optional[ArrayLike] = None) -> ArrayLike:
  """Caculates the L2 loss of predictions wrt targets.

  If targets are not provided this function acts as an L2-regularizer for preds.

  Note: the 0.5 term is standard in "Pattern Recognition and Machine Learning"
  by Bishop, but not "The Elements of Statistical Learning" by Tibshirani.

  Args:
    predictions: a vector of arbitrary shape.
    targets: a vector of shape compatible with predictions.

  Returns:
    a vector of same shape of `predictions`.
  """
  if targets is None:
    targets = jnp.zeros_like(predictions)
  base.type_assert([predictions, targets], float)
  return 0.5 * (predictions - targets)**2


def likelihood(predictions: ArrayLike, targets: ArrayLike) -> ArrayLike:
  """Calculates the likelihood of predictions wrt targets.

  Args:
    predictions: a vector of arbitrary shape.
    targets: a vector of shape compatible with predictions.

  Returns:
    a vector of same shape of `predictions`.
  """
  base.type_assert([predictions, targets], float)
  likelihood_vals = predictions**targets * (1. - predictions)**(1. - targets)
  # Note: 0**0 evaluates to NaN on TPUs, manually set these cases to 1.
  filter_indices = jnp.logical_or(
      jnp.logical_and(targets == 1, predictions == 1),
      jnp.logical_and(targets == 0, predictions == 0))
  return jnp.where(filter_indices, 1, likelihood_vals)


def log_loss(
    predictions: ArrayLike,
    targets: ArrayLike,
) -> ArrayLike:
  """Calculates the log loss of predictions wrt targets.

  Args:
    predictions: a vector of probabilities of arbitrary shape.
    targets: a vector of probabilities of shape compatible with predictions.

  Returns:
    a vector of same shape of `predictions`.
  """
  base.type_assert([predictions, targets], float)
  return -jnp.log(likelihood(predictions, targets))

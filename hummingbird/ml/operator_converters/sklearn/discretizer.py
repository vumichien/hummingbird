# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
Converter for scikit-learn discretizers: Binarizer and KBinsDiscretizer.
"""
import torch
import numpy as np
from onnxconverter_common.registration import register_converter
from .._base_operator import BaseOperator
from .._discretizer_implementations import Binarizer, KBinsDiscretizer


def convert_sklearn_binarizer(operator, device, extra_config):
    """
    Converter for `sklearn.preprocessing.Binarizer`

    Args:
        operator: An operator wrapping a `sklearn.preprocessing.Binarizer` model
        device: String defining the type of device the converted operator should be run on
        extra_config: Extra configuration used to select the best conversion strategy

    Returns:
        A PyTorch model
    """
    return Binarizer(operator.raw_operator.threshold, device)


def convert_sklearn_k_bins_discretizer(operator, device, extra_config):
    """
        Converter for `sklearn.preprocessing.KBinsDiscretizer`

        Args:
            operator: An operator wrapping a `sklearn.preprocessing.KBinsDiscretizer` model
            device: String defining the type of device the converted operator should be run on
            extra_config: Extra configuration used to select the best conversion strategy

        Returns:
            A PyTorch model
        """
    bin_edges = []
    max_bin_edges = 0
    labels = []
    for x in operator.raw_operator.bin_edges_:
        bin_edges.append(x.flatten().tolist())
        max_bin_edges = max(max_bin_edges, len(bin_edges[-1]))

    for i in range(len(bin_edges)):
        labels.append(np.array([i for i in range(len(bin_edges[i]) - 1)]))
        if len(bin_edges[i]) < max_bin_edges:
            bin_edges[i] = (
                [bin_edges[i][0]]
                + bin_edges[i][1:-1]
                + [np.inf for _ in range((max_bin_edges - len(bin_edges[i])))]
                + [bin_edges[i][-1]]
            )

    return KBinsDiscretizer(operator.raw_operator.encode, np.array(bin_edges), labels, device)


register_converter("SklearnBinarizer", convert_sklearn_binarizer)
register_converter("SklearnKBinsDiscretizer", convert_sklearn_k_bins_discretizer)

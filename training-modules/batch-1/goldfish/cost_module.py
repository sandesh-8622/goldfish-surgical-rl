"""
goldfish.cost_module

biological cost functions for surgical needle insertion.
every threshold is taken from a real biomechanics paper.
"""

import numpy as np


# all thresholds in this module are cited
THRESHOLDS = {
    "max_strain":         0.20,   # Fung 1993, soft tissue ultimate strain
    "max_force_N":        4.0,    # Okamura et al 2004, needle insertion
    "min_vascular_mm":    3.0,    # Abolhassani et al 2007, safe margin
    "max_inflammation":   0.60,   # DiMaio and Salcudean 2003
}


class TissueTraumaCost:
    """penalty for excessive strain and insertion force."""

    def __init__(self, strain_weight=1.0, force_weight=0.5):
        self.strain_weight = strain_weight
        self.force_weight = force_weight

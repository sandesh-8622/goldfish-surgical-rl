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

    def compute(self, strain, force_N):
        strain_pen = 0.0
        if strain > THRESHOLDS["max_strain"]:
            strain_pen = self.strain_weight * (strain / THRESHOLDS["max_strain"]) ** 2
        force_pen = 0.0
        if force_N > THRESHOLDS["max_force_N"]:
            force_pen = self.force_weight * (force_N / THRESHOLDS["max_force_N"]) ** 2
        return strain_pen + force_pen



class VascularProximityCost:
    """penalty for needle approaching blood vessels too closely."""

    def __init__(self, min_distance_mm=3.0, weight=2.0):
        self.min_distance_mm = min_distance_mm
        self.weight = weight

    def compute(self, distance_mm):
        if distance_mm >= self.min_distance_mm:
            return 0.0
        # quadratic penalty as distance shrinks below threshold
        deficit = self.min_distance_mm - distance_mm
        return self.weight * (deficit / self.min_distance_mm) ** 2



class InflammationModel:
    """cumulative trauma to inflammation response estimate.

    based on DiMaio and Salcudean 2003. trauma accumulates; inflammation
    is a saturating function of total trauma.
    """

    def __init__(self, saturation=0.6):
        self.saturation = saturation
        self.cumulative_trauma = 0.0

    def update(self, trauma_step):
        self.cumulative_trauma += max(0.0, trauma_step)
        # saturating exponential
        return self.saturation * (1.0 - np.exp(-self.cumulative_trauma / 5.0))

    def reset(self):
        self.cumulative_trauma = 0.0



class BiologicalCostModule:
    """combined cost from trauma, vascular proximity, and inflammation.

    this is the thing the env actually calls each step. it wraps the
    individual cost components and returns a single scalar plus a dict
    of components for logging.
    """

    def __init__(self):
        self.trauma   = TissueTraumaCost()
        self.vascular = VascularProximityCost()
        self.inflam   = InflammationModel()

    def reset(self):
        self.inflam.reset()

    def compute(self, strain, force_N, vascular_distance_mm):
        t = self.trauma.compute(strain, force_N)
        v = self.vascular.compute(vascular_distance_mm)
        i = self.inflam.update(t)
        total = t + v + (i if i > THRESHOLDS["max_inflammation"] else 0.0)
        return total, {"trauma": t, "vascular": v, "inflammation": i}

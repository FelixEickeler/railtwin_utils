# 20/06/2024$ -----------------------------------------------------------------------------------------------------
#  created by: felix 
#              felix.eickeler@obermeyer-group.com    
# ----------------------------------------------------------------------------------------------------------------
#
import numpy as np
import pandas as pd
import scipy.interpolate
from scipy.interpolate import BSpline

from src.io.patches.strict_pos import ensure_strict_pos
from src.common.logger import getLogger

logger = getLogger()
logger.setLevel("DEBUG")


class Spline2D:

    @classmethod
    def build(cls, x, y, mse_threshold=0.001, error_threshold=0.0001):
        assert len(x) > 5 and len(y) > 5, "Not enough data points for spline interpolation"
        if isinstance(x, pd.DataFrame) or isinstance(x, pd.Series):
            x = x.to_numpy()
        if isinstance(y, pd.DataFrame) or isinstance(y, pd.Series):
            y = y.to_numpy()

        x = ensure_strict_pos(x)
        y = ensure_strict_pos(y)
        s = error_threshold / 256  # first guess
        # noinspection PyUnresolvedReferences
        tck = scipy.interpolate.splrep(x=x, y=y, s=s)
        mse = 1e12
        max_error = 1e12
        for i in range(50):
            # noinspection PyUnresolvedReferences
            p2spline_distance = y - scipy.interpolate.splev(x, tck)
            mse = np.mean(p2spline_distance ** 2) / len(p2spline_distance)
            max_error = np.max(np.abs(p2spline_distance))

            if mse < mse_threshold and max_error < error_threshold:
                logger.info(f"Spline fit successful after {i + 1} iterations with {len(tck[0])} knots, mse={mse}, max_error={max_error}")
                break
            else:
                logger.debug(f"Trying l={len(tck[0])}, mse={mse}, max_error={max_error}")

            s = s / 8
            # noinspection PyUnresolvedReferences
            tck = scipy.interpolate.splrep(x=x, y=y, s=s)
        return cls(tck, mse, max_error, mse_threshold, error_threshold)

    def __init__(self, tck, mse, max_error, mse_threshold=0.001, error_threshold=0.0001):
        self._spline = BSpline(tck[0], tck[1], tck[2])
        self.requested_mse_threshold = mse_threshold
        self.requested_error_threshold = error_threshold
        self.mse_error = mse
        self.max_error = max_error

        # bspline = scipy.interpolate.make_smoothing_spline(x=self.x, y=y, estimated_mse=estimated_mse, error_threshold=error_threshold)

    def evaluate(self, t):
        pass

    def goodness_of_fit(self, tck):
        pass

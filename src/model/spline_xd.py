# 19/06/2024$ -----------------------------------------------------------------------------------------------------
#  created by: felix 
#              felix@eickeler.com    
# ----------------------------------------------------------------------------------------------------------------
#

import numpy as np
import pandas as pd
from scipy import interpolate


class SplineXD:

    @classmethod
    def build(cls, x, y, mse_threshold=0.001, error_threshold=0.0001):
        """
        Initialize the Spline with time values and corresponding 3D points.

        :param x: Array-like, time values in GPS time.
        :param y: Array-like, 3D points corresponding to the time values.
        :param mse_threshold: float, maximum mean squared error for the spline fit.
        :param error_threshold: float, maximum error for the spline fit.
        """

        if isinstance(x, pd.DataFrame) or isinstance(x, pd.Series):
            x = x.to_numpy()
        else:
            x = np.array(x)
        if isinstance(y, pd.DataFrame) or isinstance(y, pd.Series):
            y = y.to_numpy()

        if len(y.shape) == 1:
            y = y[:, np.newaxis]

        def goodness_of_fit(_tck):
            fit = interpolate.splev(x, _tck)
            fit_points = np.vstack(fit).T
            res = (y - fit_points)
            _mse = np.mean(res ** 2)
            return _mse, np.max(res)

        s = error_threshold / 256
        # noinspection PyTupleAssignmentBalance
        tck, _ = interpolate.splprep(x=y.T, u=x, s=s)
        mse, max_error = goodness_of_fit(tck)

        for i in range(50):
            print(f"Trying l={len(tck[1][0])}, s={s}, mse={mse}, max_error={max_error}")
            if mse < mse_threshold and max_error < error_threshold:
                break
            s = s / 2
            # noinspection PyTupleAssignmentBalance
            tck, _ = interpolate.splprep(x=y.T, u=x, s=s)
            mse, max_error = goodness_of_fit(tck)

        if mse > mse_threshold or max_error > error_threshold:
            raise ValueError(f"Could not fit spline with MSE {mse} below estimated MSE {mse_threshold}")

        return cls(tck, mse, max_error, mse_threshold, error_threshold)

    def __init__(self, tck, mse, max_error, mse_threshold=0.001, error_threshold=0.0001):
        self.tck = tck
        self.requested_mse_threshold = mse_threshold
        self.mse_error = mse
        self.requested_error_threshold = error_threshold
        self.max_error = max_error

    def evaluate(self, t):
        """
        Evaluate the spline at given time values.

        :param t: Array-like, time values at which to evaluate the spline.
        :return: Array of shape (len(t), 3) with the evaluated points.
        """
        x, y, z = interpolate.splev(t, self.tck)
        return np.vstack((x, y, z)).T

    def goodness_of_fit(self):
        """
        Compute the mean squared error and maximum error of the spline fit.

        :return: Tuple of (mean squared error, maximum error).
        """
        return self.mse_error, self.max_error

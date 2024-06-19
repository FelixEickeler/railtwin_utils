# 19/06/2024$ -----------------------------------------------------------------------------------------------------
#  created by: felix 
#              felix@eickeler.com    
# ----------------------------------------------------------------------------------------------------------------
#

import numpy as np
from scipy import interpolate


class Spline3D:
    def __init__(self, t, points, estimated_mse=0.001, error_threshold=0.0001):
        """
        Initialize the Spline with time values and corresponding 3D points.

        :param t: Array-like, time values in GPS time.
        :param points: Array-like, 3D points corresponding to the time values.
        """

        if points.shape[1] != 3:
            raise ValueError("Points should be a 3D array with shape (n_points, 3)")
        self.t = np.array(t)

        def goodness_of_fit(tck):
            x_fit, y_fit, z_fit = interpolate.splev(self.t, tck)
            fit_points = np.vstack((x_fit, y_fit, z_fit)).T
            res = (points - fit_points)
            mse = np.mean(res ** 2)
            return mse, np.max(res)

        s = (len(self.t) - np.sqrt(2 * len(self.t))) / 16384
        tck, _ = interpolate.splprep(points.to_numpy().T, u=self.t, s=s)
        mse, max_error = goodness_of_fit(tck)

        for i in range(50):
            print(f"Trying l={len(tck[1][0])}, s={s}, mse={mse}, max_error={max_error}")
            if mse < estimated_mse and max_error < error_threshold:
                break
            s = s / 2
            tck, _ = interpolate.splprep(points.to_numpy().T, u=self.t, s=s)
            mse, max_error = goodness_of_fit(tck)

        if mse > estimated_mse or max_error > error_threshold:
            raise ValueError(f"Could not fit spline with MSE {mse} below estimated MSE {estimated_mse}")

        self.tck = tck
        self.mse = mse
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
        return self.mse, self.max_error

    def to_npz(self, filename):
        """
        Save the spline to a npz file.

        :param filename: str, path to the file.
        """
        np.savez(filename, tck=self.tck, mse=self.mse, max_error=self.max_error)
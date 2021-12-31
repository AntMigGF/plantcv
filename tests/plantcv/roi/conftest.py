import pytest
import os
import numpy as np
import matplotlib

# Disable plotting
matplotlib.use("Template")


class RoiTestData:
    def __init__(self):
        """Initialize simple variables."""
        # Test data directory
        self.datadir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "testdata")
        # RGB image
        self.small_rgb_img = os.path.join(self.datadir, "setaria_small_plant_rgb.png")
        # Gray image
        self.small_gray_img = os.path.join(self.datadir, "setaria_small_plant_gray.png")
        # Contours file
        self.small_contours_file = os.path.join(self.datadir, "setaria_small_plant_contours.npz")

    def load_npz(self, npz_file):
        """Load data saved in a NumPy .npz file."""
        data = np.load(npz_file, encoding="latin1")
        return data['arr_0']


@pytest.fixture(scope="session")
def roi_test_data():
    return RoiTestData()

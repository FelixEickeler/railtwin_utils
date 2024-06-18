import numpy as np
from pandas import DataFrame


def required_decimals(df: DataFrame) -> dict:
    decimal_places_dict = {}
    for column in df.columns:
        values = df[column].values
        differences = np.diff(np.sort(values))
        min_difference = np.min(differences[differences > 0])  # Ignore zero differences

        if min_difference == 0:
            decimal_places_dict[column] = 0
        else:
            decimal_places = -int(np.floor(np.log10(min_difference)))
            decimal_places_dict[column] = max(decimal_places, 0)

    return decimal_places_dict

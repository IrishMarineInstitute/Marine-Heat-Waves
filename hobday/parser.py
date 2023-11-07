import glob
import os
from typing import Union, Dict

import xarray as xr


def check_precalc_clim_thresh(data: Dict[str, Dict[str, str]]) -> None:
    if not {"clim", "percent"} <= data.keys():
        print(
            "Precalculated climatological mean and/or percentile \
            have not been referenced in config file. \n\
        They will be recalculated by Hobday's method."
        )


def check_file_exist(conf: Dict[str, Dict[str, Dict[str, str]]]) -> None:
    for datas in conf["data"]:
        if not os.path.exists(conf["data"][datas]["path"]):
            raise ValueError("This file does not exist: ", conf["data"][datas]["path"])


def parse_data(
    conf: Dict[str, Dict[str, Dict[str, str]]], cut: bool = True
) -> Dict[str, Dict[str, str]]:
    data = conf["data"]

    if cut:
        for key in data.keys():
            data[key]["path"] = os.path.join(os.path.dirname(data[key]["path"]), "Cut_")

    check_precalc_clim_thresh(data)
    return data


def count_files(conf: Dict[str, Dict[str, Dict[str, str]]]) -> int:
    return (
        len(
            [
                name
                for name in glob.glob(
                    os.path.dirname(conf["data"]["data"]["path"]) + "/Cut_*.nc"
                )
            ]
        )
        + 1
    )


def get_optional_datasets(
    datasets: Dict[str, Dict[str, str]]
) -> Union[None, Dict[str, Dict[str, str]]]:
    if not {"clim", "percent"} <= datasets.keys():
        optional_datasets = None
    else:
        optional_datasets = datasets
        del optional_datasets["data"]

    return optional_datasets


def check_climato_period(conf: Dict[str, Dict[str, Dict[str, str]]]) -> None:
    ds = xr.open_dataset(conf["data"]["data"]["path"])
    period = conf["params"]["climatologyPeriod"]

    min = ds.time.min().values.astype("datetime64[Y]").astype(int) + 1970
    max = ds.time.max().values.astype("datetime64[Y]").astype(int) + 1970

    assert (period[0] >= min) and (
        period[1] <= max
    ), "The dataset does not cover the climatologyPeriod."

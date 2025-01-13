import datetime
import os
from typing import Any, Optional, Union, Tuple, Dict

import numpy as np
import xarray as xr

import src.mhw_detect.detection.marineHeatWavesOpt as mhw


def subset_geo(
    ds: xr.Dataset, lat: Tuple[float, float], lon: Tuple[float, float]
) -> xr.Dataset:
    if "latitude" in ds.coords:
        return ds.sel(latitude=slice(lat[0], lat[1]), longitude=slice(lon[0], lon[1]))
    else:
        return ds.sel(lat=slice(lat[0], lat[1]), lon=slice(lon[0], lon[1]))


def subset_depth(ds: xr.Dataset, var: str, depth: float) -> xr.Dataset:
    if "depth" in ds[var].dims:
        return ds.sel(depth=depth, method="nearest")
    else:
        return ds


def open_file_subset(
    iter: int,
    path: str,
    var: str,
    depth: Optional[float] = 0.0,
    lat_lon: Optional[Tuple[float, float, float, float]] = None,
) -> xr.DataArray:
    if lat_lon is not None:
        ds = xr.open_dataset(path)
        ds = subset_geo(ds, lat_lon[0:2], lat_lon[2:4])
    else:
        ds = xr.open_dataset(path + str(iter) + ".nc")

    ds = subset_depth(ds, var, depth)

    return ds[var]


def prepare_computation(
    iter: int,
    detect_options: Dict[str, Union[str, Tuple[int, int], int, bool]],
    data: Dict[str, str],
    outdir: str,
    mask: bool,
    optional_datasets: Optional[Dict[str, Dict[str, str]]] = None,
    lat_lon: Optional[Tuple[float, float, float, float]] = None,
) -> None:
    txtfile = os.path.join(outdir, str(iter) + ".txt")

    if "depth" in detect_options:
        depth = detect_options["depth"]
        del detect_options["depth"]
    else:
        depth = 0.0

    print("Opening: ", data["path"], "- iteration: ", str(iter))
    ds = open_file_subset(iter, data["path"], data["var"], depth, lat_lon)

    if optional_datasets is not None:
        clim = optional_datasets["clim"]
        climato = open_file_subset(iter, clim["path"], clim["var"], depth, lat_lon)

        percent = optional_datasets["percent"]
        percentile = open_file_subset(
            iter, percent["path"], percent["var"], depth, lat_lon
        )
        p = detect_options["pctile"]

        percentile = percentile.sel(quantile=str(p / 100))

        if "offset" in optional_datasets:
            offset = optional_datasets["offset"]
            offset_ds = open_file_subset(
                iter, offset["path"], offset["var"], depth, lat_lon
            )
            offset_ds = offset_ds.sel(quantile=str(p / 100))
        else:
            offset_ds = None
    else:
        climato = None
        percentile = None
        offset_ds = None

    compute_detection(ds, detect_options, txtfile, mask, climato, percentile, offset_ds)


def compute_detection(
    ds: xr.DataArray,
    detect_options: Any,
    txtfile: str,
    mask: Optional[bool] = False,
    climato: Optional[xr.DataArray] = None,
    percent: Optional[xr.DataArray] = None,
    offset: Optional[xr.DataArray] = None,
) -> None:
    if "latitude" in ds.coords:
        var_lat = "latitude"
        var_lon = "longitude"
    else:
        var_lat = "lat"
        var_lon = "lon"

    lat = len(ds[var_lat])
    lon = len(ds[var_lon])

    # Data preloading for fast cache retrieval
    data = ds.values
    if (climato is not None) and (percent is not None):
        thresh_climYear = percent.values
        seas_climYear = climato.values

    if offset is not None:
        thresh_climYear += offset.values

    t_mhw = np.array(
        [
            datetime.datetime.utcfromtimestamp(t.astype("O") / 1e9).toordinal()
            for t in ds.time.values
        ]
    )

    with open(txtfile, "w") as f:
        f.write(
            "lat;lon;time_deb;time_end;time_peak;duration;duration_mod;"
            + "duration_str;duration_sev;duration_ext;categ;"
            + "imax;imean;ivar;rate_onset;rate_decline\n"
        )

        if mask:
            mask_array = xr.Dataset(
                data_vars=dict(
                    category=(["time", "latitude", "longitude"], np.full(ds.shape, 0))
                ),
                coords=ds.coords,
            )

        for latitude in range(0, lat):
            for longitude in range(0, lon):
                temp = data[:, latitude, longitude]

                if len(np.where(np.isnan(temp))[0]) < (80 / 100) * len(temp):
                    temp[temp < 0] = np.nan

                    if (climato is None) or (percent is None):
                        mhw_prop, mhw_date, categs = mhw.detect(
                            t_mhw, temp, **detect_options
                        )
                    else:
                        mhw_prop, mhw_date, categs = mhw.detect(
                            t_mhw,
                            temp,
                            thresh_climYear=thresh_climYear[:, latitude, longitude],
                            seas_climYear=seas_climYear[:, latitude, longitude],
                            **detect_options
                        )

                    if len(mhw_prop["time_start"]) != 0:
                        for num_mhw in range(len(mhw_prop["time_start"])):
                            time = str(mhw_date["date_start"][num_mhw])
                            time_end = str(mhw_date["date_end"][num_mhw])

                            if mask:
                                mask_array.category.isel(
                                    latitude=latitude, longitude=longitude
                                ).loc[time:time_end] = categs[str(num_mhw)]

                            f.write(
                                str(ds[var_lat][latitude].values)
                                + ";"
                                + str(ds[var_lon][longitude].values)
                                + ";"
                                + time
                                + ";"
                                + time_end
                                + ";"
                                + str(mhw_date["date_peak"][num_mhw])
                                + ";"
                                + str(int(mhw_prop["duration"][num_mhw]))
                                + ";"
                                + str(mhw_prop["duration_moderate"][num_mhw])
                                + ";"
                                + str(mhw_prop["duration_strong"][num_mhw])
                                + ";"
                                + str(mhw_prop["duration_severe"][num_mhw])
                                + ";"
                                + str(mhw_prop["duration_extreme"][num_mhw])
                                + ";"
                                + str(mhw_prop["category"][num_mhw])
                                + ";"
                                + str(mhw_prop["intensity_max"][num_mhw])
                                + ";"
                                + str(mhw_prop["intensity_mean"][num_mhw])
                                + ";"
                                + str(mhw_prop["intensity_var"][num_mhw])
                                + ";"
                                + str(mhw_prop["rate_onset"][num_mhw])
                                + ";"
                                + str(mhw_prop["rate_decline"][num_mhw])
                                + "\n"
                            )

        if mask:
            mask_array.where(~ds.isnull(), np.nan).astype(np.int8).to_netcdf(
                txtfile + ".nc"
            )

import xarray as xr

import multiprocessing as mp
import os
import sys
from functools import partial
from typing import Tuple, List

import click
import pandas as pd
import yaml

from src.mhw_detect.detection.detect import prepare_computation
from src.mhw_detect.detection.parser import (
    check_climato_period,
    check_file_exist,
    count_files,
    parse_data,
    get_optional_datasets,
)


def remove_files(paths: List[str]) -> None:
    for path in paths:
        try:
            os.remove(path)
        except OSError:
            click.echo("Error while deleting file: ", path)


def check_extension(ctx, param, value: str):
    if not value.endswith((".parquet", ".csv")):
        raise click.BadParameter("The extension must be .parquet or .csv")
    else:
        return value

def extreme_events(config, output_df, categ_map=False, geographical_subset=None):

    mask = bool(categ_map)

    conf = yaml.safe_load(open(config))

    output = conf["output_detection"]

    try:
        check_file_exist(conf)
    except Exception as error:
        click.echo(repr(error))
        sys.exit()

    param = conf["params"]

    def output_path(file_name: str) -> str:
        return os.path.join(output, file_name)

    def save_dataframe(dataframe: pd.DataFrame) -> None:
        if output_df.endswith(".parquet"):
            dataframe.to_parquet(output_path(output_df))
        else:
            dataframe.to_csv(output_path(output_df), sep=";")

    if geographical_subset is not None:
        datasets = parse_data(conf, False)
        data = datasets["data"]

        optional_datasets = get_optional_datasets(datasets)

        if optional_datasets is None:
            check_climato_period(conf)

        prepare_computation(
            0, param, data, output, mask, optional_datasets, lat_lon=geographical_subset
        )

        click.echo("Creating csv")
        df = pd.read_csv(output_path("0.txt"), sep=";")
        save_dataframe(df)

        remove_files([output_path("0.txt")])

        if categ_map:
            click.echo("Creating mask")
            os.rename(output_path("0.txt.nc"), output_path(categ_map))

    else:
        nfile = count_files(conf)

        datasets = parse_data(conf)
        data = datasets["data"]

        optional_datasets = get_optional_datasets(datasets)

        #if optional_datasets is None:
        #    check_climato_period(conf)

        pool = mp.Pool()
        pool.imap(
            partial(
                prepare_computation,
                detect_options=param,
                data=data,
                outdir=output,
                mask=mask,
                optional_datasets=optional_datasets,
            ),
            range(1, nfile),
        )
        pool.close()
        pool.join()

        click.echo("Computation done")

        click.echo("Saving dataframe")

        def f(i: str) -> pd.DataFrame:
            return pd.read_csv(i, sep=";")

        filepaths = [output_path(str(i) + ".txt") for i in range(1, nfile)]
        df = pd.concat(map(f, filepaths))
        save_dataframe(df)

        remove_files(filepaths)

        if categ_map:
            click.echo("Creating mask")
            mask = xr.open_mfdataset(output_path("*.txt.nc"))
            comp = dict(zlib=True)
            encoding = {var: comp for var in mask.data_vars}
            mask.to_netcdf(output_path(categ_map), encoding=encoding, engine="netcdf4")
            p = [output_path(str(g) + ".txt.nc") for g in range(1, nfile)]

            remove_files(p)


if __name__ == "__main__":
    extreme_events()

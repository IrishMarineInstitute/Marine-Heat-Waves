import itertools
import os

import xarray as xr
import yaml
from dask.diagnostics import ProgressBar


# Créer un dataset par chunk dask
def split_by_chunks(dataset: xr.Dataset):
    chunk_slices = {}
    for dim, chunks in dataset.chunks.items():
        slices = []
        start = 0
        for chunk in chunks:
            if start >= dataset.sizes[dim]:
                break
            stop = start + chunk
            slices.append(slice(start, stop))
            start = stop
        chunk_slices[dim] = slices
    for slices in itertools.product(*chunk_slices.values()):
        selection = dict(zip(chunk_slices.keys(), slices))
        yield dataset[selection]

def cut(config):
    conf = yaml.safe_load(open(config))

    lat = conf["cut"]["nb_lat"]
    lon = conf["cut"]["nb_lon"]

    for datas in conf["data"]:
        path = conf["data"][datas]["path"]
        var = conf["data"][datas]["var"]

        if os.path.exists(os.path.join(os.path.dirname(path), "Cut_1.nc")):
            print(path, " already cut.")
            continue

        ds = xr.open_dataset(path)

        if "latitude" in ds.coords:
            chunks = {"latitude": lat, "longitude": lon}
        else:
            chunks = {"lat": lat, "lon": lon}

        ds = xr.open_dataset(path, chunks=chunks)[var].to_dataset()

        chunked_ds = list(split_by_chunks(ds))

        p = [
            os.path.dirname(path) + "/Cut_" + str(i + 1) + ".nc"
            for i in range(len(chunked_ds))
        ]
        print("Saving in " + os.path.dirname(path))
        delayed = xr.save_mfdataset(datasets=chunked_ds, paths=p, compute=False)
        with ProgressBar():
            delayed.compute()
        print(str(len(chunked_ds)) + " files saved.")


if __name__ == "__main__":
    cut()

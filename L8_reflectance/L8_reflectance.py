#! /usr/bin/env python
# 
# Author: Roberto Cuccu - RSS Team - 2018

from argparse import ArgumentParser
import os, sys, shutil
import numpy as np
import gdal
from L8_reflectance.L8_utils import L8_MTL, L8_Product


def process_band(myband, mult, add, se, outband):
    print
    myband + ' | ' + mult + ' | ' + add + ' | ' + se + ' | ' + outband

    # Open input band with GDAL
    ds = gdal.Open(myband)
    band = ds.GetRasterBand(1)
    arr = band.ReadAsArray()
    [cols, rows] = arr.shape

    # Calculate TOA reflectance band
    # ------------------------------------------------------------------
    # Reference: https://landsat.usgs.gov/using-usgs-landsat-8-product
    # ------------------------------------------------------------------
    rf = ((np.float32(mult) * arr.astype(np.float32)) + np.float32(add)) / np.sin(np.deg2rad(np.float32(se)))

    # Write Output TOA reflectanf band in GTiff Float32
    driver = gdal.GetDriverByName("GTiff")
    outdata = driver.Create(outband, rows, cols, 1, gdal.GDT_Float32)
    outdata.SetGeoTransform(ds.GetGeoTransform())  # Set same GEO transformation coeff as input
    outdata.SetProjection(ds.GetProjection())  # Set same projection as input
    outdata.GetRasterBand(1).WriteArray(rf)
    outdata.FlushCache()

    # Release variables
    outdata = None
    band = None
    ds = None


def main():
    # parse arguments
    parser = ArgumentParser()
    parser.add_argument('product', help="Input Landsat-8 product path")
    parser.add_argument('outproduct', help="Output L8 TOA reflectance product path")
    args = parser.parse_args()

    # Get L8 product and its metadata	
    L8_prod = L8_Product(args.product)
    L8_metadata = L8_MTL(args.product)

    # Check if the output product dir exist otherwise create it
    outprodpath = args.outproduct

    if not os.path.exists(outprodpath):
        os.makedirs(outprodpath)

    # Create L8 TOA output product folder
    input_prod = args.product
    base_input_prod = os.path.basename(input_prod)
    out_prod_toa = base_input_prod + '_TOA'
    L8_outprodpath = os.path.join(outprodpath, out_prod_toa)

    if os.path.exists(L8_outprodpath):
        print
        "Found existing directory {} . cleaning it and recreating it..".format(L8_outprodpath)
        shutil.rmtree(L8_outprodpath)
        os.makedirs(L8_outprodpath)
    else:
        os.makedirs(L8_outprodpath)

    # Retrieve sun elevation angle from metadata
    se = L8_metadata.sun_elevation_angle

    # L8 reflectance band indexes
    bi = [1, 2, 3, 4, 5, 6, 7]

    # Loop over bands
    for i in bi:
        # Retrieve input band location
        curr_band = L8_prod.bands["b{}".format(i)]

        # Determine output band location
        input_band_filename = os.path.basename(curr_band)
        output_band_filename = input_band_filename.replace(".TIF", "_TOA.TIF")
        output_band_path = os.path.join(L8_outprodpath, output_band_filename)

        # Retrieve rescaling factors
        mult = L8_metadata.reflectance_mult_factors["REFLECTANCE_MULT_BAND_{}".format(i)]
        add = L8_metadata.reflectance_add_factors["REFLECTANCE_ADD_BAND_{}".format(i)]

        # Process band
        process_band(curr_band, mult, add, se, output_band_path)

    sys.exit(0)


if __name__ == "__main__":
    main()

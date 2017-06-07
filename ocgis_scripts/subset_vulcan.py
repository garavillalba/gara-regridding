import ocgis

PATH_IN = "/software/co2flux/Saved_WRF_runs/reversed_vulcan_fossilCO2_ioapi.nc"
PATH_OUT = '/software/co2flux/Saved_WRF_runs/subset_reversed_vulcan_fossilCO2_ioapi.nc'
# PATH_IN = 'data/reversed_vulcan_fossilCO2_ioapi.nc'
# PATH_OUT = 'data/subset_reversed_vulcan_fossilCO2_ioapi.nc'

rd = ocgis.RequestDataset(PATH_IN)

oo = OcgOperations(dataset=rd, geom=[-125, 35, -119, 40], output_format='nc',
                   prefix=PATH_OUT)

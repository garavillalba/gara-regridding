import ocgis

# PATH_IN = "/software/co2flux/SurfaceFluxData/CASA/GEE.3hrly.1x1.25.2015.nc"
PATH_IN = '/home/ryan/sandbox/gara-regridding/GEE.3hrly.1x1.25.2015.nc'

# PATH_OUT = "/software/co2flux/SurfaceFluxData/CASA/modified_GEE.3hrly.1x1.25.2015.nc"
PATH_OUT = 'modified_GEE.3hrly.1x1.25.2015.nc'

rd = ocgis.RequestDataset(PATH_IN)
vc = rd.get_variable_collection()

# now create a grid and write bounds
grid = ocgis.Grid(vc["lon"].extract(), vc['lat'].extract(), crs=ocgis.crs.Spherical())
grid.set_extrapolated_bounds('bounds_lon', 'bounds_lat', 'corners')
grid.x.bounds.attrs.pop('units')
grid.y.bounds.attrs.pop('units')

# write from Field to get the variables
ocgis.Field(grid=grid, variables=vc["GEE"].extract()).write(PATH_OUT)

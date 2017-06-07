
import ocgis

# wrfout file may need to be renamed to have a .nc ending for ocgis to recognize the format
# PATH_IN = "/software/co2flux/SurfaceFluxData/CASA/GEE.3hrly.1x1.25.2015.nc"

PATH_IN = '/home/ryan/sandbox/gara-regridding/GEE.3hrly.1x1.25.2015.nc'

# PATH_OUT = "/software/co2flux/SurfaceFluxData/CASA/modified_GEE.3hrly.1x1.25.2015.nc"
PATH_OUT = 'modified_GEE.3hrly.1x1.25.2015.nc'

rd = ocgis.RequestDataset(PATH_IN)
vc = rd.get_variable_collection()

lat = vc["lat"]
lat.attrs["units"] = "degrees_north"
lat = vc["lon"]
lon.attrs["units"] = "degrees_east"

# now create a grid and write bounds
grid = ocgis.Grid(sub['lon'].extract(), sub['lat'].extract())
grid.set_extrapolated_bounds('bounds_lat', 'bounds_lon', 'corners')
grid.x.bounds.attrs.pop('units')
grid.y.bounds.attrs.pop('units')

grid.parent.write(PATH_OUT)

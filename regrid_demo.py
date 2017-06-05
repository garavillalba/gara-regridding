# This is an ESMPy reproducer of uvcdat bug 1125, esmf support request 3613723
import ESMF
import numpy as np

# vulcangrid = "/software/co2flux/FieldRead/vulcangrid.10.2012.nc"
vulcan_grid_file = "/home/ryan/sandbox/gara-regridding/vulcangrid.10.2012.nc"
# vulcandata = "/software/co2flux/SurfaceFluxData/VULCAN/reversed_vulcan_fossilCO2_ioapi.nc"
vulcan_data_file = "/home/ryan/sandbox/gara-regridding/reversed_vulcan_fossilCO2_ioapi.nc"
# stem_grid_file = "/software/co2flux/Saved_WRF_runs/subset_wrfout.nc"
stem_grid_file = "/home/ryan/sandbox/gara-regridding/subset_wrfout.nc"

def initialize_field(field):
    realdata = False
    try:
        import netCDF4 as nc

        f = nc.Dataset(vulcan_data_file)
        co2f = f.variables['CO2_FLUX']
        # import pdb; pdb.set_trace()
        co2f = co2f[0, 0, :, :]
        realdata = True
    except:
        raise ImportError('netCDF4 not available on this machine')

    if realdata:
        # transpose because uvcdat data is represented as lat/lon
        field.data[:] = co2f.T
    else:
        field.data[:] = 42.0


    return field

def compute_mass(valuefield, areafield, fracfield, dofrac):
    mass = 0.0
    areafield.get_area()
    if dofrac:
        mass = np.sum(areafield.data[:]*valuefield.data[:]*fracfield.data[:])
    else:
        mass = np.sum(areafield.data[:] * valuefield.data[:])

    return mass

def plot(srclons, srclats, srcfield, dstlons, dstlats, interpfield):

    try:
        import matplotlib
        import matplotlib.pyplot as plt
    except:
        raise ImportError("matplotlib is not available on this machine")

    fig = plt.figure(1, (15, 6))
    fig.suptitle('Vulcan data regridding to WRF-STEM', fontsize=14, fontweight='bold')

    ax = fig.add_subplot(1, 2, 1)
    im = ax.imshow(srcfield.data.T, vmin=0, vmax=1, cmap='hot', aspect='auto',
                   extent=[np.min(srclons), np.max(srclons), np.min(srclats), np.max(srclats)])
    ax.set_xbound(lower=np.min(srclons), upper=np.max(srclons))
    ax.set_ybound(lower=np.min(srclats), upper=np.max(srclats))
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title("Vulcan fossil CO2 data")

    ax = fig.add_subplot(1, 2, 2)
    im = ax.imshow(interpfield.data.T, vmin=0, vmax=1, cmap='hot', aspect='auto',
                   extent=[np.min(dstlons), np.max(dstlons), np.min(dstlats), np.max(dstlats)])
    ax.set_xbound(lower=np.min(dstlons), upper=np.max(dstlons))
    ax.set_ybound(lower=np.min(dstlats), upper=np.max(dstlats))
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title("Conservative Regrid Solution on WRF STEM")

    fig.subplots_adjust(right=0.8)
    cbar_ax = fig.add_axes([0.9, 0.1, 0.01, 0.8])
    fig.colorbar(im, cax=cbar_ax)

    plt.show()

##########################################################################################


# Start up ESMF, this call is only necessary to enable debug logging
esmpy = ESMF.Manager(debug=True)

# timesteps = 365*24
timesteps = 24

# Create a destination grid from a GRIDSPEC formatted file.
srcgrid = ESMF.Grid(filename=vulcan_grid_file,
                    filetype=ESMF.FileFormat.GRIDSPEC, add_corner_stagger=True)
dstgrid = ESMF.Grid(filename=stem_grid_file,
                    filetype=ESMF.FileFormat.GRIDSPEC, add_corner_stagger=True)

srcfield = ESMF.Field(srcgrid, "srcfield", staggerloc=ESMF.StaggerLoc.CENTER)
dstfield = ESMF.Field(dstgrid, "dstfield", staggerloc=ESMF.StaggerLoc.CENTER)
srcareafield = ESMF.Field(srcgrid, "srcfield", staggerloc=ESMF.StaggerLoc.CENTER)
dstareafield = ESMF.Field(dstgrid, "dstfield", staggerloc=ESMF.StaggerLoc.CENTER)
srcfracfield = ESMF.Field(srcgrid, "srcfield", staggerloc=ESMF.StaggerLoc.CENTER)
dstfracfield = ESMF.Field(dstgrid, "dstfield", staggerloc=ESMF.StaggerLoc.CENTER)

srcfield = initialize_field(srcfield)

# Regrid from source grid to destination grid.
regridSrc2Dst = ESMF.Regrid(srcfield, dstfield,
                            regrid_method=ESMF.RegridMethod.CONSERVE,
                            unmapped_action=ESMF.UnmappedAction.ERROR,
                            src_frac_field=srcfracfield,
                            dst_frac_field=dstfracfield)

dstfield = regridSrc2Dst(srcfield, dstfield)

srcmass = compute_mass(srcfield, srcareafield, srcfracfield, True)
dstmass = compute_mass(dstfield, dstareafield, 0, False)

print "Conservative error = {}".format(abs(srcmass-dstmass)/abs(srcmass))

try:
    import netCDF4 as nc
except:
    raise ImportError('netCDF4 not available on this machine')

# read longitudes and latitudes from file
f = nc.Dataset(vulcan_grid_file)
srclons = f.variables['longitude'][:]
srclats = f.variables['latitude'][:]
srclonbounds = f.variables['x_bounds'][:]
srclatbounds = f.variables['y_bounds'][:]

f = nc.Dataset(stem_grid_file)
dstlons = f.variables['XLONG'][:]
dstlats = f.variables['XLAT'][:]
dstlonbounds = f.variables['XLONG_BNDS'][:]
dstlatbounds = f.variables['XLAT_BNDS'][:]

plot(srclons, srclats, srcfield, dstlons, dstlats, dstfield)

print '\nregrid demo completed successfully.\n'

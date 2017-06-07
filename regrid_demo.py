# This is an ESMPy reproducer of uvcdat bug 1125, esmf support request 3613723
import ESMF
import numpy as np

# CASA_grid_file = "/software/co2flux/SurfaceFluxData/CASA/GEE.3hrly.1x1.25.2015.nc"
CASA_grid_file = "/home/ryan/sandbox/gara-regridding/GEE.3hrly.1x1.25.2015.nc"
# STEM_grid_file = "/software/co2flux/Saved_WRF_runs/subset_wrfout.nc"
STEM_grid_file = "/home/ryan/sandbox/gara-regridding/subset_wrfout.nc"

def initialize_field(field):
    realdata = False
    try:
        import netCDF4 as nc

        f = nc.Dataset(CASA_grid_file)
        gee = f.variables['GEE']
        # import pdb; pdb.set_trace()
        gee = gee[0, :, :]
        realdata = True
    except:
        raise ImportError('netCDF4 not available on this machine')

    if realdata:
        # transpose because uvcdat data is represented as lat/lon
        field.data[:] = gee.T
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
    fig.suptitle('CASA data regridding to 9km WRF-STEM', fontsize=14, fontweight='bold')

    ax = fig.add_subplot(1, 2, 1)
    im = ax.imshow(srcfield.data.T, vmin=0, vmax=0.2, cmap='hot', aspect='auto', origin="lower",
                   extent=[np.min(srclons), np.max(srclons), np.min(srclats), np.max(srclats)])
    ax.set_xbound(lower=np.min(srclons), upper=np.max(srclons))
    ax.set_ybound(lower=np.min(srclats), upper=np.max(srclats))
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title("CASA GEE CO2 data")

    ax = fig.add_subplot(1, 2, 2)
    im = ax.imshow(interpfield.data.T, vmin=0, vmax=0.2, cmap='hot', aspect='auto', origin="lower",
                   extent=[np.min(dstlats), np.max(dstlats), np.min(dstlons), np.max(dstlons)])
    ax.set_xbound(lower=np.min(dstlats), upper=np.max(dstlats))
    ax.set_ybound(lower=np.min(dstlons), upper=np.max(dstlons))
    ax.set_xlabel("Latitude")
    ax.set_ylabel("Longitude")
    ax.set_title("Conservative Regrid Solution on 9km WRF-STEM")

    fig.subplots_adjust(right=0.8)
    cbar_ax = fig.add_axes([0.9, 0.1, 0.01, 0.8])
    fig.colorbar(im, cax=cbar_ax)

    plt.show()

##########################################################################################


# Start up ESMF, this call is only necessary to enable debug logging
esmpy = ESMF.Manager(debug=True)

# Create a destination grid from a GRIDSPEC formatted file.
srcgrid = ESMF.Grid(filename=CASA_grid_file, filetype=ESMF.FileFormat.GRIDSPEC,
                    add_corner_stagger=True, is_sphere=False)
dstgrid = ESMF.Grid(filename=STEM_grid_file, filetype=ESMF.FileFormat.GRIDSPEC,
                    add_corner_stagger=True, is_sphere=False)

srcfield = ESMF.Field(srcgrid, "srcfield", staggerloc=ESMF.StaggerLoc.CENTER)
dstfield = ESMF.Field(dstgrid, "dstfield", staggerloc=ESMF.StaggerLoc.CENTER)
# srcareafield = ESMF.Field(srcgrid, "srcfield", staggerloc=ESMF.StaggerLoc.CENTER)
# dstareafield = ESMF.Field(dstgrid, "dstfield", staggerloc=ESMF.StaggerLoc.CENTER)
# srcfracfield = ESMF.Field(srcgrid, "srcfield", staggerloc=ESMF.StaggerLoc.CENTER)
# dstfracfield = ESMF.Field(dstgrid, "dstfield", staggerloc=ESMF.StaggerLoc.CENTER)

srcfield = initialize_field(srcfield)

# Regrid from source grid to destination grid.
regridSrc2Dst = ESMF.Regrid(srcfield, dstfield,
                            regrid_method=ESMF.RegridMethod.BILINEAR,
                            unmapped_action=ESMF.UnmappedAction.ERROR)#,
                            # src_frac_field=srcfracfield,
                            # dst_frac_field=dstfracfield)

dstfield = regridSrc2Dst(srcfield, dstfield)

# srcmass = compute_mass(srcfield, srcareafield, srcfracfield, True)
# dstmass = compute_mass(dstfield, dstareafield, 0, False)
# print "Conservative error = {}".format(abs(srcmass-dstmass)/abs(srcmass))

try:
    import netCDF4 as nc
except:
    raise ImportError('netCDF4 not available on this machine')

# read longitudes and latitudes from file
f = nc.Dataset(CASA_grid_file)
srclons = f.variables['lon'][:]
srclats = f.variables['lat'][:]
#srclonbounds = f.variables['x_bounds'][:]
#srclatbounds = f.variables['y_bounds'][:]

f = nc.Dataset(STEM_grid_file)
dstlons = f.variables['XLONG'][:]
dstlats = f.variables['XLAT'][:]
dstlonbounds = f.variables['XLONG_BNDS'][:]
dstlatbounds = f.variables['XLAT_BNDS'][:]

plot(srclons, srclats, srcfield, dstlons, dstlats, dstfield)

print '\nregrid demo completed successfully.\n'

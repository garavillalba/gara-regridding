!Gara
program FieldRead

use ESMF

use netcdf

implicit none

integer :: rc

rc = ESMF_SUCCESS


! Initialize ESMF
call ESMF_Initialize (defaultlogfilename="ESMF.Log", rc=rc)
if (rc /= ESMF_SUCCESS) call ESMF_Finalize(endflag=ESMF_END_ABORT)

call test_fieldread(rc)
if (rc /= ESMF_SUCCESS) call ESMF_Finalize(endflag=ESMF_END_ABORT)


call ESMF_Finalize()

contains

subroutine test_fieldread(rc)
integer, intent(out)  :: rc

logical :: correct
integer :: localrc
type(ESMF_RouteHandle) :: routehandle
type(ESMF_Grid) :: grid, STEMgrid
type(ESMF_Field) :: field, STEMfield
type(ESMF_VM) :: vm

character(len=200) :: vulcangrid, vulcandata, stem_grid_file
character(16), parameter :: apConv = 'Attribute_IO'
character(16), parameter :: apPurp = 'attributes'

integer :: timesteps

integer :: localPet, petCount

! result code
integer :: finalrc

! init success flag
correct=.true.

rc=ESMF_SUCCESS

vulcangrid = "/software/co2flux/FieldRead/vulcangrid.10.2012.nc"
! vulcangrid = "/home/ryan/sandbox/gara-regridding/vulcangrid.10.2012.nc"
vulcandata = "/software/co2flux/SurfaceFluxData/VULCAN/reversed_vulcan_fossilCO2_ioapi.nc"
! vulcandata = "/home/ryan/sandbox/gara-regridding/reversed_vulcan_fossilCO2_ioapi.nc"
stem_grid_file = "/software/co2flux/Saved_WRF_runs/subset_wrfout.nc"
! stem_grid_file = "/home/ryan/sandbox/gara-regridding/subset_wrfout.nc"

timesteps = 365*24
! timesteps = 24

! SOURCE GRID AND FIELD

! Grid create from file
grid = ESMF_GridCreate(vulcangrid, ESMF_FILEFORMAT_GRIDSPEC, &
    addCornerStagger=.true., & ! use this with 'bounds' in nc file to add CORNER stagger coordinates for conservative regridding
    rc=localrc)
    if (localrc /= ESMF_SUCCESS) return

! Create field
field = ESMF_FieldCreate(grid, ESMF_TYPEKIND_R8, staggerloc=ESMF_STAGGERLOC_CENTER, &
    ungriddedLBound=(/1, 1/), ungriddedUBound=(/1, timesteps/), &
    name="field", rc=localrc)
if (localrc /= ESMF_SUCCESS) return

! Read Field data from file
call ESMF_FieldRead(field, vulcandata, &
    variableName="CO2_FLUX", timeslice=timesteps, rc=localrc)
if (localrc /= ESMF_SUCCESS) return

! DESTINATION GRID AND FIELD

! Grid create from file
STEMgrid = ESMF_GridCreate(stem_grid_file, ESMF_FILEFORMAT_GRIDSPEC, &
    addCornerStagger=.true., & ! use this with 'bounds' in nc file to add CORNER stagger coordinates for conservative regridding
    rc=localrc)
if (localrc /= ESMF_SUCCESS) return

! Create Field
STEMfield = ESMF_FieldCreate(STEMgrid, ESMF_TYPEKIND_R8, staggerloc=ESMF_STAGGERLOC_CENTER, &
    ungriddedLBound=(/1, 1/), ungriddedUBound=(/1, timesteps/), &
    name="STEMfield", rc=localrc)
if (localrc /= ESMF_SUCCESS) return


! build interpolation matrix and return a routehandle
call ESMF_FieldRegridStore(field, STEMfield, routehandle=routehandle, &
    regridMethod=ESMF_REGRIDMETHOD_CONSERVE, &
    unmappedAction=ESMF_UNMAPPEDACTION_ERROR, rc=localrc)
if (localrc /= ESMF_SUCCESS) return

! apply the routehandle to the destination Field
call ESMF_FieldRegrid(field, STEMfield, routehandle, rc=localrc)
if (localrc /= ESMF_SUCCESS) return

! Field Print just for quick visual verification that everything worked
call ESMF_FieldPrint(STEMfield, rc=localrc)
if (localrc /= ESMF_SUCCESS) return


! write out the regridded Field data to file (set dimension names on grid first)
call ESMF_AttributeAdd (STEMgrid,  convention=apConv, purpose=apPurp,  &
     attrList=(/ ESMF_ATT_GRIDDED_DIM_LABELS /), &
     rc=rc)
if (localrc /= ESMF_SUCCESS) return

call ESMF_AttributeSet(STEMgrid, ESMF_ATT_GRIDDED_DIM_LABELS, &
    valueList=(/"longitude", "latitude "/), &
    convention=apConv, purpose=apPurp, rc=localrc)
if (localrc /= ESMF_SUCCESS) return

call ESMF_AttributeAdd (STEMfield,  convention=apConv, purpose=apPurp,  &
     attrList=(/ ESMF_ATT_UNGRIDDED_DIM_LABELS /), &
     rc=rc)
if (localrc /= ESMF_SUCCESS) return

call ESMF_AttributeSet(STEMfield, ESMF_ATT_UNGRIDDED_DIM_LABELS, &
    valueList=(/"level", "time "/), &
    convention=apConv, purpose=apPurp, rc=localrc)
if (localrc /= ESMF_SUCCESS) return

call ESMF_FieldWrite(STEMfield, overwrite=.true., "STEMfield.nc", &
    convention=apConv, purpose=apPurp, rc=localrc)
if (localrc /= ESMF_SUCCESS) return

! Destroy the Fields and Grids
call ESMF_FieldDestroy(field, rc=localrc)
if (localrc /= ESMF_SUCCESS) return

call ESMF_GridDestroy(grid, rc=localrc)
if (localrc /= ESMF_SUCCESS) return

! return answer based on correct flag
if (correct) then
    rc=ESMF_SUCCESS
else
    rc=ESMF_FAILURE
endif

end subroutine test_fieldread

end program FieldRead

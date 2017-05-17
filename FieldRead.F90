
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
type(ESMF_ArraySpec) :: arrayspec, STEMarrayspec
type(ESMF_VM) :: vm


integer :: localPet, petCount

! result code
integer :: finalrc

! init success flag
correct=.true.

rc=ESMF_SUCCESS

! get pet info
call ESMF_VMGetGlobal(vm, rc=localrc)
if (ESMF_LogFoundError(rcToCheck=localrc, msg=ESMF_LOGERR_PASSTHRU, &
line=__LINE__, file=__FILE__, rcToReturn=rc)) &
call ESMF_Finalize(endflag=ESMF_END_ABORT)

call ESMF_VMGet(vm, petCount=petCount, localPet=localpet, rc=localrc)
if (ESMF_LogFoundError(rcToCheck=localrc, msg=ESMF_LOGERR_PASSTHRU, &
line=__LINE__, file=__FILE__, rcToReturn=rc)) &
call ESMF_Finalize(endflag=ESMF_END_ABORT)


! Grid create from file
grid = ESMF_GridCreate(&
    "/software/co2flux/FieldRead/vulcangrid.10.2012.nc", &
    ESMF_FILEFORMAT_GRIDSPEC, rc=localrc)
if (localrc /= ESMF_SUCCESS) return


! Create source/destination fields
call ESMF_ArraySpecSet(arrayspec, 4, ESMF_TYPEKIND_R8, rc=localrc)
if (localrc /= ESMF_SUCCESS) return

field = ESMF_FieldCreate(grid, arrayspec, staggerloc=ESMF_STAGGERLOC_CENTER, &
    ungriddedLBound=(/1,1/), ungriddedUBound=(/365*24,1/), gridToFieldMap=(/3, 4/), &
    name="field", rc=localrc)
if (localrc /= ESMF_SUCCESS) return


call ESMF_FieldRead(field, &
    "/software/co2flux/SurfaceFluxData/VULCAN/reversed_vulcan_fossilCO2_ioapi.nc", &
    variableName="CO2_FLUX", timeslice=365*24, rc=localrc)
if (localrc /= ESMF_SUCCESS) return

call ESMF_FieldPrint(field)

! DESTINATION GRID, AND FIELD

! Grid create from file
STEMgrid = ESMF_GridCreate(&
    "/software/co2flux/Saved_WRF_runs/wrfout_d01_2015-03-05_00:00:00", &
    ESMF_FILEFORMAT_GRIDSPEC, rc=localrc)
if (localrc /= ESMF_SUCCESS) return


! Create source/destination fields
call ESMF_ArraySpecSet(STEMarrayspec, 4, ESMF_TYPEKIND_R8, rc=localrc)
if (localrc /= ESMF_SUCCESS) return

STEMfield = ESMF_FieldCreate(STEMgrid, STEMarrayspec, staggerloc=ESMF_STAGGERLOC_CENTER, &
    ungriddedLBound=(/1,1/), ungriddedUBound=(/365*24,1/), gridToFieldMap=(/3, 4/), &
    name="STEMfield", rc=localrc)
if (localrc /= ESMF_SUCCESS) return

! regrid
call ESMF_FieldRegridStore(field, STEMfield, routehandle=routehandle,&
regridMethod=ESMF_REGRIDMETHOD_CONSERVE,&
unmappedAction=ESMF_UNMAPPEDACTION_ERROR, rc=localrc)
if (localrc /= ESMF_SUCCESS) return

call ESMF_FieldRegrid(field, STEMfield, routehandle, rc=localrc)
if (localrc /= ESMF_SUCCESS) return




! Destroy the Fields
call ESMF_FieldDestroy(field, rc=localrc)
if (localrc /= ESMF_SUCCESS) return

! Free the grids
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

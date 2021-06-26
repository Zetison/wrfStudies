;   Example script - plot terrain (using some basic WRF scripts)
;   Overwrite basic map background settings
;   November 2008

load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_code.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/wrf/WRFUserARW.ncl"

begin

  ; a = addfile("SED_pathToResults/wps_io/geo_em.d01.nc","r")           ; Open a file



  type = "SED_NCL_OUTPUT_TYPE"
  wks = gsn_open_wks(type,"plt_geo_6")         ; Create a plot workstation
  gsn_define_colormap(wks,"MPL_terrain")

  opts = True                                  ; Set some Basic Plot options
  opts@MainTitle = "GEOGRID FIELDS"
  opts@InitTime = False                        ; Do not plot time or footers
  opts@Footer = False    

  ter = wrf_user_getvar(a,"HGT_M",0)           ; Read the variable to memory

  res = opts                                   ; Use basic options for this field
  res@cnFillOn = True                          ; Create a color fill plot
  res@ContourParameters = (/ 0., 4000., 100. /) ; Set the levels

  contour = wrf_contour(a,wks,ter,res)

  pltres = True                                ; Set plot options
  mpres = True                                 ; Set map options
  mpres@mpGeophysicalLineColor      = "Black"  ; Overwrite basic map settings
  mpres@mpGridLineColor             = "Black"
  mpres@mpLimbLineColor             = "Black"
  mpres@mpNationalLineColor         = "White"
  mpres@mpPerimLineColor            = "Black"
  mpres@mpGridSpacingF              = 10
  mpres@mpOutlineBoundarySets       = "National"
  plot = wrf_map_overlays(a,wks,(/contour/),pltres,mpres) ; Plot field over map background

end



;   Example script to produce plots for a WRF real-data run,
;   with the ARW coordinate dynamics option.

load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_code.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/wrf/WRFUserARW.ncl"
;load "./WRFUserARW.ncl"

begin
;
; The WRF ARW input file.  
; This needs to have a ".nc" appended, so just do it.
  a = addfile("./wrfout_dSED_I_DOMAIN.nc","r")

; We generate plots, but what kind do we prefer?
  type = "SED_NCL_OUTPUT_TYPE"
  wks = gsn_open_wks(type,"plt_Surface3")
;  gsn_define_colormap(wks,"SINTEF1")
  gsn_define_colormap(wks,"NCV_blu_red")

; Set some Basic Plot options
  res = True
  res@MainTitle                   = "REAL-TIME WRF"

  pltres = True
  mpres = True

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

; What times and how many time steps are in the data set?
  times = wrf_user_getvar(a,"times",-1)  ; get all times in the file
  ntimes = dimsizes(times)         ; number of times in the file

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

  do it = 0,ntimes-1               ; TIME LOOP

    print("Working on time: " + times(it) )
    res@TimeLabel = times(it)   ; Set Valid time to use on plots

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; First get the variables we will need        

    slp = wrf_user_getvar(a,"slp",it)  ; slp
      wrf_smooth_2d( slp, 3 )          ; smooth slp
    tc = wrf_user_getvar(a,"tc",it)    ; 3D tc 
      tf = tc                  ; Turn temperature into Fahrenheit 
      tf@description = "Surface Air Temperature"
      tf@units = "C"
    u  = wrf_user_getvar(a,"ua",it)    ; 3D U at mass points
    v  = wrf_user_getvar(a,"va",it)    ; 3D V at mass points
      u = u*1.94386                    ; Turn wind into knots 
      v = v*1.94386
      u@units = "kts"
      v@units = "kts"


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

    ; Plotting options for T                
      opts = res                          
      opts@cnFillOn = True  
      opts@cnLinesOn = False
      opts@ContourParameters = (/ 0., 30., 0.5/)
      opts@gsnSpreadColorEnd = -1  ; End third from the last color in color map
      contour_tc = wrf_contour(a,wks,tf(0,:,:),opts)
      delete(opts)


    ; Plotting options for SLP                     
      opts = res          
      opts@cnLineColor = "Black"
      opts@cnHighLabelsOn = True
      opts@cnLowLabelsOn = True
      opts@ContourParameters = (/ 900., 1100., 4. /)
      opts@cnLineLabelBackgroundColor = -1
      opts@gsnContourLineThicknessesScale = 2.0
      contour_psl = wrf_contour(a,wks,slp,opts)
      delete(opts)

    ; Plotting options for Wind Vectors                 
      opts = res          
      opts@FieldTitle = "Wind"    ; overwrite Field Title
      opts@NumVectors = 15        ; density of wind barbs
      vector = wrf_vector(a,wks,u(0,:,:),v(0,:,:),opts)
      delete(opts)


    ; MAKE PLOTS                                       
      plot = wrf_map_overlays(a,wks,(/contour_tc,contour_psl,vector/),pltres,mpres)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

  end do        ; END OF TIME LOOP

end


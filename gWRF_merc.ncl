
;   Script to produce plots for a WRF real-data run,
;   with the ARW coordinate dynamics option.

load "$NCARG_ROOT/lib/ncarg/nclscripts/csm/gsn_code.ncl"
load "$NCARG_ROOT/lib/ncarg/nclscripts/wrf/WRFUserARW.ncl"
;load "./WRFUserARW.ncl"

begin
;
; Make a list of all files we are interested in
  DATADir = "/mmmtmp/bruyerec/"
  FILES = systemfunc (" ls -1 " + DATADir + "wrfout_d01_2007* ")
  numFILES = dimsizes(FILES)
  print("numFILES = " + numFILES)
  print(FILES)
  print (" ")

; We generate plots, but what kind do we prefer?
  type = "x11"
; type = "pdf"
; type = "ps"
; type = "ncgm"
  wks = gsn_open_wks(type,"gwrf_merc")
  gsn_define_colormap(wks,"wh-bl-gr-ye-re")

; Basic Plot Information                             
    resB = True
    resB@MainTitle = " "
    resB@Footer = False

    pltres = True
    mpres = True
    mpres@mpGeophysicalLineThicknessF = 2.0
    mpres@mpNationalLineThicknessF    = 2.0
    mpres@mpUSStateLineThicknessF     = 2.0
    mpresB = mpres
    mpresB@mpGeophysicalLineColor      = "Black"
    mpresB@mpNationalLineColor         = "Black"
    mpresB@mpUSStateLineColor          = "Black"
    mpresB@mpGridLineColor             = "Black"
    mpresB@mpLimbLineColor             = "Black"
    mpresB@mpPerimLineColor            = "Black"




; Interval to loop through the data
  timeINT = 10

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

; The specific pressure levels that we want the data interpolated to.
  pressure_levels = (/ 850., 700., 500., 300./)   ; pressure levels to plot
  nlevels         = dimsizes(pressure_levels)     ; number of pressure levels

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

FirstTime = True
do ifil = 0, numFILES-1      ; BIG FILES LOOP
   a = addfile(FILES(ifil)+".nc","r")
   print("Working on FILE: " +FILES(ifil) )

   ; What times and how many time steps are in this data set?
     times  = wrf_user_list_times(a)  ; get times in the file
     ntimes = dimsizes(times)         ; number of times in the file

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

  do it = 0,ntimes-1,timeINT        ; TIME LOOP

    print("Working on time: " + times(it) )
    resB@TimeLabel = times(it)      ; Set Valid time to use on plots
    if (FirstTime) then
      times_sav = times(it)
    end if

    res = resB
    ;res@cnRasterModeOn = True
    res@cnFillOn = False

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; First get the variables we will need        

    ter = wrf_user_getvar(a,"HGT",it)    
    slp = wrf_user_getvar(a,"slp",it)       ; psl
      wrf_smooth_2d(slp, 3)                 ; smooth psl          
    tc  = wrf_user_getvar(a,"tc",it)        ; T in C
    td  = wrf_user_getvar(a,"td",it)        ; Td
    u   = wrf_user_getvar(a,"ua",it)        ; u averaged to mass points
    v   = wrf_user_getvar(a,"va",it)        ; v averaged to mass points
    p   = wrf_user_getvar(a, "pressure",it) ; pressure
    z   = wrf_user_getvar(a, "z",it)        ; grid point height
    rh = wrf_user_getvar(a,"rh",it)         ; relative humidity

    if ( it .eq. 0 ) then                
      tc2 = tc(0,:,:)                       ; Use lowest T at time zero
      td2 = td(0,:,:)                       ; Use lowest Td at time zero
      u10 = u(0,:,:)                        ; Use lowest level at time 0
      v10 = v(0,:,:)
    else
      tc2 = wrf_user_getvar(a,"T2",it)      ; T2 in Kelvin
         tc2 = tc2-273.16                   ; T2 in C
      td2 =  wrf_user_getvar(a,"td2",it)    ; Td2 in C
      u10 = wrf_user_getvar(a,"U10",it)     ; u at 10 m, mass point
      v10 = wrf_user_getvar(a,"V10",it)     ; v at 10 m, mass point
    end if

  ;       Get non-convective, convective and total precipitation
  ;       Calculate tendency values                               
    rain_exp = wrf_user_getvar(a,"RAINNC",it)
    rain_con = wrf_user_getvar(a,"RAINC",it)
    snow_exp = wrf_user_getvar(a,"SNOWNC",it)
    rain_tot = rain_exp + rain_con
    if( FirstTime ) then
      rain_exp_save = rain_exp
      rain_con_save = rain_con
      rain_tot_save = rain_tot
    end if
    rain_exp_tend = rain_exp - rain_exp_save
    rain_con_tend = rain_con - rain_con_save
    rain_tot_tend = rain_tot - rain_tot_save
  ;       Bookkeeping, just to allow the tendency at the next time step
    rain_exp_save = rain_exp
    rain_con_save = rain_con
    rain_tot_save = rain_tot

    tf2 = 1.8*tc2+32.                    ; Turn temperature into Fahrenheit
      tf2@description = "Surface Temperature"
      tf2@units = "F"
    td_f = 1.8*td2+32.                   ; Turn temperature into Fahrenheit
      td_f@description = "Surface Dew Point Temp"
      td_f@units = "F"
    u10 = u10*1.94386                ; Turn wind into knots
    v10 = v10*1.94386
      u10@units = "kts"
      v10@units = "kts"

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

    if (FirstTime) then
      opts = res
      opts@cnFillOn = True
      opts@cnLevelSelectionMode = "ExplicitLevels"
      opts@cnLevels = (/ 0., 100., 200., 300., 400., 500., \
                         1000., 1500., 2000., 2500., 3000.,\
                         3500., 4000., 4500., 5000., 5500. /)
      contour = wrf_contour(a,wks,ter,opts)
      plot = wrf_map_overlays(a,wks,(/contour/),pltres,mpres)
      delete(opts)
    end if

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

    ; Plotting options for T                
      opts = res                          
      opts@cnFillOn = True  
      opts@ContourParameters = (/ -20., 90., 5./)
      opts@gsnSpreadColorEnd = -3 
      contour_tc  = wrf_contour(a,wks,tf2,opts)
      delete(opts)
 
    ; Plotting options for Td
      opts = res          
      opts@cnFillOn = True 
      opts@cnLinesOn = True
      opts@cnLineLabelsOn = True
      opts@ContourParameters = (/ -20., 90., 5./)
      opts@cnLineLabelBackgroundColor = -1
      opts@gsnSpreadColorEnd = -3
      contour_td  = wrf_contour(a,wks,td_f,opts)
      delete(opts)

    ; Plotting options for SLP                     
      opts = res          
      opts@ContourParameters = (/ 900., 1100., 10. /)
      ;opts@cnLineColor = "NavyBlue"
      ;opts@cnHighLabelsOn = True
      ;opts@cnLowLabelsOn = True
      opts@cnLineLabelsOn = False
      opts@cnLineLabelBackgroundColor = -1
      opts@gsnContourLineThicknessesScale = 1.5
      contour_psl = wrf_contour(a,wks,slp,opts)
      delete(opts)

    ; Plotting options for Wind Vectors                 
      opts = resB          
      opts@FieldTitle = "Wind"
      opts@NumVectors = 30
      vector = wrf_vector(a,wks,u10,v10,opts)
      delete(opts)


    ; MAKE PLOTS                                       
      plot = wrf_map_overlays(a,wks,(/contour_tc,contour_psl,vector/),pltres,mpres)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

    do level = 0,nlevels-1     ; LOOP over pressure levels

      pressure = pressure_levels(level)

      tc_plane = wrf_user_intrp3d(tc,p,"h",pressure,0.,False)
      z_plane  = wrf_user_intrp3d( z,p,"h",pressure,0.,False)
      rh_plane = wrf_user_intrp3d(rh,p,"h",pressure,0.,False)
      u_plane  = wrf_user_intrp3d( u,p,"h",pressure,0.,False)
      v_plane  = wrf_user_intrp3d( v,p,"h",pressure,0.,False)

      spd     = (u_plane*u_plane + v_plane*v_plane)^(0.5) ; m/sec
      spd@description = "Wind Speed"
      spd@units = "m/s"
      u_plane = u_plane*1.94386     ; kts
      v_plane = v_plane*1.94386     ; kts
      u_plane@units = "kts"
      v_plane@units = "kts"


      ; Plotting options for T                
        opts = res                          
        opts@cnFillOn = True  
        opts@ContourParameters = (/ 10.0 /)
        opts@gsnContourLineThicknessesScale = 1.5
        contour_tc = wrf_contour(a,wks,tc_plane,opts)
        delete(opts)

      ; Plotting options for RH                
        opts = res                          
        opts@cnFillOn = True  
        opts@ContourParameters = (/ 10., 90., 10./)
        opts@cnFillColors = (/"White","White","White", \
                              "White","Chartreuse","Green",\
                              "Green3","Green4", \
                              "ForestGreen","PaleGreen4"/)
        contour_rh = wrf_contour(a,wks,rh_plane,opts)
        delete(opts)

      ; Plotting options for Wind Speed                
        opts = res                          
        opts@cnFillOn = True  
        opts@FieldTitle = "Wind Speed"
        opts@UnitLabel = "m/s"
        opts@ContourParameters = (/ 20., 70., 5./)
        opts@cnInfoLabelOrthogonalPosF = 0.07
        opts@gsnContourLineThicknessesScale = 1.5
        contour_spd = wrf_contour(a,wks,spd,opts)
        delete(opts)

      ; Plotting options for Wind Vectors                 
        opts = resB          
        opts@FieldTitle = "Wind"
        opts@NumVectors = 30
        opts@vcWindBarbColor = "Black"
        vector = wrf_vector(a,wks,u_plane,v_plane,opts)
        delete(opts)

      ; Plotting options for Geopotential Heigh
        opts_z = res                          
        ;opts_z@cnLineColor = "NavyBlue"
        ;opts_z@cnHighLabelsOn = True
        ;opts_z@cnLowLabelsOn = True
        opts_z@cnLineLabelsOn = False
        opts_z@gsnContourLineThicknessesScale = 1.5


      ; MAKE PLOTS                                       

        if ( pressure .eq. 850 ) then
          opts_z@ContourParameters = (/ 50.0 /)
          contour_height = wrf_contour(a,wks,z_plane,opts_z)
          plot = wrf_map_overlays(a,wks,(/contour_rh/),pltres,mpresB)
          plot = wrf_map_overlays(a,wks,(/contour_tc,contour_height, \
                                    vector/),pltres,mpres)
        end if

        if ( pressure .eq. 700 ) then
          opts_z@ContourParameters = (/ 60.0 /)
          contour_height = wrf_contour(a,wks, z_plane,opts_z)
          plot = wrf_map_overlays(a,wks,(/contour_tc,contour_height, \
                                    vector/),pltres,mpres)
        end if
    
        if ( pressure .eq. 500 ) then
          opts_z@ContourParameters = (/ 100.0 /)
          contour_height = wrf_contour(a,wks, z_plane,opts_z)
          plot = wrf_map_overlays(a,wks,(/contour_tc,contour_height, \
                                    vector/),pltres,mpres)
        end if
    
        if ( pressure .eq. 300 ) then
          opts_z@ContourParameters = (/ 100.0 /)
          opts_z@cnLineColor         = "NavyBlue"
          contour_height = wrf_contour(a,wks, z_plane,opts_z)
          plot = wrf_map_overlays(a,wks,(/contour_spd,contour_height, \
                                    vector/),pltres,mpresB)
        end if

        delete(opts_z)
    
    
    end do      ; END OF pressure LOOP

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

    ; Plotting options for Sea Level Pressure
      opts = res          
      opts@ContourParameters = (/ 900., 1100., 10. /)
      opts@cnLineColor = "Blue"
      opts@cnInfoLabelOn = False
      ;opts@cnHighLabelsOn = True
      ;opts@cnLowLabelsOn = True
      opts@gsnContourLineThicknessesScale = 1.0
      contour_psl = wrf_contour(a,wks,slp,opts)
      delete(opts)
  
  
    ; Plotting options for Precipitation
      opts = res                        
      opts@cnLevelSelectionMode = "ExplicitLevels"
      opts@cnLevels = (/ .1, .2, .4, .8, 1.6, 3.2, 6.4, \
                         12.8, 25.6, 51.2, 102.4/)
      opts@cnFillColors = (/"White","White","DarkOliveGreen1", \
                            "DarkOliveGreen3","Chartreuse", \
                            "Chartreuse3","Green","ForestGreen", \
                            "Yellow","Orange","Red","Violet"/)
      opts@cnInfoLabelOn = False
      opts@cnConstFLabelOn = False
  
  
    ; Precipitation (color fill)
      opts@cnFillOn             = True
      opts@FieldTitle = "RAINNC"
      contour_1 = wrf_contour(a,wks, rain_exp, opts)
      opts@FieldTitle = "RAINC"
      contour_2 = wrf_contour(a,wks, rain_con, opts)
      opts@FieldTitle = "SNOWNC"
      contour_3 = wrf_contour(a,wks, snow_exp, opts)
  
    ; Total Precipitation (color fill)
      opts@FieldTitle = "Total Precipitation"
      contour_tot = wrf_contour(a,wks, rain_tot, opts)
  
    ; Precipitation Tendency (color fill)
      opts@FieldTitle = "Precipitation Tendency"
      opts@SubFieldTitle = "from " + times_sav + " to " + times(it)
      contour_tend = wrf_contour(a,wks, rain_tot_tend,opts)
  
    ; Non-Convective Precipitation Tendency (color fill)
      opts@FieldTitle = "Explicit Precipitation Tendency"
      opts@SubFieldTitle = "from " + times_sav + " to " + times(it)
      contour_res = wrf_contour(a,wks,rain_exp_tend,opts)
  
    ; Convective Precipitation Tendency (contour lines)
      opts@FieldTitle = "Param  Precipitation Tendency"
      opts@SubFieldTitle = "from " + times_sav + " to " + times(it)
      opts@cnFillOn = False
      opts@cnLineColor = "Red4"
      contour_prm = wrf_contour(a,wks,rain_con_tend,opts)
  
      delete(opts)
  
  
    ; MAKE PLOTS                                       
      plot = wrf_map_overlays(a,wks,contour_1,pltres,mpres)
      plot = wrf_map_overlays(a,wks,contour_2,pltres,mpres)
      plot = wrf_map_overlays(a,wks,contour_3,pltres,mpres)
  
      ; Total Precipitation Tendency + SLP
        ;plot = wrf_map_overlays(a,wks,(/contour_tend,contour_psl/),pltres,mpres)
  
      ; Total Precipitation 
        ;plot = wrf_map_overlays(a,wks,contour_tot,True)
  
      ; Non-Convective and Convective Precipiation Tendencies
        ;plot = wrf_map_overlays(a,wks,(/contour_res,contour_prm/),pltres,mpres)
  
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

    times_sav = times(it)
    FirstTime = False

  end do  ;       end of the time loop
end do  ;       END IF BIG FILE LOOP

end


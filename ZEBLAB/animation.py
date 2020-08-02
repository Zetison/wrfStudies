# trace generated using paraview version 5.8.0
#
# To ensure correct image size when batch processing, please search 
# for and uncomment the line `# renderView*.ViewSize = [*,*]`

#### import the simple module from the paraview
from paraview.simple import *
from numpy import pi
#### disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()

# create a new 'XML Structured Grid Reader'

R = 6370e3 # WRF radius of earth (assumes earth is a sphere)
# get active view
renderView1 = GetActiveViewOrCreate('RenderView')
# uncomment following to set a specific view size
# renderView1.ViewSize = [2180, 1084]

layout1 = GetLayout()


# create a new 'Calculator'
max_dom = 1
i_parent_start = [1, 84, 33, 33, 50, 33]
j_parent_start = [1, 31, 42, 33, 50, 33]
e_we = [100,100,100,100,100,100]
e_sn = [100,100,100,100,100,100]
#e_we = [26,26]
#e_sn = [26,26]
i_parent_start = [1, 31]
j_parent_start = [1, 31]
def getData(i):
	surfacepvd = PVDReader(FileName='/home/zetison/results/WRF/ZEBLAB/2020073112/d0'+str(i+1)+'_surface.pvd')
	surfacepvd.PointArrays = ['T2']
	surfacepvdDisplay = Show(surfacepvd, renderView1, 'StructuredGridRepresentation')
	surfacepvdDisplay.Representation = 'Surface'
	surfacepvdDisplay.OSPRayScaleArray = 'T2'
	ColorBy(surfacepvdDisplay, ('POINTS', 'T2'))
	surfacepvdDisplay.RescaleTransferFunctionToDataRange(True, False)
	surfacepvdDisplay.SetScalarBarVisibility(renderView1, True)
	surfacepvdDisplay.SetRepresentationType('Surface With Edges')
	pLUT = GetColorTransferFunction('T2')
	# change scalar bar placement
	pLUT.AutomaticRescaleRangeMode = "Never"
	pLUT.RescaleOnVisibilityChange = 0
	pLUT.RescaleTransferFunction(280,290)

	calculator1 = Calculator(Input=surfacepvd)
	
	# show data in view
	calculator1Display = Show(calculator1, renderView1, 'StructuredGridRepresentation')
	calculator1Display.SetRepresentationType('Surface With Edges')
	
	# hide data in view
	Hide(surfacepvd, renderView1)
	
	# show color bar/color legend
	# calculator1Display.SetScalarBarVisibility(renderView1, True)
	
	# Properties modified on calculator1
	calculator1.ResultArrayName = 'RotCoord'
	calculator1.CoordinateResults = 1
	
	# Properties modified on calculator1
	mincoordsX = 100562.546875
	maxcoordsX = 39923332
	mincoordsY = 101070.453125
	maxcoordsY = 19910880
#	mincoordsX = 15000
#	maxcoordsX = 2955000
#	mincoordsY = 15000
#	maxcoordsY = 2955000
	LX = maxcoordsX-mincoordsX
	LY = maxcoordsY-mincoordsY
	dx = LX/(e_we[i]-2) # Note that LY is the full width minus 2*dy (the boundary is cut away)
	dy = LY/(e_sn[i]-2) # similar to dx
	cx = maxcoordsX - (i_parent_start[i]-1)*dx
	cy = maxcoordsY - (j_parent_start[i]-1)*dy
#	cx = (i_parent_start[i]-1)*dx
#	cy = (j_parent_start[i]-1)*dy
	WRFmapping = '('+str(R)+'+coordsZ)*cos('+str(pi)+'/2*(1+2*(coordsY-'+str(cy)+')/'+str(LY)+'))*cos('+str(pi)+'*(1+2*(coordsX-'+str(cx)+')/'+str(LX)+'))*iHat' \
	            +'+('+str(R)+'+coordsZ)*cos('+str(pi)+'/2*(1+2*(coordsY-'+str(cy)+')/'+str(LY)+'))*sin('+str(pi)+'*(1+2*(coordsX-'+str(cx)+')/'+str(LX)+'))*jHat' \
	            +'+('+str(R)+'+coordsZ)*sin('+str(pi)+'/2*(1+2*(coordsY-'+str(cy)+')/'+str(LY)+'))*kHat' 
#	WRFmapping = '(coordsX + '+str(cx)+')*iHat + (coordsY + '+str(cy)+')*jHat + coordsZ*kHat'
	print([dx,dy,LX,LY])
	print(WRFmapping)
	calculator1.Function = WRFmapping
	# update the view to ensure updated data information
	renderView1.Update()


for i in range(0,max_dom):
	getData(i)
#### saving camera placements for all active views
# reset view to fit data
#renderView1.ResetCamera()


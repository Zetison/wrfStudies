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
surface_00001vts = XMLStructuredGridReader(FileName=['/home/zetison/results/WRF/ZEBLAB/2020073000/surface_00001.vts'])
surface_00001vts.PointArrayStatus = ['T2']

R = 6370e3 # WRF radius of earth (assumes earth is a sphere)
# get active view
renderView1 = GetActiveViewOrCreate('RenderView')
# uncomment following to set a specific view size
# renderView1.ViewSize = [2180, 1084]

# get layout
layout1 = GetLayout()

# show data in view
surface_00001vtsDisplay = Show(surface_00001vts, renderView1, 'StructuredGridRepresentation')

# trace defaults for the display properties.
surface_00001vtsDisplay.Representation = 'Surface'
surface_00001vtsDisplay.ColorArrayName = [None, '']
surface_00001vtsDisplay.OSPRayScaleArray = 'T2'
surface_00001vtsDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
surface_00001vtsDisplay.SelectOrientationVectors = 'None'
surface_00001vtsDisplay.ScaleFactor = 3982276.9453125
surface_00001vtsDisplay.SelectScaleArray = 'None'
surface_00001vtsDisplay.GlyphType = 'Arrow'
surface_00001vtsDisplay.GlyphTableIndexArray = 'None'
surface_00001vtsDisplay.GaussianRadius = 199113.847265625
surface_00001vtsDisplay.SetScaleArray = ['POINTS', 'T2']
surface_00001vtsDisplay.ScaleTransferFunction = 'PiecewiseFunction'
surface_00001vtsDisplay.OpacityArray = ['POINTS', 'T2']
surface_00001vtsDisplay.OpacityTransferFunction = 'PiecewiseFunction'
surface_00001vtsDisplay.DataAxesGrid = 'GridAxesRepresentation'
surface_00001vtsDisplay.PolarAxes = 'PolarAxesRepresentation'
surface_00001vtsDisplay.ScalarOpacityUnitDistance = 1655186.5998485514
surface_00001vtsDisplay.InputVectors = [None, '']
surface_00001vtsDisplay.SelectInputVectors = [None, '']
surface_00001vtsDisplay.WriteLog = ''

# init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
surface_00001vtsDisplay.OSPRayScaleFunction.Points = [0.00514701349531455, 0.0, 0.5, 0.0, 0.013980567542770658, 0.0, 0.5, 0.0, 0.0934825539698756, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
surface_00001vtsDisplay.ScaleTransferFunction.Points = [212.28143310546875, 0.0, 0.5, 0.0, 222.68084411621095, 0.0, 0.5, 0.0, 316.2755432128906, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
surface_00001vtsDisplay.OpacityTransferFunction.Points = [212.28143310546875, 0.0, 0.5, 0.0, 222.68084411621095, 0.0, 0.5, 0.0, 316.2755432128906, 1.0, 0.5, 0.0]

# get the material library
materialLibrary1 = GetMaterialLibrary()

# update the view to ensure updated data information
renderView1.Update()

# set scalar coloring
ColorBy(surface_00001vtsDisplay, ('POINTS', 'T2'))

# rescale color and/or opacity maps used to include current data range
surface_00001vtsDisplay.RescaleTransferFunctionToDataRange(True, False)

# show color bar/color legend
surface_00001vtsDisplay.SetScalarBarVisibility(renderView1, True)

# get color transfer function/color map for 'T2'
t2LUT = GetColorTransferFunction('T2')

# get opacity transfer function/opacity map for 'T2'
t2PWF = GetOpacityTransferFunction('T2')

# create a new 'Calculator'
max_dom = 1
i_parent_start = [1, 84, 33, 33, 50, 33]
j_parent_start = [1, 31, 42, 33, 50, 33]
e_we = [200,100,100,100,100,100]
e_sn = [100,100,100,100,100,100]

for i in range(0,max_dom):
	calculator1 = Calculator(Input=surface_00001vts)
	
	# show data in view
	calculator1Display = Show(calculator1, renderView1, 'StructuredGridRepresentation')
	
	# hide data in view
	Hide(surface_00001vts, renderView1)
	
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
	LX = maxcoordsX-mincoordsX
	LY = maxcoordsY-mincoordsY
	dx = (maxcoordsX-mincoordsX)/(e_we[i]-1)
	dy = (maxcoordsY-mincoordsY)/(e_sn[i]-1)
	cx = maxcoordsX + (i_parent_start[i]-1)*dx
	cy = maxcoordsY + (j_parent_start[i]-1)*dy
	WRFmapping = '('+str(R)+'+coordsZ)*cos('+str(pi)+'/2*(1+2*(coordsY-'+str(cy)+')/'+str(LY)+'))*cos('+str(pi)+'*(1+2*(coordsX-'+str(cx)+')/'+str(LX)+'))*iHat' \
	            +'+('+str(R)+'+coordsZ)*cos('+str(pi)+'/2*(1+2*(coordsY-'+str(cy)+')/'+str(LY)+'))*sin('+str(pi)+'*(1+2*(coordsX-'+str(cx)+')/'+str(LX)+'))*jHat' \
	            +'+('+str(R)+'+coordsZ)*sin('+str(pi)+'/2*(1+2*(coordsY-'+str(cy)+')/'+str(LY)+'))*kHat' 
	calculator1.Function = WRFmapping
	# update the view to ensure updated data information
	renderView1.Update()

#### saving camera placements for all active views
# reset view to fit data
renderView1.ResetCamera()


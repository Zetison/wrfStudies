from os.path import expanduser
import sys
import numpy as np
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, home+'/kode/paraUtils')
home = expanduser("~")

import earthInSpace
import SINTEFlogo

from paraview.simple import *
# get active view
renderView1 = GetActiveViewOrCreate('RenderView')
# create a new 'PVD Reader'
wrfout_d01pvd = PVDReader(FileName=home+'/results/WRF/global/2020092700/wrfout_d01.pvd')
wrfout_d01pvd.PointArrays = ['P', 'T', 'T2', 'U', 'U10', 'V', 'V10', 'W']

# get animation scene
animationScene1 = GetAnimationScene()

# get the time-keeper
timeKeeper1 = GetTimeKeeper()

# update animation scene based on data timesteps
animationScene1.UpdateAnimationUsingDataTimeSteps()

# create a new 'Calculator'
calculator1 = Calculator(Input=wrfout_d01pvd)
calculator1.Function = ''

# Properties modified on calculator1
calculator1.Function = ''

# show data in view
calculator1Display = Show(calculator1, renderView1, 'UnstructuredGridRepresentation')

# trace defaults for the display properties.
calculator1Display.Representation = 'Surface'
calculator1Display.ColorArrayName = [None, '']
calculator1Display.OSPRayScaleArray = 'P'
calculator1Display.OSPRayScaleFunction = 'PiecewiseFunction'
calculator1Display.SelectOrientationVectors = 'None'
calculator1Display.ScaleFactor = 307267.29676407116
calculator1Display.SelectScaleArray = 'None'
calculator1Display.GlyphType = 'Arrow'
calculator1Display.GlyphTableIndexArray = 'None'
calculator1Display.GaussianRadius = 15363.364838203557
calculator1Display.SetScaleArray = ['POINTS', 'P']
calculator1Display.ScaleTransferFunction = 'PiecewiseFunction'
calculator1Display.OpacityArray = ['POINTS', 'P']
calculator1Display.OpacityTransferFunction = 'PiecewiseFunction'
calculator1Display.DataAxesGrid = 'GridAxesRepresentation'
calculator1Display.PolarAxes = 'PolarAxesRepresentation'
calculator1Display.ScalarOpacityUnitDistance = 205300.10534295466
calculator1Display.InputVectors = [None, '']
calculator1Display.SelectInputVectors = [None, '']
calculator1Display.WriteLog = ''

# init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
calculator1Display.OSPRayScaleFunction.Points = [-1.60970643249866e-06, 0.0, 0.5, 0.0, -1.220962564368047e-06, 0.0, 0.5, 0.0, 2.27773224880747e-06, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
calculator1Display.ScaleTransferFunction.Points = [-986.3046875, 0.0, 0.5, 0.0, -613.85703125, 0.0, 0.5, 0.0, 2738.171875, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
calculator1Display.OpacityTransferFunction.Points = [-986.3046875, 0.0, 0.5, 0.0, -613.85703125, 0.0, 0.5, 0.0, 2738.171875, 1.0, 0.5, 0.0]

# hide data in view
Hide(wrfout_d01pvd, renderView1)

# update the view to ensure updated data information
renderView1.Update()

# Properties modified on calculator1
calculator1.Function = 'sqrt(U10^2+V10^2)'

# update the view to ensure updated data information
renderView1.Update()

# Properties modified on calculator1
calculator1.ResultArrayName = 'Wind at 10m'

# update the view to ensure updated data information
renderView1.Update()

# set scalar coloring
ColorBy(calculator1Display, ('POINTS', 'Wind at 10m'))

# rescale color and/or opacity maps used to include current data range
calculator1Display.RescaleTransferFunctionToDataRange(True, False)

# show color bar/color legend
calculator1Display.SetScalarBarVisibility(renderView1, True)

# get color transfer function/color map for 'Windat10m'
windat10mLUT = GetColorTransferFunction('Windat10m')

# get opacity transfer function/opacity map for 'Windat10m'
windat10mPWF = GetOpacityTransferFunction('Windat10m')

# Properties modified on windat10mLUT
windat10mLUT.EnableOpacityMapping = 1

################################################

programmableFilter1 = ProgrammableFilter(Input=calculator1)
programmableFilter1.Script = ''
programmableFilter1.RequestInformationScript = ''
programmableFilter1.RequestUpdateExtentScript = ''
programmableFilter1.PythonPath = ''
epoch = 1601164800 # obtained by: date -u +'%s' --date="2020-09-27"

# Properties modified on programmableFilter1
programmableFilter1.Script = 'pdo =  self.GetOutput()\n\
from datetime import datetime\n\
sexaTime = vtk.vtkStringArray()\n\
sexaTime.SetName("SexaTime")\n\
t = inputs[0].GetInformation().Get(vtk.vtkDataObject.DATA_TIME_STEP())\n\
timeAsString = str(datetime.utcfromtimestamp('+str(epoch)+'+t).strftime("%Y-%m-%d %H:%M UTC"))\n\
sexaTime.InsertNextValue(timeAsString)\n\
pdo.GetFieldData().AddArray(sexaTime)'

# strftime("%Y-%m-%d %H:%M:%S UTC"))
# create a new 'Annotate Attribute Data'
annotateAttributeData1 = AnnotateAttributeData(Input=programmableFilter1)
annotateAttributeData1.SelectInputArray = ['FIELD', 'SexaTime']

# Properties modified on annotateAttributeData1
annotateAttributeData1.Prefix = 'WRF: '

# show data in view
annotateAttributeData1Display = Show(annotateAttributeData1, renderView1, 'TextSourceRepresentation')
annotateAttributeData1Display.FontSize = 12

animationScene1.GoToLast()

# update the view to ensure updated data information
renderView1.Update()

# Rescale transfer function
windat10mLUT.RescaleTransferFunction(0.011410207580437114, 17.14499218072963)

# Rescale transfer function
windat10mPWF.RescaleTransferFunction(0.011410207580437114, 17.14499218072963)

# update the view to ensure updated data information
renderView1.Update()

# update the view to ensure updated data information
renderView1.Update()

cameraAnimationCue1 = GetCameraTrack(view=renderView1)

# create a key frame
keyFrame = CameraKeyFrame()
keyFrame.KeyTime = 0.0
keyFrame.KeyValues = [0.0]
keyFrame.Position = [6490203.814580697, 335645.9177908342,0]
keyFrame.FocalPoint = [0.0, 0.0, 0.0]
keyFrame.ViewUp = [0.0, 0.0, 1.0]
keyFrame.ViewAngle = 30.0
keyFrame.ParallelScale = 1.73
keyFrame.PositionMode = 'Path'
keyFrame.FocalPointMode = 'Path'
keyFrame.ClosedFocalPath = 0
keyFrame.ClosedPositionPath = 1

def cameraPath(t,axisCenter,radius,component):
	temp = axisCenter[component]
	if component == 0:
		temp += radius*np.cos(2*np.pi*t)
	elif component == 1:
		temp += radius*np.sin(2*np.pi*t)
	else:
		temp = 0
	return temp

N = 721
axisCenter = [0,0,0]
radius = 25000000
t = np.linspace(0.0,1.0,N)
positionPathPoints = np.zeros((N,3));
for i in range(0,3):
	positionPathPoints[:,i] = cameraPath(t,axisCenter,radius,i)

positionPathPoints = np.reshape(positionPathPoints,3*N)
positionPathPoints = [-1690414.2495330623, -31553988.481395524, 3343847.5804185355, 6702868.940717658,-8233878.7211645115, 14236046.679383121, 5329758.91244422, 67637.01959551555, 13008794.500356803, 11914519.530324157, -531541.9319099111, 12114741.09150445, 5600809.803112263, 9625778.000199161, -17918073.040220123, -2615303.514955571, 7567726.647222995, -18633238.311893556, -18949646.72433445, 25532812.726450253, -2111617.097631029, -21762221.580803443, 7109349.401801563, 11434566.391817434, -22488229.53160724, -12403647.318957299, 10196487.205719497, -18949646.724334415, -26058236.22842707, -1213078.0503668599]
#positionPathPoints = [-1690414.2495330623, -31553988.481395524, 3343847.5804185355, 6702868.940717658,-8233878.7211645115, 14236046.679383121, 5329758.91244422, 67637.01959551555, 13008794.500356803]
keyFrame.FocalPathPoints = axisCenter[:2]
keyFrame.PositionPathPoints = positionPathPoints

dummy_keyFrame = CameraKeyFrame()
dummy_keyFrame.KeyTime = 1.0
dummy_keyFrame.Position = keyFrame.Position
dummy_keyFrame.PositionPathPoints = keyFrame.PositionPathPoints
dummy_keyFrame.FocalPoint = keyFrame.FocalPoint
dummy_keyFrame.ViewUp = keyFrame.ViewUp
dummy_keyFrame.ParallelScale = keyFrame.ParallelScale

# initialize the animation track
cameraAnimationCue1.TimeMode = 'Normalized'
cameraAnimationCue1.StartTime = 0.0
cameraAnimationCue1.EndTime = 1.0
cameraAnimationCue1.Enabled = 1
cameraAnimationCue1.Mode = 'Path-based'
cameraAnimationCue1.KeyFrames = [keyFrame,dummy_keyFrame]
cameraAnimationCue1.DataSource = None


# get animation scene
animationScene1 = GetAnimationScene()

# set active source
SetActiveSource(calculator1)

# create a new 'Calculator'
calculator2 = Calculator(Input=wrfout_d01pvd)
calculator2.Function = ''

# Properties modified on calculator2
calculator2.Function = ''

# show data in view
calculator2Display = Show(calculator2, renderView1, 'UnstructuredGridRepresentation')

# trace defaults for the display properties.
calculator2Display.Representation = 'Surface'
calculator2Display.ColorArrayName = [None, '']
calculator2Display.OSPRayScaleArray = 'P'
calculator2Display.OSPRayScaleFunction = 'PiecewiseFunction'
calculator2Display.SelectOrientationVectors = 'None'
calculator2Display.ScaleFactor = 307267.29676407116
calculator2Display.SelectScaleArray = 'None'
calculator2Display.GlyphType = 'Arrow'
calculator2Display.GlyphTableIndexArray = 'None'
calculator2Display.GaussianRadius = 15363.364838203557
calculator2Display.SetScaleArray = ['POINTS', 'P']
calculator2Display.ScaleTransferFunction = 'PiecewiseFunction'
calculator2Display.OpacityArray = ['POINTS', 'P']
calculator2Display.OpacityTransferFunction = 'PiecewiseFunction'
calculator2Display.DataAxesGrid = 'GridAxesRepresentation'
calculator2Display.PolarAxes = 'PolarAxesRepresentation'
calculator2Display.ScalarOpacityUnitDistance = 205300.10534295466
calculator2Display.InputVectors = [None, '']
calculator2Display.SelectInputVectors = [None, '']
calculator2Display.WriteLog = ''

# init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
calculator2Display.OSPRayScaleFunction.Points = [-1.60970643249866e-06, 0.0, 0.5, 0.0, -1.220962564368047e-06, 0.0, 0.5, 0.0, 2.27773224880747e-06, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
calculator2Display.ScaleTransferFunction.Points = [-102.703125, 0.0, 0.5, 0.0, 178.3359375, 0.0, 0.5, 0.0, 2707.6875, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
calculator2Display.OpacityTransferFunction.Points = [-102.703125, 0.0, 0.5, 0.0, 178.3359375, 0.0, 0.5, 0.0, 2707.6875, 1.0, 0.5, 0.0]

# hide data in view
Hide(wrfout_d01pvd, renderView1)
Hide(calculator1, renderView1)

# update the view to ensure updated data information
renderView1.Update()

# Properties modified on calculator2
calculator2.Function = 'sqrt(U^2+V^2+W^2)'

# update the view to ensure updated data information
renderView1.Update()

# Properties modified on calculator2
calculator2.ResultArrayName = 'Wind'

# update the view to ensure updated data information
renderView1.Update()

# Properties modified on calculator2
calculator2.ResultArrayName = 'Wind speed'

# update the view to ensure updated data information
renderView1.Update()

# set scalar coloring
ColorBy(calculator2Display, ('POINTS', 'Wind speed'))

# rescale color and/or opacity maps used to include current data range
calculator2Display.RescaleTransferFunctionToDataRange(True, False)

# show color bar/color legend
calculator2Display.SetScalarBarVisibility(renderView1, True)

# get color transfer function/color map for 'Windspeed'
windspeedLUT = GetColorTransferFunction('Windspeed')

# get opacity transfer function/opacity map for 'Windspeed'
windspeedPWF = GetOpacityTransferFunction('Windspeed')

# Properties modified on windspeedLUT
windspeedLUT.EnableOpacityMapping = 1

# get color legend/bar for windspeedLUT in view renderView1
windspeedLUTColorBar = GetScalarBar(windspeedLUT, renderView1)

# change scalar bar placement
windspeedLUTColorBar.WindowLocation = 'AnyLocation'
windspeedLUTColorBar.ScalarBarLength = 0.32999999999999985
windspeedLUTColorBar.WindowLocation = 'UpperRightCorner'

# update the view to ensure updated data information
renderView1.Update()

# save animation
if True:
	SaveAnimation(home+'/Videos/global.ogv', renderView1, ImageResolution=[1920, 1080],
	    FrameRate=15)

#### uncomment the following to render all views
# RenderAllViews()
# alternatively, if you want to write images, you can use SaveScreenshot(...).

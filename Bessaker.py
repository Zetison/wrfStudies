# some_file.py
import sys
# insert at 1, 0 is the script path (or '' in REPL)
sys.path.insert(1, '/home/zetison/kode/paraUtils')

import earthInSpace
import SINTEFlogo

from paraview.simple import *
# get active view
renderView1 = GetActiveViewOrCreate('RenderView')
# create a new 'PVD Reader'
wrfout_d01pvd = PVDReader(FileName='/home/zetison/results/WRF/Bessaker/2020091500/wrfout_d01.pvd')
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

animationScene1.GoToLast()

# create a new 'Annotate Time Filter'
annotateTimeFilter1 = AnnotateTimeFilter(Input=calculator1)

# show data in view
annotateTimeFilter1Display = Show(annotateTimeFilter1, renderView1, 'TextSourceRepresentation')

# update the view to ensure updated data information
renderView1.Update()

# Rescale transfer function
windat10mLUT.RescaleTransferFunction(0.011410207580437114, 17.14499218072963)

# Rescale transfer function
windat10mPWF.RescaleTransferFunction(0.011410207580437114, 17.14499218072963)

# Properties modified on annotateTimeFilter1
annotateTimeFilter1.Format = 'Bessaker: %2.0f:00 UTC, 15. sep. 2020'

# update the view to ensure updated data information
renderView1.Update()

# Properties modified on annotateTimeFilter1
annotateTimeFilter1.Scale = 0.0002777777777777778

# update the view to ensure updated data information
renderView1.Update()

# get camera animation track for the view
cameraAnimationCue1 = GetCameraTrack(view=renderView1)

# create keyframes for this animation track

# create a key frame
keyFrame15980 = CameraKeyFrame()
keyFrame15980.Position = [6490203.814580697, 335645.9177908342, 11839358.935738495]
keyFrame15980.FocalPoint = [-1140808.7231353712, 2367074.5126317227, 823358.8605524981]
keyFrame15980.ViewUp = [-0.8250813257113501, -0.15854170710145818, 0.5423147914926869]
keyFrame15980.ParallelScale = 11009723.242661461
keyFrame15980.PositionPathPoints = [0.0, -4.799127132977675, -1.4029892235927837, 1.6605344456757887, -4.562983983682464, 1.1923936092505267, 2.6868011725933916, -2.583936042741949, 3.332322611328297, 2.686801172593391, 0.38208764177008936, 4.199417637358462, 1.660534445675788, 3.2021668338072473, 3.4624778588734757, -2.220446049250313e-16, 4.799127132977672, 1.4029892235927834, -1.660534445675788, 4.562983983682463, -1.1923936092505256, -2.6868011725933907, 2.583936042741948, -3.332322611328295, -2.6868011725933902, -0.3820876417700889, -4.199417637358461, -1.6605344456757873, -3.2021668338072455, -3.4624778588734744]
keyFrame15980.FocalPathPoints = [0.0, 0.0, 0.0]
keyFrame15980.ClosedPositionPath = 1

# create a key frame
keyFrame15981 = CameraKeyFrame()
keyFrame15981.KeyTime = 1.0
keyFrame15981.Position = [6490203.814580697, 335645.9177908342, 11839358.935738495]
keyFrame15981.FocalPoint = [-1140808.7231353712, 2367074.5126317227, 823358.8605524981]
keyFrame15981.ViewUp = [-0.8250813257113501, -0.15854170710145818, 0.5423147914926869]
keyFrame15981.ParallelScale = 11009723.242661461

# initialize the animation track
cameraAnimationCue1.Mode = 'Path-based'
cameraAnimationCue1.KeyFrames = [keyFrame15980, keyFrame15981]

# set active source
SetActiveSource(calculator1)

# create a new 'PVD Reader'
wrfout_d02pvd = PVDReader(FileName='/home/zetison/results/WRF/Bessaker/2020091500/wrfout_d02.pvd')
wrfout_d02pvd.PointArrays = ['P', 'T', 'T2', 'U', 'U10', 'V', 'V10', 'W']

# create a new 'PVD Reader'
wrfout_d03pvd = PVDReader(FileName='/home/zetison/results/WRF/Bessaker/2020091500/wrfout_d03.pvd')
wrfout_d03pvd.PointArrays = ['P', 'T', 'T2', 'U', 'U10', 'V', 'V10', 'W']

# create a new 'PVD Reader'
wrfout_d04pvd = PVDReader(FileName='/home/zetison/results/WRF/Bessaker/2020091500/wrfout_d04.pvd')
wrfout_d04pvd.PointArrays = ['P', 'T', 'T2', 'U', 'U10', 'V', 'V10', 'W']

# show data in view
wrfout_d02pvdDisplay = Show(wrfout_d02pvd, renderView1, 'UnstructuredGridRepresentation')

# trace defaults for the display properties.
wrfout_d02pvdDisplay.Representation = 'Surface'
wrfout_d02pvdDisplay.ColorArrayName = [None, '']
wrfout_d02pvdDisplay.OSPRayScaleArray = 'P'
wrfout_d02pvdDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
wrfout_d02pvdDisplay.SelectOrientationVectors = 'None'
wrfout_d02pvdDisplay.ScaleFactor = 104006.554404477
wrfout_d02pvdDisplay.SelectScaleArray = 'None'
wrfout_d02pvdDisplay.GlyphType = 'Arrow'
wrfout_d02pvdDisplay.GlyphTableIndexArray = 'None'
wrfout_d02pvdDisplay.GaussianRadius = 5200.3277202238505
wrfout_d02pvdDisplay.SetScaleArray = ['POINTS', 'P']
wrfout_d02pvdDisplay.ScaleTransferFunction = 'PiecewiseFunction'
wrfout_d02pvdDisplay.OpacityArray = ['POINTS', 'P']
wrfout_d02pvdDisplay.OpacityTransferFunction = 'PiecewiseFunction'
wrfout_d02pvdDisplay.DataAxesGrid = 'GridAxesRepresentation'
wrfout_d02pvdDisplay.PolarAxes = 'PolarAxesRepresentation'
wrfout_d02pvdDisplay.ScalarOpacityUnitDistance = 69366.7263816176
wrfout_d02pvdDisplay.InputVectors = [None, '']
wrfout_d02pvdDisplay.SelectInputVectors = [None, '']
wrfout_d02pvdDisplay.WriteLog = ''

# init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
wrfout_d02pvdDisplay.OSPRayScaleFunction.Points = [-1.60970643249866e-06, 0.0, 0.5, 0.0, -1.220962564368047e-06, 0.0, 0.5, 0.0, 2.27773224880747e-06, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
wrfout_d02pvdDisplay.ScaleTransferFunction.Points = [728.390625, 0.0, 0.5, 0.0, 890.28515625, 0.0, 0.5, 0.0, 2347.3359375, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
wrfout_d02pvdDisplay.OpacityTransferFunction.Points = [728.390625, 0.0, 0.5, 0.0, 890.28515625, 0.0, 0.5, 0.0, 2347.3359375, 1.0, 0.5, 0.0]

# show data in view
wrfout_d04pvdDisplay = Show(wrfout_d04pvd, renderView1, 'UnstructuredGridRepresentation')

# trace defaults for the display properties.
wrfout_d04pvdDisplay.Representation = 'Surface'
wrfout_d04pvdDisplay.ColorArrayName = [None, '']
wrfout_d04pvdDisplay.OSPRayScaleArray = 'P'
wrfout_d04pvdDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
wrfout_d04pvdDisplay.SelectOrientationVectors = 'None'
wrfout_d04pvdDisplay.ScaleFactor = 11592.329968854163
wrfout_d04pvdDisplay.SelectScaleArray = 'None'
wrfout_d04pvdDisplay.GlyphType = 'Arrow'
wrfout_d04pvdDisplay.GlyphTableIndexArray = 'None'
wrfout_d04pvdDisplay.GaussianRadius = 579.6164984427081
wrfout_d04pvdDisplay.SetScaleArray = ['POINTS', 'P']
wrfout_d04pvdDisplay.ScaleTransferFunction = 'PiecewiseFunction'
wrfout_d04pvdDisplay.OpacityArray = ['POINTS', 'P']
wrfout_d04pvdDisplay.OpacityTransferFunction = 'PiecewiseFunction'
wrfout_d04pvdDisplay.DataAxesGrid = 'GridAxesRepresentation'
wrfout_d04pvdDisplay.PolarAxes = 'PolarAxesRepresentation'
wrfout_d04pvdDisplay.ScalarOpacityUnitDistance = 7723.814131985568
wrfout_d04pvdDisplay.InputVectors = [None, '']
wrfout_d04pvdDisplay.SelectInputVectors = [None, '']
wrfout_d04pvdDisplay.WriteLog = ''

# init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
wrfout_d04pvdDisplay.OSPRayScaleFunction.Points = [-1.60970643249866e-06, 0.0, 0.5, 0.0, -1.220962564368047e-06, 0.0, 0.5, 0.0, 2.27773224880747e-06, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
wrfout_d04pvdDisplay.ScaleTransferFunction.Points = [1103.578125, 0.0, 0.5, 0.0, 1153.76640625, 0.0, 0.5, 0.0, 1605.4609375, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
wrfout_d04pvdDisplay.OpacityTransferFunction.Points = [1103.578125, 0.0, 0.5, 0.0, 1153.76640625, 0.0, 0.5, 0.0, 1605.4609375, 1.0, 0.5, 0.0]

# show data in view
wrfout_d03pvdDisplay = Show(wrfout_d03pvd, renderView1, 'UnstructuredGridRepresentation')

# trace defaults for the display properties.
wrfout_d03pvdDisplay.Representation = 'Surface'
wrfout_d03pvdDisplay.ColorArrayName = [None, '']
wrfout_d03pvdDisplay.OSPRayScaleArray = 'P'
wrfout_d03pvdDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
wrfout_d03pvdDisplay.SelectOrientationVectors = 'None'
wrfout_d03pvdDisplay.ScaleFactor = 34770.12828924502
wrfout_d03pvdDisplay.SelectScaleArray = 'None'
wrfout_d03pvdDisplay.GlyphType = 'Arrow'
wrfout_d03pvdDisplay.GlyphTableIndexArray = 'None'
wrfout_d03pvdDisplay.GaussianRadius = 1738.5064144622509
wrfout_d03pvdDisplay.SetScaleArray = ['POINTS', 'P']
wrfout_d03pvdDisplay.ScaleTransferFunction = 'PiecewiseFunction'
wrfout_d03pvdDisplay.OpacityArray = ['POINTS', 'P']
wrfout_d03pvdDisplay.OpacityTransferFunction = 'PiecewiseFunction'
wrfout_d03pvdDisplay.DataAxesGrid = 'GridAxesRepresentation'
wrfout_d03pvdDisplay.PolarAxes = 'PolarAxesRepresentation'
wrfout_d03pvdDisplay.ScalarOpacityUnitDistance = 23167.79550746678
wrfout_d03pvdDisplay.InputVectors = [None, '']
wrfout_d03pvdDisplay.SelectInputVectors = [None, '']
wrfout_d03pvdDisplay.WriteLog = ''

# init the 'PiecewiseFunction' selected for 'OSPRayScaleFunction'
wrfout_d03pvdDisplay.OSPRayScaleFunction.Points = [-1.60970643249866e-06, 0.0, 0.5, 0.0, -1.220962564368047e-06, 0.0, 0.5, 0.0, 2.27773224880747e-06, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
wrfout_d03pvdDisplay.ScaleTransferFunction.Points = [809.90625, 0.0, 0.5, 0.0, 910.7140625, 0.0, 0.5, 0.0, 1817.984375, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
wrfout_d03pvdDisplay.OpacityTransferFunction.Points = [809.90625, 0.0, 0.5, 0.0, 910.7140625, 0.0, 0.5, 0.0, 1817.984375, 1.0, 0.5, 0.0]

# update the view to ensure updated data information
renderView1.Update()

# change representation type
wrfout_d04pvdDisplay.SetRepresentationType('Feature Edges')

# change solid color
wrfout_d04pvdDisplay.AmbientColor = [0.0, 0.0, 0.0]
wrfout_d04pvdDisplay.DiffuseColor = [0.0, 0.0, 0.0]

# set active source
SetActiveSource(wrfout_d03pvd)

# change representation type
wrfout_d03pvdDisplay.SetRepresentationType('Feature Edges')

# change solid color
wrfout_d03pvdDisplay.AmbientColor = [0.0, 0.0, 0.0]
wrfout_d03pvdDisplay.DiffuseColor = [0.0, 0.0, 0.0]

# set active source
SetActiveSource(wrfout_d02pvd)

# change representation type
wrfout_d02pvdDisplay.SetRepresentationType('Outline')

# change solid color
wrfout_d02pvdDisplay.AmbientColor = [0.0, 0.0, 0.0]
wrfout_d02pvdDisplay.DiffuseColor = [0.0, 0.0, 0.0]

# change representation type
wrfout_d02pvdDisplay.SetRepresentationType('Feature Edges')

# set active source
SetActiveSource(wrfout_d01pvd)

# get display properties
wrfout_d01pvdDisplay = GetDisplayProperties(wrfout_d01pvd, view=renderView1)

# change representation type
wrfout_d01pvdDisplay.SetRepresentationType('Outline')

# change solid color
wrfout_d01pvdDisplay.AmbientColor = [0.0, 0.0, 0.0]
wrfout_d01pvdDisplay.DiffuseColor = [0.0, 0.0, 0.0]

# set active source
SetActiveSource(wrfout_d01pvd)

# show data in view
wrfout_d01pvdDisplay = Show(wrfout_d01pvd, renderView1, 'UnstructuredGridRepresentation')

# change representation type
wrfout_d01pvdDisplay.SetRepresentationType('Feature Edges')

# get camera animation track for the view
cameraAnimationCue1_2 = GetCameraTrack(view=renderView1)

# create keyframes for this animation track

# create a key frame
keyFrame16856 = CameraKeyFrame()
keyFrame16856.Position = [13167443.913250923, -6142582.365477984, 31770024.277042862]
keyFrame16856.FocalPoint = [0,0,0]
keyFrame16856.ViewUp = [0,0,1]
keyFrame16856.ParallelScale = 11009723.242661461
keyFrame16856.PositionPathPoints = [14810874.01757741, -7268992.661536203, 13631380.526461517, 12825703.015560722, -3025086.830466129, 16177647.659417953, 7033799.63242234,697025.3582761172, 12527111.38757966, 3582577.382017896, 632713.4233301905, 7248154.893394888]
keyFrame16856.FocalPathPoints = [2606383.1177147585, 471439.00487497053, 5463132.285989471]
keyFrame16856.ClosedPositionPath = 0

# create a key frame
keyFrame16857 = CameraKeyFrame()
keyFrame16857.KeyTime = 1.0
keyFrame16857.Position = [13167443.913250923, -6142582.365477984, 31770024.277042862]
keyFrame16857.FocalPoint = [0,0,0]
keyFrame16857.ViewUp = [0,0,1]
keyFrame16857.ParallelScale = 11009723.242661461

# initialize the animation track
cameraAnimationCue1_2.Mode = 'Path-based'
cameraAnimationCue1_2.KeyFrames = [keyFrame16856, keyFrame16857]

# set active source
SetActiveSource(calculator1)

# set active source
SetActiveSource(wrfout_d01pvd)

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

# hide data in view
Hide(calculator2, renderView1)

# set active source
SetActiveSource(calculator2)

# show data in view
calculator2Display = Show(calculator2, renderView1, 'UnstructuredGridRepresentation')

# show color bar/color legend
calculator2Display.SetScalarBarVisibility(renderView1, True)

# hide data in view
Hide(calculator2, renderView1)

# show data in view
calculator2Display = Show(calculator2, renderView1, 'UnstructuredGridRepresentation')

# show color bar/color legend
calculator2Display.SetScalarBarVisibility(renderView1, True)

# hide data in view
Hide(calculator2, renderView1)

# show data in view
calculator2Display = Show(calculator2, renderView1, 'UnstructuredGridRepresentation')

# show color bar/color legend
calculator2Display.SetScalarBarVisibility(renderView1, True)

# hide data in view
Hide(calculator1, renderView1)

# hide data in view
Hide(calculator2, renderView1)

# show data in view
calculator2Display = Show(calculator2, renderView1, 'UnstructuredGridRepresentation')

# show color bar/color legend
calculator2Display.SetScalarBarVisibility(renderView1, True)

# get color legend/bar for windspeedLUT in view renderView1
windspeedLUTColorBar = GetScalarBar(windspeedLUT, renderView1)

# change scalar bar placement
windspeedLUTColorBar.WindowLocation = 'AnyLocation'
windspeedLUTColorBar.ScalarBarLength = 0.32999999999999985
windspeedLUTColorBar.WindowLocation = 'UpperRightCorner'

# set active source
SetActiveSource(wrfout_d01pvd)

# show data in view
wrfout_d01pvdDisplay = Show(wrfout_d01pvd, renderView1, 'UnstructuredGridRepresentation')

# update the view to ensure updated data information
renderView1.Update()

# current camera placement for renderView1
renderView1.InteractionMode = 'Selection'
renderView1.CameraPosition = [3909570.6623362666, 468717.7630057344, 7818311.604590407]
renderView1.CameraViewUp = [0.0, 0.0, 1.0]
renderView1.CameraParallelScale = 11009700.0


# change scalar bar placement
#### saving camera placements for all active views

# current camera placement for renderView1
renderView1.InteractionMode = 'Selection'
renderView1.CameraPosition = [3909570.6623362666, 468717.7630057344, 7818311.604590407]
renderView1.CameraViewUp = [0.0, 0.0, 1.0]
renderView1.CameraParallelScale = 11009700.0

# save animation
if False:
	SaveAnimation('/home/zetison/Videos/Bessaker.ogv', renderView1, ImageResolution=[1920, 1080],
	    FrameRate=15,
	    FrameWindow=[0, 144])

#### uncomment the following to render all views
# RenderAllViews()
# alternatively, if you want to write images, you can use SaveScreenshot(...).

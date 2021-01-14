from os.path import expanduser,exists
from paraview.simple import *
#### disable automatic camera reset on 'Show'
#### disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()
 
home = expanduser("~")
sys.path.insert(1, home+'/kode/paraUtils')
from utils import *
from sources import cone 
ref = 0
outputPath = home+'/results/WRF/Frankfurt/lidar/'
ImportPresets(filename=home+'/kode/colormaps/SINTEF1.json')
saveScreenShots = True
importData = False
u_inf = 10.0 # is the freestream velocity of the fluid
p_inf = 101325 # is the static pressure in the freestream (i.e. remote from any disturbance)
rho_inf = 1.3 # is the freestream fluid density (Air at sea level and 15 °C is 1.225kg/m^3)
z_lnPltLvl = 0.6 # z coordinate of 1D plots
VRADH_max = 3.0
SAVE_HIST = 10
noSteps=2113
noSteps=1056
animStart=720
color = 'blue' # color of SINTEF logo
frameRate = 20
printLogo           = 1
plotLIC             = 1
plot1Dcurves        = 0 
plotStreamLines     = 0 
plotVolumeRendering = 0 
plotyplus           = 0 
plotOverTime        = 0
plotMesh            = 0
makeVideo           = 1 
viewSizeSlice=[1920,520]
viewSizeSlice2=[2*1920,2*520]
scalarBarLength = 0.2
scalarBarLength2 = 0.92
lidarLoc = [466150.8125,5543020,125.2]
phi = 3
h_max = 900 - lidarLoc[2]
# get animation scene
animationScene1 = GetAnimationScene()
# get the time-keeper
timeKeeper1 = GetTimeKeeper()
fileName = outputPath+'SED_pvdfilename'
wrfFileName = outputPath+'../SED_WRF_FOLDER/wrfout_d04_vol.pvd'

vtkName = outputPath+'cone'
cone(lidarLoc,h_max,phi,n=200,name=vtkName)
# create a new 'XML Unstructured Grid Reader'
lidar = PVDReader(registrationName='lidar', FileName=fileName)
wrf = PVDReader(registrationName='wrf', FileName=wrfFileName)
#lidar = XMLUnstructuredGridReader(registrationName='fileName', FileName=fileNames)
lidar.CellArrays = ['VRADH']
wrf.PointArrays = ['U','V','W','P','T']

cellDatatoPointData1 = CellDatatoPointData(registrationName='CellDatatoPointData1', Input=lidar)
cellDatatoPointData1.CellDataArraytoprocess = ['VRADH']
# update animation scene based on data timesteps
animationScene1.UpdateAnimationUsingDataTimeSteps()

# get active view
renderView1 = GetActiveViewOrCreate('RenderView')
layout1 = GetLayout()

# create a new 'Calculator'
calculator0 = Calculator(registrationName='Calculator_r', Input=wrf)
calculator0.Function = '(coordsX-'+str(lidarLoc[0])+')*iHat + (coordsY-'+str(lidarLoc[1])+')*jHat + (coordsZ-'+str(lidarLoc[2])+')*kHat'
calculator0.ResultArrayName = 'r' 

# create a new 'Calculator'
calculator1 = Calculator(registrationName='Calculator1', Input=calculator0)
calculator1.ResultArrayName = 'VRADH'
calculator1.Function = '(U*r_X+V*r_Y+W*r_Z)/mag(r)'
VRADHLUT = GetColorTransferFunction('VRADH')
VRADHPWF = GetOpacityTransferFunction('VRADH')

animationScene1.GoToLast()
LoadPalette(paletteName='WhiteBackground')
renderView1.OrientationAxesVisibility = 0

####################################################################################
## Layout 1 - Surface LIC plots
# create a new 'Clip'
if plotLIC:
    cone = LegacyVTKReader(registrationName='Cone', FileNames=[vtkName+'.vtk'])
    
    resampleWithDataset1 = ResampleWithDataset(SourceDataArrays=calculator1, DestinationMesh=lidar)
    resampleWithDataset1.CellLocator = 'Static Cell Locator'
    resampleWithDataset1Display = Show(resampleWithDataset1, renderView1, 'StructuredGridRepresentation')
    resampleWithDataset1Display.ColorArrayName = ['POINTS', 'VRADH']
    resampleWithDataset1Display.Ambient = 1.0
    resampleWithDataset1Display.Diffuse = 0.0

    layout1.SplitHorizontal(0, 0.5)
    # Create a new 'Render View'
    renderView2 = CreateView('RenderView')
    renderView2.AxesGrid = 'GridAxes3DActor'
    renderView2.StereoType = 'Crystal Eyes'
    renderView2.CameraFocalDisk = 1.0
    AssignViewToLayout(view=renderView2, layout=layout1, hint=2)

    
    lidarDisplay = Show(lidar, renderView2, 'StructuredGridRepresentation')
    #lidarDisplay.ColorArrayName = ['CELLS', 'VRADH']
    lidarDisplay.Ambient = 1.0
    lidarDisplay.Diffuse = 0.0
    ColorBy(lidarDisplay, ('CELLS', 'VRADH'))
    #resampleWithDataset = ResampleWithDataset(SourceDataArrays=cellDatatoPointData1, DestinationMesh=cone)
    #resampleWithDataset.CellLocator = 'Static Cell Locator'
    #lidarDisplay = Show(resampleWithDataset, renderView2, 'StructuredGridRepresentation')
    #lidarDisplay.ColorArrayName = ['POINTS', 'VRADH']
    #lidarDisplay.Ambient = 1.0
    #lidarDisplay.Diffuse = 0.0

    programmableFilter1 = ProgrammableFilter(Input=lidar)
    programmableFilter1.Script = ''
    programmableFilter1.RequestInformationScript = ''
    programmableFilter1.RequestUpdateExtentScript = ''
    programmableFilter1.PythonPath = ''
    epoch = 1607169600 # obtained by: date -u +'%s' --date="2020-09-27 12:00:00"
    
    # Properties modified on programmableFilter1
    programmableFilter1.Script = 'pdo =  self.GetOutput()\n\
from datetime import datetime\n\
sexaTime = vtk.vtkStringArray()\n\
sexaTime.SetName("SexaTime")\n\
t = inputs[0].GetInformation().Get(vtk.vtkDataObject.DATA_TIME_STEP())\n\
timeAsString = str(datetime.utcfromtimestamp('+str(SED_current_epoch)+'+t).strftime("%Y-%m-%d %H:%M:%S UTC"))\n\
sexaTime.InsertNextValue(timeAsString)\n\
pdo.GetFieldData().AddArray(sexaTime)'
    
    # strftime("%Y-%m-%d %H:%M:%S UTC"))
    # create a new 'Annotate Attribute Data'
    annotateAttributeData1 = AnnotateAttributeData(Input=programmableFilter1)
    annotateAttributeData1.SelectInputArray = ['FIELD', 'SexaTime']
    
    # Properties modified on annotateAttributeData1
    annotateAttributeData1.Prefix = ''
    
    # show data in view
    annotateAttributeData1Display = Show(annotateAttributeData1, renderView1, 'TextSourceRepresentation')
    annotateAttributeData1Display.FontSize = 8
    #annotateTimeStep(calculator1,renderView1,'UpperLeftCorner', SAVE_HIST,color=[0.0,0.0,0.0])

    VRADHLUTColorBar = GetScalarBar(VRADHLUT, renderView1)
    VRADHLUTColorBar.Title = 'VRADH'
    VRADHLUTColorBar.Orientation = 'Vertical'
    VRADHLUTColorBar.WindowLocation = 'UpperRightCorner'
    VRADHLUTColorBar.ComponentTitle = ''
    VRADHLUTColorBar.ScalarBarLength = 0.3 
    VRADHLUT.RescaleTransferFunction(-10.0, 10.0)
    VRADHLUT.ApplyPreset('SINTEF1', True)
    VRADHLUT.NanColor = [1.0, 1.0, 1.0]
    
    VRADHLUTColorBar.WindowLocation = 'LowerCenter'
    VRADHLUTColorBar.HorizontalTitle = 1
    VRADHLUTColorBar.AutoOrient = 0
    VRADHLUTColorBar.Orientation = 'Horizontal'
    VRADHLUTColorBar.RangeLabelFormat = '%-#6.1f'

    if printLogo:
        insertSINTEFlogo(renderView2,'blue', position=[0.81,0])
    
    lidarDisplay.SetScalarBarVisibility(renderView2, False)
    renderView1.InteractionMode = '2D'
    renderView1.CameraPosition = [466161.5742815666, 5541002.50741783, 231205.32145070643]
    renderView1.CameraFocalPoint = [466161.5742815666, 5541002.50741783, 2535.653536324522]
    renderView1.CameraParallelScale = 17027.58881419862
    renderView1.ViewSize = [960,1080]
    
    renderView2.OrientationAxesVisibility = 0
    renderView2.InteractionMode = '2D'
    renderView2.CameraPosition = [466161.5742815666, 5541002.50741783, 231205.32145070643]
    renderView2.CameraFocalPoint = [466161.5742815666, 5541002.50741783, 2535.653536324522]
    renderView2.CameraParallelScale = 17027.58881419862
    renderView2.ViewSize = [960,1080]
    timeKeeper1 = GetTimeKeeper()
    timeKeeper1.Time = 0.0
    saveScreenShot(layout1,outputPath+'SED_WRF_FOLDER',saveScreenShots, saveAllViews=1)
    saveAnimation(layout1,outputPath+'SED_WRF_FOLDER',noSteps,makeVideo,viewSize=[1920,1080],frameRate=frameRate,animStart=animStart, saveAllViews=1)

RenderAllViews()

* In order to create high resolution topography use qgis.
1. Open a high resolution .tif file in qgis (i.e. from geomaker or from https://land.copernicus.eu/imagery-in-situ/eu-dem/eu-dem-v1.1 )
2. Save desired area as "Project CRS: EPSG:4326 - WGS 84" in order to find xmin,ymin,xmax,ymax and xres,yres for input using in gdalwarp (see the convertTIF script)
3. Open this file and export file to WPS files using the GIS4WRF plugin (in qgis: "Datasets" -> "Process" and choose "No" to the data set being categorical)

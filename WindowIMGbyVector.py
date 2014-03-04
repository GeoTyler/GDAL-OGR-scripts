#-------------------------------------------------------------------------------
# Name:		Raster Window, NDVI, Reclass
# Purpose:   To window a landsat image by vector coordinates, and then
#				create an NDVI image, and then a reclassified NDVI image. 
#
# Author:      Tyler Dahlberg
#
# Created:     01/03/2014
#-------------------------------------------------------------------------------


#-------------------------------------------------------------------------------
    #Import Modules and set working directory

import os, gdal, ogr, numpy

## Set working directory and paths
os.chdir(r'C:\Users\tyler\Dropbox\Clark\S14\OSGIS\Data\Raster')


#-------------------------------------------------------------------------------
    # Get the Raster Attributes

img_filename = r"C:\Users\tyler\Dropbox\Clark\S14\OSGIS\Data\Raster\landsat_tm.img"
driver_img = gdal.GetDriverByName('HFA')
driver_img.Register()
landsat_ds = gdal.Open(img_filename, 0)
cols = landsat_ds.RasterXSize
rows = landsat_ds.RasterYSize
geotransform = landsat_ds.GetGeoTransform()
projection = landsat_ds.GetProjection()

originX = geotransform[0] #Origin X of Raster image
originY = geotransform[3] #Origin Y of Raster image
pixelWidth = geotransform[1] #Pixel width resolution
pixelHeight = geotransform[5] #Pixel height resolution
print 'Raster attributes acquired'


#------------------------------------------------------------------------------
    # Get Vector Attributes

shpDriver = ogr.GetDriverByName('ESRI Shapefile')
shpFilename = r"C:\Users\tyler\Dropbox\Clark\S14\OSGIS\Data\Raster\clip.shp"
shpOpen = shpDriver.Open(shpFilename,0)
lyr = shpOpen.GetLayer()
extent = lyr.GetExtent()
MinX = extent[0] #Minimum X of Vector boundary
MaxX = extent[1] #Maximum X of Vector boundary
MinY = extent[2] #Minimum Y of Vector boundary
MaxY = extent[3] #Maximum Y of Vector boundary
print 'Vector attributes acquired'


#-------------------------------------------------------------------------------
    # Calculate Pixel offsets of Vector boundaries from Raster image

offset_x = int((MinX-originX)/pixelWidth)
offset_y = int((MaxY-originY)/pixelHeight)
newcols = cols - offset_x
newrows = rows - offset_y

print 'Offset distance from image X origin to Vector X origin: %d pixels' % offset_x
print 'Offset distance from image Y origin to Vector Y origin: %d pixels' % offset_y
print 'Number of columns in original raster: %d' % cols
print 'Number of columns in new raster: %d' % newcols
print 'Number of rows in original raster: %d' % rows
print 'Number of rows in new raster: %d' % newrows



#-------------------------------------------------------------------------------
    # Load original raster bands

# Load original bands
band1 = landsat_ds.GetRasterBand(1)
band2 = landsat_ds.GetRasterBand(2)
band3 = landsat_ds.GetRasterBand(3)
band4 = landsat_ds.GetRasterBand(4)
band5 = landsat_ds.GetRasterBand(5)
band6 = landsat_ds.GetRasterBand(6)
band7 = landsat_ds.GetRasterBand(7)
print 'Successfully read in original bands'


#-------------------------------------------------------------------------------
    # Read original raster bands in as data arrays

array1 = band1.ReadAsArray(offset_x,offset_y,newcols,newrows).astype(numpy.float32)
array2 = band2.ReadAsArray(offset_x,offset_y,newcols,newrows).astype(numpy.float32)
array3 = band3.ReadAsArray(offset_x,offset_y,newcols,newrows).astype(numpy.float32)
array4 = band4.ReadAsArray(offset_x,offset_y,newcols,newrows).astype(numpy.float32)
array5 = band5.ReadAsArray(offset_x,offset_y,newcols,newrows).astype(numpy.float32)
array6 = band6.ReadAsArray(offset_x,offset_y,newcols,newrows).astype(numpy.float32)
array7 = band7.ReadAsArray(offset_x,offset_y,newcols,newrows).astype(numpy.float32)
print 'Successfully read original arrays'


#-------------------------------------------------------------------------------
    # Write arrays to new windowed bands in windowed dataset

    ## The following dataset was created with the new offsets and dimensions
windowDs = driver_img.Create('window.img',newcols,newrows,7,gdal.GDT_Float32)
gdal.SetConfigOption('HFA_USE_RRD','YES') # Tells GDAL to build pyramids
windowDs.BuildOverviews(overviewlist=[2,4,8,16,32,64,128])
windowDs.SetGeoTransform(geotransform)
windowDs.SetProjection(projection)
print 'Pyramids for new dataset created'


#-------------------------------------------------------------------------------
    # Call the bands inside the image dataset, then write arrays to them

windowDs.GetRasterBand(1).WriteArray(array1)
windowDs.GetRasterBand(2).WriteArray(array2)
windowDs.GetRasterBand(3).WriteArray(array3)
windowDs.GetRasterBand(4).WriteArray(array4)
windowDs.GetRasterBand(5).WriteArray(array5)
windowDs.GetRasterBand(6).WriteArray(array6)
windowDs.GetRasterBand(7).WriteArray(array7)

outBand1 = windowDs.GetRasterBand(1).SetNoDataValue(-999)
outBand2 = windowDs.GetRasterBand(2).SetNoDataValue(-999)
outBand3 = windowDs.GetRasterBand(3).SetNoDataValue(-999)
outBand4 = windowDs.GetRasterBand(4).SetNoDataValue(-999)
outBand5 = windowDs.GetRasterBand(5).SetNoDataValue(-999)
outBand6 = windowDs.GetRasterBand(6).SetNoDataValue(-999)
outBand7 = windowDs.GetRasterBand(7).SetNoDataValue(-999)

#-------------------------------------------------------------------------------
    # Flush the caches

windowDs = None
print 'Band caches flushed'


#-------------------------------------------------------------------------------
    # Set up NDVI equation
# NDVI = (Band 4 - Band 3) / (Band 4 + Band 3)
subset_Ds = gdal.Open(r'C:\Users\Tyler\Dropbox\Clark\S14\OSGIS\Data\Raster\window.img',0)

NIRband = subset_Ds.GetRasterBand(4)
Redband = subset_Ds.GetRasterBand(3)
print 'Read in NIR and Red bands'

NIR = NIRband.ReadAsArray(0,0,newcols,newrows).astype(numpy.float)
Red = Redband.ReadAsArray(0,0,newcols,newrows).astype(numpy.float)

mask = numpy.greater(NIR+Red,0) # Creates mask

NDVI = numpy.choose(mask, (-999, (NIR - Red) / (NIR + Red))) #Applies mask

NDVI_Ds = driver_img.Create('ndvi.img',newcols,newrows,1,gdal.GDT_Float32)
NDVI_band = NDVI_Ds.GetRasterBand(1)
NDVI_band.WriteArray(NDVI,0,0)
NDVI_band.SetNoDataValue(-999)
gdal.SetConfigOption('HFA_USE_RRD','YES') # Tells GDAL to build pyramids
NDVI_Ds.BuildOverviews(overviewlist=[2,4,8,16,32,64,128])
NDVI_Ds.SetGeoTransform(geotransform)
NDVI_Ds.SetProjection(projection)



#-------------------------------------------------------------------------------
    #Create a reclassed ndvi image
Reclass_Ds = driver_img.Create('reclass.img',newcols,newrows,1,gdal.GDT_Float32)
Reclass_band = Reclass_Ds.GetRasterBand(1)
Reclass = NDVI_band.ReadAsArray(0,0,newcols,newrows).astype(numpy.float) # Creates binary image with an if else statement

# for loop to reclassify NDVI image to values of 0 or 1
for i in range(0,newrows):
    for j in range(0, newcols):
        if Reclass[i,j] >= 0:
            Reclass[i,j] = 1
        else:
            Reclass[i,j] = 0
print 'Reclassified NDVI image to binary'

Reclass_band.WriteArray(Reclass,0,0)
Reclass_band.SetNoDataValue(-999)
gdal.SetConfigOption('HFA_USE_RRD','YES')
Reclass_Ds.BuildOverviews(overviewlist=[2,4,8,16,32,64,128])
Reclass_Ds.SetGeoTransform(geotransform)
Reclass_Ds.SetProjection(projection)
print 'New Reclassified image written to disk'

NDVI_Ds = None
Reclass_Ds = None
print 'Script Completed Successfully!'

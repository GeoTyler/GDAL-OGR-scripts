import gdal,gdalconst,ogr
from gdalconst import *

# full path to the image I'm creating
src_filename = r'Y:\Personal\0.Tian\Raster\landsat_tm.img'

# full path to the shapefile I'm reading
shp_filename = r'Y:\Personal\0.Tian\Raster\worcester_colleges.shp'

# reading the 1st band (or the blue band) in the TM
src_ds=gdal.Open(src_filename, GA_ReadOnly) 
gt=src_ds.GetGeoTransform()
rb=src_ds.GetRasterBand(1)

# reading the shapefile 
driver = ogr.GetDriverByName('ESRI Shapefile')
ds=driver.Open(shp_filename, 0)
lyr=ds.GetLayer()

feat = lyr.GetNextFeature()
while feat:
    geom = feat.GetGeometryRef()
    mx = geom.GetX()
    my = geom.GetY()  #coord in map units

    #Convert from map to pixel coordinates.
    #Only works for geotransforms with no rotation.
    
    xoffset = int((mx - gt[0]) / gt[1])
    #x gt[0]--> x coordinate of UL, gt[3] --> y coordinate of UL
    yoffset = int((my - gt[3]) / gt[5])

    # gt[1] is the pixel size in x direction
    # gt[5] is the pixel size in y direction

    arrayVals=rb.ReadAsArray(xoffset,yoffset,1,1) #Assumes 16 bit int aka 'short'
    print feat.GetField('COLLEGE'), arrayVals[0,0]

    feat = lyr.GetNextFeature()

ds.Destroy()



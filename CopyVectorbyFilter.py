#-------------------------------------------------------------------------------
# Purpose:     To copy features matching an attribute from one layer to another
# Author:      Tyler Dahlberg
#
# Created:     15/02/2014
# Copyright:   (c) Tyler 2014
#-------------------------------------------------------------------------------

## Import the necessary modules
import ogr, os

## Set working directory
os.chdir(r'C:\Users\tdahlberg\Dropbox\Clark\S14\OSGIS\Data\Worcester')


## Call the ESRI shapefile driver
driver = ogr.GetDriverByName('ESRI Shapefile')
oldShape = 'parks.shp'
newShape = 'playgrounds'


## Delete the output shapefile if it already exists
if os.path.exists(newShape+'.shp'):
    driver.DeleteDataSource(newShape+'.shp')


## Creates output datasources
outds = driver.CreateDataSource(newShape+'.shp') #creates data source
inds = driver.Open(oldShape,0) # links to old data source
print 'New shapefile, %s, created.' % (newShape)


## Creates output layers
outlyr = outds.CreateLayer(newShape, geom_type = ogr.wkbPolygon) #creates layer
print 'New layer inside shapefile created.'
inlyr = inds.GetLayer()


## Gets the input feature
infeature = inlyr.GetFeature(0)


## Gets field definitions from input layer
MBLFieldDefn = infeature.GetFieldDefnRef('MBL')
ParkFieldDefn = infeature.GetFieldDefnRef('PARK_NAME')
print 'Fields definitions accessed.'


## Writes new fields to output layer
outlyr.CreateField(MBLFieldDefn) #Creates new field from prior definition
outlyr.CreateField(ParkFieldDefn) #Creates new field from prior definition
print 'Field definitions added to output layer.'


## Get spatial ref from original file and transform to ESRI format
inds = driver.Open(oldShape,0)
parks_lyr = inds.GetLayer()
parks_sr = parks_lyr.GetSpatialRef()
parks_sr.MorphToESRI #converts prj file to ESRI format
print 'Spatial reference transformed to Esri format.'


## Write projection to output shapefile
prjFile = open(newShape+'.prj','w')
prjFile.write(parks_sr.ExportToWkt())
prjFile.close()
print'Successfully wrote spatial reference file.'


## Loop to copy attributes that match 'Playground' from input to output layer
featureDefn = outlyr.GetLayerDefn()
#searchphrase = 'Playrground'
inFeat = inlyr.GetNextFeature()
while inFeat:
    park_type2 = inFeat.GetField('PARK_TYPE2')  ##This needs to be PARK_TYPE2
    if 'Playground' in park_type2: #checks for 'Playground' attribute
        outFeature = ogr.Feature(featureDefn) #sets the output feature
        geom = inFeat.GetGeometryRef() #calls the input geometry
        outFeature.SetGeometry(geom) #sets the output geometry
        out1 = inFeat.GetField('MBL') #gets input attributes from 'MBL'
        outFeature.SetField('MBL',out1) #sets the output attributes from 'MBL'
        outlyr.CreateFeature(outFeature)
        outFeature.Destroy()
        outFeature.SetField('PARK_NAME', park_type2)
    inFeat.Destroy()
    inFeat = inlyr.GetNextFeature()
inds.Destroy()
inds.Destroy()

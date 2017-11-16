
# ---------------------------------------------------------------------------
# SelectionToSQLQuery.py
# Created on: 2016-07-02 14:02:29.00000
# Author: George Oliver (georgeoyliver@gmail.com)
# Description: Create an ArcGIS SQL query from the selected records in a feature layer or table in the
#               ArcMap Table of Contents.  Optionally apply this SQL query as a definition query.
# ---------------------------------------------------------------------------

# Import modules
import arcpy

arcpy.env.overwriteOutput = True

# Script arguments
in_layer = arcpy.GetParameterAsText(0)
freq_field = arcpy.GetParameterAsText(1)
apply_def_query = arcpy.GetParameterAsText(2)

mxd = arcpy.mapping.MapDocument("CURRENT")

query = freq_field + " IN ("

# check the type of the field selected.  Need different concatenation equations depending on field type.
fieldType = ""
for f in arcpy.ListFields(in_layer):
    if f.baseName == freq_field:
        fieldType = f.type

if fieldType in ("Date", "Blob", "Geometry", "Guid", "Raster"):
    e = "Unexpected field type: field '" + freq_field + "', type '" + fieldType + "'."
    raise Exception(e)

with arcpy.da.SearchCursor(in_layer, freq_field) as cursor:
    if fieldType == "String":
        for row in cursor:
            query += "'" + row[0] + "', "
    else:
        for row in cursor:
            query += str(row[0]) + ", "
    query = query[:-2] + ")"     ## remove the final space/comma, add  close parentheses

arcpy.AddMessage("Output query: \n\n" + query + "\n")

## apply definition query
## also keep track of whether the definition query is applied to multiple layers/table views
## and add a warning if so

if apply_def_query == "true":
    arcpy.AddMessage("Applying definition query...")
    layer_list = arcpy.mapping.ListLayers(mxd)
    tableview_list = arcpy.mapping.ListTableViews(mxd)
    matchingLayers = 0
    for layer in layer_list:
       if layer.name == in_layer:
           layer.definitionQuery = query
           arcpy.RefreshActiveView()
           matchingLayers += 1
           arcpy.AddMessage("Layer = " + layer.name)
    for table in tableview_list:
       if table.name == in_layer:
           table.definitionQuery = query
           arcpy.RefreshActiveView()
           matchingLayers += 1
           arcpy.AddMessage("TableView = " + table.name)
    if matchingLayers > 1:
        arcpy.AddWarning("More than one Layer or Table View had the same name.  The definition query was applied to each.")

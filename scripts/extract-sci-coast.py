from pathlib import Path
import cartopy.feature as cfeature
import geopandas as gpd
from shapely.geometry import box
import matplotlib.pyplot as plt
import cartopy.crs as ccrs


# Define outfile path
root_dir = Path().resolve().parent
out_fpath = root_dir / 'data' / 'geospatial' / 'sci-coastline' / 'sci-coastline.shp'

# Define your bounding box for santa cruz island
latmin = 33.8
latmax = 34.2
lonmin = -119.94
lonmax = -119.48
bounding_box = box(lonmin, latmin, lonmax, latmax)

# Create a NaturalEarthFeature for coastlines
coastline_feature = cfeature.NaturalEarthFeature(
    category='physical',
    name='coastline',
    scale='10m',
    facecolor='none'
)

# Extract geometries from the feature
geometries = list(coastline_feature.geometries())

# Create a GeoDataFrame from the geometries
coast_gdf = gpd.GeoDataFrame(geometry=geometries, crs="EPSG:4326")

# Clip the GeoDataFrame to the bounding box
clipped_coast = gpd.clip(coast_gdf, bounding_box)

# Export the clipped coastline to a shapefile
clipped_coast.to_file(out_fpath)

# Plot the object
clipped_coast.plot()
plt.title("Clipped Coastline (33.8°N to 34.2°N, -119.98°E to -119.48°E)")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.show()

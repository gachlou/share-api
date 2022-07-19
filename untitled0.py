# -*- coding: utf-8 -*-
"""
Created on Mon Jun 20 11:25:36 2022

@author: r.gachlou
"""

from sentinelhub import SHConfig
import logging
from http.client import HTTPConnection
#for import data
import os
import datetime
import numpy as np
import matplotlib.pyplot as plt
from sentinelhub import (MimeType,CRS,BBox,SentinelHubRequest,SentinelHubDownloadClient,DataCollection,bbox_to_dimensions,DownloadRequest,MosaickingOrder)


from utils  import plot_image

config = SHConfig()

config.instance_id = 'ab598b07-91f4-43d6-9954-2583527bb66f'
config.sh_client_id = 'db15b13d-f6ef-48ec-bb2b-53049c8476bb'
config.sh_client_secret = 'x<)Jj*(yPl)*EON8!^4XhP/@mj;(m;TAP@u?okOo'

logging.basicConfig(level=logging.DEBUG)
logging.captureWarnings(True)


"""In case standard logs are not detailed enough, it is possible
 to obtain full information about HTTP requests by propagating 
 low-level urllib3 logs
"""
# requests_log = logging.getLogger("requests.packages.urllib3")
# requests_log.setLevel(logging.DEBUG)
# requests_log.propagate = True

"""# The default format is '%(levelname)s:%(name)s:%(message)s'

logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s:%(name)s:%(threadName)s:%(message)s',
)"""




betsiboka_coords_wgs84 = [50.44641097403206,30.78320023455708,
54.55103696696979,36.8838011535297 ]
resolution =10
betsiboka_bbox = BBox(bbox=betsiboka_coords_wgs84, crs=CRS.WGS84)
betsiboka_size = bbox_to_dimensions(betsiboka_bbox, resolution=resolution)

print(f"Image shape at {resolution} m resolution: {betsiboka_size} pixels")

#############################################################################
#############################################################################
#########################################################


evalscript = """
//VERSION=3
function setup() {
  return {
    input: [{bands:["B02", "B03", "B04"],
             units:"DN"}],
    output: { bands: 3, sampleType: "INT16"}
  }
}

function evaluatePixel(sample) {
 
  return [sample.B04, sample.B03, sample.B02,];;
}
"""

request_band = SentinelHubRequest(
    evalscript=evalscript,
    input_data=[SentinelHubRequest.input_data(data_collection=DataCollection.SENTINEL2_L1C,
                                              time_interval=("2022-01-01", "2022-01-16"))],
    responses=[SentinelHubRequest.output_response("default", MimeType.PNG)],
    bbox=betsiboka_bbox,
    size=betsiboka_size,
    config=config,)
  
# """mosaicking_order=MosaickingOrder.LEAST_CC,"""  in part input

imgs = request_band.get_data()

print(f"Returned data is of type = {type(imgs)} and length {len(imgs)}.")
print(f"Single element in the list is of type {type(imgs[-1])} and has shape {imgs[-1].shape}")


image = imgs[0]
print(f"Image type: {image.dtype}")

# plot function
# factor 1/255 to scale between 0-1
# factor 3.5 to increase brightness
plot_image(image[:,:,1],vmin=1,vmax=38)
plot_image(image, factor=3.5 / 255, clip_range=(0, 1))
# print("Supported DataCollections:\n")
# for collection in DataCollection.get_available_collections():
#     print(collection)





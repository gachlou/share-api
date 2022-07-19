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


from utils import plot_image

config = SHConfig()

# config.instance_id = 'ab598b07-91f4-43d6-9954-2583527bb66f'
# config.sh_client_id = 'db15b13d-f6ef-48ec-bb2b-53049c8476bb'
# config.sh_client_secret = 'x<)Jj*(yPl)*EON8!^4XhP/@mj;(m;TAP@u?okOo'

logging.basicConfig(level=logging.DEBUG)
logging.captureWarnings(True)

config.save()
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




betsiboka_coords_wgs84 = [
54.54609485882231,36.8888400970877,
54.55128092626309,36.88273332647389 ]
resolution =5
betsiboka_bbox = BBox(bbox=betsiboka_coords_wgs84, crs=CRS.WGS84)
betsiboka_size = bbox_to_dimensions(betsiboka_bbox, resolution=resolution)

print(f"Image shape at {resolution} m resolution: {betsiboka_size} pixels")
#############################################################################

start = datetime.datetime(2022, 1, 1)
end = datetime.datetime(2022, 7, 11)
n_chunks = 10
tdelta = (end - start) / n_chunks
edges = [(start + i * tdelta).date().isoformat() for i in range(n_chunks)]
slots = [(edges[i], edges[i + 1]) for i in range(len(edges) - 1)]

print("Monthly time windows:\n")
for slot in slots:
    print(slot)

# for i in range(n_chunks):
#     print(i)
    
    

#############################################################################
#############################################################################


evalscript = """
//VERSION=3
function setup() {
  return {
    input: [{bands:["B04","B08"],
             units:"DN"}],
    output: { bands: 1, sampleType: "FLOAT32"}
  }
}

function evaluatePixel(sample) {
  NDVI=(sample.B08-sample.B04)/(sample.B08+sample.B04)
  return [NDVI];;
}
"""


##############################################################
def get_request(time_interval):
    return SentinelHubRequest(
           evalscript=evalscript,
    input_data=[SentinelHubRequest.input_data(data_collection=DataCollection.SENTINEL2_L1C,
                                              time_interval=time_interval,mosaicking_order=MosaickingOrder.LEAST_CC,)],
    responses=[SentinelHubRequest.output_response("default", MimeType.TIFF)],
    bbox=betsiboka_bbox,
    size=betsiboka_size,
    config=config,)
  
# """mosaicking_order=MosaickingOrder.LEAST_CC,"""  in part input
#("2019-06-01", "2020-06-01")

list_of_requests = [get_request(slot) for slot in slots]
list_of_requests = [request.download_list[0] for request in list_of_requests]
#print(f"Returned data is of type = {type(imgs)} and length {len(imgs)}.")
#print(f"Single element in the list is of type {type(imgs[-1])} and has shape {imgs[-1].shape}")

#imgs = request_band.get_data()
imgs = SentinelHubDownloadClient(config=config).download(list_of_requests, max_threads=2)

position_to_select = [1, 3, 6]
#image = imgs[position_to_select]
image=imgs[1]
#print(f"Image type: {image.dtype}")

# plot function
# factor 1/255 to scale between 0-1
# factor 3.5 to increase brightness
plot_image(image,vmin=0,vmax=1)
 
# print("Supported DataCollections:\n")
# for collection in DataCollection.get_available_collections():
#     print(collection)

b=[]
for i in range(0,len(slots)):
    b += list(slots[i][0].split(" ") )
    
    
mean_image=[]
for im in imgs :
    print(np.mean(im))
    mean_image.append(np.mean(im))
    

plt.figure()
plt.plot(b,mean_image)



# -*- coding: utf-8 -*-
"""
Created on Sat Jul  2 09:38:11 2022

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
from sentinelhub import (MimeType,CRS,BBox,SentinelHubRequest,SentinelHubDownloadClient,
                         DataCollection,bbox_to_dimensions,DownloadRequest,MosaickingOrder)


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




betsiboka_coords_wgs84 = [51.101357,35.456726,51.508911,35.991009]
resolution =100
betsiboka_bbox = BBox(bbox=betsiboka_coords_wgs84, crs=CRS.WGS84)
betsiboka_size = bbox_to_dimensions(betsiboka_bbox, resolution=resolution)

print(f"Image shape at {resolution} m resolution: {betsiboka_size} pixels")

#############################################################################
#############################################################################
#############################################################################

start = datetime.datetime(2019, 1, 1)
end = datetime.datetime(2019, 12, 31)
n_chunks = 13
tdelta = (end - start) / n_chunks
edges = [(start + i * tdelta).date().isoformat() for i in range(n_chunks)]
slots = [(edges[i], edges[i + 1]) for i in range(len(edges) - 1)]

print("Monthly time windows:\n")
for slot in slots:
    print(slot)

for i in range(n_chunks):
    print(i)
    
    
###########################################################################
###########################################################################

evalscript = """
    //VERSION=3

    function setup() {
        return {
            input: [{
                bands: ["B02", "B03", "B04"],
                units: "DN"
            }],
            output: {
                bands: 3,
                sampleType: "INT16"
            }
        };
    }

    function updateOutputMetadata(scenes, inputMetadata, outputMetadata) {
      outputMetadata.userData = { "norm_factor":  inputMetadata.normalizationFactor }
   }

    function evaluatePixel(sample) {
        return [sample.B02, sample.B03, sample.B04];
    }
"""

###########################################################################
###########################################################################
def get_true_color_request(time_interval):
    return SentinelHubRequest(
        evalscript=evalscript,
        input_data=[
            SentinelHubRequest.input_data(
                data_collection=DataCollection.SENTINEL2_L1C,
                time_interval=time_interval,
               
            )
        ],
        responses=[SentinelHubRequest.output_response("default", MimeType.PNG)],
        bbox=betsiboka_bbox,
        size=betsiboka_size,
        config=config,
    )

 ##mosaicking_order=MosaickingOrder.LEAST_CC,  in part input

#########################################################################
#########################################################################

# create a list of requests
list_of_requests = [get_true_color_request(slot) for slot in slots]
list_of_requests = [request.download_list[0] for request in list_of_requests]

# download data with multiple threads
data = SentinelHubDownloadClient(config=config).download(list_of_requests, max_threads=5)


##########################################################################
##########################################################################

# some stuff for pretty plots
ncols = 4
nrows = 3
aspect_ratio = betsiboka_size[0] / betsiboka_size[1]
subplot_kw = {"xticks": [], "yticks": [], "frame_on": False}

fig, axs = plt.subplots(ncols=ncols, nrows=nrows, figsize=(5 * ncols * aspect_ratio, 5 * nrows), subplot_kw=subplot_kw)

for idx, image in enumerate(data):
    ax = axs[idx // ncols][idx % ncols]
    ax.imshow(np.clip(image * 8/ 255, 0, 0.5))
    ax.set_title(f"{slots[idx][0]}  -  {slots[idx][1]}", fontsize=10)

plt.tight_layout()


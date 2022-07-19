# -*- coding: utf-8 -*-
"""
Created on Tue Jun 28 14:32:57 2022

@author: r.gachlou
"""
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
#############################################
request_multitype = SentinelHubRequest(
    evalscript=evalscript,
    input_data=[
        SentinelHubRequest.input_data(
            data_collection=DataCollection.SENTINEL2_L1C,
            time_interval=("2020-06-01", "2020-06-30"),
            mosaicking_order=MosaickingOrder.LEAST_CC,
        )
    ],
    responses=[
        SentinelHubRequest.output_response("default", MimeType.TIFF),
        SentinelHubRequest.output_response("userdata", MimeType.JSON),
    ],
    bbox=betsiboka_bbox,
    size=betsiboka_size,
    config=config,
)

############################################### print out information  ##########################################################
multi_data = request_multitype.get_data()[0]
multi_data.keys()


# normalize image
img = multi_data["default.tif"]
norm_factor = multi_data["userdata.json"]["norm_factor"]

img_float32 = img * norm_factor


plot_image(img_float32)


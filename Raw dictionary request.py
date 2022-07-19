# -*- coding: utf-8 -*-
"""
Created on Wed Jun 29 09:47:19 2022

@author: r.gachlou
"""

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
import rasterio
#############

from sentinelhub import SHConfig
import logging
from http.client import HTTPConnection
#for import data
import os
import datetime
import numpy as np
import matplotlib.pyplot as plt
from sentinelhub import (MimeType,CRS,BBox,SentinelHubRequest,SentinelHubDownloadClient,DataCollection,
                         bbox_to_dimensions,DownloadRequest,MosaickingOrder)


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




#betsiboka_coords_wgs84 = [51.141357,35.456726,53.508911,37.191009]
betsiboka_coords_wgs84 = [51.141356,35.456724,51.141458,35.456825]
resolution =1
betsiboka_bbox = BBox(bbox=betsiboka_coords_wgs84, crs=CRS.WGS84)
betsiboka_size = bbox_to_dimensions(betsiboka_bbox, resolution=resolution)

print(f"Image shape at {resolution} m resolution: {betsiboka_size} pixels")


################################################################
################################################################
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

 
    function evaluatePixel(sample) {
        return [sample.B02, sample.B03, sample.B04];
    }
"""
##############################################################################
request_raw_dict = {
    "input": {
        "bounds": {"properties": {"crs": betsiboka_bbox.crs.opengis_string}, "bbox": list(betsiboka_bbox)},
        "data": [
            {
                "type": "S2L1C",
                "dataFilter": {
                    "timeRange": {"from": "2020-06-01T00:00:00Z", "to": "2022-06-30T00:00:00Z"},
                    "mosaickingOrder": "leastCC",
                },
            }
        ],
    },
    "output": {
        "width": betsiboka_size[0],
        "height": betsiboka_size[1],
        "responses": [{"identifier": "default", "format": {"type": MimeType.TIFF.get_string()}}],
    },
    "evalscript": evalscript,
}


################################################################
################################################################

# create request
download_request = DownloadRequest(
    request_type="POST",
    url="https://services.sentinel-hub.com/api/v1/process",
    post_values=request_raw_dict,
    data_type=MimeType.TIFF,
    headers={"content-type": "application/json"},
    use_session=True,
)

# execute request
client = SentinelHubDownloadClient(config=config)
img = client.download(download_request)
################################################################

plot_image(img[:,:,[0,1,2]],factor=1/ 1e4)
img2=img*255/ 1e4
plt.imshow(img[:,:,[0]])




# Alexander Hess
# CS370

# PackageTrack

# APIS
# USPS
import fedex.base_service
from usps import USPSApi

# UPS imports
import xml.etree.ElementTree as ET
import requests as req
import sys

# FedEx
from fedex.config import FedexConfig
from fedex.services.track_service import FedexTrackRequest
from fedex.tools.conversion import sobject_to_dict


########
# USPS #
########
class USPS:
    usps = USPSApi('013HESSI6341')

    def __init__(self):
        tracking = None

    def track_package(self):
        response = self.usps.track(self.tracking)

        return response.result


#######
# UPS #
#######
class UPS:
    def __init__(self, track_num):
        # Create AccessRequest XML
        _AccessLicenseNumber = '7D99F9CCA800B796'
        _userId = 'Kuroteren'
        _password = 'Terenhst1!1!'

        # UPS Provided Code

        self.AccessLicenseNumber = bytes(_AccessLicenseNumber, 'utf-8').decode('utf-8', 'ignore')
        self.userId = bytes(_userId, 'utf-8').decode('utf-8', 'ignore')
        self.password = bytes(_password, 'utf-8').decode('utf-8', 'ignore')
        self.AccessRequest = ET.Element('AccessRequest')
        ET.SubElement(self.AccessRequest, 'AccessLicenseNumber').text = _AccessLicenseNumber
        ET.SubElement(self.AccessRequest, 'UserId').text = _userId
        ET.SubElement(self.AccessRequest, 'Password').text = _password

        self.TrackToolsRequest = ET.Element('TrackRequest')
        self.Request = ET.SubElement(self.TrackToolsRequest, 'Request')
        self.TransactionReference = ET.SubElement(self.Request, 'TransactionReference')
        ET.SubElement(self.TransactionReference, 'CustomerContext').text = 'Customer context'
        ET.SubElement(self.TransactionReference, 'XpciVersion').text = '1.0'
        ET.SubElement(self.Request, 'RequestAction').text = 'Track'
        ET.SubElement(self.Request, 'RequestOption').text = 'none'
        ET.SubElement(self.TrackToolsRequest, 'TrackingNumber').text = track_num

        _reqString = ET.tostring(self.AccessRequest)

        self.tree = ET.ElementTree(ET.fromstring(_reqString))
        self.root = self.tree.getroot()

        _QuantunmRequest = ET.tostring(self.TrackToolsRequest)
        self.quantunmTree = ET.ElementTree(ET.fromstring(_QuantunmRequest))
        self.quantRoot = self.quantunmTree.getroot()

    def track(self):
        _XmlRequest = ET.tostring(self.root, encoding='utf8', method='xml') + ET.tostring(self.quantRoot,
                                                                                          encoding='utf8',
                                                                                          method='xml')
        _XmlRequest = _XmlRequest.decode().replace('\n', '')
        _host = 'https://onlinetools.ups.com/ups.app/xml/Track'
        res = req.post(_host, _XmlRequest, verify=False)

        # Make an element tree from the response
        activity = ET.fromstring(res.content)

        # Pull out the delivery status description from the depth of the xml tree
        status = activity[1][9][3][1][0][1].text

        # return status
        return status


#########
# Fedex #
#########
class FedEx:
    def __init__(self, track_num):
        self.config = FedexConfig(key="9O8UDTCTJF8nXS5C",
                                  password="Hj6AQd4SZJyGR5tVyVyFnX3A6",
                                  account_number="510088000",
                                  meter_number="119217841",
                                  use_test_server=True)
        self.tracking = track_num

    def track(self):
        track = FedexTrackRequest(self.config)
        track.SelectionDetails.PackageIdentifier.Type = 'TRACKING_NUMBER_OR_DOORTAG'
        track.SelectionDetails.PackageIdentifier.Value = self.tracking

        try:
            track.send_request()
        except fedex.base_service.FedexError as e:
            print(e.error_code)
            print(e.value)

        response_dict = sobject_to_dict(track.response)

        return response_dict['CompletedTrackDetails'][0]['TrackDetails'][0]['Events'][0]['EventDescription']


###########################
# Delivered Package Class #
###########################
class DeliveredPackages:
    def __init__(self):
        self.packages = []

    def add(self, package):
        self.packages.append(package)

    def clear(self):
        self.packages.clear()

    def delivered(self):
        return self.packages

    def length(self):
        return len(self.packages)
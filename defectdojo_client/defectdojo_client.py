#!/usr/bin/env python

"""
Descripton : A python client for DefectDojo to upload Scan Result 

"""
# from defectdojo_api import defectdojo
import defectdojo_apiv2 as defectdojo
from datetime import datetime, timedelta
import os, sys
import argparse
import time

def dojo_connection(host, api_key, user, proxy):
    #Optionally, specify a proxy
    proxies = None
    if proxy:
        proxies = {
          'http': proxy,
          'https': proxy,
        }

    # Instantiate the DefectDojo api wrapper
    dd = defectdojo.DefectDojoAPIv2(host, api_key, user, proxies=proxies, verify_ssl=False, timeout=360, debug=False)

    return dd


def return_engagement(dd, product_id, user, build_id=None):
    product_id = product_id
    engagement_id = None
    start_date = datetime.now()
    end_date = start_date+timedelta(days=1)
    users = dd.list_users(user)
    user_id = "admin"

    dojoTime = start_date.strftime("%H:%M:%S")
    engagementText = "CI/CD Integration (" + dojoTime + ")"
    if build_id is not None:
        engagementText = engagementText + " - Build #" + build_id + "(" + start_date.strftime("%H:%M:%S") + ")"

    engagement_id = dd.create_engagement(engagementText, product_id, str(user_id),
    "In Progress", start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
    return engagement_id



def upload_result(dd, engagement_id, file, scannerName):
    print("Uploading Scan Result : "  + file)
    date = datetime.now()
    dojoDate = date.strftime("%Y-%m-%d")
    response = dd.upload_scan(engagement_id, scannerName, file, active="true", verified="true",close_old_findings="true", skip_duplicates="true",scan_date=dojoDate)

    if response == None:
        print ("Upload failed: Please check if the file exists:")
    elif response.success == False:
        print ("Upload failed: Detailed error message: " + response.data)

    return response


class Main:
    if __name__ == "__main__":
        parser = argparse.ArgumentParser(description='CI/CD integration for DefectDojo')
        parser.add_argument('--host', help="DefectDojo Hostname", required=True)
        parser.add_argument('--proxy', help="Proxy ex:localhost:8080", required=False, default=None)
        parser.add_argument('--api_key', help="API Key", required=True)
        parser.add_argument('--build_id', help="Reference to external build id", required=False)
        parser.add_argument('--user', help="User", required=True)
        parser.add_argument('--product', help="DefectDojo Product ID", required=True)
        parser.add_argument('--file', help="Scanner file", required=False)
        parser.add_argument('--dir', help="Scanner directory, needs to have the scanner name with the scan file in the folder. Ex: reports/nmap/nmap.csv", required=False)
        parser.add_argument('--scanner', help="Type of scanner", required=False)
        parser.add_argument('--build', help="Build ID", required=False)
        parser.add_argument('--engagement', help="Engagement ID (optional)", required=False)
        parser.add_argument('--critical', help="Maximum new critical vulns to pass the build.", required=False)
        parser.add_argument('--high', help="Maximum new high vulns to pass the build.", required=False)
        parser.add_argument('--medium', help="Maximum new medium vulns to pass the build.", required=False)

        parser.add_argument('--build_url', help="Build URL", required=False)
        parser.add_argument('--source_code_management_uri', help="source_code_management_uri", required=False)
        parser.add_argument('--version', help="Reference to the version being scanned", required=False)
        parser.add_argument('--commit_hash', help="Reference to commit hash being scanned", required=False)


        parser.add_argument('--active', help="Should uploaded findings be marked as active?", required=False, default=False)
        parser.add_argument('--verified', help="Should uploaded findings be marked as verified?", required=False, default=False)
        parser.add_argument('--close_old_findings', help="Should findings not present in this uplaod be closed?", required=False, default=False)
        parser.add_argument('--skip_duplicates', help="Should findings already present in DefectDojo be skipped?", required=False, default=False)

        parser.add_argument('--auto_group_by', help="Should new findings automatically be group on this field?", required=False)

        parser.add_argument('--debug', help="Do we want debug logging?", required=False, default=False)


        #Parse out arguments
        args = vars(parser.parse_args())
        host = args["host"]
        api_key = args["api_key"]
        user = args["user"]
        product_id = args["product"]
        file = args["file"]
        dir = args["dir"]
        scannerName = args["scanner"]
        engagement_id = args["engagement"]
        max_critical = args["critical"]
        max_high = args["high"]
        max_medium = args["medium"]
        build = args["build"]
        proxy = args["proxy"]
        build_id = args["build_id"]

        version = args["version"]
        build_url = args["build_url"]
        commit_hash = args["commit_hash"]
        source_code_management_uri = args["source_code_management_uri"]


        active = args["active"]
        verified = args["verified"]
        close_old_findings = args["close_old_findings"]
        skip_duplicates = args["skip_duplicates"]
        auto_group_by = args["auto_group_by"]


        dd = dojo_connection(host, api_key, user, proxy=proxy)
        engagement_id = return_engagement(dd, product_id, user, build_id=build_id)
        response = upload_result(dd, engagement_id, file, scannerName=scannerName)
        #Close the engagement_id
        dd.close_engagement(engagement_id)

 
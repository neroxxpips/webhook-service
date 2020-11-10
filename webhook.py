#!/usr/bin/python3

import json  
import os   
from flask import Flask, request  
import requests  
from decouple import config
import time

'''
This script automates the protection of the main branch of a new repository created for an organization
and creates an issue to notify user of the action

'''


application = Flask(__name__)

# supply credential fron .env config file
username = config('USERNAME')
password = config('USER_PASSWORD')

@application.route("/", methods=["POST"])
def branch_protector():
    # get payload from github webhook
    payload = request.get_json()
    # new repository protection dump
    protection_data = {
            "required_status_checks": {"strict": True, "contexts": ["default"]},
            "enforce_admins": False,
            "required_pull_request_reviews": None,
            "restrictions": None,
        }
     # issue creation template   
    issue_data = {
                        "title": "Added Protection to Main Branch",
                        "body": "@"
                        + username
                        + " Main branch is now protected.",
                    }
     
   
    if payload["action"] == "created":
        time.sleep(2)
        # apply protection to newly created repository.
        session = requests.session()
        session.auth = (username, password)
        protect_response = session.put(
            payload["repository"]["url"] + "/branches/main/protection",
            json.dumps(protection_data),
        )
        
        if protect_response.status_code == 200:
            print(
                "Branch Protection: SUCCESSFUL. Status code: ",
                protect_response.status_code,
            )
            print(payload["repository"]["full_name"], "is now protected!!!")

            # issue creation for newly created repository to notify user.
            
            if payload["repository"]["has_issues"]:
                
                session = requests.session()
                session.auth = (username, password)
                issue_response = session.post(
                    payload["repository"]["url"] + "/issues", json.dumps(issue_data)
                )
                if issue_response.status_code == 201:
                    print(
                        "Issue Creation: SUCCESSFUL. Status code: ",
                        issue_response.status_code,
                    )
                else:
                    print(
                        "Issue Creation: UNSUCCESSFUL. Status code: ",
                        issue_response.status_code,
                    )
            else:
                print(
                    "No Issue Available at this time!!!"
                )
        else:
            print(protect_response.content)
            print(
                "Branch Protection: UNSUCCESSFUL. Status code: ",
                protect_response.status_code,
            )
    

    return "OK"


if __name__ == "__main__":
    application.run()

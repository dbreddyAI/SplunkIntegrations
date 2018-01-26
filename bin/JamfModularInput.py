##
# Copyright 2018 Jamf
##
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
##
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
##

# JamfModularInput
# splunkmodularinput
#
# Created by Aryik Bhattacharya on 6/19/17
#
# Modular input app to allow Jamf Pro to interface with Splunk
# Logs detailed information about the computers enrolled in Jamf Pro.
# To retrieve different data, modify the jss_url and the handling of the
# response in stream_data.

import sys
import json
import splunklib.modularinput as splunk
import requests


class JamfModularInput(splunk.Script):

    # return a splunklib.modularinput.Scheme object configured as needed
    def get_scheme(self):
        scheme = splunk.Scheme("Jamf Modular Input")
        scheme.description = "Retrieves computer data from Jamf Pro."
        scheme.use_external_validation = True

        username_argument = splunk.Argument("jss_username")
        username_argument.data_type = splunk.Argument.data_type_string
        username_argument.description = "Jamf Pro Username"
        username_argument.required_on_create = True
        scheme.add_argument(username_argument)

        password_argument = splunk.Argument("jss_password")
        password_argument.data_type = splunk.Argument.data_type_string
        password_argument.description = "Jamf Pro Password"
        password_argument.required_on_create = True
        scheme.add_argument(password_argument)

        api_argument = splunk.Argument("api_call")
        api_argument.data_type = splunk.Argument.data_type_string
        api_argument.description = "Type of Advanced Search to call"
        api_argument.required_on_create = True
        scheme.add_argument(api_argument)

        search_name_argument = splunk.Argument("search_name")
        search_name_argument.data_type = splunk.Argument.data_type_string
        search_name_argument.description = "Preconfigured Advanced Search to call"
        search_name_argument.required_on_create = True
        scheme.add_argument(search_name_argument)

        url_argument = splunk.Argument("jss_url")
        url_argument.data_type = splunk.Argument.data_type_string
        url_argument.description = "Jamf Pro URL"
        url_argument.required_on_create = True
        scheme.add_argument(url_argument)

        index_argument = splunk.Argument("index")
        index_argument.data_type = splunk.Argument.data_type_string
        index_argument.description = "Destination index"

        host_argument = splunk.Argument("host")
        host_argument.data_type = splunk.Argument.data_type_string
        host_argument.description = "Host"

        return scheme

    # Make sure the credentials are good
    def validate_input(self, validation_definition):
        username = str(validation_definition.parameters["jss_username"])
        password = str(validation_definition.parameters["jss_password"])
        url = str(validation_definition.parameters["jss_url"])
        api_call = str(validation_definition.parameters["api_call"])

        if api_call != "computer" and api_call != "mobile_device":
            raise ValueError("%s is not a valid option for the api_call param"
                             % api_call)
        jss_url = url + "/JSSResource/activationcode"
        r = requests.get(jss_url,
                         auth=(username, password),
                         headers={'accept': 'application/json'})
        # raise an exception if the response's status code is not 200
        r.raise_for_status()

    # Make the API call and return the data as a string.
    def stream_events(self, inputs, ew):
        for input_name, input_item in inputs.inputs.iteritems():
            # Get fields from the InputDefinition object
            username = input_item["jss_username"]
            password = input_item["jss_password"]
            url = input_item["jss_url"]
            api_call = input_item["api_call"]
            search_name = input_item["search_name"]

            # Host and index should always be included in the stanza by splunk
            index = input_item["index"]
            host = input_item["host"]

            if api_call == "computer":
                jss_url = "%s/JSSResource/advancedcomputersearches/name/%s" % (
                    url, search_name)
            elif api_call == "mobile_device":
                jss_url = "%s/JSSResource/advancedmobiledevicesearches/name/%s" % (
                    url, search_name)
            else:
                splunk.EventWriter.log(ew, splunk.EventWriter.ERROR,
                                       "api_call: %s not specified correctly" % api_call)
                return

            # Log that we are beginning to retrieve data.
            splunk.EventWriter.log(ew, splunk.EventWriter.INFO,
                                   "Started retrieving data for user %s" % username)
            response = requests.get(jss_url, auth=(username, password),
                                    headers={'accept': 'application/json'})
            response.raise_for_status()
            jsondata = response.json()

            if api_call == "computer":
                computers = jsondata["advanced_computer_search"]["computers"]

                for computer in computers:
                    event = splunk.Event(
                        data=json.dumps(computer),
                        stanza=computer["Computer_Name"],
                        index=index,
                        host=host
                    )
                    # Tell the EventWriter to write this event
                    ew.write_event(event)
            elif api_call == "mobile_device":
                mobile_devices = \
                    jsondata["advanced_mobile_device_search"]["mobile_devices"]
                for mobile_device in mobile_devices:
                    event = splunk.Event(
                        data=json.dumps(mobile_device),
                        stanza=mobile_device["name"],
                        index=index,
                        host=host
                    )
                    ew.write_event(event)


# Script must implement the following args: scheme, validate-arguments
if __name__ == '__main__':
    sys.exit(JamfModularInput().run(sys.argv))

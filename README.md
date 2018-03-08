# Splunk Integration

This is a simple Splunk app based on a modular input script that makes API calls to the Jamf Pro Server. 

Currently, you have the option of using a computer advanced search or a mobile device advanced search of your choosing. Note that when you enter the advanced search name, it is case sensitive and must exactly match the name in Jamf Pro.

## UI Demo

The ui-demo tag shows how to create a UI for the modular input. Specifically, look at the files in the default/data and default/metadata directories, as well as the [ui] section in app.conf.

## Splunk Modular Inputs

Modular inputs allows adding more interactive inputs for Splunk Enterprise.

  + [Splunk Modular Inputs](https://docs.splunk.com/Documentation/Splunk/6.6.3/AdvancedDev/ModInputsScripts)


## Developing on Splunk Modular Input

To develop on the splunk modular input, you can just clone this repository into $SPLUNK_HOME/etc/apps.
```bash
> cd $SPLUNK_HOME/etc/apps
> git clone https://github.com/jamf/SplunkIntegrations.git JamfModularInput
```
After cloning the repositroy, restart your Splunk server and then go to settings > data inputs to add the data from Jamf Pro to Splunk.

We welcome pull requests and forks for new features or bug fixes.


### Connecting to JamfPro via Direct Database Access

This document contains instructions to connect to a JamfPro database directly for use with Splunk.  Great care and consideration should be taken before doing this as allowing access to the JamfPro database can be a security risk.

  + [direct db connection](https://github.com/jamf/SplunkModularInput/tree/master/misc/Splunk_MySQL_JamfPro.pdf)



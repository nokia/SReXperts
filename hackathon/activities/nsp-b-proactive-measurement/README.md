# Proactive Delay Measurment using NSP

| Item | Details |
| --- | --- |
| Short Description | TWAMP/light using intents and OAM manager |
| Skill Level | Beginner |
| Tools Used | NSP IM and OAM manager, vsCode |

## Prerequisites
Basic knowledge the NSP UI

## Objectives

This activity is about getting a familar with Intent Manager (NSP Network Intents), OAM Manager (NSP OAM Tests).
For improved DevOps experience, consider using the IM vsCode extension from [marketplace](https://marketplace.visualstudio.com/items?itemName=Nokia.nokia-intent-manager).

The purpose of this activity is to create a TWAMP light session between two nodes using IM and to check the results in the NSP WebUI.

A ready-to-use intent-type will be provided, that contains YANG files, script and resource files to create a TWAMP light session between two nodes.

In a second step, you will do little changes to the intent-type definition.

### Goals to achieve

Gather practical experience using
* Intent Manager
* OAM Manager
* vsCode extension for NSP IM

## Access to the Lab
Access details to NSP will be provided in the hackathon. There is no requirement to access the NEs directly.

## Steps

#### Discovery of the lab

If this is your first NSP activity for this hackathon, ensure to first execute the activity called `nsp-b-lab-discovery`. It should not take long!

#### Check the pre-built intent-type
An intent-type called `oamtest` (version 1) should be installed on the shared NSP system.
Open the `Network Intents` in the NSP WebUI, to list all the intent-types installed in the system.
You may click on `EDIT` to review the anatomy of an intent-type.

Once done, press `CANCEL` to avoid saving any changes!
**Remind, this is a shared system! Saving changes to the pre-built intent-type impacts other groups executing the same use-case!**

#### Explore the life-cycle of an OAM intent
Create an intent between two 7750SR nodes in your system: p1, p2, pe1, pe2, pe3, or pe4.
The `Test Id` is the intent target, which used as identifier in NSP and must be unique.
To avoid conflict with other groups, use your group number plus two digits for the tests you create.

Examples:
* Group 5: Test Id range from 500 to 599
* Group 23: Test Id range from 2300 to 2399

Before you press the `CREATE` button, you may want to login to one of your nodes via CLI and enter the following commands:
```
# edit-config private
# /configure router twamp-light
# info
# /configure test-oam
# info
```
**Keep the CLI session open!**

After the intent has been created, enter the following CLI commands (same session):
```
# /configure
# compare candidate running
# /update /configure
```

At the beginning you see the `!` indicator, that a change was applied.
The compare command lists the OAM related configuration that was added.

Apply a configuration change to your network element.
Run audit to check for misalignments and review the changes.
Run synchronize to reconcile the intent, reverting back the changes made via CLI.

Apply changes to the intent by modifying one of the endpoints.
Check the function of audit and synchronize, doing those changes.

Change the desired `Network State` from `Active` to `Not Present`.
Synchronize the intent and check the device configuration (using CLI or MDC).
Change the desired `Network State` back to `Active` and validate configuration again.

#### Explore OAM Manager
Open `OAM Tests` in the NSP WebUI and filter for test type `Twamp-light`.
All tests are automatically discovered from the network element.
Discovery of tests might take a while, so don't worry if you don't see a test just after creation.

Double-click on one of your tests, to review the test results.
Both test-streaming and accounting should work.
Accounting file retrieval is dependend on SFTP.
Collection interval and file interval are both configured for 5min intervals, so data will be available with some delay.

#### Modify the intent-type (intermediate)
For this part of the exercise, download Visual Studio Code and the latest vsCode extension for NSP IM.
Under vsCode settings provide your credentials (NSP IP, username, password, port: 443).

Select `Create intent-type` in the context menu of `Intent Manager`.
Use `oamtest-groupXX` as intent-type name, while XX is your group number!
Select `latencySRX24` as template.

*Note: Alternatively you can `clone` the existing `oamtest` intent-type using the NSP WebUI.
In this case you need to modify the YANG module, script, and viewConfig to reflect the new intent-type name.*

Create an intent and check the corresponding device configuration.
Under `TWAMP Session` make a small change like changing the interval from 100 to 1000.
Audit and synchronize the intent. Check the device configuration again.

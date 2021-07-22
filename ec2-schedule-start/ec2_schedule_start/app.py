import json
import boto3
import logging, sys


def lambda_handler(event, context):
    logging.basicConfig(stream=sys.stderr, level=logging.warning)
    logging.warning("Starting ec2-schedule-start lamba handler")

    ec2Client = boto3.client("ec2")

    matchedInstances = []
    instDict = ec2Client.describe_instances()
    logging.warning("Ran describe instances")
    try:
        logging.warning("Found {len} reservations".format(len=len(instDict)))
        for r in instDict["Reservations"]:
            logging.warning("Found {len} instances".format(len=len(r)))
            for i in r["Instances"]:
                jripperConditionMet = False
                poweronConditionMet = False
                for t in i["Tags"]:
                    if (
                        str(t["Key"]).upper() == "PROJECT"
                        and str(t["Value"]).upper() == "JRIPPER"
                    ):
                        jripperConditionMet = True
                        logging.warning(
                            "%s: Instance is part of JRipper project, met jripper condition",
                            i["InstanceId"],
                        )
                    if (
                        str(t["Key"]).upper() == "AUTOPOWERON"
                        and str(t["Value"]).upper() == "TRUE"
                    ):
                        poweronConditionMet = True
                        logging.warning(
                            "%s: Instance is tagged with AUTOPOWERON, met power on condition",
                            i["InstanceId"],
                        )

                if jripperConditionMet and poweronConditionMet:
                    matchedInstances.append(i["InstanceId"])
                    logging.warning(
                        "%s: Instance met both AUTOPOWERON and PROJECT conditions",
                        i["InstanceId"],
                    )
                else:
                    logging.warning(
                        "%s: Instance did not meet AUTOPOWERON and/or PROJECT conditions, skipping",
                        i["InstanceId"],
                    )

    except Exception as e:
        logging.error(
            "Did not find Reservations or Instances key in Dictionary.  Terminating."
        )
        logging.error(str(e))
        return False

    logging.warning("Finished iterating ec2 instances, now beginning invoke")
    try:
        ec2Client.start_instances(InstanceIds=matchedInstances)
        logging.warning(
            "Successfully issued power on command to systems: {hosts}".format(
                hosts=str(matchedInstances)
            )
        )
    except Exception as e:
        logging.error("Failed to start instances.  Terminating.")
        logging.error(str(e))
        return False


if __name__ == "__main__":
    lambda_handler("", "")

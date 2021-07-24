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
        logging.warning(f"Found {len(instDict)} reservations")
        for r in instDict["Reservations"]:
            logging.warning(f"Found {len(r)} instances")
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
                            f"{i['InstanceId']}: Instance is part of JRipper project, met jripper condition"
                        )
                    if (
                        str(t["Key"]).upper() == "AUTOPOWERON"
                        and str(t["Value"]).upper() == "TRUE"
                    ):
                        poweronConditionMet = True
                        logging.warning(
                            f"{i['InstanceId']}: Instance is tagged with AUTOPOWERON, met power on condition"
                        )

                if jripperConditionMet and poweronConditionMet:
                    matchedInstances.append(i["InstanceId"])
                    logging.warning(
                        f"{i['InstanceId'],}: Instance met both AUTOPOWERON and PROJECT conditions"
                    )
                else:
                    logging.warning(
                        f"{i['InstanceId']}: Instance did not meet AUTOPOWERON and/or PROJECT conditions, skipping"
                    )

    except Exception as e:
        logging.error(
            "Did not find Reservations or Instances key in Dictionary.  Terminating."
        )
        logging.error(str(e))
        raise

    logging.warning("Finished iterating ec2 instances, now beginning invoke")
    try:
        ec2Client.start_instances(InstanceIds=matchedInstances)
        logging.warning(
            f"Successfully issued power on command to systems: {str(matchedInstances)}"
        )
        return {"statusCode": 200, "body": json.dumps("Success")}
    except Exception as e:
        logging.error("Failed to start instances.  Terminating.")
        logging.error(str(e))
        return False


if __name__ == "__main__":
    lambda_handler("", "")

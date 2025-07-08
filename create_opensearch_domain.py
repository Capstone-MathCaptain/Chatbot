import boto3
import json
import os
from dotenv import load_dotenv
load_dotenv(dotenv_path=".env")
boto3.setup_default_session(
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_DEFAULT_REGION", "us-east-1")
)

# OpenSearch 클라이언트 생성 (리전 확인 필수!)
client = boto3.client("opensearch", region_name="us-east-1")

# 도메인 이름
domain_name = "mydomain-finegrained"

# 마스터 사용자 자격 증명 설정 (fine-grained access control용)
master_user_name = os.getenv("OS_MASTER_USER")
master_user_password = os.getenv("OS_MASTER_PASSWORD")

# VPC 설정 정보
vpc_config = {
    "SubnetIds": [
        "subnet-0bf0f220ebc8165a7"
    ],
    "SecurityGroupIds": [
        "sg-0225afb45fd02af83"
    ]
}

# 도메인 생성 요청
response = client.create_domain(
    DomainName=domain_name,
    EngineVersion="OpenSearch_2.17",
    ClusterConfig={
        "InstanceType": "r6g.large.search",
        "InstanceCount": 2,
        "DedicatedMasterEnabled": False,
        "ZoneAwarenessEnabled": False
    },
    EBSOptions={
        "EBSEnabled": True,
        "VolumeSize": 10,
        "VolumeType": "gp3"
    },
    AccessPolicies=json.dumps({
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "AWS": "*"
                },
                "Action": "es:*",
                "Resource": f"arn:aws:es:us-east-1:160885280013:domain/{domain_name}/*"
            }
        ]
    }),
    VPCOptions=vpc_config,
    CognitoOptions={"Enabled": False},
    EncryptionAtRestOptions={"Enabled": True},
    NodeToNodeEncryptionOptions={"Enabled": True},
    DomainEndpointOptions={
        "EnforceHTTPS": True,
        "TLSSecurityPolicy": "Policy-Min-TLS-1-2-2019-07"
    },
    AdvancedSecurityOptions={
        "Enabled": True,
        "InternalUserDatabaseEnabled": True,
        "MasterUserOptions": {
            "MasterUserName": master_user_name,
            "MasterUserPassword": master_user_password
        }
    }
)

print("도메인 생성 요청이 완료되었습니다.")
print(response)
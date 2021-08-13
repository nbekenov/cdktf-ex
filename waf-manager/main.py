#!/usr/bin/env python
"""
AWS Firewall Manager CDK-TF module
"""
import os
import sys
import json
from constructs import Construct
from cdktf import App, TerraformStack
from imports.aws import (
    AwsProvider, FmsPolicy,
    FmsAdminAccount,
    FmsPolicySecurityServicePolicyData
)

class FirewallManager(TerraformStack):
    """
    AWS Firewall Manager class
    available public methods:
        * set_admin_account
        * create_global_policy
        * create_region_policy
    """
    def __init__(self, scope: Construct, ns: str, profile_name, partition):
        super().__init__(scope, ns)

        self.profile_name = profile_name if profile_name else "default"
        region = "us-gov-west-1" if "gov" in partition else "us-east-1"
        AwsProvider(self, f"aws-{region}", region=region, profile=profile_name)

    def set_admin_account(self):
        """
        Associates an AWS Firewall Manager administrator account.
        This operation must be performed in the us-east-1 or us-gov-west-1 region.
        """
        FmsAdminAccount(self, "fms-admin")

    def create_global_policy(self, policy_name, rules_file, remediate: bool):
        """
        Create AWS Firewall Manager policy
        global scope -> CloudFront
        remediate - if set True then auto remediate any noncompliant resources
        """
        rules = self.__parse_rule(rules_file)

        global_policy = FmsPolicy(self,f"fms-globalpolicy-{policy_name}",
            name=policy_name,
            exclude_resource_tags=False,
            resource_type = "AWS::CloudFront::Distribution",
            security_service_policy_data = [
                FmsPolicySecurityServicePolicyData(
                    type="WAFV2",
                    managed_service_data = json.dumps(rules)
                )
            ],
            remediation_enabled=remediate,
        )
        global_policy.override_logical_id(f"fms-globalpolicy-{policy_name}")

    def create_region_policy(self, policy_name, rules_file, region, remediate: bool):
        """
        Create AWS Firewall Manager policy
        region scope -> ALB, ApiGateway
        remediate - if set True then auto remediate any noncompliant resources
        """
        aws = AwsProvider(self, f"aws-fms-{region}",
            region=region,
            profile=self.profile_name,
            alias = f"aws-{region}"
        )
        rules = self.__parse_rule(rules_file)

        region_policy = FmsPolicy(self,f"fms-regionpolicy-{policy_name}",
            name=policy_name,
            exclude_resource_tags=False,
            resource_type_list = [
                "AWS::ElasticLoadBalancingV2::LoadBalancer",
                "AWS::ApiGateway::Stage"
            ],
            security_service_policy_data = [
                FmsPolicySecurityServicePolicyData(
                    type="WAFV2",
                    managed_service_data = json.dumps(rules)
                )
            ],
            remediation_enabled=remediate,
            provider = aws
        )
        region_policy.override_logical_id(f"fms-regionpolicy-{policy_name}")

    @staticmethod
    def __parse_rule(file_name):
        """
        Private helper method to parse and validate json file with rules definitions
        """
        project_dir = os.path.dirname(os.path.realpath(__file__))
        rule_data = {}
        try:
            with open(f"{project_dir}/{file_name}") as rules_rile:
                rule_data = json.load(rules_rile)
            rules_num = len(rule_data["preProcessRuleGroups"])
            print(f"LOG: number of preProcessRuleGroups {rules_num}")
        except FileNotFoundError as fnf_err:
            sys.exit(f"{fnf_err}: rule file not found")

        return rule_data


def main():
    """
    Example: Create FMS policies for global and region scope
        aws_account_profile_name - your profile name, if epmty then profile "default" will be used
        partition - "aws" or "aws-us-gov"
    """
    # const
    aws_account_profile_name = ""
    partition="aws"

    app = App(stack_traces=False)
    waf_manager = FirewallManager(app,
        "waf-manager",
        profile_name=aws_account_profile_name,
        partition=partition
    )
    # waf_manager.set_admin_account()
    waf_manager.create_global_policy(policy_name="FMS-Test-global",
        rules_file="AWSCommonRuleSet.json",
        remediate=True
    )

    waf_manager.create_region_policy(policy_name="FMS-Test-regional",
        rules_file="AWSCommonRuleSet.json",
        region="us-east-1",
        remediate=True
    )
    app.synth()


if __name__ == "__main__":
    main()

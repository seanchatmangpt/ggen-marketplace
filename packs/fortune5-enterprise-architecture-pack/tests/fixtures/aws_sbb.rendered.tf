# GENERATED from templates/aws-sbb.tf.tera (rendered: sbbSlug=finance-sbb,
# sbbDomain=finance, region=us-east-1, air-gap parity mirrored via interface
# VPC endpoints). Fixture for tests/test_resource_graph.py.

terraform {
  required_version = ">= 1.7.1"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.40"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

locals {
  tags = merge(
    {
      workload          = "finance-sbb"
      domain            = "finance"
      sbb-exact-subject = "https://example.ea/finance-sbb@01HZZZZZZZZZZZZZZZZZZZZZZZ"
      managed-by        = "terraform"
    },
    var.tags,
  )
}

resource "aws_ssoadmin_permission_set" "sbb" {
  name             = "finance-sbb-permission-set"
  instance_arn     = var.sso_instance_arn
  session_duration = "PT1H"
  tags             = local.tags
}

resource "aws_ssoadmin_managed_policy_attachment" "sbb" {
  instance_arn       = aws_ssoadmin_permission_set.sbb.instance_arn
  permission_set_arn = aws_ssoadmin_permission_set.sbb.arn
  managed_policy_arn = var.sso_managed_policy_arn
}

resource "aws_iam_role_policy_inline" "sbb_identity_center" {
  name = "finance-sbb-identity-center-inline"
  role = var.sbb_role_name
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid      = "IdentityCenterEnumeratedOnly"
      Effect   = "Allow"
      Resource = "*"
      Action   = [
        "sso:ListInstances",
        "sso:DescribeInstance",
        "sso:CreateApplication",
        "sso:DescribeApplication",
        "sso-directory:DescribeDirectory",
        "sso-directory:ListDirectories",
      ]
    }]
  })
}

resource "aws_controltower_landing_zone" "sbb" {
  manifest_json = var.controltower_manifest_json
  tags          = local.tags
}

resource "aws_iam_role_policy_inline" "sbb_control_tower" {
  name = "finance-sbb-control-tower-inline"
  role = var.sbb_role_name
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid      = "ControlTowerEnumeratedOnly"
      Effect   = "Allow"
      Resource = "*"
      Action   = [
        "controltower:GetLandingZone",
        "controltower:ListManagedAccounts",
        "controltower:GetGuardrail",
        "organizations:DescribeOrganization",
        "organizations:ListAccounts",
      ]
    }]
  })
}

resource "aws_ec2_transit_gateway" "sbb" {
  description = "SBB finance / finance-sbb"
  tags        = local.tags
}

resource "aws_ec2_transit_gateway_vpc_attachment" "sbb" {
  subnet_ids         = var.tgw_subnet_ids
  transit_gateway_id = aws_ec2_transit_gateway.sbb.id
  vpc_id             = var.tgw_vpc_id
  tags               = local.tags
}

resource "aws_vpc_endpoint" "sbb" {
  for_each            = var.vpc_endpoint_services
  vpc_id              = var.tgw_vpc_id
  service_name        = each.value
  vpc_endpoint_type   = "Interface"
  subnet_ids          = var.tgw_subnet_ids
  private_dns_enabled = true
  tags                = merge(local.tags, { air-gap-parity = "mirrored" })
}

resource "aws_cloudtrail_event_data_store" "sbb" {
  name                           = "finance-sbb-eds"
  organization_enabled           = false
  retention_period               = 3650
  termination_protection_enabled = true
  tags                           = local.tags
}

resource "aws_iam_role_policy_inline" "sbb_cloudtrail_lake" {
  name = "finance-sbb-cloudtrail-lake-inline"
  role = var.sbb_role_name
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid      = "CloudTrailLakeEnumeratedOnly"
      Effect   = "Allow"
      Resource = "*"
      Action   = [
        "cloudtrail:GetEventDataStore",
        "cloudtrail:ListEventDataStores",
        "cloudtrail:StartQuery",
      ]
    }]
  })
}

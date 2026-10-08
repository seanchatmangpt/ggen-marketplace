# GENERATED from templates/azure-sbb.tf.tera (rendered: sbbSlug=fin-sbb,
# sbbDomain=finance, region=eastus). Fixture for tests/test_resource_graph.py.

terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.100"
    }
  }
}

provider "azurerm" { features {} }

resource "azurerm_management_group" "root" {
  display_name = "finance-enclave-root"
}

resource "azurerm_management_group" "landing_zone" {
  display_name               = "finance-landing-zone"
  parent_management_group_id = azurerm_management_group.root.id
}

resource "azurerm_management_group" "enclave" {
  display_name               = "finance-enclave"
  parent_management_group_id = azurerm_management_group.landing_zone.id
}

resource "azurerm_resource_group" "connectivity" {
  name     = "rg-fin-sbb-connectivity"
  location = "eastus"
}

resource "azurerm_virtual_wan" "this" {
  name                = "vwan-fin-sbb"
  resource_group_name = azurerm_resource_group.connectivity.name
  location            = "eastus"
}

resource "azurerm_virtual_hub" "hub" {
  name                = "vhub-fin-sbb-eastus"
  resource_group_name = azurerm_resource_group.connectivity.name
  location            = "eastus"
  virtual_wan_id      = azurerm_virtual_wan.this.id
  address_prefix      = var.hub_address_prefix
}

resource "azurerm_virtual_hub_connection" "spoke" {
  for_each                  = toset(var.spoke_vnet_ids)
  name                      = "sconn-${each.value}"
  virtual_hub_id            = azurerm_virtual_hub.hub.id
  remote_virtual_network_id = each.value
}

resource "azurerm_resource_group_policy_assignment" "guest_config" {
  for_each             = { for a in guest_config_assignments : a.assignmentName => a }
  name                 = each.value.assignmentName
  resource_group_id    = azurerm_resource_group.connectivity.id
  policy_definition_id = each.value.initiativeName
}

resource "azurerm_resource_group" "hsm" {
  name     = "rg-fin-sbb-hsm"
  location = "eastus"
}

resource "azurerm_dedicated_hardware_security_module" "this" {
  name                = "hsm-fin-sbb"
  resource_group_name = azurerm_resource_group.hsm.name
  location            = "eastus"
  sku_name            = var.hsm_sku
  subnet_id           = var.hsm_subnet_id
  management_network_profile {
    network_interface_private_ip_addresses = []
  }
  network_profile {
    network_interface_private_ip_addresses = []
    subnet_id                              = var.hsm_subnet_id
  }
}

resource "azurerm_resource_group" "confcomp" {
  name     = "rg-fin-sbb-confcomp"
  location = "eastus"
}

resource "azurerm_subscription_policy_assignment" "confidential_vm" {
  name                 = "confidential-vm-dccv5-only"
  subscription_id      = var.subscription_id
  policy_definition_id = var.confidential_vm_policy_definition_id
  parameters = jsonencode({
    allowedVmSizes = {
      value = ["Standard_DC2ccs_v5", "Standard_DC4ccs_v5"]
    }
  })
}

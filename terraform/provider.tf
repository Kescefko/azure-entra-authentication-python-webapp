terraform {
  required_providers {
    azuread = {
      source  = "hashicorp/azuread"
      version = "~> 2.39.0"
    }
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.98.0"
    }
  }
}

provider "azurerm" {
  features {}
  subscription_id = var.subscription_id
}

provider "azuread" {}
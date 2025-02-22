resource "azuread_application" "app" {
  display_name = "PythonApp"
}

resource "azuread_service_principal" "sp" {
  client_id = azuread_application.app.client_id
}

resource "azuread_service_principal_password" "example" {
  service_principal_id = azuread_service_principal.sp.id
}

resource "azurerm_role_assignment" "rbac" {
  scope                = "/subscriptions/${var.subscription_id}"
  role_definition_name = "Contributor"
  principal_id         = azuread_service_principal.sp.object_id
}

output "app_id" {
  value = azuread_application.app.client_id
}

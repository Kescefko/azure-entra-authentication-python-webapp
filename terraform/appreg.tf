# =============================
# Azure AD Application for Flask App
# =============================
resource "azuread_application" "flask_app" {
  display_name = "FlaskPythonApp"

  web {
    redirect_uris = ["http://localhost:5000/getAToken"]
  }

  api {
    oauth2_permission_scope {
      admin_consent_description = "Allow access to Flask Api"
      admin_consent_display_name = "Access Flask API"
      id = "00000000-0000-0000-0000-000000000001"
      type = "Admin"
      value = "api.access"
    }
  }
}

resource "azuread_service_principal" "flask_sp" {
  application_id = azuread_application.flask_app.application_id
}

resource "azuread_service_principal_password" "flask_sp_secret" {
  service_principal_id = azuread_service_principal.flask_sp.id
}

# Placeholder for RBAC assignment if needed
# resource "azurerm_role_assignment" "flask_rbac" {
#   scope                = "/subscriptions/${var.subscription_id}"
#   role_definition_name = "Contributor"
#   principal_id         = azuread_service_principal.flask_sp.object_id
# }

# Output the Flask Application (Client) ID
output "flask_app_id" {
  value = azuread_application.flask_app.application_id
}

output "flask_app_secret" {
  value = azuread_service_principal_password.flask_sp_secret.value
  sensitive = true
}

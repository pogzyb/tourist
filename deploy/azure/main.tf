locals {
  tags = {
    Project = var.project_name
  }
}

resource "random_string" "unique" {
  length      = 5
  min_numeric = 5
  numeric     = true
  special     = false
  lower       = true
  upper       = false
}

resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.region
}

resource "azurerm_container_registry" "cr" {
  name                = var.container_registry_name
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "Standard"
  admin_enabled       = false
}

resource "null_resource" "docker" {
  provisioner "local-exec" {
    command = <<-EOT
      echo "$ARM_CLIENT_SECRET" | docker login ${azurerm_container_registry.cr.name}.azurecr.io -u "$ARM_CLIENT_ID" --password-stdin
      docker pull ghcr.io/pogzyb/tourist:${var.image_tag}
      docker tag ghcr.io/pogzyb/tourist:${var.image_tag} ${azurerm_container_registry.cr.name}.azurecr.io/tourist:latest
      docker push ${azurerm_container_registry.cr.name}.azurecr.io/tourist:latest
      sleep 10s
    EOT
    when    = create
  }

  depends_on = [azurerm_container_registry.cr]
}

resource "azurerm_storage_account" "sa" {
  name                     = "${var.storage_account_name}${random_string.unique.result}"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_service_plan" "sp" {
  name                = var.service_plan_name
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  os_type             = "Linux"
  sku_name            = "B1"
}

resource "azurerm_log_analytics_workspace" "law" {
  name                = "touristLogAnalyticsWorkspace"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  sku                 = "PerGB2018"
  retention_in_days   = 30
}

resource "azurerm_container_app_environment" "env" {
  name                       = "touristContainerAppEnv"
  location                   = azurerm_resource_group.rg.location
  resource_group_name        = azurerm_resource_group.rg.name
  logs_destination           = "log-analytics"
  log_analytics_workspace_id = azurerm_log_analytics_workspace.law.id

  identity {
    type = "SystemAssigned"
  }
}

resource "azurerm_role_assignment" "acr_pull" {
  scope                            = azurerm_container_registry.cr.id
  role_definition_name             = "AcrPull"
  principal_id                     = azurerm_container_app_environment.env.identity[0].principal_id
  skip_service_principal_aad_check = true
}

resource "azurerm_container_app" "app" {
  container_app_environment_id = azurerm_container_app_environment.env.id
  name                         = "tourist"
  resource_group_name          = azurerm_resource_group.rg.name
  revision_mode                = "Single"
  max_inactive_revisions       = 5
  tags                         = local.tags

  identity {
    type = "SystemAssigned"
  }

  ingress {
    allow_insecure_connections = false
    external_enabled           = true
    target_port                = 8000
    transport                  = "auto"
    traffic_weight {
      latest_revision = true
      percentage      = 100
    }
  }

  registry {
    identity = "system-environment"
    server = azurerm_container_registry.cr.login_server
  }

  template {
    container {
      command = []
      args = [ var.mode ]
      cpu     = 2
      image   = "${azurerm_container_registry.cr.login_server}/tourist:${var.image_tag}"
      memory  = "4Gi"
      name    = "tourist"
      env {
        name  = "X_API_KEY"
        value = var.x_api_key
      }
      env {
        name  = "FUNCTIONS_WORKER_RUNTIME"
        value = "python"
      }
      env {
        name  = "AzureWebJobsStorage"
        value = azurerm_storage_account.sa.primary_connection_string
      }
    }
  }

  depends_on = [null_resource.docker]
}

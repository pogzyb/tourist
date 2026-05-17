output "function_urls" {
  value = azurerm_container_app.app.latest_revision_fqdn
}
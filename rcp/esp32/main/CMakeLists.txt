idf_component_register(
	SRCS "main.cpp"
	INCLUDE_DIRS "."
	PRIV_REQUIRES rcp_core esp_driver_gpio esp_netif esp_wifi esp_event nvs_flash
)


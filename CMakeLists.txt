cmake_minimum_required(VERSION 3.28)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON CACHE BOOL "Export compile_commands.json" FORCE)

option(DSIG_ESP32 "Build the ESP32 firmware with ESP-IDF" OFF)
if (DSIG_ESP32)
    include("${CMAKE_CURRENT_SOURCE_DIR}/rcp/apps/esp32/CMakeLists.txt")
    return() # Uses ESP-IDF to configure
endif ()

project(rcp
	VERSION 0.1.0
	LANGUAGES C CXX
	HOMEPAGE_URL "https://github.com/marcusgigandet/dsig/tree/main"
)

#####################
# Compiler settings #
#####################

set(CMAKE_C_STANDARD 23)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

##################
# Subdirectories #
##################

add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/rcp)

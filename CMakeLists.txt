cmake_minimum_required(VERSION 3.28)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON CACHE BOOL "Export compile_commands.json" FORCE)

option(DSIG_ESP32 "Build the ESP32 firmware with ESP-IDF" OFF)
if (DSIG_ESP32)
    include("${CMAKE_CURRENT_SOURCE_DIR}/rcp/esp32/cmake/project.cmake")
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

#################
# cmake-tooling #
#################

if (EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/vendor/cmake-tooling/CMakeLists.txt)
    add_subdirectory(${CMAKE_CURRENT_SOURCE_DIR}/vendor/cmake-tooling)
else ()
    message(STATUS "cmake-tooling submodule not found, tooling targets are disabled.")
endif ()

add_cmake_format_target(
	TARGET dsig
	FILES ${CMAKE_CURRENT_SOURCE_DIR}/CMakeLists.txt
)
add_cmake_lint_target(
	TARGET dsig
	FILES ${CMAKE_CURRENT_SOURCE_DIR}/CMakeLists.txt
)

##############
# Sanitizers #
##############

option(DSIG_SANITIZERS "Enable ASan/UBSan instrumentation on project targets" OFF)

##################
# Subdirectories #
##################

add_subdirectory(rcp/rcp_core)
add_subdirectory(rcp/raspberry_pi)

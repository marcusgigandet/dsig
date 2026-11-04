########################
# Collect source files #
########################

file(GLOB_RECURSE RCP_COMMON_SOURCES
		${CMAKE_CURRENT_SOURCE_DIR}/src/*.c
		${CMAKE_CURRENT_SOURCE_DIR}/src/*.cpp
)

file(GLOB_RECURSE RCP_COMMON_HEADERS
		${CMAKE_CURRENT_SOURCE_DIR}/include/*.h
		${CMAKE_CURRENT_SOURCE_DIR}/include/*.hpp
)

##################
# Create Library #
##################

if (COMMAND idf_component_register) # ESP32 (IDF) regstration
	idf_component_register(
			SRCS ${RCP_COMMON_SOURCES}
			INCLUDE_DIRS "include"
	)
else () # Default CMake library creation
	add_library(rcp_common)
	add_library(rcp::common ALIAS rcp_common)
	target_sources(rcp_common
			PRIVATE
			${RCP_COMMON_SOURCES}
	)
	target_include_directories(rcp_common
			PUBLIC
			${CMAKE_CURRENT_SOURCE_DIR}/include
	)
endif ()

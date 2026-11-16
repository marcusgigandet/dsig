########################
# Collect source files #
########################

file(GLOB_RECURSE RCP_CORE_SOURCES
		${CMAKE_CURRENT_SOURCE_DIR}/src/*.c
		${CMAKE_CURRENT_SOURCE_DIR}/src/*.cpp
)

file(GLOB_RECURSE RCP_CORE_HEADERS
		${CMAKE_CURRENT_SOURCE_DIR}/include/*.h
		${CMAKE_CURRENT_SOURCE_DIR}/include/*.hpp
)

##################
# Create Library #
##################

if (COMMAND idf_component_register) # ESP32 (IDF) registration
	idf_component_register(
			SRCS ${RCP_CORE_SOURCES}
			INCLUDE_DIRS "include"
	)
	idf_component_get_property(rcp_core_target rcp_core COMPONENT_LIB)
	add_library(rcp::core ALIAS ${rcp_core_target})
else () # Default CMake library creation
	add_library(rcp_core)
	add_library(rcp::core ALIAS rcp_core)
	target_sources(rcp_core
			PRIVATE
			${RCP_CORE_SOURCES}
	)
	target_include_directories(rcp_core
			PUBLIC
			${CMAKE_CURRENT_SOURCE_DIR}/include
	)

	add_code_format_target(
		TARGET rcp_core
		ON_BUILD
		FILES ${RCP_CORE_SOURCES} ${RCP_CORE_HEADERS}
	)
	add_clang_tidy_target(
		TARGET rcp_core
		ON_BUILD
		FILES ${RCP_CORE_SOURCES}
	)

	add_cmake_format_target(
		TARGET rcp_core
		FILES ${CMAKE_CURRENT_SOURCE_DIR}/CMakeLists.txt
	)
	add_cmake_lint_target(
		TARGET rcp_core
		FILES ${CMAKE_CURRENT_SOURCE_DIR}/CMakeLists.txt
	)

	if (DSIG_SANITIZERS)
		enable_target_sanitizers(TARGET rcp_core)
	endif ()
endif ()

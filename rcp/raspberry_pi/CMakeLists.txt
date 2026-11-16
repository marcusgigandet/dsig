########################
# Collect source files #
########################

file(GLOB_RECURSE RCP_RPI_SOURCES CONFIGURE_DEPENDS
		${CMAKE_CURRENT_SOURCE_DIR}/src/*.cpp
)

file(GLOB_RECURSE RCP_RPI_HEADERS CONFIGURE_DEPENDS
		${CMAKE_CURRENT_SOURCE_DIR}/include/*.hpp
)

##############################
# Executable setup - RCP RPi #
##############################

add_executable(rcp_rpi)
target_sources(rcp_rpi
		PRIVATE
		${RCP_RPI_SOURCES}
)

target_include_directories(rcp_rpi
		PRIVATE
		${CMAKE_CURRENT_SOURCE_DIR}/include
)

target_link_libraries(rcp_rpi
		PRIVATE
		rcp::core
)

add_code_format_target(
	TARGET rcp_rpi
	ON_BUILD
	FILES ${RCP_RPI_SOURCES} ${RCP_RPI_HEADERS}
)
add_clang_tidy_target(
	TARGET rcp_rpi
	FILES ${RCP_RPI_SOURCES}
)
add_compile_commands_copy_target(TARGET rcp_rpi)

if (DSIG_SANITIZERS)
	enable_target_sanitizers(TARGET rcp_rpi)
endif ()

add_cmake_format_target(
	TARGET rcp_rpi
	FILES ${CMAKE_CURRENT_SOURCE_DIR}/CMakeLists.txt
)
add_cmake_lint_target(
	TARGET rcp_rpi
	FILES ${CMAKE_CURRENT_SOURCE_DIR}/CMakeLists.txt
)

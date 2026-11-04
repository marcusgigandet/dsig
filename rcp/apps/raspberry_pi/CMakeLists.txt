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
		rcp::common
)

get_filename_component(DSIG_ESP32_DIR "${CMAKE_CURRENT_LIST_DIR}/.." ABSOLUTE)
set(DSIG_CORE_DIR "${CMAKE_SOURCE_DIR}/rcp/rcp_core")
set(EXTRA_COMPONENT_DIRS "${DSIG_ESP32_DIR}/main" "${DSIG_CORE_DIR}")

include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(esp32)

include("${CMAKE_CURRENT_LIST_DIR}/targets.cmake")

if (EXISTS "${CMAKE_SOURCE_DIR}/vendor/cmake-tooling/CMakeLists.txt")
	# ESP-IDF's toolchain setup runs again if the submodule calls project().
	# Load its modules directly so compiler specs are registered only once.
	file(GLOB tooling_modules "${CMAKE_SOURCE_DIR}/vendor/cmake-tooling/modules/*.cmake")
	foreach (tooling_module IN LISTS tooling_modules)
		include("${tooling_module}")
	endforeach ()

	idf_component_get_property(main_target main COMPONENT_LIB)
	idf_component_get_property(core_target rcp_core COMPONENT_LIB)

	file(GLOB_RECURSE core_sources CONFIGURE_DEPENDS
		"${DSIG_CORE_DIR}/src/*.c"
		"${DSIG_CORE_DIR}/src/*.cpp")
	file(GLOB_RECURSE core_headers CONFIGURE_DEPENDS
		"${DSIG_CORE_DIR}/include/*.h"
		"${DSIG_CORE_DIR}/include/*.hpp")

	add_code_format_target(
		TARGET ${main_target}
		ON_BUILD
		FILES "${DSIG_ESP32_DIR}/main/main.cpp"
	)
	add_clang_tidy_target(
		TARGET ${main_target}
		FILES "${DSIG_ESP32_DIR}/main/main.cpp"
	)
	add_code_format_target(
		TARGET ${core_target}
		ON_BUILD
		FILES ${core_sources} ${core_headers}
	)
	add_clang_tidy_target(
		TARGET ${core_target}
		FILES ${core_sources}
	)
	add_compile_commands_copy_target(TARGET esp32.elf)

	set(DSIG_ESP32_CMAKE_FILES
		"${CMAKE_SOURCE_DIR}/CMakeLists.txt"
		"${CMAKE_CURRENT_LIST_FILE}"
		"${DSIG_ESP32_DIR}/main/CMakeLists.txt"
		"${DSIG_ESP32_DIR}/cmake/targets.cmake"
		"${DSIG_CORE_DIR}/CMakeLists.txt")
	add_cmake_format_target(TARGET esp32 FILES ${DSIG_ESP32_CMAKE_FILES})
	add_cmake_lint_target(TARGET esp32 FILES ${DSIG_ESP32_CMAKE_FILES})
else ()
	message(STATUS
		"cmake-tooling submodule not found; ESP32 tooling targets are disabled")
endif ()

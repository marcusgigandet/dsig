set(DSIG_FLASH_BAUD 460800 CACHE STRING "ESP32 flashing baud rate")

idf_build_get_property(idf_python PYTHON)
idf_build_get_property(idf_path IDF_PATH)
idf_build_get_property(build_dir BUILD_DIR)
idf_component_get_property(esptool_cmd esptool_py ESPTOOLPY_CMD)
idf_component_get_property(esptool_dir esptool_py COMPONENT_DIR)
idf_component_get_property(flash_args esptool_py FLASH_ARGS)
get_target_property(flash_dependencies flash MANUALLY_ADDED_DEPENDENCIES)

foreach (board RANGE 1 2)
	math(EXPR tcp_port "3999 + ${board}")
	set(DSIG_BOARD_${board}_PORT "rfc2217://host.docker.internal:${tcp_port}?ign_set_control"
		CACHE STRING "ESP32 board ${board} serial port")
	set(port "${DSIG_BOARD_${board}_PORT}")

	# Reuse IDF's image arguments, dependencies, and fast reflashing support.
	add_custom_target(flash-${board}
		COMMAND "${CMAKE_COMMAND}" -E env "ESPPORT=${port}" "ESPBAUD=${DSIG_FLASH_BAUD}"
			"${CMAKE_COMMAND}"
			"-DIDF_PATH=${idf_path}"
			"-DSERIAL_TOOL=${esptool_cmd}"
			"-DSERIAL_TOOL_ARGS=${flash_args};write-flash;@flash_args"
			-DSERIAL_TOOL_IS_WRITE_FLASH=1
			-DSERIAL_TOOL_FLASH_ARGS_FILE=flash_args
			"-DWORKING_DIRECTORY=${build_dir}"
			-P "${esptool_dir}/run_serial_tool.cmake"
		DEPENDS ${flash_dependencies}
		USES_TERMINAL
		VERBATIM
	)

	add_custom_target(erase-${board}
		COMMAND ${esptool_cmd} --port "${port}" --baud "${DSIG_FLASH_BAUD}" erase-flash
		USES_TERMINAL
		VERBATIM
	)
endforeach ()

add_custom_target(flash-all DEPENDS flash-1 flash-2)
add_custom_target(erase-all DEPENDS erase-1 erase-2)

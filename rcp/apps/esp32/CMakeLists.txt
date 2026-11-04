set(EXTRA_COMPONENT_DIRS
	"${CMAKE_CURRENT_LIST_DIR}/main"
	"${CMAKE_CURRENT_LIST_DIR}/../../libs/common"
)

include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(dsig)

include("${CMAKE_CURRENT_LIST_DIR}/targets.cmake")

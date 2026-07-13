find_package(Qt6 REQUIRED COMPONENTS Core)

add_executable(morfbeacon_demo main.cpp)
target_link_libraries(morfbeacon_demo PRIVATE morfBeacon::morfBeacon Qt6::Core)

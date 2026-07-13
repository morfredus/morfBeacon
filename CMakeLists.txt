cmake_minimum_required(VERSION 3.21)

# Version pilotee par le fichier VERSION (meme convention que ComponentHub / SiteWatch).
set(MORFBEACON_VERSION_FILE "${CMAKE_CURRENT_SOURCE_DIR}/VERSION")
set_property(DIRECTORY APPEND PROPERTY CMAKE_CONFIGURE_DEPENDS "${MORFBEACON_VERSION_FILE}")
file(STRINGS "${MORFBEACON_VERSION_FILE}" MORFBEACON_VERSION_FROM_FILE LIMIT_COUNT 1)
string(STRIP "${MORFBEACON_VERSION_FROM_FILE}" MORFBEACON_VERSION_FROM_FILE)

project(morfBeacon VERSION "${MORFBEACON_VERSION_FROM_FILE}" LANGUAGES CXX)

# --- Standard C++ ---------------------------------------------------------
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# --- Qt : generation automatique du moc (classes QObject) -----------------
set(CMAKE_AUTOMOC ON)

# La bibliotheque ne depend QUE de Qt Core + Qt Network. Pas de widgets :
# elle est utilisable dans une app GUI comme dans un service sans interface.
find_package(Qt6 REQUIRED COMPONENTS Core Network)

# --- Bibliotheque ---------------------------------------------------------
add_library(morfBeacon STATIC
    src/Heartbeat.cpp
    src/StatusServer.cpp
    src/PresenceService.cpp
    include/morfbeacon/PresenceConfig.h
    include/morfbeacon/IMetricsProvider.h
    include/morfbeacon/Heartbeat.h
    include/morfbeacon/StatusServer.h
    include/morfbeacon/PresenceService.h
)
add_library(morfBeacon::morfBeacon ALIAS morfBeacon)

target_include_directories(morfBeacon PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)

target_link_libraries(morfBeacon PUBLIC Qt6::Core Qt6::Network)

# Numero de version accessible depuis le code.
target_compile_definitions(morfBeacon PUBLIC MORFBEACON_VERSION="${PROJECT_VERSION}")

if(MSVC)
    target_compile_options(morfBeacon PRIVATE /utf-8)
endif()

# --- Exemple (compile seulement en build autonome, pas via add_subdirectory) -
if(CMAKE_SOURCE_DIR STREQUAL CMAKE_CURRENT_SOURCE_DIR)
    set(_morfbeacon_standalone ON)
else()
    set(_morfbeacon_standalone OFF)
endif()
option(MORFBEACON_BUILD_EXAMPLES "Compiler l'exemple de demonstration" ${_morfbeacon_standalone})

if(MORFBEACON_BUILD_EXAMPLES)
    add_subdirectory(examples/minimal)
endif()

cmake_minimum_required(VERSION 3.10)

project(rb-road-network VERSION 0.1.0 LANGUAGES CXX)

# Set C++ standard
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Include directories
include_directories(include)

# Add executables
add_executable(justPop src/justPop.cc src/lodepng.cpp)
add_executable(roadsrb src/roadsrb.cc src/lodepng.cpp)

# Link libraries
find_package(PkgConfig REQUIRED)
pkg_check_modules(GTK3 REQUIRED gtk+-3.0)
include_directories(${GTK3_INCLUDE_DIRS})
link_directories(${GTK3_LIBRARY_DIRS})
add_definitions(${GTK3_CFLAGS_OTHER})

target_link_libraries(justPop PRIVATE shp pthread stdc++fs)
target_link_libraries(roadsrb PRIVATE shp pthread stdc++fs ${GTK3_LIBRARIES} cairo xml2)

# Install targets
install(TARGETS justPop roadsrb DESTINATION bin)
install(DIRECTORY resources DESTINATION share/rb-road-network)
install(DIRECTORY scripts DESTINATION libexec/rb-road-network)
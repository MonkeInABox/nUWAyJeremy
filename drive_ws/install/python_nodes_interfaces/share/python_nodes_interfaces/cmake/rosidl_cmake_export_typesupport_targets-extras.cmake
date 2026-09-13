# generated from
# rosidl_cmake/cmake/template/rosidl_cmake_export_typesupport_targets.cmake.in

set(_exported_typesupport_targets
  "__rosidl_generator_c:python_nodes_interfaces__rosidl_generator_c;__rosidl_typesupport_fastrtps_c:python_nodes_interfaces__rosidl_typesupport_fastrtps_c;__rosidl_generator_cpp:python_nodes_interfaces__rosidl_generator_cpp;__rosidl_typesupport_fastrtps_cpp:python_nodes_interfaces__rosidl_typesupport_fastrtps_cpp;__rosidl_typesupport_introspection_c:python_nodes_interfaces__rosidl_typesupport_introspection_c;__rosidl_typesupport_c:python_nodes_interfaces__rosidl_typesupport_c;__rosidl_typesupport_introspection_cpp:python_nodes_interfaces__rosidl_typesupport_introspection_cpp;__rosidl_typesupport_cpp:python_nodes_interfaces__rosidl_typesupport_cpp;__rosidl_generator_py:python_nodes_interfaces__rosidl_generator_py")

# populate python_nodes_interfaces_TARGETS_<suffix>
if(NOT _exported_typesupport_targets STREQUAL "")
  # loop over typesupport targets
  foreach(_tuple ${_exported_typesupport_targets})
    string(REPLACE ":" ";" _tuple "${_tuple}")
    list(GET _tuple 0 _suffix)
    list(GET _tuple 1 _target)

    set(_target "python_nodes_interfaces::${_target}")
    if(NOT TARGET "${_target}")
      # the exported target must exist
      message(WARNING "Package 'python_nodes_interfaces' exports the typesupport target '${_target}' which doesn't exist")
    else()
      list(APPEND python_nodes_interfaces_TARGETS${_suffix} "${_target}")
    endif()
  endforeach()
endif()

// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from python_nodes_interfaces:msg/StringMultiArrayStamped.idl
// generated code does not contain a copyright notice

#ifndef PYTHON_NODES_INTERFACES__MSG__DETAIL__STRING_MULTI_ARRAY_STAMPED__STRUCT_H_
#define PYTHON_NODES_INTERFACES__MSG__DETAIL__STRING_MULTI_ARRAY_STAMPED__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__struct.h"
// Member 'layout'
#include "std_msgs/msg/detail/multi_array_layout__struct.h"
// Member 'action_commands'
// Member 'direction_commands'
// Member 'tertiary_commands'
#include "std_msgs/msg/detail/string__struct.h"

/// Struct defined in msg/StringMultiArrayStamped in the package python_nodes_interfaces.
typedef struct python_nodes_interfaces__msg__StringMultiArrayStamped
{
  std_msgs__msg__Header header;
  std_msgs__msg__MultiArrayLayout layout;
  std_msgs__msg__String__Sequence action_commands;
  std_msgs__msg__String__Sequence direction_commands;
  std_msgs__msg__String__Sequence tertiary_commands;
} python_nodes_interfaces__msg__StringMultiArrayStamped;

// Struct for a sequence of python_nodes_interfaces__msg__StringMultiArrayStamped.
typedef struct python_nodes_interfaces__msg__StringMultiArrayStamped__Sequence
{
  python_nodes_interfaces__msg__StringMultiArrayStamped * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} python_nodes_interfaces__msg__StringMultiArrayStamped__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // PYTHON_NODES_INTERFACES__MSG__DETAIL__STRING_MULTI_ARRAY_STAMPED__STRUCT_H_

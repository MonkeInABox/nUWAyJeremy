// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from python_nodes_interfaces:msg/StringStamped.idl
// generated code does not contain a copyright notice

#ifndef PYTHON_NODES_INTERFACES__MSG__DETAIL__STRING_STAMPED__STRUCT_H_
#define PYTHON_NODES_INTERFACES__MSG__DETAIL__STRING_STAMPED__STRUCT_H_

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
// Member 'data'
#include "std_msgs/msg/detail/string__struct.h"

/// Struct defined in msg/StringStamped in the package python_nodes_interfaces.
typedef struct python_nodes_interfaces__msg__StringStamped
{
  std_msgs__msg__Header header;
  std_msgs__msg__String data;
} python_nodes_interfaces__msg__StringStamped;

// Struct for a sequence of python_nodes_interfaces__msg__StringStamped.
typedef struct python_nodes_interfaces__msg__StringStamped__Sequence
{
  python_nodes_interfaces__msg__StringStamped * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} python_nodes_interfaces__msg__StringStamped__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // PYTHON_NODES_INTERFACES__MSG__DETAIL__STRING_STAMPED__STRUCT_H_

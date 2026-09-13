// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from python_nodes_interfaces:msg/BoolStamped.idl
// generated code does not contain a copyright notice

#ifndef PYTHON_NODES_INTERFACES__MSG__DETAIL__BOOL_STAMPED__STRUCT_H_
#define PYTHON_NODES_INTERFACES__MSG__DETAIL__BOOL_STAMPED__STRUCT_H_

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

/// Struct defined in msg/BoolStamped in the package python_nodes_interfaces.
typedef struct python_nodes_interfaces__msg__BoolStamped
{
  std_msgs__msg__Header header;
  bool data;
} python_nodes_interfaces__msg__BoolStamped;

// Struct for a sequence of python_nodes_interfaces__msg__BoolStamped.
typedef struct python_nodes_interfaces__msg__BoolStamped__Sequence
{
  python_nodes_interfaces__msg__BoolStamped * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} python_nodes_interfaces__msg__BoolStamped__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // PYTHON_NODES_INTERFACES__MSG__DETAIL__BOOL_STAMPED__STRUCT_H_

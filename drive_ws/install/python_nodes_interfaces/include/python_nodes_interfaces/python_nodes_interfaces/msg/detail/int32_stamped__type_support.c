// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from python_nodes_interfaces:msg/Int32Stamped.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "python_nodes_interfaces/msg/detail/int32_stamped__rosidl_typesupport_introspection_c.h"
#include "python_nodes_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "python_nodes_interfaces/msg/detail/int32_stamped__functions.h"
#include "python_nodes_interfaces/msg/detail/int32_stamped__struct.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/header.h"
// Member `header`
#include "std_msgs/msg/detail/header__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void python_nodes_interfaces__msg__Int32Stamped__rosidl_typesupport_introspection_c__Int32Stamped_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  python_nodes_interfaces__msg__Int32Stamped__init(message_memory);
}

void python_nodes_interfaces__msg__Int32Stamped__rosidl_typesupport_introspection_c__Int32Stamped_fini_function(void * message_memory)
{
  python_nodes_interfaces__msg__Int32Stamped__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember python_nodes_interfaces__msg__Int32Stamped__rosidl_typesupport_introspection_c__Int32Stamped_message_member_array[2] = {
  {
    "header",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(python_nodes_interfaces__msg__Int32Stamped, header),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "data",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_INT32,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(python_nodes_interfaces__msg__Int32Stamped, data),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers python_nodes_interfaces__msg__Int32Stamped__rosidl_typesupport_introspection_c__Int32Stamped_message_members = {
  "python_nodes_interfaces__msg",  // message namespace
  "Int32Stamped",  // message name
  2,  // number of fields
  sizeof(python_nodes_interfaces__msg__Int32Stamped),
  python_nodes_interfaces__msg__Int32Stamped__rosidl_typesupport_introspection_c__Int32Stamped_message_member_array,  // message members
  python_nodes_interfaces__msg__Int32Stamped__rosidl_typesupport_introspection_c__Int32Stamped_init_function,  // function to initialize message memory (memory has to be allocated)
  python_nodes_interfaces__msg__Int32Stamped__rosidl_typesupport_introspection_c__Int32Stamped_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t python_nodes_interfaces__msg__Int32Stamped__rosidl_typesupport_introspection_c__Int32Stamped_message_type_support_handle = {
  0,
  &python_nodes_interfaces__msg__Int32Stamped__rosidl_typesupport_introspection_c__Int32Stamped_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_python_nodes_interfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, python_nodes_interfaces, msg, Int32Stamped)() {
  python_nodes_interfaces__msg__Int32Stamped__rosidl_typesupport_introspection_c__Int32Stamped_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, std_msgs, msg, Header)();
  if (!python_nodes_interfaces__msg__Int32Stamped__rosidl_typesupport_introspection_c__Int32Stamped_message_type_support_handle.typesupport_identifier) {
    python_nodes_interfaces__msg__Int32Stamped__rosidl_typesupport_introspection_c__Int32Stamped_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &python_nodes_interfaces__msg__Int32Stamped__rosidl_typesupport_introspection_c__Int32Stamped_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif

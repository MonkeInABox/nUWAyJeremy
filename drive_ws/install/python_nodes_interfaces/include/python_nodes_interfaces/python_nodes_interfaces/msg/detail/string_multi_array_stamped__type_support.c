// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from python_nodes_interfaces:msg/StringMultiArrayStamped.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "python_nodes_interfaces/msg/detail/string_multi_array_stamped__rosidl_typesupport_introspection_c.h"
#include "python_nodes_interfaces/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "python_nodes_interfaces/msg/detail/string_multi_array_stamped__functions.h"
#include "python_nodes_interfaces/msg/detail/string_multi_array_stamped__struct.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/header.h"
// Member `header`
#include "std_msgs/msg/detail/header__rosidl_typesupport_introspection_c.h"
// Member `layout`
#include "std_msgs/msg/multi_array_layout.h"
// Member `layout`
#include "std_msgs/msg/detail/multi_array_layout__rosidl_typesupport_introspection_c.h"
// Member `action_commands`
// Member `direction_commands`
// Member `tertiary_commands`
#include "std_msgs/msg/string.h"
// Member `action_commands`
// Member `direction_commands`
// Member `tertiary_commands`
#include "std_msgs/msg/detail/string__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void python_nodes_interfaces__msg__StringMultiArrayStamped__rosidl_typesupport_introspection_c__StringMultiArrayStamped_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  python_nodes_interfaces__msg__StringMultiArrayStamped__init(message_memory);
}

void python_nodes_interfaces__msg__StringMultiArrayStamped__rosidl_typesupport_introspection_c__StringMultiArrayStamped_fini_function(void * message_memory)
{
  python_nodes_interfaces__msg__StringMultiArrayStamped__fini(message_memory);
}

size_t python_nodes_interfaces__msg__StringMultiArrayStamped__rosidl_typesupport_introspection_c__size_function__StringMultiArrayStamped__action_commands(
  const void * untyped_member)
{
  const std_msgs__msg__String__Sequence * member =
    (const std_msgs__msg__String__Sequence *)(untyped_member);
  return member->size;
}

const void * python_nodes_interfaces__msg__StringMultiArrayStamped__rosidl_typesupport_introspection_c__get_const_function__StringMultiArrayStamped__action_commands(
  const void * untyped_member, size_t index)
{
  const std_msgs__msg__String__Sequence * member =
    (const std_msgs__msg__String__Sequence *)(untyped_member);
  return &member->data[index];
}

void * python_nodes_interfaces__msg__StringMultiArrayStamped__rosidl_typesupport_introspection_c__get_function__StringMultiArrayStamped__action_commands(
  void * untyped_member, size_t index)
{
  std_msgs__msg__String__Sequence * member =
    (std_msgs__msg__String__Sequence *)(untyped_member);
  return &member->data[index];
}

void python_nodes_interfaces__msg__StringMultiArrayStamped__rosidl_typesupport_introspection_c__fetch_function__StringMultiArrayStamped__action_commands(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const std_msgs__msg__String * item =
    ((const std_msgs__msg__String *)
    python_nodes_interfaces__msg__StringMultiArrayStamped__rosidl_typesupport_introspection_c__get_const_function__StringMultiArrayStamped__action_commands(untyped_member, index));
  std_msgs__msg__String * value =
    (std_msgs__msg__String *)(untyped_value);
  *value = *item;
}

void python_nodes_interfaces__msg__StringMultiArrayStamped__rosidl_typesupport_introspection_c__assign_function__StringMultiArrayStamped__action_commands(
  void * untyped_member, size_t index, const void * untyped_value)
{
  std_msgs__msg__String * item =
    ((std_msgs__msg__String *)
    python_nodes_interfaces__msg__StringMultiArrayStamped__rosidl_typesupport_introspection_c__get_function__StringMultiArrayStamped__action_commands(untyped_member, index));
  const std_msgs__msg__String * value =
    (const std_msgs__msg__String *)(untyped_value);
  *item = *value;
}

bool python_nodes_interfaces__msg__StringMultiArrayStamped__rosidl_typesupport_introspection_c__resize_function__StringMultiArrayStamped__action_commands(
  void * untyped_member, size_t size)
{
  std_msgs__msg__String__Sequence * member =
    (std_msgs__msg__String__Sequence *)(untyped_member);
  std_msgs__msg__String__Sequence__fini(member);
  return std_msgs__msg__String__Sequence__init(member, size);
}

size_t python_nodes_interfaces__msg__StringMultiArrayStamped__rosidl_typesupport_introspection_c__size_function__StringMultiArrayStamped__direction_commands(
  const void * untyped_member)
{
  const std_msgs__msg__String__Sequence * member =
    (const std_msgs__msg__String__Sequence *)(untyped_member);
  return member->size;
}

const void * python_nodes_interfaces__msg__StringMultiArrayStamped__rosidl_typesupport_introspection_c__get_const_function__StringMultiArrayStamped__direction_commands(
  const void * untyped_member, size_t index)
{
  const std_msgs__msg__String__Sequence * member =
    (const std_msgs__msg__String__Sequence *)(untyped_member);
  return &member->data[index];
}

void * python_nodes_interfaces__msg__StringMultiArrayStamped__rosidl_typesupport_introspection_c__get_function__StringMultiArrayStamped__direction_commands(
  void * untyped_member, size_t index)
{
  std_msgs__msg__String__Sequence * member =
    (std_msgs__msg__String__Sequence *)(untyped_member);
  return &member->data[index];
}

void python_nodes_interfaces__msg__StringMultiArrayStamped__rosidl_typesupport_introspection_c__fetch_function__StringMultiArrayStamped__direction_commands(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const std_msgs__msg__String * item =
    ((const std_msgs__msg__String *)
    python_nodes_interfaces__msg__StringMultiArrayStamped__rosidl_typesupport_introspection_c__get_const_function__StringMultiArrayStamped__direction_commands(untyped_member, index));
  std_msgs__msg__String * value =
    (std_msgs__msg__String *)(untyped_value);
  *value = *item;
}

void python_nodes_interfaces__msg__StringMultiArrayStamped__rosidl_typesupport_introspection_c__assign_function__StringMultiArrayStamped__direction_commands(
  void * untyped_member, size_t index, const void * untyped_value)
{
  std_msgs__msg__String * item =
    ((std_msgs__msg__String *)
    python_nodes_interfaces__msg__StringMultiArrayStamped__rosidl_typesupport_introspection_c__get_function__StringMultiArrayStamped__direction_commands(untyped_member, index));
  const std_msgs__msg__String * value =
    (const std_msgs__msg__String *)(untyped_value);
  *item = *value;
}

bool python_nodes_interfaces__msg__StringMultiArrayStamped__rosidl_typesupport_introspection_c__resize_function__StringMultiArrayStamped__direction_commands(
  void * untyped_member, size_t size)
{
  std_msgs__msg__String__Sequence * member =
    (std_msgs__msg__String__Sequence *)(untyped_member);
  std_msgs__msg__String__Sequence__fini(member);
  return std_msgs__msg__String__Sequence__init(member, size);
}

size_t python_nodes_interfaces__msg__StringMultiArrayStamped__rosidl_typesupport_introspection_c__size_function__StringMultiArrayStamped__tertiary_commands(
  const void * untyped_member)
{
  const std_msgs__msg__String__Sequence * member =
    (const std_msgs__msg__String__Sequence *)(untyped_member);
  return member->size;
}

const void * python_nodes_interfaces__msg__StringMultiArrayStamped__rosidl_typesupport_introspection_c__get_const_function__StringMultiArrayStamped__tertiary_commands(
  const void * untyped_member, size_t index)
{
  const std_msgs__msg__String__Sequence * member =
    (const std_msgs__msg__String__Sequence *)(untyped_member);
  return &member->data[index];
}

void * python_nodes_interfaces__msg__StringMultiArrayStamped__rosidl_typesupport_introspection_c__get_function__StringMultiArrayStamped__tertiary_commands(
  void * untyped_member, size_t index)
{
  std_msgs__msg__String__Sequence * member =
    (std_msgs__msg__String__Sequence *)(untyped_member);
  return &member->data[index];
}

void python_nodes_interfaces__msg__StringMultiArrayStamped__rosidl_typesupport_introspection_c__fetch_function__StringMultiArrayStamped__tertiary_commands(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const std_msgs__msg__String * item =
    ((const std_msgs__msg__String *)
    python_nodes_interfaces__msg__StringMultiArrayStamped__rosidl_typesupport_introspection_c__get_const_function__StringMultiArrayStamped__tertiary_commands(untyped_member, index));
  std_msgs__msg__String * value =
    (std_msgs__msg__String *)(untyped_value);
  *value = *item;
}

void python_nodes_interfaces__msg__StringMultiArrayStamped__rosidl_typesupport_introspection_c__assign_function__StringMultiArrayStamped__tertiary_commands(
  void * untyped_member, size_t index, const void * untyped_value)
{
  std_msgs__msg__String * item =
    ((std_msgs__msg__String *)
    python_nodes_interfaces__msg__StringMultiArrayStamped__rosidl_typesupport_introspection_c__get_function__StringMultiArrayStamped__tertiary_commands(untyped_member, index));
  const std_msgs__msg__String * value =
    (const std_msgs__msg__String *)(untyped_value);
  *item = *value;
}

bool python_nodes_interfaces__msg__StringMultiArrayStamped__rosidl_typesupport_introspection_c__resize_function__StringMultiArrayStamped__tertiary_commands(
  void * untyped_member, size_t size)
{
  std_msgs__msg__String__Sequence * member =
    (std_msgs__msg__String__Sequence *)(untyped_member);
  std_msgs__msg__String__Sequence__fini(member);
  return std_msgs__msg__String__Sequence__init(member, size);
}

static rosidl_typesupport_introspection_c__MessageMember python_nodes_interfaces__msg__StringMultiArrayStamped__rosidl_typesupport_introspection_c__StringMultiArrayStamped_message_member_array[5] = {
  {
    "header",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(python_nodes_interfaces__msg__StringMultiArrayStamped, header),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "layout",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(python_nodes_interfaces__msg__StringMultiArrayStamped, layout),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "action_commands",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(python_nodes_interfaces__msg__StringMultiArrayStamped, action_commands),  // bytes offset in struct
    NULL,  // default value
    python_nodes_interfaces__msg__StringMultiArrayStamped__rosidl_typesupport_introspection_c__size_function__StringMultiArrayStamped__action_commands,  // size() function pointer
    python_nodes_interfaces__msg__StringMultiArrayStamped__rosidl_typesupport_introspection_c__get_const_function__StringMultiArrayStamped__action_commands,  // get_const(index) function pointer
    python_nodes_interfaces__msg__StringMultiArrayStamped__rosidl_typesupport_introspection_c__get_function__StringMultiArrayStamped__action_commands,  // get(index) function pointer
    python_nodes_interfaces__msg__StringMultiArrayStamped__rosidl_typesupport_introspection_c__fetch_function__StringMultiArrayStamped__action_commands,  // fetch(index, &value) function pointer
    python_nodes_interfaces__msg__StringMultiArrayStamped__rosidl_typesupport_introspection_c__assign_function__StringMultiArrayStamped__action_commands,  // assign(index, value) function pointer
    python_nodes_interfaces__msg__StringMultiArrayStamped__rosidl_typesupport_introspection_c__resize_function__StringMultiArrayStamped__action_commands  // resize(index) function pointer
  },
  {
    "direction_commands",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(python_nodes_interfaces__msg__StringMultiArrayStamped, direction_commands),  // bytes offset in struct
    NULL,  // default value
    python_nodes_interfaces__msg__StringMultiArrayStamped__rosidl_typesupport_introspection_c__size_function__StringMultiArrayStamped__direction_commands,  // size() function pointer
    python_nodes_interfaces__msg__StringMultiArrayStamped__rosidl_typesupport_introspection_c__get_const_function__StringMultiArrayStamped__direction_commands,  // get_const(index) function pointer
    python_nodes_interfaces__msg__StringMultiArrayStamped__rosidl_typesupport_introspection_c__get_function__StringMultiArrayStamped__direction_commands,  // get(index) function pointer
    python_nodes_interfaces__msg__StringMultiArrayStamped__rosidl_typesupport_introspection_c__fetch_function__StringMultiArrayStamped__direction_commands,  // fetch(index, &value) function pointer
    python_nodes_interfaces__msg__StringMultiArrayStamped__rosidl_typesupport_introspection_c__assign_function__StringMultiArrayStamped__direction_commands,  // assign(index, value) function pointer
    python_nodes_interfaces__msg__StringMultiArrayStamped__rosidl_typesupport_introspection_c__resize_function__StringMultiArrayStamped__direction_commands  // resize(index) function pointer
  },
  {
    "tertiary_commands",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(python_nodes_interfaces__msg__StringMultiArrayStamped, tertiary_commands),  // bytes offset in struct
    NULL,  // default value
    python_nodes_interfaces__msg__StringMultiArrayStamped__rosidl_typesupport_introspection_c__size_function__StringMultiArrayStamped__tertiary_commands,  // size() function pointer
    python_nodes_interfaces__msg__StringMultiArrayStamped__rosidl_typesupport_introspection_c__get_const_function__StringMultiArrayStamped__tertiary_commands,  // get_const(index) function pointer
    python_nodes_interfaces__msg__StringMultiArrayStamped__rosidl_typesupport_introspection_c__get_function__StringMultiArrayStamped__tertiary_commands,  // get(index) function pointer
    python_nodes_interfaces__msg__StringMultiArrayStamped__rosidl_typesupport_introspection_c__fetch_function__StringMultiArrayStamped__tertiary_commands,  // fetch(index, &value) function pointer
    python_nodes_interfaces__msg__StringMultiArrayStamped__rosidl_typesupport_introspection_c__assign_function__StringMultiArrayStamped__tertiary_commands,  // assign(index, value) function pointer
    python_nodes_interfaces__msg__StringMultiArrayStamped__rosidl_typesupport_introspection_c__resize_function__StringMultiArrayStamped__tertiary_commands  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers python_nodes_interfaces__msg__StringMultiArrayStamped__rosidl_typesupport_introspection_c__StringMultiArrayStamped_message_members = {
  "python_nodes_interfaces__msg",  // message namespace
  "StringMultiArrayStamped",  // message name
  5,  // number of fields
  sizeof(python_nodes_interfaces__msg__StringMultiArrayStamped),
  python_nodes_interfaces__msg__StringMultiArrayStamped__rosidl_typesupport_introspection_c__StringMultiArrayStamped_message_member_array,  // message members
  python_nodes_interfaces__msg__StringMultiArrayStamped__rosidl_typesupport_introspection_c__StringMultiArrayStamped_init_function,  // function to initialize message memory (memory has to be allocated)
  python_nodes_interfaces__msg__StringMultiArrayStamped__rosidl_typesupport_introspection_c__StringMultiArrayStamped_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t python_nodes_interfaces__msg__StringMultiArrayStamped__rosidl_typesupport_introspection_c__StringMultiArrayStamped_message_type_support_handle = {
  0,
  &python_nodes_interfaces__msg__StringMultiArrayStamped__rosidl_typesupport_introspection_c__StringMultiArrayStamped_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_python_nodes_interfaces
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, python_nodes_interfaces, msg, StringMultiArrayStamped)() {
  python_nodes_interfaces__msg__StringMultiArrayStamped__rosidl_typesupport_introspection_c__StringMultiArrayStamped_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, std_msgs, msg, Header)();
  python_nodes_interfaces__msg__StringMultiArrayStamped__rosidl_typesupport_introspection_c__StringMultiArrayStamped_message_member_array[1].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, std_msgs, msg, MultiArrayLayout)();
  python_nodes_interfaces__msg__StringMultiArrayStamped__rosidl_typesupport_introspection_c__StringMultiArrayStamped_message_member_array[2].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, std_msgs, msg, String)();
  python_nodes_interfaces__msg__StringMultiArrayStamped__rosidl_typesupport_introspection_c__StringMultiArrayStamped_message_member_array[3].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, std_msgs, msg, String)();
  python_nodes_interfaces__msg__StringMultiArrayStamped__rosidl_typesupport_introspection_c__StringMultiArrayStamped_message_member_array[4].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, std_msgs, msg, String)();
  if (!python_nodes_interfaces__msg__StringMultiArrayStamped__rosidl_typesupport_introspection_c__StringMultiArrayStamped_message_type_support_handle.typesupport_identifier) {
    python_nodes_interfaces__msg__StringMultiArrayStamped__rosidl_typesupport_introspection_c__StringMultiArrayStamped_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &python_nodes_interfaces__msg__StringMultiArrayStamped__rosidl_typesupport_introspection_c__StringMultiArrayStamped_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif

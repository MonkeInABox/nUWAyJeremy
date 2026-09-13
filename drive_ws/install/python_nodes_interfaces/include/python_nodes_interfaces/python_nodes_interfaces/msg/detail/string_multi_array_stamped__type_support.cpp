// generated from rosidl_typesupport_introspection_cpp/resource/idl__type_support.cpp.em
// with input from python_nodes_interfaces:msg/StringMultiArrayStamped.idl
// generated code does not contain a copyright notice

#include "array"
#include "cstddef"
#include "string"
#include "vector"
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_typesupport_cpp/message_type_support.hpp"
#include "rosidl_typesupport_interface/macros.h"
#include "python_nodes_interfaces/msg/detail/string_multi_array_stamped__struct.hpp"
#include "rosidl_typesupport_introspection_cpp/field_types.hpp"
#include "rosidl_typesupport_introspection_cpp/identifier.hpp"
#include "rosidl_typesupport_introspection_cpp/message_introspection.hpp"
#include "rosidl_typesupport_introspection_cpp/message_type_support_decl.hpp"
#include "rosidl_typesupport_introspection_cpp/visibility_control.h"

namespace python_nodes_interfaces
{

namespace msg
{

namespace rosidl_typesupport_introspection_cpp
{

void StringMultiArrayStamped_init_function(
  void * message_memory, rosidl_runtime_cpp::MessageInitialization _init)
{
  new (message_memory) python_nodes_interfaces::msg::StringMultiArrayStamped(_init);
}

void StringMultiArrayStamped_fini_function(void * message_memory)
{
  auto typed_message = static_cast<python_nodes_interfaces::msg::StringMultiArrayStamped *>(message_memory);
  typed_message->~StringMultiArrayStamped();
}

size_t size_function__StringMultiArrayStamped__action_commands(const void * untyped_member)
{
  const auto * member = reinterpret_cast<const std::vector<std_msgs::msg::String> *>(untyped_member);
  return member->size();
}

const void * get_const_function__StringMultiArrayStamped__action_commands(const void * untyped_member, size_t index)
{
  const auto & member =
    *reinterpret_cast<const std::vector<std_msgs::msg::String> *>(untyped_member);
  return &member[index];
}

void * get_function__StringMultiArrayStamped__action_commands(void * untyped_member, size_t index)
{
  auto & member =
    *reinterpret_cast<std::vector<std_msgs::msg::String> *>(untyped_member);
  return &member[index];
}

void fetch_function__StringMultiArrayStamped__action_commands(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const auto & item = *reinterpret_cast<const std_msgs::msg::String *>(
    get_const_function__StringMultiArrayStamped__action_commands(untyped_member, index));
  auto & value = *reinterpret_cast<std_msgs::msg::String *>(untyped_value);
  value = item;
}

void assign_function__StringMultiArrayStamped__action_commands(
  void * untyped_member, size_t index, const void * untyped_value)
{
  auto & item = *reinterpret_cast<std_msgs::msg::String *>(
    get_function__StringMultiArrayStamped__action_commands(untyped_member, index));
  const auto & value = *reinterpret_cast<const std_msgs::msg::String *>(untyped_value);
  item = value;
}

void resize_function__StringMultiArrayStamped__action_commands(void * untyped_member, size_t size)
{
  auto * member =
    reinterpret_cast<std::vector<std_msgs::msg::String> *>(untyped_member);
  member->resize(size);
}

size_t size_function__StringMultiArrayStamped__direction_commands(const void * untyped_member)
{
  const auto * member = reinterpret_cast<const std::vector<std_msgs::msg::String> *>(untyped_member);
  return member->size();
}

const void * get_const_function__StringMultiArrayStamped__direction_commands(const void * untyped_member, size_t index)
{
  const auto & member =
    *reinterpret_cast<const std::vector<std_msgs::msg::String> *>(untyped_member);
  return &member[index];
}

void * get_function__StringMultiArrayStamped__direction_commands(void * untyped_member, size_t index)
{
  auto & member =
    *reinterpret_cast<std::vector<std_msgs::msg::String> *>(untyped_member);
  return &member[index];
}

void fetch_function__StringMultiArrayStamped__direction_commands(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const auto & item = *reinterpret_cast<const std_msgs::msg::String *>(
    get_const_function__StringMultiArrayStamped__direction_commands(untyped_member, index));
  auto & value = *reinterpret_cast<std_msgs::msg::String *>(untyped_value);
  value = item;
}

void assign_function__StringMultiArrayStamped__direction_commands(
  void * untyped_member, size_t index, const void * untyped_value)
{
  auto & item = *reinterpret_cast<std_msgs::msg::String *>(
    get_function__StringMultiArrayStamped__direction_commands(untyped_member, index));
  const auto & value = *reinterpret_cast<const std_msgs::msg::String *>(untyped_value);
  item = value;
}

void resize_function__StringMultiArrayStamped__direction_commands(void * untyped_member, size_t size)
{
  auto * member =
    reinterpret_cast<std::vector<std_msgs::msg::String> *>(untyped_member);
  member->resize(size);
}

size_t size_function__StringMultiArrayStamped__tertiary_commands(const void * untyped_member)
{
  const auto * member = reinterpret_cast<const std::vector<std_msgs::msg::String> *>(untyped_member);
  return member->size();
}

const void * get_const_function__StringMultiArrayStamped__tertiary_commands(const void * untyped_member, size_t index)
{
  const auto & member =
    *reinterpret_cast<const std::vector<std_msgs::msg::String> *>(untyped_member);
  return &member[index];
}

void * get_function__StringMultiArrayStamped__tertiary_commands(void * untyped_member, size_t index)
{
  auto & member =
    *reinterpret_cast<std::vector<std_msgs::msg::String> *>(untyped_member);
  return &member[index];
}

void fetch_function__StringMultiArrayStamped__tertiary_commands(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const auto & item = *reinterpret_cast<const std_msgs::msg::String *>(
    get_const_function__StringMultiArrayStamped__tertiary_commands(untyped_member, index));
  auto & value = *reinterpret_cast<std_msgs::msg::String *>(untyped_value);
  value = item;
}

void assign_function__StringMultiArrayStamped__tertiary_commands(
  void * untyped_member, size_t index, const void * untyped_value)
{
  auto & item = *reinterpret_cast<std_msgs::msg::String *>(
    get_function__StringMultiArrayStamped__tertiary_commands(untyped_member, index));
  const auto & value = *reinterpret_cast<const std_msgs::msg::String *>(untyped_value);
  item = value;
}

void resize_function__StringMultiArrayStamped__tertiary_commands(void * untyped_member, size_t size)
{
  auto * member =
    reinterpret_cast<std::vector<std_msgs::msg::String> *>(untyped_member);
  member->resize(size);
}

static const ::rosidl_typesupport_introspection_cpp::MessageMember StringMultiArrayStamped_message_member_array[5] = {
  {
    "header",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<std_msgs::msg::Header>(),  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(python_nodes_interfaces::msg::StringMultiArrayStamped, header),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "layout",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<std_msgs::msg::MultiArrayLayout>(),  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(python_nodes_interfaces::msg::StringMultiArrayStamped, layout),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "action_commands",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<std_msgs::msg::String>(),  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(python_nodes_interfaces::msg::StringMultiArrayStamped, action_commands),  // bytes offset in struct
    nullptr,  // default value
    size_function__StringMultiArrayStamped__action_commands,  // size() function pointer
    get_const_function__StringMultiArrayStamped__action_commands,  // get_const(index) function pointer
    get_function__StringMultiArrayStamped__action_commands,  // get(index) function pointer
    fetch_function__StringMultiArrayStamped__action_commands,  // fetch(index, &value) function pointer
    assign_function__StringMultiArrayStamped__action_commands,  // assign(index, value) function pointer
    resize_function__StringMultiArrayStamped__action_commands  // resize(index) function pointer
  },
  {
    "direction_commands",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<std_msgs::msg::String>(),  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(python_nodes_interfaces::msg::StringMultiArrayStamped, direction_commands),  // bytes offset in struct
    nullptr,  // default value
    size_function__StringMultiArrayStamped__direction_commands,  // size() function pointer
    get_const_function__StringMultiArrayStamped__direction_commands,  // get_const(index) function pointer
    get_function__StringMultiArrayStamped__direction_commands,  // get(index) function pointer
    fetch_function__StringMultiArrayStamped__direction_commands,  // fetch(index, &value) function pointer
    assign_function__StringMultiArrayStamped__direction_commands,  // assign(index, value) function pointer
    resize_function__StringMultiArrayStamped__direction_commands  // resize(index) function pointer
  },
  {
    "tertiary_commands",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<std_msgs::msg::String>(),  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(python_nodes_interfaces::msg::StringMultiArrayStamped, tertiary_commands),  // bytes offset in struct
    nullptr,  // default value
    size_function__StringMultiArrayStamped__tertiary_commands,  // size() function pointer
    get_const_function__StringMultiArrayStamped__tertiary_commands,  // get_const(index) function pointer
    get_function__StringMultiArrayStamped__tertiary_commands,  // get(index) function pointer
    fetch_function__StringMultiArrayStamped__tertiary_commands,  // fetch(index, &value) function pointer
    assign_function__StringMultiArrayStamped__tertiary_commands,  // assign(index, value) function pointer
    resize_function__StringMultiArrayStamped__tertiary_commands  // resize(index) function pointer
  }
};

static const ::rosidl_typesupport_introspection_cpp::MessageMembers StringMultiArrayStamped_message_members = {
  "python_nodes_interfaces::msg",  // message namespace
  "StringMultiArrayStamped",  // message name
  5,  // number of fields
  sizeof(python_nodes_interfaces::msg::StringMultiArrayStamped),
  StringMultiArrayStamped_message_member_array,  // message members
  StringMultiArrayStamped_init_function,  // function to initialize message memory (memory has to be allocated)
  StringMultiArrayStamped_fini_function  // function to terminate message instance (will not free memory)
};

static const rosidl_message_type_support_t StringMultiArrayStamped_message_type_support_handle = {
  ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  &StringMultiArrayStamped_message_members,
  get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_introspection_cpp

}  // namespace msg

}  // namespace python_nodes_interfaces


namespace rosidl_typesupport_introspection_cpp
{

template<>
ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<python_nodes_interfaces::msg::StringMultiArrayStamped>()
{
  return &::python_nodes_interfaces::msg::rosidl_typesupport_introspection_cpp::StringMultiArrayStamped_message_type_support_handle;
}

}  // namespace rosidl_typesupport_introspection_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, python_nodes_interfaces, msg, StringMultiArrayStamped)() {
  return &::python_nodes_interfaces::msg::rosidl_typesupport_introspection_cpp::StringMultiArrayStamped_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif

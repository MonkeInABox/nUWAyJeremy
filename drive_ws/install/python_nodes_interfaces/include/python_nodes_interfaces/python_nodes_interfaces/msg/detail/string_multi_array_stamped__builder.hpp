// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from python_nodes_interfaces:msg/StringMultiArrayStamped.idl
// generated code does not contain a copyright notice

#ifndef PYTHON_NODES_INTERFACES__MSG__DETAIL__STRING_MULTI_ARRAY_STAMPED__BUILDER_HPP_
#define PYTHON_NODES_INTERFACES__MSG__DETAIL__STRING_MULTI_ARRAY_STAMPED__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "python_nodes_interfaces/msg/detail/string_multi_array_stamped__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace python_nodes_interfaces
{

namespace msg
{

namespace builder
{

class Init_StringMultiArrayStamped_tertiary_commands
{
public:
  explicit Init_StringMultiArrayStamped_tertiary_commands(::python_nodes_interfaces::msg::StringMultiArrayStamped & msg)
  : msg_(msg)
  {}
  ::python_nodes_interfaces::msg::StringMultiArrayStamped tertiary_commands(::python_nodes_interfaces::msg::StringMultiArrayStamped::_tertiary_commands_type arg)
  {
    msg_.tertiary_commands = std::move(arg);
    return std::move(msg_);
  }

private:
  ::python_nodes_interfaces::msg::StringMultiArrayStamped msg_;
};

class Init_StringMultiArrayStamped_direction_commands
{
public:
  explicit Init_StringMultiArrayStamped_direction_commands(::python_nodes_interfaces::msg::StringMultiArrayStamped & msg)
  : msg_(msg)
  {}
  Init_StringMultiArrayStamped_tertiary_commands direction_commands(::python_nodes_interfaces::msg::StringMultiArrayStamped::_direction_commands_type arg)
  {
    msg_.direction_commands = std::move(arg);
    return Init_StringMultiArrayStamped_tertiary_commands(msg_);
  }

private:
  ::python_nodes_interfaces::msg::StringMultiArrayStamped msg_;
};

class Init_StringMultiArrayStamped_action_commands
{
public:
  explicit Init_StringMultiArrayStamped_action_commands(::python_nodes_interfaces::msg::StringMultiArrayStamped & msg)
  : msg_(msg)
  {}
  Init_StringMultiArrayStamped_direction_commands action_commands(::python_nodes_interfaces::msg::StringMultiArrayStamped::_action_commands_type arg)
  {
    msg_.action_commands = std::move(arg);
    return Init_StringMultiArrayStamped_direction_commands(msg_);
  }

private:
  ::python_nodes_interfaces::msg::StringMultiArrayStamped msg_;
};

class Init_StringMultiArrayStamped_layout
{
public:
  explicit Init_StringMultiArrayStamped_layout(::python_nodes_interfaces::msg::StringMultiArrayStamped & msg)
  : msg_(msg)
  {}
  Init_StringMultiArrayStamped_action_commands layout(::python_nodes_interfaces::msg::StringMultiArrayStamped::_layout_type arg)
  {
    msg_.layout = std::move(arg);
    return Init_StringMultiArrayStamped_action_commands(msg_);
  }

private:
  ::python_nodes_interfaces::msg::StringMultiArrayStamped msg_;
};

class Init_StringMultiArrayStamped_header
{
public:
  Init_StringMultiArrayStamped_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_StringMultiArrayStamped_layout header(::python_nodes_interfaces::msg::StringMultiArrayStamped::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_StringMultiArrayStamped_layout(msg_);
  }

private:
  ::python_nodes_interfaces::msg::StringMultiArrayStamped msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::python_nodes_interfaces::msg::StringMultiArrayStamped>()
{
  return python_nodes_interfaces::msg::builder::Init_StringMultiArrayStamped_header();
}

}  // namespace python_nodes_interfaces

#endif  // PYTHON_NODES_INTERFACES__MSG__DETAIL__STRING_MULTI_ARRAY_STAMPED__BUILDER_HPP_

// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from python_nodes_interfaces:msg/StringStamped.idl
// generated code does not contain a copyright notice

#ifndef PYTHON_NODES_INTERFACES__MSG__DETAIL__STRING_STAMPED__BUILDER_HPP_
#define PYTHON_NODES_INTERFACES__MSG__DETAIL__STRING_STAMPED__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "python_nodes_interfaces/msg/detail/string_stamped__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace python_nodes_interfaces
{

namespace msg
{

namespace builder
{

class Init_StringStamped_data
{
public:
  explicit Init_StringStamped_data(::python_nodes_interfaces::msg::StringStamped & msg)
  : msg_(msg)
  {}
  ::python_nodes_interfaces::msg::StringStamped data(::python_nodes_interfaces::msg::StringStamped::_data_type arg)
  {
    msg_.data = std::move(arg);
    return std::move(msg_);
  }

private:
  ::python_nodes_interfaces::msg::StringStamped msg_;
};

class Init_StringStamped_header
{
public:
  Init_StringStamped_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_StringStamped_data header(::python_nodes_interfaces::msg::StringStamped::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_StringStamped_data(msg_);
  }

private:
  ::python_nodes_interfaces::msg::StringStamped msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::python_nodes_interfaces::msg::StringStamped>()
{
  return python_nodes_interfaces::msg::builder::Init_StringStamped_header();
}

}  // namespace python_nodes_interfaces

#endif  // PYTHON_NODES_INTERFACES__MSG__DETAIL__STRING_STAMPED__BUILDER_HPP_

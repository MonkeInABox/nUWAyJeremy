// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from python_nodes_interfaces:msg/BoolStamped.idl
// generated code does not contain a copyright notice

#ifndef PYTHON_NODES_INTERFACES__MSG__DETAIL__BOOL_STAMPED__BUILDER_HPP_
#define PYTHON_NODES_INTERFACES__MSG__DETAIL__BOOL_STAMPED__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "python_nodes_interfaces/msg/detail/bool_stamped__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace python_nodes_interfaces
{

namespace msg
{

namespace builder
{

class Init_BoolStamped_data
{
public:
  explicit Init_BoolStamped_data(::python_nodes_interfaces::msg::BoolStamped & msg)
  : msg_(msg)
  {}
  ::python_nodes_interfaces::msg::BoolStamped data(::python_nodes_interfaces::msg::BoolStamped::_data_type arg)
  {
    msg_.data = std::move(arg);
    return std::move(msg_);
  }

private:
  ::python_nodes_interfaces::msg::BoolStamped msg_;
};

class Init_BoolStamped_header
{
public:
  Init_BoolStamped_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_BoolStamped_data header(::python_nodes_interfaces::msg::BoolStamped::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_BoolStamped_data(msg_);
  }

private:
  ::python_nodes_interfaces::msg::BoolStamped msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::python_nodes_interfaces::msg::BoolStamped>()
{
  return python_nodes_interfaces::msg::builder::Init_BoolStamped_header();
}

}  // namespace python_nodes_interfaces

#endif  // PYTHON_NODES_INTERFACES__MSG__DETAIL__BOOL_STAMPED__BUILDER_HPP_

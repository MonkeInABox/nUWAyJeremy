// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from python_nodes_interfaces:msg/Int32Stamped.idl
// generated code does not contain a copyright notice

#ifndef PYTHON_NODES_INTERFACES__MSG__DETAIL__INT32_STAMPED__BUILDER_HPP_
#define PYTHON_NODES_INTERFACES__MSG__DETAIL__INT32_STAMPED__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "python_nodes_interfaces/msg/detail/int32_stamped__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace python_nodes_interfaces
{

namespace msg
{

namespace builder
{

class Init_Int32Stamped_data
{
public:
  explicit Init_Int32Stamped_data(::python_nodes_interfaces::msg::Int32Stamped & msg)
  : msg_(msg)
  {}
  ::python_nodes_interfaces::msg::Int32Stamped data(::python_nodes_interfaces::msg::Int32Stamped::_data_type arg)
  {
    msg_.data = std::move(arg);
    return std::move(msg_);
  }

private:
  ::python_nodes_interfaces::msg::Int32Stamped msg_;
};

class Init_Int32Stamped_header
{
public:
  Init_Int32Stamped_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_Int32Stamped_data header(::python_nodes_interfaces::msg::Int32Stamped::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_Int32Stamped_data(msg_);
  }

private:
  ::python_nodes_interfaces::msg::Int32Stamped msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::python_nodes_interfaces::msg::Int32Stamped>()
{
  return python_nodes_interfaces::msg::builder::Init_Int32Stamped_header();
}

}  // namespace python_nodes_interfaces

#endif  // PYTHON_NODES_INTERFACES__MSG__DETAIL__INT32_STAMPED__BUILDER_HPP_

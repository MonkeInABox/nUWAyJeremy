// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from python_nodes_interfaces:msg/Float32MultiArrayStamped.idl
// generated code does not contain a copyright notice

#ifndef PYTHON_NODES_INTERFACES__MSG__DETAIL__FLOAT32_MULTI_ARRAY_STAMPED__BUILDER_HPP_
#define PYTHON_NODES_INTERFACES__MSG__DETAIL__FLOAT32_MULTI_ARRAY_STAMPED__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "python_nodes_interfaces/msg/detail/float32_multi_array_stamped__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace python_nodes_interfaces
{

namespace msg
{

namespace builder
{

class Init_Float32MultiArrayStamped_data
{
public:
  explicit Init_Float32MultiArrayStamped_data(::python_nodes_interfaces::msg::Float32MultiArrayStamped & msg)
  : msg_(msg)
  {}
  ::python_nodes_interfaces::msg::Float32MultiArrayStamped data(::python_nodes_interfaces::msg::Float32MultiArrayStamped::_data_type arg)
  {
    msg_.data = std::move(arg);
    return std::move(msg_);
  }

private:
  ::python_nodes_interfaces::msg::Float32MultiArrayStamped msg_;
};

class Init_Float32MultiArrayStamped_layout
{
public:
  explicit Init_Float32MultiArrayStamped_layout(::python_nodes_interfaces::msg::Float32MultiArrayStamped & msg)
  : msg_(msg)
  {}
  Init_Float32MultiArrayStamped_data layout(::python_nodes_interfaces::msg::Float32MultiArrayStamped::_layout_type arg)
  {
    msg_.layout = std::move(arg);
    return Init_Float32MultiArrayStamped_data(msg_);
  }

private:
  ::python_nodes_interfaces::msg::Float32MultiArrayStamped msg_;
};

class Init_Float32MultiArrayStamped_header
{
public:
  Init_Float32MultiArrayStamped_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_Float32MultiArrayStamped_layout header(::python_nodes_interfaces::msg::Float32MultiArrayStamped::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_Float32MultiArrayStamped_layout(msg_);
  }

private:
  ::python_nodes_interfaces::msg::Float32MultiArrayStamped msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::python_nodes_interfaces::msg::Float32MultiArrayStamped>()
{
  return python_nodes_interfaces::msg::builder::Init_Float32MultiArrayStamped_header();
}

}  // namespace python_nodes_interfaces

#endif  // PYTHON_NODES_INTERFACES__MSG__DETAIL__FLOAT32_MULTI_ARRAY_STAMPED__BUILDER_HPP_

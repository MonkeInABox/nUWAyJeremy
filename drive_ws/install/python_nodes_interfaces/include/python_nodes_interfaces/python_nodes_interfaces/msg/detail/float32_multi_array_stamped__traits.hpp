// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from python_nodes_interfaces:msg/Float32MultiArrayStamped.idl
// generated code does not contain a copyright notice

#ifndef PYTHON_NODES_INTERFACES__MSG__DETAIL__FLOAT32_MULTI_ARRAY_STAMPED__TRAITS_HPP_
#define PYTHON_NODES_INTERFACES__MSG__DETAIL__FLOAT32_MULTI_ARRAY_STAMPED__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "python_nodes_interfaces/msg/detail/float32_multi_array_stamped__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__traits.hpp"
// Member 'layout'
#include "std_msgs/msg/detail/multi_array_layout__traits.hpp"

namespace python_nodes_interfaces
{

namespace msg
{

inline void to_flow_style_yaml(
  const Float32MultiArrayStamped & msg,
  std::ostream & out)
{
  out << "{";
  // member: header
  {
    out << "header: ";
    to_flow_style_yaml(msg.header, out);
    out << ", ";
  }

  // member: layout
  {
    out << "layout: ";
    to_flow_style_yaml(msg.layout, out);
    out << ", ";
  }

  // member: data
  {
    if (msg.data.size() == 0) {
      out << "data: []";
    } else {
      out << "data: [";
      size_t pending_items = msg.data.size();
      for (auto item : msg.data) {
        rosidl_generator_traits::value_to_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const Float32MultiArrayStamped & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: header
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "header:\n";
    to_block_style_yaml(msg.header, out, indentation + 2);
  }

  // member: layout
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "layout:\n";
    to_block_style_yaml(msg.layout, out, indentation + 2);
  }

  // member: data
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.data.size() == 0) {
      out << "data: []\n";
    } else {
      out << "data:\n";
      for (auto item : msg.data) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "- ";
        rosidl_generator_traits::value_to_yaml(item, out);
        out << "\n";
      }
    }
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const Float32MultiArrayStamped & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace msg

}  // namespace python_nodes_interfaces

namespace rosidl_generator_traits
{

[[deprecated("use python_nodes_interfaces::msg::to_block_style_yaml() instead")]]
inline void to_yaml(
  const python_nodes_interfaces::msg::Float32MultiArrayStamped & msg,
  std::ostream & out, size_t indentation = 0)
{
  python_nodes_interfaces::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use python_nodes_interfaces::msg::to_yaml() instead")]]
inline std::string to_yaml(const python_nodes_interfaces::msg::Float32MultiArrayStamped & msg)
{
  return python_nodes_interfaces::msg::to_yaml(msg);
}

template<>
inline const char * data_type<python_nodes_interfaces::msg::Float32MultiArrayStamped>()
{
  return "python_nodes_interfaces::msg::Float32MultiArrayStamped";
}

template<>
inline const char * name<python_nodes_interfaces::msg::Float32MultiArrayStamped>()
{
  return "python_nodes_interfaces/msg/Float32MultiArrayStamped";
}

template<>
struct has_fixed_size<python_nodes_interfaces::msg::Float32MultiArrayStamped>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<python_nodes_interfaces::msg::Float32MultiArrayStamped>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<python_nodes_interfaces::msg::Float32MultiArrayStamped>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // PYTHON_NODES_INTERFACES__MSG__DETAIL__FLOAT32_MULTI_ARRAY_STAMPED__TRAITS_HPP_

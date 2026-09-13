// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from python_nodes_interfaces:msg/StringMultiArrayStamped.idl
// generated code does not contain a copyright notice

#ifndef PYTHON_NODES_INTERFACES__MSG__DETAIL__STRING_MULTI_ARRAY_STAMPED__TRAITS_HPP_
#define PYTHON_NODES_INTERFACES__MSG__DETAIL__STRING_MULTI_ARRAY_STAMPED__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "python_nodes_interfaces/msg/detail/string_multi_array_stamped__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__traits.hpp"
// Member 'layout'
#include "std_msgs/msg/detail/multi_array_layout__traits.hpp"
// Member 'action_commands'
// Member 'direction_commands'
// Member 'tertiary_commands'
#include "std_msgs/msg/detail/string__traits.hpp"

namespace python_nodes_interfaces
{

namespace msg
{

inline void to_flow_style_yaml(
  const StringMultiArrayStamped & msg,
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

  // member: action_commands
  {
    if (msg.action_commands.size() == 0) {
      out << "action_commands: []";
    } else {
      out << "action_commands: [";
      size_t pending_items = msg.action_commands.size();
      for (auto item : msg.action_commands) {
        to_flow_style_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: direction_commands
  {
    if (msg.direction_commands.size() == 0) {
      out << "direction_commands: []";
    } else {
      out << "direction_commands: [";
      size_t pending_items = msg.direction_commands.size();
      for (auto item : msg.direction_commands) {
        to_flow_style_yaml(item, out);
        if (--pending_items > 0) {
          out << ", ";
        }
      }
      out << "]";
    }
    out << ", ";
  }

  // member: tertiary_commands
  {
    if (msg.tertiary_commands.size() == 0) {
      out << "tertiary_commands: []";
    } else {
      out << "tertiary_commands: [";
      size_t pending_items = msg.tertiary_commands.size();
      for (auto item : msg.tertiary_commands) {
        to_flow_style_yaml(item, out);
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
  const StringMultiArrayStamped & msg,
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

  // member: action_commands
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.action_commands.size() == 0) {
      out << "action_commands: []\n";
    } else {
      out << "action_commands:\n";
      for (auto item : msg.action_commands) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "-\n";
        to_block_style_yaml(item, out, indentation + 2);
      }
    }
  }

  // member: direction_commands
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.direction_commands.size() == 0) {
      out << "direction_commands: []\n";
    } else {
      out << "direction_commands:\n";
      for (auto item : msg.direction_commands) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "-\n";
        to_block_style_yaml(item, out, indentation + 2);
      }
    }
  }

  // member: tertiary_commands
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    if (msg.tertiary_commands.size() == 0) {
      out << "tertiary_commands: []\n";
    } else {
      out << "tertiary_commands:\n";
      for (auto item : msg.tertiary_commands) {
        if (indentation > 0) {
          out << std::string(indentation, ' ');
        }
        out << "-\n";
        to_block_style_yaml(item, out, indentation + 2);
      }
    }
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const StringMultiArrayStamped & msg, bool use_flow_style = false)
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
  const python_nodes_interfaces::msg::StringMultiArrayStamped & msg,
  std::ostream & out, size_t indentation = 0)
{
  python_nodes_interfaces::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use python_nodes_interfaces::msg::to_yaml() instead")]]
inline std::string to_yaml(const python_nodes_interfaces::msg::StringMultiArrayStamped & msg)
{
  return python_nodes_interfaces::msg::to_yaml(msg);
}

template<>
inline const char * data_type<python_nodes_interfaces::msg::StringMultiArrayStamped>()
{
  return "python_nodes_interfaces::msg::StringMultiArrayStamped";
}

template<>
inline const char * name<python_nodes_interfaces::msg::StringMultiArrayStamped>()
{
  return "python_nodes_interfaces/msg/StringMultiArrayStamped";
}

template<>
struct has_fixed_size<python_nodes_interfaces::msg::StringMultiArrayStamped>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<python_nodes_interfaces::msg::StringMultiArrayStamped>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<python_nodes_interfaces::msg::StringMultiArrayStamped>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // PYTHON_NODES_INTERFACES__MSG__DETAIL__STRING_MULTI_ARRAY_STAMPED__TRAITS_HPP_

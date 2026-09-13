// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from python_nodes_interfaces:msg/StringMultiArrayStamped.idl
// generated code does not contain a copyright notice

#ifndef PYTHON_NODES_INTERFACES__MSG__DETAIL__STRING_MULTI_ARRAY_STAMPED__STRUCT_HPP_
#define PYTHON_NODES_INTERFACES__MSG__DETAIL__STRING_MULTI_ARRAY_STAMPED__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__struct.hpp"
// Member 'layout'
#include "std_msgs/msg/detail/multi_array_layout__struct.hpp"
// Member 'action_commands'
// Member 'direction_commands'
// Member 'tertiary_commands'
#include "std_msgs/msg/detail/string__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__python_nodes_interfaces__msg__StringMultiArrayStamped __attribute__((deprecated))
#else
# define DEPRECATED__python_nodes_interfaces__msg__StringMultiArrayStamped __declspec(deprecated)
#endif

namespace python_nodes_interfaces
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct StringMultiArrayStamped_
{
  using Type = StringMultiArrayStamped_<ContainerAllocator>;

  explicit StringMultiArrayStamped_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_init),
    layout(_init)
  {
    (void)_init;
  }

  explicit StringMultiArrayStamped_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_alloc, _init),
    layout(_alloc, _init)
  {
    (void)_init;
  }

  // field types and members
  using _header_type =
    std_msgs::msg::Header_<ContainerAllocator>;
  _header_type header;
  using _layout_type =
    std_msgs::msg::MultiArrayLayout_<ContainerAllocator>;
  _layout_type layout;
  using _action_commands_type =
    std::vector<std_msgs::msg::String_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<std_msgs::msg::String_<ContainerAllocator>>>;
  _action_commands_type action_commands;
  using _direction_commands_type =
    std::vector<std_msgs::msg::String_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<std_msgs::msg::String_<ContainerAllocator>>>;
  _direction_commands_type direction_commands;
  using _tertiary_commands_type =
    std::vector<std_msgs::msg::String_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<std_msgs::msg::String_<ContainerAllocator>>>;
  _tertiary_commands_type tertiary_commands;

  // setters for named parameter idiom
  Type & set__header(
    const std_msgs::msg::Header_<ContainerAllocator> & _arg)
  {
    this->header = _arg;
    return *this;
  }
  Type & set__layout(
    const std_msgs::msg::MultiArrayLayout_<ContainerAllocator> & _arg)
  {
    this->layout = _arg;
    return *this;
  }
  Type & set__action_commands(
    const std::vector<std_msgs::msg::String_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<std_msgs::msg::String_<ContainerAllocator>>> & _arg)
  {
    this->action_commands = _arg;
    return *this;
  }
  Type & set__direction_commands(
    const std::vector<std_msgs::msg::String_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<std_msgs::msg::String_<ContainerAllocator>>> & _arg)
  {
    this->direction_commands = _arg;
    return *this;
  }
  Type & set__tertiary_commands(
    const std::vector<std_msgs::msg::String_<ContainerAllocator>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<std_msgs::msg::String_<ContainerAllocator>>> & _arg)
  {
    this->tertiary_commands = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    python_nodes_interfaces::msg::StringMultiArrayStamped_<ContainerAllocator> *;
  using ConstRawPtr =
    const python_nodes_interfaces::msg::StringMultiArrayStamped_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<python_nodes_interfaces::msg::StringMultiArrayStamped_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<python_nodes_interfaces::msg::StringMultiArrayStamped_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      python_nodes_interfaces::msg::StringMultiArrayStamped_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<python_nodes_interfaces::msg::StringMultiArrayStamped_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      python_nodes_interfaces::msg::StringMultiArrayStamped_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<python_nodes_interfaces::msg::StringMultiArrayStamped_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<python_nodes_interfaces::msg::StringMultiArrayStamped_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<python_nodes_interfaces::msg::StringMultiArrayStamped_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__python_nodes_interfaces__msg__StringMultiArrayStamped
    std::shared_ptr<python_nodes_interfaces::msg::StringMultiArrayStamped_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__python_nodes_interfaces__msg__StringMultiArrayStamped
    std::shared_ptr<python_nodes_interfaces::msg::StringMultiArrayStamped_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const StringMultiArrayStamped_ & other) const
  {
    if (this->header != other.header) {
      return false;
    }
    if (this->layout != other.layout) {
      return false;
    }
    if (this->action_commands != other.action_commands) {
      return false;
    }
    if (this->direction_commands != other.direction_commands) {
      return false;
    }
    if (this->tertiary_commands != other.tertiary_commands) {
      return false;
    }
    return true;
  }
  bool operator!=(const StringMultiArrayStamped_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct StringMultiArrayStamped_

// alias to use template instance with default allocator
using StringMultiArrayStamped =
  python_nodes_interfaces::msg::StringMultiArrayStamped_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace python_nodes_interfaces

#endif  // PYTHON_NODES_INTERFACES__MSG__DETAIL__STRING_MULTI_ARRAY_STAMPED__STRUCT_HPP_

// generated from rosidl_generator_c/resource/idl__functions.h.em
// with input from python_nodes_interfaces:msg/StringMultiArrayStamped.idl
// generated code does not contain a copyright notice

#ifndef PYTHON_NODES_INTERFACES__MSG__DETAIL__STRING_MULTI_ARRAY_STAMPED__FUNCTIONS_H_
#define PYTHON_NODES_INTERFACES__MSG__DETAIL__STRING_MULTI_ARRAY_STAMPED__FUNCTIONS_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stdlib.h>

#include "rosidl_runtime_c/visibility_control.h"
#include "python_nodes_interfaces/msg/rosidl_generator_c__visibility_control.h"

#include "python_nodes_interfaces/msg/detail/string_multi_array_stamped__struct.h"

/// Initialize msg/StringMultiArrayStamped message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * python_nodes_interfaces__msg__StringMultiArrayStamped
 * )) before or use
 * python_nodes_interfaces__msg__StringMultiArrayStamped__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_python_nodes_interfaces
bool
python_nodes_interfaces__msg__StringMultiArrayStamped__init(python_nodes_interfaces__msg__StringMultiArrayStamped * msg);

/// Finalize msg/StringMultiArrayStamped message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_python_nodes_interfaces
void
python_nodes_interfaces__msg__StringMultiArrayStamped__fini(python_nodes_interfaces__msg__StringMultiArrayStamped * msg);

/// Create msg/StringMultiArrayStamped message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * python_nodes_interfaces__msg__StringMultiArrayStamped__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_python_nodes_interfaces
python_nodes_interfaces__msg__StringMultiArrayStamped *
python_nodes_interfaces__msg__StringMultiArrayStamped__create();

/// Destroy msg/StringMultiArrayStamped message.
/**
 * It calls
 * python_nodes_interfaces__msg__StringMultiArrayStamped__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_python_nodes_interfaces
void
python_nodes_interfaces__msg__StringMultiArrayStamped__destroy(python_nodes_interfaces__msg__StringMultiArrayStamped * msg);

/// Check for msg/StringMultiArrayStamped message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_python_nodes_interfaces
bool
python_nodes_interfaces__msg__StringMultiArrayStamped__are_equal(const python_nodes_interfaces__msg__StringMultiArrayStamped * lhs, const python_nodes_interfaces__msg__StringMultiArrayStamped * rhs);

/// Copy a msg/StringMultiArrayStamped message.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source message pointer.
 * \param[out] output The target message pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer is null
 *   or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_python_nodes_interfaces
bool
python_nodes_interfaces__msg__StringMultiArrayStamped__copy(
  const python_nodes_interfaces__msg__StringMultiArrayStamped * input,
  python_nodes_interfaces__msg__StringMultiArrayStamped * output);

/// Initialize array of msg/StringMultiArrayStamped messages.
/**
 * It allocates the memory for the number of elements and calls
 * python_nodes_interfaces__msg__StringMultiArrayStamped__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_python_nodes_interfaces
bool
python_nodes_interfaces__msg__StringMultiArrayStamped__Sequence__init(python_nodes_interfaces__msg__StringMultiArrayStamped__Sequence * array, size_t size);

/// Finalize array of msg/StringMultiArrayStamped messages.
/**
 * It calls
 * python_nodes_interfaces__msg__StringMultiArrayStamped__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_python_nodes_interfaces
void
python_nodes_interfaces__msg__StringMultiArrayStamped__Sequence__fini(python_nodes_interfaces__msg__StringMultiArrayStamped__Sequence * array);

/// Create array of msg/StringMultiArrayStamped messages.
/**
 * It allocates the memory for the array and calls
 * python_nodes_interfaces__msg__StringMultiArrayStamped__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_python_nodes_interfaces
python_nodes_interfaces__msg__StringMultiArrayStamped__Sequence *
python_nodes_interfaces__msg__StringMultiArrayStamped__Sequence__create(size_t size);

/// Destroy array of msg/StringMultiArrayStamped messages.
/**
 * It calls
 * python_nodes_interfaces__msg__StringMultiArrayStamped__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_python_nodes_interfaces
void
python_nodes_interfaces__msg__StringMultiArrayStamped__Sequence__destroy(python_nodes_interfaces__msg__StringMultiArrayStamped__Sequence * array);

/// Check for msg/StringMultiArrayStamped message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_python_nodes_interfaces
bool
python_nodes_interfaces__msg__StringMultiArrayStamped__Sequence__are_equal(const python_nodes_interfaces__msg__StringMultiArrayStamped__Sequence * lhs, const python_nodes_interfaces__msg__StringMultiArrayStamped__Sequence * rhs);

/// Copy an array of msg/StringMultiArrayStamped messages.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source array pointer.
 * \param[out] output The target array pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer
 *   is null or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_python_nodes_interfaces
bool
python_nodes_interfaces__msg__StringMultiArrayStamped__Sequence__copy(
  const python_nodes_interfaces__msg__StringMultiArrayStamped__Sequence * input,
  python_nodes_interfaces__msg__StringMultiArrayStamped__Sequence * output);

#ifdef __cplusplus
}
#endif

#endif  // PYTHON_NODES_INTERFACES__MSG__DETAIL__STRING_MULTI_ARRAY_STAMPED__FUNCTIONS_H_

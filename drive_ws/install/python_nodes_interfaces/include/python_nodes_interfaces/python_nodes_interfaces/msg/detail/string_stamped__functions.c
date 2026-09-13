// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from python_nodes_interfaces:msg/StringStamped.idl
// generated code does not contain a copyright notice
#include "python_nodes_interfaces/msg/detail/string_stamped__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/detail/header__functions.h"
// Member `data`
#include "std_msgs/msg/detail/string__functions.h"

bool
python_nodes_interfaces__msg__StringStamped__init(python_nodes_interfaces__msg__StringStamped * msg)
{
  if (!msg) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__init(&msg->header)) {
    python_nodes_interfaces__msg__StringStamped__fini(msg);
    return false;
  }
  // data
  if (!std_msgs__msg__String__init(&msg->data)) {
    python_nodes_interfaces__msg__StringStamped__fini(msg);
    return false;
  }
  return true;
}

void
python_nodes_interfaces__msg__StringStamped__fini(python_nodes_interfaces__msg__StringStamped * msg)
{
  if (!msg) {
    return;
  }
  // header
  std_msgs__msg__Header__fini(&msg->header);
  // data
  std_msgs__msg__String__fini(&msg->data);
}

bool
python_nodes_interfaces__msg__StringStamped__are_equal(const python_nodes_interfaces__msg__StringStamped * lhs, const python_nodes_interfaces__msg__StringStamped * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__are_equal(
      &(lhs->header), &(rhs->header)))
  {
    return false;
  }
  // data
  if (!std_msgs__msg__String__are_equal(
      &(lhs->data), &(rhs->data)))
  {
    return false;
  }
  return true;
}

bool
python_nodes_interfaces__msg__StringStamped__copy(
  const python_nodes_interfaces__msg__StringStamped * input,
  python_nodes_interfaces__msg__StringStamped * output)
{
  if (!input || !output) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__copy(
      &(input->header), &(output->header)))
  {
    return false;
  }
  // data
  if (!std_msgs__msg__String__copy(
      &(input->data), &(output->data)))
  {
    return false;
  }
  return true;
}

python_nodes_interfaces__msg__StringStamped *
python_nodes_interfaces__msg__StringStamped__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  python_nodes_interfaces__msg__StringStamped * msg = (python_nodes_interfaces__msg__StringStamped *)allocator.allocate(sizeof(python_nodes_interfaces__msg__StringStamped), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(python_nodes_interfaces__msg__StringStamped));
  bool success = python_nodes_interfaces__msg__StringStamped__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
python_nodes_interfaces__msg__StringStamped__destroy(python_nodes_interfaces__msg__StringStamped * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    python_nodes_interfaces__msg__StringStamped__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
python_nodes_interfaces__msg__StringStamped__Sequence__init(python_nodes_interfaces__msg__StringStamped__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  python_nodes_interfaces__msg__StringStamped * data = NULL;

  if (size) {
    data = (python_nodes_interfaces__msg__StringStamped *)allocator.zero_allocate(size, sizeof(python_nodes_interfaces__msg__StringStamped), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = python_nodes_interfaces__msg__StringStamped__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        python_nodes_interfaces__msg__StringStamped__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
python_nodes_interfaces__msg__StringStamped__Sequence__fini(python_nodes_interfaces__msg__StringStamped__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      python_nodes_interfaces__msg__StringStamped__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

python_nodes_interfaces__msg__StringStamped__Sequence *
python_nodes_interfaces__msg__StringStamped__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  python_nodes_interfaces__msg__StringStamped__Sequence * array = (python_nodes_interfaces__msg__StringStamped__Sequence *)allocator.allocate(sizeof(python_nodes_interfaces__msg__StringStamped__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = python_nodes_interfaces__msg__StringStamped__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
python_nodes_interfaces__msg__StringStamped__Sequence__destroy(python_nodes_interfaces__msg__StringStamped__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    python_nodes_interfaces__msg__StringStamped__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
python_nodes_interfaces__msg__StringStamped__Sequence__are_equal(const python_nodes_interfaces__msg__StringStamped__Sequence * lhs, const python_nodes_interfaces__msg__StringStamped__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!python_nodes_interfaces__msg__StringStamped__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
python_nodes_interfaces__msg__StringStamped__Sequence__copy(
  const python_nodes_interfaces__msg__StringStamped__Sequence * input,
  python_nodes_interfaces__msg__StringStamped__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(python_nodes_interfaces__msg__StringStamped);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    python_nodes_interfaces__msg__StringStamped * data =
      (python_nodes_interfaces__msg__StringStamped *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!python_nodes_interfaces__msg__StringStamped__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          python_nodes_interfaces__msg__StringStamped__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!python_nodes_interfaces__msg__StringStamped__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}

// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from python_nodes_interfaces:msg/Float32MultiArrayStamped.idl
// generated code does not contain a copyright notice
#include "python_nodes_interfaces/msg/detail/float32_multi_array_stamped__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/detail/header__functions.h"
// Member `layout`
#include "std_msgs/msg/detail/multi_array_layout__functions.h"
// Member `data`
#include "rosidl_runtime_c/primitives_sequence_functions.h"

bool
python_nodes_interfaces__msg__Float32MultiArrayStamped__init(python_nodes_interfaces__msg__Float32MultiArrayStamped * msg)
{
  if (!msg) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__init(&msg->header)) {
    python_nodes_interfaces__msg__Float32MultiArrayStamped__fini(msg);
    return false;
  }
  // layout
  if (!std_msgs__msg__MultiArrayLayout__init(&msg->layout)) {
    python_nodes_interfaces__msg__Float32MultiArrayStamped__fini(msg);
    return false;
  }
  // data
  if (!rosidl_runtime_c__float__Sequence__init(&msg->data, 0)) {
    python_nodes_interfaces__msg__Float32MultiArrayStamped__fini(msg);
    return false;
  }
  return true;
}

void
python_nodes_interfaces__msg__Float32MultiArrayStamped__fini(python_nodes_interfaces__msg__Float32MultiArrayStamped * msg)
{
  if (!msg) {
    return;
  }
  // header
  std_msgs__msg__Header__fini(&msg->header);
  // layout
  std_msgs__msg__MultiArrayLayout__fini(&msg->layout);
  // data
  rosidl_runtime_c__float__Sequence__fini(&msg->data);
}

bool
python_nodes_interfaces__msg__Float32MultiArrayStamped__are_equal(const python_nodes_interfaces__msg__Float32MultiArrayStamped * lhs, const python_nodes_interfaces__msg__Float32MultiArrayStamped * rhs)
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
  // layout
  if (!std_msgs__msg__MultiArrayLayout__are_equal(
      &(lhs->layout), &(rhs->layout)))
  {
    return false;
  }
  // data
  if (!rosidl_runtime_c__float__Sequence__are_equal(
      &(lhs->data), &(rhs->data)))
  {
    return false;
  }
  return true;
}

bool
python_nodes_interfaces__msg__Float32MultiArrayStamped__copy(
  const python_nodes_interfaces__msg__Float32MultiArrayStamped * input,
  python_nodes_interfaces__msg__Float32MultiArrayStamped * output)
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
  // layout
  if (!std_msgs__msg__MultiArrayLayout__copy(
      &(input->layout), &(output->layout)))
  {
    return false;
  }
  // data
  if (!rosidl_runtime_c__float__Sequence__copy(
      &(input->data), &(output->data)))
  {
    return false;
  }
  return true;
}

python_nodes_interfaces__msg__Float32MultiArrayStamped *
python_nodes_interfaces__msg__Float32MultiArrayStamped__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  python_nodes_interfaces__msg__Float32MultiArrayStamped * msg = (python_nodes_interfaces__msg__Float32MultiArrayStamped *)allocator.allocate(sizeof(python_nodes_interfaces__msg__Float32MultiArrayStamped), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(python_nodes_interfaces__msg__Float32MultiArrayStamped));
  bool success = python_nodes_interfaces__msg__Float32MultiArrayStamped__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
python_nodes_interfaces__msg__Float32MultiArrayStamped__destroy(python_nodes_interfaces__msg__Float32MultiArrayStamped * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    python_nodes_interfaces__msg__Float32MultiArrayStamped__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
python_nodes_interfaces__msg__Float32MultiArrayStamped__Sequence__init(python_nodes_interfaces__msg__Float32MultiArrayStamped__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  python_nodes_interfaces__msg__Float32MultiArrayStamped * data = NULL;

  if (size) {
    data = (python_nodes_interfaces__msg__Float32MultiArrayStamped *)allocator.zero_allocate(size, sizeof(python_nodes_interfaces__msg__Float32MultiArrayStamped), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = python_nodes_interfaces__msg__Float32MultiArrayStamped__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        python_nodes_interfaces__msg__Float32MultiArrayStamped__fini(&data[i - 1]);
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
python_nodes_interfaces__msg__Float32MultiArrayStamped__Sequence__fini(python_nodes_interfaces__msg__Float32MultiArrayStamped__Sequence * array)
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
      python_nodes_interfaces__msg__Float32MultiArrayStamped__fini(&array->data[i]);
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

python_nodes_interfaces__msg__Float32MultiArrayStamped__Sequence *
python_nodes_interfaces__msg__Float32MultiArrayStamped__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  python_nodes_interfaces__msg__Float32MultiArrayStamped__Sequence * array = (python_nodes_interfaces__msg__Float32MultiArrayStamped__Sequence *)allocator.allocate(sizeof(python_nodes_interfaces__msg__Float32MultiArrayStamped__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = python_nodes_interfaces__msg__Float32MultiArrayStamped__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
python_nodes_interfaces__msg__Float32MultiArrayStamped__Sequence__destroy(python_nodes_interfaces__msg__Float32MultiArrayStamped__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    python_nodes_interfaces__msg__Float32MultiArrayStamped__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
python_nodes_interfaces__msg__Float32MultiArrayStamped__Sequence__are_equal(const python_nodes_interfaces__msg__Float32MultiArrayStamped__Sequence * lhs, const python_nodes_interfaces__msg__Float32MultiArrayStamped__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!python_nodes_interfaces__msg__Float32MultiArrayStamped__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
python_nodes_interfaces__msg__Float32MultiArrayStamped__Sequence__copy(
  const python_nodes_interfaces__msg__Float32MultiArrayStamped__Sequence * input,
  python_nodes_interfaces__msg__Float32MultiArrayStamped__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(python_nodes_interfaces__msg__Float32MultiArrayStamped);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    python_nodes_interfaces__msg__Float32MultiArrayStamped * data =
      (python_nodes_interfaces__msg__Float32MultiArrayStamped *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!python_nodes_interfaces__msg__Float32MultiArrayStamped__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          python_nodes_interfaces__msg__Float32MultiArrayStamped__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!python_nodes_interfaces__msg__Float32MultiArrayStamped__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}

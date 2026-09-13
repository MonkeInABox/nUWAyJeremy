// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from python_nodes_interfaces:msg/Float32Stamped.idl
// generated code does not contain a copyright notice
#include "python_nodes_interfaces/msg/detail/float32_stamped__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/detail/header__functions.h"

bool
python_nodes_interfaces__msg__Float32Stamped__init(python_nodes_interfaces__msg__Float32Stamped * msg)
{
  if (!msg) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__init(&msg->header)) {
    python_nodes_interfaces__msg__Float32Stamped__fini(msg);
    return false;
  }
  // data
  return true;
}

void
python_nodes_interfaces__msg__Float32Stamped__fini(python_nodes_interfaces__msg__Float32Stamped * msg)
{
  if (!msg) {
    return;
  }
  // header
  std_msgs__msg__Header__fini(&msg->header);
  // data
}

bool
python_nodes_interfaces__msg__Float32Stamped__are_equal(const python_nodes_interfaces__msg__Float32Stamped * lhs, const python_nodes_interfaces__msg__Float32Stamped * rhs)
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
  if (lhs->data != rhs->data) {
    return false;
  }
  return true;
}

bool
python_nodes_interfaces__msg__Float32Stamped__copy(
  const python_nodes_interfaces__msg__Float32Stamped * input,
  python_nodes_interfaces__msg__Float32Stamped * output)
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
  output->data = input->data;
  return true;
}

python_nodes_interfaces__msg__Float32Stamped *
python_nodes_interfaces__msg__Float32Stamped__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  python_nodes_interfaces__msg__Float32Stamped * msg = (python_nodes_interfaces__msg__Float32Stamped *)allocator.allocate(sizeof(python_nodes_interfaces__msg__Float32Stamped), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(python_nodes_interfaces__msg__Float32Stamped));
  bool success = python_nodes_interfaces__msg__Float32Stamped__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
python_nodes_interfaces__msg__Float32Stamped__destroy(python_nodes_interfaces__msg__Float32Stamped * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    python_nodes_interfaces__msg__Float32Stamped__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
python_nodes_interfaces__msg__Float32Stamped__Sequence__init(python_nodes_interfaces__msg__Float32Stamped__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  python_nodes_interfaces__msg__Float32Stamped * data = NULL;

  if (size) {
    data = (python_nodes_interfaces__msg__Float32Stamped *)allocator.zero_allocate(size, sizeof(python_nodes_interfaces__msg__Float32Stamped), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = python_nodes_interfaces__msg__Float32Stamped__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        python_nodes_interfaces__msg__Float32Stamped__fini(&data[i - 1]);
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
python_nodes_interfaces__msg__Float32Stamped__Sequence__fini(python_nodes_interfaces__msg__Float32Stamped__Sequence * array)
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
      python_nodes_interfaces__msg__Float32Stamped__fini(&array->data[i]);
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

python_nodes_interfaces__msg__Float32Stamped__Sequence *
python_nodes_interfaces__msg__Float32Stamped__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  python_nodes_interfaces__msg__Float32Stamped__Sequence * array = (python_nodes_interfaces__msg__Float32Stamped__Sequence *)allocator.allocate(sizeof(python_nodes_interfaces__msg__Float32Stamped__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = python_nodes_interfaces__msg__Float32Stamped__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
python_nodes_interfaces__msg__Float32Stamped__Sequence__destroy(python_nodes_interfaces__msg__Float32Stamped__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    python_nodes_interfaces__msg__Float32Stamped__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
python_nodes_interfaces__msg__Float32Stamped__Sequence__are_equal(const python_nodes_interfaces__msg__Float32Stamped__Sequence * lhs, const python_nodes_interfaces__msg__Float32Stamped__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!python_nodes_interfaces__msg__Float32Stamped__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
python_nodes_interfaces__msg__Float32Stamped__Sequence__copy(
  const python_nodes_interfaces__msg__Float32Stamped__Sequence * input,
  python_nodes_interfaces__msg__Float32Stamped__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(python_nodes_interfaces__msg__Float32Stamped);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    python_nodes_interfaces__msg__Float32Stamped * data =
      (python_nodes_interfaces__msg__Float32Stamped *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!python_nodes_interfaces__msg__Float32Stamped__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          python_nodes_interfaces__msg__Float32Stamped__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!python_nodes_interfaces__msg__Float32Stamped__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}

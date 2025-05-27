from django import template

register = template.Library()

@register.filter(name='get_item')
def get_item(dictionary, key):
    """Get an item from a dictionary using the key."""
    return dictionary.get(key)

@register.filter(name='get_attendance_label')
def get_attendance_label(status_code, choices):
    """Convert attendance status code to label."""
    for code, label in choices:
        if code == status_code:
            return label
    return "-"

@register.filter(name='sum_attr')
def sum_attr(obj_list, attr_name):
    """Sum a specific attribute from a list of objects."""
    total = 0
    for obj in obj_list:
        value = getattr(obj, attr_name, 0)
        if value is None:
            value = 0
        total += value
    return total

@register.filter(name='sub')
def sub(value, arg):
    """Subtract the arg from the value."""
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        try:
            return value - arg
        except Exception:
            return 0

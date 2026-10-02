# Task refactor

You wanted to add subclasses, but were initially unconvinced about moving attributes out of `Task`.

| Your concern | What we worked through | Your decision |
|---|---|---|
| **Common attributes make functions consistent across task types.** | Functions can check whether an attribute exists and what value it holds, without checking task type. | Move type-specific attributes into relevant subclasses. Functions can still work across types based on attribute state. |
| **Common attributes make storage easier.** | JSON supports objects with different fields. A mixed list keeps cross-type operations straightforward. | Keep **one mixed list**. Each class’s `to_dict()` returns applicable fields plus `"type"`; loading uses `"type"` to reconstruct the subclass. Dates serialize as ISO strings. |
| **Unused attributes make `None` ambiguous.** | `None` previously meant both “not applicable” and “not specified yet.” | Define attributes only where applicable: **absent = not applicable; `None` = unspecified; value = specified.** |

All three original concerns now have a decision.

## Approach

1. Add one child class for each task type: `DeadlineTask`, `EventTask`, `TodoTask`, and `RecurringTask`, all inheriting from `Task`.
2. Keep attributes shared across all task types in `Task`. Move task-type-specific attributes into the relevant child classes.
3. Define an attribute only for task types where it applies. Use `None` when an applicable attribute has not been specified.
4. Adapt functions that work across task types to handle missing attributes and inspect attribute values. Use `getattr(task, "attribute_name", None)` where missing and unspecified attributes should receive the same treatment.
5. Keep tasks in one mixed list.
6. Give each class a `to_dict()` method that includes common fields, applicable type-specific fields, and a `"type"` field. Serialize datetime values as ISO strings and `None` as JSON `null`; omit inapplicable fields.
7. Save the list of dictionaries as JSON. When loading, use `"type"` to reconstruct the appropriate child class and convert date strings back to datetime values.

## Note: searching by attribute state

A mixed list of task objects can be filtered by whether an attribute exists, is unspecified, or has a value, without checking task type:

```python
# Attribute exists
[t for t in tasks if hasattr(t, "start_date")]

# Attribute does not exist
[t for t in tasks if not hasattr(t, "start_date")]

# Attribute exists but is unspecified
[t for t in tasks if hasattr(t, "start_date") and t.start_date is None]

# Attribute has a value
[t for t in tasks if getattr(t, "start_date", None) is not None]
```

These examples apply to task objects in memory. For serialized dictionaries, check whether the key exists and inspect its value instead.

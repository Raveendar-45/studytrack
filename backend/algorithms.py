from typing import List, Dict, Any, Union


def insertion_sort_by_field(students: List[Dict[str, Any]], field: str) -> List[Dict[str, Any]]:
    """
    Sorts a list of student dictionaries in-place ascending by the specified field ('age' or 'name')
    using a hand-written Insertion Sort algorithm.
    Does NOT call sorted() or list.sort().
    """
    n = len(students)
    for i in range(1, n):
        key = students[i]
        j = i - 1
        # Shift elements of students[0..i-1] that are greater than key[field] to one position ahead
        while j >= 0 and students[j][field] > key[field]:
            students[j + 1] = students[j]
            j -= 1
        students[j + 1] = key
    return students


def binary_search_by_name(sorted_by_name_list: List[Dict[str, Any]], name: str) -> Union[Dict[str, Any], int]:
    """
    Performs a hand-written iterative binary search for a student by exact name match
    on an alphabetically sorted list of student dicts.
    Uses the overflow-safe midpoint formula: mid = low + (high - low) // 2.
    Returns the student dict if found, or -1 if not found.
    """
    low = 0
    high = len(sorted_by_name_list) - 1

    while low <= high:
        mid = low + (high - low) // 2
        mid_name = sorted_by_name_list[mid]["name"]

        if mid_name == name:
            return sorted_by_name_list[mid]
        elif mid_name < name:
            low = mid + 1
        else:
            high = mid - 1

    return -1


def format_roster_report(students: List[Dict[str, Any]]) -> str:
    """
    Formats a list of student dictionaries into a multi-line string report.
    Each line follows the exact format: '[Age {age}] {name} <{email}>'
    """
    lines = []
    for s in students:
        line = f"[Age {s['age']}] {s['name']} <{s['email']}>"
        lines.append(line)
    return "\n".join(lines)


def count_students_meeting_min_age(students: List[Dict[str, Any]], min_age: int) -> int:
    """
    Counts how many students have age >= min_age using an explicit loop with an accumulator variable.
    """
    count = 0
    for student in students:
        if student["age"] >= min_age:
            count += 1
    return count

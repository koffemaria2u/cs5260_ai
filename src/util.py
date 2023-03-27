import csv


def read_file(file_path, file_type):
    """
    Utility function to read various files
    """
    with open(file_path, mode='r') as file:
        csvreader = csv.DictReader(file)

        if file_type == "resource":
            file_contents = {}
            for row in csvreader:
                # Extract the resource name from the first column
                resource = row.pop('resource')

                # Convert the values to floats and store in a nested dictionary
                file_contents[resource] = {key: float(value) for key, value in row.items()}

        elif file_type == "country":
            file_contents = [convert_to_int(row) for row in csvreader]

        elif file_type == "template":
            file_contents = file.read()

    return file_contents


def convert_to_int(data_dict):
    """
    Utility function to help convert string values to integer
    """
    for key, value in data_dict.items():
        try:
            data_dict[key] = int(value)
        except ValueError:
            pass

    return data_dict


def write_file(output_file, output_string):
    """
    Utility function to write/append string to a file
    """
    output_file = open(output_file, "a")
    output_file.write(output_string)
    output_file.close()


def find_schedule_info(node, find_parent_node=False, find_successor_count=False):
    """
    Utility function to find the schedule info going UP node tree
    """
    # check if root node
    if node.parent_node is None and find_successor_count:
        return 0

    schedule_list = [node]
    next_parent_up = node.parent_node
    # as long as there is an action template on a node, insert it into the schedule list
    while next_parent_up.action is not None:
        schedule_list.insert(0, next_parent_up)
        next_parent_up = next_parent_up.parent_node

    # return the top level parent node
    if find_parent_node:
        return schedule_list[0]

    # return the total count of a node and its parents
    elif find_successor_count:
        return len(schedule_list)

    # return the full schedule list
    else:
        return schedule_list


def stringify_schedule(node, schedule_count, node_id_count, current_depth, eu_score):
    """
    Utility function to help output schedules in a string format
    """
    nodes = find_schedule_info(node)

    if len(nodes) == 0:
        return ""

    sched_string = \
        f"====================\n" \
        f"Schedule Num: {schedule_count}\n" \
        f"Node ID: {node_id_count}\n" \
        f"Depth: {current_depth}\n" \
        f"Expected Utility Score: {eu_score}\n" \
        f"====================\n"
    sched_string += "[\n"
    for i_node in nodes:
        sched_string += f"{i_node.action.strip()}\n"

    sched_string += "]\n"

    return sched_string

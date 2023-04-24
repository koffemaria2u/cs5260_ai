import csv
import matplotlib.pyplot as plt


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


def write_summary_file(output_file, best_eu_score, schedule_count, node_count, node):
    """
    Utility function to summarize the schedules on the finalized output file
    """
    # Open the file for reading
    with open(output_file, 'r') as f:
        # Read in the file contents
        file_contents = f.read()

    # Count the occurrences of 'TRANSFORM' and 'TRANSFER'
    transform_count = file_contents.count('TRANSFORM')
    transfer_count = file_contents.count('TRANSFER')
    iam_country = node.world_state.get_country(node.iam_country)

    # Prepend the counts to the file contents
    new_file_contents = f"====================\n" \
                        f"SCHEDULE SUMMARY\n" \
                        f"Country: {node.iam_country}\n" \
                        f"Best EU score: {best_eu_score}\n" \
                        f"Node count: {node_count}\n" \
                        f"Schedule count: {schedule_count}\n" \
                        f"TRANSFORM count: {transform_count}\n" \
                        f"TRANSFER count: {transfer_count}\n" \
                        f"Population: {iam_country['Population']}\n" \
                        f"Electronics: {iam_country['Electronics']}\n" \
                        f"MetallicElements: {iam_country['MetallicElements']}\n" \
                        f"MetallicAlloys: {iam_country['MetallicAlloys']}\n" \
                        f"Housing: {iam_country['Housing']}\n" \
                        f"Timber: {iam_country['Timber']}\n" \
                        f"====================\n"

    # Open the file for writing and overwrite the contents
    with open(output_file, 'a') as f:
        f.write(new_file_contents)


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

    iam_country = node.world_state.get_country(node.iam_country)
    sched_string = \
        f"====================\n" \
        f"Self Country: {node.iam_country}\n" \
        f"Schedule Num: {schedule_count}\n" \
        f"Node ID: {node_id_count}\n" \
        f"Depth: {current_depth}\n" \
        f"Expected Utility Score: {eu_score}\n" \
        f"Population: {iam_country['Population']}\n" \
        f"Electronics: {iam_country['Electronics']}\n" \
        f"MetallicElements: {iam_country['MetallicElements']}\n" \
        f"MetallicAlloys: {iam_country['MetallicAlloys']}\n" \
        f"Housing: {iam_country['Housing']}\n" \
        f"Timber: {iam_country['Timber']}\n" \
        f"====================\n"
    sched_string += "[\n"
    for i_node in nodes:
        sched_string += f"{i_node.action.strip()}\n"

    sched_string += "]\n"

    return sched_string


def plot_results(output, output_file):
    """
    FIXED 3, see notes 3
    Utility function to plot the best schedule
    """
    x = [i for i in range(len(output))]
    y = [output[i][0] for i in range(len(output))]

    plt.plot(x, y, marker='o')
    plt.xticks(range(1, len(output)+1))
    plt.title('Best EU Scores')
    plt.xlabel('Node order')
    plt.ylabel('EU score')
    fig1 = plt.gcf()
    # plt.show()
    fig1.savefig(output_file, dpi=100)

from queue import LifoQueue

# Graph represented as an adjacency list
graph = {
    'A': ['B', 'C'],
    'B': ['D', 'E'],
    'C': ['F'],
    'D': [],
    'E': ['F'],
    'F': []
}


def hdfs(graph, start, goal, heuristic):
    frontier = LifoQueue()
    frontier.put((0, start))
    visited = set()

    while not frontier.empty():
        _, vertex = frontier.get()

        if vertex == goal:
            print("Goal reached!")
            return

        visited.add(vertex)

        for neighbor in graph[vertex]:
            if neighbor not in visited:
                heuristic_value = heuristic(neighbor, goal)  # Get the heuristic value for the neighbor
                frontier.put((heuristic_value, neighbor))

    print("Goal not reachable")


def get_heuristic(current, goal):
    # In this example, we use the number of nodes between the current node and the goal node as the heuristic value
    return abs(ord(current) - ord(goal))


# Example usage
hdfs(graph, 'A', 'F', get_heuristic)

"""
backup working 4/17
            if resource_name == "Electronics":
                resource_weight = self.resource_list.get(resource_name)["weight"]
                resource_metals = iam_country["MetallicElements"]
                resource_alloys = iam_country["MetallicAlloys"]

                # perform floor division on each raw material, divide by the min amount needed to produce 1 Electronic
                # take the min of both needed to produce
                raw_materials_to_produce_electronics = min(resource_metals // 3, resource_alloys // 2)

                # reduce reward for un-built electronics, but have the raw materials to build
                discount_unbuilt_electronics = 0.5
                unbuilt_electronics_score = raw_materials_to_produce_electronics * discount_unbuilt_electronics

                # NEW FEAT: improve SQ complexity, see notes #3
                # if producing too much electronics against world population, penalize
                # assume that each person can handle/own 2 electronics at a time
                e_threshold = 1     # set to 1 for now
                electronics_per_person = 2
                electronics_population_ratio = math.ceil(iam_country["Population"] * electronics_per_person)
                if resource_amount > electronics_population_ratio:
                    # apply Electronics threshold to discourage acquiring more electronics
                    e_threshold = 0.33
                    unbuilt_electronics_score = 0

                e_sub_score = resource_weight * resource_amount * e_threshold
                pre_result = e_sub_score + unbuilt_electronics_score
                result_score += pre_result

# Test Case 1
# GAMMA = 0.95
# COST_OF_FAILURE = -5
# L = 1
# K = 1
# X_0 = 0

# ideal
GAMMA = 0.95
COST_OF_FAILURE = -10
L = 1
K = 0.001
X_0 = 5

# jf
# GAMMA = 0.95
# COST_OF_FAILURE = -10
# L = 1
# K = 0.001
# X_0 = 5

"""
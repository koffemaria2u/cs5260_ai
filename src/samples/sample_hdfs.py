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

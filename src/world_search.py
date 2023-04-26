import math
import numpy as np
import datetime
import random
from queue import PriorityQueue
from util import find_schedule_info, write_file, stringify_schedule, plot_results, write_summary_file
from base_classes import TransferTemplate, Node, TransformTemplate

# constant values for expected utility
GAMMA = 0.95
COST_OF_FAILURE = -10
L = 1
K = 0.001
X_0 = 5

"""
# Test Case 1, Part 1
GAMMA = 0.95
COST_OF_FAILURE = -5
L = 1
K = 1
X_0 = 0

# Test Case 2, Part 1
GAMMA = 0.95
COST_OF_FAILURE = -10
L = 1
K = 0.5
X_0 = 0.5
"""

CURRENT_DATETIME = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


class WorldSearch:
    def __init__(self, root_node, max_depth, resource_list, your_country_name, output_schedule_filename,
                 num_output_schedules, frontier_max_size, logger, search_type):
        self.root_node = root_node              # root/parent Node to start
        self.max_depth = max_depth              # max depth to go down the search tree
        self.resource_list = resource_list      # list of initial resources
        self.iam_country = your_country_name    # name of country the agent plays
        self.output_schedule_filename = output_schedule_filename + "_" + str(max_depth) + "depth_" + CURRENT_DATETIME + ".txt"
        self.output_schedule_plotfile = f"src/output_files/result_plots/{search_type}_{your_country_name}_" + str(max_depth) + "depth_" + CURRENT_DATETIME + ".png"
        self.frontier_max_size = frontier_max_size          # max amount of nodes on the frontier
        self.num_output_schedules = num_output_schedules    # max number of schedules
        self.logger = logger                    # logger
        self.search_type = search_type          # indicates search type to be used
        self.frontier = self.init_frontier()    # sets up the frontier
        self.best_node_eu = (0, root_node)  # to start, the best node is the root/parent node
        self.best_schedule_list = []        # keep the best schedule, used for plotting
        self.final_schedule = "["    # empty schedule string, to be populated with schedules with the best EU scores
        self.schedule_count = 1     # keeps track of the count of schedules
        self.current_depth = 1      # keeps track of the current depth of search tree
        self.successor_child_count = 0    # keeps track of the count of successor child nodes
        self.node_count_id = root_node.node_id  # keeps track of node count and use as an ID; includes root node
        # self.world_population = self.compute_world_resource("Population")   # currently unused
        # self.world_electronics = self.compute_world_resource("Electronics") # currently unused

    def compute_world_resource(self, resource_type):
        """
        Compute world population based on initial world state
            CURRENTLY NOT USED
        """
        world_resource = 0
        for country in self.root_node.world_state.country_list:
            world_resource += country[resource_type]

        return world_resource

    def init_frontier(self):
        """
        Helper function to setup the frontier depending on the search type and append init root node
            HDFS = Python built-in List
            GBFS = PriorityQueue
        """
        self.logger.info(f"Initializing frontier for search type {self.search_type}...")
        if self.search_type in ["hdfs", "bfs"]:
            frontier = [(0, self.root_node)]
        elif self.search_type == "gbfs":
            frontier = PriorityQueue()
            frontier.put((0, self.root_node))
        else:
            raise ValueError("Invalid selection search_type=%s" % self.search_type)

        return frontier

    def validate_iam_country(self, country):
        """
        Helper function to validate if a current iteration of a country is its own self.
        Useful to prevent actions on a self country that does not make sense, e.g. TRANSFER actions
        """
        if country == self.iam_country:
            return True
        else:
            return False

    def hdfs_search(self):
        """
        NEW FEAT 5
        Heuristic Depth-First Search algorithm
        To prevent searching down nodes with bad EU scores, the agent prunes the lower scored nodes and only takes
        the top 2 nodes (shuffled) to append on the frontier.
            source: https://www.youtube.com/watch?v=pcKY4hjDrxk&t=730s
        """
        visited = set()
        while (self.successor_child_count <= self.frontier_max_size or self.current_depth > self.max_depth) and self.frontier:
            # on the latest set of appended nodes, pop the last inserted node  from the frontier (LIFO)
            eu_score, current_node = self.frontier.pop()
            # print(f"{eu_score}, node_id {current_node.node_id}")

            # helps limit the depth of schedules to the max depth arg
            sched_count_depth = find_schedule_info(current_node, find_successor_count=True)
            if sched_count_depth >= self.max_depth:
                continue

            # check the current score against the best score found so far
            if current_node.iam_country == self.iam_country and current_node not in visited:
                self.evaluate_best_score(eu_score=eu_score, current_node=current_node)
            else:
                continue

            visited.add(current_node)

            # if there's no child nodes, generate successors of your current node
            child_node_successors = self.create_child_nodes(parent_node=current_node)
            self.successor_child_count += len(child_node_successors)

            # evaluate EU scores all children nodes generated
            temp_child_node_successors = []
            for child_node in child_node_successors:
                if child_node is None:
                    continue

                # calculate EU score; insert child into current node
                eu_score = self.expected_utility(child_node)
                current_node.insert_child_node(child_node)

                # append score and node to temp list
                temp_child_node_successors.append((eu_score, child_node))

                # update the current depth
                child_node_count = find_schedule_info(child_node, find_successor_count=True)
                self.current_depth = max(self.current_depth, child_node_count)

            # DO NOT USE!! introduces human intuition
            # Prune the lowest scores
            # sort highest to lowest; take best 2 scores; shuffle and insert to frontier
            # temp_child_node_successors.sort(reverse=True)
            # best_two = temp_child_node_successors[:2]
            # random.shuffle(best_two)
            # self.frontier.extend(best_two)

            random.shuffle(temp_child_node_successors)
            self.frontier.extend(temp_child_node_successors)

        plot_results(output=self.best_schedule_list, output_file=self.output_schedule_plotfile)
        write_summary_file(output_file=self.output_schedule_filename, best_eu_score=self.best_node_eu[0],
                           schedule_count=self.schedule_count, node_count=self.node_count_id, node=self.best_node_eu[1])
        self.logger.info(f"HDFS complete! Check resuls in file: {self.output_schedule_filename}")
        return self.best_node_eu, self.current_depth, self.node_count_id, self.schedule_count

    def bfs_search(self):
        """
        NEW FEAT 6
        Heuristic Depth-First Search algorithm
            source: https://www.youtube.com/watch?v=pcKY4hjDrxk&t=252s
        """
        visited = set()
        while (self.successor_child_count <= self.frontier_max_size or self.current_depth > self.max_depth) and self.frontier:
            # on the latest set of appended nodes, pop the node from the front of the frontier (FIFO)
            eu_score, current_node = self.frontier.pop(0)
            # print(f"{eu_score}, node_id {current_node.node_id}")

            # helps limit the depth of schedules to the max depth arg
            sched_count_depth = find_schedule_info(current_node, find_successor_count=True)
            if sched_count_depth >= self.max_depth:
                continue

            # check the current score against the best score found so far
            if current_node.iam_country == self.iam_country and current_node not in visited:
                self.evaluate_best_score(eu_score=eu_score, current_node=current_node)
            else:
                continue

            visited.add(current_node)

            # if there's no child nodes, generate successors of your current node
            child_node_successors = self.create_child_nodes(parent_node=current_node)
            self.successor_child_count += len(child_node_successors)

            # evaluate EU scores all children nodes generated
            temp_child_node_successors = []
            for child_node in child_node_successors:
                if child_node is None:
                    continue

                # calculate EU score; insert child into current node
                eu_score = self.expected_utility(child_node)
                current_node.insert_child_node(child_node)

                # append score and node to temp list
                temp_child_node_successors.append((eu_score, child_node))

                # update the current depth
                child_node_count = find_schedule_info(child_node, find_successor_count=True)
                self.current_depth = max(self.current_depth, child_node_count)

            random.shuffle(temp_child_node_successors)
            self.frontier.extend(temp_child_node_successors)

        plot_results(output=self.best_schedule_list, output_file=self.output_schedule_plotfile)
        write_summary_file(output_file=self.output_schedule_filename, best_eu_score=self.best_node_eu[0],
                           schedule_count=self.schedule_count, node_count=self.node_count_id, node=self.best_node_eu[1])
        self.logger.info(f"HDFS complete! Check resuls in file: {self.output_schedule_filename}")
        return self.best_node_eu, self.current_depth, self.node_count_id, self.schedule_count

    def gbfs_search(self):
        """
        Greedy Best First Search algorithm
            source: https://www.youtube.com/watch?v=dv1m3L6QXWs
        """
        # project req: end the search when the node count exceeds a max frontier size value or max depth of search space
        while self.successor_child_count <= self.frontier_max_size or self.current_depth > self.max_depth:
            eu_score, current_node = self.frontier.get()

            # using PriorityQueue, need to invert the value in order to
            # source: https://stackoverflow.com/questions/15124097/priority-queue-with-higher-priority-first-in-python
            # not converting to negative fails the program
            eu_score = -eu_score
            # print(eu_score)

            # helps limit the depth of schedules to the max depth arg
            sched_count_depth = find_schedule_info(current_node, find_successor_count=True)
            if sched_count_depth >= self.max_depth:
                continue

            # check the current score against the best score found so far
            # FIXED 1, see notes #1
            if current_node.iam_country == self.iam_country:
                self.evaluate_best_score(eu_score=eu_score, current_node=current_node)

            # start generating successors of your current node from the frontier
            child_node_successors = self.create_child_nodes(parent_node=current_node)
            self.successor_child_count += len(child_node_successors)

            # FIXED 2: randomize templates, see notes #2
            random.shuffle(child_node_successors)

            # evaluate EU scores all children nodes generated
            for child_node in child_node_successors:
                if child_node is None:
                    continue
                eu_score = self.expected_utility(child_node)

                # on PriorityQueue, need to set the score as negative priority, so it's returned first by get() method
                # source: https://stackoverflow.com/a/15124115
                self.frontier.put((-eu_score, child_node))
                current_node.insert_child_node(child_node)

                # update the current depth if needed
                child_node_count = find_schedule_info(child_node, find_successor_count=True)
                self.current_depth = max(self.current_depth, child_node_count)

        self.logger.info(f"GBFS complete! Check resuls in file: {self.output_schedule_filename}")
        plot_results(output=self.best_schedule_list, output_file=self.output_schedule_plotfile)
        write_summary_file(output_file=self.output_schedule_filename, best_eu_score=self.best_node_eu[0],
                           schedule_count=self.schedule_count, node_count=self.node_count_id, node=self.best_node_eu[1])
        return self.best_node_eu, self.current_depth, self.node_count_id, self.schedule_count

    def evaluate_best_score(self, eu_score, current_node):
        """
        Evaluate an EU score against the best score found so far;
        if best score, then write templates of all associated upstream nodes
        """
        if eu_score > self.best_node_eu[0]:
            self.logger.info(f"found higher score: {eu_score}; node_id: {current_node.node_id}; sched#: {self.schedule_count}")
            self.best_node_eu = (eu_score, current_node)
            self.best_schedule_list.append((eu_score, current_node))
            if self.schedule_count <= self.num_output_schedules:
                best_schedule = stringify_schedule(self.best_node_eu[1], self.schedule_count, self.node_count_id, self.current_depth, eu_score)
                write_file(self.output_schedule_filename, best_schedule)
            self.schedule_count += 1

    def create_child_nodes(self, parent_node):
        """
        Create children nodes from a parent node
        Create Transform and Transfer templates
        """
        # create copy of the parent's world state and its country list as master vars to make deep copies of
        world_state_parent = parent_node.world_state
        country_list = world_state_parent.country_list

        # transform template functions in TransformTemplate class
        transform_templates = ["housing", "alloy", "electronics"]

        # set return var of this function
        child_nodes = []

        # loop through each item in transform_templates, and each country in country_list
        # set possible actions according to each template
        for template in transform_templates:
            # create a set of variables to denote the current world state, country list, transform actions
            world_country_clone_transform = world_state_parent.copy_world_state()
            # FIXED 1, see notes #1; we only care about the self country, in this case NCR
            # current_country_transform = world_country_clone_transform.country_list[0] # this works
            current_country_transform = world_country_clone_transform.get_country(self.iam_country)
            action_transform = TransformTemplate(current_country_transform, template)

            # skip is there is no transform action available
            if not action_transform:
                continue

            # create and append child node to the return list var
            # includes transform template action
            self.node_count_id += 1
            child_node = Node(parent_node=parent_node,
                              world_state=world_country_clone_transform,
                              action=action_transform.transform_template,
                              your_country_name=self.iam_country,
                              node_count_id=self.node_count_id,
                              frontier_max_size=self.frontier_max_size)

            child_nodes.append(child_node)

        # only allowed to barter with raw resources
        transfer_resources = ["MetallicElements", "Timber", "MetallicAlloys",
                              # "Electronics"
                              ]

        # set a random percentage between 10% to 20% for transferring resources
        transfer_percentage = random.uniform(0.1, 0.2)

        # similar to previous loop, but for resources
        for resource in transfer_resources:
            for i in range(len(country_list)):
                # check to prevent a TRANSFER action on a country with itself
                if self.validate_iam_country(country_list[i]["Country"]):
                    continue

                # create set of variables for the current world state, country list, target country for transfer action
                world_country_clone_transfer = world_state_parent.copy_world_state()
                source_country_transfer = world_country_clone_transfer.get_country(self.iam_country)
                target_country_transfer = world_country_clone_transfer.country_list[i]

                # set random resources and values for transfer action
                source_values = round(source_country_transfer[resource] * transfer_percentage)
                target_values = round(target_country_transfer[resource] * transfer_percentage)
                random_target_resource = random.choice([x for x in transfer_resources if x != resource])

                # create transfer template class, then initiate a transfer if possible
                action_transfer = TransferTemplate(source_country=source_country_transfer,
                                                   source_resource=resource,
                                                   source_values=source_values,
                                                   target_country=target_country_transfer,
                                                   target_resource=random_target_resource,
                                                   target_values=target_values)
                if not action_transfer.init_transfer():
                    continue

                # create and child node with a successful transfer template action to the return list var
                self.node_count_id += 1
                child_node = Node(parent_node=parent_node,
                                  world_state=world_country_clone_transfer,
                                  action=action_transfer.write_transfer_template(),
                                  your_country_name=self.iam_country,
                                  node_count_id=self.node_count_id,
                                  frontier_max_size=self.frontier_max_size,
                                  transfer_target_country=target_country_transfer
                                  )
                child_nodes.append(child_node)

        # finally, return list of child nodes
        return child_nodes

    def expected_utility(self, node):
        """
        The probability that a schedule will be accepted and succeed
        Formula: EU(c_i, state_j) = (P(sch_j) * DR(c_i, sch_j)) + ((1-P(sch_j)) * C)
        English: EU of State (S) = Probability (Sch) will succeed * Discounted Reward (Sch) + ((1 - Probability (Sch) will succeed) * C)
        """
        # P(sch_j)
        sched_success_probability_result = self.schedule_success_probability(node)

        # DR(c_i, sch_j))
        discounted_reward_result = self.discounted_reward(node)

        # (P(sch_j) * DR(c_i, sch_j))
        eu_left = sched_success_probability_result * discounted_reward_result

        # ((1-P(sch_j)) * C)
        eu_right = (1 - sched_success_probability_result) * COST_OF_FAILURE

        # EU(c_i, state_j)
        expected_util_result = eu_left + eu_right

        return expected_util_result

    def schedule_success_probability(self, node):
        """
        Probability that a given country will accept a set of proposed transfers & transforms to get to specified state
        Formula: L / ( 1 + e^-k(x - x_0) )
            where:
                x_0 = value of sigmoid midpoint
                L = max value of the function
                K = affects curve steepness
        Logistic function source: https://en.wikipedia.org/wiki/Logistic_function
        """
        schedule_success_probability_result = 1
        if not node.action:
            return schedule_success_probability_result
        elif "TRANSFER" in node.action and node.transfer_target_node:
            # DR(c_i, sch_j)
            x_self = self.discounted_reward(node)
            x_target = self.discounted_reward(node.transfer_target_node)

            # P(sch_j)
            schedule_success_probability_self_country = L / 1 + np.exp(-K * (x_self - X_0))
            schedule_success_probability_target_country = L / 1 + np.exp(-K * (x_target - X_0))

            # P(sch_j)
            pre_res = schedule_success_probability_self_country * schedule_success_probability_target_country
            schedule_success_probability_result *= pre_res

        # DR(c_i, sch_j)
        x = self.discounted_reward(node)

        # P(sch_j)
        schedule_success_probability_result = L / 1 + np.exp(-K * (x - X_0))

        # print(schedule_success_probability_result)
        return schedule_success_probability_result

    def discounted_reward(self, node):
        """
        Penalize the Undiscounted Reward based on how long it takes a country to get into a specified state
        Formula: DR(c_i, sch_j) = GAMMA^N * (Q_end(c_i, sch_j) – Q_start(c_i, sch_j)), where 0 <= gamma < 1.
        """
        # Q_end(c_i, s_j) – Q_start(c_i, s_j)
        undiscounted_reward_result = self.undiscounted_reward(node)

        # GAMMA^N
        schedule_count_depth = find_schedule_info(node, find_successor_count=True)
        discounted_reward_result = (GAMMA ** schedule_count_depth)

        # DR(c_i, s_j)
        final_discounted_reward = undiscounted_reward_result * discounted_reward_result

        return final_discounted_reward

    def undiscounted_reward(self, node):
        """
        Difference between state quality of any given state for a certain country
            and the state quality for the initial state of the country.
        Formula: R(c_i, state_j) = Q_end(c_i, sch_j) – Q_start(c_i, sch_j)
        """
        # Q_start(c_i, sch_j)
        # state quality for the initial state of the country
        start_node = find_schedule_info(node, find_parent_node=True)
        state_quality_start = self.state_quality(start_node)

        # Q_end(c_i, sch_j)
        # state quality of any given state for a certain country
        state_quality_current = self.state_quality(node)

        # R(c_i, state_j)
        undiscounted_reward_final = state_quality_current - state_quality_start

        return undiscounted_reward_final

    def state_quality(self, node):
        """
        NEW FEAT 3
        State Quality goal is to produce maximum electronics given the available resources
            Measure how much electronics you currently have
            Measure how much electronics you can potentially create, given your current amount of resources available
            If producing more Electronics against country population, penalize Electronics, MetallicElements, MetallicAlloys
            if producing too much Housing against country population, penalize Housing
        """
        result_score = 0

        # State Quality is always counted against the "self" country
        iam_country = node.invoke_get_country()

        # assume that each person can handle/own 2 electronics at a time
        e_per_person = 2
        electronics_population_ratio = math.ceil(iam_country["Population"] * e_per_person)

        # assume it is optimal for 4 people to live in a single housing
        h_threshold = 1.25
        h_per_person = 4
        ideal_housing_population_ratio = math.ceil(iam_country["Population"] / h_per_person)

        for resource_name, resource_amount in iam_country.items():
            # reset this everytime because it's used by multiple resources
            e_threshold = 1.5
            # exclude from processing Country as a resource
            if resource_name == "Country":
                continue

            elif resource_name == "Housing":
                resource_weight = self.resource_list.get(resource_name)["weight"]

                # if the housing to population ratio is considered optimal, penalize
                if resource_amount > ideal_housing_population_ratio:
                    # apply Housing threshold to discourage building more housing than needed
                    h_threshold = 0.33

                h_sub_score = resource_weight * resource_amount * h_threshold
                result_score += h_sub_score

            elif resource_name == "MetallicElements":
                resource_weight = self.resource_list.get(resource_name)["weight"]

                if resource_amount > electronics_population_ratio:
                    # apply Electronics threshold to discourage acquiring more electronics
                    e_threshold = 0.33

                me_sub_score = resource_weight * resource_amount * e_threshold
                result_score += me_sub_score

            elif resource_name == "MetallicAlloys":
                resource_weight = self.resource_list.get(resource_name)["weight"]

                if resource_amount > electronics_population_ratio:
                    # apply Electronics threshold to discourage acquiring more electronics
                    e_threshold = 0.33

                ma_sub_score = resource_weight * resource_amount * e_threshold
                result_score += ma_sub_score

            elif resource_name == "Electronics":
                resource_weight = self.resource_list.get(resource_name)["weight"]
                resource_metals = iam_country["MetallicElements"]
                resource_alloys = iam_country["MetallicAlloys"]

                # perform floor division on each raw material, divide by the min amount needed to produce 1 Electronic
                # take the min of both needed to produce
                raw_materials_to_produce_electronics = min(resource_metals // 3, resource_alloys // 2)

                # reduce reward for un-built electronics, but have the raw materials to build
                discount_unbuilt_electronics = 0.5
                unbuilt_electronics_score = raw_materials_to_produce_electronics * discount_unbuilt_electronics

                # if producing too much electronics against world population, penalize
                if resource_amount > electronics_population_ratio:
                    # apply Electronics threshold to discourage acquiring more electronics
                    e_threshold = 0.33
                    unbuilt_electronics_score = 0

                e_sub_score = resource_weight * resource_amount * e_threshold
                pre_result = e_sub_score + unbuilt_electronics_score
                result_score += pre_result

            elif resource_name == "ElectronicsWaste":
                resource_weight = self.resource_list.get(resource_name)["weight"]

                # believe it or not, they recycle in the post-apocalyptic world because resources are scarce
                # assume roughly 17% of e-waste is recycled or converted to something useful
                # https://www.genevaenvironmentnetwork.org/resources/updates/the-growing-environmental-risks-of-e-waste/
                recycle_chance = 0.17
                recycled_amount = resource_amount - math.ceil(resource_amount * recycle_chance)

                ew_sub_score = resource_weight * recycled_amount

                result_score += ew_sub_score

            else:
                # Otherwise, multiply the amount of the resource by the weight
                resource_weight = self.resource_list.get(resource_name)["weight"]
                result_score += resource_weight * resource_amount

        return result_score

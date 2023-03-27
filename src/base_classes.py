from copy import deepcopy
from abc import ABC


class WorldState:
    def __init__(self, country_list):
        self.country_list = country_list    # init from csv file

    def copy_world_state(self):
        """
        Perform deepcopy of the current country_list, else updates will reference diff country_list
        Notes:
            "normal assignment operations will simply point the new variable towards the existing object"
            source: https://stackoverflow.com/a/17246744
        """
        country_list = deepcopy(self.country_list)
        return WorldState(country_list)

    def get_country(self, your_country_name):
        """
        Return the country information for the input parameter
        """
        for country in self.country_list:
            if country["Country"] == your_country_name:
                return country
            else:
                # default to return first country on list, which is usually the 'your_country_name'
                # added this as a safety, because returning None causes the program to fail on higher max depths
                return self.country_list[0]


class Node:
    def __init__(self, parent_node, world_state, action, your_country_name, node_count_id):
        self.iam_country = your_country_name    # name of country the agent plays
        self.parent_node = parent_node          # parent Node to start
        self.world_state = world_state          # instantiated WorldState class
        self.action = action                    # action to either transform or transfer
        self.child_node_list = []               # list of child nodes under current parent_node
        self.node_id = node_count_id            # keep track of the node count and use as an ID

    def __lt__(self, child_node):
        """
        Magic method to properly use PriorityQueue.put(), due to tuples in self.child_node_list are not unique.
        source: https://stackoverflow.com/a/53554555
        """
        return self.node_id < child_node.node_id

    def invoke_get_country(self):
        """
        Getter-type method to retrieve the country self from the instantiated WorldState class
        """
        return self.world_state.get_country(self.iam_country)

    def insert_child_node(self, child_node):
        """
        Helper method to insert child node into list
        """
        self.child_node_list.append(child_node)


class ActionHelper(ABC):
    def __init__(self):
        self.source_country = None

    def validate_resources(self, country_resource_info, resource_input_template):
        """
        Utility method used to validate the number of resources
        """
        for key, value in resource_input_template.items():
            if country_resource_info[key] < value or value == 0:
                return False
        return True

    def modify_resource_values(self, country_resource_info, mod_value_template, transfer=False, source=False):
        """
        Utility action method used to manipulate resources on for a given template
        """
        if not transfer:
            # used for TRANSFORM templates
            for resource_name, resource_value in mod_value_template.items():
                country_resource_info[resource_name] += resource_value

        else:
            # used for TRANSFER templates
            if source:
                # specifically for the source country
                for resource_name, resource_value in mod_value_template["source"].items():
                    country_resource_info[resource_name] += resource_value
            else:
                # specifically for the target country
                for resource_name, resource_value in mod_value_template["target"].items():
                    country_resource_info[resource_name] += resource_value


class TransferTemplate(ActionHelper):
    def __init__(self, source_country, source_resource, source_values, target_country, target_resource, target_values):
        super().__init__()
        self.source_country = source_country
        self.source_resource = source_resource
        self.source_values = source_values
        self.target_country = target_country
        self.target_resource = target_resource
        self.target_values = target_values

    def write_transfer_template(self):
        """
        Write the transfer template to a string for the Schedule
        """
        transfer_template = f"""
(TRANSFER BETWEEN {self.source_country["Country"]} and {self.target_country["Country"]} 
    ({self.source_country["Country"]} acquired {self.target_resource} {self.target_values}
    {self.target_country["Country"]} acquired {self.source_resource} {self.source_values})
)
"""

        return transfer_template

    def init_transfer(self):
        """
        Initiate a transfer of selected resources between source and target countries
        """

        # check if both source and target countries have resources to trade
        if not self.validate_resources(self.source_country, {self.source_resource: self.source_values}):
            return False
        if not self.validate_resources(self.target_country, {self.target_resource: self.target_values}):
            return False

        if not self.check_resource_balance():
            return False

        # template the source and target items for easier transfers
        # notice negative placements to reduce values in exchange for increased values on source/target combinations
        mod_value_template = {"source": {self.source_resource: -self.source_values,
                                         self.target_resource: self.target_values},
                              "target": {self.source_resource: self.source_values,
                                         self.target_resource: -self.target_values}}

        # add/subtract resources from source and target countries
        self.modify_resource_values(self.source_country, mod_value_template, transfer=True, source=True)
        self.modify_resource_values(self.target_country, mod_value_template, transfer=True, source=False)

        return True

    def check_resource_balance(self):
        """
        Check if resource transfer amounts are balanced between source and target, else risk unfair transfers
        """
        if self.source_values >= (self.target_values * 2) or self.target_values > (self.source_values * 2):
            return False
        else:
            return True


class TransformTemplate(ActionHelper):
    def __init__(self, country_resource_info, transform_template):
        super().__init__()
        self.country_resource_info = country_resource_info
        self.transform_template = self.set_template(transform_template)

    def set_template(self, transform_template_choice):
        """
        helper function to invoke the proper template function based on the input parameter
        """
        if transform_template_choice == "housing":
            return self.housing_template()

        elif transform_template_choice == "alloy":
            return self.alloy_template()

        elif transform_template_choice == "electronics":
            return self.electronics_template()

    def housing_template(self):
        """
        Base housing template taken from project requirements
        """
        # static templates to help transformation; based on project reqs
        resource_input_template = {"Population": 5, "MetallicElements": 1, "Timber": 5, "MetallicAlloys": 3}
        mod_value_template = {"MetallicElements": -1, "Timber": -5, "MetallicAlloys": -3, "Housing": 1, "HousingWaste": 1}

        # check if the country has enough resources to transform
        if not self.validate_resources(self.country_resource_info, resource_input_template):
            return None

        # if enough resources, then apply the transform
        self.modify_resource_values(self.country_resource_info, mod_value_template)

        # I elected to use simple f-strings here as it was the easiest to manipulate.
        # I had attempted to use John Ford's template code he posted on Piazza but was having trouble parsing them out.
        template_result = f"""
(TRANSFORM Housing {self.country_resource_info["Country"]}
    (INPUTS  (Population 5)
             (Metallic Elements 1)
             (Timber 5)
             (Metallic Alloys 3)
    )
    (OUTPUTS (Housing 1)
             (Housing Waste 1)
    )
)
"""

        return template_result

    def alloy_template(self):
        """
        Base alloy template taken from project requirements
        """
        resource_input_template = {"Population": 1, "MetallicElements": 2}
        mod_value_template = {"MetallicElements": -2, "MetallicAlloys": 1, "MetallicAlloysWaste": 1}
        if not self.validate_resources(self.country_resource_info, resource_input_template):
            return None

        self.modify_resource_values(self.country_resource_info, mod_value_template)

        template_result = f"""
(TRANSFORM Alloy {self.country_resource_info["Country"]}
    (INPUTS  (Population 1)
             (Metallic Elements 2)
    )
    (OUTPUTS (Metallic Alloys 1)
             (Metallic Alloys Waste 1)
    )
)
"""

        return template_result

    def electronics_template(self):
        """
        Base electronics template taken from project requirements
        """
        resource_input_template = {"Population": 1, "MetallicElements": 3, "MetallicAlloys": 2}
        mod_value_template = {"MetallicElements": -3, "MetallicAlloys": -2, "Electronics": 2, "ElectronicsWaste": 1}

        if not self.validate_resources(self.country_resource_info, resource_input_template):
            return None

        self.modify_resource_values(self.country_resource_info, mod_value_template)

        template_result = f"""
(TRANSFORM Electronics {self.country_resource_info["Country"]}
    (INPUTS  (Population 1)
             (Metallic Elements 3)
             (Metallic Alloys 2)
    )
    (OUTPUTS (Electronics 2)
             (ElectronicsWaste 1)
    )
)
"""
        return template_result

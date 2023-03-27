import logging
import argparse
from base_classes import WorldState, Node
from bfs import WorldSearch
from util import read_file, stringify_schedule


def country_scheduler(your_country_name, resources_filename, initial_state_filename, output_schedule_filename,
                      num_output_schedules, depth_bound, frontier_max_size, logger):

    logger.info("Reading csv files...")
    country_list = read_file(file_path=initial_state_filename, file_type="country")
    resource_list = read_file(file_path=resources_filename, file_type="resource")

    logger.info(f"Initializing World State countries from file: \n {country_list} ")
    world_state = WorldState(country_list=country_list)

    logger.info(f"Initializing root Node of country: {your_country_name}")
    my_country = Node(your_country_name=your_country_name,
                      parent_node=None,
                      world_state=world_state,
                      action=None,
                      node_count_id=1)

    logger.info(f"Initializing WorldSearch class...")
    world_search = WorldSearch(root_node=my_country, max_depth=depth_bound,
                               resource_list=resource_list, your_country_name=your_country_name,
                               output_schedule_filename=output_schedule_filename,
                               num_output_schedules=num_output_schedules,
                               frontier_max_size=frontier_max_size, logger=logger)

    logger.info(f"Initializing WorldSearch of country: {your_country_name}")
    best_node_eu, current_depth, node_count_id, schedule_count = world_search.bfs_search()

    best_schedule = stringify_schedule(best_node_eu[1], schedule_count, node_count_id, current_depth, best_node_eu[0])
    logger.info(f"\n Best EU score: {best_node_eu[0]} "
                f"\n Node ID: {node_count_id}"
                f"\n Best schedule: {best_schedule}")

    logger.info("Country Scheduler successfully completed!")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--country-self', '-c', type=str, default="NewCaliforniaRepublic", help='init country to start')
    parser.add_argument('--resource-file', '-r', type=str, default="src/input_files/world_resources_1.csv",
                        help='init resource csv filepath')
    parser.add_argument('--state-file', '-s', type=str, default="src/input_files/world_state_1.csv",
                        help='init state country csv filepath')
    parser.add_argument('--output-file', '-o', type=str, default="src/output_files/bfs_results",
                        help='output textfile filepath')
    parser.add_argument('--num-schedules', '-ns', type=int, required=False, default=10,
                        help='expected num of output schedules to limit search space; not implemented yet')
    parser.add_argument('--depth-bound', '-d', type=int, required=False, default=20,
                        help='expected max depth of tree to limit search space')
    parser.add_argument('--frontier-size', '-f', type=int, required=False, default=15000,
                        help='expected max frontier size of queue to limit search space; not implemented')
    parser.add_argument("--loglevel", "-l", action="store", default="INFO", help="logging level")

    args = parser.parse_args()
    logging.basicConfig(format='%(asctime)s %(levelname)s %(funcName)s:%(lineno)d %(message)s', level="INFO")
    logger = logging.getLogger("CountryScheduler main")

    # main driver function
    country_scheduler(your_country_name=args.country_self,
                      resources_filename=args.resource_file,
                      initial_state_filename=args.state_file,
                      output_schedule_filename=args.output_file,
                      num_output_schedules=args.num_schedules,
                      depth_bound=args.depth_bound,
                      frontier_max_size=args.frontier_size,
                      logger=logger)


if __name__ == '__main__':
    exit(main())

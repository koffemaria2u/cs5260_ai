# cs5260_ai

## Requirements
- must use csv files to load resources
- use singleton transfer for part 1 only
  - treat transfer options as if transfering one at a time
  - transfer one good at a time
- state quality function
  - heuristic to decide how good/bad a state is
  - state - # of resources a country has
- resource utility weighing
  - resource weights on how a country values it state quality
  - for part 1, all resource weights are static and shared by all countries

- expected utility
  - aka evaluation value, or f-value
  - how and what order items are added to frontier in various search strategies
  - follows directly from state quality function and resource utility weights
  - reward country receives by getting into its target state

- undiscounted reward function
  - diff between state quality (of any given state of a country) and the initial state quality of the country
    - `state_quality_future` - `initial_state_quality`
- discounted reward function
  - penalize undiscounted reward based on how long it takes for a country to get into its specified state
  - to-do play around with gamma value in formula

- country accept probability
  - probability that a different country will accept the cumulative set of transfers proposed to it
  - uses `logistic function` formula
    - to-do play with vals `k`, `x`
  - involves individual country will accept transfer proposal by another country

- schedule success probability
  - probability that all countries will accept the whole set of schedule ()
  - combines all results in a single probability that the schedule will succeed
    - 

- input csv files
  - all manufactured resources must have values of 0 to start
  - only raw resources will have values to start

- output must be csv text file containing:
  - sequence of **grounded** transfer and transform ops
    - grounded - no variables remaining, only constants parsed out

- top level func `country_scheduler`
  - `depth_bound` param - dictates how many ops agent is searching for in the schedule


### Suggestions for getting started
- Decide on a State Quality function for your agent
- Create your State representation in code
- Come up with your initial listing of all available resources, weights, and the initial world state
- Write code to calculate the State Quality, rewards, and success probabilities for a given country and schedule
- Write code to calculate the Expected Utility of a given schedule
- Write code to parse TRANSFORM operators into Actions in your code
- Write code to expand a current State into a set of possible next States given a set of possible Actions (along with their prerequisites)
- Fine-tune your code
    - Pre-shrink any variable domains using the GAC algorithm 
    - Implement different search strategies
    - Add more resources and/or transformation operators
    - Play with the Expected Utility gamma, k, and x0 values
    - Try sorting any priority queues on different values
- Don’t create too many countries or resources initially 
    - Increases branching factor
- Carefully read through the Programming Project section entitled “Search Strategy” for more explicit suggestions for getting started on Part 1
- Ignore the “Deliverables” section for now
- Take a look at my sample Python code base on GitHub for ideas of how to get started implementing different search strategies in a generalized fashion



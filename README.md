# CS 5260 - Artificial Intelligence
This repository contains the Project requirements for Artificial Intelligence class in Spring 2023 for the 
MS. of Computer Science program of Vanderbilt University.

by: Kevin Offemaria


## Project Requirements
The project requirements and relevant information are found in the directory: 
[project_reqs](project_reqs).

For the required project submission documents, see dir: [submission_files](submission_files).
- `test_cases_summary.pdf`
- `talk_slides.pptx`
- `video_link.txt`

## Usage
### Installation
To install the project requirements:

```bash
# install python virtual environment
pyenv virtualenv 3.10.1 venv_name
pyenv activate venv_name

# install reqs file
pip install -r requirements.txt
```

### Running the Program
The main program is the `country_scheduler.py`. Many of the arguments have default values, so you may invoke the module
without passing any parameters.
Run this from the top level directory as follows:

```bash
# run with default args
python src/country_scheduler.py

# run with custom args
python src/country_scheduler.py 
  --country-self NewCaliforniaRepublic 
  --resource-file src/input_files/world_resources_1.csv
  --state-file src/input_files/world_state_1.csv
  --output-file src/output_files/bfs_results
  --num-schedules 10
  --depth-bound 10
  --frontier-size 5000
  --loglevel INFO
```

## Around the repo
1. Test Results are found in the [output_files](src/output_files)
   - The last few characters of the file name indicate the test case and iteration (eg. `bfs_res...test1a.txt`)
2. Initial states are found in [input_files](src/input_files)


## Presentation Notes
1. At first, I embedded the `ActionTransfer` functions (now a class) into the WorldSearch. But realized it could be too
tightly coupled, and figured I could use this on its own somehow on Part 2 of the project.
2. Adding a hardcoded transfer percentage of up to 20% of resources
   - this would cause uneven trades if 1 resource is much higher than the other
   - to balance, add a check that resources for transfer shouldn't be > 200% both ways
3. higher COST_OF_FAILURE lead to finding_best nodes in deeper depths

### Notes
Logical function variables:
- `x` is the input or independent variable
- `L` is the maximum value of the function
- `k` is the steepness of the curve
- `x_0` is the x-value of the sigmoid's midpoint

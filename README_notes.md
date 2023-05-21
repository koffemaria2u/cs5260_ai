# Kevin's Notes
### Project Part 1 Feedback
1. Somewhat simplistic state quality function, but I love that you are including recycling to offset the creation of waste

2. You are weighting electronics heavily and then weighting things used to produce electronics slightly less with the 
purpose of encoding that we need alloys to create electronics <- this is human intuition that is not needed in AI...
if your "good state" (as determined by your state quality function) involves having lots of electronics, your AI should 
automatically find schedules that allow you to produce those electronics

3. If you are implementing Breadth-First Search, then you can't be using a Priority Queue <- 
I think you may have implemented Greedy Best-First Search instead.

4. I love your initial state being based on Fallout 2...very creative idea!

5. I like that you include the number of nodes visited as a statistic in your Node ID...neat way to visualize how many
nodes had to be traversed to find a schedule

6. Test 1 Results: You say that in some of the runs, you only reached a depth of 10...do you mean the schedule with the 
best EU was FOUND at a depth of 10, or your algorithm only searched to a depth of 10, presumably because your frontier ran out of space?

7. For the next part, I would definitely move away from anything breadth-first related, as (I think you've seen), 
the search space gets very large very quickly and doesn't allow you to go very deep to find better solutions.

8. I also see that you are inverting your EU values, presumably because they are negative. If they are negative, 
I would debug that calculation, since EU should be positive (and hopefully increasing over time).
   - this is incorrect, I'm flipping the values because the PQ's `get()` method returns the lowest value which is what
   we want for GBFS implementation


### Project Part 2 Proposal
1. No programmatic improvements are graded. But can if I fix some aspects based on the feedback from part 1, 
  will that be included in grading part 2? how significantly?
  - [x] fix or not use priority queue, for using BFS
    - BFS traverses the frontier in the order that you've added items to the frontier FIFO
    - a PriorityQueue will always reorder items in the frontier anytime an item is added
  - [x] removing human intuition from state quality
    - resource weighting influencing agent towards Electronics and its raw materials
  - [x] fix EU values in GBFS, inverting negative values
    - this is correct, nothing to change 
    - GBFS selects the node with the HIGHEST heuristic value from the priority queue and expands it, adding its
    neighboring nodes to the priority queue in order of their heuristic values 
    - [video explanation](https://www.youtube.com/watch?v=dv1m3L6QXWs)
  - [x] randomize EU evaluation of templates
  - [x] add graphs/plots
  - [x] 6 test cases
    - [x] use NCR; w/ GBFS and HDFS and BFS
      - moderate resources, 
      - high electronics/housing to population ratio (higher state quality to start)
      - generally more transfers
    - [x] use Arroyo; w/ GBFS and HDFS and BFS
      - extremely high resources, 
      - low electronics/housing to population ratio (lower state quality to start)
      - generally more transforms

2. new features:
   - [x] NEW FEAT 1 
     - add more uncertainty on templated actions
     - "random encounters" during TRANSFERs, possibly getting hijacked of resources
     - [source](https://fallout.fandom.com/wiki/Fallout_2_random_encounters)
   - [x] NEW FEAT 2 On Transforms
     - [x] Recycling would not only reduce waste, but also increase raw materials by reusing working electronic parts from the waste
   - [x] NEW FEAT 3 increase SQ complexity 
     - [x] if producing more Electronics against country population, penalize Electronics, MetallicElements, MetallicAlloys
     - [x] if producing too much Housing against country population, penalize Housing
   - [x] NEW FEAT 4 add entropy or decaying of resources
     - this would introduce maintenance of Electronics, maybe
     - Deterioration rates
       - Metals [1% - 5% corrosion rate](https://xapps.xyleminc.com/Crest.Grindex/help/grindex/contents/Metals.htm)
       - Timber [20% decay rate](https://www.fs.usda.gov/research/treesearch/7717)
     - every 3000 nodes
   - [x] NEW FEAT 5 - implement HDFS
     - make note of the limitations you are seeing with HDFS and report on your findings
   - [x] NEW FEAT 6 - implement BFS

3. deliverables:
   - [] TalkSlides.pptx: PowerPoint slides to accompany your video
   - [] VideoLink.txt: Text file containing a link to your narrative video (e.g., a private link on YouTube or a link to 
   a Zoom recording of no more than 15 minutes). The bulk of your Part 2 grade will be based on the video and slides, 
   with expected content to include:
     - [x] A figure and explanation of the comprehensive architectural design of your system, 
     - [x] A focus on any improvements, additions, changes, or expansions that you made since Part 1, 
     - [x] Summaries of experimental studies, including explanations of selected test cases, graphs, and tables,
     - [x] Comparisons between the results of your Part 1 and Part 2 outputs, including the quality of the resulting 
          schedules, the speed or efficiency of your algorithms, and the complexity of the resulting outputs, 
     - [x] Citations to outside sources that you used, including references to other students.
   - [] SourceCode.zip: well-documented and well-formatted code, including:
     - [x] README: Containing clear and detailed directions for running your code and identifying the file containing the country scheduler function, and any other important top-level functions.
     - You will also be graded on the documentation and format of the entirety of Part 1 and Part 2 code.



### Notes for Part 2
1. found bug on func `create_child_nodes()` 
   - the Transform template was doing unnecessary looping for all countries, but we only care about Transforms of the `self.country = NCR` 
   - as a result on `evaluate_best_score()`, we only need to evaluate the EU score of our own self country
2. randomize EU evaluation of templates
   - remove Electronics as barter resource
3. plot results function
4. stabilize resource weights
5. 6 test cases
6. increase SQ complexity 
   - if producing more Electronics against country population, penalize Electronics, MetallicElements, MetallicAlloys
     - separate calculation
   - if producing too much Housing against country population, penalize Housing
7. add random encounters on Transfers
8. add recycle chance on Transforms
9. add plot of EU best scores
10. Fix GBFS, remove BFS
11. Implement HDFS
    - w/ reached
    - dfs forces the search to go down the leftmost branch whether it's a good schedule or not 
    - it sets the standard for what is "good" then as it travels slowly to the right
    - at the end of each iteration before appending the nodes to the `self.frontier`, I'm sorting the new child nodes in ascending order.
    - This forces the next `self.frontier.pop()` to take the last node with highest EU score
12. add resource decay
    - i noticed that there are more transfers to keep decay at bay
13. bfs
    - calculate EU
    - use built-in python list
14. test case 1, 
    - GBFS, 
    - -ns 20, 
    - -d 20, 
    - -f 10000
    - NCR
15. test case 2
    - GBFS, 
    - -ns 20, 
    - -d 20, 
    - -f 10000
    - Arroyo
16. test case 3, 
    - HDFS, 
    - -ns 20, 
    - -d 5, 
    - -f 20000
    - NCR
17. test case 4, 
    - HDFS, 
    - -ns 20, 
    - -d 5, 
    - -f 20000
    - Arroyo
18. test case 5, 
    - BFS, 
    - -ns 20, 
    - -d 10, 
    - -f 50000
    - NCR
19. test case 6, 
    - BFS, 
    - -ns 20, 
    - -d 10, 
    - -f 50000
    - Arroyo
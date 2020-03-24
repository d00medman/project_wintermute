# Project Wintermute
#### Reinforcement learning applied to Role Playing Video games

The formalization of moral decision making is the most important scientific question facing mankind. Should we induce an intelligence explosion without having done so, the existential risk to the Homo Sapien is disconcertingly high. Last October, it dawned on me that many modern role playing video games (RPGs) require the player to make moral decisions. It follows that an agent capable of playing games would provide invaluable data about the moral decision making of machines. I began to work on project Wintermute to pursue this insight. 

Project Wintermute’s goal is to produce a Reinforcement Learning (RL) agent capable of playing the seminal 1988 RPG Final Fantasy. While Final Fantasy has a linear narrative, and thus no opportunity for moral decision making (the emulator technology needed to pursue such games simply does not exist at present), it is a highly complicated problem space. Producing agents to handle this space will require the same elements of high cognition which I believe play a critical role in moral decision making.

At present, I have made progress in prototyping a navigation and perception system (dubbed Ulysses and Melete, respectively). The Ulysses prototype uses Sutton and Barto's offline Q-learning to derive and navate path to a denoted, visible objective. I then turned my attention to prototyping Melete by building a Google Cloud training pipeline for a Deep Convolutional Autoencoder (DCEC, a state of the art unsupervised clustering algorithm). When integrated, Melete will be responsible for denoting which agent (Ulysses or Achilles, the combat system) should select an action for a given observation.

Upon completion of the Melete pipeline, I turned my attention to upgrading Ulysses. This upgrade consists of creating an online Q-Learning algorithm for a [Partially Observable Markov Decision Process (POMDP)](https://en.wikipedia.org/wiki/Partially_observable_Markov_decision_process). At the time of writing, I have mostly been intensively studying academic literature in search of the best approach to this problem. Moving forward, I will be using [Ray-Rllib](https://ray.readthedocs.io/en/latest/rllib.html) library’s implementation of [Horgan's Ape-X Distributed Deep-Q Network](https://arxiv.org/abs/1803.00933). My next steps at time of writing (3/3/2020) will thus be to bring the agent online with one actor and learner, then expand it to accommodate n actors and run it on the cloud.Once this is done, I plan on upgrading the agent's topology and training process to approximate Kapturowski's (amazingly named) [R2D2](https://openreview.net/forum?id=r1lyTjAqYX).

Once I have sucessfully upgraded Ulysses, I will seek to integrate it with Melete and begin work on the Achilles combat system. At present, I little beyond the notion that it will be a modified version of AlphaZero. This will allow Project Wintermute to complete my primary near-term goal; the ability to successfully complete the first quest line in the game. From there, I will need to expand the system to handle inventory management, a problem I have not yet considered. Once this is done, I will have a system capable of handling most quests in the game.

That is the point where things become interesting. During Wintermute's development, each quest will be manually marked with a reward point. My interest is in developing an agent capable of accumulating information from the game (mostly done by speaking with NPCs) and assessing where the reward should lie. Such a system would be more or less entirely without precedent, and the intellectual challenge it represents is tantalizing. I have dubbed this Project Neuromancer. 

I am very proud of my work on this project thus far. I have been able to, with very little assistance, derive a fairly robust knowledge of the modern AI landscape. Furthermore, I have done so while pursuing groundbreaking research into a sector of science critical to the future of humanity. 
    
## Ulysses - Navigation subsystem

Named for the Hero who wandered to the corners of the earth. Used his Latin name because it had a nice symmetry with Achilles

##### Overview as of 1/9/2020

Going to give an overview of the state of the Ulysses prototype system. As of writing, I am ~98% of the way towards a terminal point in the prototype. There is some outstanding work,
which I will detail later. The goal of this exercise is to, as clearly as possible, define the current scope of the Wintermute system. This will give me precise definitions of the limits 
of the system, which will in turn allow me to ponder solutions.
    First, the system must be set up. The steps to do this are as follows:
    
1. Activate the Nintaco emulator. This is done via a command line `java -jar Nintaco.jar` in the proper directory (I have a bash alias to do this globally)
2. Load the Final Fantasy file, then load the `prototype_trial_start_point.save`.
3. Enable the program server. Thus far, I am uncertain if this can be done programatically or needs to feed through the GUI. This step has been one of the biggest
   conceptual blocks in efforts to streamline the startup process.
4. Open a second terminal window, go to the `wintermute_prototype/nes_environment` directory and run `python nes_environment.py` to enable the System which communicates between the 
   Emulator and the agent system
5. Open a third terminal window, go to the root of the file and run `source wintermute_prototype_venv/bin/activate` to activate a python 3 venv,
   go to the `wintermute_prototype/wintermute_amalgam` directory and run `python3 communication_nexus.py` to enable the agent system.
6. Open a fourth terminal window (my practice here is to open a new tab in the window which is running Nintaco. For all intents and purposes, this is the same thing),
   run `su -l kafka` to log into the kafka command line. In this command line, run `echo "kickstart" | ~/kafka/bin/kafka-console-producer.sh --broker-list localhost:9092 --topic amalgam_to_emulator > /dev/null`
   This command will run the Ulysses prototype
   
At present, there are a lot of moving parts involved in the setup, but not so many that a streamlined process is entirely needed. I am of the opinion
That this is an excellent use case for docker. That said, this case is very complicated, and I am fairly green with Docker. I am running numerous systems which run
in different languages and each needs to be set up differently to play nice with others. Most concerningly, if there is no way to launch the project server sans GUI 
interaction, it is out and out not possible to place that section of the process in a container. I am unsure of what the implications of this would be. This requires
expert advice as well as studying. I have purchased some books on Docker to this end. As the system grows more and more complex, quickstart measures will be needed.
That said, in the current standalone situation, it is not a primary concern, making the scope of the problem out of proportion to the necessity of attacking it.

The system itself is spread across the `nes_environment` and `wintermute_amalgam` directories. The former contains a python 2.7 script which acts as a channel of communication
between the Agent and the actual running emulator. The latter contains the code which makes up the agent. `nes_environment.py` contains a kafka consumer which reads from the topic `amalgam_to_emulator`.
It is also equipped with a kafka producer. Adjacent to the file is the python `nintaco.py` API code, which is more or less unmodified. This API was originally implemented in java and thus
has some design decisions which reflect this. `nes_environment.py` first starts a nintaco API, then waits to recieve messages from `amalgam_to_emulator`. The API's core vector for interaction is the callback
`renderFinished` which is called once per frame. As this frequency of action is mentally unmanageable, I implemented logic to throttle the frequency at which action is taken (defaulting to once per second).
When the emulator takes action, it first checks if it has a `navigation_plan`. If it does, it pops and executes the first action in the plan. If it does not, it runs `listen`, which listens for messages
on `amalgam_to_emulator`. On initialization, we send the kickstart message to this topic. This will cause the environment to send a 1D list of all the pixels on screen to the agent. Non kickstart messages
received afterward are from the agent. These messages contain an action plan. The environment takes this message, performs some simple normalizations on this and sets it as its action plan. It then proceeds to execute
The action plan. At present, the agent in the successful case actually sends more actions than necessary, but this is indicative of a shortcoming in the agent system rather than anything in the environment.
    
The Agent itself is started by running a `communication_nexus.py`. This nexus is very similar to the `nes_environment.py` in that it contains a kafka producer and a consumer which recieves messages from the topic `emulator_to_amalgam`
unlike the `nes_environment.py`, `communication_nexus.py` hosts an instance of `ulysses.py`, the code for the navigation agent. This agent is initialized when the communication nexus is instantiated. This agent is initialzied with its
baseline hyperparameters and action set. When `nes_environment.py` sends a message to `emulator_to_amalgam`, `communication_nexus.py` decodes the message, then passes the list to the `pixel_grid_builder`. This file contains three free-floating
methods (two in practice, as one of the three is a helper method). First, we run `create_pixel_grid`, which formats the string as a 15x13 matrix where each entry is a 16x16 matrix of pixel color values. This replicates the screen. We then run
`reduce_grid`, which outputs a 15x13 matrix whose entries are the most common scalar value in each of the 16x16 entries of the whole screen representation. Once this representation has been produced, it is passed to the `q_learn_environment`
method of the agent.

`q_learn_environment` first creates a `FinalFantasyGridWorld`, which is an extension of a more generic `gridworld.py` I built on top of the discrete environment from the open AI gym.
Gridworld is initialized by assigning each visible state a scalar value. The grid then generates a set of transition tuples for each state-action pair. Each tuple has a scalar next state,
the terminality of said next state, the reward present at the next state, and a probability value of one, whose purpose is unclear to me. Terminal state is set to a specific scalar state.
The scalar next states are determined by defining movement rules within the environment. In the default `gridworld.py`, movement is unrestricted (though attempts to move off the edge) will result
in a next state scalar identical to the current state) and the terminal point is defined with a scalar state ID. In the final fantasy gridworld, this restriction holds and is extended to also
take effect when the next action would take the player character into an impassible tile (strictly a tile with a scalar value indicating blue is the most common color i.e a water tile). The scalar value
of 16 only appears once in the Shrine of Fiends representation used to build the prototype. This was thus set as the terminal point. Both classes also include a render functionality which present the reward,
terminal states and all other states. The final fantasy gridworld uses characters which correspond to the scalar values of the representation.

Once the environment has been set up, the agent executes `learn_q`, an implementation of Sutton and Barto's Q learning algorithm. In its default setting, the agent has 1000 episodes, each of which
is 250 steps in length. These 250K steps are used to learn the state value function (Q) of the environment. At the start of each episode, `epsilon_greedy_action_selection` selects an action. At each other
step, we select the action with the highest Q value. At each step, we update the Q value for the state action tuple to reflect new information learned about it. After all episodes are run, we return and set
the Q value to the agent. The agent then executes `get_q_plan`. This has the agent return a plan of actions which will get the agent to the reward (with a maximum length of 20). In the context of the prototype,
these specifications are met and the action plan can be executed in less than 20 moves. We then increment each action by 4 (to reflect their button values in the emulator. I have tried to make these two scalar sets
match, but have found that the nature of the argmax function makes the ex-post facto incrementation necessary without further investigation). This action plan is then encoded as json and written to `amalgam_to_emulator`;
and its execution has already been detailed.

## Melete - Perception subsystem - Prototype

Named for the Muse whose name means "ponder", as pondering is the crux of her nature.

##### Overview as of 1/17/2020

The Melete process is more or less complete in its outline at this point. Data is streamed from the NES emulator to a kafka topic. At a given point in time, I will spin up the control
system to take all the messages and write them to a CSV file. A model is then built, trained and saved. When the standard two way emulator-agent communication channel is set up, now
have the ability to spin up an instance of Melete, which can assess the class of the state. All of this is procedurally rough; need to move to smooth the process out. Also of note is
the fact that the Melete CNN model almost certainly does not work. This was intentional, I wanted to spin the procedure up around her first and put a rough black box CNN in place.

Now comes the process of optimizing both the model pipeline and the model's construction itself.  
# Project Wintermute - prototype

## 12/27/19

  Porting old README to this repo. Only has one other entry, but might as well keep all notes together.

  Major inflection point hit: A Ulysses agent that is capable of maneuvering to the denoted location. Once both systems are spun up, send a kickstart message to the nes environment,
starts the feedback loop between environment and amalgam (current name for environment and agent deciding actions for environment). The nes environment needs a move plan.
If it does not have one, it sends the raw pixel string that represents the current screen. The communication nexus in the amalgam directory first spins up an agent and awaits
messages. When one is noted, the message is formatted into a 13x15 (YxX) grid of 16x16 pixel grid squares. Another simple mapping algorithm is applied to each square to derive the
most common color in each square. The agent uses this compressed representation of the state and applies a Q learning algorithm to it. Once the Q function is learned, we output the
actions needed to get to the reward point. each action is incremented by 4, to match their definitions in nintaco. The action string is then sent to the emulator, which decodes the
message and sets its navigation plan. With the navigation plan set, it executes one of the navigation commands at each discrete execution point.

  It is worth noting that, at time of present, output solution for prototype start point has too many actions; indicating that my state is in fact somewhat malformed.

A few different next steps.

1. begin efforts to dockerize the project
2. Final investigation of fidelity of state representation
3. Begin to consider question of combat state identification & combat writ large

  Imagine 1 & 2 will be focus of work for forseeable in this hard burn. Question of how to order these unknown; neither seem directly connected.
dockerizing the project is probably the way to go, as progress on this front enables me to work on this project beyond my personal desk.
  While not the most important thing on earth, the fidelity of the state representation should be mostly accurate.
Combat state identification is essentially a different domain of AI challenge. Some passive thought has been given about using a CNN, but will now need to more
closely consider nature of problem.

## 12/20/19

 Hit another major inflection point. I was able to get a roughly successful run at the gridworld problem using data I manufactured for the state.

 Next step is to stream actions into the environment, which will begin the agent-environment feedback loop. Getting to this position before the fuel of this (pretty wildly productive) hard burn would be close to ideal for me.

Update 2:22 PM^

Wintermute is a learning Agent whose goal is to successfully play Final Fantasy. Final Fantasy is the progenitor of the role playing game.
No remotely-publicized attention has been given to the challenge of creating a learning agent to play RPGs. This is a shame, because
RPGs contain both the thought processes required for true intelligence: Long term planning and execution and the ability to derive a goal
through generalized analysis of available information.

This is the first prototype of Wintermute, the system which will actually be playing the game. Wintermute prototype will start with the Temple of Fiends
(the first dungeon of the game as well as the initial reward point) in sight. It will then use Dynamic programming policy improvement to make its way to the Reward
When it is attacked, it will need to know that it is under attack. If it comes under attack, it will run. Handling a combat strategy will be next step after
Cowardly approach is working.

At time of posting, contains the emulation layer, which runs in python 2.7 and consists of the Nintaco API, a file named actuation which connects to the API, gets the pixels at an externally
determined interval and encodes these pictures to a kafka topic, `emulator_to_environment`.

On other side of topic is a python 3 consumer. This consumer takes the raw data and formats it in a 15 x 13 matrix of 16 x 16 pixel grid squares.

Next step is to flesh out agent/environment interactions. Worth noting that there are all sorts of hacky bullshit methods to get to the Temple, but none will matter
without the ability to recognize that the character is in a fight. Requires a simple perception function, but have not contemplated the details of that.

I also need to actually code the gridworld playing agent. I think this will probably mean re-examining each of its rules and determining what that action flow should be

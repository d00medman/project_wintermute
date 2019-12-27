1. at /project_wintermute/nintaco, run `java -jar Nintaco.jar` to launch nintaco emulator
2. In Nintaco GUI, load final fantasy and turn program server on (determine if this is doable programtically, or is manual)
3. Attempted to run nes_environment/nes_environment.py; this cannot be done in a window where `wintermute_prototype_venv` is active. Possible conflict between python 2.7 the emulator is running and the 3.6 emulator all other sytems are on.
  - This will be a source of problems in the future. Does the nes environment need its own venv? how is this venv to interact w/ the venv the main system is using
4. in /project_wintermute/wintermute_prototype, run `source wintermute_prototype_venv/bin/activate` to enable the venv (why is the venv needed? when does it need to be on?)

5. Run the kafka setup in other md file
6. activate communication nexus after turning on the venv
7. activate the nes environment with no venv on
8. manually write a message to the topic that the nes environment reads from
- controller must be plugged into system for controller to be usable by emulator. need to restart if they aren't directly connecting

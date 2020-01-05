action_switcher = {
    'UP': {
        'scalar_value': 0,
        'stationary_condition': lambda y: y == 0
    },
    'DOWN': {
        'scalar_value': 1,
        'stationary_condition': lambda y, max_y: y == (max_y - 1)
    },
    'LEFT': {
        'scalar_value': 2,
        'stationary_condition': lambda x: x == 0
    },
    'RIGHT': {
        'scalar_value': 3,
        'stationary_condition': lambda x, max_x: x == (max_x - 1)
    }
}
# action = action_switcher.get('UP')
# no_movew
# print(action['stationary_condition'](0))

for action in action_switcher:
    print(action_switcher.get(action).get('scalar_value'))
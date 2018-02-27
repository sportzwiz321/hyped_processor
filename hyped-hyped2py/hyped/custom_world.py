import hyped.interpreter as itp
from heapq import heappop, heappush

def interact(automata):
	global start
	split = automata.split(" ")
	if split[2] == "enemy":
		# print split[3]
		x = int(split[0][1:2])
		y = 6 - int(split[1][0:1])
		tup = (x, y)
		if split[3] == "alive":
			print "I will kill the enemy at", tup
			global modified_key
			modified_key = inventory
			path = findExitPath(start, tup)
			print
			if path:
				for x in range(0, len(path)):
					print "(" + str(path[x][0]) + ",", str(height - path[x][1] - 1) + ")"
					if x == len(path) - 1:
						# print path[x]
						start = path[x]
			else:
				print "N/A"
			print
		else:
			print "The enemy is already dead at", tup
	# print split

def isInvalidAutomata(atype, isDynamic):
	if atype == "door" or atype == "enemy_tracker":
		return isDynamic
	else:
		return not isDynamic

def stateCombinations(dungeon_automata, isDynamic):

	combo = []

	if not dungeon_automata:
		pass
	else:

		keys = dungeon_automata.keys()
		count = 0
		rem_list = []
		while count < len(keys) and isInvalidAutomata(dungeon_automata[keys[count]]["type"], isDynamic):
			rem_list.append(keys[count])
			count += 1

		sub_dict = dict(dungeon_automata)
		for item in rem_list:
			del sub_dict[item]

		if not sub_dict:
			pass
		else:
			pos = keys[count]
			automata_type = dungeon_automata[pos]["type"]

			sub_dict = dict(dungeon_automata)
			del sub_dict[keys[count]]
			sub_combo = stateCombinations(sub_dict, isDynamic)
			for state in dungeon_automata[pos]["states"]:
				next_entry = str(pos) + " " + automata_type + " " + state
				if sub_combo:
					for combination in sub_combo:
						combo_pointer = list(combination)
						combo_pointer.append(next_entry)
						combo.append(combo_pointer)
				else:
					combo.append([next_entry])
	return combo

def addAdj(x, y):
	adj_list = []
	if x - 1 >= 0 and positionIsPassable((x - 1, y)):
		adj_list.append((x - 1, y))
	if y - 1 >= 0 and positionIsPassable((x, y - 1)):
		adj_list.append((x, y - 1))
	if x + 1 < width and positionIsPassable((x + 1, y)):
		adj_list.append((x + 1, y))
	if y + 1 < height and positionIsPassable((x, y + 1)):
		adj_list.append((x, y + 1))
	return adj_list

def findExitPath(initial_position, destination):
	q = []
	heappush(q, (0, initial_position))
	parent = {}
	cost = {}
	parent[initial_position] = None
	cost[initial_position] = 0

	while q:
	    current = heappop(q)
	    if current == destination:
	        break

	    for next in addAdj(current[1][0], current[1][1]):
	        new_cost = cost[current[1]] + 1
	        if next not in cost or new_cost < cost[next]:
	            cost[next] = new_cost
	            priority = new_cost
	            heappush(q, (priority, next))
	            parent[next] = current[1]

	if destination in parent:
	    current = destination
	    path = [current]
	    while current != initial_position:
	    	for item in door_layout:
		    	parse = item.split(" ")
		    	if parse[0] + " " + parse[1] == str((current[0], height - current[1] - 1)):
		    		if parse[2] == "door" and parse[3] == "closed":
		    			global modified_key
	    				modified_key = "don't have"
	        current = parent[current]
	        path.append(current)
	    path.reverse()
	else:
		path = []

	return path

def findAllExit(initial_position, exit):
	for goal in exit:
		global modified_key
		modified_key = inventory
		print "initial_position: (" + str(initial_position[0]) + ",", str(height - initial_position[1] - 1) + ")"
		print "initial key possession:", modified_key
		path = findExitPath(initial_position, goal)
		print "final key possession:", modified_key
		print "goal: (" + str(goal[0]) + ",", str(height - goal[1] - 1) + ")"
		print
		if path:
			for step in path:
				print "(" + str(step[0]) + ",", str(height - step[1] - 1) + ")"
		else:
			print "N/A"
		print

# to grab the x and y offset of the enemy tracker
# for automata.name == enemy_tracker and automata.collider.is_static == true
# automata.collider.shape.x.value
def getPossibleStates(automata_name):
	all_states = []
	for entry in world.automata:
		if entry.name == automata_name:
			automata_name = entry.name
			automata_group = entry.groups[automata_name]
			automata_modes = automata_group.modes
			for mode in automata_modes:
				all_states.append(automata_modes[mode].name)
	return all_states

def automataAtPosition(position, dungeon_automata):
	for automata in dungeon_automata:
		if automata[0] != "link":
			automata_x = automata[2]["x"] / tile_width
			automata_y = automata[2]["y"] / tile_height - 1
			if (automata_x, automata_y) == position:
				return automata[0]
		elif automata[0] == "link":
			automata_x = automata[2]["x"] / tile_width
			automata_y = automata[2]["y"] / tile_height
			if (automata_x, automata_y) == position:
				return automata[0]
	return None

def positionIsPassable(position):

	real_position = (position[0], height - position[1] - 1)
	automata = automataAtPosition(real_position, space.initial_automata)

	for door in door_layout:
		parse = door.split(" ")
		if parse[0] + " " + parse[1] == str(real_position):
			if parse[2] == "door":
				if parse[3] == 'open':
					return True
				elif inventory == "have":
					return True
				else:
					return False
			else:
				if parse[3] == "enemies_dead":
					return True
				else:
					return False

	if (automata == None or isPassable(world, link_collider, automata)) and world_map[position[1]][position[0]] != 1:
		return True
	else:
		return False

def isPassable(world, link_collider, automata_name):
	for item in world.automata:
		if item.name == automata_name:
			for collide in item.colliders:
				if world.theories.collision.blocking_typesets(link_collider, collide.types):
					return False
			return True

def showPaths():
	if len(exit) == 1:
		print "*************************"
		findAllExit(exit[0], exit)
		print "*************************"
	else:
		for portal in exit:
			print "*************************"
			temp_copy = list(exit)
			temp_copy.remove(portal)
			findAllExit(portal, temp_copy)
			print "*************************"
	print

# map_index = 2

# initialize global data

# for each grid
# initialize grid data
# print grid layout and determines exits
# store all automata states
# if a door exists, print a path with the door open and closed

# initialize global data:
# world
# link_collider
# link
world = itp.load_zelda()

for item in world.automata:
	if item.name == "link":
		link = item
		link_collider = link.colliders[0].types
		break

# for each grid
for grid in world._spaces:
	# initialize grid data:
	# space
	# world_map
	# height
	# width
	# tile_height
	# tile_width
	# adj
	# exit
	# automata_states
	print "/////////////////////////"
	print "/////////////////////////"
	space = grid[1]
	world_map = space.static_colliders[0].shape.tiles

	height = len(world_map)
	width = len(world_map[0])

	tile_height = space.static_colliders[0].shape.tile_height
	tile_width = space.static_colliders[0].shape.tile_width

	adj = {}
	exit = []

	# prints grid layout and determines exits
	for y in range(0, height):
		wall = ""
		for x in range(0, width):
			if world_map[y][x] != 1:
				if world_map[y][x] == 2:
					exit.append((x, y))

			wall = wall + str(world_map[y][x]) + " "
		print wall

	print ""

	automata_states = {}
	local_automata = {}

	# store all automata states
	if space.initial_automata:
		for automata in space.initial_automata:
			if automata[0] != "link":
				automata_x = automata[2]["x"] / tile_width
				automata_y = automata[2]["y"] / tile_height - 1
				automata_states[automata[0]] = getPossibleStates(automata[0])

				if automata[0] == "enemy_tracker":
					for instance in world.automata:
						if instance.name == "enemy_tracker":
							for collider in instance.colliders:
								if collider.is_static:
									x_offset = collider.shape.x.value / 32
									y_offset = collider.shape.y.value / 32
					automata_pos = (int(automata_x + x_offset), int(automata_y + y_offset))
				else:
					automata_pos = (automata_x, automata_y)

				local_data = {}
				local_data["type"] = automata[0]
				local_data["states"] = getPossibleStates(automata[0])

				local_automata[automata_pos] = local_data
			elif automata[0] == "link":
				automata_x = automata[2]["x"] / tile_width
				automata_y = automata[2]["y"] / tile_height
	else:
		print "automata: none"
		print "initital state: n/a"
		print

	# example case for showing different paths for various combinations of open and closed doors
	# 
	# test_data = {
	# 	(4, 5): {
	# 		"type": "door",
	# 		"states": [
	# 			"open",
	# 			"closed"
	# 		]
	# 	},
	# 	(4, 1): {
	# 		"type": "door",
	# 		"states": [
	# 			"open",
	# 			"closed"
	# 		]
	# 	}
	# }
	# 
	# test_combos = stateCombinations(test_data)
	# for layout in test_combos:
	# 	# local global door_layout
	# 	door_layout = layout
	# 	print layout
	# 	showPaths()

	print "exits:"
	exit_list = []
	for path in exit:
		exit_list.append((path[0], height - path[1] - 1))
	print exit_list
	print

	# print local_automata

	key_state = ["have", "don't have"]
	modified_key = ""

	# fully implemented
	# current configuration takes for all possible automata, what paths are possible
	# can also implement possible with and without key as a global variable
	# currently loses key when the character explores the path that contains the door
	live_combos = stateCombinations(local_automata, False)
	if live_combos:
		for posession in key_state:
			if posession == "have":
				inventory = posession
				for layout in live_combos:
					door_layout = layout
					print "current configuration:"
					print layout
					showPaths()
	else:
		for posession in key_state:
			inventory = posession
			door_layout = []
			print "empty configuration"
			showPaths()

	dyn_automata = stateCombinations(local_automata, True)

	init = (1, 1)

	# print "False"
	if dyn_automata:
		for posession in key_state:
			if posession == "have":
				inventory = posession
				print inventory
				print
				for item in dyn_automata:
					start = (1, 6 - init[1])
					item_state = item
					print "current item state"
					for obj in item_state:
						interact(obj)
					print

	# print
	# print "True"
	# for item in live_combos:
	# 	print item

	# next approach should read in automata and determine what needs to happen
	# if enemy_tracker is active, kill enemies
	# if key is there, make it gone

	if grid[0] == "1":
		break
'''
	# prints and finds all exits for a given dungeon
	if space.initial_automata and space.initial_automata[0][0] == "link":
		initial_location = space.initial_automata[0][2]
		initial_x = initial_location["x"] / tile_width
		initial_y = initial_location["y"] / tile_height
		initial_position = (initial_x, height - initial_y - 1)
		findAllExit(initial_position, exit, adj)
	else:
		if len(exit) == 1:
			print "*************************"
			findAllExit(exit[0], exit, adj)
			print "*************************"
		else:
			for portal in exit:
				print "*************************"
				temp_copy = list(exit)
				temp_copy.remove(portal)
				findAllExit(portal, temp_copy, adj)
				print "*************************"
'''

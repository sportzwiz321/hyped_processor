import hyped.interpreter as itp
from heapq import heappop, heappush

def stateCombinations(dungeon_automata):

	print dungeon_automata

	combo = []

	if not dungeon_automata:
		pass
	else:

		keys = dungeon_automata.keys()
		pos = keys[0]
		automata_type = dungeon_automata[pos]["type"]

		sub_dict = dict(dungeon_automata)
		del sub_dict[keys[0]]
		sub_combo = stateCombinations(sub_dict, depth + 1)
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

def addAdj(x, y, door_status):
	adj_list = []
	if x - 1 >= 0 and positionIsPassable((x - 1, y), door_status):
		adj_list.append((x - 1, y))
	if y - 1 >= 0 and positionIsPassable((x, y - 1), door_status):
		adj_list.append((x, y - 1))
	if x + 1 < width and positionIsPassable((x + 1, y), door_status):
		adj_list.append((x + 1, y))
	if y + 1 < height and positionIsPassable((x, y + 1), door_status):
		adj_list.append((x, y + 1))
	return adj_list

def findExitPath(initial_position, destination, door_status):
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

	    for next in addAdj(current[1][0], current[1][1], door_status):
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
	        current = parent[current]
	        path.append(current)
	    path.reverse()
	else:
		path = []

	return path

def findAllExit(initial_position, exit, door_status):
	for goal in exit:
		path = findExitPath(initial_position, goal, door_status)
		print "initial_position: (" + str(initial_position[0]) + ",", str(height - initial_position[1] - 1) + ")"
		print "goal: (" + str(goal[0]) + ",", str(height - goal[1] - 1) + ")"
		print ""
		for step in path:
			print "(" + str(step[0]) + ",", str(height - step[1] - 1) + ")"
		print ""

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

def positionIsPassable(position, door_status):
	real_position = (position[0], height - position[1] - 1)
	automata = automataAtPosition(real_position, space.initial_automata)
	if automata == "door" and door_status == "open":
		return True
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

def showPaths(status):
	print status
	if len(exit) == 1:
		print "*************************"
		findAllExit(exit[0], exit, status)
		print "*************************"
	else:
		for portal in exit:
			print "*************************"
			temp_copy = list(exit)
			temp_copy.remove(portal)
			findAllExit(portal, temp_copy, status)
			print "*************************"

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

	test_data = {
		(0, 0): {
			"type": "enemy",
			"states": [
				"alive",
				"dead"
			]
		},
		(1, 1): {
			"type": "door",
			"states": [
				"open",
				"closed"
			]
		}
	}

	live_combos = stateCombinations(local_automata)
	# for layout in live_combos:
	# 	print layout

	for x in range(0, len(live_combos)):
		print str(x + 1) + ".", live_combos[x]


	# if a door exists, print a path with the door open and closed
	if "door" in automata_states:
		for init_state in automata_states["door"]:
			for final_state in automata_states["door"]:
				if final_state == "open":
					print "open door:", init_state + "-" + final_state
					# showPaths("open")
					print
				elif init_state == "closed":
					print "closed door:", init_state + "-" + final_state
					# showPaths("closed")
					print
	else:
		print "I don't exist"
	print

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

import hyped.interpreter as itp
from heapq import heappop, heappush

def addAdj(space, x, y, width, height, world, link_collider, real_space, door_status):
	adj_list = []
	# if x - 1 >= 0 and space[y][x - 1] != 1:
	# 	adj_list.append((x - 1, y))
	# if y - 1 >= 0 and space[y - 1][x] != 1:
	# 	adj_list.append((x, y - 1))
	# if x + 1 < width and space[y][x + 1] != 1:
	# 	adj_list.append((x + 1, y))
	# if y + 1 < height and space[y + 1][x] != 1:
	# 	adj_list.append((x, y + 1))
	if x - 1 >= 0 and positionIsPassable(world, link_collider, (x - 1, y), real_space, space, height, door_status):
		adj_list.append((x - 1, y))
	if y - 1 >= 0 and positionIsPassable(world, link_collider, (x, y - 1), real_space, space, height, door_status):
		adj_list.append((x, y - 1))
	if x + 1 < width and positionIsPassable(world, link_collider, (x + 1, y), real_space, space, height, door_status):
		adj_list.append((x + 1, y))
	if y + 1 < height and positionIsPassable(world, link_collider, (x, y + 1), real_space, space, height, door_status):
		adj_list.append((x, y + 1))
	# dict[(x, y)] = adj_list
	return adj_list

def findExitPath(initial_position, destination, door_status, width, height, world, link_collider, real_space, space):
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

	    # print current

	    for next in addAdj(space, current[1][0], current[1][1], width, height, world, link_collider, real_space, door_status):
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

def findAllExit(initial_position, exit, door_status, width, height, world, link_collider, real_space, space):
	for goal in exit:
		path = findExitPath(initial_position, goal, door_status, width, height, world, link_collider, real_space, space)
		print "initial_position: (" + str(initial_position[0]) + ",", str(height - initial_position[1] - 1) + ")"
		print "goal: (" + str(goal[0]) + ",", str(height - goal[1] - 1) + ")"
		print ""
		for step in path:
			print "(" + str(step[0]) + ",", str(height - step[1] - 1) + ")"
		print ""

def printInitialState(world, automata_name):
	all_states = []
	for entry in world.automata:
		if entry.name == automata_name:
			automata_name = entry.name
			automata_group = entry.groups[automata_name]
			automata_modes = automata_group.modes
			# print "automata:", automata_name
			for mode in automata_modes:
				# print automata_modes[mode].name
				all_states.append(automata_modes[mode].name)
				# if automata_modes[mode].is_initial:
					# print "initial state:", automata_modes[mode].name
					# break
			# break
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

def positionIsPassable(world, link_collider, position, real_space, space, height, door_status):
	real_position = (position[0], height - position[1] - 1)
	automata = automataAtPosition(real_position, real_space.initial_automata)
	if automata == "door" and door_status == "open":
		return True
	# print "space:", space
	# print "real_space:", real_space
	if (automata == None or isPassable(world, link_collider, automata)) and space[position[1]][position[0]] != 1:
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

def showPaths(status, exit, width, height, world, link_collider, real_space, space):
	print status
	if len(exit) == 1:
		print "*************************"
		findAllExit(exit[0], exit, status, width, height, world, link_collider, real_space, space)
		print "*************************"
	else:
		for portal in exit:
			print "*************************"
			temp_copy = list(exit)
			temp_copy.remove(portal)
			findAllExit(portal, temp_copy, status, width, height, world, link_collider, real_space, space)
			print "*************************"

map_index = 2

world = itp.load_zelda()

for item in world.automata:
	if item.name == "link":
		link = item
		link_collider = link.colliders[0].types
		break

# tupleA = (1, 10)
# tupleB = (10, 1)
# tupleC = (1, 10)

# print "A:", tupleA
# print "B:", tupleB
# print "C:", tupleC

# # print "A is B:", tupleA is tupleB
# # print "A == B:", tupleA == tupleB
# # print "A is C:", tupleA is tupleC
# print "A == C:", tupleA == tupleC

# print
# for item in world.automata:
# 	if item.name != "link":
# 		print item.name
# 		print
# 		for collide in item.colliders:
# 			print collide
# 			print
# 		print

# test_automata = "key"

# print "link can collide with", test_automata + ":", isPassable(world, link_collider, test_automata)

# print
# for item in world.automata:
# 	if item.name == "link":
# 		print item.name
# 		print
# 		# print item.colliders
# 		for collide in item.colliders:
# 			print collide
# 			for other_item in world.automata:
# 				if other_item.name != "link":
# 					print other_item.name
# 					for other_collide in other_item.colliders:
# 						# if other_item.name == "enemy_tracker":
# 						# 	print other_collide
# 						print world.theories.collision.blocking_typesets(collide.types, other_collide.types)
# 						# print
# 					print
# 			print
			# print
			# print collide
			# print
		# print

# print world.automata

# print world.theories.collision.blocking_typesets(player, automata)



# iterates through every dungeon in the world
for grid in world._spaces:
# grid = world._spaces[1]
	# break
	print "/////////////////////////"
	print "/////////////////////////"
	# print grid[1]
	space = grid[1]
	world_map = space.static_colliders[0].shape.tiles

	height = len(world_map)
	width = len(world_map[0])

	tile_height = space.static_colliders[0].shape.tile_height
	tile_width = space.static_colliders[0].shape.tile_width

	adj = {}
	exit = []

	# creates adjaceny list and prints out the dungeon layout
	for y in range(0, height):
		wall = ""
		for x in range(0, width):
			# print x, y, world_map[y][x]
			if world_map[y][x] != 1:
				if world_map[y][x] == 2:
					exit.append((x, y))
				# addAdj(adj, world_map, x, y, width, height, world, link_collider, space)

			wall = wall + str(world_map[y][x]) + " "
		print wall

	print ""


	# print
	# for y in range(0, height):
	# 	for x in range(0, width):
	# 		pair = (x, y)
	# 		if automataAtPosition(pair, space.initial_automata) is not None:
	# 			print pair, automataAtPosition(pair, space.initial_automata)
	# 		if world_map[y][x] != 1:
	# 			print pair, adj[pair]
	# 			print

	# if grid[0] == "1":
	# 	break

	automata_states = {}

	# displays all initial automata within a dungeon
	if space.initial_automata:
		for automata in space.initial_automata:
			if automata[0] != "link":
			# print automata[0]
				automata_x = automata[2]["x"] / tile_width
				automata_y = automata[2]["y"] / tile_height - 1
				automata_states[automata[0]] = printInitialState(world, automata[0])
				# print str(automata_x) + "," + str(automata_y)
				# print
			elif automata[0] == "link":
				automata_x = automata[2]["x"] / tile_width
				automata_y = automata[2]["y"] / tile_height
				# print "automata: link"
				# print "initial state: alive"
				# print str(automata_x) + "," + str(automata_y)
				# print
	else:
		print "automata: none"
		print "initital state: n/a"
		print

	# print "automata_states:"
	# for key in automata_states:
	# 	print key, automata_states[key]

	if "door" in automata_states:
		for init_state in automata_states["door"]:
			for final_state in automata_states["door"]:
				if final_state == "open":
					print "open door:", init_state + "-" + final_state
					# print "open door path"
					showPaths("open", exit, width, height, world, link_collider, space, world_map)
					print
				elif init_state == "closed":
					print "closed door:", init_state + "-" + final_state
					# print "closed door path"
					showPaths("closed", exit, width, height, world, link_collider, space, world_map)
					print
				# else:
				# 	pass
				# print "initial state:", init_state
				# print "final state:", final_state
		# print "I exist"
	else:
		print "I don't exist"

	# print "all states:", automata_states
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

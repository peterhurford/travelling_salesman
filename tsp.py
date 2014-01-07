#!/usr/local/bin/python3

# Peter Hurford and Danny Persia
# March 11, 2011
# A genetic algorithm for the TSP.

import math, cTurtle, random

# ************ GENERAL PURPOSE TSP FUNCTIONS ************

# Return the distance between points p and q.
def distance(p, q):
	return math.sqrt((p[0] - q[0])**2 + (p[1] - q[1])**2)
	
# Return the total length of a tour.
def tourLength(tour):
	length = 0
	for i in range(1, len(tour)):
		length = length + distance(tour[i - 1], tour[i])
		
	length = length + distance(tour[-1], tour[0])
	
	return length
	
# Read a list of city coordinates from a file.
# The first line in the file contains the width and height 
# of the coordinate system on which the cities are plotted.
# The function returns the list of cities and the width and height
# in a 3-element tuple.
def readCities(filename):
	inputFile = open(filename, 'r')   # open file named filename for reading
	
	line = inputFile.readline()       # read the first line into a string
	values = line.split()             # split the line into a list of "words"
	width = int(values[0])            # first "word" is the width of the cities
	height = int(values[1])           # second "word" is the height of the cities
	
	cities = []                       # init the list of city coordinates
	for line in inputFile:            # process rest of the lines one at a time
		values = line.split()          # split line into "words" (x and y values)
		cities.append([float(values[0]), float(values[1])])   # append (x,y)
		
	return (cities, width, height)    # return 3 values packaged in a tuple
	
	
def drawTour(tour, width, height):
	'''Draw a tour expressed as a list of (x,y) coordinates.'''
	t = cTurtle.Turtle()
	t.setWorldCoordinates(0, 0, width, height)
	t.speed(0)
	t.tracer(1000)
	t.hideturtle()
	t.up()
	t.goto(tour[0][0], tour[0][1])
	t.down()
	t.dot()
	for i in range(1, len(tour)):
		t.goto(tour[i][0], tour[i][1])
		t.dot()
	t.pencolor("red")
	t.goto(tour[0][0], tour[0][1])
	t.dot()
	t.update()
	t.exitOnClick()

	
# ********************* GENETIC ALGORITHM FOR TSP ***********************

GENERATIONS = 10000     # number of generations to evolve
SIZE = 350                # size of the population
MUTATION_RATE = 0.20     # probability that a mutation happens

# Create a population consisting of random permutations of the cities.
def makePopulation(cities):
	population = []
	for i in range(SIZE):
		population.append(cities[:])
		random.shuffle(population[i]) #Add a random city to the starting population
	return population
		
# Perform a crossover operation
def crossover(mom, pop):
	momcutlen = random.randrange(1, len(mom)-1) #Get a random length to cut
	momoffsetmax = len(mom) - momcutlen #Get a random offset
	momcutstart = random.randrange(0, momoffsetmax) #Random startpoint of sublist
	momcutend = momcutstart + momcutlen #Determine endpoint from startpoint and length
	momrandcut = mom[momcutstart:momcutend] #Get a random set of cities from mom
	child1 = [city for city in pop if city not in momrandcut] #Delete the cities from pop
	
	bestlength = tourLength(mom) #Use the unedited string as current best
	usechild = []
	usechild.extend(mom) #Create a test list starting with the mom list
	for j in range(len(child1)):
		testchild = []
		testchild.extend(child1)
		for i in range(len(momrandcut)): #Insert the subsection in every possible location
			testchild.insert(j+i, momrandcut[i])
		testlength = tourLength(testchild)
		if testlength < bestlength: #Find the best location to put the subsection in
			usechild = []
			usechild.extend(testchild)
			bestlength = testlength
	
	child1 = []
	child1.extend(usechild) #Make child1 the best of tested crossovers
	
	#Repeat the same for the pop list
	popcutlen = random.randrange(1, len(pop)-1)
	popoffsetmax = len(pop) - popcutlen
	popcutstart = random.randrange(0, popoffsetmax)
	popcutend = popcutstart + popcutlen
	poprandcut = pop[popcutstart:popcutend]
	child2 = [city for city in pop if city not in poprandcut]
	
	bestlength = tourLength(pop)
	usechild = []
	usechild.extend(pop)
	for j in range(len(child2)):
		testchild = []
		testchild.extend(child2)
		for i in range(len(poprandcut)):
			testchild.insert(j+i, poprandcut[i])
		testlength = tourLength(testchild)
		if testlength < bestlength:
			usechild = []
			usechild.extend(testchild)
			bestlength = testlength
	
	child2 = []
	child2.extend(usechild)
	
	return (child1, child2) #return the two children
	
# Swap two elements in a list (used by mutate).
def swap(L, i, j):
	temp = L[i]
	L[i] = L[j]
	L[j] = temp

# Mutate an individual by taking out a city at random and put it back in the best possible position.
def greedy_mutate(individual):
	preserve = []
	preserve.extend(individual) #Keep an intial copy of the tour
	i = random.randrange(0, len(individual))
	a = individual[i] #Take a random city for the string
	best = tourLength(individual)
	for j in range(len(individual)):
		if j == 0: #If at the beginning...
			individual.pop(i) #...take out the random city from its starting place
		else: #Otherwise...
			individual.pop(j-1) #...take out the random city from the last point it was put in
		individual.insert(j, a) #Insert it at different points
		test = tourLength(individual) #Check the tour length
		if test < best: #If it is better, use that mutation
			return individual
	return preserve #If no better tour is found, return the first tour

#Random swap mutation to increase population diversity
def mutate(individual):
	a = random.randrange(0, len(individual))
	b = random.randrange(0, len(individual))
	swap(individual, a, b)

# Crossover two individuals and mutate them in various ways.
def newGeneration(population):
	#Randomly choose a mating fraction between 0.05 and 0.95
	MATING_FRACTION = random.randrange(50, 950)
	MATING_FRACTION = MATING_FRACTION/1000
	
	mate1 = random.choice(population[:int(SIZE * MATING_FRACTION)])
	mate2 = random.choice(population[:int(SIZE * MATING_FRACTION)]) #Choose the two mates
	
	(child1, child2) = crossover(mate1, mate2) #Cross them
	
	greedy_mutate(child1) #Mutate them for the better
	greedy_mutate(child2)
	
	#If the resulting children are better than the worst of the population, replace the worst
	if tourLength(child1) < tourLength(population[SIZE - 2]):
		population[SIZE - 2] = child1
	if tourLength(child2) < tourLength(population[SIZE - 1]):
		population[SIZE - 1] = child2
		
	#To prevent local optima, randomly mutate a city on occasion
	if random.random() < MUTATION_RATE:
		i = random.randrange(1, len(population))
		mutate(population[i])
	
# Display a frequency chart of the current population diversity.
def histogram(population):
	hist = {} #Create an empty dictionary
	for i in range(len(population)):
		if tourLength(population[i]) not in hist: #If the tourlength is not currently in the dictionary, add it to the dictionary
			hist[tourLength(population[i])] = 1
		else: #Otherwise increase the value in the dictionary to reflect a second element
			hist[tourLength(population[i])] = hist[tourLength(population[i])] + 1
	
	#Print the histogram
	print("Population Diversity:")
	histogram = []
	for tuple in hist.items(): #Make it a list so it can be sorted
		histogram.append([tuple[0], tuple[1]])
	histogram.sort()
	for tuple in histogram: #Print the sorted histogram
		print(tuple[0], " : ", "*"*tuple[1])
	print("") #Print a spacer

# Periodically display information about the current population.
def report(population, generation, minLength):
	
	if generation % 100 == 0: #display the generation number every 100
		print("GENERATION", generation)
			
	if generation % 1000 == 0: #display population diversity every 1000
		histogram(population)
		
	#get the best tour length in this population
	currentBest = tourLength(population[0])
	if currentBest < minLength: #if it is the best so far, then print it
		print(currentBest)
		minLength = currentBest
		
	return minLength #return the best tour length so far
	
	
# Genetic algorithm for TSP
def tspGA(filename):
	(cities, width, height) = readCities(filename) 
	
	# Evolve over GENERATIONS generations.
	population = makePopulation(cities) 
	population.sort(key = tourLength)
	bestSoFar = tourLength(population[0])           
	for g in range(GENERATIONS):
		bestSoFar = report(population, g, bestSoFar)
		newGeneration(population)
		population.sort(key = tourLength)
		
	tour = population[0]         # the best tour in the final generation
	drawTour(tour, width, height)     # draw the tour
	return tourLength(tour)           # return the tour's length
	
def main():
	tspGA("tsp10.txt")
	
main()
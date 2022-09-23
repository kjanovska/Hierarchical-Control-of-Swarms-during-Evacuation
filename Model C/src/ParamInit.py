class ParamInit:
	def __init__(self):
		# parameters are set as base values
		self.informed_leaders = 100
		self.follower_obedience = 90
		self.follower_sight = 40
		self.leader_sight = 15
		self.leader_conflict_distance = 3
		self.min_swarm_denominator = 3  # x in ceil(agents/x)
		self.experiment_number = ""
		self.map = ""
		self.scenario = ""

		self.user_input()

	def user_input(self):
		print("Follower sight length: ")
		self.follower_sight = int(input())
		print("Leader sight length: ")
		self.leader_sight = int(input())
		print("Minimum followers in a swarm - denominator: ")
		self.min_swarm_denominator = int(input())
		print("Percentage of follower obedience: ")
		self.follower_obedience = int(input())
		print("Leader conflict distance: ")
		self.leader_conflict_distance = int(input())
		print("Experiment label: ")
		self.experiment_number = input()
		print("Used map: ")
		self.map = input()

		
		

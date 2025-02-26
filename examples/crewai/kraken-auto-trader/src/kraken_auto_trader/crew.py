from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from hyperpocket_crewai import PocketCrewAI

# If you want to run a snippet of code before or after the crew starts, 
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class KrakenAutoTrader():
	"""KrakenAutoTrader crew"""

	# Learn more about YAML configuration files here:
	# Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
	# Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	# If you would like to add tools to your agents, you can learn more about it here:
	# https://docs.crewai.com/concepts/agents#agent-tools
	
	def __enter__(self):
		return self
	
	def __exit__(self, exc_type, exc_val, exc_tb):
		if hasattr(self, 'analyzer_pocket'):
			self.analyzer_pocket.teardown()
		if hasattr(self, 'trader_pocket'):
			self.trader_pocket.teardown()
			
	@agent
	def market_trend_reader(self) -> Agent:
		self.analyzer_pocket = PocketCrewAI(
			tools=[
				"https://github.com/vessl-ai/hyperpocket/tree/main/tools/kraken/kraken-get-ticker",
				"https://github.com/vessl-ai/hyperpocket/tree/main/tools/kraken/kraken-get-recent-trades"
			]
		)
		self.analyzer_pocket.init()
		return Agent(
			config=self.agents_config['market_trend_reader'],
			verbose=True,
			tools=self.analyzer_pocket.get_tools(),
		)

	@agent
	def trader(self) -> Agent:
		self.trader_pocket = PocketCrewAI(
			tools=[
				"https://github.com/vessl-ai/hyperpocket/tree/main/tools/kraken/kraken-get-account-balance",
				"https://github.com/vessl-ai/hyperpocket/tree/main/tools/kraken/kraken-create-order",
			]
		)
		self.trader_pocket.init()
		return Agent(
			config=self.agents_config['trader'],
			verbose=True,
			tools=self.trader_pocket.get_tools(),
		)

	# To learn more about structured task outputs, 
	# task dependencies, and task callbacks, check out the documentation:
	# https://docs.crewai.com/concepts/tasks#overview-of-a-task
	@task
	def read_ticker(self) -> Task:
		return Task(
			config=self.tasks_config['read_ticker'],
		)
	
	@task
	def read_recent_trades(self) -> Task:
		return Task(
			config=self.tasks_config['read_recent_trades'],
		)

	@task
	def analyze_pair_trend(self) -> Task:
		return Task(
			config=self.tasks_config['analyze_pair_trend'],
			output_file='report.md'
		)
	
	@task
	def make_trading_decision(self) -> Task:
		return Task(
			config=self.tasks_config['make_trading_decision'],
		)
	
	@task
	def trade(self) -> Task:
		return Task(
			config=self.tasks_config['trade'],
		)
	
	@task
	def review_balance(self) -> Task:
		return Task(
			config=self.tasks_config['review_balance'],
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the KrakenAutoTrader crew"""
		# To learn how to add knowledge sources to your crew, check out the documentation:
		# https://docs.crewai.com/concepts/knowledge#what-is-knowledge

		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True,
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)

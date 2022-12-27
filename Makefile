SHELL := /bin/bash

deploy:
	func azure functionapp publish saans-dev-af-appsrv

start:
	func start
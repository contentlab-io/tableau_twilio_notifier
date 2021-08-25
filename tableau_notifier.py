from flask import Flask, request
import tableauserverclient as TSC
import os
import json
from twilio.rest import Client

app = Flask(__name__)

@app.route("/notifier", methods=["GET", "POST"])
def notify():
	if request.method == "POST":
		logPaths = ["/opt/python/log/test", "log"] # Debugging

		twilioSID = os.environ["TWILIO_ACCOUNT_SID"]
		twilioAuthToken = os.environ["TWILIO_AUTH_TOKEN"]
		twilioClient = Client(twilioSID, twilioAuthToken)
		sendingNumber = os.environ["TWILIO_FROM_NUMBER"]
		receivingNumber = os.environ["TO_NUMBER"]
		whatsappFrom = os.environ["WHATSAPP_FROM"]
		whatsappTo = os.environ["WHATSAPP_TO"]

		for path in logPaths:
			with open(path, "w") as logFile:
				logFile.write(f"Request: {request}\nRequest values: {request.values}\nRequest data: {request.data}\n\nTwilio info:\n----------\nSID: {twilioSID}\nAuth token: {twilioAuthToken}\n\n")
				logFile.write(f'Tableau data:\n---------------\nUsername: {os.environ["TABLEAU_USERNAME"]}\nPassword: {os.environ["TABLEAU_PASSWORD"]}\nSite name: {os.environ["TABLEAU_SITENAME"]}\nTableau server: {os.environ["TABLEAU_SERVER"]}\n')
				tableauAuth = TSC.TableauAuth(os.environ["TABLEAU_USERNAME"], os.environ["TABLEAU_PASSWORD"], os.environ["TABLEAU_SITENAME"]) # Create an authorization object
				server = TSC.Server(os.environ["TABLEAU_SERVER"])
		
				with server.auth.sign_in(tableauAuth):
					allDatasources, paginationItem = server.datasources.get()
					logFile.write(f"There are {paginationItem.total_available} datasources on site\n")
					for dataSource in allDatasources:
						msgStr = f"Datasource refresh failed\n\tName: {dataSource.name}\n\tDescription: {dataSource.description}\n\tLast updated: {dataSource.updated_at}\nContent URL: {dataSource.content_url}\nCreated at: {dataSource.created_at}\nCertified: {dataSource.certified}\nCertification note: {dataSource.certification_note}\nType: {dataSource.datasource_type}\nEncrypt extracts: {dataSource.encrypt_extracts}\nHas extracts: {dataSource.has_extracts}\nID: {dataSource.id}\nOwner ID: {dataSource.owner_id}\nProject ID: {dataSource.project_id}\nProject name: {dataSource.project_name}\nUse remote query agent: {dataSource.use_remote_query_agent}\nWebpage URL: {dataSource.webpage_url}\nSending message from {sendingNumber} to {receivingNumber}\n\n"
						logFile.write(msgStr)
						textMessage = twilioClient.messages.create(
							body=msgStr,
							from_=sendingNumber,
							to=receivingNumber
						)
						logFile.write(f"Text message SID: {textMessage.sid}\nSending Whatsapp message from {whatsappFrom} to {whatsappTo}\n")
						whatsappMessage = twilioClient.messages.create(
							body=msgStr,
							from_=whatsappFrom,
							to=whatsappTo
						)
						logFile.write(f"Whatsapp message SID: {whatsappMessage.sid}\nCalling {receivingNumber} from {sendingNumber}\n")
						call = twilioClient.calls.create(
							to=receivingNumber,
							from_=sendingNumber,
							twiml=f"<Response><Say>{msgStr}</Say></Response>"
						)
						logFile.write(f"Call SID: {call.sid}")
	

		return "Success"
	
	else:
		return f"""Unimplemented"""

if __name__ == "__main__":
	app.run()
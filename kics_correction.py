#!/usr/bin/python3

# Generic includes
import json
import argparse
import re

# Default varirables
input_file="sonarqube-results.json"
output_file="sonarqube-results.json"

# Initialize parser
parser = argparse.ArgumentParser()
parser.add_argument("-o", "--output", help = "Output file")
parser.add_argument("-i", "--input", help = "Input file")
parser.add_argument("-f", "--filepath_correction", action='store_true', help = "Correct the filePath key - value of the sonarqube-results.json file")

args = parser.parse_args()

if args.output is not None:
    output_file=args.output
if args.input is not None:
    input_file=args.input

# Convert file to python json object
with open(input_file, 'r') as f:
  data = json.load(f)

# Correct the loaded json
def correction(json_part):
  
  # We retrieve every information from each secondaryLocations key
  file_path = json_part['secondaryLocations']
  json_to_return = ''
  
  # Default and mendatory information to provide to sonarqube are the following : 
  basic = {"engineId": json_part['engineId'],
			"ruleId": json_part['ruleId'],
			"severity": json_part['severity'],
			"type": json_part['type'],
			"primaryLocation": {
				"message": json_part['primaryLocation']['message'],
				"filePath": json_part['primaryLocation']['filePath'],
				"textRange": {
					"startLine": json_part['primaryLocation']['textRange']['startLine']
			}
		}
  }

  json_to_return = json.dumps(basic, indent=4)[1:]

  # For each secondaryLocation item we will create a new issue so it can be interpreted by sonarqube
  for j in range(0, len(file_path)):
    to_merge = {
      "engineId": json_part['engineId'],
			"ruleId": json_part['ruleId'],
			"severity": json_part['severity'],
			"type": json_part['type'],
      # We can copy almost all information as they are the same from the primary location except for the startLine and filePath
      # Which we will retrieve from the secondaryLocation itself
			"primaryLocation": {
				"message": json_part['primaryLocation']['message'],
				"filePath": file_path[j]['filePath'],
				"textRange": {
					"startLine": file_path[j]['textRange']['startLine']
				  }
			  }
    }
    # We merge all our json output
    json_to_return += json.dumps(to_merge, indent=4)
  
  return json_to_return


# Check if vulnerability has a secondary Location
for i in range(0, len(data['issues'])):
  if 'secondaryLocations' in data['issues'][i]:
    # When a secondaryLocations if found within one issue we replaced it with our modified one
    # So that we remove every secondaryLocations to replace them by new issue
    data['issues'][i] = correction(data['issues'][i])

# Format the json data as newline are not interpreted, \ are present to escape some characters and some json malformation that have to be corrected
formatted_output = json.dumps(data, ensure_ascii=True, indent=4).replace('"\\n', "{\n").replace('\\n', '\n').replace('\\', '').replace('}"', '}').replace('}{', '},\n{')

# If precised correct the filePath entry
if args.filepath_correction:
    formatted_output = re.sub('"filePath": "../../', '"filePath": "/', formatted_output)

# Write the output of the formmated string into the desired file
with open(output_file, 'w', encoding='utf-8') as f:
  f.write(formatted_output)

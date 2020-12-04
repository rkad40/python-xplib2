import os
import csv
import re
import yaml
import fs
import importlib.util as importer

DEBUG = False


def Worksheet(file=""):
    if file:
        ext = fs.get_ext(file).lower()
        if ext == "txt":
            return WorksheetTxtFileParser(file)
        if ext == "yml":
            return WorksheetYmlFileParser(file)
        else:
            raise Exception("Don't know how to process file \"{}\".".format(file))


def WorksheetTxtFileParser(file):

    # Initialize variables.
    type = None
    version = None
    file = fs.get_abs_path(file)

    # Read first line of file to get type and version.
    with open(file, newline='') as csv_file_object:
        csv_file_stream = csv.reader(csv_file_object, dialect='excel-tab')
        for row in csv_file_stream:
            cell = row[0]
            m = re.search('^(\w+)', cell)
            if not m: raise Exception("Worksheet type not defined.")
            # Example type: "DTEdgesetSheet".
            type = m.group(1)
            # Convert type to lower case; strip leading "dt"; strip trailing "sheet"
            # if found.
            type = type.lower()
            type = re.sub(r'^dt', '', type)
            type = re.sub(r'sheet$', '', type)
            # Get the sheet version.
            m = re.search('version=(\d+\.\d+)', cell)
            if not m: raise Exception("Worksheet version not defined.")
            version = float(m.group(1))
            # Break out of loop as we are only interested in reading the first line.
            # We do this to determine what type of worksheet this is and
            # subsequently what worksheet parser to use.
            break

    # Load worksheet module and create corresponding worksheet object.
    module_file = fs.join_names(fs.get_dir_name(fs.get_abs_path(__file__)), 'sheets', type, str(version) + ".py")
    if DEBUG: print("Loading \"{}\" ...".format(module_file))
    if not fs.file_exists(module_file): raise Exception("File \"{}\" does not exist.".format(module_file))
    spec = importer.spec_from_file_location(name="", location=module_file)
    module_spec = importer.module_from_spec(spec)
    spec.loader.exec_module(module_spec)
    worksheet = module_spec.Worksheet()
    worksheet.read_txt_file(file)
    return(worksheet)


def WorksheetYmlFileParser(file):

    # Initialize variables.
    type = None
    version = None
    file = fs.get_abs_path(file)
    
    # Load YAML data.
    stream = open(file, 'r')
    data = yaml.load(stream)
    
    # Verify that type and version are defined.
    if 'Info' not in data: raise Exception("File \"{}\" does not appear to be an IG-XL worksheet YML.".format(file))
    if 'Type' not in data['Info']: raise Exception("File \"{}\" does not appear to be an IG-XL worksheet YML.".format(file))
    if 'Version' not in data['Info']: raise Exception("File \"{}\" does not appear to be an IG-XL worksheet YML.".format(file))
    
    # Get type and version.
    type = data['Info']['Type']
    version = data['Info']['Version']
    
    # Convert type to lower case; strip leading "dt"; strip trailing "sheet"
    # if found.
    type = type.lower()
    type = re.sub(r'^dt', '', type)
    type = re.sub(r'sheet$', '', type)
    
    # Convert version to float.
    version = float(version)

    # Load worksheet module and create corresponding worksheet object.
    module_file = fs.join_names(fs.get_dir_name(fs.get_abs_path(__file__)), 'sheets', type, str(version) + ".py")
    if DEBUG: print("Loading \"{}\" ...".format(module_file))
    if not fs.file_exists(module_file): raise Exception("File \"{}\" does not exist.".format(module_file))
    spec = importer.spec_from_file_location(name="", location=module_file)
    module_spec = importer.module_from_spec(spec)
    spec.loader.exec_module(module_spec)
    worksheet = module_spec.Worksheet()
    worksheet.data = data
    return(worksheet)



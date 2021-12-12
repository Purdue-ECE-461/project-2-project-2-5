
from flask import Flask, request, jsonify, Blueprint
import nacl.pwhash
from secrets import token_urlsafe
from datetime import datetime, timedelta

app = Flask(__name__)
import google.cloud.datastore as datastore
from google.cloud import secretmanager
import json
import sys
sys.path.append("project1")
from project1.CLIHandler import CLIHandler

@app.route("/")
def homepage():
    return "<p>Hello, World!</p>"

# @app.route("/<id>")
# def newhome(id):
#     return "<p>Hello, World! </p>" + id

# @app.route("/https://ece461.purdue.edu/project2/package", methods=['POST'])
# def upload_blob(bucket_name, source_file_name, destination_blob_name):
#     storage_client = storage.Client()
#     # gcp_json_credentials_dict = json.loads(gcp_credentials_string)
#     # credentials = service_account.Credentials.from_service_account_info(gcp_json_credentials_dict)
#     # storage_client = storage.Client(project=gcp_json_credentials_dict['project-2-331602'], credentials=credentials)
#     bucket = storage_client.bucket(bucket_name)
#     blob = bucket.blob(destination_blob_name)
#     # image = Image.open(source_file_name)
#     # fs = FileStorage()
#     # image.save(fs, format="JPEG")
#     blob.upload_from_filename(source_file_name)

#     print("File {} uploaded to {}.".format(source_file_name,destination_blob_name))


@app.route("/package", methods=['POST'])
def callHandler():
    dataFull = request.json
    try:
        metadata = dataFull["metadata"]
        data = dataFull["data"]
    except:
        return "", 403

    if "Content" in data.keys():
        returnvVal, responseVal = create(metadata, data)
    else :
        returnvVal,responseVal = ingestion(metadata, data)
    
    return returnvVal,responseVal

def create(metadata, data):
    if len(data) != 2 or len(metadata) != 3 or "ID" not in metadata or "Name" not in metadata or "Version" not in metadata or "Content" not in data or "JSProgram" not in data or data["Content"] == "<base-64>" or len(metadata["Version"].split('.')) != 3:
        return "", 400

    data_client = datastore.Client()
    query = data_client.query(kind = "package")
    query.add_filter("id", "=", metadata["ID"])
    query.add_filter("name", "=", metadata["Name"])
    query.add_filter("version", "=", metadata["Version"])
    queryList = list(query.fetch())
    if len(queryList) > 0:
        return "", 403

    # Check Token
    auth_token = request.headers.get('X-Authorization')
    token = auth_token.split()[1]

    data_client = datastore.Client()
    q_lookup = data_client.query(kind='Users')
    q_lookup.add_filter("token", "=", token)
    res = list(q_lookup.fetch())
    error = { "code": -1, "message": "An error occurred while validating the user"}

    if len(res) != 1:
        return error, 401

    # DO Package creation
    full_key = data_client.key("package", metadata["Name"] + ": " + metadata["Version"] + ": " + metadata["ID"])
    newEntity = datastore.Entity(key=full_key, exclude_from_indexes=["content"])

    newEntity["name"] = metadata["Name"]
    newEntity["version"] = metadata["Version"]
    version = metadata["Version"].split('.')
    newEntity["id"] = metadata["ID"]
    newEntity["content"] = data["Content"]
    newEntity["url"] = ""
    newEntity["jsprogram"] = data["JSProgram"]
    newEntity["major"] = int(version[0])
    newEntity["minor"] = int(version[1])
    newEntity["patch"] = int(version[2])

    data_client.put(newEntity)
    for user in q_lookup.fetch():
        full_key = data_client.key("UserActions", metadata["Name"] + ": " + metadata["Version"] + ": " + metadata["ID"] + ": " + user["name"] +": CREATE")
        newUserEntity = datastore.Entity(key=full_key)
        newUserEntity["userName"] = user["name"]
        newUserEntity["userIsAdmin"] = user["isAdmin"]
        newUserEntity["packageName"] = metadata["Name"]
        newUserEntity["packageVersion"] = metadata["Version"]
        newUserEntity["packageID"] = metadata["ID"]
        newUserEntity["Date"] = datetime.now()
        newUserEntity["Action"] = "CREATE"
        data_client.put(newUserEntity)
    return metadata, 201

def ingestion(metadata, data):
    if len(data) != 2 or len(metadata) != 3 or "ID" not in metadata or "Name" not in metadata or "Version" not in metadata or "URL" not in data or "JSProgram" not in data:
        return "", 400
    
    # Check Token
    auth_token = request.headers.get('X-Authorization')
    token = auth_token.split()[1]

    data_client = datastore.Client()
    q_lookup = data_client.query(kind='Users')
    q_lookup.add_filter("token", "=", token)
    res = list(q_lookup.fetch())
    error = { "code": -1, "message": "An error occurred while validating the user"}

    if len(res) != 1:
        return error, 401

    # Do ingestion
    url = data["URL"]
    cli = CLIHandler(url)
    cli.calc()
    # net, rampUp, correctness, bus_factor, responsiveness, license_score, dependency_score
    # cli.print_to_console()
    scores = cli.getScores()
    print(scores)
    
    for score in scores:
        if score < 0.5:
            return "scores were bad", 200

    data_client = datastore.Client()
    query = data_client.query(kind = "package")
    query.add_filter("id", "=", metadata["ID"])
    query.add_filter("name", "=", metadata["Name"])
    query.add_filter("version", "=", metadata["Version"])
    queryList = list(query.fetch())
    if len(queryList) != 1:
        return "error in retrieving package", 400

    # full_key = data_client.key("package", metadata["Name"] + ": " + metadata["Version"] + ": " + metadata["ID"])
    for package in query.fetch():
        if package["url"] != "":
            return "URL already exists", 403
        package["url"] = data["URL"]
        data_client.put(package)
    
    for user in q_lookup.fetch():
        full_key = data_client.key("UserActions", metadata["Name"] + ": " + metadata["Version"] + ": " + metadata["ID"] + ": " + user["name"] +": INGEST")
        newUserEntity = datastore.Entity(key=full_key)
        newUserEntity["userName"] = user["name"]
        newUserEntity["userIsAdmin"] = user["isAdmin"]
        newUserEntity["packageName"] = metadata["Name"]
        newUserEntity["packageVersion"] = metadata["Version"]
        newUserEntity["packageID"] = metadata["ID"]
        newUserEntity["Date"] = datetime.now()
        newUserEntity["Action"] = "INGEST"
        data_client.put(newUserEntity)

    return metadata, 201
    
    """
    try:
        #x_auth = header.split()
        #print(x_auth)

        # function calls for authentication:
        # use x_auth[1], x_auth[2]

        #dataFull = json.loads(data_raw)
        #data = json.loads(dataFull["data"])
        
        url = data["URL"]
        cli = CLIHandler([url])
        cli.calc()
        cli.print_to_console()

        return metadata

    except:
        if request != "https://ece461.purdue.edu/project2/package":
            raise NameError(request)
        if x_auth[0] != "X-Authorization:":
            raise NameError(header)
        else:
            raise Exception()
    """

@app.route("/package/<id>", methods=['GET'])
def getPackageByID(id):
    # Get Auth Token
    auth_token = request.headers.get('X-Authorization')
    token = auth_token.split()[1]

    data_client = datastore.Client()
    q_lookup = data_client.query(kind='Users')
    q_lookup.add_filter("token", "=", token)
    res = list(q_lookup.fetch())
    error = { "code": -1, "message": "An error occurred while validating the user"}

    if len(res) != 1:
        return error, 500
    
    metadata = {}
    data = {}
    dataFull = {}
    error = { "code": -1, "message": "An error occurred while retrieving package"}
    
    data_client = datastore.Client()
    query = data_client.query(kind = "package")
    query.add_filter("id", "=", id)
    i = 0
    for package in query.fetch():
        i = i + 1
        metadata["Name"] = package["name"]
        metadata["Version"] = package["version"]
        metadata["ID"] = package["id"]
        data["Content"] = package["content"]
        data["URL"] = package["url"]
        data["JSProgram"] = package["jsprogram"]

    if i != 1:
        return error, 500
    
    dataFull["metadata"] = metadata
    dataFull["data"] = data
    for user in q_lookup.fetch():
        full_key = data_client.key("UserActions", metadata["Name"] + ": " + metadata["Version"] + ": " + metadata["ID"] + ": " + user["name"] +": DOWNLOAD BY ID")
        newUserEntity = datastore.Entity(key=full_key)
        newUserEntity["userName"] = user["name"]
        newUserEntity["userIsAdmin"] = user["isAdmin"]
        newUserEntity["packageName"] = metadata["Name"]
        newUserEntity["packageVersion"] = metadata["Version"]
        newUserEntity["packageID"] = metadata["ID"]
        newUserEntity["Date"] = datetime.now()
        newUserEntity["Action"] = "DOWNLOAD BY ID"
        data_client.put(newUserEntity)
        
    return dataFull, 200

    # except:
    #     # if request != "https://ece461.purdue.edu/project2/package/" + id:
    #     #     raise NameError(request)
    #     # if x_auth[0] != "X-Authorization:":
    #     #     raise NameError(header)
    #     # if package.id != id:
    #     #     raise NameError(id)
    #     if i > 1:
    #         return error, 500
    #     # else:
    #     #     raise Exception()
    #     pass

@app.route("/package/<id>", methods=['PUT'])
def packageUpdate(id):
    # Get Token
    # auth_token = request.headers.get('X-Authorization')
    # token = auth_token.split()[1]

    # data_client = datastore.Client()
    # q_lookup = data_client.query(kind='Users')
    # q_lookup.add_filter("token", "=", token)
    # res = list(q_lookup.fetch())
    # error = { "code": -1, "message": "An error occurred while validating the user"}

    # if len(res) != 1:
    #     return error, 500

    request.get_data()
    dat = request.data.decode("utf-8")
    dataFull = json.loads(dat)

    # dataFull = request.json
    metadata = dataFull["metadata"]
    data = dataFull["data"]
    # id = metadata["ID"]

    if metadata["ID"] != id:
       return metadata["ID"] + " : " + id + " : " + dataFull, 400

    # data_client = datastore.Client()
    # query = data_client.query(kind = "package")
    # query.add_filter("id", "=", metadata["ID"])
    # query.add_filter("name", "=", metadata["Name"])
    # query.add_filter("version", "=", metadata["Version"])
    # queryList = list(query.fetch())
    # if len(queryList) != 1:
    #     return "No such package", 400

    # for package in query.fetch():
    #     package["content"] = data["Content"]
    #     package["url"] = data["URL"]
    #     package["jsprogram"] = data["JSProgram"]

    # data_client.put(package)
    # for user in q_lookup.fetch():
    #     full_key = data_client.key("UserActions", metadata["Name"] + ": " + metadata["Version"] + ": " + metadata["ID"] + ": " + user["name"] +": UPDATE")
    #     newUserEntity = datastore.Entity(key=full_key)
    #     newUserEntity["userName"] = user["name"]
    #     newUserEntity["userIsAdmin"] = user["isAdmin"]
    #     newUserEntity["packageName"] = metadata["Name"]
    #     newUserEntity["packageVersion"] = metadata["Version"]
    #     newUserEntity["packageID"] = metadata["ID"]
    #     newUserEntity["Date"] = datetime.now()
    #     newUserEntity["Action"] = "UPDATE"
    #     data_client.put(newUserEntity)
    return dataFull, 200

@app.route("/package/<id>", methods=['DELETE'])
def deletePackage(id):
    # Check Token
    auth_token = request.headers.get('X-Authorization')
    token = auth_token.split()[1]

    data_client = datastore.Client()
    q_lookup = data_client.query(kind='Users')
    q_lookup.add_filter("token", "=", token)
    res = list(q_lookup.fetch())
    error = { "code": -1, "message": "An error occurred while validating the user"}

    if len(res) != 1:
        return error, 500
    
    data_client = datastore.Client()
    query = data_client.query(kind = "package")
    query.add_filter("id", "=", id)
    queryList = list(query.fetch())
    if len(queryList) != 1:
        return 400
    for package in query.fetch():
        # i = i + 1
        key = data_client.key("package", package["name"] + ": " + package["version"] + ": " + package["id"])
        data_client.delete(key)

        for user in q_lookup.fetch():
            full_key = data_client.key("UserActions", package["name"] + ": " + package["version"] + ": " + package["id"] + ": " + user["name"] +": DELETE BY ID")
            newUserEntity = datastore.Entity(key=full_key)
            newUserEntity["userName"] = user["name"]
            newUserEntity["userIsAdmin"] = user["isAdmin"]
            newUserEntity["packageName"] = package["name"]
            newUserEntity["packageVersion"] = package["version"]
            newUserEntity["packageID"] = package["id"]
            newUserEntity["Date"] = datetime.now()
            newUserEntity["Action"] = "DELETE BY ID"
            data_client.put(newUserEntity)
    
    return "", 200
        
    # except:
    #     # if request != "https://ece461.purdue.edu/project2/package/" + id:
    #     #     raise NameError(request)
    #     # if x_auth[0] != "X-Authorization:":
    #     #     raise NameError(header)
    #     if i > 1:
    #         raise NameError(id)
    #     else:
    #         raise Exception()

@app.route("/package/byName/<name>", methods=['GET'])
def getPackageByName(name):
    # try:
    # x_auth = header.split()
    # print(x_auth)
    
    # function calls for authentication:
    # use x_auth[1], x_auth[2]

    auth_token = request.headers.get('X-Authorization')
    token = auth_token.split()[1]

    data_client = datastore.Client()
    q_lookup = data_client.query(kind='Users')
    q_lookup.add_filter("token", "=", token)
    res = list(q_lookup.fetch())
    error = { "code": -1, "message": "An error occurred while validating the user"}

    if len(res) != 1:
        return error, 500

    data_client = datastore.Client()
    query = data_client.query(kind = "UserActions")
    query.add_filter("packageName", "=", name)
    queryList = list(query.fetch())
    if len(queryList) == 0:
        return "", 400

    returnList = []

    for package in query.fetch():
        newDict = {}
        newDict["User"] = {} 
        newDict["User"]["name"] = package["userName"]
        newDict["User"]["isAdmin"] = package["userIsAdmin"]
        newDict["Date"] = package["Date"]
        newDict["PackageMetadata"] = {}
        newDict["PackageMetadata"]["Name"] = package["packageName"]
        newDict["PackageMetadata"]["Version"] = package["packageVersion"]
        newDict["PackageMetadata"]["ID"] = package["packageID"]
        newDict["Action"] = package["Action"]
        returnList.append(newDict)

    returnList.sort(key=sortByDateHelper)

    return jsonify(returnList)
    # except:
    #     if request != "https://ece461.purdue.edu/project2/package/" + name:
    #         raise NameError(request)
    #     if x_auth[0] != "X-Authorization:":
    #         raise NameError(header)
    #     if idCheck != id:
    #         raise NameError(id)
    #     else:
    #         raise Exception()
def sortByDateHelper(inputDict):
    return inputDict["Date"]

@app.route("/package/byName/<name>", methods=['DELETE'])
def deleteAllVersions(name):
    auth_token = request.headers.get('X-Authorization')
    token = auth_token.split()[1]

    data_client = datastore.Client()
    q_lookup = data_client.query(kind='Users')
    q_lookup.add_filter("token", "=", token)
    res = list(q_lookup.fetch())
    error = { "code": -1, "message": "An error occurred while validating the user"}

    if len(res) != 1:
        return error, 500
    data_client = datastore.Client()
    query = data_client.query(kind = "package")
    query.add_filter("name", "=", name)
    queryList = list(query.fetch())
    if len(queryList) == 0:
        return "", 400

    for package in query.fetch():
        key = data_client.key("package", package["name"] + ": " + package["version"] + ": " + package["id"])
        data_client.delete(key)
    
        for user in q_lookup.fetch():
            full_key = data_client.key("UserActions", package["name"] + ": " + package["version"] + ": " + package["id"] + ": " + user["name"] +": DELETE ALL VERSIONS BY NAME")
            newUserEntity = datastore.Entity(key=full_key)
            newUserEntity["userName"] = user["name"]
            newUserEntity["userIsAdmin"] = user["isAdmin"]
            newUserEntity["packageName"] = package["name"]
            newUserEntity["packageVersion"] = package["version"]
            newUserEntity["packageID"] = package["id"]
            newUserEntity["Date"] = datetime.now()
            newUserEntity["Action"] = "DELETE ALL VERSIONS BY NAME"
            data_client.put(newUserEntity)

    return "", 200


@app.route("/package/<id>/rate", methods=['GET'])
def getPackageRate(id):
    url = ""
    data_client = datastore.Client()
    query = data_client.query(kind = "package")
    query.add_filter("id", "=", id)
    queryList = list(query.fetch())
    if len(queryList) != 1:
        return "", 400
    auth_token = request.headers.get('X-Authorization')
    token = auth_token.split()[1]

    data_client = datastore.Client()
    q_lookup = data_client.query(kind='Users')
    q_lookup.add_filter("token", "=", token)
    res = list(q_lookup.fetch())
    error = { "code": -1, "message": "An error occurred while validating the user"}

    if len(res) != 1:
        return error, 500
    info = {}
    for package in query.fetch():
        url = package["url"]
        cli = CLIHandler(url)
        cli.calc()
        # net, rampUp, correctness, bus_factor, responsiveness, license_score, dependency_score
        scores = cli.getScores()
        info["RampUp"] = scores[1]
        info["Correctness"] = scores[2]
        info["BusFactor"] = scores[3]
        info["ResponsiveMaintainer"] = scores[4]
        info["LicenseScore"] = scores[5]
        info["GoodPinningPractice"] = scores[6]
        for user in q_lookup.fetch():
            full_key = data_client.key("UserActions", package["name"] + ": " + package["version"] + ": " + package["id"] + ": " + user["name"] +": GET RATE FROM URL")
            newUserEntity = datastore.Entity(key=full_key)
            newUserEntity["userName"] = user["name"]
            newUserEntity["userIsAdmin"] = user["isAdmin"]
            newUserEntity["packageName"] = package["name"]
            newUserEntity["packageVersion"] = package["version"]
            newUserEntity["packageID"] = package["id"]
            newUserEntity["Date"] = datetime.now()
            newUserEntity["Action"] = "GET RATE FROM URL"
            data_client.put(newUserEntity)

    return info, 200
    # pass

@app.route("/authenticate", methods=['PUT'])
def getToken():
    request.get_data()
    sp_kind = 'Users'

    dat = request.data.decode("utf-8")
    body = json.loads(dat)

    try:
        name = body["User"]["name"]
        isAdmin = body["User"]["isAdmin"]
        passw_in = body["Secret"]["password"]
    except:
        response = {}
        return response, 401
    data_client = datastore.Client()

    q_lookup = data_client.query(kind=sp_kind)
    q_lookup.add_filter("name", "=", name)
    ret_serv = list(q_lookup.fetch())

    if len(ret_serv) == 1:
        key = data_client.key(sp_kind, name)
        data_user = data_client.get(key)
        data_passw = data_user["password"]
        try:
            res = nacl.pwhash.argon2id.verify(str.encode(data_passw), str.encode(passw_in))
            # res = passw_in
        except:
            response = ""
            return response, 401
            
        token = token_urlsafe(128)
        data_user["token"] = token
        exp_time = datetime.now() + timedelta(hours=10)
        data_user["expiration"] = exp_time
        data_user["api_uses"] = 0
        data_client.put(data_user)
        
        response = "bearer " + token
        return response, 200
    else:
        response = ""
        return response, 401


@app.route("/packages", methods=['POST'])
def getPackages():
    error = { "code": -1, "message": "An error occurred while retrieving package"}
    if request.args:
        offset = request.args["offset"]
        # currPage = [1,2,3..offset]
    else:
        offset = 1
        # currPage = 1

    dataList = request.json
    
    print(dataList)
    data_client = datastore.Client()
    
    returnList = []
    
    for package in dataList:
        # print("THIS IS THE PACKAGE")
        # print(package)
        if "Name" not in package or "Version" not in package:
            return error,500
        query = data_client.query(kind = "package")
        query.add_filter("name", "=", package["Name"])
        version = package["Version"].replace(" ","")
        version = version.replace("=","")
        version = version.replace("v","")
        if "-" in version:
            # print("range version: ",version)
            versions = version.split('-')
            startV_str = versions[0]
            endV_str = versions[1]
            startV = startV_str.split('.')
            endV = endV_str.split('.')
            # print("start: ",startV," end: ", endV)
            
            if len(startV) != 3 or len(endV) != 3:
                return error, 500
            # query.add_filter(("version".split(".")[0]), ">=", int(startV[0]))
            # query.add_filter(("version".split(".")[0]), "<=", int(endV[0]))
            # query.add_filter(("version".split(".")[1]), ">=", int(startV[1]))
            # query.add_filter(("version".split(".")[1]), "<=", int(endV[1]))
            # query.add_filter(("version".split(".")[2]), ">=", int(startV[2]))
            # query.add_filter(("version".split(".")[2]), "<=", int(endV[2]))
            
            for currPackage in query.fetch():
                # print(currPackage["version"], currPackage["major"], currPackage["minor"], currPackage["patch"])
                # print(int(startV[0]),int(startV[1]),int(startV[2]))
                # print(int(endV[0]),int(endV[1]),int(endV[2]))
                inBound = False
                if currPackage["major"] > int(startV[0]) and currPackage["major"] < int(endV[0]):
                    inBound = True
                if currPackage["major"] == int(startV[0]):
                    if currPackage["minor"] > int(startV[1]) and currPackage["major"] <= int(endV[0]):
                        inBound = True
                    elif currPackage["minor"] == int(startV[1]):
                        if currPackage["patch"] >= int(startV[2]):
                            inBound = True
                if currPackage["major"] == int(endV[0]):
                    if currPackage["minor"] > int(endV[1]):
                        inBound = False
                    elif currPackage["minor"] == int(endV[1]):
                        if currPackage["patch"] > int(endV[2]):
                            inBound = False
                if inBound == True:
                    info = {}
                    info["Name"] = package["Name"]
                    info["Version"] = currPackage["version"]
                    info["ID"] = currPackage["id"]
                    # print("THIS WORKED: ", info)
                    returnList.append(info)
                    # print("RANGE: ", returnList)

        elif "~" in version:
            # print("tilda version: ",version)
            version = version.replace("~","")
            currV = version.split('.')
            if len(currV) == 3:
                # query.add_filter("major", "=", int(currV[0]))
                # query.add_filter("minor", "=", int(currV[1]))
                # query.add_filter("patch", ">=", int(currV[2]))
                for currPackage in query.fetch():
                    if currPackage["major"] == int(currV[0]) and currPackage["minor"] == int(currV[1]) and currPackage["patch"] >= int(currV[2]):
                        info = {}
                        info["Name"] = package["Name"]
                        info["Version"] = currPackage["version"]
                        info["ID"] = currPackage["id"]
                        returnList.append(info)
                        # print("TIL: ", returnList)
            elif len(currV) == 2:
                # query.add_filter("major", "=", int(currV[0]))
                # query.add_filter("minor", "=", int(currV[1]))
                for currPackage in query.fetch():
                    if currPackage["major"] == int(currV[0]) and currPackage["minor"] == int(currV[1]):
                        info = {}
                        info["Name"] = package["Name"]
                        info["Version"] = currPackage["version"]
                        info["ID"] = currPackage["id"]
                        returnList.append(info)
                        # print("TIL: ", returnList)
            elif len(currV) == 1:
                # query.add_filter("major", "=", int(currV[0]))
                for currPackage in query.fetch():
                    if currPackage["major"] == int(currV[0]):
                        info = {}
                        info["Name"] = package["Name"]
                        info["Version"] = currPackage["version"]
                        info["ID"] = currPackage["id"]
                        returnList.append(info)
                        # print("TIL: ", returnList)
            else:
                return error, 500

        elif "^" in version:
            # print("carrot version: ",version)
            version = version.replace("^","")
            currV = version.split('.')
            if len(currV) != 3:
                return error, 500
            if int(currV[0]) != 0:
                # print("going to full carrot")
                # query.add_filter("major", "=", int(currV[0]))
                # query.add_filter("minor", ">=", int(currV[1]))
                # query.add_filter("patch", ">=", int(currV[2]))
                for currPackage in query.fetch():
                    if currPackage["major"] == int(currV[0]) and currPackage["minor"] >= int(currV[1]) and currPackage["patch"] >= int(currV[2]):
                        info = {}
                        info["Name"] = package["Name"]
                        info["Version"] = currPackage["version"]
                        info["ID"] = currPackage["id"]
                        returnList.append(info)
                        # print("CAR: ", returnList)
            elif int(currV[0]) == 0 and int(currV[1]) != 0:
                # print("going to minor carrot")
                # query.add_filter("major", "=", int(currV[0]))
                # query.add_filter("minor", "=", int(currV[1]))
                # query.add_filter("patch", ">=", int(currV[2]))
                for currPackage in query.fetch():
                    if currPackage["major"] == int(currV[0]) and currPackage["minor"] == int(currV[1]) and currPackage["patch"] >= int(currV[2]):
                        info = {}
                        info["Name"] = package["Name"]
                        info["Version"] = currPackage["version"]
                        info["ID"] = currPackage["id"]
                        returnList.append(info)
                        # print("CAR: ", returnList)
            else:
                # print("going to patch carrot")
                # query.add_filter("major", "=", int(currV[0]))
                # query.add_filter("minor", "=", int(currV[1]))
                # query.add_filter("patch", "=", int(currV[2]))
                for currPackage in query.fetch():
                    if currPackage["major"] == int(currV[0]) and currPackage["minor"] == int(currV[1]) and currPackage["patch"] == int(currV[2]):
                        info = {}
                        info["Name"] = package["Name"]
                        info["Version"] = currPackage["version"]
                        info["ID"] = currPackage["id"]
                        returnList.append(info)
                        # print("CAR: ", returnList)

        else:
            # print("EXACT VERSION: ",version)
            info = {}
            info["Name"] = package["Name"]
            query.add_filter("version", "=", version)
            i = 0
            for currPackage in query.fetch():
                # print("in exact for loop")
                i = i + 1
                info["Version"] = currPackage["version"]
                info["ID"] = currPackage["id"]
                if i != 1:
                    return error, 500
            if "Version" in info:
                # print(info)
                returnList.append(info)
                # print("EXACT: ", returnList)
    # print(returnList)
    if len(returnList) > 10:
        # if offset == 1:
        if 10*(offset - 1) < (len(returnList) - 1):
            paginatedList = returnList[10*(offset-1) : min(10*(offset), len(returnList) - 1)]
            return jsonify(paginatedList),200
        else:
            paginatedList = returnList[len(returnList) - 11, len(returnList) - 1]
            return jsonify(paginatedList),200

    else:
        return jsonify(returnList), 200



@app.route("/reset", methods=['DELETE'])
def deleteRegistry():
    
    # Check authentication
    auth_token = request.headers.get('X-Authorization')
    token = auth_token.split()[1]

    data_client = datastore.Client()
    q_lookup = data_client.query(kind='Users')
    q_lookup.add_filter("token", "=", token)
    res = list(q_lookup.fetch())

    if len(res) != 1:
        response = ""
        return response, 401

    for user in q_lookup.fetch():
        if user["isAdmin"] not in ["true", "True", True]:
            return "", 401

    data_client = datastore.Client()
    query = data_client.query(kind = "package")
    for package in query.fetch():
        key = data_client.key("package", package["name"] + ": " + package["version"] + ": " + package["id"])
        data_client.delete(key)

    actionQuery = data_client.query(kind="UserActions")
    for package in actionQuery.fetch():
        full_key = data_client.key("UserActions", package["packageName"] + ": " + package["packageVersion"] + ": " + package["packageID"] + ": " + package["userName"] +": " + package["Action"])
        data_client.delete(full_key)
    
    userQuery = data_client.query(kind="Users")
    for entity in userQuery.fetch():
        full_key = data_client.key("Users", entity["name"])
        data_client.delete(full_key)
        
    
    registration_key = data_client.key("Users", "ece461defaultadminuser")
    newEntity = datastore.Entity(key=registration_key)
    newEntity["name"] = "ece461defaultadminuser"
    newEntity["isAdmin"] = "True"
    newEntity["password"] = '$argon2id$v=19$m=262144,t=3,p=1$W5DDEKOSVOdysF/f2H4SbA$V0cwX7eh4rMSstY1UzGFuHHiHpg2B8fKbjzs2goEO9A'
    newEntity["token"] = ""
    newEntity["expiration"] = ""
    data_client.put(newEntity)

    return "", 200

@app.route("/register", methods=['POST'])
def createUser():
    # passw = the plaintext password string, don't worry about the other arguments
    recv_json = request.get_json()

    auth_token = request.headers.get('X-Authorization')
    token = auth_token.split()[1]
    print("token" + token)

    data_client = datastore.Client()
    q_lookup = data_client.query(kind='Users')
    q_lookup.add_filter("token", "=", token)
    res = list(q_lookup.fetch())

    if len(res) != 1:
        response = ""
        return response, 401

    for user in q_lookup.fetch():
        if user["isAdmin"] not in ["true", "True", True]:
            return "", 401
    
    # full_key = data_client.key("Users", username)
    try:
        regis_name = recv_json["User"]["name"]
        regis_isAdmin = recv_json["User"]["isAdmin"]
        regis_passw = recv_json["Secret"]["password"]
    except:
        response = ""
        return response, 401
    
    registration_key = data_client.key("Users", regis_name)

    newEntity = datastore.Entity(key=registration_key)
    newEntity["name"] = regis_name
    newEntity["isAdmin"] = regis_isAdmin

    bytes_passw = str.encode(regis_passw) # Convert to Bytes string
    hashed_passw = nacl.pwhash.argon2id.str(bytes_passw, opslimit=nacl.pwhash.OPSLIMIT_MODERATE, memlimit=nacl.pwhash.MEMLIMIT_MODERATE)
    final_passw = hashed_passw.decode("utf-8")
    #final_passw = regis_passw
    newEntity["password"] = final_passw # stored as string

    newEntity["token"] = ""
    newEntity["expiration"] = ""
    data_client.put(newEntity)
    response = {"message" : "Successfully created new user."}
    return response, 200

@app.route("/register/admin", methods=["POST"])
def createAdmin():
    error = "Incorrect administrative password"
    auth_pw = request.headers.get('X-Authorization')
    if auth_pw != "adminPassword":
        return error, 401
    recv_json = request.json
    print(recv_json)
    try:
        regis_name = recv_json["User"]["name"]
        regis_isAdmin = recv_json["User"]["isAdmin"]
        regis_passw = recv_json["Secret"]["password"]
    except:
       
        response = "hello"
        return response, 401

    data_client = datastore.Client()
    registration_key = data_client.key("Users", regis_name)

    newEntity = datastore.Entity(key=registration_key)
    newEntity["name"] = regis_name
    newEntity["isAdmin"] = regis_isAdmin
    bytes_passw = str.encode(regis_passw) # Convert to Bytes string
    hashed_passw = nacl.pwhash.argon2id.str(bytes_passw, opslimit=nacl.pwhash.OPSLIMIT_MODERATE, memlimit=nacl.pwhash.MEMLIMIT_MODERATE)
    final_passw = hashed_passw.decode("utf-8")
    #final_passw = regis_passw
    newEntity["password"] = final_passw 
    newEntity["token"] = ""
    newEntity["expiration"] = ""
    data_client.put(newEntity)
    response = {"message" : "Successfully created new user."}
    return response, 200

if __name__ == "__main__":
    app.run(port=8080, debug=True)

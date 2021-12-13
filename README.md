# ECE 46100 Fall 2021 Team 5, Project 1
project-2-project-2-5 created by GitHub Classroom

## Introduction

This project is a Flask application that serves as a package repository. It uploads, downloads, updates, and rates packages that are stored as entities in Google Datastore.

## Startup
In order to use this tool, first clone the repository and change your current working directory to the root of the cloned repository.
There are three different commands that are accepted.
First, the dependencies must be installed to a virtual environment. To do this, run the command ```bash ./run.sh install``` on the command line interface. This will install all needed dependencies within a virtual environment.

After all dependencies are installed, you can then begin to run the environment. The system runs [here](https://project-2-331602.uc.r.appspot.com/) and is deployed by Google App Engine. 

To run the app, run  ```bash ./run.sh```. To deploy the app Google App Engine (with appropriate permissions), run the following command in terminal:
```gcloud deploy app```

## Usage
To interact with the app, you can send requests using [this link](https://go.postman.co/workspace/Team-Workspace~cd32ddf6-19ca-4a76-8445-250dc8989b0d/collection/18650989-01a09883-c276-44ea-9d79-61b905fce095). 

There are multiple different kinds of requests that the system can handle, which are laid out below.

### Package Functions:

* Create a package: ```POST https://project-2-331602.uc.r.appspot.com/package``` 
    * This will create a package in Datastore if the package does not already exist. This action tracks the user, and thus requires an "X-Authorization" field in the form of "bearer \<token>" in the header. The body of this request is the package contents and is a JSON object with the following structure:
    ```
    {
        "metadata": {
            "Name": String,
            "Version": String (major, minor, and patch number required),
            "ID": String (must be unique from all other packages in the repository)
        },
        "data": {
            "Content": (base-64 encoded content),
            "JSProgram": String
        }
    }
    ```
* Ingest a package: ```POST https://project-2-331602.uc.r.appspot.com/package```
    * This will ingest a package using an implementation of Project 1 by taking the input URL and determining scores for the Ramp Up time, Correctness, Bus Factor, Responsiveness, Licenses, and Good Pinning Practice. If the scores (which are between 0 and 1) are at LEAST 0.5 for all metrics, the package will be ingested and the URL will be placed in the relevant spot in the Datastore entry, as well as each of the individual scores for the specific package. This action tracks the user, and thus requires an "X-Authorization" field in the form of "bearer \<token>" in the header. The body of this request is the package metadata as well as the package URL and is a JSON object with the following structure:
    ```
    {
        "metadata": {
            "Name": String,
            "Version": String (major, minor, and patch number required),
            "ID": String (must be unique from all other packages in the repository)
        },
        "data": {
            "URL": String (GitHub or nppmjs link),
            "JSProgram": String
        }
    }
    ```
* Get a package (by ID): ```GET https://project-2-331602.uc.r.appspot.com/package/:id```
    * This will fetch the relevant package from the registry using the unique ID provided by the user. It will return an error if the action cannot be completed as desired. This action tracks the user, and thus requires an "X-Authorization" field in the form of "bearer \<token>" in the header. The body of this request is empty.
* Update a package (by ID): ```PUT https://project-2-331602.uc.r.appspot.com/package/:id```
    * This will update the relevant package from the registry with new "Content", a new "URL", and a new "JSProgram". It will return an error if the action cannot be completed as desired. This action tracks the user, and thus requires an "X-Authorization" field in the form of "bearer \<token>" in the header. The body of this request is the package metadata and updated package data in the form of a JSON object with the following structure:
    ```
    {
        "metadata": {
            "Name": String,
            "Version": String (major, minor, and patch number required),
            "ID": String (must be unique from all other packages in the repository)
        },
        "data": {
            "Content": (base-64 encoded content),
            "URL": String (GitHub or nppmjs link),
            "JSProgram": String
        }
    }
    ```
* Deleta a package (by ID): ```DELETE https://project-2-331602.uc.r.appspot.com/package/:id```
    * This will delete the relevant package from the registry using the unique ID provided by the user. It will return an error if the action cannot be completed as desired. This action tracks the user, and thus requires an "X-Authorization" field in the form of "bearer \<token>" in the header. The body of this request is empty.
* Get package(s) (by Name): ```GET https://project-2-331602.uc.r.appspot.com/package/byName/:name```
    * This will fetch all versions of a package with the specified name provided by the user. It returns a chronological list of all actions taken on all versions of the package by any user in the registry. The information includes the user's name, administrator status, the date the action was taken, the metadata of the package that the action affected, and a description of the action itself. It will return an error if the action cannot be completed as desired. This action tracks the user, and thus requires an "X-Authorization" field in the form of "bearer \<token>" in the header. The body of this request is empty.
* Delete package(s) (by Name): ```DELETE https://project-2-331602.uc.r.appspot.com/package/byName/:name```
    * This will delete all package from the registry with the specified name provided by the user. It will return an error if the action cannot be completed as desired. This action tracks the user, and thus requires an "X-Authorization" field in the form of "bearer \<token>" in the header. The body of this request is empty.
* Get package rate (by ID): ```GET https://project-2-331602.uc.r.appspot.com/package/:id```
    * This will return the scores for each of the individual metrics (Ramp Up time, Correctness, Bus Factor, Responsiveness, Licenses, and Good Pinning Practice) for the package in the registry with the unique ID matching the specified ID provided by the user. It will return an error if the action cannot be completed as desired. This action tracks the user, and thus requires an "X-Authorization" field in the form of "bearer \<token>" in the header. The body of this request is empty.
* Get package(s): ```GET https://project-2-331602.uc.r.appspot.com/packages```
    * This will return all packages in the registry that match the name and version(s) specified in the request body. There are four different ways to specify the version number:
        * Bounded range (inclusive): 1.2.3-4.5.6 (no spaces allowed, must specify the major, minor, and patch number for both upper and lower bounds)
        * ^: ^1.2.3 (must specify the major, minor, and patch number)
        * ~: ~1.2.3 (must specify at LEAST the major number)
        * Exact: 1.2.3 (must specify the major, minor, and patch number)
    * The body of the request contains a list JSON objects of the name(s) of the package(s) as well as the version number(s) that the user is trying to see. The request has the following form:
    ```
    [
        {
            "Version": String (as described above),
            "Name": String
        },
        ...
    ]
    ```
* Reset registry: ```DELETE https://project-2-331602.uc.r.appspot.com/reset```
    * This will clear the registry completely of all packages and users, as well as clearing the history of all user actions. This requires administrator status. It will reset the default administrator to have no token, so in order for the registry to be used once again, the default administrative user must be re-authenticated. This will return an error if the action cannot be completed as desired. The body of this request is empty.

### User Functions:

* Create User: ```POST https://project-2-331602.uc.r.appspot.com/register```
    * This will create a new user in the registry, with the properties of the request body. Only administrators have the ability to create users. This will return an error if the action cannot be completed as desired. The body of the request is the new user's name, administrator status, and password as a JSON object with the following structure:
    ```
    {
        "User": {
            "name": String,
            "isAdmin": Bool (True or False)
        },
        "Secret": {
            "password": String
        }
    }
    ```
* Authenticate: ```PUT https://project-2-331602.uc.r.appspot.com/authenticate```
    * This will create a token for the user specified in the body of the request. The tokens last for 10 hours. This will return an error if the user making the request does not exist in the registry, or if the action cannot be completed as desired. The body of this request is the user's name, password, and administrator status as a JSON object with the following structure:
    ```
    {
        "User": {
            "name": "ece461defaultadminuser",
            "isAdmin": true
        },
        "Secret": {
            "password": "correcthorsebatterystaple123(!__+@**(A"
        }
    }
    ```
### For testing:
* Create Administrator: ```POST https://project-2-331602.uc.r.appspot.com/register/admin```
    * This is a helper function that creates a base administrator. There is a default administrator password, and this function only works if the request header contains that correct default administrator password in the form of the "X-Authorization" field with the value "bearer \<password>". This will return an error if the action cannot be completed as desired. The body of the request is the new administrator's name, administrator status, and password as a JSON object with the following structure:
    ```
    {
        "User": {
            "name": String,
            "isAdmin": Bool (True)
        },
        "Secret": {
            "password": String
        }
    }
    ```

This application was developed as part of ECE 46100 Fall 2021 at Purdue University by Raymond Ngo, Isabelle Akian, and Vraj Parmar

import json

from flask import Flask, request, Response, g, jsonify
from flask.ext.restful import Resource, Api, abort
from werkzeug.exceptions import NotFound,  UnsupportedMediaType

from utils import RegexConverter
import database


DEFAULT_DB_PATH = 'db/project.db'

#Constants for hypermedia formats and profiles
COLLECTIONJSON = "application/vnd.collection+json"
HAL = "application/hal+json"
PROJECT_PROFILES = "http://confluence.atlassian.virtues.fi/display/PWP/PWP01#PWP01-RESTfulAPIdesign"

#Define the application and the api
app = Flask(__name__)
app.debug = True
#Set the database API. Change the DATABASE value from app.config to modify the
#database to be used (for instance for testing)
app.config.update({'DATABASE':database.ProjectDatabase(DEFAULT_DB_PATH)})
#Start the RESTful API.
api = Api(app)


def create_error_response(status_code, title, message, resource_type=None):
    response = jsonify(title=title, message=message, resource_type=resource_type)
    response.status_code = status_code
    return response

@app.errorhandler(404)
def resource_not_found(error):
    return create_error_response(404, "Resource not found", "This resource url does not exit")

@app.errorhandler(500)
def unknown_error(error):
    return create_error_response(500, "Error", "The system has failed. Please, contact the administrator")

@app.before_request
def set_database():
    '''Stores an instance of the database API before each request in the flas.g
    variable accessible only from the application context'''
    g.db = app.config['DATABASE']


#Define the resources
class Tasks(Resource):
    '''
    Resource Messages implementation
    '''
    def get(self):
        '''
        Get all messages in my system.

        INPUT parameters:
          None

        OUTPUT: 
         * Media type: Collection+JSON: 
         * Profile: Task profile

        '''
        
        #Extract tasks from database
        tasks_db = g.db.get_tasks()

        #Create the envelope
        envelope = {}
        collection = {}
        envelope["collection"] = collection
        collection['version'] = "1.0"
        collection['href'] = api.url_for(Tasks)
        collection['links'] = [{"href" : api.url_for(Users), "rel" : "users-all", "prompt" : "Users in the system"}]
        collection['template'] = {
          "data" : [
                {"prompt" : "Title of the task", "name" : "title", "value" : "", "required":True},
                {"prompt" : "Category of the task", "name" : "category", "value" : "", "required":True},
                {"prompt" : "Description of the task", "name" : "description", "value" : "", "required":True},
                {"prompt" : "Priority of the task", "name" : "priority", "value" : "", "required":True},
                {"prompt" : "Status of the task", "name" : "status", "value" : "", "required":True}]
        }
        #Create the items
        items = []
        for task in tasks_db: 
            _task = task['task_id']
            _title = task['title']
            _category = task['category']
            _status = task['status']
            _date = task['date']
            _url = api.url_for(Task, taskid=_task)
            task = {}
            task['href'] = _url
            task['data'] = []
            value0 = {'name':'title', 'value':_title}
            value1 = {'name':'category', 'value':_category}
            value2 = {'name':'status', 'value':_status}
            value3 = {'name':'date', 'value':_date}
            task['data'].append(value0)
            task['data'].append(value1)
            task['data'].append(value2)
            task['data'].append(value3)
            task['links'] = [{"href" : api.url_for(Comments, taskid=_task), "rel" : "Comments", "prompt" : "Comments for this task"},
                             {"href" : api.url_for(Assignees, taskid=_task), "rel" : "Assignees", "prompt" : "Assignees for this task"}]
            items.append(task)
        collection['items'] = items
        
        return envelope

    def post(self):
        '''
        Adds a a new task to the system.

        ENTITY BODY INPUT FORMAT:
        * Media type: Collection+JSON: 
         * Profile: Task profile

        The body should be a Collection+JSON template.         
        Semantic descriptors used in template: title, category, description, priority, status

        OUTPUT:
        Returns 201 if the task was added successfully
        Returns 400 if the message is not well formed or the entity body is
        empty.
        Returns 415 if the format of the response is not json
        Returns 500 if the task could not be added

          {"template" : {
          "data" : [
                {"prompt" : "Title of the task", "name" : "title", "value" : "", "required":True},
                {"prompt" : "Category of the task", "name" : "category", "value" : "", "required":True},
                {"prompt" : "Description of the task", "name" : "description", "value" : "", "required":True},
                {"prompt" : "Priority of the task", "name" : "priority", "value" : "", "required":True},
                {"prompt" : "Status of the task", "name" : "status", "value" : "", "required":True}]
        }}

        '''
        

        #get JSON
        input = request.get_json(force=True)
        if not input:
            abort(415)

        try: 
            data = input['template']['data']
            title = None
            category = None
            description = None
            priority = None
            status = None

            for d in data: 
                if d['name'] == 'title':
                    title = d['value']
                elif d['name'] == 'category':
                    category = d['value']
                elif d['name'] == 'description':
                    description = d['value']
                elif d['name'] == 'priority':
                    priority = d['value']
                elif d['name'] == 'status':
                    status = d['value']

            #Check that the data is correct
            if not title or not category or not description or not priority or not status:
                return create_error_response(400, "Wrong request format",
                                             "Be sure you include task title, category, description, priority and status",
                                             "Tasks")
        except: 
            #This is launched if either title or body does not exist or if 
            # the template.data array does not exist.
            return create_error_response(400, "Wrong request format",
                                             "Be sure you include task title, category, description, priority and status",
                                             "Tasks")
        
        #Create new task or raise an error 500
        newtask = g.db.add_task(title, category, description, int(priority), int(status))
        if newtask == False:
            abort(500)
               
        #TODO: Get ID of the new task from DB (not implemented in the DB API)
        url = "url" #api.url_for(Task, taskid=newmessageid)

        return Response(status=201, headers={'Location':url})

class Task(Resource):
    '''
    Single task.
    '''

    def get(self, taskid):
        '''
        Get specific task.
        Returns status code 404 if the task does not exist
        Returns 200 if everything is fine.

        INPUT PARAMETERS:
        * taskid = ID of the task

        ENTITY BODY OUTPUT FORMAT: 
         * Media type: application/hal+json: 
         * Profile: Task profile

        '''

        #PEFORM OPERATIONS INITIAL CHECKS
        #Get the message from db
        task_db = g.db.get_task(taskid)
        if not task_db:
            return create_error_response(404, "Unknown task",
                                         "There is no a task with id %s" % taskid,
                                         "Task")
        envelope = {}
        links = {}
        envelope["_links"] = links

        _curies = [
            {
                "name": "msg",
                "href": PROJECT_PROFILES,
            }
        ]
        links['curies'] = _curies
        links['self'] = {'href':api.url_for(Task, taskid=taskid),
                         'profile': PROJECT_PROFILES}
        links['collection'] = {'href':api.url_for(Tasks),
                               'profile': PROJECT_PROFILES,
                               'type':COLLECTIONJSON}
        links['users-all'] = {'href':api.url_for(Users),
                               'profile': PROJECT_PROFILES,
                               'type':COLLECTIONJSON}
        links['comments'] = {"href" : api.url_for(Comments, taskid=taskid),
                             'profile' : PROJECT_PROFILES,
                             'type':COLLECTIONJSON}
        links['assignees'] = {"href" : api.url_for(Assignees, taskid=taskid),
                             'profile' : PROJECT_PROFILES,
                             'type':COLLECTIONJSON}

        envelope['template'] = {
          "data" : [
                {"prompt" : "Title of the task", "name" : "title", "value" : "", "required":True},
                {"prompt" : "Category of the task", "name" : "category", "value" : "", "required":True},
                {"prompt" : "Description of the task", "name" : "description", "value" : "", "required":True},
                {"prompt" : "Priority of the task", "name" : "priority", "value" : "", "required":True},
                {"prompt" : "Status of the task", "name" : "status", "value" : "", "required":True}]
        }

        envelope['title'] = task_db['title']
        envelope['category'] = task_db['category']
        envelope['description'] = task_db['description'] #Calculated before. It can be Anonymous
        envelope['priority'] = task_db['priority']
        envelope['status'] = task_db['status']
        envelope['date_created'] = task_db['date']
        
        return Response (json.dumps(envelope), 200, mimetype=HAL+";"+PROJECT_PROFILES)

    def delete(self, taskid):
        '''
        Deletes a task from the Project API. 

        INPUT PARAMETERS:
         - taskid: The id of the task to be deleted from the system
  
        OUTPUT
        Returns 204 if the task was deleted
        Returns 404 if the taskid is not associated to any task.
        '''

        #PERFORM DELETE OPERATIONS
        if g.db.remove_task(taskid):
            return '', 204
        else:
            #Send error message
            return create_error_response(404, "Unknown task",
                                         "There is no a task with id %s" % taskid,
                                         "Task")
    
    def put(self, taskid):
        '''
        Modifies task.

        ENTITY BODY INPUT FORMAT:
        * Media type: Collection+JSON: 
        * Profile: Task profile

       
        OUTPUT:
        204 if task was modified succesfully
        400 if the entity body is malformed
        404 if the task does not exist
        415 if the input is not JSON

        {"template" : {
          "data" : [
                {"prompt" : "Title of the task", "name" : "title", "value" : "", "required":True},
                {"prompt" : "Category of the task", "name" : "category", "value" : "", "required":True},
                {"prompt" : "Description of the task", "name" : "description", "value" : "", "required":True},
                {"prompt" : "Priority of the task", "name" : "priority", "value" : "", "required":True},
                {"prompt" : "Status of the task", "name" : "status", "value" : "", "required":True}]
        }}

        '''

        #CHECK THAT MESSAGE EXISTS
        if not g.db.get_task(taskid):
            raise NotFound()

        input = request.get_json(force=True)
        if not input:
            return create_error_response(415, "Unsupported Media Type",
                                    "Use a JSON compatible format",
                                    "Tasks")
        try: 
            data = input['template']['data']
            title = None
            category = None
            description = None
            priority = None
            status = None
            for d in data: 
                if d['name'] == 'title':
                    title = d['value']
                elif d['name'] == 'category':
                    category = d['value']
                elif d['name'] == 'description':
                    description = d['value']
                elif d['name'] == 'priority':
                    priority = d['value']
                elif d['name'] == 'status':
                    status = d['value']
                    
            if not title or not category or not description or not priority or not status:
                abort(400)
        except: 
            abort(400)
        else:
            if not g.db.update_title(int(taskid),title):
                return NotFound()
            elif not g.db.update_description(int(taskid),description):
                return NotFound()
            elif not g.db.update_category(int(taskid),category):
                return NotFound()
            elif not g.db.update_priority(int(taskid),int(priority)):
                return NotFound()
            elif not g.db.update_status(int(taskid),int(status)):
                return NotFound
            return '', 204

class Users(Resource): 
    
    def get(self):
        '''
        If everything is OK, returns 200.
        
        OUTPUT: 
            * Media type: Collection+JSON: 
            * Profile: User profile

        '''
        users_db = g.db.get_users()

       #Create the envelope
        envelope = {}
        collection = {}
        envelope["collection"] = collection
        collection['version'] = "1.0"
        collection['href'] = api.url_for(Users)
        collection['links'] = [{"href" : api.url_for(Tasks), "rel" : "users-all", "prompt" : "Tasks in system"}]
        collection['template'] = {
                "data" : [
                {"prompt" : "Insert user nickname", "name" : "nickname", "value" : "", "required":True},
                {"prompt" : "Insert user role", "name" : "role", "value" : "", "required":True},
                {"prompt" : "Insert user e-mail adress", "name" : "email", "value" : "", "required":True},
                {"prompt" : "Insert user's boss", "name" : "boss", "value" : "", "required":True}
                ]
        }
        #Create the items
        items = []
        for user in users_db: 
            print user
            _nickname = user['nickname']
            _url = api.url_for(User, username=_nickname)
            user = {}
            user['href'] = _url
            user['data'] = []
            value = {'name':'nickname', 'value':_nickname}
            user['data'].append(value)
            user['links'] = []
            items.append(user)
        collection['items'] = items
        
        return envelope

    
    def post(self):
        '''
        Adds a new user in the database.

        Media type: Collection+JSON: 
        Profile: User profile

        OUTPUT: 
        Returns 201 + the url of the new resource in the Location header (TODO: get the id of the new user from DB)
        Return 400 if the body is not well formed
        Return 415 if mediatype not JSON

        {"template" : {
                "data" : [
                {"prompt" : "Insert user nickname", "name" : "nickname", "value" : "", "required":True},
                {"prompt" : "Insert user role", "name" : "role", "value" : "", "required":True},
                {"prompt" : "Insert user e-mail adress", "name" : "email", "value" : "", "required":True},
                {"prompt" : "Insert user's boss", "name" : "boss", "value" : "", "required":True}
                ]
        }}

        '''
        #PARSE THE REQUEST:
        input = request.get_json(force=True)
        if not input:
            return create_error_response(415, "Unsupported Media Type",
                                         "Use a JSON compatible format",
                                         "User")
    
        data = input['template']['data']
        nickname = None
        email = None
        role = None
        boss = None
        for d in data:
            if d['name'] == 'nickname':
                nickname = d['value']
            elif d['name'] == 'email':
                email = d['value']
            elif d['name'] == 'role':
                role = d['value']
            elif d['name'] == 'boss':
                boss = d['value']

        #Error if not required value
        if not nickname or not email or not role or not boss:
            return create_error_response(400, "Wrong request format",
                                              "Be sure you include all mandatory"\
                                              "properties",
                                              "User") 

        useradded = g.db.add_user(nickname, email, role, boss)
        if useradded == False:
            abort(400)

        #CREATE RESPONSE AND RENDER
        return  Response(status=201)
        
class User(Resource):
    '''
    User Resource.
    '''
    def _isauthorized(self, nickname, authorization): 
        '''
        Check if a user is authorized or not to perform certain operation.
        '''
        if authorization is not None and \
                                (authorization.lower() == "admin" or 
                                 authorization.lower() == nickname.lower()):
            return True
        return False

    def get(self, username): 
        '''
        Get basic information of a user:

        INPUT:
            *nickname

        OUTPUT:
        Return 200 if the nickname exists.
        Return 404 if the nickname is not stored in the system.
         
       
        ENTITY BODY OUTPUT FORMAT: 
         * Media type: HAL+json
         * Profile: User profile

        '''
        #PERFORM OPERATIONS
        user_id = g.db.get_user_id(username)

        if user_id == False:
            return create_error_response(404, "Unknown user", username)

        #Create the envelope:
        envelope = {}
        #Now create the links
        links = {}
        envelope["_links"] = links

        #Fill the links
        _curies = [
            {
                "name": username,
                "href": PROJECT_PROFILES,
            },

        ]
        links['curies'] = _curies
        links['self'] = {'href':api.url_for(User, username=username),
                         'profile': PROJECT_PROFILES}
        links['collection'] = {'href':api.url_for(Users),
                         'profile': PROJECT_PROFILES}
        envelope['userid'] = user_id
        envelope['nickname'] = username
        
        #RENDER
        return Response (json.dumps(envelope), 200, mimetype=HAL+";"+PROJECT_PROFILES)

    def delete(self, username):
        '''
        Delete a user in the system.
        OUTPUT:

        If the user is authorized delete the given user and returns 204.
        If the nickname does not exist return 404
        '''

        user_id = g.db.get_user_id(username)
        if user_id == False:
            return create_error_response(404, "Unknown user",
            "There is no a user with nickname %s" 
            % username,
            "User")
        
        if g.db.delete_user(user_id):
            #RENDER RESPONSE
            return '', 204
        else:
            #GENERATE ERROR RESPONSE
            return create_error_response(404, "Unknown user",
            "There is no a user with nickname %s" 
            % username,
            "User")

    def put(self, username):
        '''
        Modifies username.

        ENTITY BODY INPUT FORMAT:
        * Media type: Collection+JSON: 
        * Profile: User profile

       
        OUTPUT:
        204 if task was modified succesfully
        400 if the entity body is malformed
        404 if the task does not exist
        415 if the input is not JSON

        {"template" : {
          "data" : [
            {"prompt" : "New username", "name" : "new_username", "value" : "", "required":True}]
        }}

        '''

        #CHECK THAT MESSAGE EXISTS
        if not g.db.get_user_id(username):
            raise NotFound()

        input = request.get_json(force=True)
        if not input:
            return create_error_response(415, "Unsupported Media Type",
                                    "Use a JSON compatible format",
                                    "Tasks")
        try: 
            data = input['template']['data']
            new_username = None
            for d in data: 
                if d['name'] == 'new_username':
                    new_username = d['value']
                    
            if not new_username:
                abort(400)
        except: 
            abort(400)
        else:
            if not g.db.update_username(username, new_username):
                return NotFound()
            return '', 204


class Comments(Resource):
    def get(self, taskid):
        comments_db = g.db.get_comments(taskid)

        #FILTER AND GENERATE RESPONSE

        #Create the envelope
        envelope = {}
        collection = {}
        envelope["collection"] = collection
        collection['version'] = "1.0"
        collection['href'] = api.url_for(Comments, taskid=taskid)
        collection['links'] = [{'prompt':'List of all users in the system', 
                              'rel':'users-all','href': api.url_for(Users)},
                               {'prompt':'List of all users in the system', 
                              'rel':'tasks-all','href': api.url_for(Tasks)},
                               {'prompt':'Task',
                                'rel':'task', 'href' : api.url_for(Task, taskid=taskid)}
                           ]
        collection['template'] = {
          "data" : [
                {"prompt" : "Comment body", "name" : "comment", "value" : "", "required":True}
                ]
        }
        #Create the items
        items = []
        for comment in comments_db: 
            _id = comment['comment_id']
            _comment = comment['comment']
            _date = comment['date']
            _url = api.url_for(Comments, taskid=taskid)
            comment = {}
            comment['href'] = _url
            comment['data'] = []
            value0 = {'name':'comment_id', 'value':_id}
            value1 = {'name':'comment', 'value':_comment}
            value2 = {'name':'date', 'value':_date}
            comment['data'].append(value0)
            comment['data'].append(value1)
            comment['data'].append(value2)
            comment['links'] = []
            items.append(comment)
        collection['items'] = items
        
        return envelope

    def post(self, taskid):
        '''
        Return 200 if OK
        Return 415 if input not JSON
        Return 400 if the request data is wrong

        {"template" : {
          "data" : [
                {"prompt" : "Comment body", "name" : "comment", "value" : "", "required":
        ]}}
        '''

        #TODO: check that taskid exists
        
        input = request.get_json(force=True)
        if not input:
            abort(415)

        #It throws a BadRequest exception, and hence a 400 code if the JSON is 
        #not wellformed
        try: 
            data = input['template']['data']
            comment = None

            for d in data: 
                #This code has a bad performance. We write it like this for
                #simplicity. Another alternative should be used instead.
                if d['name'] == 'comment':
                    comment = d['value']

            #CHECK THAT DATA RECEIVED IS CORRECT
            if not comment:
                return create_error_response(400, "Wrong request format",
                                             "Be sure you include task title, category, description, priority and status",
                                             "Tasks")
        except: 
            return create_error_response(400, "Wrong request format",
                                             "Be sure you include task title, category, description, priority and status",
                                             "Tasks")
        
        newcomment = g.db.add_comment(comment, taskid)
        if newcomment == False:
            abort(500)
               
        #TODO: Add ID to DB? Only returns true or false.
        url = "url" #api.url_for(Task, taskid=taskid)

        #RENDER
        #Return the response
        return Response(status=201, headers={'Location':url})


class Comment(Resource):
    def delete(self, taskid, commentid):
        '''
        Returns 204 if comment was succesfully deleted.
        Returns 404 if there is no comment with such ID.
        '''
        if g.db.delete_comment(commentid):
            #RENDER RESPONSE
            return '', 204
        else:
            #GENERATE ERROR RESPONSE
            return create_error_response(404, "No such comment",
            "There is no comment with id %s" 
            % commentid,
            "Comment")

class Assignees(Resource):
    def get(self, taskid):

        '''
        Return 200 if everything is OK
        '''
        
        assignee_db = g.db.get_assigned_users(taskid)

        #FILTER AND GENERATE RESPONSE

        #Create the envelope
        envelope = {}
        collection = {}
        envelope["collection"] = collection
        collection['version'] = "1.0"
        collection['href'] = api.url_for(Assignees, taskid=taskid)
        collection['links'] = [{'prompt':'List of all users in the system', 
                              'rel':'users-all','href': api.url_for(Users)},
                               {'prompt':'List of all tasks ihn the system', 
                              'rel':'tasks-all','href': api.url_for(Tasks)},
                               {'prompt':'This task', 
                              'rel':'task','href': api.url_for(Task, taskid=taskid)}
                           ]
        collection['template'] = {
          "data" : [
                {"prompt" : "User to assign", "name" : "nickname", "value" : "", "required":True}
                ]
        }
        #Create the items
        items = []
        for assignee in assignee_db: 
            _id = assignee['user']
            _nickname = g.db.get_user(_id)
            _url = api.url_for(Assignees, taskid=taskid)
            assignee = {}
            assignee['href'] = _url
            assignee['data'] = []
            value0 = {'name':'user_id', 'value':_id}
            value1 = {'name':'nickname', 'value':_nickname}
            assignee['data'].append(value0)
            assignee['data'].append(value1)
            assignee['links'] = []
            items.append(assignee)
        collection['items'] = items
        
        #RENDER
        return envelope

    
    def post(self,taskid):
        '''

        Return 201 if OK
        Return 415 if input not JSON
        Return 404 if username does not exist
        Return 400 request format is wrong
        Return 500 if assignee couldn't be added.
        
        {"template" : {
          "data" : [
                {"prompt" : "User to assign", "name" : "nickname", "value" : "", "required":True}
                ]
        }}
        '''
        #TODO: check that taskid exists
        
        input = request.get_json(force=True)
        if not input:
            abort(415)

        #It throws a BadRequest exception, and hence a 400 code if the JSON is 
        #not wellformed
        try: 
            data = input['template']['data']
            nickname = None

            for d in data: 
                if d['name'] == 'nickname':
                    nickname = d['value']

            #CHECK THAT DATA RECEIVED IS CORRECT
            if not nickname:
                return create_error_response(400, "Wrong request format",
                                             "Be sure you include nickname",
                                             "Assignees")
        except: 
            return create_error_response(400, "Wrong request format",
                                             "Be sure you include task title, category, description, priority and status",
                                             "Tasks")

        userid = g.db.get_user_id(nickname)
        if not userid:
            return create_error_response(404, "No such username",
                                              "Be sure you have a right username",
                                              "Assignees")
        
        newassignee = g.db.assign_to_task(taskid,userid)
        if not newassignee:
            abort(500)
               
        url = api.url_for(Assignees, taskid=taskid)

        #Return the response
        return Response(status=201, headers={'Location':url})
    
class Assignee(Resource):
    
    def delete(self,taskid,username):
        userid = g.db.get_user_id(username)
        if g.db.remove_assignee(taskid,userid):
            #RENDER RESPONSE
            return '', 204
        else:
            #GENERATE ERROR RESPONSE
            return create_error_response(404, "Assignee does not exist",
            "There is no a user with nickname %s" 
            % username,
            "User")

class Team(Resource):
    def get(self, leaderid):
        '''
        Returns 200 if OK
        
        Meditype: collection + JSON
        Profile: User profile?
        '''
        team_db = g.db.get_team(leaderid)

        #Create the envelope
        envelope = {}
        collection = {}
        envelope["collection"] = collection
        collection['version'] = "1.0"
        collection['href'] = api.url_for(Team, leaderid=leaderid)
        #collection['links'] = [{'prompt':'List of all users in the Forum', 
        #                      'rel':'users-all','href': api.url_for(Users)}
        #                   ]
        collection['template'] = {
          "data" : [
                {"prompt" : "Member name", "name" : "nickname", "value" : "", "required":True}
                ]
        }
        #Create the items
        items = []
        for team in team_db: 
            _nickname = team['nickname']
            _url = api.url_for(Team, leaderid=leaderid)
            comment = {}
            comment['href'] = _url
            comment['data'] = []
            value = {'name':'nickname', 'value':_nickname}
            comment['data'].append(value)
            comment['links'] = []
            items.append(comment)
        collection['items'] = items
        
        #RENDER
        return envelope

    def post(self, leaderid):
        '''
        {"template" : {
          "data" : [
                {"prompt" : "Member name", "name" : "nickname", "value" : "", "required":True}
                ]
        }}
        '''

        input = request.get_json(force=True)
        if not input:
            abort(415)
        try: 
            data = input['template']['data']
            nickname = None

            for d in data: 
                #This code has a bad performance. We write it like this for
                #simplicity. Another alternative should be used instead.
                if d['name'] == 'nickname':
                    nickname = d['value']

            #CHECK THAT DATA RECEIVED IS CORRECT
            if not nickname:
                return create_error_response(400, "Wrong request format",
                                             "Be sure you include task title, category, description, priority and status",
                                             "Tasks")
        except: 
            #This is launched if either title or body does not exist or if 
            # the template.data array does not exist.
            return create_error_response(400, "Wrong request format",
                                             "Be sure you include task title, category, description, priority and status",
                                             "Tasks")
        
        userid = g.db.get_user_id(nickname)
        
        newcomment = g.db.add_to_team(userid, leaderid)
        if newcomment == False:
            abort(500)
               
        #Create the Location header with the id of the message created
        #TODO: Add ID to DB api or other witchcraft?
        url = api.url_for(Team, leaderid=leaderid)
        
        return Response(status=201, headers={'Location':url})

class Team_member(Resource):
    def delete(self, leaderid, nickname):

        memberid = g.db.get_user_id(nickname)
        if memberid:
            if g.db.remove_from_team(memberid,leaderid):
                #RENDER RESPONSE
                return '', 204
            else:
                #GENERATE ERROR RESPONSE
                return create_error_response(404, "Unknown user",
                "There is no a user with nickname %s" 
                % nickname,
                   "User")

        else:
            return create_error_response(404, "Unknown team member",
            "There is no team member with nickname %s" % nickname,
            "Team_member")

app.url_map.converters['regex'] = RegexConverter


#Define the routes
api.add_resource(Tasks, '/project/api/tasks/',
                 endpoint='tasks')
api.add_resource(Task, '/project/api/tasks/<taskid>/',
                endpoint='task')
api.add_resource(Assignees, '/project/api/tasks/<taskid>/assignees/',
                 endpoint='assignees')
api.add_resource(Assignee, '/project/api/tasks/<taskid>/assignees/<username>/',
                 endpoint='assignee')
api.add_resource(Comments, '/project/api/tasks/<taskid>/comments/',
                 endpoint='comments')
api.add_resource(Comment, '/project/api/tasks/<taskid>/comments/<commentid>/',
                 endpoint='comment')
api.add_resource(Users, '/project/api/users/',
                 endpoint='users')
api.add_resource(User, '/project/api/users/<username>/',
                 endpoint='user')
api.add_resource(Team, '/project/api/users/team/<leaderid>/',
                 endpoint='team')
api.add_resource(Team_member, '/project/api/users/team/<leaderid>/<nickname>/',
                 endpoint='team_member')

#Start the application
if __name__ == '__main__':
    app.run(debug=True)

from werkzeug.serving import run_simple
from werkzeug.wsgi import DispatcherMiddleware
from db_api.resources import app as project
from project_admin.application import app as project_admin

application = DispatcherMiddleware(project, {
     '/project_admin': project_admin
})
if __name__ == '__main__':
    run_simple('localhost', 5000, application,
               use_reloader=True, use_debugger=True, use_evalex=True)
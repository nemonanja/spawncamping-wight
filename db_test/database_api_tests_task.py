import sqlite3, unittest
from .database_api_tests_common import BaseTestCase, db, db_path


task = {'task_id':1, 'title':'Add help button', 'category':'frontend', 'description':'Tallanen nappi puuttuu, lisaa asap!', 'priority':2, 'status':1}
task2 = {'task_id':2, 'title':'Connection bug', 'category':'bug', 'description':'Ei yhdistaa servulle, valittaa etta "Bad url"...', 'priority':3, 'status':1}

comment1 = {'comment':'I will do this. -Teppo', 'task_id':1}
comment2 = {'comment_id':2,'comment':'Who can start on this one??? -Seppo', 'task_id':2}

class TasksDbAPITestCase(BaseTestCase):

    @classmethod
    def setUpClass(cls):
        print "Testing ", cls.__name__
        
        
    def test_update_title(self):
        '''Test update_title. Test also update for task that does not exist'''
    
        print '('+self.test_update_title.__name__+')',\
        self.test_update_title.__doc__
        
        
        update = db.update_title(1,"New title!!")
        self.assertTrue(update)
        
        update = db.update_title(60, "Can't do this")
        self.assertFalse(update)
    

    def test_update_description(self):
        '''Test update_description. Test also update for task that does not exist'''
        print '('+self.test_update_description.__name__+')',\
        self.test_update_description.__doc__

        update = db.update_description(1,"New desc!!")
        self.assertTrue(update)
        
        update = db.update_description(60, "Can't do this")
        self.assertFalse(update)
        
    def test_update_category(self):
        '''Test update_title. Test also update for category and task which do not exist'''
        print '('+self.test_update_category.__name__+')',\
        self.test_update_category.__doc__
        
        update = db.update_category(1,"bug")
        self.assertTrue(update)
        
        update = db.update_category(1, "thisdoesnotexist")
        self.assertFalse(update)
        
        update = db.update_category(666, "bug")
        self.assertFalse(update)
        
        
    def test_remove_assignee(self):
        '''Remove assignee and assignee that does not exist'''
        print '('+self.test_remove_assignee.__name__+')',\
        self.test_remove_assignee.__doc__
        
        db.assign_to_task(1,3)
        
        remove1 = db.remove_assignee(1,5)
        self.assertFalse(remove1)
        
        remove2 = db.remove_assignee(1,3)
        self.assertTrue(remove2)
        
        
    def test_assign_to_task(self):
        '''Assign to task'''
        print '('+self.test_assign_to_task.__name__+')',\
        self.test_assign_to_task.__doc__
        assign = db.assign_to_task(1,2)
        self.assertTrue(assign)
        
        #assign = db.assign_to_task(4,2)
        #self.assertTrue(assign)
        
    def test_add_comment(self):
        '''Add new comment'''
        print '('+self.test_add_comment.__name__+')',\
        self.test_add_comment.__doc__
    
    
        comment = db.add_comment("Test comment", 1)
        self.assertTrue(comment)
        
        new_comment = db.get_comments(1)
        self.assertEquals(new_comment[1]['comment_id'], 3)
        
        db.delete_comment(3)
        
    def test_get_comments(self):
        '''Get comments from task_id 2'''
        print '('+self.test_get_comments.__name__+')',\
        self.test_get_comments.__doc__
        
        comments = db.get_comments(2)
        
        self.assertEquals(comments[0]['comment'], comment2['comment'])
        self.assertEquals(comments[0]['comment_id'], comment2['comment_id'])
        
    def test_delete_comment(self):
        '''Create and delete comment with comment_id 3'''
        print '('+self.test_delete_comment.__name__+')',\
        self.test_add_task.__doc__
        
        db.add_comment("Test",1)
        
        delete = db.delete_comment(3)
        self.assertTrue(delete)
        
        delete = db.delete_comment(18)
        self.assertFalse(delete)
        
        
    def test_get_tasks(self):
        '''Get tasks'''
        print '('+self.test_get_tasks.__name__+')',\
        self.test_get_tasks.__doc__
        
        new_task = db.get_tasks()
        
        self.assertEquals(new_task[0]['task_id'],task['task_id'])
        self.assertEquals(new_task[0]['title'],task['title'])
        self.assertEquals(new_task[0]['description'],task['description'])
        self.assertEquals(new_task[0]['priority'],task['priority'])
        self.assertEquals(new_task[0]['status'],task['status'])
        
        self.assertEquals(new_task[1]['task_id'],task2['task_id'])
        self.assertEquals(new_task[1]['title'],task2['title'])
        self.assertEquals(new_task[1]['description'],task2['description'])
        self.assertEquals(new_task[1]['priority'],task2['priority'])
        self.assertEquals(new_task[1]['status'],task2['status'])
        
        
    def test_get_task(self):
        '''Get task with task_id 1'''
        print '('+self.test_get_task.__name__+')',\
        self.test_add_task.__doc__
        
        new_task = db.get_task(task['task_id'])
        
        self.assertEquals(new_task['task_id'],task['task_id'])
        self.assertEquals(new_task['title'],task['title'])
        self.assertEquals(new_task['description'],task['description'])
        self.assertEquals(new_task['priority'],task['priority'])
        self.assertEquals(new_task['status'],task['status'])
        
        
        #Task that does not exist
        new_task = db.get_task(13)
        self.assertFalse(new_task)
        
        
    def test_update_status(self):
        '''Update task status'''
        print '('+self.test_update_status.__name__+')',\
        self.test_update_status.__doc__
        
        update = db.update_status(1,3)
        self.assertTrue(update)
        
        #update = db.update_status(1,15)
        #self.assertFalse(update)
        
    def test_update_priority(self):
        '''Update task priority'''
        print '('+self.test_update_priority.__name__+')',\
        self.test_update_priority.__doc__
        
        update = db.update_status(1,3)
        self.assertTrue(update)
        
        #update = db.update_status(1,15)
        #self.assertFalse(update)        
    
    
    def test_add_task(self):
        '''Test adding task'''
        print '('+self.test_add_task.__name__+')',\
        self.test_add_task.__doc__
        
        #Succsessfully add task
        task = db.add_task("New title", "bug", "Super cool", 1, 3)
        self.assertTrue(task)
        
    def test_remove_task(self):
        '''Removet task'''
        print '('+self.test_add_task.__name__+')',\
        self.test_add_task.__doc__
        
        db.add_task("New title", "bug", "Super cool", 1, 3)
        
        remove = db.remove_task(3)
        self.assertTrue(remove)
        
        remove2 = db.remove_task(14)
        self.assertFalse(remove2)
        
if __name__ == '__main__':
    print 'Start running tests'
    unittest.main()
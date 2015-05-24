import sqlite3, unittest

from .database_api_tests_common import BaseTestCase, db, db_path

class UserDbAPITestCase(BaseTestCase):

    user1_nickname = 'Seppo'
    user1_id = 1
    user1_role = 'leader'
    user2_nickname = 'Teppo'
    user2_id = 2
    user2_role = 'member'
    user3_nickname = 'Reijo'
    user4_nickname = 'Kyllikki'
    user5_id = 5
    user5_nickname = 'Ismo'
    user5_email = 'ismo@jippii.fi'
    user5_role = 'member'
    user5_boss = 1

    #Initially 4 rows in USERS table (check sql dump)
    initial_size = 4

    @classmethod
    def setUpClass(cls):
        print "Testing ", cls.__name__

    def test_get_users(self):
        '''
        Test that get_users work correctly and extract required user info
        '''
        print '('+self.test_get_users.__name__+')', \
              self.test_get_users.__doc__
        users = db.get_users()
        #Check that the size is correct
        self.assertEquals(len(users), self.initial_size)
        #Iterate throug users and check if the users with user1_id and
        #user2_id are correct:
        for user in users:
            if user['nickname'] == self.user1_nickname:
                self.assertEquals(user['nickname'], self.user1_nickname)
            elif user['nickname'] == self.user2_nickname:
                self.assertEquals(user['nickname'], self.user2_nickname)
            elif user['nickname'] == self.user3_nickname:
                self.assertEquals(user['nickname'], self.user3_nickname)
            elif user['nickname'] == self.user4_nickname:
                self.assertEquals(user['nickname'], self.user4_nickname)


    def test_get_user(self):
        '''
        Test get_user with user1_id and user2_id
        '''
        print '('+self.test_get_user.__name__+')', \
              self.test_get_user.__doc__
        user = db.get_user(self.user1_id)
        self.assertEquals(user, self.user1_nickname)
        user = db.get_user(self.user2_id)
        self.assertEquals(user, self.user2_nickname)

    def test_get_role(self):
        '''
        Test get_role with user1_id and user2_id
        '''
        print '('+self.test_get_role.__name__+')', \
              self.test_get_role.__doc__
        role = db.get_role(self.user1_id)
        self.assertEquals(role, self.user1_role)
        role = db.get_role(self.user2_id)
        self.assertEquals(role, self.user2_role)

    def test_add_user(self):
        '''
        Test if add_user returns True
        '''
        print '('+self.test_add_user.__name__+')', \
              self.test_add_user.__doc__
        returnvalue = db.add_user(self.user5_nickname, self.user5_email, self.user5_role, self.user5_boss)
        self.assertTrue(returnvalue, True)

    def test_delete_user(self):
        '''
        Test if delete_user returns True
        '''
        print '('+self.test_delete_user.__name__+')', \
              self.test_delete_user.__doc__
        returnvalue = db.delete_user(self.user5_id)
        self.assertTrue(returnvalue, True)

    def test_get_team(self):
        '''
        Test get_team method with user1_id (Seppo's team)
        '''
        print '('+self.test_get_team.__name__+')', \
              self.test_get_team.__doc__
        team = db.get_team(self.user1_id)
        #Iterate throug users and check if the users with user1_id and
        #user2_id are correct:
        for member in team:
            if member['nickname'] == self.user1_nickname:
                self.assertEquals(member['nickname'], self.user1_nickname)
            elif member['nickname'] == self.user2_nickname:
                self.assertEquals(member['nickname'], self.user2_nickname)
            elif member['nickname'] == self.user3_nickname:
                self.assertEquals(member['nickname'], self.user3_nickname)
            elif member['nickname'] == self.user4_nickname:
                self.assertEquals(member['nickname'], self.user4_nickname)

    def test_add_to_team(self):
        '''
        Test adding member to the team (Add Ismo to Seppo's team)
        '''
        print '('+self.test_add_to_team.__name__+')', \
              self.test_add_to_team.__doc__
        db.add_user(self.user5_nickname, self.user5_email, self.user5_role, self.user5_boss)
        returnvalue = db.add_to_team(self.user5_id, self.user1_id)
        self.assertTrue(returnvalue, True)

    def test_delete_from_team(self):
        '''
        Test deleting team from team (Remove Ismo from Seppo's team)
        '''
        print '('+self.test_delete_from_team.__name__+')', \
              self.test_delete_from_team.__doc__
        #Add Ismo to database
        db.add_user(self.user5_nickname, self.user5_email, self.user5_role, self.user5_boss)
        #Add Ismo to Seppo's team
        db.add_to_team(self.user5_id, self.user1_id)
        returnvalue = db.remove_from_team(self.user5_id, self.user1_id)
        self.assertTrue(returnvalue, True)

    def test_get_user_id(self):
        '''
        Test get_user_id (return Seppos userid
        '''
        print '('+self.test_get_user_id.__name__+')', \
              self.test_get_user_id.__doc__
        userid = db.get_user_id(self.user1_nickname)
        self.assertEquals(userid, self.user1_id)




if __name__ == '__main__':
    print 'Start running tests'
    unittest.main()
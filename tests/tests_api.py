import unittest
from flask import Flask, jsonify
from flask_testing import TestCase
from app import app
from app.models import db, AllUsers, LoginLog
from datetime import datetime
from flask_login import login_user, login_required, logout_user, current_user

# class TestLoginAPI(TestCase):
#     def create_app(self):
#         app.config['TESTING'] = True
#         app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Deevia%40123@localhost/homologation'
#         return app

#     def setUp(self):
#         db.create_all()

#         # Create a test user
#         test_user = AllUsers(
#             employee_id='test_employee',
#             name='Test User',
#             password='test_password',
#             user_type='operator'
#         )
#         db.session.add(test_user)
#         db.session.commit()

#     def tearDown(self):
#         db.session.remove()
#         db.drop_all()

#     def test_successful_login(self):
#         response = self.client.post('/login', json={'employee_id': 'test_employee', 'password': 'test_password'})
#         self.assertEqual(response.status_code, 200)
#         self.assertIn('Login successful', str(response.data))

#     def test_invalid_credentials(self):
#         response = self.client.post('/login', json={'employee_id': 'test_employee', 'password': 'wrong_password'})
#         self.assertEqual(response.status_code, 401)
#         self.assertIn('Invalid credentials', str(response.data))

#     def test_missing_employee_id(self):
#         response = self.client.post('/login', json={'password': 'test_password'})
#         self.assertEqual(response.status_code, 401)
#         self.assertIn('Invalid credentials', str(response.data))

#     def test_missing_password(self):
#         response = self.client.post('/login', json={'employee_id': 'test_employee'})
#         self.assertEqual(response.status_code, 401)
#         self.assertIn('Invalid credentials', str(response.data))

#     def test_login_log_created_for_operator(self):
#         response = self.client.post('/login', json={'employee_id': 'test_employee', 'password': 'test_password'})
#         self.assertEqual(response.status_code, 200)

#         login_log = LoginLog.query.filter_by(user_id='test_employee').first()
#         self.assertIsNotNone(login_log)
#         self.assertEqual(login_log.user_id, 'test_employee')
#         self.assertIsNotNone(login_log.login_time)


# class TestLogoutAPI(TestCase):
#     def create_app(self):
#         app.config['TESTING'] = True
#         app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Deevia%40123@localhost/homologation:'
#         app.config['SECRET_KEY'] = 'Deevia@123_homologation'
#         return app

#     def setUp(self):
#         db.create_all()

#         # Create a test operator user
#         operator_user = AllUsers(
#             employee_id='operator_124',
#             name='Operator User',
#             password='operator_password',
#             user_type='operator'
#         )

#         db.session.add(operator_user)

#         # Create a test admin user
#         admin_user = AllUsers(
#             employee_id='admin_4564',
#             name='Admin User',
#             password='admin_password',
#             user_type='admin'
#         )

#         db.session.add(admin_user)
#         db.session.add(operator_user)

#         # Commit changes
#         db.session.commit()

#     def tearDown(self):
#         db.session.remove()
        

#     def test_successful_logout(self):
#         # Log in as an operator user
#         user = AllUsers.query.filter_by(employee_id='operator_123').first()
#         self.assertIsNotNone(user, "Operator user does not exist in the database")

#         login_user(user)
#         self.assertEqual(current_user.employee_id, 'operator_123', "User login failed")

#         # Make a request to /logout
#         response = self.client.post('/logout')
#         self.assertEqual(response.status_code, 200)
#         self.assertIn('Logout successful', str(response.data))

#         # Check if the logout log is created for the operator
#         logout_log = LoginLog.query.filter_by(user_id='operator_123').first()
#         self.assertIsNotNone(logout_log, "Logout log not created for operator")
#         self.assertEqual(logout_log.user_id, 'operator_123', "Incorrect user_id in the logout log")
#         self.assertIsNotNone(logout_log.logout_time, "logout_time is None in the logout log")


#     def test_logout_without_active_session(self):
#         # Make a request to /logout without logging in first
#         response = self.client.post('/logout')
#         self.assertEqual(response.status_code, 400)
#         self.assertIn('No active session found', str(response.data))

#     def test_logout_log_not_created_for_admin(self):
#         # Log in as an admin user
#         user = AllUsers.query.filter_by(employee_id='admin_456').first()
#         login_user(user)

#         # Make a request to /logout
#         response = self.client.post('/logout')
#         self.assertEqual(response.status_code, 200)

#         # Check if the logout log is created for the admin
#         logout_log = LoginLog.query.filter_by(user_id='admin_456').first()
#         self.assertIsNone(logout_log)

if __name__ == '__main__':
    unittest.main()


import os
import json
import base64
from flask import request, jsonify, request
from app import app, db, logger, jwt
from app.models import AllUsers, ProcessTable, LoginLog, FinalTable
from datetime import datetime, timedelta
from collections import defaultdict
from sqlalchemy import func, distinct, case 
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity


@app.route('/login', methods=['POST'])
def login():
    try:
        logger.info('Login API called')

        data = request.get_json()
        json_data = data['user_data']
        employee_id = json_data.get('employee_id')
        password = json_data.get('password')
        user_type = json_data.get('user_type')  

        user = AllUsers.query.get(employee_id)

        if user and password and user.password == password and user.user_type == user_type:
            access_token = create_access_token(identity=user.employee_id, expires_delta=timedelta(hours=10))
            
            # Include the token in the response
            response = {
                'access_token': access_token,
                'message': 'Login successful',
                'employee_id': employee_id,
                'name': user.name,
                'status': True
            }

            if user.user_type == "operator":
                login_log = LoginLog(user_id=user.employee_id, login_time=datetime.now())
                db.session.add(login_log)
                db.session.commit()

            logger.info('Login successful for user {}'.format(employee_id))
            return jsonify(response), 200
        else:
            logger.warning('Invalid credentials for user {}'.format(employee_id))
            return jsonify({'message': 'Invalid credentials', 'status': False}), 200

    except Exception as e:
        logger.error('An error occurred in login API: {}'.format(str(e)))
        return jsonify({'error': str(e)}), 500
    


@app.route('/logout', methods=['GET'])
@jwt_required()
def logout():
    try:
        logger.info('Logout API called')

        logout_time = datetime.now()
        user_id = get_jwt_identity()

        user = AllUsers.query.get(user_id)

        if user.user_type == "operator":
            login_log = LoginLog.query.filter_by(user_id=user_id, logout_time=None).first()
            print(login_log)

            if login_log:
                login_log.logout_time = logout_time
                db.session.commit()


        logger.info('Logout successful for user {}'.format(user_id))
        return jsonify({'message': 'Logout successful for user id: {}'.format(user_id)}), 200

    except Exception as e:
        logger.error('An error occurred in logout API: {}'.format(str(e)))
        return jsonify({'error': str(e)}), 500
    

    

@app.route('/report_analysis', methods=['POST'])
@jwt_required()
def report_analysis():
    try:
        logger.info('Report Analysis API called')

        user_id = get_jwt_identity()

        # Check if the user is an admin or super_user
        user = AllUsers.query.get(user_id)
        if user.user_type not in ["super_user", "admin"]:
            logger.warning('Unauthorized, only Super User and Admins can add new camera') 
            return jsonify({'message': 'Unauthorized, only Super User and Admins can add new camera'}), 401

        data = request.get_json()
        json_data = data['report_data']
        start_date_str = json_data.get('start_date')
        end_date_str = json_data.get('end_date')
        query_page = json_data.get('query_page', 1)
        per_page = json_data.get('per_page', None)

        # Parse date strings to datetime objects with the correct format
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d %H:%M')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d %H:%M')

        # Calculate the offset based on the requested page and page size
        offset = (query_page - 1) * per_page if per_page else None

        # Query distinct job_ids between start_date and end_date
        distinct_job_ids = db.session.query(distinct(ProcessTable.job_id)).filter(
            ProcessTable.date_time.between(start_date, end_date),
        ).limit(per_page).offset(offset).all()

        # Extract job_ids from the result
        distinct_job_ids = [job_id[0] for job_id in distinct_job_ids]

        # Query entries for the selected job_ids
        entries = ProcessTable.query.filter(
            ProcessTable.job_id.in_(distinct_job_ids),
            ProcessTable.date_time.between(start_date, end_date),
        ).all()

        entries_by_group = defaultdict(lambda: {'date_time': '', 'vehicle_name': '', 'vehicle_parts': defaultdict(list)})

        for entry in entries:
            entry_data = {
                'id': entry.id,
                'admin_id': entry.admin_id,
                'operator_id': entry.operator_id,
                'part_code_name': entry.part_code_name,
                'part_code_requirement': entry.part_code_requirement,
                'scan_output': entry.scan_output,
                'result': entry.result,
                'image': base64.b64encode(entry.image).decode('utf-8') if entry.image else None,
                'approve_status': entry.approve_status
            }

            entries_by_group[entry.job_id]['job_id'] = entry.job_id
            entries_by_group[entry.job_id]['date_time'] = entry.date_time  # Corrected line
            entries_by_group[entry.job_id]['vehicle_name'] = entry.vehicle_name
            entries_by_group[entry.job_id]['vehicle_parts'][entry.vehicle_part].append(entry_data)

        # Convert entries_by_group to the desired format
        result_data = list(entries_by_group.values())

        # Query to count the total number of distinct job_ids
        total_job_ids = db.session.query(func.count(distinct(ProcessTable.job_id))).filter(
            ProcessTable.date_time.between(start_date, end_date)
        ).scalar()

        logger.info('Report Analysis API successfully processed')
        return jsonify({'result': result_data, 'total_job_ids': total_job_ids}), 200

    except Exception as e:
        logger.error('An error occurred in Report Analysis API: {}'.format(str(e)))
        return jsonify({'error': str(e)}), 500

        # # Serialize the entries to JSON and group by job_id, vehicle_part, and part_code_name
        # entries_by_group = defaultdict(lambda: defaultdict(list))
        # for entry in entries:
        #     entry_data = {
        #         'id': entry.id,
        #         'admin_id': entry.admin_id,
        #         'operator_id': entry.operator_id,
        #         'date_time': entry.date_time.strftime('%Y-%m-%dT%H:%M'),
        #         'vehicle_name': entry.vehicle_name,
        #         'part_code_name': entry.part_code_name,
        #         'part_code_requirement': entry.part_code_requirement,
        #         'scan_output': entry.scan_output,
        #         'result': entry.result,
        #         'image': base64.b64encode(entry.image).decode('utf-8') if entry.image else None,
        #         'approve_status': entry.approve_status
        #     }
        #     entries_by_group[entry.job_id][entry.vehicle_part].append(entry_data)

        # # Convert entries_by_group to the desired format
        # result_data = [
        #     {
        #         'job_id': job_id,
        #         'vehicle_parts': [
        #             {
        #                 'vehicle_part': vehicle_part,
        #                 'vehicle_part_reports': reports
        #             }
        #             for vehicle_part, reports in vehicle_parts.items()
        #         ]
        #     }
        #     for job_id, vehicle_parts in entries_by_group.items()
        # ]


@app.route('/report_analysis_by_job_id', methods=['POST'])
@jwt_required()
def get_entries_by_job_id():
    try:
        logger.info('Report Analysis by Job Id API called')

        user_id = get_jwt_identity()

        # Check if the user is an admin or super_user
        user = AllUsers.query.get(user_id)
        if user.user_type not in ["super_user", "admin"]:
            logger.warning('Unauthorized, only Super User and Admins can get Report Analysis by Job Id') 
            return jsonify({'message': 'Unauthorized, only Super User and Admins can get Report Analysis by Job Id'}), 401

        data = request.json

        entries = ProcessTable.query.filter_by(job_id=data['jobID']).all()
        if not entries:
            return jsonify({'message': 'No entries found for the specified job_id'})

        # Use a dictionary to group entries by vehicle_part
        grouped_entries = {}
        for entry in entries:
            entry_data = {
                'id': entry.id,
                'job_id': entry.job_id,
                'admin_id': entry.admin_id,
                'operator_id': entry.operator_id,
                'date_time': entry.date_time,
                'vehicle_name': entry.vehicle_name,
                'vehicle_part': entry.vehicle_part,
                'part_code_name': entry.part_code_name,
                'part_code_requirement': entry.part_code_requirement,
                'scan_output': entry.scan_output,
                'result': entry.result,
                'image': base64.b64encode(entry.image).decode('utf-8') if entry.image else None,
                'approve_status': entry.approve_status
            }
            
            if entry.vehicle_part not in grouped_entries:
                grouped_entries[entry.vehicle_part] = []
            
            grouped_entries[entry.vehicle_part].append(entry_data)

        return jsonify({'entries': grouped_entries, 'status': True}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Add New Camera rtsp as json
@app.route('/add_camera', methods=['POST'])
@jwt_required()
def add_camera():
    try:
        logger.info('Add Camera API called')

        # Obtain user identity from the JWT
        user_id = get_jwt_identity()

        # Check if the user is an admin or super_user
        user = AllUsers.query.get(user_id)
        if user.user_type not in ["super_user", "admin"]:
            logger.warning('Unauthorized, only Super User and Admins can add new camera') 
            return jsonify({'message': 'Unauthorized, only Super User and Admins can add new camera'}), 401

        data = request.json
        json_info = data['camDetails']
        camera_ip = json_info.get('camIP')
        user_id = json_info.get('userId')
        password = json_info.get('password')
        port = json_info.get('port')

        # Create the RTSP link
        rtsp_link = 'rtsp://' + user_id + ':' + password + '@' + camera_ip + ':' + port + '/?h264x=4'

        # Create the desired JSON structure
        json_data = {"rtsplink": rtsp_link}

        # You can customize the filename and path as needed
        filename = 'rtsp.json'
        filepath = os.path.join(app.root_path, filename)

        # Save the JSON data to a file
        with open(filepath, 'w') as file:
            json.dump(json_data, file)

        logger.info('Rtsp link successfully added')
        return jsonify({'message': 'Data saved successfully', 'status': True}), 200

    except Exception as e:
        logger.error('An error occurred in Add Camera API: {}'.format(str(e)))
        return jsonify({'error': str(e), 'status': False}), 400



# ############################# SUPER USER ##################################
# ################################ APIS #####################################

# User Registration
@app.route('/registration', methods=['POST'])
@jwt_required()
def register_user():
    try:
        logger.info('Registration API called')

        # Obtain user identity from the JWT
        user_id = get_jwt_identity()

        # Check if the user is super_user
        user = AllUsers.query.get(user_id)
        if user.user_type != "super_user":
            logger.warning('Unauthorized, only Super User can registers new users') 
            return jsonify({'message': 'Unauthorized, only Super User can registers new users'}), 401

        data = request.json
        json_data = data['data']

        # Check if 'employee_id', 'name', 'designation', 'password', and 'user_type' are in the request data
        if 'employee_id' not in json_data or 'name' not in json_data or 'password' not in json_data or 'user_type' not in json_data:
            return jsonify({'error': 'All fields are required'}), 400

        # Check if the provided employee_id is not already in use
        existing_user = AllUsers.query.get(json_data['employee_id'])
        if existing_user:
            logger.warning('Employee ID already in use. Please choose a different one.') 
            return jsonify({'error': 'Employee ID already in use. Please choose a different one.'}), 400

        # Create a new user
        new_user = AllUsers(
            employee_id=json_data['employee_id'],
            name=json_data['name'],
            password=json_data['password'],
            user_type=json_data['user_type']
        )
        db.session.add(new_user)
        db.session.commit()

        logger.info('User registration successful for employee_id: {}'.format(json_data['employee_id']))
        return jsonify({'message': 'User registration successful', 'status': True}), 201

    except Exception as e:
        logger.error('An error occurred in registration API: {}'.format(str(e)))
        return jsonify({'error': str(e)}), 500


# Modify Admin/Operator Password
@app.route('/modify_password', methods=['PUT'])
@jwt_required()
def modify_password():
    try:
        logger.info('Modify Password API called')
        user_id = get_jwt_identity()

        user = AllUsers.query.get(user_id)

        if user and user.user_type != "super_user":
            logger.warning('Unauthorized, only Super User can modify passwords') 
            return jsonify({'message': 'Unauthorized, only Super User can modify passwords'}), 401

        json_data = request.json
        data = json_data['data']
        # Check if 'employee_id' and 'new_password' are in the request data
        employee_id = data.get('employee_id')
        new_password = data.get('new_password')

        if not employee_id or not new_password:
            return jsonify({'error': 'Employee ID and new password are required'}), 400

        # Query the database for the user with the specified employee_id
        user = AllUsers.query.get(employee_id)

        if user:
            # Update the password
            user.password = new_password
            db.session.commit()

            logger.info('Password modified successfully for employee_id: {}'.format(employee_id))
            return jsonify({'message': 'Password modified successfully', 'status': True}), 200
        else:
            logger.warning('User not found for Modify Password API - employee_id: {}'.format(employee_id))
            return jsonify({'error': 'User not found'}), 404

    except Exception as e:
        logger.error('An error occurred in Modify Password API: {}'.format(str(e)))
        return jsonify({'error': 'Internal Server Error'}), 500


# Number of Users API
@app.route('/number_of_users', methods=['GET', 'POST'])
@jwt_required()
def get_user_stats():
    try:
        logger.info('Get User Stats API called')

        # Obtain user identity from the JWT
        user_id = get_jwt_identity()

        # Check if the user is an admin or super_user
        user = AllUsers.query.get(user_id)
        if user.user_type != "super_user":
            logger.warning('Unauthorized, only Super User and Admins can get number of users') 
            return jsonify({'message': 'Unauthorized, only Super User and Admins can get number of users'}), 401
        
        operators_count = AllUsers.query.filter_by(user_type='operator').count()
        admins_count = AllUsers.query.filter_by(user_type='admin').count()

        logger.info('Number of users successfully returned')
        return jsonify({'operators': operators_count, 'admins': admins_count}), 200

    except Exception as e:
        logger.error('An error occurred in Get User Stats API: {}'.format(str(e)))
        return jsonify({'error': str(e)}), 500


# Weekly graph report
@app.route('/weekly_report', methods=['GET'])
@jwt_required()
def weekly_report():
    try:
        logger.info('Get Weekly Reports API called')

        # Obtain user identity from the JWT
        user_id = get_jwt_identity()

        # Check if the user is an admin or super_user
        user = AllUsers.query.get(user_id)
        if user and user.user_type not in ["admin", "super_user"]:
            logger.warning('Unauthorized, only Super User and Admins can get weekly reports') 
            return jsonify({'message': 'Unauthorized, only Super User and Admins can get weekly reports'}), 401

        now = datetime.now()

        # Calculate the start date of the current week
        start_date_current_week = now - timedelta(days=now.weekday() + 1)

        # Calculate the start date of the previous week
        start_date_previous_week = start_date_current_week - timedelta(days=7)

        # Query entries for both the current week and the previous week
        entries_current_week = ProcessTable.query.filter(ProcessTable.date_time >= start_date_current_week).all()
        entries_previous_week = ProcessTable.query.filter(
            ProcessTable.date_time >= start_date_previous_week,
            ProcessTable.date_time < start_date_current_week
        ).all()

        # Count entries for the current week
        daywise_count_current_week = {}
        for entry in entries_current_week:
            day = entry.date_time.strftime('%Y-%m-%d')
            daywise_count_current_week[day] = daywise_count_current_week.get(day, 0) + 1

        # Count entries for the previous week
        daywise_count_previous_week = {}
        for entry in entries_previous_week:
            day = entry.date_time.strftime('%Y-%m-%d')
            daywise_count_previous_week[day] = daywise_count_previous_week.get(day, 0) + 1

        logger.info('Weekly report successfully returned')
        return jsonify({
            'current_week': daywise_count_current_week,
            'previous_week': daywise_count_previous_week
        })

    except Exception as e:
        logger.error('An error occurred in Get Weekly Reports API: {}'.format(str(e)))
        return jsonify({'error': str(e)}), 500
    
@app.route('/quarterly_report', methods=['GET'])
@jwt_required()
def quarterly_report():
    try:
        logger.info('Quarterly Reports API called')

        user_id = get_jwt_identity()

        user = AllUsers.query.get(user_id)
        if user and user.user_type not in ["admin", "super_user"]:
            return jsonify({'message': 'Unauthorized, only Super User and Admins can get quarterly reports'}), 401
        
        now = datetime.now()
        start_date = now.replace(month=1, day=1)
        start_date += timedelta(days=90 * ((now.month - 1) // 3))

        quarterly_counts = db.session.query(
            func.count().label('total'),
            func.sum(case((ProcessTable.approve_status == 'Approved', 1), else_=0)).label('Approved'),
            func.sum(case((ProcessTable.approve_status == 'Rejected', 1), else_=0)).label('Rejected')
        ).filter(
            ProcessTable.date_time >= start_date,
            ProcessTable.approve_status.in_(['Approved', 'Rejected'])
        ).first()
        return jsonify({
            'quarterly_report': {
                'approved': quarterly_counts.Approved,
                'rejected': quarterly_counts.Rejected,
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


    

# ############################# ADMIN ####################################
# ############################# APIS #####################################


# API endpoint to get entries with 'Pending' approve_status and update approval status
@app.route('/pending_status_change', methods=['PUT'])
@jwt_required()
def pending_status_change():
    try:
        logger.info('Change Pending Report Status API called')

        user_id = get_jwt_identity()

        # Check if the user is an admin or super_user
        user = AllUsers.query.get(user_id)

        # Add your custom authorization check here
        if user and user.user_type != "admin":
            logger.warning('Unauthorized, only Admins can modify status') 
            return jsonify({'message': 'Unauthorized, only Admins can modify status'}), 401

        # Get data from the request JSON body
        data = request.get_json()

        # Validate and extract data
        entry_id = data.get('id')
        new_status = data.get('approve_status')

        # Use a single update query to change the approval status
        updated_rows = ProcessTable.query.filter_by(id=entry_id).update({'approve_status': new_status})

        # Commit the changes to the database
        db.session.commit()

        if updated_rows > 0:
            logger.info('Report Status updated successfully')
            return jsonify({'message': f'Approval status updated for entry with ID {entry_id}'}), 200
        else:
            logger.warning('Report not found')
            return jsonify({'error': f'Entry with ID {entry_id} not found', 'status': True}), 404

    except Exception as e:
        logger.error('An error occurred in Changing Status API: {}'.format(str(e)))
        return jsonify({'error': str(e)}), 500


# Pending Admin Reports
from collections import defaultdict

@app.route('/get_pending_reports', methods=['GET'])
@jwt_required()
def get_pending_reports():
    try:
        logger.info('Get Pending Reports API called')

        user_id = get_jwt_identity()

        # Check if the user is an admin or super_user
        user = AllUsers.query.get(user_id)

        # Add your custom authorization check here
        if user and user.user_type != "admin":
            logger.warning('Unauthorized, only Admins can fetch pending reports')
            return jsonify({'message': 'Unauthorized, only Admins can fetch pending reports'}), 401

        entries = ProcessTable.query.filter_by(admin_id=user_id, approve_status='Pending').all()

        # Convert the query results to a list of dictionaries
        entries_by_group = defaultdict(lambda: {'date_time': '', 'vehicle_name': '', 'vehicle_parts': defaultdict(list)})

        for entry in entries:
            entry_data = {
                'id': entry.id,
                'admin_id': entry.admin_id,
                'operator_id': entry.operator_id,
                'part_code_name': entry.part_code_name,
                'part_code_requirement': entry.part_code_requirement,
                'scan_output': entry.scan_output,
                'result': entry.result,
                'image': base64.b64encode(entry.image).decode('utf-8') if entry.image else None,
                'approve_status': entry.approve_status
            }

            entries_by_group[entry.job_id]['job_id'] = entry.job_id
            entries_by_group[entry.job_id]['date_time'] = entry.date_time  # Corrected line
            entries_by_group[entry.job_id]['vehicle_name'] = entry.vehicle_name
            entries_by_group[entry.job_id]['vehicle_parts'][entry.vehicle_part].append(entry_data)

        # Convert entries_by_group to the desired format
        result_data = list(entries_by_group.values())

        logger.info('Get Pending Reports API returned')
        return jsonify({'result': result_data, 'status': True}), 200

    except Exception as e:
        logger.error('An error occurred in Get Pending Reports API: {}'.format(str(e)))
        return jsonify({'error': str(e)}), 500




#Admin Password Change
@app.route('/modify_admin_password', methods=['PUT'])
@jwt_required()
def modify_admin_password():
    try:
        logger.info('Modify Admin password API called')

        user_id = get_jwt_identity()

        user = AllUsers.query.get(user_id)

        # Add your custom authorization check here
        if user and user.user_type != "admin":
            logger.warning('Unauthorized, only admins can modify passwords')
            return jsonify({'message': 'Unauthorized, only admins can modify passwords'}), 401

        json_data = request.get_json()
        data = json_data['data']
        old_password = data.get('oldPassword')
        new_password = data.get('newPassword')

        # Update the password only if the current user is an admin
        updated_rows = AllUsers.query.filter_by(employee_id=user.employee_id, password=old_password).update({'password': new_password})
        db.session.commit()

        if updated_rows > 0:
            logger.info('Admin password successfully updated') 
            return jsonify({'message': 'Password modified successfully', 'status': True}), 200
        else:
            logger.warning('Invalid credentials or old password does not match')
            return jsonify({'message': 'Invalid credentials or old password does not match'}), 401

    except Exception as e:
        logger.error('An error occurred in Modify Admin Password API: {}'.format(str(e)))
        return jsonify({'error': str(e)}), 500


@app.route('/move_to_final/<job_id>', methods=['POST'])
@jwt_required()
def move_to_final(job_id):
    try:
        logger.info('Move to final table API called')

        user_id = get_jwt_identity()

        user = AllUsers.query.get(user_id)

        # Add your custom authorization check here
        if user and user.user_type != "admin":
            logger.warning('Unauthorized, Admin aceess required.')
            return jsonify({'message': 'Unauthorized, Admin aceess required.'}), 401
        
        # Check if all entries with the given job_id have either 'approved' or 'rejected' status
        process_entries = ProcessTable.query.filter_by(job_id=job_id).all()
        
        if all(entry.approve_status in ['approved', 'rejected'] for entry in process_entries):
            # Move entries to FinalTable
            final_entries = []
            for entry in process_entries:
                final_entry = FinalTable(
                    job_id=entry.job_id,
                    admin_id=entry.admin_id,
                    operator_id=entry.operator_id,
                    date_time_operator=entry.date_time,
                    date_time_admin=datetime.now(),
                    vehicle_name=entry.vehicle_name,
                    vehicle_part=entry.vehicle_part,
                    part_code_name=entry.part_code_name,
                    part_code_requirement=entry.part_code_requirement,
                    scan_output=entry.scan_output,
                    result=entry.result,
                    image=entry.image,
                    approve_status=entry.approve_status
                )
                final_entries.append(final_entry)
            
            # Add entries to FinalTable
            db.session.add_all(final_entries)
            db.session.commit()

            # Delete entries from ProcessTable
            for entry in process_entries:
                db.session.delete(entry)
            db.session.commit()

            return jsonify({'message': 'Rows moved to FinalTable successfully'}), 200
        else:
            return jsonify({'message': 'Not all entries have approved or rejected status'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/reinspect_reports', methods=['POST'])
@jwt_required()
def reinspect_reports():
    try:
        logger.info('Reinspect Reports API called')

        user_id = get_jwt_identity()

        # Check if the user is an admin or super_user
        user = AllUsers.query.get(user_id)
        if user.user_type != "admin":
            logger.warning('Unauthorized, only Admins can update approve status') 
            return jsonify({'message': 'Unauthorized, only Admins can update approve status'}), 401

        data = request.get_json()
        job_id = data.get('job_id')
        print(job_id)
        vehicle_part_id = data.get('vehicle_part_id', [])
        print(vehicle_part_id)

        # Validate if job_id and vehicle_part_ids are present in the request body
        if not job_id or not vehicle_part_id:
            return jsonify({'message': 'Please provide both job_id and vehicle_part_ids'}), 400

        # Update the approve_status to 'Reinspect' for the specified job_id and vehicle_part_ids
        ProcessTable.query.filter(
            ProcessTable.job_id == job_id,
            ProcessTable.vehicle_part_id.in_(vehicle_part_id)
        ).update({'approve_status': 'Reinspect'}, synchronize_session=False)

        # Commit the changes to the database
        db.session.commit()

        logger.info('Update Approve Status API successfully processed')
        return jsonify({'message': 'Approve status updated successfully'}), 200

    except Exception as e:
        logger.error('An error occurred in Update Approve Status API: {}'.format(str(e)))
        return jsonify({'error': str(e)}), 500




















@app.route('/add_process', methods=['POST'])
def index():
    # Example: Adding a process to the database
    new_entry = ProcessTable(
    job_id='job2',
    admin_id='admin123',
    operator_id='operator789',
    date_time='2024-01-23 02:00:00',
    vehicle_name='Grazia',
    vehicle_part='Air Filter',
    part_code_name = 'Id on Case',
    part_code_requirement='XYZ',
    scan_output='XYZ',
    result='True',
    image=b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\xf3\xeea\x00\x00\x00\x0bIDAT\x08\xd7c\xf8\xff\xff?\x00\x05\xfe\x02\xfe\xb2\x0c\xfeIEND\xaeB`\x82',
    approve_status='Pending',
)
    db.session.add(new_entry)
    db.session.commit()

    return 'Process added to the database!'





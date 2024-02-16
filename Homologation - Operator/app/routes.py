import string, random, base64, cv2, json, jwt
from flask import request, jsonify, render_template
from app import app, db, socketio, logger
from app.models import AllUsers, VehicleDetails, ProcessTable,Test, LoginLog, TestTable
from datetime import datetime
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from collections import deque
from flask_socketio import emit

final_frame = None
ocr_text = None

# year(2 digits) + month(2 digits) + date(2 digits) + hour(2 digits) + min(2 digits) + sec(2 digits) + first 4 of emp_id(fetch from jwt token) + random alphanumeric 4 digits (total 20 digits)
def generate_job_id(emp_id):
    # Get the current date and time
    now = datetime.now()

    # Extract individual components
    year = now.strftime('%y')
    month = now.strftime('%m')
    day = now.strftime('%d')
    hour = now.strftime('%H')
    minute = now.strftime('%M')
    second = now.strftime('%S')

    # Extract the first 4 digits of emp_id
    emp_id_prefix = emp_id[:4] if len(emp_id) >= 4 else emp_id

    # Generate random alphanumeric 4 digits
    random_digits = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))

    # Concatenate all components to form the job ID
    job_id = f"{year}{month}{day}{hour}{minute}{second}{emp_id_prefix}{random_digits}"

    return job_id

# Load the RTSP link from the JSON file
with open('app/rtsp.json', 'r') as file:
    rtsp_config = json.load(file)

rtsp_link = rtsp_config.get('rtsp_link', '')

# Initialize the camera using the RTSP link
camera = cv2.VideoCapture(0)

def cam_feed():
    global final_frame
    global ocr_text
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Encode the frame to base64
        _, buffer = cv2.imencode('.jpg', frame)
        frame_encoded = base64.b64encode(buffer)

        # Perform OCR on the frame
        ocr_text = ocr_output(frame)
        print(ocr_text)

        if ocr_text:
            # Save the frame and OCR text to the database
            final_frame = frame_encoded

            # Emit the frame and OCR text to all connected clients
            socketio.emit('image', {'image': frame_encoded.decode('utf-8')}, namespace='/camera')
            
        socketio.sleep(1)

    cap.release()

def perform_ocr(frame):
    return "ME$"

# Queue to store recent OCR results
ocr_results_queue = deque(maxlen=5)

# Function to simulate OCR output from a model
def ocr_output(frame):
    simulated_ocr_result = perform_ocr(frame)

    # Add the simulated result to the queue
    ocr_results_queue.append(simulated_ocr_result)
    print(ocr_results_queue)

    # If the queue is full and all elements are the same, return the result
    if len(ocr_results_queue) == 5 and len(set(ocr_results_queue)) == 1:
        return ocr_results_queue[0]

    # If not, return None
    return None

# Function to perform OCR validation
def ocr_validation(vehicle_part_id, job_id):
    try:
        global ocr_text
        # Retrieve the Test record based on the provided ID
        test_record = TestTable.query.filter_by(vehicle_part_id=vehicle_part_id, job_id=job_id).first()
        if test_record:

            if ocr_text is not None:
                print(ocr_text)
                print(test_record.part_code_requirement) 
                # Compare the OCR result with the "Expected_Value" column
                if ocr_text == test_record.part_code_requirement:
                    # Update the result field
                    test_record.result = 'True'
                else:
                    test_record.result = 'False'
                    
                # Commit the changes to the database
                db.session.commit()

                return ocr_text
            else:
                return False

        return False

    except Exception as e:
        # Handle exceptions and return False in case of an error
        print(f"An error occurred: {str(e)}")
        return False

@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('connect', namespace='/camera')
def handle_connect():
    print('Client Connected')
    # Start the background thread when the first client connects
    if not socketio.thread:
        socketio.thread = socketio.start_background_task(target=cam_feed)



# @socketio.on('disconnect', namespace='/camera')
# def handle_disconnect():
#     logger.info('Client disconnected')
#     print('disconnected....')
#     # Try to reconnect after a delay
#     delay = 5 
#     time.sleep(delay)
#     socketio.emit('reconnect', namespace='/camera')


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
            access_token = create_access_token(identity=user.employee_id, expires_delta=datetime.timedelta(hours=10))
            
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
            login_log = LoginLog.query.filter_by(user_id=user, logout_time=None).first()

            if login_log:
                login_log.logout_time = logout_time
                db.session.commit()

        logger.info('Logout successful for user {}'.format(user_id))
        return jsonify({'message': 'Logout successful for user id: {}'.format(user_id)}), 200

    except Exception as e:
        logger.error('An error occurred in logout API: {}'.format(str(e)))
        return jsonify({'error': str(e)}), 500


# Get data for scan from db
@app.route('/get_inspection_data', methods=['GET'])
@jwt_required()
def inspection_data():
    try:
        user_id = get_jwt_identity()

        # Check if the user is an admin or super_user
        user = AllUsers.query.get(user_id)
        if user.user_type != "operator":
            logger.warning('Unauthorized, only Operator can get inspection data') 
            return jsonify({'message': 'Unauthorized, only Operator can get inspection data'}), 401
        
        data = request.json
        vehicle_name = data['vehicle_name']
        vehicle_model = data['vehicle_model']
        vehicle_variant = data['vehicle_variant']

        table_name = f"{vehicle_name}{vehicle_model}{vehicle_variant}"
        print(table_name)
        
        parts_mapping = {}

        entries = Test.query.all()
        for entry in entries:
            part_name = entry.Parts.lower()

            if part_name not in parts_mapping:
                parts_mapping[part_name] = {}

            # Include "ID" along with "Regulation_Requirements" and "Expected_Value"
            parts_mapping[part_name][entry.Regulation_Requirements] = {
                'ID': entry.ID,
                'Expected_Value': entry.Expected_Value
            }

        logger.info('Inspection data retrieved successfully')
        return jsonify(parts_mapping)

    except Exception as e:
        logger.error(f'Error in /get_inspection_data API: {str(e)}')
        return jsonify({'error': f'Error in /get_inspection_data API: {str(e)}'}), 500


# get vehicle data available before scan
@app.route('/vehicle-details', methods=['GET'])
@jwt_required()
def get_rows_by_name():
    try:
        user_id = get_jwt_identity()

        # Check if the user is an admin or super_user
        user = AllUsers.query.get(user_id)
        if user.user_type != "operator":
            logger.warning('Unauthorized, only Operator can getvehicle details.') 
            return jsonify({'message': 'Unauthorized, onlyOperator can getvehicle details.'}), 401
        
        jsonData = request.json
        data = jsonData['data']
        vehicle_name= data['vehicle_name']

        # Query the database to get all rows where 'part_name' column matches the provided value
        all_values = VehicleDetails.query.filter_by(name=vehicle_name).all()

        # Create a list to store the results
        results = []

        # Iterate over the query result and append data to the results list
        for entry in all_values:
            results.append({
                'name': entry.name,
                'model': entry.model, 
                'variant': entry.variant,
            })

        # Return the results in the response
        logger.info(f'Vehicle details returned successfully for name: {vehicle_name}')
        return jsonify({'results': results}), 200

    except Exception as e:
        logger.error(f'Error in /vehicle-details/{vehicle_name} API: {str(e)}')
        return jsonify({'error': f'Error in /vehicle-details/{vehicle_name} API: {str(e)}'}), 500



#Abort operation
@app.route('/abort', methods=['DELETE'])
@jwt_required()
def abort():
    try:
        user_id = get_jwt_identity()

        # Check if the user is an admin or super_user
        user = AllUsers.query.get(user_id)
        if user.user_type != "operator":
            logger.warning('Unauthorized, only Operator can abort opertion.') 
            return jsonify({'message': 'Unauthorized, only Operator can abort opertion.'}), 401
        
        data = request.json
        job_id = data['job_id']

        # Query the database to get entries with the specified job_id
        entries_to_delete = TestTable.query.filter_by(job_id=job_id).all()

        # Delete each entryF
        for entry in entries_to_delete:
            db.session.delete(entry)

        # Commit the changes to the database
        db.session.commit()

        logger.info(f'Entries deleted successfully for job_id {job_id}')
        return jsonify({'message': 'Entries deleted successfully', 'status': True}), 200

    except Exception as e:
        logger.error(f'Error in /abort/{job_id} API: {str(e)}')
        return jsonify({'error': str(e)}), 500

# fetch all values for job_id before submitting
@app.route('/final_report', methods=['GET'])
@jwt_required()
def get_entries_by_job_id():
    try:
        user_id = get_jwt_identity()

        # Check if the user is an admin or super_user
        user = AllUsers.query.get(user_id)
        if user.user_type != "operator":
            logger.warning('Unauthorized, only Operator can check final report after scan.') 
            return jsonify({'message': 'Unauthorized, only Operator can check final report after scan.'}), 401
        
        jsonData = request.json
        data = jsonData['data']
        job_id= data['job_id']
        
        # Query the database for entries with the specified job_id and current admin_id
        entries = ProcessTable.query.filter_by(job_id=job_id).all()

        # Serialize the entries to JSON
        entries_data = []
        for entry in entries:
            entry_data = {
                'id': entry.id,
                'job_id': entry.job_id,
                'operator_id': entry.operator_id,
                'date_time': entry.date_time.isoformat(),
                'vehicle_name': entry.vehicle_name,
                'vehicle_part': entry.vehicle_part,
                'vehicle_part_id' : entry.vehicle_part_id,
                'part_code_name': entry.part_code_name,
                'part_code_requirement': entry.part_code_requirement,
                'scan_output': entry.scan_output,
                'result': entry.result,
                'image': base64.b64encode(entry.image).decode('utf-8') if entry.image else None,
                'approve_status': entry.approve_status
            }
            entries_data.append(entry_data)

        logger.info(f'Final reports returned to operator successfully for job_id {job_id}')
        return jsonify({'entries': entries_data}), 200

    except Exception as e:
        logger.error(f'Error in /final_report/{job_id} API: {str(e)}')
        return jsonify({'error': str(e)}), 500


@app.route('/scan_part', methods=['POST'])
@jwt_required()
def scan_part():
    try:
        user_id = get_jwt_identity()

        # Check if the user is an admin or super_user
        user = AllUsers.query.get(user_id)
        if user.user_type != "operator":
            logger.warning('Unauthorized, only Operator can scan parts.') 
            return jsonify({'message': 'Unauthorized, only Operator can scan parts.'}), 401
        
        data = request.json

        part = TestTable.query.filter_by(job_id=data['job_id'], vehicle_part_id=data['vehicle_part_id']).first()



        if part:
            scan_output = ocr_validation(data['vehicle_part_id'], data['job_id'])
            part.scan_output = scan_output

            # Access the global variable final_frame here and save it to the database
            global final_frame
            if final_frame:
                part.image = final_frame
                final_frame = None  # Reset the global variable

            db.session.commit()

            logger.info('Scan output stored successfully')
            return jsonify({'message': 'Scan output stored successfully', 'scan_output': scan_output}), 200
        else:
            return jsonify({'message': 'Part not found for the specified job_id and vehicle_part_id'}), 404

    except Exception as e:
        logger.error(f'Error in /scan_part API: {str(e)}')
        return jsonify({'error': str(e)}), 500    


@app.route('/start_inspection', methods=['POST'])
@jwt_required()
def start_inspection():
    try:
        user_id = get_jwt_identity()

        # Check if the user is an admin or super_user
        user = AllUsers.query.get(user_id)
        if user.user_type != "operator":
            logger.warning('Unauthorized, only Operator can start inspection.') 
            return jsonify({'message': 'Unauthorized, only Operator can start inspection.'}), 401
        
        data = request.json
        vehicle_name = data['vehicle_name']
        vehicle_model = data['vehicle_model']
        vehicle_variant = data['vehicle_variant']

        table_name = f"{vehicle_name}{vehicle_variant}{vehicle_model}"
        print(table_name)

        user_id = get_jwt_identity()

        job_id = generate_job_id(user_id)
        print(job_id)

        # Fetch values from Test table based on the provided table_name
        entries = Test.query.all()

        # Map and store values in ProcessTable
        process_entries = []
        for entry in entries:
            process_entry = TestTable(
                job_id=job_id,
                admin_id='', 
                operator_id=user_id,
                vehicle_name=vehicle_name,
                vehicle_part=entry.Parts,
                vehicle_part_id=entry.ID,
                part_code_name=entry.Regulation_Requirements,
                part_code_requirement=entry.Expected_Value,
                scan_output='',
                result='',   
                approve_status='Pending'
            )
            process_entries.append(process_entry)

        # Add entries to ProcessTable
        db.session.add_all(process_entries)
        db.session.commit()

        logger.info(f'Inspection started successfully')
        return jsonify({'message': 'Inspection started successfully'}), 200
    
    except Exception as e:
        logger.error(f'Error in /start_inspection API: {str(e)}') 
        return jsonify({'error': str(e)}), 500 
        

@app.route('/update_admin_id', methods=['POST'])
@jwt_required()
def update_admin_id():
    try:
        user_id = get_jwt_identity()

        # Check if the user is an admin or super_user
        user = AllUsers.query.get(user_id)
        if user.user_type != "operator":
            logger.warning('Unauthorized, only Operator can update admin id.') 
            return jsonify({'message': 'Unauthorized, only Operator can update admin id.'}), 401
        
        data = request.json
        admin_id = data.get('admin_id')
        job_id = data.get('job_id')

        # Update admin_id for entries with the specified job_id
        entries = TestTable.query.filter_by(job_id=job_id).all()
        for entry in entries:
            entry.admin_id = admin_id
            entry.date_time = datetime.now()

        db.session.commit()

        logger.info(f'Admin ID updated successfully for job_id {job_id}')
        return jsonify({'message': f'Admin ID updated for job_id {job_id}'}), 200

    except Exception as e:
        logger.error(f'Error in /update_admin_id API: {str(e)}')
        return jsonify({'error': f'Error in /update_admin_id API: {str(e)}'}), 500



@app.route('/get_admins', methods=['GET'])
@jwt_required()
def get_admins():
    try:
        logger.info('Get Admin API called')

        user_id = get_jwt_identity()

        user = AllUsers.query.get(user_id)

        # Add your custom authorization check here
        if user and user.user_type != "admin":
            logger.warning('Unauthorized, only Operators can get admin list.')
            return jsonify({'message': 'Unauthorized, only Operators can get admin list.'}), 401
    
        # Query the database for users with user_type as 'admin'
        admin_users = AllUsers.query.filter_by(user_type='admin').all()

        # Extract employee_id from each admin user
        admin_ids = [user.employee_id for user in admin_users]

        return jsonify({'admin_ids': admin_ids}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    

@app.route('/get_reinspect_reports', methods=['GET'])
@jwt_required()
def get_reinspect_reports():
    try:
        logger.info('Get reinspect reports API called')

        user_id = get_jwt_identity()

        user = AllUsers.query.get(user_id)

        # Add your custom authorization check here
        if user and user.user_type != "operator":
            logger.warning('Unauthorized, only Operators can get reinspect reports.')
            return jsonify({'message': 'Unauthorized, only Operators can get reinspect reports.'}), 401
    
        # Query the database for users with user_type as 'admin'
        reinspect_reports = ProcessTable.query.filter_by(approve_status='Reinspect').all()

        grouped_reports = {}
        for report in reinspect_reports:
            job_id = report.job_id

            if job_id not in grouped_reports:
                grouped_reports[job_id] = []

            grouped_reports[job_id].append({
                'id': report.id,
                'admin_id': report.admin_id,
                'operator_id': report.operator_id,
                'date_time': report.date_time.strftime('%Y-%m-%d %H:%M:%S'),
                'vehicle_name': report.vehicle_name,
                'vehicle_part': report.vehicle_part,
                'vehicle_part_id': report.vehicle_part_id,
                'part_code_name': report.part_code_name,
                'part_code_requirement': report.part_code_requirement,
                'scan_output': report.scan_output,
                'result': report.result,
                'image': base64.b64encode(report.image).decode('utf-8') if report.image else None,
                'approve_status': report.approve_status
            })

        logger.info('Reinspect reports successfully fetched')
        return jsonify({'reinspect_reports': grouped_reports}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


#  MAKE UPDATE REINSPECT API (JOB_ID and PART_ID)

# 1. Fix admin/super_user apis for final table
# 2. When all things are approved and admin clicks submit, shift all data to final table.
# 3. APIs to change: get pending reports, report_analysis (change table), weekly/ quarterly reports(show checks or jobs?), can db run 2 queries at one time.
    


# 1. DONE - dash-> inspection (vehicle api)
# 2. DONE - get vehicle table info on start inspection (get vehicle name to get that table, and create job_id and import data from that table to process table.)
# 3. DONE - scan_api - get job_id, part id, scan image from websocket, check for 5 frames from ocr, call validation, then store scan output, image, result, in processtable.
# 4. on submit - store admin_id(send to front end also, might have to make api)(take input from front_end), and date_time. 

# 5. dash-> reinspect, store time of reinspection?
# 6. when to shift to final table. 
    

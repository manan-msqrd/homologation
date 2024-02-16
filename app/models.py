from app import db

class AllUsers(db.Model):
    employee_id = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    user_type = db.Column(db.String(10), nullable=False)
    login_logs = db.relationship('LoginLog', backref='all_user', lazy=True)


class LoginLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(20), db.ForeignKey('all_users.employee_id'), nullable=False)
    login_time = db.Column(db.DateTime, nullable=False)
    logout_time = db.Column(db.DateTime)


class VehicleDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    variant = db.Column(db.String(50), nullable=False)
    model = db.Column(db.String(50), nullable=False)

class ProcessTable(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    job_id = db.Column(db.String(20), nullable=False)
    admin_id = db.Column(db.String(50), nullable=False)
    operator_id = db.Column(db.String(50), nullable=False)
    date_time = db.Column(db.DateTime, nullable=False)
    vehicle_name = db.Column(db.String(20), nullable=False)
    vehicle_part = db.Column(db.String(50))
    vehicle_part_id = db.Column(db.Integer)
    part_code_name = db.Column(db.String(100))
    part_code_requirement = db.Column(db.String(50))
    scan_output = db.Column(db.String(50))
    result = db.Column(db.String(20), nullable=False)
    image = db.Column(db.LargeBinary())
    approve_status = db.Column(db.String(50), nullable=False, default='Pending')

class FinalTable(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    job_id = db.Column(db.String(20), nullable=False)
    admin_id = db.Column(db.String(50), nullable=False)
    operator_id = db.Column(db.String(50), nullable=False)
    date_time_operator = db.Column(db.DateTime, nullable=False)
    date_time_admin = db.Column(db.DateTime, nullable=False)
    vehicle_name = db.Column(db.String(20), nullable=False)
    vehicle_part = db.Column(db.String(50))
    part_code_name = db.Column(db.String(550))
    part_code_requirement = db.Column(db.String(50))
    scan_output = db.Column(db.String(50))
    result = db.Column(db.String(20), nullable=False)
    image = db.Column(db.LargeBinary())
    approve_status = db.Column(db.String(50), nullable=False)

class TestTable(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True) 
    job_id = db.Column(db.String(20), nullable=False) # create with start inspec
    admin_id = db.Column(db.String(50), nullable=False) # at the end with submit report
    operator_id = db.Column(db.String(50), nullable=False) # fetch from token during submit
    date_time = db.Column(db.DateTime) # during submit
    vehicle_name = db.Column(db.String(20), nullable=False) # from front end when start inspection
    vehicle_part = db.Column(db.String(550)) # from front-end with scan 
    vehicle_part_id = db.Column(db.Integer) # from front-end with scan 
    part_code_name = db.Column(db.String(550)) # from front-end with scan 
    part_code_requirement = db.Column(db.String(550)) # from test table (expected value)
    scan_output = db.Column(db.String(50)) #
    result = db.Column(db.String(20), nullable=False) #True/ false/ scanned
    image = db.Column(db.LargeBinary()) # fetch with websocket
    approve_status = db.Column(db.String(50), nullable=False, default='Pending')

class Test(db.Model):
    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Parts = db.Column(db.String(50))
    Regulation_Requirements = db.Column(db.String(510))
    Expected_Value = db.Column(db.String(255))

# class TableStatus(db.Model):
#     job_id = db.Column(db.String(20), primary_key=True, autoincrement=True)
#     table_status = db.Column(db.String(50), nullable=False, default='Pending')
#     date_time_operator = db.Column(db.DateTime, nullable=False)
#     date_time_admin = db.Column(db.DateTime, nullable=False)
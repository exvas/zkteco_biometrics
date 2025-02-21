# Copyright (c) 2025, sammish and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime
from zkteco_biometrics.zkteco_biometrics.zkteco.attendance import get_attendance
import json
from datetime import datetime, timedelta

class ZKTeco(Document):
    pass

punchMap = {
    0: "IN",
    1: "OUT"
}

@frappe.whitelist()
def get_attendance_by_date(device_id, ip_address, clear_device_log:bool, port=4370, timeout=30, from_date=None, to_date=None):
    try:
        frappe.enqueue(
        	get_device_attendance,
        	device_id=device_id,
        	ip_address=ip_address,
        	clear_device_log=clear_device_log,
        	port=port,
        	timeout=timeout,
        	from_date=from_date,
            to_date=to_date,  
        	queue="long"
        )
        # get_device_attendance(
        #     device_id=device_id,
        #     ip_address=ip_address,
        #     clear_device_log=clear_device_log,
        #     port=port,
        #     timeout=timeout,
        #     from_date=from_date,
        #     to_date=to_date)
    except Exception as e:
        frappe.log_error(message=e,title="Zkteco - Data by date")

def get_device_attendance(device_id, ip_address, clear_device_log:bool, port=4370, timeout=30, from_date=None, to_date=None):
    try:
        date_list = generate_date_range(from_date, to_date)
        data = attn = []
        attn_data = get_attendance(
            ip=ip_address,
            port=4370,
            timeout=timeout,
            device_id=device_id,
            clear_from_device_on_fetch=False
        )
        if attn_data:
            data = attn_data.get("attendance")
        if data and date_list:
            data = data[::-1]
            for i in data:
                if not i.timestamp.strftime("%Y-%m-%d") in date_list:
                    continue
                employee = frappe.db.get_value("Employee", {"attendance_device_id": i.user_id}, "name")
                if not employee:
                    frappe.log_error(message="Orphaned user id: {0}".format(i.user_id), title="Zkteco - Scheduler")
                    continue
                if not frappe.db.exists("Employee Checkin", {"time": i.timestamp, "employee": employee}):
                    attendance = frappe.new_doc("Employee Checkin")
                    attendance.employee = employee
                    attendance.time = i.timestamp
                    attendance.log_type = punchMap[i.punch]
                    attendance.device_id = device_id
                    attendance.insert()
                attn.append(i)
        log = frappe.new_doc("ZKTeco")
        log.title = datetime.now()
        log.attendance = str(attn)
        log.insert()
                
    except Exception as e:
        frappe.log_error(message=e,title="Zkteco - Data by date")
    

def generate_date_range(from_date: str, to_date: str):
    from_dt = datetime.strptime(from_date, "%Y-%m-%d")
    to_dt = datetime.strptime(to_date, "%Y-%m-%d")

    if from_dt > to_dt:
        raise ValueError("From Date must be earlier than To Date")
    else:
        date_list = [(from_dt + timedelta(days=i)).strftime("%Y-%m-%d") for i in range((to_dt - from_dt).days + 1)]
        return date_list
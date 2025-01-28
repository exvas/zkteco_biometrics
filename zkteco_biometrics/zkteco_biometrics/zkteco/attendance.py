import frappe
from zk import ZK, const
from datetime import datetime

def get_attendance(ip:str, port=4370, timeout=30, device_id=None, clear_from_device_on_fetch=False):
    conn = None
    try:
        zk = ZK(ip=ip, port=int(port), timeout=int(timeout))
        conn = zk.connect()
        disable_device = None
        attendance = None
        enable_device = None
        clear_attendance = None
        disable_device = conn.disable_device()
        attendance = conn.get_attendance()
        clear_attendance = ""
        if clear_from_device_on_fetch:
            clear_attendance = conn.clear_attendance()
        enable_device = conn.enable_device()
        return {"attendance": attendance, "disable_device": disable_device, "clear_attendance": clear_attendance, "enable_device": enable_device}
    except Exception as e:
        frappe.log_error(message=e,title="Zkteco - Get Attendance")
    finally:
        if conn:
            conn.disconnect()
        
punchMap = {
    0: "IN",
    1: "OUT"
}

@frappe.whitelist()
def get_attendance_by_device():
    devices = frappe.db.get_all("Devices", {"disable_data_capture": False}, ["*"])
    try:
        for device in devices:
            attn_data = get_attendance(
                ip=device.ip,
                port=4370,
                timeout=30, 
                device_id=device.device_id,
                clear_from_device_on_fetch=device.clear_device_log
            )
            data = []
            if attn_data:
                data = attn_data.get("attendance")
            if data:
                data = data[::-1]
                for i in data:
                    if i.timestamp.strftime("%Y-%m-%d") != datetime.now().strftime("%Y-%m-%d"):
                        frappe.log_error(message=i.timestamp.strftime("%Y-%m-%d"), title="Zkteco - Scheduler")
                        break
                    employee = frappe.db.get_value("Employee", {"attendance_device_id": i.user_id}, "name")
                    if not employee:
                        frappe.log_error(message="Orphaned user id: {0}".format(i.user_id), title="Zkteco - Scheduler")
                        continue
                    if not frappe.db.exists("Employee Checkin", {"time": i.timestamp, "employee": employee}):
                        attendance = frappe.new_doc("Employee Checkin")
                        attendance.employee = employee
                        attendance.time = i.timestamp
                        attendance.log_type = punchMap[i.punch]
                        attendance.device_id = device.device_id
                        attendance.insert()
    except Exception as e:
        frappe.log_error(message=e,title="Zkteco - Scheduler")
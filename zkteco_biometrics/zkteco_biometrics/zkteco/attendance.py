import frappe
from zk import ZK, const

def get_attendance(ip:str, port=4370, timeout=30, device_id=None, clear_from_device_on_fetch=False):
    conn = None
    try:
        zk = ZK(ip="ip", port=port, timeout=timeout)
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
        frappe.throw("Something wrong! Please check error log.")
    finally:
        if conn:
            conn.disconnect()

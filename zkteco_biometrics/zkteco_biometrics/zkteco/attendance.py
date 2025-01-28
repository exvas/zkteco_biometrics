import frappe
from zk import ZK, const

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
        frappe.throw("Something wrong! Please check error log.")
    finally:
        if conn:
            conn.disconnect()


@frappe.whitelist()
def get_attendance_by_device(device_id, ip_address, clear_device_log:bool, port=4370, timeout=30):
	# ip, port=4370, timeout=30, device_id=None, clear_from_device_on_fetch=False
	data = get_attendance(
			ip=ip_address,
			port=4370,
			timeout=timeout,
			device_id=device_id,
			clear_from_device_on_fetch=clear_device_log
		)

	log_doc = frappe.new_doc("ZKTeco")
	log_doc.title = datetime.now()
	log_doc.attendance = json.dumps(data.get("attendance")[0:5]) if data.get("attendance") else ""
	log_doc.disable_device = str(data.get("disable_device")) if data.get("disable_device") else ""
	log_doc.enable_device = str(data.get("enable_device")) if data.get("disable_device") else ""
	log_doc.clear_device = str(data.get("clear_attendance")) if data.get("clear_attendance") else ""
	log_doc.insert()
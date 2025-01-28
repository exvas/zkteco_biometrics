# Copyright (c) 2025, sammish and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from datetime import datetime
from zkteco_biometrics.zkteco_biometrics.zkteco.attendance import get_attendance

class ZKTeco(Document):
	pass
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
	log_doc.attendance = data.get("attendance")[0:5] if data.get("attendance") else ""
	log_doc.disable_device = str(data.get("disable_device")) if data.get("disable_device") else ""
	log_doc.enable_device = str(data.get("enable_device")) if data.get("disable_device") else ""
	log_doc.clear_device = str(data.get("clear_attendance")) if data.get("clear_attendance") else ""
	log_doc.insert()


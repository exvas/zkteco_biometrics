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
	log_doc.attendance = data.get("attendance")
	log_doc.disable_device = data.get("disable_device")
	log_doc.enable_device = data.get("enable_device")
	log_doc.clear_device = data.get("clear_attendance")
	log_doc.insert()


// Copyright (c) 2024, sammish and contributors
// For license information, please see license.txt

frappe.ui.form.on("Devices", {
	refresh(frm) {
        frm.add_custom_button("Fetch Attendance", ()=>{
            frappe.prompt([
                {
                    fieldtype: "Date",
                    label: __("From Date"),
                    fieldname: "from_date",
                    reqd: 1,
                },
                {
                    fieldtype: "Date",
                    label: __("To Date"),
                    fieldname: "to_date",
                    reqd: 1,
                }
            ],
            function(data){
                frappe.msgprint("Started")
                frappe.call({
                    // freeze: true,
                    // freeze_message: "Please wait...",
                    method: "zkteco_biometrics.zkteco_biometrics.doctype.zkteco.zkteco.get_attendance_by_date",
                    args: {
                        device_id: frm.doc.device_id, 
                        ip_address: frm.doc.ip,
                        clear_device_log: frm.doc.clear_device_log,
                        port: 4370, 
                        timeout: 30,
                        from_date: data.from_date,
                        to_date: data.to_date
                    },
                    callback(r){
                        frappe.msgprint("Completed")
                    }
                })
            })
            
        })
	},
});

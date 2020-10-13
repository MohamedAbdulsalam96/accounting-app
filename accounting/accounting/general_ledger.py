from __future__ import unicode_literals
import frappe
from frappe.model.document import Document

def make_gl_entries(gl_entry):
    for gl in gl_entry:
        gl.update({"doctype": "GL Entry"});
        doc = frappe.get_doc(gl);
        doc.insert();

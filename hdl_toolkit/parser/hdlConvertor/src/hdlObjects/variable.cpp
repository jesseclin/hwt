#include "variable.h"

PyObject* Variable::toJson() const {
	PyObject*d = Named::toJson();
	if (!type)
		throw "Variable has no type";

	PyDict_SetItemString(d, "type", type->toJson());

	if (value) {
		PyDict_SetItemString(d, "value", value->toJson());
	} else {
		Py_IncRef(Py_None);
		PyDict_SetItemString(d, "value", Py_None);
	}
	Py_IncRef(d);
	return d;
}

void Variable::dump(int indent) const {
	Named::dump(indent);
	indent += INDENT_INCR;
	dumpKey("type", indent);
	type->dump(indent);
	std::cout << ",\n";

	if (value) {
		dumpKey("value", indent);
		value->dump(indent);
	} else {
		dumpVal("value", indent, "None");
	}
	mkIndent(indent - INDENT_INCR) << "}";
}

#include "context.h"

PyObject * Context::toJson() const {
	PyObject * c = PyDict_New();
	addJsonArrP(c, "imports", imports);
	addJsonArrP(c, "entities", entities);
	addJsonArrP(c, "architectures", architectures);
	addJsonArrP(c, "packages", packages);
	addJsonArrP(c, "packageHeaders", packageHeaders);
	Py_INCREF(c);
	return c;
}

void Context::dump(int indent) const {
	mkIndent(indent) << "{\n";
	indent += INDENT_INCR;
	dumpArrP("imports", indent, imports) << ",\n";
	dumpArrP("entities", indent, entities) << ",\n";
	dumpArrP("architectures", indent, architectures) << ",\n";
	dumpArrP("packages", indent, packages) << ",\n";
	dumpArrP("packageHeaders", indent, packageHeaders) << ",\n";
	indent -= INDENT_INCR;
	mkIndent(indent) << "}";
}

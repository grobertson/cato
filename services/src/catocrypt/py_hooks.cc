//########################################################################
// Copyright 2012 Cloud Sidekick
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//    http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
//########################################################################

#include <Python.h>
#include <string.h>
#include <stdlib.h>
#include "blowfish.h"

using namespace std;

static PyObject* encrypt_string(PyObject* self, PyObject *args)
{
    char *pword = NULL;
    char *key = NULL;
    string ePassword;
    PyObject *result = NULL;

    if (!PyArg_ParseTuple(args, "ss", &pword, &key)) {
      return NULL;
    }
    if (strlen(pword) == 0) {
	PyErr_SetString(PyExc_ValueError, "String to encrypt cannot be empty");
	return NULL;
    }

    encryptPassword(pword, ePassword, key);
    result = Py_BuildValue("s", (char *)ePassword.c_str());

    return result;
}

static PyObject* decrypt_string(PyObject* self, PyObject *args)
{
    char *ePword = NULL;
    char *key = NULL;
    string pword;
    PyObject *result = NULL;

    if (!PyArg_ParseTuple(args, "ss", &ePword, &key)) {
      return NULL;
    }
    if (strlen(ePword) == 0) {
	PyErr_SetString(PyExc_ValueError, "String to decrypt cannot be empty");
	return NULL;
    }
    decryptPassword(ePword, pword, key);
    result = Py_BuildValue("s", (char *)pword.c_str());

    return result;

}
static char encrypt_string_docs[] = "encrypt_string(string,key): Encrypts a string using the Cato blowfish algorithm\n";
static char decrypt_string_docs[] = "decrypt_string(string,key): Decrypts a string using the Cato blowfish algorithm\n";

static PyMethodDef catocryptpy_funcs[] = {
    {"encrypt_string", (PyCFunction)encrypt_string, METH_VARARGS, encrypt_string_docs},
    {"decrypt_string", (PyCFunction)decrypt_string, METH_VARARGS, decrypt_string_docs},
    {NULL}
};

PyMODINIT_FUNC initcatocryptpy(void)
{
    Py_InitModule3("catocryptpy", catocryptpy_funcs, "Cato blowfish module");
}

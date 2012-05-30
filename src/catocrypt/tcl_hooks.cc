//########################################################################
// Copyright 2011 Cloud Sidekick
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

//#include "tcl_hooks.h"
#include <tcl.h>
#include <string.h>
#include <stdlib.h>
#include "blowfish.h"

extern "C" {



using namespace std;

int
tcl_encryptPassword(ClientData clientData, Tcl_Interp *interp, int objc,
            Tcl_Obj * CONST objv[])
{
    char *pword = NULL;
    char *key = NULL;
    static char key_string[32];
    string ePassword;
    if (objc != 3) {
        Tcl_SetResult(interp, (char *)"ERROR: encrypt requires exactly two arguments:string_to_encrypt and key", TCL_VOLATILE);
        return TCL_ERROR;
    }
    pword = strdup((const char *)objv[1]);
    if (!pword) {
        Tcl_SetResult(interp, (char *)"ERROR: Unable to retrieve password from params.", TCL_VOLATILE);
        return TCL_ERROR;
    }
    key = strdup((const char *)objv[2]);

    if (!encryptPassword(pword, ePassword, key)) {
        Tcl_SetResult(interp, (char *)"ERROR: Failed to encrypt password.", TCL_VOLATILE);
        return TCL_ERROR;
    }

    Tcl_SetResult(interp, (char *)ePassword.c_str(), TCL_VOLATILE);
    free(pword);
    free(key);
    return TCL_OK;
}

int
tcl_decryptPassword(ClientData clientData, Tcl_Interp *interp, int objc,
            Tcl_Obj * CONST objv[])
{
    char *ePword = NULL;
    char *key = NULL;
    static char key_string[32];
    string pword;
    if (objc != 3) {
        Tcl_SetResult(interp, (char *)"ERROR: decrypt requires exactly two arguments:string_to_decrypt and key", TCL_VOLATILE);
        return TCL_ERROR;
    }

    ePword = strdup((const char *)objv[1]);
    key = strdup((const char *)objv[2]);
    if (!ePword) {
        Tcl_SetResult(interp, (char *)"ERROR: Unable to retrieve encrypted password from params.", 
                TCL_VOLATILE);
        return TCL_ERROR;
    }

    if (!decryptPassword(ePword, pword, key)) {
        Tcl_SetResult(interp, (char *)"ERROR: Failed to decrypt password.", TCL_VOLATILE);
        return TCL_ERROR;
    }

    Tcl_SetResult(interp, (char *)pword.c_str(), TCL_VOLATILE);
    free(ePword);
    free(key);
    return TCL_OK;
}

    int
    Catocrypttcl_Init(Tcl_Interp * interp)
    {
	if (Tcl_InitStubs(interp, "8.4", 0) == NULL) {
		return TCL_ERROR;
	}
        Tcl_CreateCommand(interp, "encrypt_string", (Tcl_CmdProc *) tcl_encryptPassword, NULL, NULL);
	Tcl_CreateCommand(interp, "decrypt_string", (Tcl_CmdProc *) tcl_decryptPassword, NULL, NULL);
	Tcl_PkgProvide(interp, "catocrypttcl", "1.0");

		return TCL_OK;
        return TCL_OK;
    }
    int Catocrypttcl_SafeInit(Tcl_Interp *interp) {
        return Catocrypttcl_Init(interp);
    }
    int Catocrypttcl_SafeUnload(Tcl_Interp *interp) {}
    int Catocrypttcl_Unload(Tcl_Interp *interp) {}

}

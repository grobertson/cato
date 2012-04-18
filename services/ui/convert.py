#!/usr/bin/env python

import re

out = ""

with open("convert.in", 'r') as f_in:
    if not f_in:
        print "ERROR: convert.in not found."

    for line in f_in:
        INDENT = 0
        sINDENTp4 = "    "

        # FIRST THINGS FIRST ... for Python, we wanna fix tabs into spaces...
        line = line.replace("\t", "    ")
        
        # now that the tabs are fixed, 
        # we wanna count the whitespace at the beginning of the line
        # might use it later for indent validation, etc.
        p = re.compile(r"^\s+")
        m = p.match(line)
        if m:
            INDENT = len(m.group())
        
        #if INDENT > 0 and INDENT < 4:
        #    line = "SHORT INDENT\n" + line
            
        #if INDENT >= 4:
        #    if INDENT % 4:
        #        line = "!! BAD INDENT\n" + line

        sINDENT = " " * INDENT
        # this string global contains the current indent level + 4
        sINDENTp4 = " " * (INDENT+4)
        # + 8
        sINDENTp8 = " " * (INDENT+8)
        
        # braces are a tricky, but lets first just remove any lines that only contain an open/close brace
        if line.strip() == "{": continue
        if line.strip() == "}": continue
              
        # if the brace appears at the end of a line (like after an "if")
        if len(line.strip()) > 1:
            s = line.strip()
            if s[-1] == "{":
                line = s[:-1]
        
        # comments
        if line.strip()[:2] == "//":
            line = line.replace("//", "# ")
        line = line.replace("/*", "\"\"\"").replace("*/", "\"\"\"")
        
        # Fixing semicolon line endings (not otherwise, may be in a sql statement or something)
        line = line.replace(";\n", "\n")

        # Fixing line wrapped string concatenations
        line = line.replace("+\n", "\\\n")

        
        # Fixing function declarations...    
        line = line.replace("public ", "def ")
        line = line.replace("private ", "def ")
        if line.strip()[:3] == "def":
            line = line.replace(")", "):")
        
        # Fixing variable declarations...    
        # doing "string" and "int" again down below with a regex, because they could be a line starter, or part of a bigger word
        line = line.replace(" int ", " ").replace(" string ", " ").replace(" bool ", " ").replace(" void ", " ")
        line = line.replace("(int ", "(").replace("(string ", "(").replace("(bool ", "(")

        # common C# functions and keywords
        line = line.replace(".ToString()", "") # no equivalent, not necessary
        line = line.replace(".ToLower()", ".lower()")
        line = line.replace("\" + Environment.NewLine", "\\n\"")
        line = line.replace(".IndexOf(", ".find(")
        line = line.replace(".Replace", ".replace")
        line = line.replace(".Trim()", ".strip()")
        line = line.replace("HttpContext.Current.Server.MapPath(", "") # this will leave a trailing paren !
        line = line.replace(".Value", ".findtext(value, \"\")") #should work most of the time for Cato code
        

        # Try/Catch blocks
        line = line.replace("try", "try:")
        line = line.replace("catch (Exception ex)", "except Exception, ex:")
        # I often threw "new exceptions" - python doesn't need the extra stuff
        line = line.replace("new Exception", "Exception")
        line = line.replace("throw", "raise")
        
        
        # no longer needed
        if line.strip() == "dataAccess dc = new dataAccess()":
            continue

        #these commonly appear on a line alone, and we aren't using them any more
        if line.strip() == "acUI.acUI ui = new acUI.acUI()": continue
        if line.strip() == "sErr = \"\"": continue
        if line.lower().strip() == "ssql = \"\"": continue # there's mixed case usage of "sSql"
        if "dataAccess.acTransaction" in line: continue
        if line.strip() == "DataRow dr = null": continue
        if line.strip() == "DataTable dt = new DataTable()": continue

        
        # a whole bunch of common phrases from Cato C# code
        line = line.replace("Globals.acObjectTypes", "uiGlobals.CatoObjectTypes")
        line = line.replace("ui.", "uiCommon.")
        line = line.replace("dc.IsTrue", "uiCommon.IsTrue")
        line = line.replace("../images", "static/images")
        
        
        #these now need a db connection passed in
        line = line.replace("WriteObjectChangeLog(", "WriteObjectChangeLog(db, ")
        line = line.replace("WriteObjectAddLog(", "WriteObjectAddLog(db, ")
        line = line.replace("WriteObjectDeleteLog(", "WriteObjectDeleteLog(db, ")
        
        # this will *usually work
        line = line.replace("if (!dc.sqlExecuteUpdate(sSQL, ref sErr))", "if not db.exec_db_noexcep(sSQL):")
        if "!dc.sqlGetSingleString" in line:
            line = sINDENT + "00000 = db.select_col_noexcep(sSQL)\n" + sINDENT + "if db.error:\n"
        line = line.replace("+ sErr", "+ db.error") # + sErr is *usually used for displaying a db error.  Just switch it.
        line = line.replace("if (!oTrans.ExecUpdate(ref sErr))", "if not db.tran_exec_noexcep(sSQL):")
        line = line.replace("oTrans.Command.CommandText", "sSQL") # transactions are different, regular sSQL variable
        line = line.replace("oTrans.Commit()", "db.tran_commit()")
        line = line.replace("oTrans.RollBack()", "db.tran_rollback()")
        line = line.replace("DataRow dr in dt.Rows", "dr in dt")
        line = line.replace("dt.Rows.Count > 0", "dt")
        
        # this will be helpful
        if "CommonAttribs" in line:
            line = "### CommonAttribsWithID ????\nuiCommon.NewGUID()\n" + line
        
        # random stuff that may or may not work
        line = line.replace("== null", "is None")
        line = line.replace("!= null", "is not None")
        if line.strip() == "if (!dc.sqlGetDataRow(ref dr, sSQL, ref sErr))":
            line = sINDENT + "dr = db.select_row_dict(sSQL)\n" + sINDENT + "if db.error:\n" + sINDENTp4 + "raise Exception(db.error)\n"
        if line.strip() == "if (!dc.sqlGetDataTable(ref dt, sSQL, ref sErr))":
            line = sINDENT + "dt = db.select_all_dict(sSQL)\n" + sINDENT + "if db.error:\n" + sINDENTp4 + "raise Exception(db.error)\n"
        # xml/Linq stuff
        line = line.replace(".Attribute(", ".get(")

        # true/false may be problematic, but these should be ok
        line = line.replace(", true", ", True").replace(", false", ", False")
        
        
        line = line.replace("XDocument.Load", "ET.parse")
        line = line.replace("XDocument ", "").replace("XElement ", "")
        line = line.replace("XDocument.Parse", "ET.fromstring")
        line = line.replace("IEnumerable<XElement> ", "")
        
        # note the order of the following
        line = line.replace(".XPathSelectElements", ".findall").replace(".XPathSelectElement", ".find") 
        line = line.replace(".SetValue", ".text")
        
        line = line.replace("ex.Message", "ex.__str__()")

        #!!! this has to be done after the database stuff, because they all use a "ref sErr" and we're matching on that!
        # passing arguments by "ref" doesn't work in python, mark that code obviously
        # because it need attention
        line = line.replace("ref ", "0000BYREF_ARG0000")

        # if this is a function declaration and it's a "wm" web method, 
        # throw the new argument getter line on there
        if "def wm" in line:
            line = line + sINDENTp4 + "ARG = uiCommon.getAjaxArg(\"ARG\")\n"

        # else statements on their own line
        if line.strip() == "else":
            line = line.replace("else", "else:")

        # let's try some stuff with regular expressions
        # string and int declarations
        p = re.compile("^int ")
        m = p.match(line)
        if m:
            line = line.replace("int ", "")
        p = re.compile("^string ")
        m = p.match(line)
        if m:
            line = line.replace("string ", "")
        
        # if statements
        p = re.compile(".*if \(.*\)")
        m = p.match(line)
        if m:
            line = line.replace("if (", "if ")
            line = line[:-2] + ":\n"

        # foreach statements (also marking them because type declarations may need fixing)
        p = re.compile(".*foreach \(.*\)")
        m = p.match(line)
        if m:
            line = line.replace("foreach (", "for ")
            line = line[:-2] + ":\n"
            line = "### CHECK NEXT LINE for type declarations !!!\n" + line

        p = re.compile(".*while \(.*\)")
        m = p.match(line)
        if m:
            line = line.replace("while (", "while ")
            line = line[:-2] + ":\n"
            line = "### CHECK NEXT LINE for type declarations !!!\n" + line

        # && and || comparison operators in an "if" statement
        p = re.compile("^.*if.*&&")
        m = p.match(line)
        if m:
            line = line.replace("&&", "and")
            line = "### VERIFY 'ANDs' !!!\n" + line

        p = re.compile("^.*if.*\|\|")
        m = p.match(line)
        if m:
            line = line.replace("||", "or")
            line = "### VERIFY 'ORs' !!!\n" + line
        

        out += line
    
with open("convert.out", 'w') as f_out:
    if not f_out:
        print "ERROR: unable to create convert.out."

    f_out.write(out)

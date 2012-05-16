"""
    Tags are used to establish user-defined relationships between objects.
    For example, by giving a user and a task the same tag, you ensure that user can 
    manage that task.
"""
import json
from catocommon import catocommon

""" Tags is a list of all the defined tags.  It's different from 'ObjectTags', which is a list of relationships."""
class Tags(object): 
    rows = {}

    def __init__(self, sFilter="", sObjectID=""):
        try:
            sWhereString = ""
            if sFilter:
                aSearchTerms = sFilter.split()
                for term in aSearchTerms:
                    if term:
                        sWhereString += " and (t.tag_name like '%%" + term + "%%' " \
                            "or t.tag_desc like '%%" + term + "%%') "
    
            # if an object id arg is passed, we explicitly limit to that object
            if sObjectID:
                sWhereString += " and ot.object_id = '%s'" % sObjectID
                
            sSQL = """select t.tag_name, t.tag_desc, count(ot.tag_name) as in_use
                from tags t
                left outer join object_tags ot on t.tag_name = ot.tag_name
                where (1=1) %s
                group by t.tag_name, t.tag_desc
                order by t.tag_name""" % sWhereString
            
            db = catocommon.new_conn()
            self.rows = db.select_all_dict(sSQL)
        except Exception, ex:
            raise Exception(ex)
        finally:
            db.close()

    def AsJSON(self):
        try:
            return json.dumps(self.rows)
        except Exception, ex:
            raise ex

class Tag(object):
    ID = ""
    FullName = ""


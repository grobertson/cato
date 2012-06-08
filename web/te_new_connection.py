
# Copyright 2012 Cloud Sidekick
#  
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#  
#     http:# www.apache.org/licenses/LICENSE-2.0
#  
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
 


# there is a global connection object in the task_engine.
# it's a dictionary of connections.
# whatever we create here, add it to that dict.


# here's a conversation - these steps have a short life span... they execute and go away.
# so, there's no need to for this to be a class...
# because instantiating a class for each command could eat up memory

# on a case by case basis you may want to, but usually I think you won't.

# so... this is not a class!


def connect(step):
    print "in connect"
    import te_globals

    print te_globals.connections
    te_globals.connections["this_conn"] = "hey baby"
    
    return ""
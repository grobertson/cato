

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
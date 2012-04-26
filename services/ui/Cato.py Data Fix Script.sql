#select function_xml from task_step
#where function_xml like '%<function command_type="cmd_line" parse_method="2">%'

update task_step set function_xml = 
replace(function_xml,'command_type="sql_exec" parse_method="1"','command_type="sql_exec" variables="true" parse_method="1"')
where function_name = 'sql_exec';

update task_step set function_xml = 
replace(function_xml,'command_type="cmd_line" parse_method="2"','command_type="cmd_line" variables="true" parse_method="2"')
where function_name = 'cmd_line';

update task_step set function_xml = 
replace(function_xml,'command_type="read_file" parse_method="2"','command_type="read_file" variables="true" parse_method="2"')
where function_name = 'read_file';

update task_step set function_xml = 
replace(function_xml,'command_type="http" parse_method="2"','command_type="http" variables="true" parse_method="2"')
where function_name = 'http';

update task_step set function_xml = 
replace(function_xml,'command_type="parse_text" parse_method="2"','command_type="parse_text" variables="true" parse_method="2"')
where function_name = 'parse_text';

## COMMAND LINE command
update task_step set function_xml = 
replace(function_xml,
'<conn_name input_type="text">',
'<conn_name input_type="text" connection_picker="true" label="Connection" break_after="true" required="true">'
)
where function_name = 'cmd_line';
update task_step set function_xml = 
replace(function_xml,
'<conn_name input_type="text" />',
'<conn_name input_type="text" connection_picker="true" label="Connection" break_after="true" required="true" />'
)
where function_name = 'cmd_line';

update task_step set function_xml = 
replace(function_xml,
'<command input_type="text">',
'<command input_type="textarea" rows="3" label="Command" class="w95pct" required="true" label_style="display: block;">'
)
where function_name = 'cmd_line';
update task_step set function_xml = 
replace(function_xml,
'<command input_type="text" />',
'<command input_type="textarea" rows="3" label="Command" class="w95pct" required="true" label_style="display: block;" />'
)
where function_name = 'cmd_line';

update task_step set function_xml = 
replace(function_xml,
'<timeout input_type="text">',
'<timeout input_type="text" option_tab="Options" label="Timeout" break_after="true">'
)
where function_name = 'cmd_line';
update task_step set function_xml = 
replace(function_xml,
'<timeout input_type="text" />',
'<timeout input_type="text" option_tab="Options" label="Timeout" break_after="true" />'
)
where function_name = 'cmd_line';

update task_step set function_xml = 
replace(function_xml,
'<positive_response input_type="text">',
'<positive_response input_type="text" option_tab="Options" label="Positive Response" break_after="true">'
)
where function_name = 'cmd_line';
update task_step set function_xml = 
replace(function_xml,
'<positive_response input_type="text" />',
'<positive_response input_type="text" option_tab="Options" label="Positive Response" break_after="true" />'
)
where function_name = 'cmd_line';

update task_step set function_xml = 
replace(function_xml,
'<negative_response input_type="text">',
'<negative_response input_type="text" option_tab="Options" label="Negative Response" break_after="true">'
)
where function_name = 'cmd_line';
update task_step set function_xml = 
replace(function_xml,
'<negative_response input_type="text" />',
'<negative_response input_type="text" option_tab="Options" label="Negative Response" break_after="true" />'
)
where function_name = 'cmd_line';



# DROP CONNECTION
update task_step set function_xml = 
replace(function_xml,
'<conn_name input_type="text">',
'<conn_name input_type="text" label="Connection">'
)
where function_name = 'drop_connection';

# END
update task_step set 
function_xml = replace(function_xml,
'<status input_type="select">',
'<status input_type="select" label="Status">'
),
function_xml = replace(function_xml,
'<message input_type="text">',
'<message input_type="textarea" rows="3" label="Message" class="w95pct" label_style="display: block;">'
)
where function_name = 'end';

# SLEEP
update task_step set 
function_xml = replace(function_xml,
'<seconds input_type="text">',
'<seconds input_type="text" label="Sleep">'
)
where function_name = 'sleep';

# CANCEL TASK
update task_step set 
function_xml = replace(function_xml,
'<task_instance input_type="text">',
'<task_instance input_type="text" label="Task Instance ID(s)">'
)
where function_name = 'cancel_task';

# SET LOGGING LEVEL
update task_step set 
function_xml = replace(function_xml,
'<debug_level input_type="text">',
'<debug_level input_type="dropdown" label="Logging Level" datasource="function" dataset="ddDataSource_GetDebugLevels">'
)
where function_name = 'set_debug_level';

# GET TASK INSTANCE
update task_step set 
function_xml = replace(function_xml,
'<instance input_type="text">',
'<instance input_type="text" label="Task Instance">'
),
function_xml = replace(function_xml,
'<handle input_type="text">',
'<handle input_type="text" label="Handle">'
)
where function_name = 'get_instance_handle';
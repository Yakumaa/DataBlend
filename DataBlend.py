import bpy
import psycopg2

# Database connection parameters
conn_params = {
    "dbname": "DataBlend",
    "user": "postgres",
    "password": "1234",
    "host": "localhost",
    "port": "5432"
}

# Table and column names
table_name = "characters"
id_column = "id"
name_column = "name"
height_column = "height"
weight_column = "weight"
eye_color_column = "eye_color"

        
# Define UI panel
class CharacterCreatorPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Character Creator"
    bl_idname = "OBJECT_PT_character_creator"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"
        
    def draw(self, context):
        layout = self.layout

        # Create character section
        create_box = layout.box()
        col = create_box.column(align=True)
        col.label(text="Create Character")
        col.prop(context.scene, "name")
        col.prop(context.scene, "height")
        col.prop(context.scene, "weight")
        col.prop(context.scene, "eye_color")
        col.operator("character_creator.create_character")

        #Read Character section
        read_box = layout.box()
        col = read_box.column(align=True)
        col.label(text="Retrieve Character")
        row = col.row(align=True)
        row.prop(context.scene, "retrieved_id")
        row.operator("object.read_character", text="", icon="FILE_REFRESH")
        col.separator()
        col.prop(context.scene, "retrieved_name", text="Name")
        col.prop(context.scene, "retrieved_height", text="Height")
        col.prop(context.scene, "retrieved_weight", text="Weight")
        col.prop(context.scene, "retrieved_eye_color", text="Eye Color")
        
        # Update character section
        update_box = layout.box()
        col = update_box.column(align=True)
        col.label(text="Update Character")
        col.prop(context.scene, "update_id")
        col.prop(context.scene, "update_name")
        col.prop(context.scene, "update_height")
        col.prop(context.scene, "update_weight")
        col.prop(context.scene, "update_eye_color")
        col.operator("character_creator.update_character")

        # Delete character section
        delete_box = layout.box()
        col = delete_box.column(align=True)
        col.label(text="Delete Character")
        col.prop(context.scene, "delete_id")
        col.operator("character_creator.delete_character")
        
        
table_panel_timer = None    
class MyAddonPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_my_addon_panel"
    bl_label = "My Addon Panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "DataBlend"

    def draw(self, context):
        global table_panel_timer
        layout = self.layout
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()
        cur.execute("SELECT * FROM characters")
        rows = cur.fetchall()
#        for row in rows:
#            col = layout.column()
#            col.label(text=f"id: {row[0]}")
#            col.label(text=f"name: {row[1]}")
#            col.label(text=f"height: {row[2]}")
#            col.label(text=f"weight: {row[3]}")
#            col.label(text=f"eye_color: {row[4]}")
#            col.separator() 

         # Create a list of column widths based on the maximum width of each field
        col_widths = [max(len(str(row[i])) for row in rows) for i in range(len(rows[0]))]

        # Add the header row with the column names
        header_row = layout.row()
        header_row.label(text="id")
        header_row.label(text="name")
        header_row.label(text="height")
        header_row.label(text="weight")
        header_row.label(text="eye_color")

        # Add a separator row between the header row and the data rows
        sep_row = layout.row()
        sep_row.separator()

        # Add the data rows with the field values aligned vertically
        for row in rows:
            data_row = layout.row()
            for i in range(len(row)):
                data_row.label(text=str(row[i]).ljust(col_widths[i]))
                
        # Add the reload button
        layout.separator()
        layout.operator("object.reload_table", text="Reload", icon="FILE_REFRESH")         


        if table_panel_timer is None:
            table_panel_timer = bpy.app.timers.register(self.timer_callback)

    def timer_callback(self):
        # Call the internal operator to reload the table data
        bpy.ops.object.reload_table_internal()
        return 0.1

# Define create character operator
class CreateCharacterOperator(bpy.types.Operator):
    """Create a new character in the database"""
    bl_idname = "character_creator.create_character"
    bl_label = "Create Character"

    def execute(self, context):
        name = context.scene.name
        height = float(context.scene.height)
        weight = float(context.scene.weight)
        eye_color = context.scene.eye_color
        create_character(name, height, weight, eye_color)
        
        # Clear the fields in the Object Properties panel
        context.scene.name = ""
        context.scene.height = 0.0
        context.scene.weight = 0.0
        context.scene.eye_color = ""
        
        return {'FINISHED'}

#Define read charcter operator
class ReadCharacterOperator(bpy.types.Operator):
    bl_idname = "object.read_character"
    bl_label = "Read Character"
    
    def execute(self, context):
        id = bpy.context.scene.retrieved_id
        result = read_character(id)
        if result is not None:
            bpy.context.scene.retrieved_name = result[1]
            bpy.context.scene.retrieved_height = result[2]
            bpy.context.scene.retrieved_weight = result[3]
            bpy.context.scene.retrieved_eye_color = result[4]
            self.report({'INFO'}, f"Retrieved character with ID {id}")
        else:
            self.report({'ERROR'}, f"Character with ID {id} not found")
            
#        # Clear the fields in the Object Properties panel
#        #context.scene.update_id = 0
#        context.scene.retrieved_name = ""
#        context.scene.retrieved_height = 0.0
#        context.scene.retrieved_weight = 0.0
#        context.scene.retrieved_eye_color = ""
        
        return {'FINISHED'}


# Define update character operator
class UpdateCharacterOperator(bpy.types.Operator):
    """Update an existing character in the database"""
    bl_idname = "character_creator.update_character"
    bl_label = "Update Character"

    def execute(self, context):
        id = context.scene.update_id
        name = context.scene.update_name
        height = context.scene.update_height
        weight = context.scene.update_weight
        eye_color = context.scene.update_eye_color
        update_character(id, name=name, height=height, weight=weight, eye_color=eye_color)
        
        # Clear the fields in the Object Properties panel
        context.scene.update_id = 0
        context.scene.update_name = ""
        context.scene.update_height = 0.0
        context.scene.update_weight = 0.0
        context.scene.update_eye_color = ""
        return {'FINISHED'}

# Define delete character operator
class DeleteCharacterOperator(bpy.types.Operator):
    """Delete an existing character from the database"""
    bl_idname = "character_creator.delete_character" 
    bl_label = "Delete Character"

    def execute(self, context):
        id = context.scene.delete_id
        delete_character(id)
        
        # Clear the fields in the Object Properties panel
        context.scene.delete_id = 0
        
        return {'FINISHED'}

class ReloadTableOperator(bpy.types.Operator):
    bl_idname = "object.reload_table"
    bl_label = "Reload Table"

    def execute(self, context):
        bpy.ops.object.reload_table_internal()
        return {'FINISHED'}

class ReloadTableInternalOperator(bpy.types.Operator):
    bl_idname = "object.reload_table_internal"
    bl_label = "Reload Table Internal"

    def execute(self, context):
        return {'FINISHED'}

# Register UI panel and operators
def register():
    bpy.utils.register_class(CharacterCreatorPanel)
    bpy.utils.register_class(MyAddonPanel)
    bpy.utils.register_class(CreateCharacterOperator)
    bpy.utils.register_class(ReadCharacterOperator)
    bpy.utils.register_class(UpdateCharacterOperator)
    bpy.utils.register_class(DeleteCharacterOperator)
    bpy.utils.register_class(ReloadTableOperator)
    bpy.utils.register_class(ReloadTableInternalOperator)


#Unregister UI panel and operators
def unregister():
    bpy.utils.unregister_class(CharacterCreatorPanel)
    bpy.utils.unregister_class(MyAddonPanel)
    bpy.utils.unregister_class(CreateCharacterOperator)
    bpy.utils.unregister_class(ReadCharacterOperator)
    bpy.utils.unregister_class(UpdateCharacterOperator)
    bpy.utils.unregister_class(DeleteCharacterOperator)
    bpy.utils.unregister_class(ReloadTableOperator)
    bpy.utils.unregister_class(ReloadTableInternalOperator)

    global table_panel_timer
    if table_panel_timer is not None:
        bpy.app.timers.unregister(table_panel_timer)
        table_panel_timer = None
    
#Set up scene properties
def setup_properties():
    bpy.types.Scene.name = bpy.props.StringProperty(name="Name")
    bpy.types.Scene.height = bpy.props.FloatProperty(name="Height")
    bpy.types.Scene.weight = bpy.props.FloatProperty(name="Weight")
    bpy.types.Scene.eye_color = bpy.props.StringProperty(name="Eye Color")
    bpy.types.Scene.retrieved_id = bpy.props.IntProperty(name="ID")
    bpy.types.Scene.retrieved_name = bpy.props.StringProperty(name="Name")
    bpy.types.Scene.retrieved_height = bpy.props.FloatProperty(name="Height")
    bpy.types.Scene.retrieved_weight = bpy.props.FloatProperty(name="Weight")
    bpy.types.Scene.retrieved_eye_color = bpy.props.StringProperty(name="Eye Color")
    bpy.types.Scene.update_id = bpy.props.IntProperty(name="ID")
    bpy.types.Scene.update_name = bpy.props.StringProperty(name="Name")
    bpy.types.Scene.update_height = bpy.props.FloatProperty(name="Height")
    bpy.types.Scene.update_weight = bpy.props.FloatProperty(name="Weight")
    bpy.types.Scene.update_eye_color = bpy.props.StringProperty(name="Eye Color")
    bpy.types.Scene.delete_id = bpy.props.IntProperty(name="ID")
    
#Connect to database
def connect():
    conn = psycopg2.connect(**conn_params)
    return conn

#Create character
def create_character(name, height, weight, eye_color):
    conn = connect()
    cur = conn.cursor()
    cur.execute(f"INSERT INTO {table_name} ({name_column}, {height_column}, {weight_column}, {eye_color_column}) VALUES (%s, %s, %s, %s)", (name, height, weight, eye_color))
    conn.commit()
    cur.close()
    conn.close()

#Read character
def read_character(id):
    conn = connect()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {table_name} WHERE {id_column} = %s", (id,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result

#Update character
def update_character(id, name=None, height=None, weight=None, eye_color=None):
    conn = connect()
    cur = conn.cursor()

    set_clauses = []
    values = []
    if name is not None:
        set_clauses.append(f"{name_column} = %s")
        values.append(name)
    if height is not None:
        set_clauses.append(f"{height_column} = %s")
        values.append(height)
    if weight is not None:
        set_clauses.append(f"{weight_column} = %s")
        values.append(weight)
    if eye_color is not None:
        set_clauses.append(f"{eye_color_column} = %s")
        values.append(eye_color)

    update_clause = ", ".join(set_clauses)
    values.append(id)

    cur.execute(f"UPDATE {table_name} SET {update_clause} WHERE {id_column} = %s", tuple(values))      
    conn.commit()
    cur.close()
    conn.close()


#Delete character
def delete_character(id):
    conn = connect()
    cur = conn.cursor()
    cur.execute(f"DELETE FROM {table_name} WHERE {id_column} = %s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    

#Set up properties and register UI panel and operators
setup_properties()
register()
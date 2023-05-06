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


# Connect to database
def connect():
    conn = psycopg2.connect(**conn_params)
    return conn

# Create tables
conn = connect()
cur = conn.cursor()
cur.execute("""
    CREATE TABLE IF NOT EXISTS Object (
        id SERIAL PRIMARY KEY,
        name TEXT UNIQUE,
        vertex_count INT
    )
""")
cur.execute("""
    CREATE TABLE IF NOT EXISTS Location (
        id SERIAL PRIMARY KEY,
        object_id INT REFERENCES Object(id),
        x REAL,
        y REAL,
        z REAL
    )
""")
cur.execute("""
    CREATE TABLE IF NOT EXISTS Dimension (
        id SERIAL PRIMARY KEY,
        object_id INT REFERENCES Object(id),
        width REAL,
        height REAL,
        depth REAL
    )
""")

# Define handler function to update object and its data from database when updated in Blender
def update_database(scene):
    for obj in bpy.context.scene.objects:
        if obj.type != 'MESH':
            continue

        name = obj.name
        vertex_count = len(obj.data.vertices)

        # Insert or update object data in Object table
        cur.execute("""
            INSERT INTO Object (name, vertex_count)
            VALUES (%s, %s)
            ON CONFLICT (name) DO UPDATE
            SET vertex_count = %s
            RETURNING id
        """, (name, vertex_count, vertex_count))
        object_id = cur.fetchone()[0]

        # Get current location and dimensions data from database
        cur.execute("SELECT x, y, z FROM Location WHERE object_id = %s", (object_id,))
        loc_row = cur.fetchone()
        cur.execute("SELECT width, height, depth FROM Dimension WHERE object_id = %s", (object_id,))
        dim_row = cur.fetchone()

        # Insert location data into Location table
        loc = obj.location
        cur.execute("""
            INSERT INTO Location (object_id, x, y, z)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (object_id) DO UPDATE SET x = EXCLUDED.x, y = EXCLUDED.y, z = EXCLUDED.z
        """, (object_id, loc.x, loc.y, loc.z))

        # Insert dimension data into Dimension table
        dim = obj.dimensions
        cur.execute("""
            INSERT INTO Dimension (object_id, width, height, depth)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (object_id) DO UPDATE SET width = EXCLUDED.width, height = EXCLUDED.height, depth = EXCLUDED.depth
        """, (object_id, dim.x, dim.y, dim.z))
        
    conn.commit()

# Register the handler function
bpy.app.handlers.depsgraph_update_post.append(update_database)

# Define handler function to delete object and its data from database when deleted in Blender viewport
def object_delete_handler(scene):
    cur.execute("SELECT id, name FROM Object")
    rows = cur.fetchall()
    for row in rows:
        obj_id = row[0]
        obj_name = row[1]
        if bpy.data.objects.get(obj_name) is None:
            cur.execute("DELETE FROM Location WHERE object_id = %s", (obj_id,))
            cur.execute("DELETE FROM Dimension WHERE object_id = %s", (obj_id,))
            cur.execute("DELETE FROM Object WHERE id = %s", (obj_id,))
    
    conn.commit()

# Register object_delete_handler to run on object delete in Blender viewport
bpy.app.handlers.depsgraph_update_post.append(object_delete_handler)


# Define UI panel

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
        cur.execute("""
            SELECT Object.id, Object.name, Object.vertex_count, Location.x, Location.y, Location.z,
            Dimension.width, Dimension.height, Dimension.depth
            FROM Object
            LEFT JOIN Location ON Object.id = Location.object_id
            LEFT JOIN Dimension ON Object.id = Dimension.object_id
        """)
        rows = cur.fetchall()
        
        if not rows:
            return

        # Create a list of column widths based on the maximum width of each field
        col_widths = [max(len(str(row[i])) for row in rows) for i in range(len(rows[0]))]

        # Add the header row with the column names
        header_row = layout.row()
        header_row.label(text="id")
        header_row.label(text="name")
        header_row.label(text="vertexCount")
        header_row.label(text="loc_x")
        header_row.label(text="loc_y")
        header_row.label(text="loc_z")
        header_row.label(text="width")
        header_row.label(text="height")
        header_row.label(text="depth")

        # Add a separator row between the header row and the data rows
        sep_row = layout.row()
        sep_row.separator()

        # Add the data rows with the field values aligned vertically
        for row in rows:
            data_row = layout.row()
            for i in range(len(row)):
                data_row.label(text=str(row[i]).ljust(col_widths[i]))

#        # Add the reload button
#        layout.separator()
#        layout.operator("object.reload_table",
#                        text="Reload", icon="FILE_REFRESH")

#        if table_panel_timer is None:
#            table_panel_timer = bpy.app.timers.register(self.timer_callback)

#    def timer_callback(self):
#        # Call the internal operator to reload the table data
#        bpy.ops.object.reload_table_internal()
#        return 0.1


#class ReloadTableOperator(bpy.types.Operator):
#    bl_idname = "object.reload_table"
#    bl_label = "Reload Table"

#    def execute(self, context):
#        bpy.ops.object.reload_table_internal()
#        return {'FINISHED'}


#class ReloadTableInternalOperator(bpy.types.Operator):
#    bl_idname = "object.reload_table_internal"
#    bl_label = "Reload Table Internal"

#    def execute(self, context):
#        return {'FINISHED'}

# Register UI panel and operators


def register():
    bpy.utils.register_class(MyAddonPanel)
#    bpy.utils.register_class(ReloadTableOperator)
#    bpy.utils.register_class(ReloadTableInternalOperator)


# Unregister UI panel and operators
def unregister():
    bpy.utils.unregister_class(MyAddonPanel)
#    bpy.utils.unregister_class(ReloadTableOperator)
#    bpy.utils.unregister_class(ReloadTableInternalOperator)

#    global table_panel_timer
#    if table_panel_timer is not None:
#        bpy.app.timers.unregister(table_panel_timer)
#        table_panel_timer = None



# Set up properties and register UI panel and operators
register()

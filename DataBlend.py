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

# Iterate through objects
for obj in bpy.context.scene.objects:
    if obj.type != 'MESH':
        continue

    name = obj.name
    vertex_count = len(obj.data.vertices)

    # Insert object data into Object table
    cur.execute("""
        INSERT INTO Object (name, vertex_count)
        VALUES (%s, %s)
        ON CONFLICT (name) DO NOTHING
    """, (name, vertex_count))

    # Get object ID
    cur.execute("SELECT id FROM Object WHERE name = %s", (name,))
    object_id = cur.fetchone()[0]

    # Insert location data into Location table
    loc = obj.location
    cur.execute("""
        INSERT INTO Location (object_id, x, y, z)
        VALUES (%s, %s, %s, %s)
    """, (object_id, loc.x, loc.y, loc.z))

    # Insert dimension data into Dimension table
    dim = obj.dimensions
    cur.execute("""
        INSERT INTO Dimension (object_id, width, height, depth)
        VALUES (%s, %s, %s, %s)
    """, (object_id, dim.x, dim.y, dim.z))

# Commit changes to database
conn.commit()

# Close database connection
cur.close()
conn.close()


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
            SELECT
                o.id,
                o.name,
                o.vertex_count,
                l.x,
                l.y,
                l.z,
                d.width,
                d.height,
                d.depth
            FROM
                object o
                JOIN location l ON o.id = l.object_id
                JOIN dimension d ON o.id = d.object_id
        """)
        rows = cur.fetchall()

        # Create a list of column widths based on the maximum width of each field
        col_widths = [max(len(str(row[i])) for row in rows)
                      for i in range(len(rows[0]))]

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

        # Add the reload button
        layout.separator()
        layout.operator("object.reload_table",
                        text="Reload", icon="FILE_REFRESH")

        if table_panel_timer is None:
            table_panel_timer = bpy.app.timers.register(self.timer_callback)

    def timer_callback(self):
        # Call the internal operator to reload the table data
        bpy.ops.object.reload_table_internal()
        return 0.1


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
    bpy.utils.register_class(MyAddonPanel)
    bpy.utils.register_class(ReloadTableOperator)
    bpy.utils.register_class(ReloadTableInternalOperator)


# Unregister UI panel and operators
def unregister():
    bpy.utils.unregister_class(MyAddonPanel)
    bpy.utils.unregister_class(ReloadTableOperator)
    bpy.utils.unregister_class(ReloadTableInternalOperator)

    global table_panel_timer
    if table_panel_timer is not None:
        bpy.app.timers.unregister(table_panel_timer)
        table_panel_timer = None



# Set up properties and register UI panel and operators
register()

from django.db import migrations


def forwards(apps, schema_editor):
    """Rename DB column ilgi_alanlari -> ilgi_alanlarim if it exists."""
    table = 'members_user'
    old = 'ilgi_alanlari'
    new = 'ilgi_alanlarim'
    conn = schema_editor.connection
    with conn.cursor() as cursor:
        vendor = conn.vendor
        if vendor == 'sqlite':
            cursor.execute("PRAGMA table_info('%s')" % table)
            cols = [row[1] for row in cursor.fetchall()]
            if old in cols and new not in cols:
                cursor.execute(f"ALTER TABLE {table} RENAME COLUMN {old} TO {new};")
        elif vendor in ('postgresql', 'postgres'):
            cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name=%s", [table])
            cols = [r[0] for r in cursor.fetchall()]
            if old in cols and new not in cols:
                cursor.execute(f'ALTER TABLE "{table}" RENAME COLUMN "{old}" TO "{new}";')
        else:
            # MySQL fallback
            try:
                cursor.execute(f"SHOW COLUMNS FROM {table}")
                cols = [row[0] for row in cursor.fetchall()]
                if old in cols and new not in cols:
                    cursor.execute(f"ALTER TABLE {table} CHANGE {old} {new} TEXT;")
            except Exception:
                # If this fails, skip — database might already match model state
                pass


def backwards(apps, schema_editor):
    """Reverse rename if needed (ilgi_alanlarim -> ilgi_alanlari)."""
    table = 'members_user'
    old = 'ilgi_alanlarim'
    new = 'ilgi_alanlari'
    conn = schema_editor.connection
    with conn.cursor() as cursor:
        vendor = conn.vendor
        if vendor == 'sqlite':
            cursor.execute("PRAGMA table_info('%s')" % table)
            cols = [row[1] for row in cursor.fetchall()]
            if old in cols and new not in cols:
                cursor.execute(f"ALTER TABLE {table} RENAME COLUMN {old} TO {new};")
        elif vendor in ('postgresql', 'postgres'):
            cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name=%s", [table])
            cols = [r[0] for r in cursor.fetchall()]
            if old in cols and new not in cols:
                cursor.execute(f'ALTER TABLE "{table}" RENAME COLUMN "{old}" TO "{new}";')
        else:
            try:
                cursor.execute(f"SHOW COLUMNS FROM {table}")
                cols = [row[0] for row in cursor.fetchall()]
                if old in cols and new not in cols:
                    cursor.execute(f"ALTER TABLE {table} CHANGE {old} {new} TEXT;")
            except Exception:
                pass


class Migration(migrations.Migration):

    dependencies = [
        ('members', '0004_alter_user_finansal_kod_numarasi'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]

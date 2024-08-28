from flask import Flask, render_template, request, redirect, send_file, url_for, flash, session, make_response
from flask_mysqldb import MySQL, MySQLdb
from datetime import datetime
from flask import jsonify
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
# opcionales
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Table, TableStyle
# titulo
from reportlab.platypus import SimpleDocTemplate, PageBreak, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import os
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
import requests
from requests import Session
import json
from flask import Flask, jsonify
from flask_apscheduler import APScheduler
from apscheduler.schedulers.background import BackgroundScheduler


app = Flask(__name__, template_folder="template")

# Mysql Connection
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'agavecare'
mysql = MySQL(app)

# settings
app.secret_key = 'mysecretkey'

@app.context_processor
def inject_now():
    return {'now': datetime.now()}

@app.route('/api/trabajadores')
def api_trabajadores():
    trabajadores = obtener_trabajadores()
    return jsonify(trabajadores)

def is_admin():
    return 'idAdmin' in session

def is_user():
    return 'campoAsignado' in session

@app.route('/home')
def homePage():
    if 'nombre' in session:
        session.clear()
    return render_template('home.html')

@app.route('/acerca')
def acerca():
    return render_template('acerca.html')


# (MARCO) START: Sirve para obtener datos de diferentes tablas

def obtener_trabajadores():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM trabajadores")
    trabajadores = cur.fetchall()
    cur.close()
    return trabajadores

def obtener_campos():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM campos")
    campos = cur.fetchall()
    cur.close()
    return campos

def obtener_surcos():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM surcos")
    surcos = cur.fetchall()
    cur.close()
    return surcos

def obtener_vehiculos():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM vehiculos")
    vehiculos = cur.fetchall()
    cur.close()
    return vehiculos
def obtener_herramientas():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM herramientas")
    herramientas = cur.fetchall()
    cur.close()
    return herramientas

# END: Obtener datos de todas las tablas

# PDF#####################

@app.route('/generate_pdf')
def generate_pdf():
    trabajadores = obtener_trabajadores()
    campos = obtener_campos()

    pdf_filename = "reporte.pdf"
    pdf_path = f"C:\\agaveNewVerde\\static\\reportes\\{pdf_filename}"

    directory = os.path.dirname(pdf_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    pdf = canvas.Canvas(pdf_path, pagesize=letter)
    pdf.setTitle("Reporte de Trabajadores y Campos")

    # Estilos
    basic_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkolivegreen),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 16),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 15),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1.5, colors.black),
        ('INNERGRID', (0, 1), (-1, -1), 0.75, colors.black),
        ('BOX', (0, 0), (-1, -1), 2.5, colors.olivedrab),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROUND', (0, 0), (-1, -1), 10)   # Bordas redondeadas
    ])

    # Titulo de Trabajadores
    pdf.setFont("Helvetica-Bold", 28)
    pdf.drawCentredString(300, 750, "Reporte de Trabajadores")

    # Tabla de Trabajadores
    data = [['Télefono', 'Nombre', 'Campo Asignado', 'Sueldo']]
    for trabajador in trabajadores:
        data.append([trabajador[0], trabajador[1], trabajador[3], trabajador[6]])

    table = Table(data, colWidths=[1.75*inch, 2.25*inch, 2.25*inch, 1.75*inch])
    table.setStyle(basic_style)
    w, h = table.wrapOn(pdf, 0, 0)
    table.drawOn(pdf, (letter[0]-w)/2, 580-h)

    # Titulo de Campos
    pdf.setFont("Helvetica-Bold", 28)
    pdf.drawCentredString(300, 420, "Reporte de Campos")

    # Tabla de Campos
    data2 = [['Campo', 'Capacidad de agaves', 'Agaves plantados', 'Surcos']]
    for campo in campos:
        data2.append([campo[0], campo[1], campo[4], campo[3]])

    table2 = Table(data2, colWidths=[1.75*inch, 2.25*inch, 2.25*inch, 1.75*inch])
    table2.setStyle(basic_style)
    w2, h2 = table2.wrapOn(pdf, 0, 0)
    table2.drawOn(pdf, (letter[0]-w2)/2, 250-h2)

    pdf.save()
    return send_file(pdf_path, as_attachment=True)



#############################

# (MARCO) se puede eliminar
@app.route('/datos')
def datos():
    campos = obtener_campos()
    # surcos = obtener_surcos()
    # trabajadores = obtener_trabajadores()
    
    return render_template('datos.html', campos=campos)

@app.route('/informes/')
def informes():
    trabajadores = obtener_trabajadores()
    #print(trabajadores)  # Añade esta línea
    return render_template('informes.html', trabajadores=trabajadores)

@app.route('/contactanos')
def contactanos():
    return render_template('contactanos.html')

@app.route('/index')
def index():
    if not is_admin():
        flash('No tienes permiso para acceder a esta página.')
        return redirect(url_for('homePage'))
    trabajadores = obtener_trabajadores()
    campos = obtener_campos()
    vehiculos = obtener_vehiculos()
    herramientas = obtener_herramientas()
    surcos = obtener_surcos()
    return render_template('index.html', trabajadores=trabajadores, campos=campos, vehiculos=vehiculos, herramientas=herramientas, surcos=surcos)

#### prueba campos y surcos

def insertCampos(idCampo, maxAgaves, cantSurcos, cursor):
    try:
        cursor.execute('INSERT INTO campos (idCampo, maxAgaves, cantSurcos) VALUES (%s, %s, %s)', (idCampo, maxAgaves, cantSurcos))
        return True
    except:
        return False

def insertSurcos(idCampo, cantSurcos, cursor):
    try:
        for surco in range(1, int(cantSurcos) + 1):
            cursor.execute('INSERT INTO surcos (idCampo, noSurco) VALUES (%s, %s)', (idCampo, surco))
        return True
    except:
        return False

####

@app.route('/editcampo/<string:idCampo>')
def edit_campo(idCampo):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM campos WHERE idCampo = {campo_id}'.format(campo_id=idCampo))
    campo = cur.fetchone()
    cur.close()
    return render_template('edit_campo.html', campo=campo)


@app.route('/update_field/<string:id>', methods=['POST'])
def update_field(id):
    if request.method == 'POST':
        maxAgaves = request.form['maxAgaves']
        agavesPlantados = request.form['agavesPlantados']
        cantSurcos = request.form['cantSurcos']

        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE campos
            SET maxAgaves = %s,
                agavesPlantados = %s,
                cantSurcos = %s
            WHERE idCampo = %s
        """, (maxAgaves, agavesPlantados, cantSurcos, id))
        cur.connection.commit()
        flash('Campo actualizado correctamente!')
        return redirect(url_for('index'))

# (MARCO) Funcion que se ejecuta automaticamente para eliminar los surcos del campo
def deleteSurcos(idCampo):
    try:
        cur = mysql.connection.cursor()
        cur.execute('DELETE FROM surcos WHERE idCampo = {idcampo}'.format(idcampo = idCampo))
        mysql.connection.commit()
        print("True surcos")
        return True
    except:
        print("False surcos")
        return False
    finally:
        cur.close()

# (MARCO) Funcion que se ejecuta al eliminar un campo en index
@app.route('/deletecampo/<string:idCampo>')
def deletecampo(idCampo):
    try:
        if deleteSurcos(idCampo):
            cur = mysql.connection.cursor()
            #cur.execute('DELETE FROM trabajadores WHERE telefono = {0}'.format(id)
            cur.execute('DELETE FROM campos WHERE idCampo = {idcampo}'.format(idcampo = idCampo))
            mysql.connection.commit()
            flash('Campo eliminados correctamente!')
            return redirect(url_for('index'))
        else:
            flash('Algo salió mal. Intentalo nuevamente. (surcos)')
            return redirect(url_for('index'))
    except:
        flash('Algo salió mal. Intentalo nuevamente.')
        return redirect(url_for('index'))
    finally:
        cur.close()

#####

def guardar_campo_en_db(idCampo, maxAgaves, cantSurcos):
    cur = mysql.connection.cursor()
    try:
        cur.execute("INSERT INTO campos (idCampo, maxAgaves, cantSurcos) VALUES (%s, %s, %s)", (idCampo, maxAgaves, cantSurcos))
        mysql.connection.commit()
    except Exception as e:
        print(f"Error: {e}")
        mysql.connection.rollback()  # rollback in case there is any error
    finally:
        cur.close()

        
# (DANI) Obtener para la grafica
@app.route('/api/campos')
def get_campos_data():
    cur = mysql.connection.cursor()
    cur.execute('SELECT idCampo, agavesPlantados, maxAgaves FROM campos')
    rows = cur.fetchall()
    cur.close()

    campos_data = [{"idCampo": row[0], "agavesPlantados": row[1], "maxAgaves": row[2]} for row in rows]

    return jsonify(campos_data)

# Vehiculos
@app.route('/vehicle_registration')
def vehicle_registration():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM campos")
    lista_campos = cur.fetchall()
    cur.close()
    # Asegúrate de que los datos estén en un formato que pueda ser convertido a JSON
    campos_dict = [dict(campo) for campo in lista_campos]
    return jsonify({'campos': campos_dict})

# (DANI) Obtener datos de campos para el select del formulario de vehículos
@app.route('/api/campos-select')
def get_campos_select_data():
    cur = mysql.connection.cursor()
    cur.execute('SELECT idCampo FROM campos')
    rows = cur.fetchall()
    cur.close()

    # Si solo necesitas el idCampo
    campos_select_data = [{"idCampo": row[0]} for row in rows]

    return jsonify(campos_select_data)

@app.route('/add_vehicle', methods=['POST'])
def add_vehicle():
    if request.method == 'POST':
        placa = request.form['placa']
        marca = request.form['marca']
        enCampo = request.form['enCampo']
        detalles = request.form['detalles']
        litrosLlenados = request.form['litrosLlenados']
        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO vehiculos (placa, marca, enCampo, detalles, litrosLlenados) VALUES (%s, %s, %s, %s, %s)", 
                        (placa, marca, enCampo, detalles, litrosLlenados))
            mysql.connection.commit()
            flash('Vehículo agregado correctamente!', 'success')
        except Exception as e:
            mysql.connection.rollback()
            flash('Hubo un error al agregar el vehículo. {}'.format(e), 'danger')
        finally:
            cur.close()
        return redirect(url_for('index'))

@app.route('/deletevehicle/<string:placa>')
def delete_vehicle(placa):
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM vehiculos WHERE placa = %s", [placa])
        mysql.connection.commit()
        flash('Vehículo eliminado correctamente!', 'success')
    except Exception as e:
        mysql.connection.rollback()
        flash('Hubo un error al eliminar el vehículo. {}'.format(e), 'danger')
    finally:
        cur.close()
    return redirect(url_for('index'))

@app.route('/editvehicle/<placa>', methods=['GET'])
def editvehicle(placa):
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM vehiculos WHERE placa = %s", [placa])
    if result > 0:
        vehiculo = cur.fetchone()
        cur.close()
        return render_template('editvehicle.html', vehiculo=vehiculo)
    else:
        cur.close()
        return 'Vehículo no encontrado', 404


@app.route('/update_vehiculo/<string:placa>', methods=['POST'])
def update_vehiculo(placa):
    if request.method == 'POST':
        # Recoge los datos del formulario
        marca = request.form['marca']
        enCampo = request.form['enCampo']
        detalles = request.form['detalles']
        litrosLlenados = request.form['litrosLlenados']

        # Ejecuta la consulta de actualización
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE vehiculos
            SET marca = %s, enCampo = %s, detalles = %s, litrosLlenados = %s
            WHERE placa = %s
        """, (marca, enCampo, detalles, litrosLlenados, placa))
        mysql.connection.commit()
        flash('Vehículo actualizado correctamente!')
        return redirect(url_for('index'))


#(DANI) Herramientas
@app.route('/add_tool', methods=['POST'])
def add_tool():
    if request.method == 'POST':
        nombreHerramienta = request.form['nombreHerramienta']
        existencias = request.form['existencias']
        comentarios = request.form.get('comentarios', 'SIN COMENTARIOS')  # Si no hay comentarios, usar valor por defecto
        try:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO herramientas (nombreHerramienta, existencias, comentarios) VALUES (%s, %s, %s)", 
                        (nombreHerramienta, existencias, comentarios))
            mysql.connection.commit()
            flash('Herramienta agregada correctamente!', 'success')
        except Exception as e:
            mysql.connection.rollback()
            flash('Hubo un error al agregar la herramienta. {}'.format(e), 'danger')
        finally:
            cur.close()
        return redirect(url_for('index'))  # Asegúrate de que 'index' sea la vista que muestra la lista de herramientas

@app.route('/delete_tool/<int:idHerramienta>')
def delete_tool(idHerramienta):
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM herramientas WHERE idHerramienta = %s", [idHerramienta])
        mysql.connection.commit()
        flash('Herramienta eliminada correctamente!', 'success')
    except Exception as e:
        mysql.connection.rollback()
        flash('Hubo un error al eliminar la herramienta. {}'.format(e), 'danger')
    finally:
        cur.close()
    return redirect(url_for('index'))  # Asegúrate de que 'index' sea la vista que muestra la lista de herramientas

@app.route('/edit_tool/<int:idHerramienta>', methods=['GET'])
def edit_tool(idHerramienta):
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM herramientas WHERE idHerramienta = %s", [idHerramienta])
    if result > 0:
        herramienta = cur.fetchone()
        cur.close()
        return render_template('editar_herramienta.html', herramienta=herramienta)
    else:
        cur.close()
        flash('Herramienta no encontrada', 'warning')
        return redirect(url_for('index'))  # Redirige a la lista de herramientas si no se encuentra



@app.route('/update_tool/<int:idHerramienta>', methods=['POST'])
def update_tool(idHerramienta):
    if request.method == 'POST':
        # Recoge los datos del formulario
        nombreHerramienta = request.form['nombreHerramienta']
        existencias = request.form['existencias']
        comentarios = request.form['comentarios']

        # Ejecuta la consulta de actualización
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE herramientas
            SET nombreHerramienta = %s, existencias = %s, comentarios = %s
            WHERE idHerramienta = %s
        """, (nombreHerramienta, existencias, comentarios, idHerramienta))
        mysql.connection.commit()
        flash('Herramienta actualizada correctamente!', 'success')
        return redirect(url_for('index'))  # Redirige a la lista de herramientas tras la actualización

# (DANI) Surcos
@app.route('/add_surco', methods=['POST'])
def add_surco():
    if request.method == 'POST':
        noSurco = request.form['noSurco']
        capMax = request.form['capMax']
        idCampo = request.form['idCampo']
        
        # Asumiendo que ya tienes una conexión a la base de datos llamada mysql
        cur = mysql.connection.cursor()
        try:
            cur.execute(
                "INSERT INTO surcos (noSurco, capMax, idCampo) VALUES (%s, %s, %s)",
                (noSurco, capMax, idCampo)
            )
            mysql.connection.commit()
            flash('Surco registrado con éxito.', 'success')
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error al registrar el surco: {e}', 'danger')
        finally:
            cur.close()
        
        return redirect(url_for('index'))

@app.route('/delete_surco/<int:noSurco>', methods=['GET'])
def delete_surco(noSurco):
    cur = mysql.connection.cursor()
    try:
        cur.execute("DELETE FROM surcos WHERE noSurco = %s", [noSurco])
        mysql.connection.commit()
        flash('Surco eliminado con éxito.', 'success')
    except Exception as e:
        mysql.connection.rollback()
        flash(f'Error al eliminar el surco: {e}', 'danger')
    finally:
        cur.close()
    
    return redirect(url_for('index'))

@app.route('/update_surco/<int:noSurco>', methods=['POST'])
def update_surco(noSurco):
    if request.method == 'POST':
        capMax = request.form['capMax']
        agavesPlantados = request.form['agavesPlantados']
        
        cur = mysql.connection.cursor()
        try:
            cur.execute("""
                UPDATE surcos
                SET capMax = %s, agavesPlantados = %s
                WHERE noSurco = %s
            """, (capMax, agavesPlantados, noSurco))
            mysql.connection.commit()
            flash('Información del surco actualizada correctamente.', 'success')
        except Exception as e:
            mysql.connection.rollback()
            flash(f'Error al actualizar el surco: {e}', 'danger')
        finally:
            cur.close()
        
        return redirect(url_for('index'))  # Cambiado a 'mostrar_surcos'



@app.route('/edit_surco/<int:noSurco>')
def edit_surco(noSurco):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM surcos WHERE noSurco = %s", [noSurco])
    surco = cur.fetchone()
    cur.close()
    
    if surco:
        return render_template('editar_surco.html', surco=surco)
    else:
        flash('Surco no encontrado.', 'danger')
        return redirect(url_for('index'))  # Asegúrate de que 'index' sea la vista correcta para redirigir al usuario


# @app.route('/index/campos')
# def indexCampos():
#     if not is_admin():
#         flash('No tienes permiso para acceder a esta página.')
#         return redirect(url_for('homePage'))
#     cur = mysql.connection.cursor()
#     cur.execute('SELECT * FROM campos')
#     data = cur.fetchall()
#     return render_template('index.html', campos=data)


# MARCO: FUNCION MODIFICADA PARA CREAR CAMPOS Y TAMBIEN LOS SURCOS QUE TIENE DICHO CAMPO
@app.route('/add_field', methods=['POST'])
def add_field():
    if request.method == 'POST':
        try:
            idCampo = request.form['idCampo']
            maxAgaves = request.form['maxAgaves']
            cantSurcos = request.form['cantSurcos']
            
            cur = mysql.connection.cursor()
            
            if insertCampos(idCampo, maxAgaves, cantSurcos, cur) and insertSurcos(idCampo, cantSurcos, cur):
                mysql.connection.commit()
                flash('Campo añadido exitosamente!')
                return redirect(url_for('index'))
            else:
                flash('Algo salió mal. Inténtalo nuevamente.')
                return redirect(url_for('index'))
        except:
            flash('Algo salió mal. Intentalo nuevamente.')
            return redirect(url_for('index'))
        finally:
            cur.close()

@app.route('/add_contact', methods=['POST'])
def add_contact():
    if request.method == 'POST':
        try:
            telefono = request.form['telefono']
            nombre = request.form['nombre']
            contrasena = request.form['contrasena']
            campoAsignado = request.form['campoAsignado']
            cur = mysql.connection.cursor()
            cur.execute('INSERT INTO trabajadores (telefono, nombre, contrasena, campoAsignado) VALUES (%s, %s, %s, %s)', (telefono, nombre, contrasena, int(campoAsignado)))
            mysql.connection.commit()
            flash('Contacto añadido exitosamente!')
            return redirect(url_for('index'))
        except:
            flash('Algo salió mal. Intentalo nuevamente.')
            return redirect(url_for('index'))
        finally:
            cur.close()
            
    
@app.route('/edit/<telefono>')
def get_contact(telefono):
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM trabajadores WHERE telefono= {tel}'.format(tel = telefono))
    data = cur.fetchall()
    return render_template('edit-contact.html', trabajador = data[0])

@app.route('/update/<string:telefono>', methods = ['POST'])
def update_contact(telefono):
    if request.method == 'POST':
        nombre = request.form['nombre']
        contrasena = request.form['contrasena']
        campoAsignado = request.form['campoAsignado']
        horasTrabajadas = int(request.form['horasTrabajadas'])
        horasExtras = int(request.form['horasExtras'])
        sueldo = horasTrabajadas * 100 + horasExtras * 180

        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE trabajadores
            SET nombre = %s,
                contrasena = %s,
                campoAsignado = %s,
                horasTrabajadas = %s,
                horasExtras = %s,
                sueldo = %s
            WHERE telefono = %s           
        """, (nombre, contrasena, int(campoAsignado), horasTrabajadas, horasExtras, sueldo, telefono))
        cur.connection.commit()
        flash('Trabajador actualizado correctamente!')
        return redirect(url_for('index'))


@app.route('/delete/<string:telefono>')
def delete_contact(telefono):
    cur = mysql.connection.cursor()
    #cur.execute('DELETE FROM trabajadores WHERE telefono = {0}'.format(id)
    cur.execute('DELETE FROM trabajadores WHERE telefono = {tel}'.format(tel = telefono))
    mysql.connection.commit()
    flash('Trabajador eliminado correctamente!')
    return redirect(url_for('index'))

# Registro y Login para ADMINISTRADOR

'''@app.route('/login_pagAdmin')
def login_pagAdmin():
    return render_template('login-admin.html', now=datetime.now())

@app.route('/login_admin', methods=['POST'])
def login_admin():
    try:
        if request.method == 'POST':
            name = request.form['nombre']
            tel = request.form['telefono']
            password = request.form['contrasena']

            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute('SELECT * FROM admin WHERE telefono=%s', (tel,))
            user = cur.fetchone()
            #if user['idAdmin']:
            
            #login_user(user, remember=True)
            if len(user) > 0:
                if password == user['contrasena'] and name == user['nombre']:
                    session['nombre'] = user['nombre']
                    session['telefono'] = user['telefono'] # REDIRECT ES CON NOMBRE DE FUNCION
                    session['idAdmin'] = user['idAdmin'] # REDIRECT ES CON NOMBRE DE FUNCION
                    
                    return redirect(url_for('index')) # Se direcciona a la pagina indexUser y se pasan los datos de usuario
                else:
                    flash('Contraseña o nombre no coinciden.')
                    return redirect(url_for('login_pagAdmin'))
                    #return 'Error. El telefono o la contraseña no coinciden'
            else:
                flash('Error. Administrador no encontrado.')
                return redirect(url_for('login_pagAdmin'))
                #return 'Error. Usuario no encontrado'
        else:
            flash('Algo salió mal. Intentalo nuevamente.')
            return redirect(url_for('login_pagAdmin'))
            #return render_template('login-user.html')
    except:
        flash('Algo salió mal. Intentalo nuevamente.')
        return redirect(url_for('login_pagAdmin'))   '''

# TODA LA PROGRAMACION PARA LA VISTA DEL USUARIO ESTA ACA ABAJO

# (MARCO) para ir a la pagina login user
'''@app.route('/login_pag')
def login_pag():
    return render_template('login-user.html')

@app.route('/login_user', methods=['POST'])
def login_user():
    try:
        if request.method == 'POST':
            tel = request.form['telefono']
            password = request.form['contrasena']

            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute('SELECT * FROM trabajadores WHERE telefono=%s', (tel,))
            user = cur.fetchone()
            #if user['idAdmin']:
            
            #login_user(user, remember=True)
            if len(user) > 0:
                if password == user['contrasena']:
                    session['nombre'] = user['nombre']
                    session['campoAsignado'] = user['campoAsignado']
                    session['horasTrabajadas'] = user['horasTrabajadas']
                    session['horasExtras'] = user['horasExtras']
                    session['sueldo'] = user['sueldo']
                    return redirect(url_for('indexUser')) # Se direcciona a la pagina indexUser y se pasan los datos de usuario
                else:
                    flash('Teléfono o contraseña no coinciden.')
                    return redirect(url_for('login_pag'))
                    #return 'Error. El telefono o la contraseña no coinciden'
            else:
                flash('Error. Usuario no encontrado.')
                return redirect(url_for('login_pag'))
                #return 'Error. Usuario no encontrado'
        else:
            flash('Algo salió mal. Intentalo nuevamente.')
            return redirect(url_for('login_pag'))
            #return render_template('login-user.html')
    except:
        flash('Algo salió mal. Intentalo nuevamente.')
        return redirect(url_for('login_pag'))'''

@app.route('/login_pag')
def login_pag():
    return render_template('login-user.html')

@app.route('/login_user', methods=['POST'])
def login():
    if request.method == 'POST':
        tel = request.form['telefono']
        password = request.form['contrasena']

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Primero intenta encontrar al usuario en la tabla 'admin'
        cur.execute('SELECT * FROM admin WHERE telefono = %s AND contrasena = %s', (tel, password))
        user = cur.fetchone()

        if user:
            # Usuario encontrado en la tabla 'admin'
            session['nombre'] = user['nombre']
            session['telefono'] = user['telefono']
            session['idAdmin'] = user['idAdmin']
            return redirect(url_for('index'))  # Redirige a la página principal del Admin

        # Si no es admin, busca en la tabla 'trabajadores'
        cur.execute('SELECT * FROM trabajadores WHERE telefono = %s AND contrasena = %s', (tel, password))
        user = cur.fetchone()

        if user:
            # Usuario encontrado en la tabla 'trabajadores'
            session['nombre'] = user['nombre']
            session['campoAsignado'] = user['campoAsignado']
            session['horasTrabajadas'] = user['horasTrabajadas']
            session['horasExtras'] = user['horasExtras']
            session['sueldo'] = user['sueldo']
            return redirect(url_for('indexUser'))  # Redirige a la página principal del Trabajador

        # Si no se encuentra el usuario en ninguna tabla
        flash('Teléfono o contraseña no coinciden.')
        return redirect(url_for('login_pag'))

    # Si la solicitud no es POST, simplemente muestra la página de inicio de sesión
    return render_template('login-user.html')
                
@app.route('/indexUser')
def indexUser():
    if not is_user():
        flash('No tienes permiso para acceder a esta página.')
        return redirect(url_for('homePage'))
    return render_template('indexUser.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('homePage'))

@app.route('/clima')
def clima():
    return render_template('clima.html')

@app.route('/agave_precio')
def agave_precio():
    return render_template('agave_precio.html')

# API Key para OpenWeatherMap (obtén una clave API en https://openweathermap.org/api)

#latitud1 = '20.6667'
#longitud1 = '-103.3333'
#api_key = '97b20a75a1d9cc16f1328d9e2c176698'

# Función para programar tareas
def schedule_tasks1():
    scheduler.add_job(func=almacenar_datos_climaticos, trigger='interval', seconds=60, id='job_datos_climaticos')

def obtener_datos_climaticos_clima(api_key, latitud, longitud):
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={latitud}&lon={longitud}&appid={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = json.loads(response.content.decode('utf-8'))
        print(data)  # Imprime para depurar
        return data
    else:
        print(f"Error al hacer la solicitud a la API: {response.status_code}")
        return None

@app.route('/obtener_datos_climaticos', methods=['GET'])
def obtener_datos_climaticos():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM datos_climaticos ORDER BY fecha DESC LIMIT 50")
    datos = cur.fetchall()
    column_names = [column[0] for column in cur.description]
    cur.close()
    
    datos_climaticos = []
    for dato in datos:
        dato_dict = dict(zip(column_names, dato))
        dato_dict['fecha'] = dato_dict['fecha'].strftime('%Y-%m-%d %H:%M:%S')
        dato_dict['temperatura'] = float(dato_dict['temperatura'])
        dato_dict['humedad'] = float(dato_dict['humedad'])
        dato_dict['precipitacion'] = float(dato_dict['precipitacion']) if dato_dict['precipitacion'] else None
        dato_dict['velocidadViento'] = float(dato_dict['velocidadViento']) if dato_dict['velocidadViento'] else None
        datos_climaticos.append(dato_dict)
    return jsonify(datos_climaticos)


@app.route('/almacenar_datos_climaticos', methods=['GET'])
def almacenar_datos_climaticos():
    api_key = '97b20a75a1d9cc16f1328d9e2c176698'
    latitud = '20.6667'
    longitud = '-103.3333'

    datos_clima = obtener_datos_climaticos_clima(api_key, latitud, longitud)
    if datos_clima:
        try:
            temperatura = datos_clima['main']['temp']
            humedad = datos_clima['main']['humidity']
            # Para precipitacion necesitas revisar si la respuesta incluye 'rain' y luego '1h'.
            precipitacion = datos_clima.get('rain', {}).get('1h', 0)
            velocidad_viento = datos_clima['wind']['speed']

            cur = mysql.connection.cursor()
            cur.execute("""
            INSERT INTO datos_climaticos 
            (fecha, latitud, longitud, temperatura, humedad, precipitacion, velocidadViento) 
            VALUES (NOW(), %s, %s, %s, %s, %s, %s)
            """, (latitud, longitud, temperatura, humedad, precipitacion, velocidad_viento))

            mysql.connection.commit()
            cur.close()
            return jsonify({"mensaje": "Datos climáticos almacenados con éxito."})
        except KeyError as e:
            return jsonify({"mensaje": f"Error al extraer datos climáticos: {e}"})
    return jsonify({"mensaje": "Error al obtener datos climáticos."})


# PRECIO AGAVE

api_key2 = '7fb4bc0d-b1ed-43c3-999b-bdc3e3a9bacf'
def obtener_precio_agve():
    url = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest'
    parameters = {'slug': 'agave', 'convert': 'USD'}
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': api_key2
    }

    response = requests.get(url, headers=headers, params=parameters)
    if response.status_code == 200:
        data = response.json()
        cripto_data = next(iter(data['data'].values()))  # Obtiene los datos de la criptomoneda
        precio_agve = cripto_data['quote']['USD']['price']
        return precio_agve, cripto_data['last_updated']
    else:
        print(f"Error al obtener el precio: {response.status_code}, {response.text}")
        return None, None

def almacenar_precio_agve():
    precio_agve, last_updated = obtener_precio_agve()
    if precio_agve is not None:
        cur = mysql.connection.cursor()
        # Convertir la fecha a un formato que MySQL pueda almacenar
        fecha_actualizada = datetime.strptime(last_updated, '%Y-%m-%dT%H:%M:%S.%fZ')
        cur.execute("INSERT INTO precios_cripto (fecha, precio) VALUES (%s, %s)", (fecha_actualizada, precio_agve))
        mysql.connection.commit()
        cur.close()

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

#@app.before_first_request
def schedule_jobs():
    scheduler.add_job(func=almacenar_precio_agve, trigger='interval', minutes=1, id='job_precio_agve')
# Programar la tarea para que se ejecute cada minuto


@app.route('/obtener_ultimo_precio_agve', methods=['GET'])
def obtener_ultimo_precio_agve():
    almacenar_precio_agve()
    cur = mysql.connection.cursor()
    cur.execute("SELECT precio, fecha FROM precios_cripto ORDER BY fecha DESC LIMIT 1")
    ultimo_precio = cur.fetchone()
    cur.close()
    if ultimo_precio:
        return jsonify({
            'precio': float(ultimo_precio[0]),
            'fecha': ultimo_precio[1].strftime('%Y-%m-%d %H:%M:%S')
        })
    else:
        return jsonify({"error": "No hay datos disponibles."})

if __name__ == '__main__':
    app.run(port=2000, debug=True)
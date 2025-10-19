# -*- coding: utf-8 -*-
import time
import json
from flask import Blueprint, request, redirect, url_for, flash, render_template, jsonify, Response, stream_with_context

from zoneinfo import available_timezones

from zkteco_app.models import DeviceSettings, DeviceUser, UserTemplate, UserAttendance
from zkteco_app import db

from zkteco.zkteco_server import start_zk, stop_zk, restart_zk, sync_zk_state, get_connected_sessions



routes = Blueprint('routes', __name__)


connected_zkteco_sessions = 0

def config_settings():
    settings = DeviceSettings.query.limit(1).first()

    if not settings:
        settings = DeviceSettings(
                name="",
                timezone="UTC",
                host="0.0.0.0",
                port=4370,
                timeout=3,
                protocol="TCP",
                is_punch_enabled=True
                )
        db.session.add(settings)
        db.session.commit()
        return settings
    else:
        return settings


def update_zkteco_connected_sessions():
    global connected_zkteco_sessions

    connected_sessions = get_connected_sessions()
    if connected_sessions != connected_zkteco_sessions:
        connected_zkteco_sessions = connected_sessions
        return connected_sessions
    else:
        return None


@routes.route('/')
def index():
    return redirect(url_for('routes.users'))

@routes.route('/settings', methods=['GET', 'POST'])
def settings():
    settings = DeviceSettings.query.first()
    if not settings:
        settings = config_settings()

    timezones = sorted(available_timezones())

    if request.method == 'POST':
        required_fields = ['name', 'timezone', 'host', 'port', 'protocol']
        if all(field in request.form for field in required_fields):
            name = request.form.get('name')
            timezone = request.form.get('timezone')
            host = request.form.get('host')
            port = request.form.get('port')
            timeout = request.form.get('timeout')
            protocol = request.form.get('protocol')
            if port:
                port = int(port)
            if timeout:
                timeout = int(timeout)

            if name and timezone and host and port and protocol:
                if not settings:
                    settings = DeviceSettings(
                            name=name, 
                            timezone=timezone, 
                            host=host, 
                            port=port,
                            timeout=timeout,
                            protocol=protocol
                            )
                    db.session.add(settings)
                else:
                    settings.name = name
                    settings.timezone = timezone
                    settings.host = host
                    settings.port = port
                    settings.timeout = timeout
                    settings.protocol = protocol

                db.session.commit()
                flash('Settings saved successfully!', 'success')
                return redirect(url_for('routes.settings'))
            else:
                flash('Please fill all required fields.', 'error')
                return redirect(url_for('routes.settings'))
        else:
            flash('Please fill all required fields.', 'error')
            return redirect(url_for('routes.settings'))
    
    global connected_zkteco_sessions
    connected_sessions = get_connected_sessions()
    connected_zkteco_sessions = connected_sessions
    return render_template('settings.html', settings=settings, timezones=timezones, connected_sessions=connected_sessions)


@routes.route('/settings/reset', methods=['GET', 'POST'])
def reset_settings():
    settings = DeviceSettings.query.first()
    if not settings:
        settings = config_settings()

    timezones = sorted(available_timezones())

    if request.method == 'POST':
        required_fields = ['reset']
        if all(field in request.form for field in required_fields):
            reset = request.form.get('reset')
            if reset == "reset_settings":
                if not settings:
                    settings = DeviceSettings(
                            name="",
                            timezone="UTC",
                            host="0.0.0.0",
                            port=4370,
                            timeout=3,
                            protocol="TCP"
                            )
                    db.session.add(settings)
                else:
                    settings.name = ""
                    settings.timezone = "UTC"
                    settings.host = "0.0.0.0"
                    settings.port = 4370
                    settings.timeout = 3
                    settings.protocol = "TCP"

                db.session.commit()
                flash('Settings have been restored to default.', 'success')
                return redirect(url_for('routes.settings'))
            else:
                return redirect(url_for('routes.settings'))
        else:
            return redirect(url_for('routes.settings'))

    return render_template('settings.html', settings=settings, timezones=timezones)

@routes.route('/users/upload', methods=['GET', 'POST'])
def upload_users():
    settings = DeviceSettings.query.first()
    if not settings:
        settings = config_settings()

    timezones = sorted(available_timezones())
    if request.method == 'POST':
        required_fields = ['privilege', 'password', 'name', 'card', 'group_id', 'timezone']
        if all(field in request.form for field in required_fields):
            privilege = int(request.form.get('privilege'))
            password = str(request.form.get('password'))
            name = str(request.form.get('name'))
            card = int(request.form.get('card'))
            group_id = int(request.form.get('group_id'))
            timezone = request.form.get('timezone')
            max_uid = db.session.query(db.func.max(DeviceUser.uid)).scalar() or 0
            new_uid = max_uid + 1

            max_user_id = db.session.query(db.func.max(DeviceUser.user_id)).scalar() or 0
            new_user_id = max_user_id + 1

            new_user = DeviceUser(
                    uid = new_uid,
                    privilege = privilege,
                    password = password,
                    name = name,
                    card = card,
                    group_id = group_id,
                    timezone = timezone,
                    user_id = new_uid
                    )
            db.session.add(new_user)
            db.session.commit()

            flash(f'User {name} was added successfully!', 'success')
            return redirect(url_for('routes.edit_user', id=new_user.id))
        else:
            flash('Error!')
            return redirect(url_for('routes.upload_users'))
    return render_template('upload_user.html', settings=settings, timezones=timezones)


@routes.route('/user/<id>/edit', methods=['GET', 'POST'])
def edit_user(id):
    id = int(id)
    user = db.session.query(DeviceUser).filter_by(id=id).first()
    if not user:
        flash('User not found!', 'error')
        return redirect(url_for('routes.users'))
    
    timezones = sorted(available_timezones())
    if request.method == 'POST':
        required_fields = ['id', 'privilege', 'password', 'name', 'card', 'group_id', 'timezone']
        if all(field in request.form for field in required_fields):
            rec_id = int(request.form.get('id'))
            privilege = int(request.form.get('privilege'))
            password = str(request.form.get('password'))
            name = str(request.form.get('name'))
            card = int(request.form.get('card'))
            group_id = int(request.form.get('group_id'))
            timezone = request.form.get('timezone')
            
            rec_user = db.session.query(DeviceUser).filter_by(id=rec_id).first()
            if rec_user:
                rec_user.name = name
                rec_user.privilege = privilege
                rec_user.password = password
                rec_user.card = card
                rec_user.group_id = group_id
                rec_user.timezone = timezone

                db.session.commit()
                flash(f'The user {name} has been successfully updated.', 'success')
                return redirect(url_for('routes.edit_user', id=rec_id))
        else:
            flash('Error!')
            return redirect(url_for('routes.edit_user', id=id))
    return render_template('edit_user.html', user=user, timezones=timezones)


@routes.route('/users/template/upload', methods=['GET', 'POST'])
def upload_user_template():
    users_list = DeviceUser.query.order_by(DeviceUser.create_date.desc()).all()
    if request.method == 'POST':
        required_fields = ['uid', 'valid']
        if all(field in request.form for field in required_fields) and 'template' in request.files:
            uid_str = str(request.form.get('uid', '')) + ':'
            uid, name = uid_str.split(":", 1)
            uid = int(uid)
            valid = int(request.form.get('valid'))
            fid = int(request.form.get('fid'))

            file = request.files['template']
            template_data = file.read()
            size = len(template_data)

            if any(user.uid == uid for user in users_list):
                new_template = UserTemplate(
                        device_user_id = uid,
                        uid = uid,
                        fid = fid,
                        valid = valid,
                        template = template_data,
                        size = size,
                        )
                db.session.add(new_template)
                db.session.commit()

                flash(f'Template was added successfully!', 'success')
                return redirect(url_for('routes.edit_user_template', id=new_template.id))
            else:
                flash("Selected user does not exist", "error")
                return redirect(url_for('routes.upload_user_template'))
        else:
            flash('Error!')
            return redirect(url_for('routes.upload_user_template'))
    return render_template('upload_user_template.html', users_list=users_list)


@routes.route('/template/<id>/edit', methods=['GET', 'POST'])
def edit_user_template(id):
    id = int(id)
    template = db.session.query(UserTemplate).filter_by(id=id).first()
    users_list = DeviceUser.query.order_by(DeviceUser.create_date.desc()).all()
    
    if not template:
        flash('Template not found!', 'error')
        return redirect(url_for('routes.users_templates'))

    if request.method == 'POST':
        required_fields = ['id', 'uid', 'valid']
        if all(field in request.form for field in required_fields) and 'template' in request.files:
            rec_id = int(request.form.get('id'))
            uid_str = str(request.form.get('uid', '')) + ':'
            uid, name = uid_str.split(":", 1)
            uid = int(uid)
            valid = int(request.form.get('valid'))
            fid = int(request.form.get('fid'))
            delete_template_file = request.form.get('delete_template_file')

            file = request.files['template']
            template_data = file.read()
            size = len(template_data)

            if any(user.uid == uid for user in users_list):
                rec_template = db.session.query(UserTemplate).filter_by(id=rec_id).first()
                if rec_template:
                    rec_template.device_user_id = uid
                    rec_template.uid = uid
                    rec_template.fid = fid
                    rec_template.valid = valid
                    if size > 0:
                        rec_template.template = template_data
                        rec_template.size = size
                    if delete_template_file:
                        rec_template.template = b''
                        rec_template.size = 0
                    
                    db.session.commit()
                    
                    updt_template = db.session.query(UserTemplate).filter_by(id=rec_id).first()
                    flash(f'The template {rec_id}:{updt_template.device_user.name} has been successfully updated.', 'success')
                    return redirect(url_for('routes.edit_user_template', id=rec_id))
        else:
            flash('Error!')
            return redirect(url_for('routes.edit_user_template', id=id))
    return render_template('edit_user_template.html', template=template)

@routes.route('/punch/in', methods=['GET', 'POST'])
def punch_in():
    settings = DeviceSettings.query.first()
    if not settings:
        settings = config_settings()

    if request.method == 'POST':
        if request.form:
            if not settings.is_punch_enabled:
                flash("Device is currently busy processing data. Please try again later.", "warning")
                return redirect(url_for('routes.punch_in'))

            for usrid in request.form:
                uid = request.form.get(usrid)
                if uid:
                    uid = int(uid)
                    workcode = request.form.get(f'workcode_{uid}')
                    user = db.session.query(DeviceUser).filter_by(uid=uid).first()
                    if user:
                        user_id = user.user_id
                        new_attendance = UserAttendance(
                                device_user_id = uid,
                                uid = uid,
                                #status = 1,
                                punch = 0,
                                user_id = user_id,
                                #reserved = reserved,
                                workcode = workcode,
                                )
                        db.session.add(new_attendance)
                        db.session.commit()
                        flash(f'Successfully!', 'success')
                        return redirect(url_for('routes.punch_in'))
                    else:
                        flash(f'User {uid} not found', 'error')
                        return redirect(url_for('routes.punch_in'))
        else:
            flash("No data submitted in form.", "warning")
            return redirect(url_for('routes.punch_in'))

    users_list = DeviceUser.query.order_by(DeviceUser.create_date.desc()).all()
    return render_template('punch_in.html', users_list=users_list)


@routes.route('/punch/out', methods=['GET', 'POST'])
def punch_out():
    settings = DeviceSettings.query.first()
    if not settings:
        settings = config_settings()

    if request.method == 'POST':
        if not settings.is_punch_enabled:
            flash("Device is currently busy processing data. Please try again later.", "warning")
            return redirect(url_for('routes.punch_out'))

        for usrid in request.form:
            uid = request.form.get(usrid)
            if uid:
                uid = int(uid)
                workcode = request.form.get(f'workcode_{uid}')
                user = db.session.query(DeviceUser).filter_by(uid=uid).first()
                if user:
                    user_id = user.user_id
                    new_attendance = UserAttendance(
                            device_user_id = uid,
                            uid = uid,
                            #status = 1,
                            punch = 1,
                            user_id = user_id,
                            #reserved = reserved,
                            workcode = workcode,
                            )
                    db.session.add(new_attendance)
                    db.session.commit()
                    flash(f'Successfully!', 'success')
                    return redirect(url_for('routes.punch_out'))
                else:
                    flash(f'User {uid} not found', 'error')
                    return redirect(url_for('routes.punch_out'))
        else:
            flash('Error!')
            return redirect(url_for('routes.punch_out'))
    users_list = DeviceUser.query.order_by(DeviceUser.create_date.desc()).all()
    return render_template('punch_out.html', users_list=users_list)

@routes.route('/users')
def users():
    users_list = DeviceUser.query.order_by(DeviceUser.create_date.desc()).all()
    return render_template('users.html', users_list=users_list)

@routes.route('/users/list/delete', methods=['GET','POST'])
def delete_users_list():
    if request.method == 'POST':
        for usrid in request.form:
            uid = request.form.get(usrid)
            if uid:
                uid = int(uid)
                user = db.session.query(DeviceUser).filter_by(uid=uid).first()
                if user:
                    name = user.name
                    db.session.delete(user)
                    db.session.commit()
                    flash(f'User {name} was deleted successfully', 'success')
                else:
                    flash(f'User {uid} not found', 'error')
        return redirect(url_for('routes.users'))
    users_list = DeviceUser.query.order_by(DeviceUser.create_date.desc()).all()
    return render_template('users.html', users_list=users_list)


@routes.route('/user/delete', methods=['GET','POST'])
def delete_user():
    if request.method == 'POST':
        if 'device_user_id' in request.form:
            device_user_id = request.form.get('device_user_id')
            if device_user_id:
                device_user_id = int(device_user_id)
                user = db.session.query(DeviceUser).filter_by(id=device_user_id).first()
                if user:
                    name = user.name
                    db.session.delete(user)
                    db.session.commit()
                    flash(f'User {name} was deleted successfully', 'success')
                else:
                    flash(f'User {device_user_id} not found', 'error')
        return redirect(url_for('routes.users'))
    users_list = DeviceUser.query.order_by(DeviceUser.create_date.desc()).all()
    return render_template('users.html', users_list=users_list)

@routes.route('/users/templates')
def users_templates():
    users_templates = UserTemplate.query.order_by(UserTemplate.create_date.desc()).all()
    return render_template('users_templates.html', users_templates=users_templates)


@routes.route('/users/templates/list/delete', methods=['GET','POST'])
def delete_users_templates_list():
    users_templates = UserTemplate.query.order_by(UserTemplate.create_date.desc()).all()
    if request.method == 'POST':
        for tmplt_id in request.form:
            template_id = request.form.get(tmplt_id)
            if template_id:
                template_id = int(template_id)
                template = db.session.query(UserTemplate).filter_by(id=template_id).first()
                if template:
                    db.session.delete(template)
                    db.session.commit()
                    flash(f'Template {template_id} was deleted successfully', 'success')
                else:
                    flash(f'Template {template_id} not found', 'error')
        return redirect(url_for('routes.users_templates'))
    return render_template('users_templates.html', users_templates=users_templates)


@routes.route('/user/template/delete', methods=['GET','POST'])
def delete_user_template():
    users_templates = UserTemplate.query.order_by(UserTemplate.create_date.desc()).all()
    if request.method == 'POST':
        if 'template_id' in request.form:
            template_id = request.form.get('template_id')
            if template_id:
                template_id = int(template_id)
                template = db.session.query(UserTemplate).filter_by(id=template_id).first()
                if template:
                    db.session.delete(template)
                    db.session.commit()
                    flash(f'Template {template_id} was deleted successfully', 'success')
                else:
                    flash(f'Template {template_id} not found', 'error')
        return redirect(url_for('routes.users_templates'))
    return render_template('users_templates.html', users_templates=users_templates)


@routes.route('/attendance/list/delete', methods=['GET','POST'])
def delete_attendance_list():
    attendance_list = UserAttendance.query.order_by(UserAttendance.create_date.desc()).all()
    if request.method == 'POST':
        for att_id in request.form:
            attendance_id = request.form.get(att_id)
            if attendance_id:
                attendance_id = int(attendance_id)
                attendance = db.session.query(UserAttendance).filter_by(id=attendance_id).first()
                if attendance:
                    db.session.delete(attendance)
                    db.session.commit()
                    flash(f'Attendance {attendance_id} was deleted successfully', 'success')
                else:
                    flash(f'Attendance {attendance_id} not found', 'error')
        return redirect(url_for('routes.users_attendance'))
    return render_template('attendance.html', attendance_list=attendance_list)
###

@routes.route('/attendance')
def users_attendance():
    attendance_list = UserAttendance.query.order_by(UserAttendance.create_date.desc()).all()
    return render_template('attendance.html', attendance_list=attendance_list)



@routes.route("/zk/start", methods=['GET', 'POST'])
def start_zk_server():
    settings = DeviceSettings.query.first()
    if not settings:
        settings = config_settings()

    if not settings.is_active:
        try:
            start_zk()
            status = [True, '']
        except Exception as e:
            status = [False, str(e)]
        if status[0]:
            return jsonify({"status": "ZKTeco server started"})
        else:
            return jsonify({"status": str(status[1])})
    else:
        return jsonify({"status": "ZKTeco server is already running"})

@routes.route("/zk/stop", methods=['GET', 'POST'])
def stop_zk_server():
    settings = DeviceSettings.query.first()
    if not settings:
        settings = config_settings()

    print(settings.is_active)
    if settings.is_active:
        try:
            status = stop_zk()
        except Exception as e:
            status = [False, str(e)]
        if not isinstance(status, list):
            return jsonify({"status": str(status)})
        if status[0]:
            return jsonify({"status": "ZKTeco server stopped"})
        else:
            return jsonify({"status": str(status[1])})
    else:
        return jsonify({"status": "ZKTeco server is not running"})


@routes.route("/zk/restart", methods=['GET', 'POST'])
def restart_zk_server():
    settings = DeviceSettings.query.first()
    if not settings:
        settings = config_settings()

    if settings.is_active:
        try:
            restart_zk()
            status = [True, '']
        except Exception as e:
            status = [False, str(e)]
        if status[0]:
            return jsonify({"status": "ZK server restarted"})
        else:
            return jsonify({"status": str(status[1])})
    else:
        return jsonify({"status": "ZK server is not running"})


@routes.route("/zk/state/sync", methods=['GET', 'POST'])
def sync_zk_server_state():
    settings = DeviceSettings.query.first()
    if not settings:
        settings = config_settings()

    try:
        if settings.is_active:
            sync_zk_state(True)
        else:
            sync_zk_state()
        status = [True, '']
    except Exception as e:
        status = [False, str(e)]
    if status[0]:
        return jsonify({"status": "ZK server state synchronized successfully"})
    else:
        return jsonify({"status": str(status[1])})

#@routes.route("/zk/sessions/connected", methods=['POST'])
#def zk_connected_sessions():
#    connected_sessions = get_connected_sessions()
#    return jsonify({"sessions": connected_sessions})


@routes.route('/zk/sessions/connected/stream')
def stream_connected_zk_sessions():                                #TODO:
    def event_stream():
        if True:          #TODO
            sessions = update_zkteco_connected_sessions()
            if sessions:
                sessions_info = json.dumps({"sessions": sessions})
                yield f"data: {sessions_info}\n\n"
            time.sleep(3)
    return Response(
            stream_with_context(event_stream()), 
            mimetype='text/event-stream', 
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no',
                'Connection': 'keep-alive'
                }
            )

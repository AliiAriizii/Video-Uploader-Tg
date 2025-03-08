import os
from flask import Flask, request, redirect, url_for, render_template, send_from_directory
from create_db import User, Catgory, Video, session

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploaded_videos'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # File size limit (e.g., 100 MB)

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])


@app.route('/')
def index():
    videos = session.query(Video).all()
    categories = session.query(Catgory).all()
    data = {
        'categories': categories,
        'videos': videos
    }
    
    return render_template('admin_panel.html', data=data)


@app.route('/category/add', methods=['POST'])
def add_category():
    title = request.form['title']
    slug = request.form['slug']
    isActive = request.form.get('isActive') == 'on'

    category = Catgory(title=title, slug=slug, isActive=isActive)
    session.add(category)
    session.commit()
    
    return redirect(url_for('index'))


@app.route('/add', methods=['POST'])
def add_video():
    title = request.form['title']
    category_id = request.form['category']
    file = request.files['file']
    cost = request.form['required_points']
    isActive = request.form.get('isActive') == 'on'

    if file:
        filename = file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        video = Video(Video=filename, Catgory_id=category_id, title=title, cost=cost, isActive=isActive)
        session.add(video)
        session.commit()
        
    return redirect(url_for('index'))


@app.route('/delete', methods=['POST'])
def delete_video():
    video_id = request.form['video_id']
    
    video = session.query(Video).filter_by(id=int(video_id)).first()
    if video:
        filename = video.Video
        if filename:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                
        session.delete(video)
        session.commit()
        
    return redirect(url_for('index'))


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    app.run(debug=True,port=3000,host="127.0.0.1")

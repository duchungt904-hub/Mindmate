import os
from werkzeug.utils import secure_filename
from PIL import Image

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file, upload_folder, prefix=''):
    """
    保存上传的文件
    
    Args:
        file: 上传的文件对象
        upload_folder: 上传目录
        prefix: 文件名前缀
    
    Returns:
        保存后的文件路径（相对路径）或 None
    """
    if not file or file.filename == '':
        return None
    
    if not allowed_file(file.filename):
        return None
    
    # 确保上传目录存在
    os.makedirs(upload_folder, exist_ok=True)
    
    # 生成安全的文件名
    filename = secure_filename(file.filename)
    if prefix:
        filename = f"{prefix}_{filename}"
    
    filepath = os.path.join(upload_folder, filename)
    
    # 保存文件
    file.save(filepath)
    
    # 压缩图片（如果是图片）
    try:
        img = Image.open(filepath)
        
        # 调整大小（最大宽度 800px）
        max_width = 800
        if img.width > max_width:
            ratio = max_width / img.width
            new_height = int(img.height * ratio)
            img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
        
        # 保存压缩后的图片
        img.save(filepath, optimize=True, quality=85)
    except Exception as e:
        print(f"图片压缩失败: {e}")
    
    # 返回相对路径
    return os.path.relpath(filepath, start=upload_folder.rsplit('/', 1)[0])

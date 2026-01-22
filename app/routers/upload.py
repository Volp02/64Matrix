from fastapi import APIRouter, File, UploadFile, Request, HTTPException
import shutil
import os
import aiofiles
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/upload", tags=["Upload"])

@router.post("/file")
async def upload_file(request: Request, file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    filename = file.filename
    
    # Security: Prevent directory traversal
    if ".." in filename or "/" in filename or "\\" in filename:
        raise HTTPException(status_code=400, detail="Invalid filename")
    
    # Determine destination
    if filename.endswith(".py"):
        dest_dir = "scenes/scripts"
    elif filename.endswith(".zip") or filename.endswith(".gif"):
        dest_dir = "scenes/clips"
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type. Supported: .py, .gif, .zip")

    # Ensure directory exists
    try:
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
    except Exception as e:
        logger.error(f"Failed to create directory {dest_dir}: {e}")
        raise HTTPException(status_code=500, detail="Failed to create destination directory")

    file_path = os.path.join(dest_dir, filename)
    
    # Save file
    try:
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await file.read()
            # Basic size check (e.g., 10MB limit)
            max_size = 10 * 1024 * 1024  # 10MB
            if len(content) > max_size:
                raise HTTPException(status_code=400, detail=f"File too large. Maximum size: {max_size / 1024 / 1024}MB")
            await out_file.write(content)
            logger.info(f"Successfully uploaded file: {filename}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to save file {filename}: {e}")
        # Clean up partial file if it exists
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
        
    # Metadata Initialization
    try:
        lib_mgr = request.app.state.library_manager
        clean_name = os.path.splitext(filename)[0].replace("_", " ").title()
        lib_mgr.update_metadata(filename, title=clean_name)
    except Exception as e:
        logger.warning(f"Failed to update metadata for {filename}: {e}")
        # Don't fail the upload if metadata update fails
        
    return {"status": "ok", "filename": filename}

from fastapi import APIRouter, File, UploadFile, Request
import shutil
import os
import aiofiles

router = APIRouter(prefix="/api/upload", tags=["Upload"])

@router.post("/file")
async def upload_file(request: Request, file: UploadFile = File(...)):
    filename = file.filename
    
    # Determine destination
    if filename.endswith(".py"):
        dest_dir = "scenes/scripts"
    elif filename.endswith(".zip") or filename.endswith(".gif"):
        dest_dir = "scenes/clips"
    else:
        return {"error": "Unsupported file type"}

    # Ensure directory exists
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    file_path = os.path.join(dest_dir, filename)
    
    # Save file
    async with aiofiles.open(file_path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)
        
    # Metadata Initialization
    lib_mgr = request.app.state.library_manager
    clean_name = os.path.splitext(filename)[0].replace("_", " ").title()
    lib_mgr.update_metadata(filename, title=clean_name)
    
    # Refresh logic (optional but good practice)
    # request.app.state.script_loader.refresh() ? 
    # Current implementation of list_scenes scans dir every time, so it's fine.
        
    return {"status": "ok", "filename": filename}

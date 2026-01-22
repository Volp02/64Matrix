from fastapi import APIRouter, File, UploadFile, Request, HTTPException
import shutil
import os
import aiofiles
import logging
from PIL import Image, ImageSequence
import io

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
        content = await file.read()
        # Basic size check (e.g., 10MB limit)
        max_size = 10 * 1024 * 1024  # 10MB
        if len(content) > max_size:
            raise HTTPException(status_code=400, detail=f"File too large. Maximum size: {max_size / 1024 / 1024}MB")
        
        # Process GIF files: resize to 64x64 if needed
        if filename.lower().endswith('.gif'):
            try:
                # Open the uploaded GIF
                gif_buffer = io.BytesIO(content)
                with Image.open(gif_buffer) as img:
                    # Check if resizing is needed
                    if img.size != (64, 64):
                        logger.info(f"Resizing GIF {filename} from {img.size} to 64x64")
                        
                        # Collect all frames with their durations
                        frames = []
                        durations = []
                        for frame in ImageSequence.Iterator(img):
                            # Convert to RGB and resize
                            frame_rgb = frame.convert('RGB')
                            frame_resized = frame_rgb.resize((64, 64), Image.Resampling.LANCZOS)
                            frames.append(frame_resized)
                            
                            # Preserve frame duration
                            duration = frame.info.get('duration', 100)  # default 100ms
                            durations.append(duration)
                        
                        # Save as new GIF with all frames
                        output_buffer = io.BytesIO()
                        if len(frames) > 0:
                            frames[0].save(
                                output_buffer,
                                format='GIF',
                                save_all=True,
                                append_images=frames[1:] if len(frames) > 1 else [],
                                duration=durations,
                                loop=0,  # Infinite loop
                                optimize=False  # Keep all frames for better quality
                            )
                            content = output_buffer.getvalue()
                            logger.info(f"Successfully resized GIF {filename} to 64x64 ({len(frames)} frames)")
                        else:
                            logger.warning(f"GIF {filename} has no frames, saving as-is")
                    else:
                        logger.debug(f"GIF {filename} is already 64x64, no resizing needed")
                    
                    # Generate thumbnail from first frame
                    try:
                        gif_buffer.seek(0)  # Reset buffer position
                        with Image.open(gif_buffer) as img:
                            # Get first frame
                            first_frame = next(ImageSequence.Iterator(img))
                            first_frame_rgb = first_frame.convert('RGB')
                            
                            # Resize thumbnail if needed (thumbnails can be larger for better quality)
                            thumb_size = (128, 128)  # 2x size for better thumbnail quality
                            if first_frame_rgb.size != thumb_size:
                                thumbnail = first_frame_rgb.resize(thumb_size, Image.Resampling.LANCZOS)
                            else:
                                thumbnail = first_frame_rgb
                            
                            # Save thumbnail
                            thumb_dir = os.path.join("scenes", "thumbnails")
                            if not os.path.exists(thumb_dir):
                                os.makedirs(thumb_dir)
                            
                            thumb_path = os.path.join(thumb_dir, f"{filename}.png")
                            thumbnail.save(thumb_path, "PNG")
                            logger.info(f"Generated thumbnail for GIF {filename}")
                    except Exception as e:
                        logger.warning(f"Failed to generate thumbnail for GIF {filename}: {e}")
            except Exception as e:
                logger.error(f"Failed to process GIF {filename}: {e}")
                # If GIF processing fails, save original file anyway
                logger.warning(f"Saving GIF {filename} without resizing due to processing error")
        
        # Write the (possibly processed) file
        async with aiofiles.open(file_path, 'wb') as out_file:
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

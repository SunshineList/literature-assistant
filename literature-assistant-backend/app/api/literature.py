"""
文献管理 API
"""
import os
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse, FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse
from app.core.database import get_db
from app.core.response import Response, PageData
from app.core.response_builder import ResponseBuilder, PageDataBuilder
from app.core.exceptions import FileException, LiteratureException, NotFoundException
from app.models.schemas import (
    LiteratureQueryRequest,
    LiteratureResponse,
    LiteratureDetailResponse,
    HealthResponse
)
from app.models.users import User
from app.services.literature_service import literature_service
from app.services.file_service import file_service
from app.services.ai_service import ai_service
from app.services.ai_model_service import ai_model_service
from app.utils.auth import get_current_user
from app.config import settings

router = APIRouter(prefix="/literature", tags=["文献管理"])


@router.get("/health", response_model=Response[HealthResponse])
async def health_check():
    """健康检查"""
    return ResponseBuilder.ok(
        data=HealthResponse(status="ok", message="服务正常运行"),
        message="健康检查通过"
    )


@router.post("/page", response_model=Response[PageData[LiteratureResponse]])
async def page_query(
    query_params: LiteratureQueryRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    分页查询文献列表（只返回当前用户的文献）
    """
    try:
        literatures, total = await literature_service.page_query(db, query_params, user_id=current_user.id)
        
        # 转换为响应模型
        records = [literature_service.to_response(lit) for lit in literatures]
        
        # 使用建造者模式构建分页数据
        page_data = PageDataBuilder.from_query_result(
            records=records,
            total=total,
            page_num=query_params.pageNum,
            page_size=query_params.pageSize
        )
        
        return ResponseBuilder.ok(data=page_data, message="查询成功")
    
    except LiteratureException as e:
        return ResponseBuilder.error(message=e.message, code=e.code)
    except Exception as e:
        return ResponseBuilder.error(message=f"查询失败: {str(e)}", code=500)


@router.get("/{literature_id}", response_model=Response[LiteratureDetailResponse])
async def get_literature_detail(
    literature_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取文献详情（只能查看自己的文献）
    """
    try:
        literature = await literature_service.get_literature_by_id(db, literature_id, user_id=current_user.id)
        
        if not literature:
            raise NotFoundException("文献不存在或无权限访问")
        
        detail = literature_service.to_detail_response(literature)
        
        return ResponseBuilder.ok(data=detail, message="查询成功")
    
    except NotFoundException as e:
        return ResponseBuilder.not_found(message=e.message)
    except LiteratureException as e:
        return ResponseBuilder.error(message=e.message, code=e.code)
    except Exception as e:
        return ResponseBuilder.error(message=f"查询失败: {str(e)}", code=500)


@router.get("/{literature_id}/download")
async def download_literature(
    literature_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    下载文献文件（只能下载自己的文献）
    """
    try:
        literature = await literature_service.get_literature_by_id(db, literature_id, user_id=current_user.id)
        
        if not literature:
            raise HTTPException(status_code=404, detail="文献不存在或无权限访问")
        
        # 构建完整文件路径
        file_path = os.path.join(settings.UPLOAD_DIR, literature.file_path)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="文件不存在")
        
        # 返回文件
        return FileResponse(
            path=file_path,
            filename=literature.original_name,
            media_type="application/octet-stream"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"下载失败: {str(e)}")


@router.post("/generate-guide")
async def generate_reading_guide(
    file: UploadFile = File(...),
    aiModelId: int = Form(None),  # 可选的AI模型ID
    expertId: str = Form("academic-mentor"),  # 专家ID，默认为学术导师
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    上传文献并生成阅读指南（SSE流式响应）
    使用用户指定的AI模型或默认模型，以及指定的专家
    
    Args:
        file: 上传的文件
        aiModelId: 可选的AI模型ID，不提供则使用默认模型
        expertId: 专家ID，默认为"academic-mentor"（学术导师）
    """
    
    literature_id = None
    file_full_path = None
    
    async def event_generator():
        nonlocal literature_id, file_full_path
        
        try:
            # 获取AI模型（优先使用用户指定的，否则使用默认的）
            if aiModelId:
                ai_model = await ai_model_service.get_model_by_id(db, aiModelId, current_user.id)
                if not ai_model:
                    yield {
                        "event": "error",
                        "data": "指定的AI模型不存在或无权限访问"
                    }
                    return
            else:
                ai_model = await ai_model_service.get_default_model(db, current_user.id)
                if not ai_model:
                    yield {
                        "event": "error",
                        "data": "请先在AI模型管理中配置默认AI模型"
                    }
                    return
            
            # 1. 保存文件
            yield {
                "event": "progress",
                "data": "正在保存文件..."
            }
            
            file_full_path, file_relative_path, file_size, file_type = await file_service.save_file(file)
            
            # 2. 提取文件内容
            yield {
                "event": "progress",
                "data": "正在解析文件内容..."
            }
            
            content = await file_service.extract_content(file_full_path, file_type)
            content_length = len(content)
            
            # 3. 创建文献记录（初始状态为处理中）
            yield {
                "event": "progress",
                "data": "正在创建文献记录..."
            }
            
            literature = await literature_service.create_literature(
                db=db,
                user_id=current_user.id,
                original_name=file.filename,
                file_path=file_relative_path,
                file_size=file_size,
                file_type=file_type,
                content_length=content_length,
                status=0  # 处理中
            )
            literature_id = literature.id
            await db.commit()
            
            # 4. 生成阅读指南（流式）
            yield {
                "event": "start",
                "data": "开始生成阅读指南..."
            }
            
            reading_guide_parts = []
            
            async for message in ai_service.generate_reading_guide_stream(
                content=content,
                ai_model=ai_model,
                expert_id=expertId
            ):
                msg_type = message.get("type")
                msg_data = message.get("data", "")
                
                if msg_type == "content":
                    reading_guide_parts.append(msg_data)
                    yield {
                        "event": "content",
                        "data": msg_data
                    }
                elif msg_type == "progress":
                    yield {
                        "event": "progress",
                        "data": msg_data
                    }
            
            # 5. 保存完整的阅读指南
            reading_guide = "".join(reading_guide_parts)
            
            # 6. 从阅读指南中提取标签和描述
            yield {
                "event": "progress",
                "data": "正在提取标签和描述..."
            }
            
            tags, description = await ai_service.extract_tags_and_description(
                reading_guide,
                ai_model
            )
            
            await literature_service.update_literature(
                db=db,
                literature_id=literature_id,
                reading_guide=reading_guide,
                tags=tags,
                description=description,
                status=1  # 已完成
            )
            await db.commit()
            
            # 7. 发送完成消息
            yield {
                "event": "complete",
                "data": "阅读指南生成完成！"
            }
        
        except LiteratureException as e:
            # 更新状态为失败
            if literature_id:
                try:
                    await literature_service.update_literature(
                        db=db,
                        literature_id=literature_id,
                        status=2  # 失败
                    )
                    await db.commit()
                except:
                    pass
            
            yield {
                "event": "error",
                "data": e.message
            }
        
        except Exception as e:
            # 更新状态为失败
            if literature_id:
                try:
                    await literature_service.update_literature(
                        db=db,
                        literature_id=literature_id,
                        status=2  # 失败
                    )
                    await db.commit()
                except:
                    pass
            
            # 清理文件
            if file_full_path and os.path.exists(file_full_path):
                try:
                    file_service.delete_file(file_full_path)
                except:
                    pass
            
            yield {
                "event": "error",
                "data": f"生成失败: {str(e)}"
            }
    
    return EventSourceResponse(event_generator())


@router.post("/batch-import")
async def batch_import_literatures(
    files: list[UploadFile] = File(...),
    aiModelId: int = Form(None),  # 可选的AI模型ID
    expertId: str = Form("academic-mentor"),  # 专家ID，默认为学术导师
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    批量导入文献并生成阅读指南（SSE流式响应）
    使用用户指定的AI模型或默认模型，以及指定的专家
    
    Args:
        files: 上传的文件列表
        aiModelId: 可选的AI模型ID，不提供则使用默认模型
        expertId: 专家ID，默认为"academic-mentor"（学术导师）
    """
    # 关键修复：在生成器外部先保存所有文件到磁盘
    # 这样避免了在生成器运行时 UploadFile 对象被关闭的问题
    saved_files_info = []
    try:
        for index, file in enumerate(files):
            try:
                # 保存文件到磁盘
                file_full_path, file_relative_path, file_size, file_type = await file_service.save_file(file)
                saved_files_info.append({
                    'index': index,
                    'filename': file.filename,
                    'file_full_path': file_full_path,
                    'file_relative_path': file_relative_path,
                    'file_size': file_size,
                    'file_type': file_type
                })
            except Exception as e:
                # 如果某个文件保存失败，清理已保存的文件
                for saved_info in saved_files_info:
                    try:
                        if os.path.exists(saved_info['file_full_path']):
                            file_service.delete_file(saved_info['file_full_path'])
                    except:
                        pass
                raise FileException(f"文件 '{file.filename}' 保存失败: {str(e)}")
    except Exception as e:
        raise FileException(f"批量文件保存失败: {str(e)}")
    
    async def event_generator():
        # 获取AI模型（优先使用用户指定的，否则使用默认的）
        if aiModelId:
            ai_model = await ai_model_service.get_model_by_id(db, aiModelId, current_user.id)
            if not ai_model:
                yield {
                    "event": "error",
                    "data": "指定的AI模型不存在或无权限访问"
                }
                return
        else:
            ai_model = await ai_model_service.get_default_model(db, current_user.id)
            if not ai_model:
                yield {
                    "event": "error",
                    "data": "请先在AI模型管理中配置默认AI模型"
                }
                return
        
        total_files = len(saved_files_info)
        completed_files = 0
        
        for file_info in saved_files_info:
            index = file_info['index']
            filename = file_info['filename']
            file_full_path = file_info['file_full_path']
            file_relative_path = file_info['file_relative_path']
            file_size = file_info['file_size']
            file_type = file_info['file_type']
            
            literature_id = None
            
            try:
                # 发送开始处理当前文件的消息
                yield {
                    "event": "file_start",
                    "data": f"{index}|{filename}"
                }
                
                # 文件已经保存，直接进入下一步
                
                # 2. 提取文件内容
                yield {
                    "event": "file_progress",
                    "data": f"{index}|正在解析文件内容..."
                }
                
                content = await file_service.extract_content(file_full_path, file_type)
                content_length = len(content)
                
                # 3. 创建文献记录
                yield {
                    "event": "file_progress",
                    "data": f"{index}|正在创建文献记录..."
                }
                
                literature = await literature_service.create_literature(
                    db=db,
                    user_id=current_user.id,
                    original_name=filename,
                    file_path=file_relative_path,
                    file_size=file_size,
                    file_type=file_type,
                    content_length=content_length,
                    status=0  # 处理中
                )
                literature_id = literature.id
                await db.commit()
                
                # 4. 生成阅读指南
                yield {
                    "event": "file_progress",
                    "data": f"{index}|正在生成阅读指南..."
                }
                
                reading_guide_parts = []
                
                async for message in ai_service.generate_reading_guide_stream(
                    content=content,
                    ai_model=ai_model,
                    expert_id=expertId
                ):
                    msg_type = message.get("type")
                    msg_data = message.get("data", "")
                    
                    if msg_type == "content":
                        reading_guide_parts.append(msg_data)
                    elif msg_type == "progress":
                        yield {
                            "event": "file_progress",
                            "data": f"{index}|{msg_data}"
                        }
                
                reading_guide = "".join(reading_guide_parts)
                
                # 5. 提取标签和描述
                yield {
                    "event": "file_progress",
                    "data": f"{index}|正在提取标签和描述..."
                }
                
                tags, description = await ai_service.extract_tags_and_description(reading_guide, ai_model)
                
                # 6. 更新文献记录
                await literature_service.update_literature(
                    db=db,
                    literature_id=literature_id,
                    tags=tags,
                    description=description,
                    reading_guide=reading_guide,
                    status=1  # 成功
                )
                await db.commit()
                
                completed_files += 1
                
                # 发送文件完成消息
                yield {
                    "event": "file_complete",
                    "data": f"{index}|{literature_id}"
                }
                
            except Exception as e:
                # 更新状态为失败
                if literature_id:
                    try:
                        await literature_service.update_literature(
                            db=db,
                            literature_id=literature_id,
                            status=2  # 失败
                        )
                        await db.commit()
                    except:
                        pass
                
                # 清理文件
                if file_full_path and os.path.exists(file_full_path):
                    try:
                        file_service.delete_file(file_full_path)
                    except:
                        pass
                
                # 发送文件错误消息
                yield {
                    "event": "file_error",
                    "data": f"{index}|{str(e)}"
                }
        
        # 发送批量处理完成消息
        yield {
            "event": "batch_complete",
            "data": f"批量处理完成！成功: {completed_files}/{total_files}"
        }
    
    return EventSourceResponse(event_generator())


@router.delete("/{literature_id}", response_model=Response[bool])
async def delete_literature(
    literature_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    删除文献（只能删除自己的文献）
    """
    try:
        await literature_service.delete_literature(db, literature_id, current_user.id)
        await db.commit()
        
        return ResponseBuilder.ok(data=True, message="删除成功")
    
    except NotFoundException as e:
        return ResponseBuilder.not_found(message=e.message)
    except LiteratureException as e:
        return ResponseBuilder.error(message=e.message, code=e.code)
    except Exception as e:
        return ResponseBuilder.error(message=f"删除失败: {str(e)}", code=500)


@router.get("/experts/list")
async def get_experts_list(
    current_user: User = Depends(get_current_user)
):
    """
    获取所有可用的专家列表
    """
    try:
        experts = ai_service.get_available_experts()
        return ResponseBuilder.ok(data=experts, message="获取成功")
    except Exception as e:
        return ResponseBuilder.error(message=f"获取专家列表失败: {str(e)}", code=500)

